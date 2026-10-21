---
task: Orquestrador diário, sentinelas e estado das 9 fontes atuais
status: em andamento — passos 1 a 8 concluídos (21/10/2026); parado antes do passo 9 para revisão do backtest do 3σ e do diff
criada: 2026-10-21
depende_de: 34 (concluída), design 33
---

# Orquestrador diário (`atualizar.py` + `verificar.yml`)

## Objetivo
Todo dia às 14h (Brasília), o GitHub Actions verifica por canal oficial se as 9 fontes atuais têm dado novo e coleta só quando há; cada fonte é aceita inteira ou recusada inteira, e o robô atualiza `painel_dados.json` e `estado_fontes.json` sem intervenção.

## Por quê
Nada roda sozinho hoje: a coleta é manual (`scripts/exportar_painel.py`, a receita do Tesouro leva ~25 min) e o painel só reflete o que alguém coletou. Sem isso, "dados atualizados conforme a regra de cada fonte" não existe. O rascunho que o Bruno trouxe foi corrigido em 21/10: o IBGE tem **7** coletores (não 6), o Tesouro tem **1** (só a receita corrente líquida), e o TSE traz titulares **eleitos** (não "em exercício").

## As 9 fontes
| Fonte | Coletores |
|---|---|
| IBGE / SIDRA (7) | `TO-TER-01` população, `TO-TER-02` PIB municipal, `TO-TER-03` PIB estadual, `TO-TER-04` área, `TO-TER-05` PAM, `TO-TER-06` PPM, `TO-TER-07` PNAD Contínua |
| Tesouro / SICONFI (1) | `TO-REC-02` receita corrente líquida (RREO, com RGF para os municípios pequenos) |
| TSE (1) | `TO-GER-01` titulares eleitos (139 prefeitos + governador) |

## Sentinelas (como cada fonte avisa que há dado novo)
| Fonte | Sentinela (gera a `marca`) | Coleta também quando |
|---|---|---|
| IBGE | `/agregados/{id}/periodos`: "último período \| data de modificação"; 6 consultas (6579, 5938 compartilhado por TER-02 e TER-03, 4714, 5457, 3939, 4099) | — |
| SICONFI | `extrato_entregas` do estado (ente 17), últimos 3 exercícios: maior `data_status` de RREO/RGF | a cada 30 dias, para pegar as entregas tardias dos municípios |
| TSE | eleição vigente **calculada pela data**: prefeito 2024 até 31/12/2028; governador 2022 até 31/12/2026 e 2026 a partir de 01/01/2027 (posse em 1º de janeiro). `Last-Modified` do zip **não serve**: o TSE regrava os arquivos (o zip de 2024 foi de 63,91 MB em 14/10 para 63,97 MB em 21/10) | a cada 30 dias, para correções do TSE |

Coleta quando: não há estado da fonte (1ª execução), a `marca` mudou, passou o intervalo fixo, ou o Bruno forçou (`workflow_dispatch` com `forcar`). A `proxima_divulgacao` vem do calendário do IBGE quando o produto é conhecido (PNAD Contínua trimestral = `produto_id` 9173); senão é `null`.

## Regras de validação (decisões do Bruno, 21/10)
- **Cobertura de municípios.**
  - **IBGE e TSE: 139 municípios (100%)**, porque a publicação é simultânea; menos que isso recusa a fonte inteira. No TSE, 139 prefeitos + 1 governador, como a `validar_titulares` já exige.
  - **SICONFI: tolerância à inadimplência e ao atraso das prefeituras.** O atraso de municípios pequenos no RREO/RGF não pode impedir a atualização do agregado estadual nem dos municípios que já entregaram. Regras: (a) validação própria do `TO-REC-02` no lugar do piso genérico de 90%; (b) o **estado** precisa ter valor no exercício; (c) **piso:** município que já tem valor válido para um exercício nunca perde esse valor (a coleta nova é **mesclada** por município e exercício: entrega nova entra, retificação entra se passar na integridade, ausência na coleta nova mantém o valor anterior); (d) município sem entrega fica **ausente**, nunca zero (RF-55); (e) a cobertura por exercício nunca diminui.
