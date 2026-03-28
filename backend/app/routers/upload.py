from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import Category, Transaction
from app.schemas import UploadResponse
from app.services.categorizer import categorize_transactions
from app.services.parser_common import parse_file

router = APIRouter()

ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".pdf"}


@router.post("/upload", response_model=UploadResponse)
def upload_statement(file: UploadFile, db: Session = Depends(get_db)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")

    # Save uploaded file
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_path = upload_dir / f"{timestamp}_{file.filename}"

    with open(save_path, "wb") as f:
        content = file.file.read()
        f.write(content)

    # Parse the file
    try:
        parsed = parse_file(str(save_path))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not parsed:
        raise HTTPException(status_code=400, detail="No transactions found in the uploaded file")

    # Deduplicate against existing transactions
    new_transactions = []
    for t in parsed:
        exists = db.query(Transaction).filter(
            Transaction.date == t["date"],
            Transaction.description == t["description"],
            Transaction.amount == t["amount"],
        ).first()
        if not exists:
            new_transactions.append(t)

    if not new_transactions:
        return UploadResponse(
            file_name=file.filename,
            transaction_count=0,
            message="All transactions already exist in the database",
        )

    # Categorize using Claude API
    categories = db.query(Category).all()
    category_names = [c.name for c in categories]
    category_map = {c.name: c.id for c in categories}

    descriptions = [t["description"] for t in new_transactions]
    assigned_categories = categorize_transactions(descriptions, category_names)

    # Insert transactions
    for t, cat_name in zip(new_transactions, assigned_categories):
        transaction = Transaction(
            date=t["date"],
            description=t["description"],
            amount=t["amount"],
            category_id=category_map.get(cat_name),
            source_file=file.filename,
            raw_text=t.get("raw_text"),
        )
        db.add(transaction)

    db.commit()

    return UploadResponse(
        file_name=file.filename,
        transaction_count=len(new_transactions),
        message=f"Successfully imported {len(new_transactions)} transactions",
    )
