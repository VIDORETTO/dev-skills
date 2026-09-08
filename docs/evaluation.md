# Avaliação

## Como interpretar os resultados

`deterministic` mede apenas o que o runner consegue comprovar: estrutura, IDs, referências, grafo, projeções, checkpoint, fingerprints e deduplicação. `behavioral` exige observar uma IA escolhendo e executando a rota; não é aprovado pela presença de uma regra no `SKILL.md` ou por um schema válido.

Nesta construção, os checks determinísticos locais foram executados para o pacote, para os exemplos e para fixtures temporários. Os subchecks determinísticos cobertos diretamente são E03, E12, E14, E15, E19, E22, E27, E28 e E31. Não houve segundo modelo/contexto autorizado para executar a avaliação comportamental; portanto os casos que exigem decisão ou execução de uma IA estão `pending_model`. A economia, superioridade e comparação contra Spec Kit/Matt permanecem sem medição.

## Procedimento reproduzível

```powershell
python scripts/hybrid.py package-validate --json
python -m unittest discover -s tests -v
```

O relatório da execução atual, incluindo a revisão testada e a limitação de cada caso, está em [`validation-report.md`](validation-report.md).

Para avaliação comportamental, o avaliador deve fornecer à executora somente o `input` de cada caso em `examples/evaluation/cases.json`, o pacote instalado e as referências que o caso autoriza. Deve guardar o `expected` fora do contexto da executora, registrar o modelo/versão, contexto, tempo, perguntas, alterações, comandos realmente executados e resultado contra o critério. Não simular publicação remota para E20.

## Matriz E01–E31

| Caso | Tipo | Determinístico local | Avaliação comportamental | Limitação |
| --- | --- | --- | --- | --- |
| E01 | rota de ideia vaga | preparado | pendente | exige julgamento de descoberta |
| E02 | compacto | preparado | pendente | exige escolha proporcional |
| E03 | legado/alterações locais | passado | pendente | check local cobre baseline Git e preservação de alterações reportadas; decisão da IA sobre escopo continua humana/modelo |
| E04 | artefatos aceitos | preparado | pendente | exige não repetir gates |
| E05 | ambiguidade crítica | preparado | pendente | exige pergunta material |
| E06 | campo editorial | preparado | pendente | exige autonomia contextual |
| E07 | bug | preparado | pendente | exige reprodução/correção |
| E08 | oráculo tautológico | preparado | pendente | exige avaliar teste e implementação |
| E09 | migração | preparado | pendente | exige sequenciamento real |
| E10 | interrupção | preparado | pendente | exige executar e retomar |
| E11 | mudança de spec | preparado | pendente | exige reconciliação sem reuso cego |
| E12 | código após evidência | passado | pendente | check local cobre fingerprint e invalidação de evidência; a classificação semântica continua humana/modelo |
| E13 | review com arquivo novo | preparado | pendente | exige diff completo |
| E14 | requisito omitido | passado | pendente | check local cobre aceite sem evidência corrente; não avalia a decisão da executora |
| E15 | deduplicação | passado | pendente | check local cobre apenas chave/estado |
| E16 | verificação indisponível | preparado | pendente | exige honestidade da executora |
| E17 | review-only | preparado | pendente | exige não editar/publicar |
| E18 | checklist de reviewer | preparado | pendente | exige ownership |
| E19 | contrato compartilhado | passado | pendente | check local cobre detecção de `owned_areas` sobrepostas; coordenação efetiva continua avaliação comportamental |
| E20 | timeout de tracker | não aplicável | não aplicável | adapter remoto não incluído |
| E21 | carregamento progressivo | preparado | pendente | exige medir contexto da execução |
| E22 | reexecução sem mudanças | passado | pendente | check local cobre projeção sem-op |
| E23 | métrica pós-entrega | preparado | pendente | exige separar observação de teste |
| E24 | cancelamento/mudança | preparado | pendente | exige preservar checkpoint |
| E25 | pacote sem conversa | preparado | pendente | exige segunda IA/contexto |
| E26 | caminho desatualizado | preparado | pendente | exige retorno focalizado |
| E27 | candidato não refinado | passado | pendente | check local cobre backlog/todo derivados; promoção ainda exige avaliação de prontidão |
| E28 | AC alterado | passado | pendente | check local cobre revisão de contrato, fingerprint/evidência e reabertura do ticket |
| E29 | esperado enfraquecido | preparado | pendente | exige review semântico |
| E30 | mesma IA nos dois papéis | preparado | pendente | exige preservar separação de artefatos |
| E31 | projeções derivadas | passado | pendente | check local cobre geração/hash |

`passed` acima significa somente o subcheck determinístico descrito na limitação. Não significa que o cenário comportamental esteja aprovado.
