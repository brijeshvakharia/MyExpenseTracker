import { useEffect, useState } from 'react';
import {
  deleteTransaction,
  getCategories,
  getTransactions,
  updateTransactionCategory,
} from '../api/client';
import type { Category, Transaction } from '../types';

export default function TransactionsPage() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [sortBy, setSortBy] = useState('date');
  const [sortOrder, setSortOrder] = useState('desc');
  const [editingId, setEditingId] = useState<number | null>(null);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [txns, cats] = await Promise.all([
        getTransactions({
          search: search || undefined,
          category_id: categoryFilter ? Number(categoryFilter) : undefined,
          date_from: dateFrom || undefined,
          date_to: dateTo || undefined,
          sort_by: sortBy,
          sort_order: sortOrder,
        }),
        getCategories(),
      ]);
      setTransactions(txns);
      setCategories(cats);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [search, categoryFilter, dateFrom, dateTo, sortBy, sortOrder]);

  const handleSort = (col: string) => {
    if (sortBy === col) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(col);
      setSortOrder('desc');
    }
  };

  const handleCategoryChange = async (txnId: number, categoryId: number) => {
    await updateTransactionCategory(txnId, categoryId);
    setEditingId(null);
    fetchData();
  };

  const handleDelete = async (txnId: number) => {
    await deleteTransaction(txnId);
    fetchData();
  };

  const sortIcon = (col: string) => {
    if (sortBy !== col) return '';
    return sortOrder === 'asc' ? ' \u2191' : ' \u2193';
  };

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Transactions</h2>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6 flex flex-wrap gap-4">
        <input
          type="text"
          placeholder="Search descriptions..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-md text-sm flex-1 min-w-[200px]"
        />
        <select
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-md text-sm"
        >
          <option value="">All Categories</option>
          {categories.map((c) => (
            <option key={c.id} value={c.id}>{c.name}</option>
          ))}
        </select>
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

      {/* Table */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-gray-500">Loading...</div>
        ) : transactions.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            No transactions found. Upload a bank statement to get started.
          </div>
        ) : (
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th
                  onClick={() => handleSort('date')}
                  className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase cursor-pointer hover:bg-gray-100"
                >
                  Date{sortIcon('date')}
                </th>
                <th
                  onClick={() => handleSort('description')}
                  className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase cursor-pointer hover:bg-gray-100"
                >
                  Description{sortIcon('description')}
                </th>
                <th
                  onClick={() => handleSort('amount')}
                  className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase cursor-pointer hover:bg-gray-100"
                >
                  Amount{sortIcon('amount')}
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Category
                </th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {transactions.map((txn) => (
                <tr key={txn.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-sm text-gray-600 whitespace-nowrap">{txn.date}</td>
                  <td className="px-4 py-3 text-sm text-gray-900">{txn.description}</td>
                  <td className={`px-4 py-3 text-sm text-right whitespace-nowrap font-medium ${
                    txn.amount < 0 ? 'text-red-600' : 'text-green-600'
                  }`}>
                    {txn.amount < 0 ? '-' : '+'}${Math.abs(txn.amount).toFixed(2)}
                  </td>
                  <td className="px-4 py-3 text-sm">
                    {editingId === txn.id ? (
                      <select
                        autoFocus
                        defaultValue={txn.category?.id || ''}
                        onChange={(e) => handleCategoryChange(txn.id, Number(e.target.value))}
                        onBlur={() => setEditingId(null)}
                        className="px-2 py-1 border border-gray-300 rounded text-sm"
                      >
                        {categories.map((c) => (
                          <option key={c.id} value={c.id}>{c.name}</option>
                        ))}
                      </select>
                    ) : (
                      <button
                        onClick={() => setEditingId(txn.id)}
                        className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                        style={{
                          backgroundColor: `${txn.category?.color || '#6b7280'}20`,
                          color: txn.category?.color || '#6b7280',
                        }}
                      >
                        {txn.category?.name || 'Uncategorized'}
                      </button>
                    )}
                  </td>
                  <td className="px-4 py-3 text-sm text-right">
                    <button
                      onClick={() => handleDelete(txn.id)}
                      className="text-red-400 hover:text-red-600 text-xs"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
