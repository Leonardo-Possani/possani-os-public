import time
from datetime import datetime, timezone
from uuid import UUID, uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings
from app.customers.domain import Address, Cnpj, Customer, CustomerName, Cpf, Email, Whatsapp
from app.customers.models import CustomerModel
from app.customers.repository import SqlAlchemyCustomerRepository
from app.customers.service import CustomerAlreadyExistsError, CustomerService
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


@pytest.mark.anyio
async def test_create_customer_persists_in_postgres(
    postgres_api,
    postgres_session: Session,
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

    persisted_customer = (
        postgres_session.execute(
            text(
                """
                SELECT name, whatsapp, cpf, email, street, zip_code, notes, is_active
                FROM customers
                WHERE id = :id
                """
            ),
            {"id": body["id"]},
        )
        .mappings()
        .one()
    )
    assert persisted_customer["name"] == "Maria Clara"
    assert persisted_customer["whatsapp"] == "11999991234"
    assert persisted_customer["cpf"] == "52998224725"
    assert persisted_customer["email"] == "maria@example.com"
    assert persisted_customer["street"] == "Rua A"
    assert persisted_customer["zip_code"] == "12345678"
    assert persisted_customer["notes"] == "Some notes"
    assert persisted_customer["is_active"] is True


@pytest.mark.anyio
async def test_create_customer_without_cpf_or_cnpj_persists_in_postgres(
    postgres_api,
    postgres_session: Session,
) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/customers/",
            json={
                "name": "Maria Clara",
                "whatsapp": "(11) 99999-1234",
            },
        )

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Maria Clara"
    assert body["whatsapp"] == "11999991234"
    assert body["cpf"] is None
    assert body["cnpj"] is None

    persisted_customer = (
        postgres_session.execute(
            text(
                """
                SELECT name, whatsapp, cpf, cnpj
                FROM customers
                WHERE id = :id
                """
            ),
            {"id": body["id"]},
        )
        .mappings()
        .one()
    )
    assert persisted_customer["name"] == "Maria Clara"
    assert persisted_customer["whatsapp"] == "11999991234"
    assert persisted_customer["cpf"] is None
    assert persisted_customer["cnpj"] is None


@pytest.mark.anyio
async def test_create_customer_returns_bad_request_for_cpf_and_cnpj_in_postgres(
    postgres_api,
) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/customers/",
            json={
                "name": "Maria Clara",
                "whatsapp": "(11) 99999-1234",
                "cpf": "529.982.247-25",
                "cnpj": "11.222.333/0001-81",
            },
        )

    assert response.status_code == 400
    assert response.json()["detail"] == "CPF and CNPJ are mutually exclusive."


@pytest.mark.anyio
async def test_get_customer_returns_customer_persisted_in_postgres(
    postgres_api,
) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        create_response = await client.post(
            "/customers/",
            json={
                "name": "Ana Clara",
                "whatsapp": "(11) 98888-7777",
                "cnpj": "11.222.333/0001-81",
            },
        )

        customer_id = create_response.json()["id"]
        get_response = await client.get(f"/customers/{customer_id}")

    assert create_response.status_code == 201
    assert get_response.status_code == 200
    assert get_response.json() == {
        "id": customer_id,
        "name": "Ana Clara",
        "whatsapp": "11988887777",
        "cpf": None,
        "cnpj": "11222333000181",
        "email": None,
        "address": None,
        "notes": None,
        "is_active": True,
        "deactivated_at": None,
    }


@pytest.mark.anyio
async def test_list_customers_applies_pagination_in_postgres(
    postgres_api,
    postgres_session: Session,
) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        first_response = await client.post(
            "/customers/",
            json={
                "name": "Maria Clara",
                "whatsapp": "11999991234",
                "cpf": "529.982.247-25",
            },
        )
        second_response = await client.post(
            "/customers/",
            json={
                "name": "Ana Clara",
                "whatsapp": "11988887777",
                "cnpj": "11.222.333/0001-81",
            },
        )
        third_response = await client.post(
            "/customers/",
            json={
                "name": "Joao Silva",
                "whatsapp": "11977776666",
                "cpf": "111.444.777-35",
            },
        )
        postgres_session.execute(
            text(
                """
                UPDATE customers
                SET created_at = :created_at
                WHERE id = :id
                """
            ),
            {
                "id": first_response.json()["id"],
                "created_at": datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc),
            },
        )
        postgres_session.execute(
            text(
                """
                UPDATE customers
                SET created_at = :created_at
                WHERE id = :id
                """
            ),
            {
                "id": second_response.json()["id"],
                "created_at": datetime(2026, 1, 2, 10, 0, tzinfo=timezone.utc),
            },
        )
        postgres_session.execute(
            text(
                """
                UPDATE customers
                SET created_at = :created_at
                WHERE id = :id
                """
            ),
            {
                "id": third_response.json()["id"],
                "created_at": datetime(2026, 1, 3, 10, 0, tzinfo=timezone.utc),
            },
        )
        postgres_session.commit()

        list_response = await client.get("/customers/?limit=1&offset=1")

    assert first_response.status_code == 201
    assert second_response.status_code == 201
    assert third_response.status_code == 201
    assert list_response.status_code == 200
    assert [item["id"] for item in list_response.json()] == [
        second_response.json()["id"],
    ]


