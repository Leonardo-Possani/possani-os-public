from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.customers.interfaces import AbstractCustomerRepository
from app.dependencies import get_customer_repository, get_service_order_repository
from app.service_orders.interfaces import AbstractServiceOrderRepository
from app.service_orders.schemas import (
    ServiceOrderCreate,
    ServiceOrderRead,
    ServiceOrderStatusUpdate,
)
from app.service_orders.service import (
    ServiceOrderCustomerNotFoundError,
    ServiceOrderNotFoundError,
    ServiceOrderService,
)

router = APIRouter()


async def get_service_order_service(
    repository: AbstractServiceOrderRepository = Depends(get_service_order_repository),
    customer_repository: AbstractCustomerRepository = Depends(get_customer_repository),
) -> ServiceOrderService:
    return ServiceOrderService(
        repository=repository,
        customer_repository=customer_repository,
    )


@router.post("/", response_model=ServiceOrderRead, status_code=status.HTTP_201_CREATED)
async def create_service_order(
    payload: ServiceOrderCreate,
    service: ServiceOrderService = Depends(get_service_order_service),
) -> ServiceOrderRead:
    try:
        service_order = service.create(
            customer_id=payload.customer_id,
            equipment_type=payload.equipment_type,
            reported_problem=payload.reported_problem,
            equipment_brand=payload.equipment_brand,
            equipment_model=payload.equipment_model,
            equipment_identification=payload.equipment_identification,
            internal_notes=payload.internal_notes,
        )
    except ServiceOrderCustomerNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return ServiceOrderRead.from_domain(service_order)


@router.get("/", response_model=list[ServiceOrderRead])
async def list_service_orders(
    customer_id: UUID | None = None,
    limit: int = Query(default=100, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    service: ServiceOrderService = Depends(get_service_order_service),
) -> list[ServiceOrderRead]:
    service_orders = service.list(
        customer_id=customer_id,
        limit=limit,
        offset=offset,
    )
    return [
        ServiceOrderRead.from_domain(service_order)
        for service_order in service_orders
    ]


@router.get("/{id}", response_model=ServiceOrderRead)
async def get_service_order(
    id: UUID,
    service: ServiceOrderService = Depends(get_service_order_service),
) -> ServiceOrderRead:
    try:
        service_order = service.get_by_id(id)
    except ServiceOrderNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return ServiceOrderRead.from_domain(service_order)


@router.patch("/{id}/status", response_model=ServiceOrderRead)
async def update_service_order_status(
    id: UUID,
    payload: ServiceOrderStatusUpdate,
    service: ServiceOrderService = Depends(get_service_order_service),
) -> ServiceOrderRead:
    try:
        service_order = service.update_status(id, payload.status)
    except ServiceOrderNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return ServiceOrderRead.from_domain(service_order)
