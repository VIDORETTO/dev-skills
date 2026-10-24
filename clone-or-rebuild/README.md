# Clone or Rebuild — skill de engenharia reversa orientada por decisões

**Versão 1.0.0 · 23/10/2026 · Português (Brasil)**

Skill portátil no formato [Agent Skills](https://agentskills.io/specification) para ajudar um agente a **entrevistar o usuário, decidir se precisa de engenharia reversa, escolher as ferramentas adequadas e reconstruir com evidências e testes**. Serve para funcionalidade, interface, API, biblioteca, desktop, mobile, executável, protocolo, jogo ou migração de legado.

> Não é o REA e não inclui decompiladores, serviços, binários ou MCP. É uma skill original de decisão, execução e verificação, inspirada em boas práticas com links para as fontes no arquivo `references/sources.md`.

## Instalação

1. Extraia o ZIP preservando a pasta `clone-or-rebuild/` e o arquivo obrigatório `SKILL.md` na raiz desta pasta.
2. Copie **a pasta inteira** para o diretório de skills aceito pelo seu agente. Exemplo comum em projetos compatíveis com Agent Skills: `.agents/skills/clone-or-rebuild/`. Para Claude Code, uma opção reconhecida é `.claude/skills/clone-or-rebuild/`. Confira a documentação do cliente se usar outra localização.
3. Reinicie/recarregue a sessão do agente se necessário. No chat, peça: **“Use a skill clone-or-rebuild. Quero reproduzir a função X do aplicativo Y. Comece a entrevista grill-me.”**
4. Quando a entrevista terminar, aprove o plano e as operações que alterem ambiente, executem o alvo ou acessem dados.

### Instalação manual por terminal (a partir do diretório que contém esta pasta)

```bash
mkdir -p .agents/skills
cp -R clone-or-rebuild .agents/skills/
python3 .agents/skills/clone-or-rebuild/scripts/validate_skill.py .agents/skills/clone-or-rebuild
```

Ou copie para `.claude/skills/` se esse for o diretório apropriado ao seu cliente. Não copie apenas `SKILL.md`; as referências são carregadas sob demanda.

## Como a skill se comporta

1. **Grill-me guiado:** não despeja 30 perguntas. Prioriza bloqueadores, pergunta pouco por rodada, verifica respostas e aprofunda quando importa.
2. **Triage de viabilidade:** pergunta se há fonte, documentação, API, OSS ou caminho mais simples. “Clonar” não significa automaticamente “descompilar”.
3. **Seleção de ferramentas:** usa fonte, Playwright, Ghidra, JADX, REA, CLI e outras opções *condicionalmente*, de acordo com o alvo.
4. **Provas antes da implementação:** versões, hashes, contrato comportamental, evidências com proveniência, casos normais/de borda.
5. **Loop de qualidade:** implementar a menor funcionalidade → comparar com oráculo → corrigir → registrar cobertura e limites.

## Navegação do pacote

```text
clone-or-rebuild/
├── SKILL.md                         # núcleo, gates e roteamento
├── README.md                        # instalação, uso, escopo
├── references/
│   ├── grill-me.md                  # entrevista progressiva
│   ├── decision-engine.md           # decisão, ROI e alternativas
│   ├── tool-routing.md              # alvos, ferramentas e pré-condições
│   ├── evidence-and-tests.md        # ledger, oráculos, testes
│   ├── quality-gates.md             # definição de pronto
│   ├── safety-and-rights.md         # autorização, IP, dados, segurança
│   ├── agent-roles.md               # papéis e handoffs
│   ├── whole-app-planning.md       # quando querem um software inteiro
│   └── sources.md                   # links e base da pesquisa
├── assets/templates/                # formulários preenchíveis
├── examples/                        # 6 cenários trabalhados
├── scripts/
│   ├── triage.py                    # sugestão de rota sem dependências
│   ├── compare_jsonl.py             # comparação determinística
│   └── validate_skill.py           # valida estrutura do pacote
└── tests/                           # testes unitários dos scripts
```

## Comandos opcionais (stdlib Python 3.9+)

```bash
python3 scripts/validate_skill.py .
python3 scripts/triage.py --source complete --target web --oracle yes --authorized yes
python3 scripts/triage.py --source none --target electron --oracle yes --authorized yes
python3 scripts/compare_jsonl.py --reference exemplos/ref.jsonl --candidate exemplos/novo.jsonl
python3 -m unittest discover -s tests -v
```

O `triage.py` não decide direitos ou riscos por você: fornece um **palpite explicável** que o agente deve revisar. O `compare_jsonl.py` usa igualdade estrutural com tolerância numérica opcional e **não executa** os programas; serve para dados sem informações sensíveis. Os arquivos de exemplo `.jsonl` dos comandos acima são nomes ilustrativos e devem ser substituídos por arquivos reais.

## Instalar REA? Só se o plano justificar

A skill oficial do [REA](https://github.com/morluto/rea) orienta a **pular REA na análise comum de um repositório-fonte completo**. A regra aqui é mais geral: só usar REA se existir uma pergunta que exija inspeção do artefato entregue, descompilação, execução observável ou múltiplos provedores. Instalação/registro do REA é uma etapa separada, opcional e sujeita a revisão das mudanças propostas.

Referências detalhadas, incluindo comparações e limitações de benchmark, estão em `references/sources.md`.

## Limitações

- Nenhuma skill garante reprodução integral, fidelidade visual ou compatibilidade só por existir.
- Disponibilidade de agentes, ferramentas, permissões, SO e formatos deve ser verificada em tempo de execução.
- Respeitar propriedade intelectual, licenças, contratos, dados pessoais e escopo de autorização é obrigatório. Uma implementação independente não dá automaticamente o direito de copiar código, ícones, marcas, assets e conteúdo protegido.
- Os scores de triagem são **heurísticas locais**, não resultados científicos nem aconselhamento jurídico.
