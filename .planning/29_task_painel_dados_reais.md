---
task: Painel novo com dados reais exportados
status: concluída (14/10/2026)
criada: 2026-10-14
---

# Painel com dados reais

## Objetivo
O painel novo exibe os valores exportados pelos coletores reais, sem números copiados à mão.

## Por quê
Hoje os valores do painel novo estão escritos à mão em `painel_indicadores.json` (ilustrativos ou copiados), e ficam defasados em silêncio. Depende da task 28.

## Arquivos envolvidos
| Arquivo | O que muda |
|---|---|
| `scripts/exportar_painel.py` | criar: roda os 8 coletores reais e gera os dados do painel |
| `src/ui/data/painel_dados.json` | gerado: valores e séries por município e estado |
| `src/ui/data/painel_indicadores.json` | editar: só definição dos indicadores (sem valores ilustrativos) |
| `index.html` (painel novo) | editar: ler `painel_dados.json` e distinguir "Não coletado" de "Sem dado" |
| `src/ui/painel-logica.js` | criar (registrado a posteriori): funções puras do painel (formatação, variação, telas, mapa), testáveis no Node; mantém o `index.html` abaixo de 500 linhas |
| `tests/test_exportar_painel.py`, `tests/ui/test_painel_logica.py` | criar (registrado a posteriori): testes do exportador (sem rede, respostas reais gravadas) e da lógica do painel |

## Critérios de aceite
- [x] `scripts/exportar_painel.py` roda os 8 coletores e gera `src/ui/data/painel_dados.json` com as séries históricas.
      — *execução real 14/10: "8/8 fontes ok, 139 municípios" (TER-01 417, TER-02 695, TER-03 5, TER-04 139, TER-05 695, TER-06 695, TER-07 4, REC-02 414 registros); `tests/test_exportar_painel.py` (8 testes)*
- [x] `painel_indicadores.json` não tem mais valores ilustrativos.
      — *o arquivo virou catálogo (`ind`, `moeda`, `fonte`, `sentido`), sem campo de valor; Playwright: nenhum "ilustrativo", NaN, ∞ ou undefined na página*
- [x] Palmas mostra PIB R$ 14,2 bi (série 2019–2023) e RCL real; o Estado mostra PIB R$ 64,3 bi, área 277.424 km² e desocupação real; Gurupi (e qualquer município) mostra PIB, rebanho, produção e RCL reais.
      — *Playwright contra o arquivo real: Palmas PIB 14,2 R$ bi +18,5% vs. 2022 (mini-gráfico de 5 anos) e RCL 2,2 R$ bi em 2025 (a série traz 2023 = 1,83 bi, valor citado na versão anterior deste critério); Estado PIB 64,3 R$ bi, área 277.424 km², desocupação 4,1% no 2T2026 (−1,5 p.p., favorável), RCL 15,6 R$ bi; Gurupi PIB 3,7 R$ bi, produção 195,0 R$ mi, rebanho 137.914, RCL 516,2 R$ mi*
- [x] Indicador sem coletor real aparece como "Não coletado", diferente de "Sem dado" (omissão da fonte, RF-55).
      — *Playwright: Leitos SUS (sem coletor) e RCL com a fonte em erro → "Não coletado"; produção sem valor do município com a fonte ok → "Sem dado"; Muricilândia (prefeitura não entregou RREO/RGF) → "Sem dado", nunca zero; `tests/ui/test_painel_logica.py::test_nao_coletado_x_sem_dado_x_carregando`*

## Fora de escopo
- Saúde e Educação reais (DATASUS/INEP).
- Leitura do BigQuery (task 31, depois da autenticação da conta de infraestrutura do projeto; a task 30 é o coletor de titulares).

## Plano
- [x] 1. Formato de `painel_dados.json` e mapeamento indicador ↔ coletor (com conversão de unidade).
- [x] 2. `scripts/exportar_painel.py`.
- [x] 3. Limpar valores de `painel_indicadores.json`.
- [x] 4. Painel lê `painel_dados.json`; "Não coletado" × "Sem dado".
- [x] 5. Verificação.

## Segurança
| Item | Status | Evidência | Correção |
|---|---|---|---|
| S2 | ✅ | o painel só aceita `painel_dados.json` com `fontes`, `estado` e `municipios` como objetos (senão mostra "formato inesperado"); `dadoDe` descarta ponto que não seja número finito (`painel-logica.js:15`); Playwright com arquivo ausente (404), formato inválido e série inválida: página de pé, sem erro | — |
| S15 | ✅ | o exportador registra `status: erro` por fonte (uma falha não derruba as outras); se nenhuma fonte der ok, devolve 1 e não toca o arquivo; grava em arquivo temporário e só depois substitui (`test_exportar_painel.py`) | — |
| S11 | ✅ | coletas por HTTPS com verificação de certificado e de nome do host (`http.py:22-30`, task 28); `badssl.com` com certificado expirado, host errado, autoassinado e raiz não confiável → rejeitado | — |
| Demais | N/A | página estática, sem login, formulário, upload ou servidor próprio | — |

## Verificação
```bash
.venv/bin/python scripts/exportar_painel.py            # ~20 min (REC-02); --pular TO-REC-02 reaproveita o anterior
.venv/bin/python -m pytest -q                          # 164 passaram, 0 falharam (14/10)
node test_task29.mjs                                   # Playwright, fora do repo: 45 checagens, todas passaram (14/10)
```

## Decisões tomadas
- **Formato:** `{gerado_em, fontes{id:{indicador, status, registros|erro}}, unidades, estado{ind:[[rótulo, valor]]}, municipios{cod:{ind:[[rótulo, valor]]}}}`. O painel cruza o `ind` do catálogo com as séries; `fontes` diz se o indicador foi coletado (senão, "Não coletado").
- **Totais estaduais:** população, PIB e desocupação vêm direto do IBGE para o estado. Área, produção agrícola e rebanho são a soma dos 139 municípios, só quando os 139 têm valor (senão o estado fica sem dado). Conferido contra a API: população e rebanho idênticos; a produção difere em R$ 51 mil por arredondamento, por isso o rótulo "(soma dos municípios)" no órgão IBGE.
- **Receita do estado muda de métrica:** o painel novo mostra a RCL do RREO/RGF (TO-REC-02), não a receita da DCA do painel antigo.
- **Ordem das categorias:** categorias com dado real primeiro (Economia e Produção na tela 1 dos municípios; Território, Economia e Finanças no estado), para a tela inicial não abrir só com "Não coletado". "Tocantins em Números" e "Malhas municipais" saíram do órgão IBGE (não são indicadores).
- **Escala de moeda:** valores em R$ mil viram R$ bi, R$ mi ou R$ mil pelo tamanho (Palmas 14,2 R$ bi; Abreulândia 141,9 R$ mi).
- **Cobertura da RCL:** 138 de 139 municípios. Os 51 que só entregam o RREO Simplificado entram pelo RGF (task 28). Muricilândia (1713957) fica "Sem dado": a prefeitura não entregou RREO nem RGF de 2023 a 2025 (extrato de entregas do SICONFI); só a Câmara entregou o RGF de 2024. Usar o RGF do Legislativo seria possível (a RCL é do ente), mas fica para decisão do Bruno.
- **`--pular`:** reaproveita do arquivo anterior as fontes indicadas, para não repetir os ~20 min do REC-02 quando só o IBGE muda.
