from typing import Protocol, runtime_checkable
from uuid import UUID

from app.service_orders.domain import ServiceOrder


@runtime_checkable
class AbstractServiceOrderRepository(Protocol):
    def add(self, service_order: ServiceOrder) -> ServiceOrder:
        ...

    def get_by_id(self, id: UUID) -> ServiceOrder | None:
        ...

    def list(
        self,
        customer_id: UUID | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[ServiceOrder]:
        ...

    def update(self, service_order: ServiceOrder) -> ServiceOrder:
        ...