@pytest.mark.anyio
async def test_delete_customer_deactivates_customer_in_postgres(
    postgres_api,
    postgres_session: Session,
) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        create_response = await client.post(
            "/customers/",
            json={
                "name": "Joao Silva",
                "whatsapp": "(11) 97777-6666",
                "cpf": "111.444.777-35",
            },
        )

        customer_id = create_response.json()["id"]
        delete_response = await client.delete(f"/customers/{customer_id}")

    assert create_response.status_code == 201
    assert delete_response.status_code == 200
    body = delete_response.json()
    assert body["id"] == customer_id
    assert body["is_active"] is False
    assert body["deactivated_at"] is not None

    persisted_customer = (
        postgres_session.execute(
            text(
                """
                SELECT is_active, deactivated_at
                FROM customers
                WHERE id = :id
                """
            ),
            {"id": customer_id},
        )
        .mappings()
        .one()
    )
    assert persisted_customer["is_active"] is False
    assert persisted_customer["deactivated_at"] is not None


def test_postgres_uniqueness_checks_ignore_excluded_customer(
    postgres_session: Session,
) -> None:
    repository = SqlAlchemyCustomerRepository(postgres_session)
    service = CustomerService(repository)

    first_cpf_customer = service.create(
        name="Maria Clara",
        whatsapp="11999991234",
        cpf="529.982.247-25",
    )
    second_cpf_customer = service.create(
        name="Joao Silva",
        whatsapp="11988887777",
        cpf="111.444.777-35",
    )
    first_cnpj_customer = service.create(
        name="Ana Empresa",
        whatsapp="11977776666",
        cnpj="11.222.333/0001-81",
    )
    second_cnpj_customer = service.create(
        name="Beto Empresa",
        whatsapp="11966665555",
        cnpj="04.252.011/0001-10",
    )

    assert repository.exists_by_whatsapp(
        first_cpf_customer.whatsapp.value,
        exclude_id=first_cpf_customer.id,
    ) is False
    assert repository.exists_by_whatsapp(
        second_cpf_customer.whatsapp.value,
        exclude_id=first_cpf_customer.id,
    ) is True

    assert repository.exists_by_cpf(
        first_cpf_customer.cpf.value,
        exclude_id=first_cpf_customer.id,
    ) is False
    assert repository.exists_by_cpf(
        second_cpf_customer.cpf.value,
        exclude_id=first_cpf_customer.id,
    ) is True

    assert repository.exists_by_cnpj(
        first_cnpj_customer.cnpj.value,
        exclude_id=first_cnpj_customer.id,
    ) is False
    assert repository.exists_by_cnpj(
        second_cnpj_customer.cnpj.value,
        exclude_id=first_cnpj_customer.id,
    ) is True


@pytest.mark.parametrize(
    ("field_name", "first_document", "second_document", "conflicting_value"),
    [
        ("whatsapp", {"cpf": "529.982.247-25"}, {"cpf": "111.444.777-35"}, "11988887777"),
        ("cpf", {"cpf": "529.982.247-25"}, {"cpf": "111.444.777-35"}, "111.444.777-35"),
        ("cnpj", {"cnpj": "11.222.333/0001-81"}, {"cnpj": "04.252.011/0001-10"}, "04.252.011/0001-10"),
    ],
)
def test_customer_service_update_rejects_unique_field_collisions_in_postgres(
    postgres_session: Session,
    field_name: str,
    first_document: dict[str, str],
    second_document: dict[str, str],
    conflicting_value: str,
) -> None:
    repository = SqlAlchemyCustomerRepository(postgres_session)
    service = CustomerService(repository)

    first_customer = service.create(
        name="Maria Clara",
        whatsapp="11999991234",
        **first_document,
    )
    service.create(
        name="Joao Silva",
        whatsapp="11988887777",
        **second_document,
    )

    with pytest.raises(CustomerAlreadyExistsError):
        service.update(first_customer.id, **{field_name: conflicting_value})


