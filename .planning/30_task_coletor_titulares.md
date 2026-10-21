---
task: Coletor de titulares eleitos (prefeitos, prefeitas e governador/governadora do TO)
status: implementada e verificada em dev (14/10/2026) — todos os critérios atendidos (suíte completa verde desde o fechamento da task 28); aguardando Bruno: catálogo (TO-GER-02), texto legal e aprovação do commit
criada: 2026-10-14
---

# Coletor de Titulares Eleitos (TSE + DivulgaCandContas)

## Objetivo
Coletar nome, município/cargo e retrato de identificação do titular eleito em
exercício de cada um dos 139 municípios do TO e do governo estadual, a partir
de fontes públicas do TSE, e carregar em uma dimensão própria no BigQuery.

## Por quê
O painel não tem hoje nenhuma fonte de "quem está no cargo" — só indicadores
territoriais. Para a ficha de município e a ficha de órgão (tasks 13/20)
mostrarem o titular atual com fonte oficial, falta essa dimensão de dados.
Decisão de escopo já tratada no gate desta task: abre uma exceção estreita a
RF-11/RNF-S08 só para o retrato do titular eleito (ver `docs/PRD_Painel_Dados_Tocantins.md`
seção 0.1 e `docs/identidade.md`, ambos atualizados em 2026-10-14).

## Arquivos envolvidos
| Arquivo | O que muda |
|---|---|
| `src/coletores/to_ger_01.py` | criar — coletor TSE Dados Abertos (nome, município, cargo, situação de eleito) |
| `src/coletores/tse_candidatos.py` | criar (2026-10-14) — leitura comum do CSV de candidatos do TSE (download, minimização de colunas, filtro de titular eleito, montagem do registro), no padrão de `sidra.py`; mantém `to_ger_01.py` ≤55 linhas **e** formatado pelo `ruff format`, que o CI exige |
| `tests/qualidade/test_golive.py` | editar (2026-10-14) — contagem de coletores registrados 18 → 20 (18 do go-live + `TO-GER-01`/`TO-GER-02`); arquivo da task 24, fora da lista original |
| `src/coletores/to_ger_02.py` | criar — **bloqueado por RF-71** (robots.txt do DivulgaCandContas devolve 403): levanta `ColetaBloqueadaError`, não abre conexão, não grava nada; a fonte entra como link (ver "Decisões tomadas") |
| `src/sql/ddl/dim_titular.sql` | criar — nova dimensão, fora de `fato_indicador` (não é série numérica) |
| `src/coletor_base/http.py` | sem mudança — `to_ger_01` reaproveita o `ClienteHTTP` existente |
| `src/coletor_base/base.py`, `carga.py`, `validacao.py` | editar (registrado a posteriori, 2026-10-14) — `tabela_destino`/`chave_merge` por coletor e hook `validar()` para que dimensões (`dim_titular`) usem o `ColetorBase` sem sobrescrever `executar()`; `validar_titulares` (S2). Arquivos fora da lista original |
| `src/cli.py` | editar — registrar `TO-GER-01` e `TO-GER-02` em `REGISTRO_COLETORES` (sem isso `coletar --fonte` devolve `fonte_nao_cadastrada`); arquivo fora da lista original, incluído em 2026-10-14 |
| `tests/coletores/test_bloco_governanca.py` | criar — testes de `to_ger_01`/`to_ger_02`, seguindo o padrão `test_bloco_*.py` já usado pelos demais blocos |
| `tests/fixtures/governanca_payloads.py` | criar — payload real (CSV TSE recortado) + resposta 403 do `robots.txt` do DivulgaCandContas como evidência do bloqueio, seguindo o padrão `*_payloads.py` |
| `catalogo` (Sheets, fora do repo) | editar — 2 linhas novas em `catalogo_indicadores`, `status = homologacao`, antes de codar (convenção do projeto). `TO-GER-02` deve ter `RESTRIÇÃO ROBOTS/TERMOS` começando com `Sim` (espelha o bloqueio do código) — **pendente do Bruno** |

