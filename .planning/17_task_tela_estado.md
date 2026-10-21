---
task: Tela Estado (Demo 3 — visão agregada dos indicadores do Estado do Tocantins)
status: concluída
sprint: S6
eap: 1.4.3
---

# Tela Estado (Demo 3)

## Objetivo
Entregar a interface navegável da **Tela Estado (Demo 3)**, exibindo a visão agregada dos indicadores estaduais do Tocantins (PIB Estadual, População Total, Taxa de Desocupação PNADC, Variações históricas estaduais), com suporte à alternância entre visão Municipal e visão Estadual.

## Arquivos envolvidos
| Arquivo | O que muda |
|---|---|
| `index.html` | editar — Adicionar navegação por abas (Visão Municípios / Visão Estado) |
| `src/ui/css/app.css` | editar — Estilos para navegação por abas e estatísticas estaduais |
| `src/ui/app.js` | editar — Lógica de alternância de tela e renderização de indicadores estaduais |
| `tests/ui/test_tela_estado.py` | criar — Testes da visão de Estado e navegação por abas |

## Critérios de aceite
- [ ] Navegação por abas ou alternador entre `Visão por Município` e `Visão Estadual (Tocantins)`
- [ ] Renderização dos indicadores estaduais (PIB Estadual TO, População TO, Taxa de Desocupação PNADC TO)
- [ ] Preservação de todos os selos de auditoria (fonte, data, esfera, aviso de não-oficialidade)
- [ ] Suíte de testes `tests/ui/test_tela_estado.py` validando os componentes e a navegação da Tela Estado
