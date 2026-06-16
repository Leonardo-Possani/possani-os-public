# ADR 002: Uso do PostgreSQL como Banco de Dados Principal

## Status
Proposto

## Contexto
O sistema gerencia dados operacionais críticos, incluindo Ordens de Serviço, Clientes, Estoque e Financeiro. Esses dados possuem forte relação entre si e exigem consistência e integridade referencial.

## Decisão
Utilizar o **PostgreSQL** como sistema de gerenciamento de banco de dados relacional (RDBMS) principal desde o início do projeto.

## Justificativa
- **Confiabilidade:** Padrão de indústria para persistência de dados relacionais com forte garantia de integridade (ACID).
- **Escalabilidade:** Suporta o crescimento do sistema desde o MVP até operações de larga escala.
- **Recursos Avançados:** Suporte robusto a tipos de dados complexos (como JSONB se necessário) e extensões.
- **Evitar Retrabalho:** Começar com o banco de produção evita dores de cabeça futuras com migrações de bancos mais simples (como SQLite) para relacionais robustos.

## Consequências
- Necessidade de gerenciar instâncias de PostgreSQL (localmente ou via containers).
- Uso do SQLAlchemy 2.0 como ORM para abstração e manipulação dos dados.
- Obrigatoriedade do uso de migrações versionadas (Alembic) para qualquer alteração estrutural.
