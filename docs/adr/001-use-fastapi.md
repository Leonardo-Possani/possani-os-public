# ADR 001: Uso do FastAPI como Framework Backend

## Status
Proposto

## Contexto
O projeto necessita de uma API robusta, rápida e fácil de evoluir para suportar as operações de assistência técnica. É fundamental que o framework ofereça suporte nativo a tipagem, validação forte de dados e boa integração com ferramentas de automação e IA.

## Decisão
Adotar o **FastAPI** como framework principal para o desenvolvimento do backend.

## Justificativa
- **Performance:** Um dos frameworks Python mais rápidos disponíveis, baseado em Starlette e Pydantic.
- **Produtividade:** Uso extensivo de Type Hints do Python para validação automática e geração de documentação (OpenAPI).
- **Simplicidade:** Curva de aprendizado baixa e código conciso, alinhado à diretriz de "priorizar simplicidade sobre abstração".
- **Ecossistema:** Excelente suporte para operações assíncronas e injeção de dependências.

## Consequências
- Uso obrigatório de `async/await` nos endpoints e serviços quando apropriado.
- Utilização de Pydantic para todos os Schemas de entrada e saída.
- Documentação automática da API via `/docs` (Swagger UI).
