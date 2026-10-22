---
task: Painel público no GitHub Pages, "verificado em" e situação das fontes
status: concluída (22/10/2026)
criada: 2026-10-21
depende_de: 35 (concluída), design 33
---

# Painel público (`dadosgovtocantins/painel` + GitHub Pages)

## Objetivo
Qualquer pessoa abre `https://dadosgovtocantins.github.io/painel/` e vê o painel com os dados da última verificação, com "Verificado em" e a situação de cada fonte. O código, a coleta e os testes continuam no repositório privado.

## Por quê
O painel só roda no computador do Bruno (`python3 -m http.server`). A task 35 já atualiza os dados todo dia, mas ninguém de fora enxerga o resultado, e a tela mostra só "Dados coletados em …" (a data da última coleta, não a da última verificação) e esconde se uma fonte está com erro ou defasada.

## O que muda
| Arquivo | O que muda |
|---|---|
| `scripts/montar_site.py` | criar: copia para uma pasta de saída **só** os arquivos de uma lista fixa (nada fora dela), confere o conteúdo e falha se achar o e-mail de infraestrutura ou um segredo |
| `scripts/publicar_site.sh`, `scripts/github_known_hosts` | criar: atualização **incremental** do clone do repositório público (só os arquivos que mudaram entram no commit) por **deploy key SSH** (escrita só no `painel`); servidor conferido contra as chaves oficiais da GitHub |
| `.github/workflows/verificar.yml` | editar: passo de publicação depois do commit dos dados; só roda se o segredo `PAINEL_DEPLOY_KEY` existir |
| `.github/workflows/ci.yml` | editar: `pip-audit` no lock (S14) |
| `.github/dependabot.yml` | criar: `pip` e `github-actions`, semanal (S14) |
| `index.html`, `src/ui/painel-logica.js`, `src/ui/css/painel.css` | editar: ícones e fonte locais (sem unpkg), "Verificado em", situação das fontes, aviso legal dos titulares |
| `src/ui/vendor/phosphor/`, `src/ui/vendor/inter/` | criar: ícones Phosphor 2.1.1 (MIT) e Inter (OFL) servidos pelo próprio site, com a licença de cada um |
| `tests/test_montar_site.py`, `tests/test_publicar_site.py`, `tests/ui/*`, `tests/test_nao_oficialidade.py` | criar/editar |
| `README.md`, `docs/runbook.md` | editar: endereço do painel e como publicar/reverter |

## Lista fixa do site (o que vai para o público)
`index.html`, `support.js`, `tocantins_municipios_regioes.geojson`, `bandeiras/`, `src/ui/painel-logica.js`, `src/ui/css/painel.css`, `src/ui/vendor/` e `src/ui/data/{painel_dados,painel_indicadores,municipios_to,estado_fontes}.json`, mais `.nojekyll`, `404.html` e `robots.txt` gerados. **Fora:** `src/` de Python, `tests/`, `.planning/`, `docs/`, `scripts/`, `.github/`, `.data_raw/`, `*.pptx`, `index-antigo.html`, o `dados_coletados_real.json` antigo (dados simulados) e qualquer arquivo novo que ninguém tenha colocado na lista. A lista foi conferida no código: o `index.html` só carrega esses arquivos (prova no Chrome, sem 404 além do `favicon.ico` do navegador).

## Decisões do Bruno (21/10/2026)
- **Endurecimento junto desta task:** `pip-audit` no `ci.yml` e `.github/dependabot.yml` (pip e github-actions). **Trivy/Docker continua só manual** (`imagem.yml`) e documentado como fora do caminho crítico: a produção é GitHub Actions + Pages, sem container.
- **unpkg:** a chamada externa sai; os arquivos dos ícones ficam no próprio site, dentro da lista fixa do `montar_site.py`.
- **Google Fonts:** pode ficar na CDN ou local, se for simples; a falha da fonte nunca pode bloquear a renderização (`display=swap`, pilha de fontes de reserva).
- **Texto legal dos titulares (LAI):** o aviso do painel diz que os nomes de prefeitos e governador vêm da base pública oficial do TSE e se referem exclusivamente a ocupantes de cargos públicos eletivos.
- **Histórico do repositório público:** publicação **incremental** sobre o clone, para as bandeiras e o GeoJSON (3,8 MB) não serem duplicados a cada commit diário; muda só o que mudou (o `estado_fontes.json`).
- **Lista estrita** no `montar_site.py`, com testes que barram arquivo fora da lista e vazamento do e-mail de infraestrutura.
- **Parar antes de publicar:** o Bruno cria o repositório `dadosgovtocantins/painel` e o token de escopo mínimo (`PAT_PUBLICACAO_PAINEL`).

