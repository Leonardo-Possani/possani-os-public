from datetime import datetime, timezone
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.main import app


pytestmark = pytest.mark.postgres


@pytest.fixture()
def postgres_api(postgres_session: Session):
    original_repository_type = settings.repository_type
    settings.repository_type = "sqlalchemy"

    def override_get_db():
        try:
            yield postgres_session
            postgres_session.commit()
        except Exception:
            postgres_session.rollback()
            raise

    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()
    settings.repository_type = original_repository_type


async def create_customer(
    client: AsyncClient,
    whatsapp: str,
    cpf: str = "529.982.247-25",
) -> str:
    response = await client.post(
        "/customers/",
        json={
            "name": "Maria Clara",
            "whatsapp": whatsapp,
            "cpf": cpf,
        },
    )

    assert response.status_code == 201
    return response.json()["id"]


async def create_service_order(
    client: AsyncClient,
    *,
    customer_id: str,
    equipment_type: str = "Notebook",
    reported_problem: str = "Does not turn on",
) -> dict:
    response = await client.post(
        "/service-orders/",
        json={
            "customer_id": customer_id,
            "equipment_type": equipment_type,
            "reported_problem": reported_problem,
            "equipment_brand": "Dell",
            "equipment_model": "Latitude 5420",
            "equipment_identification": "SN-123",
            "internal_notes": "Priority customer",
        },
    )

    assert response.status_code == 201
    return response.json()


@pytest.mark.anyio
async def test_create_service_order_persists_in_postgres(
    postgres_api,
    postgres_session: Session,
) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        customer_id = await create_customer(client, "(11) 99999-1234")
        response = await client.post(
            "/service-orders/",
            json={
                "customer_id": customer_id,
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
    assert body["customer_id"] == customer_id
    assert body["equipment_type"] == "Notebook"
    assert body["reported_problem"] == "Does not turn on"
    assert body["equipment_brand"] == "Dell"
    assert body["equipment_model"] == "Latitude 5420"
    assert body["equipment_identification"] == "SN-123"
    assert body["internal_notes"] == "Priority customer"
    assert body["status"] == "opened"
    assert body["closed_at"] is None

    persisted_service_order = (
        postgres_session.execute(
            text(
                """
                SELECT customer_id, equipment_type, reported_problem,
                       equipment_brand, equipment_model, equipment_identification,
                       internal_notes, status, closed_at
                FROM service_orders
                WHERE id = :id
                """
            ),
            {"id": body["id"]},
        )
        .mappings()
        .one()
    )
    assert str(persisted_service_order["customer_id"]) == customer_id
    assert persisted_service_order["equipment_type"] == "Notebook"
    assert persisted_service_order["reported_problem"] == "Does not turn on"
    assert persisted_service_order["equipment_brand"] == "Dell"
    assert persisted_service_order["equipment_model"] == "Latitude 5420"
    assert persisted_service_order["equipment_identification"] == "SN-123"
    assert persisted_service_order["internal_notes"] == "Priority customer"
    assert persisted_service_order["status"] == "opened"
    assert persisted_service_order["closed_at"] is None


@pytest.mark.anyio
async def test_create_service_order_returns_not_found_for_unknown_customer(
    postgres_api,
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
async def test_list_service_orders_reads_from_postgres_with_customer_filter(
    postgres_api,
    postgres_session: Session,
) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        target_customer_id = await create_customer(client, "(11) 99999-1234")
        other_customer_id = await create_customer(
            client,
            "(11) 98888-7777",
            cpf="111.444.777-35",
        )
        first = await create_service_order(
            client,
            customer_id=target_customer_id,
            equipment_type="Notebook",
        )
        await create_service_order(
            client,
            customer_id=other_customer_id,
            equipment_type="Printer",
        )
        second = await create_service_order(
            client,
            customer_id=target_customer_id,
            equipment_type="Desktop",
        )

        postgres_session.execute(
            text(
                """
                UPDATE service_orders
                SET created_at = :created_at
                WHERE id = :id
                """
            ),
            {
                "id": first["id"],
                "created_at": datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc),
            },
        )
        postgres_session.execute(
            text(
                """
                UPDATE service_orders
                SET created_at = :created_at
                WHERE id = :id
                """
            ),
            {
                "id": second["id"],
                "created_at": datetime(2026, 1, 2, 10, 0, tzinfo=timezone.utc),
            },
        )
        postgres_session.commit()

        all_response = await client.get("/service-orders/")
        filtered_response = await client.get(
            f"/service-orders/?customer_id={target_customer_id}",
        )

    assert all_response.status_code == 200
    assert len(all_response.json()) == 3
    assert filtered_response.status_code == 200
    assert [item["id"] for item in filtered_response.json()] == [
        second["id"],
        first["id"],
    ]


@pytest.mark.anyio
async def test_list_service_orders_applies_pagination_in_postgres(
    postgres_api,
    postgres_session: Session,
) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        customer_id = await create_customer(client, "(11) 99999-1234")
        oldest = await create_service_order(
            client,
            customer_id=customer_id,
            equipment_type="Notebook",
        )
        middle = await create_service_order(
            client,
            customer_id=customer_id,
            equipment_type="Desktop",
        )
        newest = await create_service_order(
            client,
            customer_id=customer_id,
            equipment_type="Printer",
        )

        for service_order, created_at in [
            (oldest, datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc)),
            (middle, datetime(2026, 1, 2, 10, 0, tzinfo=timezone.utc)),
            (newest, datetime(2026, 1, 3, 10, 0, tzinfo=timezone.utc)),
        ]:
            postgres_session.execute(
                text(
                    """
                    UPDATE service_orders
                    SET created_at = :created_at
                    WHERE id = :id
                    """
                ),
                {
                    "id": service_order["id"],
                    "created_at": created_at,
                },
            )
        postgres_session.commit()

        response = await client.get("/service-orders/?limit=1&offset=1")

    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [middle["id"]]


@pytest.mark.anyio
async def test_list_service_orders_applies_pagination_with_customer_filter_in_postgres(
    postgres_api,
    postgres_session: Session,
) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        target_customer_id = await create_customer(client, "(11) 99999-1234")
        other_customer_id = await create_customer(
            client,
            "(11) 98888-7777",
            cpf="111.444.777-35",
        )
        target_oldest = await create_service_order(
            client,
            customer_id=target_customer_id,
            equipment_type="Notebook",
        )
        target_middle = await create_service_order(
            client,
            customer_id=target_customer_id,
            equipment_type="Desktop",
        )
        target_newest = await create_service_order(
            client,
            customer_id=target_customer_id,
            equipment_type="Printer",
        )
        other = await create_service_order(
            client,
            customer_id=other_customer_id,
            equipment_type="Monitor",
        )

        for service_order, created_at in [
            (target_oldest, datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc)),
            (target_middle, datetime(2026, 1, 2, 10, 0, tzinfo=timezone.utc)),
            (target_newest, datetime(2026, 1, 3, 10, 0, tzinfo=timezone.utc)),
            (other, datetime(2026, 1, 4, 10, 0, tzinfo=timezone.utc)),
        ]:
            postgres_session.execute(
                text(
                    """
                    UPDATE service_orders
                    SET created_at = :created_at
                    WHERE id = :id
                    """
                ),
                {
                    "id": service_order["id"],
                    "created_at": created_at,
                },
            )
        postgres_session.commit()

        response = await client.get(
            f"/service-orders/?customer_id={target_customer_id}&limit=1&offset=1",
        )

    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [target_middle["id"]]


