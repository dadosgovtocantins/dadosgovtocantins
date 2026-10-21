---
documento: Design — automação da coleta (GitHub Actions + Python)
status: aprovado pelo Bruno em 2026-10-21, com 4 travas técnicas incorporadas (seção 4); próxima: spec 34
criado: 2026-10-21
---

# Automação da coleta — design

## 1. Intenção
O painel deve mostrar **dados reais e atualizados conforme o ritmo de cada fonte**, sem ninguém rodar nada à mão.
Hoje nada roda sozinho: a coleta é manual (`scripts/exportar_painel.py`), o painel só abre no computador do Bruno e a maior parte dos cartões diz "Não coletado".

A fonte de verdade das fontes é a planilha **Base_Mestre_Dados_Abertos_TO** (aba BASE_MESTRE, 30 fontes).

## 2. Metas, não-metas e anti-metas
**Metas**
- Verificar todo dia, de forma automática, se cada fonte publicou algo novo, e coletar só quando houver novidade.
- Publicar o painel com link público e com o dado mais recente de cada fonte.
- Mostrar em cada cartão de que período é o dado, de qual fonte e quando foi verificado.
- Cobrir as fontes federais que têm API ou arquivo oficial, e as exceções aprovadas (seção 4).

**Não-metas**
- Fontes estaduais sem API oficial (Portal da Transparência TO, TCE-TO, DOE, SEPLAN, SSP, SECTUR, AGETO, CGE, SEDUC, Lab63): continuam como **link**. Leitura de página/PDF fica para outro projeto.
- Atualização de hora em hora: nenhuma das 30 fontes publica nesse ritmo (a mais frequente, o DOE, é diária e fica como link).
- Painel lendo direto do BigQuery.

**Anti-metas (o que tornaria isto um fracasso mesmo "funcionando")**
- Qualquer número inventado, estimado sem aviso, ou **zero no lugar de ausente** (RF-55).
- Publicar coleta **pela metade** (uma fonte com parte dos municípios, uma tabela incompleta).
- Expor o e-mail da conta de infraestrutura, uma chave ou um token.
- Qualquer custo financeiro.
- Contornar robots.txt, WAF, login ou limite de uso de uma fonte (RF-71).
- O painel parecer canal oficial do Governo do Tocantins (RR-05).

## 3. Restrições (conferidas na documentação oficial em 20–21/10/2026)
- **GitHub Free, repositório privado:** 2.000 min/mês de Actions e 500 MB de artefatos; acabou a cota sem cartão → as execuções **param, sem cobrança**. A regra que desliga agendamentos após 60 dias sem atividade vale **só para repositório público**.
- **GitHub Pages:** grátis só em repositório **público** (no privado exige plano pago).
- **BigQuery Sandbox:** sem cartão; tabelas expiram em 60 dias (a carga renova); sem DML; 10 GiB de armazenamento por toda a vida do projeto; sem partição por data (ver task 31).
- **Regras do projeto:** catálogo antes do código (RF-82); nome do coletor = ID da planilha; testes nunca acessam a internet; log estruturado; nenhum segredo no repositório; e-mail de infraestrutura nunca em texto público.

