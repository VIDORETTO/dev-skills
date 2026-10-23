# 03: Fontes por domínio

Ponto de partida para escolher onde pesquisar. Não é uma lista fechada: as fontes que a própria skill já cita (e os autores que aparecem na bola de neve) costumam ser as melhores. Comunidades e sites mudam; se algum estiver parado ou tiver sumido, substitua e registre.

## Mapa

| Domínio | Oficial / técnica | Comunidade | Social e sinais precoces |
|---|---|---|---|
| **IA generativa de imagem, vídeo e áudio** (ComfyUI, LoRAs, modelos abertos) | Model cards e aba Community no Hugging Face, repositórios dos nós/workflows no GitHub, docs do ComfyUI, papers (HF Papers, arXiv) | r/StableDiffusion, r/comfyui, r/aivideo, r/LocalLLaMA (modelos abertos em geral), Civitai (workflows e comentários), issues dos repositórios | X dos autores de LoRAs/nós, comfyui-wiki (notícias), note.com/Zenn (comunidade japonesa), Bilibili/Zhihu, YouTube de criadores de workflows |
| **LLMs, agentes e engenharia de prompt** | Docs e guias de prompt dos provedores (Anthropic, OpenAI, Google), changelogs de API, model deprecations, leaderboards (LMArena, Artificial Analysis, SWE-bench, Aider) | r/ClaudeAI, r/LocalLLaMA, r/PromptEngineering, r/ChatGPTCoding, Hacker News, GitHub de frameworks de agentes | X de pesquisadores e devrels dos provedores, newsletters de IA, Simon Willison (blog), Latent Space |
| **Skills e agentes de código** (o formato das próprias skills) | Especificação Agent Skills (agentskills.io), docs de skills do Claude Code e do Codex, repositórios oficiais de skills de exemplo | r/ClaudeAI, r/ClaudeCode, r/cursor, r/ChatGPTCoding, Hacker News, repositórios `awesome-*-skills` | X dos times de produto, changelogs do Claude Code/Codex/Cursor |
| **Desenvolvimento web e front-end** | Docs e blogs oficiais (React, Next.js, Vite, Node), MDN, State of JS/CSS, Baseline/caniuse | r/webdev, r/reactjs, r/javascript, r/node, Hacker News, Stack Overflow, GitHub Discussions | X/Bluesky de mantenedores, newsletters (JavaScript Weekly, Bytes) |
| **Back-end e linguagens** (Python, Go, Rust, Java…) | Release notes da linguagem, PEPs, changelogs de frameworks, PyPI/crates/npm | r/Python, r/golang, r/rust, r/java, Hacker News, Stack Overflow, Lobsters | Mantenedores no X/Bluesky/Mastodon, Python Weekly, Golang Weekly |
| **DevOps, VPS, infraestrutura e cloud** | Docs de Docker, Nginx, Caddy, Certbot/Let's Encrypt, PM2, systemd, distribuições (Ubuntu/Debian release notes), provedores de cloud, endoflife.date | r/selfhosted, r/sysadmin, r/devops, r/docker, r/homelab, r/kubernetes, Server Fault, Hacker News | Status pages e blogs de engenharia, newsletters de DevOps |
| **Segurança** | CVE/NVD, avisos de segurança do GitHub, OWASP, CISA KEV, avisos das distribuições | r/netsec, r/cybersecurity, r/sysadmin, Hacker News | Pesquisadores no X/Bluesky/Mastodon |
| **Dados e ML clássico** | Docs de pandas, Polars, DuckDB, scikit-learn, Spark, dbt; papers | r/dataengineering, r/datascience, r/MachineLearning, Kaggle (discussões) | Newsletters de dados, X de mantenedores |
| **Mobile** | Docs Android/iOS/Flutter/React Native e notas de versão das lojas | r/androiddev, r/iOSProgramming, r/FlutterDev, r/reactnative | X de devrels das plataformas |
| **Automação e no-code** | Docs de n8n, Make, Zapier e changelogs | r/n8n, r/nocode, fóruns oficiais (community.n8n.io) | YouTube de criadores de automação |
| **Educação e design instrucional** | Literatura de aprendizagem (Mayer, Bloom revisada), docs de plataformas (Moodle, plataformas de cursos), relatórios do setor | r/instructionaldesign, r/elearning, r/Teachers | LinkedIn de designers instrucionais, newsletters de L&D |
| **Documentação e escrita técnica** | Guias de estilo (Google, Microsoft), Diátaxis, docs do GitHub sobre README e Markdown, shields.io | r/technicalwriting, Write the Docs (comunidade), Hacker News | Newsletters de docs |
| **Marketing, conteúdo e SEO** | Documentação do Google Search Central, políticas das plataformas, changelogs de ferramentas | r/SEO, r/marketing, r/content_marketing | X/LinkedIn de profissionais do setor; muito hype, exija dados |

## Como escolher

1. Comece pelas fontes que a skill já cita (arquivo de fontes, links nas referências). Elas mostram em que o autor confia.
2. Adicione 1–2 fontes oficiais e 2–3 comunidades por eixo volátil do perfil.
3. Se a skill cruza domínios (ex.: uma skill de VPS que instala Node), pesquise cada eixo no seu próprio domínio.
4. Para domínios muito nichados, encontre a comunidade certa com `"<nicho>" subreddit`, `"<nicho>" discord`, `"<nicho>" forum` e com os autores mais citados.
