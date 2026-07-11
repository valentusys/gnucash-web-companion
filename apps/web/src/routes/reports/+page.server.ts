import { isHttpError, isRedirect } from '@sveltejs/kit';
import { apiFetch, getActiveBookContext, getAuthToken } from '$lib/api/server';
import type { CashflowData, CashflowPeriod, ExpenseByAccount, PeriodReportResponse } from '$lib/api/types';
import type { PageServerLoad } from './$types';

const ISO_DATE_RE = /^\d{4}-\d{2}-\d{2}$/;
const REPORT_PRESETS = ['this-month', 'last-month', 'year-to-date', 'custom'] as const;
const REDACTED_SECTION_ERROR = 'Reports API returned a section error. Backend details are redacted.';

type ReportPreset = (typeof REPORT_PRESETS)[number];

type ReportPeriod = {
	preset: ReportPreset;
	dateFrom: string;
	dateTo: string;
};

type PeriodResolution = {
	period: ReportPeriod;
	validationError: string | null;
};

type ReportSummaryView = {
	currency: string;
	income: string | null;
	expenses: string | null;
	net: string | null;
	assets: string | null;
	liabilities: string | null;
	netWorth: string | null;
};

type ReportView = {
	requestedPeriod: ReportPeriod;
	reportingBasis: string;
	includesCurrencyConversion: boolean;
	limitations: string[];
	summary: ReportSummaryView | null;
	cashflow: CashflowData | null;
	cashflowMonthly: CashflowPeriod[];
	expensesByAccount: ExpenseByAccount[];
	sectionErrors: Record<'summary' | 'cashflow' | 'expenses_by_account', string | null>;
};

type DrilldownLinks = {
	period: string;
	cashflowByMonth: Record<string, string>;
	expensesByAccount: Record<string, string>;
};

function isRecord(value: unknown): value is Record<string, unknown> {
	return typeof value === 'object' && value !== null;
}

function formatDate(date: Date): string {
	return date.toISOString().slice(0, 10);
}

function strictIsoDate(value: string): boolean {
	if (!ISO_DATE_RE.test(value)) return false;
	const date = new Date(`${value}T00:00:00Z`);
	return !Number.isNaN(date.getTime()) && formatDate(date) === value;
}

function presetRange(preset: Exclude<ReportPreset, 'custom'>, now = new Date()): { dateFrom: string; dateTo: string } {
	const year = now.getUTCFullYear();
	const month = now.getUTCMonth();
	const today = formatDate(now);
	if (preset === 'last-month') {
		return {
			dateFrom: formatDate(new Date(Date.UTC(year, month - 1, 1))),
			dateTo: formatDate(new Date(Date.UTC(year, month, 0)))
		};
	}
	if (preset === 'year-to-date') {
		return {
			dateFrom: formatDate(new Date(Date.UTC(year, 0, 1))),
			dateTo: today
		};
	}
	return {
		dateFrom: formatDate(new Date(Date.UTC(year, month, 1))),
		dateTo: today
	};
}

function isReportPreset(value: string | null): value is ReportPreset {
	return REPORT_PRESETS.includes(value as ReportPreset);
}

function resolvePeriod(url: URL): PeriodResolution {
	const rawPreset = url.searchParams.get('preset');
	const requestedPreset = isReportPreset(rawPreset) ? rawPreset : null;
	const hasDateParam = url.searchParams.has('date_from') || url.searchParams.has('date_to');
	const rawDateFrom = url.searchParams.get('date_from') ?? '';
	const rawDateTo = url.searchParams.get('date_to') ?? '';

	if (hasDateParam || requestedPreset === 'custom') {
		if (!strictIsoDate(rawDateFrom) || !strictIsoDate(rawDateTo)) {
			return {
				period: { preset: requestedPreset ?? 'custom', dateFrom: rawDateFrom, dateTo: rawDateTo },
				validationError: 'Enter a valid custom date_from/date_to range using YYYY-MM-DD dates.'
			};
		}
		if (rawDateFrom > rawDateTo) {
			return {
				period: { preset: requestedPreset ?? 'custom', dateFrom: rawDateFrom, dateTo: rawDateTo },
				validationError: 'Invalid range: date_from must be on or before date_to.'
			};
		}
		return {
			period: { preset: requestedPreset ?? 'custom', dateFrom: rawDateFrom, dateTo: rawDateTo },
			validationError: null
		};
	}

	if (rawPreset !== null && !requestedPreset) {
		const fallback = presetRange('this-month');
		return {
			period: { preset: 'this-month', dateFrom: fallback.dateFrom, dateTo: fallback.dateTo },
			validationError: 'Choose a supported report period preset.'
		};
	}

	const preset = requestedPreset ?? 'this-month';
	const range = presetRange(preset);
	return {
		period: { preset, dateFrom: range.dateFrom, dateTo: range.dateTo },
		validationError: null
	};
}

function reportsUrl(preset: ReportPreset, dateFrom: string, dateTo: string): string {
	const params = new URLSearchParams({ preset, date_from: dateFrom, date_to: dateTo });
	return `/reports?${params.toString()}`;
}

