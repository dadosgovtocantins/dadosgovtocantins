---
task: Parsing com IA Gemini (estruturação de PDF/HTML com schema fixo)
status: concluída
sprint: S8
eap: 1.2.9
---

# Parsing com IA Gemini

## Objetivo
Implementar o módulo de extração e estruturação de documentos não estruturados (PDF/HTML) utilizando a **Gemini API**, convertendo relatórios em JSON no formato do catálogo de indicadores. Registros gerados por IA são marcados obrigatoriamente com `gerado_por_ia = TRUE`, respeitando o teto de tokens e sem delegar cálculos matemáticos à IA.

## Arquivos envolvidos
| Arquivo | O que muda |
|---|---|
| `src/ia/parser_gemini.py` | criar — Módulo de integração com Gemini API e validação de JSON Schema |
| `tests/ia/test_parser_gemini.py` | criar — Testes unitários com mocks de resposta da API |

## Critérios de aceite
- [ ] Módulo recebe texto de PDF/HTML e retorna lista de dicionários no formato canônico da `fato_indicador`
- [ ] Todo registro gerado via Gemini possui obrigatoriamente `gerado_por_ia = TRUE` (RF-70)
- [ ] Controle estrito de teto de tokens (teto mensal < 70% da franquia gratuita)
- [ ] IA restrita à extração e formatação — a IA NUNCA calcula valores ou soma totais (RF-94)
- [ ] Suíte de testes `tests/ia/test_parser_gemini.py` com 100% de aprovação
