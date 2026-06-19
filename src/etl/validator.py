import pandas as pd


class ValidationFailure:

    def __init__(
        self, rule_id, severity, table_name, company_id, year, field_name, message
    ):
        self.rule_id = rule_id
        self.severity = severity
        self.table_name = table_name
        self.company_id = company_id
        self.year = year
        self.field_name = field_name
        self.message = message

    def to_dict(self):
        return {
            "rule_id": self.rule_id,
            "severity": self.severity,
            "table_name": self.table_name,
            "company_id": self.company_id,
            "year": self.year,
            "field_name": self.field_name,
            "message": self.message,
        }


class DataValidator:

    def __init__(self):
        self.failures = []

    def add_failure(
        self, rule_id, severity, table_name, company_id, year, field_name, message
    ):

        self.failures.append(
            ValidationFailure(
                rule_id, severity, table_name, company_id, year, field_name, message
            )
        )

    def export_failures(self, output_path="output/validation_failures.csv"):

        columns = [
            "rule_id",
            "severity",
            "table_name",
            "company_id",
            "year",
            "field_name",
            "message",
        ]

        rows = [f.to_dict() for f in self.failures]

        pd.DataFrame(
            rows,
            columns=columns
        ).to_csv(
            output_path,
            index=False
        )

    def dq01_company_pk_uniqueness(self, companies_df):

        duplicates = companies_df[companies_df["id"].duplicated()]

        for _, row in duplicates.iterrows():

            self.add_failure(
                "DQ-01",
                "CRITICAL",
                "companies",
                row["id"],
                None,
                "id",
                "Duplicate company primary key",
            )

    def dq02_annual_pk_uniqueness(self, df, table_name):

        duplicates = df[df.duplicated(subset=["company_id", "year"], keep=False)]

        for _, row in duplicates.iterrows():

            self.add_failure(
                "DQ-02",
                "CRITICAL",
                table_name,
                row["company_id"],
                row["year"],
                "(company_id,year)",
                "Duplicate annual record",
            )

    def dq03_fk_integrity(self, companies_df, child_df, table_name):

        valid_ids = set(companies_df["id"])

        invalid_rows = child_df[~child_df["company_id"].isin(valid_ids)]

        for _, row in invalid_rows.iterrows():

            self.add_failure(
                "DQ-03",
                "CRITICAL",
                table_name,
                row["company_id"],
                row.get("year"),
                "company_id",
                "Foreign key not found",
            )

    def dq04_balance_sheet_balance(self, balancesheet_df):

        for _, row in balancesheet_df.iterrows():

            assets = row["total_assets"]
            liabilities = row["total_liabilities"]

            if assets == 0:
                continue

            difference = abs(assets - liabilities) / assets

            if difference > 0.01:

                self.add_failure(
                    "DQ-04",
                    "WARNING",
                    "balancesheet",
                    row["company_id"],
                    row["year"],
                    "total_assets",
                    "Balance sheet mismatch >1%",
                )

    def dq05_opm_crosscheck(self, profit_df):

        for _, row in profit_df.iterrows():

            sales = row["sales"]

            if sales == 0:
                continue

            computed_opm = (row["operating_profit"] / sales) * 100

            difference = abs(computed_opm - row["opm_percentage"])

            if difference > 1:

                self.add_failure(
                    "DQ-05",
                    "WARNING",
                    "profitandloss",
                    row["company_id"],
                    row["year"],
                    "opm_percentage",
                    "OPM mismatch >1%",
                )

    def dq06_positive_sales(self, profit_df):

        invalid_rows = profit_df[profit_df["sales"] <= 0]

        for _, row in invalid_rows.iterrows():

            self.add_failure(
                "DQ-06",
                "WARNING",
                "profitandloss",
                row["company_id"],
                row["year"],
                "sales",
                "Sales must be positive",
            )

    def dq07_year_format(self, df, table_name):
        """
        Validate YYYY-MM format.
        """

        for _, row in df.iterrows():

            year = str(row.get("year", ""))

            if len(year) != 7 or "-" not in year:

                self.add_failure(
                    "DQ-07",
                    "WARNING",
                    table_name,
                    row.get("company_id"),
                    year,
                    "year",
                    "Invalid year format",
                )

    def dq08_ticker_format(self, df, table_name):
        """
        Tickers should be uppercase.
        """

        for _, row in df.iterrows():

            ticker = row.get("company_id")

            if ticker is None:
                continue

            if str(ticker) != str(ticker).upper():

                self.add_failure(
                    "DQ-08",
                    "WARNING",
                    table_name,
                    ticker,
                    row.get("year"),
                    "company_id",
                    "Ticker not uppercase",
                )

    def dq09_net_cash_check(self, cashflow_df):

        for _, row in cashflow_df.iterrows():

            expected = (
                row["operating_activity"]
                + row["investing_activity"]
                + row["financing_activity"]
            )

            actual = row["net_cash_flow"]

            if abs(expected - actual) > 10:

                self.add_failure(
                    "DQ-09",
                    "WARNING",
                    "cashflow",
                    row["company_id"],
                    row["year"],
                    "net_cash_flow",
                    "Net cash flow mismatch >10 Cr",
                )

    def dq10_non_negative_fixed_assets(self, balancesheet_df):

        invalid_rows = balancesheet_df[balancesheet_df["fixed_assets"] < 0]

        for _, row in invalid_rows.iterrows():

            self.add_failure(
                "DQ-10",
                "WARNING",
                "balancesheet",
                row["company_id"],
                row["year"],
                "fixed_assets",
                "Fixed assets cannot be negative",
            )

    def dq11_tax_rate_range(self, profit_df):

        invalid_rows = profit_df[
            (profit_df["tax_percentage"] < 0) | (profit_df["tax_percentage"] > 100)
        ]

        for _, row in invalid_rows.iterrows():

            self.add_failure(
                "DQ-11",
                "WARNING",
                "profitandloss",
                row["company_id"],
                row["year"],
                "tax_percentage",
                "Tax rate outside valid range",
            )

    def dq12_dividend_payout_cap(self, profit_df):

        invalid_rows = profit_df[profit_df["dividend_payout"] > 300]

        for _, row in invalid_rows.iterrows():

            self.add_failure(
                "DQ-12",
                "WARNING",
                "profitandloss",
                row["company_id"],
                row["year"],
                "dividend_payout",
                "Dividend payout unusually high",
            )

    def dq13_url_validity(self, documents_df):

        for _, row in documents_df.iterrows():

            url = str(
                row.get("annual_report", "")
            ).strip()

            if not (url.startswith("http://") or url.startswith("https://")):

                self.add_failure(
                    "DQ-13",
                    "WARNING",
                    "documents",
                    row.get("company_id"),
                    None,
                    "url",
                    "Invalid URL",
                )

    def dq14_eps_sign_consistency(self, profit_df):

        for _, row in profit_df.iterrows():

            profit = row.get("net_profit")
            eps = row.get("eps")

            if pd.notna(profit) and pd.notna(eps):

                if profit > 0 and eps < 0:

                    self.add_failure(
                        "DQ-14",
                        "WARNING",
                        "profitandloss",
                        row["company_id"],
                        row["year"],
                        "eps",
                        "Profit positive but EPS negative",
                    )

                if profit < 0 and eps > 0:

                    self.add_failure(
                        "DQ-14",
                        "WARNING",
                        "profitandloss",
                        row["company_id"],
                        row["year"],
                        "eps",
                        "Profit negative but EPS positive",
                    )

    def dq15_bse_ase_balance(self, analysis_df):

        if (
            "book_value" not in analysis_df.columns
            or "market_price" not in analysis_df.columns
        ):
            return

        for _, row in analysis_df.iterrows():

            book = row["book_value"]
            market = row["market_price"]

            if pd.notna(book) and pd.notna(market) and book > 0:

                ratio = market / book

                if ratio > 50:

                    self.add_failure(
                        "DQ-15",
                        "WARNING",
                        "analysis",
                        row["company_id"],
                        row.get("year"),
                        "market_price",
                        "Extreme market/book ratio",
                    )

    def dq16_coverage_check(self, df, table_name):

        coverage = df.groupby("company_id")["year"].nunique()

        for company_id, years in coverage.items():

            if years < 5:

                self.add_failure(
                    "DQ-16",
                    "WARNING",
                    table_name,
                    company_id,
                    None,
                    "year",
                    "Less than 5 years coverage",
                )


    def get_failures_df(self):

        return pd.DataFrame([failure.to_dict() for failure in self.failures])


    def save_failures(self, path="output/validation_failures.csv"):

        columns = [
            "rule_id",
            "severity",
            "table_name",
            "company_id",
            "year",
            "field_name",
            "message",
        ]

        df = self.get_failures_df()

        if df.empty:
            df = pd.DataFrame(columns=columns)

        df.to_csv(path, index=False)

if __name__ == "__main__":

    validator = DataValidator()

    print("Running DQ checks...")

    validator.save_failures()

    print("validation_failures.csv generated")