# Sprint 1 – Day 6 Manual Data Quality Review

## Objective

Perform a manual review of the loaded SQLite database after completion of the ETL pipeline and full data load. The goal is to verify data completeness, integrity, coverage, and consistency before Sprint 1 sign-off.

---

## Review Date

Day 6 – Sprint 1 (Data Foundation)

## Database Reviewed

`data/processed/nifty100.db`

---

## Validation Activities Performed

### 1. Row Count Verification

All tables were verified after loading:

| Table            | Rows Loaded |
| ---------------- | ----------: |
| companies        |          92 |
| profitandloss    |        1164 |
| balancesheet     |        1140 |
| cashflow         |        1068 |
| analysis         |           4 |
| documents        |        1456 |
| prosandcons      |          14 |
| sectors          |          92 |
| financial_ratios |        1041 |
| peer_groups      |          56 |
| market_cap       |         552 |
| stock_prices     |        5520 |

Result: PASS

---

### 2. Foreign Key Integrity Verification

Executed:

```sql
PRAGMA foreign_key_check;
```

Result:

```text
0 rows returned
```

Result: PASS

All child records reference valid companies.

---

### 3. Duplicate Company-Year Verification

Checked for duplicate composite keys:

* profitandloss
* balancesheet
* cashflow
* financial_ratios

Result:

No duplicate `(company_id, year)` combinations found.

Result: PASS

---

### 4. Random Company Sampling Review

Five companies were randomly selected for manual inspection.

| Company ID | Company Name         | Years Available |
| ---------- | -------------------- | --------------: |
| HEROMOTOCO | Hero MotoCorp Ltd    |              12 |
| CANBK      | Canara Bank          |              13 |
| JSWENERGY  | JSW Energy Ltd       |              13 |
| PNB        | Punjab National Bank |              13 |
| ABB        | Abbott India Ltd     |              13 |

Result: PASS

Historical records appear complete and correctly linked.

---

### 5. Year Coverage Analysis

Coverage was calculated using the Profit & Loss dataset.

Observation:

* Majority of companies contain 10–13 years of historical financial data.
* No unexpected coverage gaps detected.

Result: PASS

---

### 6. Companies With Less Than 5 Years History

Identified:

| Company ID | Years |
| ---------- | ----: |
| JIOFIN     |     3 |

Manual investigation performed.

Reason:
Jio Financial Services is a recently listed company and therefore naturally contains fewer historical records.

This is a business-data limitation and not an ETL defect.

Result: ACCEPTED

---

### 7. Companies Missing Profit & Loss Data

Verification performed against the master company table.

Result:


No companies missing P&L records.

Result: PASS

---

### 8. Loader Bug Resolution Review

Issues discovered during Day 5:

* Foreign key failures
* Duplicate company-year records
* Missing company mappings
* Excel loading inconsistencies

Actions taken:

* Normalized company IDs
* Removed duplicate records before loading
* Filtered orphan company references
* Corrected column mappings
* Re-ran complete database load

Result: RESOLVED

---

## Day 6 Review Conclusion

All manual review activities defined for Sprint 1 Day 6 were completed successfully.

Summary:

* Database loads successfully
* Foreign key integrity maintained
* Duplicate records removed
* Historical coverage reviewed
* Low-coverage companies investigated
* Random company validation completed
* Loader issues fixed and re-tested

Overall Status: PASS

Recommendation:
Sprint 1 Day 6 can be marked as completed and approved. Proceed to Day 7 (Sprint Wrap-Up and Final Review).
