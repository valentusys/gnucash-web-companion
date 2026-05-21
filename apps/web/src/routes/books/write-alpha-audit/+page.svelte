<script lang="ts">
	import EmptyState from '$lib/components/EmptyState.svelte';
	import { DEFAULT_LOCALE, t, type Locale, type MessageKey } from '$lib/i18n';
	import type { PageData } from './$types';

	type SelectOption = { value: string; labelKey: MessageKey };

	let { data }: { data: PageData } = $props();
	let locale = $derived<Locale>(data.locale ?? DEFAULT_LOCALE);
	const appliedFilters = $derived(data.auditSummary?.filters ?? {});
	const pagination = $derived(data.auditSummary?.pagination ?? {});
	const ownershipSummary = $derived(data.auditSummary?.ownership_summary ?? {});

	function pageHref(targetOffset: unknown): string {
		const params = new URLSearchParams();
		for (const key of ['action', 'result', 'since', 'until', 'limit']) {
			const value = appliedFilters[key];
			if (value !== null && value !== undefined && String(value) !== '') {
				params.set(key, String(value));
			}
		}
		params.set('offset', String(targetOffset ?? 0));
		return `/books/write-alpha-audit?${params.toString()}`;
	}

	const actionOptions: SelectOption[] = [
		{ value: '', labelKey: 'audit.allActions' },
		{ value: 'transaction.create', labelKey: 'audit.create' },
		{ value: 'transaction.patch', labelKey: 'audit.patch' },
		{ value: 'transaction.delete', labelKey: 'audit.delete' }
	];
	const resultOptions: SelectOption[] = [
		{ value: '', labelKey: 'audit.allResults' },
		{ value: 'success', labelKey: 'audit.success' },
		{ value: 'failed', labelKey: 'audit.failed' },
		{ value: 'started', labelKey: 'audit.started' },
		{ value: 'unknown', labelKey: 'audit.unknown' }
	];
</script>

<svelte:head>
	<title>{t(locale, 'audit.title')}</title>
</svelte:head>