- **3σ só em agregados estaduais e séries estruturais** (estado, população, Ideb), aplicada à **variação percentual entre períodos consecutivos**, não ao nível (série em tendência reprovaria valor legítimo). Reaproveita `checar_variacao_3_sigma`; com histórico menor que 3 pontos não trava. **Piso de variação** (descoberto no backtest): além de sair de 3σ, a variação precisa passar de 10% (população e PIB estadual) ou 6 p.p. (desocupação) para ser suspeita. Avalia toda variação que termina num período recém-coletado, inclusive a emenda com o histórico. Suspeito → não publica, mantém o anterior e abre issue. **Backtest** nas séries reais gravadas antes de ligar; se mais de 5% dos pontos históricos forem marcados, a regra é revista.
- **Municipais voláteis** (PAM, PPM, PIB municipal, receita municipal, e Comex, CAGED, SIH nas tasks futuras): **só integridade** — código IBGE de 7 dígitos entre os 139, contagem (conforme a regra de cobertura acima), tipo (número finito) e unidade.
- **Falha** (rede, 429 depois das tentativas, validação): mantém o último dado válido da fonte, `status = erro`, `falhas_consecutivas + 1`, mensagem truncada; nunca grava zero. `defasado` quando passa do prazo da fonte + 50%: anual 450 dias, trimestral 150, mensal 60.

## Arquivos envolvidos
| Arquivo | O que muda |
|---|---|
| `src/orquestracao/__init__.py`, `src/orquestracao/alcance.py` | criar: lógica da sonda (testável) |
| `scripts/testar_alcance.py` | criar: linha de comando da sonda |
| `.github/workflows/alcance.yml` | criar: execução manual da sonda no runner |
| `src/orquestracao/estado.py`, `src/orquestracao/sentinelas.py` | criar (passos 3 e 4) |
| `src/ui/data/estado_fontes.json` | criar (passo 3), versionado |
| `scripts/atualizar.py` | criar (passo 7) |
| `.github/workflows/verificar.yml` | criar (passo 8); `ci.yml` ganha `actionlint` |
| `src/coletor_base/http.py`, `src/coletores/siconfi.py`, `src/coletores/tse_candidatos.py`, `scripts/exportar_painel.py` | editar (passos 2, 5 e 6) |
| `tests/orquestracao/*`, `tests/fixtures/gravadas/*` | criar: testes sem rede, com respostas reais gravadas |

## Critérios de aceite
- [x] **Sonda de alcance:** `scripts/testar_alcance.py` testa as 9 fontes atuais e os endereços das tasks 39–45 (Comex Stat, API DEMAS, Inep, CKAN do Tesouro Transparente, FTP do CAGED, FTP do DATASUS, API da CGU) com 1 requisição leve cada e timeout de 15 s. O relatório JSON traz `url`, `protocolo`, `status_code`, `latencia_ms`, `tls_ok`, `acessivel` e `classe`; endereço inacessível não derruba os demais. Roda local e no GitHub (`alcance.yml`, manual); o relatório comparativo é registrado nesta spec e a diferença entre os dois ambientes recebe a classe `bloqueio_rede_runner`.
      — *26 endereços testados (14 das fontes atuais e 12 das tasks 39–45) no Mac do Bruno e no runner do GitHub (execução 39537078620, manual); 48 testes da sonda sem rede; relatório comparativo na seção "Resultado da sonda"; classes: ok, ok_requer_chave, erro_http_4xx, erro_servidor_5xx, falha_tls, falha_dns, falha_conexao, timeout, erro_ftp, erro_inesperado*
- [x] **Pausa depois da sonda:** se IBGE, SICONFI ou TSE estiver inacessível a partir do runner, a task para e o plano é revisto com o Bruno antes de construir o resto.
      — *IBGE, SICONFI e TSE (14 de 14 endereços) respondem a partir do runner: a condição de bloqueio não ocorreu; a task só segue para o passo 2 com o "de acordo" do Bruno*
- [x] **429:** o cliente HTTP inclui 429 nas tentativas, respeita `Retry-After` e o SICONFI usa 1 s entre consultas e até 5 tentativas (teste da configuração).
      — *`ClienteHTTP` com `Retry` do urllib3 (429/500/502/503/504, `Retry-After` respeitado, teto de 120 s); SICONFI com 1 s entre consultas e 5 tentativas; 7 testes com servidor local (`test_http_retry.py`), incluindo "404 não tenta de novo"*
