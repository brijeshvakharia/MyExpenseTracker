from datetime import date, datetime

from pydantic import BaseModel


class CategoryOut(BaseModel):
    id: int
    name: str
    color: str

    model_config = {"from_attributes": True}


class CategoryCreate(BaseModel):
    name: str
    color: str = "#6b7280"


class CategoryUpdate(BaseModel):
    name: str | None = None
    color: str | None = None


class TransactionOut(BaseModel):
    id: int
    date: date
    description: str
    amount: float
    category: CategoryOut | None = None
    source_file: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class TransactionUpdate(BaseModel):
    category_id: int


class UploadResponse(BaseModel):
    file_name: str
    transaction_count: int
    message: str


class CategoryBreakdown(BaseModel):
    category: str
    color: str
    total: float
    percentage: float


class MonthlyTrend(BaseModel):
    month: str
    expenses: float
    income: float


class DashboardSummary(BaseModel):
    total_expenses: float
    total_income: float
    by_category: list[CategoryBreakdown]
    monthly_trend: list[MonthlyTrend]
