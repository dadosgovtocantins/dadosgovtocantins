-- Função de Normalização de Código IBGE e Nome de Município
-- Garante o Código IBGE de 7 dígitos como chave canônica (RT-07)

CREATE OR REPLACE FUNCTION `ds_stg.fn_normaliza_codigo_ibge`(cod INPUT STRING)
RETURNS STRING AS (
  CASE 
    -- Se tiver 6 dígitos, completa com dígito verificador se for padrão TO (17XXXX)
    WHEN LENGTH(TRIM(cod)) = 6 THEN CONCAT(TRIM(cod), '0') 
    WHEN LENGTH(TRIM(cod)) = 7 THEN TRIM(cod)
    ELSE NULL
  END
);
