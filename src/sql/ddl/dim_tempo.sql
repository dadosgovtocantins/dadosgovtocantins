-- DDL da Dimensão Tempo: dim_tempo

CREATE TABLE IF NOT EXISTS `ds_mart.dim_tempo` (
  data_ref         DATE      NOT NULL OPTIONS(description="Data de referência (chave)"),
  ano              INT64     NOT NULL OPTIONS(description="Ano ex: 2024"),
  trimestre        INT64     NOT NULL OPTIONS(description="Trimestre 1 a 4"),
  mes              INT64     NOT NULL OPTIONS(description="Mês 1 a 12"),
  nome_mes         STRING    NOT NULL OPTIONS(description="Janeiro, Fevereiro..."),
  semestre         INT64     NOT NULL OPTIONS(description="Semestre 1 ou 2")
);
