from datetime import datetime, timezone
import uuid
import pytest
from app.customers.domain import Customer, CustomerName, Whatsapp, Cpf, Cnpj, Email, Address
from app.customers.models import CustomerModel
from app.customers.mappers import CustomerMapper

def test_round_trip_pf_with_address():
    # Arrange
    customer_id = uuid.uuid4()
    domain_customer = Customer(
        id=customer_id,
        name=CustomerName("João da Silva"),
        whatsapp=Whatsapp("11999999999"),
        cpf=Cpf("035.776.570-22"),
        email=Email("joao@example.com"),
        address=Address(
            street="Rua das Flores",
            neighborhood="Centro",
            number="123",
            complement="Apto 1",
            zip_code="01234-567"
        ),
        notes="Cliente VIP",
        is_active=True
    )
    
    # Act
    model = CustomerMapper.to_orm(domain_customer)
    back_to_domain = CustomerMapper.to_domain(model)
    
    # Assert
    assert back_to_domain.id == domain_customer.id
    assert back_to_domain.name.value == domain_customer.name.value
    assert back_to_domain.whatsapp.value == domain_customer.whatsapp.value
    assert back_to_domain.cpf.value == domain_customer.cpf.value
    assert back_to_domain.email.value == domain_customer.email.value
    assert back_to_domain.address == domain_customer.address
    assert back_to_domain.notes == domain_customer.notes
    assert back_to_domain.is_active == domain_customer.is_active

def test_round_trip_pj_without_address():
    # Arrange
    customer_id = uuid.uuid4()
    domain_customer = Customer(
        id=customer_id,
        name=CustomerName("Empresa LTDA"),
        whatsapp=Whatsapp("11988888888"),
        cnpj=Cnpj("11.222.333/0001-81"),
        address=None,
        is_active=False
    )
    
    # Act
    model = CustomerMapper.to_orm(domain_customer)
    back_to_domain = CustomerMapper.to_domain(model)
    
    # Assert
    assert back_to_domain.id == domain_customer.id
    assert back_to_domain.name.value == domain_customer.name.value
    assert back_to_domain.whatsapp.value == domain_customer.whatsapp.value
    assert back_to_domain.cnpj.value == domain_customer.cnpj.value
    assert back_to_domain.address is None
    assert back_to_domain.is_active == domain_customer.is_active

def test_map_orm_to_domain_fields():
    # Arrange
    customer_id = uuid.uuid4()
    model = CustomerModel(
        id=customer_id,
        name="Maria Souza",
        whatsapp="11977777777",
        cpf="03577657022",
        cnpj=None,
        email="maria@example.com",
        street="Rua B",
        neighborhood="Bairro C",
        number="456",
        complement=None,
        zip_code="87654321",
        notes="Observação",
        is_active=True
    )
    
    # Act
    domain = CustomerMapper.to_domain(model)
    
    # Assert
    assert domain.id == customer_id
    assert domain.name.value == "Maria Souza"
    assert domain.whatsapp.value == "11977777777"
    assert domain.cpf.value == "03577657022"
    assert domain.cnpj is None
    assert domain.email.value == "maria@example.com"
    assert domain.address.street == "Rua B"
    assert domain.address.neighborhood == "Bairro C"
    assert domain.address.number == "456"
    assert domain.address.complement is None
    assert domain.address.zip_code == "87654321"
    assert domain.notes == "Observação"
    assert domain.is_active is True

def test_round_trip_pf_without_address():
    # Arrange
    customer_id = uuid.uuid4()
    domain_customer = Customer(
        id=customer_id,
        name=CustomerName("João da Silva"),
        whatsapp=Whatsapp("11999999999"),
        cpf=Cpf("035.776.570-22"),
        address=None,
        is_active=True
    )
    
    # Act
    model = CustomerMapper.to_orm(domain_customer)
    back_to_domain = CustomerMapper.to_domain(model)
    
    # Assert
    assert back_to_domain.id == domain_customer.id
    assert back_to_domain.address is None
    assert back_to_domain.cpf.value == domain_customer.cpf.value
    assert back_to_domain.cnpj is None

