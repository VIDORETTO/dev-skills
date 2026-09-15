# Fases 7 e 8 — Revisão de Qualidade e Empacotamento

## Fase 7 — Revisão de qualidade

Faça essa revisão depois de ter um rascunho completo do curso, antes de gerar o arquivo final. Use `assets/checklist-qualidade.md` como checklist rápida durante essa fase.

### 1. Fact-check
Toda afirmação factual não-trivial (números, alegações causais, "melhores práticas", passos de um processo técnico) deve ter apoio em pelo menos 2 fontes independentes do material coletado na Fase 1. Se uma afirmação importante só tem uma fonte, ou nenhuma fonte registrada (veio de conhecimento genérico), sinalize isso explicitamente para o usuário em vez de deixar passar silenciosamente.

### 2. Checagem de progressão
Releia o curso do início ao fim como uma sequência única. Em cada transição de aula/módulo, pergunte: "o que essa aula assume que o aluno já sabe, e isso já foi ensinado antes?" Qualquer salto onde a resposta é "não" precisa ser corrigido — adicionando uma explicação prévia ou reordenando.

### 3. Checagem de jargão
Todo termo técnico usado precisa ter sido definido antes do primeiro uso não-trivial (ou estar no glossário e referenciado). Um jeito prático de checar: percorra o glossário bruto da Fase 1.9 e confirme que cada termo aparece definido antes de ser usado como se já fosse conhecido.

### 4. Revisão de direitos autorais
- Nenhum parágrafo do curso deve ser uma paráfrase próxima o suficiente de uma fonte para substituir a leitura dela — reescreva com liberdade, mantendo só a ideia.
- Citações diretas: no máximo uma por fonte, sempre abaixo de 15 palavras.
- Nenhuma letra de música, poema, trecho de livro ou imagem protegida deve ser reproduzida.
- Toda fonte usada deve estar registrada na lista de referências final (Fase 8).

### 5. Leitura como o aluno-alvo
Releia o curso simulando a persona definida na Fase 0 (o que ela já sabe, o que não sabe, por que está ali). Isso costuma revelar tanto trechos condescendentes demais (explicando o óbvio para o nível declarado) quanto trechos rápidos demais (pulando uma etapa que essa persona específica não teria).

## Fase 8 — Empacotamento final

### 1. Escolher e preparar o formato de saída
O formato foi decidido na Fase 0. Antes de gerar o arquivo, **sempre** leia a skill correspondente do ambiente para as regras específicas de formatação:

| Formato pedido | O que fazer |
|---|---|
| Documento/handbook para ler (Word) | Ler `/mnt/skills/public/docx/SKILL.md` antes de gerar o arquivo |
| Apresentação de slides | Ler `/mnt/skills/public/pptx/SKILL.md` antes de gerar o arquivo |
| Curso web / texto para publicar | Markdown estruturado, seguindo os padrões de formatação de conteúdo do ambiente |
| PDF para distribuir | Ler `/mnt/skills/public/pdf/SKILL.md` antes de gerar o arquivo |

Nunca pule essa leitura mesmo que o formato pareça simples — essas skills contêm detalhes de ambiente (bibliotecas disponíveis, como inserir imagem, quirks de renderização) que não fazem parte deste guia e cuja ausência causa retrabalho.

### 2. Elementos obrigatórios no material final
- **Sumário/índice navegável** no início, refletindo a arquitetura definida na Fase 2.
- **Glossário consolidado** ao final, com todos os termos técnicos definidos (consolidado a partir do glossário bruto da Fase 1.9, revisado na Fase 7.3).
- **Lista de referências/fontes**, consolidada a partir do registro de fontes da Fase 1.10. Formato simples: título, autor/veículo se disponível, link.
- Se o formato suportar, inclua também um "guia de uso do curso" curto (como navegar, quanto tempo cada módulo leva, o que fazer se travar em um exercício).

### 3. Conferência final antes de entregar
Antes de considerar o curso pronto, confirme rapidamente:
- [ ] Todo módulo tem objetivo de aprendizagem claro (Fase 3)
- [ ] Toda aula segue a micro-estrutura definida (Fase 4)
- [ ] Toda imagem/diagrama presente passa no teste "reduz carga cognitiva" (Fase 5)
- [ ] Todo módulo tem quiz e/ou exercício prático (Fase 6)
- [ ] Fact-check, progressão, jargão e direitos autorais revisados (Fase 7)
- [ ] Sumário, glossário e referências presentes (Fase 8)

Se qualquer item falhar, volte para a fase correspondente antes de entregar — não tente "remendar" no arquivo final já formatado, é mais rápido corrigir na estrutura e regerar.
