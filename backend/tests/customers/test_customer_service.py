from uuid import UUID, uuid4

import pytest

from app.customers.in_memory_repository import InMemoryCustomerRepository
from app.customers.service import (
    CustomerAlreadyExistsError,
    CustomerNotFoundError,
    CustomerService,
)


class RecordingCustomerRepository(InMemoryCustomerRepository):
    def __init__(self) -> None:
        super().__init__()
        self.whatsapp_exclude_id: UUID | None = None
        self.cpf_exclude_id: UUID | None = None
        self.cnpj_exclude_id: UUID | None = None

    def exists_by_whatsapp(self, whatsapp: str, exclude_id: UUID | None = None) -> bool:
        self.whatsapp_exclude_id = exclude_id
        return super().exists_by_whatsapp(whatsapp, exclude_id=exclude_id)

    def exists_by_cpf(self, cpf: str, exclude_id: UUID | None = None) -> bool:
        self.cpf_exclude_id = exclude_id
        return super().exists_by_cpf(cpf, exclude_id=exclude_id)

    def exists_by_cnpj(self, cnpj: str, exclude_id: UUID | None = None) -> bool:
        self.cnpj_exclude_id = exclude_id
        return super().exists_by_cnpj(cnpj, exclude_id=exclude_id)


class RepositoryThatFailsOnUpdate(InMemoryCustomerRepository):
    def update(self, customer):
        raise ValueError("Customer with this WhatsApp already exists.")


def test_update_partially_updates_customer() -> None:
    service = CustomerService(repository=InMemoryCustomerRepository())
    customer = service.create(
        name="Maria Clara",
        whatsapp="11999991234",
        cpf="529.982.247-25",
        email="maria@example.com",
        street="Rua A",
        neighborhood="Bairro X",
        number="123",
        zip_code="12345-678",
        notes="Initial notes",
    )

    updated = service.update(
        customer.id,
        name="Maria Silva",
        address={"street": "Rua B", "zip_code": None},
        notes=None,
    )

    assert updated.id == customer.id
    assert updated.name.value == "Maria Silva"
    assert updated.whatsapp.value == "11999991234"
    assert updated.email.value == "maria@example.com"
    assert updated.address.street == "Rua B"
    assert updated.address.neighborhood == "Bairro X"
    assert updated.address.number == "123"
    assert updated.address.zip_code == "12345678"
    assert updated.notes is None


def test_update_completely_updates_customer() -> None:
    service = CustomerService(repository=InMemoryCustomerRepository())
    customer = service.create(
        name="Maria Clara",
        whatsapp="11999991234",
        cpf="529.982.247-25",
    )

    updated = service.update(
        customer.id,
        name="Ana Clara",
        whatsapp="11988887777",
        cpf=None,
        cnpj="11.222.333/0001-81",
        email="ana@example.com",
        address={
            "street": "Rua B",
            "neighborhood": "Bairro Y",
            "number": "456",
            "complement": "Sala 2",
            "zip_code": "87654-321",
        },
        notes="Updated notes",
    )

    assert updated.name.value == "Ana Clara"
    assert updated.whatsapp.value == "11988887777"
    assert updated.cpf is None
    assert updated.cnpj.value == "11222333000181"
    assert updated.email.value == "ana@example.com"
    assert updated.address.street == "Rua B"
    assert updated.address.neighborhood == "Bairro Y"
    assert updated.address.number == "456"
    assert updated.address.complement == "Sala 2"
    assert updated.address.zip_code == "87654321"
    assert updated.notes == "Updated notes"


def test_update_raises_not_found_for_unknown_customer() -> None:
    service = CustomerService(repository=InMemoryCustomerRepository())

    with pytest.raises(CustomerNotFoundError, match="Customer not found."):
        service.update(uuid4(), name="Maria Silva")


@pytest.mark.parametrize(
    ("field_name", "first_document", "second_document", "conflicting_value", "message"),
    [
        (
            "whatsapp",
            {"cpf": "529.982.247-25"},
            {"cpf": "111.444.777-35"},
            "11988887777",
            "Customer with this WhatsApp already exists.",
        ),
        (
            "cpf",
            {"cpf": "529.982.247-25"},
            {"cpf": "111.444.777-35"},
            "111.444.777-35",
            "Customer with this CPF already exists.",
        ),
        (
            "cnpj",
            {"cnpj": "11.222.333/0001-81"},
            {"cnpj": "04.252.011/0001-10"},
            "04.252.011/0001-10",
            "Customer with this CNPJ already exists.",
        ),
    ],
)
def test_update_rejects_unique_field_used_by_another_customer(
    field_name: str,
    first_document: dict[str, str],
    second_document: dict[str, str],
    conflicting_value: str,
    message: str,
) -> None:
    repository = InMemoryCustomerRepository()
    service = CustomerService(repository=repository)
    first_customer = service.create(
        name="Maria Clara",
        whatsapp="11999991234",
        **first_document,
    )
    service.create(
        name="Ana Clara",
        whatsapp="11988887777",
        **second_document,
    )

    with pytest.raises(CustomerAlreadyExistsError, match=message):
        service.update(first_customer.id, **{field_name: conflicting_value})


def test_update_passes_customer_id_as_exclude_id_to_unique_checks() -> None:
    repository = RecordingCustomerRepository()
    service = CustomerService(repository=repository)
    customer = service.create(
        name="Maria Clara",
        whatsapp="11999991234",
        cpf="529.982.247-25",
    )

    service.update(
        customer.id,
        whatsapp="11988887777",
        cpf=None,
        cnpj="11.222.333/0001-81",
    )

    assert repository.whatsapp_exclude_id == customer.id
    assert repository.cnpj_exclude_id == customer.id


def test_update_raises_value_error_for_invalid_value_object_data() -> None:
    service = CustomerService(repository=InMemoryCustomerRepository())
    customer = service.create(
        name="Maria Clara",
        whatsapp="11999991234",
        cpf="529.982.247-25",
    )

    with pytest.raises(ValueError, match="Email is invalid."):
        service.update(customer.id, email="invalid-email")


def test_update_can_clear_optional_fields() -> None:
    service = CustomerService(repository=InMemoryCustomerRepository())
    customer = service.create(
        name="Maria Clara",
        whatsapp="11999991234",
        cpf="529.982.247-25",
        email="maria@example.com",
        street="Rua A",
        notes="Some notes",
    )

    updated = service.update(
        customer.id,
        email=None,
        address=None,
        notes=None,
    )

    assert updated.email is None
    assert updated.address is None
    assert updated.notes is None


def test_update_rejects_customer_with_cpf_and_cnpj() -> None:
    service = CustomerService(repository=InMemoryCustomerRepository())
    customer = service.create(
        name="Maria Clara",
        whatsapp="11999991234",
        cpf="529.982.247-25",
    )

    with pytest.raises(ValueError, match="CPF and CNPJ are mutually exclusive"):
        service.update(customer.id, cnpj="11.222.333/0001-81")


def test_update_translates_repository_unique_conflict_to_customer_already_exists() -> None:
    repository = RepositoryThatFailsOnUpdate()
    service = CustomerService(repository=repository)
    customer = service.create(
        name="Maria Clara",
        whatsapp="11999991234",
        cpf="529.982.247-25",
    )

    with pytest.raises(CustomerAlreadyExistsError, match="Customer with this WhatsApp already exists."):
        service.update(customer.id, name="Maria Silva")
