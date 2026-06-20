# Possani OS

Possani OS é um sistema para gestão de assistência técnica, criado para organizar clientes, ordens de serviço e histórico operacional de uma assistência real.

O projeto tem como objetivo evoluir de uma base operacional simples para uma plataforma mais completa, com backend robusto, frontend web, automações e recursos inteligentes no futuro.

## Objetivo

O Possani OS nasce para resolver problemas reais de uma assistência técnica:

* cadastro e gestão de clientes;
* abertura e acompanhamento de ordens de serviço;
* registro de equipamentos;
* histórico de atendimentos;
* organização do fluxo operacional;
* base técnica preparada para evolução futura.

## Estado Atual

O projeto está em desenvolvimento ativo.

Atualmente, o backend já possui:

* API em FastAPI;
* banco PostgreSQL via Docker;
* migrations com Alembic;
* módulo de clientes;
* módulo de ordens de serviço;
* regras de domínio isoladas;
* repository pattern;
* service layer;
* testes unitários;
* testes de integração com PostgreSQL real.

O frontend já possui uma base inicial em Next.js/React, preparada para evoluir a interface da aplicação.

## Módulos Implementados

### Clientes

O módulo de clientes permite cadastrar, listar, consultar e desativar clientes.

Principais características:

* entidade de domínio isolada;
* validações de dados;
* persistência com SQLAlchemy;
* soft delete;
* testes unitários e de integração.

### Ordens de Serviço

O módulo de ordens de serviço representa o fluxo principal da assistência técnica.

Principais características:

* criação de ordem de serviço vinculada a um cliente;
* registro de tipo de equipamento;
* marca, modelo e identificação do equipamento;
* problema relatado pelo cliente;
* observações internas;
* status da ordem de serviço;
* regras de transição de status protegidas no domínio;
* persistência em PostgreSQL;
* testes unitários e de integração.

Fluxo base:

```text
cliente cadastrado -> ordem de serviço criada -> status acompanhado -> histórico preservado
```

## Stack

### Backend

* Python
* FastAPI
* PostgreSQL
* SQLAlchemy
* Alembic
* Pytest
* Docker

### Frontend

* Next.js
* React
* TypeScript

### Arquitetura

O projeto segue uma abordagem pragmática inspirada em Clean Architecture e DDD, com separação entre:

* domínio;
* casos de uso;
* repositórios;
* models de persistência;
* schemas de API;
* rotas FastAPI;
* testes automatizados.

## Estrutura do Repositório

```text
backend/
  app/
    customers/
    service_orders/
    db.py
    dependencies.py
    main.py
  alembic/
  tests/

frontend/
  app/
  components/
  features/
  lib/
  providers/

docs/
  adr/
  domain/
  api.md
  backend-patterns.md
  database.md
  testing-guide.md

docker-compose.yml
README.md
```

## Documentação Técnica

* `docs/api.md`: visão geral da API.
* `docs/database.md`: decisões sobre banco de dados e migrations.
* `docs/testing-guide.md`: comandos e estratégia de testes.
* `docs/backend-patterns.md`: padrões técnicos adotados no backend.
* `docs/domain/`: documentação dos módulos de domínio.
* `docs/adr/`: decisões arquiteturais públicas.

## Como Rodar o Projeto

Crie o arquivo `.env` a partir do exemplo:

```bash
cp .env.example .env
```

Suba os containers:

```bash
docker compose up -d
```

Aplique as migrations no banco principal:

```bash
docker compose exec backend alembic upgrade head
```

A API ficará disponível em:

```text
http://localhost:8000/docs
```

## Banco de Testes PostgreSQL

Os testes de integração usam um banco separado chamado `possani_os_test`.

Crie o banco de teste:

```bash
docker compose exec postgres psql -U possani -d postgres -c "CREATE DATABASE possani_os_test;"
```

Aplique as migrations no banco de teste:

```bash
docker compose exec backend sh -c 'DATABASE_URL="$POSTGRES_TEST_DATABASE_URL" alembic upgrade head'
```

## Rodando os Testes

Rodar todos os testes:

```bash
docker compose exec backend pytest
```

Rodar apenas testes PostgreSQL:

```bash
docker compose exec backend pytest -m postgres
```

Rodar testes sem PostgreSQL:

```bash
docker compose exec backend pytest -m "not postgres"
```

## Próximos Marcos

Os próximos passos do projeto incluem:

* evolução do frontend;
* telas de clientes;
* telas de ordens de serviço;
* autenticação;
* melhoria da experiência operacional;
* automações futuras;
* preparação para implantação em VPS.

## Status

Projeto em desenvolvimento ativo.

