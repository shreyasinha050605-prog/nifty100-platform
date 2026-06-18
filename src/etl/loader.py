from pathlib import Path

import pandas as pd
import sqlite3

from src.etl.normaliser import (
    normalize_ticker,
    normalize_year,
)

CORE_FILES = {
    "companies",
    "profitandloss",
    "balancesheet",
    "cashflow",
    "analysis",
    "documents",
    "prosandcons",
}


class ExcelLoader:

    def load_excel(self, file_path):

        name = Path(file_path).stem.lower()

        header = 1 if name in CORE_FILES else 0

        df = pd.read_excel(file_path, header=header, engine="openpyxl")

        if "company_id" in df.columns:
            df["company_id"] = df["company_id"].apply(normalize_ticker)

        if "id" in df.columns and name == "companies":
            df["id"] = df["id"].apply(normalize_ticker)

        if "year" in df.columns:
            df["year"] = df["year"].apply(normalize_year)

        return df

    def load_all(self, directory):

        directory = Path(directory)

        result = {}

        for file in directory.glob("*.xlsx"):
            result[file.stem] = self.load_excel(file)

        return result


def create_database():
    conn = sqlite3.connect(
        "data/processed/nifty100.db"
    )

    conn.execute(
        "PRAGMA foreign_keys = ON"
    )

    with open(
        "db/schema.sql",
        "r",
        encoding="utf-8"
    ) as f:
        schema = f.read()

    conn.executescript(schema)

    conn.commit()
    conn.close()

    print(
        "Database created successfully"
    )


if __name__ == "__main__":
    create_database()