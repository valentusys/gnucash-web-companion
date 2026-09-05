import { isRedirect } from '@sveltejs/kit';
import { getAuthToken, getActiveBookContext, apiFetch } from '$lib/api/server';
import type {
	CashflowData,
	CashflowPeriod,
	DashboardDrilldownLinks,
	DashboardExpenseChange,
	DashboardSectionErrors,
	DashboardUpcomingObligations,
	ExpenseByAccount,
	PeriodReport,
	PeriodReportComparison,
	ReportSummary,
	ScheduledTransaction,
	TransactionListItem
} from '$lib/api/types';
import { compareDecimalStrings } from '$lib/money.js';
import { buildTransactionsExplorerUrl } from '$lib/transactions/explorer';

const DAY_MS = 24 * 60 * 60 * 1000;
const ISO_DATE_RE = /^\d{4}-\d{2}-\d{2}$/;

function transactionFilterHref(params: Record<string, string>): string {
	return buildTransactionsExplorerUrl({
		dateFrom: params.date_from,
		dateTo: params.date_to,
		accountIds: params.account_ids ? [params.account_ids] : params.account_id ? [params.account_id] : [],
		type: params.type === 'income' || params.type === 'expense' ? params.type : '',
		sort: 'date_desc',
		pageSize: 50
	});
}

function strictIsoDate(value: string | null | undefined): value is string {
	if (!value || !ISO_DATE_RE.test(value)) return false;
	const parsed = new Date(`${value}T00:00:00Z`);
	return !Number.isNaN(parsed.getTime()) && parsed.toISOString().slice(0, 10) === value;
}

function formatUtcDate(value: Date): string {
	return value.toISOString().slice(0, 10);
}

function addUtcDays(value: string, days: number): string {
	return formatUtcDate(new Date(new Date(`${value}T00:00:00Z`).getTime() + days * DAY_MS));
}

function monthStart(value: string): string {
	return `${value.slice(0, 7)}-01`;
}

function previousEquivalentRange(dateFrom: string, dateTo: string): { date_from: string; date_to: string } {
	const inclusiveDays = Math.round(
		(new Date(`${dateTo}T00:00:00Z`).getTime() - new Date(`${dateFrom}T00:00:00Z`).getTime()) / DAY_MS
	) + 1;
	return {
		date_from: addUtcDays(dateFrom, -inclusiveDays),
		date_to: addUtcDays(dateFrom, -1)
	};
}

function monthRange(month: string): { date_from: string; date_to: string } {
	const match = /^(\d{4})-(\d{2})$/.exec(month);
	if (!match) return { date_from: '', date_to: '' };
	const year = parseInt(match[1], 10);
	const monthIndex = parseInt(match[2], 10);
	if (monthIndex < 1 || monthIndex > 12) return { date_from: '', date_to: '' };
	const lastDay = new Date(Date.UTC(year, monthIndex, 0)).getUTCDate();
	return {
		date_from: `${year}-${String(monthIndex).padStart(2, '0')}-01`,
		date_to: `${year}-${String(monthIndex).padStart(2, '0')}-${String(lastDay).padStart(2, '0')}`
	};
}

function clampedMonthRange(month: string, dateFrom: string, dateTo: string): { date_from: string; date_to: string } {
	const range = monthRange(month);
	if (!range.date_from || !range.date_to) return range;
	return {
		date_from: range.date_from < dateFrom ? dateFrom : range.date_from,
		date_to: range.date_to > dateTo ? dateTo : range.date_to
	};
}

function reportHref(dateFrom: string, dateTo: string): string {
	const params = new URLSearchParams();
	params.set('preset', 'custom');
	params.set('date_from', dateFrom);
	params.set('date_to', dateTo);
	return `/reports?${params.toString()}`;
}

function sectionStatus(report: PeriodReport | null, section: string): string | null {
	return report?.section_statuses?.find((candidate) => candidate.section === section)?.status ?? null;
}

function sortExpenses(expenses: ExpenseByAccount[]): ExpenseByAccount[] {
	return [...expenses].sort(
		(left, right) =>
			compareDecimalStrings(right.total, left.total) ||
			left.account_name.localeCompare(right.account_name) ||
			left.account_id.localeCompare(right.account_id)
	);
}

function largestExpenseChanges(comparison: PeriodReportComparison | null): DashboardExpenseChange[] {
	return (comparison?.expense_changes ?? [])
		.filter(
			(change): change is typeof change & { delta: string; absolute_delta: string } =>
				change.status === 'ok' && typeof change.delta === 'string' && typeof change.absolute_delta === 'string'
		)
		.sort(
			(left, right) =>
				compareDecimalStrings(right.absolute_delta, left.absolute_delta) ||
				left.account_name.localeCompare(right.account_name) ||
				left.account_id.localeCompare(right.account_id)
		)
		.slice(0, 3)
		.map((change) => ({
			account_id: change.account_id,
			account_name: change.account_name,
			delta: change.delta,
			absolute_delta: change.absolute_delta,
			currency: change.currency
		}));
}

