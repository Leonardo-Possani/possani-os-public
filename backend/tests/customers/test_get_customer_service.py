from uuid import uuid4

import pytest

from app.customers.domain import Customer, CustomerName, Whatsapp
from app.customers.in_memory_repository import InMemoryCustomerRepository
from app.customers.service import CustomerNotFoundError, CustomerService


def test_get_customer_service_returns_customer_by_id() -> None:
    repository = InMemoryCustomerRepository()
    service = CustomerService(repository=repository)
    customer = Customer(
        id=uuid4(),
        name=CustomerName("Maria Clara"),
        whatsapp=Whatsapp("11999991234"),
    )

    repository.add(customer)

    assert service.get_by_id(customer.id) == customer


def test_get_customer_service_returns_none_for_unknown_id() -> None:
    service = CustomerService(repository=InMemoryCustomerRepository())

    assert service.get_by_id(uuid4()) is None


def test_get_customer_service_returns_inactive_customer_by_id() -> None:
    repository = InMemoryCustomerRepository()
    service = CustomerService(repository=repository)
    customer = Customer(
        id=uuid4(),
        name=CustomerName("Maria Clara"),
        whatsapp=Whatsapp("11999991234"),
    ).deactivate()

    repository.add(customer)

    result = service.get_by_id(customer.id)

    assert result == customer
    assert result is not None
    assert result.is_active is False


def test_get_customer_service_returns_inactive_customer_after_soft_delete() -> None:
    repository = InMemoryCustomerRepository()
    service = CustomerService(repository=repository)
    customer = Customer(
        id=uuid4(),
        name=CustomerName("Maria Clara"),
        whatsapp=Whatsapp("11999991234"),
    )
    repository.add(customer)

    service.deactivate_customer(customer.id)

    result = service.get_by_id(customer.id)

    assert result is not None
    assert result.id == customer.id
    assert result.is_active is False


def test_deactivate_customer_persists_deactivated_state_through_repository_contract() -> None:
    repository = InMemoryCustomerRepository()
    service = CustomerService(repository=repository)
    customer = Customer(
        id=uuid4(),
        name=CustomerName("Maria Clara"),
        whatsapp=Whatsapp("11999991234"),
    )
    repository.add(customer)

    result = service.deactivate_customer(customer.id)

    assert result.is_active is False
    assert result.deactivated_at is not None
    assert repository.get_by_id(customer.id) == result
    assert repository.get_by_id(customer.id) is not None
    assert repository.get_by_id(customer.id).is_active is False
    assert repository.get_by_id(customer.id).deactivated_at is not None


def test_deactivate_customer_uses_repository_contract_without_internal_items() -> None:
    customer = Customer(
        id=uuid4(),
        name=CustomerName("Maria Clara"),
        whatsapp=Whatsapp("11999991234"),
    )

    class RepositoryWithoutItems:
        def __init__(self, stored_customer: Customer) -> None:
            self._customer = stored_customer
            self.updated_customer: Customer | None = None

        def exists_by_whatsapp(self, whatsapp: str) -> bool:
            return False

        def exists_by_cpf(self, cpf: str) -> bool:
            return False

        def exists_by_cnpj(self, cnpj: str) -> bool:
            return False

        def get_by_id(self, id):
            if id == self._customer.id:
                return self._customer
            return None

        def add(self, customer: Customer) -> Customer:
            self._customer = customer
            return customer

        def update(self, customer: Customer) -> Customer:
            self.updated_customer = customer
            self._customer = customer
            return customer

        def list(
            self,
            limit: int | None = None,
            offset: int | None = None,
        ) -> list[Customer]:
            return [self._customer]

    repository = RepositoryWithoutItems(customer)
    service = CustomerService(repository=repository)

    result = service.deactivate_customer(customer.id)

    assert repository.updated_customer == result
    assert result.is_active is False


def test_deactivate_customer_raises_for_unknown_customer() -> None:
    service = CustomerService(repository=InMemoryCustomerRepository())

    with pytest.raises(CustomerNotFoundError, match="Customer not found."):
        service.deactivate_customer(uuid4())
