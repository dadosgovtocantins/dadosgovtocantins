# Painel TO em Dados

**Painel de Business Intelligence para Consolidação e Monitoramento de
Indicadores de Políticas Públicas do Estado do Tocantins**

> ⚠️ **Este não é um canal oficial do Governo do Tocantins.**
> Projeto acadêmico de extensão universitária (PIBIEX / TO Graduado / Unitins).
> Os dados são reproduzidos de fontes públicas, sempre com indicação de origem
> e link para o dado original. O projeto não tem vínculo institucional com o
> Governo do Estado do Tocantins e não utiliza seus símbolos oficiais.

**Painel público:** https://dadosgovtocantins.github.io/painel/ (atualizado todo dia às 14h, horário de Brasília; o
rodapé mostra quando as fontes foram verificadas pela última vez e a situação de cada uma).

---

## O que é

Portal público de leitura que consolida indicadores de políticas públicas do
Tocantins em três níveis de navegação:

| Tela | Cobertura |
|---|---|
| **Município** | os 139 municípios, com paridade entre capital e municípios pequenos |
| **Estado** | indicadores estaduais agregados |
| **Órgão** | 11 órgãos: indicadores, catálogo de fontes e índice de maturidade de dados abertos |

A base é um catálogo de **40 fontes públicas**, das quais ≥18 com coleta
automatizada. O painel **mede o território, não a gestão**: a maior parte dos
dados vem de fontes federais (IBGE, INEP, DATASUS, SICONFI, Transferegov).

## O que o projeto produz além do painel

1. **Índice de maturidade de dados abertos por órgão** — quanto do que cada
   órgão publica é efetivamente reutilizável por um sistema, e não apenas
   legível por uma pessoa.
2. **Catálogo de 40 fontes** com classificação metodológica documentada,
   publicado como recurso aberto.
3. **Metodologia replicável** — 16 das fontes automatizáveis são federais e
   seguem o mesmo padrão de acesso para qualquer unidade da federação.

## Dois cuidados metodológicos

- **`sem_dado` ≠ `0`.** Fontes declaratórias omitem entes que não responderam.
  Exibir essa ausência como zero é factualmente errado e penaliza municípios que
  apenas não enviaram o dado. O modelo carrega essa distinção até a tela.
- **A IA não calcula valor.** O Gemini é usado para estruturar texto (HTML/PDF)
  e gerar resumo narrativo rotulado. Todo número vem da fonte primária.

## Stack

Google Sheets (catálogo) · Python 3.11 em Cloud Run Jobs (ingestão) ·
Cloud Storage (zona bruta imutável) · BigQuery (warehouse) ·
Looker Studio (visualização) · Gemini via AI Studio (parsing e narrativa)

**Custo de operação: R$ 0.** Tudo roda no nível gratuito do Google — nenhum
serviço fora da franquia é habilitado.

## Como navegar este repositório

| Pasta | O que tem |
|---|---|
| [`.planning/`](.planning/) | Especificações (SDD) e o framework de execução (GSD) |
| `src/coletor_base/` | Framework de coleta: hash, validação, idempotência, conformidade |
| `src/coletores/` | Um coletor por fonte, nomeado pelo ID do catálogo |
| `src/sql/` | DDL, normalização e agregados de consumo |
| `infra/` | Provisionamento, CI/CD, agendamento |
| `docs/` | Runbook, dicionário de dados, metodologia |

Comece por [`.planning/01_system_prompt.md`](.planning/01_system_prompt.md)
(regras do projeto) e [`.planning/ROADMAP.md`](.planning/ROADMAP.md) (estado atual).

## Desenvolvimento

```bash
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
ruff check src tests && pytest -q
```

## Conformidade de coleta

Toda fonte tem `robots.txt` e termos de uso verificados e datados no catálogo.
Fonte com restrição registrada **não é coletada** — o coletor falha por design.
Fontes bloqueadas entram no painel como link para consulta, nunca como dado
ingerido. Todo acesso usa rate limit auto-imposto e User-agent identificando o
projeto, a instituição e um canal de contato.

## Licença

[MIT](LICENSE). Os dados reproduzidos permanecem sob a licença de suas fontes
primárias, citadas em cada card e em cada export.
