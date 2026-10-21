---
task: Coletores reais do IBGE e do Tesouro
status: concluída
criada: 2026-10-14
---

# Coletores reais (IBGE e Tesouro)

## Objetivo
TO-TER-01 a 07 e TO-REC-02 buscam os dados reais nas APIs; os outros 10 coletores param de inventar números.

## Por quê
Todos os 18 coletores têm a URL real, mas `extrair()` gera dados simulados com códigos IBGE inventados (1700001…) e `transformar()` marca tudo como `qualidade: ok`. Qualquer carga sai fabricada. Decisão do Bruno (2026-10-14): tornar reais IBGE e Tesouro agora; o resto deixa de inventar.

## Arquivos envolvidos
| Arquivo | O que muda |
|---|---|
| `src/coletores/to_ter_01.py` … `to_ter_07.py` | editar: `extrair()` real via `ClienteHTTP`; `transformar()` lê o formato SIDRA |
| `src/coletores/to_rec_02.py` | editar: RCL dos 139 municípios + estado (SICONFI RREO Anexo 3) |
| `src/coletores/sidra.py`, `src/coletores/siconfi.py` | criar: leitura comum do SIDRA e coleta/leitura da RCL do SICONFI |
| `src/coletor_base/http.py`, `src/coletor_base/certs/sectigo_dv_r36.pem` | editar/criar: TLS com certifi + intermediário da Sectigo e timeout (ver Decisões) |
| `requirements.txt` | editar: declara `certifi==2026.7.22` (já travado no lock) |
| `tests/conftest.py` | criar: `rede_gravada` e trava contra acesso à internet nos testes |
| `tests/test_automacao_coleta.py`, `tests/coletores/test_nao_implementados.py` | criar |
| `src/coletores/to_eco_*.py`, `to_edu_*.py`, `to_rec_01.py`, `to_rec_03.py`, `to_sau_*.py`, `to_trab_01.py` | editar: `extrair()` levanta erro explícito |
| `src/coletor_base/excecoes.py` | editar: exceção de coleta não implementada |
| `tests/fixtures/ibge_payloads.py`, `recursos_payloads.py` | editar: recortes reais gravados |
| `tests/coletores/*.py` | editar: testes no formato real e dos coletores não implementados |
| `scripts/automacao_coleta.py` | editar: sem fallback simulado |

## Critérios de aceite
- [x] Os 8 coletores chamam a API real pelo `ClienteHTTP` e leem o formato real.
- [x] Os 139 municípios saem com os códigos IBGE verdadeiros (7 dígitos).
- [x] Marcação do IBGE: "...", "X" e ".." não geram registro; "-" vira 0 (zero absoluto) — RF-55.
- [x] As fixtures são recortes gravados das respostas reais e os testes rodam sem rede.
- [x] Os outros 10 coletores levantam erro explícito ("coleta real não implementada") em vez de gerar números.
- [x] `automacao_coleta.py` não troca mais por dados simulados quando a API falha.
- [x] Uma coleta real pelo CLI (`TO-TER-02`) termina com 139 registros reais.

## Fora de escopo
- Coletas de DATASUS, INEP, CAGED, Comex Stat, Mapa de Empresas, Transferegov e CAPAG.
- Carga real no BigQuery (o carregador continua local).

## Plano
- [x] 1. Exceção de coleta não implementada + 10 coletores sem números inventados.
- [x] 2. Módulo `sidra.py` (URL com séries, leitura, marcações do IBGE).
- [x] 3. TO-TER-01 a 07 reais (descobrir o código "Total" da PAM nos metadados).
- [x] 4. TO-REC-02 real (RCL municipal + estadual).
- [x] 5. Fixtures reais gravadas + testes.
- [x] 6. `automacao_coleta.py` sem fallback simulado.
- [x] 7. Verificação (pytest, ruff, coleta real).

## Segurança
S2 (validar a resposta da API antes de usar), S14 (nenhuma dependência nova), S15 (erro explícito, sem dado falso), RF-71 (conformidade robots/termos já no `ColetorBase`).

## Verificação
```bash
.venv/bin/python -m pytest -q
.venv/bin/ruff check src tests scripts
.venv/bin/python -m src.cli coletar --fonte TO-TER-02 --ambiente dev
```

