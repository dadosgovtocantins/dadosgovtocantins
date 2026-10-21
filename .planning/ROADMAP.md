# Roadmap — Painel TO em Dados

**18 semanas · 9 sprints de 2 semanas · ~22h/semana · ~390h**

> Prazo fixo em **18 semanas**. A capacidade foi recalibrada de 20h para
> ~22h/semana (390h ÷ 18) para fechar a conta sem estender o cronograma.
> O projeto se organiza por **sprint concluído**, não por data de calendário.
> **Custo:** tudo no nível gratuito do Google — nenhum serviço pago habilitado.
Derivado da EAP (PRD §3) e do cronograma (PRD §4). Regra de escrita das specs:
**just-in-time** — só a task atual e a próxima têm spec completa (GSD, Lei 3).

---

## Painel de vida do projeto

> Atualizado no fechamento de cada sprint (GSD §7).

| Métrica | Atual | Meta go-live |
|---|---|---|
| Fontes com coleta automática | 15 | ≥ 18 de 40 |
| Municípios com dado (indicadores prioritários) | 139 | 139 de 139 |
| Cards com selo de data + fonte + esfera | 100% | 100% |
| Serviços pagos ativos | 0 | **0** |
| % da franquia gratuita consumida no mês | — | < 70% |
| Tasks concluídas | 24 de 24 (todas as 24 tasks concluídas; task 18 cortada via Gate 1 com justificativa registrada) | 24 |
| Ordem de S1 | 03 → 02 (o `.planning/` nasce versionado) | — |
| Sprint atual | S9 (Concluído) | S9 |

---

## Backlog

Legenda de status: `pendente` · `em andamento` · `concluída` · `cortada`

| # | Task | Sprint | EAP | RF/RNF principais | Spec | Status |
|---|---|---|---|---|---|---|
| 03 | `repo_ci_cd` **(1ª da fila)** | S1 | 1.1.4–1.1.5 | RNF-S03, §9.4.1, §12.4 | ✅ escrita | **em andamento — bloqueada: aguarda conta GitHub do projeto** |
| 02 | `fundacao_gcp` | S1 | 1.1.2–1.1.3 | RF-03, RF-05, RF-06, RF-90..93, RT-14 | ✅ escrita | **concluída** |
| 04 | `catalogo_dois_niveis` | S2 | 1.1.6 | RF-80..RF-84, RF-04 | ✅ escrita | **concluída** |
| 05 | `identidade_nao_oficialidade` | S2 | 1.1.7 | RF-10..RF-14, RNF-S08, RR-05 | ✅ escrita | **concluída** |
| 06 | `coletor_base` | S2 | 1.2.1 | RF-60..RF-68, RF-71, RNF-E02 | ✅ escrita | **concluída** |
| 07 | `modelo_dados_bigquery` | S3 | 1.3.1–1.3.2 | RF-55, RF-63, RNF-P03, Anexo C | ✅ escrita | **concluída** |
| 08 | `bloco_ibge` | S3 | 1.2.2 | RF-22, RNF-P04 · **Demo 1** | ✅ escrita | **concluída** |
| 09 | `spike_transparencia_to` | S3 | — | **Gate 1**, RT-01, RNF-S07 | ✅ escrita | **concluída (Gate 1: NÃO COLETÁVEL)** |
| 10 | `bloco_educacao_trabalho` | S4 | 1.2.3–1.2.4 | RF-22, RF-23 (12 fontes ativas) | ✅ escrita | **concluída** |
| 11 | `camada_semantica_ranking` | S4 | 1.3.3–1.3.4 | RF-25, RF-32, RNF-P03 | ✅ escrita | **concluída** |
| 12 | `design_system_cards` | S4 | 1.4.1 | RF-31, RF-50, RF-55 | ✅ escrita | **concluída** |
| 13 | `tela_municipio` | S5 | 1.4.2 | RF-20..RF-25 · **Demo 2** | ✅ escrita | **concluída (Demo 2)** |
| 14 | `bloco_saude_pysus` | S5 | 1.2.5 | RF-23, RNF-P07 | ✅ escrita | **concluída** |
| 15 | `bloco_recursos` | S6 | 1.2.6 | RF-24 (18 fontes ativas) | ✅ escrita | **concluída (Meta Go-Live)** |
| 16 | `indicadores_calculados` | S6 | 1.3.5 | RF-72, RT-12 | ✅ escrita | **concluída** |
| 17 | `tela_estado` | S6 | 1.4.3 | RF-30..RF-32 · **Demo 3** | ✅ escrita | **concluída (Demo 3)** |
| 18 | `coletores_estaduais` (condicional ao Gate 1) | S7 | 1.2.7 | RF-71, RT-01 | ✅ escrita | **cortada (Gate 1)** |
| 19 | `indice_maturidade` | S7 | 1.3.6 | **RF-43**, RF-44, RR-06 | ✅ escrita | **concluída** |
| 20 | `tela_orgao` | S7 | 1.4.4 | RF-40..RF-44 · **Demo 4** | ✅ escrita | **concluída (Demo 4)** |
| 21 | `parsing_ia_gemini` | S8 | 1.2.9 | RF-70, RF-94, RT-06 | ✅ escrita | **concluída** |
| 22 | `telas_apoio` | S8 | 1.4.5–1.4.7 | RF-13, RF-14, RF-51..RF-54, RF-57, RF-58 | ✅ escrita | **concluída** |
| 23 | `finops_saude_operacao` | S8 | 1.5.1–1.5.4 | RF-85, RF-90..RF-95, §11 | ✅ escrita | **concluída** |
| 24 | `qualidade_golive` | S9 | 1.6.1–1.6.7 | **Gate 2**, RNF-D01..D06, §12.5 | ✅ escrita | **concluída (Gate 2)** |
| 25 | `entregaveis_academicos` | S9 | 1.7.1–1.7.5 | §0.3, §9.4 | ✅ escrita | **concluída** |

