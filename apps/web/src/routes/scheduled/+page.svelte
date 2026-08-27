<script lang="ts">
	import EmptyState from '$lib/components/EmptyState.svelte';
	import Money from '$lib/components/Money.svelte';
	import type { ScheduledTransactionAmount } from '$lib/api/types';
	import { DEFAULT_LOCALE, t, type Locale, type MessageKey } from '$lib/i18n';

	let { data } = $props();
	let locale = $derived<Locale>(data.locale ?? DEFAULT_LOCALE);

	const groupLabelKeys: Record<string, MessageKey> = {
		overdue: 'scheduled.group.overdue',
		upcoming: 'scheduled.group.upcoming',
		next_30_days: 'scheduled.group.next30',
		later_or_inactive: 'scheduled.group.laterOrInactive'
	};

	function formatDate(value: string | null): string {
		return value ?? t(locale, 'scheduled.notConfigured');
	}

	function formatNumber(value: number | null): string {
		return value === null ? t(locale, 'scheduled.notConfigured') : String(value);
	}

	function formatBoolean(value: boolean): string {
		return value ? t(locale, 'scheduled.yes') : t(locale, 'scheduled.no');
	}

	function templateStatusLabel(status: string): string {
		return status === 'present_redacted'
			? t(locale, 'scheduled.templatePresentRedacted')
			: t(locale, 'scheduled.templateNotPresentRedacted');
	}

	function activeClass(active: boolean): string {
		return active ? 'border-transparent text-white' : 'border-[var(--app-border)]';
	}

	function activeStyle(active: boolean): string {
		return active ? 'background-color: var(--app-accent);' : 'color: var(--app-text);';
	}

	function recurrenceSummary(item: { period_type: string; multiplier: number | null; period_start: string | null; weekend_adjust: string }): string {
		const parts = [
			item.multiplier === null ? null : t(locale, 'scheduled.recurrenceEvery', { count: item.multiplier }),
			item.period_type || null,
			item.period_start ? t(locale, 'scheduled.recurrenceFrom', { date: item.period_start }) : null,
			item.weekend_adjust ? t(locale, 'scheduled.recurrenceWeekend', { value: item.weekend_adjust }) : null
		].filter(Boolean);
		return parts.length ? parts.join(' · ') : t(locale, 'scheduled.recurrenceUnavailable');
	}

	function hasResolvedAmount(
		amount: ScheduledTransactionAmount
	): amount is ScheduledTransactionAmount & { status: 'resolved'; amount: string; currency: string } {
		return amount.status === 'resolved' && amount.amount !== null && amount.currency !== null;
	}

	function groupLabel(key: string): string {
		return t(locale, groupLabelKeys[key] ?? 'scheduled.group.laterOrInactive');
	}

	function forecastStatusLabel(status: 'ready' | 'disabled' | 'exhausted'): string {
		return t(locale, `scheduled.forecast.status.${status}` as MessageKey);
	}

	function boundedDates(values: string[]): string {
		return values.length ? values.join(', ') : t(locale, 'scheduled.forecast.none');
	}
</script>

<svelte:head>
	<title>{t(locale, 'scheduled.title')} — GnuCash Web Companion</title>
</svelte:head>

