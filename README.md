# Hybrid development skills

Pacote local da primeira versão do sistema híbrido descrito em `ARQUITETURA-HIBRIDA-SKILLS.md` 1.2. Ele combina contrato comportamental, domínio, desenho de Modules/Interfaces/Seams, fatias verticais, execução por ticket, evidência, retomada e revisão separada de Standards e Spec.

O pacote contém dez skills distribuíveis em `skills/`, uma fonte compartilhada em `shared/`, o runner determinístico em `scripts/hybrid.py`, exemplos, testes e o protocolo de avaliação. Os repositórios `spec-kit/` e `mattpocock-skills-filtered/` da raiz foram preservados como fontes de consulta.

## Adoção local

O formato detectado neste ambiente é uma pasta de skill contendo `SKILL.md` com frontmatter YAML. A instalação local copia as dez pastas para `.agents/skills` quando essa pasta existe; se o projeto já usa `.cursor/skills` ou `.github/skills`, passe essa raiz explicitamente. Em um projeto novo, a raiz padrão é `.agents/skills`.

O runner não tem dependências externas e requer Python 3.10 ou posterior. Git é opcional: com commits ele registra o SHA; sem commits usa fingerprint de inventário.

Partindo desta pasta do pacote:

```powershell
python scripts/hybrid.py install --project C:\caminho\do\projeto --json
python .hybrid/hybrid.py init --project C:\caminho\do\projeto --json
```

`install` também coloca as referências em `.agents/shared` (ao lado das skills), uma cópia para o runtime em `.hybrid/shared`, e o runner em `.hybrid/hybrid.py`. Arquivos diferentes já existentes geram conflito e ficam preservados; só use `--force` depois de revisar o inventário. O comando não instala globalmente, altera configurações pessoais, publica, cria tracker remoto ou executa serviço externo.

Para outra raiz de skills:

```powershell
python scripts/hybrid.py install --project C:\caminho\do\projeto --skill-root .cursor/skills --json
```

## Fluxo rápido

Em um projeto adotado, use `$hybrid-start` para classificar ou retomar. Depois, o fluxo padrão é `$hybrid-discover` → `$hybrid-domain` quando necessário → `$hybrid-specify` → `$hybrid-plan` → `$hybrid-slice` → `$hybrid-check` → `$hybrid-implement` → `$hybrid-verify` → `$hybrid-review`. A skill de entrada pula fases que já têm artefatos atuais.

Para iniciar um esforço manualmente:

```powershell
python .hybrid/hybrid.py init --project . --mode standard --json
python .hybrid/hybrid.py scaffold --project . --effort 014-reserva-estoque --title "Reserva de estoque" --json
```

Preencha `spec.md`. No perfil padrão, escreva `plan.md`, crie tickets a partir de `shared/templates/standard/ticket.md`, valide e gere as visões:

```powershell
python .hybrid/hybrid.py validate --project . --effort 014-reserva-estoque --json
python .hybrid/hybrid.py graph --project . --effort 014-reserva-estoque --json
python .hybrid/hybrid.py render --project . --effort 014-reserva-estoque --view all --json
python .hybrid/hybrid.py package --project . --effort 014-reserva-estoque --ticket TK-001 --json
```

O pacote só retorna `ready: true` quando contrato e plano estão aceitos/prontos, os insumos canônicos estão registrados e atuais, os blockers estão satisfeitos e o ticket contém todas as seções do pacote. Quando falha, o campo `errors` explica a reconciliação necessária.

No perfil compacto, `scaffold --mode compact` cria `change.md`; ele reúne contrato, plano breve, tarefas e limitações. Não crie tickets ou `tasks.md` concorrentes para essa mudança.

Para executar uma fatia, entregue à executora a própria `tickets/TK-xxx.md`, os caminhos indicados em “Leitura em ordem”, o contrato e o plano referenciados. Ela pode receber apenas esse pacote e as referências compartilhadas. Rode `package` para conferir a prontidão, implemente um comportamento por vez e registre evidência:

```powershell
python .hybrid/hybrid.py ticket update --project . --effort 014-reserva-estoque --ticket TK-001 --status in_progress --json
python .hybrid/hybrid.py evidence add --project . --effort 014-reserva-estoque --ticket TK-001 --acceptance-refs AC-001 --procedure "python -m pytest tests/stock/test_reservation.py -q" --result passed --executed --path src/stock --path tests/stock --observations "resultado observado" --json
```

O primeiro comando atualiza estado do ticket; não é prova de teste. Resultados `passed`, `failed` e `partial` exigem `--executed` e pelo menos um `--path` existente. Use `not_run` e uma limitação concreta quando o ambiente impedir a execução. `todo.md`, `backlog.md` e `verification.md` são projeções e não devem ser editados como listas concorrentes.

## Retomada e convergência

```powershell
python .hybrid/hybrid.py start --project . --effort 014-reserva-estoque --json
python .hybrid/hybrid.py invalidate --project . --effort 014-reserva-estoque --json
python .hybrid/hybrid.py invalidate --project . --effort 014-reserva-estoque --write --json
python .hybrid/hybrid.py check --project . --effort 014-reserva-estoque --mode convergence --json
python .hybrid/hybrid.py dedupe --project . --effort 014-reserva-estoque --write --json
```

Checkpoints usam escrita atômica e `--expected-revision` para detectar escrita concorrente. Uma mudança de contrato, plano, código sob teste ou ambiente invalida apenas evidências afetadas depois de classificação. A mesma lacuna aberta é identificada por uma chave estável e não gera outra correção.

## Validação do pacote

```powershell
python scripts/hybrid.py package-validate --json
python -m unittest discover -s tests -v
```

`package-validate` verifica as dez skills, frontmatter, tamanho, links relativos, schemas e compilação do runner. O teste de unidade exercita os invariantes no workspace temporário e nos fixtures. Isso não substitui a avaliação comportamental por modelo: os casos E01–E31 estão em `examples/evaluation/` e seu estado é reportado em [docs/evaluation.md](docs/evaluation.md).

O registro executado por caso, com procedimento, revisão testada e limitação, está em [docs/validation-report.md](docs/validation-report.md).

## Limites desta versão

O pacote trabalha localmente. Não inclui adapter de tracker remoto (E20 é não aplicável), preset Spec Kit, motor genérico de workflows, GUI, publicação, merge, deploy, instalação global ou medição comparativa de custo/economia. Consultas de documentação atual para bibliotecas, SDKs, APIs, CLIs e serviços ficam a cargo da skill `hybrid-plan` por meio do Context7 quando essa capacidade existir.
