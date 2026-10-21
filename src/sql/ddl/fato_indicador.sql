-- DDL da Tabela Fato Principal: fato_indicador
-- PRD v4.2 Anexo C | PARTITION BY periodo_ref | CLUSTER BY id_indicador, id_municipio

CREATE TABLE IF NOT EXISTS `ds_mart.fato_indicador` (
  id_registro       STRING    NOT NULL OPTIONS(description="Hash de identificação única: hash(indicador+orgao+municipio+periodo)"),
  id_indicador      STRING    NOT NULL OPTIONS(description="ID atômico do indicador (FK dim_indicador)"),
  id_orgao          STRING             OPTIONS(description="ID do órgão (FK dim_orgao; NULL = nível estadual)"),
  id_municipio      STRING             OPTIONS(description="Código IBGE 7 dígitos (FK dim_municipio; NULL = estadual/geral)"),
  periodo_ref       DATE      NOT NULL OPTIONS(description="Data de referência do período do indicador"),
  periodicidade     STRING    NOT NULL OPTIONS(description="Anual, Mensal, Trimestral, Bienal"),
  valor_num         NUMERIC            OPTIONS(description="Valor numérico do indicador"),
  valor_texto       STRING             OPTIONS(description="Valor em texto (ex: CAPAG 'A')"),
  unidade           STRING             OPTIONS(description="Unidade de medida (R$, %, hab, nota)"),
  posicao_ranking   INT64              OPTIONS(description="Posição no ranking estadual entre os 139 municípios (1º a 139º)"),
  id_fonte          STRING    NOT NULL OPTIONS(description="ID da fonte do catálogo (FK dim_fonte)"),
  esfera_fonte      STRING    NOT NULL OPTIONS(description="Esfera do dado: federal | estadual (RF-12)"),
  dt_coleta         TIMESTAMP NOT NULL OPTIONS(description="Timestamp da coleta do dado pelo pipeline"),
  dt_publicacao_org DATE               OPTIONS(description="Data oficial de publicação pelo órgão primário"),
  qualidade         STRING    NOT NULL OPTIONS(description="Enum de integridade: ok | estimado | defasado | suspeito | sem_dado | falho"),
  calculado         BOOL               OPTIONS(description="TRUE se o indicador for derivado de fórmula"),
  gerado_por_ia     BOOL               OPTIONS(description="TRUE se texto gerado por IA"),
  hash_origem       STRING             OPTIONS(description="Hash SHA-256 da payload bruta no Cloud Storage")
)
PARTITION BY periodo_ref
CLUSTER BY id_indicador, id_municipio;
