---
task: Nomes dos titulares eleitos no painel (prefeitos e governador)
status: concluída (15/10/2026)
criada: 2026-10-14
---

# Nomes dos titulares no painel

## Objetivo
O painel mostra o nome do prefeito eleito de cada município e o do governador eleito, vindos do `TO-GER-01` (TSE) pelo `painel_dados.json`.

## Por quê
O `TO-GER-01` (task 30) já coleta os 140 titulares do TSE, mas o painel mostra "Prefeito(a) não informado(a)" em todos: o exportador não inclui a fonte e o `index.html` tem os nomes em branco, fixos no código.

## Arquivos envolvidos
| Arquivo | O que muda |
|---|---|
| `scripts/exportar_painel.py` | editar: roda o `TO-GER-01`, valida com `validar_titulares` e grava `titulares` (separado das séries de indicadores) |
| `src/ui/painel-logica.js` | editar: função pura `titular()` (valida e formata o nome) |
| `index.html` | editar: lê `titulares`; remove os campos fixos `prefeito`/`governador`; mostra "Eleito(a) em AAAA · Fonte: TSE" |
| `tests/conftest.py` | editar: rota simulada do TSE (zip montado a partir da fixture real da task 30) |
| `tests/test_exportar_painel.py` | editar: testes dos titulares no exportador |
| `tests/ui/test_painel_logica.py` | editar: testes da `titular()` |
| `tests/ui/test_tela_municipio.py` | editar (15/10, correção pós-entrega): teste do `?v=` dos arquivos do painel |

## Critérios de aceite
- [x] `exportar_painel.py` roda o `TO-GER-01` e grava `titulares` no `painel_dados.json`: 139 prefeitos + governador, cada um com nome, cargo, ano da eleição e fonte "TSE".
      — *coleta real 15/10: "TO-GER-01 ok: 140", "9/9 fontes ok"; 139 municípios com os mesmos códigos do painel; cada titular só com `nome`, `cargo`, `ano_eleicao`, `fonte` (sem `sq_candidato` nem `url_foto`); `test_titulares_eleitos_vao_para_o_painel`*
- [x] Os titulares só são gravados se passarem pela `validar_titulares` (task 30): município fora dos 139, duplicata ou dois governadores → fonte em "erro", nenhum titular gravado.
      — *`test_titulares_invalidos_nao_sao_gravados` (filtro deixando passar não eleitos: 3 governadores e prefeitos duplicados → `ValidacaoError`, sem `titulares`, demais fontes ok)*
- [x] Falha do TSE não derruba as outras 8 fontes; o painel mostra "Prefeito(a) não informado(a)"; `--pular TO-GER-01` reaproveita os titulares do arquivo anterior.
      — *`test_falha_do_tse_nao_derruba_as_outras_fontes` (8 ok), `test_pular_reaproveita_os_titulares` (nenhuma chamada ao TSE); Playwright com o TSE em erro: "Prefeito(a) não informado(a)" e "Governador(a) não informado(a)", cartões de indicadores na tela. A coleta real com `--pular` das 8 fontes manteve as séries idênticas às do arquivo anterior*
- [x] Palmas mostra "Eduardo Siqueira Campos", Gurupi "Josi Nunes" e o Estado "Wanderlei Barbosa" (conferidos no bruto real do TSE em 14/10).
      — *Playwright contra o arquivo real: "Eduardo Siqueira Campos · Eleito(a) em 2024 · Fonte: TSE", "Josi Nunes · …", "Wanderlei Barbosa · Eleito(a) em 2022 · Fonte: TSE"; Muricilândia "João Victor" (acento preservado)*
- [x] Ao lado do nome: "Eleito(a) em 2024 · Fonte: TSE" (2022 para o governador), na mesma tela do aviso de não-oficialidade.
      — *Playwright: legenda e "sem vínculo com o Governo do Estado do Tocantins" na mesma página; a aba Órgão não mostra legenda*
- [x] Município sem titular no arquivo → "Prefeito(a) não informado(a)", nunca nome inventado ou de outro município.
      — *Playwright: Palmas removida do arquivo → "não informado(a)", Gurupi segue com o próprio nome; `titulares`/`municipios` em texto e `nome` numérico ou vazio → "não informado(a)", sem erro de página; `test_titular_ausente_ou_invalido_nao_vira_nome` (8 casos)*
- [x] O nome é tratado como texto: valor com `<b>` ou `<script>` aparece literal, sem criar elemento na página.
      — *Playwright com `<b>INJ</b><img src=x onerror=…>`: o HTML gerado é `&lt;b&gt;inj&lt;/b&gt;&lt;img …&gt;`, só `span` (os `span.sc-interp` do runtime) e nenhum script executado*
- [x] Nome exibido com iniciais maiúsculas (partículas de/da/do/dos/das/e em minúsculas); o arquivo guarda o nome como o TSE publica (nome de urna, em maiúsculas).
      — *`test_titular_formata_o_nome_de_urna_e_cita_o_tse` ("Maria do Socorro", espaço duplo e final removidos, "João-Paulo", partícula no início fica maiúscula); arquivo com "EDUARDO SIQUEIRA CAMPOS"*
- [x] As fotos continuam como espaço reservado em todos os municípios.
      — *Playwright: "Foto do(a) prefeito(a)" e nenhuma imagem "Foto de …" no município e no estado*
- [x] `pytest` e `ruff` passam, sem rede nos testes; `index.html` abaixo de 500 linhas.
      — *`pytest -q`: 170 passaram, 0 falharam (eram 164; +4 exportador, +2 lógica); `ruff check` e `ruff format --check` limpos nos 4 arquivos Python da task; `index.html` 431 linhas. Ver ressalva do ruff em Verificação*

