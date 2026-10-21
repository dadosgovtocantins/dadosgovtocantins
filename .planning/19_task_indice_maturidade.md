---
task: Índice de maturidade de dados abertos (cálculo A/B vs D por órgão)
status: concluída
sprint: S7
eap: 1.3.6
---

# Índice de Maturidade de Dados Abertos

## Objetivo
Implementar o algoritmo e a visualização do **Índice de Maturidade de Dados Abertos** para os 11 órgãos catalogados do Estado do Tocantins, calculando a proporção de fontes estruturadas reutilizáveis (Grau A/B — JSON/CSV/API) versus fontes apenas-link/documento (Grau D — PDF/HTML), conforme exigido no RF-43 e RF-44.

## Arquivos envolvidos
| Arquivo | O que muda |
|---|---|
| `src/catalogo/maturidade.py` | criar — Módulo de cálculo da pontuação e classificação dos 11 órgãos |
| `src/sql/mart/vw_indice_maturidade.sql` | criar — View de agregação de maturidade por órgão |
| `tests/catalogo/test_maturidade.py` | criar — Testes unitários do cálculo de maturidade |

## Critérios de aceite
- [ ] Cálculo da taxa de reuso por órgão: `(fontes_reutilizaveis_A_B / total_fontes) * 100`
- [ ] Classificação em 4 níveis: `Inexistente` (0%), `Inicial` (1-49%), `Intermediário` (50-79%), `Avançado` (80-100%)
- [ ] Cobertura dos 11 órgãos catalogados (SEFAZ, SES, SEDUC, SSP, etc.)
- [ ] Respeito à decisão do Gate 1 (Task 09): portais sem API pública recebem avaliação D por ausência de dados abertos estruturados
- [ ] Suíte de testes `tests/catalogo/test_maturidade.py` com 100% de aprovação
