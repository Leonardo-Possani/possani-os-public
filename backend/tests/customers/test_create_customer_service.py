from uuid import UUID

import pytest

from app.customers.domain import Address, Cnpj, Customer, CustomerName, Whatsapp
from app.customers.in_memory_repository import InMemoryCustomerRepository
from app.customers.service import CustomerAlreadyExistsError, CustomerService


def test_create_customer_creates_active_customer_with_normalized_values() -> None:
    service = CustomerService(repository=InMemoryCustomerRepository())

    customer = service.create(
        name="  Maria   Clara  ",
        whatsapp="(11) 99999-1234",
        cpf="529.982.247-25",
    )

    assert isinstance(customer.id, UUID)
    assert customer.name.value == "Maria Clara"
    assert customer.whatsapp.value == "11999991234"
    assert customer.cpf is not None
    assert customer.cpf.value == "52998224725"
    assert customer.cnpj is None
    assert customer.is_active is True


def test_create_customer_rejects_duplicate_normalized_whatsapp() -> None:
    repository = InMemoryCustomerRepository()
    service = CustomerService(repository=repository)

    service.create(
        name="Maria Clara",
        whatsapp="(11) 99999-1234",
        cpf="529.982.247-25",
    )

    with pytest.raises(CustomerAlreadyExistsError):
        service.create(
            name="Ana Clara",
            whatsapp="11 99999-1234",
            cnpj="11.222.333/0001-81",
        )


def test_create_customer_rejects_duplicate_normalized_cpf() -> None:
    repository = InMemoryCustomerRepository()
    service = CustomerService(repository=repository)

    service.create(
        name="Maria Clara",
        whatsapp="(11) 99999-1234",
        cpf="529.982.247-25",
    )

    with pytest.raises(CustomerAlreadyExistsError):
        service.create(
            name="Ana Clara",
            whatsapp="11 98888-7777",
            cpf="52998224725",
        )


def test_create_customer_rejects_duplicate_normalized_cnpj() -> None:
    repository = InMemoryCustomerRepository()
    service = CustomerService(repository=repository)

    service.create(
        name="Maria Clara",
        whatsapp="(11) 99999-1234",
        cnpj="11.222.333/0001-81",
    )

    with pytest.raises(CustomerAlreadyExistsError):
        service.create(
            name="Ana Clara",
            whatsapp="11 98888-7777",
            cnpj="11222333000181",
        )


def test_create_customer_accepts_optional_fields() -> None:
    service = CustomerService(repository=InMemoryCustomerRepository())

    customer = service.create(
        name="Maria Clara",
        whatsapp="(11) 99999-1234",
        cpf="529.982.247-25",
        email="  MARIA@EXAMPLE.COM ",
        street=" Rua A ",
        neighborhood="Bairro X",
        number="123",
        complement=" Ap. 101 ",
        zip_code="12345-678",
        notes=" Some notes ",
    )

    assert customer.cpf is not None
    assert customer.cpf.value == "52998224725"
    assert customer.cnpj is None
    assert customer.email is not None
    assert customer.email.value == "maria@example.com"
    assert customer.address is not None
    assert customer.address.street == "Rua A"
    assert customer.address.neighborhood == "Bairro X"
    assert customer.address.number == "123"
    assert customer.address.complement == "Ap. 101"
    assert customer.address.zip_code == "12345678"
    assert customer.notes == "Some notes"


def test_create_customer_accepts_cnpj_without_cpf() -> None:
    service = CustomerService(repository=InMemoryCustomerRepository())

    customer = service.create(
        name="Maria Clara",
        whatsapp="(11) 99999-1234",
        cnpj="11.222.333/0001-81",
    )

    assert customer.cpf is None
    assert customer.cnpj is not None
    assert customer.cnpj.value == "11222333000181"


def test_create_customer_accepts_without_cpf_or_cnpj() -> None:
    service = CustomerService(repository=InMemoryCustomerRepository())

    customer = service.create(
        name="Maria Clara",
        whatsapp="(11) 99999-1234",
    )

    assert customer.name.value == "Maria Clara"
    assert customer.whatsapp.value == "11999991234"
    assert customer.cpf is None
    assert customer.cnpj is None


def test_create_customer_rejects_both_cpf_and_cnpj() -> None:
    service = CustomerService(repository=InMemoryCustomerRepository())

    with pytest.raises(ValueError, match="CPF and CNPJ are mutually exclusive."):
        service.create(
            name="Maria Clara",
            whatsapp="(11) 99999-1234",
            cpf="529.982.247-25",
            cnpj="11.222.333/0001-81",
        )


# --- Race condition tests ---

class _RepositoryThatFailsOnAdd(InMemoryCustomerRepository):
    """Stub: passa nos exists_by_* mas levanta ValueError no add(), simulando race condition."""

    def __init__(self, error_message: str) -> None:
        super().__init__()
        self._error_message = error_message

    def exists_by_whatsapp(self, whatsapp: str) -> bool:
        return False

    def exists_by_cpf(self, cpf: str) -> bool:
        return False

    def exists_by_cnpj(self, cnpj: str) -> bool:
        return False

    def add(self, customer: Customer) -> Customer:
        raise ValueError(self._error_message)


def test_create_raises_customer_already_exists_when_repository_add_fails_for_whatsapp() -> None:
    repository = _RepositoryThatFailsOnAdd("Customer with this WhatsApp already exists.")
    service = CustomerService(repository=repository)

    with pytest.raises(CustomerAlreadyExistsError, match="Customer with this WhatsApp already exists."):
        service.create(
            name="Maria Clara",
            whatsapp="11999991234",
            cpf="529.982.247-25",
        )


def test_create_raises_customer_already_exists_when_repository_add_fails_for_cpf() -> None:
    repository = _RepositoryThatFailsOnAdd("Customer with this CPF already exists.")
    service = CustomerService(repository=repository)

    with pytest.raises(CustomerAlreadyExistsError, match="Customer with this CPF already exists."):
        service.create(
            name="Maria Clara",
            whatsapp="11999991234",
            cpf="529.982.247-25",
        )


def test_create_raises_customer_already_exists_when_repository_add_fails_for_cnpj() -> None:
    repository = _RepositoryThatFailsOnAdd("Customer with this CNPJ already exists.")
    service = CustomerService(repository=repository)

    with pytest.raises(CustomerAlreadyExistsError, match="Customer with this CNPJ already exists."):
        service.create(
            name="Maria Clara",
            whatsapp="11999991234",
            cnpj="11.222.333/0001-81",
        )
