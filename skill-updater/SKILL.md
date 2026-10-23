---
name: skill-updater
description: >-
  Atualiza skills existentes (pastas com SKILL.md) para o estado da arte atual.
  Entende o objetivo de cada skill, inventaria o que ela usa (ferramentas,
  modelos, bibliotecas, versões, técnicas, comandos, links), pesquisa na web,
  em fóruns e redes sociais (Reddit, Hacker News, X, GitHub, Hugging Face,
  YouTube, blogs) o que mudou e o que há de melhor hoje, avalia as evidências e
  aplica mudanças mínimas e verificadas, com relatório e fontes datadas. Use
  quando o usuário pedir para "atualizar a skill", "modernizar/revisar uma
  skill", "deixar a skill em dia", "ver se a skill está desatualizada",
  "pesquisar novidades para a skill", "auditar minhas skills", "update/refresh
  skill", ou apontar uma pasta de skills e perguntar o que mudou. Serve para uma
  ou várias skills, de qualquer domínio (código, DevOps, IA generativa, prompts,
  educação, documentação).
---

# Skill Updater

Uma skill é uma fotografia do que era a melhor forma de fazer algo **na data em que foi escrita**. Ferramentas novas aparecem, modelos são substituídos, bibliotecas quebram a API, links morrem e a comunidade descobre técnicas melhores. Esta skill renova essa fotografia: entende para que a skill serve, descobre o que ficou velho, pesquisa o que existe de melhor **hoje** e atualiza a skill sem destruir o que já foi validado.

O processo é sempre o mesmo, mas o conteúdo é dinâmico: o domínio da skill, o repositório onde ela vive e o que ela cita decidem onde pesquisar e o que vale mudar.

## Regras de ouro (e por quê)

