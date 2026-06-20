import time
import uuid
from typing import Protocol, Type
import pytest
from app.customers.domain import Address, Customer, CustomerName, Whatsapp, Cpf, Cnpj, Email
from app.customers.interfaces import AbstractCustomerRepository as CustomerRepository
from app.customers.in_memory_repository import InMemoryCustomerRepository
from app.customers.repository import SqlAlchemyCustomerRepository
from app.customers.models import CustomerModel
from app.db import Base, engine, SessionFactory

class RepositoryFactory(Protocol):
    def __call__(self) -> CustomerRepository:
        ...

class CustomerRepositoryContract:
    @pytest.fixture
    def repository(self) -> CustomerRepository:
        raise NotImplementedError("Subclasses must implement this fixture")

    def test_add_customer(self, repository: CustomerRepository):
        customer = Customer(
            id=uuid.uuid4(),
            name=CustomerName("João Silva"),
            whatsapp=Whatsapp("11999999999")
        )
        repository.add(customer)
        assert repository.get_by_id(customer.id).id == customer.id

    def test_add_rejects_duplicate_id(self, repository: CustomerRepository):
        customer_id = uuid.uuid4()
        c1 = Customer(id=customer_id, name=CustomerName("João Silva"), whatsapp=Whatsapp("11999999999"))
        c2 = Customer(id=customer_id, name=CustomerName("Maria Souza"), whatsapp=Whatsapp("11988888888"))
        
        repository.add(c1)
        with pytest.raises(ValueError, match="already exists"):
            repository.add(c2)

    def test_add_rejects_duplicate_whatsapp(self, repository: CustomerRepository):
        whatsapp = Whatsapp("11999999999")
        c1 = Customer(id=uuid.uuid4(), name=CustomerName("João Silva"), whatsapp=whatsapp)
        c2 = Customer(id=uuid.uuid4(), name=CustomerName("Maria Souza"), whatsapp=whatsapp)
        
        repository.add(c1)
        with pytest.raises(ValueError, match="WhatsApp already exists"):
            repository.add(c2)

    def test_add_rejects_duplicate_cpf(self, repository: CustomerRepository):
        cpf = Cpf("035.776.570-22")
        c1 = Customer(id=uuid.uuid4(), name=CustomerName("João Silva"), whatsapp=Whatsapp("11999999999"), cpf=cpf)
        c2 = Customer(id=uuid.uuid4(), name=CustomerName("Maria Souza"), whatsapp=Whatsapp("11988888888"), cpf=cpf)
        
        repository.add(c1)
        with pytest.raises(ValueError, match="CPF already exists"):
            repository.add(c2)

    def test_add_rejects_duplicate_cnpj(self, repository: CustomerRepository):
        cnpj = Cnpj("11.222.333/0001-81")
        c1 = Customer(id=uuid.uuid4(), name=CustomerName("Empresa A"), whatsapp=Whatsapp("11999999999"), cnpj=cnpj)
        c2 = Customer(id=uuid.uuid4(), name=CustomerName("Empresa B"), whatsapp=Whatsapp("11988888888"), cnpj=cnpj)
        
        repository.add(c1)
        with pytest.raises(ValueError, match="CNPJ already exists"):
            repository.add(c2)

    def test_get_by_id_returns_none_if_not_found(self, repository: CustomerRepository):
        assert repository.get_by_id(uuid.uuid4()) is None

    def test_update_customer(self, repository: CustomerRepository):
        customer = Customer(id=uuid.uuid4(), name=CustomerName("João Silva"), whatsapp=Whatsapp("11999999999"))
        repository.add(customer)
        
        updated = customer.deactivate()
        repository.update(updated)
        
        assert repository.get_by_id(customer.id).is_active is False

    def test_update_replaces_customer_fields(self, repository: CustomerRepository):
        customer = Customer(
            id=uuid.uuid4(),
            name=CustomerName("João Silva"),
            whatsapp=Whatsapp("11999999999"),
            cpf=Cpf("035.776.570-22"),
            email=Email("joao@example.com"),
            address=Address(street="Rua A", zip_code="12345-678"),
            notes="Initial notes",
        )
        repository.add(customer)

        updated = Customer(
            id=customer.id,
            name=CustomerName("Maria Souza"),
            whatsapp=Whatsapp("11988888888"),
            cnpj=Cnpj("11.222.333/0001-81"),
            email=Email("maria@example.com"),
            address=Address(
                street="Rua B",
                neighborhood="Bairro B",
                number="456",
                complement="Sala 1",
                zip_code="87654-321",
            ),
            notes="Updated notes",
        )

        result = repository.update(updated)
        persisted = repository.get_by_id(customer.id)

        assert result.id == customer.id
        assert persisted.name.value == "Maria Souza"
        assert persisted.whatsapp.value == "11988888888"
        assert persisted.cpf is None
        assert persisted.cnpj.value == "11222333000181"
        assert persisted.email.value == "maria@example.com"
        assert persisted.address.street == "Rua B"
        assert persisted.address.neighborhood == "Bairro B"
        assert persisted.address.number == "456"
        assert persisted.address.complement == "Sala 1"
        assert persisted.address.zip_code == "87654321"
        assert persisted.notes == "Updated notes"

    def test_update_persists_none_for_optional_fields(self, repository: CustomerRepository):
        customer = Customer(
            id=uuid.uuid4(),
            name=CustomerName("João Silva"),
            whatsapp=Whatsapp("11999999999"),
            cpf=Cpf("035.776.570-22"),
            email=Email("joao@example.com"),
            address=Address(street="Rua A", zip_code="12345-678"),
            notes="Initial notes",
        )
        repository.add(customer)

        updated = Customer(
            id=customer.id,
            name=customer.name,
            whatsapp=customer.whatsapp,
            cpf=customer.cpf,
            email=None,
            address=None,
            notes=None,
        )

        repository.update(updated)
        persisted = repository.get_by_id(customer.id)

        assert persisted.email is None
        assert persisted.address is None
        assert persisted.notes is None

    def test_update_rejects_unknown_id(self, repository: CustomerRepository):
        customer = Customer(id=uuid.uuid4(), name=CustomerName("João Silva"), whatsapp=Whatsapp("11999999999"))
        with pytest.raises(ValueError, match="does not exist"):
            repository.update(customer)

    def test_list_returns_all_ordered_by_created_at_desc(self, repository: CustomerRepository):
        c1 = Customer(id=uuid.uuid4(), name=CustomerName("Cliente Um"), whatsapp=Whatsapp("11911111111"))
        c2 = Customer(id=uuid.uuid4(), name=CustomerName("Cliente Dois"), whatsapp=Whatsapp("11922222222"))
        
        repository.add(c1)
        repository.add(c2)
        
        results = repository.list()
        assert len(results) == 2
        assert results[0].id == c2.id
        assert results[1].id == c1.id

    def test_list_applies_limit_and_offset(self, repository: CustomerRepository):
        c1 = Customer(id=uuid.uuid4(), name=CustomerName("Cliente Um"), whatsapp=Whatsapp("11911111111"))
        c2 = Customer(id=uuid.uuid4(), name=CustomerName("Cliente Dois"), whatsapp=Whatsapp("11922222222"))
        c3 = Customer(id=uuid.uuid4(), name=CustomerName("Cliente Tres"), whatsapp=Whatsapp("11933333333"))

        repository.add(c1)
        repository.add(c2)
        repository.add(c3)

        results = repository.list(limit=1, offset=1)

        assert [customer.id for customer in results] == [c2.id]

    def test_list_returns_only_active_customers(self, repository: CustomerRepository):
        active = Customer(id=uuid.uuid4(), name=CustomerName("Cliente Ativo"), whatsapp=Whatsapp("11911111111"))
        inactive = Customer(id=uuid.uuid4(), name=CustomerName("Cliente Inativo"), whatsapp=Whatsapp("11922222222"))

        repository.add(active)
        repository.add(inactive)
        repository.update(inactive.deactivate())

        results = repository.list()
        ids = [c.id for c in results]
        assert active.id in ids
        assert inactive.id not in ids

    def test_list_returns_empty_when_all_customers_are_inactive(self, repository: CustomerRepository):
        customer = Customer(id=uuid.uuid4(), name=CustomerName("Cliente Inativo"), whatsapp=Whatsapp("11911111111"))

        repository.add(customer)
        repository.update(customer.deactivate())

        results = repository.list()
        assert results == []

    def test_exists_checks(self, repository: CustomerRepository):
        customer = Customer(
            id=uuid.uuid4(), 
            name=CustomerName("João Silva"), 
            whatsapp=Whatsapp("11999999999"),
            cpf=Cpf("035.776.570-22")
        )
        repository.add(customer)
        
        assert repository.exists_by_whatsapp("11999999999") is True
        assert repository.exists_by_whatsapp("11988888888") is False
        assert repository.exists_by_cpf("03577657022") is True
        assert repository.exists_by_cpf("12345678901") is False
        assert repository.exists_by_cnpj("11222333000181") is False

    def test_exists_checks_ignore_excluded_customer(self, repository: CustomerRepository):
        first_customer = Customer(
            id=uuid.uuid4(),
            name=CustomerName("João Silva"),
            whatsapp=Whatsapp("11999999999"),
            cpf=Cpf("035.776.570-22"),
        )
        second_customer = Customer(
            id=uuid.uuid4(),
            name=CustomerName("Maria Souza"),
            whatsapp=Whatsapp("11988888888"),
            cpf=Cpf("529.982.247-25"),
        )
        first_company = Customer(
            id=uuid.uuid4(),
            name=CustomerName("Empresa Alpha"),
            whatsapp=Whatsapp("11977777777"),
            cnpj=Cnpj("11.222.333/0001-81"),
        )
        second_company = Customer(
            id=uuid.uuid4(),
            name=CustomerName("Empresa Beta"),
            whatsapp=Whatsapp("11966666666"),
            cnpj=Cnpj("04.252.011/0001-10"),
        )
        repository.add(first_customer)
        repository.add(second_customer)
        repository.add(first_company)
        repository.add(second_company)

        assert repository.exists_by_whatsapp("11999999999", exclude_id=first_customer.id) is False
        assert repository.exists_by_whatsapp("11988888888", exclude_id=first_customer.id) is True
        assert repository.exists_by_cpf("03577657022", exclude_id=first_customer.id) is False
        assert repository.exists_by_cpf("52998224725", exclude_id=first_customer.id) is True
        assert repository.exists_by_cnpj("11222333000181", exclude_id=first_company.id) is False
        assert repository.exists_by_cnpj("04252011000110", exclude_id=first_company.id) is True