## 4. Decisões do Bruno (20–21/10/2026)
| Tema | Decisão |
|---|---|
| Onde roda | **GitHub Actions**, com os coletores em Python |
| Repositório do código | `dadosgovtocantins/dadosgovtocantins`, **privado**. Nome mantido ciente do risco de parecer oficial (RR-05) |
| Painel público | **2º repositório, público, só com o site** (painel + arquivos de dados), servido pelo GitHub Pages gratuito |
| Microdados (CAGED, SIH, SIM/Sinasc) | **Exceção à RNF-S05:** o arquivo é lido em memória, só o **total por município** é gravado, nenhum registro individual é salvo, o arquivo é descartado. **Trava de memória (Bruno, 21/10):** a leitura é obrigatoriamente em **streaming/chunks ou DuckDB com filtro UF = 17 aplicado durante a leitura**; é proibido carregar o arquivo nacional inteiro na RAM (ex.: `pandas.read_csv` sem filtro nem `chunksize`) |
| Travas técnicas do Bruno (21/10) | (1) histórico do Git limpo antes do 1º envio e varredura de segredos no histórico inteiro (seção 8); (2) microdado só em streaming/DuckDB (linha acima e seção 6); (3) trava de 3σ só em agregados estaduais e séries estruturais (seção 6); (4) a conta `brunovima83` **não** é colaboradora do repositório; alertas só no e-mail da conta do projeto, e o redirecionamento o Bruno resolve fora do GitHub (seção 11) |
| Chave da CGU (repasses FNDE) | **Exceção a "sem cadastro":** chave gratuita da API do Portal da Transparência, guardada como segredo do GitHub. O dado em si é público sem login |
| Cartões fora da planilha | **Incluir os que têm fonte oficial** (entram primeiro na planilha); **retirar os sem fonte viável** |

## 5. Como funciona
```
Repositório PRIVADO (código)                          Repositório PÚBLICO (só o site)
 ├─ .github/workflows/verificar.yml  (todo dia)  ──►   index.html, support.js, src/ui/…,
 │     └─ scripts/atualizar.py                         painel_dados.json, estado_fontes.json
 │          1. para cada fonte: "há novidade?"         └─ GitHub Pages → link público
 │          2. se sim: coleta → valida → aceita
 │          3. regenera painel_dados.json + estado_fontes.json
 │          4. commit dos dados no privado (histórico)
 │          5. publica o site no repositório público
 │          6. carrega no BigQuery (se a ligação sem chave funcionar)
 └─ .github/workflows/testes.yml  (todo envio: ruff + pytest)
```

**Verificação de novidade ("sentinela") — consulta barata e oficial, antes de baixar qualquer coisa:**

| Fonte | Como saber se há dado novo | Ritmo da fonte |
|---|---|---|
| IBGE/SIDRA (PIB, população, PAM, PPM, área, PNAD) | API de Calendário do IBGE + campo `modificacao` em `/agregados/{id}/periodos` | trimestral/anual |
| SICONFI (RCL, LRF) | toda semana: endpoint oficial `extrato_entregas` (novas entregas de RREO/RGF dos 140 entes); coleta só dos entes/períodos novos | bimestral/quadrimestral |
| TSE (titulares) | eleição mais recente **cujo mandato já começou**: os eleitos de 2026 entram em 01/01/2027 (antes disso, segue 2022/2024) | por eleição |
| Comex Stat (exportações) | `GET /cities/dates/updated` | mensal |
| Saúde — CNES leitos | maior competência (`nu_comp`) disponível na API DEMAS | mensal |
| Inep (Ideb, Censo Escolar, rendimento) | arquivo do ano seguinte passa a existir (`HEAD` com `Last-Modified`) | anual/bienal |
| CAPAG (Tesouro Transparente) | `metadata_modified` do conjunto no CKAN | quadrimestral |
| CAGED | nova pasta `AAAAMM` no FTP oficial do PDET | mensal |
| SIH (internações) | nova competência na API DEMAS | mensal |
| SIM/Sinasc (mortalidade infantil) | novo arquivo `DOTOAAAA`/`DNTOAAAA` no FTP do DATASUS | anual |
| FNDE (repasses, via CGU) | novo mês com dados na API | mensal |

**Estado por fonte (`estado_fontes.json`, versionado):** último período coletado, `verificado_em`, `coletado_em`, status (`ok`/`erro`/`defasado`), mensagem de erro, próxima divulgação conhecida.

