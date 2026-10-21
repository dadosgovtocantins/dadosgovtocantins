# Apresentação Institucional e Relatório de UX Design

**Projeto:** Painel TO em Dados — Monitoramento e Transparência de Políticas Públicas do Tocantins  
**Vínculo:** Projeto de Extensão Universitária PIBIEX / TO Graduado — Unitins  
**Especialidade:** UX/UI Design & KPI Dashboard Governance  

---

## 1. Visão Geral e Proposta de Valor de UX

 O **Painel TO em Dados** foi projetado sob os princípios modernos de **UX Design para Dashboards de KPIs**, garantindo acessibilidade, carga cognitiva reduzida, máxima clareza metodológica e navegação fluida para gestores públicos, cidadãos e pesquisadores acadêmicos.

---

## 2. Arquitetura de Informação e Hierarquia Visual

O painel foi estruturado em **3 Níveis de Navegação (Dashboard Hierarchy)** para atender diferentes perfis de usuários:

```
├── 1. Visão por Município (Tática / Operacional)
│   ├── Seleção interativa dos 139 municípios do TO
│   ├── 11 Cards de KPIs Socioeconômicos, Educação, Saúde, Trabalho e Recursos
│   └── Comparativo de Posição no Ranking (1º ao 139º no estado)
│
├── 2. Visão Geral do Estado (Estratégica)
│   ├── KPIs consolidados estaduais (PIB TO, População, Desocupação PNADC, Receita STN)
│   └── Variação histórica percentual vs. período anterior (▲ / ▼)
│
└── 3. Visão por Órgão & Transparência (Governança & Auditabilidade)
    ├── Diagnóstico do Índice de Maturidade de Dados Abertos (Grau A/B vs D)
    ├── Matriz de transparência dos 11 órgãos catalogados
    └── Veredito do Gate 1 (Respeito às diretrizes de robots/termos)
```

---

## 3. Design System de Cards de KPIs (7 Estados e Selos)

Seguindo as melhores práticas de **KPI Dashboard Design**:

| Elemento de UX | Padrão Adotado | Justificativa de UX / Acessibilidade |
|---|---|---|
| **Limite de KPIs** | 5–10 cards por tela | Evita sobrecarga cognitiva (Miller's Law) e mantém o foco no essencial |
| **Estados Visuais (7)** | `ok`, `estimado`, `defasado`, `suspeito`, `sem_dado`, `falho`, `carregando` | Feedback imediato sobre a saúde e a qualidade da informação |
| **Selo Amber `sem_dado`** | Distinção entre omissão e zero | **Inovação de UX:** omissão declaratória nunca é exibida como R$ 0 para não penalizar reputacionalmente o município |
| **Selos de Auditabilidade** | Esfera (`Federal`/`Estadual`), Data e Fonte Oficial | Garante transparência total e rastreabilidade da origem do dado |
| **Contraste WCAG AA** | Slate + Sky Blue + Amber (Mínimo 4.5:1) | Alta legibilidade para todos os perfis de usuários em desktop e mobile |

---

## 4. Indicadores-Chave Chaves por Bloco Temático

| Bloco | KPI Principal | Unidade | Frequência | Fonte |
|---|---|---|---|---|
| **Território & Demografia** | População Residente / Área | hab / km² | Anual | IBGE |
| **Desenvolvimento Econômico**| PIB Municipal & PIB per Capita | R$ mil / R$/hab | Anual | IBGE / Calculado |
| **Educação & Formação** | IDEB Anos Iniciais / Repasses FNDE | Nota / BRL | Bienal / Anual | INEP / FNDE |
| **Trabalho & Renda** | Saldo de Emprego Formal | Postos | Mensal | Novo CAGED |
| **Saúde Pública** | Leitos SUS / Cobertura Vacinal PNI | Leitos / % | Mensal / Anual | DATASUS / PNI |
| **Gestão Fiscal & Recursos** | Convenios & Receita Corrente Líquida | BRL / R$ mil | Mensal / Anual | Transferegov / SICONFI |

---

## 5. Próximos Passos de Apresentação Acadêmica

1. **Submissão ao Orientador:** Envio do relatório [relatorio_pibiex.md](file:///Users/brunovima/DADOS%20GOV/docs/relatorio_pibiex.md) e do artigo [artigo_maturidade_dados.md](file:///Users/brunovima/DADOS%20GOV/docs/artigo_maturidade_dados.md).
2. **Defesa de Extensão (Unitins):** Apresentação interativa da interface rodando ao vivo em [http://localhost:8080](http://localhost:8080).
