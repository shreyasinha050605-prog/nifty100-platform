import sqlite3
import pandas as pd
import random

DB = "data/processed/nifty100.db"

conn = sqlite3.connect(DB)

print("\n" + "=" * 70)
print("DAY 6 MANUAL REVIEW")
print("=" * 70)

# --------------------------------------------------
# 1. Row counts
# --------------------------------------------------

print("\nROW COUNTS\n")

tables = [
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
    "stock_prices"
]

for table in tables:
    count = pd.read_sql_query(
        f"SELECT COUNT(*) AS cnt FROM {table}",
        conn
    ).iloc[0]["cnt"]

    print(f"{table:<20} {count}")

# --------------------------------------------------
# 2. FK integrity
# --------------------------------------------------

print("\n" + "=" * 70)
print("FOREIGN KEY CHECK")
print("=" * 70)

fk = pd.read_sql_query(
    "PRAGMA foreign_key_check",
    conn
)

if len(fk) == 0:
    print("PASS")
else:
    print("FAIL")
    print(fk)

# --------------------------------------------------
# 3. Duplicate company-year check
# --------------------------------------------------

print("\n" + "=" * 70)
print("DUPLICATE COMPANY-YEAR CHECK")
print("=" * 70)

for table in [
    "profitandloss",
    "balancesheet",
    "cashflow",
    "financial_ratios"
]:

    q = f"""
    SELECT company_id,
           year,
           COUNT(*) AS cnt
    FROM {table}
    GROUP BY company_id, year
    HAVING COUNT(*) > 1
    """

    dup = pd.read_sql_query(q, conn)

    print(f"\n{table}")

    if len(dup) == 0:
        print("PASS")
    else:
        print(f"FAIL ({len(dup)} duplicates)")
        print(dup.head())

# --------------------------------------------------
# 4. 5 random companies
# --------------------------------------------------

print("\n" + "=" * 70)
print("5 RANDOM COMPANY REVIEW")
print("=" * 70)

companies = pd.read_sql_query(
    """
    SELECT id, company_name
    FROM companies
    """,
    conn
)

sample = companies.sample(
    n=5,
    random_state=42
)

for _, row in sample.iterrows():

    cid = row["id"]

    years = pd.read_sql_query(
        f"""
        SELECT COUNT(*) AS cnt
        FROM profitandloss
        WHERE company_id='{cid}'
        """,
        conn
    ).iloc[0]["cnt"]

    print(
        f"{cid:<15} "
        f"{row['company_name'][:40]:<40} "
        f"Years={years}"
    )

# --------------------------------------------------
# 5. Year coverage
# --------------------------------------------------

print("\n" + "=" * 70)
print("YEAR COVERAGE")
print("=" * 70)

coverage = pd.read_sql_query(
    """
    SELECT
        company_id,
        COUNT(*) AS years
    FROM profitandloss
    GROUP BY company_id
    ORDER BY years DESC
    """,
    conn
)

print(coverage.head(10))

# --------------------------------------------------
# 6. Companies with <5 years
# --------------------------------------------------

print("\n" + "=" * 70)
print("COMPANIES WITH < 5 YEARS")
print("=" * 70)

few_years = coverage[
    coverage["years"] < 5
]

if len(few_years) == 0:
    print("PASS")
else:
    print(few_years)

# --------------------------------------------------
# 7. Missing companies
# --------------------------------------------------

print("\n" + "=" * 70)
print("COMPANIES WITH NO P&L DATA")
print("=" * 70)

missing = pd.read_sql_query(
    """
    SELECT c.id
    FROM companies c
    LEFT JOIN profitandloss p
      ON c.id = p.company_id
    WHERE p.company_id IS NULL
    """,
    conn
)

if len(missing) == 0:
    print("PASS")
else:
    print(missing)

# --------------------------------------------------
# 8. Summary
# --------------------------------------------------

print("\n" + "=" * 70)
print("DAY 6 SUMMARY")
print("=" * 70)

print(f"Companies             : {len(companies)}")
print(f"Coverage records      : {len(coverage)}")
print(f"Companies <5 years    : {len(few_years)}")
print(f"Companies missing P&L : {len(missing)}")

conn.close()