## Fora de escopo
- Fotos: `TO-GER-02` segue bloqueado (RF-71).
- Titular em exercício (afastamento, renúncia, cassação): o TSE informa quem foi eleito; por isso o texto diz "eleito(a) em", não "em exercício".
- Eleições de 2026: os eleitos tomam posse em 1/1/2027; trocar o ano em `ELEICOES` (`tse_candidatos.py`) fica para outra task.
- Vice, secretariado, partido e gênero: gênero e partido não são coletados (minimização, RNF-S05); por isso o texto mantém "(a)".
- `docs/textos_legais.md:37` ("nenhuma informação pessoal identificável é coletada"): com os nomes na tela, contradiz o painel. Redação do Bruno, antes de publicar.

## Plano
- [x] 1. Exportador: `TO-GER-01` → `titulares` validados; `--pular TO-GER-01` reaproveita.
- [x] 2. Rota simulada do TSE no `conftest.py` e testes do exportador.
- [x] 3. `titular()` em `painel-logica.js` e testes no Node.
- [x] 4. `index.html` lê `titulares` e mostra nome, ano da eleição e fonte.
- [x] 5. Coleta real do TSE, Playwright, suíte completa e ruff.

## Segurança
| Item | Status | Evidência | Correção |
|---|---|---|---|
| S1 segredos | ✅ | o TSE não exige chave; nenhum segredo nos arquivos da task | — |
| S2 validação | ✅ | exportador: `validar_titulares` antes de gravar (`exportar_painel.py`, `coletar`); painel: `titular()` só aceita objeto com `nome` texto de 1 a 80 caracteres (`painel-logica.js`); o runtime escapa o texto (`support.js:576`, renderização pelo React); Playwright com HTML injetado → texto literal | — |
| S11 HTTPS | ✅ | `URL_TSE` https com verificação de certificado e host (`http.py:22-30`) | — |
| S15 erro | ✅ | falha do TSE fica em `fontes["TO-GER-01"]` e não derruba as outras (`test_falha_do_tse_nao_derruba_as_outras_fontes`) | — |
| RNF-S05 | ✅ | nenhuma coluna nova além das 7 da task 30; o painel recebe só nome, cargo, ano e fonte | — |
| S3–S10, S12–S14, S16–S23 | N/A | página estática, sem login, formulário, upload, SQL, dependência nova ou servidor próprio | — |

## Verificação
```bash
.venv/bin/python scripts/exportar_painel.py --pular TO-TER-01 TO-TER-02 TO-TER-03 TO-TER-04 TO-TER-05 TO-TER-06 TO-TER-07 TO-REC-02
#   [00:01:06] coletando TO-GER-01...  ok: 140
#   Exportado: …/painel_dados.json (9/9 fontes ok, 139 municípios).   (22 s)
.venv/bin/python -m pytest -q          # 170 passaram, 0 falharam
.venv/bin/ruff check src tests          # 14 erros, todos em src/coletores/scrapers_estaduais.py (anteriores, fora da task)
node test_task32.mjs                   # Playwright, fora do repo: 21 checagens, TUDO PASSOU
node test_task29.mjs                   # regressão da task 29: 45 checagens, TUDO PASSOU
```
Ressalva: `ruff check src tests scripts` (comando original desta spec) dá 23 erros: 14 em `scrapers_estaduais.py` e 9 em outros arquivos de `scripts/` (imports sem uso ou fora de ordem em `automacao_coleta.py`, `exportar_ui_data.py`, `gerar_*`). Nenhum nos arquivos desta task; o CI lint só `src tests`.

## Decisões tomadas
- **Validação só nos titulares:** o exportador chama `validar()` apenas no `TO-GER-01`. Aplicar o `validar_registros` padrão às 8 fontes de indicadores mudaria o comportamento delas (cobertura mínima de 90%), fora do escopo.
- **Legenda com o estilo existente:** "Eleito(a) em AAAA · Fonte: TSE" usa a classe `.pop-fonte` (a mesma do "IBGE · Censo 2022"), na mesma linha do nome; nenhum CSS novo.
- **Fonte fixa "TSE" na legenda:** o painel não exibe o campo `fonte` do arquivo; a origem do dado é sempre o `TO-GER-01`.
- **Ano inválido não é inventado:** sem `ano_eleicao` inteiro, a legenda fica só "Fonte: TSE".
- **`MUNICIPIOS` e `ESTADO` sem nome fixo:** a entrada de Palmas, que só repetia os valores padrão, saiu; os nomes vêm apenas do `painel_dados.json`.
- **Teste de escape:** o runtime envolve cada interpolação em `span.sc-interp`; o teste confere que só existem `span` (nenhum `b`, `img` ou `script`) e que nenhum script rodou.
- **Correção pós-entrega (15/10) — cache do navegador:** o Bruno viu "PainelLogica.titular is not a function". Causa confirmada: o servidor entregava o `painel-logica.js` novo (com `titular`), mas sem `Cache-Control` (só `Last-Modified`); o navegador reaproveitou o `.js` antigo do cache com o `index.html` novo. O Playwright não pegou porque abre sempre sem cache. Correção: `index.html` carrega `painel-logica.js?v=<SHA-256[:8]>` e `painel.css?v=<SHA-256[:8]>`; mudou o arquivo, muda o endereço. `test_arquivos_do_painel_tem_versao_pelo_conteudo` falha se o `?v=` não bater com o arquivo (falhou antes da correção, passa depois). Verificado: o navegador pede `painel-logica.js?v=14a9517c`, `typeof PainelLogica.titular === "function"`, suíte 171/0, Playwright das tasks 29 e 32 sem falha.
