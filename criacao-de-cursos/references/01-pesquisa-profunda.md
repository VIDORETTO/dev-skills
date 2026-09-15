# Fase 1 — Pesquisa Profunda

## Por que esta fase existe

O conhecimento genérico de um modelo de linguagem sobre um tema é uma média estatística de tudo que já foi escrito sobre ele — o que tende a ser correto, mas raso e genérico. O que separa um curso bom de um curso raso não é a correção factual básica, é: (1) saber quais são as dúvidas reais que as pessoas têm ao aprender aquilo, (2) saber onde elas erram e travam, e (3) ter analogias e exemplos que já foram testados em outras pessoas. Isso só existe em fóruns, comentários, vídeos didáticos e comparações entre cursos existentes — não em uma definição enciclopédica do tema.

## Passo a passo

### 1. Mapeamento de fontes primárias
Antes de sair buscando aleatoriamente, identifique:
- Livros de referência do tema (busque "[tema] best book" ou "[tema] recommended reading").
- Documentação oficial, se for um tema técnico (framework, ferramenta, linguagem).
- Instituições ou autores reconhecidos como referência no assunto.

Isso vira sua "espinha dorsal" de credibilidade — as fontes que você vai cruzar com tudo o mais.

### 2. Busca em camadas
Não faça uma única busca ampla — faça buscas específicas por tipo de conteúdo. Padrões de query que funcionam bem:
- `"[tema] guide"`, `"[tema] fundamentals"`, `"[tema] explained"` → conteúdo introdutório de qualidade
- `"[tema] tutorial"`, `"[tema] step by step"` → conteúdo prático
- `"[tema] common mistakes"`, `"[tema] misconceptions"`, `"why is [tema] confusing"` → pontos de dúvida real
- `"[tema] vs [alternativa]"` → comparações que revelam trade-offs importantes
- `"[tema] advanced"`, `"[tema] deep dive"` → para módulos finais

Cada query deve ser curta (3-6 palavras) e específica. Faça várias buscas diferentes em vez de uma genérica — resultados de uma busca ampla tendem a ser superficiais para todos os subtemas ao mesmo tempo.

**Escala de esforço**: um tema estreito e bem definido (ex: "como fazer nó de gravata") pode precisar de 10-15 buscas. Um tema amplo (ex: "marketing digital") precisa de pesquisa por subtema — trate cada pilar do curso (ver Fase 2) como um mini-tema com sua própria rodada de 5-10 buscas. Não economize aqui: é a fase que mais determina a qualidade final.

### 3. Fóruns — onde estão as dúvidas reais
Fóruns revelam o que as pessoas *de verdade* não entendem, não o que os autores de blogs acham que elas não entendem. Busque:
- `site:reddit.com [tema]`
- `site:reddit.com [tema] eli5` (explicações simplificadas costumam ser ouro para analogias)
- `[tema] stack exchange` ou `site:stackoverflow.com [tema]` (se técnico)
- `[tema] quora`

Ao ler os resultados, extraia especificamente:
- Perguntas que se repetem com frases diferentes (sinal de dúvida estrutural, não pontual)
- Respostas muito upvotadas/aceitas — costumam conter as melhores explicações e analogias já testadas em público
- Discordâncias entre respondentes — sinal de que o tema tem uma área genuinamente controversa ou mal padronizada, que vale mencionar no curso

