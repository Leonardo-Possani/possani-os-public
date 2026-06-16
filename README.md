# Possani OS

Sistema de gestão para assistências técnicas desenvolvido com foco em **qualidade de software, arquitetura escalável e manutenibilidade de longo prazo**.

Este projeto demonstra a aplicação prática de conceitos como **Clean Architecture**, **Domain-Driven Design (DDD)**, **TDD** e **boas práticas de desenvolvimento backend**, utilizando tecnologias modernas do ecossistema Python.

---

## 🎯 Problema

Muitas assistências técnicas ainda dependem de planilhas, anotações informais ou sistemas rígidos que dificultam a operação diária.

O objetivo do Possani OS é fornecer uma base sólida para gerenciar:

* Cadastro de clientes
* Ordens de serviço
* Histórico de atendimentos
* Controle operacional
* Gestão de estoque e peças
* Evolução futura para ambiente multiusuário

A proposta é construir um sistema capaz de crescer sem comprometer a qualidade do código e a previsibilidade da manutenção.

---

## 🚀 Estado Atual

O projeto encontra-se em desenvolvimento ativo.

### ✅ Implementado

* Módulo de Clientes
* API REST com FastAPI
* Persistência PostgreSQL
* Migrations versionadas com Alembic
* Validação de CPF
* Validação de CNPJ
* Validação de WhatsApp
* Validação de CEP
* Repository Pattern
* Testes unitários
* Testes de integração

### 🚧 Em Desenvolvimento

* Módulo de Ordens de Serviço
* Módulo de Estoque
* Autenticação e Autorização
* Frontend Web
* Dashboard Operacional

---

## 📊 Qualidade Técnica

O projeto foi construído com foco em qualidade e evolução contínua.

### Destaques

* 213 testes automatizados
* Testes unitários e de integração
* PostgreSQL real nos testes de integração
* Migrations versionadas
* Ambiente totalmente containerizado
* Arquitetura orientada ao domínio
* Separação explícita entre regras de negócio e infraestrutura

---

## 🏗️ Arquitetura

O backend segue os princípios da **Clean Architecture**, mantendo o domínio isolado de frameworks, banco de dados e detalhes externos.

```text
┌──────────────────────┐
│       FastAPI        │
└──────────┬───────────┘
           │
┌──────────▼───────────┐
│     Application      │
│      Services        │
└──────────┬───────────┘
           │
┌──────────▼───────────┐
│       Domain         │
│ Entities / VOs       │
└──────────┬───────────┘
           │
┌──────────▼───────────┐
│ Infrastructure Layer │
│ SQLAlchemy / DB      │
└──────────────────────┘
```

### Conceitos Aplicados

#### Domain-Driven Design (DDD)

* Entities
* Value Objects
* Domain Validation
* Ubiquitous Language

#### Repository Pattern

Toda a persistência é acessada através de interfaces, permitindo alternar entre:

* Repositórios em memória
* PostgreSQL
* Outros provedores futuros

#### Explicit Mapping

Conversão explícita entre:

* Domínio
* ORM
* Schemas de API

Evita acoplamento entre regras de negócio e infraestrutura.

#### Dependency Inversion

O domínio não depende de:

* FastAPI
* SQLAlchemy
* PostgreSQL

Essas tecnologias permanecem nas camadas externas.

---

## 🛠️ Stack Tecnológica

### Backend

* Python 3.12+
* FastAPI
* SQLAlchemy 2.x
* Pydantic v2

### Banco de Dados

* PostgreSQL 17
* Alembic

### Testes

* Pytest
* Testes Unitários
* Testes de Integração

### Infraestrutura

* Docker
* Docker Compose

---

## 🧪 Estratégia de Testes

A suíte de testes é dividida em duas camadas para equilibrar velocidade e confiabilidade.

### Testes Unitários

Executam em memória e validam:

* Regras de negócio
* Entidades
* Value Objects
* Serviços
* Mappers

Fornecem feedback rápido durante o desenvolvimento.

### Testes de Integração

Executam contra um PostgreSQL real em container Docker.

Validam:

* Migrations
* Repositórios
* Persistência
* Contratos da API

Isso garante maior proximidade com o ambiente de produção.

### Executando os testes

```bash
# Todos os testes
docker compose exec backend pytest

# Apenas integração PostgreSQL
docker compose exec backend pytest -m postgres
```

---

## 🚀 Executando o Projeto

### 1. Clonar o repositório

```bash
git clone https://github.com/seu-usuario/possani-os-public.git
cd possani-os-public
```

### 2. Subir os serviços

```bash
docker compose up -d
```

### 3. Acessar documentação da API

Swagger:

```text
http://localhost:8000/docs
```

ReDoc:

```text
http://localhost:8000/redoc
```

---

## 🗺️ Roadmap

### V1 — Backend Core

* [x] Cadastro de Clientes
* [x] Persistência PostgreSQL
* [x] API REST
* [x] Testes Automatizados
* [x] Migrations

### V2 — Operação

* [ ] Ordens de Serviço
* [ ] Controle de Estoque
* [ ] Cadastro de Equipamentos
* [ ] Histórico de Atendimento

### V3 — Plataforma

* [ ] Autenticação JWT
* [ ] Controle de Permissões
* [ ] Frontend React
* [ ] Dashboard Operacional
* [ ] Relatórios

---

## 📚 Documentação

A documentação complementar encontra-se na pasta:

```text
docs/
```

Incluindo:

* ADRs (Architecture Decision Records)
* Regras de desenvolvimento
* Modelagem de domínio
* Estratégia de testes
* Padrões arquiteturais

---

## 👨‍💻 Objetivo do Projeto

Este repositório é mantido como parte de um portfólio profissional e demonstra a aplicação de práticas modernas de engenharia de software na construção de sistemas de negócio.

O foco principal está na qualidade do código, arquitetura sustentável, testes automatizados e evolução incremental orientada ao domínio.

