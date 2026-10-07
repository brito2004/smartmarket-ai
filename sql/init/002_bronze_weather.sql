-- Bronze: respostas brutas da API Open-Meteo (endpoint /v1/forecast).
-- Cada linha é UMA chamada à API, com o JSON completo da resposta.

CREATE TABLE IF NOT EXISTS bronze.weather_forecast_raw (
    id            BIGSERIAL    PRIMARY KEY,
    collected_at  TIMESTAMPTZ  NOT NULL,                -- quando a API foi consultada
    source        TEXT         NOT NULL,                -- URL do endpoint
    params        JSONB        NOT NULL,                -- parâmetros usados na chamada
    payload       JSONB        NOT NULL,                -- resposta completa da API
    source_file   TEXT         NOT NULL,                -- arquivo de origem do registro
    loaded_at     TIMESTAMPTZ  NOT NULL DEFAULT now(),  -- quando entrou no banco

    -- Idempotência: a mesma coleta, com os mesmos parâmetros, só entra uma vez.
    CONSTRAINT uq_weather_forecast_raw UNIQUE (collected_at, params)
);

COMMENT ON TABLE bronze.weather_forecast_raw IS
    'Respostas brutas da API Open-Meteo /v1/forecast, uma linha por chamada';
