-- DDL da Dimensão Órgão: dim_orgao (11 órgãos referenciados na Base Mestre)

CREATE TABLE IF NOT EXISTS `ds_mart.dim_orgao` (
  id_orgao          STRING    NOT NULL OPTIONS(description="Sigla única do órgão (ex: SEPLAN, SEFAZ, SEDUC)"),
  nome_orgao        STRING    NOT NULL OPTIONS(description="Nome completo da instituição"),
  esfera            STRING    NOT NULL OPTIONS(description="estadual | federal"),
  possui_api        BOOL               OPTIONS(description="TRUE se expõe API pública estruturada (Classe A/B)")
);

INSERT INTO `ds_mart.dim_orgao` (id_orgao, nome_orgao, esfera, possui_api)
SELECT * FROM UNNEST([
  STRUCT('SEPLAN' AS id_orgao, 'Secretaria do Planejamento e Orçamento' AS nome_orgao, 'estadual' AS esfera, FALSE AS possui_api),
  STRUCT('SEFAZ' AS id_orgao, 'Secretaria da Fazenda' AS nome_orgao, 'estadual' AS esfera, FALSE AS possui_api),
  STRUCT('CGE-TO' AS id_orgao, 'Controladoria-Geral do Estado do Tocantins' AS nome_orgao, 'estadual' AS esfera, FALSE AS possui_api),
  STRUCT('ATI-TO' AS id_orgao, 'Agência de Tecnologia da Informação' AS nome_orgao, 'estadual' AS esfera, FALSE AS possui_api),
  STRUCT('SEDUC-TO' AS id_orgao, 'Secretaria da Educação' AS nome_orgao, 'estadual' AS esfera, FALSE AS possui_api),
  STRUCT('SSP-TO' AS id_orgao, 'Secretaria da Segurança Pública' AS nome_orgao, 'estadual' AS esfera, FALSE AS possui_api),
  STRUCT('SECTUR' AS id_orgao, 'Secretaria da Cultura e Turismo' AS nome_orgao, 'estadual' AS esfera, FALSE AS possui_api),
  STRUCT('AGETO' AS id_orgao, 'Agência Tocantinense de Transportes e Obras' AS nome_orgao, 'estadual' AS esfera, FALSE AS possui_api),
  STRUCT('SEAGRO' AS id_orgao, 'Secretaria da Agricultura, Pecuária e Aquicultura' AS nome_orgao, 'estadual' AS esfera, FALSE AS possui_api),
  STRUCT('TCE-TO' AS id_orgao, 'Tribunal de Contas do Estado do Tocantins' AS nome_orgao, 'estadual' AS esfera, FALSE AS possui_api),
  STRUCT('DOE-TO' AS id_orgao, 'Diário Oficial do Estado do Tocantins' AS nome_orgao, 'estadual' AS esfera, FALSE AS possui_api),
  STRUCT('IBGE' AS id_orgao, 'Instituto Brasileiro de Geografia e Estatística' AS nome_orgao, 'federal' AS esfera, TRUE AS possui_api),
  STRUCT('DATASUS' AS id_orgao, 'Departamento de Informática do SUS' AS nome_orgao, 'federal' AS esfera, TRUE AS possui_api),
  STRUCT('STN' AS id_orgao, 'Secretaria do Tesouro Nacional' AS nome_orgao, 'federal' AS esfera, TRUE AS possui_api)
])
WHERE NOT EXISTS (SELECT 1 FROM `ds_mart.dim_orgao` WHERE id_orgao = 'SEPLAN');
