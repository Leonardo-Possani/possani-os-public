from uuid import uuid4

import pytest

from app.customers.domain import Address, Cnpj, Cpf, Customer, CustomerName, Email, Whatsapp


# Domain tests
def test_customer_name_normalizes_whitespace() -> None:
    name = CustomerName("  Maria   Clara  ")

    assert name.value == "Maria Clara"


def test_customer_name_accepts_unicode_characters() -> None:
    name = CustomerName("João Antônio")
    assert name.value == "João Antônio"

    name = CustomerName("Renée Françoise")
    assert name.value == "Renée Françoise"


def test_customer_name_rejects_empty_string() -> None:
    with pytest.raises(ValueError, match="Customer name cannot be empty."):
        CustomerName("")


def test_customer_name_rejects_only_spaces() -> None:
    with pytest.raises(ValueError, match="Customer name cannot be empty."):
        CustomerName("   ")


def test_customer_name_rejects_special_characters() -> None:
    with pytest.raises(ValueError, match="Customer name contains invalid characters."):
        CustomerName("Maria @Clara")


def test_customer_name_rejects_digits() -> None:
    with pytest.raises(ValueError, match="Customer name contains invalid characters."):
        CustomerName("Maria 123")


def test_customer_name_rejects_mixed_invalid_characters() -> None:
    with pytest.raises(ValueError, match="Customer name contains invalid characters."):
        CustomerName("Maria !@#$123")


def test_customer_name_requires_minimum_three_characters() -> None:
    with pytest.raises(ValueError, match="Customer name must have at least 3 characters."):
        CustomerName("Jo")


def test_customer_name_requires_at_least_two_parts() -> None:
    with pytest.raises(ValueError, match="Customer name must have at least two parts."):
        CustomerName("João")


def test_customer_name_accepts_valid_names() -> None:
    name = CustomerName("João Silva")
    assert name.value == "João Silva"

    name = CustomerName("Maria Clara")
    assert name.value == "Maria Clara"


def test_whatsapp_normalizes_to_digits_only() -> None:
    whatsapp = Whatsapp("(55) 99999-1234")

    assert whatsapp.value == "55999991234"


def test_whatsapp_accepts_10_digit_numbers() -> None:
    whatsapp = Whatsapp("(11) 3456-7890")

    assert whatsapp.value == "1134567890"


def test_whatsapp_accepts_11_digit_numbers() -> None:
    whatsapp = Whatsapp("(11) 93456-7890")

    assert whatsapp.value == "11934567890"


@pytest.mark.parametrize("invalid_whatsapp", ["9999-1234", "123456789", "123456789012"])
def test_whatsapp_rejects_invalid_length(invalid_whatsapp: str) -> None:
    with pytest.raises(ValueError, match="Whatsapp must contain 10 or 11 digits."):
        Whatsapp(invalid_whatsapp)


def test_cpf_accepts_valid_unformatted_cpf() -> None:
    cpf = Cpf("03577657022")
    assert cpf.value == "03577657022"


def test_cpf_accepts_valid_formatted_cpf() -> None:
    cpf = Cpf("035.776.570-22")
    assert cpf.value == "03577657022"


@pytest.mark.parametrize(
    "invalid_cpf",
    [
        "000.000.000-00",
        "111.111.111-11",
        "222.222.222-22",
        "333.333.333-33",
        "444.444.444-44",
        "555.555.555-55",
        "666.666.666-66",
        "777.777.777-77",
        "888.888.888-88",
        "999.999.999-99",
    ],
)
def test_cpf_rejects_all_repeating_digits(invalid_cpf: str) -> None:
    with pytest.raises(ValueError, match="CPF is invalid."):
        Cpf(invalid_cpf)


@pytest.mark.parametrize(
    "invalid_cpf",
    [
        "12345678900",
        "98765432101",
        "123.456.789-10",
        "987.654.321-11",
    ],
)
def test_cpf_rejects_invalid_verification_digits(invalid_cpf: str) -> None:
    with pytest.raises(ValueError, match="CPF is invalid."):
        Cpf(invalid_cpf)


