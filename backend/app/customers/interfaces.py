from abc import abstractmethod
from typing import Protocol, runtime_checkable
from uuid import UUID
from app.customers.domain import Customer

@runtime_checkable
class AbstractCustomerRepository(Protocol):
    def exists_by_whatsapp(self, whatsapp: str, exclude_id: UUID | None = None) -> bool:
        ...

    def exists_by_cpf(self, cpf: str, exclude_id: UUID | None = None) -> bool:
        ...

    def exists_by_cnpj(self, cnpj: str, exclude_id: UUID | None = None) -> bool:
        ...

    def get_by_id(self, id: UUID) -> Customer | None:
        ...

    def add(self, customer: Customer) -> Customer:
        ...

    @abstractmethod
    def update(self, customer: Customer) -> Customer:
        ...

    def list(self) -> list[Customer]:
        ...
