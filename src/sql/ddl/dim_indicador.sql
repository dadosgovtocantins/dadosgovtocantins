-- DDL da Dimensão Indicador: dim_indicador
-- Criada e populada a partir da visão ext_catalogo_indicadores (Task 04)

CREATE TABLE IF NOT EXISTS `ds_mart.dim_indicador` (
  id_indicador      STRING    NOT NULL OPTIONS(description="Slug único do indicador atômico"),
  id_fonte          STRING    NOT NULL OPTIONS(description="ID da fonte no catálogo"),
  nome_exibicao     STRING    NOT NULL OPTIONS(description="Rótulo principal do card no Looker"),
  definicao_cidadao STRING             OPTIONS(description="Texto explicativo para tooltip cidadão"),
  unidade           STRING    NOT NULL OPTIONS(description="Unidade única (R$, %, hab, nota)"),
  sentido           STRING    NOT NULL OPTIONS(description="maior_melhor | menor_melhor | neutro"),
  tela              STRING    NOT NULL OPTIONS(description="municipio | estado | orgao"),
  ordem_card        INT64              OPTIONS(description="Posição no grid visual"),
  icone             STRING             OPTIONS(description="Nome do ícone da UI"),
  calculado         BOOL               OPTIONS(description="TRUE se derivado de cálculo"),
  formula           STRING             OPTIONS(description="Fórmula matemática explicativa"),
  status            STRING    NOT NULL OPTIONS(description="ativo | homologacao | descontinuado")
);
