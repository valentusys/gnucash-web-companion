import { isRedirect } from '@sveltejs/kit';
import { getAuthToken, getActiveBookContext, apiFetch } from '$lib/api/server';
import type {
	DashboardDrilldownLinks,
	DashboardSectionErrors,
	ReportSummary,
	ExpenseByAccount,
	CashflowPeriod,
	TransactionListItem
} from '$lib/api/types';

function transactionFilterHref(params: Record<string, string>): string {
	const sp = new URLSearchParams({ limit: '50', offset: '0' });
	for (const [key, value] of Object.entries(params)) {
		if (value) sp.set(key, value);
	}
	return `/transactions?${sp.toString()}`;
}

function monthRange(month: string): { date_from: string; date_to: string } {
	const match = /^(\d{4})-(\d{2})$/.exec(month);
	if (!match) {
		return { date_from: '', date_to: '' };
	}
	const year = parseInt(match[1], 10);
	const monthIndex = parseInt(match[2], 10);
	if (monthIndex < 1 || monthIndex > 12) {
		return { date_from: '', date_to: '' };
	}
	const lastDay = new Date(year, monthIndex, 0).getDate();
	return {
		date_from: `${year}-${String(monthIndex).padStart(2, '0')}-01`,
		date_to: `${year}-${String(monthIndex).padStart(2, '0')}-${String(lastDay).padStart(2, '0')}`
	};
}

export async function load({ cookies, fetch: fetchFn }: { cookies: any; fetch: any }) {
	const token = getAuthToken(cookies);
	const { activeBook, bookPrefix } = await getActiveBookContext(fetchFn, cookies, token);

	const today = new Date();
	const firstOfMonth = new Date(today.getFullYear(), today.getMonth(), 1);
	const dateFrom = firstOfMonth.toISOString().slice(0, 10);
	const dateTo = today.toISOString().slice(0, 10);

	let summary: ReportSummary | null = null;
	let expenses: ExpenseByAccount[] = [];
	let cashflowPeriods: CashflowPeriod[] = [];
	let recentTransactions: TransactionListItem[] = [];
	const sectionErrors: DashboardSectionErrors = {
		summary: false,
		expenses: false,
		cashflow: false,
		recentTransactions: false
	};

	try {
		summary = await apiFetch<ReportSummary>(fetchFn, `${bookPrefix}/reports/summary`, token);
	} catch (reason) {
		if (isRedirect(reason)) throw reason;
		sectionErrors.summary = true;
	}

	try {
		expenses = await apiFetch<ExpenseByAccount[]>(
			fetchFn,
			`${bookPrefix}/reports/expenses-by-account?date_from=${dateFrom}&date_to=${dateTo}`,
			token
		);
	} catch (reason) {
		if (isRedirect(reason)) throw reason;
		sectionErrors.expenses = true;
		expenses = [];
	}

	try {
		cashflowPeriods = await apiFetch<CashflowPeriod[]>(
			fetchFn,
			`${bookPrefix}/reports/cashflow?date_from=${dateFrom}&date_to=${dateTo}&by_month=true`,
			token
		);
	} catch (reason) {
		if (isRedirect(reason)) throw reason;
		sectionErrors.cashflow = true;
		cashflowPeriods = [];
	}

	try {
		recentTransactions = await apiFetch<TransactionListItem[]>(
			fetchFn,
			`${bookPrefix}/reports/recent-transactions?limit=10`,
			token
		);
	} catch (reason) {
		if (isRedirect(reason)) throw reason;
		sectionErrors.recentTransactions = true;
		recentTransactions = [];
	}

	const drilldowns: DashboardDrilldownLinks = {
		recent: transactionFilterHref({}),
		incomeThisMonth: transactionFilterHref({ date_from: dateFrom, date_to: dateTo }),
		expensesThisMonth: transactionFilterHref({ date_from: dateFrom, date_to: dateTo }),
		cashflowByMonth: Object.fromEntries(
			cashflowPeriods.map((period) => [period.month, transactionFilterHref(monthRange(period.month))])
		),
		expensesByAccount: Object.fromEntries(
			expenses.map((expense) => [
				expense.account_id,
				transactionFilterHref({ account_id: expense.account_id, date_from: dateFrom, date_to: dateTo })
			])
		)
	};

	return { summary, expenses, cashflowPeriods, recentTransactions, sectionErrors, activeBook, drilldowns };
}