def test_round_trip_pj_with_address():
    # Arrange
    customer_id = uuid.uuid4()
    domain_customer = Customer(
        id=customer_id,
        name=CustomerName("Empresa LTDA"),
        whatsapp=Whatsapp("11988888888"),
        cnpj=Cnpj("11.222.333/0001-81"),
        address=Address(
            street="Avenida Paulista",
            neighborhood="Bela Vista",
            number="1000",
            zip_code="01310-100"
        ),
        is_active=True
    )
    
    # Act
    model = CustomerMapper.to_orm(domain_customer)
    back_to_domain = CustomerMapper.to_domain(model)
    
    # Assert
    assert back_to_domain.id == domain_customer.id
    assert back_to_domain.cnpj.value == domain_customer.cnpj.value
    assert back_to_domain.address == domain_customer.address

def test_round_trip_pf_inactive():
    # Arrange
    customer_id = uuid.uuid4()
    domain_customer = Customer(
        id=customer_id,
        name=CustomerName("João Inativo"),
        whatsapp=Whatsapp("11999999999"),
        cpf=Cpf("035.776.570-22"),
        is_active=False
    )
    
    # Act
    model = CustomerMapper.to_orm(domain_customer)
    back_to_domain = CustomerMapper.to_domain(model)
    
    # Assert
    assert back_to_domain.id == domain_customer.id
    assert back_to_domain.is_active is False

def test_round_trip_with_none_email_and_notes():
    # Arrange
    customer_id = uuid.uuid4()
    domain_customer = Customer(
        id=customer_id,
        name=CustomerName("João Sem Dados"),
        whatsapp=Whatsapp("11999999999"),
        cpf=Cpf("035.776.570-22"),
        email=None,
        notes=None,
        is_active=True
    )
    
    # Act
    model = CustomerMapper.to_orm(domain_customer)
    back_to_domain = CustomerMapper.to_domain(model)
    
    # Assert
    assert back_to_domain.id == domain_customer.id
    assert back_to_domain.email is None
    assert back_to_domain.notes is None

def test_round_trip_partial_address():
    # Arrange
    customer_id = uuid.uuid4()
    domain_customer = Customer(
        id=customer_id,
        name=CustomerName("João Endereço Parcial"),
        whatsapp=Whatsapp("11999999999"),
        cpf=Cpf("035.776.570-22"),
        address=Address(
            street="Rua A",
            zip_code="01234-567"
        ),
        is_active=True
    )
    
    # Act
    model = CustomerMapper.to_orm(domain_customer)
    back_to_domain = CustomerMapper.to_domain(model)
    
    # Assert
    assert back_to_domain.id == domain_customer.id
    assert back_to_domain.address.street == "Rua A"
    assert back_to_domain.address.zip_code == "01234567"
    assert back_to_domain.address.neighborhood is None
    assert back_to_domain.address.number is None
    assert back_to_domain.address.complement is None

def test_round_trip_with_deactivated_at():
    # Arrange
    customer_id = uuid.uuid4()
    deactivated_at = datetime.now(timezone.utc)
    domain_customer = Customer(
        id=customer_id,
        name=CustomerName("João Inativo"),
        whatsapp=Whatsapp("11999999999"),
        cpf=Cpf("035.776.570-22"),
        is_active=False,
        deactivated_at=deactivated_at
    )
    
    # Act
    model = CustomerMapper.to_orm(domain_customer)
    back_to_domain = CustomerMapper.to_domain(model)
    
    # Assert
    assert back_to_domain.id == domain_customer.id
    assert back_to_domain.is_active is False
    assert back_to_domain.deactivated_at == domain_customer.deactivated_at
    assert model.deactivated_at == domain_customer.deactivated_at

def test_customer_cpf_and_cnpj_mutually_exclusive():
    with pytest.raises(ValueError, match="CPF and CNPJ are mutually exclusive"):
        Customer(
            id=uuid.uuid4(),
            name=CustomerName("João Duas Identidades"),
            whatsapp=Whatsapp("11999999999"),
            cpf=Cpf("035.776.570-22"),
            cnpj=Cnpj("11.222.333/0001-81")
        )
