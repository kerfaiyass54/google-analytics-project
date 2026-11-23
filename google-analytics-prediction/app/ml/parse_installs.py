import pandas as pd


def parse_installs(value) -> int | None:
    if value is None or pd.isna(value):
        return None
    digits = (
        str(value)
        .replace(",", "")
        .replace("+", "")
        .strip()
    )
    return int(digits) if digits.isdigit() else None
