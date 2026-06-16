# Testing Guide

O projeto usa testes unitarios rapidos e testes de integracao com PostgreSQL real.

## Test Types

- Testes unitarios validam dominio, services, mappers, repositories em memoria e rotas com isolamento.
- Testes de integracao PostgreSQL ficam em `backend/tests/integration/postgres` e validam banco real, constraints, API com persistencia e Alembic.
- Testes unitarios de `customers` ficam em `backend/tests/customers`.

## Commands

```bash
docker compose up -d
docker compose ps
docker compose logs backend
docker compose logs postgres
docker compose exec backend pytest
docker compose exec backend pytest tests/customers
docker compose exec backend pytest tests/integration/postgres
docker compose exec backend pytest -q
```

## When To Run

- Rode `pytest tests/customers` ao mudar regras, schemas, services, rotas, mappers ou repositories de `customers`.
- Rode `pytest tests/integration/postgres` ao mudar models, migrations, constraints, configuracao de banco ou persistencia SQLAlchemy.
- Rode `pytest` antes de finalizar mudancas maiores no backend.
- Para alteracoes apenas documentais, testes nao sao necessarios.

## Testing Rules

- Nao remover testes existentes.
- Todo novo campo/regra precisa de teste correspondente.
- Alteracoes em banco precisam rodar testes PostgreSQL.
- Alteracoes em migrations precisam rodar testes de integracao.
- Preferir testes unitarios rapidos para regra de dominio.
- Usar integracao PostgreSQL para validar banco real, constraints e Alembic.
