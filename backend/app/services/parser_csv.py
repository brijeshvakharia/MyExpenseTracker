import pandas as pd


def _find_column(columns: list[str], keywords: list[str]) -> str | None:
    """Find a column name that contains any of the given keywords (case-insensitive)."""
    for col in columns:
        for kw in keywords:
            if kw in col.lower():
                return col
    return None


def parse_csv(filepath: str) -> list[dict]:
    """Parse a CSV bank statement and return normalized transactions."""
    df = pd.read_csv(filepath)
    df.columns = [c.strip() for c in df.columns]
    cols = list(df.columns)

    date_col = _find_column(cols, ["date", "transaction date", "posted"])
    desc_col = _find_column(cols, ["description", "memo", "narration", "details", "particulars", "reference"])
    amount_col = _find_column(cols, ["amount", "value"])
    debit_col = _find_column(cols, ["debit", "withdrawal", "dr"])
    credit_col = _find_column(cols, ["credit", "deposit", "cr"])

    if not date_col:
        raise ValueError(f"Could not find a date column. Available columns: {cols}")
    if not desc_col:
        raise ValueError(f"Could not find a description column. Available columns: {cols}")

    transactions = []
    for _, row in df.iterrows():
        date_val = str(row[date_col]).strip()
        desc_val = str(row[desc_col]).strip()

        if amount_col:
            try:
                amount = float(str(row[amount_col]).replace(",", "").replace("$", "").replace("£", "").replace("€", ""))
            except (ValueError, TypeError):
                continue
        elif debit_col and credit_col:
            debit = _parse_amount(row.get(debit_col))
            credit = _parse_amount(row.get(credit_col))
            amount = credit - debit if (credit or debit) else 0
            if amount == 0:
                continue
        else:
            raise ValueError(f"Could not find amount/debit/credit columns. Available columns: {cols}")

        if not date_val or date_val == "nan" or not desc_val or desc_val == "nan":
            continue

        transactions.append({
            "date": _parse_date(date_val),
            "description": desc_val,
            "amount": amount,
            "raw_text": str(row.to_dict()),
        })

    return transactions


def _parse_amount(val) -> float:
    """Parse a monetary amount, returning 0 if empty/invalid."""
    if pd.isna(val):
        return 0.0
    try:
        return abs(float(str(val).replace(",", "").replace("$", "").replace("£", "").replace("€", "")))
    except (ValueError, TypeError):
        return 0.0


def _parse_date(date_str: str) -> str:
    """Try to parse a date string into YYYY-MM-DD format."""
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y", "%m-%d-%Y", "%Y/%m/%d", "%d %b %Y", "%d %B %Y", "%b %d, %Y"):
        try:
            from datetime import datetime
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return date_str