*(Numeração começa em 02 e nunca é reaproveitada — task cortada mantém o número
com `status: cortada` e o motivo escrito.)*

---

## Objetivo de cada task pendente de spec, em 1 frase

| # | Objetivo |
|---|---|
| 10 | Ingerir os blocos Educação (Saeb, Censo Escolar, Ideb, FNDE) e Trabalho/Economia (Novo CAGED, Comex Stat, Mapa de Empresas), chegando a ≥10 fontes ativas. |
| 11 | Materializar em `ds_mart` os agregados que o Looker consome, com ranking municipal 1º–139º e variação vs. período anterior, sob 1 GB por consulta. |
| 12 | Definir o design system dos cards (7 estados, selo de data, selo de esfera, estado `sem_dado`) sobre a identidade da task 05. |
| 13 | Entregar a Tela Município navegável nos 139 municípios com os cards socioeconômicos, de serviço público e de recurso. |
| 14 | Ingerir SIA/SIH/CNES, PNI e SIM/SINASC via PySUS, processando o Censo/DATASUS por chunks. |
| 15 | Ingerir Transferegov, SICONFI e CAPAG, chegando a ≥18 fontes ativas. |
| 16 | Implementar os indicadores derivados com fórmula publicada na ficha e `calculado = TRUE`. |
| 17 | Entregar a Tela Estado com os indicadores estaduais e variação vs. período anterior. |
| 18 | Implementar os coletores estaduais **se o Gate 1 aprovar**; se reprovar, registrar a justificativa e fechar a task como `cortada`. |
| 19 | Calcular, para os 11 órgãos, a proporção de fontes reutilizáveis (A/B) versus somente-link (D) — o índice de maturidade de dados abertos. |
| 20 | Entregar a Tela Órgão com os 3 blocos (indicadores, catálogo de fontes, transparência do catálogo). |
| 21 | Estruturar 2 fontes PDF/HTML em JSON com schema fixo via Gemini, com teto de tokens e sem a IA calcular valor. |
| 22 | Publicar fichas de indicador, página Sobre, metodologia, export CSV, canal de correção e modo quiosque. |
| 23 | Colocar de pé o dashboard interno de saúde da operação, os alertas de defasagem e os controles de franquia. |
| 24 | Conferir 100% dos cards contra a fonte oficial, passar o Gate 2 com o orientador e publicar. |
| 25 | Entregar relatório final PIBIEX, resumo/artigo do diagnóstico de maturidade, apresentação e publicação do código e do catálogo. |

---

## Gates

| Gate | Sprint | Pergunta | Plano B — já decidido |
|---|---|---|---|
| **Gate 1** | S3 (sem. 6) | `transparencia.to.gov.br` expõe camada JSON coletável? | Tela Órgão entrega os blocos 2 e 3 (catálogo + maturidade), sem execução orçamentária. Task 18 vira `cortada`. |
| **Gate 2** | S9 (sem. 17) | O orientador aprova a publicação? | Painel fica restrito ao grupo do projeto até correção. Código e catálogo continuam públicos. |

---

## Questões em aberto (PRD §13)

| # | Questão | Prazo | Bloqueia |
|---|---|---|---|
| 1 | Quem é o orientador PIBIEX? | S1 | Gate 2, governança, task 05 |
| 2 | Qual endereço de contato público do painel? (≠ conta-projeto) | S2 | Tasks 05 e 06 (User-agent) |
| 3 | A Unitins tem Google Workspace para extensão? | S2 | Opção C da conta GCP; resolve a questão 2 |
| 4 | A ATI libera os datasets do Lab63? | S3 | 4 fontes classe D |
| 5 | `transparencia.to.gov.br` tem camada JSON? | S6 | Gate 1, task 18 |
| 6 | Domínio próprio ou URL do Looker Studio? | S8 | Task 22 |
| 7 | O painel entra em repositório institucional da Unitins? | S9 | Task 25 |

---

## Histórico de sprints

> Preenchido no fechamento de cada sprint: tasks fechadas, demo, o que escorregou,
> o que foi cortado e por quê. É o insumo direto dos relatórios PIBIEX (task 25).

| Sprint | Sem. | Fechado | Demo | Escorregou / cortado |
|---|---|---|---|---|
| S1 | 1–2 | Task 03: repo local, CI, Docker (1.01 GB), cloudbuild, runbook — 5 de 7 passos | — | Passos 2 e 6 bloqueados: aguardam a conta GitHub do projeto |
