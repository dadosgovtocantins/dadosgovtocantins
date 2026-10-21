---
task: Bloco Educação e Trabalho — 5 novos coletores (12 fontes ativas)
status: concluída
sprint: S4
eap: 1.2.3, 1.2.4
---

# Bloco Educação e Trabalho/Economia

## Objetivo
Implementar 5 coletores de dados das áreas de Educação (`TO-EDU-01`, `TO-EDU-02`), Trabalho (`TO-TRAB-01`) e Economia (`TO-ECO-01`, `TO-ECO-02`), expandindo o total de fontes ativas de 7 para 12 fontes automáticas.

## Coletores a criar
| ID Fonte | Nome / Indicador | Origem | Cobertura |
|---|---|---|---|
| `TO-EDU-01` | IDEB e Matrículas Escolares | INEP | 139 municípios |
| `TO-EDU-02` | Repasses FNDE (PNAE/PNATE/FUNDEB) | FNDE | 139 municípios |
| `TO-TRAB-01` | Saldo de Emprego Formal (CAGED) | MTE / Novo CAGED | 139 municípios |
| `TO-ECO-01` | Balança Comercial (Comex Stat) | MDIC / Comex Stat | 139 municípios |
| `TO-ECO-02` | Empresas Ativas | Mapa de Empresas (ME) | 139 municípios |

## Arquivos envolvidos
| Arquivo | O que muda |
|---|---|
| `src/coletores/to_edu_01.py` | criar — IDEB / Censo Escolar (≤ 50 linhas) |
| `src/coletores/to_edu_02.py` | criar — Repasses FNDE (≤ 50 linhas) |
| `src/coletores/to_trab_01.py` | criar — Novo CAGED (≤ 50 linhas) |
| `src/coletores/to_eco_01.py` | criar — Comex Stat (≤ 50 linhas) |
| `src/coletores/to_eco_02.py` | criar — Mapa de Empresas (≤ 50 linhas) |
| `tests/fixtures/educacao_trabalho_payloads.py` | criar — Payloads offline simulados |
| `tests/coletores/test_bloco_educacao_trabalho.py` | criar — Suíte de testes contratuais e transformações |
| `src/cli.py` | editar — Registrar os 5 novos coletores no catálogo |
| `infra/schedulers.yaml` | editar — Adicionar agendamentos dos 5 coletores |

## Critérios de aceite
- [ ] Todos os 5 coletores herdam de `ColetorBase` e **não sobrescrevem `executar()`**
- [ ] Cada coletor tem **≤ 50 linhas de código**
- [ ] Cobertura de 139 municípios do Tocantins nos indicadores municipais
- [ ] Fixtures offline em `tests/fixtures/educacao_trabalho_payloads.py` sem dependência de rede externa
- [ ] Execução idempotente (segunda execução com mesmo payload retorna `sem_mudanca`)
- [ ] Suíte de testes `tests/coletores/test_bloco_educacao_trabalho.py` com 100% de aprovação
- [ ] Suporte no CLI `python -m src.cli coletar --fonte TO-EDU-01` etc.
- [ ] Total de fontes com coleta automática atinge 12 (superando a meta do sprint de ≥10)
