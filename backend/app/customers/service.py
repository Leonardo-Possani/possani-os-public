from dataclasses import replace
from uuid import UUID, uuid4

from app.customers.domain import Address, Cpf, Cnpj, Customer, CustomerName, Email, Whatsapp
from app.customers.interfaces import AbstractCustomerRepository


class CustomerAlreadyExistsError(Exception):
    pass


class CustomerNotFoundError(Exception):
    pass


class CustomerService:
    def __init__(self, repository: AbstractCustomerRepository) -> None:
        self.repository = repository

    def create(
        self,
        *,
        name: str,
        whatsapp: str,
        cpf: str | None = None,
        cnpj: str | None = None,
        email: str | None = None,
        street: str | None = None,
        neighborhood: str | None = None,
        number: str | None = None,
        complement: str | None = None,
        zip_code: str | None = None,
        notes: str | None = None,
    ) -> Customer:
        if cpf is not None and cnpj is not None:
            raise ValueError("CPF and CNPJ are mutually exclusive.")

        customer_name = CustomerName(name)
        customer_whatsapp = Whatsapp(whatsapp)
        customer_cpf = Cpf(cpf) if cpf else None
        customer_cnpj = Cnpj(cnpj) if cnpj else None
        customer_email = Email(email) if email else None
        customer_address = (
            Address(
                street=street,
                neighborhood=neighborhood,
                number=number,
                complement=complement,
                zip_code=zip_code,
            )
            if any([street, neighborhood, number, complement, zip_code])
            else None
        )

        if self.repository.exists_by_whatsapp(customer_whatsapp.value):
            raise CustomerAlreadyExistsError("Customer with this WhatsApp already exists.")
        if customer_cpf and self.repository.exists_by_cpf(customer_cpf.value):
            raise CustomerAlreadyExistsError("Customer with this CPF already exists.")
        if customer_cnpj and self.repository.exists_by_cnpj(customer_cnpj.value):
            raise CustomerAlreadyExistsError("Customer with this CNPJ already exists.")

        customer = Customer(
            id=uuid4(),
            name=customer_name,
            whatsapp=customer_whatsapp,
            cpf=customer_cpf,
            cnpj=customer_cnpj,
            email=customer_email,
            address=customer_address,
            notes=notes,
        )
        try:
            return self.repository.add(customer)
        except ValueError as exc:
            raise CustomerAlreadyExistsError(str(exc)) from exc

    def list(self, limit: int | None = None, offset: int | None = None) -> list[Customer]:
        return self.repository.list(limit=limit, offset=offset)

    def get_by_id(self, id: UUID) -> Customer | None:
        return self.repository.get_by_id(id)

    def update(self, customer_id: UUID, **kwargs) -> Customer:
        updated_fields = {}

        current_customer = self.repository.get_by_id(customer_id)
        if current_customer is None:
            raise CustomerNotFoundError("Customer not found.")

        value_object_fields = {
            "name": CustomerName,
            "whatsapp": Whatsapp,
            "cpf": Cpf,
            "cnpj": Cnpj,
            "email": Email,
        }
        for field_name, value_object in value_object_fields.items():
            if field_name not in kwargs:
                continue

            value = kwargs[field_name]
            updated_fields[field_name] = None if value is None else value_object(value)

        if "address" in kwargs:
            address = kwargs["address"]
            if address is None:
                updated_fields["address"] = None
            elif isinstance(address, dict):
                current_address = current_customer.address
                address_fields = {
                    "street": current_address.street if current_address else None,
                    "neighborhood": current_address.neighborhood if current_address else None,
                    "number": current_address.number if current_address else None,
                    "complement": current_address.complement if current_address else None,
                    "zip_code": current_address.zip_code if current_address else None,
                }
                address_fields.update(
                    {
                        field_name: value
                        for field_name, value in address.items()
                        if value is not None
                    }
                )
                updated_fields["address"] = Address(**address_fields)

        if "notes" in kwargs:
            updated_fields["notes"] = kwargs["notes"]

        updated_customer = replace(current_customer, **updated_fields)

        if updated_customer.whatsapp.value != current_customer.whatsapp.value:
            if self.repository.exists_by_whatsapp(
                updated_customer.whatsapp.value,
                exclude_id=customer_id,
            ):
                raise CustomerAlreadyExistsError("Customer with this WhatsApp already exists.")

        updated_cpf = updated_customer.cpf.value if updated_customer.cpf else None
        current_cpf = current_customer.cpf.value if current_customer.cpf else None
        if updated_cpf is not None and updated_cpf != current_cpf:
            if self.repository.exists_by_cpf(updated_cpf, exclude_id=customer_id):
                raise CustomerAlreadyExistsError("Customer with this CPF already exists.")

        updated_cnpj = updated_customer.cnpj.value if updated_customer.cnpj else None
        current_cnpj = current_customer.cnpj.value if current_customer.cnpj else None
        if updated_cnpj is not None and updated_cnpj != current_cnpj:
            if self.repository.exists_by_cnpj(updated_cnpj, exclude_id=customer_id):
                raise CustomerAlreadyExistsError("Customer with this CNPJ already exists.")

        try:
            return self.repository.update(updated_customer)
        except ValueError as exc:
            if "already exists" in str(exc):
                raise CustomerAlreadyExistsError(str(exc)) from exc
            raise CustomerNotFoundError("Customer not found.") from exc

    def deactivate_customer(self, id: UUID) -> Customer:
        customer = self.repository.get_by_id(id)
        if customer is None:
            raise CustomerNotFoundError("Customer not found.")

        deactivated_customer = customer.deactivate()
        return self.repository.update(deactivated_customer)
