---
task: Indicadores calculados derivados (fórmulas com calculado = TRUE)
status: concluída
sprint: S6
eap: 1.3.5
---

# Indicadores Calculados Derivados

## Objetivo
Implementar o mecanismo de cálculo de indicadores derivados (como PIB per capita municipal, densidade demográfica e taxa de dependência fiscal), marcados com `calculado = TRUE` e `gerado_por_ia = FALSE`, com fórmulas auditáveis publicadas na ficha do indicador.

## Arquivos envolvidos
| Arquivo | O que muda |
|---|---|
| `src/sql/mart/vw_indicadores_calculados.sql` | criar — View de cálculo de indicadores derivados |
| `src/indicadores/calculador.py` | criar — Módulo Python para execução e validação de fórmulas |
| `tests/indicadores/test_calculador.py` | criar — Testes unitários das fórmulas de cálculo |

## Critérios de aceite
- [ ] PIB per Capita calculado via `(PIB Municipal * 1000) / População Residente`
- [ ] Densidade Demográfica calculada via `População Residente / Área Territorial (km²)`
- [ ] Todos os registros calculados possuem obrigatoriamente `calculado = TRUE` e `gerado_por_ia = FALSE`
- [ ] Omissão de dados de entrada (`qualidade = 'sem_dado'`) gera indicador derivado `sem_dado`, nunca zero
- [ ] Suíte de testes `tests/indicadores/test_calculador.py` validando precisão das fórmulas e tratamento de nulos
