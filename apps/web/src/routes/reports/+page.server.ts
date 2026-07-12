import { isHttpError, isRedirect } from '@sveltejs/kit';
import { apiFetch, getActiveBookContext, getAuthToken } from '$lib/api/server';
import type {
	CashflowData,
	CashflowPeriod,
	DeltaSectionStatus,
	ExpenseAccountComparison,
	ExpenseByAccount,
	MoneyDelta,
	PeriodReport,
	PeriodReportComparison,
	PeriodReportSectionStatus,
	ReportComparisonMode
} from '$lib/api/types';
import { localeFromCookie, t, type Locale } from '$lib/i18n';
import type { PageServerLoad } from './$types';

const ISO_DATE_RE = /^\d{4}-\d{2}-\d{2}$/;
const REPORT_PRESETS = ['this-month', 'last-month', 'year-to-date', 'custom'] as const;
const COMPARISON_MODES = ['previous_equivalent', 'same_period_last_year', 'custom'] as const;
const REPORT_SECTION_KEYS = ['summary', 'cashflow', 'monthly_cashflow', 'expenses_by_account'] as const;
const DELTA_SECTION_KEYS = ['summary', 'cashflow', 'expenses_by_account'] as const;
const DAY_MS = 24 * 60 * 60 * 1000;

type ReportPreset = (typeof REPORT_PRESETS)[number];
type ComparisonMode = (typeof COMPARISON_MODES)[number];
type ReportSectionKey = (typeof REPORT_SECTION_KEYS)[number];
type DeltaSectionKey = (typeof DELTA_SECTION_KEYS)[number];

type ReportPeriod = {
	preset: ReportPreset;
	dateFrom: string;
	dateTo: string;
};

type ComparisonPeriod = {
	mode: ComparisonMode;
	dateFrom: string;
	dateTo: string;
};

type PeriodResolution = {
	period: ReportPeriod;
	validationError: string | null;
};

