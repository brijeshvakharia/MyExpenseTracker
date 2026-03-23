import pandas as pd

from app.services.parser_csv import _find_column, _parse_amount, _parse_date


def parse_xlsx(filepath: str) -> list[dict]:
    """Parse an Excel bank statement and return normalized transactions."""
    df = pd.read_excel(filepath, engine="openpyxl")
    df.columns = [str(c).strip() for c in df.columns]
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
