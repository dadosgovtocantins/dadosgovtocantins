-- DDL da Dimensão Titular: dim_titular (titular eleito em exercício — task 30)
-- Chave canônica: id_titular = '<CARGO>:<id_municipio>' para prefeito
-- (ex: 'PREFEITO:1721000') e 'GOVERNADOR:TO' para o governo estadual.
-- 1 linha por cargo/território: 139 prefeituras + 1 governo estadual = 140.
-- Exceção estreita a RF-11/RNF-S08 (PRD §0.1, docs/identidade.md, 2026-10-14):
-- só nome, cargo, território e retrato de identificação do titular eleito.
-- Nenhum campo de brasão, marca ou paleta institucional existe nesta tabela.
-- Nenhum dado pessoal além do nome público de urna (sem CPF, e-mail, título,
-- nascimento) — minimização aplicada já na extração (RNF-S05).

CREATE TABLE IF NOT EXISTS `ds_mart.dim_titular` (
  id_titular     STRING    NOT NULL OPTIONS(description="Chave canônica '<CARGO>:<id_municipio>' ou 'GOVERNADOR:TO'"),
  id_municipio   STRING             OPTIONS(description="Código IBGE de 7 dígitos; NULL para o governador (nível estadual)"),
  cargo          STRING    NOT NULL OPTIONS(description="PREFEITO | GOVERNADOR"),
  nome_titular   STRING    NOT NULL OPTIONS(description="Nome de urna do titular eleito (NM_URNA_CANDIDATO do TSE)"),
  ano_eleicao    INT64     NOT NULL OPTIONS(description="Ano da eleição que originou o mandato (2024 prefeito, 2022 governador)"),
  sq_candidato   STRING             OPTIONS(description="Sequencial TSE da candidatura — vínculo técnico com o retrato (TO-GER-02)"),
  url_foto       STRING             OPTIONS(description="URL do retrato de identificação; NULL enquanto TO-GER-02 estiver bloqueada (RF-71)"),
  fonte          STRING    NOT NULL OPTIONS(description="TSE | DIVULGACANDCONTAS"),
  id_fonte       STRING    NOT NULL OPTIONS(description="ID da fonte no catalogo_fontes (TO-GER-01 | TO-GER-02)"),
  qualidade      STRING    NOT NULL OPTIONS(description="ok | defasado — falha de coleta preserva o último valor como 'defasado' (RF-66)"),
  hash_origem    STRING    NOT NULL OPTIONS(description="SHA-256 do payload bruto que originou a linha (RF-62)"),
  atualizado_em  TIMESTAMP NOT NULL OPTIONS(description="Momento da coleta/carga da linha")
)
OPTIONS(
  description="Titular eleito em exercício por município (139) e governo estadual (1). Fonte: TSE.",
  labels=[("projeto", "painel-to"), ("ambiente", "ds"), ("modulo", "governanca")]
);
