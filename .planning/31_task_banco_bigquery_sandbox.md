---
task: Banco no BigQuery (Sandbox) com os dados reais
status: concluída (20/10/2026)
criada: 2026-10-19
---

# Banco no BigQuery (Sandbox)

## Objetivo
Criar os datasets e as tabelas do modelo no projeto atual, em modo Sandbox, e carregar no ambiente `dev` os dados reais das 9 fontes já coletadas.

## Por quê
O BigQuery da conta de infraestrutura está vazio (conferido em 19/10: 1 projeto, 0 datasets, 0 jobs). O carregador do pipeline só simula a gravação em memória e o `aplicar_ddl.sh` só imprime o SQL. Os dados reais existem só no `painel_dados.json`.

## Decisões do Bruno (19/10)
- Projeto: o atual, `project-6f15f3eb-e07f-48fc-ba7` (ID aleatório, mantido).
- Faturamento: BigQuery Sandbox, sem cartão.
- Escopo: banco + dados reais em `dev`.
- Região: `southamerica-east1` (São Paulo).

## Limites do Sandbox (página oficial, conferida em 19/10)
10 GiB de armazenamento por toda a vida do projeto (apagar não devolve); 1 TiB de consulta por mês; tabelas, views e partições expiram em 60 dias; sem DML (INSERT/UPDATE/MERGE), sem streaming, sem Data Transfer Service.

## Arquivos envolvidos
| Arquivo | O que muda |
|---|---|
| `infra/provision.sh` | criar: os 9 datasets, idempotente |
| `src/sql/aplicar_ddl.sh` | editar: executar de verdade (hoje só imprime) |
| `src/sql/ddl/*.sql` | sem mudança: o `aplicar_ddl.sh` executa só o `CREATE` de cada arquivo; os valores dos INSERT de `dim_municipio`/`dim_orgao` são lidos pela carga (fonte única; o teste da task 30 usa a lista do `dim_municipio.sql`) |
| `scripts/carregar_bigquery.py` | criar: coleta e carga por arquivo |
| `tests/test_carregar_bigquery.py` | criar |

## Critérios de aceite
- [x] 9 datasets (`dev|hml|ds` × `raw|stg|mart`) em `southamerica-east1`, com rótulos `projeto`, `ambiente`, `modulo`; `bq ls` lista os 9.
      — *`infra/provision.sh`: 1ª execução criou os 9, 2ª respondeu "já existe" nos 9; `bq ls` lista os 9 com `location: southamerica-east1`; `dev_mart` com rótulos `projeto: painel-to`, `ambiente: dev`, `modulo: mart`*
- [x] `fato_indicador`, `dim_municipio`, `dim_indicador`, `dim_orgao`, `dim_fonte`, `dim_tempo` e `dim_titular` criadas pelo mesmo script nos 3 ambientes; rodar 2x não dá erro.
      — *`aplicar_ddl.sh dev|hml|ds`: as 7 tabelas em cada `*_mart`; 2ª execução em `dev` sem erro; `dim_titular` de `hml` com rótulo `ambiente: hml`; `test_aplicar_ddl_sem_dml_sem_particao_e_com_teto` e `test_aplicar_ddl_recusa_ambiente_invalido`*
- [x] `dev` carregado: `dim_municipio` 139 (sem duplicata nem nulo); `dim_titular` 140; `fato_indicador` com as 8 fontes de indicadores, cada uma com a contagem da coleta; `dim_orgao` 14; `dim_fonte` com as 9 fontes implementadas e `dim_indicador` com os 8 indicadores (o titular é dimensão, não indicador).
      — *consulta de 20/10: `dim_municipio` 139/139 distintos/0 nulos; `dim_titular` 140; `dim_orgao` 14; `dim_fonte` 9; `dim_indicador` 8; `dim_tempo` 11; `fato_indicador` 3.064 linhas = TER-01 417, TER-02 695, TER-03 5, TER-04 139, TER-05 695, TER-06 695, TER-07 4, REC-02 414 (iguais à coleta), todas com `id_registro` distinto*
- [x] Consultas no BigQuery devolvem os mesmos valores do `painel_dados.json` (ex.: PIB de Palmas 2023 = 14.168.469 R$ mil; RCL do estado 2025 = 15.568.042,57 R$ mil).
      — *`pib_municipal` 1721000/2023 = 14168469; `receita_corrente_liquida` estado/2025 = 15568042.57326; Palmas/2025 = 2155602.77972*