- [x] **`estado_fontes.json`** com as 9 fontes (`ultimo_periodo_coletado`, `marca_sentinela`, `verificado_em`, `coletado_em`, `status`, `falhas_consecutivas`, `mensagem_erro`, `proxima_divulgacao`), schema validado por teste (`status` em ok/erro/defasado/suspeito, datas ISO em UTC, chave desconhecida recusada) e escrita atômica.
      — *`src/orquestracao/estado.py`, 34 testes; arquivo inicial gravado por `atualizar.py --inicializar` a partir do painel de 14/10 e das sentinelas de 21/10 (9 de 9 fontes com dado); campo extra `confirmado_em` (última vez em que a fonte foi confirmada atual, base do `defasado`)*
- [x] **Sentinelas** das 9 fontes testadas com respostas reais gravadas; o TSE com datas congeladas (31/12/2026 → governador 2022; 01/01/2027 → governador 2026; prefeito 2024 até 31/12/2028); `ELEICOES` do coletor deixa de ser fixo.
      — *`src/orquestracao/sentinelas.py`, 41 testes com respostas reais gravadas; `tse_candidatos.eleicoes_vigentes(data)` calcula as eleições (testes em 31/12/2026, 01/01/2027, 01/01/2029); o TSE não consulta rede na sentinela*
- [x] **Cenários da orquestração:** (a) sem novidade → não coleta, só `verificado_em`; (b) novidade → coleta, valida e atualiza os dois arquivos; (c) falha → mantém o dado anterior, `falhas_consecutivas + 1`, nada zerado; (d) agregado estadual suspeito → não publica; (e) município volátil → só integridade; (f) IBGE/TSE com menos de 139 municípios → recusa a fonte inteira; (g) SICONFI com municípios atrasados → atualiza o estado e os que entregaram, preserva o piso e deixa os ausentes sem dado; (h) `--forcar` só aceita ids conhecidos ou `todas`.
      — *19 testes do orquestrador (`test_orquestrador.py`) cobrem (a) a (g), recoleta fixa de 30 dias, `defasado` nos três prazos e sentinela fora do ar; 12 testes de ponta a ponta de `atualizar.py` cobrem (h) (`;rm -rf /`, `todas,TO-TER-01` e ids inventados são recusados com código 2 sem tocar nos arquivos); 54 testes de validação com o backtest nas séries reais*
- [ ] **`verificar.yml`:** `cron 0 17 * * *` (14h Brasília) e `workflow_dispatch` com `forcar`; `permissions` mínimas (`contents: write`, `issues: write`); `concurrency` sem cancelar a execução em andamento; `timeout-minutes: 60`; entrada passada por variável de ambiente e validada por lista; commit do `github-actions[bot]` com `[skip ci]` e sem `force push`; passa no `actionlint`, que também entra na CI.
      — *escrito; `actionlint` 1.7.12 local sem achados; job `workflows` adicionado à `ci.yml` com binário e SHA-256 fixos; falta a CI verde no GitHub*
- [ ] **Prova no GitHub:** execução manual com `forcar=TO-TER-04` e depois `forcar=todas`: os valores batem com o painel (PIB de Palmas 14.168.469; receita do estado 15.568.042,57; titulares), a CI **não** dispara no commit do robô, e uma segunda execução sem novidade altera só o `estado_fontes.json`.
- [x] **Issue automática** por fonte com 2 falhas seguidas, fechada quando volta a ok (lógica testada com `gh` simulado; o caminho real só será provado na primeira falha de verdade).
      — *`src/orquestracao/issues.py` + `scripts/sincronizar_issues.py`, 12 testes com `gh` simulado (abre com 2 falhas seguidas ou `defasado`, não duplica, fecha ao voltar a `ok`)*
- [ ] Custo projetado abaixo de 400 dos 2.000 minutos mensais; `pytest`, `ruff` e CI verdes; gate S1–S23 reportado.

## Fora de escopo
- Fontes novas (tasks 39–45); BigQuery a partir do GitHub (38); painel público e `estado_fontes` na tela (36); IDs da planilha no código (37).
- Coleta incremental por município (coleta-se a fonte inteira quando há novidade).
- 2FA e custódia da conta GitHub (pendência do Bruno).

## Plano
- [x] 1. Sonda de alcance: lógica, linha de comando, `alcance.yml`, execução local e no GitHub, relatório comparativo. **PAUSA para o Bruno.**
- [x] 2. Tratamento do 429 no `ClienteHTTP` e ritmo do SICONFI.
- [x] 3. Schema e módulo de estado (`estado_fontes.json`).
- [x] 4. Sentinelas das 9 fontes, com respostas reais gravadas.
- [x] 5. Eleições do TSE calculadas pela data.
- [x] 6. Exportador que preserva o último dado válido e mescla o SICONFI por município.
- [x] 7. `atualizar.py` com as regras de validação, incluindo o backtest do 3σ.
- [x] 8. `verificar.yml`, issue automática e `actionlint` na CI.
- [ ] 9. Execução real no GitHub (`forcar=TO-TER-04`, `forcar=todas`, execução sem novidade).
- [ ] 10. Gate S1–S23, documentação e ROADMAP.