## Critérios de aceite
- [x] **Endurecimento:** `pip-audit` roda na CI contra `requirements.lock.txt` e reprova com vulnerabilidade conhecida; `dependabot.yml` valida (pip e github-actions, semanal); Trivy documentado como manual/fora do caminho crítico.
      — *job `dependencias` na `ci.yml` (`pip-audit` 2.10.1 contra o lock, `--no-deps --disable-pip`) e execução semanal da CI às segundas, para vulnerabilidade nova aparecer sem precisar de push; `.github/dependabot.yml` (pip e github-actions, semanal); `actionlint` limpo; Trivy segue só no `imagem.yml` manual e está no runbook como fora do caminho crítico. O `pip-audit` já achou e corrigimos o `certifi` (PYSEC-2026-4320) na task 35*
- [x] **Sem terceiros bloqueantes:** `index.html` não referencia `unpkg.com` nem nenhum outro endereço externo além (no máximo) do Google Fonts com `display=swap`; um teste varre o site montado e falha com qualquer `http(s)://` de CDN não permitido; ícones e fonte carregam do próprio site.
      — *ícones Phosphor 2.1.1 (só woff2) e Inter (subconjunto latino) em `src/ui/vendor/`; **o `support.js` carregava React e ReactDOM do unpkg (sem eles o painel nem abria)**: copiados para `src/ui/vendor/react/` (SHA-384 conferido contra o SRI do original) e o runtime aponta para a cópia; o Babel (que só serve a `x-import` de JSX, inexistente aqui) não é carregado. Prova no Chrome: todas as requisições da página são do próprio endereço. Google Fonts saiu de vez (Inter local, `font-display: swap`). Licenças (MIT, OFL, MIT) junto dos arquivos; `?v=` do `support.js` entrou na checagem por SHA-256*
- [x] **`montar_site.py`:** monta a pasta só com a lista fixa; arquivo extra na lista de origem é ignorado, arquivo da lista ausente derruba a montagem; falha se o e-mail de infraestrutura (padrão do segredo/arquivo local) ou um segredo aparecer em qualquer arquivo; saída determinística; roda sem rede.
      — *`src/orquestracao/site.py` + `scripts/montar_site.py`; 61 testes em `tests/test_montar_site.py` (arquivo intruso em pasta liberada, `.DS_Store`, arquivo da lista ausente, 5 tipos de segredo em 3 arquivos sem vazar o conteúdo na mensagem, padrão do e-mail, endereço externo nos 5 arquivos próprios, JSON quebrado, `painel_dados` sem bloco, estado fora do schema, saída perigosa (projeto, dentro, pai), pasta com outras coisas intocada, sincronização que apaga o que saiu e preserva o `.git`, CLI). O site real tem 107 arquivos e 4,4 MB; serviu e renderizou no Chrome sem nenhum 404 além do `favicon.ico` do navegador*
- [x] **Tela:** o rodapé mostra "Verificado em dd/mm/aaaa hh:mm (Brasília)" a partir do `estado_fontes.json`; um bloco "Situação das fontes" (recolhido por padrão) lista as 9 fontes com nome, órgão, status por **texto e ícone** (não só cor), data do último dado e, quando houver, a mensagem; `estado_fontes.json` ausente ou inválido não quebra o painel (a linha some e o aviso diz que a situação não está disponível); funciona nos temas claro e escuro, em 375 px, sem rolagem horizontal e com navegação por teclado.
      — *rodapé com "Última verificação das fontes: 21/10/2026 às 09:34 (horário de Brasília) · 9 de 9 fontes atualizadas" e bloco recolhido (`<details>`, teclado nativo) com 9 fontes, status por ícone + texto (Atualizada, Defasada, Com falha, Em análise) e mensagem só fora de `ok`; lógica pura `PainelLogica.situacaoFontes` testada no Node (13 testes: horário UTC→Brasília inclusive na virada do ano, status inventado vira "Com falha" e não é repassado, fonte ausente não some, arquivo inválido devolve `null`); conferido no Chrome nos temas claro e escuro em 1280 px. **Não verificado em 375 px:** o Chrome sem janela não reduz o viewport abaixo de ~500 px, então a checagem de celular ficou só pelo CSS (grade `minmax(0,1fr)`, `overflow-wrap`, alvo de toque de 44 px)*
