import { apiFetch, getActiveBookContext, getAuthToken } from '$lib/api/server';
import type { ScheduledTransaction } from '$lib/api/types';
import type { PageServerLoad } from './$types';

type ScheduledStatusFilter = 'all' | 'enabled' | 'disabled';
type ScheduledTemplateFilter = 'all' | 'with_template' | 'without_template';
type ScheduledSort = 'next_due' | 'name' | 'enabled_first';
type ScheduledForecastGroupKey = 'overdue' | 'upcoming' | 'next_30_days' | 'later_or_inactive' | 'unavailable';

type ScheduledForecastGroups = Record<ScheduledForecastGroupKey, ScheduledTransaction[]>;

const STATUS_FILTERS: ScheduledStatusFilter[] = ['all', 'enabled', 'disabled'];
const TEMPLATE_FILTERS: ScheduledTemplateFilter[] = ['all', 'with_template', 'without_template'];
const SORT_OPTIONS: ScheduledSort[] = ['next_due', 'name', 'enabled_first'];
const GROUP_ORDER: ScheduledForecastGroupKey[] = ['overdue', 'upcoming', 'next_30_days', 'later_or_inactive', 'unavailable'];

function normalizeParam<T extends string>(value: string | null, allowed: readonly T[], fallback: T): T {
	return value && allowed.includes(value as T) ? (value as T) : fallback;
}

function scheduledFilterHref(status: ScheduledStatusFilter, template: ScheduledTemplateFilter, sort: ScheduledSort): string {
	const params = new URLSearchParams();
	if (status !== 'all') params.set('status', status);
	if (template !== 'all') params.set('template', template);
	if (sort !== 'next_due') params.set('sort', sort);
	const query = params.toString();
	return query ? `/scheduled?${query}` : '/scheduled';
}

function filterScheduledTransactions(
	items: ScheduledTransaction[],
	status: ScheduledStatusFilter,
	template: ScheduledTemplateFilter
): ScheduledTransaction[] {
	return items.filter((item) => {
		if (status === 'enabled' && !item.enabled) return false;
		if (status === 'disabled' && item.enabled) return false;
		if (template === 'with_template' && !item.has_template_account) return false;
		if (template === 'without_template' && item.has_template_account) return false;
		return true;
	});
}

function nextDueSortValue(item: ScheduledTransaction): string {
	return item.forecast.next_due_date ?? '9999-99-99';
}

function sortScheduledTransactions(items: ScheduledTransaction[], sort: ScheduledSort): ScheduledTransaction[] {
	return [...items].sort((a, b) => {
		if (sort === 'name') {
			return (a.name || '').localeCompare(b.name || '') || a.id.localeCompare(b.id);
		}
		if (sort === 'enabled_first') {
			return Number(b.enabled) - Number(a.enabled)
				|| nextDueSortValue(a).localeCompare(nextDueSortValue(b))
				|| a.id.localeCompare(b.id);
		}
		return nextDueSortValue(a).localeCompare(nextDueSortValue(b))
			|| (a.name || '').localeCompare(b.name || '')
			|| a.id.localeCompare(b.id);
	});
}

function forecastGroupKey(item: ScheduledTransaction): ScheduledForecastGroupKey {
	const { forecast } = item;
	if (forecast.status === 'unavailable') return 'unavailable';
	if (forecast.is_overdue) return 'overdue';
	const nextDue = forecast.next_due_date;
	if (nextDue && forecast.upcoming_7_days.includes(nextDue)) return 'upcoming';
	if (nextDue && forecast.upcoming_30_days.includes(nextDue)) return 'next_30_days';
	return 'later_or_inactive';
}

function groupScheduledTransactions(items: ScheduledTransaction[]): ScheduledForecastGroups {
	const groups: ScheduledForecastGroups = {
		overdue: [],
		upcoming: [],
		next_30_days: [],
		later_or_inactive: [],
		unavailable: []
	};
	for (const item of items) groups[forecastGroupKey(item)].push(item);
	return groups;
}

export const load: PageServerLoad = async ({ cookies, fetch, url }) => {
	const token = getAuthToken(cookies);
	const { books, activeBook, bookPrefix } = await getActiveBookContext(fetch, cookies, token);
	const scheduledTransactionsRaw = activeBook
		? await apiFetch<ScheduledTransaction[]>(fetch, `${bookPrefix}/scheduled-transactions`, token)
		: [];
	const statusFilter = normalizeParam(url.searchParams.get('status'), STATUS_FILTERS, 'all');
	const templateFilter = normalizeParam(url.searchParams.get('template'), TEMPLATE_FILTERS, 'all');
	const sort = normalizeParam(url.searchParams.get('sort'), SORT_OPTIONS, 'next_due');
	const scheduledTransactions = sortScheduledTransactions(
		filterScheduledTransactions(scheduledTransactionsRaw, statusFilter, templateFilter),
		sort
	);
	const grouped = groupScheduledTransactions(scheduledTransactions);
	const enabledCount = scheduledTransactionsRaw.filter((item) => item.enabled).length;
	const disabledCount = scheduledTransactionsRaw.length - enabledCount;
	const templateCount = scheduledTransactionsRaw.filter((item) => item.has_template_account).length;

	return {
		books,
		activeBook,
		scheduledTransactions,
		scheduledGroups: GROUP_ORDER.map((key) => ({ key, items: grouped[key], count: grouped[key].length }))
			.filter((group) => group.count > 0),
		scheduledSummary: {
			total: scheduledTransactionsRaw.length,
			shown: scheduledTransactions.length,
			unavailable: scheduledTransactionsRaw.filter((item) => item.forecast.status === 'unavailable').length,
			enabled: enabledCount,
			disabled: disabledCount,
			withTemplate: templateCount,
			withoutTemplate: scheduledTransactionsRaw.length - templateCount,
			overdue: grouped.overdue.length,
			upcoming: grouped.upcoming.length,
			next30Days: grouped.next_30_days.length,
			laterOrInactive: grouped.later_or_inactive.length
		},
		filters: {
			status: statusFilter,
			template: templateFilter,
			sort,
			links: {
				all: scheduledFilterHref('all', templateFilter, sort),
				enabled: scheduledFilterHref('enabled', templateFilter, sort),
				disabled: scheduledFilterHref('disabled', templateFilter, sort),
				allTemplates: scheduledFilterHref(statusFilter, 'all', sort),
				withTemplate: scheduledFilterHref(statusFilter, 'with_template', sort),
				withoutTemplate: scheduledFilterHref(statusFilter, 'without_template', sort),
				nextDue: scheduledFilterHref(statusFilter, templateFilter, 'next_due'),
				name: scheduledFilterHref(statusFilter, templateFilter, 'name'),
				enabledFirst: scheduledFilterHref(statusFilter, templateFilter, 'enabled_first'),
				clear: scheduledFilterHref('all', 'all', 'next_due')
			}
		}
	};
};