<section class="min-w-0 space-y-6 overflow-x-hidden">
	<div class="rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-950 shadow-sm">
		<p class="font-semibold">{t(locale, 'audit.bannerTitle')}</p>
		<p class="mt-2">{t(locale, 'audit.bannerMessage')}</p>
		<p class="mt-2">{t(locale, 'audit.redactionMessage')}</p>
	</div>

	<div class="flex min-w-0 flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
		<div class="min-w-0">
			<p class="text-xs uppercase tracking-wide text-slate-500">{t(locale, 'audit.activeBook')}</p>
			<h1 class="truncate text-2xl font-semibold text-slate-900">{data.activeBook?.name ?? t(locale, 'audit.noAccessibleBook')}</h1>
		</div>
		<a class="inline-flex min-h-11 items-center justify-center rounded-full border border-slate-300 px-4 text-sm font-medium text-slate-700" href="/books">
			{t(locale, 'audit.reviewBooks')}
		</a>
	</div>

	<form method="GET" class="grid min-w-0 gap-3 rounded-2xl border border-slate-200 bg-white p-4 text-sm shadow-sm md:grid-cols-5" aria-label={t(locale, 'audit.filtersLabel')}>
		<label class="min-w-0 space-y-1">
			<span class="font-medium text-slate-700">{t(locale, 'audit.action')}</span>
			<select name="action" class="min-h-11 w-full min-w-0 rounded-xl border border-slate-300 bg-white px-3" autocomplete="off">
				{#each actionOptions as option}
					<option value={option.value} selected={appliedFilters.action === option.value || (!appliedFilters.action && option.value === '')}>{t(locale, option.labelKey)}</option>
				{/each}
			</select>
		</label>
		<label class="min-w-0 space-y-1">
			<span class="font-medium text-slate-700">{t(locale, 'audit.result')}</span>
			<select name="result" class="min-h-11 w-full min-w-0 rounded-xl border border-slate-300 bg-white px-3" autocomplete="off">
				{#each resultOptions as option}
					<option value={option.value} selected={appliedFilters.result === option.value || (!appliedFilters.result && option.value === '')}>{t(locale, option.labelKey)}</option>
				{/each}
			</select>
		</label>
		<label class="min-w-0 space-y-1">
			<span class="font-medium text-slate-700">{t(locale, 'audit.sinceIso')}</span>
			<input name="since" value={appliedFilters.since ?? ''} class="min-h-11 w-full min-w-0 rounded-xl border border-slate-300 px-3" placeholder="2026-05-20T10:00:00Z" autocomplete="off" />
		</label>
		<label class="min-w-0 space-y-1">
			<span class="font-medium text-slate-700">{t(locale, 'audit.untilIso')}</span>
			<input name="until" value={appliedFilters.until ?? ''} class="min-h-11 w-full min-w-0 rounded-xl border border-slate-300 px-3" placeholder="2026-05-20T11:00:00Z" autocomplete="off" />
		</label>
		<label class="min-w-0 space-y-1">
			<span class="font-medium text-slate-700">{t(locale, 'audit.limit')}</span>
			<select name="limit" class="min-h-11 w-full min-w-0 rounded-xl border border-slate-300 bg-white px-3" autocomplete="off">
				{#each [10, 25, 50, 100] as option}
					<option value={option} selected={String(appliedFilters.limit ?? 25) === String(option)}>{option}</option>
				{/each}
			</select>
		</label>
		<input type="hidden" name="offset" value="0" />
		<div class="flex flex-col gap-2 md:col-span-5 sm:flex-row">
			<button type="submit" class="inline-flex min-h-11 items-center justify-center rounded-full bg-slate-900 px-4 font-medium text-white">{t(locale, 'audit.applyFilters')}</button>
			<a href="/books/write-alpha-audit" class="inline-flex min-h-11 items-center justify-center rounded-full border border-slate-300 px-4 font-medium text-slate-700">{t(locale, 'audit.clearFilters')}</a>
		</div>
	</form>

	{#if data.auditSummary}
		<div class="grid min-w-0 gap-3 text-sm sm:grid-cols-2 lg:grid-cols-5" aria-label={t(locale, 'audit.countsLabel')}>
			<div class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
				<p class="text-xs uppercase tracking-wide text-slate-500">{t(locale, 'audit.filteredRows')}</p>
				<p class="mt-1 text-2xl font-semibold text-slate-900">{data.auditSummary.total_count}</p>
				<p class="text-slate-600">{t(locale, 'audit.returnedCount', { count: String(data.auditSummary.returned_count) })}</p>
			</div>
			<div class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
				<p class="text-xs uppercase tracking-wide text-slate-500">{t(locale, 'audit.actions')}</p>
				<p class="break-words text-slate-700">{t(locale, 'audit.create')} {data.auditSummary.counts_by_action['transaction.create'] ?? 0} · {t(locale, 'audit.patch')} {data.auditSummary.counts_by_action['transaction.patch'] ?? 0} · {t(locale, 'audit.delete')} {data.auditSummary.counts_by_action['transaction.delete'] ?? 0}</p>
			</div>
			<div class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
				<p class="text-xs uppercase tracking-wide text-slate-500">{t(locale, 'audit.results')}</p>
				<p class="break-words text-slate-700">{t(locale, 'audit.success')} {data.auditSummary.counts_by_result.success ?? 0} · {t(locale, 'audit.failed')} {data.auditSummary.counts_by_result.failed ?? 0}</p>
			</div>
			<div class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
				<p class="text-xs uppercase tracking-wide text-slate-500">{t(locale, 'audit.window')}</p>
				<p class="break-words text-slate-700">{t(locale, 'audit.requestedWindow', { since: data.auditSummary.time_window.requested_since ?? t(locale, 'audit.noStart'), until: data.auditSummary.time_window.requested_until ?? t(locale, 'audit.noEnd') })}</p>
				<p class="mt-1 break-words text-slate-600">{t(locale, 'audit.returnedWindow', { oldest: data.auditSummary.time_window.oldest_returned ?? t(locale, 'audit.none'), newest: data.auditSummary.time_window.newest_returned ?? t(locale, 'audit.none') })}</p>
			</div>
			<div class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
				<p class="text-xs uppercase tracking-wide text-slate-500">{t(locale, 'audit.ownership')}</p>
				<p class="break-words text-slate-700">{t(locale, 'audit.ownedCreated')}: {ownershipSummary.write_alpha_created_count ?? 0} · {t(locale, 'audit.nonOwnedRejected')}: {ownershipSummary.non_owned_mutation_rejections_count ?? 0}</p>
				<p class="mt-1 break-words text-slate-600">{t(locale, 'audit.lastMutation')}: {ownershipSummary.last_mutation_type ?? t(locale, 'audit.none')}</p>
			</div>
		</div>
	{/if}

	{#if !data.auditSummary || data.auditSummary.items.length === 0}
		<EmptyState
			title={t(locale, 'audit.emptyTitle')}
			message={t(locale, 'audit.emptyMessage')}
		>
			<a class="inline-flex min-h-11 items-center justify-center rounded-full border border-slate-300 px-4 text-sm font-medium text-slate-700" href="/transactions">
				{t(locale, 'audit.browseTransactions')}
			</a>
		</EmptyState>
	{:else}
		<div class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
			<div class="border-b border-slate-100 px-4 py-3 text-sm text-slate-600">
				<p>{t(locale, 'audit.showingEntries', { returned: String(data.auditSummary.returned_count), total: String(data.auditSummary.total_count) })}</p>
				<p class="mt-1">{t(locale, 'audit.pageStatus', { offset: String(pagination.offset ?? 0), limit: String(pagination.limit ?? 25) })}</p>
				{#if data.auditSummary.status_summary.length}
					<ul class="mt-2 list-disc space-y-1 pl-5">
						{#each data.auditSummary.status_summary as statusLine}
							<li>{statusLine}</li>
						{/each}
					</ul>
				{/if}
			</div>
			<ul class="divide-y divide-slate-100">
				{#each data.auditSummary.items as item}
					<li class="grid min-w-0 gap-3 p-4 text-sm md:grid-cols-[minmax(0,10rem)_7rem_minmax(0,11rem)_8rem_minmax(0,1fr)] md:items-center">
						<div class="min-w-0">
							<p class="text-xs uppercase tracking-wide text-slate-500">{t(locale, 'audit.action')}</p>
							<p class="truncate font-medium text-slate-900">{item.action}</p>
						</div>
						<div class="min-w-0">
							<p class="text-xs uppercase tracking-wide text-slate-500">{t(locale, 'audit.result')}</p>
							<p class="truncate font-medium text-slate-900">{item.result}</p>
						</div>
						<div class="min-w-0">
							<p class="text-xs uppercase tracking-wide text-slate-500">{t(locale, 'audit.timestamp')}</p>
							<p class="break-words text-slate-700">{item.timestamp}</p>
						</div>
						<div class="min-w-0">
							<p class="text-xs uppercase tracking-wide text-slate-500">{t(locale, 'audit.txnPrefix')}</p>
							<p class="truncate font-mono text-slate-700">{item.transaction_id_prefix ?? t(locale, 'audit.none')}</p>
						</div>
						<div class="min-w-0">
							<p class="text-xs uppercase tracking-wide text-slate-500">{t(locale, 'audit.backupSafeError')}</p>
							<p class="text-slate-700">{item.backup_present ? t(locale, 'audit.backupPresent') : t(locale, 'audit.backupMissing')}</p>
							{#if item.backup_artifact_ref}
								<p class="mt-1 truncate font-mono text-xs text-slate-600">{t(locale, 'audit.backupRef')}: {item.backup_artifact_ref}</p>
							{/if}
							{#if item.error}
								<p class="mt-1 break-words text-slate-700">{item.error}</p>
							{/if}
						</div>
					</li>
				{/each}
			</ul>
			<nav class="flex min-w-0 flex-col gap-2 border-t border-slate-100 px-4 py-3 text-sm sm:flex-row sm:items-center sm:justify-between" aria-label={t(locale, 'audit.paginationLabel')}>
				<p class="text-slate-600">{t(locale, 'audit.paginationSummary', { offset: String(pagination.offset ?? 0), limit: String(pagination.limit ?? 25) })}</p>
				<div class="flex min-w-0 flex-col gap-2 sm:flex-row">
					{#if pagination.has_previous}
						<a class="inline-flex min-h-11 items-center justify-center rounded-full border border-slate-300 px-4 font-medium text-slate-700" href={pageHref(pagination.previous_offset)}>{t(locale, 'audit.previousPage')}</a>
					{/if}
					{#if pagination.has_next}
						<a class="inline-flex min-h-11 items-center justify-center rounded-full border border-slate-300 px-4 font-medium text-slate-700" href={pageHref(pagination.next_offset)}>{t(locale, 'audit.nextPage')}</a>
					{/if}
				</div>
			</nav>
		</div>
	{/if}

	{#if data.auditSummary?.limitations.length}
		<div class="rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700">
			<p class="font-semibold text-slate-900">{t(locale, 'audit.limitations')}</p>
			<ul class="mt-2 list-disc space-y-1 pl-5">
				{#each data.auditSummary.limitations as limitation}
					<li>{limitation}</li>
				{/each}
			</ul>
		</div>
	{/if}
</section>
