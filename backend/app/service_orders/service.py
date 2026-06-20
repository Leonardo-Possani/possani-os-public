from uuid import UUID, uuid4

from app.customers.interfaces import AbstractCustomerRepository
from app.service_orders.domain import ServiceOrder, ServiceOrderStatus
from app.service_orders.interfaces import AbstractServiceOrderRepository


class ServiceOrderCustomerNotFoundError(Exception):
    pass


class ServiceOrderNotFoundError(Exception):
    pass


class ServiceOrderService:
    def __init__(
        self,
        repository: AbstractServiceOrderRepository,
        customer_repository: AbstractCustomerRepository,
    ) -> None:
        self.repository = repository
        self.customer_repository = customer_repository

    def create(
        self,
        *,
        customer_id: UUID,
        equipment_type: str,
        reported_problem: str,
        equipment_brand: str | None = None,
        equipment_model: str | None = None,
        equipment_identification: str | None = None,
        internal_notes: str | None = None,
    ) -> ServiceOrder:
        customer = self.customer_repository.get_by_id(customer_id)
        if customer is None:
            raise ServiceOrderCustomerNotFoundError("Customer not found.")

        service_order = ServiceOrder(
            id=uuid4(),
            customer_id=customer_id,
            equipment_type=equipment_type,
            reported_problem=reported_problem,
            equipment_brand=equipment_brand,
            equipment_model=equipment_model,
            equipment_identification=equipment_identification,
            internal_notes=internal_notes,
        )

        return self.repository.add(service_order)

    def get_by_id(self, id: UUID) -> ServiceOrder:
        service_order = self.repository.get_by_id(id)
        if service_order is None:
            raise ServiceOrderNotFoundError("Service order not found.")

        return service_order

    def list(
        self,
        customer_id: UUID | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[ServiceOrder]:
        return self.repository.list(
            customer_id=customer_id,
            limit=limit,
            offset=offset,
        )

    def update_status(
        self,
        id: UUID,
        status: ServiceOrderStatus,
    ) -> ServiceOrder:
        service_order = self.repository.get_by_id(id)
        if service_order is None:
            raise ServiceOrderNotFoundError("Service order not found.")

        updated_service_order = service_order.change_status(status)
        return self.repository.update(updated_service_order)
