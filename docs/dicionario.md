# Dicionário de Dados — Catálogo em Dois Níveis

**Versão do Projeto:** Painel TO em Dados (PRD v4.2 §1.4, Anexo B)  
**Tabelas de Origem:** Google Sheets (`catalogo_fontes`, `catalogo_indicadores`) / BigQuery (`ds_stg.ext_catalogo_fontes`, `ds_stg.ext_catalogo_indicadores`)

---

## 1. Tabela `catalogo_fontes` (40 colunas)

Mapeia cada origem de dados consultada pelo projeto, seus parâmetros técnicos de coleta, licenças e conformidade.

| # | Coluna | Tipo | Descrição | Valores de Exemplo / Regras |
|---|---|---|---|---|
| 1 | `ID` | STRING | Identificador único da fonte | `TO-TER-01`, `TO-SAU-01` |
| 2 | `ÓRGÃO` | STRING | Sigla do órgão custodiante principal | `IBGE`, `DATASUS`, `STN` |
| 3 | `INDICADOR` | STRING | Nome sintético da fonte/pesquisa | `Estimativas de População` |
| 4 | `ÁREA` | STRING | Área temática de aplicação | `Território`, `Saúde`, `Educação` |
| 5 | `SISTEMA` | STRING | Nome do sistema de origem | `SIDRA`, `TabNet`, `SICONFI` |
| 6 | `O QUE REPRESENTA` | STRING | Descrição conceitual do dado | `População residente estimada` |
| 7 | `LINK PÚBLICO` | STRING | URL da página pública de acesso | `https://sidra.ibge.gov.br/...` |
| 8 | `URL DA API` | STRING | Endpoint base da API REST/FTP | `https://servicodados.ibge.gov.br/...` |
| 9 | `ENDPOINT` | STRING | Rota específica ou consulta | `/api/v3/agregados/6579/...` |
| 10 | `AUTENTICAÇÃO` | STRING | Requisito de chave/token | `Nenhuma`, `API Key` |
| 11 | `FORMATO` | STRING | Formato nativo dos dados | `JSON`, `CSV`, `DBC` |
| 12 | `CLASSE DE FORMATO` | STRING | Categoria estrutural da API | `A (API JSON)`, `B (Download)`, `D (HTML)` |
| 13 | `PERIODICIDADE EXATA` | STRING | Frequência oficial de atualização | `Anual`, `Mensal`, `Bienal` |
| 14 | `DEFASAGEM` | STRING | Atraso médio na publicação | `6 meses`, `1 ano` |
| 15 | `ÚLTIMA ATUALIZAÇÃO` | STRING | Data da última coleta registrada | `2026-08-30` |
| 16 | `HISTÓRICO DISPONÍVEL` | STRING | Intervalo de anos com cobertura | `2010 a 2024` |
| 17 | `NÍVEL GEOGRÁFICO` | STRING | Menor granularidade geográfica | `Municipal (139)`, `Estadual` |
| 18 | `GRANULARIDADE TEMPORAL` | STRING | Intervalo temporal dos registros | `Anual`, `Mensal` |
| 19 | `UNIDADE DE MEDIDA` | STRING | Unidade padrão do dado bruto | `habitantes`, `R$`, `%` |
| 20 | `RESPONSÁVEL PELO DADO` | STRING | Entidade legal responsável | `IBGE`, `Ministério da Saúde` |
| 21 | `FONTE PRIMÁRIA/SECUNDÁRIA` | STRING | Origem do dado | `Primária`, `Secundária` |
| 22 | `TIPO DE FONTE` | STRING | Esfera da instituição | `Federal`, `Estadual` |
| 23 | `FONTE ABERTA EQUIVALENTE` | STRING | Alternativa pública se restrito | `N/A` |
| 24 | `PAINEL LAB63 RELACIONADO` | STRING | ID no portal Lab63 se houver | `N/A` |
| 25 | `POWER BI DATASET ID` | STRING | ID técnico se fonte for PowerBI | `N/A` |
| 26 | `POWER BI REPORT ID` | STRING | ID do relatório PowerBI | `N/A` |
| 27 | `ACESSO PÚBLICO SEM CADASTRO?` | STRING | Acesso livre a qualquer cidadão | `Sim`, `Não` |
| 28 | `REUTILIZÁVEL?` | STRING | Reuso automático permitido | `Sim`, `Não` |
| 29 | `API PÚBLICA?` | STRING | Exposição de API estruturada | `Sim`, `Não` |
| 30 | `DADOS REALMENTE ABERTOS?` | STRING | Conformidade com Dados Abertos | `Sim`, `Não` |
| 31 | `QUADRANTE` | STRING | Q1 (Ingerível) ou Q2 (Leitura) | `Q1`, `Q2` |
| 32 | `ESCOPO` | STRING | Pertence ao escopo MVP | `In`, `Out` |
| 33 | `LICENÇA DE USO` | STRING | Licença jurídica dos dados | `Domínio Público`, `CC-BY 4.0` |
| 34 | `RESTRIÇÃO ROBOTS/TERMOS` | STRING | Verificação do robots.txt + data | `Não restritivo (checado em 31/08/2026)` |
| 35 | `MÉTODO DE COLETA` | STRING | Estratégia de ingestão no Python | `API Direct`, `PySUS`, `Scraping` |
| 36 | `STATUS DE VALIDAÇÃO` | STRING | Situação da homologação | `Homologado`, `Pendente` |
| 37 | `NÍVEL DE CONFIABILIDADE` | STRING | **DESATIVADA-MVP** (RF-84) | Preservada para retrocompatibilidade |
| 38 | `CLASSIFICAÇÃO` | STRING | Classe de prioridade/qualidade | `A`, `B`, `C`, `D` |
| 39 | `PRIORIDADE` | STRING | Ordem de implementação | `1`, `2`, `3` |
| 40 | `OBSERVAÇÕES TÉCNICAS` | STRING | Notas para dev do coletor | Ex: `Requer parsing de charset Latin-1` |