@pytest.mark.parametrize("short_cpf", ["", "123", "1234567890", "   "])
def test_cpf_rejects_cpf_with_less_than_11_digits(short_cpf: str) -> None:
    with pytest.raises(ValueError, match="CPF is invalid."):
        Cpf(short_cpf)


def test_cpf_rejects_cpf_with_more_than_11_digits() -> None:
    with pytest.raises(ValueError, match="CPF is invalid."):
        Cpf("123456789012")


def test_cpf_rejects_non_digit_characters_after_normalization() -> None:
    with pytest.raises(ValueError, match="CPF is invalid."):
        Cpf("123.ABC.789-00")


def test_email_normalizes_trim_and_lowercase() -> None:
    email = Email("  TESTE@EXAMPLE.COM ")

    assert email.value == "teste@example.com"


@pytest.mark.parametrize(
    "valid_email",
    [
        "user@example.com",
        "nome.sobrenome@example.com",
        "user+tag@example.com.br",
    ],
)
def test_email_accepts_valid_formats(valid_email: str) -> None:
    email = Email(valid_email)

    assert email.value == valid_email.lower()


@pytest.mark.parametrize(
    "invalid_email",
    [
        "email-invalido",
        "a@b.c",
        "user@domain.c",
        "user@.com",
    ],
)
def test_email_rejects_invalid_format(invalid_email: str) -> None:
    with pytest.raises(ValueError, match="Email is invalid."):
        Email(invalid_email)


def test_cnpj_normalizes_mask() -> None:
    cnpj = Cnpj("11.222.333/0001-81")

    assert cnpj.value == "11222333000181"


def test_cnpj_accepts_valid_unformatted_cnpj() -> None:
    cnpj = Cnpj("11222333000181")

    assert cnpj.value == "11222333000181"


@pytest.mark.parametrize(
    "invalid_cnpj",
    [
        "",
        "123",
        "1234567890123",
        "12.345.678/0001",
        "12.345.678/0001-9A",
        "   ",
    ],
)
def test_cnpj_rejects_values_without_exactly_14_digits(invalid_cnpj: str) -> None:
    with pytest.raises(ValueError, match="CNPJ must contain exactly 14 digits."):
        Cnpj(invalid_cnpj)


@pytest.mark.parametrize(
    "invalid_cnpj",
    [
        "00.000.000/0000-00",
        "11.111.111/1111-11",
        "22.222.222/2222-22",
        "90.751.488/0001-21",
        "12.345.678/0001-00",
    ],
)
def test_cnpj_rejects_invalid_verification_digits(invalid_cnpj: str) -> None:
    with pytest.raises(ValueError, match="CNPJ is invalid."):
        Cnpj(invalid_cnpj)


def test_address_can_be_created_with_all_fields() -> None:
    address = Address(
        street="Rua da Assunção",
        neighborhood="Centro",
        number="123",
        complement="Apto 101",
        zip_code="00000-000",
    )

    assert address.street == "Rua da Assunção"
    assert address.neighborhood == "Centro"
    assert address.number == "123"
    assert address.complement == "Apto 101"
    assert address.zip_code == "00000000"


def test_address_normalizes_empty_strings_to_none() -> None:
    address = Address(
        street="   ",
        neighborhood="",
        zip_code=" ",
    )

    assert address.street is None
    assert address.neighborhood is None
    assert address.zip_code is None


def test_address_rejects_invalid_zip_code() -> None:
    with pytest.raises(ValueError, match="Zip code must be 8 digits."):
        Address(zip_code="12345")


def test_address_can_be_created_with_optional_fields_as_none() -> None:
    address = Address(
        street="Rua da Assunção",
        neighborhood="Centro",
        number="123",
        complement=None,
        zip_code=None,
    )

    assert address.street == "Rua da Assunção"
    assert address.neighborhood == "Centro"
    assert address.number == "123"
    assert address.complement is None
    assert address.zip_code is None


