# Runbook operacional — Painel TO em Dados

> Documento de operação. Quem assumir o projeto (novo bolsista, Unitins ou
> órgão) opera a partir daqui. Mitigação direta de **RT-09** (conhecimento
> concentrado em uma pessoa).

## Estado deste runbook

| Seção | Task que preenche | Status |
|---|---|---|
| Deploy e rollback | 03 | ✅ preenchida |
| Identificadores do projeto GCP | 02 | ⏳ pendente |
| Custódia de credenciais e recuperação de conta | 02 | ⏳ pendente |
| Transferência de titularidade | 02 | ⏳ pendente |
| Serviços ativos e franquia gratuita de cada um | 02 | ⏳ pendente |
| Operação dos coletores (reexecutar, reprocessar) | 06 / 08 / 35 | ✅ atualização diária e coleta forçada (abaixo) |
| Painel público (GitHub Pages) | 36 | ✅ preenchida; publicação ligada só depois de criar o repositório e o token |
| Restauração de backup | 24 | ⏳ pendente |

---

## Deploy

### Fluxo
```
feature/*  --PR-->  main (prod)        CI verde é obrigatório para o merge
                     |
   push em `hml`  ---+--->  Cloud Build  --->  Cloud Run Job coletor-hml
   tag v*         ------->  Cloud Build  --->  Cloud Run Job coletor-prod
```

**Regra que não se contorna:** nenhum coletor chega a PROD sem ter rodado em
HML. A tag de produção só é criada a partir de um commit que já rodou em
homologação com dado real.

### Subir para homologação
```bash
git checkout hml && git merge --ff-only <commit já em main>
git push origin hml          # dispara o Cloud Build para HML
```

### Subir para produção
```bash
git tag -a v0.1.0 -m "<o que entra>"
git push origin v0.1.0       # dispara o Cloud Build para PROD
```

### Rollback
A imagem anterior continua no Artifact Registry. Rollback é apontar o job para
a tag anterior — não é rebuild, não é revert de código:
```bash
gcloud run jobs update coletor-prod \
  --image=<REGIAO>-docker.pkg.dev/<PROJETO>/painel-to/painel-to:<SHA_ANTERIOR> \
  --region=<REGIAO>
```
Depois do rollback: abrir issue com o que quebrou **antes** de tentar corrigir.
O registro é o que evita repetir o mesmo erro em 3 meses.

### Se o CI barrar por segredo detectado
1. **Não force o push.** O segredo já vazou se o push chegou ao GitHub.
2. Revogue/rotacione a credencial **primeiro** — remover do histórico não
   desvaza nada.
3. Só então limpe o histórico e recommite.

---

## Atualização diária das fontes (task 35)

O workflow **Verificar fontes** (`verificar.yml`) roda todo dia às 14h de Brasília: consulta a sentinela de cada
fonte, coleta só o que tem novidade, valida e commita `src/ui/data/estado_fontes.json` (sempre) e
`painel_dados.json` (só com dado novo aceito). O commit do robô leva `[skip ci]`.

- **Ver a situação:** `src/ui/data/estado_fontes.json` (status por fonte: `ok`, `erro`, `defasado`, `suspeito`).
- **Forçar uma coleta:** Actions > Verificar fontes > Run workflow, campo `forcar` = `TO-TER-04` (ids separados por
  vírgula) ou `todas` (≈ 26 min). Qualquer outro valor é recusado.
- **Fonte com erro:** após 2 falhas seguidas (ou `defasado`) abre uma issue `[ID] fonte com problema` e ela fecha
  sozinha quando a fonte volta a `ok`. O painel continua mostrando o último dado válido.
- **Dado `suspeito`:** variação fora de 3σ e acima do piso (10%, 10% e 6 p.p.): o dado novo NÃO é publicado.
  Se for legítimo, conferir na fonte oficial; a regra está em `src/orquestracao/validacao.py`.
- **Local:** `python scripts/atualizar.py [--forcar ...]`; `python scripts/backtest_3sigma.py` refaz o backtest.

## Painel público (task 36)

O site público é um **segundo repositório, só com o site** (`dadosgovtocantins/painel`, GitHub Pages, endereço
`https://dadosgovtocantins.github.io/painel/`). O código e a coleta ficam no repositório privado.

**Montagem.** `python scripts/montar_site.py --saida <pasta>` copia só a lista fixa de `src/orquestracao/site.py`
(nada fora dela), confere dados, segredos, o padrão do e-mail de infraestrutura e endereços externos, e sincroniza a
pasta (só muda o que mudou; `.git` intacto). Para o site incluir um arquivo novo, ele precisa entrar na lista.

**Publicação.** O último passo do `verificar.yml` roda `scripts/publicar_site.sh`: clona o repositório público,
monta o site nele e commita só se houver diferença (normalmente só o `estado_fontes.json`). Sem
`PAT_PUBLICACAO_PAINEL` o passo termina verde dizendo "Publicação desligada".

**Ligar a publicação (uma vez, feito pelo Bruno):**
1. Criar o repositório público `dadosgovtocantins/painel` (vazio, sem README) e ativar Pages: Settings > Pages >
   Deploy from a branch > `main` / `/ (root)`.
2. Criar um token **fine-grained** (Settings > Developer settings): só o repositório `painel`, permissão
   **Contents: Read and write**, sem nenhuma outra; validade com data (renovar antes de vencer).
3. No repositório **privado**: Settings > Secrets and variables > Actions > New repository secret
   `PAT_PUBLICACAO_PAINEL` = o token. O segredo `PADRAO_EMAIL_INFRA` já existe e é exigido pela publicação.
4. Disparar **Verificar fontes** à mão e abrir o endereço do painel.

**Reverter uma publicação ruim:** nunca `--force`. No repositório público, `git revert <commit>` e push; o site volta
ao estado anterior no próximo build do Pages (1 a 2 min). Para tirar o painel do ar: apagar o segredo
`PAT_PUBLICACAO_PAINEL` (para de publicar) e, se preciso, desativar Pages no repositório público.

**Trocar/revogar o token:** gerar outro, atualizar o segredo e revogar o antigo na conta do projeto.

---

## Verificações locais antes de abrir PR

```bash
source .venv/bin/activate
ruff check src tests && ruff format --check src tests
pytest -q
docker build -t painel-to:dev .
docker run --rm -v "$PWD":/repo zricethezav/gitleaks:latest detect --source /repo --redact
```

---

## Contatos e papéis

| Papel | Quem | Observação |
|---|---|---|
| Executor / bolsista | Bruno Vieira de Melo Aguiar | P4 — operação |
| Conta-projeto (owner) | e-mail guardado fora do repositório, com o Bruno | P5 — **uso interno, nunca exibida ao público** |
| Orientador PIBIEX | a definir (questão 1) | aprova publicação (Gate 2) |
| Contato público do painel | a definir (questão 2) | **≠ conta-projeto**, sem a partícula "gov" |
