import { isHttpError, isRedirect } from '@sveltejs/kit';
import { apiFetch, getActiveBookContext, getAuthToken } from '$lib/api/server';
import type { CashflowData, CashflowPeriod, ExpenseByAccount, ReportSummary } from '$lib/api/types';
import { localeFromCookie, t, type Locale } from '$lib/i18n';
import type { PageServerLoad } from './$types';

const ISO_DATE_RE = /^\d{4}-\d{2}-\d{2}$/;
const REPORT_PRESETS = ['this-month', 'last-month', 'year-to-date', 'custom'] as const;

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

type ReportSectionErrors = Record<'summary' | 'cashflow' | 'expenses_by_account', string | null>;

type ReportView = {
	requestedPeriod: ReportPeriod;
	reportingBasis: string;
	includesCurrencyConversion: boolean;
	limitations: string[];
	summary: ReportSummaryView | null;
	cashflow: CashflowData | null;
	cashflowMonthly: CashflowPeriod[];
	expensesByAccount: ExpenseByAccount[];
	sectionErrors: ReportSectionErrors;
};

type DrilldownLinks = {
	period: string;
	cashflowByMonth: Record<string, string>;
	expensesByAccount: Record<string, string>;
};

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

function resolvePeriod(url: URL, locale: Locale): PeriodResolution {
	const rawPreset = url.searchParams.get('preset');
	const requestedPreset = isReportPreset(rawPreset) ? rawPreset : null;
	const hasDateParam = url.searchParams.has('date_from') || url.searchParams.has('date_to');
	const rawDateFrom = url.searchParams.get('date_from') ?? '';
	const rawDateTo = url.searchParams.get('date_to') ?? '';

	if (hasDateParam || requestedPreset === 'custom') {
		if (!strictIsoDate(rawDateFrom) || !strictIsoDate(rawDateTo)) {
			return {
				period: { preset: requestedPreset ?? 'custom', dateFrom: rawDateFrom, dateTo: rawDateTo },
				validationError: t(locale, 'reports.validation.invalidDateRange')
			};
		}
		if (rawDateFrom > rawDateTo) {
			return {
				period: { preset: requestedPreset ?? 'custom', dateFrom: rawDateFrom, dateTo: rawDateTo },
				validationError: t(locale, 'reports.validation.invalidRange')
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
			validationError: t(locale, 'reports.validation.unsupportedPreset')
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

function buildPresetOptions(period: ReportPeriod, locale: Locale) {
	return (['this-month', 'last-month', 'year-to-date'] as const).map((preset) => {
		const range = presetRange(preset);
		const labelKey =
			preset === 'this-month'
				? 'reports.preset.thisMonth'
				: preset === 'last-month'
					? 'reports.preset.lastMonth'
					: 'reports.preset.yearToDate';
		return {
			id: preset,
			label: t(locale, labelKey),
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

function normalizeSummary(value: ReportSummary | null, fallbackCurrency: string): ReportSummaryView | null {
	if (!value) return null;
	const summary = {
		currency: stringValue(value.currency) ?? fallbackCurrency,
		income: stringValue(value.income_this_month),
		expenses: stringValue(value.expenses_this_month),
		net: null,
		assets: stringValue(value.assets),
		liabilities: stringValue(value.liabilities),
		netWorth: stringValue(value.net_worth)
	};
	if (!summary.income && !summary.expenses && !summary.net && !summary.assets && !summary.liabilities && !summary.netWorth) {
		return null;
	}
	return summary;
}

function normalizeCashflow(value: CashflowData | null): CashflowData | null {
	if (!value) return null;
	if (!stringValue(value.inflow) && !stringValue(value.outflow) && !stringValue(value.net)) return null;
	return value;
}

function normalizeCashflowPeriods(periods: CashflowPeriod[] | null): CashflowPeriod[] {
	return Array.isArray(periods)
		? periods.filter((period) => stringValue(period.month) && stringValue(period.inflow) && stringValue(period.outflow) && stringValue(period.net))
		: [];
}

function normalizeExpenses(value: ExpenseByAccount[] | null): ExpenseByAccount[] {
	return Array.isArray(value)
		? value.filter((expense) => stringValue(expense.account_id) && stringValue(expense.account_name) && stringValue(expense.total) && stringValue(expense.currency))
		: [];
}

function isFulfilled<T>(result: PromiseSettledResult<T>): result is PromiseFulfilledResult<T> {
	return result.status === 'fulfilled';
}

function rethrowRedirects(results: PromiseSettledResult<unknown>[]): void {
	for (const result of results) {
		if (result.status === 'rejected' && isRedirect(result.reason)) throw result.reason;
	}
}

function sectionError(result: PromiseSettledResult<unknown>, locale: Locale): string | null {
	return result.status === 'rejected' ? t(locale, 'reports.sectionError.redacted') : null;
}

function safeLoadError(reason: unknown, locale: Locale): string {
	if (isHttpError(reason)) {
		if (reason.status === 403) return t(locale, 'reports.error.forbidden');
		if (reason.status === 404) return t(locale, 'reports.error.notFound');
		if (reason.status === 502 || reason.status === 503) return t(locale, 'reports.error.serviceUnavailable');
		return t(locale, 'reports.error.requestFailed');
	}
	return t(locale, 'reports.error.unknown');
}

async function loadReport(
	fetchFn: typeof fetch,
	bookPrefix: string,
	token: string,
	period: ReportPeriod,
	locale: Locale
): Promise<{ report: ReportView | null; loadError: string | null }> {
	const summaryParams = new URLSearchParams({ as_of_date: period.dateTo });
	const rangeParams = new URLSearchParams({ date_from: period.dateFrom, date_to: period.dateTo });
	const monthlyParams = new URLSearchParams({ date_from: period.dateFrom, date_to: period.dateTo, by_month: 'true' });

	const [summaryResult, cashflowResult, monthlyResult, expensesResult] = await Promise.allSettled([
		apiFetch<ReportSummary>(fetchFn, `${bookPrefix}/reports/summary?${summaryParams.toString()}`, token),
		apiFetch<CashflowData>(fetchFn, `${bookPrefix}/reports/cashflow?${rangeParams.toString()}`, token),
		apiFetch<CashflowPeriod[]>(fetchFn, `${bookPrefix}/reports/cashflow?${monthlyParams.toString()}`, token),
		apiFetch<ExpenseByAccount[]>(fetchFn, `${bookPrefix}/reports/expenses-by-account?${rangeParams.toString()}`, token)
	]);
	const settled = [summaryResult, cashflowResult, monthlyResult, expensesResult] as PromiseSettledResult<unknown>[];
	rethrowRedirects(settled);

	const fulfilledCount = settled.filter(isFulfilled).length;
	if (fulfilledCount === 0) {
		const firstFailure = settled.find((result) => result.status === 'rejected');
		return { report: null, loadError: safeLoadError(firstFailure?.status === 'rejected' ? firstFailure.reason : null, locale) };
	}

	const summaryResponse = isFulfilled(summaryResult) ? summaryResult.value : null;
	const cashflow = normalizeCashflow(isFulfilled(cashflowResult) ? cashflowResult.value : null);
	const cashflowMonthly = normalizeCashflowPeriods(isFulfilled(monthlyResult) ? monthlyResult.value : null);
	const expensesByAccount = normalizeExpenses(isFulfilled(expensesResult) ? expensesResult.value : null);
	const fallbackCurrency = summaryResponse?.currency ?? cashflow?.currency ?? expensesByAccount[0]?.currency ?? 'base';

	return {
		report: {
			requestedPeriod: period,
			reportingBasis: summaryResponse?.reporting_basis ?? 'base_currency_only',
			includesCurrencyConversion: summaryResponse?.includes_currency_conversion === true,
			limitations: Array.isArray(summaryResponse?.limitations) ? summaryResponse.limitations : [],
			summary: normalizeSummary(summaryResponse, fallbackCurrency),
			cashflow,
			cashflowMonthly,
			expensesByAccount,
			sectionErrors: {
				summary: sectionError(summaryResult, locale),
				cashflow: sectionError(cashflowResult, locale) ?? sectionError(monthlyResult, locale),
				expenses_by_account: sectionError(expensesResult, locale)
			}
		},
		loadError: null
	};
}

function sectionWarnings(report: ReportView | null) {
	if (!report) return [];
	return Object.entries(report.sectionErrors)
		.filter((entry): entry is [string, string] => entry[1] !== null)
		.map(([section, message]) => ({ section, message }));
}

export const load: PageServerLoad = async ({ cookies, fetch, url }) => {
	const locale = localeFromCookie(cookies);
	const token = getAuthToken(cookies);
	const { activeBook, bookPrefix } = await getActiveBookContext(fetch, cookies, token);
	const { period, validationError } = resolvePeriod(url, locale);
	const presetOptions = buildPresetOptions(period, locale);

	let report: ReportView | null = null;
	let loadError: string | null = null;

	if (!validationError) {
		const result = await loadReport(fetch, bookPrefix, token, period, locale);
		report = result.report;
		loadError = result.loadError;
	}

	const activePeriod = report?.requestedPeriod ?? period;
	const drilldowns = buildDrilldowns(activePeriod, report?.expensesByAccount ?? [], report?.cashflowMonthly ?? []);

	return {
		activeBook,
		locale,
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