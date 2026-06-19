# verify_sprint1.py
from __future__ import annotations

import re
import sqlite3
import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent

DB_PATH = ROOT / "data" / "processed" / "nifty100.db"
LOAD_AUDIT_PATH = ROOT / "output" / "load_audit.csv"
VALIDATION_FAILURES_PATH = ROOT / "output" / "validation_failures.csv"
SCHEMA_PATH = ROOT / "db" / "schema.sql"
LOADER_PATH = ROOT / "src" / "etl" / "loader.py"
NORMALISER_PATH = ROOT / "src" / "etl" / "normaliser.py"
VALIDATOR_PATH = ROOT / "src" / "etl" / "validator.py"

EXPECTED_COUNTS = {
    "companies": 92,
    "stock_prices": 5520,
}

ALL_TABLES = [
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

PK_CHECKS = {
    "profitandloss": ["company_id", "year"],
    "balancesheet": ["company_id", "year"],
    "cashflow": ["company_id", "year"],
    "financial_ratios": ["company_id", "year"],
    "documents": ["company_id", "year"],
    "stock_prices": ["company_id", "date"],
    "analysis": ["company_id"],
    "sectors": ["company_id"],
    "market_cap": ["company_id", "year"],
    "peer_groups": ["company_id", "peer_group"],
    "companies": ["id"],
    "prosandcons": ["id"],
}

failures: list[str] = []


def pass_msg(message: str) -> None:
    print(f"PASS: {message}")


def warn_msg(message: str) -> None:
    print(f"WARN: {message}")


def fail_msg(message: str) -> None:
    print(f"FAIL: {message}")
    failures.append(message)


def require_file(path: Path, label: str) -> None:
    if path.exists():
        pass_msg(f"{label} exists")
    else:
        fail_msg(f"{label} is missing: {path}")


def read_sql(
    conn: sqlite3.Connection,
    query: str,
    params=None
) -> pd.DataFrame:

    return pd.read_sql_query(
        query,
        conn,
        params=params
    )


def find_col(df: pd.DataFrame, candidates: list[str]) -> str | None:
    cols = {c.lower(): c for c in df.columns}
    for candidate in candidates:
        if candidate.lower() in cols:
            return cols[candidate.lower()]
    return None


def check_code_markers(path: Path, label: str, markers: list[str]) -> None:
    if not path.exists():
        fail_msg(f"{label} missing, cannot verify markers")
        return

    text = path.read_text(encoding="utf-8", errors="ignore")

    missing = []
    for marker in markers:
        if not re.search(marker, text, flags=re.IGNORECASE | re.MULTILINE):
            missing.append(marker)

    if missing:
        fail_msg(f"{label} missing markers: {missing}")
    else:
        pass_msg(f"{label} contains required markers")


def main() -> int:
    print("\n" + "=" * 80)
    print("SPRINT 1 ONE-SHOT VERIFICATION")
    print("=" * 80)

    # ------------------------------------------------------------------
    # File existence checks
    # ------------------------------------------------------------------
    print("\nFILES")
    require_file(DB_PATH, "SQLite database")
    require_file(LOAD_AUDIT_PATH, "load_audit.csv")
    require_file(VALIDATION_FAILURES_PATH, "validation_failures.csv")
    require_file(SCHEMA_PATH, "db/schema.sql")
    require_file(LOADER_PATH, "src/etl/loader.py")
    require_file(NORMALISER_PATH, "src/etl/normaliser.py")
    require_file(VALIDATOR_PATH, "src/etl/validator.py")

    # ------------------------------------------------------------------
    # Code marker checks
    # ------------------------------------------------------------------
    print("\nCODE MARKERS")
    check_code_markers(
        NORMALISER_PATH,
        "normaliser.py",
        [
            r"\bnormalize_year\b",
            r"\bnormalize_ticker\b",
        ],
    )

    check_code_markers(
        VALIDATOR_PATH,
        "validator.py",
        [rf"\bdq[-_]?0?{i}\b" for i in range(1, 17)],
    )

    # ------------------------------------------------------------------
    # Database checks
    # ------------------------------------------------------------------
    if DB_PATH.exists():
        conn = sqlite3.connect(DB_PATH)
        try:
            print("\nDATABASE")

            for table, expected in EXPECTED_COUNTS.items():
                count = int(
                    read_sql(conn, f"SELECT COUNT(*) AS cnt FROM {table}")
                    .iloc[0]["cnt"]
                )
                if count == expected:
                    pass_msg(f"{table} row count = {count}")
                else:
                    fail_msg(f"{table} row count = {count}, expected {expected}")

            # all table names present
            tables_df = read_sql(
                conn,
                """
                SELECT name
                FROM sqlite_master
                WHERE type='table'
                ORDER BY name
                """,
            )
            loaded_tables = set(tables_df["name"].tolist())
            missing_tables = [t for t in ALL_TABLES if t not in loaded_tables]
            if missing_tables:
                fail_msg(f"Missing tables in SQLite: {missing_tables}")
            else:
                pass_msg("All expected tables exist in SQLite")

            # foreign keys
            fk = read_sql(conn, "PRAGMA foreign_key_check")
            if len(fk) == 0:
                pass_msg("Foreign key check returned 0 rows")
            else:
                fail_msg(f"Foreign key check returned {len(fk)} rows")
                print(fk.head(20).to_string(index=False))

            # duplicate key checks
            print("\nDUPLICATE PRIMARY KEY CHECKS")
            for table, keys in PK_CHECKS.items():
                cols = ", ".join(keys)
                group_cols = ", ".join(keys)
                dup_q = f"""
                    SELECT {group_cols}, COUNT(*) AS cnt
                    FROM {table}
                    GROUP BY {group_cols}
                    HAVING COUNT(*) > 1
                """
                dup = read_sql(conn, dup_q)
                if len(dup) == 0:
                    pass_msg(f"{table}: no duplicate {cols}")
                else:
                    fail_msg(f"{table}: {len(dup)} duplicate key groups found")
                    print(dup.head(10).to_string(index=False))

            # random manual review sample
            print("\nRANDOM COMPANY REVIEW")
            companies = read_sql(
                conn,
                """
                SELECT id, company_name
                FROM companies
                ORDER BY id
                """,
            )
            sample = companies.sample(n=5, random_state=42)

            for _, row in sample.iterrows():
                cid = row["id"]
                years = int(
                    read_sql(
                        conn,
                        """
                        SELECT COUNT(DISTINCT year) AS cnt
                        FROM profitandloss
                        WHERE company_id = ?
                        """,
                        params=[cid]
                    ).iloc[0]["cnt"]
                )
                print(f"{cid:<15} {row['company_name'][:45]:<45} years={years}")

            # coverage
            print("\nYEAR COVERAGE")
            coverage = read_sql(
                conn,
                """
                SELECT company_id, COUNT(DISTINCT year) AS years
                FROM profitandloss
                GROUP BY company_id
                ORDER BY years DESC, company_id
                """,
            )
            print(coverage.head(10).to_string(index=False))

            low_coverage = coverage[coverage["years"] < 5]
            if len(low_coverage) == 0:
                pass_msg("No companies have fewer than 5 years of P&L data")
            else:
                warn_msg("Companies with fewer than 5 years of P&L data:")
                print(low_coverage.to_string(index=False))

            # expected low-coverage company check
            jiofin = read_sql(
                conn,
                """
                SELECT company_id, year, sales, expenses, operating_profit,
                       opm_percentage, other_income, interest, depreciation,
                       profit_before_tax, tax_percentage, net_profit, eps,
                       dividend_payout
                FROM profitandloss
                WHERE company_id = 'JIOFIN'
                ORDER BY year
                """,
            )
            if len(jiofin) > 0:
                pass_msg(f"JIOFIN records found ({len(jiofin)} rows)")
                print(jiofin.to_string(index=False))
            else:
                fail_msg("JIOFIN records not found")

            # companies with no P&L data
            missing_pl = read_sql(
                conn,
                """
                SELECT c.id
                FROM companies c
                LEFT JOIN profitandloss p
                  ON c.id = p.company_id
                WHERE p.company_id IS NULL
                ORDER BY c.id
                """,
            )
            if len(missing_pl) == 0:
                pass_msg("No companies missing P&L data")
            else:
                fail_msg(f"{len(missing_pl)} companies missing P&L data")
                print(missing_pl.to_string(index=False))

            # load_audit summary
            print("\nLOAD AUDIT")
            if LOAD_AUDIT_PATH.exists():
                audit = pd.read_csv(LOAD_AUDIT_PATH)
                print(audit.to_string(index=False))

                rejected_col = find_col(audit, ["rows_rejected", "rejected"])
                if rejected_col:
                    total_rejected = int(pd.to_numeric(audit[rejected_col], errors="coerce").fillna(0).sum())
                    print(f"\nTotal rows rejected in load_audit.csv: {total_rejected}")
                else:
                    warn_msg("load_audit.csv has no rows_rejected column")
            else:
                fail_msg("load_audit.csv not found")

            # validation_failures summary
            print("\nVALIDATION FAILURES")
            if VALIDATION_FAILURES_PATH.exists():
                vf = pd.read_csv(VALIDATION_FAILURES_PATH)
                print(f"validation_failures.csv rows: {len(vf)}")
                sev_col = find_col(vf, ["severity", "level"])
                if sev_col:
                    critical = vf[vf[sev_col].astype(str).str.upper().eq("CRITICAL")]
                    print(f"CRITICAL failures: {len(critical)}")
                    if len(critical) == 0:
                        pass_msg("No CRITICAL validation failures remain")
                    else:
                        fail_msg(f"{len(critical)} CRITICAL validation failures remain")
                        print(critical.to_string(index=False))
                else:
                    warn_msg("validation_failures.csv has no severity/level column to inspect")
            else:
                fail_msg("validation_failures.csv not found")

            # pytest verification
            print("\nPYTEST CHECK")
            pytest_cmd = [sys.executable, "-m", "pytest", "tests/etl", "-q"]
            result = subprocess.run(
                pytest_cmd,
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            print(result.stdout)
            if result.returncode == 0:
                pass_msg("pytest tests/etl passed")
            else:
                fail_msg("pytest tests/etl failed")
                if result.stderr.strip():
                    print(result.stderr)

        finally:
            conn.close()

    print("\n" + "=" * 80)
    if failures:
        print("OVERALL RESULT: FAIL")
        print(f"Total failures: {len(failures)}")
        for item in failures:
            print(f"- {item}")
        return 1

    print("OVERALL RESULT: PASS")
    print("Sprint 1 is complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())