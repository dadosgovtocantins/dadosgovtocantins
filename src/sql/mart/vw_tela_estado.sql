-- View de consumo para Tela Estado
-- Exibe indicadores em nível estadual do Tocantins
CREATE OR REPLACE VIEW `{project_id}.{dataset_mart}.vw_tela_estado` AS
SELECT 
    f.id_registro,
    f.id_indicador,
    i.nome_indicador,
    i.categoria,
    f.periodo_ref,
    f.periodicidade,
    f.valor_num,
    f.valor_texto,
    f.unidade,
    f.id_fonte,
    f.esfera_fonte,
    f.dt_coleta,
    f.qualidade,
    f.calculado,
    f.gerado_por_ia
FROM `{project_id}.{dataset_mart}.fato_indicador` f
INNER JOIN `{project_id}.{dataset_mart}.dim_indicador` i 
    ON f.id_indicador = i.id_indicador
WHERE f.id_municipio IS NULL;
