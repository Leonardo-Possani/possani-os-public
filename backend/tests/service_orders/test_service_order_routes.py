from datetime import datetime, timezone
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.customers.domain import Customer, CustomerName, Cpf, Whatsapp
from app.customers.in_memory_repository import InMemoryCustomerRepository
from app.dependencies import get_customer_repository, get_service_order_repository
from app.main import app
from app.service_orders.domain import ServiceOrder, ServiceOrderStatus
from app.service_orders.in_memory_repository import InMemoryServiceOrderRepository


def make_customer(**overrides: object) -> Customer:
    data = {
        "id": uuid4(),
        "name": CustomerName("Maria Clara"),
        "whatsapp": Whatsapp("11999991234"),
        "cpf": Cpf("529.982.247-25"),
    }
    data.update(overrides)
    return Customer(**data)


def make_service_order(**overrides: object) -> ServiceOrder:
    data = {
        "id": uuid4(),
        "customer_id": uuid4(),
        "equipment_type": "Notebook",
        "reported_problem": "Does not turn on",
    }
    data.update(overrides)
    return ServiceOrder(**data)


@pytest.fixture
def repositories() -> tuple[InMemoryCustomerRepository, InMemoryServiceOrderRepository]:
    customer_repository = InMemoryCustomerRepository()
    service_order_repository = InMemoryServiceOrderRepository()

    async def override_customer_repository() -> InMemoryCustomerRepository:
        return customer_repository

    async def override_service_order_repository() -> InMemoryServiceOrderRepository:
        return service_order_repository

    app.dependency_overrides[get_customer_repository] = override_customer_repository
    app.dependency_overrides[get_service_order_repository] = (
        override_service_order_repository
    )
    yield customer_repository, service_order_repository
    app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_create_service_order_returns_created_service_order(
    repositories: tuple[InMemoryCustomerRepository, InMemoryServiceOrderRepository],
) -> None:
    customer_repository, _ = repositories
    customer = customer_repository.add(make_customer())

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/service-orders/",
            json={
                "customer_id": str(customer.id),
                "equipment_type": "  Notebook  ",
                "reported_problem": "  Does not turn on  ",
                "equipment_brand": "  Dell  ",
                "equipment_model": "  Latitude 5420  ",
                "equipment_identification": "  SN-123  ",
                "internal_notes": "  Priority customer  ",
            },
        )

    assert response.status_code == 201
    body = response.json()
    assert body["id"]
    assert body["customer_id"] == str(customer.id)
    assert body["equipment_type"] == "Notebook"
    assert body["reported_problem"] == "Does not turn on"
    assert body["equipment_brand"] == "Dell"
    assert body["equipment_model"] == "Latitude 5420"
    assert body["equipment_identification"] == "SN-123"
    assert body["internal_notes"] == "Priority customer"
    assert body["status"] == "opened"
    assert body["created_at"]
    assert body["updated_at"]
    assert body["closed_at"] is None


@pytest.mark.anyio
async def test_create_service_order_returns_not_found_for_unknown_customer(
    repositories: tuple[InMemoryCustomerRepository, InMemoryServiceOrderRepository],
) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/service-orders/",
            json={
                "customer_id": str(uuid4()),
                "equipment_type": "Notebook",
                "reported_problem": "Does not turn on",
            },
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Customer not found."


@pytest.mark.anyio
async def test_list_service_orders_returns_all_and_filters_by_customer_id(
    repositories: tuple[InMemoryCustomerRepository, InMemoryServiceOrderRepository],
) -> None:
    _, service_order_repository = repositories
    target_customer_id = uuid4()
    other_customer_id = uuid4()
    first = service_order_repository.add(
        make_service_order(
            customer_id=target_customer_id,
            created_at=datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc),
        ),
    )
    service_order_repository.add(make_service_order(customer_id=other_customer_id))
    second = service_order_repository.add(
        make_service_order(
            customer_id=target_customer_id,
            created_at=datetime(2026, 1, 2, 10, 0, tzinfo=timezone.utc),
        ),
    )

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        all_response = await client.get("/service-orders/")
        filtered_response = await client.get(
            f"/service-orders/?customer_id={target_customer_id}",
        )

    assert all_response.status_code == 200
    assert len(all_response.json()) == 3
    assert filtered_response.status_code == 200
    assert [item["id"] for item in filtered_response.json()] == [
        str(second.id),
        str(first.id),
    ]


