# Exemplo 6 — Pedido de “clonar o software inteiro”

**Pedido:** “Quero recriar um editor desktop inteiro, igualzinho.”

### Grill-me mínimo

1. “Você precisa 1:1 em aparência, compatibilidade de arquivos, comportamento ou apenas os cinco fluxos que usuários realmente utilizam?”
2. “Qual versão, plataforma e nível de acesso têm? Existe fonte/documentação ou dependemos de observar a execução?”
3. “Quais são os cinco fluxos que tornariam uma versão inicial útil? Podemos medir cada um em exemplos reais?”

**Hipótese:** editor antigo da própria empresa, sem fonte, com formatos documentados e projeto novo multiplataforma.

### Decisão

**SPEC_FIRST + BLACK_BOX**, ferramenta pontual para plugins fechados só se imprescindível. Priorizar importação, edição básica, salvamento, exportação e recuperação de erro; deixar plugins, extensões e configurações avançadas para marcos posteriores.

### Catálogo inicial

| Capacidade | Prioridade | Oráculo | Status inicial |
|---|---|---|---|
| Abrir documentos | crítica | 30 fixtures | não iniciado |
| Editar/salvar | crítica | round-trip e golden files | não iniciado |
| Exportar | crítica | arquivos de referência | não iniciado |
| Temas/atalhos | importante | UI + testes de teclado | não iniciado |
| Plugin complexo | opcional | ainda desconhecido | excluído da fase 1 |

### Como reportar

“Versão 0.1 reproduz 3/5 fluxos críticos catalogados com 51/56 testes aprovados; plugin não está incluído; 2 formatos têm divergências”. Não dizer “91% do aplicativo clonado”: essa porcentagem não mede todas as funcionalidades possíveis.

### Referência operativa

`references/whole-app-planning.md`: mapear funcionalidades e dependências, escolher fatias com critérios de sucesso e não confundir porcentagem de teste com completude.
