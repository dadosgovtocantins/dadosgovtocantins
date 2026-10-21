---
task: Camada semântica e ranking municipal (views em ds_mart)
status: concluída
sprint: S4
eap: 1.3.3, 1.3.4
---

# Camada semântica e ranking municipal

## Objetivo
Materializar em `ds_mart` as views otimizadas para consumo do frontend/Looker: `vw_tela_municipio`, `vw_tela_estado` e `vw_ranking_municipios` com ranking municipal 1º–139º e variação vs. período anterior, garantindo consumo de **< 1 GB** por consulta (`maximum_bytes_billed`).

## Arquivos envolvidos
| Arquivo | O que muda |
|---|---|
| `src/sql/mart/vw_tela_municipio.sql` | criar — View de agregados por município |
| `src/sql/mart/vw_tela_estado.sql` | criar — View de agregados estaduais |
| `src/sql/mart/vw_ranking_municipios.sql` | criar — View com DENSE_RANK() 1º–139º e variação |
| `tests/sql/test_camada_semantica.py` | criar — Testes SQL de integridade das views e custo |

## Critérios de aceite
- [ ] `vw_tela_municipio` consolida os indicadores dos 139 municípios do Tocantins
- [ ] `vw_ranking_municipios` atribui posição `1º` a `139º` utilizando `DENSE_RANK() OVER (PARTITION BY id_indicador, periodo_ref ORDER BY valor_num DESC)`
- [ ] Variação em relação ao período anterior calculada via `LAG()`
- [ ] Consultas executadas sob limite rígido de **< 1 GB** (`maximum_bytes_billed = 1000000000`)
- [ ] Suíte de testes `tests/sql/test_camada_semantica.py` validando integridade lógica e ausência de duplicação
