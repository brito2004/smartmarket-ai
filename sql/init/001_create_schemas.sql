-- Camadas da arquitetura Medallion implementadas como schemas do Postgres.

CREATE SCHEMA IF NOT EXISTS bronze;  -- dado bruto, como chegou da fonte
CREATE SCHEMA IF NOT EXISTS silver;  -- dado limpo, tipado e padronizado
CREATE SCHEMA IF NOT EXISTS gold;    -- dado pronto para análise e IA

COMMENT ON SCHEMA bronze IS 'Dados brutos, imutáveis, exatamente como recebidos da fonte';
COMMENT ON SCHEMA silver IS 'Dados limpos, tipados, deduplicados e com regras de qualidade aplicadas';
COMMENT ON SCHEMA gold   IS 'Tabelas e métricas de negócio para dashboards, modelos e camada semântica';
