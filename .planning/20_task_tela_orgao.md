---
task: Tela Órgão (Demo 4 — 3 blocos: indicadores, catálogo e transparência de dados abertos)
status: concluída
sprint: S7
eap: 1.4.4
---

# Tela Órgão (Demo 4)

## Objetivo
Entregar a interface da **Tela Órgão (Demo 4)**, estruturada em 3 blocos funcionais: (1) Indicadores fornecidos pelo órgão selecionado, (2) Catálogo de fontes do órgão com metadados e classe de reuso, e (3) Diagnóstico de Transparência e Índice de Maturidade de Dados Abertos (Task 19).

## Arquivos envolvidos
| Arquivo | O que muda |
|---|---|
| `index.html` | editar — Adicionar a 3ª aba de navegação (Visão por Órgão) |
| `src/ui/css/app.css` | editar — Estilos para seletores de órgão, tabelas de transparência e badges de maturidade |
| `src/ui/app.js` | editar — Lógica da Tela Órgão, filtros por órgão e renderização dos 3 blocos |
| `tests/ui/test_tela_orgao.py` | criar — Testes de integridade da Tela Órgão e seus 3 blocos |

## Critérios de aceite
- [ ] Aba `Visão por Órgão` adicionada ao menu de navegação principal do painel
- [ ] Seletor com os 11 órgãos catalogados
- [ ] Bloco 1: Renderização dos cards de indicadores fornecidos pelo órgão selecionado
- [ ] Bloco 2: Catálogo de fontes do órgão com link oficial, periodicidade e classe de reuso
- [ ] Bloco 3: Painel de Transparência exibindo a pontuação e o Nível de Maturidade (Avançado/Intermediário/Inicial/Inexistente)
- [ ] Suíte de testes `tests/ui/test_tela_orgao.py` com 100% de aprovação