- [x] **Texto legal:** o rodapé traz o aviso dos titulares (TSE, LAI); o teste de não-oficialidade passa a proibir **só o e-mail completo** da conta de infraestrutura (o nome da conta e o endereço do painel são públicos).
      — *aviso no rodapé (TSE, cargos públicos eletivos, Lei 12.527/2011); `test_email_da_conta_de_infraestrutura_nunca_aparece_em_texto_publico` proíbe o nome da conta seguido de "@" no README, LICENSE e `index.html`; o `montar_site` barra o mesmo em qualquer arquivo do site e o padrão completo do e-mail quando disponível*
- [x] **`publicar_site.sh`:** testado com um repositório remoto local: primeira publicação cria tudo; segunda sem mudança não cria commit; mudança só no `estado_fontes.json` gera um commit que toca só esse arquivo; nunca usa `--force`; o token não aparece no log.
      — *11 testes contra um repositório remoto local vazio: 1ª publicação cria o site inteiro (1 commit), a 2ª diz "Nada a publicar" e não cria commit, mudança só no `estado_fontes.json` gera 1 commit que toca só esse arquivo, arquivo que saiu da lista é removido, segredo no site aborta antes de qualquer push (repositório continua vazio), sem o padrão do e-mail recusa, repositório inexistente falha com mensagem clara, token ausente da saída, sem `--force`/`set -x`; autor `github-actions[bot]`. O token vai pelo ambiente do Git (`GIT_CONFIG_*`), nunca na URL nem em argumento*
- [x] **`verificar.yml`:** o passo de publicação só roda com o segredo presente (sem ele, a execução termina verde e diz que a publicação está desligada); `actionlint` e CI verdes.
      — *último passo do workflow, depois das issues; `actionlint` limpo; o repositório de destino e o segredo `PADRAO_EMAIL_INFRA` (obrigatório na publicação) entram por `env`; CI verde no GitHub (commit 18a955b); a execução agendada das 14h (cron de verdade) rodou sozinha com o passo novo e terminou verde dizendo "Publicação desligada"*
- [x] `pytest`, `ruff` e CI verdes; gate S1–S23 reportado.
      — *556 testes verdes, `ruff` e `actionlint` limpos, gitleaks limpo, CI verde nos 4 jobs (`qualidade`, `dependencias`, `segredos`, `workflows`; commit 18a955b); gate na seção abaixo*
- [x] **Depois do "de acordo" do Bruno (passos 9 e 10):** primeira publicação real, URL pública abrindo com dados e "Verificado em" do dia, gitleaks no repositório público limpo, execução sem novidade atualizando só o `estado_fontes.json` no público.
      — *1ª publicação (execução 39715926513, commit público c731201): 107 arquivos, nenhum `.py`/`.md`/`tests`/`.planning`/`scripts`/`docs`/`.github`/segredo; gitleaks sem achados e o padrão do e-mail de infraestrutura ausente do conteúdo e dos metadados; autor `github-actions[bot]`. Pages ligado por `gh api` (`main` / raiz, HTTPS forçado, build `built`). **URL pública `https://dadosgovtocantins.github.io/painel/`**: todos os arquivos principais respondem 200, o Chrome renderiza o painel com dados reais (Palmas, PIB 14,2 R$ bi, população 302.692, titular do TSE) e a página só contata o próprio endereço. 2ª execução sem novidade (39716156534): 9 "sem novidade" e o commit público 11dbc99 tocou só `src/ui/data/estado_fontes.json` (+19 −19)*

## Fora de escopo
- Domínio próprio, analytics e cookies.
- Fontes novas (tasks 39–45) e o BigQuery a partir do GitHub (38).
- Reescrever o painel ou mudar as telas além do rodapé e da situação das fontes.
- 2FA e custódia da conta GitHub (pendência do Bruno, RT-14; recomendada **antes** de ligar a publicação).

