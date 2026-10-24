# Gates de qualidade e definição de pronto

## Antes da implementação

- Objetivo real compreendido e escopo por funcionalidade, não “copiar tudo”.
- Abordagens comparadas; REA e descompilação justificadas apenas se necessárias.
- Autoridade e limites determinados para cada ação; operações mutantes com aprovação quando apropriado.
- Ambiente e versão/identidade do original reproduzíveis.
- Oráculo e critérios de aceite definidos **antes** da maior parte da implementação.
- Mudanças de arquitetura reversíveis e repositório com controle de versão.

## Durante a implementação

- Cada módulo novo cumpre uma fatia observável.
- Código original próprio ou dependências com licenças adequadas; não copiar material protegido sem permissão.
- Cada bug/descoberta adiciona teste regressivo onde viável.
- Não ajustar o oráculo para tornar o teste verde; alterações no contrato devem ser registradas e aprovadas.
- Testar em ambiente isolado, com dados sintéticos e sem credenciais de produção quando possível.
- Separar qualidade de interface da qualidade funcional: uma não prova a outra.

## Critérios específicos

| Eixo | Como testar | O que NÃO prova sucesso |
|---|---|---|
| Comportamento | casos diferenciais, estados, exceções, contratos | app abre sem erro |
| Visual | snapshots multi-breakpoint, inspeção de fontes/spacing, estados | screenshot único da home |
| Dados | golden files, round-trips, schema, migração/rollback | ler um único arquivo |
| Integração | APIs, retries, timeouts, limites, autenticação legítima | mock que sempre retorna 200 |
| Performance | p50/p95, carga, consumo de recursos | tempo de um run isolado |
| Acessibilidade | navegação por teclado, semântica, contraste e leitores | semelhança pixel-perfect |
| Segurança | secrets, dependências, input validation, permissões | scanner sem findings sozinho |

## Como reportar a qualidade

Não invente “98% clonado” baseado em percepção. **Taxa observada** é `testes_passados / testes_executados`, sempre com escopo e versão. “100% de 15 testes” não significa “100% do programa”. Defina também **cobertura de funcionalidades e riscos não testados**.

Relatório final deve distinguir:

- **Concluído**: teste e evidência concretos.
- **Parcial**: comportamento implementado mas lacuna identificada.
- **Não iniciado**: explicitamente fora do incremento.
- **Desconhecido**: sem método confiável de avaliação.

Marcar “pronto para produção” só após critérios do projeto, revisão de segurança, observabilidade e rollback. Para legacy migration, canary/dual run, comparação e implantação incremental podem ser mais relevantes que paridade total imediata.

## Stop rules

- Progresso estagnado em análise profunda sem hipótese decisiva → renegociar escopo.
- Erro de evidência ou mudança de versão do alvo → invalidar conclusões dependentes.
- Falta de orçamento/tempo para cobertura essencial → apresentar riscos e versão parcial.
- Dependência de artefato/acesso não permitido → parar aquele caminho e propor alternativa segura.
