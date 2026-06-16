from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.customers.in_memory_repository import InMemoryCustomerRepository
from app.dependencies import get_customer_repository
from app.customers.service import CustomerService
from app.main import app


@pytest.fixture
def customer_repository() -> InMemoryCustomerRepository:
    repository = InMemoryCustomerRepository()

    async def override_customer_repository() -> InMemoryCustomerRepository:
        return repository

    app.dependency_overrides[get_customer_repository] = override_customer_repository
    yield repository
    app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_create_customer_returns_created_customer(
    customer_repository: InMemoryCustomerRepository,
) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/customers/",
            json={
                "name": "  Maria   Clara  ",
                "whatsapp": "(11) 99999-1234",
                "cpf": "529.982.247-25",
                "email": "  MARIA@EXAMPLE.COM ",
                "address": {
                    "street": " Rua A ",
                    "neighborhood": "Bairro X",
                    "number": "123",
                    "complement": " Ap. 101 ",
                    "zip_code": "12345-678",
                },
                "notes": " Some notes ",
            },
        )

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Maria Clara"
    assert body["whatsapp"] == "11999991234"
    assert body["cpf"] == "52998224725"
    assert body["cnpj"] is None
    assert body["email"] == "maria@example.com"
    assert body["address"] == {
        "street": "Rua A",
        "neighborhood": "Bairro X",
        "number": "123",
        "complement": "Ap. 101",
        "zip_code": "12345678",
    }
    assert body["notes"] == "Some notes"
    assert body["is_active"] is True
    assert body["id"]


@pytest.mark.anyio
async def test_create_customer_returns_conflict_for_duplicate_whatsapp(
    customer_repository: InMemoryCustomerRepository,
) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        payload = {
            "name": "Maria Clara",
            "whatsapp": "(11) 98888-7777",
            "cpf": "529.982.247-25",
        }

        first_response = await client.post("/customers/", json=payload)
        second_response = await client.post(
            "/customers/",
            json={
                "name": "Ana Clara",
                "whatsapp": "11 98888-7777",
                "cnpj": "11.222.333/0001-81",
            },
        )

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "Customer with this WhatsApp already exists."


@pytest.mark.anyio
async def test_get_customer_returns_customer_by_id(
    customer_repository: InMemoryCustomerRepository,
) -> None:
    service = CustomerService(repository=customer_repository)
    customer = service.create(
        name="Maria Clara",
        whatsapp="(11) 99999-1234",
        cpf="529.982.247-25",
    )

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.get(f"/customers/{customer.id}")

    assert response.status_code == 200
    assert response.json() == {
        "id": str(customer.id),
        "name": "Maria Clara",
        "whatsapp": "11999991234",
        "cpf": "52998224725",
        "cnpj": None,
        "email": None,
        "address": None,
        "notes": None,
        "is_active": True,
        "deactivated_at": None,
    }