## Plano
- [x] 1. Endurecimento: `pip-audit` na CI e `dependabot.yml`.
- [x] 2. Ícones (Phosphor) e fonte (Inter) locais; `index.html` sem unpkg.
- [x] 3. `montar_site.py` com a lista fixa e os testes de vazamento.
- [x] 4. Tela: "Verificado em", situação das fontes e aviso legal; testes de UI.
- [x] 5. Teste do e-mail completo no lugar do nome da conta.
- [x] 6. `publicar_site.sh` incremental, testado com remoto local; passo no `verificar.yml` desligado sem segredo.
- [x] 7. Documentação (README, runbook), gate S1–S23 e CI verde. **PAUSA para o Bruno criar o repositório e o token.**
- [x] 8. Primeira publicação real e prova da URL pública.
- [x] 9. Fechar a task no ROADMAP.

## Segurança
- **S1:** a deploy key SSH (`PAINEL_DEPLOY_KEY`, escrita só no `painel`, sem acesso à conta nem ao repositório do código) é segredo do GitHub; a chave privada nunca passa pelo chat nem pelo log: vai para um arquivo temporário 0600 apagado ao sair, sem configuração nem agente SSH da máquina e com o servidor conferido (`StrictHostKeyChecking=yes`).
- **S2:** o site é só leitura; o texto vindo dos JSONs é sempre exibido como texto, nunca como HTML (como já é para o titular).
- **S11:** o Pages força HTTPS; sem cabeçalhos próprios (limite do Pages), então o site não carrega script nem estilo de terceiros e a fonte, se externa, só como CSS de fonte. Registrar a limitação.
- **S12:** o token de publicação não escreve em nenhum outro repositório; `verificar.yml` continua com `contents` e `issues` e nada além.
- **S14/S20:** `pip-audit`, Dependabot e ações fixadas por commit; ícones e fonte vendorizados com versão, licença e SHA-256 conferidos por teste.
- **S22:** nenhum log com o token nem com o conteúdo dos arquivos.
- **Privacidade (LAI/LGPD):** os nomes dos titulares são dado público de cargo eletivo, só nome e cargo (sem CPF, sem endereço, sem partido); o aviso legal fica no rodapé.
- Demais: N/A (sem login, upload, banco ou servidor próprio).

## Riscos
- O repositório público expõe o nome da conta e o endereço do painel (decisão do Bruno no design).
- Sem 2FA na conta, o risco de publicar um site público sob ela sobe.
- O Pages não permite cabeçalhos de segurança próprios (CSP, HSTS configurável).
- A reversão de uma publicação ruim é um novo commit no repositório público (nunca `--force`); anotar no runbook.

## Gate S1–S23 (21/10/2026)
| Item | Status | Evidência | Correção |
|---|---|---|---|
| S1 | ✅ | token só como segredo do GitHub e só pelo ambiente do Git (`scripts/publicar_site.sh`, `GIT_CONFIG_*`); teste prova que não aparece na saída; gitleaks no histórico e `montar_site` com 5 tipos de segredo + padrão do e-mail: 0 achados | — |
| S2 | ✅ | `src/orquestracao/site.py` valida JSON, schema do estado e blocos do painel antes de copiar; a tela exibe mensagens como texto e `situacaoFontes` descarta status inventado (`tests/ui/test_situacao_fontes.py`) | — |
| S3–S10 | N/A | site estático: sem SQL, login, sessão, cookie, CSRF nem escrita | — |
| S11 | ⚠️ | HTTPS é forçado pelo Pages; CSP por `<meta>` no `index.html` (`default-src 'none'`, script/estilo/fonte/conexão só do próprio site, sem host externo; testada no Chrome: 0 violações, e uma CSP propositalmente restritiva gerou violações, o que prova que o log as enxerga). **Limite do Pages:** não permite cabeçalhos próprios (HSTS ajustável, `X-Frame-Options`, `frame-ancestors`) e a meta CSP não cobre `frame-ancestors`; `'unsafe-eval'` é exigido pelo runtime `x-dc` | aceito; reavaliar se um dia houver domínio próprio com Cloudflare |
| S12 | ✅ | `verificar.yml` com `contents` e `issues` write só nele; o token de publicação é fine-grained só do repositório `painel` com `contents: write` (runbook); CI e demais workflows em `contents: read` | — |
| S13, S16–S18, S21, S23 | N/A | sem upload, Electron, VPS, WAF, chave de API própria nem conta de usuário; o aviso legal do TSE/LAI está no rodapé | — |
| S14 | ✅ | `pip-audit` na CI (`ci.yml`, job `dependencias`) e semanal; `dependabot.yml` (pip e github-actions); ações fixadas por commit; `tests/ui/test_vendor.py` confere SHA-256 de cada arquivo de terceiros e o SHA-384 do React contra o SRI do runtime | — |
| S15 | ✅ | `publicar_site.sh` e `montar_site.py` mostram só nome de arquivo e tipo do achado, nunca o conteúdo | — |
| S19 | ⚠️ | Trivy só manual (`imagem.yml`), **decisão do Bruno**: produção é GitHub Actions + Pages, sem container; documentado no runbook | aceito |
| S20 | ⚠️ | lock commitado e `pip-audit` limpo, mas sem hashes (`--require-hashes`); o front não tem gerenciador de pacotes (arquivos de terceiros fixados por SHA-256) | avaliar hashes junto do Dependabot |
| S22 | ✅ | sem `set -x`, token fora da saída (testes); log do orquestrador só com id da fonte e contagem | — |

