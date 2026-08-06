# The purpose of this script is to easily create the sql database without notebooks.

import pandas as pd
from pathlib import Path
from .loaders import load_range
import sqlite3

def build():
    SCRIPT_DIR = Path(__file__).parent
    DATA_DIR = SCRIPT_DIR.parent / "data"

    df = load_range(2000, 1, 2023, 2, data_dir=str(DATA_DIR))

    df.to_parquet(DATA_DIR / "station_data.parquet", index=False)

    connection = sqlite3.connect(DATA_DIR / "station_data.db")
    df.to_sql("weather", con=connection, if_exists="replace", index=False, chunksize=10_000)
    connection.close()
    return


if __name__ == "__main__":
    build()