def test_sqlalchemy_repository_update_persists_all_fields_and_updates_timestamp(
    postgres_session: Session,
) -> None:
    repository = SqlAlchemyCustomerRepository(postgres_session)
    customer = Customer(
        id=uuid4(),
        name=CustomerName("Maria Clara"),
        whatsapp=Whatsapp("11999991234"),
        cpf=Cpf("529.982.247-25"),
        email=Email("maria@example.com"),
        address=Address(street="Rua A", zip_code="12345-678"),
        notes="Initial notes",
    )
    repository.add(customer)
    postgres_session.commit()
    model = postgres_session.get(CustomerModel, customer.id)
    initial_updated_at = model.updated_at

    time.sleep(0.1)
    updated = Customer(
        id=customer.id,
        name=CustomerName("Ana Clara"),
        whatsapp=Whatsapp("11988887777"),
        cnpj=Cnpj("11.222.333/0001-81"),
        email=Email("ana@example.com"),
        address=Address(
            street="Rua B",
            neighborhood="Bairro Y",
            number="456",
            complement="Sala 2",
            zip_code="87654-321",
        ),
        notes="Updated notes",
    )

    result = repository.update(updated)
    postgres_session.expire_all()
    persisted_model = postgres_session.get(CustomerModel, customer.id)

    assert result.name.value == "Ana Clara"
    assert result.whatsapp.value == "11988887777"
    assert result.cpf is None
    assert result.cnpj.value == "11222333000181"
    assert result.email.value == "ana@example.com"
    assert result.address.street == "Rua B"
    assert result.address.neighborhood == "Bairro Y"
    assert result.address.number == "456"
    assert result.address.complement == "Sala 2"
    assert result.address.zip_code == "87654321"
    assert result.notes == "Updated notes"
    assert persisted_model.updated_at > initial_updated_at


def test_sqlalchemy_repository_update_persists_none_for_optional_fields(
    postgres_session: Session,
) -> None:
    repository = SqlAlchemyCustomerRepository(postgres_session)
    customer = Customer(
        id=uuid4(),
        name=CustomerName("Maria Clara"),
        whatsapp=Whatsapp("11999991234"),
        cpf=Cpf("529.982.247-25"),
        email=Email("maria@example.com"),
        address=Address(street="Rua A", zip_code="12345-678"),
        notes="Initial notes",
    )
    repository.add(customer)
    postgres_session.commit()

    updated = Customer(
        id=customer.id,
        name=customer.name,
        whatsapp=customer.whatsapp,
        cpf=customer.cpf,
        email=None,
        address=None,
        notes=None,
    )

    repository.update(updated)
    persisted_customer = (
        postgres_session.execute(
            text(
                """
                SELECT email, street, neighborhood, number, complement, zip_code, notes
                FROM customers
                WHERE id = :id
                """
            ),
            {"id": str(customer.id)},
        )
        .mappings()
        .one()
    )

    assert persisted_customer["email"] is None
    assert persisted_customer["street"] is None
    assert persisted_customer["neighborhood"] is None
    assert persisted_customer["number"] is None
    assert persisted_customer["complement"] is None
    assert persisted_customer["zip_code"] is None
    assert persisted_customer["notes"] is None


@pytest.mark.anyio
async def test_update_customer_partially_updates_customer_in_postgres(
    postgres_api,
    postgres_session: Session,
) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        create_response = await client.post(
            "/customers/",
            json={
                "name": "Maria Clara",
                "whatsapp": "11999991234",
                "cpf": "529.982.247-25",
                "email": "maria@example.com",
                "address": {
                    "street": "Rua A",
                    "neighborhood": "Bairro X",
                    "number": "123",
                    "zip_code": "12345-678",
                },
                "notes": "Initial notes",
            },
        )
        customer_id = create_response.json()["id"]
        customer_uuid = UUID(customer_id)
        initial_updated_at = postgres_session.get(CustomerModel, customer_uuid).updated_at
        time.sleep(0.1)
        update_response = await client.put(
            f"/customers/{customer_id}",
            json={
                "name": "Maria Silva",
                "address": {"street": "Rua B", "zip_code": None},
                "notes": None,
            },
        )

    assert create_response.status_code == 201
    assert update_response.status_code == 200
    body = update_response.json()
    assert body["id"] == customer_id
    assert body["name"] == "Maria Silva"
    assert body["whatsapp"] == "11999991234"
    assert body["cpf"] == "52998224725"
    assert body["email"] == "maria@example.com"
    assert body["address"] == {
        "street": "Rua B",
        "neighborhood": "Bairro X",
        "number": "123",
        "complement": None,
        "zip_code": "12345678",
    }
    assert body["notes"] is None

    postgres_session.expire_all()
    updated_model = postgres_session.get(CustomerModel, customer_uuid)
    assert updated_model.updated_at > initial_updated_at