## Critérios de aceite
- [x] `to_ger_01` lê o CSV de candidatos do TSE (Dados Abertos), filtra `UF=TO`
      e `DS_CARGO IN ('PREFEITO','GOVERNADOR')` e `DS_SIT_TOT_TURNO` indicando
      eleito, e produz 1 registro por titular com `id_municipio` (código IBGE
      7 dígitos; `NULL` para o governador, nível estadual) e `nome_titular`
      — *coleta real 14/10: bruto com 139 `PREFEITO` (2024) + 1 `GOVERNADOR`
      (2022), todos `ELEITO`; `test_to_ger_01_id_municipio_ibge_7_digitos_e_governador_null`*
- [x] `to_ger_01` cobre as 139 prefeituras do TO + o governo estadual = 140
      registros em execução íntegra (teste com fixture confirma a contagem)
      — *CLI real: `linhas_processadas=140`, `municipios_cobertos=139`;
      `test_to_ger_01_140_titulares`*
- [x] `to_ger_02` NÃO consulta o DivulgaCandContas: o `robots.txt` devolve 403
      (WAF) e a fonte entra como link (RF-71). `executar()` levanta
      `ColetaBloqueadaError` antes de abrir qualquer conexão e não grava nada;
      `url_foto` permanece `NULL` nos 140 registros. *(Critério original —
      gravar a URL do retrato — substituído em 2026-10-14 por decisão do
      Bruno, opção 1; ver "Decisões tomadas")*
      — *CLI: `coletar --fonte TO-GER-02` → `ColetaBloqueadaError` em
      `base.py:72` (guarda, antes de qualquer conexão); `url_foto` não nulo
      em 0 dos 140 registros; `test_to_ger_02_bloqueado_antes_de_qualquer_requisicao`*
- [x] Falha de rede em `to_ger_01` preserva o último valor válido com
      `qualidade='defasado'`, nunca grava nulo/zero por falha (RF-66, mesmo
      contrato do `ColetorBase`); o bloqueio de `to_ger_02` nunca apaga nem
      zera os titulares já carregados
      — *`test_to_ger_01_falha_de_rede_preserva_ultimo_valido_defasado`,
      `test_to_ger_02_bloqueio_preserva_titulares_do_to_ger_01`*
- [x] Conformidade checada pela guarda existente (`checar_conformidade_coleta`)
      antes de qualquer requisição em `to_ger_01`; `robots.txt` de
      `cdn.tse.jus.br` (404, sem regras) e `dadosabertos.tse.jus.br`
      (Crawl-Delay 10, respeitado) conferidos em 2026-10-14
      — *`test_to_ger_01_conformidade_antes_de_qualquer_requisicao`; `curl`
      dos dois `robots.txt` em 14/10 (404 e 200 com `Crawl-Delay: 10`)*
- [x] DDL de `dim_titular` escrito com `id_titular`, `id_municipio` (NULL
      para estadual), `cargo` (`PREFEITO`|`GOVERNADOR`), `nome_titular`,
      `url_foto`, `fonte`, `hash_origem`, `atualizado_em` (mais `ano_eleicao`,
      `sq_candidato`, `id_fonte`, `qualidade`). A aplicação no BigQuery real
      fica fora desta task: o carregador do projeto ainda é local (mesma
      linha da task 28)
      — *`src/sql/ddl/dim_titular.sql` (12 colunas). Não está ligado em
      `src/sql/aplicar_ddl.sh` (hoje só imprime os DDLs) — ligar junto com a
      aplicação real no BigQuery*
- [x] Nenhum campo de brasão, marca ou paleta institucional é gravado ou
      referenciado — só nome, cargo, município e retrato do titular
      — *`test_to_ger_01_sem_brasao_marca_paleta_nem_dado_pessoal`*
- [x] Teste de cada coletor roda com fixture gravada em
      `tests/fixtures/governanca_payloads.py`, sem bater na rede
      — *`test_to_ger_01_extrair_minimiza_colunas_sem_rede` (rede
      monkeypatched), `test_to_ger_02_bloqueado_*` (rede proibida)*
