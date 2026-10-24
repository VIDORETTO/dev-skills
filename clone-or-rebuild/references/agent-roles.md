# Papeis de agentes, orquestração e transferência de contexto

Não crie cinco agentes apenas porque consegue. Paralelize apenas quando tarefas são separáveis, artefatos versionados e existe revisor/integrador. Se o projeto for pequeno, um agente executa todos os papéis sequencialmente.

| Papel | Entrada | Saída | Regra |
|---|---|---|---|
| **Interviewer / Architect** | pedido e contexto | objetivo, permissões, decisão, plano, fatias | não escolher stack antes de saber restrições |
| **Investigator** | hipótese, identidade do alvo, acesso aprovado | ledger de evidências + lacunas | não implementar sobre hipótese não marcada |
| **Contract Tester** | oráculo, fixtures, comportamento observado | casos e contrato de comparação | criar testes independentes do novo código |
| **Builder** | spec versionada + testes | código próprio, commits, logs de teste | não plagiar material protegido; não apagar testes |
| **Verifier / Reviewer** | original permitido, candidato, ledger | divergências, riscos, relatório | não confiar só na autoavaliação do builder |

## Contrato de handoff entre etapas

```yaml
scope: "Exportação CSV da tela de relatórios"
target_version: "vX, hash SHA-256 ..."
authorization: "inspeção e execução em staging"
source_status: "complete | partial | none"
decision: "SOURCE_FIRST"
question: "Como escapam aspas e newlines?"
evidence:
  - id: EV-004
    state: OBSERVADO
    location: "arquivo:linha ou caso de teste"
unknowns:
  - "normalização de CRLF no Windows"
acceptance:
  - "12/12 fixtures devem produzir dados semanticamente iguais"
limits:
  - "sem avaliação de throughput"
next_action: "implementar exportador com suite de regressão"
```

Use tokens/contexto racionalmente: ledger curto, linkar artefatos e não colar milhares de linhas no prompt. O investigator registra evidência encontrada; o builder não precisa receber todo o binário ou logs confidenciais.

## Controle de conflitos

- Mudanças em testes devem ser revisadas por papel distinto do responsável pelo código quando possível.
- Testes do original devem ser congelados/versionados antes da implementação.
- Quando dois agentes divergem, resolva via experimento reproduzível e registro de evidências, nunca por “autoridade do modelo”.
- Um papel não assume poderes (admin, produção, instalação, rede) concedidos a outro sem autorização explícita.
