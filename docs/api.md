# API

A API usa FastAPI e responde JSON. Este documento registra convencoes estaveis e contratos importantes.

## Interactive Docs

Com o backend rodando, a documentacao interativa e testavel fica disponivel em:

- `http://localhost:8000/docs`
- `http://localhost:8000/redoc`

Detalhes especificos dos endpoints devem ser conferidos na documentacao automatica do FastAPI.

## Rules

- Rotas devem continuar magras.
- Contratos HTTP ficam em `schemas.py`.
- Regras e orquestracao ficam em `service.py`.
- Erros de dominio ou service devem ser traduzidos para HTTP nas rotas.
