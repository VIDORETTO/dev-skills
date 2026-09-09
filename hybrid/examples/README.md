# Exemplos

`standard/reserva-estoque/` e `compact/limite-desconto/` são projetos de referência executáveis pelo runner. Os caminhos de código continuam deliberadamente ilustrativos: valide-os antes de usar uma fatia em outro repositório. Os testes criam projetos temporários completos para exercitar o runner, preservando a separação entre exemplo documental e evidência de execução.

Exemplo padrão:

```powershell
python scripts/hybrid.py validate --project examples/standard/reserva-estoque --effort 014-reserva-estoque --json
python scripts/hybrid.py graph --project examples/standard/reserva-estoque --effort 014-reserva-estoque --json
python scripts/hybrid.py render --project examples/standard/reserva-estoque --effort 014-reserva-estoque --view all --json
```

Exemplo compacto:

```powershell
python scripts/hybrid.py validate --project examples/compact/limite-desconto --effort 002-limite-desconto --json
```

`evaluation/cases.json` contém os pedidos e oráculos para avaliação comportamental. O avaliador deve ocultar o campo `expected` da executora.
