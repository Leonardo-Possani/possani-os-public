import re
import unicodedata
from datetime import datetime, timezone
from dataclasses import dataclass, replace
from uuid import UUID


def _require_string(value: object, field_name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string.")
    return value


def _require_max_length(value: str, max_length: int, field_name: str) -> None:
    if len(value) > max_length:
        raise ValueError(f"{field_name} must have at most {max_length} characters.")


class CustomerName:
    MAX_LENGTH = 120

    def __init__(self, value: str) -> None:
        value = _require_string(value, "Customer name")
        _require_max_length(value, self.MAX_LENGTH, "Customer name")

        normalized = " ".join(value.split())
        if not normalized:
            raise ValueError("Customer name cannot be empty.")
        if len(normalized) < 3:
            raise ValueError("Customer name must have at least 3 characters.")
        if len(normalized.split()) < 2:
            raise ValueError("Customer name must have at least two parts.")
        if not self._is_valid(normalized):
            raise ValueError("Customer name contains invalid characters.")
        self.value = normalized

    @staticmethod
    def _is_valid(value: str) -> bool:
        return all(char == " " or CustomerName._is_letter(char) for char in value)

    @staticmethod
    def _is_letter(char: str) -> bool:
        category = unicodedata.category(char)
        return category.startswith("L")


class Whatsapp:
    MAX_LENGTH = 20

    def __init__(self, value: str) -> None:
        value = _require_string(value, "Whatsapp")
        _require_max_length(value, self.MAX_LENGTH, "Whatsapp")
        normalized = re.sub(r"\D", "", value)
        if len(normalized) not in {10, 11}:
            raise ValueError("Whatsapp must contain 10 or 11 digits.")
        self.value = normalized


class Cpf:
    MAX_LENGTH = 14

    def __init__(self, value: str) -> None:
        value = _require_string(value, "CPF")
        _require_max_length(value, self.MAX_LENGTH, "CPF")
        normalized = re.sub(r"\D", "", value)
        if not self._is_valid(normalized):
            raise ValueError("CPF is invalid.")
        self.value = normalized

    @staticmethod
    def _is_valid(value: str) -> bool:
        if len(value) != 11 or value == value[0] * 11:
            return False

        first_digit = Cpf._calculate_digit(value[:9], start_weight=10)
        second_digit = Cpf._calculate_digit(value[:10], start_weight=11)
        return value[-2:] == f"{first_digit}{second_digit}"

    @staticmethod
    def _calculate_digit(value: str, start_weight: int) -> int:
        total = sum(
            int(digit) * weight
            for digit, weight in zip(value, range(start_weight, 1, -1))
        )
        remainder = total % 11
        return 0 if remainder < 2 else 11 - remainder


class Email:
    MAX_LENGTH = 254

    def __init__(self, value: str) -> None:
        value = _require_string(value, "Email")
        _require_max_length(value, self.MAX_LENGTH, "Email")
        normalized = value.strip().lower()
        if not self._is_valid(normalized):
            raise ValueError("Email is invalid.")
        self.value = normalized

    @staticmethod
    def _is_valid(value: str) -> bool:
        return bool(
            re.fullmatch(r"[a-z0-9._%+-]+@[a-z0-9-]+(?:\.[a-z0-9-]+)*\.[a-z]{2,}", value)
        )


class Cnpj:
    MAX_LENGTH = 18

    def __init__(self, value: str) -> None:
        value = _require_string(value, "CNPJ")
        _require_max_length(value, self.MAX_LENGTH, "CNPJ")
        normalized = re.sub(r"\D", "", value)
        if len(normalized) != 14:
            raise ValueError("CNPJ must contain exactly 14 digits.")
        if not self._is_valid(normalized):
            raise ValueError("CNPJ is invalid.")
        self.value = normalized

    @staticmethod
    def _is_valid(value: str) -> bool:
        if value == value[0] * 14:
            return False

        first_digit = Cnpj._calculate_digit(value[:12], weights=[5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
        second_digit = Cnpj._calculate_digit(value[:13], weights=[6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
        return value[-2:] == f"{first_digit}{second_digit}"

    @staticmethod
    def _calculate_digit(value: str, weights: list[int]) -> int:
        total = sum(int(digit) * weight for digit, weight in zip(value, weights))
        remainder = total % 11
        return 0 if remainder < 2 else 11 - remainder


@dataclass(frozen=True)
class Address:
    STREET_MAX_LENGTH = 120
    NEIGHBORHOOD_MAX_LENGTH = 80
    NUMBER_MAX_LENGTH = 20
    COMPLEMENT_MAX_LENGTH = 120
    ZIP_CODE_MAX_LENGTH = 9

    street: str | None = None
    neighborhood: str | None = None
    number: str | None = None
    complement: str | None = None
    zip_code: str | None = None

    def __post_init__(self) -> None:
        if self.zip_code is not None:
            self._validate_optional_string(self.zip_code, "Zip code", self.ZIP_CODE_MAX_LENGTH)
            normalized_zip = re.sub(r"\D", "", self.zip_code)
            object.__setattr__(self, "zip_code", normalized_zip or None)

        field_specs = {
            "street": ("Street", self.STREET_MAX_LENGTH),
            "neighborhood": ("Neighborhood", self.NEIGHBORHOOD_MAX_LENGTH),
            "number": ("Number", self.NUMBER_MAX_LENGTH),
            "complement": ("Complement", self.COMPLEMENT_MAX_LENGTH),
        }
        for field_name, (label, max_length) in field_specs.items():
            current_value = getattr(self, field_name)
            if current_value is None:
                continue

            self._validate_optional_string(current_value, label, max_length)
            normalized_value = current_value.strip()
            object.__setattr__(self, field_name, normalized_value or None)

        if self.zip_code and not re.fullmatch(r"^\d{8}$", self.zip_code):
            raise ValueError("Zip code must be 8 digits.")

    @staticmethod
    def _validate_optional_string(value: object, field_name: str, max_length: int) -> None:
        normalized = _require_string(value, field_name)
        _require_max_length(normalized, max_length, field_name)


@dataclass(frozen=True)
class Customer:
    NOTES_MAX_LENGTH = 1000

    id: UUID
    name: CustomerName
    whatsapp: Whatsapp
    cpf: Cpf | None = None
    cnpj: Cnpj | None = None
    email: Email | None = None
    address: Address | None = None
    notes: str | None = None
    is_active: bool = True
    deactivated_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.cpf is not None and self.cnpj is not None:
            raise ValueError("CPF and CNPJ are mutually exclusive")

        if self.notes is not None:
            notes = _require_string(self.notes, "Customer notes")
            _require_max_length(notes, self.NOTES_MAX_LENGTH, "Customer notes")
            normalized_notes = notes.strip()
            object.__setattr__(self, "notes", normalized_notes or None)

    def deactivate(self) -> "Customer":
        if not self.is_active:
            return self

        return replace(self, is_active=False, deactivated_at=datetime.now(timezone.utc))
