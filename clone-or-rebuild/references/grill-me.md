# Grill-me — entrevista de descoberta de alta informação

## Objetivo da entrevista

Descobrir **qual resultado serve ao usuário**, não apenas “qual produto clonar”. Conduza uma conversa objetiva e questionadora, sem hostilidade e sem colocar o usuário para preencher um questionário gigante. Evite repetir respostas disponíveis no contexto ou nos arquivos. Trate cada pergunta como uma hipótese que você está tentando distinguir.

## Método: uma pergunta decisiva por rodada

1. Resuma o entendimento atual em uma linha; enuncie **uma hipótese a testar**.
2. Faça **uma pergunta de maior ganho de informação** (até três questões independentes se cada uma for bloqueadora e custaria uma rodada extra). Mostre exemplos de respostas para reduzir fricção.
3. Após a resposta, atualize o briefing em silêncio ou no registro, **não reinicie do zero**.
4. Pergunte de novo somente sobre lacunas que mudem o plano, a segurança, a qualidade ou o orçamento.
5. Apresente uma proposta após as respostas mínimas: **objetivo, acesso, direitos, fonte, oráculo, escopo inicial**. Permita correção da interpretação.

## Ordem sugerida das perguntas, com ramificações

| Prioridade | Pergunta orientativa | O que decide | Se respondeu... |
|---|---|---|---|
| 1 | “O que precisa ficar igual para você considerar sucesso: tela, comportamento, dados, integração, performance ou tudo? Qual fluxo é mais importante?” | Objetivo/escopo | “Tudo” → desafiar: “qual é a primeira funcionalidade indispensável?” |
| 2 | “Você tem o código-fonte e permissão para usá-lo, ou só acesso ao executável, site ou demonstração?” | Fonte vs RE | Fonte completa → procurar testes/docs e caminho SOURCE_FIRST |
| 3 | “Qual é o alvo exato (link, repositório, arquivo, versão, SO) e em que ambiente você consegue acessá-lo?” | Tooling/identidade | Sem artefato → escopo black-box/público ou especificação |
| 4 | “Você possui/autorizou análise, execução, tráfego e reprodução? Há dados de terceiros ou segredos?” | Gate de autorização | Incerto → plano sem intervenções até delimitar autoridade |
| 5 | “Dê 2–3 entradas e saídas que podemos comparar, ou uma conta/teste onde o resultado é observável.” | Oráculo de fidelidade | Sem oráculo → fase de descoberta de contrato antes de prometer clone |
| 6 | “Qual a stack/ambiente de destino e as restrições (prazo, equipe, dependências, offline, custo)?” | Build vs reuse/tool | Sem restrições → registrar premissas e propor stack reversível |
| 7 | “O que explicitamente *não* precisamos copiar: marca, conteúdo, backend, animações, sistema de conta, arquivos, todos os casos extremos?” | Excluir escopo | Metas irreais → negociar MVP testável |
| 8 | “É permitido reutilizar bibliotecas, API pública, open source e padrões equivalentes?” | REUSE vs SPEC | Se sim → comparar alternativas antes de RE profunda |

Não é roteiro fixo: a resposta pode eliminar perguntas subsequentes. Use perguntas específicas ao projeto, não uma lista lida literalmente.

## Perguntas especiais por objetivo

**UI** — quais telas, tamanhos, responsividade, estados (loading, vazio, erro, hover), dados de demonstração, fontes e assets licenciados, acessibilidade, navegação? Qual é a referência visual estável?

**API ou protocolo** — quais endpoints/mensagens, esquemas, autenticação autorizada, ordem de eventos, idempotência, erros, rate limits? Existem OpenAPI/SDK/logs?

**Binário nativo** — SO/arquitetura, versão/hash, símbolos disponíveis, DLL/dependências, inputs que pode testar, risco de execução, código compilador?

**Electron/desktop** — instalação, asar, módulos nativos, comportamento de processo principal/renderer/preload, dados locais, versão do app?

**Android/iOS** — app próprio ou autorizado, pacote/versão/dispositivo, permissões, store/contrato, capacidade de execução e instrumentação?

**Migração** — tem código, schema e testes? quais contratos externos, dados, integrações, SLO, rolling back? O objetivo é compatibilidade exata ou modernização?

**Jogo** — mecânicas ou aparência? engine, assets próprios/licenciados, ritmo/FPS, determinismo, saves, física, input devices, modo online?

## Critérios para parar de perguntar

Pare quando conseguir escrever uma primeira tarefa segura e útil que seja falsificável. Não exija prazo/orçamento quando não mudarem a primeira fase. Se o usuário já descreveu tudo, proponha o plano diretamente. Para projetos longos, faça outra rodada de perguntas **apenas quando surgir nova incerteza material**.

## Exemplo de diálogo curto

**Usuário:** “Quero clonar um editor de texto.”

**Agente:** “Você precisa principalmente da aparência, da edição de documentos ou da compatibilidade com um formato de arquivo específico? Qual desses tem de funcionar primeiro?”

**Usuário:** “Quero importar arquivos .foo e exportar iguais. Tenho o código antigo.”

**Agente:** “Como já há código, provavelmente não precisamos descompilar nada. O código antigo abre exemplos reais do formato e você tem arquivos de referência que podemos comparar após exportar?”

**Usuário:** “Sim, dez arquivos. Preciso migrar de Java para Rust.”

**Agente:** “Sugestão: SOURCE_FIRST, contratos por arquivo e testes diferenciais; primeiro importação/exportação básica em Rust. Não começaria com REA. Vou mapear parser e fixtures e deixar claro quais formatos avançados ainda não estão cobertos.”

## Caso de entrada ambígua ou nenhum artefato

Não simule inspeção. Solicite **somente a peça mínima bloqueadora**: nome/arquivo/link/descrição de comportamento. Se o usuário preferir protótipo a fidelidade, ofereça SPEC_FIRST e implemente comportamento inspirado com trabalho original, sem declarar que o original foi investigado.