type ComparisonResolution = {
	comparison: ComparisonPeriod;
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

type ReportSectionErrors = Record<ReportSectionKey, string | null>;
type DeltaSectionMessages = Record<DeltaSectionKey, string | null>;

type ReportView = {
	requestedPeriod: ReportPeriod;
	reportingBasis: string;
	includesCurrencyConversion: boolean;
	limitations: string[];
	partialFailure: boolean;
	empty: boolean;
	summary: ReportSummaryView | null;
	cashflow: CashflowData | null;
	cashflowMonthly: CashflowPeriod[];
	expensesByAccount: ExpenseByAccount[];
	sectionErrors: ReportSectionErrors;
};

type MoneyDeltaView = {
	primary: string;
	comparison: string;
	delta: string;
	absoluteDelta: string;
	currency: string;
};

type SummaryDeltaView = {
	assets: MoneyDeltaView;
	liabilities: MoneyDeltaView;
	netWorth: MoneyDeltaView;
};

type CashflowDeltaView = {
	inflow: MoneyDeltaView;
	outflow: MoneyDeltaView;
	net: MoneyDeltaView;
};

type ExpenseChangeView = {
	accountId: string;
	accountName: string;
	primaryTotal: string;
	comparisonTotal: string;
	delta: string | null;
	absoluteDelta: string | null;
	currency: string;
	status: 'ok' | 'not_comparable';
};

type ComparisonReportView = {
	bookId: number;
	comparisonMode: ComparisonMode;
	primary: ReportView;
	comparison: ReportView;
	reportingBasis: string;
	includesCurrencyConversion: boolean;
	limitations: string[];
	partialFailure: boolean;
	empty: boolean;
	comparable: boolean;
	deltaSectionMessages: DeltaSectionMessages;
	summaryDelta: SummaryDeltaView | null;
	cashflowDelta: CashflowDeltaView | null;
	expenseChanges: ExpenseChangeView[];
};

type DrilldownLinks = {
	period: string;
	cashflowByMonth: Record<string, string>;
	expensesByAccount: Record<string, string>;
};

type ComparisonDrilldownLinks = {
	primary: DrilldownLinks;
	comparison: DrilldownLinks;
	expenseChanges: Record<string, { primary: string; comparison: string }>;
};

type SectionWarning = {
	source: 'primary' | 'comparison';
	section: string;
	message: string;
};

function formatDate(date: Date): string {
	return date.toISOString().slice(0, 10);
}

function strictIsoDate(value: string): boolean {
	if (!ISO_DATE_RE.test(value)) return false;
	const date = new Date(`${value}T00:00:00Z`);
	return !Number.isNaN(date.getTime()) && formatDate(date) === value;
}

function parseIsoDate(value: string): Date {
	return new Date(`${value}T00:00:00Z`);
}

function addDays(value: string, days: number): string {
	return formatDate(new Date(parseIsoDate(value).getTime() + days * DAY_MS));
}

function inclusiveDayCount(dateFrom: string, dateTo: string): number {
	return Math.floor((parseIsoDate(dateTo).getTime() - parseIsoDate(dateFrom).getTime()) / DAY_MS) + 1;
}

function daysInMonth(year: number, monthIndex: number): number {
	return new Date(Date.UTC(year, monthIndex + 1, 0)).getUTCDate();
}

function shiftOneYearBackClamp(value: string): string {
	const source = parseIsoDate(value);
	const year = source.getUTCFullYear() - 1;
	const month = source.getUTCMonth();
	const day = Math.min(source.getUTCDate(), daysInMonth(year, month));
	return formatDate(new Date(Date.UTC(year, month, day)));
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

function previousEquivalentRange(period: ReportPeriod): { dateFrom: string; dateTo: string } {
	const days = inclusiveDayCount(period.dateFrom, period.dateTo);
	return {
		dateFrom: addDays(period.dateFrom, -days),
		dateTo: addDays(period.dateFrom, -1)
	};
}

function samePeriodLastYearRange(period: ReportPeriod): { dateFrom: string; dateTo: string } {
	return {
		dateFrom: shiftOneYearBackClamp(period.dateFrom),
		dateTo: shiftOneYearBackClamp(period.dateTo)
	};
}

function expectedComparisonRange(mode: Exclude<ComparisonMode, 'custom'>, period: ReportPeriod): { dateFrom: string; dateTo: string } {
	return mode === 'same_period_last_year' ? samePeriodLastYearRange(period) : previousEquivalentRange(period);
}

function isReportPreset(value: string | null): value is ReportPreset {
	return REPORT_PRESETS.includes(value as ReportPreset);
}

function isComparisonMode(value: string | null): value is ComparisonMode {
	return COMPARISON_MODES.includes(value as ComparisonMode);
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

function fallbackComparisonPeriod(url: URL, period: ReportPeriod): ComparisonPeriod {
	const rawMode = url.searchParams.get('comparison_mode');
	const mode: ComparisonMode = isComparisonMode(rawMode) ? rawMode : 'previous_equivalent';
	const rawDateFrom = url.searchParams.get('comparison_date_from') ?? '';
	const rawDateTo = url.searchParams.get('comparison_date_to') ?? '';
	if (mode !== 'custom' && strictIsoDate(period.dateFrom) && strictIsoDate(period.dateTo) && period.dateFrom <= period.dateTo) {
		const expected = expectedComparisonRange(mode, period);
		return { mode, ...expected };
	}
	return { mode, dateFrom: rawDateFrom, dateTo: rawDateTo };
}

function resolveComparisonPeriod(url: URL, period: ReportPeriod, locale: Locale): ComparisonResolution {
	const rawMode = url.searchParams.get('comparison_mode');
	const mode = isComparisonMode(rawMode) ? rawMode : 'previous_equivalent';
	const rawDateFrom = url.searchParams.get('comparison_date_from') ?? '';
	const rawDateTo = url.searchParams.get('comparison_date_to') ?? '';
	const hasDateParam = url.searchParams.has('comparison_date_from') || url.searchParams.has('comparison_date_to');

	if (rawMode !== null && !isComparisonMode(rawMode)) {
		return {
			comparison: { mode, ...expectedComparisonRange('previous_equivalent', period) },
			validationError: t(locale, 'reports.comparison.validation.unsupportedMode')
		};
	}

	if (mode === 'custom') {
		if (!strictIsoDate(rawDateFrom) || !strictIsoDate(rawDateTo)) {
			return {
				comparison: { mode, dateFrom: rawDateFrom, dateTo: rawDateTo },
				validationError: t(locale, 'reports.comparison.validation.invalidDateRange')
			};
		}
		if (rawDateFrom > rawDateTo) {
			return {
				comparison: { mode, dateFrom: rawDateFrom, dateTo: rawDateTo },
				validationError: t(locale, 'reports.comparison.validation.invalidRange')
			};
		}
		return { comparison: { mode, dateFrom: rawDateFrom, dateTo: rawDateTo }, validationError: null };
	}

	const expected = expectedComparisonRange(mode, period);
	if (hasDateParam) {
		if (!strictIsoDate(rawDateFrom) || !strictIsoDate(rawDateTo)) {
			return {
				comparison: { mode, dateFrom: rawDateFrom, dateTo: rawDateTo },
				validationError: t(locale, 'reports.comparison.validation.invalidDateRange')
			};
		}
		if (rawDateFrom !== expected.dateFrom || rawDateTo !== expected.dateTo) {
			return {
				comparison: { mode, dateFrom: rawDateFrom, dateTo: rawDateTo },
				validationError: t(locale, 'reports.comparison.validation.inconsistentRange', {
					dateFrom: expected.dateFrom,
					dateTo: expected.dateTo
				})
			};
		}
	}
	return { comparison: { mode, ...expected }, validationError: null };
}

function reportsUrl(period: ReportPeriod, comparison: ComparisonPeriod): string {
	const params = new URLSearchParams({
		preset: period.preset,
		date_from: period.dateFrom,
		date_to: period.dateTo,
		comparison_mode: comparison.mode,
		comparison_date_from: comparison.dateFrom,
		comparison_date_to: comparison.dateTo
	});
	return `/reports?${params.toString()}`;
}

function comparisonForPrimary(period: ReportPeriod, comparison: ComparisonPeriod): ComparisonPeriod {
	if (comparison.mode === 'custom') return comparison;
	return { mode: comparison.mode, ...expectedComparisonRange(comparison.mode, period) };
}

function buildPresetOptions(period: ReportPeriod, comparison: ComparisonPeriod, locale: Locale) {
	return (['this-month', 'last-month', 'year-to-date'] as const).map((preset) => {
		const range = presetRange(preset);
		const nextPeriod = { preset, dateFrom: range.dateFrom, dateTo: range.dateTo };
		const labelKey =
			preset === 'this-month'
				? 'reports.preset.thisMonth'
				: preset === 'last-month'
					? 'reports.preset.lastMonth'
					: 'reports.preset.yearToDate';
		return {
			id: preset,
			label: t(locale, labelKey),
			href: reportsUrl(nextPeriod, comparisonForPrimary(nextPeriod, comparison)),
			active: period.preset === preset && period.dateFrom === range.dateFrom && period.dateTo === range.dateTo
		};
	});
}

function buildComparisonModeOptions(period: ReportPeriod, comparison: ComparisonPeriod, locale: Locale) {
	return (['previous_equivalent', 'same_period_last_year'] as const).map((mode) => {
		const nextComparison = { mode, ...expectedComparisonRange(mode, period) };
		return {
			id: mode,
			label:
				mode === 'previous_equivalent'
					? t(locale, 'reports.comparison.mode.previousEquivalent')
					: t(locale, 'reports.comparison.mode.samePeriodLastYear'),
			href: reportsUrl(period, nextComparison),
			active: comparison.mode === mode,
			dateFrom: nextComparison.dateFrom,
			dateTo: nextComparison.dateTo
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

function buildComparisonDrilldowns(report: ComparisonReportView): ComparisonDrilldownLinks {
	return {
		primary: buildDrilldowns(report.primary.requestedPeriod, report.primary.expensesByAccount, report.primary.cashflowMonthly),
		comparison: buildDrilldowns(report.comparison.requestedPeriod, report.comparison.expensesByAccount, report.comparison.cashflowMonthly),
		expenseChanges: Object.fromEntries(
			report.expenseChanges.map((expense) => [
				expense.accountId,
				{
					primary: transactionFilterHref({
						account_id: expense.accountId,
						date_from: report.primary.requestedPeriod.dateFrom,
						date_to: report.primary.requestedPeriod.dateTo
					}),
					comparison: transactionFilterHref({
						account_id: expense.accountId,
						date_from: report.comparison.requestedPeriod.dateFrom,
						date_to: report.comparison.requestedPeriod.dateTo
					})
				}
			])
		)
	};
}

function fallbackComparisonDrilldowns(period: ReportPeriod, comparison: ComparisonPeriod): ComparisonDrilldownLinks {
	return {
		primary: buildDrilldowns(period, [], []),
		comparison: buildDrilldowns({ preset: 'custom', dateFrom: comparison.dateFrom, dateTo: comparison.dateTo }, [], []),
		expenseChanges: {}
	};
}

function stringValue(value: unknown): string | null {
	return typeof value === 'string' && value.trim() ? value : null;
}

function normalizeSummary(
	value: PeriodReport['summary'],
	cashflow: CashflowData | null,
	fallbackCurrency: string
): ReportSummaryView | null {
	const summary = {
		currency: stringValue(value?.currency) ?? stringValue(cashflow?.currency) ?? fallbackCurrency,
		income: stringValue(cashflow?.inflow),
		expenses: stringValue(cashflow?.outflow),
		net: stringValue(cashflow?.net),
		assets: stringValue(value?.assets),
		liabilities: stringValue(value?.liabilities),
		netWorth: stringValue(value?.net_worth)
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

function emptySectionErrors(): ReportSectionErrors {
	return {
		summary: null,
		cashflow: null,
		monthly_cashflow: null,
		expenses_by_account: null
	};
}

function emptyDeltaSectionMessages(): DeltaSectionMessages {
	return {
		summary: null,
		cashflow: null,
		expenses_by_account: null
	};
}

function sectionErrorFromStatus(
	statuses: PeriodReportSectionStatus[],
	section: ReportSectionKey,
	locale: Locale
): string | null {
	const status = statuses.find((candidate) => candidate.section === section);
	return status?.status === 'error' ? t(locale, 'reports.sectionError.redacted') : null;
}

function sectionErrorsFromStatuses(statuses: PeriodReportSectionStatus[], locale: Locale): ReportSectionErrors {
	return {
		summary: sectionErrorFromStatus(statuses, 'summary', locale),
		cashflow: sectionErrorFromStatus(statuses, 'cashflow', locale),
		monthly_cashflow: sectionErrorFromStatus(statuses, 'monthly_cashflow', locale),
		expenses_by_account: sectionErrorFromStatus(statuses, 'expenses_by_account', locale)
	};
}

function deltaSectionMessageFromStatus(statuses: DeltaSectionStatus[], section: DeltaSectionKey, locale: Locale): string | null {
	const status = statuses.find((candidate) => candidate.section === section);
	if (status?.status === 'error') return t(locale, 'reports.comparison.deltaError');
	if (status?.status === 'not_comparable') return t(locale, 'reports.comparison.notComparable');
	if (status?.status === 'empty') return t(locale, 'reports.comparison.emptyDelta');
	return null;
}

function deltaSectionMessagesFromStatuses(statuses: DeltaSectionStatus[], locale: Locale): DeltaSectionMessages {
	return {
		summary: deltaSectionMessageFromStatus(statuses, 'summary', locale),
		cashflow: deltaSectionMessageFromStatus(statuses, 'cashflow', locale),
		expenses_by_account: deltaSectionMessageFromStatus(statuses, 'expenses_by_account', locale)
	};
}

function normalizeReportView(periodReport: PeriodReport, period: ReportPeriod, locale: Locale): ReportView {
	const cashflow = normalizeCashflow(periodReport.cashflow);
	const cashflowMonthly = normalizeCashflowPeriods(periodReport.monthly_cashflow);
	const expensesByAccount = normalizeExpenses(periodReport.expenses_by_account);
	const fallbackCurrency =
		stringValue(periodReport.currency) ?? stringValue(periodReport.summary?.currency) ?? cashflow?.currency ?? expensesByAccount[0]?.currency ?? 'base';
	const requestedPeriod: ReportPeriod = {
		preset: period.preset,
		dateFrom: stringValue(periodReport.date_from) ?? period.dateFrom,
		dateTo: stringValue(periodReport.date_to) ?? period.dateTo
	};

	return {
		requestedPeriod,
		reportingBasis: stringValue(periodReport.reporting_basis) ?? 'base_currency_only',
		includesCurrencyConversion: periodReport.includes_currency_conversion === true,
		limitations: Array.isArray(periodReport.limitations) ? periodReport.limitations : [],
		partialFailure: periodReport.partial_failure === true,
		empty: periodReport.empty === true,
		summary: normalizeSummary(periodReport.summary, cashflow, fallbackCurrency),
		cashflow,
		cashflowMonthly,
		expensesByAccount,
		sectionErrors: Array.isArray(periodReport.section_statuses)
			? sectionErrorsFromStatuses(periodReport.section_statuses, locale)
			: emptySectionErrors()
	};
}

function normalizeMoneyDelta(value: MoneyDelta | null | undefined): MoneyDeltaView | null {
	const primary = stringValue(value?.primary);
	const comparison = stringValue(value?.comparison);
	const delta = stringValue(value?.delta);
	const absoluteDelta = stringValue(value?.absolute_delta);
	const currency = stringValue(value?.currency);
	if (!primary || !comparison || !delta || !absoluteDelta || !currency) return null;
	return { primary, comparison, delta, absoluteDelta, currency };
}

function normalizeSummaryDelta(value: PeriodReportComparison['summary_delta']): SummaryDeltaView | null {
	if (!value) return null;
	const assets = normalizeMoneyDelta(value.assets);
	const liabilities = normalizeMoneyDelta(value.liabilities);
	const netWorth = normalizeMoneyDelta(value.net_worth);
	if (!assets || !liabilities || !netWorth) return null;
	return { assets, liabilities, netWorth };
}

function normalizeCashflowDelta(value: PeriodReportComparison['cashflow_delta']): CashflowDeltaView | null {
	if (!value) return null;
	const inflow = normalizeMoneyDelta(value.inflow);
	const outflow = normalizeMoneyDelta(value.outflow);
	const net = normalizeMoneyDelta(value.net);
	if (!inflow || !outflow || !net) return null;
	return { inflow, outflow, net };
}

function normalizeExpenseChanges(value: ExpenseAccountComparison[] | null | undefined): ExpenseChangeView[] {
	return Array.isArray(value)
		? value
				.map((expense) => ({
					accountId: stringValue(expense.account_id),
					accountName: stringValue(expense.account_name),
					primaryTotal: stringValue(expense.primary_total),
					comparisonTotal: stringValue(expense.comparison_total),
					delta: stringValue(expense.delta),
					absoluteDelta: stringValue(expense.absolute_delta),
					currency: stringValue(expense.currency),
					status: expense.status === 'not_comparable' ? ('not_comparable' as const) : ('ok' as const)
				}))
				.filter(
					(expense): expense is ExpenseChangeView =>
						Boolean(
							expense.accountId &&
								expense.accountName &&
								expense.primaryTotal &&
								expense.comparisonTotal &&
								expense.currency &&
								(expense.status === 'not_comparable' || (expense.delta && expense.absoluteDelta))
						)
				)
		: [];
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

async function loadComparisonReport(
	fetchFn: typeof fetch,
	bookPrefix: string,
	token: string,
	period: ReportPeriod,
	comparison: ComparisonPeriod,
	locale: Locale
): Promise<{ comparisonReport: ComparisonReportView | null; loadError: string | null }> {
	const comparisonParams = new URLSearchParams({
		date_from: period.dateFrom,
		date_to: period.dateTo,
		comparison_mode: comparison.mode,
		comparison_date_from: comparison.dateFrom,
		comparison_date_to: comparison.dateTo
	});

	try {
		const payload = await apiFetch<PeriodReportComparison>(fetchFn, `${bookPrefix}/reports/comparison?${comparisonParams.toString()}`, token);
		const primary = normalizeReportView(payload.primary, period, locale);
		const comparisonReport = normalizeReportView(payload.comparison, { preset: 'custom', dateFrom: comparison.dateFrom, dateTo: comparison.dateTo }, locale);
		const comparisonMode = isComparisonMode(payload.comparison_mode) ? payload.comparison_mode : comparison.mode;
		const deltaSectionStatuses = Array.isArray(payload.delta_section_statuses) ? payload.delta_section_statuses : [];

		return {
			comparisonReport: {
				bookId: payload.book_id,
				comparisonMode,
				primary,
				comparison: comparisonReport,
				reportingBasis: stringValue(payload.reporting_basis) ?? 'base_currency_only',
				includesCurrencyConversion: payload.includes_currency_conversion === true,
				limitations: Array.isArray(payload.limitations) ? payload.limitations : [],
				partialFailure: payload.partial_failure === true,
				empty: payload.empty === true,
				comparable: payload.comparable === true,
				deltaSectionMessages: deltaSectionMessagesFromStatuses(deltaSectionStatuses, locale),
				summaryDelta: normalizeSummaryDelta(payload.summary_delta),
				cashflowDelta: normalizeCashflowDelta(payload.cashflow_delta),
				expenseChanges: normalizeExpenseChanges(payload.expense_changes)
			},
			loadError: null
		};
	} catch (reason) {
		if (isRedirect(reason)) throw reason;
		return { comparisonReport: null, loadError: safeLoadError(reason, locale) };
	}
}

function sectionWarnings(report: ComparisonReportView | null): SectionWarning[] {
	if (!report) return [];
	return [
		...Object.entries(report.primary.sectionErrors)
			.filter((entry): entry is [string, string] => entry[1] !== null)
			.map(([section, message]) => ({ source: 'primary' as const, section, message })),
		...Object.entries(report.comparison.sectionErrors)
			.filter((entry): entry is [string, string] => entry[1] !== null)
			.map(([section, message]) => ({ source: 'comparison' as const, section, message }))
	];
}

export const load: PageServerLoad = async ({ cookies, fetch, url }) => {
	const locale = localeFromCookie(cookies);
	const token = getAuthToken(cookies);
	const { activeBook, bookPrefix } = await getActiveBookContext(fetch, cookies, token);
	const periodResolution = resolvePeriod(url, locale);
	const comparisonResolution = periodResolution.validationError
		? { comparison: fallbackComparisonPeriod(url, periodResolution.period), validationError: null }
		: resolveComparisonPeriod(url, periodResolution.period, locale);
	const validationError = periodResolution.validationError ?? comparisonResolution.validationError;

	let comparisonReport: ComparisonReportView | null = null;
	let loadError: string | null = null;

	if (!validationError) {
		const result = await loadComparisonReport(fetch, bookPrefix, token, periodResolution.period, comparisonResolution.comparison, locale);
		comparisonReport = result.comparisonReport;
		loadError = result.loadError;
	}

	const activePeriod = comparisonReport?.primary.requestedPeriod ?? periodResolution.period;
	const activeComparison: ComparisonPeriod = comparisonReport
		? {
				mode: comparisonReport.comparisonMode,
				dateFrom: comparisonReport.comparison.requestedPeriod.dateFrom,
				dateTo: comparisonReport.comparison.requestedPeriod.dateTo
			}
		: comparisonResolution.comparison;
	const presetOptions = buildPresetOptions(activePeriod, activeComparison, locale);
	const comparisonModeOptions = buildComparisonModeOptions(activePeriod, activeComparison, locale);
	const drilldowns = comparisonReport
		? buildComparisonDrilldowns(comparisonReport)
		: fallbackComparisonDrilldowns(activePeriod, activeComparison);

	return {
		activeBook,
		locale,
		period: activePeriod,
		comparisonPeriod: activeComparison,
		selectedPreset: periodResolution.period.preset,
		presetOptions,
		comparisonModeOptions,
		validationError,
		loadError,
		report: comparisonReport?.primary ?? null,
		comparisonReport,
		sectionWarnings: sectionWarnings(comparisonReport),
		drilldowns
	};
};
