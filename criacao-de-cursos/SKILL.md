---
name: criacao-de-cursos
description: >-
  Use sempre que o usuário pedir para criar, estruturar ou desenvolver um curso,
  treinamento, trilha de aprendizagem, aula, workshop ou material didático sobre
  qualquer assunto — mesmo sem conhecimento prévio profundo do tema no contexto
  atual. Dispare para "crie um curso sobre X", "monte uma trilha de aprendizado",
  "estruture um treinamento completo", ou qualquer pesquisa profunda (deep
  research) visando produzir conteúdo educacional com módulos, exemplos, imagens,
  quizzes e exercícios. Cobre o pipeline completo: pesquisa multi-fonte (artigos,
  fóruns, blogs, vídeos do YouTube, papers, cursos concorrentes), síntese de
  conhecimento, arquitetura curricular, objetivos de aprendizagem (Bloom), design
  instrucional aula a aula, curadoria de mídia, avaliações interativas, revisão de
  qualidade e empacotamento final (docx, pptx ou markdown). Use mesmo para temas
  muito nichados ou técnicos — a pesquisa profunda é parte do processo.
---

# Criação de Cursos com Pesquisa Profunda

## Filosofia

Não é preciso ser especialista no tema para criar um curso excelente — mas é preciso **pesquisar como um especialista pesquisaria**, e depois **ensinar como um bom professor ensina**. Essas são duas habilidades distintas e esta skill trata das duas separadamente: primeiro construir conhecimento real e verificado sobre o tema (Fases 1-2), depois transformar esse conhecimento em uma experiência de aprendizagem bem desenhada (Fases 3-9).

O erro mais comum ao gerar cursos com IA é pular direto para escrever aulas a partir do conhecimento genérico que já se tem sobre o assunto. Isso produz cursos rasos, genéricos e que não resolvem as dúvidas reais que as pessoas têm. Esta skill existe para evitar esse atalho: force a pesquisa antes da escrita.

## Visão geral do pipeline

O processo tem 10 fases. As fases 1, 2, 5 e 6 têm guias detalhados em `references/` — leia o arquivo correspondente quando chegar nessa fase, não tente reconstruir os detalhes de memória.

| Fase | O que acontece | Onde estão os detalhes |
|---|---|---|
| 0. Escopo | Definir tema, público, nível, formato de entrega, duração alvo | Seção "Fase 0" abaixo |
| 1. Pesquisa profunda | Buscar em artigos, fóruns, YouTube, papers, cursos concorrentes; extrair FAQ real, erros comuns, glossário | `references/01-pesquisa-profunda.md` |
| 2. Síntese e arquitetura | Mapear conceitos, sequenciar por dependência, desenhar de trás para frente (backward design) | `references/02-sintese-arquitetura.md` |
| 3. Objetivos de aprendizagem | Escrever objetivos testáveis por módulo usando Taxonomia de Bloom | `references/03-objetivos-design-instrucional.md` |
| 4. Design instrucional das aulas | Estruturar cada aula (gancho, explicação, exemplo, contra-exemplo, checagem, recap) | `references/03-objetivos-design-instrucional.md` |
| 5. Curadoria de mídia | Decidir onde imagem/diagrama ajuda de verdade; buscar ou gerar | `references/04-midia-interatividade.md` |
| 6. Interatividade e avaliação | Quizzes, exercícios, projeto integrador | `references/04-midia-interatividade.md` |
| 7. Revisão de qualidade | Fact-check, checagem de progressão, jargão, direitos autorais | `references/05-qualidade-empacotamento.md` |
| 8. Empacotamento final | Formatar no output certo (docx/pptx/markdown), sumário, glossário, referências | `references/05-qualidade-empacotamento.md` |
| 9. Loop de feedback | Definir métricas de sucesso e pontos de revisão pós-lançamento | Seção "Fase 9" abaixo |

## Fase 0 — Escopo (sempre primeiro, nunca pular)

Antes de pesquisar qualquer coisa, você precisa de respostas para isto. Se o usuário já deu essas informações no pedido original, extraia-as em vez de perguntar de novo — só pergunte o que realmente falta, e prefira uma única rodada de perguntas a várias:

1. **Tema exato e nível** — iniciante absoluto, intermediário ou avançado? Isso muda o vocabulário, a profundidade e os pré-requisitos assumidos.
2. **Público-alvo** — quem é, o que já sabe, por que quer aprender isso, quanto tempo tem disponível por semana.
3. **Transformação prometida** — uma frase única: "ao final, o aluno será capaz de ___". Essa frase guia todas as fases seguintes; se não conseguir escrevê-la com clareza, o escopo ainda não está definido.
4. **Formato de entrega** — texto corrido/handbook (docx), apresentação de slides (pptx), curso web navegável (markdown/html), ou roteiro de vídeo-aulas. Isso determina qual skill de output usar na Fase 8.
5. **Duração alvo** — número de módulos e tempo estimado por módulo. Funciona como orçamento de conteúdo: evita tanto um curso raso demais quanto um curso infinito que nunca termina.

Não avance para a pesquisa com escopo ambíguo. Um curso "sobre Python" pode ser um curso de 2 horas para quem nunca programou ou um curso de 40 horas de Python avançado para desenvolvedores — são pesquisas, estruturas e tons completamente diferentes.

## Fase 9 — Loop de feedback

Isso só se aplica se o curso for algo que o usuário vai manter/atualizar (não um one-off). Se relevante, feche a entrega sugerindo:
1. Métricas de sucesso simples (taxa de conclusão por módulo, nota média em quiz, percepção qualitativa).
2. Um ponto de revisão natural — normalmente 4-8 semanas após o lançamento, quando dúvidas recorrentes dos alunos revelam lacunas que a pesquisa original não cobriu.

Não é preciso implementar nada disso automaticamente — apenas deixar essa recomendação registrada no material final, como uma nota para o criador do curso.

## Ferramentas por fase (ambiente Claude.ai / Claude Code / Cowork)

| Fase | Ferramentas recomendadas |
|---|---|
| Pesquisa (1) | `web_search`, `web_fetch`; se houver conector MCP de YouTube/transcrição disponível, use-o — senão siga o fallback descrito em `references/01-pesquisa-profunda.md` |
| Síntese/Arquitetura (2) | Nenhuma ferramenta externa — é trabalho de raciocínio sobre o material já coletado |
| Mídia (5) | `image_search` para fotos/referências reais; diagramas de processo/fluxo via Visualizer (`mcp__visualize__show_widget`) quando o ambiente oferecer, ou descrições textuais precisas para quem for montar o material depois |
| Interatividade (6) | `quiz_display_v0` quando disponível para preview interativo; caso contrário, escrever quizzes e exercícios diretamente no documento final |
| Empacotamento (8) | Ler o `SKILL.md` da skill de output correspondente **antes** de gerar o arquivo: `/mnt/skills/public/docx/SKILL.md`, `/mnt/skills/public/pptx/SKILL.md`, ou `/mnt/skills/public/md/SKILL.md` se existir. Essas skills têm as regras de formatação e evitam erros de renderização. |

## Padrão de qualidade (aplica-se a toda fase de produção de conteúdo)

Estes princípios vêm da literatura de design instrucional e devem guiar decisões, não ser citados no curso final:

- **Backward design** (Wiggins & McTighe): desenhar do resultado final para o início, nunca do início "porque é o capítulo 1 de todo livro sobre o assunto".
- **Taxonomia de Bloom**: objetivos e avaliações devem progredir de "lembrar/entender" para "aplicar/analisar/criar" ao longo do curso — um curso que fica inteiro em "lembrar fatos" não ensina de verdade.
- **Princípios de aprendizagem multimídia (Mayer)**: imagem só quando reduz carga cognitiva, nunca decorativa; texto e imagem relacionados devem ficar espacialmente próximos; evitar redundância entre narração/texto e imagem dizendo a mesma coisa de formas diferentes.
- **Regra dos 7±2 / chunking**: nenhuma aula deve introduzir mais de ~4-6 conceitos novos genuinamente não-triviais de uma vez.
- **Toda afirmação factual relevante deve vir de pelo menos 2 fontes independentes** encontradas na Fase 1 — não do conhecimento genérico do modelo sobre o tema.
- **Direitos autorais**: nunca reproduzir texto, letras, trechos de livros ou artigos além de citações curtas (abaixo de 15 palavras, uma citação por fonte). Parafrasear é a regra, não a exceção — isso vale mesmo dentro do próprio curso.

## Antes de começar a produzir conteúdo

Sempre que a próxima ação envolver criar um arquivo de saída (docx, pptx, etc.), consulte a skill de formato correspondente **antes** de escrever qualquer conteúdo nela — essas skills têm regras específicas do ambiente (bibliotecas disponíveis, caminhos, particularidades de renderização) que não fazem parte deste guia e que evitam retrabalho.