@pytest.mark.anyio
async def test_list_service_orders_applies_limit_and_offset(
    repositories: tuple[InMemoryCustomerRepository, InMemoryServiceOrderRepository],
) -> None:
    _, service_order_repository = repositories
    oldest = service_order_repository.add(
        make_service_order(created_at=datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc)),
    )
    middle = service_order_repository.add(
        make_service_order(created_at=datetime(2026, 1, 2, 10, 0, tzinfo=timezone.utc)),
    )
    service_order_repository.add(
        make_service_order(created_at=datetime(2026, 1, 3, 10, 0, tzinfo=timezone.utc)),
    )

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.get("/service-orders/?limit=2&offset=1")

    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [
        str(middle.id),
        str(oldest.id),
    ]


@pytest.mark.anyio
async def test_list_service_orders_applies_pagination_with_customer_filter(
    repositories: tuple[InMemoryCustomerRepository, InMemoryServiceOrderRepository],
) -> None:
    _, service_order_repository = repositories
    target_customer_id = uuid4()
    other_customer_id = uuid4()
    service_order_repository.add(
        make_service_order(
            customer_id=target_customer_id,
            created_at=datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc),
        ),
    )
    expected = service_order_repository.add(
        make_service_order(
            customer_id=target_customer_id,
            created_at=datetime(2026, 1, 2, 10, 0, tzinfo=timezone.utc),
        ),
    )
    service_order_repository.add(make_service_order(customer_id=other_customer_id))
    service_order_repository.add(
        make_service_order(
            customer_id=target_customer_id,
            created_at=datetime(2026, 1, 3, 10, 0, tzinfo=timezone.utc),
        ),
    )

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.get(
            f"/service-orders/?customer_id={target_customer_id}&limit=1&offset=1",
        )

    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [str(expected.id)]


@pytest.mark.anyio
@pytest.mark.parametrize("query_string", ["limit=0", "limit=101", "offset=-1"])
async def test_list_service_orders_rejects_invalid_pagination_params(
    repositories: tuple[InMemoryCustomerRepository, InMemoryServiceOrderRepository],
    query_string: str,
) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.get(f"/service-orders/?{query_string}")

    assert response.status_code == 422


@pytest.mark.anyio
async def test_get_service_order_returns_existing_service_order(
    repositories: tuple[InMemoryCustomerRepository, InMemoryServiceOrderRepository],
) -> None:
    _, service_order_repository = repositories
    service_order = service_order_repository.add(make_service_order())

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.get(f"/service-orders/{service_order.id}")

    assert response.status_code == 200
    assert response.json()["id"] == str(service_order.id)


@pytest.mark.anyio
async def test_get_service_order_returns_not_found_for_unknown_id(
    repositories: tuple[InMemoryCustomerRepository, InMemoryServiceOrderRepository],
) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.get(f"/service-orders/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Service order not found."


@pytest.mark.anyio
async def test_update_service_order_status_returns_updated_service_order(
    repositories: tuple[InMemoryCustomerRepository, InMemoryServiceOrderRepository],
) -> None:
    _, service_order_repository = repositories
    service_order = service_order_repository.add(make_service_order())

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.patch(
            f"/service-orders/{service_order.id}/status",
            json={"status": "in_progress"},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == str(service_order.id)
    assert body["status"] == "in_progress"
    assert body["closed_at"] is None


@pytest.mark.anyio
async def test_update_service_order_status_returns_bad_request_for_invalid_transition(
    repositories: tuple[InMemoryCustomerRepository, InMemoryServiceOrderRepository],
) -> None:
    _, service_order_repository = repositories
    service_order = service_order_repository.add(make_service_order())

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.patch(
            f"/service-orders/{service_order.id}/status",
            json={"status": "delivered"},
        )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid service order status transition."


@pytest.mark.anyio
async def test_update_service_order_status_returns_bad_request_for_terminal_order(
    repositories: tuple[InMemoryCustomerRepository, InMemoryServiceOrderRepository],
) -> None:
    _, service_order_repository = repositories
    service_order = service_order_repository.add(
        make_service_order(status=ServiceOrderStatus.CANCELLED),
    )

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.patch(
            f"/service-orders/{service_order.id}/status",
            json={"status": "in_progress"},
        )

    assert response.status_code == 400
    assert response.json()["detail"] == "Terminal service order cannot change status."


@pytest.mark.anyio
async def test_update_service_order_status_returns_not_found_for_unknown_id(
    repositories: tuple[InMemoryCustomerRepository, InMemoryServiceOrderRepository],
) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.patch(
            f"/service-orders/{uuid4()}/status",
            json={"status": "in_progress"},
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Service order not found."
