export interface Category {
  id: number;
  name: string;
  color: string;
}

export interface Transaction {
  id: number;
  date: string;
  description: string;
  amount: number;
  category: Category | null;
  source_file: string | null;
  created_at: string;
}

export interface UploadResponse {
  file_name: string;
  transaction_count: number;
  message: string;
}

export interface CategoryBreakdown {
  category: string;
  color: string;
  total: number;
  percentage: number;
}

export interface MonthlyTrend {
  month: string;
  expenses: number;
  income: number;
}

export interface DashboardSummary {
  total_expenses: number;
  total_income: number;
  by_category: CategoryBreakdown[];
  monthly_trend: MonthlyTrend[];
}
