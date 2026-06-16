# Database

O PostgreSQL roda via Docker Compose. Alembic controla migrations e SQLAlchemy registra os models em `Base.metadata`.

## Runtime

- O servico `postgres` e definido em `docker-compose.yml`.
- O backend usa `DATABASE_URL` carregado pela configuracao.
- `backend/app/db.py` cria engine, session factory e importa models para registro no `Base.metadata`.
- Novos models SQLAlchemy precisam ser importados em `backend/app/db.py` para o Alembic detectar.

## Access

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

## Constraints

Constraints importantes devem existir no banco, nao apenas no service. Em `customers`, WhatsApp, CPF e CNPJ sao unicos no model ORM e no schema gerado por migration.

- Campos unicos devem ser protegidos no banco com `Unique Constraints`.
- Validacao no `service.py` ajuda a retornar erro amigavel, mas nao substitui constraint no banco.
- Novos campos unicos devem ter teste e migration correspondente.

## Migration Rules

- Nao editar migration antiga sem justificativa forte.
- Criar nova migration para mudancas de schema.
- Conferir se o model esta importado em `app/db.py`.
- Rodar testes PostgreSQL depois de alterar schema.
