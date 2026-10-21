-- DDL da Dimensão Fonte: dim_fonte

CREATE TABLE IF NOT EXISTS `ds_mart.dim_fonte` (
  id_fonte                 STRING    NOT NULL OPTIONS(description="ID único da fonte (ex: TO-TER-01)"),
  id_orgao                 STRING    NOT NULL OPTIONS(description="FK para dim_orgao"),
  indicador_fonte          STRING    NOT NULL OPTIONS(description="Nome sintético da fonte/pesquisa"),
  link_publico             STRING             OPTIONS(description="URL pública de consulta"),
  esfera                   STRING    NOT NULL OPTIONS(description="federal | estadual"),
  classificacao            STRING    NOT NULL OPTIONS(description="Classe A, B, C ou D"),
  quadrante                STRING    NOT NULL OPTIONS(description="Q1 ou Q2"),
  restricao_robots_termos  STRING    NOT NULL OPTIONS(description="Registro e data da checagem de robots.txt")
);
