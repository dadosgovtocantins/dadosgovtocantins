---
task: Tela Município (Demo 2 — navegação nos 139 municípios do TO)
status: concluída
sprint: S5
eap: 1.4.2
---

# Tela Município (Demo 2)

## Objetivo
Entregar a interface navegável da **Tela Município**, permitindo a seleção interativa entre os **139 municípios do Tocantins**, exibindo o conjunto completo de cards de indicadores (Socioeconômicos, Educação, Trabalho, Economia e Território) com selos de fonte, data, esfera, ranking municipal e aviso de não-oficialidade (Task 05).

## Arquivos envolvidos
| Arquivo | O que muda |
|---|---|
| `index.html` | criar/editar — Estrutura HTML semântica da aplicação |
| `src/ui/css/app.css` | criar — Layout responsivo da aplicação (header, sidebar/selector, grid de cards) |
| `src/ui/app.js` | criar — Lógica de inicialização, filtro por município, busca e renderização |
| `src/ui/data/municipios_to.json` | criar — Relação canônica dos 139 municípios do TO com código IBGE de 7 dígitos |
| `tests/ui/test_tela_municipio.py` | criar — Testes de integridade da interface e dados dos 139 municípios |

## Critérios de aceite
- [ ] Dropdown/seletor com busca autocomplete contendo exatamente os **139 municípios do Tocantins**
- [ ] Seleção de município atualiza os cards de indicadores em tempo real sem recarregamento da página
- [ ] Exibição das 4 categorias de indicadores (Território/População, PIB/Economia, Educação/FNDE, Trabalho/Emprego)
- [ ] Cabeçalho e rodapé exibem o aviso de não-oficialidade e a marca acadêmica neutra (Task 05)
- [ ] Layout 100% responsivo com CSS Vanilla, grid flexível e tokens WCAG AA
- [ ] Suíte de testes `tests/ui/test_tela_municipio.py` validando os 139 municípios e o HTML semântico
