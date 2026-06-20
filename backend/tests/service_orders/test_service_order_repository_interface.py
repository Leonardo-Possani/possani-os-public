from typing import get_type_hints
from uuid import UUID

from app.service_orders.domain import ServiceOrder
from app.service_orders.interfaces import AbstractServiceOrderRepository


def test_service_order_repository_contract_defines_expected_methods() -> None:
    assert hasattr(AbstractServiceOrderRepository, "add")
    assert hasattr(AbstractServiceOrderRepository, "get_by_id")
    assert hasattr(AbstractServiceOrderRepository, "list")
    assert hasattr(AbstractServiceOrderRepository, "update")


def test_service_order_repository_contract_uses_expected_types() -> None:
    add_hints = get_type_hints(AbstractServiceOrderRepository.add)
    get_by_id_hints = get_type_hints(AbstractServiceOrderRepository.get_by_id)
    list_hints = get_type_hints(AbstractServiceOrderRepository.list)
    update_hints = get_type_hints(AbstractServiceOrderRepository.update)

    assert add_hints == {
        "service_order": ServiceOrder,
        "return": ServiceOrder,
    }
    assert get_by_id_hints == {
        "id": UUID,
        "return": ServiceOrder | None,
    }
    assert list_hints == {
        "customer_id": UUID | None,
        "limit": int | None,
        "offset": int | None,
        "return": list[ServiceOrder],
    }
    assert update_hints == {
        "service_order": ServiceOrder,
        "return": ServiceOrder,
    }


def test_service_order_repository_contract_is_runtime_checkable() -> None:
    class CompleteRepository:
        def add(self, service_order: ServiceOrder) -> ServiceOrder:
            return service_order

        def get_by_id(self, id: UUID) -> ServiceOrder | None:
            return None

        def list(
            self,
            customer_id: UUID | None = None,
            limit: int | None = None,
            offset: int | None = None,
        ) -> list[ServiceOrder]:
            return []

        def update(self, service_order: ServiceOrder) -> ServiceOrder:
            return service_order

    assert isinstance(CompleteRepository(), AbstractServiceOrderRepository)
