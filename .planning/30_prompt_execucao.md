# Prompt de execução — Task 30 (Coletor de Titulares Eleitos)

> Cole este prompt inteiro em uma nova sessão do Claude Code, já dentro do
> repositório `DADOS GOV` (raiz onde está `.planning/`). Ele é autossuficiente:
> não depende do histórico da conversa onde foi gerado.

---

Execute a task `.planning/30_task_coletor_titulares.md` deste repositório,
seguindo a skill `sdd-planning` (Fase 2 — Executar) e o `01_system_prompt.md`
em `.planning/`.

## Contexto que você precisa saber antes de começar

1. **O que é esta task:** criar dois coletores de dados — `TO-GER-01` (nome e
   situação de eleito de prefeitos/governador via Dados Abertos do TSE) e
   `TO-GER-02` (retrato de identificação do titular via DivulgaCandContas REST
   do TSE) — e carregar os dois num novo dimensão `dim_titular` no BigQuery.

2. **Por que existe uma exceção de regra de negócio aqui:** o PRD deste
   projeto (`docs/PRD_Painel_Dados_Tocantins.md`, RF-11/RNF-S08) proíbe foto
   de agente público na interface, para não ser confundido com canal oficial
   do governo. Essa task abre uma **exceção estreita**, já registrada e
   aprovada em 2026-10-14 no próprio PRD (seção 0.1) e em `docs/identidade.md`:
   só o retrato de identificação do titular eleito (prefeito/governador) pode
   ser coletado/exibido, sempre com fonte citada, nunca como peça de marca do
   painel, e nunca acompanhado de brasão/paleta de governo. **Não reabra essa
   discussão** — ela já foi decidida; seu trabalho é implementar dentro dos
   limites já escritos nesses dois arquivos.

3. **Pré-requisito que pode estar pendente:** o passo 1 do plano da task
   exige cadastrar `TO-GER-01` e `TO-GER-02` no catálogo (Google Sheets,
   aba `catalogo_fontes` e `catalogo_indicadores`) com `status = homologacao`,
   antes de escrever código (convenção RF-82 do projeto). **Pergunte ao Bruno
   se isso já foi feito.** Se não foi feito e ele não tiver acesso imediato ao
   Sheets, pergunte como prosseguir — não assuma que pode pular a trava
   silenciosamente.

## O que fazer

1. Leia `.planning/01_system_prompt.md` e `.planning/30_task_coletor_titulares.md`
   inteiros antes de tocar em qualquer código.
2. Mude o front-matter da task de `status: pendente` para `status: em andamento`.
3. Siga o `## Plano` da task passo a passo, marcando `[x]` em
   `.planning/30_task_coletor_titulares.md` a cada passo concluído (não no
   final — a cada passo).
4. Convenções obrigatórias deste projeto (não negocie com elas):
   - Coletor herda `ColetorBase` (`src/coletor_base/base.py`), implementa só
     `extrair()` e `transformar()`. Se sentir vontade de sobrescrever
     `executar()`, é sinal de que o framework está errado — pare e avise, não
     sobrescreva.
   - Use `ClienteHTTP` de `src/coletor_base/http.py` para as requisições —
     já tem User-Agent identificado, rate limit e retry. Não crie outro
     cliente HTTP.
   - Nome do arquivo do coletor = ID da fonte em minúsculo: `TO-GER-01` →
     `to_ger_01.py`, `TO-GER-02` → `to_ger_02.py`, em `src/coletores/`.
   - Teste e fixture seguem o padrão já em uso (veja
     `tests/coletores/test_bloco_recursos.py` e
     `tests/fixtures/recursos_payloads.py` como referência de formato) — crie
     `tests/coletores/test_bloco_governanca.py` e
     `tests/fixtures/governanca_payloads.py`. Teste nunca bate na rede: payload
     real gravado como fixture.
   - Falha de extração preserva o último valor válido com
     `qualidade='defasado'` — nunca grava nulo/zero por falha. Isso já é
     tratado pelo `ColetorBase.executar()`; não precisa reimplementar, só não
     quebrar esse contrato.
   - Exceção específica em erro (`FonteIndisponivelError` já existe em
     `src/coletor_base/excecoes.py`), nunca `except Exception: pass`.
   - `id_municipio` é sempre o código IBGE de 7 dígitos (ver
     `src/sql/ddl/dim_municipio.sql` para a lista canônica dos 139 municípios).
     Para o governador, `id_municipio` é `NULL` (nível estadual).
   - Toda query de carga usa `MERGE` parametrizado — nunca concatenação de
     string — e `maximum_bytes_billed` em toda query.
   - Checagem de conformidade (`checar_conformidade_coleta`, já existe em
     `src/coletor_base/conformidade.py`) roda antes de qualquer requisição de
     rede, para as duas fontes (`divulgacandcontas.tse.jus.br` e
     `dadosabertos.tse.jus.br`).
5. Para o DDL (`src/sql/ddl/dim_titular.sql`), siga o estilo de
   `src/sql/ddl/dim_municipio.sql` e `src/sql/ddl/dim_orgao.sql`: comentário de
   cabeçalho explicando a chave canônica, `CREATE TABLE IF NOT EXISTS`, colunas
   com `OPTIONS(description=...)`. Colunas mínimas exigidas pelos critérios de
   aceite da task: `id_titular`, `id_municipio` (NULL permitido), `cargo`
   (`PREFEITO`|`GOVERNADOR`), `nome_titular`, `url_foto`, `fonte`
   (`TSE`|`DIVULGACANDCONTAS`), `hash_origem`, `atualizado_em`.
6. Toda decisão não-óbvia que você tomar durante a implementação (ex: formato
   exato do endpoint do DivulgaCandContas, se a foto é gravada como URL ou
   como bytes no Storage) registre em `## Decisões tomadas` no arquivo da
   task, com o porquê.
7. Ao final, rode o bloco `## Verificação` da task inteiro e cole a saída
   real — não afirme "passou" sem ter visto a saída.
8. Marque os critérios de aceite da task `[x]` um por um, só com evidência
   (comando rodado + saída), igual ao formato de tabela usado no resto do
   projeto.
9. Esta task toca coleta de dado pessoal de titular de cargo público — rode o
   gate de segurança **S1–S21** da skill `/secure-by-default-webdev` e
   reporte na tabela `Item | Status | Evidência (arquivo:linha) | Correção`.
   A seção `## Segurança` da task já lista quais itens se aplicam e quais são
   N/A — confirme, não assuma que a lista está certa sem checar o código real.
10. Só marque `status: concluída` na task depois que todos os critérios de
    aceite estiverem `[x]` com evidência e o gate de segurança estiver sem
    nenhum ❌.

## O que NÃO fazer

- Não implemente exibição do titular/foto em nenhuma tela (município, estado,
  órgão) — está explicitamente fora de escopo nesta task.
- Não colete vice-prefeito, vice-governador, secretariado ou qualquer agente
  público que não seja o titular eleito do cargo.
- Não grave nem referencie brasão, marca ou paleta institucional do governo
  em nenhum lugar do dado coletado.
- Não pule o passo 1 (cadastro no catálogo) sem perguntar ao Bruno primeiro.
- Não decida sozinho reabrir ou alterar a exceção de RF-11/RNF-S08 — ela já
  está fechada; qualquer ajuste de redação nela é decisão do Bruno, não sua.

Se qualquer critério de aceite se revelar impossível, ou você precisar de uma
decisão que não está na task, **pare e pergunte** — não improvise.
