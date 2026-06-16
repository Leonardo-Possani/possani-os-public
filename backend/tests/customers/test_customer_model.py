import uuid
from datetime import datetime, timezone
from sqlalchemy import select
from app.db import Base, engine, SessionLocal
from app.customers.models import CustomerModel

def test_customer_model_persistence():
    # Arrange
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    
    customer_id = uuid.uuid4()
    customer_data = {
        "id": customer_id,
        "name": "João da Silva",
        "whatsapp": "11999999999",
        "cpf": "12345678901",
        "cnpj": "12345678901234",
        "email": "joao@example.com",
        "street": "Rua das Flores",
        "neighborhood": "Centro",
        "number": "123",
        "complement": "Apto 1",
        "zip_code": "01234567",
        "notes": "Some notes here",
        "is_active": True,
    }
    
    customer = CustomerModel(**customer_data)
    
    # Act
    session.add(customer)
    session.commit()
    
    # Assert
    stmt = select(CustomerModel).where(CustomerModel.id == customer_id)
    retrieved_customer = session.execute(stmt).scalar_one()
    
    assert retrieved_customer.id == customer_id
    assert retrieved_customer.name == "João da Silva"
    assert retrieved_customer.whatsapp == "11999999999"
    assert retrieved_customer.cpf == "12345678901"
    assert retrieved_customer.cnpj == "12345678901234"
    assert retrieved_customer.email == "joao@example.com"
    assert retrieved_customer.street == "Rua das Flores"
    assert retrieved_customer.neighborhood == "Centro"
    assert retrieved_customer.number == "123"
    assert retrieved_customer.complement == "Apto 1"
    assert retrieved_customer.zip_code == "01234567"
    assert retrieved_customer.notes == "Some notes here"
    assert retrieved_customer.is_active is True
    assert isinstance(retrieved_customer.created_at, datetime)
    assert isinstance(retrieved_customer.updated_at, datetime)
    assert retrieved_customer.deactivated_at is None
    
    session.close()
    Base.metadata.drop_all(bind=engine)

def test_customer_model_defaults():
    # Arrange
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    
    customer_id = uuid.uuid4()
    customer = CustomerModel(
        id=customer_id,
        name="Only Name",
        whatsapp="11999999999"
    )
    
    # Act
    session.add(customer)
    session.commit()
    
    # Assert
    retrieved = session.get(CustomerModel, customer_id)
    assert retrieved.is_active is True
    assert retrieved.created_at is not None
    assert retrieved.updated_at is not None
    assert retrieved.deactivated_at is None
    assert retrieved.cpf is None
    assert retrieved.street is None
    
    session.close()
    Base.metadata.drop_all(bind=engine)
