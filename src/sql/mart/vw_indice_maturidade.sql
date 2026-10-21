-- View SQL de Índice de Maturidade de Dados Abertos por Órgão
CREATE OR REPLACE VIEW `{project_id}.{dataset_mart}.vw_indice_maturidade` AS
SELECT 
    f.id_orgao,
    COUNT(DISTINCT f.id_fonte) AS total_fontes,
    COUNT(DISTINCT CASE WHEN f.classe_reuso IN ('A', 'B') THEN f.id_fonte END) AS fontes_reutilizaveis,
    COUNT(DISTINCT CASE WHEN f.classe_reuso = 'D' THEN f.id_fonte END) AS fontes_apenas_link,
    SAFE_DIVIDE(
        COUNT(DISTINCT CASE WHEN f.classe_reuso IN ('A', 'B') THEN f.id_fonte END) * 100.0,
        COUNT(DISTINCT f.id_fonte)
    ) AS percentual_maturidade,
    CASE 
        WHEN SAFE_DIVIDE(
            COUNT(DISTINCT CASE WHEN f.classe_reuso IN ('A', 'B') THEN f.id_fonte END) * 100.0,
            COUNT(DISTINCT f.id_fonte)
        ) >= 80.0 THEN 'Avançado'
        WHEN SAFE_DIVIDE(
            COUNT(DISTINCT CASE WHEN f.classe_reuso IN ('A', 'B') THEN f.id_fonte END) * 100.0,
            COUNT(DISTINCT f.id_fonte)
        ) >= 50.0 THEN 'Intermediário'
        WHEN SAFE_DIVIDE(
            COUNT(DISTINCT CASE WHEN f.classe_reuso IN ('A', 'B') THEN f.id_fonte END) * 100.0,
            COUNT(DISTINCT f.id_fonte)
        ) > 0.0 THEN 'Inicial'
        ELSE 'Inexistente'
    END AS nivel_maturidade
FROM `{project_id}.{dataset_mart}.dim_fonte` f
GROUP BY f.id_orgao;