### 4. Vídeos do YouTube
Vídeos didáticos costumam ter as melhores analogias porque foram otimizados para reter atenção. Processo:
1. Busque `[tema] youtube` ou `[tema] explained youtube` e identifique os vídeos mais relevantes/bem avaliados pelos resultados.
2. **Obtenção de transcrição**: verifique primeiro se há um conector MCP de YouTube/transcrição disponível no ambiente atual (ferramenta de busca de conectores). Se houver, use-o diretamente.
3. Se não houver ferramenta de transcrição disponível, não tente adivinhar o conteúdo do vídeo a partir do título. Em vez disso:
   - Busque o título do vídeo + `"transcript"` — vídeos populares às vezes têm transcrições publicadas em blogs ou sites de notas.
   - Busque artigos ou posts que resumem ou reagem ao vídeo especificamente.
   - Use a descrição do vídeo e os comentários mais curtidos (frequentemente contêm resumos feitos por outros espectadores ou perguntas de esclarecimento do próprio criador).
   - Se nada disso trouxer conteúdo substancial, não force — simplesmente não cite esse vídeo como fonte e siga para outras.
4. Nunca invente ou "lembre" o conteúdo de um vídeo específico a partir de memória — isso é uma citação fabricada. Se não há certeza real do conteúdo, não atribua a afirmação a ele.

### 5. Papers e pesquisa acadêmica (quando aplicável)
Para temas com base científica: busque `[tema] research`, `[tema] systematic review`, `[tema] meta-analysis`. Priorize revisões sistemáticas sobre estudos isolados — dão uma visão mais robusta do consenso atual.

### 6. Cursos concorrentes — benchmark, não cópia
Busque como o tema já é ensinado em plataformas estabelecidas (nomes de cursos, ementas públicas, descrições de módulos). O objetivo **não é copiar a estrutura**, é:
- Identificar a ordem "padrão de mercado" dos tópicos, para não fugir dela sem motivo
- Identificar o que os cursos existentes deixam de fora ou fazem mal — sua chance de diferenciação
- Calibrar a duração/densidade esperada para esse nível de curso

### 7. Extração de FAQ real
Ao final da varredura de fóruns e vídeos, consolide uma lista de 20-30 perguntas que realmente aparecem repetidas. Essa lista deve informar diretamente quais pontos cada aula precisa resolver explicitamente — não é material de referência, é insumo de design instrucional.

### 8. Extração de erros comuns e pontos de confusão
Separado da FAQ: uma lista específica de onde as pessoas erram na prática (não só o que não entendem, mas o que fazem errado). Isso alimenta os "contra-exemplos" de cada aula (ver `03-objetivos-design-instrucional.md`).

### 9. Glossário bruto
Enquanto pesquisa, vá anotando todo termo técnico/jargão encontrado, mesmo sem definir ainda. Isso vira a base do glossário final (Fase 8) e ajuda a garantir que nenhum termo apareça no curso sem ter sido definido antes.

### 10. Registro de fontes
Para cada fonte relevante usada, registre: título, URL, tipo (artigo/fórum/vídeo/paper/curso), data de acesso, e um resumo de uma frase do que ela contribuiu. Isso serve para:
- Montar a lista de referências final do curso
- Permitir cross-check (nenhuma afirmação forte deve se apoiar em uma única fonte)
- Evitar problemas de direitos autorais — você cita a fonte, nunca reproduz o texto dela

## Formato de registro sugerido

Mantenha um documento de trabalho (pode ser um arquivo markdown temporário) organizado por subtema, não por fonte:

```
## Subtema: [nome]

### Conceitos-chave encontrados
- ...

### FAQ real (fórum/comentários)
- P: ... — fonte: [título](url)

### Erros comuns
- ...

### Analogias/exemplos que funcionaram (vídeos/fóruns)
- ...

### Fontes usadas nesta seção
- [título](url) — tipo — o que contribuiu
```

Isso facilita a Fase 2 (síntese), que consome esse material subtema por subtema.

## Regra de direitos autorais durante a pesquisa

Ao anotar o que encontrou, escreva sempre com suas próprias palavras. Se uma frase específica for genuinamente valiosa por sua formulação exata, anote a citação entre aspas com menos de 15 palavras e a fonte — mas isso deve ser raro, não o padrão. O curso final nunca deve conter parágrafos que sejam paráfrase próxima o suficiente para funcionar como substituto da fonte original.
