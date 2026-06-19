# Sprint 1 Retrospective

## What Went Well

* ETL pipeline successfully implemented.
* Data normalization functions stabilized.
* SQLite schema finalized.
* Foreign key integrity enforced.
* Unit testing completed successfully.
* Duplicate company-year issues identified and fixed.

## Challenges

* Duplicate rows in profitandloss dataset.
* Foreign key failures during initial loads.
* Dataset inconsistencies across source files.
* Coverage gaps for JIOFIN and analysis datasets.

## Actions Taken

* Added duplicate removal logic.
* Added primary key verification checks.
* Added foreign key validation.
* Re-ran full ETL pipeline.
* Performed manual company review.

## Lessons Learned

* Validate source files before loading.
* Always verify primary keys before insert.
* Build automated verification scripts early.

## Next Sprint Focus

Sprint 2 – Financial Ratio Engine

* Generate 50+ KPIs
* Populate financial_ratios table
* Validate calculations
* Build ratio test suite

# Sprint 1 Review Report

## Project

Nifty 100 Financial Intelligence Platform

## Sprint

Sprint 1 – Data Foundation

## Duration

Day 01 – Day 07

## Objective

Build a fully loaded and validated SQLite database containing all source datasets and establish the ETL foundation for future analytics modules.

## Deliverables Completed

* nifty100.db created
* 12 source datasets processed
* 10 database tables populated
* ETL pipeline implemented
* Schema validation completed
* Data quality checks completed
* load_audit.csv generated
* validation_failures.csv generated
* 35 ETL unit tests passing

## Database Summary

| Metric                  | Value |
| ----------------------- | ----- |
| Companies               | 92    |
| Stock Price Records     | 5520  |
| Profit & Loss Records   | 1164  |
| Balance Sheet Records   | 1140  |
| Cash Flow Records       | 1068  |
| Financial Ratio Records | 1041  |

## Validation Results

* Foreign Key Violations: 0
* Duplicate Primary Keys: 0
* Critical DQ Failures: 0
* Manual Review Completed: Yes

## Exit Criteria

All Sprint 1 exit criteria successfully satisfied.

## Sprint Status

PASS
READY FOR SPRINT 2