- [x] `ruff check` e `pytest -q` passam
      — *Reconferido em 14/10, depois do fechamento da task 28: suíte
      completa com 164 testes, 0 falhas; os 15 da task (13 governança +
      2 go-live) passam. A falha antiga de `test_coletor_referencia_to_ter_01`
      (417 ≠ 139) foi resolvida na task 28 (o teste passou a usar respostas
      reais gravadas, sem rede). `ruff check` limpo nos 10 arquivos `.py`
      da task. `ruff format --check` (que o CI também roda) apontava
      `src/coletor_base/base.py:59`, linha alterada por esta task; corrigido
      em 14/10 (a chamada `carregar_merge` quebrada em 3 linhas, só
      formatação), e os 10 arquivos passam no format*

## Fora de escopo
- Exibição do titular/retrato nas telas de município (task 13) ou órgão
  (task 20) — essa task só coleta e carrega o dado; UI é task separada.
- Histórico de titulares anteriores/mandatos passados — só o titular em
  exercício atual.
- Vice-prefeito, vice-governador, secretariado ou qualquer outro agente
  público além do titular eleito do cargo (continua proibido por RF-11).
- Atualização automática por troca de titular fora do ciclo eleitoral (ex.:
  renúncia, cassação, reeleição indireta) — fica para decisão futura se for
  necessário; nesta task o dado reflete o resultado eleitoral mais recente.
- Coleta do retrato do titular enquanto o DivulgaCandContas negar acesso
  automatizado (WAF). Reabrir só com autorização do TSE ou fonte alternativa
  com robots/termos confirmáveis — decisão do Bruno, em outra task.
- Contornar o WAF (troca de User-Agent, proxy, headless) — proibido.

## Plano
- [x] 1. Cadastrar `TO-GER-01` e `TO-GER-02` no catálogo (Sheets) com
         `status = homologacao` — confirmado pelo Bruno em 2026-10-14 (cadastro
         manual no Sheets do catálogo; não verificado pelo agente)
- [x] 2. Criar `src/sql/ddl/dim_titular.sql`
- [x] 3. Implementar `to_ger_01.py` (TSE Dados Abertos CSV → filtro TO →
         prefeito/governador eleito), herdando `ColetorBase`
- [x] 4. Gravar fixture real do CSV recortado em
         `tests/fixtures/governanca_payloads.py` e escrever os testes de
         `to_ger_01` em `tests/coletores/test_bloco_governanca.py`
- [x] 5. `to_ger_02.py` implementado como coletor **bloqueado** por RF-71
         (levanta `ColetaBloqueadaError`, sem requisição) — substitui o
         coletor REST do plano original (opção 1, Bruno, 2026-10-14)
- [x] 6. Fixture `RESPOSTA_DIVULGACANDCONTAS_ROBOTS_403` (evidência real do
         bloqueio) na `governanca_payloads.py` + testes do bloqueio
- [x] 7. Registrar `TO-GER-01`/`TO-GER-02` em `src/cli.py`; rodar `TO-GER-01`
         em `dev` com rede real e confirmar 140 linhas / 139 municípios;
         rodar `TO-GER-02` e confirmar o bloqueio — feito 14/10 (duas coletas
         reais, mesmo `hash_origem` `18e19ef5…`; ver Resultado do gate abaixo)
- [x] 8. Rodar gate de segurança S1–S23 e preencher a tabela — sem ❌;
         4 ⚠️ (S12, S14, S19, S23), todos fora do código desta task

## Segurança
Itens da `/secure-by-default-webdev` que se aplicam:
- **S1 segredos** — nenhuma das duas APIs exige chave; confirmar que nada é
  passado via querystring que pareça credencial.
- **S2 validação de entrada** — validar `UF`, `DS_CARGO` e `id_municipio`
  contra `dim_municipio` antes de carregar; rejeitar município fora dos 139.
- **S3 SQL** — `MERGE` parametrizado, igual aos demais coletores; nunca
  concatenar string na query de carga.
- **S11 headers/CORS/HTTPS** — ambas as origens são HTTPS; sem CORS aplicável
  (chamada server-to-server).
- **S12 menor privilégio** — Service Account do Cloud Run Job só com escrita
  em `dim_titular`, mesmo princípio dos demais coletores.
- **S14 dependências/CI** — nenhuma lib nova além do que `coletor_base/http.py`
  já usa; se precisar de lib de parsing CSV adicional, justificar aqui.
- **S15 tratamento de erro** — exceção específica (`FonteIndisponivelError`),
  nunca `except Exception: pass`.
