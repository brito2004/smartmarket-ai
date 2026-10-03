"""
Teste de extração da API Open-Meteo (SmartMarket AI).

Faz uma chamada ao endpoint /v1/forecast, imprime a resposta JSON
e salva o JSON bruto em data/raw/weather/, com a data da coleta no nome.
"""

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

URL = "https://api.open-meteo.com/v1/forecast"
TIMEZONE = "America/Sao_Paulo"

# Coordenadas de exemplo (centro de São Paulo). Troque pelas da loja.
LATITUDE = -23.55
LONGITUDE = -46.63

DAILY_VARIABLES = [
    "temperature_2m_max",
    "temperature_2m_mean",
    "temperature_2m_min",
    "apparent_temperature_max",
    "precipitation_sum",
    "precipitation_probability_max",
    "weather_code",
]

PARAMS = {
    "latitude": LATITUDE,
    "longitude": LONGITUDE,
    "daily": ",".join(DAILY_VARIABLES),
    "timezone": TIMEZONE,
    "past_days": 3,
    "forecast_days": 8,
}

OUTPUT_DIR = Path("data/raw/weather")


def fetch_weather() -> dict:
    """Chama a API e devolve a resposta como dicionário."""
    response = requests.get(URL, params=PARAMS, timeout=30)

    # 400 = parâmetro errado: não adianta tentar de novo, é bug no pedido.
    if response.status_code == 400:
        reason = response.json().get("reason", "motivo não informado")
        raise ValueError(f"Parâmetro inválido na chamada à API: {reason}")

    # Qualquer outro erro HTTP (429, 5xx...) interrompe a execução.
    response.raise_for_status()
    return response.json()


def save_raw(payload: dict, collected_at: datetime) -> Path:
    """Salva a resposta bruta junto com os metadados da coleta."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    file_path = OUTPUT_DIR / f"forecast_{collected_at:%Y%m%dT%H%M%S}.json"

    record = {
        "collected_at": collected_at.isoformat(),
        "source": URL,
        "params": PARAMS,
        "payload": payload,
    }

    file_path.write_text(
        json.dumps(record, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return file_path


def main() -> None:
    collected_at = datetime.now(ZoneInfo(TIMEZONE))
    payload = fetch_weather()

    print(json.dumps(payload, ensure_ascii=False, indent=2))

    file_path = save_raw(payload, collected_at)
    print(f"\nJSON bruto salvo em: {file_path}")


if __name__ == "__main__":
    main()
