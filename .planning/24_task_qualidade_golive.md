---
task: Qualidade e Go-Live (Gate 2 — auditoria 100% dos cards e publicação)
status: concluída
sprint: S9
eap: 1.6.1, 1.6.2, 1.6.3, 1.6.4, 1.6.5, 1.6.6, 1.6.7
---

# Qualidade e Go-Live (Gate 2)

## Objetivo
Realizar a auditoria de qualidade final de 100% dos cards de indicadores dos 139 municípios do Tocantins contra as publicações oficiais, validar os critérios de aceite do **Gate 2** e declarar a prontidão para publicação (Go-Live).

## Arquivos envolvidos
| Arquivo | O que muda |
|---|---|
| `docs/verificacao_golive.md` | criar — Matriz de auditoria de amostragem de dados e checklist do Gate 2 |
| `tests/qualidade/test_golive.py` | criar — Testes de validação de qualidade, integridade e ausência de regressão |

## Critérios de aceite
- [ ] 100% dos cards de indicadores exibem obrigatoriamente selos de esfera, data de coleta e fonte oficial com link
- [ ] Amostragem de conferência cruzada auditada em 5 municípios representativos (Palmas, Araguaína, Gurupi, Porto Nacional, Paraíso do Tocantins)
- [ ] Zero erros de console no navegador e 100% dos testes unitários/integrados passando
- [ ] Documento `docs/verificacao_golive.md` preenchido e aprovado no Gate 2
- [ ] Suíte de testes `tests/qualidade/test_golive.py` com 100% de aprovação