@pytest.mark.anyio
async def test_get_customer_returns_not_found_for_unknown_id(
    customer_repository: InMemoryCustomerRepository,
) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.get(f"/customers/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Customer not found."


@pytest.mark.anyio
async def test_delete_customer_deactivates_existing_customer(
    customer_repository: InMemoryCustomerRepository,
) -> None:
    service = CustomerService(repository=customer_repository)
    customer = service.create(
        name="Maria Clara",
        whatsapp="(11) 99999-1234",
        cpf="529.982.247-25",
    )

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.delete(f"/customers/{customer.id}")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == str(customer.id)
    assert body["is_active"] is False
    assert body["deactivated_at"] is not None


@pytest.mark.anyio
async def test_delete_customer_returns_not_found_for_unknown_id(
    customer_repository: InMemoryCustomerRepository,
) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.delete(f"/customers/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Customer not found."


@pytest.mark.anyio
async def test_update_customer_returns_updated_customer(
    customer_repository: InMemoryCustomerRepository,
) -> None:
    service = CustomerService(repository=customer_repository)
    customer = service.create(
        name="Maria Clara",
        whatsapp="(11) 99999-1234",
        cpf="529.982.247-25",
        email="maria@example.com",
        street="Rua A",
        neighborhood="Bairro X",
        number="123",
        complement="Ap. 101",
        zip_code="12345-678",
        notes="Initial notes",
    )

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.put(
            f"/customers/{customer.id}",
            json={
                "name": "  Maria   Silva  ",
                "address": {
                    "street": " Rua B ",
                    "zip_code": None,
                },
                "notes": None,
            },
        )

    assert response.status_code == 200
    assert response.json() == {
        "id": str(customer.id),
        "name": "Maria Silva",
        "whatsapp": "11999991234",
        "cpf": "52998224725",
        "cnpj": None,
        "email": "maria@example.com",
        "address": {
            "street": "Rua B",
            "neighborhood": "Bairro X",
            "number": "123",
            "complement": "Ap. 101",
            "zip_code": "12345678",
        },
        "notes": None,
        "is_active": True,
        "deactivated_at": None,
    }


@pytest.mark.anyio
async def test_update_customer_returns_not_found_for_unknown_id(
    customer_repository: InMemoryCustomerRepository,
) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.put(
            f"/customers/{uuid4()}",
            json={"name": "Maria Silva"},
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Customer not found."


@pytest.mark.anyio
async def test_update_customer_returns_bad_request_for_invalid_data(
    customer_repository: InMemoryCustomerRepository,
) -> None:
    service = CustomerService(repository=customer_repository)
    customer = service.create(
        name="Maria Clara",
        whatsapp="(11) 99999-1234",
        cpf="529.982.247-25",
    )

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.put(
            f"/customers/{customer.id}",
            json={"name": "Maria"},
        )

    assert response.status_code == 400
    assert response.json()["detail"] == "Customer name must have at least two parts."


@pytest.mark.anyio
@pytest.mark.parametrize(
    ("field_name", "first_document", "second_document", "conflicting_value", "detail"),
    [
        (
            "whatsapp",
            {"cpf": "529.982.247-25"},
            {"cpf": "111.444.777-35"},
            "11 98888-7777",
            "Customer with this WhatsApp already exists.",
        ),
        (
            "cpf",
            {"cpf": "529.982.247-25"},
            {"cpf": "111.444.777-35"},
            "111.444.777-35",
            "Customer with this CPF already exists.",
        ),
        (
            "cnpj",
            {"cnpj": "11.222.333/0001-81"},
            {"cnpj": "04.252.011/0001-10"},
            "04.252.011/0001-10",
            "Customer with this CNPJ already exists.",
        ),
    ],
)
async def test_update_customer_returns_conflict_for_duplicate_unique_fields(
    customer_repository: InMemoryCustomerRepository,
    field_name: str,
    first_document: dict[str, str],
    second_document: dict[str, str],
    conflicting_value: str,
    detail: str,
) -> None:
    service = CustomerService(repository=customer_repository)
    first_customer = service.create(
        name="Maria Clara",
        whatsapp="(11) 99999-1234",
        **first_document,
    )
    service.create(
        name="Ana Clara",
        whatsapp="(11) 98888-7777",
        **second_document,
    )

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.put(
            f"/customers/{first_customer.id}",
            json={field_name: conflicting_value},
        )

    assert response.status_code == 409
    assert response.json()["detail"] == detail


@pytest.mark.anyio
async def test_list_customers_excludes_deactivated_customers(
    customer_repository: InMemoryCustomerRepository,
) -> None:
    service = CustomerService(repository=customer_repository)
    active_customer = service.create(
        name="Maria Clara",
        whatsapp="(11) 99999-1234",
        cpf="529.982.247-25",
    )
    inactive_customer = service.create(
        name="Ana Clara",
        whatsapp="(11) 98888-7777",
        cnpj="11.222.333/0001-81",
    )

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        deactivate_response = await client.delete(f"/customers/{inactive_customer.id}")
        list_response = await client.get("/customers/")

    assert deactivate_response.status_code == 200
    assert list_response.status_code == 200
    assert list_response.json() == [
        {
            "id": str(active_customer.id),
            "name": "Maria Clara",
            "whatsapp": "11999991234",
            "cpf": "52998224725",
            "cnpj": None,
            "email": None,
            "address": None,
            "notes": None,
            "is_active": True,
            "deactivated_at": None,
        }
    ]


@pytest.mark.anyio
async def test_create_customer_returns_conflict_for_duplicate_cpf(
    customer_repository: InMemoryCustomerRepository,
) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        first_response = await client.post(
            "/customers/",
            json={
                "name": "Maria Clara",
                "whatsapp": "(11) 99999-1234",
                "cpf": "529.982.247-25",
            },
        )
        second_response = await client.post(
            "/customers/",
            json={
                "name": "Ana Clara",
                "whatsapp": "11 98888-7777",
                "cpf": "52998224725",
            },
        )

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "Customer with this CPF already exists."


@pytest.mark.anyio
async def test_create_customer_returns_conflict_for_duplicate_cnpj(
    customer_repository: InMemoryCustomerRepository,
) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        first_response = await client.post(
            "/customers/",
            json={
                "name": "Maria Clara",
                "whatsapp": "(11) 99999-1234",
                "cnpj": "11.222.333/0001-81",
            },
        )
        second_response = await client.post(
            "/customers/",
            json={
                "name": "Ana Clara",
                "whatsapp": "11 98888-7777",
                "cnpj": "11222333000181",
            },
        )

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "Customer with this CNPJ already exists."
