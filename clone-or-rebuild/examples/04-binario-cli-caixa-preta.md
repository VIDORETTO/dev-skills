# Exemplo 4 — Reimplementar uma função matemática de CLI nativo autorizado

**Pedido:** “Tenho um executável interno antigo que converte medidas. Quero portar para Rust sem fonte.”

### Grill-me

1. “Quais entradas, saídas e tolerâncias são exigidas? A versão do binário é fixa?”
2. “Está autorizado executar e analisar em ambiente controlado? Existem entradas reais ou regras publicadas?”

**Hipótese:** CLI interno autorizado, arquitetura x86_64, 60 fixtures, sem fonte, saída decimal.

### Decisão por fases

1. **SPEC_FIRST** se a fórmula é um padrão bem definido e os testes passam.
2. **BLACK_BOX** para descobrir arredondamento, validação e códigos de erro com inputs gerados.
3. **STATIC_RE Ghidra/REA**, apenas se divergência material depender de regras implementadas no binário que os experimentos não desvendarem.

### Experimentos

- Identidade e hash do executável; copiar para ambiente isolado.
- Testes com zero, negativos, limites, NaN/inf se permitido, conversão repetida, Unicode no CLI, erro, arredondamento e precisão.
- Em cada caso armazenar stdin/argv, stdout, stderr, exit code e versão.
- Criar binário novo com algoritmo conhecido e comparar fixtures; no caso de desvios, investigar funções específicas com símbolos/strings, depois desassemblagem guiada.

**Critério:** equivalência nos 60 casos de referência **não prova** equivalência para todas as entradas; quantificar região coberta.

**Não fazer:** executar CLI sem checar origem, anexar debugger a processo de terceiro, desativar proteção ou presumir que pseudocódigo decompilado é fonte exata.