## Decisões tomadas
- Coletor IBGE vira configuração: `ColetorSidra` (em `sidra.py`) monta a URL, lê a resposta e gera os registros; cada `to_ter_NN.py` declara só agregado, variável, períodos e unidade (16 a 22 linhas, contrato RNF-E02 de ~50).
- Cada coleta traz os últimos períodos disponíveis (população 3, PIB/PAM/PPM 5, PNADC 4 trimestres), não só o mais recente: o `fato_indicador` é particionado por `periodo_ref` e a task 29 precisa da série para o mini-gráfico. Por isso TER-01 gera 139 x 3 = 417 registros.
- Marcações do IBGE: "-" vira 0 (zero absoluto); "...", "..", "X", vazio e não numérico não geram registro (RF-55). Resposta com mais de 1 resultado ou fora do formato levanta `ValidacaoError`.
- PAM: variável 215 (valor da produção, R$ mil) com classificação 782[0] (total das lavouras). O coletor antigo apontava para a variável 214 (quantidade produzida), que não é R$.
- TO-TER-04: a área vem da tabela 4714 (Censo 2022), não da malha geométrica; a URL antiga de malhas não trazia área.
- TO-TER-07: tabela 4099 (taxa trimestral); `valor_texto` guarda o trimestre ("2T2026").
- `ClienteHTTP` (TLS): o Python do sistema não confiava na cadeia do IBGE (`CERTIFICATE_VERIFY_FAILED`); passou a usar o bundle do `certifi`, como o `requests`, e ganhou timeout (conexão 10 s, leitura 60 s; antes não expirava). A verificação de TLS nunca é desligada.
- Intermediário da Sectigo (2026-10-14): o `servicodados.ibge.gov.br` passou a enviar só o certificado do site, sem o intermediário (os hosts `apisidra` e `www` enviam os 3 certificados). O curl/macOS completa a cadeia sozinho (AIA); Python/OpenSSL não, e toda coleta IBGE falhava (12 de 12 chamadas). Fix padrão de cadeia incompleta: o intermediário público "Sectigo Public Server Authentication CA DV R36" (baixado do campo CA Issuers do próprio certificado) foi gravado em `src/coletor_base/certs/` e carregado no contexto TLS. Conferido com `openssl verify`: sem ele a cadeia falha, com ele valida até uma raiz do certifi; o intermediário é assinado pela raiz Sectigo R46 (já no certifi, válido até 2036). Não amplia a confiança. `badssl.com` (expirado, host errado, autoassinado, raiz não confiável) continua sendo rejeitado. Impressão digital fixada em `tests/coletor_base/test_tls.py`. Remover o arquivo quando o IBGE voltar a enviar a cadeia completa.
- TO-REC-02 troca DCA por RREO Anexo 3 (RCL anual, coluna "TOTAL (ÚLTIMOS 12 MESES)", 6º bimestre), que é onde a RCL existe. Só 87 dos 139 municípios entregam o RREO completo: os com menos de 50 mil habitantes entregam o RREO Simplificado, que não tem Anexo 3. Para eles a mesma RCL está no RGF Anexo 1 (`ReceitaCorrenteLiquidaLimiteLegal`; conferido: valor idêntico ao do RREO para Palmas e para o estado). O coletor tenta o RREO e, se não houver RCL, o RGF Simplificado semestral e depois o RGF quadrimestral; cada item guarda a origem. Município que não entregou nada fica sem registro (RF-55). Lista de municípios vem da API de localidades do IBGE. A zona raw guarda só a linha da RCL de cada ente (a resposta completa tem ~100 KB por ente). Coleta completa: 140 entes x 3 exercícios, ~13 min (0,5 s de intervalo + latência de ~1,8 s). Valores convertidos de R$ para R$ mil.
- Os 10 coletores sem coleta real levantam `ColetaNaoImplementadaError`; `executar()` a relança como `FonteIndisponivelError` (nada é gravado). A fixture sintética deles segue só para testar o contrato de `transformar()` e está identificada como SINTÉTICA.
- `scripts/automacao_coleta.py`: sem fallback simulado; se uma API falha, mantém os CSV anteriores e sai com código 1.
- `tests/coletores/__init__.py` era cópia exata de `test_bloco_ibge.py`; foi esvaziado.
- Trava no `conftest`: nenhum teste acessa a internet (precisa de `rede_gravada` ou de monkeypatch próprio). Comprovada com um teste descartável.
- Não editado (fora do escopo): `src/cli.py`, `src/coletor_base/base.py` e `carga.py` (em alteração por outra frente: task 30, titulares). 14 arquivos já estavam fora do `ruff format` e 14 avisos de lint são de `scrapers_estaduais.py`.

## Evidência (2026-10-14)
`pytest -q`: 138 testes, 0 falhas (eram 86). `ruff check src tests`: só os 14 avisos antigos de `scrapers_estaduais.py`; arquivos novos e alterados passam no `ruff check` e no `ruff format`.
Coleta real pelo CLI: `TO-TER-04` ok, 139 linhas, 139 municípios; `TO-TER-05` ok, 695 linhas, 139 municípios; `TO-TER-06` ok, 695 linhas, 139 municípios; `TO-TER-07` ok, 4 linhas (estadual). `TO-TER-02` retornou `sem_mudanca` (hash da mesma resposta real já registrado), e a chamada direta devolveu 695 valores de 139 municípios.
`TO-SAU-01`: falha explícita ("coleta real (CNES/DATASUS) ainda não implementada; nenhum valor é gerado").
Checagens cruzadas reais: soma das áreas dos 139 municípios = 277.423,631 km² (estado: 277.423,627); soma da população 2024 = 1.577.342 (igual ao CSV coletado antes, de forma independente); PIB de Palmas 2023 = R$ 14.168.469 mil; RCL do estado 2025 = R$ 15,57 bi, Palmas R$ 2,16 bi.
