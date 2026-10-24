# 05: Aplicar as mudanças

Só comece depois da aprovação do relatório (salvo se o usuário mandou aplicar direto). Aplique só o que foi aprovado.

## Regras de edição

1. **Mínimo e local.** Troque a linha, o parâmetro ou o parágrafo afetado. Não reorganize arquivos, não renomeie seções, não reescreva o que está certo.
2. **Mesma voz.** Mesma língua, tom, formato de listas e tabelas, convenção de nomes e numeração de arquivos (`NN-nome.md`). Quem lê não deve perceber onde a skill foi remendada.
3. **Todas as ocorrências.** Use `skill_scan.py inventory --json` (ou `grep`) para achar cada lugar onde o item aparece: SKILL.md, referências, scripts, README, exemplos. Versão trocada em um arquivo e esquecida em outro é pior que não trocar.
4. **Onde cada coisa vai:**
   - SKILL.md: regras, fluxo, decisões e ponteiros. Fica enxuto (< 500 linhas).
   - `references/`: detalhes, parâmetros, comparações, passo a passo.
   - `scripts/`: só mude código se a mudança for testada (rode o script) ou se for trivial e verificável (URL, nome de pacote, versão).
   - `description` do frontmatter: atualize quando a skill passar a cobrir ferramentas ou gatilhos novos, ou quando citar algo que foi trocado. Respeite o limite de 1024 caracteres.
5. **Validado fica.** Receita validada só muda com a evidência exigida em [04](04-avaliar-evidencias.md). Novidade promissora entra como alternativa, com: o que é, quando considerar, como testar (A/B), status ("não testado nesta skill").
6. **Marque o status.** Use os termos que a skill já usa ("experimental", "não testado", "validado"); se não houver, use "(não testado nesta skill, AAAA-MM-DD)".
7. **Pins.** Ao atualizar uma versão ou commit fixado, registre de qual para qual e por quê. Se não deu para testar, mantenha o pin e anote a versão nova como candidata.
8. **Nada de origem duvidosa.** Comando, script, URL de instalação ou dependência nova só entra com fonte oficial e nome conferido ([04](04-avaliar-evidencias.md#segurança)).
9. **Nada de datas relativas.** Escreva "em 23/10/2026", nunca "recentemente" ou "a versão mais nova".

## Registro de fontes

Toda atualização deixa rastro dentro da skill:

- Se a skill já tem um arquivo de fontes, estado da arte ou changelog, acrescente uma seção datada nele, no formato que ele já usa, por exemplo `## Usadas na atualização de 23/10/2026`, com as fontes que sustentam cada mudança e uma linha de lacunas (fontes bloqueadas, buscas sem resultado).
- Se não tem, proponha criar um arquivo `fontes.md` em `references/` (ou o nome que combine com a numeração da skill) com: data da revisão, fontes por item e lacunas. Pergunte antes de criar arquivo novo.
- Registre também os itens **Confirmados**: "verificado em 23/10/2026, continua atual". Isso diz ao próximo revisor o que não precisa pesquisar de novo.

## Validar

```bash
python scripts/skill_scan.py validate <pasta-da-skill>   # frontmatter, links relativos, .py e .json
python scripts/skill_scan.py links    <pasta-da-skill>   # links externos, incluindo os novos
```

Depois:

- Rode os testes ou validadores da própria skill, se existirem (ex.: `python scripts/hybrid.py package-validate --json` e `python -m unittest` no Hybrid Spec Kit).
- Rode os scripts que você alterou, ao menos com `--help` ou num caso pequeno.
- Leia o `git diff` inteiro como revisor: algo foi trocado sem fonte? Alguma ocorrência ficou para trás? O SKILL.md cresceu sem necessidade? A língua e o tom batem?
- Se o repositório tem README listando a skill, atualize o que mudou lá (ferramentas, versões, requisitos).

## Entregar

Resumo curto no chat:

- O que mudou (por arquivo), com a fonte principal de cada mudança.
- O que entrou só como alternativa a testar e como testar.
- O que ficou **Incerto** e o que falta para decidir.
- Fontes que ficaram de fora (bloqueio, sem resultado).
- Data sugerida para a próxima revisão, pela volatilidade (alta: 1–3 meses; média: 6 meses; baixa: 12 meses).

Commit só se o usuário pedir, na convenção do repositório (ex.: `docs(<skill>): atualiza fontes e versões (revisão de 2026-10-23)` ou `feat(<skill>): …` quando a skill ganha capacidade nova). Uma skill por commit quando forem várias.
