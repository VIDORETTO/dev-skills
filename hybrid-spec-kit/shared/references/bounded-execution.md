# Execução limitada e continuação

## Um marco por sessão

Um pedido para fazer tudo autoriza o resultado completo; organize sua execução em marcos sem repetir perguntas já resolvidas. Planejamento, implementação e avaliação longa têm marcos separados. Para trabalho novo, fixe primeiro o contrato e a lista inicial de tickets.

Use `session --effort <id> --json` para sugerir até três tickets executáveis em série; priorize o ticket ativo. Reduza para um ticket quando ele for grande ou quando os demais não contribuírem para o mesmo resultado. O comando agenda; não aprova prontidão, evidência, revisão ou conclusão do esforço. Antes de editar, use as verificações de prontidão já exigidas pelo ticket, uma vez por conjunto de inputs.

Defaults operacionais: até 3 tickets; janela de trabalho de 30 minutos; renovar sessão a partir de 60% de contexto usado; nenhuma compactação planejada. Ao alcançar o primeiro limite, termine a operação segura em andamento, registre trabalho real e entregue a continuação. Não interrompa migração/transação, abandone subprocesso sem registrar como acompanhar, nem repita inferência externa com resultado desconhecido. Se uma compactação ocorrer automaticamente, não reinicie a investigação: use o checkpoint e encerre no próximo ponto seguro. Valores expressos pelo usuário prevalecem; não invente medição de contexto indisponível.

São limites de condução do agente, não watchdogs do runtime. `session` não mede contexto, encerra processos, abre conversas nem controla Goals. Não crie cron, loop de sessões ou automação de publicação por inferência.

## Goals honestos

Crie um Goal somente quando o usuário o solicitar. Antes da criação, selecione o marco e inclua o limite e a entrega alternativa no próprio objetivo:

> Trabalhar nos tickets <IDs> até cumprir seus aceites e revisão, ou alcançar o limite de sessão; em ambos os casos entregar checkpoint verdadeiro e prompt curto de continuação. Não ampliar escopo. O projeto só está concluído quando todos os aceites e gates exigidos estiverem comprovados.

O resultado deste Goal pode ser o marco concluído ou uma entrega de continuação prevista no objetivo. Nesse segundo caso diga que os tickets/projeto continuam pendentes; não altere seu status para done. Um Goal antigo cujo objetivo exige concluir o projeto inteiro não pode ser declarado completo só para trocar de sessão. Não use paused sem pedido explícito nem blocked só por atingir tempo/contexto. Token budget só é definido se o usuário o pedir expressamente. Não crie o Goal do próximo marco na mesma sessão.

## Contexto e verificações proporcionais

Leia checkpoint, ticket e somente suas seções/referências/arquivos afetados. O histórico de chat não é insumo obrigatório. Não recarregue skills/referências inalteradas. Agrupe leituras independentes; prefira saída resumida e guarde logs extensos em arquivos.

Faça red/green pelo comportamento e regressão das interfaces afetadas. Rode gates obrigatórios no momento exigido. Uma suíte global já válida só se repete quando mudança, falha ou risco pertinente justificar. Não enfraqueça aceites, oráculos ou requisitos de produção para ganhar tempo.

Combine atualização de inputs/checkpoint por comportamento ou bloco concluído, falha material ou troca de sessão. Reuse verificações determinísticas apenas com inputs e resultados iguais. Uma mudança de código exige nova evidência pertinente; classifique impacto sem transformar todo hash novo em auditoria global. Não registre cada leitura ou poll como evidência.

Avaliação externa: qualifique runner/adapter e uma amostra diagnóstica pequena antes do conjunto integral, quando o contrato permitir. Depois congele seus inputs durante a captura. Capture andamento por processo/arquivo, sem consumir rodadas do modelo só para polling. O conjunto integral permanece obrigatório se aceito; subprocessos vivos, cancelados ou desconhecidos devem estar no checkpoint.

## Controle de tickets

Correção necessária ao aceite de um ticket fica nele, com revisão e evidência afetada. Registre defeitos encontrados em finding deduplicado. Abra novo ticket somente se exigir resultado independente, mudança de contrato, área/dependência distinta ou se o ticket anterior já estiver encerrado e não puder ser reaberto justificadamente. Implementar o helper de um teste não gera automaticamente um ticket novo. Não apague IDs/histórico existentes.

Fixe a quantidade inicial de tickets no planejamento com `session --write --json`. O comando preserva a baseline na continuação gerada; para uma migração com quantidade original conhecida, use `--baseline-tickets <n>` uma vez. Sem essa informação, a primeira contagem observada é a baseline, não uma reconstrução do histórico. Crescimento maior que 20% é sinal para reconciliar causas antes de outra expansão; não é permissão para omitir bugs. Melhoria opcional vai a backlog/finding e não entra no Goal atual. Trabalho indispensável já autorizado pode ser replanejado com motivo e impacto, sem pedir permissão novamente. Escolha material de produto/contrato requer a decisão correspondente.

## Encerramento e retomada

Atualize state.json pelo checkpoint normal: resultado, próximos IDs, arquivos, testes/evidências, pendências e processos. Mantenha next_action curto; detalhes ficam no ticket/evidência já existente. `session --write --json` gera `.hybrid/continuations/<effort>.md` a partir do estado atual sem editar contratos, tickets ou o checkpoint.

Toda sessão que encerra um marco ou alcança um limite entrega o resultado observado e um único prompt, no idioma do usuário, preferencialmente uma frase:

> Em <projeto>, use hybrid-start para continuar <esforço> pelo checkpoint, em um Goal limitado ao próximo marco; ao terminar, entregue o próximo prompt.

Não adicione novo pedido de confirmação rotineira. Se houver bloqueio real, o prompt aponta a decisão/recurso pendente. Ao concluir o esforço, confira os gates de entrega e pare; não gere novas melhorias para manter o Goal ativo. Se outras specs já estiverem autorizadas, o próximo prompt aponta a próxima spec; não declara todo o projeto pronto só porque os tickets deste esforço estão done.
