from fastapi import FastAPI

from app.customers.routes import router as customers_router


app = FastAPI(title="Possani OS API")

app.include_router(customers_router, prefix="/customers", tags=["customers"])
