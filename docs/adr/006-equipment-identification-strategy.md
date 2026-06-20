# ADR 006 — Equipment Identification Strategy

## Status
Proposto

## Contexto
Clientes frequentemente trazem múltiplos dispositivos do mesmo modelo (ex: dois "iPhone 13" pretos). Apenas os campos Marca e Modelo não são suficientes para a identificação inequívoca do ativo na bancada.

## Decisão
Adicionaremos o campo `equipment_identification` à entidade `ServiceOrder`:
1. **Formato:** String de texto livre (opcional).
2. **Uso:** Destinado a Número de Série, IMEI, Tag de Patrimônio ou descrição física distintiva.
3. **Persistência:** O campo será armazenado na tabela de OS e não em uma tabela separada de "Equipamentos", simplificando a V1.

## Consequências
* **Positivas:** Redução de erros de troca de aparelhos entre clientes; flexibilidade para diferentes tipos de dispositivos (eletrônicos, ferramentas, etc.).
* **Negativas:** Por ser um campo de texto livre, pode haver inconsistência na entrada de dados (ex: um usuário digita "S/N: 123" e outro apenas "123").
