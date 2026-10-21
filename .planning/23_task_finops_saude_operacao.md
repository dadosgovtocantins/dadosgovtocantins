---
task: FinOps e saúde da operação (monitoramento de custos $0 e alertas de defasagem)
status: concluída
sprint: S8
eap: 1.5.1, 1.5.2, 1.5.3, 1.5.4
---

# FinOps e Saúde da Operação

## Objetivo
Implementar o módulo de monitoramento de saúde da operação e controle de FinOps, garantindo **Custo R$ 0,00 (100% no nível gratuito do Google Cloud)**, monitorando o consumo de cotas de BigQuery e Cloud Run, e gerando alertas automáticos de defasagem de dados (RF-85, RF-90..95).

## Arquivos envolvidos
| Arquivo | O que muda |
|---|---|
| `src/operacao/finops.py` | criar — Módulo de auditoria de franquia gratuita e alertas de custo |
| `tests/operacao/test_finops.py` | criar — Testes unitários do validador de FinOps |

## Critérios de aceite
- [ ] Validador de FinOps garante que consumo de BigQuery seja **< 1 TB/mês** (limite gratuito)
- [ ] Teto rígido `maximum_bytes_billed` presente em 100% das consultas executadas
- [ ] Monitor de saúde registra status das 18 fontes ativas e identifica defasagem
- [ ] Zero serviços pagos habilitados (trava de segurança FinOps)
- [ ] Suíte de testes `tests/operacao/test_finops.py` com 100% de aprovação
