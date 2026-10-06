# Execução limitada e continuação

- **Escopo antes de tudo.** Trabalho direto (veja o filtro de escopo em `hybrid-start`) não usa o kit.
- **Um marco por sessão.** Planejamento e execução ficam em sessões separadas. `next` seleciona até 3 tickets relacionados e prioriza o ativo; um ticket grande fica sozinho.
- **Renovação.** Troque de sessão na fronteira de um ticket ou perto de 100 mil tokens de contexto, nunca no meio de uma migração, transação ou subprocesso sem registro. Se houver compactação automática, retome pelo checkpoint e não repita a investigação.
- **Orçamento de chamadas.** Rota compacta: no máximo 2 chamadas ao runner. Rota padrão: até 3 por ticket (`next`, `ticket update`, `evidence run`). Uma verificação só se repete quando seus insumos mudaram.
- **Crescimento de tickets.** A primeira contagem vira baseline (`session --write`, ou `--baseline-tickets <n>` uma vez). Crescimento acima de 20% exige reconciliar causas. Correções do aceite ficam no próprio ticket; melhorias opcionais vão para o backlog.
- **Encerramento honesto.** Entregue o resultado observado e um único prompt curto, no idioma do usuário. Trabalho parcial continua pendente: nunca marque `done` para encerrar a sessão.
- **Goals.** Crie um somente a pedido do usuário. O objetivo inclui o marco, o limite e a entrega alternativa (checkpoint + prompt). Não declare concluído um Goal antigo que pedia o projeto inteiro.

O runner apenas agenda e registra: ele não mede contexto, não encerra processos, não abre sessões e não cria Goals.
