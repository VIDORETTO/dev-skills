# Teste por comportamento

Escolha o seam mais alto que continue rápido, determinístico e diagnóstico. Uma função pública é suficiente para regra pura; um fluxo persistente pode exigir banco representativo; integração externa usa Interface/Adapter controlado e contrato; jornada visual exige inspeção renderizada e interação afetada.

O caso deve atravessar a Interface que consumidor usa e descrever o que ele observa. O resultado esperado vem de requisito, propriedade válida ou exemplo calculado independentemente. Um teste que recompõe o algoritmo da implementação, acessa estado interno, verifica colaborador interno ou consulta banco por fora do Module não é oráculo independente.

Execute um caso por vez: red por comportamento ausente/incorreto, green com o mínimo, pequena refatoração com a suíte verde, depois próximo caso. Erro de ambiente, arquivo ausente ou dependência quebrada não é red válido para regra de negócio.

Mock somente no que realmente varia na seam: serviço externo, relógio, aleatoriedade, filesystem ou banco quando não houver substituto representativo. Não simule seus próprios módulos internos para obter uma passagem artificial. Se houver dois adapters reais (produção e teste), registre por que a seam existe; um único adapter pode ser indirection sem valor.

Dispensa de novo teste é exceção documentada para ajuste editorial, inspeção visual trivial, experimento descartável ou comportamento já coberto adequadamente. Ela não dispensa as verificações obrigatórias do projeto.

## Custo proporcional

Execute red/green para o comportamento novo e regressão afetada; não escreva testes que apenas reproduzem implementação nem testes novos para alterações editoriais reversíveis. Reuse cobertura válida quando já observa o comportamento. A suíte global segue os gates obrigatórios do projeto e o impacto real das mudanças. Uma avaliação longa exige runner estável e inputs congelados; qualificação pequena não substitui a amostra integral aceita. Veja [bounded-execution.md](bounded-execution.md) para handoff sem repetição de trabalho.