- [x] Ausente nunca vira zero: Muricilândia continua sem RCL no banco (consulta prova).
      — *0 linhas de RCL para 1713957; 138 municípios com RCL; 0 valores iguais a zero*
- [x] Carga sem INSERT/MERGE (arquivo, substituindo o conteúdo); rodar 2x não duplica linhas.
      — *`load_table_from_json` com `WRITE_TRUNCATE` (`test_carga_substitui_o_conteudo_e_renova_a_expiracao`); `dim_municipio` foi carregada 3 vezes em 20/10 e tem 139 linhas*
- [x] Linhas com `periodo_ref` de 2019 continuam na tabela após a carga (expiração de partição do Sandbox tratada).
      — *mais antigo 2019-01-01, mais recente 2026-04-01, 140 linhas anteriores a 2020; `fato_indicador` sem `timePartitioning` (ver Decisões)*
- [x] Expiração de 60 dias: a carga renova a validade das tabelas e informa a data; registrado que é preciso rodar ao menos a cada 60 dias.
      — *as 7 tabelas de `dev` expiram em 18/12/2026; o script imprime "Expiração renovada para … rode de novo antes disso"; ver Decisões ("renovar em vez de recriar")*
- [x] Toda consulta do script com `maximum_bytes_billed`; nenhuma credencial em arquivo; o e-mail da conta de infraestrutura não aparece no repositório.
      — *o carregador só faz load jobs (nenhuma consulta); o `aplicar_ddl.sh` passa `--maximum_bytes_billed=100000000` em cada DDL (teste com `bq` falso); credencial = token do `gcloud` em memória (`cliente_gcloud`); `grep dadosgov` nos arquivos da task: 0*
- [x] `pytest` e `ruff` passam; testes do carregador sem acesso à nuvem (cliente simulado).
      — *suíte completa 177 passaram, 0 falharam (6 novos do carregador + bq falso); `ruff check` e `ruff format --check` limpos nos arquivos da task. O cliente simulado reproduz as regras que derrubaram cargas reais: etag (412), NUMERIC com mais de 9 casas e campo obrigatório nulo*

## Fora de escopo
- O painel ler do BigQuery (continua lendo `painel_dados.json`).
- Buckets, Cloud Run, Scheduler, orçamento (exigem faturamento).
- Contas de serviço, Secret Manager, 2FA, runbook completo (restante da task 02).
- Carga em `hml`/`ds` (só estrutura), views `vw_*`, snapshot diário.
- `dim_fonte`/`dim_indicador` a partir da planilha (IDs divergentes do código); alinhar IDs é outra task.
- Tratar o "429" do SICONFI no coletor (ver Pendências).

## Plano
- [x] 1. Sondagem: partição com data antiga sobrevive no Sandbox? (dataset temporário, apagado ao fim)
- [x] 2. `infra/provision.sh` com os 9 datasets; rodar 2x.
- [x] 3. DDLs executados só no `CREATE` (sem DML, `fato_indicador` sem partição); `aplicar_ddl.sh` executando nos 3 ambientes; rodar 2x.
- [x] 4. `scripts/carregar_bigquery.py` + testes sem nuvem.
- [x] 5. Carga real em `dev` e consultas de conferência.
- [x] 6. Suíte, ruff e gate de segurança.

## Segurança
| Item | Status | Evidência | Correção |
|---|---|---|---|
| S1 segredos | ✅ | nenhuma chave em arquivo: o carregador pede `gcloud auth print-access-token` e usa o token só em memória (`carregar_bigquery.py`, `cliente_gcloud`); o ID do projeto não é segredo | — |
| S2 validação | ✅ | antes da carga, cada fonte passa pelo `validar()` do coletor (cobertura, campos obrigatórios; titulares pela `validar_titulares`); o schema da tabela filtra colunas e o BigQuery recusa tipo inválido | — |
| S3 SQL | ✅ | só DDL versionado (`src/sql/ddl`); dados entram por load job do cliente oficial, sem SQL montado com valores | — |
| S12 menor privilégio | ⚠️ | carga feita pela conta dona do projeto (`roles/owner`) | contas de serviço por ambiente, sem chave JSON — task 02 |
| S14 dependências | N/A | nenhuma dependência nova (`google-cloud-bigquery` já estava no lock) | — |
| S15 erros | ✅ | fonte com erro → a tabela dela não é carregada (fica a carga anterior) e o script devolve 1 (`test_fonte_com_erro_nao_carrega_a_tabela_dela`); aconteceu de verdade com o "429" do SICONFI: `fato_indicador` não foi gravada pela metade | — |
| S20/S21 | N/A | sem pacote novo; sem API key | — |
| Demais (S4–S11, S13, S16–S19, S22–S23) | N/A | sem login, endpoint, upload, servidor ou dado pessoal novo | — |

