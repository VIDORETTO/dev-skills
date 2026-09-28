# Referência dos frameworks de prompt

Este arquivo detalha os sete frameworks que a skill `prompt-crafter` usa. Para cada um: o que cada letra significa, origem/referência, quando usar, quando evitar, e um exemplo completo.

---

## 1. CO-STAR

**Context · Objective · Style · Tone · Audience · Response**

Framework popularizado por Sheila Teo (GovTech Singapura), vencedora do primeiro campeonato mundial de prompt engineering promovido pela Singapore's AI community/DataBricks (2023). É hoje um dos frameworks mais citados para prompts de geração de conteúdo.

- **Context (Contexto):** informações de fundo necessárias para a IA entender a situação.
- **Objective (Objetivo):** o que exatamente a tarefa deve realizar.
- **Style (Estilo):** estilo de escrita desejado (ex: como um redator específico, jornalístico, técnico).
- **Tone (Tom):** tom emocional da resposta (formal, bem-humorado, empático, direto).
- **Audience (Público):** para quem é a resposta — molda vocabulário e nível de detalhe.
- **Response (Formato da resposta):** formato de saída (lista, tabela, parágrafo, e-mail, JSON etc.).

**Quando usar:** conteúdo de marca, copywriting, posts de redes sociais, e-mails, roteiros — qualquer coisa em que tom, estilo e público mudam completamente o resultado.

**Quando evitar:** tarefas técnicas puras (código, extração de dados) onde tom não importa — CO-STAR vira excesso de estrutura para pouco ganho.

**Exemplo:**
```
Context: Somos uma cafeteria de bairro que está lançando uma nova blend de café descafeinado.
Objective: Escrever um post para Instagram anunciando o lançamento.
Style: Estilo caloroso e conversacional, como se um dono de cafeteria estivesse falando com clientes fiéis.
Tone: Animado, mas não exagerado.
Audience: Moradores do bairro, 25-45 anos, que já frequentam a cafeteria.
Response: Um parágrafo curto (até 80 palavras) + 3 hashtags no final.
```

---

## 2. CRAFT

**Context · Role · Action · Format · Target**

Variante popular derivada dos frameworks clássicos de "role prompting", frequentemente citada em guias de prompt engineering como alternativa mais orientada a entregáveis do que o CO-STAR.

- **Context (Contexto):** a situação/cenário de fundo.
- **Role (Papel):** que persona ou especialista a IA deve assumir.
- **Action (Ação):** a tarefa específica a ser executada.
- **Format (Formato):** como o resultado deve ser estruturado/apresentado.
- **Target (Público-alvo):** quem vai consumir o resultado e o impacto desejado.

**Quando usar:** entregáveis estruturados como relatórios, propostas, documentos internos, materiais educacionais — quando formato final e público são tão importantes quanto o conteúdo.

**Quando evitar:** perguntas simples e diretas, onde definir um "Role" elaborado é desnecessário.

**Exemplo:**
```
Context: Preciso apresentar para a diretoria os resultados do último trimestre de vendas.
Role: Aja como um analista de dados sênior especializado em relatórios executivos.
Action: Resuma os principais números de vendas do trimestre e destaque 3 tendências relevantes.
Format: Um resumo executivo de até 200 palavras, seguido de 3 bullet points com as tendências.
Target: Diretores que têm pouco tempo e não são especialistas técnicos — evite jargão.
```

---

## 3. RTF

**Role · Task · Format**

O framework mais minimalista e um dos mais usados no dia a dia — cobre o essencial sem sobrecarregar o prompt.

- **Role (Papel):** quem a IA deve ser/simular.
- **Task (Tarefa):** o que precisa ser feito, de forma clara e específica.
- **Format (Formato):** como a resposta deve ser entregue.

**Quando usar:** tarefas rápidas e diretas do dia a dia (resumir, traduzir, reescrever, transformar um transcript em ata de reunião).

**Quando evitar:** tarefas que dependem fortemente de tom, público ou processo passo a passo — RTF não cobre essas dimensões.

**Exemplo:**
```
Role: Você é um assistente executivo experiente.
Task: Transforme a transcrição de reunião abaixo em uma ata objetiva, com decisões tomadas e próximos passos.
Format: Título, lista de participantes, lista de decisões, lista de próximos passos com responsáveis.
```

---

## 4. KERNEL

**Keep it simple · Easy to verify · Reproducible results · Narrow scope · Explicit constraints · Logical structure**

Diferente dos outros frameworks, o KERNEL não é um "preencha os campos" — é um **checklist de princípios de qualidade** para revisar e enrijecer qualquer prompt, especialmente prompts técnicos, de código ou system prompts que precisam de comportamento confiável e repetível.

- **Keep it simple (Simplicidade):** um objetivo claro por prompt; evite empilhar várias tarefas não relacionadas no mesmo pedido.
- **Easy to verify (Fácil de verificar):** a saída deve ter um jeito claro de checar se está certa (critério de sucesso explícito).
- **Reproducible results (Resultados reprodutíveis):** o prompt deve gerar resultados consistentes se repetido, evitando ambiguidade que gere respostas muito diferentes a cada execução.
- **Narrow scope (Escopo restrito):** limite bem o que está dentro e fora do pedido.
- **Explicit constraints (Restrições explícitas):** diga não só o que fazer, mas o que NÃO fazer (limites, formato proibido, coisas a evitar).
- **Logical structure (Estrutura lógica):** organize o prompt em uma ordem que facilita o raciocínio da IA (contexto → tarefa → passos → restrições → formato).

**Quando usar:** prompts técnicos (geração/revisão de código), system prompts para agentes, prompts que serão reutilizados em produção e precisam de comportamento estável.

