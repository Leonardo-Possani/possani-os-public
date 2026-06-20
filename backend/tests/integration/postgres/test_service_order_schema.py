import pytest
from sqlalchemy import inspect


pytestmark = pytest.mark.postgres


def test_service_orders_table_exists(postgres_engine) -> None:
    inspector = inspect(postgres_engine)

    tables = inspector.get_table_names()

    assert "service_orders" in tables


def test_service_orders_table_has_expected_columns(postgres_engine) -> None:
    inspector = inspect(postgres_engine)

    columns = inspector.get_columns("service_orders")
    column_names = {column["name"] for column in columns}

    assert column_names == {
        "id",
        "customer_id",
        "equipment_type",
        "reported_problem",
        "equipment_brand",
        "equipment_model",
        "equipment_identification",
        "internal_notes",
        "status",
        "created_at",
        "updated_at",
        "closed_at",
    }


def test_service_orders_table_has_expected_nullability(postgres_engine) -> None:
    inspector = inspect(postgres_engine)

    columns = {
        column["name"]: column
        for column in inspector.get_columns("service_orders")
    }

    assert columns["id"]["nullable"] is False
    assert columns["customer_id"]["nullable"] is False
    assert columns["equipment_type"]["nullable"] is False
    assert columns["reported_problem"]["nullable"] is False
    assert columns["status"]["nullable"] is False
    assert columns["created_at"]["nullable"] is False
    assert columns["updated_at"]["nullable"] is False
    assert columns["equipment_brand"]["nullable"] is True
    assert columns["equipment_model"]["nullable"] is True
    assert columns["equipment_identification"]["nullable"] is True
    assert columns["internal_notes"]["nullable"] is True
    assert columns["closed_at"]["nullable"] is True


def test_service_orders_table_has_expected_string_lengths(postgres_engine) -> None:
    inspector = inspect(postgres_engine)

    columns = {
        column["name"]: column
        for column in inspector.get_columns("service_orders")
    }

    assert columns["equipment_type"]["type"].length == 500
    assert columns["reported_problem"]["type"].length == 2000
    assert columns["equipment_brand"]["type"].length == 255
    assert columns["equipment_model"]["type"].length == 255
    assert columns["equipment_identification"]["type"].length == 255
    assert columns["internal_notes"]["type"].length == 2000
    assert columns["status"]["type"].length == 32


def test_service_orders_table_has_customer_foreign_key(postgres_engine) -> None:
    inspector = inspect(postgres_engine)

    foreign_keys = inspector.get_foreign_keys("service_orders")

    assert any(
        foreign_key["constrained_columns"] == ["customer_id"]
        and foreign_key["referred_table"] == "customers"
        and foreign_key["referred_columns"] == ["id"]
        for foreign_key in foreign_keys
    )


def test_service_orders_table_has_expected_indexes(postgres_engine) -> None:
    inspector = inspect(postgres_engine)

    indexes = {
        index["name"]: index["column_names"]
        for index in inspector.get_indexes("service_orders")
    }

    assert indexes["ix_service_orders_customer_id"] == ["customer_id"]
    assert indexes["ix_service_orders_status"] == ["status"]
