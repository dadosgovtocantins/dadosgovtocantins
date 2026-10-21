-- Procedure de Snapshot Diário para ds_mart
-- Retenção de 30 dias em dataset de backup isolado (PRD §12.5)

CREATE PROCEDURE IF NOT EXISTS `ds_mart.sp_gerar_snapshot_diario`()
BEGIN
  DECLARE data_hoje STRING;
  SET data_hoje = FORMAT_DATE('%Y%m%d', CURRENT_DATE());
  
  -- Cria snapshot do fato_indicador no dataset de backup
  EXECUTE IMMEDIATE FORMAT("""
    CREATE OR REPLACE TABLE `ds_backup.fato_indicador_snap_%s`
    CLONE `ds_mart.fato_indicador`
    OPTIONS(expiration_timestamp = TIMESTAMP_ADD(CURRENT_TIMESTAMP(), INTERVAL 30 DAY));
  """, data_hoje);
END;