## 6. "Sem erros": garantias e como cada uma é cumprida
| Garantia | Mecanismo |
|---|---|
| Nada pela metade | cada fonte é aceita ou recusada inteira; recusada → fica o último dado válido |
| Ausente ≠ zero | mantido do código atual (RF-55); testes existentes cobrem |
| Dado velho não passa por novo | passou o prazo esperado da fonte + tolerância sem dado novo → status `defasado`, visível no painel |
| Bloqueio de uso (429) e instabilidade | nova tentativa com espera crescente, respeitando `Retry-After`; ritmo por fonte (SICONFI 1 s entre consultas) |
| Valor estranho — agregados estaduais e séries estruturais | variação > 3σ marca `suspeito` e **não publica** sem revisão (regra do PRD); o painel mantém o último valor válido e abre uma issue. Vale para: todo indicador do **estado** (PIB, receita, desocupação…), **população** e **Ideb** (séries estruturais, definidas pelo Bruno) |
| Valor estranho — dados municipais voláteis | **sem 3σ** (evita falso positivo em município pequeno: um único ano de safra ou de exportação já foge de 3σ). Só **integridade**: código IBGE de 7 dígitos entre os 139, contagem de municípios (cobertura mínima de 90%, como já faz `validar_registros`; município ausente continua ausente, nunca zero), tipo (número finito, nunca texto/NaN) e unidade esperada. Vale para: **Comex Stat, CAGED, SIH, mortalidade** (definidos pelo Bruno) e, por chamada minha, **PAM, PPM, PIB municipal e receita municipal** |
| Memória e disco do runner | microdado nacional nunca inteiro na RAM: streaming/chunks ou DuckDB com `UF = 17` na leitura; teto de trabalho de 6 GB. Runner de repositório privado: 2 vCPU, **8 GB de RAM e 14 GB de disco** (documentação do GitHub, 21/10; o Bruno citou 7 GB: adoto o teto menor); descompactação também precisa caber nos 14 GB, então o arquivo é lido direto do `.7z`/`.dbc` sem extrair tudo |
| Rodar duas vezes ao mesmo tempo | `concurrency` no workflow: uma execução por vez |
| Falha silenciosa | falha do workflow → e-mail do GitHub; fonte com erro → issue automática no repositório privado, fechada quando volta |
| Regressão de código | testes offline com respostas reais gravadas; CI verde obrigatório antes de juntar código |
| Estourar a cota | tempo máximo por job; estimativa ≈ 300–400 min/mês de 2.000 |
| Segredos | GitHub Secrets; BigQuery por Workload Identity Federation (sem chave JSON); commits com e-mail "noreply" |

## 7. O que o painel passa a mostrar
- Em cada cartão: período do dado e fonte (já existe) + "verificado em DD/MM".
- Fonte com status `defasado` ou `erro`: aviso discreto no cartão; nunca número inventado.
- No rodapé: "Dados verificados em DD/MM/AAAA"; quando conhecida, a próxima divulgação (calendário do IBGE).
- Cartões retirados por não terem fonte viável: **Cobertura vacinal** (a API oficial não filtra por UF) e **Convênios recebidos** (sem fonte oficial verificada).
- Cartões cuja fonte existe mas não tem API (Mapa de Empresas: "Empresas ativas", "Empresas abertas e fechadas"; e todos os estaduais) passam a mostrar **link para a consulta oficial** em vez de "Não coletado".

