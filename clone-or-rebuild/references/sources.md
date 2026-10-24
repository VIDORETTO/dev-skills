# Fontes, inspiração e alcance das evidências

**Data de checagem:** 23/10/2026. Links externos podem mudar; conferir versão do projeto, licença e ferramentas atuais antes de usar. Estas fontes embasam práticas, mas **não provam um único workflow universalmente superior**. Os documentos do pacote são originais e não redistribuem implementações dessas ferramentas.

## Referências oficiais / documentação técnica

1. **Agent Skills — Specification**. Estrutura obrigatória (`SKILL.md` + YAML frontmatter), diretórios opcionais, disclosure progressivo. https://agentskills.io/specification ou https://github.com/agentskills/agentskills/blob/main/docs/specification.mdx
2. **REA — repositório e README oficial.** Propósito, classes de alvo, CLI, MCP, provedores e diferença entre análise local e política do modelo. https://github.com/morluto/rea
3. **REA — skill oficial.** Regra explícita de pular REA para análise comum de repositório com fonte completa; registro de evidências e análise incremental. https://github.com/morluto/rea/blob/main/.agents/skills/reverse-engineer-anything/SKILL.md
4. **REA — evidence workflows.** Proveniência, estados epistêmicos, retenção de registros, análise focada. https://github.com/morluto/rea/blob/main/.agents/skills/reverse-engineer-anything/references/evidence-workflows.md
5. **REA — DISCLAIMER.** Pesquisa lícita, autoridade específica para execução/captura e limites de licenciamento/uso. https://github.com/morluto/rea/blob/main/DISCLAIMER.md
6. **REA — setup e compatibilidade.** Skill-only não registra MCP; capacidades podem variar com a versão instalada. https://github.com/morluto/rea/blob/main/docs/installation.md
7. **Playwright — Visual comparisons.** `expect(page).toHaveScreenshot()` e condições para snapshots reprodutíveis. https://playwright.dev/docs/test-snapshots
8. **Microsoft — Strangler Fig.** Migração progressiva em sistemas legados. https://learn.microsoft.com/pt-br/azure/architecture/patterns/strangler-fig
9. **Ghidra — plataforma de engenharia reversa.** https://github.com/NationalSecurityAgency/ghidra
10. **JADX — decompilação Android.** https://github.com/skylot/jadx
11. **Electron @electron/asar.** Empacotamento/extração ASAR. https://github.com/electron/asar
12. **Frida — instrumentação dinâmica.** https://frida.re/

## Comunidade, experimentos e ressalvas

13. **leanrea (2026), benchmark próprio publicado.** Skill de CLI enxuta comparada com REA 6.5.0 em quatro tarefas, três repetições/variante e um ambiente. Relatou 38% menos tempo e 35% menos custo, mas sem Ghidra/Hopper/JADX instalados, só um modelo/host e ligeira diferença de pontuação. **Conclusão adequada:** CLI pode ser preferível em tarefas simples, não que “REA nunca presta”. https://github.com/aicodeking/leanrea
14. **GitTested (out/2026), review do REA.** Comparação de agente com e sem integração em alvos pequenos; sinal de que a orquestração agrega overhead e nem sempre melhora precisão. **Não generalizar para casos grandes.** https://gittested.com/reviews/morluto-rea/
15. **Casos oficiais do REA, DX-Ball e Notion.** Demonstrações de reconstrução focalizada e inspeção de fluxos, não prova de clonagem completa de apps. https://rea.tools/ e https://rea.tools/showcase/notion/

## Princípios derivados (recomendação autoral do pacote)

- **Source-first**, depois apenas a RE necessária: inferência prática coerente com a regra oficial do REA.
- **Grill-me progressivo**: metodologia de entrevista proposta para esta skill, não um protocolo científico validado.
- **Modelo de pontuação S = 3F+3V+2A+2C+T**: heurística original, não benchmark e não orientação jurídica.
- **Evidence ledger**: esquema simplificado inspirado no tratamento de autoridade/limitações do REA, adaptado a qualquer tipo de projeto.
- **Gates/qualidade**: processo de engenharia recomendado, não garantia universal de resultados.

Não atribua resultados deste pacote ao REA/leanrea nem prometa ganho medido sem benchmark da mesma tarefa, infraestrutura e versão.
