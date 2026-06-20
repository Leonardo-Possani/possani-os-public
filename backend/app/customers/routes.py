from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.customers.interfaces import AbstractCustomerRepository
from app.dependencies import get_customer_repository
from app.customers.schemas import CustomerCreate, CustomerRead, CustomerUpdate
from app.customers.service import (
    CustomerAlreadyExistsError,
    CustomerNotFoundError,
    CustomerService,
)

router = APIRouter()


async def get_customer_service(
    repository: AbstractCustomerRepository = Depends(get_customer_repository),
) -> CustomerService:
    return CustomerService(repository=repository)


@router.post("/", response_model=CustomerRead, status_code=status.HTTP_201_CREATED)
async def create_customer(
    payload: CustomerCreate,
    service: CustomerService = Depends(get_customer_service),
) -> CustomerRead:
    try:
        customer = service.create(
            name=payload.name,
            whatsapp=payload.whatsapp,
            cpf=payload.cpf,
            cnpj=payload.cnpj,
            email=payload.email,
            street=payload.address.street if payload.address else None,
            neighborhood=payload.address.neighborhood if payload.address else None,
            number=payload.address.number if payload.address else None,
            complement=payload.address.complement if payload.address else None,
            zip_code=payload.address.zip_code if payload.address else None,
            notes=payload.notes,
        )
    except CustomerAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return CustomerRead.from_domain(customer)


@router.get("/", response_model=list[CustomerRead])
async def list_customers(
    limit: int = Query(default=100, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    service: CustomerService = Depends(get_customer_service),
) -> list[CustomerRead]:
    customers = service.list(limit=limit, offset=offset)
    return [CustomerRead.from_domain(customer) for customer in customers]


@router.get("/{id}", response_model=CustomerRead)
async def get_customer(
    id: UUID,
    service: CustomerService = Depends(get_customer_service),
) -> CustomerRead:
    customer = service.get_by_id(id)
    if customer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found.")

    return CustomerRead.from_domain(customer)


@router.put("/{id}", response_model=CustomerRead)
async def update_customer(
    id: UUID,
    payload: CustomerUpdate,
    service: CustomerService = Depends(get_customer_service),
) -> CustomerRead:
    try:
        customer = service.update(
            customer_id=id,
            **payload.model_dump(exclude_unset=True),
        )
    except CustomerNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except CustomerAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return CustomerRead.from_domain(customer)


@router.delete("/{id}", response_model=CustomerRead)
async def deactivate_customer(
    id: UUID,
    service: CustomerService = Depends(get_customer_service),
) -> CustomerRead:
    try:
        customer = service.deactivate_customer(id)
    except CustomerNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return CustomerRead.from_domain(customer)
