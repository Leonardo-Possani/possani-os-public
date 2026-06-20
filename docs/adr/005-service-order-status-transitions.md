# ADR 005 — Service Order Status Transitions

## Status
Proposto

## Contexto
O fluxo de trabalho de uma assistência técnica exige consistência. Status alterados de forma arbitrária (ex: de "Aberto" para "Entregue" sem passar por "Finalizado") geram dados de baixa qualidade e confusão operacional.

## Decisão
Implementaremos uma **Matriz de Transição de Status** rígida na camada de Domínio:
1. **Fluxo Controlado:** O domínio validará se o `novo_status` é um sucessor permitido do `status_atual`.
2. **Estados Terminais:** Os status `delivered` e `cancelled` são considerados finais. Uma vez atingidos, a OS é "fechada" e não permite novas transições.
3. **Automação de Fechamento:** O campo `closed_at` será gerenciado exclusivamente pelo domínio, sendo preenchido no momento da entrada em um estado terminal.
4. **Reabertura Limitada:** Na V1, não será permitida a reabertura de OSs em estados terminais.

## Consequências
* **Positivas:** Garantia de integridade do processo; métricas de tempo de atendimento (SLA) mais confiáveis.
* **Negativas:** Menor flexibilidade para correções de erros operacionais imediatos (ex: cancelar por engano).
