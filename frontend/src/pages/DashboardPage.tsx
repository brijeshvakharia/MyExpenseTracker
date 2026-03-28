import { useEffect, useState } from 'react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { getDashboardSummary } from '../api/client';
import type { DashboardSummary } from '../types';

export default function DashboardPage() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');

  useEffect(() => {
    const fetchSummary = async () => {
      setLoading(true);
      try {
        const data = await getDashboardSummary(
          dateFrom || undefined,
          dateTo || undefined
        );
        setSummary(data);
      } finally {
        setLoading(false);
      }
    };
    fetchSummary();
  }, [dateFrom, dateTo]);

  if (loading) {
    return <div className="text-center text-gray-500 py-12">Loading dashboard...</div>;
  }

  if (!summary || (summary.total_expenses === 0 && summary.total_income === 0)) {
    return (
      <div className="text-center text-gray-500 py-12">
        <p className="text-lg mb-2">No data yet</p>
        <p className="text-sm">Upload a bank statement to see your expense dashboard.</p>
      </div>
    );
  }

  const net = summary.total_income - summary.total_expenses;

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Dashboard</h2>
        <div className="flex gap-3">
          <input
            type="date"
            value={dateFrom}
            onChange={(e) => setDateFrom(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm"
          />
          <input
            type="date"
            value={dateTo}
            onChange={(e) => setDateTo(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm"
          />
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <p className="text-sm text-gray-500 mb-1">Total Expenses</p>
          <p className="text-2xl font-bold text-red-600">${summary.total_expenses.toFixed(2)}</p>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <p className="text-sm text-gray-500 mb-1">Total Income</p>
          <p className="text-2xl font-bold text-green-600">${summary.total_income.toFixed(2)}</p>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <p className="text-sm text-gray-500 mb-1">Net</p>
          <p className={`text-2xl font-bold ${net >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {net >= 0 ? '+' : '-'}${Math.abs(net).toFixed(2)}
          </p>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pie Chart - Category Breakdown */}
        {summary.by_category.length > 0 && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Expenses by Category</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={summary.by_category}
                  dataKey="total"
                  nameKey="category"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  label={({ category, percentage }) => `${category} (${percentage}%)`}
                >
                  {summary.by_category.map((entry, index) => (
                    <Cell key={index} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip formatter={(value: number) => `$${value.toFixed(2)}`} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Bar Chart - Monthly Trend */}
        {summary.monthly_trend.length > 0 && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Monthly Trend</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={summary.monthly_trend}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip formatter={(value: number) => `$${value.toFixed(2)}`} />
                <Legend />
                <Bar dataKey="expenses" fill="#ef4444" name="Expenses" />
                <Bar dataKey="income" fill="#22c55e" name="Income" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* Category Breakdown Table */}
      {summary.by_category.length > 0 && (
        <div className="mt-6 bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Category Breakdown</h3>
          <div className="space-y-3">
            {summary.by_category.map((cat) => (
              <div key={cat.category} className="flex items-center">
                <div
                  className="w-3 h-3 rounded-full mr-3 shrink-0"
                  style={{ backgroundColor: cat.color }}
                />
                <span className="text-sm text-gray-700 flex-1">{cat.category}</span>
                <span className="text-sm font-medium text-gray-900 mr-4">
                  ${cat.total.toFixed(2)}
                </span>
                <div className="w-32 bg-gray-100 rounded-full h-2">
                  <div
                    className="h-2 rounded-full"
                    style={{ width: `${cat.percentage}%`, backgroundColor: cat.color }}
                  />
                </div>
                <span className="text-xs text-gray-500 ml-2 w-12 text-right">
                  {cat.percentage}%
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
