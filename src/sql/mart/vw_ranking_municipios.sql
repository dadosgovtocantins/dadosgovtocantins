-- View de ranking municipal (1º ao 139º) e variação histórica
CREATE OR REPLACE VIEW `{project_id}.{dataset_mart}.vw_ranking_municipios` AS
WITH dados_ordenados AS (
    SELECT 
        f.id_indicador,
        f.id_municipio,
        m.nome_municipio,
        f.periodo_ref,
        f.valor_num,
        f.unidade,
        f.qualidade,
        DENSE_RANK() OVER (
            PARTITION BY f.id_indicador, f.periodo_ref 
            ORDER BY f.valor_num DESC
        ) AS posicao_ranking,
        LAG(f.valor_num) OVER (
            PARTITION BY f.id_indicador, f.id_municipio 
            ORDER BY f.periodo_ref ASC
        ) AS valor_anterior
    FROM `{project_id}.{dataset_mart}.fato_indicador` f
    INNER JOIN `{project_id}.{dataset_mart}.dim_municipio` m 
        ON f.id_municipio = m.id_municipio
    WHERE f.id_municipio IS NOT NULL 
      AND f.qualidade = 'ok'
)
SELECT 
    id_indicador,
    id_municipio,
    nome_municipio,
    periodo_ref,
    valor_num,
    unidade,
    posicao_ranking,
    valor_anterior,
    SAFE_DIVIDE((valor_num - valor_anterior), valor_anterior) * 100 AS variacao_percentual
FROM dados_ordenados;
