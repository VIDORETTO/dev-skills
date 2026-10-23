# 04: Avaliar evidências e classificar achados

## Força da evidência

| Nível | O que conta | Basta para |
|---|---|---|
| **A** | Fonte oficial (docs, changelog, release, aviso de depreciação, model card) **ou** teste feito agora nesta sessão | Corrigir algo quebrado, atualizar versão/link/comando |
| **B** | Benchmark ou comparação reproduzível com números e método; issue confirmada pelo mantenedor | Propor trocar uma ferramenta/técnica não validada pela skill |
| **C** | Dois ou mais relatos independentes e concordantes da comunidade (threads diferentes, autores diferentes) | Registrar como alternativa a testar; mudar recomendação leve |
| **D** | Relato isolado, post viral, vídeo sem demonstração, blog sem data | Só pista para pesquisar mais; nunca muda a skill sozinho |

Para trocar algo que a skill **validou em uso real**, exija A ou B **e** um caminho de teste (A/B) antes de remover o antigo.

## Sinais de alerta (rebaixe a evidência)

- Listicles "Top 10 ferramentas de <ano>" sem método, com links de afiliado ou texto genérico de IA.
- Comparação feita pelo próprio fornecedor de uma das opções.
- Página sem data, ou com o ano só no título.
- Post viral sem código, sem números ou sem como reproduzir.
- Estrelas do GitHub crescendo rápido sem issues, commits ou usuários reais.
- Ferramenta que só aparece em uma fonte, ou em várias que copiam o mesmo texto.
- Opinião sobre versão antiga apresentada como atual.

## Sinais de confiança

- Mantenedor confirmando em issue, release ou thread.
- Números com método (dataset, hardware, versão) e, melhor ainda, script de reprodução.
- Consenso entre comunidades diferentes (ex.: Reddit + HN + issues).
- Relatos negativos detalhados também (quem usou de verdade relata problemas).
- Adoção visível: dependentes, downloads, menções em projetos sérios.

## Classificação dos achados

| Classe | Significado | Ação padrão |
|---|---|---|
| **Quebrado** | Não funciona mais: link 404, pacote removido, flag inexistente, API desligada, modelo retirado | Corrigir (com nível A) |
| **Obsoleto** | Funciona, mas foi descontinuado ou tem prazo para acabar; ou tem vulnerabilidade conhecida | Atualizar ou migrar, com nota de prazo |
| **Superado** | Existe opção claramente melhor para o objetivo da skill | Se o item não foi validado e a evidência é A/B: trocar. Se foi validado: alternativa + critério de A/B |
| **Novo** | Ferramenta, técnica ou recurso que a skill não cita e que serve ao objetivo | Adicionar como opção (com quando usar e quando não usar) ou como alavanca a testar |
| **Confirmado** | Continua sendo a escolha certa | Registrar a verificação e a data (isso também é atualização) |
| **Incerto** | Sinais contraditórios ou evidência fraca | Não mudar; listar no relatório com o que falta para decidir |

## Confiança e impacto

Dê a cada achado:

- **Confiança:** alta (A, ou B+C), média (B ou C), baixa (D).
- **Impacto:** crítico (a skill falha ou causa dano/custo), alto (resultado visivelmente melhor), médio (conveniência, custo menor), baixo (cosmético, link, redação).

Priorize no relatório: crítico/alta primeiro; baixo/baixa pode ficar só listado.

## Conflitos

- Oficial contra comunidade: o oficial diz o que **deveria** acontecer, a comunidade o que **acontece**. Registre os dois e, se possível, teste.
- Comunidades em desacordo: geralmente é dependência de contexto (hardware, tamanho do projeto, sistema operacional). Escreva a regra condicional ("use X quando…, Y quando…") em vez de escolher um lado.
- Contexto do repositório (Fase 3) contra a internet: uma decisão registrada localmente com motivo vale até que o motivo deixe de existir.
