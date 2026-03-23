import axios from 'axios';
import type { Category, DashboardSummary, Transaction, UploadResponse } from '../types';

const api = axios.create({
  baseURL: '/api',
});

export async function uploadFile(file: File): Promise<UploadResponse> {
  const form = new FormData();
  form.append('file', file);
  const { data } = await api.post<UploadResponse>('/upload', form);
  return data;
}

export interface TransactionFilters {
  category_id?: number;
  date_from?: string;
  date_to?: string;
  search?: string;
  sort_by?: string;
  sort_order?: string;
  skip?: number;
  limit?: number;
}

export async function getTransactions(filters: TransactionFilters = {}): Promise<Transaction[]> {
  const params = Object.fromEntries(
    Object.entries(filters).filter(([, v]) => v !== undefined && v !== '')
  );
  const { data } = await api.get<Transaction[]>('/transactions', { params });
  return data;
}

export async function updateTransactionCategory(id: number, categoryId: number): Promise<Transaction> {
  const { data } = await api.patch<Transaction>(`/transactions/${id}`, { category_id: categoryId });
  return data;
}

export async function deleteTransaction(id: number): Promise<void> {
  await api.delete(`/transactions/${id}`);
}

export async function getCategories(): Promise<Category[]> {
  const { data } = await api.get<Category[]>('/categories');
  return data;
}

export async function getDashboardSummary(dateFrom?: string, dateTo?: string): Promise<DashboardSummary> {
  const params: Record<string, string> = {};
  if (dateFrom) params.date_from = dateFrom;
  if (dateTo) params.date_to = dateTo;
  const { data } = await api.get<DashboardSummary>('/dashboard/summary', { params });
  return data;
}
