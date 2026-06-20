from uuid import UUID, uuid4

import pytest

from app.customers.domain import Customer, CustomerName, Cpf, Whatsapp
from app.customers.in_memory_repository import InMemoryCustomerRepository
from app.service_orders.domain import ServiceOrder, ServiceOrderStatus
from app.service_orders.in_memory_repository import InMemoryServiceOrderRepository
from app.service_orders.service import (
    ServiceOrderCustomerNotFoundError,
    ServiceOrderService,
)


def make_customer() -> Customer:
    return Customer(
        id=uuid4(),
        name=CustomerName("Maria Clara"),
        whatsapp=Whatsapp("11999991234"),
        cpf=Cpf("529.982.247-25"),
    )


def test_create_service_order_with_valid_data() -> None:
    customer_repository = InMemoryCustomerRepository()
    service_order_repository = InMemoryServiceOrderRepository()
    customer = customer_repository.add(make_customer())
    service = ServiceOrderService(
        repository=service_order_repository,
        customer_repository=customer_repository,
    )

    service_order = service.create(
        customer_id=customer.id,
        equipment_type="  Notebook  ",
        reported_problem="  Does not turn on  ",
        equipment_brand="  Dell  ",
        equipment_model="  Inspiron 15  ",
        equipment_identification="  SN-123  ",
        internal_notes="  Priority customer  ",
    )

    assert isinstance(service_order, ServiceOrder)
    assert isinstance(service_order.id, UUID)
    assert service_order.customer_id == customer.id
    assert service_order.equipment_type == "Notebook"
    assert service_order.reported_problem == "Does not turn on"
    assert service_order.equipment_brand == "Dell"
    assert service_order.equipment_model == "Inspiron 15"
    assert service_order.equipment_identification == "SN-123"
    assert service_order.internal_notes == "Priority customer"
    assert service_order.status == ServiceOrderStatus.OPENED
    assert service_order.closed_at is None
    assert service_order_repository.get_by_id(service_order.id) == service_order


def test_create_service_order_raises_error_when_customer_not_found() -> None:
    service_order_repository = InMemoryServiceOrderRepository()
    service = ServiceOrderService(
        repository=service_order_repository,
        customer_repository=InMemoryCustomerRepository(),
    )

    with pytest.raises(ServiceOrderCustomerNotFoundError, match="Customer not found."):
        service.create(
            customer_id=uuid4(),
            equipment_type="Notebook",
            reported_problem="Does not turn on",
        )

    assert service_order_repository.list() == []


def test_create_service_order_raises_validation_error_without_persisting() -> None:
    customer_repository = InMemoryCustomerRepository()
    service_order_repository = InMemoryServiceOrderRepository()
    customer = customer_repository.add(make_customer())
    service = ServiceOrderService(
        repository=service_order_repository,
        customer_repository=customer_repository,
    )

    with pytest.raises(ValueError, match="Reported problem cannot be empty."):
        service.create(
            customer_id=customer.id,
            equipment_type="Notebook",
            reported_problem="  ",
        )

    assert service_order_repository.list() == []


def test_create_service_order_rejects_massive_text_payload_without_persisting() -> None:
    customer_repository = InMemoryCustomerRepository()
    service_order_repository = InMemoryServiceOrderRepository()
    customer = customer_repository.add(make_customer())
    service = ServiceOrderService(
        repository=service_order_repository,
        customer_repository=customer_repository,
    )

    with pytest.raises(ValueError, match="Internal notes cannot exceed 2000 characters."):
        service.create(
            customer_id=customer.id,
            equipment_type="Notebook",
            reported_problem="Does not turn on",
            equipment_brand="Dell",
            equipment_model="Inspiron 15",
            equipment_identification="SN-123",
            internal_notes="a" * 10_000,
        )

    assert service_order_repository.list() == []
