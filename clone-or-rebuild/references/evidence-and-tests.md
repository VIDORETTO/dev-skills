# Evidência, oráculos e testes diferenciais

## Ledger de evidências

Toda afirmação significativa deve ter:

| Campo | Significado |
|---|---|
| `id` | Identificador local estável (`EV-001`) ou ID retornado pelo REA |
| `claim` | Afirmação específica e falsificável |
| `state` | `OBSERVADO`, `INFERIDO`, `DESCONHECIDO` ou `INDISPONIVEL` |
| `authority` | Fonte: repo, bytecode, arquivo, DOM, documentação, runtime autorizado, relato de usuário |
| `location` | arquivo:linha, endereço/símbolo, URL, nome do teste, tela, hash |
| `target_identity` | nome, versão, hash, SO e ambiente relevantes |
| `method` | comando/leitura/chamada/teste usado, sem incluir segredos |
| `limits` | cobertura, confiança, risco de erro e condição não testada |
| `next_proof` | experimento que confirmaria ou refutaria a hipótese |

**OBSERVADO** refere-se somente ao objeto efetivamente examinado: ler código prova o que o código *contém*, não o que o programa *fez*. `INFERIDO` deve dizer por qual raciocínio; `DESCONHECIDO` nunca deve ser apresentado como confirmado. Evidência de runtime inclui pré-condições, ambiente, entradas e saída. Diferencie execução simulada de execução do original.

## Protocolo de investigação

1. Liste no máximo 3 hipóteses mais valiosas por rodada.
2. Para cada hipótese: predição → experimento menor possível → evidência → conclusão com ressalva.
3. Evidência contraditória não deve ser descartada: compare versão, configuração, permissão, cache, dados, SO e ordem das ações.
4. Se um teste falhar, reduza o caso antes de ampliar a engenharia reversa.
5. Registre resultados no `assets/templates/evidence-ledger.csv` e testes em `assets/templates/test-matrix.csv`.
6. Marque buscas negativas como delimitadas: “não localizei em X/Y”, não “não existe”.

## Tipos de oráculo

- **Contratos publicados:** OpenAPI, RFC, parser formal, fixtures e exemplos, quando lícitos.
- **Fonte executável:** testes do programa que já existe, especialmente com entradas estáveis.
- **Golden master / characterization:** registrar comportamento atual antes de mudar o legado; validar se é intencional ou bug legado.
- **Diferencial:** mesma entrada no original e novo, saída normalizada quando apropriado.
- **Propriedades/metamórficos:** invariantes (importar→exportar preserva informação, ordenação idempotente, operações reversíveis).
- **UI visual:** snapshots em tamanho, tema, fontes, navegador e dados equivalentes; verificar também navegação e estados.
- **Performance:** distribuição p50/p95 de latência, memória, throughput ou FPS sobre entradas representativas, ambiente consistente.

Sem oráculo confiável, rebaixe o compromisso de “clone exato” para “implementação plausível baseada nas observações disponíveis”.

## Matriz mínima de testes por fatia

1. **Happy path:** comportamento principal com entrada típica.
2. **Boundary:** zero/vazio, mínimo/máximo, Unicode, arquivo grande, condições de tempo.
3. **Erro:** resposta inválida, desconexão, falta de permissão, dados corrompidos.
4. **Estado e sequência:** ordem de operações, repetição, idempotência, persistência, desfazer.
5. **Compatibilidade:** plataforma/versão de referência, dados legados, integração.
6. **Não funcional:** acessibilidade, segurança, tempo, memória quando críticos.

Defina previamente *o que comparar*: bytes exatos, JSON estrutural, semântica, renderização visual ou observação humana. Para floats e relógio, especifique tolerâncias. Não normalize diferenças relevantes para ocultar falhas.

### Exemplo de contrato

```text
Feature: exportar CSV do editor
Dado: 3 linhas com aspas, acentos, newline embutido
Quando: usuário clica em Exportar
Então: arquivo UTF-8 e escaping conforme contrato de referência
Casos: vazio, 100k linhas, permissões negadas, nomes duplicados
Oráculo: 12 fixtures do sistema original + parser CSV independente
Tolerância: equivalência semântica por coluna; ordem preservada
```

### Comparação local JSONL

Se um teste é representado por um JSON por linha (mesma ordem), execute:

```bash
python3 scripts/compare_jsonl.py --reference /path/original.jsonl --candidate /path/novo.jsonl --tolerance 0.000001
```

Os relatórios mostram divergências por linha/caminho, não um simples “passou”. Proteja amostras com dados pessoais; use conteúdo sintético sempre que possível. O script não roda binários e não verifica direitos.

## Artefatos de trabalho

Salvar um `target-manifest` com hash, versão e ambiente; `decision-record`; `feature-spec`; `evidence-ledger`; `test-matrix`; relatório de validação. Isso torna o trabalho reproduzível e evita reanálises cara. Use os modelos do diretório `assets/templates/`.