@pytest.mark.anyio
async def test_get_service_order_returns_postgres_record(
    postgres_api,
) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        customer_id = await create_customer(client, "(11) 99999-1234")
        service_order = await create_service_order(client, customer_id=customer_id)
        response = await client.get(f"/service-orders/{service_order['id']}")

    assert response.status_code == 200
    assert response.json() == service_order


@pytest.mark.anyio
async def test_update_service_order_status_to_terminal_persists_closed_at(
    postgres_api,
    postgres_session: Session,
) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        customer_id = await create_customer(client, "(11) 99999-1234")
        service_order = await create_service_order(client, customer_id=customer_id)

        in_progress_response = await client.patch(
            f"/service-orders/{service_order['id']}/status",
            json={"status": "in_progress"},
        )
        finished_response = await client.patch(
            f"/service-orders/{service_order['id']}/status",
            json={"status": "finished"},
        )
        delivered_response = await client.patch(
            f"/service-orders/{service_order['id']}/status",
            json={"status": "delivered"},
        )

    assert in_progress_response.status_code == 200
    assert in_progress_response.json()["status"] == "in_progress"
    assert finished_response.status_code == 200
    assert finished_response.json()["status"] == "finished"
    assert delivered_response.status_code == 200
    delivered_body = delivered_response.json()
    assert delivered_body["status"] == "delivered"
    assert delivered_body["closed_at"] is not None

    persisted_service_order = (
        postgres_session.execute(
            text(
                """
                SELECT status, closed_at
                FROM service_orders
                WHERE id = :id
                """
            ),
            {"id": service_order["id"]},
        )
        .mappings()
        .one()
    )
    assert persisted_service_order["status"] == "delivered"
    assert persisted_service_order["closed_at"] is not None
