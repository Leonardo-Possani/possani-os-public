# Backend

Guia rapido para rodar o backend do Possani OS.

## Subir Ambiente

```bash
docker compose up -d
docker compose ps
docker compose logs backend
docker compose logs postgres
```

## Rodar Testes

```bash
docker compose exec backend pytest
docker compose exec backend pytest tests/customers
docker compose exec backend pytest tests/integration/postgres
docker compose exec backend pytest -q
```

## Acessar PostgreSQL

```bash
docker compose exec postgres psql -U possani -d possani_os
```

Dentro do `psql`:

```sql
\l
\dt
\d customers
SELECT * FROM customers;
```

## Mais Documentacao

- `docs/backend-patterns.md`
- `docs/testing-guide.md`
- `docs/database.md`
- `docs/api.md`
- `docs/domain/customers.md`
