# Motor de decisão — quando NÃO fazer engenharia reversa

## Primeiro, classifique a pergunta

Um usuário pode dizer “clonar” querendo: (a) mesmo comportamento; (b) UX parecida; (c) interoperabilidade; (d) migração; (e) uma feature inspirada; (f) reconstituição bit-a-bit. O método e o custo mudam muito. Não presuma que “mais RE” aumenta qualidade.

## Árvore operacional

```text
O usuário autorizou a ação concreta sobre o alvo/dados?
  NÃO / INCERTO -> limitar a plano/alternativas; esclarecer alcance de autorização
  SIM
    Existe solução comprável, open source, API ou padrão que atenda ao requisito?
      SIM -> REUSE + provas de licença/adequação; comparar custo de integração
      NÃO / NÃO CONVÉM
        Existe fonte atual, completa, legalmente utilizável e suficiente?
          SIM -> SOURCE_FIRST: testes + leitura de repo + caracterização
          PARCIAL -> SOURCE_FIRST + HYBRID_RE apenas para as lacunas
          NÃO
            Há contrato/documentação/testes de comportamento suficientes?
              SIM -> SPEC_FIRST: implementar contrato e testar
              NÃO
                Existe forma legítima de observar o comportamento original?
                  SIM -> BLACK_BOX: experimentos + oráculo + testes diferenciais
                  NÃO -> reformular escopo, obter artefato/acesso ou STOP
                Falta explicação sobre módulo empacotado/compilado?
                  SIM -> STATIC_RE e, com aprovação específica, DYNAMIC_RE
                  NÃO -> continue BLACK_BOX/SPEC_FIRST
```

**INCREMENTAL_MIGRATION**: preferir extração por capacidade/contrato quando existe legado em produção; não cortar tudo de uma vez se migração gradual e rollback são viáveis.

**STOP**: se impedimentos legais, de segurança, de acesso ou de verificabilidade tornam a execução inadequada, explique e ofereça projeto original, documentação pública, API ou alternativa aberta.

## Regra da fonte — com nuances

REA oficial: use quando uma afirmação **depende do binário/pacote/runtime** ou não pode ser estabelecida a partir do código. Para arquitetura normal de **repositório completo**, não rodar readiness/provider do REA. Mas código-fonte disponível pode ser incompleto, divergente do deploy, inacessível em um componente compilado, ou diferente do comportamento observado. Nesses casos justifique **RE pontual**, não trate como proibição absoluta.

| Fonte disponível? | Exemplo | Abordagem |
|---|---|---|
| Completa + mesma versão + confiável | Repo interno com testes | SOURCE_FIRST |
| Parcial | Frontend disponível, DLL sem código | SOURCE_FIRST + STATIC_RE na DLL se necessário |
| Completa mas artefato divergente | Código diz X, app distribuído faz Y | Source diff + build identity + inspeção delimitada do artefato |
| Sem código, API documentada | Serviço com OpenAPI | SPEC_FIRST ou REUSE; não decompilar por costume |
| Sem código nem contrato | Binário próprio que processa arquivos | BLACK_BOX → STATIC_RE para lacunas específicas |
| Sem acesso/sem autorização | Serviço privado de terceiros | Projeto independente baseado no que pode ser usado legitimamente |

## Comparação de valor, custo e verificabilidade

Aplique **somente como heurística** (não é benchmark científico). Para cada abordagem plausível marque em escala `0/1/2`:

- Capacidade de atingir o requisito (`F`: 0 ruim, 2 alta)
- Verificabilidade com dados/oráculo (`V`: 0 ausente, 2 forte)
- Autoridade e risco (`A`: 0 não permitido, 1 condicionado, 2 autorizado)
- Custos total de descoberta + implantação + manutenção (`C`: 0 alto, 2 baixo)
- Tempo e reversibilidade (`T`: 0 ruim, 2 favorável)

Pontuação explicativa: `S = 3F + 3V + 2A + 2C + T` (máx 22). **Veto:** `A=0` impede aquela abordagem, mesmo que a nota seja alta. Não apresente os números como ciência ou substitua julgamento contextual. Documente suposições. Calcule pelo menos SOURCE_FIRST, REUSE, SPEC_FIRST, BLACK_BOX e RE somente quando aplicáveis.

### Compensa fazer RE profunda?

Só quando existe uma **lacuna específica** cuja resolução vale mais do que a análise:

- Qual detalhe crítico ainda não sabemos?
- Qual artefato evidencia esse detalhe?
- Qual experimento mais barato pode resolvê-lo?
- Um componente OSS ou implementação funcionalmente equivalente resolveria?
- O resultado mudaria o projeto ou apenas satisfaria curiosidade?
- Há teste que prova a hipótese após implementação?

Se o custo marginal da RE superar o benefício provável, pare a investigação e escreva uma implementação original baseada nos requisitos aceitos. Não invente fidelidade.

## Documento de decisão que o agente deve emitir

```text
Resultado buscado:
Fonte/docs/API/OSS existentes:
Evidência do que falta:
Opções comparadas + trade-offs:
Abordagem escolhida e motivo:
Ferramenta inicial + quando promover para REA ou motor profundo:
Autorização e limites:
Experimento curto de viabilidade:
Critérios de sucesso / condição de parar:
```

Consulte `assets/templates/decision-record.md` para preencher.
