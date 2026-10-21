# Regras do projeto — Painel TO em Dados

> Nome oficial: **Painel de Business Intelligence para Consolidação e
> Monitoramento de Indicadores de Políticas Públicas do Estado do Tocantins**
> Fonte de verdade do escopo: `PRD_Painel_Dados_Tocantins.md` (v4.2).
> Em caso de conflito entre este arquivo e o PRD, **o PRD ganha** — e este
> arquivo é corrigido no mesmo dia.

## O que é

Portal público de leitura que consolida indicadores de políticas públicas do
Tocantins em três níveis de navegação — **Município (139) → Estado → Órgão (11)**
— a partir de 40 fontes catalogadas, das quais ≥18 com coleta automatizada.
É um **projeto de extensão universitária** (PIBIEX / TO Graduado / Unitins),
executado por um bolsista, **sem vínculo com o Governo do Tocantins**.
Público-alvo: cidadãos, jornalistas, vereadores, conselhos municipais,
pesquisadores e órgãos de controle (TCE-TO, CGE-TO).

Duas frases que definem tudo o mais:
1. **O painel mede o território, não a gestão.** Nenhuma fonte estadual é
   automatizável (RT-10); os dados vêm majoritariamente de fontes federais.
2. **O teto de custo é R$ 0, por construção.** Tudo roda no **nível gratuito do
   Google** — BigQuery, Cloud Run, Storage, Scheduler, Logging, Sheets, Apps
   Script, Looker Studio e Gemini via AI Studio. Nenhum serviço fora da franquia
   é habilitado. Onde elegância técnica conflitar com a franquia gratuita,
   **a franquia vence** (decisão arquitetural 4 do PRD); serviço que ameaça sair
   da franquia é substituído ou recortado, **nunca pago** (RF-95).

## Stack

| Camada | Tecnologia |
|---|---|
| Catálogo / config | Google Sheets + Apps Script (tabela externa no BigQuery) |
| Ingestão | Python 3.11 em Cloud Run Jobs |
| Scraping | Playwright em container Cloud Run |
| DATASUS | PySUS / FTP público (DBC → DBF → CSV) |
| Orquestração | Cloud Scheduler |
| Zona bruta | Cloud Storage (imutável, hash SHA-256) |
| Warehouse | BigQuery particionado + clusterizado |
| Visualização | Looker Studio (embed público, Extract Data) |
| IA | Gemini via AI Studio — **parsing e narrativa, nunca cálculo** |
| Segredos | Secret Manager |
| CI/CD | GitHub (público) + Cloud Build |
| Observabilidade | Cloud Logging + Monitoring + Error Reporting |

## Comandos

> Definidos na task `03_task_repo_ci_cd.md`. Até ela fechar, são o alvo, não o
> estado atual.

| Ação | Comando |
|---|---|
| Ambiente | `python3.11 -m venv .venv && source .venv/bin/activate && pip install -r requirements-dev.txt` |
| Rodar um coletor local | `python -m src.cli coletar --fonte <ID_FONTE> --ambiente dev` |
| Testes | `pytest -q` |
| Testes + cobertura | `pytest --cov=src --cov-report=term-missing` |
| Lint / format | `ruff check src tests && ruff format --check src tests` |
| Scan de segredos | `gitleaks detect --no-git --redact` |
| Build da imagem | `docker build -t painel-to:dev .` |
| Dry-run de custo de query | `bq query --dry_run --use_legacy_sql=false < src/sql/<arquivo>.sql` |
| Provisionar infra do zero | `bash infra/provision.sh <ambiente>` |

## Estrutura de pastas

```
.planning/          # SDD: GSD, regras, roadmap e specs de task. VAI PRO GIT.
src/
  coletor_base/     # framework: extrair/transformar/executar, hash, validação, guarda robots
  coletores/        # 1 subclasse por fonte, ~40 linhas cada (RNF-E02). Nome = ID do catálogo
  catalogo/         # leitura do Sheets e das tabelas externas
  sql/
    ddl/            # fato_indicador, dimensões
    stg/            # normalização (encoding, código IBGE)
    mart/           # agregados que o Looker consome — e SÓ isso ele consome
  cli.py            # entrypoint dos Cloud Run Jobs
tests/              # espelha src/; fixtures de payload real em tests/fixtures/
infra/              # provision.sh, cloudbuild.yaml, Dockerfile, schedulers
docs/
  runbook.md        # operação, recuperação, transferência de titularidade
  dicionario.md     # dicionário de dados
  metodologia.md    # critério A–D e Q1/Q2 — publicado no painel (RF-14)
  demos/            # 1 registro por sprint (GSD §3)
```

## Convenções deste projeto

- **Nomenclatura:** Python em `snake_case`, pt-BR no domínio (`coletar`,
  `transformar`, `municipio`, `periodo_ref`), inglês só onde a linguagem exige.
  Nome do arquivo do coletor = ID da fonte no catálogo, minúsculo
  (`TO-TER-01` → `to_ter_01.py`). Isso é a rastreabilidade catálogo ↔ código.
- **Padrão de coletor:** herda de `ColetorBase`, implementa só `extrair()` e
  `transformar()`. Se precisar sobrescrever `executar()`, é sinal de que o
  framework está errado — **conserta o framework, não o coletor**.
- **Catálogo antes de código:** nenhum coletor é escrito antes da linha existir
  em `catalogo_indicadores` com `status = homologacao` (RF-82).