## Verificação
```bash
bash infra/provision.sh && bash infra/provision.sh      # 9 criados; depois 9 "já existe"
bash src/sql/aplicar_ddl.sh dev                          # (e hml, ds) 7 tabelas por ambiente
.venv/bin/python scripts/carregar_bigquery.py --ambiente dev
bq query --nouse_legacy_sql --maximum_bytes_billed=100000000 '<conferências acima>'
.venv/bin/python -m pytest -q                            # 177 passaram, 0 falharam (20/10)
```

## Decisões tomadas
- **Sem partição no Sandbox (sondagem de 19/10):** tabela particionada por data recebeu linhas de 2019, 2025 e 2026 e guardou só a de 2026 (`numRows: 1`): a expiração de 60 dias conta a partir da data de cada partição. Tentar desligar devolve "Partition expiration time must be less than 60 days while in sandbox mode". Tabela sem partição guardou as 3 linhas. Decisão: no Sandbox a `fato_indicador` é criada **sem `PARTITION BY`**, mantendo `CLUSTER BY id_indicador, id_municipio`; o volume (≈3 mil linhas) não precisa de partição. Ao ativar faturamento, voltar ao Anexo C. Dataset temporário apagado.
- **Limite mínimo por consulta:** o BigQuery cobra no mínimo ~10 MB por tabela lida; `maximum_bytes_billed` de 10 MB foi recusado ("20971520 or higher required"). Usar 100 MB nas consultas do projeto.
- **DDLs intactos (19/10):** em vez de tirar os INSERT de `dim_municipio.sql`/`dim_orgao.sql`, o `aplicar_ddl.sh` corta cada arquivo no primeiro `INSERT` e a carga lê os `STRUCT(...)` do próprio arquivo. Motivo: `test_bloco_governanca.py` usa a lista do `dim_municipio.sql` como fonte canônica dos 139 códigos.
- **Renovar em vez de recriar:** a spec dizia "a carga recria as tabelas"; a carga **renova a data de expiração** (59 dias) depois de cada `WRITE_TRUNCATE`, o que tem o mesmo efeito sem apagar a tabela. O `aplicar_ddl.sh` só cria o que não existe.
- **Credencial pelo `gcloud`:** a credencial padrão do Python (ADC) desta máquina é da conta pessoal; o carregador usa o token da conta ativa do `gcloud` (a de infraestrutura), sem novo login e sem arquivo.
- **`dim_indicador` com 8, não 9:** o `TO-GER-01` (titulares) é dimensão (`dim_titular`), não indicador; `dim_fonte` tem as 9 fontes.
- **Correções descobertas nas cargas reais (20/10), cada uma com teste que reproduz o erro:** (1) `412 Precondition Failed` ao renovar a expiração com o etag de antes da carga → o carregador relê a tabela depois da carga; (2) `Invalid NUMERIC value: 41355.172170000005` (R$ ÷ 1000 em ponto flutuante) → campos NUMERIC arredondados a 9 casas; o cliente simulado passou a recusar NUMERIC com mais de 9 casas e campo obrigatório nulo, como o BigQuery.
- **Carga final feita em execução pontual com cache:** para não repetir 15 min de coleta a cada falha, as coletas foram guardadas num arquivo temporário (fora do repositório), pré-validadas com as mesmas regras do BigQuery e carregadas com `carregar_bigquery.carregar()`. Na recoleta do `TO-REC-02` dessa execução pontual, o SICONFI usou 1 s entre consultas (o coletor usa 0,5 s), por causa do "429" (ver Pendências).

## Pendências (fora desta task)
- **SICONFI "429 – muitas requisições":** na 3ª coleta completa do dia, a API do Tesouro bloqueou por volta da 320ª consulta, sem `Retry-After`. Proposta para aprovar: tratar 429 no `ClienteHTTP` (esperar e tentar de novo) e usar 1 s entre consultas no SICONFI.
- Rodar a carga ao menos a cada 60 dias (próximo limite: 18/12/2026) até haver agendamento automático.