- **S21 API keys** — N/A, sem chave de API nestas duas fontes.
- **S4–S10, S13, S16–S18, S20** — N/A, mesmo motivo estrutural do
  `01_system_prompt.md` (painel público sem cadastro, sem upload, sem VPS).

### Resultado do gate S1–S23 (2026-10-14, conferido no código real)
| Item | Status | Evidência | Correção |
|---|---|---|---|
| S1 | ✅ | grep de `key/secret/token/password/environ` nos arquivos da task: 0; fontes sem chave; `.gitignore:13-15` cobre `.env`; gitleaks no CI (`ci.yml:46`) — **não rodei local** (não instalado) | — |
| S2 | ✅ | `validacao.py:14` `validar_titulares` (cargo, nome, município ∈ 139, governador NULL e único, sem duplicata); `tse_candidatos.py` filtra UF/cargo/ELEITO; `test_to_ger_01_rejeita_municipio_fora_dos_139` | — |
| S3 | N/A | nenhum SQL no código da task (carga local em dict); `ruff` S608 ativo em `pyproject.toml:15` e passa | `MERGE` parametrizado entra com a carga real no BigQuery |
| S4–S9 | N/A | sem login, senha, JWT, cookie, endpoint com `:id` ou formulário | — |
| S10 | N/A | sem endpoint de entrada; o rate limit de saída (`Crawl-Delay` 10s, `to_ger_01.py`) é outra coisa | — |
| S11 | ✅ | saída só HTTPS com verificação de certificado e de nome do host: `_contexto_tls()` (`http.py:22-30`, certifi + intermediário público da Sectigo que o IBGE deixou de enviar, task 28); `URL_TSE` https; `cdn.tse.jus.br` e `dadosabertos.tse.jus.br` respondem 200 com esse contexto (14/10). Headers/CORS: N/A (sem servidor) | — |
| S12 | ⚠️ | a Service Account só-escrita em `dim_titular` ainda não existe: `02_task_fundacao_gcp.md:53` pendente, `infra/iam.md` não existe | incluir `dim_titular` na matriz SA×papel ao executar a task 02 |
| S13 | N/A | sem upload; o zip do TSE é lido em memória, só o membro fixo `consulta_cand_{ano}_TO.csv` (sem extrair em disco, sem zip-slip) | — |
| S14 | ⚠️ | nenhuma dependência nova (só stdlib); mas não há `dependabot.yml`/`renovate.json`; `pip-audit` não rodado (não instalado) | adicionar Dependabot (pip) — escopo da task 03 |
| S15 | ✅ | coletores sem `except`; erros específicos (`ColetaBloqueadaError`, `FonteIndisponivelError`); `base.py:77` re-lança, não engole | — |
| S16–S18 | N/A | sem Electron, VPS ou site exposto (Cloud Run Job) | — |
| S19 | ⚠️ | Trivy no CI, mas `aquasecurity/trivy-action@master` sem versão fixa (`ci.yml:60`); a task não adiciona imagem | fixar versão/SHA — escopo da task 03 |
| S20 | ✅ | `requirements.lock.txt` rastreado; CI e Dockerfile instalam do lock (`ci.yml:27`, `Dockerfile:18-20`); a task não adiciona pacote | — |
| S21 | N/A | nenhuma das fontes usa chave de API | — |
| S22 | ✅ | `log.py:12` registra só metadados (fonte, status, contagens, hash); a saída real da coleta não traz nome nem payload | — |
| S23 | ⚠️ | exclusão de conta e backup: N/A (sem contas). LGPD: 7 colunas apenas (`tse_candidatos.py`), CPF/e-mail/nascimento cobertos por teste; **mas** `docs/textos_legais.md:37` afirma "nenhuma informação pessoal identificável é coletado ou armazenado", o que a `dim_titular` (nome do titular) contradiz | Bruno decide a redação do texto legal (exceção do PRD §0.1 já existe) |

