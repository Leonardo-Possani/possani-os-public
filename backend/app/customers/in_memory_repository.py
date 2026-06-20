from uuid import UUID
from app.customers.domain import Customer
from app.customers.interfaces import AbstractCustomerRepository

class InMemoryCustomerRepository(AbstractCustomerRepository):
    def __init__(self) -> None:
        self.items: dict[UUID, Customer] = {}

    def exists_by_whatsapp(self, whatsapp: str, exclude_id: UUID | None = None) -> bool:
        return any(
            customer.id != exclude_id and customer.whatsapp.value == whatsapp
            for customer in self.items.values()
        )

    def exists_by_cpf(self, cpf: str, exclude_id: UUID | None = None) -> bool:
        return any(
            customer.id != exclude_id
            and customer.cpf is not None
            and customer.cpf.value == cpf
            for customer in self.items.values()
        )

    def exists_by_cnpj(self, cnpj: str, exclude_id: UUID | None = None) -> bool:
        return any(
            customer.id != exclude_id
            and customer.cnpj is not None
            and customer.cnpj.value == cnpj
            for customer in self.items.values()
        )

    def add(self, customer: Customer) -> Customer:
        if customer.id in self.items:
            raise ValueError("Customer with this ID already exists.")
        if self.exists_by_whatsapp(customer.whatsapp.value):
            raise ValueError("Customer with this WhatsApp already exists.")
        if customer.cpf and self.exists_by_cpf(customer.cpf.value):
            raise ValueError("Customer with this CPF already exists.")
        if customer.cnpj and self.exists_by_cnpj(customer.cnpj.value):
            raise ValueError("Customer with this CNPJ already exists.")

        self.items[customer.id] = customer
        return customer

    def update(self, customer: Customer) -> Customer:
        if customer.id not in self.items:
            raise ValueError("Customer with this ID does not exist.")

        self.items[customer.id] = customer
        return customer

    def get_by_id(self, id: UUID) -> Customer | None:
        return self.items.get(id)

    def list(self, limit: int | None = None, offset: int | None = None) -> list[Customer]:
        # Return only active customers in reverse insertion order to simulate created_at DESC
        customers = [c for c in reversed(list(self.items.values())) if c.is_active]
        start = offset or 0
        if limit is None:
            return customers[start:]
        return customers[start:start + limit]
