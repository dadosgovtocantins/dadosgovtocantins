---
task: Modelo de dados — star schema no BigQuery
status: concluída
sprint: S3
eap: 1.3.1, 1.3.2
---

# Modelo de dados (star schema)

## Objetivo
Criar `fato_indicador` e as cinco dimensões no BigQuery, particionadas e
clusterizadas, com o enum de qualidade que distingue `sem_dado`, `falho` e zero.

## Por quê
Duas coisas ficam impossíveis de corrigir depois: **a chave canônica de município**
(código IBGE de 7 dígitos — RT-07) e **a distinção entre ausência de dado e dado
zero** (RF-55, RT-11). A segunda é uma das quatro inovações declaradas do projeto:
fontes declaratórias omitem quem não respondeu, e exibir isso como zero penaliza
reputacionalmente um município que apenas não enviou o dado. Se o modelo não
carregar essa diferença desde a origem, ela não chega à tela.

## Arquivos envolvidos
| Arquivo | O que muda |
|---|---|
| `src/sql/ddl/fato_indicador.sql` | criar — Anexo C, literal |
| `src/sql/ddl/dim_*.sql` | criar — indicador, orgao, municipio, fonte, tempo |
| `src/sql/stg/normaliza_municipio.sql` | criar — encoding e código IBGE |
| `src/sql/ddl/snapshot.sql` | criar — snapshot diário de `ds_mart` |
| `tests/sql/test_modelo.py` | criar |
| `docs/dicionario.md` | editar — tabelas e campos |

## Critérios de aceite
- [ ] `fato_indicador` criada exatamente como o Anexo C, com
      `PARTITION BY periodo_ref` e `CLUSTER BY id_indicador, id_municipio`
- [ ] `dim_municipio` com **139 linhas**, chave = código IBGE de 7 dígitos,
      sem duplicata e sem nulo (query de conferência colada)
- [ ] `dim_indicador`, `dim_orgao`, `dim_fonte`, `dim_tempo` criadas e populadas
      a partir do catálogo (task 04), não digitadas à mão
- [ ] `qualidade` aceita apenas `ok|estimado|defasado|suspeito|sem_dado|falho`
      — carga com valor fora do enum é rejeitada (teste prova)
- [ ] **Teste das três linhas:** um município com `valor_num = 0` + um com
      `qualidade='sem_dado'` + um com `qualidade='falho'` são distinguíveis em
      uma única consulta, e os três renderizam diferente na camada de consumo
- [ ] `esfera_fonte` preenchida em 100% das linhas (federal/estadual — RF-12)
- [ ] Consulta que alimenta uma tela completa processa **< 1 GB** —
      `bq query --dry_run` colado como evidência (RNF-P03)
- [ ] `maximum_bytes_billed` presente em toda query do `src/` — `grep` prova
- [ ] Snapshot diário de `ds_mart` agendado, retenção 30 dias, em dataset
      separado com escrita bloqueada (PRD §12.5)
- [ ] DDL roda nos 3 ambientes a partir do mesmo script, sem edição manual

## Fora de escopo
- Views e agregados de consumo, ranking e variação (task 11)
- Indicadores calculados (task 16)
- Índice de maturidade (task 19)

## Plano
- [ ] 1. DDL da `fato_indicador` conforme Anexo C
- [ ] 2. DDL das 5 dimensões
- [ ] 3. Popular `dim_municipio` com a malha IBGE (139) e conferir a contagem
- [ ] 4. Popular as demais dimensões a partir do catálogo
- [ ] 5. Enum de qualidade + teste das três linhas
- [ ] 6. `dry_run` de custo e ajuste de partição/cluster se passar de 1 GB
- [ ] 7. Snapshot diário + dataset de backup com escrita bloqueada
- [ ] 8. Atualizar `docs/dicionario.md`

## Segurança
Gate S1–S21: **S3 SQL** (DDL versionado, carga por cliente oficial e parâmetros),
**S12 menor privilégio** (escrita em PROD só pelas SAs do pipeline; dataset de
snapshot com escrita bloqueada), **S2 validação** (enum e NOT NULL no schema, não
só na aplicação), **LGPD/RNF-S01** (somente agregados — nenhuma coluna do modelo
permite identificar pessoa, isolada ou combinada).

## Verificação
```bash
bash src/sql/aplicar_ddl.sh dev
bq query --use_legacy_sql=false --maximum_bytes_billed=1000000000 \
  'SELECT COUNT(*) n, COUNT(DISTINCT id_municipio) m FROM `<proj>.dev_mart.dim_municipio`'   # n=139, m=139
bq query --dry_run --use_legacy_sql=false < src/sql/mart/tela_municipio.sql   # < 1 GB
pytest tests/sql -q
grep -rLn "maximum_bytes_billed" src/**/*.py | grep -v tests || echo "OK"
```

## Decisões tomadas
<preenchido durante a execução>
