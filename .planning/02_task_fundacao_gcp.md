---
task: Fundação GCP — conta, projeto, datasets, buckets e teto de custo
status: pendente
sprint: S1
eap: 1.1.2, 1.1.3
---

# Fundação GCP

## Objetivo
Provisionar a conta-projeto, o projeto GCP e a infraestrutura base (datasets,
buckets, service accounts, budget) com o teto de custo de R$ 0 travado **antes**
de qualquer dado entrar.

## Por quê
Tudo depende disso e nada pode ser refeito depois: o ID do projeto é imutável,
e o budget alert precisa existir **antes** da primeira query, não depois da
primeira fatura. Além disso, a conta é hoje o ponto único de falha do projeto
(RT-14, impacto **Crítico**) — perder o acesso é perder BigQuery, buckets,
agendamentos e o painel de uma vez.

## Arquivos envolvidos
| Arquivo | O que muda |
|---|---|
| `infra/provision.sh` | criar — provisionamento idempotente de datasets, buckets, SAs, labels |
| `infra/budget.yaml` | criar — definição do budget alert |
| `infra/iam.md` | criar — matriz SA × papel × ambiente |
| `docs/runbook.md` | criar — IDs, custódia, recuperação, transferência de titularidade |
| `.env.example` | criar — só IDs não sensíveis |

## Critérios de aceite
- [ ] 2FA ativo na conta-projeto, com telefone **e** e-mail de
      recuperação distintos configurados — print no runbook
- [ ] Projeto GCP criado com ID estável; ID registrado em `docs/runbook.md`
      (imutável — conferir a grafia **antes** de confirmar)
- [ ] **Decisão de faturamento registrada no runbook**, entre as duas formas de
      operar 100% no gratuito, com os limites vigentes conferidos na página
      oficial do GCP (mudam — não assumir de memória):
      **(a) BigQuery Sandbox**, sem meio de pagamento — zero risco financeiro, mas
      com limites de armazenamento/consulta e **expiração automática de tabelas**,
      o que conflita com o histórico exigido pelo PRD; ou
      **(b) faturamento habilitado** apenas para destravar Cloud Run e Scheduler,
      com budget alert de teto simbólico — o cartão existe para desbloquear
      serviço, **não para gastar**
- [ ] Se (b): **budget alert ativo antes de qualquer outro recurso**, com
      notificações em 50%, 80% e 100% — `gcloud billing budgets list` como evidência
- [ ] Nenhum serviço fora do nível gratuito habilitado; lista dos serviços ativos
      e da franquia de cada um registrada em `docs/runbook.md`
- [ ] 9 datasets existem: `dev_raw/stg/mart`, `hml_raw/stg/mart`, `ds_raw/stg/mart`
      — `bq ls --project_id=<proj>` lista os 9
- [ ] 2 buckets: `<proj>-raw` com versionamento + lifecycle (Nearline 90d,
      Coldline 365d) e `<proj>-backup` — `gsutil lifecycle get` como evidência
- [ ] 3 service accounts (`sa-coletor-dev`, `-hml`, `-prod`) com papéis mínimos
      documentados em `infra/iam.md`; **nenhuma chave JSON baixada**
- [ ] Nenhuma SA tem papel `Editor` ou `Owner` — `gcloud projects get-iam-policy`
      comprova
- [ ] Secret Manager habilitado; nenhum segredo em texto plano em lugar nenhum
- [ ] Todo recurso criado carrega os labels `projeto`, `ambiente`, `modulo`
- [ ] `bash infra/provision.sh dev` roda 2x seguidas sem erro e sem duplicar
      recurso (idempotência)
- [ ] `docs/runbook.md` contém: IDs, onde estão as credenciais, procedimento de
      recuperação de conta e **procedimento de transferência de titularidade**
- [ ] Créditos e franquias vigentes verificados na página oficial do GCP e o
      resultado registrado no runbook (valores mudam — não assumir)
- [ ] Orientador informado da existência da conta-projeto (registro por e-mail)

## Fora de escopo
- Migração para `@unitins.br` (opção C) — negociada em paralelo, não bloqueia
- Cloud Run, Cloud Scheduler, Cloud Build — tasks 03 e 06
- Criação das tabelas (DDL) — task 07

## Plano
- [ ] 1. Ativar 2FA e recuperação na conta-projeto; registrar a custódia
- [ ] 2. Criar o projeto GCP com ID estável e ativar as APIs necessárias
- [ ] 3. Conferir os limites gratuitos vigentes, decidir entre Sandbox e
      faturamento com budget, registrar a decisão — e, se houver faturamento,
      criar o budget alert **antes de qualquer outro recurso**
- [ ] 4. Escrever `infra/provision.sh` (datasets, buckets, lifecycle, labels)
- [ ] 5. Criar as 3 SAs e escrever a matriz de papéis em `infra/iam.md`
- [ ] 6. Rodar `provision.sh` 2x em dev e provar idempotência
- [ ] 7. Escrever `docs/runbook.md` com IDs, custódia, recuperação e transferência
- [ ] 8. Verificar créditos vigentes e perguntar à coordenação sobre Workspace Unitins (questão 3)

## Segurança
Gate S1–S21 aplicável: **S1 segredos** (nada em texto plano, Secret Manager ativo),
**S12 menor privilégio** (SAs sem Editor/Owner, uma por ambiente),
**S21 API keys** (nenhuma chave JSON baixada; impersonation/Workload Identity),
**S14 dependências/CI** (N/A nesta task — entra na 03).
Demais itens N/A com o motivo escrito na tabela de fechamento.

Mitigação explícita de **RT-14**: 2FA + recuperação dupla + custódia documentada
+ runbook de transferência desde o primeiro dia.

## Verificação
```bash
gcloud config get-value project
gcloud billing budgets list --billing-account=<ID>
bq ls --project_id=<proj>
gsutil ls -L -b gs://<proj>-raw | grep -i -E "lifecycle|versioning"
gcloud projects get-iam-policy <proj> --format=json | grep -E "roles/(editor|owner)"   # deve ser vazio para SAs
bash infra/provision.sh dev && bash infra/provision.sh dev
```

## Decisões tomadas
<preenchido durante a execução>
