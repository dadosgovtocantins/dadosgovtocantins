---
task: Primeiro envio ao GitHub — histórico limpo, sem segredos, CI verde
status: em andamento — passos 1 a 10 feitos (21/10/2026); parado antes do push (passo 11, revisão do Bruno)
criada: 2026-10-21
---

# Primeiro envio ao GitHub

## Objetivo
O repositório privado `dadosgovtocantins/dadosgovtocantins` recebe o projeto com histórico novo e limpo, sem o e-mail de infraestrutura nem segredos, e a CI roda verde no GitHub.

## Por quê
O repositório remoto está vazio e nada do projeto está lá. O estado local não pode subir como está (conferido em 21/10, só leitura):
- o e-mail de infraestrutura está em **2 dos 3 commits** e em 4 arquivos rastreados (7 no total) — editar arquivos não apaga o histórico;
- os 3 commits têm o **e-mail pessoal do Bruno como autor**;
- `.gitignore`: a regra `data/` ignora também `src/ui/data/` (`painel_dados.json`, `painel_indicadores.json`, `municipios_to.json`) e `*.pem` ignora o certificado do IBGE: num clone, o painel, os testes e toda coleta do IBGE falhariam;
- `.data_raw/` (69 MB, com zip de 64 MB do TSE e dados simulados antigos) não está ignorado: 277 arquivos entrariam;
- a CI está vermelha: `ruff check` (14 erros em `scrapers_estaduais.py`, 3 deles `verify=False`) e `ruff format --check` (4 arquivos em `src` e 5 em `scripts`); `scripts/` ainda tem 9 erros de lint e a CI não o cobre.

Sem isso o robô diário (task 35) não tem onde rodar. Esta task cumpre também os passos 2 e 6 da task 03.

## Arquivos envolvidos
| Arquivo | O que muda |
|---|---|
| `.gitignore` | editar: `data/` → `/data/`; incluir `.data_raw/`; liberar `!src/coletor_base/certs/*.pem` |
| `scripts/varrer_segredos.sh` | criar: gitleaks no histórico inteiro + padrão do e-mail de infraestrutura em todos os commits, blobs e arquivos compactados (`.pptx`, `.zip`) |
| `.github/workflows/ci.yml` | editar: `ruff` e formato cobrem `scripts/`; varredura de segredos com gitleaks fixo + padrão do segredo `PADRAO_EMAIL_INFRA`; Trivy e imagem Docker com versão fixa e só quando Dockerfile/dependências mudam; tirar "repositório público" do comentário |
| `docs/PRD_Painel_Dados_Tocantins.md`, `docs/runbook.md`, `.planning/01_system_prompt.md`, `.planning/02_task_fundacao_gcp.md`, `.planning/05_task_identidade_nao_oficialidade.md`, `apresentacao_painel_to.html`, `scripts/gerar_pptx_apresentacao.py` | editar: trocar o e-mail por "a conta de infraestrutura do projeto" (sem o endereço); PRD e `01`/`03` também registram que o repositório do código é **privado** e o público terá só o site |
| `apresentacao_painel_to.pptx` | regenerar pelo script corrigido (é um zip: `grep` direto não enxerga o conteúdo) |
| `src/coletores/scrapers_estaduais.py` | **removido** (decisão do Bruno, 21/10, depois de eu corrigir o lint): tinha números inventados escritos como resultado e nenhum código o chamava. Cópia fora do projeto em `~/Backups/painel-to/` |
| `src/catalogo/maturidade.py`, `src/ia/parser_gemini.py`, `src/operacao/finops.py` | editar: só formatação |
| `scripts/automacao_coleta.py`, `exportar_ui_data.py`, `gerar_municipios_oficiais.py`, `gerar_pptx_apresentacao.py`, `gerar_sql_dim_municipio.py` | editar: 9 erros de lint (imports, `datetime.UTC`, `next(iter(...))`) e formatação |
| `.planning/03_task_repo_ci_cd.md`, `.planning/ROADMAP.md` | editar: registrar o que esta task fechou |

## Critérios de aceite
- [x] **Histórico limpo.** `git log --all` mostra só commits novos; `git log --all -G"$PADRAO_EMAIL_INFRA"` e `git grep -I -E "$PADRAO_EMAIL_INFRA" $(git rev-list --all)` devolvem 0; `git fsck --unreachable --no-reflogs` não lista objeto antigo; nenhum commit tem o e-mail pessoal do Bruno (autor nem committer).
      — *commit `e430bd9` é o único em todas as refs; `git log --all -G` = 0; padrão em qualquer objeto do repositório (`git cat-file --batch-all-objects`) = 0; `git fsck --unreachable --no-reflogs` = 0; autor e committer só o e-mail noreply; e-mail pessoal do Bruno = 0 em metadados e em arquivos*