function buildPresetOptions(period: ReportPeriod) {
	return (['this-month', 'last-month', 'year-to-date'] as const).map((preset) => {
		const range = presetRange(preset);
		return {
			id: preset,
			label: preset === 'this-month' ? 'This month' : preset === 'last-month' ? 'Last month' : 'Year to date',
			href: reportsUrl(preset, range.dateFrom, range.dateTo),
			active: period.preset === preset && period.dateFrom === range.dateFrom && period.dateTo === range.dateTo
		};
	});
}

function transactionFilterHref(params: Record<string, string>): string {
	const sp = new URLSearchParams({ limit: '50', offset: '0' });
	for (const [key, value] of Object.entries(params)) {
		if (value) sp.set(key, value);
	}
	return `/transactions?${sp.toString()}`;
}

function maxIsoDate(left: string, right: string): string {
	return left > right ? left : right;
}

function minIsoDate(left: string, right: string): string {
	return left < right ? left : right;
}

function monthRange(month: string, period: ReportPeriod): { date_from: string; date_to: string } {
	const match = /^(\d{4})-(\d{2})$/.exec(month);
	if (!match) {
		return { date_from: period.dateFrom, date_to: period.dateTo };
	}
	const year = parseInt(match[1], 10);
	const monthIndex = parseInt(match[2], 10);
	if (monthIndex < 1 || monthIndex > 12) {
		return { date_from: period.dateFrom, date_to: period.dateTo };
	}
	const monthStart = `${match[1]}-${match[2]}-01`;
	const monthEnd = formatDate(new Date(Date.UTC(year, monthIndex, 0)));
	return {
		date_from: maxIsoDate(monthStart, period.dateFrom),
		date_to: minIsoDate(monthEnd, period.dateTo)
	};
}

function buildDrilldowns(period: ReportPeriod, expenses: ExpenseByAccount[], cashflowMonthly: CashflowPeriod[]): DrilldownLinks {
	return {
		period: transactionFilterHref({ date_from: period.dateFrom, date_to: period.dateTo }),
		cashflowByMonth: Object.fromEntries(
			cashflowMonthly.map((cashflowPeriod) => [cashflowPeriod.month, transactionFilterHref(monthRange(cashflowPeriod.month, period))])
		),
		expensesByAccount: Object.fromEntries(
			expenses.map((expense) => [
				expense.account_id,
				transactionFilterHref({ account_id: expense.account_id, date_from: period.dateFrom, date_to: period.dateTo })
			])
		)
	};
}

function stringValue(value: unknown): string | null {
	return typeof value === 'string' && value.trim() ? value : null;
}

function firstString(record: Record<string, unknown>, keys: string[]): string | null {
	for (const key of keys) {
		const value = stringValue(record[key]);
		if (value !== null) return value;
	}
	return null;
}

function stringArray(value: unknown): string[] {
	return Array.isArray(value) ? value.filter((item): item is string => typeof item === 'string' && item.trim().length > 0) : [];
}

function normalizeSummary(value: unknown, fallbackCurrency: string): ReportSummaryView | null {
	if (!isRecord(value)) return null;
	const summary = {
		currency: firstString(value, ['currency']) ?? fallbackCurrency,
		income: firstString(value, ['income', 'income_total', 'total_income', 'period_income', 'income_this_month']),
		expenses: firstString(value, ['expenses', 'expense_total', 'total_expenses', 'period_expenses', 'expenses_this_month']),
		net: firstString(value, ['net', 'net_income', 'period_net', 'cashflow_net', 'profit_loss']),
		assets: firstString(value, ['assets']),
		liabilities: firstString(value, ['liabilities']),
		netWorth: firstString(value, ['net_worth'])
	};
	if (!summary.income && !summary.expenses && !summary.net && !summary.assets && !summary.liabilities && !summary.netWorth) {
		return null;
	}
	return summary;
}

function normalizeCashflow(value: unknown, period: ReportPeriod, fallbackCurrency: string): CashflowData | null {
	if (!isRecord(value)) return null;
	const inflow = firstString(value, ['inflow', 'income', 'cash_in']);
	const outflow = firstString(value, ['outflow', 'expenses', 'cash_out']);
	const net = firstString(value, ['net', 'cashflow_net']);
	if (!inflow && !outflow && !net) return null;
	return {
		date_from: firstString(value, ['date_from']) ?? period.dateFrom,
		date_to: firstString(value, ['date_to']) ?? period.dateTo,
		currency: firstString(value, ['currency']) ?? fallbackCurrency,
		inflow: inflow ?? '0',
		outflow: outflow ?? '0',
		net: net ?? '0'
	};
}

