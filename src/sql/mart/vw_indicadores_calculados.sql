-- View de Indicadores Calculados Derivados
-- Fórmulas publicadas:
-- 1. PIB per Capita = (PIB Municipal em R$ mil * 1000) / População Residente
-- 2. Densidade Demográfica = População Residente / Área km²

CREATE OR REPLACE VIEW `{project_id}.{dataset_mart}.vw_indicadores_calculados` AS
WITH pib AS (
    SELECT id_municipio, periodo_ref, valor_num AS pib_mil_reais, qualidade
    FROM `{project_id}.{dataset_mart}.fato_indicador`
    WHERE id_indicador = 'pib_municipal'
),
pop AS (
    SELECT id_municipio, periodo_ref, valor_num AS populacao, qualidade
    FROM `{project_id}.{dataset_mart}.fato_indicador`
    WHERE id_indicador = 'populacao_residente'
),
area AS (
    SELECT id_municipio, periodo_ref, valor_num AS area_km2, qualidade
    FROM `{project_id}.{dataset_mart}.fato_indicador`
    WHERE id_indicador = 'area_territorial'
)
SELECT 
    CONCAT('pib_per_capita:TO:', p.id_municipio, ':', p.periodo_ref) AS id_registro,
    'pib_per_capita' AS id_indicador,
    p.id_municipio,
    p.periodo_ref,
    SAFE_DIVIDE((p.pib_mil_reais * 1000.0), pop.populacao) AS valor_num,
    'R$/hab' AS unidade,
    TRUE AS calculado,
    FALSE AS gerado_por_ia,
    CASE 
        WHEN p.qualidade = 'sem_dado' OR pop.qualidade = 'sem_dado' THEN 'sem_dado'
        ELSE 'ok'
    END AS qualidade
FROM pib p
INNER JOIN pop ON p.id_municipio = pop.id_municipio AND p.periodo_ref = pop.periodo_ref

UNION ALL

SELECT 
    CONCAT('densidade_demografica:TO:', pop.id_municipio, ':', pop.periodo_ref) AS id_registro,
    'densidade_demografica' AS id_indicador,
    pop.id_municipio,
    pop.periodo_ref,
    SAFE_DIVIDE(pop.populacao, a.area_km2) AS valor_num,
    'hab/km²' AS unidade,
    TRUE AS calculado,
    FALSE AS gerado_por_ia,
    CASE 
        WHEN pop.qualidade = 'sem_dado' OR a.qualidade = 'sem_dado' THEN 'sem_dado'
        ELSE 'ok'
    END AS qualidade
FROM pop
INNER JOIN area a ON pop.id_municipio = a.id_municipio AND pop.periodo_ref = a.periodo_ref;
