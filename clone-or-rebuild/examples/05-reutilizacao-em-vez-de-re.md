# Exemplo 5 — Em vez de RE, adotar padrão ou biblioteca existente

**Pedido:** “Quero clonar o motor de geração de QR Code de outro app.”

### Grill-me

1. “O objetivo é gerar QR Code válido e compatível ou igualar detalhes específicos de layout e erros?”
2. “Tem requisito de licença, linguagem, capacidade offline, personalização ou performance?”

**Hipótese:** QR Code padrão, implementação comercial em app próprio; bibliotecas OSS compatíveis e com licença apropriada existem.

### Decisão

**REUSE + testes de interoperabilidade.** Primeiro avaliar biblioteca mantida, licença, adequação e geração em múltiplos leitores. Fazer RE do outro aplicativo só se houver requisito obrigatório, permitido e não explicado pelo padrão (ex.: convenção proprietária de payload), sempre de forma delimitada.

**Oráculo:** decodificar o QR gerado, round-trip de payload UTF-8, limites, níveis de correção de erros, diferentes tamanhos e leitores autorizados.

**Benefício:** manutenção mais baixa, menos dependência de detalhes internos de outro aplicativo e menor risco jurídico. A implementação inspirada no requisito geral não deve copiar marcas/arte.
