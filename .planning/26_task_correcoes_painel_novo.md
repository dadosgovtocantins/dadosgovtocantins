---
task: Correções do painel novo (achados da revisão)
status: concluída
criada: 2026-10-14
---

# Correções do painel novo

## Objetivo
Corrigir os 8 achados da revisão de código em `painel-municipio.dc.html`.

## Por quê
O painel novo mostra "∞"/"NaN", quebra inteiro com `v: null`, desenha ano sem dado como zero (fere a RF-55), compara IDEB com ano inexistente, exibe placeholder como nome, não acha bandeiras existentes e soma receitas intraorçamentárias na receita do estado.

## Arquivos envolvidos
| Arquivo | O que muda |
|---|---|
| `painel-municipio.dc.html` | editar (variação, cartão, série, rótulo vs., nome, bandeira, telas, validação de JSON) |
| `src/ui/data/painel_indicadores.json` | editar (receita exceto intraorçamentárias, `perAnt` do IDEB, nomes vazios) |

## Critérios de aceite
- [x] Variação com valor anterior 0 ou não numérico não mostra "∞" nem "NaN"; o cartão fica sem linha de variação.
- [x] Dado com `v` nulo ou ausente mostra "Sem dado" só naquele cartão; o painel continua renderizando.
- [x] Ano faltando na série (`null`) não é desenhado como zero: o ponto é omitido da linha.
- [x] O rótulo "vs." usa o período anterior real (`perAnt` quando existir); IDEB 2023 mostra "vs. 2021".
- [x] Nome de prefeito(a)/governador(a) vazio aparece como "... não informado(a)" com estilo `vago`; nenhum placeholder é tratado como nome.
- [x] Todos os municípios com arquivo em `bandeiras/` exibem a bandeira, incluindo Couto Magalhães (`couto-de-magalhaes-to.webp`).
- [x] A "(continuação)" de uma categoria nunca aparece em tela anterior à do começo dela (teste com categoria de 10 itens).
- [x] A receita do estado exclui as intraorçamentárias (R$ 14,88 bi) e o rótulo diz isso.

## Fora de escopo
- Ler dados reais exportados (task 29).
- Evitar o 404 da sondagem de bandeira inexistente.

## Plano
- [x] 1. Validar o formato dos JSON baixados antes de usar (fronteira).
- [x] 2. `variacao()`: proteger divisão por zero/NaN; `perAnt` no rótulo "vs.".
- [x] 3. `cartao()`: `v` nulo vira "Sem dado".
- [x] 4. `spark()`: ignorar pontos nulos.
- [x] 5. Nomes vazios por padrão; placeholder só como texto "não informado".
- [x] 6. Bandeira: exceções de slug conferidas contra a pasta `bandeiras/`.
- [x] 7. `montarTelas()`: continuação sempre depois do começo.
- [x] 8. Receita do estado exceto intraorçamentárias.
- [x] 9. Verificação no navegador.

## Segurança
S2 (validar dados na fronteira: JSON baixados), S15 (erro não derruba a página nem vaza detalhe). Demais itens: N/A (página estática, sem formulário, sem autenticação).

## Verificação
```bash
node --check <js extraído>
node test_correcoes.mjs   # Playwright: casos de borda injetados + 3 abas + mobile
```

## Decisões tomadas
- `perAnt` no dado tem prioridade; sem ele, o "vs." usa `per - passo` do indicador (`passo: 2` em IDEB e SAEB, que são bienais).
- Ponto nulo da série é omitido e a linha liga os pontos válidos (não desenha zero). Com menos de 2 pontos válidos, não há mini-gráfico.
- Texto com série de 1 ponto não gera variação ("subiu/caiu" exige dois pontos válidos).
- Bandeira de Couto Magalhães resolvida pelo objeto `MUNICIPIOS` (override de `bandeira`), sem regra especial no código. Conferido: era o único dos 86 arquivos sem correspondência.
- O 404 da sondagem da bandeira do estado continua (fora de escopo) até existir `bandeiras/estado-tocantins.webp`.
- Para manter o arquivo abaixo de 500 linhas, os objetos `MUNICIPIOS`/`ESTADO` e o `componentDidUpdate` foram compactados (493 linhas).

## Evidência (2026-10-14)
`node --check` ok. `test_correcoes.mjs` (Playwright, JSON com casos de borda injetado via `page.route`): 17/17 PASSOU, incluindo
"nenhum ∞/NaN/undefined", "v nulo mostra Sem dado só no cartão", "IDEB compara com 2021", "série com buraco: 4 pontos, sem NaN",
"continuação depois do começo: [A|B] → [B (continuação)]", "JSON inválido: aviso e página de pé",
"bandeira de Couto Magalhães aparece", "receita do estado 14,88", celular sem rolagem nas 3 abas.
