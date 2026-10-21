---
task: Telas de apoio (Sobre, Metodologia, Export CSV, Canal de Correção)
status: concluída
sprint: S8
eap: 1.4.5, 1.4.6, 1.4.7
---

# Telas de Apoio e Exportação CSV

## Objetivo
Implementar os modais/páginas de apoio do painel: página **Sobre** (identidade Unitins/PIBIEX), **Metodologia** (explicação da omissão declaratória sem_dado vs valor zero), **Exportação em CSV** dos dados dos cards e **Canal de Correção/Feedback**.

## Arquivos envolvidos
| Arquivo | O que muda |
|---|---|
| `index.html` | editar — Adicionar links de rodapé para Sobre, Metodologia e Modal de Exportação CSV |
| `src/ui/css/app.css` | editar — Estilos para modais de suporte e tabela metodológica |
| `src/ui/app.js` | editar — Lógica de abertura dos modais de apoio e download de CSV |
| `tests/ui/test_telas_apoio.py` | criar — Testes dos modais de apoio e exportador CSV |

## Critérios de aceite
- [ ] Modal ou aba "Sobre o Projeto" detalhando a Unitins, a bolsa PIBIEX e o disclaimer de não-oficialidade
- [ ] Modal "Metodologia" explicando os 7 estados e a regra fundamental de que ausência de dado nunca é zero
- [ ] Funcionalidade de download de dados em formato CSV para os indicadores exibidos na tela
- [ ] Suíte de testes `tests/ui/test_telas_apoio.py` com 100% de aprovação