Nenhum ❌. Os ⚠️ são limites do Pages (S11), decisão do Bruno (S19) e melhoria de lock (S20).

## Achado depois do envio: PRs do Dependabot
O `dependabot.yml` abriu 7 PRs na hora (5 de `pip`, 2 de `github-actions`: `actions/checkout` 4→7 e `actions/setup-python` 5→7). Todos reprovam no job `segredos`: **PRs do Dependabot não recebem os segredos do Actions** (`PADRAO_EMAIL_INFRA` chega vazio e o `varrer_segredos.sh` sai com 2). Correção sem enfraquecer o gate: cadastrar o mesmo segredo também como **segredo do Dependabot** (`gh secret set PADRAO_EMAIL_INFRA --app dependabot`, valor vindo do arquivo local, sem imprimir). Pendente de autorização do Bruno; os PRs não foram mesclados nem fechados.

## Achado na primeira publicação real (22/10/2026)
- **Defeito meu em `publicar_site.sh`:** o push falhou (o token foi criado só com Metadata, sem **Contents: Read and write**: 403 em `painel`, e um blob vazio também é recusado), mas o script escondia o erro (`2>/dev/null`) e o `||` do fallback engolia a falha do `git pull` num repositório vazio: imprimiu "Site publicado" com o repositório público ainda vazio. Os testes só cobriam push que dá certo. **Correção:** nada de stderr escondido; mensagem clara de recusa; uma segunda tentativa só se o ramo existir no remoto; e sucesso só depois de conferir NO REMOTO (`git ls-remote`) que o ramo aponta para o commit. 4 testes novos reproduzem o caso (remoto que recusa via `pre-receive`, recusa uma vez, recusa sempre) e reprovam o script antigo (teste negativo feito).
- **Token substituído por deploy key (22/10/2026, a pedido do Bruno: "VC PODE FAZER?"):** o token fine-grained foi criado só com Metadata (sem Contents: Read and write), o Bruno não achou a permissão na tela e a GitHub não tem API para criar/editar tokens. Troquei por uma **deploy key SSH** com a mesma garantia de escopo (um repositório, escrita), feita por comando: chave ed25519 gerada localmente, parte pública cadastrada no `painel` (id 167257619, escrita), privada como segredo `PAINEL_DEPLOY_KEY`, cópia local apagada (`rm -P`). Provas: `git push --dry-run` no `painel` aceito (`[new branch] HEAD -> main`) e **recusado** no repositório do código (`denied to deploy key`); chaves do servidor da GitHub conferidas por duas fontes (API `/meta` e `ssh-keyscan`, SHA256:+DiY3wv…). O segredo `PAT_PUBLICACAO_PAINEL` foi apagado. O token que passou pelo chat tem só leitura de metadados e pode ser revogado em Settings > Developer settings (inofensivo, mas convém).
- **SSH do Mac:** o `~/.ssh/config`/agente do computador do Bruno oferecia a chave pessoal da conta brunovima83 (`Hi brunovima!`); por isso o script usa `-F /dev/null`, `IdentityAgent=none` e `IdentitiesOnly=yes`.

## Verificação
```bash
.venv/bin/pytest -q && .venv/bin/ruff check src tests scripts && .venv/bin/ruff format --check src tests scripts
.venv/bin/python scripts/montar_site.py --saida /private/tmp/site && ls /private/tmp/site
actionlint
```

## Decisões tomadas
- **Aprovada pelo Bruno em 21/10/2026**, com as definições da seção "Decisões do Bruno".
- **Aviso legal sem "partidos" (minha chamada, a confirmar):** o painel exibe só o **nome** do titular (não o partido); o texto cita nome e cargo. Se o partido passar a ser exibido, o texto muda junto.
