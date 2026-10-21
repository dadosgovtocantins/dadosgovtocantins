# Relatório Final de Extensão Universitária (PIBIEX / Unitins)

**Título do Projeto:** Painel TO em Dados — Plataforma Acadêmica Independente para Monitoramento de Indicadores de Políticas Públicas do Estado do Tocantins  
**Vínculo:** Programa de Bolsas de Extensão (PIBIEX / TO Graduado / Unitins)  
**Instituição:** Universidade Estadual do Tocantins (Unitins)  
**Ano de Conclusão:** 2026  

---

## 1. Resumo Executivo e Objetivos

O projeto *Painel TO em Dados* desenvolveu uma plataforma tecnológica de extensão universitária voltada para a consolidação, monitoramento e transparência de indicadores socioeconômicos, ambientais, fiscais e de serviços públicos nos **139 municípios do Estado do Tocantins**.

### Objetivos Alcançados:
1. Coleta automática de **18 fontes oficiais de dados** (IBGE, INEP, FNDE, Novo CAGED, Comex Stat, Mapa de Empresas, DATASUS, SICONFI, CAPAG e Transferegov).
2. Cobertura territorial de **100% dos 139 municípios tocantinenses**.
3. Implementação da regra metodológica de **distinção estrita entre ausência de dado (omissão declaratória `sem_dado`) e valor zero**.
4. Garantia contratual de **Custo R$ 0,00**, operando integralmente na franquia gratuita de nuvem (*Google Cloud Free Tier*).
5. Elaboração do **Diagnóstico do Índice de Maturidade de Dados Abertos** para 11 órgãos públicos.

---

## 2. Metodologia da Coleta e Arquitetura de Software

A arquitetura do sistema foi desenhada em camadas modulares baseadas em Python 3.11 e BigQuery (Star Schema):
- **Camada de Ingestão (`src/coletores/`):** 18 coletores especializados de tamanho reduzido (≤ 50 linhas de código cada), herdando de `ColetorBase` com controle de idempotência e resiliência.
- **Camada de Dados:** Data Warehouse em BigQuery particionado por data e clusterizado por indicador e município, alimentando a camada semântica com views otimizadas (`< 1 GB/query`).
- **Camada de Apresentação (`index.html` / `src/ui/`):** Interface web responsiva em CSS Vanilla com suporte aos 7 estados de qualidade, selos obrigatorios de auditoria e navegação em 3 níveis (Municípios, Estado e Órgãos).

---

## 3. Impacto Social e Acadêmico

O projeto disponibiliza à sociedade civil, pesquisadores, gestores públicos e cidadãos tocantinenses uma ferramenta gratuita, neutra e auditável para acompanhamento das metas de desenvolvimento regional, reduzindo as assimetrias de informação e promovendo o controle social das políticas públicas no Tocantins.
