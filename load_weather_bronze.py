"""
Carga da camada Bronze do clima (SmartMarket AI).

Lê os arquivos JSON salvos em data/raw/weather/ pelo script de extração
e insere cada um na tabela bronze.weather_forecast_raw.

A carga é idempotente: rodar o script várias vezes não duplica registros,
porque a tabela tem uma restrição de unicidade por (collected_at, params).
"""

import json
import os
from datetime import datetime
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from psycopg.types.json import Jsonb

RAW_DIR = Path("data/raw/weather")
REQUIRED_KEYS = ("collected_at", "source", "params", "payload")

INSERT_SQL = """
    INSERT INTO bronze.weather_forecast_raw
        (collected_at, source, params, payload, source_file)
    VALUES (%s, %s, %s, %s, %s)
    ON CONFLICT (collected_at, params) DO NOTHING
"""


def get_connection() -> psycopg.Connection:
    """Abre a conexão com o Postgres usando as variáveis do arquivo .env."""
    load_dotenv()
    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )


def read_record(path: Path) -> dict:
    """Lê um arquivo bruto e confere se ele tem o formato esperado."""
    record = json.loads(path.read_text(encoding="utf-8"))

    missing = [key for key in REQUIRED_KEYS if key not in record]
    if missing:
        raise ValueError(f"{path.name}: campos ausentes no arquivo: {missing}")

    return record


def load_file(cursor: psycopg.Cursor, path: Path) -> bool:
    """Insere um arquivo na Bronze. Devolve True se inseriu, False se já existia."""
    record = read_record(path)

    cursor.execute(
        INSERT_SQL,
        (
            datetime.fromisoformat(record["collected_at"]),
            record["source"],
            Jsonb(record["params"]),
            Jsonb(record["payload"]),
            path.name,
        ),
    )
    return cursor.rowcount == 1


def main() -> None:
    files = sorted(RAW_DIR.glob("*.json"))
    if not files:
        print(f"Nenhum arquivo encontrado em {RAW_DIR}")
        return

    inserted = 0
    skipped = 0

    # O bloco "with" abre uma transação: se qualquer arquivo falhar,
    # nada é gravado. Se tudo der certo, o commit acontece ao final.
    with get_connection() as conn:
        with conn.cursor() as cursor:
            for path in files:
                if load_file(cursor, path):
                    inserted += 1
                    print(f"Inserido: {path.name}")
                else:
                    skipped += 1
                    print(f"Já existia, ignorado: {path.name}")

    print(f"\nResumo: {inserted} inserido(s), {skipped} ignorado(s), {len(files)} lido(s)")


if __name__ == "__main__":
    main()
