# Service Orders

## Objetivo Futuro

Registrar e acompanhar ordens de servico ligadas a clientes.

## Relação com Customers

Toda ordem de servico deve pertencer a um cliente existente. O modulo `customers` fornece o cadastro base e deve ser implementado antes das regras completas de OS.

## Decisão de Implementação

`service_orders` deve seguir o mesmo padrao usado em `backend/app/customers`:

- dominio em `domain.py`
- contratos HTTP em `schemas.py`
- casos de uso em `service.py`
- contrato de repositorio em `interfaces.py`
- persistencia SQLAlchemy em `repository.py`
- models ORM em `models.py`
- conversao Domain <-> ORM em `mappers.py`
- endpoints magros em `routes.py`

## Estado Atual

Campos, regras de status, historico, orcamento e detalhes tecnicos ainda podem estar em definicao.

Nao inventar implementacao final antes da regra de negocio estar definida.