- **Tratamento de erro:** exceção específica (`ColetaBloqueadaError`,
  `ValidacaoError`, `FonteIndisponivelError`), nunca `except Exception: pass`.
  Falha de coleta preserva o último valor válido com `qualidade='defasado'` —
  **nunca grava zero por falha** (RF-66).
- **Log:** JSON estruturado por execução com os 10 campos da seção 11.3 do PRD,
  emitido em stdout (é o canal que o Cloud Run coleta) **pelo módulo
  `src/coletor_base/log.py`**. Nunca `print()` de texto livre, nunca log fora
  desse módulo.
- **Testes:** em `tests/`, espelhando `src/`. Todo coletor tem teste com payload
  real gravado em `tests/fixtures/` — nunca bate na rede durante o teste.
- **SQL:** cliente oficial + parâmetros. `maximum_bytes_billed` em **toda**
  query, sem exceção.
- **Commits:** `<task NN>: <o que fechou>`. Um por bloco de trabalho, no mínimo.

## O que NUNCA fazer neste projeto

**Institucional / reputacional** (risco RR-05 — o mais caro do projeto)
- Nunca usar brasão, marca, paleta institucional do Governo do TO ou foto de
  agente público na interface (RNF-S08).
- Nunca omitir o aviso de não-oficialidade de qualquer tela (RF-10).
- Nunca expor o e-mail da conta de infraestrutura (guardado fora do repositório, com o Bruno) ao público — é conta de
  infraestrutura. Contato público, rodapé e User-agent usam endereço distinto,
  sem a partícula "gov".
- Nunca apresentar o índice de maturidade (RF-43) como ranking de "quem é
  transparente". É diagnóstico metodológico (RR-06).

**Dado**
- Nunca gravar **zero** quando o dado é ausente. `sem_dado` ≠ `falho` ≠ `0`
  (RF-55, RT-11). É uma das inovações declaradas do projeto.
- Nunca deixar a IA calcular valor. Gemini estrutura texto; número vem da fonte
  (RF-70, RT-06).
- Nunca publicar indicador calculado sem fórmula na ficha e `calculado = TRUE`.
- Nunca usar chave de município que não seja o **código IBGE de 7 dígitos**.
- Nunca ingerir fonte com robots.txt/termos restritivos — o coletor **falha por
  design** (RF-71). Fonte bloqueada entra como link, não como dado.
- Nunca ingerir microdado ou dado pessoal, isolado ou combinável (RNF-S05).
- Nunca publicar valor com `qualidade = 'suspeito'` (variação > 3σ) sem revisão.

**Custo** (teto de R$ 0 é restrição, não meta — tudo no gratuito do Google)
- Nunca rodar query sem `maximum_bytes_billed`.
- Nunca apontar o Looker para a tabela fato bruta — só agregados de `ds_mart`,
  com Extract Data ligado.
- Nunca criar recurso sem labels `projeto`, `ambiente`, `modulo`.
- Nunca habilitar serviço, região ou recurso que esteja fora do nível gratuito
  sem registrar a decisão e a alternativa gratuita descartada.

**Operação**
- Nunca escrever manualmente em PROD. Escrita em produção é exclusiva das
  Service Accounts do pipeline.
- Nunca subir coletor para PROD sem passar por HML.
- Nunca commitar credencial — repositório é público, o scan de segredos no CI é
  requisito, não precaução.
- Nunca fazer merge em `main` sem PR com CI verde.

## Ambiente e segredos

| Item | Onde |
|---|---|
| Conta-projeto (uso interno, nunca exibida) | e-mail guardado fora do repositório, com o Bruno — 2FA obrigatório |
| Projeto GCP | ID estável definido na task 02 — **imutável após criação** |
| Ambientes | `dev_*` (amostra) · `hml_*` (dado real, não publicado) · `ds_*` (produção) |
| Segredos | Secret Manager. Rotação semestral. Zero credencial em código, em `.env` versionado ou no Sheets |
| Config local | `.env.local` (no `.gitignore`), apenas com IDs não sensíveis |
| Service Accounts | Uma por ambiente, menor privilégio, **sem chave JSON baixada** — usa Workload Identity / impersonation |

## Gate de segurança

Toda task que toca coleta, credencial, endpoint, dado publicado ou deploy fecha
com o checklist **S1–S21** da `/secure-by-default-webdev`, reportado na tabela
`Item | Status | Evidência (arquivo:linha) | Correção`. **Nenhum ❌ sobe.**

Itens mais recorrentes neste projeto, pelo nome (a numeração canônica é a da
skill; cite sempre nome + número):
S1 segredos · S2 validação de entrada · S3 SQL · S11 headers/CORS/HTTPS ·
S12 menor privilégio · S14 dependências/CI · S15 tratamento de erro ·
S19 Trivy · S20 dependency confusion · S21 API keys.

Itens estruturalmente **N/A** aqui, e o motivo (escreva sempre o motivo, nunca
deixe em branco): S4–S10 (senhas, JWT, cookies, logout, IDOR, CSRF, rate
limiting de sessão) — o painel é **público e anônimo, sem cadastro** (RF-01) e
**sem endpoint de escrita exposto**. S13 upload — não há upload de usuário.
S16 Electron, S17 fail2ban, S18 WAF — não há VPS nem app desktop; a
infraestrutura é serverless gerenciada.