export async function load({ cookies, fetch: fetchFn }: { cookies: any; fetch: any }) {
	const token = getAuthToken(cookies);
	const { activeBook, bookPrefix } = await getActiveBookContext(fetchFn, cookies, token);

	let summary: ReportSummary | null = null;
	let reportComparison: PeriodReportComparison | null = null;
	let expenses: ExpenseByAccount[] = [];
	let cashflowPeriods: CashflowPeriod[] = [];
	let monthCashflow: CashflowData | null = null;
	let recentTransactions: TransactionListItem[] = [];
	let expenseChanges: DashboardExpenseChange[] = [];
	let upcomingObligations: DashboardUpcomingObligations = { enabled_count: 0, unavailable_count: 0 };
	const sectionErrors: DashboardSectionErrors = {
		summary: false,
		expenses: false,
		cashflow: false,
		recentTransactions: false,
		changes: false,
		upcomingObligations: false
	};

	try {
		summary = await apiFetch<ReportSummary>(fetchFn, `${bookPrefix}/reports/summary`, token);
	} catch (reason) {
		if (isRedirect(reason)) throw reason;
		sectionErrors.summary = true;
	}

	const fallbackAsOf = new Date().toISOString().slice(0, 10);
	const asOfDate = strictIsoDate(summary?.as_of_date) ? summary.as_of_date : fallbackAsOf;
	const dateFrom = monthStart(asOfDate);
	const dateTo = asOfDate;
	const comparisonRange = previousEquivalentRange(dateFrom, dateTo);

	const comparisonTask = async (): Promise<PeriodReportComparison | null> => {
		if (summary?.status !== 'ready') return null;
		const params = new URLSearchParams({
			date_from: dateFrom,
			date_to: dateTo,
			comparison_mode: 'previous_equivalent',
			comparison_date_from: comparisonRange.date_from,
			comparison_date_to: comparisonRange.date_to
		});
		try {
			return await apiFetch<PeriodReportComparison>(
				fetchFn,
				`${bookPrefix}/reports/comparison?${params.toString()}`,
				token
			);
		} catch (reason) {
			if (isRedirect(reason)) throw reason;
			sectionErrors.expenses = true;
			sectionErrors.cashflow = true;
			sectionErrors.changes = true;
			return null;
		}
	};

	const recentTask = async () => {
		try {
			recentTransactions = await apiFetch<TransactionListItem[]>(
				fetchFn,
				`${bookPrefix}/reports/recent-transactions?limit=20`,
				token
			);
		} catch (reason) {
			if (isRedirect(reason)) throw reason;
			sectionErrors.recentTransactions = true;
		}
	};

	const obligationsTask = async () => {
		try {
			const scheduled = await apiFetch<ScheduledTransaction[]>(fetchFn, `${bookPrefix}/scheduled-transactions`, token);
			upcomingObligations = {
				enabled_count: scheduled.filter((item) => item.enabled).length,
				unavailable_count: scheduled.filter((item) => item.forecast.status === 'unavailable').length
			};
		} catch (reason) {
			if (isRedirect(reason)) throw reason;
			sectionErrors.upcomingObligations = true;
		}
	};

	const [comparisonResult] = await Promise.all([comparisonTask(), recentTask(), obligationsTask()]);
	reportComparison = comparisonResult;

	if (reportComparison) {
		const primary = reportComparison.primary;
		expenses = sortExpenses(primary.expenses_by_account ?? []);
		cashflowPeriods = primary.monthly_cashflow ?? [];
		monthCashflow = primary.cashflow ?? null;
		expenseChanges = largestExpenseChanges(reportComparison);
		sectionErrors.expenses = sectionStatus(primary, 'expenses_by_account') === 'error';
		sectionErrors.cashflow =
			sectionStatus(primary, 'cashflow') === 'error' || sectionStatus(primary, 'monthly_cashflow') === 'error';
		const changesStatus = reportComparison.delta_section_statuses?.find(
			(candidate) => candidate.section === 'expenses_by_account'
		)?.status;
		sectionErrors.changes = changesStatus === 'error' || changesStatus === 'not_comparable';
	}

	const drilldowns: DashboardDrilldownLinks = {
		recent: transactionFilterHref({}),
		incomeThisMonth: transactionFilterHref({ date_from: dateFrom, date_to: dateTo, type: 'income' }),
		expensesThisMonth: transactionFilterHref({ date_from: dateFrom, date_to: dateTo, type: 'expense' }),
		expensesAll: reportHref(dateFrom, dateTo),
		cashflowByMonth: Object.fromEntries(
			cashflowPeriods.map((period) => [
				period.month,
				transactionFilterHref(clampedMonthRange(period.month, dateFrom, dateTo))
			])
		),
		expensesByAccount: Object.fromEntries(
			expenses.map((expense) => [
				expense.account_id,
				transactionFilterHref({ account_ids: expense.account_id, date_from: dateFrom, date_to: dateTo })
			])
		)
	};

	return {
		summary,
		expenses,
		cashflowPeriods,
		monthCashflow,
		recentTransactions,
		expenseChanges,
		upcomingObligations,
		comparisonPeriod: {
			date_from: comparisonRange.date_from,
			date_to: comparisonRange.date_to
		},
		sectionErrors,
		activeBook,
		drilldowns
	};
}
