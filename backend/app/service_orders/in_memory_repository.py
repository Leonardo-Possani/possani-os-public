from uuid import UUID

from app.service_orders.domain import ServiceOrder
from app.service_orders.interfaces import AbstractServiceOrderRepository


class InMemoryServiceOrderRepository(AbstractServiceOrderRepository):
    def __init__(self) -> None:
        self.items: dict[UUID, ServiceOrder] = {}

    def add(self, service_order: ServiceOrder) -> ServiceOrder:
        if service_order.id in self.items:
            raise ValueError("Service order with this ID already exists.")

        self.items[service_order.id] = service_order
        return service_order

    def get_by_id(self, id: UUID) -> ServiceOrder | None:
        return self.items.get(id)

    def list(
        self,
        customer_id: UUID | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[ServiceOrder]:
        service_orders = sorted(
            self.items.values(),
            key=lambda service_order: service_order.created_at,
            reverse=True,
        )
        if customer_id is not None:
            service_orders = [
                service_order
                for service_order in service_orders
                if service_order.customer_id == customer_id
            ]

        start = offset or 0
        if limit is None:
            return service_orders[start:]
        return service_orders[start:start + limit]

    def update(self, service_order: ServiceOrder) -> ServiceOrder:
        if service_order.id not in self.items:
            raise ValueError("Service order with this ID does not exist.")

        self.items[service_order.id] = service_order
        return service_order
