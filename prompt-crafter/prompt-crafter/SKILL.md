---
name: prompt-crafter
description: Ajuda o usuário a transformar uma ideia solta, pedido vago ou objetivo em um prompt de alta qualidade para uso com IA (Claude, ChatGPT, etc). Use esta skill sempre que o usuário pedir ajuda para "criar um prompt", "melhorar meu prompt", "escrever um prompt para...", "montar um system prompt", pedir uma "engenharia de prompt", perguntar qual framework de prompt usar (CO-STAR, CRAFT, RTF, RISEN, CARE, APE, KERNEL ou similares), ou descrever uma tarefa que quer delegar a uma IA e pedir o texto ideal para isso. A skill entende o objetivo real do usuário e escolhe automaticamente a melhor estrutura entre sete frameworks (CO-STAR, CRAFT, RTF, KERNEL, RISEN, CARE, APE), explicando a escolha e entregando o prompt pronto.
---

# Prompt Crafter

Skill para ajudar o usuário a ir de "objetivo vago" a "prompt pronto e eficaz", escolhendo automaticamente a melhor estrutura entre sete frameworks conhecidos de prompt engineering.

## Fluxo de trabalho

1. **Entenda o objetivo real do usuário.** Antes de escolher um framework, é preciso saber:
   - Qual é a tarefa final que a IA vai executar? (escrever, analisar, codar, responder como agente, gerar dados estruturados, etc.)
   - Para quem é o resultado (o próprio usuário, um cliente, redes sociais, um sistema automatizado)?
   - Importa tom/estilo/voz, ou o que importa é só a execução correta da tarefa?
   - É uma tarefa pontual e simples, ou complexa/multi-etapas?
   - Vai virar um prompt reutilizável (template, system prompt) ou é para usar uma vez só?

   Se o pedido do usuário já deixa isso claro, não pergunte — infira e prossiga. Se estiver genuinamente ambíguo (por exemplo, o usuário só disse "quero um prompt para marketing"), faça no máximo 1-2 perguntas objetivas antes de prosseguir (pode usar `ask_user_input_v0` para isso, com opções curtas).

2. **Escolha o framework mais adequado** usando a tabela de decisão abaixo. Leia `references/frameworks.md` para os detalhes, a explicação de cada letra, referências e exemplos completos de cada framework antes de montar o prompt final — não confie apenas na memória, o arquivo tem as definições corretas.

3. **Monte o prompt final** preenchendo cada elemento do framework escolhido com o conteúdo específico da situação do usuário — nunca entregue o framework "vazio" (ex: não escreva apenas "Role: [defina o papel]"). Escreva o prompt como um texto pronto para copiar e colar.

4. **Entregue em duas partes:**
   - Uma frase curta dizendo qual framework foi escolhido e por quê (1-2 linhas, sem enrolação).
   - O prompt final pronto, em bloco de código (para facilitar copiar), usando os elementos do framework como seções ou incorporados de forma natural no texto — o que fizer mais sentido para o tipo de prompt.
   
   Se for um prompt curto (poucas linhas), responda direto no chat. Se for um prompt longo e reutilizável (ex: system prompt extenso, template para uso recorrente), considere criar um arquivo `.md` como artefato/output.

5. Opcionalmente, ofereça 1 ajuste rápido (ex: "quer que eu deixe mais formal?" ou "posso adaptar para outro framework se preferir") — mas não insista, apenas mencione uma vez.

## Tabela de decisão rápida

| Situação do usuário | Framework recomendado | Por quê |
|---|---|---|
| Tarefa simples e direta, sem necessidade de nuance de tom (ex: "resuma este texto", "traduza isso") | **RTF** (Role, Task, Format) | Mínimo de estrutura necessária; rápido de montar e usar |
| Pedido rápido orientado a uma ação clara com motivo e resultado esperado | **APE** (Action, Purpose, Expectation) | Amarra ação a um "porquê" e a um critério de sucesso, sem burocracia |
| Conteúdo de marca, copywriting, posts, e-mails, onde tom/estilo/público importam muito | **CO-STAR** (Context, Objective, Style, Tone, Audience, Response) | É o framework mais completo para controlar voz e formato de saída |
| Entregável estruturado com público-alvo e formato de saída bem definidos (relatórios, propostas, documentos) | **CRAFT** (Context, Role, Action, Format, Target) | Força a pensar no formato final e em quem vai consumir o conteúdo |
| Tarefa complexa, multi-etapas, onde o processo importa tanto quanto o resultado (agentes, workflows, tarefas técnicas) | **RISEN** (Role, Instructions, Steps, End Goal, Narrowing) | Decompõe a tarefa em passos e define claramente os limites/restrições |
| Usuário quer que a IA siga um exemplo/estilo de referência para produzir um resultado concreto | **CARE** (Context, Action, Result, Example) | O componente "Example" ancora a saída em uma referência real |
| Prompt técnico, de código, ou system prompt que precisa ser confiável, verificável e reprodutível | **KERNEL** (Keep it simple, Easy to verify, Reproducible, Narrow scope, Explicit constraints, Logical structure) | Não é um template com campos, e sim um checklist de qualidade — útil para revisar/enrijecer qualquer prompt técnico |

Se a tarefa combinar características de mais de um framework, é aceitável fundir dois (ex: usar CO-STAR para tom/formato e aplicar o checklist do KERNEL por cima para garantir clareza e escopo restrito). Mencione isso ao usuário quando fizer sentido, mas não complique desnecessariamente — a maioria dos pedidos tem um único framework claramente melhor.

## Detalhes dos frameworks

Consulte **`references/frameworks.md`** para: explicação de cada letra/componente, origem/referência de cada framework, quando usar, quando evitar, e um exemplo completo de prompt para cada um. Sempre releia esse arquivo ao montar o prompt final — não invente definições de memória.