## 8. Antes do primeiro envio ao GitHub (obrigatório)
1. **E-mail de infraestrutura fora da árvore E do histórico.** Verificado em 21/10: o e-mail está em **2 dos 3 commits locais** e em 4 arquivos rastreados; no total aparece em 7 arquivos (PRD, runbook, specs 01/02/05, apresentação HTML, gerador de PPTX), e os 3 commits têm o **e-mail pessoal do Bruno como autor**. Editar os arquivos hoje **não apaga o passado**. Por isso: backup do repositório atual fora da pasta do projeto (`git bundle`) → o 1º envio sobe de um **histórico novo e limpo** (commit inicial), com objetos antigos eliminados (`reflog expire` + `gc --prune=now`) e conferência de que nada resta (`git log --all`, blobs e objetos soltos). Se o Bruno preferir manter os 3 commits, o caminho alternativo é `git filter-repo` (já instalado).
2. **Varredura de segredos no histórico inteiro, nunca só na árvore atual:** gitleaks com `git log --all` antes do envio (local) e a cada execução da CI (`fetch-depth: 0`); o **padrão do e-mail de infraestrutura** vira um segredo (`PADRAO_EMAIL_INFRA`, no GitHub e num arquivo local fora do repositório), para o próprio padrão nunca ser commitado. O `.pptx` é um zip: `grep` direto não enxerga o conteúdo, então ele é regenerado pelo script corrigido e conferido descompactado.
3. **`.gitignore`:** a regra `data/` ignora também `src/ui/data/` (onde estão `painel_dados.json`, `painel_indicadores.json` e `municipios_to.json`: sem eles o painel e os testes não funcionam num clone) → ancorar em `/data/`; incluir `.data_raw/` (69 MB, com zip de 64 MB do TSE e dados simulados antigos); liberar o certificado público `src/coletor_base/certs/*.pem` (hoje ignorado por `*.pem`; sem ele toda coleta do IBGE falha no GitHub).
4. `.env.example`: o Bruno confere (contém a partícula do nome da conta; o agente não pode ler o arquivo).
5. **Git local com o e-mail "noreply" da conta, configurado só neste repositório** (nunca `--global`: os outros projetos do Bruno continuam com o e-mail pessoal).
6. **CI verde no GitHub:** hoje `ruff check` falha (14 erros em `scrapers_estaduais.py`, incluindo `verify=False`) e `ruff format --check` falha em 4 arquivos; a CI passa a cobrir também `scripts/` (9 erros a corrigir); `trivy-action@master` e a imagem Docker (1 GB) passam a ter versão fixa e rodar só quando o Dockerfile ou as dependências mudam, para poupar minutos da cota.
7. Gate S1–S21 reportado na tabela da skill.

## 9. Mudanças em documentos e na planilha
- **PRD:** RNF-S05 ganha a exceção de microdado agregado em memória; a regra de acesso ganha a exceção da chave da API da CGU (só para o dado que é público no site sem login).
- **Planilha:** novas linhas (Comex Stat, CAPAG, FNDE via CGU, SIM/Sinasc, SIH, CNES leitos); corrigir o link do TCE-TO (domínio mudou para `portaldocidadao.tceto.tc.br`); o agente prepara as linhas prontas e o Bruno cola (a planilha é dele).
- **Teste `test_conta_projeto_nunca_aparece_em_texto_publico`:** hoje proíbe a palavra "dadosgovtocantins" no README e na LICENSE. Com a conta e o endereço do painel (`dadosgovtocantins.github.io`) públicos por escolha do Bruno, na task 36 o teste passa a proibir só o **e-mail completo**; até lá o README não cita a conta.
- **IDs:** o código passa a usar o ID da planilha (regra "nome do coletor = ID do catálogo"); hoje divergem (ex.: população é `TO-TER-01` no código e `TO-ECO-03` na planilha). Os dados no BigQuery são recarregados com os IDs novos.

