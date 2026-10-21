---
task: Painel novo na raiz e painel antigo sem números inventados
status: concluída
criada: 2026-10-14
---

# Painel novo na raiz

## Objetivo
`localhost:8080/` abre o painel novo; o antigo fica em `index-antigo.html` sem números inventados.

## Por quê
O painel antigo exibe valores calculados por fórmula a partir do código IBGE (PIB, área, IDEB, ranking...) com selo "ok", como se fossem oficiais. Decisão do Bruno (2026-10-14): trocar a raiz pelo painel novo e preservar o antigo só com a correção de não inventar números.

## Arquivos envolvidos
| Arquivo | O que muda |
|---|---|
| `index.html` | passa a ser o painel novo (conteúdo de `painel-municipio.dc.html`) |
| `painel-municipio.dc.html` | removido (renomeado para `index.html`) |
| `index-antigo.html` | criado (conteúdo do `index.html` antigo) |
| `src/ui/app.js` | editar: tirar valores de fórmula, ranking e variação falsos |
| `tests/ui/test_tela_*.py` | editar: apontar para os arquivos certos |

## Critérios de aceite
- [x] `GET /` serve o painel novo funcionando igual (3 abas, mapa, telas de 8 cartões, tema).
- [x] `index-antigo.html` abre o painel antigo e nenhum valor sai de fórmula: o que não é real aparece como "sem dado"; ranking e variação falsos não aparecem; a população (IBGE) e a receita do estado (SICONFI) continuam.
- [x] `pytest -q` passa com os testes de UI apontando para os arquivos certos.

## Fora de escopo
- Cor/seta por sentido (`card.js`) e exportação CSV do painel antigo.
- Novos indicadores no painel antigo.

## Plano
- [x] 1. Renomear `index.html` → `index-antigo.html` e `painel-municipio.dc.html` → `index.html`.
- [x] 2. `app.js`: substituir valores de fórmula/constantes por `sem_dado`, manter os reais.
- [x] 3. Ajustar testes de UI.
- [x] 4. Verificação.

## Segurança
N/A (páginas estáticas, sem entrada de usuário além de seletores).

## Verificação
```bash
.venv/bin/python -m pytest -q
node test_raiz.mjs   # Playwright: / e /index-antigo.html
```

## Decisões tomadas
- `app.js` antigo: em vez de apagar as definições de cartão, um helper `semDado()` marca como `sem_dado` tudo que não tem coleta real; `card.js` já exibe "Sem dado publicado" e esconde variação e ranking. Real mantido: população (IBGE 6579) e, no estado, soma da população e receita SICONFI DCA I-C exceto intraorçamentárias, líquida de deduções (14.879.502 R$ mil).
- Data de coleta da população passou a ser exibida no fuso local (antes cortava o ISO em UTC e mostrava o dia seguinte).
- Testes do painel antigo apontam para `index-antigo.html`; novo teste `test_raiz_serve_painel_novo`.
- A spec 29 citava o e-mail da conta de infraestrutura; removido (PRD 2.3: a conta nunca aparece em texto público).

## Evidência (2026-10-14)
`pytest -q`: 86 passed. `test_raiz.mjs` (Playwright): 8/8 PASSOU — raiz com painel novo (3 abas, 139 municípios, 8 cartões);
antigo/Pequizeiro sem 53.339.600, 334.560 nem "Posição:", população 5.038 real e 16 cartões "Sem dado publicado";
antigo/estado só 1.577.342 e 14.879.502; órgãos IBGE, TCE-TO e CGE-TO sem nenhum valor inventado; sem erros de página.
