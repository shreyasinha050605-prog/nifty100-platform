import re
import pandas as pd


def normalize_ticker(ticker):
    """
    Convert ticker to uppercase and remove extra spaces.
    """

    if pd.isna(ticker):
        return None

    return str(ticker).strip().upper()


def normalize_year(year):
    """
    Convert year labels like:
    Mar-23 -> 2023-03
    Mar-2024 -> 2024-03
    Dec-21 -> 2021-12
    """

    if pd.isna(year):
        return None

    year = str(year).strip()

    months = {
        "JAN": "01",
        "FEB": "02",
        "MAR": "03",
        "APR": "04",
        "MAY": "05",
        "JUN": "06",
        "JUL": "07",
        "AUG": "08",
        "SEP": "09",
        "OCT": "10",
        "NOV": "11",
        "DEC": "12",
    }

    match = re.match(r"([A-Za-z]+)-(\d{2,4})", year)

    if not match:
        return year

    month, yr = match.groups()

    month = months.get(month.upper())

    if len(yr) == 2:
        yr = f"20{yr}"

    return f"{yr}-{month}"
