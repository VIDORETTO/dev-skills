# 02: Protocolo de pesquisa

O objetivo não é listar novidades. É responder, com fontes datadas, duas perguntas:

1. **Por item:** o que a skill usa ainda é o certo hoje?
2. **Pelo objetivo:** qual é hoje a melhor forma de fazer o que a skill faz, incluindo o que ela nem cita?

## Ordem das camadas

| Camada | Para quê | Onde |
|---|---|---|
| 1. Oficial | Fatos: versão, mudanças que quebram, descontinuações, recursos novos, preço | Docs, changelog, releases, blog do mantenedor, model card, status de depreciação |
| 2. Técnica | Comparações com números, reproduções | Benchmarks, leaderboards, papers, posts técnicos com código |
| 3. Comunidade | O que funciona na prática, armadilhas, o que as pessoas usam de fato | Reddit, Hacker News, GitHub issues/discussions, Stack Overflow, fóruns do produto, Discourse |
| 4. Redes sociais | O que acabou de sair, sinais precoces, opinião de mantenedores | X, Bluesky, LinkedIn, YouTube, newsletters |

A camada oficial confirma; a comunidade revela. Uma ferramenta nova costuma aparecer primeiro nas camadas 3–4 e só depois ganha documentação. Use as redes sociais para **descobrir** e as camadas 1–2 para **confirmar**.

## Modelos de busca

Buscas curtas (3–7 palavras), específicas e com o ano corrente quando o assunto for volátil. Muitas buscas estreitas rendem mais que uma ampla. Envie as buscas independentes em paralelo.

**Por item (ferramenta, biblioteca, modelo):**
- `<item> changelog` · `<item> release notes <ano>` · `<item> latest version`
- `<item> deprecated` · `<item> breaking changes` · `<item> migration guide`
- `<item> alternative <ano>` · `<item> vs <concorrente>` · `replaced <item> with`
- `<item> not working` · `<item> issue <versão>` · `<item> problems <ano>`

**Pelo objetivo (aberta):**
- `best way to <objetivo> <ano>` · `state of the art <objetivo> <ano>`
- `what are you using for <objetivo>` · `<objetivo> workflow <ano>` (frases de fórum funcionam bem)
- `<objetivo> tips` · `<objetivo> common mistakes` · `<objetivo> lessons learned`
- `site:reddit.com <objetivo>` · `site:news.ycombinator.com <objetivo>` · `site:x.com <item ou objetivo>`
- Na língua do nicho, quando houver: muitos workflows de IA aparecem antes em japonês (note.com, Zenn), chinês (Zhihu, Bilibili) ou coreano.

**Bola de neve:** todo nome novo que aparecer (ferramenta, modelo, técnica, autor) vira uma rodada própria: `<nome> review`, `<nome> vs <atual da skill>`, `<nome> issues`, `<nome> github`. Siga também os autores e mantenedores que aparecem com frequência; o perfil e os repositórios deles costumam ter o próximo passo.

**Critério de parada:** saturação (três buscas seguidas sem nome ou fato novo relevante) ou o orçamento da profundidade escolhida.

## Acesso às fontes sociais

Busca na web indexa mal fóruns e redes recentes. Quando a rede do ambiente permitir, leia as fontes direto pelos endpoints públicos (com `WebFetch`/`web_fetch` ou `curl`). Se algum estiver bloqueado, caia para a busca com `site:` e registre a lacuna.

| Fonte | Como ler |
|---|---|
| **Reddit** | Busca num sub: `https://www.reddit.com/r/<sub>/search.json?q=<termo>&restrict_sr=1&sort=top&t=month` (`t=week|month|year`). Busca geral: `https://www.reddit.com/search.json?q=<termo>&sort=relevance&t=year`. Thread com comentários: acrescente `.json` à URL. Reddit costuma bloquear IPs de nuvem: tente `old.reddit.com` ou `site:reddit.com` na busca |
| **Hacker News** | API Algolia: `https://hn.algolia.com/api/v1/search?query=<termo>&tags=story&numericFilters=created_at_i>` + timestamp Unix do início da janela. Para comentários, `tags=comment`; para os mais recentes, `search_by_date` |
| **GitHub** | Releases e `CHANGELOG.md` do repositório; issues ordenadas por reações (`sort:reactions-+1`) e as recentes; Discussions; busca `https://api.github.com/search/repositories?q=<termo>+pushed:>AAAA-MM-DD&sort=stars`; listas `awesome-<tema>`. Repo arquivado, sem commit há meses ou com issue "is this project dead?" é sinal de troca |
| **Hugging Face** | Model card e aba *Community* (discussões) do modelo; `https://huggingface.co/api/models?search=<termo>&sort=downloads`; página de modelos em alta; `https://huggingface.co/papers` para técnicas novas |
| **X / Twitter** | Quase nunca é lido direto. Use `site:x.com "<termo>"` na busca, procure o perfil dos mantenedores e espelhos de threads (Thread Reader). Trate como pista, nunca como confirmação |
| **YouTube** | Não invente o conteúdo de um vídeo a partir do título. Use transcrição se houver ferramenta/MCP; senão, descrição, comentários fixados e posts que resumem o vídeo |
| **Stack Overflow** | `https://api.stackexchange.com/2.3/search/advanced?q=<termo>&site=stackoverflow&sort=activity&order=desc` |
| **dev.to / Lobsters / Medium / Substack** | Busca com `site:`; dev.to tem `https://dev.to/api/articles?tag=<tag>&top=30` |
| **Discord / Slack / Telegram** | Não são indexados. Procure resumos em issues, blogs e posts que citem a discussão; não afirme o que "dizem no Discord" sem ter lido |

## Recência

- Confira a data de **cada** fonte. Página sem data é evidência fraca.
- Desconfie de "best X of <ano passado>" e de páginas atualizadas só no título.
- Para modelos e ferramentas de IA, verifique a data do último commit, da última release ou da última atualização do model card.
- Quando a busca devolver material velho ou raso, troque os termos, adicione o mês/ano ou use o modo de busca mais profundo/recente da ferramenta.

## Teste prático (quando possível, vale mais que ler)

- `pip index versions <pacote>`, `pip install --dry-run <pacote>==<versão>`, `npm view <pacote> versions --json`.
- Instalar a versão nova num venv ou sandbox e rodar o script ou comando da skill afetado.
- Rodar `--help` da CLI para conferir se as flags citadas ainda existem.
- Abrir o link e ver se a página ainda diz o que a skill afirma que ela diz.

## Registro das fontes

Mantenha, no arquivo de trabalho, uma tabela organizada por item (não por fonte):

```markdown
| Item | Achado | Fonte (URL) | Tipo | Data da fonte | Acesso |
|---|---|---|---|---|---|
| faster-whisper | 1.2.1 é a última (out/2025); projeto parado? | https://pypi.org/project/faster-whisper/ | oficial | 2025-10-31 | 2026-10-23 |
```

Uma afirmação forte (trocar ferramenta, mudar parâmetro validado) precisa de pelo menos duas fontes independentes ou de uma oficial mais um teste.
