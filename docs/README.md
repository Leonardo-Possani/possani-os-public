# Documentation

Guia rapido dos documentos principais do projeto.

## Backend

- [Backend patterns](backend-patterns.md): padrao oficial de modulos usando `customers` como referencia.
- [Testing guide](testing-guide.md): comandos e regras para testes unitarios e PostgreSQL.
- [Database](database.md): PostgreSQL, SQLAlchemy, Alembic e regras de migration.
- [API](api.md): endpoints e convencoes operacionais da API.

## Domain

- [Customers](domain/customers.md): regras, fluxo, arquivos e testes do modulo de clientes.
- [Service orders](domain/service-orders.md): placeholder operacional para o proximo modulo.

## Decisions

- [ADR 001](adr/001-use-fastapi.md): uso de FastAPI.
- [ADR 002](adr/002-use-postgresql.md): uso de PostgreSQL.
- [ADR 003](adr/003-repository-pattern.md): uso de Repository Pattern.

## Rules

- [Coding rules](rules/coding-rules.md): regras para implementacao.
- [Review rules](rules/review-rules.md): checklist para revisao.
