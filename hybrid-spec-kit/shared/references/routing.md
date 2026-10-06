# Rotas e decisão

Antes de qualquer rota, aplique o filtro de escopo de `hybrid-start`. Pedidos pequenos (correção de texto, docs ou configuração, função com comportamento conhecido, bug de correção óbvia, refatoração num único arquivo, pergunta, ou algo que caiba numa sessão com cerca de 20 chamadas) são **trabalho direto**: sem artefatos, sem runner, sem skills hybrid. Medições de mercado mostram que instruções extras aumentam passos e custo (+19% a +20% só com um AGENTS.md); o kit só compensa onde evita retrabalho ou permite sessões curtas.

Classifique a demanda pela intenção, estado existente e risco, e comece na primeira etapa ainda necessária. As rotas condicionais abaixo pertencem às dez skills; não crie entrypoints adicionais só para cada variação.

| Sinal | Rota mínima |
| --- | --- |
| Ideia vaga sem repositório | problema → incertezas → primeiro resultado → preparação |
| Projeto novo | descoberta → visão/restrições → arquitetura suficiente → primeiro marco |
| Funcionalidade em legado | reconhecimento focalizado → spec → plano → fatias → implementação/verificação |
| Função ou regra pequena | `change.md` compacto → caso relevante → implementação → verificação/revisão |
| Bug de causa incerta | [diagnóstico](diagnosis.md): loop vermelho → minimizar → hipóteses → correção com regressão |
| Refatoração interna | comportamento preservado → caracterização necessária → redesenho → equivalência |
| Migração ampla | expand → lotes de migração → contract → integração final |
| Pesquisa/protótipo | pergunta → experimento/limite → evidência → decisão |
| Diff pronto | baseline → Standards e Spec separados → achados |

Use perfil compacto para mudança localizada, comportamento conhecido, baixo custo de reversão e sem decisão arquitetural relevante. Use padrão para múltiplos comportamentos/módulos, persistência ou coordenação. Use ampliado para incerteza grande, compatibilidade pública, migração difícil ou dados de alto impacto. O tamanho do diff sozinho não escolhe o perfil.

Perguntas são ordenadas por impacto × incerteza. Agrupe perguntas independentes; aguarde respostas que sejam pré-requisitos. Não repita decisão já dada, não peça fato que o ambiente revela e não invente escolha crítica. Hipótese reversível pode ser registrada e comunicada; mudança de comportamento, público, limite de dados ou autorização precisa de decisão.
