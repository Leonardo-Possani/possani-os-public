# Customers

## Objetivo
Gerenciar clientes que contratam servicos e manter dados confiaveis para os proximos modulos, especialmente `service_orders`.

## Campos Principais

- `id`
- `name`
- `whatsapp`
- `cpf` ou `cnpj`
- `email`
- `address`: `street`, `neighborhood`, `number`, `complement`, `zip_code`
- `notes`
- `is_active`
- `deactivated_at`

## Regras de Negócio

- Nome deve ter pelo menos 3 caracteres, duas partes e apenas letras/espacos.
- WhatsApp e normalizado para digitos e deve ter 10 ou 11 digitos.
- Exatamente um documento deve ser informado: CPF ou CNPJ.
- CPF e CNPJ sao validados e normalizados.
- Email e normalizado para minusculas e validado.
- CEP e normalizado para 8 digitos quando informado.
- WhatsApp, CPF e CNPJ devem ser unicos.
- Cliente novo nasce ativo.
- Inativar cliente altera `is_active` e preenche `deactivated_at`.

## Fluxo Principal

1. A rota recebe payload Pydantic.
2. O service cria value objects e valida unicidade pelo repository.
3. O repository persiste via SQLAlchemy.
4. Mappers convertem entre dominio e ORM.
5. A resposta e montada com `CustomerRead`.

## Endpoints

- `POST /customers/`
- `GET /customers/`
- `GET /customers/{id}`
- `PUT /customers/{id}`
- `DELETE /customers/{id}`

## Arquivos Principais

- `backend/app/customers/domain.py`
- `backend/app/customers/schemas.py`
- `backend/app/customers/service.py`
- `backend/app/customers/interfaces.py`
- `backend/app/customers/repository.py`
- `backend/app/customers/in_memory_repository.py`
- `backend/app/customers/models.py`
- `backend/app/customers/mappers.py`
- `backend/app/customers/routes.py`

## Testes Relacionados

- `backend/tests/customers/`
- `backend/tests/integration/postgres/test_customers_api.py`
