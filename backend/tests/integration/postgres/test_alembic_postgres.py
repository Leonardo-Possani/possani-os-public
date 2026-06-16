from uuid import uuid4

import pytest
from sqlalchemy import inspect, select

from app.customers.models import CustomerModel


pytestmark = pytest.mark.postgres


def test_alembic_created_expected_tables(postgres_engine):
    inspector = inspect(postgres_engine)

    tables = inspector.get_table_names()

    assert "alembic_version" in tables
    assert "customers" in tables


def test_customers_table_has_expected_columns(postgres_engine):
    inspector = inspect(postgres_engine)

    columns = inspector.get_columns("customers")
    column_names = {column["name"] for column in columns}

    assert "id" in column_names
    assert "name" in column_names
    assert "whatsapp" in column_names
    assert "cpf" in column_names
    assert "cnpj" in column_names
    assert "created_at" in column_names
    assert "updated_at" in column_names
    assert "deactivated_at" in column_names


def test_postgres_session_allows_committed_customer(postgres_session):
    customer = CustomerModel(
        id=uuid4(),
        name="Cliente Isolamento",
        whatsapp="11999999999",
    )

    postgres_session.add(customer)
    postgres_session.commit()

    persisted_customer = postgres_session.scalar(
        select(CustomerModel).where(CustomerModel.whatsapp == "11999999999")
    )

    assert persisted_customer is not None


def test_postgres_session_cleans_customer_data_between_tests(postgres_session):
    leaked_customer = postgres_session.scalar(
        select(CustomerModel).where(CustomerModel.whatsapp == "11999999999")
    )

    assert leaked_customer is None
