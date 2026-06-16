from datetime import datetime
from pydantic import BaseModel

from app.customers.domain import Address, Customer


class AddressSchema(BaseModel):
    street: str | None = None
    neighborhood: str | None = None
    number: str | None = None
    complement: str | None = None
    zip_code: str | None = None


class AddressUpdate(BaseModel):
    street: str | None = None
    neighborhood: str | None = None
    number: str | None = None
    complement: str | None = None
    zip_code: str | None = None


class CustomerCreate(BaseModel):
    name: str
    whatsapp: str
    cpf: str | None = None
    cnpj: str | None = None
    email: str | None = None
    address: AddressSchema | None = None
    notes: str | None = None


class CustomerUpdate(BaseModel):
    name: str | None = None
    whatsapp: str | None = None
    cpf: str | None = None
    cnpj: str | None = None
    email: str | None = None
    address: AddressUpdate | None = None
    notes: str | None = None


class CustomerRead(BaseModel):
    id: str
    name: str
    whatsapp: str
    cpf: str | None = None
    cnpj: str | None = None
    email: str | None = None
    address: AddressSchema | None = None
    notes: str | None = None
    is_active: bool
    deactivated_at: datetime | None = None

    @classmethod
    def from_domain(cls, customer: Customer) -> "CustomerRead":
        return cls(
            id=str(customer.id),
            name=customer.name.value,
            whatsapp=customer.whatsapp.value,
            cpf=customer.cpf.value if customer.cpf else None,
            cnpj=customer.cnpj.value if customer.cnpj else None,
            email=customer.email.value if customer.email else None,
            address=AddressSchema(
                street=customer.address.street,
                neighborhood=customer.address.neighborhood,
                number=customer.address.number,
                complement=customer.address.complement,
                zip_code=customer.address.zip_code,
            )
            if customer.address
            else None,
            notes=customer.notes,
            is_active=customer.is_active,
            deactivated_at=customer.deactivated_at,
        )
