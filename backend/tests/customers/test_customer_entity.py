from uuid import uuid4

from app.customers.domain import Address, Cpf, Cnpj, Customer, CustomerName, Email, Whatsapp


def test_customer_is_created_with_active_status_by_default() -> None:
    customer = Customer(
        id=uuid4(),
        name=CustomerName("Maria Clara"),
        whatsapp=Whatsapp("(11) 99999-1234"),
    )

    assert customer.is_active is True


def test_customer_accepts_optional_fields() -> None:
    address = Address(
        street="Rua A",
        neighborhood="Bairro X",
        number="123",
        complement="AP 1",
        zip_code="12345-678",
    )
    customer = Customer(
        id=uuid4(),
        name=CustomerName("Maria Clara"),
        whatsapp=Whatsapp("(11) 99999-1234"),
        cpf=Cpf("529.982.247-25"),
        email=Email("maria@example.com"),
        address=address,
        notes="Some notes about the customer",
    )

    assert customer.cpf is not None
    assert customer.email is not None
    assert customer.address == address
    assert customer.notes == "Some notes about the customer"


def test_customer_normalizes_blank_notes_to_none() -> None:
    customer = Customer(
        id=uuid4(),
        name=CustomerName("Maria Clara"),
        whatsapp=Whatsapp("(11) 99999-1234"),
        notes="   ",
    )

    assert customer.notes is None


def test_customer_deactivate_returns_inactive_customer() -> None:
    customer = Customer(
        id=uuid4(),
        name=CustomerName("Maria Clara"),
        whatsapp=Whatsapp("(11) 99999-1234"),
    )

    inactive_customer = customer.deactivate()

    assert inactive_customer.is_active is False
    assert inactive_customer.deactivated_at is not None
    assert customer.is_active is True
    assert customer.deactivated_at is None


def test_customer_deactivate_is_idempotent() -> None:
    customer = Customer(
        id=uuid4(),
        name=CustomerName("Maria Clara"),
        whatsapp=Whatsapp("(11) 99999-1234"),
        is_active=False,
    )

    inactive_customer = customer.deactivate()

    assert inactive_customer.is_active is False
    assert inactive_customer == customer
