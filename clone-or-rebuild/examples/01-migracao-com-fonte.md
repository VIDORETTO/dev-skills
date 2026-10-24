# Exemplo 1 — Migrar um serviço legado cujo código existe

**Pedido:** “Clonar nossa plataforma Laravel em Node.js e manter tudo igual.”

### Grill-me (duas rodadas)

1. “O que não pode mudar para seus usuários: APIs, dados, relatórios, UI, integrações? Qual módulo migrar primeiro?”
2. “Temos acesso ao repositório, esquema do banco e staging? Quais testes/fixtures provam o comportamento do módulo?”

**Respostas hipotéticas:** repo atualizado, autorização interna, Postgres, 23 endpoints, logs sanitizados; primeiro módulo é exportação de relatório.

### Decisão

**SOURCE_FIRST + INCREMENTAL_MIGRATION. NÃO instalar REA.** O código e o schema respondem às perguntas. Inventariar rota→controller→query→serialização e criar testes de caracterização que executem mesma entrada contra Laravel e Node.

**Ferramentas:** `rg`, análise da stack, testes HTTP/contract, banco de staging, Git e CI. Strangler Fig e roteamento gradual onde justificável.

**Oráculo:** fixtures sanitizadas com filtros, paginação, horário, timezone, acentos, acesso negado e erros. Comparar JSON semanticamente, ordenação quando contratual, exports byte-a-byte somente se necessário.

**Primeira fatia:** exportar 1 relatório em Node e passar 23 testes de referência antes de ativar em staging.

**Gatilho para RE pontual:** integração depende de DLL fechada cujo comportamento não está na fonte, e a interoperabilidade exige detalhes que os testes não revelam.

**Não fazer:** interpretar ausência de teste como autorização para inventar comportamento, reimplementar 23 endpoints antes de passar 1 contrato, copiar dados reais para o provedor de IA.
