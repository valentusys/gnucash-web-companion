import { apiFetch, getActiveBookContext, getAuthToken } from '$lib/api/server';
import type { ScheduledTransaction } from '$lib/api/types';
import type { PageServerLoad } from './$types';

type ScheduledStatusFilter = 'all' | 'enabled' | 'disabled';
type ScheduledTemplateFilter = 'all' | 'with_template' | 'without_template';
type ScheduledSort = 'start_date' | 'name' | 'enabled_first';

const STATUS_FILTERS: ScheduledStatusFilter[] = ['all', 'enabled', 'disabled'];
const TEMPLATE_FILTERS: ScheduledTemplateFilter[] = ['all', 'with_template', 'without_template'];
const SORT_OPTIONS: ScheduledSort[] = ['start_date', 'name', 'enabled_first'];

function normalizeParam<T extends string>(value: string | null, allowed: readonly T[], fallback: T): T {
	return value && allowed.includes(value as T) ? (value as T) : fallback;
}

function scheduledFilterHref(status: ScheduledStatusFilter, template: ScheduledTemplateFilter, sort: ScheduledSort): string {
	const params = new URLSearchParams();
	if (status !== 'all') params.set('status', status);
	if (template !== 'all') params.set('template', template);
	if (sort !== 'start_date') params.set('sort', sort);
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

function sortScheduledTransactions(items: ScheduledTransaction[], sort: ScheduledSort): ScheduledTransaction[] {
	return [...items].sort((a, b) => {
		if (sort === 'name') {
			return (a.name || '').localeCompare(b.name || '') || a.id.localeCompare(b.id);
		}
		if (sort === 'enabled_first') {
			return Number(b.enabled) - Number(a.enabled) || (a.start_date ?? '9999-99-99').localeCompare(b.start_date ?? '9999-99-99') || a.id.localeCompare(b.id);
		}
		return (a.start_date ?? '9999-99-99').localeCompare(b.start_date ?? '9999-99-99') || (a.name || '').localeCompare(b.name || '') || a.id.localeCompare(b.id);
	});
}

export const load: PageServerLoad = async ({ cookies, fetch, url }) => {
	const token = getAuthToken(cookies);
	const { books, activeBook, bookPrefix } = await getActiveBookContext(fetch, cookies, token);
	const scheduledTransactionsRaw = activeBook
		? await apiFetch<ScheduledTransaction[]>(fetch, `${bookPrefix}/scheduled-transactions`, token)
		: [];
	const statusFilter = normalizeParam(url.searchParams.get('status'), STATUS_FILTERS, 'all');
	const templateFilter = normalizeParam(url.searchParams.get('template'), TEMPLATE_FILTERS, 'all');
	const sort = normalizeParam(url.searchParams.get('sort'), SORT_OPTIONS, 'start_date');
	const scheduledTransactions = sortScheduledTransactions(
		filterScheduledTransactions(scheduledTransactionsRaw, statusFilter, templateFilter),
		sort
	);
	const enabledCount = scheduledTransactionsRaw.filter((item) => item.enabled).length;
	const disabledCount = scheduledTransactionsRaw.length - enabledCount;
	const templateCount = scheduledTransactionsRaw.filter((item) => item.has_template_account).length;

	return {
		books,
		activeBook,
		scheduledTransactions,
		scheduledSummary: {
			total: scheduledTransactionsRaw.length,
			shown: scheduledTransactions.length,
			enabled: enabledCount,
			disabled: disabledCount,
			withTemplate: templateCount,
			withoutTemplate: scheduledTransactionsRaw.length - templateCount
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
				startDate: scheduledFilterHref(statusFilter, templateFilter, 'start_date'),
				name: scheduledFilterHref(statusFilter, templateFilter, 'name'),
				enabledFirst: scheduledFilterHref(statusFilter, templateFilter, 'enabled_first'),
				clear: scheduledFilterHref('all', 'all', 'start_date')
			}
		}
	};
};
