# Diagnóstico da Maturidade de Dados Abertos e Transparência Governamental no Tocantins

**Autor:** Equipe de Pesquisa Painel TO em Dados (PIBIEX / Unitins)  
**Instituição:** Universidade Estadual do Tocantins (Unitins)  

---

## Resumo
Este artigo apresenta um diagnóstico inédito sobre o nível de maturidade de dados abertos dos órgãos públicos com atuação no Estado do Tocantins. A pesquisa avaliou a proporção de fontes de dados disponibilizadas em formatos estruturados e reutilizáveis (Grau A/B — API, JSON, CSV) versus fontes disponibilizadas como apenas-link ou documentos fechados (Grau D — PDF, HTML). Os resultados indicam um alto grau de maturidade nas fontes federais de cobertura municipal (100% de reuso), enquanto os portais de transparência estaduais ainda enfrentam barreiras arquiteturais significativas (tecnologias SPA baseadas em Java Vaadin sem APIs REST expostas).

---

## 1. Introdução
A transparência pública e a disponibilidade de dados abertos são requisitos indispensáveis para o fortalecimento da democracia e da governança pública. No entanto, a mera publicação de portais web não garante a reusabilidade dos dados se a infraestrutura subjacente não oferecer endpoints estruturados para consumo automatizado.

---

## 2. Metodologia
A avaliação utilizou a métrica da taxa de reuso por órgão:

$$\text{Maturidade (\%)} = \left( \frac{\text{Fontes Reutilizáveis (Grau A/B)}}{\text{Total de Fontes Catalogadas}} \right) \times 100$$

Os órgãos foram classificados em 4 níveis: **Avançado** (≥80%), **Intermediário** (50–79%), **Inicial** (1–49%) e **Inexistente** (0%).

---

## 3. Resultados e Discussão
- **Órgãos Nível Avançado (100% Reuso):** IBGE, INEP, FNDE, MTE, MDIC, ME, DATASUS e STN.
- **Órgãos Nível Inexistente (0% Reuso Direto via API):** SEFAZ-TO e portais de transparência estaduais (devido ao uso do framework Vaadin 8.9.2 com protocolo opaco GWT/UIDL sem API REST).

---

## 4. Conclusão
Recomenda-se a adoção de estratégias de dados abertos pelos órgãos estaduais do Tocantins, prevendo a exposição de APIs públicas em formato JSON/CSV para viabilizar a integração e o controle social automatizado.
