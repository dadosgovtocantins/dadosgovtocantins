---
task: Bloco Recursos — Transferegov, SICONFI e CAPAG (18 fontes ativas)
status: concluída
sprint: S6
eap: 1.2.6
---

# Bloco Recursos (Transferegov, SICONFI e CAPAG)

## Objetivo
Implementar os 3 coletores do bloco de Recursos Financeiros (`TO-REC-01` Transferegov, `TO-REC-02` SICONFI DCA e `TO-REC-03` CAPAG Tesouro Nacional), elevando o total de fontes de coleta automática de 15 para **18 fontes ativas** (atingindo 100% da meta de go-live de ≥18 fontes).

## Coletores a criar
| ID Fonte | Nome / Indicador | Origem | Cobertura |
|---|---|---|---|
| `TO-REC-01` | Convenios Transferegov | Transferegov / MGI | 139 municípios |
| `TO-REC-02` | Receita Corrente Líquida (SICONFI DCA) | SICONFI / STN | 139 municípios |
| `TO-REC-03` | Capacidade de Pagamento (CAPAG) | Tesouro Nacional | 139 municípios |

## Arquivos envolvidos
| Arquivo | O que muda |
|---|---|
| `src/coletores/to_rec_01.py` | criar — Transferegov (≤ 50 linhas) |
| `src/coletores/to_rec_02.py` | criar — SICONFI DCA (≤ 50 linhas) |
| `src/coletores/to_rec_03.py` | criar — CAPAG Tesouro (≤ 50 linhas) |
| `tests/fixtures/recursos_payloads.py` | criar — Payloads offline simulados |
| `tests/coletores/test_bloco_recursos.py` | criar — Suíte de testes contratuais e transformações |
| `src/cli.py` | editar — Registrar os 3 novos coletores no catálogo (total 18 fontes) |
| `infra/schedulers.yaml` | editar — Adicionar agendamentos dos 3 coletores de recursos |

## Critérios de aceite
- [ ] Todos os 3 coletores herdam de `ColetorBase` e **não sobrescrevem `executar()`**
- [ ] Cada coletor tem **≤ 50 linhas de código**
- [ ] Cobertura dos 139 municípios do Tocantins
- [ ] Fixtures offline em `tests/fixtures/recursos_payloads.py` sem dependência de rede externa
- [ ] Suíte de testes `tests/coletores/test_bloco_recursos.py` com 100% de aprovação
- [ ] Total de fontes com coleta automática atinge **18 fontes ativas**
