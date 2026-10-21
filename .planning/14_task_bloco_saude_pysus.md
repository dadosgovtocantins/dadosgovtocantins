---
task: Bloco Saúde (PySUS — SIA, SIH, CNES, PNI, SIM/SINASC)
status: concluída
sprint: S5
eap: 1.2.5
---

# Bloco Saúde (PySUS / DATASUS)

## Objetivo
Implementar os coletores de dados de Saúde (`TO-SAU-01` Leitos CNES, `TO-SAU-02` Cobertura Vacinal PNI, `TO-SAU-03` Mortalidade Infantil SIM/SINASC), integrando dados do DATASUS via PySUS/FTP de forma otimizada para os **139 municípios do Tocantins**.

## Coletores a criar
| ID Fonte | Nome / Indicador | Origem | Cobertura |
|---|---|---|---|
| `TO-SAU-01` | Leitos SUS por Município | CNES / DATASUS | 139 municípios |
| `TO-SAU-02` | Cobertura Vacinal (Imunizações) | PNI / DATASUS | 139 municípios |
| `TO-SAU-03` | Taxa de Mortalidade Infantil | SIM / SINASC | 139 municípios |

## Arquivos envolvidos
| Arquivo | O que muda |
|---|---|
| `src/coletores/to_sau_01.py` | criar — Leitos CNES (≤ 50 linhas) |
| `src/coletores/to_sau_02.py` | criar — Cobertura Vacinal PNI (≤ 50 linhas) |
| `src/coletores/to_sau_03.py` | criar — Mortalidade Infantil SIM/SINASC (≤ 50 linhas) |
| `tests/fixtures/saude_payloads.py` | criar — Payloads offline simulados DATASUS |
| `tests/coletores/test_bloco_saude.py` | criar — Suíte de testes contratuais e transformações |
| `src/cli.py` | editar — Registrar os 3 novos coletores no catálogo (total 15 fontes) |
| `infra/schedulers.yaml` | editar — Adicionar agendamentos dos 3 coletores de saúde |

## Critérios de aceite
- [ ] Todos os 3 coletores herdam de `ColetorBase` e **não sobrescrevem `executar()`**
- [ ] Cada coletor tem **≤ 50 linhas de código**
- [ ] Cobertura de 139 municípios do Tocantins
- [ ] Fixtures offline em `tests/fixtures/saude_payloads.py` sem dependência de rede externa
- [ ] Suíte de testes `tests/coletores/test_bloco_saude.py` com 100% de aprovação
- [ ] Registro no CLI `python -m src.cli coletar --fonte TO-SAU-01` etc.