@pytest.mark.anyio
async def test_update_customer_completely_updates_customer_in_postgres(
    postgres_api,
) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        create_response = await client.post(
            "/customers/",
            json={
                "name": "Maria Clara",
                "whatsapp": "11999991234",
                "cpf": "529.982.247-25",
            },
        )
        customer_id = create_response.json()["id"]
        update_response = await client.put(
            f"/customers/{customer_id}",
            json={
                "name": "Ana Clara",
                "whatsapp": "11988887777",
                "cpf": None,
                "cnpj": "11.222.333/0001-81",
                "email": "ana@example.com",
                "address": {
                    "street": "Rua B",
                    "neighborhood": "Bairro Y",
                    "number": "456",
                    "complement": "Sala 2",
                    "zip_code": "87654-321",
                },
                "notes": "Updated notes",
            },
        )

    assert create_response.status_code == 201
    assert update_response.status_code == 200
    assert update_response.json() == {
        "id": customer_id,
        "name": "Ana Clara",
        "whatsapp": "11988887777",
        "cpf": None,
        "cnpj": "11222333000181",
        "email": "ana@example.com",
        "address": {
            "street": "Rua B",
            "neighborhood": "Bairro Y",
            "number": "456",
            "complement": "Sala 2",
            "zip_code": "87654321",
        },
        "notes": "Updated notes",
        "is_active": True,
        "deactivated_at": None,
    }


@pytest.mark.anyio
async def test_update_customer_clears_address_when_address_is_null_in_postgres(
    postgres_api,
) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        create_response = await client.post(
            "/customers/",
            json={
                "name": "Maria Clara",
                "whatsapp": "11999991234",
                "cpf": "529.982.247-25",
                "address": {"street": "Rua A", "zip_code": "12345-678"},
            },
        )
        customer_id = create_response.json()["id"]
        update_response = await client.put(
            f"/customers/{customer_id}",
            json={"address": None},
        )

    assert create_response.status_code == 201
    assert update_response.status_code == 200
    assert update_response.json()["address"] is None


@pytest.mark.anyio
async def test_update_customer_returns_not_found_for_unknown_id_in_postgres(
    postgres_api,
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
@pytest.mark.parametrize(
    ("field_name", "first_document", "second_document", "conflicting_value", "detail"),
    [
        (
            "whatsapp",
            {"cpf": "529.982.247-25"},
            {"cpf": "111.444.777-35"},
            "11988887777",
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
async def test_update_customer_returns_conflict_for_duplicate_unique_fields_in_postgres(
    postgres_api,
    field_name: str,
    first_document: dict[str, str],
    second_document: dict[str, str],
    conflicting_value: str,
    detail: str,
) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        first_response = await client.post(
            "/customers/",
            json={
                "name": "Maria Clara",
                "whatsapp": "11999991234",
                **first_document,
            },
        )
        await client.post(
            "/customers/",
            json={
                "name": "Ana Clara",
                "whatsapp": "11988887777",
                **second_document,
            },
        )
        response = await client.put(
            f"/customers/{first_response.json()['id']}",
            json={field_name: conflicting_value},
        )

    assert first_response.status_code == 201
    assert response.status_code == 409
    assert response.json()["detail"] == detail


@pytest.mark.anyio
async def test_update_customer_returns_bad_request_for_invalid_data_in_postgres(
    postgres_api,
) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        create_response = await client.post(
            "/customers/",
            json={
                "name": "Maria Clara",
                "whatsapp": "11999991234",
                "cpf": "529.982.247-25",
            },
        )
        response = await client.put(
            f"/customers/{create_response.json()['id']}",
            json={"name": "Maria"},
        )

    assert create_response.status_code == 201
    assert response.status_code == 400
    assert response.json()["detail"] == "Customer name must have at least two parts."
