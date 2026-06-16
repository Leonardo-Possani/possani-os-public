from pydantic import BaseModel


class ServiceOrderRead(BaseModel):
    id: str
    customer_id: str
    status: str
