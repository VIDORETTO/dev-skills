# Pacote de execução

O próprio ticket é o pacote entregue a uma executora em contexto novo. `next --effort <id> --write` verifica a prontidão do primeiro ticket selecionado e devolve só o caminho, os aceites, os erros/bloqueios e o comando de validação. A executora então lê o arquivo do ticket. `package --ticket TK-xxx --write` gera uma cópia de leitura em `.hybrid/packets/`, que é projeção e nunca contrato concorrente.

Um ticket `ready` contém, no mínimo:

1. **Objetivo e limites:** comportamento observável, aceites associados e o que não inclui.
2. **Leitura em ordem:** caminho → símbolo/seção, verificados no planejamento.
3. **Exemplos de aceite:** estado, entrada, resultado e efeito proibido, com oráculo independente.
4. **Validação:** comando exato e diretório.

Seções opcionais, só quando trazem informação específica do ticket: decisões já resolvidas (com a liberdade local da executora), mapa de alterações e contrato técnico. O ciclo red/green, a condição de retorno e o relatório de saída ficam definidos em `hybrid-implement` e não se repetem em cada ticket.

A executora escolhe detalhes locais reversíveis. Quando faltar decisão de comportamento, contrato público, modelo de dados, dependência, autorização ou recurso, ela preserva o progresso e devolve:

```text
Ticket: TK-002 · Passo: teste de AC-002
Bloqueio: a Interface atual não permite a consulta exigida por AC-002.
Evidência: caminho, símbolo e resultado observado.
Decisão necessária: forma de representar e consultar a chave.
Impacto: AC-002 não pode ser implementado pela abordagem atual.
```

Comando apenas encontrado na configuração não equivale a comando executado. `evidence run` executa e registra `exit_code`; `evidence add --executed` é uma declaração e fica reservado a procedimentos manuais ou externos.
