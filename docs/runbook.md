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
| Operação dos coletores (reexecutar, reprocessar) | 06 / 08 | ⏳ pendente |
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
