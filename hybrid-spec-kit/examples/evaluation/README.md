# Casos de avaliação E01–E31

`cases.json` é o protocolo reproduzível. Cada entrada contém um pedido de entrada, o resultado esperado mantido pelo avaliador e o tipo de evidência necessário. Para uma avaliação sem viés, entregue o campo `input` e os artefatos autorizados; retenha `expected` fora do contexto da executora. Registre versão do pacote, modelo, contexto, comandos executados, alterações, perguntas e limitações.

Os casos `E03`, `E12`, `E14`, `E15`, `E19`, `E22`, `E27`, `E28` e `E31` têm subchecks determinísticos cobertos pelos testes locais. Os demais ainda precisam de uma avaliação comportamental. `E20` é não aplicável porque a primeira versão não possui adapter de tracker remoto.
