from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class ServiceOrder:
    id: UUID
    customer_id: UUID
    status: str
