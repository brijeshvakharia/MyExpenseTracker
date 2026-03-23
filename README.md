# MyExpenseTracker

A personal expense tracking app that lets you upload bank statements (CSV, XLSX, PDF), automatically categorizes transactions using keyword-matching rules, and presents an interactive dashboard with charts and filters.

## Tech Stack

- **Backend:** Python, FastAPI, SQLAlchemy, SQLite
- **Frontend:** React, TypeScript, Vite, Tailwind CSS, Recharts

## Features

- **Upload bank statements** — Drag-and-drop support for CSV, XLSX, and PDF files
- **Auto-categorization** — Transactions are categorized instantly using local keyword-matching rules across 10 categories: Food, Transport, Shopping, Bills, Entertainment, Health, Education, Travel, Income, Other
- **Transactions view** — Sortable, filterable table with search, date range, and category filters. Inline category editing by clicking the category badge
- **Dashboard** — Summary cards (total expenses, income, net), pie chart (category breakdown), bar chart (monthly trends), and percentage progress bars
- **Duplicate detection** — Re-uploading the same file skips already-imported transactions

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`. On first run, the SQLite database and default categories are created automatically.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in your browser.

## Project Structure

```
MyExpenseTracker/
├── backend/
│   ├── requirements.txt
│   └── app/
│       ├── main.py              # FastAPI app, CORS, DB init
│       ├── config.py            # Settings (DB path, upload dir)
│       ├── database.py          # SQLAlchemy engine and session
│       ├── models.py            # ORM models (Transaction, Category)
│       ├── schemas.py           # Pydantic request/response models
│       ├── routers/
│       │   ├── upload.py        # POST /api/upload
│       │   ├── transactions.py  # GET/PATCH/DELETE /api/transactions
│       │   ├── categories.py    # GET/POST/PUT /api/categories
│       │   └── dashboard.py     # GET /api/dashboard/summary
│       └── services/
│           ├── parser_common.py # File type dispatch
│           ├── parser_csv.py    # CSV parsing with pandas
│           ├── parser_xlsx.py   # Excel parsing with openpyxl
│           ├── parser_pdf.py    # PDF parsing with pdfplumber
│           └── categorizer.py   # Keyword-based categorization
├── frontend/
│   └── src/
│       ├── App.tsx              # Router and navigation
│       ├── api/client.ts        # API client (axios)
│       ├── types/index.ts       # TypeScript interfaces
│       └── pages/
│           ├── DashboardPage.tsx
│           ├── UploadPage.tsx
│           └── TransactionsPage.tsx
└── .gitignore
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/upload` | Upload and parse a bank statement |
| GET | `/api/transactions` | List transactions (supports filtering, sorting, pagination) |
| PATCH | `/api/transactions/:id` | Update transaction category |
| DELETE | `/api/transactions/:id` | Delete a transaction |
| GET | `/api/categories` | List all categories |
| POST | `/api/categories` | Create a new category |
| PUT | `/api/categories/:id` | Update category name or color |
| GET | `/api/dashboard/summary` | Get expense/income summary with breakdowns |