## Verificação
```bash
.venv/bin/ruff check src/coletores/to_ger_01.py src/coletores/to_ger_02.py src/cli.py tests/coletores/test_bloco_governanca.py tests/fixtures/governanca_payloads.py
.venv/bin/python -m pytest tests/coletores/test_bloco_governanca.py -q
.venv/bin/python -m src.cli coletar --fonte TO-GER-01 --ambiente dev   # rede real (TSE, Crawl-Delay 10s)
.venv/bin/python -m src.cli coletar --fonte TO-GER-02 --ambiente dev   # esperado: ColetaBloqueadaError, sem conexão
```
Esperado: `TO-GER-01` com `status=ok`, `linhas_processadas=140` e
`municipios_cobertos=139` (o governador tem `id_municipio` NULL); `TO-GER-02`
termina com `ColetaBloqueadaError` (RF-71). A `bq query` do plano original não
se aplica: o carregador de `dev` é local (dict em memória).

## Decisões tomadas
- **2026-10-14 — `TO-GER-02` fica bloqueado; o retrato entra como link, não
  dado (opção 1, aprovada pelo Bruno).** `GET divulgacandcontas.tse.jus.br/robots.txt`
  devolve 403 "Access Denied" (WAF Akamai; evidência em
  `RESPOSTA_DIVULGACANDCONTAS_ROBOTS_403`). Sem robots/termos confirmáveis e com
  acesso automatizado negado ativamente, vale RF-71. Leitura conservadora de
  propósito: o RFC 9309 trataria um 4xx como "sem regras", mas aqui há negação
  ativa de cliente automatizado, e contornar isso seria burlar controle de
  acesso. Consequência: `url_foto` = `NULL` (coluna mantida no DDL para quando
  houver autorização ou fonte alternativa). A dúvida "URL ou bytes" do critério
  original perde o objeto.
- **Fonte do `TO-GER-01`:** zips `consulta_cand_{ano}.zip` em `cdn.tse.jus.br`
  (`robots.txt` 404 = sem regras). Eleição mais recente de cada cargo: prefeito
  2024, governador 2022. `Crawl-Delay: 10` de `dadosabertos.tse.jus.br` aplicado
  por precaução.
- **Minimização (RNF-S05):** só 7 colunas saem da extração (`COLUNAS` em
  `to_ger_01.py`); CPF, e-mail, título e nascimento nunca entram.
- **`src/cli.py` entra na task:** `TO-GER-01`/`TO-GER-02` não estavam no
  `REGISTRO_COLETORES`; sem o registro o comando de verificação do passo 7 não
  roda. Mudança mínima de 2 linhas.
- **Gate de segurança S1–S23** (a skill hoje tem 23 itens; a spec dizia S1–S21).
- **Leitura do CSV do TSE em módulo comum (`tse_candidatos.py`):** o CI roda
  `ruff format --check src tests` e o `to_ger_01.py` formatado passava de 80
  linhas, contra o teste de contrato de ≤55. Mesmo padrão de `sidra.py` e
  `siconfi.py`. Comportamento idêntico: a coleta real repetida depois da
  refatoração devolveu o mesmo `hash_origem` (`18e19ef5…`).
- **`test_golive.py` 18 → 20:** o teste de cobertura do go-live (task 24) conta
  os coletores registrados. `TO-GER-01` e `TO-GER-02` entram no registro (o
  `TO-GER-02` bloqueado também, como `RF-71` prevê "falha por design"), então a
  contagem passa a 20. Ajuste intencional; `docs/verificacao_golive.md` segue
  dizendo "18 fontes ativas", que é verdade para o go-live.
- **Dois avisos antigos corrigidos em arquivos que a task tocou:** `listar =`
  sem uso em `src/cli.py` (F841) e espaço em branco em `test_golive.py`
  (format). Sem mudança de comportamento.
- **Pendência do Bruno (fora do repo):** no Sheets do catálogo, `TO-GER-02`
  deve ter `RESTRIÇÃO ROBOTS/TERMOS` começando com `Sim`, para o catálogo
  espelhar o bloqueio do código.
- **Pendência do Bruno (texto legal):** `docs/textos_legais.md:37` diz que
  nenhuma informação pessoal identificável é coletada ou armazenada. Com a
  `dim_titular` isso precisa citar a exceção do PRD §0.1 (nome do titular
  eleito, dado público). Não alterei: a redação é sua.
- **Pendência técnica:** `src/sql/ddl/dim_titular.sql` ainda não está em
  `src/sql/aplicar_ddl.sh`; ligar junto com a aplicação real no BigQuery.