- [x] **Árvore limpa.** Padrão do e-mail = 0 em todos os arquivos rastreados, inclusive dentro do `.pptx` descompactado; `.env.example` conferido pelo Bruno.
      — *`varrer_segredos.sh`: arquivos de texto e arquivo compactado (`.pptx` regenerado: só o slide 8 mudou) = 0; `.env.example` conferido pelo Bruno em 21/10 e coberto pela varredura sem exibir o conteúdo (`git grep -l`, gitleaks com `--redact`)*
- [x] **`.gitignore` certo.** `git check-ignore` não ignora `src/ui/data/*.json` nem `src/coletor_base/certs/sectigo_dv_r36.pem`; ignora `.data_raw/`, `.env`, `.claude/`, `CLAUDE.md`; `git ls-files | grep -c "^.data_raw"` = 0; nenhum arquivo rastreado acima de 5 MB.
      — *`git check-ignore`: `src/ui/data/*.json` e o `.pem` entram; `.data_raw/`, `/data/`, `.env`, `.claude/`, `CLAUDE.md`, `.venv/` ficam de fora; 285 arquivos, o maior com 2,59 MB; a trava temporária do Office (`~$*`) passou a ser ignorada*
- [x] **Funciona num clone.** Clone limpo do repositório local em pasta temporária + `pip install -r requirements.lock.txt` + `pytest -q`: todos passam (hoje 177, 0 falhas).
      — *clone local do commit final → venv novo → `pip install -r requirements.lock.txt` → 185 testes, código de saída 0 (medido sem `tail` no meio), 0 falhas, 0 erros, 0 pulados, cobertura 83%; o número de testes é o mesmo do repositório local*
- [x] **Lint verde.** `ruff check src tests scripts` e `ruff format --check src tests scripts` sem erro; `grep -rn "verify=False" src scripts` = 0.
      — *`ruff check src tests scripts` e `ruff format --check src tests scripts` limpos no repositório e no clone; `grep -rn "verify=False" src scripts` = 0*
- [x] **Varredura local.** `scripts/varrer_segredos.sh` (gitleaks com versão fixa e checksum conferido, `--log-opts="--all"`) = 0 achados; teste negativo: num repositório descartável fora do projeto, uma chave falsa e o padrão do e-mail fazem o script falhar.
      — *gitleaks 8.30.1 (checksum SHA-256 conferido): 1 commit varrido, nenhum vazamento; `tests/test_varrer_segredos.py` (8 testes) cobre arquivo novo, histórico, autor do commit, `.pptx`, gitleaks que acha segredo e gitleaks ausente; o gitleaks real detectou uma chave fabricada da AWS e um token `ghp_` em repositórios descartáveis. A varredura também reprovou o commit quando esta spec trazia uma chave falsa por extenso: achado real, corrigido*
- [x] **Segredo e padrão.** `PADRAO_EMAIL_INFRA` existe no GitHub (`gh secret list` mostra o nome, nunca o valor) e num arquivo local fora do repositório com permissão 600; o padrão não aparece em nenhum arquivo do projeto.
      — *`gh secret list` mostra `PADRAO_EMAIL_INFRA` (valor nunca exibido); arquivo local com permissão `-rw-------` em `~/.config/painel-to/`*
- [x] **Git local.** `git config --local user.email` = e-mail "noreply" da conta `dadosgovtocantins`; `git config --global user.email` idêntico ao de antes (comparado).
      — *`git config --local user.email` = `<id>+dadosgovtocantins@users.noreply.github.com`, autor "Painel TO em Dados"; `git config --global user.email` idêntico ao de antes (comparado)*
- [x] **Backup.** Bundle do repositório antigo fora da pasta do projeto, com `git bundle verify` ok; não é enviado a lugar nenhum.
      — *`~/Backups/painel-to/historico-antigo-2026-10-21.bundle` com `git bundle verify` = "complete history", mais cópia do `.git` antigo; ambos fora da pasta do projeto*
- [ ] **Remoto.** Repositório continua **privado** (`gh repo view --json visibility`), `main` enviada, GitHub Pages não ativado; proteção da `main` verificada e registrada como disponível ou indisponível no plano gratuito.
- [ ] **CI no GitHub.** A execução da `main` termina `success` nos jobs `qualidade` e `segredos` (e `imagem` quando disparado), com o mesmo número de testes do local; teste negativo: branch descartável com uma chave falsa no formato da AWS ("AKIA" + 16 caracteres entre A–Z e 2–7) faz o job `segredos` falhar; a chave é **montada na hora do teste e nunca escrita em arquivo do repositório** (a de exemplo da AWS é ignorada pelo gitleaks; e o valor escrito aqui na spec já reprovou a varredura em 21/10); a branch é apagada depois. O e-mail de infraestrutura **não** é usado no teste negativo (seria enviado ao GitHub).
- [ ] **Decisão registrada.** PRD, `01_system_prompt.md` e `03` dizem que o repositório do código é privado e o público terá só o site.
- [ ] Gate S1–S21 reportado na tabela da skill, sem ❌.