## 10. Plano em tasks (cada uma vira spec em `.planning/` com o gate de aprovação)
| Ordem | Task | Entrega |
|---|---|---|
| 34 | Preparar e fazer o 1º envio | seção 8: histórico limpo, e-mail fora, `.gitignore`, gitleaks no histórico inteiro, CI verde no GitHub |
| 35 | Orquestrador diário | teste de alcance a partir do GitHub; `atualizar.py`, sentinelas e estado para as 9 fontes atuais, retry de 429, workflow diário, commit dos dados |
| 36 | Painel público | repositório do site, Pages, "verificado em" e status por fonte no painel |
| 37 | Catálogo alinhado | IDs da planilha no código, linhas novas da planilha, cartões retirados/links estaduais |
| 38 | BigQuery a partir do GitHub | Workload Identity Federation; se o Sandbox não permitir, carga segue manual (registrado) |
| 39 | Comex Stat | exportações por município |
| 40 | Saúde — leitos (CNES) | leitos por município |
| 41 | Inep | Ideb, Censo Escolar (matrículas) e taxa de aprovação |
| 42 | SICONFI LRF + CAPAG | despesa com pessoal (LRF) e capacidade de pagamento |
| 43 | CAGED | saldo de empregos por município (microdado agregado). **Obrigatório:** leitura em streaming/chunks ou DuckDB filtrando UF = 17 durante a leitura; nunca o arquivo Brasil inteiro na RAM (runner: 8 GB RAM, 14 GB disco); teste com arquivo grande simulado que falha se o pico de memória passar do teto |
| 44 | SIH + SIM/Sinasc | internações e mortalidade infantil (microdado agregado). **Mesma trava de memória da task 43** (o `.dbc` do SIM/Sinasc também é lido em fluxo, registro a registro) |
| 45 | FNDE via CGU | repasses por município (depende da chave) |

## 11. Deixado para quem constrói (chamadas do agente, revisáveis)
- Horário da verificação: todo dia às 14h de Brasília (17h UTC), depois das divulgações da manhã do IBGE e do Comex.
- Nome do repositório público: `dadosgovtocantins/painel` → `https://dadosgovtocantins.github.io/painel/`.
- Publicação no repositório público por token de escopo mínimo (só aquele repositório), guardado como segredo.
- Tolerância para `defasado`: prazo esperado da fonte + 50%.
- Issue automática por fonte com erro há mais de 2 verificações seguidas.
- Commit no repositório privado **só quando algum dado muda** (repositório privado não sofre a regra dos 60 dias); o site público é republicado todo dia para atualizar o "verificado em".
- **Alertas só no e-mail da própria conta do projeto.** A conta `brunovima83` **não** é adicionada como colaboradora (decisão do Bruno, 21/10); o redirecionamento do e-mail para a caixa pessoal o Bruno resolve por fora do GitHub.
- Novas dependências previstas (cada uma passa pelo S14 na sua task): leitor de `.7z` (CAGED), leitor de `.dbc` (SIM/Sinasc), leitor de `.ods`/`.xlsx` (Inep, CAPAG).

## 12. Riscos conhecidos
- **Sites do governo bloqueando as máquinas do GitHub** (ficam fora do Brasil): ainda não testado. A task 35 começa com um teste de alcance a partir do GitHub em todos os endereços da seção 5; fonte inacessível de lá fica registrada e não entra no agendamento até haver alternativa.
- **Tesouro Transparente** derruba a conexão a partir do computador do Bruno; testar a partir do GitHub (task 42). Se falhar também, CAPAG fica como link.
- **IBGE** envia cadeia TLS incompleta (resolvido com o certificado intermediário; precisa ir para o repositório — seção 8).
- **SICONFI** bloqueia com 429 depois de muitas consultas; resolvido com ritmo de 1 s e nova tentativa com espera.
- **Workload Identity Federation no Sandbox** não confirmado (task 38 testa primeiro).
- **Cron do GitHub** pode atrasar alguns minutos em horário de pico; irrelevante para fontes diárias/mensais.
- **Proteção da `main` em repositório privado no plano gratuito:** não confirmado na documentação (a página consultada não trata de conta pessoal). A task 34 verifica; o robô precisa escrever os dados na `main` de qualquer forma, então a regra "só por pull request" valeria apenas para código.
- **RAM dos microdados:** 8 GB no runner de repositório privado; sem a trava de streaming/DuckDB (seção 4), um único mês do CAGED nacional já pode derrubar a execução.
- **Nome da conta com "gov"** (RR-05): decisão consciente do Bruno; o aviso de não-oficialidade continua em todas as telas.
