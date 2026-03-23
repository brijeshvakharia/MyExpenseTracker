from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Category, Transaction
from app.schemas import CategoryBreakdown, DashboardSummary, MonthlyTrend

router = APIRouter()


@router.get("/dashboard/summary", response_model=DashboardSummary)
def get_summary(
    date_from: date | None = None,
    date_to: date | None = None,
    db: Session = Depends(get_db),
):
    base_query = db.query(Transaction)
    if date_from:
        base_query = base_query.filter(Transaction.date >= date_from)
    if date_to:
        base_query = base_query.filter(Transaction.date <= date_to)

    # Total expenses and income
    total_expenses = abs(
        base_query.filter(Transaction.amount < 0).with_entities(func.coalesce(func.sum(Transaction.amount), 0)).scalar()
    )
    total_income = (
        base_query.filter(Transaction.amount > 0).with_entities(func.coalesce(func.sum(Transaction.amount), 0)).scalar()
    )

    # Breakdown by category (expenses only)
    category_data = (
        base_query.filter(Transaction.amount < 0)
        .join(Category, Transaction.category_id == Category.id, isouter=True)
        .with_entities(
            func.coalesce(Category.name, "Uncategorized").label("name"),
            func.coalesce(Category.color, "#6b7280").label("color"),
            func.sum(Transaction.amount).label("total"),
        )
        .group_by(Category.name, Category.color)
        .all()
    )

    by_category = []
    for row in category_data:
        abs_total = abs(row.total)
        by_category.append(
            CategoryBreakdown(
                category=row.name,
                color=row.color,
                total=abs_total,
                percentage=round((abs_total / total_expenses * 100) if total_expenses > 0 else 0, 1),
            )
        )
    by_category.sort(key=lambda x: x.total, reverse=True)

    # Monthly trend
    monthly_data = (
        base_query.with_entities(
            func.strftime("%Y-%m", Transaction.date).label("month"),
            func.sum(case((Transaction.amount < 0, Transaction.amount), else_=0)).label("expenses"),
            func.sum(case((Transaction.amount > 0, Transaction.amount), else_=0)).label("income"),
        )
        .group_by(func.strftime("%Y-%m", Transaction.date))
        .order_by(func.strftime("%Y-%m", Transaction.date))
        .all()
    )

    monthly_trend = [
        MonthlyTrend(
            month=row.month,
            expenses=abs(row.expenses),
            income=row.income,
        )
        for row in monthly_data
    ]

    return DashboardSummary(
        total_expenses=total_expenses,
        total_income=total_income,
        by_category=by_category,
        monthly_trend=monthly_trend,
    )
