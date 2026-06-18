import pytest

from src.etl.normaliser import normalize_year, normalize_ticker


@pytest.mark.parametrize(
    "input_year,expected",
    [
        ("Mar-23", "2023-03"),
        ("Mar-24", "2024-03"),
        ("Mar-25", "2025-03"),
        ("Dec-23", "2023-12"),
        ("Dec-24", "2024-12"),
        ("Jan-23", "2023-01"),
        ("Feb-23", "2023-02"),
        ("Apr-23", "2023-04"),
        ("May-23", "2023-05"),
        ("Jun-23", "2023-06"),
        ("Jul-23", "2023-07"),
        ("Aug-23", "2023-08"),
        ("Sep-23", "2023-09"),
        ("Oct-23", "2023-10"),
        ("Nov-23", "2023-11"),
        ("Mar-2024", "2024-03"),
        ("Dec-2024", "2024-12"),
        (" Mar-23 ", "2023-03"),
        (None, None),
        ("2024", "2024"),
    ],
)
def test_normalize_year(input_year, expected):
    assert normalize_year(input_year) == expected


@pytest.mark.parametrize(
    "input_ticker,expected",
    [
        ("tcs", "TCS"),
        ("infy", "INFY"),
        (" hdfcbank ", "HDFCBANK"),
        ("icicibank", "ICICIBANK"),
        ("reliance", "RELIANCE"),
        ("sbin", "SBIN"),
        ("lt", "LT"),
        ("asianpaints", "ASIANPAINTS"),
        ("itc", "ITC"),
        ("nestleind", "NESTLEIND"),
        ("abc", "ABC"),
        ("A b C", "A B C"),
        ("123", "123"),
        ("", ""),
        (None, None),
    ],
)
def test_normalize_ticker(input_ticker, expected):
    assert normalize_ticker(input_ticker) == expected
