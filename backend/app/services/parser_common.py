from pathlib import Path

from app.services.parser_csv import parse_csv
from app.services.parser_xlsx import parse_xlsx


def parse_file(filepath: str) -> list[dict]:
    """Dispatch file parsing based on extension. Returns list of dicts with keys: date, description, amount."""
    ext = Path(filepath).suffix.lower()
    if ext == ".csv":
        return parse_csv(filepath)
    elif ext == ".xlsx":
        return parse_xlsx(filepath)
    elif ext == ".pdf":
        from app.services.parser_pdf import parse_pdf
        return parse_pdf(filepath)
    raise ValueError(f"Unsupported file type: {ext}")
