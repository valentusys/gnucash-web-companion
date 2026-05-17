import { getAuthToken, getActiveBookId, apiFetch } from '$lib/api/server';
import type { ReportSummary, ExpenseByAccount, CashflowPeriod, TransactionListItem } from '$lib/api/types';

export async function load({ cookies, fetch: fetchFn }: { cookies: any; fetch: any }) {
	const token = getAuthToken(cookies);
	const activeBookId = getActiveBookId(cookies);

	const today = new Date();
	const firstOfMonth = new Date(today.getFullYear(), today.getMonth(), 1);
	const dateFrom = firstOfMonth.toISOString().slice(0, 10);
	const dateTo = today.toISOString().slice(0, 10);

	const bookPrefix = activeBookId ? `/books/${activeBookId}` : '';

	let summary: ReportSummary | null = null;
	let expenses: ExpenseByAccount[] = [];
	let cashflowPeriods: CashflowPeriod[] = [];
	let recentTransactions: TransactionListItem[] = [];
	let loadError: string | null = null;

	try {
		summary = await apiFetch<ReportSummary>(fetchFn, `${bookPrefix}/reports/summary`, token);
	} catch (e: any) {
		loadError = e.message;
	}

	try {
		expenses = await apiFetch<ExpenseByAccount[]>(
			fetchFn,
			`${bookPrefix}/reports/expenses-by-account?date_from=${dateFrom}&date_to=${dateTo}`,
			token
		);
	} catch {
		expenses = [];
	}

	try {
		cashflowPeriods = await apiFetch<CashflowPeriod[]>(
			fetchFn,
			`${bookPrefix}/reports/cashflow?date_from=${dateFrom}&date_to=${dateTo}&by_month=true`,
			token
		);
	} catch {
		cashflowPeriods = [];
	}

	try {
		recentTransactions = await apiFetch<TransactionListItem[]>(
			fetchFn,
			`${bookPrefix}/reports/recent-transactions?limit=10`,
			token
		);
	} catch {
		recentTransactions = [];
	}

	return { summary, expenses, cashflowPeriods, recentTransactions, loadError };
}
