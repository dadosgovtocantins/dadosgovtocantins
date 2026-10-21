---
task: Repositório público, CI/CD e separação de ambientes
status: concluída (21/10/2026), com 2 desvios: repositório privado e sem proteção de branch (limitação do plano gratuito) — ver task 34
sprint: S1
eap: 1.1.4, 1.1.5
---

# Repositório público, CI/CD e ambientes

## Objetivo
Colocar o código no GitHub público desde o primeiro dia, com CI que roda lint,
testes e scan de segredos em todo PR, e deploy automatizado para HML e PROD.

## Por quê
O código aberto desde a S1 é o plano de continuidade inteiro (PRD §9.4): se a
bolsa acabar antes do go-live, o que estiver público é o resultado; o que estiver
na máquina, não é. E como o repositório é **público**, o scan de segredos deixa
de ser precaução e vira requisito (PRD §12.2) — um segredo commitado é público
no instante do push.

## Arquivos envolvidos
| Arquivo | O que muda |
|---|---|
| `.gitignore`, `LICENSE`, `README.md` | criar |
| `.github/workflows/ci.yml` | criar — lint, testes, gitleaks |
| `infra/cloudbuild.yaml` | criar — build + deploy hml/prod |
| `Dockerfile` | criar — Python 3.11 + PySUS (imagem base, sem browser) |
| `pyproject.toml`, `requirements*.txt` | criar |
| `docs/runbook.md` | editar — seção de deploy e rollback |

## Critérios de aceite
- [x] Repositório no GitHub com `LICENSE` permissiva (MIT), `README.md` explicando que é
      projeto de extensão da Unitins **e não canal oficial do Governo do TO** —
      **desvio decidido pelo Bruno em 21/10/2026: repositório do código PRIVADO**
      (`dadosgovtocantins/dadosgovtocantins`); o público será só o site (task 36).
      Enviado na task 34 (commit `f7a6d0d`)
- [x] `.planning/` versionado (não está no `.gitignore`) — `git ls-files` lista os
      11 arquivos de `.planning/`
- [ ] Branch `main` protegida: merge só via PR, CI verde obrigatório, sem push
      direto — **NÃO atendido: impossível no plano gratuito.** A API do GitHub responde
      403 "Upgrade to GitHub Pro or make this repository public to enable this feature"
      para proteção de branch e rulesets (conferido em 21/10/2026). Mitigação em vigor:
      a CI (lint, formato, testes e segredos) roda em todo push e pull request
- [x] Branches `main` (prod), `hml`, `feature/*` em uso — `main` e `hml` criadas
- [x] CI roda em todo PR e falha em: erro de `ruff`, teste vermelho **ou segredo
      detectado** — CI verde na `main` (execução 39533782569: 181 testes passaram,
      4 pulados, cobertura 91%); PR de teste #1 com chave falsa: o job `segredos`
      reprovou no `push` (39534071966) e no `pull_request` (39534098715), o job
      `qualidade` passou, e a chave não aparece nos logs. `ruff` e teste vermelho não
      foram simulados no GitHub (os jobs falham pelo código de saída)
- [x] `gitleaks detect --log-opts="--all"` limpo no histórico completo —
      `1 commits scanned … no leaks found` (rodado via container oficial)
- [x] `Dockerfile` builda com Python 3.11 + PySUS e roda `pytest` no build —
      build verde, **1.01 GB** (limite 1.5 GB); step `[10/11] … pytest -q` DONE 11.9s
- [x] Container roda como usuário sem privilégio — `uid=1000(coletor)`
- [x] `cloudbuild.yaml` faz deploy em HML no push para `hml` e em PROD só via tag
      — escrito e versionado; a **execução** depende do projeto GCP (task 02)
- [x] Nenhum coletor chega a PROD sem passar por HML — regra implementada no
      gatilho (tag criada a partir de commit que já rodou em HML) e documentada
      em `docs/runbook.md`
- [x] `docs/runbook.md` tem o procedimento de rollback — e também o de segredo
      vazado (revogar antes de limpar histórico)

## Fora de escopo
- Publicar o catálogo como recurso aberto (task 25)
- Cloud Scheduler (task 08)
- Testes dos coletores (task 06)