1. **Leia a skill inteira antes de pesquisar.** SKILL.md, todas as referências, scripts e assets. Sem entender o objetivo, a pesquisa vira uma lista de novidades irrelevantes.
2. **A data de hoje é a âncora.** Anote-a no início e defina a janela de recência pelo ritmo do domínio ([01](references/01-entender-a-skill.md#volatilidade)). Inclua o ano nas buscas e confira a data de cada fonte.
3. **Não use a memória do modelo como fonte do que é atual.** O conhecimento de treino é exatamente o que está desatualizado. Toda afirmação de "novo", "melhor" ou "obsoleto" precisa de uma fonte com data. Sem ferramenta de busca disponível, pare e avise o usuário; não "atualize" de memória.
4. **Oficial > reprodução com números > vários relatos independentes > relato isolado.** Hype, post viral e listicle de SEO não são evidência ([04](references/04-avaliar-evidencias.md)).
5. **O que a skill validou em uso real só cai com evidência mais forte.** Uma receita testada (casos, logs de falha, "validado em N rodadas") não é trocada por uma promessa da internet. A novidade entra como alternativa a testar (A/B), com o critério de quando trocar.
6. **Pins intencionais não são atualizados no automático.** Commit fixado, versão travada "porque a nova quebrou": antes de mexer, confirme se o motivo do pin ainda vale.
7. **Mudança mínima, na voz da skill.** Mesma língua, estrutura, numeração de arquivos e estilo. Não reescreva o que está certo, não infle o SKILL.md (alvo < 500 linhas; detalhe vai para `references/`).
8. **Relatório antes de editar.** Mostre os achados e o plano de mudanças e espere a aprovação, salvo se o usuário mandou aplicar direto.
9. **Tudo com fonte e data.** Cada mudança aplicada fica registrada no arquivo de fontes da skill, com a data da revisão.
10. **Valide depois de editar.** Frontmatter, links, scripts, JSON e os testes da própria skill. Quando der, teste a novidade de verdade (instalar a versão nova, rodar o comando) em vez de só ler sobre ela.

## Fluxo

| Fase | O que acontece | Detalhes |
|---|---|---|
| 0. Escopo | Quais skills, modo (só relatório ou aplicar), profundidade, janela de recência | Abaixo |
| 1. Entender | Perfil da skill: objetivo, domínio, eixos voláteis, o que é validado, pins | [01](references/01-entender-a-skill.md) |
| 2. Inventário | `skill_scan.py inventory`, `latest` e `links` | Abaixo |
| 3. Contexto | Repositório onde a skill vive ou que ela atende: stack, versões em uso, convenções | Abaixo |
| 4. Plano de pesquisa | Perguntas por item volátil + perguntas abertas sobre o objetivo; fontes pelo domínio | [02](references/02-pesquisa.md), [03](references/03-fontes-por-dominio.md) |
| 5. Pesquisa | Oficial → comunidade → redes sociais, em paralelo, até saturar | [02](references/02-pesquisa.md) |
| 6. Avaliar | Classificar cada achado e dar confiança e impacto | [04](references/04-avaliar-evidencias.md) |
| 7. Relatório | Achados, mudanças propostas e o que fica igual; pedir aprovação | [modelo](assets/relatorio-atualizacao.md) |
| 8. Aplicar | Edições mínimas + registro de fontes datado | [05](references/05-aplicar-mudancas.md) |
| 9. Validar e entregar | `skill_scan.py validate`, testes da skill, diff revisado, commit se pedido | [05](references/05-aplicar-mudancas.md#validar) |

### Fase 0: Escopo

Extraia do pedido o que já estiver claro e pergunte só o que falta, numa única rodada:

- **Alvo:** uma skill, várias, ou uma pasta inteira. Para várias, faça a triagem da Fase 2 e comece pelas mais velhas e mais voláteis.
- **Modo:** `relatório` (só diagnosticar) ou `aplicar` (relatório + edições após aprovação). Padrão: `aplicar` com aprovação.
- **Profundidade:**
  - `rápida` (~10–15 buscas): versões, links, mudanças que quebram, descontinuações.
  - `padrão` (~25–40 buscas): o acima + alternativas melhores para cada ferramenta e técnicas novas para o objetivo.
  - `profunda` (60+ buscas): o acima + mudanças de paradigma, sentimento da comunidade, benchmarks e testes práticos.
- **Janela de recência:** desde a última revisão da skill (data no git ou no arquivo de fontes), limitada pela volatilidade do domínio.

### Fase 2: Inventário automático

O script coleta fatos sem modelo, só com a biblioteca padrão do Python. Rode-o da pasta desta skill (ou passe o caminho completo):

```bash
python scripts/skill_scan.py inventory <pasta-da-skill-ou-de-várias>          # o que a skill cita e quão velha está
python scripts/skill_scan.py latest    <pasta-da-skill> [--max 60]             # versão/data atual no PyPI, npm, GitHub, Hugging Face
python scripts/skill_scan.py links     <pasta-da-skill>                        # status HTTP de cada link externo
```

- `inventory` lista links, repos do GitHub e do Hugging Face, pacotes instalados ou importados, versões fixadas, commits fixados, nomes de modelos/ferramentas (candidatos, com ruído), datas citadas e a idade de cada arquivo no git. Com uma pasta de várias skills, abre com uma tabela ordenada pela mais velha: é a triagem.
- `latest` mostra a versão e a data atuais do que foi encontrado. É o ponto de partida da pesquisa, não a conclusão: versão nova não significa que a skill deve adotá-la.
- `links` separa links quebrados, redirecionados e placeholders. 403/429 costuma ser anti-bot, e "Tunnel connection failed" é bloqueio da rede do ambiente: confirme antes de chamar de link morto.
- Todos aceitam `--json`. Exporte `GITHUB_TOKEN` para evitar o limite de 60 chamadas/hora da API do GitHub.

O script não vê técnicas, conselhos, parâmetros e julgamentos escritos em prosa. Esses saem da leitura da Fase 1.

### Fase 3: Contexto do repositório

A melhor ferramenta depende de onde a skill é usada. Antes de pesquisar:

- Veja o repositório onde a skill está (README, outras skills, convenções de commit, scripts de teste) e, se a skill atende um projeto específico, os manifestos dele (`package.json`, `pyproject.toml`, `requirements*.txt`, `Dockerfile`, `go.mod`, `Cargo.toml`, CI) para saber versões, runtime, sistema operacional e restrições reais.
- Note o host de agente em uso (Claude Code, Codex, Cursor, etc.) e as ferramentas disponíveis (MCPs, busca, GPU, nuvem). Uma "melhor ferramenta" que o usuário não pode rodar não é a melhor para ele.
- Respeite decisões registradas (ADRs, notas "não usar X porque…"). Elas são evidência local, e às vezes mais forte que a da internet.

### Fases 4 a 6: Pesquisar e avaliar

Siga [02-pesquisa.md](references/02-pesquisa.md) e use [03-fontes-por-dominio.md](references/03-fontes-por-dominio.md) para escolher onde procurar. Em resumo:

1. Para cada item volátil do perfil, pergunte: ainda existe? mudou? quebrou? há algo claramente melhor? o que a comunidade usa hoje?
2. Para o objetivo da skill como um todo, pergunte de forma aberta: "qual é hoje a melhor forma de <objetivo>?", "o que as pessoas estão usando para <objetivo>?". É aqui que aparecem as ferramentas e técnicas que a skill nem cita.
3. Faça bola de neve: cada nome novo encontrado vira busca de `review`, `problemas`, `vs <atual>` e `issues`.
4. Pare por saturação (as buscas novas só repetem nomes já vistos) ou pelo orçamento da profundidade.
5. Classifique cada achado ([04](references/04-avaliar-evidencias.md)): **Quebrado**, **Obsoleto**, **Superado**, **Novo**, **Confirmado** ou **Incerto**, com confiança e impacto.

Se o host permitir subagentes e o usuário concordar, divida a pesquisa por eixo (ferramentas, técnicas, ecossistema/comunidade) e consolide os achados aqui.

### Fase 7: Relatório

Use [assets/relatorio-atualizacao.md](assets/relatorio-atualizacao.md). Em resumo: um veredito de uma linha, a tabela de achados com fonte e data, as mudanças propostas por arquivo, o que **não** muda e por quê, e o que fica para testar. Mostre no chat. Para várias skills, um relatório por skill e um resumo no topo. No modo `relatório`, o trabalho termina aqui.

### Fases 8 e 9: Aplicar, validar e entregar

Siga [05-aplicar-mudancas.md](references/05-aplicar-mudancas.md). Depois de editar:

```bash
python scripts/skill_scan.py validate <pasta-da-skill>
python scripts/skill_scan.py links    <pasta-da-skill>
```

Rode também os testes e validadores da própria skill, se existirem. Entregue um resumo curto: o que mudou, o que foi só registrado como alternativa, o que ficou incerto e a data sugerida para a próxima revisão. Faça commit apenas se o usuário pedir, seguindo a convenção do repositório.

## Ferramentas

| Necessidade | Ferramenta |
|---|---|
| Busca na web | `WebSearch` (Claude Code) ou `web_search` (claude.ai). Para notícias recentes e nichos, use o modo mais profundo/estendido quando houver |
| Ler páginas e APIs públicas | `WebFetch` ou `web_fetch`; Reddit, Hacker News e Hugging Face têm endpoints JSON ([02](references/02-pesquisa.md#acesso-às-fontes-sociais)) |
| GitHub | MCP do GitHub, `gh` ou API pública: releases, changelog, issues, discussions, busca de repositórios |
| Fatos determinísticos | `scripts/skill_scan.py` (`inventory`, `latest`, `links`, `validate`) |
| Teste prático | Shell e venv/sandbox para instalar a versão nova e rodar o comando ou script afetado |

Se a rede do ambiente bloquear alguma fonte, diga qual ficou de fora no relatório. Lacuna declarada é melhor que cobertura inventada.