## Segurança
- **S1:** a única credencial é o `GITHUB_TOKEN` da própria execução; nenhum segredo novo.
- **S2:** entrada do `workflow_dispatch` nunca vai direto para o shell (variável de ambiente + lista de ids permitidos).
- **S12:** `contents: write` e `issues: write` só no `verificar.yml`; os demais workflows ficam em `contents: read`.
- **S14:** ações de terceiros fixadas por commit; dependências do lock.
- **S15/S22:** exceções específicas, mensagens truncadas, nenhum valor sensível nos logs.
- Demais: N/A (sem login, upload ou servidor próprio).

## Resultado da sonda (21/10/2026)
Local = Mac do Bruno (21/10, 00h07 em Brasília); GitHub = runner `ubuntu-latest` (Ubuntu 24.04, Python 3.11.17), execução 39537078620, 1 minuto de Actions. Comparação: **23 `ok_nos_dois`, 3 `inacessivel_nos_dois`, 0 `bloqueio_rede_runner`**.

| Fonte | Endereços | Local | GitHub | Observação |
|---|---|---|---|---|
| IBGE (periodos de 6 agregados, dados, municípios, calendário) | 9 | 9 ok (227–432 ms) | 9 ok (629–851 ms) | cadeia TLS com o intermediário da Sectigo funciona no runner |
| SICONFI (RREO, RGF, extrato de entregas) | 3 | 3 ok | 3 ok | o RGF é o mais lento (2,4 s nos dois) |
| TSE (zips de 2022 e 2024, HEAD) | 2 | 2 ok | 2 ok | |
| Comex Stat | 2 | 2 ok | 2 ok | |
| DEMAS (API da Saúde) | 2 | 2 ok | 2 ok | |
| Tesouro Transparente (CKAN do CAPAG) | 1 | ok | ok | o `curl` do Mac tinha levado reset; com o cliente do projeto responde 200 |
| CGU (transferências) | 1 | 401 esperado | 401 esperado | alcançável; exige a chave gratuita |
| FTP do CAGED (PDET) e do DATASUS (SIM e CNES) | 3 | 3 ok (1,6–1,9 s) | 3 ok (1,9–2,7 s) | login anônimo e listagem funcionam no runner |
| **Inep** (Ideb, Censo Escolar, rendimento) | 3 | **3 falham** | **3 falham** | ver abaixo; **não é bloqueio do runner** |

**Inep:** o servidor `download.inep.gov.br` envia só o certificado do site (1 certificado), sem o intermediário "RNP ICPEdu GR46 OV TLS CA 2025"; o `curl` do macOS completa a cadeia sozinho e o Python não (`CERTIFICATE_VERIFY_FAILED`), o mesmo defeito do IBGE. Verificado com `openssl`: o intermediário (baixado do campo CA Issuers do próprio certificado) é assinado pela **GlobalSign Root R46, que já está no certifi**, e fecha a cadeia (`openssl verify` = OK; SHA-256 do certificado `E1:07:47:D4:DA:7B:AB:09:CB:A9:95:2F:01:9D:35:34:CB:9F:BA:07:0B:F1:3D:87:91:B1:69:9C:D2:FF:59:DD`). Sem verificação de TLS (só diagnóstico, fora do repositório) o servidor responde 200 em 3 de 3 tentativas. Além disso, a **primeira conexão de cada execução recebe `reset`** e as seguintes falham no TLS; o padrão é igual no Mac e no GitHub. Conclusão: a task 41 precisa levar o intermediário para `src/coletor_base/certs/` (como o da Sectigo) e o cliente precisa tentar de novo no `reset`.