## Fora de escopo
- Orquestrador diário, workflow agendado e commits do robô com `[skip ci]` (task 35).
- Repositório público do site, GitHub Pages e o teste `test_conta_projeto_nunca_aparece_em_texto_publico` (task 36).
- IDs da planilha no código e catálogo (task 37); BigQuery pelo GitHub (task 38); fontes novas (39–45).
- Renomear a conta do GitHub (decisão do Bruno: manter `dadosgovtocantins`).
- Dependabot (S14 ⚠️ registrado na task 30).
- Adicionar `brunovima83` como colaboradora (decisão do Bruno, 21/10).

## Plano
- [x] 1. Backup do repositório atual em bundle fora do projeto; registrar o e-mail global do Git para provar que não muda.
- [x] 2. Corrigir o `.gitignore` e provar com `git check-ignore`.
- [x] 3. Criar o padrão do e-mail num arquivo local (fora do repositório, permissão 600) e o segredo `PADRAO_EMAIL_INFRA` no GitHub.
- [x] 4. `scripts/varrer_segredos.sh` + teste negativo em repositório descartável.
- [x] 5. Tirar o e-mail dos 7 arquivos; regenerar o `.pptx`; conferir a árvore.
- [x] 6. Corrigir lint e formatação de `src`, `tests` e `scripts` (incluindo `verify=False`); rodar a suíte.
- [x] 7. Atualizar `ci.yml`.
- [x] 8. Histórico novo: configurar o Git local, commit inicial a partir da árvore limpa, remover os ramos antigos, `reflog expire` + `gc --prune=now`; provar a limpeza.
- [x] 9. Clone de teste local + `pytest -q`.
- [x] 10. Varredura local com gitleaks (binário da release oficial, versão fixa, checksum conferido, pasta temporária, nada instalado no sistema).
- [ ] 11. **Pausa de confirmação:** mostrar ao Bruno a lista de arquivos, o tamanho e o resultado das varreduras; só enviar com o "pode enviar".
- [ ] 12. `git push` para o repositório privado; acompanhar a CI; teste negativo com a chave falsa; verificar a proteção da `main`.
- [ ] 13. Registrar a decisão de repositório privado no PRD, `01` e `03`; gate S1–S21; atualizar status da `03` e o ROADMAP.

## Segurança
| Item | Como se aplica |
|---|---|
| S1 segredos | núcleo da task: histórico limpo, gitleaks no histórico inteiro, padrão do e-mail como segredo, nada commitado |
| S12 menor privilégio | `permissions: contents: read` na CI; o login do `gh` tem só os escopos `repo` e `workflow` |
| S14 dependências / CI | instalação pelo `requirements.lock.txt`; gitleaks e Trivy com versão fixa |
| S19 Trivy | sai de `@master` para versão fixa (⚠️ herdado da task 03) |
| S20 dependency confusion | `--index-url https://pypi.org/simple` mantido |
| S22/S23 | os nomes dos titulares são dado público do TSE; nenhum dado pessoal novo |
| Demais | N/A (sem login, upload ou servidor próprio) |

## Verificação
```bash
bash scripts/varrer_segredos.sh                          # histórico inteiro + padrão do e-mail: 0 achados
git log --all --format='%ae %ce' | sort -u               # só o e-mail noreply
.venv/bin/ruff check src tests scripts && .venv/bin/ruff format --check src tests scripts
git clone . /tmp/clone-teste && (cd /tmp/clone-teste && python -m venv .venv && .venv/bin/pip install -r requirements.lock.txt pytest ruff && .venv/bin/pytest -q)
gh repo view dadosgovtocantins/dadosgovtocantins --json visibility,defaultBranchRef
gh run list --repo dadosgovtocantins/dadosgovtocantins --limit 3
```

