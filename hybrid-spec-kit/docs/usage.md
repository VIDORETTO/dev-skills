# Uso operacional

## Iniciar um projeto

Depois da instalação, leia as instruções existentes do projeto antes de criar arquivos. Use `$hybrid-start` com a demanda. Para preparar o layout local, execute:

```text
python .hybrid/hybrid.py init --project . --mode standard --json
```

Crie `docs/project/vision.md` somente para planejamento de produto, `roadmap.md` somente quando houver marcos, e `CONTEXT.md`/ADRs somente quando o domínio exigir. Um projeto novo começa pelo resultado que testa a hipótese mais importante; não pré-crie infraestrutura sem consumidor.

## Planejar uma funcionalidade

1. `$hybrid-discover` registra problema, consumidor, limites, hipóteses, evidências e decisões materiais. Perguntas independentes podem ser agrupadas; perguntas que mudam comportamento aguardam resposta.
2. `$hybrid-domain` atualiza o vocabulário e ADRs seletivos. O glossário não recebe solução técnica.
3. `$hybrid-specify` escreve `spec.md` com `FR`/`AC` estáveis, erros, limites, escopo e sucesso. Para uma função pequena, escolha `change.md` compacto.
4. `$hybrid-plan` lê código e testes, escolhe Modules/Interfaces/Seams e registra abordagem, compatibilidade, riscos, obrigações e comandos de verificação. Use Context7 para documentação atual de uma dependência relevante.
5. `$hybrid-slice` cria tickets verticais. Cada ticket tem o pacote completo para uma sessão nova: objetivo, exclusões, leitura, símbolos existentes/novos, decisões, contrato, exemplos, dependências, sequência, validação e retorno.
6. `$hybrid-check --mode consistency` verifica as relações antes da execução. Corrija o artefato proprietário; não mude aceites para acomodar um ticket errado.

O script calcula o próximo ID, valida referências e detecta ciclos:

```text
python .hybrid/hybrid.py next-id --project . --effort 014-feature --prefix TK --json
python .hybrid/hybrid.py validate --project . --effort 014-feature --json
python .hybrid/hybrid.py graph --project . --effort 014-feature --json
```

## Selecionar o próximo marco e continuar em outra sessão

Depois de aceitar contrato/plano e preparar os tickets, execute:

```text
python .hybrid/hybrid.py session --project . --effort 014-feature --write --json
```

A saída inclui `selected_tickets`, dependências condicionais `requires_selected_done`, `limits`, `ticket_growth`, `goal_objective` e `continuation_prompt`. O padrão é até três tickets relacionados; um ticket ativo em andamento fica sozinho até sua conclusão real. Use `--max-tickets 1` para uma fatia grande e `--minutes 15` para uma janela menor. A seleção depende de contrato aceito, plano pronto e checkpoint ativo, mas não substitui `package` nem o julgamento de escopo.

`--write` cria uma projeção protegida em `.hybrid/continuations/<effort>.md`. Sua edição manual é preservada pelo controle de conflitos. A quantidade de tickets da primeira geração é mantida como baseline; `--baseline-tickets <n>` permite registrar uma quantidade original conhecida na migração, sem apagar IDs nem redefinir uma baseline existente silenciosamente. Crescimento acima de 20% emite alerta para reconciliação antes de novos tickets, sem esconder correções obrigatórias.

Crie Goal somente quando solicitado, usando o objetivo limitado proposto: cumprir aceites/revisão do marco ou entregar checkpoint verdadeiro ao chegar ao limite. Ao fim, registre o resultado e cole o prompt curto numa sessão nova. Tickets e esforço continuam pendentes quando a entrega foi parcial. O runner sugere a agenda; tempo/contexto são política do agente, sem watchdog ou abertura automática de sessões.

Reutilize verificações/evidências ainda válidas, concentre checkpoints por comportamento/bloco e execute os gates globais no momento exigido. Planejamento, implementação e avaliação externa longa são marcos separados. A [política completa](../shared/references/bounded-execution.md) define limites, escopo, correções, compactação e conclusão honesta.

## Executar um ticket sem a conversa original

Passe à executora:

- o ticket `TK-xxx` e sua revisão;
- `spec.md`/`plan.md` nas revisões referenciadas;
- os arquivos de domínio/ADR explicitamente listados;
- os caminhos e símbolos da “Leitura em ordem”;
- dependências satisfeitas e comando/procedimento de validação;
- somente os limites de edição de `owned_areas` necessários à fatia.

O comando de pacote mostra a prontidão e os campos que o consumidor seguinte encontra:

```text
python .hybrid/hybrid.py package --project . --effort 014-feature --ticket TK-003 --json
```

`ready: true` exige contrato `accepted`, plano `ready`, revisões atuais, blockers satisfeitos e o pacote completo. Se não estiver pronto, leia `errors`, preserve o trabalho e devolva a lacuna à planejadora.

A executora começa com `ready`, passa a `in_progress`, executa um caso comportamental por vez e registra o trabalho concluído. Ela pode escolher nomes locais reversíveis. Se o caminho, contrato, dependência, modelo de dados ou autorização não bastar, deve preservar teste/progresso e devolver: ticket, passo, evidência, trabalho concluído, decisão necessária e impacto.

## Verificar e revisar

Use `$hybrid-verify` para executar os comandos reais e registrar `EV-xxx`. Um resultado observado na configuração não é execução. Use `$hybrid-review` para fixar um baseline e fazer dois passes:

- Standards: regras documentadas e riscos de desenho contextualizados;
- Spec: comportamento faltante, parcial, incorreto ou fora do escopo.

Inclua commits, staged, unstaged e arquivos novos relevantes. Review-only produz relatório e não corrige nem publica comentários. `$hybrid-check --mode convergence` procura aceites sem evidência atual e tickets concluídos sem gate.

Em uma mudança compacta, mantenha tarefas e evidência em `change.md` quando isso for suficiente. Se precisar de um registro estruturado para a verificação, use `evidence add` sem `--ticket`; o runner aceita essa forma somente para esforços compactos e não cria `todo.md`. Resultados executados exigem um `--path` existente para vincular a evidência ao código ou artefato observado.

## Estado e fontes

No perfil padrão, edite apenas o ticket para estado/tarefas da execução; regenere `todo.md`. Edite a origem do esforço para comportamento/plano; regenere `backlog.md` quando os esforços mudarem. `state.json` só registra posição, revisões, baseline, insumos e próxima ação. No compacto, `change.md` é a única fonte de contrato e tarefas.

As projeções geradas possuem hash em `.hybrid/generated.json`. Se alguém editou uma projeção, o runner retorna conflito para que a edição seja reconciliada; ele não a apaga por hábito. Checkpoints usam revisão otimista:

```text
python .hybrid/hybrid.py checkpoint write --project . --effort 014-feature --expected-revision 8 --phase implementation --next-action "Executar AC-003" --json
```

Quando um plano ou outro insumo canônico passa a existir, registre seu caminho e fingerprint no checkpoint: `python .hybrid/hybrid.py checkpoint write --project . --effort 014-feature --expected-revision 9 --input plan=specs/014-feature/plan.md --json`.
