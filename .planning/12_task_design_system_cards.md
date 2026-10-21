---
task: Design System de Cards (7 estados, selo de data/fonte/esfera, estado sem_dado)
status: concluída
sprint: S4
eap: 1.4.1
---

# Design System de Cards de Indicadores

## Objetivo
Implementar o sistema de componentes CSS/JS e HTML para os Cards de Indicadores do painel, garantindo suporte aos 7 estados de qualidade (`ok`, `estimado`, `defasado`, `suspeito`, `sem_dado`, `falho`, `carregando`), selos obrigatórios de data, fonte e esfera (federal/estadual) e conformidade total com acessibilidade WCAG AA e a identidade neutra acadêmica (Task 05).

## Arquivos envolvidos
| Arquivo | O que muda |
|---|---|
| `src/ui/css/tokens.css` | criar — Design tokens de cores, tipografia, bordas e badges |
| `src/ui/css/cards.css` | criar — Estilos responsivos dos cards de KPI e seus 7 estados |
| `src/ui/components/card.js` | criar — Componente JS renderizador de card de indicador |
| `tests/ui/test_cards.py` | criar — Testes de renderização de estados e acessibilidade |

## Critérios de aceite
- [ ] Implementação de CSS Vanilla modular com tokens de design conforme `docs/identidade.md`
- [ ] Componente renderizador suporta os 7 estados:
  1. `ok`: Valor normal em destaque com variação percentual (verde/vermelho)
  2. `estimado`: Badge explicativo de estimativa
  3. `defasado`: Alerta visual de dado defasado
  4. `suspeito`: Indicativo de inconsistência declaratória
  5. `sem_dado`: Distinção visual explicita (omissão declaratória — cor Amber, NUNCA renderiza como zero)
  6. `falho`: Estado de erro de ingestão
  7. `carregando`: Skeleton loader animado
- [ ] Todo card renderiza obrigatoriamente:
  - Selo de Esfera (`Federal` ou `Estadual`)
  - Selo de Fonte com link oficial
  - Selo de Data de atualização
  - Posição no Ranking Municipal (ex: `12º de 139`) quando aplicável
- [ ] Suíte de testes `tests/ui/test_cards.py` validando os 7 estados e badges
