# ADR 004 — Service Orders V1 Scope

## Status
Proposto

## Contexto
O sistema precisa evoluir de um simples cadastro de clientes para uma ferramenta operacional. O módulo de Ordens de Serviço (OS) é o núcleo dessa evolução.

## Decisão
Implementaremos um MVP (V1) focado no ciclo de vida do status da OS, com as seguintes restrições:
1. **Vínculo Obrigatório:** Toda OS deve estar vinculada a um cliente já cadastrado.
2. **Dados Técnicos:** Foco em descrição do equipamento e problema relatado.
3. **Sem Financeiro:** Não incluiremos campos de custo, preço ou pagamento nesta fase para evitar acoplamento precoce com módulos financeiros não definidos.
4. A V1 não implementará edição geral inicialmente. A necessidade de edição controlada de campos descritivos será avaliada após a implementação do fluxo principal.
5. **Sem Deleção:** OSs não podem ser apagadas fisicamente para preservar o histórico operacional.

## Consequências
* **Positivas:** Entrega rápida do fluxo operacional básico; dados limpos para futuras funcionalidades de BI.
* **Negativas:** Usuários não podem corrigir erros de digitação em equipamentos sem suporte técnico; ausência de valor monetário impede relatórios de faturamento.
