from uuid import UUID

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


def test_list_customers_service_returns_only_active_customers() -> None:
    repository = InMemoryCustomerRepository()
    service = CustomerService(repository=repository)

    active_customer = service.create(
        name="Maria Clara",
        whatsapp="11999991234",
        cpf="529.982.247-25",
    )
    inactive_customer = service.create(
        name="João Silva",
        whatsapp="11988887777",
        cnpj="11.222.333/0001-81",
    )
    service.deactivate_customer(inactive_customer.id)

    customers = service.list()

    assert customers == [active_customer]
    names = {c.name.value for c in customers}
    assert "Maria Clara" in names
    assert "João Silva" not in names


def test_list_customers_service_delegates_filter_to_repository() -> None:
    repository = InMemoryCustomerRepository()
    service = CustomerService(repository=repository)

    service.create(
        name="Maria Clara",
        whatsapp="11999991234",
        cpf="529.982.247-25",
    )
    inactive = service.create(
        name="João Silva",
        whatsapp="11988887777",
        cnpj="11.222.333/0001-81",
    )
    service.deactivate_customer(inactive.id)

    # O repositório já deve retornar apenas ativos; o serviço não deve adicionar filtro extra.
    # Validamos que service.list() e repository.list() retornam o mesmo resultado.
    service_result = service.list()
    repository_result = repository.list()

    assert service_result == repository_result


def test_list_customers_service_delegates_pagination_to_repository() -> None:
    repository = InMemoryCustomerRepository()
    service = CustomerService(repository=repository)

    service.create(
        name="Maria Clara",
        whatsapp="11999991234",
        cpf="529.982.247-25",
    )
    expected_customer = service.create(
        name="João Silva",
        whatsapp="11988887777",
        cnpj="11.222.333/0001-81",
    )
    service.create(
        name="Ana Clara",
        whatsapp="11977776666",
        cpf="111.444.777-35",
    )

    customers = service.list(limit=1, offset=1)

    assert customers == [expected_customer]


def test_in_memory_repository_uses_customer_id_as_storage_key() -> None:
    repository = InMemoryCustomerRepository()
    service = CustomerService(repository=repository)

    first_customer = service.create(
        name="Maria Clara",
        whatsapp="11999991234",
        cpf="529.982.247-25",
    )
    second_customer = service.create(
        name="João Silva",
        whatsapp="11988887777",
        cnpj="11.222.333/0001-81",
    )

    assert repository.exists_by_whatsapp("11999991234") is True
    assert repository.exists_by_whatsapp("11988887777") is True
    assert repository.exists_by_whatsapp("11000000000") is False
    assert set(repository.items.keys()) == {first_customer.id, second_customer.id}
    assert all(isinstance(key, UUID) for key in repository.items)


@pytest.mark.anyio
async def test_list_customers_route_returns_list_of_customers(
    customer_repository: InMemoryCustomerRepository,
) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        await client.post(
            "/customers/",
            json={
                "name": "Maria Test",
                "whatsapp": "11777776666",
                "cnpj": "11.222.333/0001-81",
                "notes": "First customer notes",
                "address": {
                    "street": "Street 1",
                    "neighborhood": "Hood 1",
                    "number": "1",
                    "complement": "Comp 1",
                    "zip_code": "11111-111",
                },
            },
        )
        await client.post(
            "/customers/",
            json={
                "name": "Ana Test",
                "whatsapp": "11666665555",
                "cnpj": "40.596.521/0001-78",
                "notes": "Second customer notes",
                "address": {
                    "street": "Street 2",
                    "neighborhood": "Hood 2",
                    "number": "2",
                    "complement": "Comp 2",
                    "zip_code": "22222-222",
                },
            },
        )
        customers_response = await client.get("/customers/")
        inactive_customer_id = customers_response.json()[1]["id"]
        await client.delete(f"/customers/{inactive_customer_id}")

        response = await client.get("/customers/")

    assert response.status_code == 200
    body = response.json()
    assert body == [
        {
            "id": body[0]["id"],
            "name": "Ana Test",
            "whatsapp": "11666665555",
            "cpf": None,
            "cnpj": "40596521000178",
            "email": None,
            "address": {
                "street": "Street 2",
                "neighborhood": "Hood 2",
                "number": "2",
                "complement": "Comp 2",
                "zip_code": "22222222",
            },
            "notes": "Second customer notes",
            "is_active": True,
            "deactivated_at": None,
        },

    ]
    assert len(body) == 1
