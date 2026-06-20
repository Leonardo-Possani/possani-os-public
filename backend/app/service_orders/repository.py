from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.service_orders.domain import ServiceOrder
from app.service_orders.interfaces import AbstractServiceOrderRepository
from app.service_orders.mappers import ServiceOrderMapper
from app.service_orders.models import ServiceOrderModel


class SqlAlchemyServiceOrderRepository(AbstractServiceOrderRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, service_order: ServiceOrder) -> ServiceOrder:
        if self.get_by_id(service_order.id) is not None:
            raise ValueError("Service order with this ID already exists.")

        model = ServiceOrderMapper.to_orm(service_order)
        self.session.add(model)
        self.session.flush()
        return service_order

    def get_by_id(self, id: UUID) -> ServiceOrder | None:
        model = self.session.get(ServiceOrderModel, id)
        if model is None:
            return None

        return ServiceOrderMapper.to_domain(model)

    def list(
        self,
        customer_id: UUID | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[ServiceOrder]:
        stmt = select(ServiceOrderModel).order_by(ServiceOrderModel.created_at.desc())
        if customer_id is not None:
            stmt = stmt.where(ServiceOrderModel.customer_id == customer_id)
        if limit is not None:
            stmt = stmt.limit(limit)
        if offset is not None:
            stmt = stmt.offset(offset)

        models = self.session.execute(stmt).scalars().all()
        return [ServiceOrderMapper.to_domain(model) for model in models]

    def update(self, service_order: ServiceOrder) -> ServiceOrder:
        model = self.session.get(ServiceOrderModel, service_order.id)
        if model is None:
            raise ValueError("Service order with this ID does not exist.")

        updated_model = ServiceOrderMapper.to_orm(service_order)
        for attr in [
            "customer_id",
            "equipment_type",
            "reported_problem",
            "equipment_brand",
            "equipment_model",
            "equipment_identification",
            "internal_notes",
            "status",
            "created_at",
            "updated_at",
            "closed_at",
        ]:
            setattr(model, attr, getattr(updated_model, attr))

        self.session.flush()
        return ServiceOrderMapper.to_domain(model)
