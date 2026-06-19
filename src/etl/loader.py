from pathlib import Path

import pandas as pd
import sqlite3
import csv

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

LOAD_ORDER = [
    "companies",
    "profitandloss",
    "balancesheet",
    "cashflow",
    "analysis",
    "documents",
    "prosandcons",
    "sectors",
    "financial_ratios",
    "peer_groups",
    "market_cap",
    "stock_prices",
]

PRIMARY_KEYS = {
    "profitandloss": ["company_id", "year"],
    "balancesheet": ["company_id", "year"],
    "cashflow": ["company_id", "year"],
    "financial_ratios": ["company_id", "year"],
    "documents": ["company_id", "year"],
    "stock_prices": ["company_id", "date"],
    "analysis": ["company_id"],
    "sectors": ["company_id"],
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

def load_data():

    loader = ExcelLoader()

    datasets = loader.load_all("data/raw")

    conn = sqlite3.connect(
        "data/processed/nifty100.db"
    )

    conn.execute(
        "PRAGMA foreign_keys = ON"
    )

    audit_rows = []

    # master company ids
    company_ids = set(
        datasets["companies"]["id"]
    )

    for table in LOAD_ORDER:

        df = datasets[table]

        # remove source-file surrogate ids
        # keep id for companies because it is the PK
        if table != "companies" and "id" in df.columns:
            df = df.drop(columns=["id"])

        # column fixes
        if table == "documents":
            df = df.rename(
                columns={
                    "Year": "year",
                    "Annual_Report": "annual_report",
                }
            )

        if table == "peer_groups":
            df = df.rename(
                columns={
                    "peer_group_name": "peer_group",
                    "is_benchmark": "benchmark_company",
                }
            )
        
        if table in PRIMARY_KEYS:

            before = len(df)

            df = df.drop_duplicates(
                subset=PRIMARY_KEYS[table]
            )

            rejected += before - len(df)

        # track rejected rows
        rejected = 0

        if (
            table != "companies"
            and "company_id" in df.columns
        ):

            before = len(df)

            df = df[
                df["company_id"].isin(company_ids)
            ]

            rejected = before - len(df)

        inserted = len(df)

        df.to_sql(
            table,
            conn,
            if_exists="append",
            index=False,
        )
        
        conn.commit()

        audit_rows.append(
            {
                "table": table,
                "rows_loaded": inserted,
                "rows_rejected": rejected,
            }
        )

        print(
            f"Loaded {table}: {inserted} rows "
            f"(rejected {rejected})"
        )

    conn.commit()
    conn.close()

    with open(
        "output/load_audit.csv",
        "w",
        newline="",
        encoding="utf-8",
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=[
                "table",
                "rows_loaded",
                "rows_rejected",
            ],
        )

        writer.writeheader()
        writer.writerows(audit_rows)

    print(
        "\nload_audit.csv generated"
    )

if __name__ == "__main__":
    create_database()
    load_data()