## Decisões tomadas
Decisões de planejamento (21/10; as marcadas "minha chamada" são do agente e podem ser revertidas):
- **Histórico novo em vez de reescrever (minha chamada):** são só 3 commits, sem remoto, sem tags; um commit inicial limpo é mais simples e seguro do que reescrever. O texto dos 3 commits antigos fica no bundle de backup e nas specs de `.planning/`. Alternativa pedida pelo Bruno como válida: `git filter-repo` (já instalado).
- **Git local, nunca global:** o e-mail "noreply" vale só neste repositório; os outros projetos do Bruno seguem com o e-mail pessoal.
- **Sem trailer `Co-Authored-By` nos commits:** o `CLAUDE.md` do projeto proíbe quando `.claude/settings.json` não define `attribution.commit`.
- **Padrão do e-mail como segredo (minha chamada):** assim o próprio padrão nunca entra no repositório, nem na configuração do gitleaks.
- **Teste negativo sem o e-mail (minha chamada):** só uma chave falsa fabricada vai ao GitHub; a guarda do e-mail é testada localmente, em repositório descartável.
- **gitleaks pelo binário oficial com versão fixa (minha chamada):** em vez da action de terceiros, para controlar versão e dados.
- **`scrapers_estaduais.py` removido (decisão do Bruno, 21/10; antes, minha chamada era só corrigi-lo):** é código morto com valores inventados (RF-55). Antes de apagar, copiei para o backup, porque ele nunca esteve no histórico antigo; a suíte e o lint continuaram verdes sem ele.
- **Ramo `hml` não recriado (minha chamada):** o histórico novo nasce só com `main`; a CI continua aceitando `hml` se ele for criado depois.
- **Ficam só no disco do Bruno, fora do Git e no `.gitignore` (decisão dele, 21/10):** `index-antigo.html`, `Painel Palmas (standalone).html`, `apresentacao_painel_to.pptx` e `apresentacao_painel_to.html`. Os 4 testes do painel antigo (`tests/ui/test_tela_*.py` e `test_telas_apoio.py`) liam o `index-antigo.html`; passam a **pular quando o arquivo não existe** (rodam no computador do Bruno, pulam na CI), e `test_raiz_serve_painel_novo` deixou de exigir o arquivo antigo. O `src/ui/app.js` e os dados do painel antigo continuam no repositório.
- **Repositório do código privado:** desvio consciente do PRD e da task 03, que previam repositório público; registrado no passo 13.
- **Chave falsa nunca em arquivo (aprendido em 21/10):** ao registrar o teste negativo, a própria spec trouxe uma chave fabricada no formato da AWS e o gitleaks a reprovou no commit final. O teste de CI monta a chave a partir de pedaços no comando do `git commit` da branch descartável; nenhum arquivo do repositório a contém.
- **Teste negativo dos dois lados (feito em 21/10):** o gitleaks 8.30.1 real detectou uma chave fabricada da AWS e um token no formato `ghp_`, e ignorou a chave de exemplo da própria AWS (`...EXAMPLE`); por isso o teste de CI usa uma chave fabricada.
- **`imagem.yml` só manual (minha chamada, evidência):** simulei o recorte que o Dockerfile copia (`src/`, `tests/`, `pyproject.toml`, `README.md`, `LICENSE`) e a suíte falha na coleta (`tests/test_carregar_bigquery.py` importa `scripts/`); logo o build da imagem, que roda `pytest`, já falhava. O Cloud Run não está em uso. O Dockerfile não foi alterado.
- **CI em todo push e pull request (pedido do Bruno):** `on: push` sem filtro de branch, `pull_request` e `workflow_dispatch`; ações de terceiros fixadas por commit conferido contra a branch oficial (`checkout` v4 = `releases/v4`; `setup-python` v5 e `trivy-action` v0.36.0 na história da branch principal); `ruff==0.16.7`, `pytest==9.1.1` e `pytest-cov==7.1.0` iguais às locais; gitleaks 8.30.1 com checksum. As workflows passaram no `actionlint` 1.7.12.
- **Proteção da `main` em repositório privado gratuito:** segundo o Bruno (21/10), regras de proteção de branch e rulesets não existem nesse caso; a documentação consultada não confirma nem nega. Não bloqueia a task: a CI é a barreira em todo push e pull request. Registrar na verificação do passo 12 o que o GitHub mostrar.
- **Autor dos commits "Painel TO em Dados" (minha chamada):** só no escopo local deste repositório.
- **`~$*` ignorado:** o commit continha `~$apresentacao_painel_to.pptx`, a trava temporária do PowerPoint; saiu do commit e continua no disco.
- **Commit único reescrito 2x com `--amend` (antes de qualquer envio):** uma para tirar a trava do Office, outra para tirar a chave falsa desta spec; a cada vez, `reflog expire` + `gc --prune=now` e nova varredura.
- **Achado dos números inventados do `scrapers_estaduais.py` (12, 24, 139, 580, 12): resolvido pela remoção do módulo.**
