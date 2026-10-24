# Router técnico — escolher o menor instrumento suficiente

Nenhuma ferramenta é “sempre a melhor”. Identifique primeiro **alvo real, pergunta, host, versão e capacidades instaladas**. Prefira inventário barato e análise focada. Não execute apps desconhecidos por padrão; não confunda leitura estática com autorização para instrumentação dinâmica.

| Tipo de alvo | Começar com | Escalar se faltar evidência | Armadilha comum |
|---|---|---|---|
| Repo com fonte | `git`, `rg`, AST, testes, documentação, coverage | build de referência, traces de ambiente | iniciar REA sem necessidade |
| Web/UI pública ou própria | DevTools, DOM/CSS, Playwright, screenshots, rede autorizada | observação controlada, análise dos bundles se permitido | confundir screenshot com comportamento |
| API/serviço | OpenAPI, SDK, exemplos, logs, contratos, testes HTTP autorizados | captura HAR/mitmproxy sob controle do ambiente | inferir semântica só pelo nome do endpoint |
| Electron / JS empacotado | `file`, inventário do pacote, `@electron/asar`, `rg -uu`, sourcemaps | REA `analyze_javascript_application`; runtime autorizado | esquecer `.webpack`, preload, IPC e addons nativos |
| Binário nativo ELF/PE/Mach-O | `file`, `readelf`/`objdump`, `otool`/`nm`, `strings`, imports, símbolos | Ghidra, IDA, Hopper, Binary Ninja; REA como interface | pseudocódigo ≠ execução; arquivos sem símbolos |
| .NET | metadata, ILSpy/dnSpyEx onde licenciado, `ildasm` quando disponível | REA managed inspection, execução controlada | supor que CIL equivale ao fonte original |
| Android | manifest, `jadx`, `apktool`, ADB autorizado | REA Android, Frida sob autorização em ambiente de teste | APK/compilação e conteúdo offline podem divergir |
| iOS / app Apple | pacotes e plists, símbolos e recursos autorizados | ferramentas Mach-O e tracing controlado se permitido | limitações de plataforma, assinatura, direitos |
| Rust/Go | build metadata, `go version -m`, strings/imports, símbolos | disassembler quando falta lógica de runtime | linguagem aparente não garante semântica |
| Firmware | formatos, hashes, binwalk/unblob em cópia | análise ISA e emulação isolada autorizada | extração ≠ comportamento hardware |
| Capturas de rede / protocolo | especificações, HAR/pcap existentes, `tshark`, Wireshark | testes de interoperabilidade autorizados | dados sensíveis e tráfego de terceiros |
| Arquivos/documentos | formato e esquema publicados, parsers open source, fixtures | inspeção binária só de campos desconhecidos | usar byte-match quando equivalência semântica basta |
| Jogos | engine e scripts disponíveis, gravações determinísticas, mecânicas isoladas | inspeção de recursos/binários licenciados | copiar assets, conteúdo, marcas ou anti-cheat |
| Sistema legado | repo, banco/esquema, testes de caracterização, tracing em staging | módulo fechado pontual, migração incremental | trocar tudo antes de ter contratos/rollback |

**REA não é substituto dos motores**: integra diversos provedores, facilita evidências e sessões, mas análise profunda de nativos geralmente precisa Ghidra/IDA/Hopper ou motor compatível. Uma instalação de skill do REA isolada **não registra o MCP**. Consulte links oficiais em `sources.md`.

## Critérios para escolher REA vs CLI simples

Escolha **CLI** quando a pergunta se resolve com metadados, símbolos, pesquisa de texto, extração ASAR, `go version -m`, leitura estruturada ou pequeno conjunto de comandos já instalado. Economiza setup, contexto e latência.

Escolha **REA** quando precisa de um workflow integrado que devolva evidências, retenha sessões, una análises estáticas/artefatos/runtime, use vários provedores ou exija interação mais profunda com ferramenta que o agente não dirige bem pela CLI.

Escolha **Ghidra/IDA/Binary Ninja diretamente** quando seu processo de trabalho já domina um motor e acrescentar MCP não gera benefício. Avalie licenças comerciais e limitações de automação antes do uso.

**Confirme versão real antes de seguir nomes de ferramentas**: a documentação main do REA e a versão publicada no npm podem não coincidir; consulte `tools/list`/schemas reais quando disponível. Evite `doctor` recorrente sem erro: só diagnostique quando conexão/capacidade exigida estiver ausente ou stale.

## Sequência de pesquisa eficiente

1. Identidade: caminho, magic bytes, hashes e versão (não depender apenas de extensão).
2. Inventário: nomes, módulos, imports, exports, recursos, configs e pistas.
3. Hipótese: “que função/fluxo preciso provar?”
4. Busca focada: strings relevantes, símbolos, referências cruzadas, um processo, uma tela, um endpoint.
5. Verificação: teste de input/output ou observação legítima; preserve proveniência.
6. Só então ferramenta mais cara/profunda, se ela responder pergunta material ainda aberta.

### Padrões específicos

- **Electron**: identificar main/preload/renderer e IPC; usar `rg -uu` para arquivos ocultos; limitações de source maps e minificação.
- **Web visual**: medir fontes, espaçamento, estilos e dimensões reais; coletar estados e breakpoints; usar Playwright em ambiente estável e dados sanitizados.
- **Nativo**: prefira símbolos e referências para mapear funções antes de gerar pseudocódigo em massa.
- **Protocolo**: primeiro leia especificação, depois faça pares de input/output com tráfego consentido; não capture sessão alheia.

### Fontes recomendadas

- REA oficial: https://github.com/morluto/rea
- Skill REA: https://github.com/morluto/rea/blob/main/.agents/skills/reverse-engineer-anything/SKILL.md
- Ghidra: https://github.com/NationalSecurityAgency/ghidra
- JADX: https://github.com/skylot/jadx
- Playwright screenshots: https://playwright.dev/docs/test-snapshots
- leanrea (benchmark limitado, não “verdade universal”): https://github.com/aicodeking/leanrea