---

## 2. Tabela `catalogo_indicadores` (12 colunas)

Mapeia cada indicador atômico exibido como card nas telas do painel.

| # | Coluna | Tipo | Chave | Descrição | Validação / Regras |
|---|---|---|---|---|---|
| 1 | `id_indicador` | STRING | PK | Slug único do indicador atômico | Ex: `populacao_residente`, `pib_per_capita` |
| 2 | `id_fonte` | STRING | FK | Aponta para `catalogo_fontes.ID` | Deve existir em `catalogo_fontes.ID` |
| 3 | `nome_exibicao` | STRING | — | Rótulo do card na interface | Ex: `População Residente Estimada` |
| 4 | `definicao_cidadao` | STRING | — | Texto explicativo para tooltip cidadão | Explicação em linguagem simples |
| 5 | `unidade` | STRING | — | Unidade visual exibida no card | **Uma só** (Ex: `hab`, `R$`, `%`, `nota`) |
| 6 | `sentido` | STRING | — | Direção da variação para cor (▲/▼) | `maior_melhor`, `menor_melhor`, `neutro` |
| 7 | `tela` | STRING | — | Tela principal de destino no Looker | `municipio`, `estado`, `orgao` |
| 8 | `ordem_card` | INT64 | — | Posição no grid da tela | Número inteiro ≥ 1 |
| 9 | `icone` | STRING | — | Identificador do ícone do card | Ex: `users`, `currency-dollar`, `school` |
| 10 | `calculado` | BOOL | — | Indica se o valor é derivado de cálculo | `TRUE` ou `FALSE` |
| 11 | `formula` | STRING | — | Fórmula matemática explicativa | **Obrigatória se `calculado = TRUE`** |
| 12 | `status` | STRING | — | Estado de publicação do card | `ativo`, `homologacao`, `descontinuado` |

---

## 3. Modelo Star Schema (`ds_mart`)

### 3.1. Tabela Fato: `fato_indicador` (Particionada por `periodo_ref`, Clusterizada por `id_indicador`, `id_municipio`)
Armazena a série histórica consolidada de todos os indicadores das 40 fontes do catálogo.

| Coluna | Tipo | Chave | Descrição / Regras |
|---|---|---|---|
| `id_registro` | STRING | PK | Hash de identificação única: `hash(indicador+orgao+municipio+periodo)` |
| `id_indicador` | STRING | FK | Slug do indicador (`dim_indicador.id_indicador`) |
| `id_orgao` | STRING | FK | Sigla do órgão (`dim_orgao.id_orgao`), NULL para nível estado |
| `id_municipio` | STRING | FK | Código IBGE 7 dígitos (`dim_municipio.id_municipio`), NULL para nível estadual |
| `periodo_ref` | DATE | PK (Partition) | Data de referência (Partição do BigQuery) |
| `periodicidade` | STRING | — | Periodicidade (Anual, Mensal, Trimestral) |
| `valor_num` | NUMERIC | — | Valor numérico medido |
| `valor_texto` | STRING | — | Valor alfanumérico (ex: CAPAG 'A') |
| `unidade` | STRING | — | Unidade visual de exibição |
| `posicao_ranking` | INT64 | — | Posição no ranking municipal (1º a 139º) |
| `id_fonte` | STRING | FK | ID da fonte no catálogo |
| `esfera_fonte` | STRING | — | `federal` ou `estadual` (RF-12) |
| `dt_coleta` | TIMESTAMP | — | Timestamp da coleta automática pelo pipeline |
| `dt_publicacao_org` | DATE | — | Data oficial de publicação pelo órgão primário |
| `qualidade` | STRING | — | Enum: `ok`, `estimado`, `defasado`, `suspeito`, `sem_dado`, `falho` (RF-55) |
| `calculado` | BOOL | — | `TRUE` se derivado de fórmula matemática |
| `gerado_por_ia` | BOOL | — | `TRUE` se texto/síntese gerado por IA |
| `hash_origem` | STRING | — | Hash SHA-256 do arquivo bruto no Cloud Storage |

### 3.2. Dimensões
1. **`dim_municipio`**: 139 municípios do Tocantins com Chave Canônica de 7 dígitos IBGE (`id_municipio`), nome oficial, nome de exibição, UF, microrregião e mesorregião.
2. **`dim_indicador`**: Réplica de consumo do catálogo de indicadores.
3. **`dim_orgao`**: 11 órgãos da Base Mestre + órgãos federais parceiros.
4. **`dim_fonte`**: Réplica de consumo das 40 fontes catalogadas.
5. **`dim_tempo`**: Calendário de suporte para agregados temporais.

