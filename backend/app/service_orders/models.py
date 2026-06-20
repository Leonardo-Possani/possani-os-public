from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Index, String, UUID

from app.db import Base
from app.service_orders.domain import ServiceOrderStatus


class ServiceOrderModel(Base):
    __tablename__ = "service_orders"
    __table_args__ = (
        Index("ix_service_orders_customer_id", "customer_id"),
        Index("ix_service_orders_status", "status"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True)
    customer_id = Column(
        UUID(as_uuid=True),
        ForeignKey("customers.id"),
        nullable=False,
    )
    equipment_type = Column(String(500), nullable=False)
    reported_problem = Column(String(2000), nullable=False)
    equipment_brand = Column(String(255), nullable=True)
    equipment_model = Column(String(255), nullable=True)
    equipment_identification = Column(String(255), nullable=True)
    internal_notes = Column(String(2000), nullable=True)
    status = Column(
        String(32),
        nullable=False,
        default=ServiceOrderStatus.OPENED.value,
    )
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    closed_at = Column(DateTime(timezone=True), nullable=True, default=None)

    def __repr__(self) -> str:
        return f"<ServiceOrderModel(id={self.id}, status='{self.status}')>"