## Achados durante a construção da sonda
- No urllib3 atual, `NewConnectionError` descende de `ConnectTimeoutError` e de `TimeoutError`: uma conexão recusada ou uma falha de DNS seria classificada como `timeout`. A classificação testa essas exceções antes do timeout, e `falha_dns` virou classe própria (testes para os dois casos).
- Um único pedido por endereço pode pegar um `reset` passageiro (caso do Inep). Recomendação para o Bruno aprovar: uma nova tentativa só em `falha_conexao` e `timeout`, registrada em `tentativas`, para o `bloqueio_rede_runner` não nascer de um erro passageiro. **Aprovado pelo Bruno e aplicado:** 1 nova tentativa só em `falha_conexao` e `timeout` (até 2 tentativas), com a contagem no campo `tentativas` do relatório. O retry de conexão do Inep e o certificado intermediário ficam para a task 41.

## Resultado do backtest do 3σ (21/10/2026)
`.venv/bin/python scripts/backtest_3sigma.py`: cada variação histórica é avaliada contra as anteriores (janela que cresce, mínimo de 3), nas séries reais do estado.

| Série | Pontos | Avaliados | 3σ puro marca | Com o piso marca |
|---|---|---|---|---|
| `TO-TER-01` população (2001–2026), piso 10% | 22 | 18 | **3 (16,7%)**: 2005 (+3,4%), 2008 (−3,9%), 2011 (+8,4%) | 0 |
| `TO-TER-03` PIB estadual (2002–2023), piso 10% | 22 | 18 | 0 | 0 |
| `TO-TER-07` desocupação (1T2012–2T2026), piso 6 p.p. | 58 | 54 | **3 (5,6%)**: 1T2013 (+1,6), 1T2021 (+5,8), 3T2021 (−5,1) | 0 |

- O 3σ puro **estoura o limite de 5%** na população (quebras metodológicas do Censo/contagem) e na desocupação (a Covid), como previsto na spec; por isso a regra ganhou o piso. Com o piso, **0 de 90** pontos históricos são marcados.
- **Limite do piso:** erro menor que o piso não é pego (um valor errado em 9% na população passa). Pega o erro de escala (×10, ×0,1), que é o risco real de uma mudança de unidade ou de vírgula no IBGE.
- **Decisão pendente do Bruno:** piso de **6 p.p.** na desocupação (0 falsos positivos históricos) ou **5 p.p.** (2 marcados: os pulos reais da Covid, 3,7%; pega um erro de ×0,1 em taxas acima de 5,6%). Usei 6; `--piso TO-TER-07=5` reproduz o outro cenário.
- `TO-REC-02` (RCL do estado) tem só 3 exercícios e não recebe 3σ; fica com integridade e a regra do estado obrigatório.

## Verificação
```bash
.venv/bin/python scripts/testar_alcance.py --origem local --saida alcance_local.json   # passo 1
gh workflow run alcance.yml --repo dadosgovtocantins/dadosgovtocantins                 # passo 1, no GitHub
.venv/bin/pytest -q && .venv/bin/ruff check src tests scripts
```

## Decisões tomadas
- **Aprovada pelo Bruno em 21/10/2026**, com a regra de cobertura da seção "Regras de validação" e de acordo com as chamadas do agente: horário das 14h (17h UTC), commit diário do `estado_fontes.json` pelo `github-actions[bot]` sem disparar a CI (o `painel_dados.json` só muda com dado novo), coleta da fonte inteira, e `defasado` em 450/150/60 dias.
- **Lógica da sonda em `src/orquestracao/alcance.py` (minha chamada):** o script `scripts/testar_alcance.py` é só a linha de comando, para a lógica ficar testável e no mesmo pacote das sentinelas.
- **Piso do 3σ (minha chamada, a confirmar):** 10% na população e no PIB estadual, 6 p.p. na desocupação, depois do backtest acima.
- **`defasado` sobrepõe `erro`/`suspeito` (minha chamada):** uma fonte que fica mais que o prazo sem ser confirmada vira `defasado`, e a `mensagem_erro` continua no registro. Uma fonte confirmada todo dia (sentinela sem novidade) nunca fica defasada, mesmo que o dado tenha 600 dias.
- **Sentinela fora do ar:** a fonte vai para `erro` sem coletar (a menos que seja forçada, caso em que coleta com a marca antiga). A `marca` só é guardada quando a coleta é aceita; uma coleta recusada é tentada de novo no dia seguinte.
- **Issues por `gh` (minha chamada):** rótulo `fonte-com-problema`, uma issue por fonte (título `[ID] ...`), aberta com 2 falhas seguidas ou `defasado`, fechada ao voltar a `ok`.
- **Relatório da sonda no log do GitHub (minha chamada):** o JSON é impresso entre marcadores e vai também para o resumo da execução, em vez de depender de uma ação de upload de artefato.
