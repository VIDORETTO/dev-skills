---
schema: hybrid/change
schema_version: "1.0"
effort_id: 002-limite-desconto
revision: 1
status: accepted
profile: compact
---

# Change: Limite de desconto

## Objetivo e limites

Impedir que o total de uma compra fique negativo quando o desconto exceder o subtotal. Não inclui alteração de moeda, arredondamento ou regras de autorização.

## Contrato de comportamento

- Entradas: subtotal e desconto na unidade monetária inteira já usada pelo projeto.
- Saída: total mínimo zero.
- Erros/invariantes: valores válidos continuam não negativos.
- Compatibilidade: chamadas e casos existentes permanecem válidos.

## Requisitos e aceite

- **FR-001** — O total calculado nunca pode ser menor que zero.
- **AC-001** — Dado subtotal 1000 e desconto 1200, então o resultado observado é 0.

## Leitura e mapa de alterações

- `src/pricing/discount` → `calculateTotal` — função existente; `tests/pricing/discount` → caso novo.

## Plano breve

Seam: função pública `calculateTotal`. Abordagem: limitar o resultado no contrato da função, preservando a representação monetária existente. Dependências: nenhum.

## Sequência e tarefas

- [ ] C-001 Escrever AC-001 e observar red pelo resultado incorreto.
- [ ] C-002 Implementar o mínimo e observar green.
- [ ] C-003 Executar regressão e registrar evidência.

## Validação e evidência

Comando/procedimento: teste focalizado identificado no projeto.

Resultado executado: pending

Limitações: métrica de negócio não faz parte da entrega. Comando apenas identificado na configuração: registrar separadamente.

## Condição de retorno

Retornar se a unidade monetária, arredondamento ou símbolo observado diferir do contrato.

## Estado

`change.md` é a fonte canônica deste esforço compacto. Não crie `tasks.md` ou tickets paralelos.
