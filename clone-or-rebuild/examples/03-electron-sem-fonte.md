# Exemplo 3 — Função específica de Electron sem fonte original

**Pedido:** “Quero reproduzir a função de copiar rich text de um app Electron que temos licença e autorização para estudar.”

### Grill-me

1. “Qual saída deve ficar equivalente — HTML da área de transferência, texto simples, imagens, ou tudo?”
2. “Temos binário/ASAR da versão exata e ambiente de teste autorizado? É permitido executar/copiar dados do clipboard?”

**Hipótese:** app próprio/autorizado, build 4.2, sem repositório; alvo = copiar HTML e texto simples com links.

### Decisão

**STATIC_RE seletiva + BLACK_BOX de entrada/saída**; primeira camada com inventário ASAR e `rg -uu`. **REA opcional** se rastrear renderer→preload→IPC→main ficar difícil e a integração estiver disponível. Não tentar reimplementar o aplicativo inteiro.

### Ferramentas e investigação

1. Registrar SHA-256 de `app.asar`, versão e permissões.
2. Extrair/inventariar em cópia autorizada com `@electron/asar`; pesquisar entradas de menu, `clipboard`, `contextBridge`, `ipcRenderer`, `ipcMain` e handlers associados.
3. Distinguir candidatos de código/strings de comportamento de execução confirmado.
4. Se necessário, usar REA para seguir grafo/relacionamentos e preservar evidências.
5. Executar 12 casos num ambiente de teste: texto vazio, rich text, `<strong>`, links, Unicode, lista, conteúdo grande, falha, permissões.
6. Implementar contrato independente com API de clipboard adequada ao destino; comparar HTML e texto por normalização previamente justificada.

### Entrega honesta

“Fluxo de rich text reproduzido para os 12 casos; imagens incorporadas e interações não cobertas.”
