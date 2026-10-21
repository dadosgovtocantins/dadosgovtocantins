---
task: Orquestrador diário, sentinelas e estado das 9 fontes atuais
status: em andamento — passo 1 (sonda de alcance) em execução; pausa obrigatória depois dele
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
- **3σ só em agregados estaduais e séries estruturais** (estado, população, Ideb), aplicada à **variação percentual entre períodos consecutivos**, não ao nível (série em tendência reprovaria valor legítimo). Reaproveita `checar_variacao_3_sigma`; com histórico menor que 3 pontos não trava. Suspeito → não publica, mantém o anterior e abre issue. **Backtest** nas séries reais gravadas antes de ligar; se mais de 5% dos pontos históricos forem marcados, a regra é revista.
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
- [ ] **Sonda de alcance:** `scripts/testar_alcance.py` testa as 9 fontes atuais e os endereços das tasks 39–45 (Comex Stat, API DEMAS, Inep, CKAN do Tesouro Transparente, FTP do CAGED, FTP do DATASUS, API da CGU) com 1 requisição leve cada e timeout de 15 s. O relatório JSON traz `url`, `protocolo`, `status_code`, `latencia_ms`, `tls_ok`, `acessivel` e `classe`; endereço inacessível não derruba os demais. Roda local e no GitHub (`alcance.yml`, manual); o relatório comparativo é registrado nesta spec e a diferença entre os dois ambientes recebe a classe `bloqueio_rede_runner`.
- [ ] **Pausa depois da sonda:** se IBGE, SICONFI ou TSE estiver inacessível a partir do runner, a task para e o plano é revisto com o Bruno antes de construir o resto.
- [ ] **429:** o cliente HTTP inclui 429 nas tentativas, respeita `Retry-After` e o SICONFI usa 1 s entre consultas e até 5 tentativas (teste da configuração).
- [ ] **`estado_fontes.json`** com as 9 fontes (`ultimo_periodo_coletado`, `marca_sentinela`, `verificado_em`, `coletado_em`, `status`, `falhas_consecutivas`, `mensagem_erro`, `proxima_divulgacao`), schema validado por teste (`status` em ok/erro/defasado/suspeito, datas ISO em UTC, chave desconhecida recusada) e escrita atômica.
- [ ] **Sentinelas** das 9 fontes testadas com respostas reais gravadas; o TSE com datas congeladas (31/12/2026 → governador 2022; 01/01/2027 → governador 2026; prefeito 2024 até 31/12/2028); `ELEICOES` do coletor deixa de ser fixo.
- [ ] **Cenários da orquestração:** (a) sem novidade → não coleta, só `verificado_em`; (b) novidade → coleta, valida e atualiza os dois arquivos; (c) falha → mantém o dado anterior, `falhas_consecutivas + 1`, nada zerado; (d) agregado estadual suspeito → não publica; (e) município volátil → só integridade; (f) IBGE/TSE com menos de 139 municípios → recusa a fonte inteira; (g) SICONFI com municípios atrasados → atualiza o estado e os que entregaram, preserva o piso e deixa os ausentes sem dado; (h) `--forcar` só aceita ids conhecidos ou `todas`.
- [ ] **`verificar.yml`:** `cron 0 17 * * *` (14h Brasília) e `workflow_dispatch` com `forcar`; `permissions` mínimas (`contents: write`, `issues: write`); `concurrency` sem cancelar a execução em andamento; `timeout-minutes: 60`; entrada passada por variável de ambiente e validada por lista; commit do `github-actions[bot]` com `[skip ci]` e sem `force push`; passa no `actionlint`, que também entra na CI.
- [ ] **Prova no GitHub:** execução manual com `forcar=TO-TER-04` e depois `forcar=todas`: os valores batem com o painel (PIB de Palmas 14.168.469; receita do estado 15.568.042,57; titulares), a CI **não** dispara no commit do robô, e uma segunda execução sem novidade altera só o `estado_fontes.json`.
- [ ] **Issue automática** por fonte com 2 falhas seguidas, fechada quando volta a ok (lógica testada com `gh` simulado; o caminho real só será provado na primeira falha de verdade).
- [ ] Custo projetado abaixo de 400 dos 2.000 minutos mensais; `pytest`, `ruff` e CI verdes; gate S1–S23 reportado.

## Fora de escopo
- Fontes novas (tasks 39–45); BigQuery a partir do GitHub (38); painel público e `estado_fontes` na tela (36); IDs da planilha no código (37).
- Coleta incremental por município (coleta-se a fonte inteira quando há novidade).
- 2FA e custódia da conta GitHub (pendência do Bruno).

## Plano
- [ ] 1. Sonda de alcance: lógica, linha de comando, `alcance.yml`, execução local e no GitHub, relatório comparativo. **PAUSA para o Bruno.**
- [ ] 2. Tratamento do 429 no `ClienteHTTP` e ritmo do SICONFI.
- [ ] 3. Schema e módulo de estado (`estado_fontes.json`).
- [ ] 4. Sentinelas das 9 fontes, com respostas reais gravadas.
- [ ] 5. Eleições do TSE calculadas pela data.
- [ ] 6. Exportador que preserva o último dado válido e mescla o SICONFI por município.
- [ ] 7. `atualizar.py` com as regras de validação, incluindo o backtest do 3σ.
- [ ] 8. `verificar.yml`, issue automática e `actionlint` na CI.
- [ ] 9. Execução real no GitHub (`forcar=TO-TER-04`, `forcar=todas`, execução sem novidade).
- [ ] 10. Gate S1–S23, documentação e ROADMAP.

## Segurança
- **S1:** a única credencial é o `GITHUB_TOKEN` da própria execução; nenhum segredo novo.
- **S2:** entrada do `workflow_dispatch` nunca vai direto para o shell (variável de ambiente + lista de ids permitidos).
- **S12:** `contents: write` e `issues: write` só no `verificar.yml`; os demais workflows ficam em `contents: read`.
- **S14:** ações de terceiros fixadas por commit; dependências do lock.
- **S15/S22:** exceções específicas, mensagens truncadas, nenhum valor sensível nos logs.
- Demais: N/A (sem login, upload ou servidor próprio).

## Verificação
```bash
.venv/bin/python scripts/testar_alcance.py --origem local --saida alcance_local.json   # passo 1
gh workflow run alcance.yml --repo dadosgovtocantins/dadosgovtocantins                 # passo 1, no GitHub
.venv/bin/pytest -q && .venv/bin/ruff check src tests scripts
```

## Decisões tomadas
- **Aprovada pelo Bruno em 21/10/2026**, com a regra de cobertura da seção "Regras de validação" e de acordo com as chamadas do agente: horário das 14h (17h UTC), commit diário do `estado_fontes.json` pelo `github-actions[bot]` sem disparar a CI (o `painel_dados.json` só muda com dado novo), coleta da fonte inteira, e `defasado` em 450/150/60 dias.
- **Lógica da sonda em `src/orquestracao/alcance.py` (minha chamada):** o script `scripts/testar_alcance.py` é só a linha de comando, para a lógica ficar testável e no mesmo pacote das sentinelas.
- **Relatório da sonda no log do GitHub (minha chamada):** o JSON é impresso entre marcadores e vai também para o resumo da execução, em vez de depender de uma ação de upload de artefato.
