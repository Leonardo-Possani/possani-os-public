from fastapi import FastAPI

from app.customers.routes import router as customers_router
from app.service_orders.routes import router as service_orders_router


app = FastAPI(title="Possani OS API")

app.include_router(customers_router, prefix="/customers", tags=["customers"])
app.include_router(
    service_orders_router,
    prefix="/service-orders",
    tags=["service-orders"],
)