function normalizeCashflowPeriods(report: Record<string, unknown>): CashflowPeriod[] {
	const cashflow = report.cashflow;
	const candidates = [
		isRecord(cashflow) ? cashflow.monthly_periods : null,
		report.cashflow_monthly,
		report.monthly_periods
	];
	const periods = candidates.find(Array.isArray);
	if (!Array.isArray(periods)) return [];
	return periods.filter((period): period is CashflowPeriod => {
		return (
			isRecord(period) &&
			typeof period.month === 'string' &&
			typeof period.inflow === 'string' &&
			typeof period.outflow === 'string' &&
			typeof period.net === 'string'
		);
	});
}

function normalizeExpenses(value: unknown): ExpenseByAccount[] {
	if (!Array.isArray(value)) return [];
	return value.filter((expense): expense is ExpenseByAccount => {
		return (
			isRecord(expense) &&
			typeof expense.account_id === 'string' &&
			typeof expense.account_name === 'string' &&
			typeof expense.total === 'string' &&
			typeof expense.currency === 'string'
		);
	});
}

function redactSectionError(value: unknown): string | null {
	if (!value) return null;
	if (typeof value === 'string') return value.trim() ? REDACTED_SECTION_ERROR : null;
	if (!isRecord(value)) return REDACTED_SECTION_ERROR;
	const status = typeof value.status === 'string' ? value.status.toLowerCase() : '';
	const hasMessage = typeof value.message === 'string' && value.message.trim().length > 0;
	const hasDetail = typeof value.detail === 'string' && value.detail.trim().length > 0;
	const hasCode = typeof value.code === 'string' && value.code.trim().length > 0;
	if (status === 'ok' && !hasMessage && !hasDetail && !hasCode) return null;
	return REDACTED_SECTION_ERROR;
}

function normalizeReportResponse(response: PeriodReportResponse, fallbackPeriod: ReportPeriod): ReportView {
	const report = response as unknown as Record<string, unknown>;
	const rawRequestedPeriod = isRecord(report.requested_period) ? report.requested_period : {};
	const requestedPeriod = {
		...fallbackPeriod,
		dateFrom: firstString(rawRequestedPeriod, ['date_from']) ?? fallbackPeriod.dateFrom,
		dateTo: firstString(rawRequestedPeriod, ['date_to']) ?? fallbackPeriod.dateTo
	};
	const fallbackCurrency = firstString(report, ['currency', 'base_currency']) ?? 'base';
	const cashflow = normalizeCashflow(report.cashflow, requestedPeriod, fallbackCurrency);
	const cashflowMonthly = normalizeCashflowPeriods(report);
	const expensesByAccount = normalizeExpenses(report.expenses_by_account);
	const rawSectionErrors = isRecord(report.section_errors) ? report.section_errors : {};
	const reportingBasis = firstString(report, ['reporting_basis']) ?? 'base_currency_only';
	const limitations = stringArray(report.limitations);

	return {
		requestedPeriod,
		reportingBasis,
		includesCurrencyConversion: report.includes_currency_conversion === true,
		limitations,
		summary: normalizeSummary(report.summary, cashflow?.currency ?? fallbackCurrency),
		cashflow,
		cashflowMonthly,
		expensesByAccount,
		sectionErrors: {
			summary: redactSectionError(rawSectionErrors.summary),
			cashflow: redactSectionError(rawSectionErrors.cashflow) ?? redactSectionError(rawSectionErrors.cashflow_monthly),
			expenses_by_account: redactSectionError(rawSectionErrors.expenses_by_account)
		}
	};
}

function sectionWarnings(report: ReportView | null) {
	if (!report) return [];
	return Object.entries(report.sectionErrors)
		.filter((entry): entry is [string, string] => entry[1] !== null)
		.map(([section, message]) => ({ section, message }));
}

function safeLoadError(reason: unknown): string {
	if (isHttpError(reason)) {
		return reason.body?.message ?? 'Reports API request failed safely.';
	}
	return 'Reports API is unavailable or returned an unsupported response. Unknown backend details are redacted.';
}

export const load: PageServerLoad = async ({ cookies, fetch, url }) => {
	const token = getAuthToken(cookies);
	const { activeBook, bookPrefix } = await getActiveBookContext(fetch, cookies, token);
	const { period, validationError } = resolvePeriod(url);
	const presetOptions = buildPresetOptions(period);

	let report: ReportView | null = null;
	let loadError: string | null = null;

	if (!validationError) {
		const reportParams = new URLSearchParams({ date_from: period.dateFrom, date_to: period.dateTo });
		try {
			const response = await apiFetch<PeriodReportResponse>(fetch, `${bookPrefix}/reports?${reportParams.toString()}`, token);
			report = normalizeReportResponse(response, period);
		} catch (reason) {
			if (isRedirect(reason)) throw reason;
			loadError = safeLoadError(reason);
		}
	}

	const activePeriod = report?.requestedPeriod ?? period;
	const drilldowns = buildDrilldowns(activePeriod, report?.expensesByAccount ?? [], report?.cashflowMonthly ?? []);

	return {
		activeBook,
		period: activePeriod,
		selectedPreset: period.preset,
		presetOptions,
		validationError,
		loadError,
		report,
		sectionWarnings: sectionWarnings(report),
		drilldowns
	};
};