<main class="mx-auto max-w-5xl px-3 py-5 sm:px-4 sm:py-6">
	<header class="mb-4 min-w-0">
		<div class="flex min-w-0 flex-wrap items-end justify-between gap-2">
			<div class="min-w-0">
				<p class="text-xs font-medium uppercase tracking-wide sm:text-sm" style="color: var(--app-accent);">{t(locale, 'scheduled.kicker')}</p>
				<h1 class="mt-1 text-2xl font-bold sm:text-3xl" style="color: var(--app-text);">{t(locale, 'scheduled.title')}</h1>
			</div>
			{#if data.activeBook}
				<p class="max-w-full truncate text-xs sm:text-sm" style="color: var(--app-muted);" title={`${t(locale, 'scheduled.activeBook')}: ${data.activeBook.name}`}>
					{t(locale, 'scheduled.activeBook')}: <span class="font-semibold" style="color: var(--app-text);">{data.activeBook.name}</span>
				</p>
			{/if}
		</div>
		<p class="mt-2 max-w-3xl text-sm" style="color: var(--app-muted);">{t(locale, 'scheduled.subtitle')}</p>
	</header>

	<section class="mb-4 rounded-xl border p-3 shadow-sm" style="border-color: var(--app-border); background-color: var(--app-card-bg);" aria-label={t(locale, 'scheduled.filterSummary')}>
		<div class="flex min-w-0 flex-wrap items-center justify-between gap-2 text-sm">
			<p class="min-w-0" style="color: var(--app-muted);">
				{t(locale, 'scheduled.shownStatus', { shown: data.scheduledSummary.shown, total: data.scheduledSummary.total })}
			</p>
			<span class="shrink-0 rounded-full border px-2 py-1 text-xs font-semibold" style="border-color: var(--app-border); color: var(--app-muted);">
				{t(locale, 'scheduled.readOnlyBadge')}
			</span>
		</div>
		{#if data.scheduledSummary.total > 0}
			<div class="mt-3 hidden flex-wrap gap-2 sm:flex" aria-label={t(locale, 'scheduled.recurringMetadata')}>
				{#each [
					['overdue', data.scheduledSummary.overdue],
					['upcoming', data.scheduledSummary.upcoming],
					['next_30_days', data.scheduledSummary.next30Days],
					['later_or_inactive', data.scheduledSummary.laterOrInactive]
				] as [key, count]}
					<span class="rounded-full px-2 py-1 text-xs font-medium" style="background-color: var(--app-hover-bg); color: var(--app-muted);">
						{groupLabel(String(key))}: {count}
					</span>
				{/each}
			</div>
		{/if}
		<details class="mt-3 min-w-0">
			<summary class="w-fit cursor-pointer text-sm font-semibold underline-offset-2 hover:underline focus:outline-none focus:ring-2" style="color: var(--app-accent);">
				{t(locale, 'scheduled.filterSummary')}
			</summary>
			<div class="mt-3 grid min-w-0 gap-3 rounded-xl border p-3 text-sm md:grid-cols-3" style="border-color: var(--app-border); background-color: var(--app-bg);">
				<div class="min-w-0">
					<p class="font-semibold" style="color: var(--app-text);">{t(locale, 'scheduled.statusFilter')}</p>
					<div class="mt-2 flex flex-wrap gap-2">
						<a class={`rounded-lg border px-3 py-2 ${activeClass(data.filters.status === 'all')}`} style={activeStyle(data.filters.status === 'all')} href={data.filters.links.all}>{t(locale, 'scheduled.all')} ({data.scheduledSummary.total})</a>
						<a class={`rounded-lg border px-3 py-2 ${activeClass(data.filters.status === 'enabled')}`} style={activeStyle(data.filters.status === 'enabled')} href={data.filters.links.enabled}>{t(locale, 'scheduled.enabled')} ({data.scheduledSummary.enabled})</a>
						<a class={`rounded-lg border px-3 py-2 ${activeClass(data.filters.status === 'disabled')}`} style={activeStyle(data.filters.status === 'disabled')} href={data.filters.links.disabled}>{t(locale, 'scheduled.disabled')} ({data.scheduledSummary.disabled})</a>
					</div>
				</div>
				<div class="min-w-0">
					<p class="font-semibold" style="color: var(--app-text);">{t(locale, 'scheduled.templateFilter')}</p>
					<div class="mt-2 flex flex-wrap gap-2">
						<a class={`rounded-lg border px-3 py-2 ${activeClass(data.filters.template === 'all')}`} style={activeStyle(data.filters.template === 'all')} href={data.filters.links.allTemplates}>{t(locale, 'scheduled.all')} ({data.scheduledSummary.total})</a>
						<a class={`rounded-lg border px-3 py-2 ${activeClass(data.filters.template === 'with_template')}`} style={activeStyle(data.filters.template === 'with_template')} href={data.filters.links.withTemplate}>{t(locale, 'scheduled.templatePresent')} ({data.scheduledSummary.withTemplate})</a>
						<a class={`rounded-lg border px-3 py-2 ${activeClass(data.filters.template === 'without_template')}`} style={activeStyle(data.filters.template === 'without_template')} href={data.filters.links.withoutTemplate}>{t(locale, 'scheduled.noTemplateReference')} ({data.scheduledSummary.withoutTemplate})</a>
					</div>
				</div>
				<div class="min-w-0">
					<p class="font-semibold" style="color: var(--app-text);">{t(locale, 'scheduled.sortDisplay')}</p>
					<div class="mt-2 flex flex-wrap gap-2">
						<a class={`rounded-lg border px-3 py-2 ${activeClass(data.filters.sort === 'next_due')}`} style={activeStyle(data.filters.sort === 'next_due')} href={data.filters.links.nextDue}>{t(locale, 'scheduled.nextDueFirst')}</a>
						<a class={`rounded-lg border px-3 py-2 ${activeClass(data.filters.sort === 'name')}`} style={activeStyle(data.filters.sort === 'name')} href={data.filters.links.name}>{t(locale, 'scheduled.name')}</a>
						<a class={`rounded-lg border px-3 py-2 ${activeClass(data.filters.sort === 'enabled_first')}`} style={activeStyle(data.filters.sort === 'enabled_first')} href={data.filters.links.enabledFirst}>{t(locale, 'scheduled.enabledFirst')}</a>
					</div>
				</div>
				{#if data.filters.status !== 'all' || data.filters.template !== 'all' || data.filters.sort !== 'next_due'}
					<a class="font-semibold md:col-span-3" style="color: var(--app-accent);" href={data.filters.links.clear}>{t(locale, 'scheduled.clearFilters')}</a>
				{/if}
			</div>
		</details>
	</section>

	{#if data.scheduledTransactions.length}
		<div class="grid min-w-0 gap-5">
			{#each data.scheduledGroups as group}
				<section class="min-w-0" data-schedule-group={group.key} aria-labelledby={`schedule-group-${group.key}`}>
					<div class="mb-2 flex items-center justify-between gap-2">
						<h2 id={`schedule-group-${group.key}`} class="text-lg font-semibold" style="color: var(--app-text);">{groupLabel(group.key)}</h2>
						<span class="rounded-full border px-2 py-0.5 text-xs font-semibold" style="border-color: var(--app-border); color: var(--app-muted);">{group.count}</span>
					</div>
					<div class="grid min-w-0 gap-2">
						{#each group.items as scheduled, index (scheduled.id)}
							<article
								class="min-w-0 rounded-xl border p-3 shadow-sm"
								style="border-color: var(--app-border); background-color: var(--app-card-bg);"
								data-schedule-row
								data-first-meaningful-card={index === 0 && group === data.scheduledGroups[0] ? 'true' : undefined}
							>
								<div class="grid min-w-0 grid-cols-[minmax(0,1fr)_minmax(5rem,auto)] items-start gap-2">
									<div class="min-w-0">
										<div class="flex min-w-0 flex-wrap items-center gap-2 text-xs">
											<span class="font-semibold uppercase tracking-wide" style={`color: ${group.key === 'overdue' ? 'var(--app-danger)' : 'var(--app-accent)'};`}>
												{scheduled.forecast.next_due_date ? `${t(locale, 'scheduled.nextDue')}: ${scheduled.forecast.next_due_date}` : t(locale, 'scheduled.noDueDate')}
											</span>
											<span class="rounded-full px-2 py-0.5 font-semibold" style="background-color: var(--app-hover-bg); color: var(--app-muted);">
												{scheduled.enabled ? t(locale, 'scheduled.enabled') : t(locale, 'scheduled.disabled')}
											</span>
										</div>
										<h3 class="mt-1 break-words text-base font-semibold" style="color: var(--app-text);">{scheduled.name || t(locale, 'scheduled.unnamed')}</h3>
									</div>
									<div class="min-w-0 max-w-28 text-right">
										<p class="text-xs font-medium" style="color: var(--app-muted);">{t(locale, 'scheduled.amount.label')}</p>
										{#if hasResolvedAmount(scheduled.amount)}
											<p class="mt-1 font-semibold" style="color: var(--app-text);">
												<Money amount={scheduled.amount.amount} currency={scheduled.amount.currency} />
											</p>
										{:else}
											<p class="mt-1 text-xs" style="color: var(--app-muted);">{t(locale, 'scheduled.amount.unavailable')}</p>
										{/if}
									</div>
								</div>

								<details class="mt-2 min-w-0 border-t pt-2 text-sm" style="border-color: var(--app-border);">
									<summary class="w-fit cursor-pointer font-semibold underline-offset-2 hover:underline focus:outline-none focus:ring-2" style="color: var(--app-accent);">
										{t(locale, 'scheduled.details.summary')}
									</summary>
									<div class="mt-3 min-w-0 space-y-3">
										<dl class="grid min-w-0 gap-2 sm:grid-cols-2 lg:grid-cols-4">
											<div><dt class="font-medium" style="color: var(--app-muted);">{t(locale, 'scheduled.forecast.asOf')}</dt><dd class="break-words" style="color: var(--app-text);">{scheduled.forecast.as_of_date}</dd></div>
											<div><dt class="font-medium" style="color: var(--app-muted);">{t(locale, 'scheduled.forecast.status')}</dt><dd style="color: var(--app-text);">{forecastStatusLabel(scheduled.forecast.status)}</dd></div>
											<div><dt class="font-medium" style="color: var(--app-muted);">{t(locale, 'scheduled.startDate')}</dt><dd style="color: var(--app-text);">{formatDate(scheduled.start_date)}</dd></div>
											<div><dt class="font-medium" style="color: var(--app-muted);">{t(locale, 'scheduled.endDate')}</dt><dd style="color: var(--app-text);">{formatDate(scheduled.end_date)}</dd></div>
											<div><dt class="font-medium" style="color: var(--app-muted);">{t(locale, 'scheduled.lastOccurred')}</dt><dd style="color: var(--app-text);">{formatDate(scheduled.last_occurred)}</dd></div>
											<div><dt class="font-medium" style="color: var(--app-muted);">{t(locale, 'scheduled.occurrences')}</dt><dd style="color: var(--app-text);">{t(locale, 'scheduled.occurrencesValue', { total: formatNumber(scheduled.num_occurrences), remaining: formatNumber(scheduled.remaining_occurrences) })}</dd></div>
											<div><dt class="font-medium" style="color: var(--app-muted);">{t(locale, 'scheduled.autoCreateNotify')}</dt><dd style="color: var(--app-text);">{formatBoolean(scheduled.auto_create)} / {formatBoolean(scheduled.auto_notify)}</dd></div>
											<div><dt class="font-medium" style="color: var(--app-muted);">{t(locale, 'scheduled.templateReferenceStatus')}</dt><dd class="break-words" style="color: var(--app-text);">{templateStatusLabel(scheduled.template_reference_status)}</dd></div>
										</dl>
										<div class="grid min-w-0 gap-2 sm:grid-cols-2">
											<p class="min-w-0 break-words"><span class="font-medium" style="color: var(--app-muted);">{t(locale, 'scheduled.forecast.upcoming7')}:</span> {boundedDates(scheduled.forecast.upcoming_7_days)}</p>
											<p class="min-w-0 break-words"><span class="font-medium" style="color: var(--app-muted);">{t(locale, 'scheduled.forecast.upcoming30')}:</span> {boundedDates(scheduled.forecast.upcoming_30_days)}</p>
										</div>
										<div class="min-w-0 rounded-lg border p-3" style="border-color: var(--app-border); background-color: var(--app-bg);">
											<p class="font-medium" style="color: var(--app-text);">{t(locale, 'scheduled.recurrenceMetadata')}</p>
											{#if scheduled.recurrence.length}
												<ul class="mt-2 list-disc space-y-1 pl-5" style="color: var(--app-muted);">
													{#each scheduled.recurrence as recurrence}
														<li class="break-words">{recurrenceSummary(recurrence)}</li>
													{/each}
												</ul>
											{:else}
												<p class="mt-2" style="color: var(--app-muted);">{t(locale, 'scheduled.noRecurrenceMetadata')}</p>
											{/if}
										</div>
										{#if scheduled.new_transactions_created === 0}
											<p class="text-xs" style="color: var(--app-muted);">{t(locale, 'scheduled.forecast.readOnlyInvariant')}</p>
										{/if}
									</div>
								</details>
							</article>
						{/each}
					</div>
				</section>
			{/each}
		</div>
	{:else if data.scheduledSummary.total > 0}
		<EmptyState
			title={t(locale, 'scheduled.noMatchesTitle')}
			message={t(locale, 'scheduled.noMatchesMessage')}
			ariaLabel={t(locale, 'scheduled.noMatchesAria')}
			icon="🗓️"
		>
			<a href={data.filters.links.clear} class="rounded-xl px-4 py-2 text-sm font-semibold text-white" style="background-color: var(--app-accent);">{t(locale, 'scheduled.clearFilters')}</a>
			<a href="/books" class="rounded-xl border px-4 py-2 text-sm font-semibold" style="border-color: var(--app-border); color: var(--app-text);">{t(locale, 'scheduled.reviewBooks')}</a>
		</EmptyState>
	{:else}
		<EmptyState
			title={t(locale, 'scheduled.emptyTitle')}
			message={t(locale, 'scheduled.emptyMessage')}
			ariaLabel={t(locale, 'scheduled.emptyAria')}
			icon="🗓️"
		>
			<a href="/transactions" class="rounded-xl px-4 py-2 text-sm font-semibold text-white" style="background-color: var(--app-accent);">{t(locale, 'scheduled.browseTransactions')}</a>
			<a href="/books" class="rounded-xl border px-4 py-2 text-sm font-semibold" style="border-color: var(--app-border); color: var(--app-text);">{t(locale, 'scheduled.reviewBooks')}</a>
		</EmptyState>
	{/if}
</main>
