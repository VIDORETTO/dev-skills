# Diagnóstico de bug

Use quando a causa não é óbvia, a falha é intermitente ou houve regressão entre dois estados conhecidos. Um bug com correção evidente é trabalho direto.

1. **Loop vermelho primeiro.** Antes de formular hipóteses, tenha um comando já executado que reproduza o sintoma exato relatado e que seja determinístico, rápido e executável sem humano. Em ordem: teste no seam que alcança o bug, script HTTP/CLI com fixture, navegador headless, replay de payload capturado, harness mínimo, loop de propriedade/fuzz, `git bisect run`, comparação entre versões. Para falha intermitente, aumente a taxa de reprodução (repetição, paralelismo, estresse) até ela ficar depurável. Sem loop, pare e peça acesso, artefato capturado ou permissão para instrumentar.
2. **Minimize.** Corte entradas, chamadores, configuração e passos um de cada vez até que todo elemento restante seja necessário para o vermelho.
3. **Hipóteses falseáveis.** Liste 3 a 5, ordenadas, cada uma no formato "se X for a causa, mudar Y faz o bug sumir". Mostre a lista ao usuário e siga em frente se ele não estiver presente.
4. **Instrumente uma variável por vez.** Prefira debugger; use logs com prefixo único (`[DEBUG-a4f2]`). Em regressão de desempenho, meça antes e bisseccione.
5. **Corrija com regressão.** Transforme o caso mínimo em teste no seam correto, veja falhar, corrija, veja passar e rode de novo o loop original. Se não existir seam correto, registre isso como achado de arquitetura.
6. **Limpe.** Remova os logs pelo prefixo e registre a hipótese confirmada no commit ou no checkpoint.

Adaptado de `mattpocock/skills` (`diagnosing-bugs`).
