from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, SessionLocal, engine
from app.models import Category
from app.routers import categories, dashboard, transactions, upload

DEFAULT_CATEGORIES = [
    ("Food", "#ef4444"),
    ("Transport", "#f97316"),
    ("Shopping", "#eab308"),
    ("Bills", "#84cc16"),
    ("Entertainment", "#22c55e"),
    ("Health", "#06b6d4"),
    ("Education", "#3b82f6"),
    ("Travel", "#8b5cf6"),
    ("Income", "#10b981"),
    ("Other", "#6b7280"),
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables
    Base.metadata.create_all(bind=engine)

    # Seed default categories
    db = SessionLocal()
    try:
        if db.query(Category).count() == 0:
            for name, color in DEFAULT_CATEGORIES:
                db.add(Category(name=name, color=color))
            db.commit()
    finally:
        db.close()

    yield


app = FastAPI(title="MyExpenseTracker", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(transactions.router, prefix="/api", tags=["transactions"])
app.include_router(categories.router, prefix="/api", tags=["categories"])
app.include_router(dashboard.router, prefix="/api", tags=["dashboard"])
