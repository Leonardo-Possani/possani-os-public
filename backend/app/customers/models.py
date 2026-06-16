from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, Text, UUID
from app.db import Base

class CustomerModel(Base):
    __tablename__ = "customers"

    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String(120), nullable=False)
    whatsapp = Column(String(20), nullable=False, unique=True)
    cpf = Column(String(14), nullable=True, unique=True)
    cnpj = Column(String(18), nullable=True, unique=True)
    email = Column(String(254), nullable=True)
    
    # Address mapped as individual columns
    street = Column(String(120), nullable=True)
    neighborhood = Column(String(80), nullable=True)
    number = Column(String(20), nullable=True)
    complement = Column(String(120), nullable=True)
    zip_code = Column(String(9), nullable=True)
    
    notes = Column(String(1000), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    deactivated_at = Column(DateTime(timezone=True), nullable=True, default=None)

    def __repr__(self) -> str:
        return f"<CustomerModel(id={self.id}, name='{self.name}')>"