**Quando evitar:** como estrutura única para conteúdo criativo/livre — funciona melhor como uma "camada de revisão" aplicada por cima de outro framework (ex: monte com CRAFT ou RISEN e depois passe pelo checklist do KERNEL).

**Exemplo (usado como checklist sobre um prompt técnico):**
```
Tarefa: Escreva uma função em Python que valide CPF.

Aplicando KERNEL:
- Simples: só essa função, nada de também gerar testes ou documentação no mesmo pedido.
- Verificável: "deve retornar True/False e passar nos casos de teste: [lista de CPFs válidos/inválidos]".
- Reprodutível: especifique a assinatura exata da função e o formato de entrada esperado (string com ou sem pontuação).
- Escopo restrito: só validação de formato e dígito verificador — não checar se o CPF existe na Receita.
- Restrições explícitas: não usar bibliotecas externas, só Python padrão.
- Estrutura lógica: contexto (validação de CPF) → tarefa (função) → critério de aceite (testes) → restrições (sem libs externas).
```

---

## 5. RISEN

**Role · Instructions · Steps · End Goal · Narrowing**

Framework criado por Kyle Balmer, pensado para tarefas onde o *processo* de chegar à resposta é tão importante quanto a resposta em si.

- **Role (Papel):** persona/expertise que a IA deve assumir.
- **Instructions (Instruções):** o que precisa ser feito, de forma clara e sem ambiguidade.
- **Steps (Passos):** quebra da tarefa em etapas lógicas que a IA deve seguir em ordem.
- **End Goal (Objetivo final):** como é o resultado ideal — o que "bom" parece.
- **Narrowing (Restrições):** limites, formato, tom, tamanho ou qualquer coisa que refine o resultado final.

**Quando usar:** tarefas complexas ou multi-etapas — estratégias, planejamento, prompts de agentes que executam um processo, revisões estruturadas.

**Quando evitar:** pedidos simples de uma linha — a estrutura completa vira exagero.

**Exemplo:**
```
Role: Você é um gerente de mídias sociais experiente.
Instructions: Crie uma estratégia para aumentar o engajamento no Instagram da minha loja de roupas nos próximos 30 dias.
Steps: 1) Analise os tipos de conteúdo que costumam engajar nesse nicho. 2) Sugira 3 formatos de conteúdo. 3) Proponha uma frequência de postagem. 4) Sugira como medir sucesso.
End Goal: Um plano de 30 dias que aumente o engajamento (curtidas + comentários) em pelo menos 20%.
Narrowing: Sem usar sorteios ou brindes pagos; foco em conteúdo orgânico; máximo de 5 posts por semana.
```

---

## 6. CARE

**Context · Action · Result · Example**

Framework enxuto que se diferencia por incluir explicitamente um **exemplo de referência**, ajudando a IA a calibrar estilo ou formato a partir de uma amostra real.

- **Context (Contexto):** situação de fundo.
- **Action (Ação):** o que deve ser feito.
- **Result (Resultado desejado):** como deve ser o resultado final, especificamente.
- **Example (Exemplo):** uma amostra, referência ou modelo a ser seguido/imitado.

**Quando usar:** quando você tem um exemplo concreto do estilo/formato que quer (ex: "escreva como neste outro texto", "siga este modelo de e-mail").

**Quando evitar:** quando não há exemplo disponível e criar um do zero tomaria mais tempo do que o ganho — nesse caso outro framework é mais direto.

**Exemplo:**
```
Context: Preciso escrever cartas de recomendação para alunos de pós-graduação.
Action: Escreva uma carta de recomendação para a aluna Marina, destacando seu trabalho em pesquisa de machine learning.
Result: Uma carta de uma página, tom formal mas caloroso, destacando 2-3 conquistas concretas.
Example: [colar aqui uma carta anterior que o usuário gostou, para a IA imitar o tom e a estrutura]
```

---

## 7. APE

**Action · Purpose · Expectation**

O framework mais compacto da lista, ideal para pedidos rápidos onde o essencial é amarrar a ação a um motivo e a um critério de sucesso.

- **Action (Ação):** o que a IA deve fazer.
- **Purpose (Propósito):** por que isso está sendo pedido — o motivo por trás da tarefa.
- **Expectation (Expectativa):** o que o resultado final deve conter/parecer.

**Formato típico:** `[Ação] para [Propósito], de modo que [Expectativa]`.

**Quando usar:** pedidos rápidos, cotidianos, onde uma frase já resolve — não precisa de seções separadas.

**Quando evitar:** tarefas complexas com múltiplas etapas ou que dependem fortemente de tom/formato — aí RISEN ou CO-STAR servem melhor.

**Exemplo:**
```
Action: Resuma este artigo sobre inteligência artificial.
Purpose: Para economizar tempo e postar um resumo no LinkedIn.
Expectation: O resumo deve ter no máximo 5 linhas e terminar com uma pergunta que gere engajamento nos comentários.
```

---

## Resumo comparativo

| Framework | Nº de elementos | Foco principal | Melhor para |
|---|---|---|---|
| RTF | 3 | Simplicidade | Tarefas rápidas do dia a dia |
| APE | 3 | Ação + motivo + critério de sucesso | Pedidos pontuais e diretos |
| CARE | 4 | Exemplo/referência | Replicar um estilo ou formato existente |
| CRAFT | 5 | Entregável + público-alvo | Documentos e relatórios estruturados |
| RISEN | 5 | Processo passo a passo | Tarefas complexas/multi-etapas, agentes |
| CO-STAR | 6 | Tom, estilo e público | Copywriting e conteúdo de marca |
| KERNEL | 6 (checklist) | Qualidade, clareza e confiabilidade | Prompts técnicos, de código e system prompts |