def test_customer_notes_normalizes_whitespace() -> None:
    customer = Customer(
        id=uuid4(),
        name=CustomerName("Maria Clara"),
        whatsapp=Whatsapp("11999991234"),
        notes="  Some notes about the customer  ",
    )

    assert customer.notes == "Some notes about the customer"


# Security tests
@pytest.mark.parametrize(
    ("value", "message"),
    [
        (None, "Customer name must be a string."),
        (123, "Customer name must be a string."),
        (["João", "Silva"], "Customer name must be a string."),
        ({"name": "João Silva"}, "Customer name must be a string."),
    ],
)
def test_customer_name_rejects_non_string_input(value: object, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        CustomerName(value)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("value", "message"),
    [
        (123, "Whatsapp must be a string."),
        (None, "Whatsapp must be a string."),
    ],
)
def test_whatsapp_rejects_non_string_input(value: object, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        Whatsapp(value)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("value", "message"),
    [
        (123, "CPF must be a string."),
        (None, "CPF must be a string."),
    ],
)
def test_cpf_rejects_non_string_input(value: object, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        Cpf(value)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("value", "message"),
    [
        (123, "Email must be a string."),
        (None, "Email must be a string."),
    ],
)
def test_email_rejects_non_string_input(value: object, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        Email(value)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("value", "message"),
    [
        (123, "CNPJ must be a string."),
        (None, "CNPJ must be a string."),
    ],
)
def test_cnpj_rejects_non_string_input(value: object, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        Cnpj(value)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("field_name", "field_value", "message"),
    [
        ("street", 123, "Street must be a string."),
        ("neighborhood", 123, "Neighborhood must be a string."),
        ("number", 123, "Number must be a string."),
        ("complement", 123, "Complement must be a string."),
        ("zip_code", 123, "Zip code must be a string."),
    ],
)
def test_address_rejects_non_string_input(
    field_name: str,
    field_value: object,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        Address(**{field_name: field_value})  # type: ignore[arg-type]


def test_customer_rejects_non_string_notes() -> None:
    with pytest.raises(ValueError, match="Customer notes must be a string."):
        Customer(
            id=uuid4(),
            name=CustomerName("Maria Clara"),
            whatsapp=Whatsapp("11999991234"),
            notes=123,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    ("factory", "value", "message"),
    [
        (CustomerName, "A" * 121, "Customer name must have at most 120 characters."),
        (Whatsapp, "1" * 21, "Whatsapp must have at most 20 characters."),
        (Cpf, "1" * 15, "CPF must have at most 14 characters."),
        (Email, ("a" * 243) + "@example.com", "Email must have at most 254 characters."),
        (Cnpj, "1" * 19, "CNPJ must have at most 18 characters."),
    ],
)
def test_value_objects_reject_oversized_input(
    factory: object,
    value: str,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        factory(value)  # type: ignore[misc]


@pytest.mark.parametrize(
    ("field_name", "field_value", "message"),
    [
        ("street", "A" * 121, "Street must have at most 120 characters."),
        ("neighborhood", "A" * 81, "Neighborhood must have at most 80 characters."),
        ("number", "1" * 21, "Number must have at most 20 characters."),
        ("complement", "A" * 121, "Complement must have at most 120 characters."),
        ("zip_code", "1" * 10, "Zip code must have at most 9 characters."),
    ],
)
def test_address_rejects_oversized_input(
    field_name: str,
    field_value: str,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        Address(**{field_name: field_value})


def test_customer_rejects_oversized_notes() -> None:
    with pytest.raises(ValueError, match="Customer notes must have at most 1000 characters."):
        Customer(
            id=uuid4(),
            name=CustomerName("Maria Clara"),
            whatsapp=Whatsapp("11999991234"),
            notes="A" * 1001,
        )
