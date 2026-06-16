# Backend Patterns

O modulo `customers` e o padrao atual para novos modulos do backend.

## Module Files

| File | Responsibility |
| --- | --- |
| `domain.py` | Regras puras do dominio, entidades e value objects. |
| `schemas.py` | Entrada e saida da API com Pydantic. |
| `service.py` | Casos de uso e orquestracao de negocio. |
| `interfaces.py` | Contratos/protocolos dos repositorios. |
| `repository.py` | Implementacao SQLAlchemy. |
| `in_memory_repository.py` | Implementacao usada em testes rapidos. |
| `models.py` | Modelos ORM SQLAlchemy. |
| `mappers.py` | Conversao explicita Domain <-> ORM. |
| `routes.py` | Endpoints FastAPI magros. |

## Flow

`routes.py` recebe HTTP, valida o contrato Pydantic e chama `service.py`.
`service.py` aplica o caso de uso, cria objetos de dominio e usa o repositorio pelo contrato de `interfaces.py`.
`repository.py` persiste com SQLAlchemy e usa `mappers.py` para converter entre dominio e ORM.

## Rules

- Rotas nao acessam banco diretamente.
- Rotas nao carregam regra de negocio.
- Services nao dependem de FastAPI.
- Repositories nao devem conter regra de negocio complexa.
- Mappers devem concentrar conversao entre dominio e ORM.
- Novos modulos devem seguir o padrao de `customers`, salvo justificativa clara.
