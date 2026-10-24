# Exemplo 2 — Reprodução de UI com Playwright, não com Ghidra

**Pedido:** “Quero uma interface semelhante ao nosso dashboard antigo hospedado na web.”

### Grill-me

1. “Você precisa fidelidade visual, mesmos fluxos ou ambos? Qual página prioritária?”
2. “Você controla o site e tem autorização para screenshots, DOM/CSS e observação de rede em staging?”
3. “Qual ambiente, viewport e dados fixos permitem comparar a página?”

**Hipótese:** dashboard próprio, sem código disponível; design autorizado; page principal e filtro de datas, mobile também.

### Decisão

**BLACK_BOX visual + SPEC_FIRST funcional.** Sem Ghidra e sem REA no começo. DevTools + Playwright para layout, estados, acessibilidade, screenshots e navegação autorizada. Se o bundle precisar explicar uma regra não visível e isso for permitido, avaliar análise JS/REA dirigida à dúvida.

### Plano de evidência

- Capturar desktop 1440×900 e mobile 390×844 com fontes, tema, locale, timezone e dados fixos.
- Documentar largura dos containers, tipografia, cores, spacing, imagens e responsividade com DOM/CSS observado, em vez de inventar CSS por aproximação.
- Capturar estado loading, vazio, erro, filtro aberto e resultado após clique.
- Criar contrato de filtros e estados com casos de borda.
- Criar componentes independentes, testar navegação/teclado e comparar snapshots no mesmo ambiente.

### Exemplo ilustrativo de teste

```ts
import { test, expect } from '@playwright/test';

test('dashboard com dados fixos', async ({ page }) => {
  await page.goto('http://localhost:3000/dashboard?fixture=demo');
  await expect(page.getByRole('heading', { name: 'Visão geral' })).toBeVisible();
  await expect(page).toHaveScreenshot('dashboard-desktop.png', { fullPage: true });
});
```

Não pressupor que snapshot do Playwright seja a captura do sistema de terceiro. Baseline, ambiente e permissões precisam ser preparados. Screenshot igual **não comprova** funcionamento do backend.