class TestInMemoryRepository(CustomerRepositoryContract):
    @pytest.fixture
    def repository(self) -> CustomerRepository:
        return InMemoryCustomerRepository()

    def test_update_rejects_unknown_id(self, repository: CustomerRepository):
        customer = Customer(id=uuid.uuid4(), name=CustomerName("João Silva"), whatsapp=Whatsapp("11999999999"))
        with pytest.raises(ValueError, match="does not exist"):
            repository.update(customer)


class TestSqlAlchemyRepository(CustomerRepositoryContract):
    @pytest.fixture
    def db_session(self):
        Base.metadata.create_all(bind=engine)
        session = SessionFactory()
        try:
            yield session
        finally:
            session.close()
            Base.metadata.drop_all(bind=engine)

    @pytest.fixture
    def repository(self, db_session) -> CustomerRepository:
        return SqlAlchemyCustomerRepository(db_session)

    def test_audit_fields_behavior(self, repository: CustomerRepository, db_session):
        # 1. Criar e persistir um cliente
        customer_id = uuid.uuid4()
        customer = Customer(
            id=customer_id,
            name=CustomerName("João Audit"),
            whatsapp=Whatsapp("11999991234")
        )
        repository.add(customer)
        db_session.commit()

        # 2. Ler o CustomerModel diretamente via db_session
        model = db_session.get(CustomerModel, customer_id)
        
        # 3. Validar created_at e updated_at não nulos
        assert model.created_at is not None
        assert model.updated_at is not None
        
        # 4. Capturar valores iniciais
        initial_created_at = model.created_at
        initial_updated_at = model.updated_at
        
        # Pequeno intervalo para garantir diferença de timestamp
        time.sleep(0.1)
        
        # 5. Atualizar o cliente via repository.update()
        updated_customer = Customer(
            id=customer_id,
            name=CustomerName("João Audit Alterado"),
            whatsapp=Whatsapp("11999991234")
        )
        repository.update(updated_customer)
        db_session.commit()
        
        # 6. Recarregar o modelo
        db_session.expire(model)
        updated_model = db_session.get(CustomerModel, customer_id)
        
        # 7. Validar created_at inalterado e updated_at posterior
        assert updated_model.created_at == initial_created_at
        assert updated_model.updated_at > initial_updated_at
