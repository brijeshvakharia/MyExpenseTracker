import pdfplumber

from app.services.parser_csv import _parse_date


def parse_pdf(filepath: str) -> list[dict]:
    """Parse a PDF bank statement. Attempts table extraction first, falls back to raw text."""
    transactions = []

    with pdfplumber.open(filepath) as pdf:
        all_text_lines = []

        for page in pdf.pages:
            tables = page.extract_tables()
            if tables:
                for table in tables:
                    transactions.extend(_parse_table(table))
            else:
                text = page.extract_text()
                if text:
                    all_text_lines.append(text)

        # If no tables were found, try to parse from raw text
        if not transactions and all_text_lines:
            full_text = "\n".join(all_text_lines)
            transactions = _parse_text_lines(full_text)

    return transactions


def _parse_table(table: list[list]) -> list[dict]:
    """Parse a table extracted from PDF. First row is assumed to be headers."""
    if not table or len(table) < 2:
        return []

    headers = [str(h).lower().strip() if h else "" for h in table[0]]

    date_idx = _find_idx(headers, ["date", "transaction date", "posted"])
    desc_idx = _find_idx(headers, ["description", "memo", "narration", "details", "particulars"])
    amount_idx = _find_idx(headers, ["amount", "value"])
    debit_idx = _find_idx(headers, ["debit", "withdrawal", "dr"])
    credit_idx = _find_idx(headers, ["credit", "deposit", "cr"])

    if date_idx is None or desc_idx is None:
        return []

    transactions = []
    for row in table[1:]:
        if len(row) <= max(filter(None, [date_idx, desc_idx, amount_idx, debit_idx, credit_idx]), default=0):
            continue

        date_val = str(row[date_idx]).strip() if row[date_idx] else ""
        desc_val = str(row[desc_idx]).strip() if row[desc_idx] else ""

        if not date_val or not desc_val:
            continue

        if amount_idx is not None and row[amount_idx]:
            try:
                amount = float(str(row[amount_idx]).replace(",", "").replace("$", "").replace("£", "").replace("€", ""))
            except (ValueError, TypeError):
                continue
        elif debit_idx is not None and credit_idx is not None:
            debit = _safe_float(row[debit_idx]) if debit_idx < len(row) else 0
            credit = _safe_float(row[credit_idx]) if credit_idx < len(row) else 0
            amount = credit - debit if (credit or debit) else 0
            if amount == 0:
                continue
        else:
            continue

        transactions.append({
            "date": _parse_date(date_val),
            "description": desc_val,
            "amount": amount,
            "raw_text": " | ".join(str(c) for c in row),
        })

    return transactions


def _parse_text_lines(text: str) -> list[dict]:
    """Attempt to parse transactions from raw PDF text. Basic heuristic approach."""
    import re

    transactions = []
    date_pattern = re.compile(r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})")

    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue

        date_match = date_pattern.search(line)
        if not date_match:
            continue

        # Try to find an amount (number with optional decimal)
        amounts = re.findall(r"[-]?\d[\d,]*\.?\d*", line)
        if not amounts:
            continue

        date_str = date_match.group(1)
        # Use the last number as the amount (typically rightmost)
        amount_str = amounts[-1].replace(",", "")
        try:
            amount = float(amount_str)
        except ValueError:
            continue

        # Everything between date and amount is the description
        desc = line[date_match.end():].strip()
        # Remove the amount from description
        desc = desc.replace(amounts[-1], "").strip()
        desc = re.sub(r"\s+", " ", desc).strip(" -|")

        if desc and len(desc) > 2:
            transactions.append({
                "date": _parse_date(date_str),
                "description": desc,
                "amount": amount,
                "raw_text": line,
            })

    return transactions


def _find_idx(headers: list[str], keywords: list[str]) -> int | None:
    for i, h in enumerate(headers):
        for kw in keywords:
            if kw in h:
                return i
    return None


def _safe_float(val) -> float:
    if not val:
        return 0.0
    try:
        return abs(float(str(val).replace(",", "").replace("$", "").replace("£", "").replace("€", "")))
    except (ValueError, TypeError):
        return 0.0
