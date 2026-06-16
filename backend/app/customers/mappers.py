from app.customers.domain import Customer, CustomerName, Whatsapp, Cpf, Cnpj, Email, Address
from app.customers.models import CustomerModel

class CustomerMapper:
    @staticmethod
    def to_orm(customer: Customer) -> CustomerModel:
        return CustomerModel(
            id=customer.id,
            name=customer.name.value,
            whatsapp=customer.whatsapp.value,
            cpf=customer.cpf.value if customer.cpf else None,
            cnpj=customer.cnpj.value if customer.cnpj else None,
            email=customer.email.value if customer.email else None,
            street=customer.address.street if customer.address else None,
            neighborhood=customer.address.neighborhood if customer.address else None,
            number=customer.address.number if customer.address else None,
            complement=customer.address.complement if customer.address else None,
            zip_code=customer.address.zip_code if customer.address else None,
            notes=customer.notes,
            is_active=customer.is_active,
            deactivated_at=customer.deactivated_at
        )

    @staticmethod
    def to_domain(model: CustomerModel) -> Customer:
        address = None
        if any([model.street, model.neighborhood, model.number, model.complement, model.zip_code]):
            address = Address(
                street=model.street,
                neighborhood=model.neighborhood,
                number=model.number,
                complement=model.complement,
                zip_code=model.zip_code
            )

        return Customer(
            id=model.id,
            name=CustomerName(model.name),
            whatsapp=Whatsapp(model.whatsapp),
            cpf=Cpf(model.cpf) if model.cpf else None,
            cnpj=Cnpj(model.cnpj) if model.cnpj else None,
            email=Email(model.email) if model.email else None,
            address=address,
            notes=model.notes,
            is_active=model.is_active,
            deactivated_at=model.deactivated_at
        )
