# Fase 2 — Síntese e Arquitetura do Curso

## Por que esta fase existe

A pesquisa da Fase 1 produz um monte de material desorganizado. Escrever aulas direto a partir disso resulta em um curso que segue a ordem em que você pesquisou, não a ordem em que alguém deveria aprender. Esta fase existe para transformar material bruto em uma sequência com lógica pedagógica.

## Passo a passo

### 1. Construir o mapa de conceitos
A partir do material da Fase 1, liste todos os conceitos identificados e desenhe as dependências entre eles: "para entender B, é preciso já saber A". Não precisa ser um diagrama formal — uma lista com indentação já funciona:

```
- Conceito A (fundamental, sem pré-requisitos)
  - Conceito B (requer A)
    - Conceito D (requer B)
  - Conceito C (requer A)
- Conceito E (fundamental, independente de A)
```

Esse mapa é o que impede o erro mais comum de cursos gerados rápido: introduzir um conceito antes do pré-requisito dele estar estabelecido.

### 2. Identificar os pilares
Quase todo tema se organiza naturalmente em 4-8 grandes blocos de conhecimento. Agrupe o mapa de conceitos em pilares — cada pilar tende a virar um módulo (ou um pequeno grupo de módulos, se for grande).

### 3. Sequenciar por dependência, não por convenção
Ordene os pilares seguindo o mapa de dependências construído no passo 1. Só siga a ordem "tradicional" de outros cursos concorrentes (mapeada na Fase 1.6) se ela também for logicamente consistente — se você encontrar um pilar que é ensinado "por padrão" antes de outro que na verdade é pré-requisito dele, corrija.

### 4. Validar contra o benchmark de mercado
Compare sua sequência com a ementa dos cursos concorrentes levantados na Fase 1. Divergências não são um problema — são uma decisão consciente. Mas você deve conseguir explicar cada divergência (ex: "os cursos X e Y ensinam otimização antes de fundamentos, mas isso confunde iniciantes segundo o próprio fórum de discussão, então inverti a ordem").

## Design reverso (backward design)

Depois de ter os pilares sequenciados, aplique o desenho de trás para frente:

1. **Comece pela transformação prometida** (a frase definida na Fase 0: "ao final, o aluno será capaz de ___").
2. **Defina o projeto ou avaliação final** que comprova essa transformação — algo que force o aluno a combinar múltiplos pilares, não testar um de cada vez.
3. **Trabalhe de trás para frente**: que módulo prepara diretamente para esse projeto final? O que esse módulo, por sua vez, precisa que o aluno já saiba?
4. Só então confirme que a sequência bate com o mapa de dependências do passo 1 — os dois exercícios devem convergir. Se não convergirem, o mapa de dependências geralmente está certo e o desenho do projeto final precisa ajustar.

Esse método evita o padrão mais comum de curso ruim: uma sequência de módulos que faz sentido individualmente mas nunca se conecta em algo que o aluno realmente consegue *fazer* ao final.

## Estrutura padrão de módulo

Defina uma estrutura interna consistente para todo módulo do curso (ela será reaproveitada Fase 4 em diante, aula a aula):

```
Módulo N: [Nome]
├── Introdução (por que este módulo importa, conecta com o anterior)
├── Aula 1: [conceito]
├── Aula 2: [conceito]
├── ...
├── Prática aplicada do módulo
└── Recapitulação + checagem de entendimento
```

## Balanço teoria vs. prática

Não existe uma proporção universal — depende do tipo de curso. Use como ponto de partida, ajustando conforme o que a pesquisa da Fase 1 revelou sobre como o tema é melhor aprendido:

| Tipo de curso | Teoria | Prática |
|---|---|---|
| Habilidade técnica/ferramenta (programação, software) | ~20-30% | ~70-80% |
| Conceitual/acadêmico (história, teoria científica) | ~60-70% | ~30-40% |
| Soft skill (comunicação, liderança) | ~30-40% | ~60-70% |
| Criativo (escrita, design, música) | ~25-35% | ~65-75% |

## Saída desta fase

Ao final, você deve ter: (1) o mapa de conceitos com dependências, (2) a lista de pilares/módulos sequenciados, (3) a definição do projeto/avaliação final, (4) uma frase justificando qualquer divergência do benchmark de mercado. Isso alimenta diretamente a Fase 3 (objetivos de aprendizagem por módulo).
