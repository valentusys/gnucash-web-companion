<script lang="ts">
	import EmptyState from '$lib/components/EmptyState.svelte';
	import { DEFAULT_LOCALE, t, type Locale } from '$lib/i18n';

	let { data } = $props();
	let locale = $derived<Locale>(data.locale ?? DEFAULT_LOCALE);

	function formatDate(value: string | null): string {
		return value ?? t(locale, 'scheduled.notConfigured');
	}

	function formatNumber(value: number | null): string {
		return value === null ? t(locale, 'scheduled.notConfigured') : String(value);
	}

	function formatBoolean(value: boolean): string {
		return value ? t(locale, 'scheduled.yes') : t(locale, 'scheduled.no');
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
</script>

<svelte:head>
	<title>{t(locale, 'scheduled.title')} — GnuCash Web Companion</title>
</svelte:head>

<main class="mx-auto max-w-6xl px-4 py-8">
	<div class="mb-6 space-y-3">
		<p class="text-sm font-medium uppercase tracking-wide" style="color: var(--app-accent);">{t(locale, 'scheduled.kicker')}</p>
		<div class="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
			<div>
				<h1 class="text-3xl font-bold" style="color: var(--app-text);">{t(locale, 'scheduled.title')}</h1>
				<p class="mt-2 max-w-3xl text-sm" style="color: var(--app-muted);">
					{t(locale, 'scheduled.subtitle')}
				</p>
			</div>
			{#if data.activeBook}
				<div class="rounded-2xl border px-4 py-3 text-sm" style="border-color: var(--app-border); background-color: var(--app-card-bg);">
					<p class="font-semibold" style="color: var(--app-text);">{t(locale, 'scheduled.activeBook')}</p>
					<p class="mt-1" style="color: var(--app-muted);">{data.activeBook.name}</p>
				</div>
			{/if}
		</div>
	</div>

	<section class="rounded-2xl border p-4 shadow-sm" style="border-color: var(--app-border); background-color: var(--app-card-bg);">
		<div class="mb-4 flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
			<div>
				<h2 class="text-lg font-semibold" style="color: var(--app-text);">{t(locale, 'scheduled.recurringMetadata')}</h2>
				<p class="text-sm" style="color: var(--app-muted);">
					{t(locale, 'scheduled.metadataHelp')}
				</p>
			</div>
			<span class="inline-flex w-fit rounded-full border px-3 py-1 text-xs font-semibold" style="border-color: var(--app-border); color: var(--app-muted);">
				{t(locale, 'scheduled.readOnlyBadge')}
			</span>
		</div>

		<div class="mb-4 grid gap-3 rounded-xl border p-3 text-sm md:grid-cols-3" style="border-color: var(--app-border); background-color: var(--app-bg);">
			<div>
				<p class="font-semibold" style="color: var(--app-text);">{t(locale, 'scheduled.statusFilter')}</p>
				<div class="mt-2 flex flex-wrap gap-2">
					<a class={`rounded-lg border px-3 py-2 ${activeClass(data.filters.status === 'all')}`} style={activeStyle(data.filters.status === 'all')} href={data.filters.links.all}>{t(locale, 'scheduled.all')} ({data.scheduledSummary.total})</a>
					<a class={`rounded-lg border px-3 py-2 ${activeClass(data.filters.status === 'enabled')}`} style={activeStyle(data.filters.status === 'enabled')} href={data.filters.links.enabled}>{t(locale, 'scheduled.enabled')} ({data.scheduledSummary.enabled})</a>
					<a class={`rounded-lg border px-3 py-2 ${activeClass(data.filters.status === 'disabled')}`} style={activeStyle(data.filters.status === 'disabled')} href={data.filters.links.disabled}>{t(locale, 'scheduled.disabled')} ({data.scheduledSummary.disabled})</a>
				</div>
			</div>
			<div>
				<p class="font-semibold" style="color: var(--app-text);">{t(locale, 'scheduled.templateFilter')}</p>
				<div class="mt-2 flex flex-wrap gap-2">
					<a class={`rounded-lg border px-3 py-2 ${activeClass(data.filters.template === 'all')}`} style={activeStyle(data.filters.template === 'all')} href={data.filters.links.allTemplates}>{t(locale, 'scheduled.all')} ({data.scheduledSummary.total})</a>
					<a class={`rounded-lg border px-3 py-2 ${activeClass(data.filters.template === 'with_template')}`} style={activeStyle(data.filters.template === 'with_template')} href={data.filters.links.withTemplate}>{t(locale, 'scheduled.templatePresent')} ({data.scheduledSummary.withTemplate})</a>
					<a class={`rounded-lg border px-3 py-2 ${activeClass(data.filters.template === 'without_template')}`} style={activeStyle(data.filters.template === 'without_template')} href={data.filters.links.withoutTemplate}>{t(locale, 'scheduled.noTemplateReference')} ({data.scheduledSummary.withoutTemplate})</a>
				</div>
			</div>
			<div>
				<p class="font-semibold" style="color: var(--app-text);">{t(locale, 'scheduled.sortDisplay')}</p>
				<div class="mt-2 flex flex-wrap gap-2">
					<a class={`rounded-lg border px-3 py-2 ${activeClass(data.filters.sort === 'start_date')}`} style={activeStyle(data.filters.sort === 'start_date')} href={data.filters.links.startDate}>{t(locale, 'scheduled.startDate')}</a>
					<a class={`rounded-lg border px-3 py-2 ${activeClass(data.filters.sort === 'name')}`} style={activeStyle(data.filters.sort === 'name')} href={data.filters.links.name}>{t(locale, 'scheduled.name')}</a>
					<a class={`rounded-lg border px-3 py-2 ${activeClass(data.filters.sort === 'enabled_first')}`} style={activeStyle(data.filters.sort === 'enabled_first')} href={data.filters.links.enabledFirst}>{t(locale, 'scheduled.enabledFirst')}</a>
				</div>
			</div>
			<p class="md:col-span-3" style="color: var(--app-muted);">
				{t(locale, 'scheduled.shownStatus', { shown: data.scheduledSummary.shown, total: data.scheduledSummary.total })}
				{#if data.filters.status !== 'all' || data.filters.template !== 'all' || data.filters.sort !== 'start_date'}
					<a class="ml-2 font-semibold" style="color: var(--app-accent);" href={data.filters.links.clear}>{t(locale, 'scheduled.clearFilters')}</a>
				{/if}
			</p>
		</div>

		{#if data.scheduledTransactions.length}
			<div class="grid gap-3">
				{#each data.scheduledTransactions as scheduled (scheduled.id)}
					<article class="rounded-xl border p-4" style="border-color: var(--app-border); background-color: var(--app-bg);">
						<div class="flex flex-col gap-2 md:flex-row md:items-start md:justify-between">
							<div>
								<h3 class="text-lg font-semibold" style="color: var(--app-text);">{scheduled.name || t(locale, 'scheduled.unnamed')}</h3>
								<div class="mt-2 flex flex-wrap gap-2">
									<span class="rounded-full px-2 py-1 text-xs font-semibold" style="background-color: var(--app-accent-soft); color: var(--app-accent);">{scheduled.enabled ? t(locale, 'scheduled.enabled') : t(locale, 'scheduled.disabled')}</span>
									<span class="rounded-full px-2 py-1 text-xs font-semibold" style="background-color: var(--app-hover-bg); color: var(--app-muted);">{t(locale, 'scheduled.templateAccount')}: {formatBoolean(scheduled.has_template_account)}</span>
								</div>
							</div>
						</div>

						<dl class="mt-4 grid gap-3 text-sm sm:grid-cols-3">
							<div>
								<dt class="font-medium" style="color: var(--app-muted);">{t(locale, 'scheduled.startDate')}</dt>
								<dd class="mt-1" style="color: var(--app-text);">{formatDate(scheduled.start_date)}</dd>
							</div>
							<div>
								<dt class="font-medium" style="color: var(--app-muted);">{t(locale, 'scheduled.endDate')}</dt>
								<dd class="mt-1" style="color: var(--app-text);">{formatDate(scheduled.end_date)}</dd>
							</div>
							<div>
								<dt class="font-medium" style="color: var(--app-muted);">{t(locale, 'scheduled.lastOccurred')}</dt>
								<dd class="mt-1" style="color: var(--app-text);">{formatDate(scheduled.last_occurred)}</dd>
							</div>
							<div>
								<dt class="font-medium" style="color: var(--app-muted);">{t(locale, 'scheduled.occurrences')}</dt>
								<dd class="mt-1" style="color: var(--app-text);">{t(locale, 'scheduled.occurrencesValue', { total: formatNumber(scheduled.num_occurrences), remaining: formatNumber(scheduled.remaining_occurrences) })}</dd>
							</div>
							<div>
								<dt class="font-medium" style="color: var(--app-muted);">{t(locale, 'scheduled.autoCreateNotify')}</dt>
								<dd class="mt-1" style="color: var(--app-text);">{formatBoolean(scheduled.auto_create)} / {formatBoolean(scheduled.auto_notify)}</dd>
							</div>
							<div>
								<dt class="font-medium" style="color: var(--app-muted);">{t(locale, 'scheduled.advanceDays')}</dt>
								<dd class="mt-1" style="color: var(--app-text);">{t(locale, 'scheduled.advanceDaysValue', { create: formatNumber(scheduled.advance_create_days), notify: formatNumber(scheduled.advance_notify_days) })}</dd>
							</div>
						</dl>

						<div class="mt-4 rounded-xl border p-3 text-sm" style="border-color: var(--app-border); background-color: var(--app-card-bg);">
							<p class="font-medium" style="color: var(--app-text);">{t(locale, 'scheduled.recurrenceMetadata')}</p>
							{#if scheduled.recurrence.length}
								<ul class="mt-2 list-disc space-y-1 pl-5" style="color: var(--app-muted);">
									{#each scheduled.recurrence as recurrence}
										<li>{recurrenceSummary(recurrence)}</li>
									{/each}
								</ul>
							{:else}
								<p class="mt-2" style="color: var(--app-muted);">{t(locale, 'scheduled.noRecurrenceMetadata')}</p>
							{/if}
						</div>

						<ul class="mt-4 list-disc space-y-1 pl-5 text-sm" style="color: var(--app-muted);">
							{#each scheduled.limitations as limitation}
								<li>{limitation}</li>
							{/each}
						</ul>
					</article>
				{/each}
			</div>
		{:else if data.scheduledSummary.total > 0}
			<EmptyState
				title={t(locale, 'scheduled.noMatchesTitle')}
				message={t(locale, 'scheduled.noMatchesMessage')}
				ariaLabel={t(locale, 'scheduled.noMatchesAria')}
				icon="🗓️"
			>
				<a
					href={data.filters.links.clear}
					class="rounded-xl px-4 py-2 text-sm font-semibold text-white"
					style="background-color: var(--app-accent);"
				>
					{t(locale, 'scheduled.clearFilters')}
				</a>
				<a
					href="/books"
					class="rounded-xl border px-4 py-2 text-sm font-semibold"
					style="border-color: var(--app-border); color: var(--app-text);"
				>
					{t(locale, 'scheduled.reviewBooks')}
				</a>
			</EmptyState>
		{:else}
			<EmptyState
				title={t(locale, 'scheduled.emptyTitle')}
				message={t(locale, 'scheduled.emptyMessage')}
				ariaLabel={t(locale, 'scheduled.emptyAria')}
				icon="🗓️"
			>
				<a
					href="/transactions"
					class="rounded-xl px-4 py-2 text-sm font-semibold text-white"
					style="background-color: var(--app-accent);"
				>
					{t(locale, 'scheduled.browseTransactions')}
				</a>
				<a
					href="/books"
					class="rounded-xl border px-4 py-2 text-sm font-semibold"
					style="border-color: var(--app-border); color: var(--app-text);"
				>
					{t(locale, 'scheduled.reviewBooks')}
				</a>
			</EmptyState>
		{/if}
	</section>
</main>