## Plano
- [x] 1. `git init`, `.gitignore`, `LICENSE`, `README.md`; primeiro commit com `.planning/`
- [x] 2. Criar o repositório (privado, decisão de 21/10) — proteção de `main` impossível no plano gratuito (ver critérios)
- [x] 3. `pyproject.toml` + dependências + `ruff` configurado
- [x] 4. `Dockerfile` e build local verde
- [x] 5. `ci.yml` com lint + pytest + gitleaks
- [x] 6. PR de teste com chave falsa provando que o CI barra (PR #1, fechado sem merge; branch apagada)
- [x] 7. `cloudbuild.yaml` com deploy hml/prod e rollback documentado

## Segurança
Gate S1–S21: **S1 segredos** (gitleaks no CI, histórico limpo, nada de `.env`
versionado), **S14 dependências/CI** (versões pinadas, CI obrigatório),
**S19 Trivy** (scan da imagem no pipeline), **S20 dependency confusion**
(só PyPI oficial, sem índice extra não confiável), **S15 erros** (build não
vaza credencial em log).

## Verificação

```bash
ruff check src tests && ruff format --check src tests && pytest -q
docker run --rm -v "$PWD":/repo zricethezav/gitleaks:latest detect --source /repo --redact --log-opts="--all"
docker build -t painel-to:dev . && docker run --rm painel-to:dev coletar --fonte TO-TER-01 --ambiente dev
gh api repos/<owner>/<repo>/branches/main/protection --jq '.required_status_checks'   # pendente
```

### Saída real

```
$ ruff check src tests
All checks passed!

$ ruff format --check src tests
6 files left unchanged

$ pytest -q
....                                                                     [100%]
4 passed in 0.01s

$ gitleaks detect --source /repo --redact --log-opts="--all"
INF 1 commits scanned.
INF scanned ~67436 bytes (67.44 KB) in 242ms
INF no leaks found

$ docker build -t painel-to:dev .
#14 [10/11] RUN pip install --no-cache-dir pytest && pytest -q && pip uninstall -y pytest
#14 DONE 11.9s
#16 naming to docker.io/library/painel-to:dev DONE 8.2s
tamanho: 1.01GB

$ docker run --rm painel-to:dev coletar --fonte TO-TER-01 --ambiente dev
{"status": "nao_implementado", "id_fonte": "TO-TER-01", "ambiente": "dev",
 "detalhe": "despacho de coletores chega na task 06 (ColetorBase)"}

$ docker run --rm --entrypoint id painel-to:dev
uid=1000(coletor) gid=1000(coletor) groups=1000(coletor)
```

## Gate de segurança S1–S21

| Item | Status | Evidência | Correção |
|---|---|---|---|
| S1 segredos | ✅ | `gitleaks`: no leaks found; `.gitignore:16-24` cobre `.env`, `*.key`, `*.pem`, `service-account*.json`; `.env.example` só com identificadores | — |
| S2 validação de entrada | ✅ | `src/cli.py:28-31` — `choices` restringe ambiente a dev/hml/prod | — |
| S3 SQL | ✅ | `pyproject.toml:18` — regra `S` do ruff ativa, `S608` (SQL por interpolação) **não** está em `ignore` | — |
| S4–S10 senhas, JWT, cookies, logout, IDOR, CSRF, rate limiting de sessão | N/A | Painel público e anônimo, sem cadastro (RF-01) e sem endpoint de escrita exposto | — |
| S11 headers/CORS/HTTPS | N/A nesta task | Não há superfície HTTP ainda; entra na task 22 com a publicação | — |
| S12 menor privilégio | ✅ | `Dockerfile:34-35` — container roda como `coletor` (uid 1000), não root; `infra/cloudbuild.yaml:44` — SA por ambiente | — |
| S13 upload | N/A | Não há upload de usuário | — |
| S14 dependências/CI | ✅ | `requirements.lock.txt` com 77 pacotes travados; CI obrigatório em PR e push (`ci.yml:8-11`) | — |
| S15 tratamento de erro | ⚠️ | `src/cli.py` ainda não tem exceções específicas — o módulo de erro é entregável da task 06 | Fecha na task 06 (`ColetaBloqueadaError`, `ValidacaoError`, `FonteIndisponivelError`) |
| S16 Electron · S17 fail2ban · S18 WAF | N/A | Sem app desktop e sem VPS — infraestrutura serverless gerenciada | — |
| S19 Trivy | ✅ | `ci.yml:53-60` — scan da imagem, `CRITICAL,HIGH`, `exit-code: 1` | Rodará no primeiro PR |
| S20 dependency confusion | ✅ | `Dockerfile:22` e `ci.yml:25` — `--index-url https://pypi.org/simple` explícito, nenhum índice extra | — |
| S21 API keys | ✅ | Nenhuma credencial no repositório; chaves vão para o Secret Manager (`.env.example:3-4`) | — |

**Nenhum ❌.** O único ⚠️ (S15) é entregável declarado de outra task, não pendência desta.

## Onde parei

**Retomada e concluída em 21/10/2026 (task 34).** O texto abaixo é o registro do bloqueio anterior.

**Bloqueada, aguardando conta GitHub do projeto.**

Passos 1, 3, 4, 5 e 7 fechados e commitados localmente (3 commits, branches
`main` e `hml`). Faltam os passos 2 e 6.

O que aconteceu: o repositório chegou a ser criado na conta pessoal
(`brunovima83/painel-to-em-dados`) e recebeu push, antes de ficar decidido que o
projeto teria **conta GitHub própria**. O repositório foi excluído e o remote
`origin` removido do clone local. **Nada se perdeu** — o histórico completo está
nos 3 commits locais.

### Para retomar
1. Criar a conta GitHub do projeto. **Evitar "gov" no nome de usuário**: o dono
   aparece na URL de todo link do painel, e um usuário tipo `dadosgovtocantins`
   reproduziria o risco RR-05 que o projeto inteiro existe para evitar. O mesmo
   critério do e-mail de contato (PRD §2.3) vale aqui.
2. Autenticar (`gh auth login` com a conta nova, ou um segundo perfil).
3. Criar o repositório público e apontar o clone local para ele:
   ```bash
   git remote add origin https://github.com/<conta-nova>/<repo>.git
   git push -u origin main && git push origin hml
   ```
4. Passo 2: proteger a branch `main` (PR obrigatório + CI verde).
5. Passo 6: PR de teste com chave falsa, provando que o CI barra segredo.
6. Atualizar em `docs/runbook.md` a URL do repositório e, quando existir, a do
   Artifact Registry.

### Pendência de decisão
A conta GitHub do projeto entra na lista de custódia da task 02 (RT-14): é mais
um ponto único de falha, e precisa de 2FA, recuperação configurada e registro no
runbook — mesmo tratamento da conta-projeto do GCP.

## Decisões tomadas

- **Licença MIT**, não Apache-2.0. O PRD pede "permissiva"; MIT é a mais curta e
  a mais reconhecida em projeto acadêmico. Apache-2.0 só valeria a pena pela
  cláusula de patente, irrelevante aqui.
- **`.claude/` e `CLAUDE.md` fora do versionamento.** São configuração da
  ferramenta de agente (ruflo/claude-flow), não do produto: 200+ arquivos que
  poluiriam um repositório público e poderiam expor configuração local. O
  primeiro commit os incluiu por engano e foi corrigido com `git rm --cached`.
- **`ruvector.db`, `.swarm/` e `.agents/` no `.gitignore`** pelo mesmo motivo,
  com um agravante: são bases de estado de sessão de agente e o repositório é
  público.
- **Playwright fora da imagem base.** O PRD prevê o browser só para scraping
  complexo, e o Gate 1 pode reprovar — nesse caso o Playwright nunca é usado.
  Manter o browser na imagem base custaria ~400 MB e segundos de boot em **todo**
  coletor federal, o que consome vCPU-s da franquia gratuita sem contrapartida.
  A imagem base leva PySUS (usado pelo bloco Saúde, task 14); o container de
  scraping vira `Dockerfile.scraping` na task 18.
- **Dependências travadas em `requirements.lock.txt`** (`pip freeze` de um venv
  limpo, só runtime). Docker e CI instalam do lock, não do `requirements.txt`
  — é o que dá reprodutibilidade e fecha S14/S20.
- **`pythonpath = ["."]` no `pyproject.toml`** em vez de empacotar `src` ou usar
  `conftest.py` com `sys.path`: uma linha resolve, e o projeto não é distribuído
  como biblioteca.
- **Teste de não-oficialidade desde o primeiro commit** (`tests/test_nao_oficialidade.py`).
  RR-05 é o maior risco do projeto e a regra que o mitiga é texto — texto quebra
  em silêncio. O CI passa a barrar a remoção do aviso.
- **Retomada (21/10/2026, task 34):** a conta GitHub do projeto é `dadosgovtocantins`; o Bruno manteve o nome sabendo do risco RR-05 que esta spec apontava (o endereço público do painel terá o nome da conta). O repositório do código ficou **privado** e o site público será um repositório separado (design 33). O histórico foi refeito em um commit inicial limpo.
- **Dockerfile:** o critério "builda e roda `pytest` no build" valia em setembro; com a suíte atual o build falha (o `pytest` do build só enxerga `src/`, `tests/` e o README, e os testes precisam de `scripts/`, `docs/` e `index.html`). O `imagem.yml` ficou só manual até o Cloud Run voltar a ser usado.
- **Pendência de custódia (RT-14):** a conta `dadosgovtocantins` do GitHub precisa de 2FA, recuperação configurada e registro no runbook, como a conta-projeto do GCP (task 02).
