from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select, exc

from app.customers.domain import Customer
from app.customers.models import CustomerModel
from app.customers.mappers import CustomerMapper
from app.customers.interfaces import AbstractCustomerRepository


class SqlAlchemyCustomerRepository(AbstractCustomerRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def exists_by_whatsapp(self, whatsapp: str, exclude_id: UUID | None = None) -> bool:
        stmt = select(CustomerModel).where(CustomerModel.whatsapp == whatsapp)
        if exclude_id is not None:
            stmt = stmt.where(CustomerModel.id != exclude_id)
        return self.session.execute(stmt).scalar_one_or_none() is not None

    def exists_by_cpf(self, cpf: str, exclude_id: UUID | None = None) -> bool:
        stmt = select(CustomerModel).where(CustomerModel.cpf == cpf)
        if exclude_id is not None:
            stmt = stmt.where(CustomerModel.id != exclude_id)
        return self.session.execute(stmt).scalar_one_or_none() is not None

    def exists_by_cnpj(self, cnpj: str, exclude_id: UUID | None = None) -> bool:
        stmt = select(CustomerModel).where(CustomerModel.cnpj == cnpj)
        if exclude_id is not None:
            stmt = stmt.where(CustomerModel.id != exclude_id)
        return self.session.execute(stmt).scalar_one_or_none() is not None

    def add(self, customer: Customer) -> Customer:
        if self.get_by_id(customer.id):
            raise ValueError("Customer with this ID already exists.")
        
        model = CustomerMapper.to_orm(customer)
        self.session.add(model)
        try:
            self.session.flush()
        except exc.IntegrityError as e:
            self.session.rollback()
            error_msg = str(e.orig).lower()
            if "whatsapp" in error_msg:
                raise ValueError("Customer with this WhatsApp already exists.")
            if "cpf" in error_msg:
                raise ValueError("Customer with this CPF already exists.")
            if "cnpj" in error_msg:
                raise ValueError("Customer with this CNPJ already exists.")
            raise

        return customer

    def update(self, customer: Customer) -> Customer:
        model = self.session.get(CustomerModel, customer.id)
        if not model:
            raise ValueError("Customer with this ID does not exist.")
        
        updated_model = CustomerMapper.to_orm(customer)
        for attr in [
            "name", "whatsapp", "cpf", "cnpj", "email", 
            "street", "neighborhood", "number", "complement", "zip_code", 
            "notes", "is_active", "deactivated_at"
        ]:
            setattr(model, attr, getattr(updated_model, attr))
        
        try:
            self.session.flush()
        except exc.IntegrityError as e:
            self.session.rollback()
            error_msg = str(e.orig).lower()
            if "whatsapp" in error_msg:
                raise ValueError("Customer with this WhatsApp already exists.")
            if "cpf" in error_msg:
                raise ValueError("Customer with this CPF already exists.")
            if "cnpj" in error_msg:
                raise ValueError("Customer with this CNPJ already exists.")
            raise

        self.session.refresh(model)
        return CustomerMapper.to_domain(model)

    def get_by_id(self, id: UUID) -> Customer | None:
        model = self.session.get(CustomerModel, id)
        if not model:
            return None
        return CustomerMapper.to_domain(model)

    def list(self, limit: int | None = None, offset: int | None = None) -> list[Customer]:
        stmt = (
            select(CustomerModel)
            .where(CustomerModel.is_active == True)
            .order_by(CustomerModel.created_at.desc())
        )
        if limit is not None:
            stmt = stmt.limit(limit)
        if offset is not None:
            stmt = stmt.offset(offset)

        models = self.session.execute(stmt).scalars().all()
        return [CustomerMapper.to_domain(m) for m in models]
