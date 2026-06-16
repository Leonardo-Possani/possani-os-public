# ADR 003: Adoção do Repository Pattern

## Status
Proposto

## Contexto
Para manter a consistência arquitetural e facilitar a testabilidade, é necessário isolar a lógica de acesso a dados da lógica de negócio (domínio) e das rotas da API.

## Decisão
Implementar o **Repository Pattern** para todas as operações de persistência.

## Justificativa
- **Desacoplamento:** O domínio não conhece os detalhes da persistência (SQL, NoSQL, In-memory).
- **Testabilidade:** Facilita a criação de testes de unidade substituindo repositórios reais por mocks ou implementações em memória sem alterar a lógica de negócio.
- **Manutenibilidade:** Centraliza as consultas e operações de banco em um único lugar, facilitando otimizações e mudanças futuras.
- **Padronização:** Segue a diretriz de "Repositories apenas acessam persistência" definida no `gemini.md`.

## Consequências
- Cada módulo de domínio terá sua própria classe/interface de repositório.
- Serviços e rotas devem depender de abstrações de repositórios, injetadas via sistema de dependências do FastAPI.
- Aumento leve na verbosidade inicial em troca de maior organização a longo prazo.
