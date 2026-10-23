# 01: Entender a skill (perfil)

Antes de pesquisar qualquer coisa, monte o **perfil** da skill-alvo. Ele é o mapa da pesquisa: diz o que procurar, onde procurar e o que não pode ser mexido.

## Como ler

1. Leia o frontmatter: `name` e `description` dizem o objetivo declarado e os gatilhos.
2. Leia o SKILL.md inteiro e **todas** as referências, scripts e assets. Detalhes voláteis costumam estar nas referências (parâmetros, comandos, versões), não no SKILL.md.
3. Leia o histórico: `git log --format='%cs %s' -- <pasta>` mostra quando cada parte mudou e por quê. Mensagens como "fix: X quebrou com a versão Y" explicam pins.
4. Procure arquivos que a skill já usa para registrar conhecimento: fontes, fronteira/estado da arte, falhas, casos, changelog. Eles dizem o que já foi pesquisado e quando.
5. Procure instruções de autoatualização dentro da skill ("repita esta pesquisa", "o ecossistema muda toda semana", "pesquise novidades antes de…"). Elas indicam onde o autor espera mudança e quais fontes ele confia.

## O perfil

Escreva o perfil num arquivo de trabalho (scratchpad ou temporário), não dentro da skill:

```markdown
# Perfil: <nome-da-skill>   (revisão de AAAA-MM-DD)

**Objetivo em uma frase:** a skill existe para <resultado> para <quem>, em <contexto>.
**Domínio:** <ex.: IA generativa de vídeo / DevOps em VPS / engenharia de prompt / design instrucional>
**Volatilidade:** alta | média | baixa → janela de recência: <N meses>
**Última revisão conhecida:** <data do git ou do arquivo de fontes>
**Host e restrições:** <Claude Code, Codex…; GPU alugada; só biblioteca padrão; Windows/PowerShell…>

## Eixos voláteis
| Eixo | Itens citados (arquivo:linha) | Pergunta para a pesquisa |
|---|---|---|
| Ferramentas/serviços | … | Ainda é a melhor opção? Preço/limite mudou? |
| Modelos | … | Há versão nova ou substituto melhor? |
| Bibliotecas/pacotes/versões | … | Versão atual? Mudança que quebra? |
| APIs, CLIs e flags | … | Ainda funcionam assim? Algo foi descontinuado? |
| Técnicas e boas práticas | … | O consenso mudou? Há técnica melhor? |
| Parâmetros e limiares | … | Ainda valem com as versões novas? |
| Links e fontes | … | Vivos? Atualizados? |

## O que é validado (não trocar sem evidência mais forte)
- <receita/regra> — validada em <caso/arquivo>

## Pins intencionais
- <item fixado> — motivo: <…> — o motivo ainda vale? → verificar

## Fora do escopo da atualização
- <princípios estáveis, teoria, preferências do usuário>
```

## Volatilidade

A volatilidade decide a janela de recência e quanto esforço cada eixo merece:

| Volatilidade | Exemplos | Janela | Esforço |
|---|---|---|---|
| **Alta** | Modelos de IA e seus workflows (ComfyUI, LoRAs), ferramentas de agentes, preços e limites de API, CLIs novas, prompts para modelos específicos | 1–3 meses; olhe também a última semana | Pesquisa por item + aberta, sempre |
| **Média** | Frameworks web, bibliotecas, ferramentas de DevOps, boas práticas de segurança, versões de runtime | 6–12 meses | Versões, changelog, descontinuações, alternativas principais |
| **Baixa** | Princípios (design instrucional, arquitetura, escrita técnica), teoria, comandos POSIX clássicos | 12–24 meses | Só links, referências citadas e mudanças de consenso grandes |

Uma mesma skill pode ter eixos com volatilidades diferentes. `vps-production-agent`, por exemplo, tem princípios estáveis (backup antes de mudar) e itens voláteis (versão do Node no script do NodeSource, flags do Certbot).

## Sinais de que algo foi validado

- Arquivos de caso, falhas ou QA com números ("lip sync 0,41 → 0,67", "testado em 4 rodadas").
- Regras escritas como "(e por quê)" com um incidente real por trás.
- Mensagens de commit `fix:` ligadas àquela regra.
- Exemplos reais em `assets/`.

Nesses pontos, a atualização só propõe trocar quando a fonte nova é mais forte (oficial + reprodução, ou teste feito agora). Caso contrário, registre como alternativa com o critério de quando experimentar.
