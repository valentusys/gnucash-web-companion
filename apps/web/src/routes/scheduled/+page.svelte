<script lang="ts">
	import EmptyState from '$lib/components/EmptyState.svelte';

	let { data } = $props();

	function formatDate(value: string | null): string {
		return value ?? 'Not configured';
	}

	function formatNumber(value: number | null): string {
		return value === null ? 'Not configured' : String(value);
	}

	function formatBoolean(value: boolean): string {
		return value ? 'Yes' : 'No';
	}

	function activeClass(active: boolean): string {
		return active ? 'border-transparent text-white' : 'border-[var(--app-border)]';
	}

	function activeStyle(active: boolean): string {
		return active ? 'background-color: var(--app-accent);' : 'color: var(--app-text);';
	}

	function recurrenceSummary(item: { period_type: string; multiplier: number | null; period_start: string | null; weekend_adjust: string }): string {
		const parts = [
			item.multiplier === null ? null : `every ${item.multiplier}`,
			item.period_type || null,
			item.period_start ? `from ${item.period_start}` : null,
			item.weekend_adjust ? `weekend: ${item.weekend_adjust}` : null
		].filter(Boolean);
		return parts.length ? parts.join(' · ') : 'Raw recurrence metadata unavailable';
	}
</script>

<svelte:head>
	<title>Scheduled transactions — GnuCash Web Companion</title>
</svelte:head>

<main class="mx-auto max-w-6xl px-4 py-8">
	<div class="mb-6 space-y-3">
		<p class="text-sm font-medium uppercase tracking-wide" style="color: var(--app-accent);">Read-only scheduled transaction awareness</p>
		<div class="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
			<div>
				<h1 class="text-3xl font-bold" style="color: var(--app-text);">Scheduled transactions</h1>
				<p class="mt-2 max-w-3xl text-sm" style="color: var(--app-muted);">
					Safe summary metadata from the active GnuCash book. This pre-alpha page does not create, edit, delete,
					or calculate upcoming schedule predictions for scheduled transactions. Use GnuCash Desktop as the authoritative editor.
				</p>
			</div>
			{#if data.activeBook}
				<div class="rounded-2xl border px-4 py-3 text-sm" style="border-color: var(--app-border); background-color: var(--app-card-bg);">
					<p class="font-semibold" style="color: var(--app-text);">Active book</p>
					<p class="mt-1" style="color: var(--app-muted);">{data.activeBook.name}</p>
				</div>
			{/if}
		</div>
	</div>

	<section class="rounded-2xl border p-4 shadow-sm" style="border-color: var(--app-border); background-color: var(--app-card-bg);">
		<div class="mb-4 flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
			<div>
				<h2 class="text-lg font-semibold" style="color: var(--app-text);">Recurring metadata</h2>
				<p class="text-sm" style="color: var(--app-muted);">
					Only safe schedule fields are shown. Template split details and private raw SQL are not exposed.
					Filters and sorting are URL-only display controls; they do not save scheduled metadata in browser storage.
				</p>
			</div>
			<span class="inline-flex w-fit rounded-full border px-3 py-1 text-xs font-semibold" style="border-color: var(--app-border); color: var(--app-muted);">
				Read-only · no scheduling editor
			</span>
		</div>

		<div class="mb-4 grid gap-3 rounded-xl border p-3 text-sm md:grid-cols-3" style="border-color: var(--app-border); background-color: var(--app-bg);">
			<div>
				<p class="font-semibold" style="color: var(--app-text);">Status filter</p>
				<div class="mt-2 flex flex-wrap gap-2">
					<a class={`rounded-lg border px-3 py-2 ${activeClass(data.filters.status === 'all')}`} style={activeStyle(data.filters.status === 'all')} href={data.filters.links.all}>All ({data.scheduledSummary.total})</a>
					<a class={`rounded-lg border px-3 py-2 ${activeClass(data.filters.status === 'enabled')}`} style={activeStyle(data.filters.status === 'enabled')} href={data.filters.links.enabled}>Enabled ({data.scheduledSummary.enabled})</a>
					<a class={`rounded-lg border px-3 py-2 ${activeClass(data.filters.status === 'disabled')}`} style={activeStyle(data.filters.status === 'disabled')} href={data.filters.links.disabled}>Disabled ({data.scheduledSummary.disabled})</a>
				</div>
			</div>
			<div>
				<p class="font-semibold" style="color: var(--app-text);">Template metadata filter</p>
				<div class="mt-2 flex flex-wrap gap-2">
					<a class={`rounded-lg border px-3 py-2 ${activeClass(data.filters.template === 'all')}`} style={activeStyle(data.filters.template === 'all')} href={data.filters.links.allTemplates}>All ({data.scheduledSummary.total})</a>
					<a class={`rounded-lg border px-3 py-2 ${activeClass(data.filters.template === 'with_template')}`} style={activeStyle(data.filters.template === 'with_template')} href={data.filters.links.withTemplate}>Template present ({data.scheduledSummary.withTemplate})</a>
					<a class={`rounded-lg border px-3 py-2 ${activeClass(data.filters.template === 'without_template')}`} style={activeStyle(data.filters.template === 'without_template')} href={data.filters.links.withoutTemplate}>No template reference ({data.scheduledSummary.withoutTemplate})</a>
				</div>
			</div>
			<div>
				<p class="font-semibold" style="color: var(--app-text);">Sort display</p>
				<div class="mt-2 flex flex-wrap gap-2">
					<a class={`rounded-lg border px-3 py-2 ${activeClass(data.filters.sort === 'start_date')}`} style={activeStyle(data.filters.sort === 'start_date')} href={data.filters.links.startDate}>Start date</a>
					<a class={`rounded-lg border px-3 py-2 ${activeClass(data.filters.sort === 'name')}`} style={activeStyle(data.filters.sort === 'name')} href={data.filters.links.name}>Name</a>
					<a class={`rounded-lg border px-3 py-2 ${activeClass(data.filters.sort === 'enabled_first')}`} style={activeStyle(data.filters.sort === 'enabled_first')} href={data.filters.links.enabledFirst}>Enabled first</a>
				</div>
			</div>
			<p class="md:col-span-3" style="color: var(--app-muted);">
				Showing {data.scheduledSummary.shown} of {data.scheduledSummary.total} safe scheduled metadata rows. No template split amounts, accounts, memos, transaction descriptions, or raw SQL are exposed.
				{#if data.filters.status !== 'all' || data.filters.template !== 'all' || data.filters.sort !== 'start_date'}
					<a class="ml-2 font-semibold" style="color: var(--app-accent);" href={data.filters.links.clear}>Clear scheduled filters</a>
				{/if}
			</p>
		</div>

		{#if data.scheduledTransactions.length}
			<div class="grid gap-3">
				{#each data.scheduledTransactions as scheduled (scheduled.id)}
					<article class="rounded-xl border p-4" style="border-color: var(--app-border); background-color: var(--app-bg);">
						<div class="flex flex-col gap-2 md:flex-row md:items-start md:justify-between">
							<div>
								<h3 class="text-lg font-semibold" style="color: var(--app-text);">{scheduled.name || 'Unnamed scheduled transaction'}</h3>
								<div class="mt-2 flex flex-wrap gap-2">
									<span class="rounded-full px-2 py-1 text-xs font-semibold" style="background-color: var(--app-accent-soft); color: var(--app-accent);">{scheduled.enabled ? 'Enabled' : 'Disabled'}</span>
									<span class="rounded-full px-2 py-1 text-xs font-semibold" style="background-color: var(--app-hover-bg); color: var(--app-muted);">Template account: {formatBoolean(scheduled.has_template_account)}</span>
								</div>
							</div>
						</div>

						<dl class="mt-4 grid gap-3 text-sm sm:grid-cols-3">
							<div>
								<dt class="font-medium" style="color: var(--app-muted);">Start date</dt>
								<dd class="mt-1" style="color: var(--app-text);">{formatDate(scheduled.start_date)}</dd>
							</div>
							<div>
								<dt class="font-medium" style="color: var(--app-muted);">End date</dt>
								<dd class="mt-1" style="color: var(--app-text);">{formatDate(scheduled.end_date)}</dd>
							</div>
							<div>
								<dt class="font-medium" style="color: var(--app-muted);">Last occurred</dt>
								<dd class="mt-1" style="color: var(--app-text);">{formatDate(scheduled.last_occurred)}</dd>
							</div>
							<div>
								<dt class="font-medium" style="color: var(--app-muted);">Occurrences</dt>
								<dd class="mt-1" style="color: var(--app-text);">total {formatNumber(scheduled.num_occurrences)} · remaining {formatNumber(scheduled.remaining_occurrences)}</dd>
							</div>
							<div>
								<dt class="font-medium" style="color: var(--app-muted);">Auto-create / notify</dt>
								<dd class="mt-1" style="color: var(--app-text);">{formatBoolean(scheduled.auto_create)} / {formatBoolean(scheduled.auto_notify)}</dd>
							</div>
							<div>
								<dt class="font-medium" style="color: var(--app-muted);">Advance days</dt>
								<dd class="mt-1" style="color: var(--app-text);">create {formatNumber(scheduled.advance_create_days)} · notify {formatNumber(scheduled.advance_notify_days)}</dd>
							</div>
						</dl>

						<div class="mt-4 rounded-xl border p-3 text-sm" style="border-color: var(--app-border); background-color: var(--app-card-bg);">
							<p class="font-medium" style="color: var(--app-text);">Recurrence metadata</p>
							{#if scheduled.recurrence.length}
								<ul class="mt-2 list-disc space-y-1 pl-5" style="color: var(--app-muted);">
									{#each scheduled.recurrence as recurrence}
										<li>{recurrenceSummary(recurrence)}</li>
									{/each}
								</ul>
							{:else}
								<p class="mt-2" style="color: var(--app-muted);">No safe recurrence metadata is available through the adapter.</p>
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
				title="No scheduled transactions match these display filters"
				message="The active book has scheduled metadata, but the current URL-only scheduled filters hide every row. Clear filters to return to the full safe read-only metadata view."
				ariaLabel="No scheduled transactions match display filters"
				icon="🗓️"
			>
				<a
					href={data.filters.links.clear}
					class="rounded-xl px-4 py-2 text-sm font-semibold text-white"
					style="background-color: var(--app-accent);"
				>
					Clear scheduled filters
				</a>
				<a
					href="/books"
					class="rounded-xl border px-4 py-2 text-sm font-semibold"
					style="border-color: var(--app-border); color: var(--app-text);"
				>
					Review books
				</a>
			</EmptyState>
		{:else}
			<EmptyState
				title="No scheduled transactions found"
				message="No scheduled transactions are available through the safe read-only adapter for this book. If the book uses scheduled transactions, manage and review them in GnuCash Desktop."
				ariaLabel="No scheduled transactions found"
				icon="🗓️"
			>
				<a
					href="/transactions"
					class="rounded-xl px-4 py-2 text-sm font-semibold text-white"
					style="background-color: var(--app-accent);"
				>
					Browse transactions
				</a>
				<a
					href="/books"
					class="rounded-xl border px-4 py-2 text-sm font-semibold"
					style="border-color: var(--app-border); color: var(--app-text);"
				>
					Review books
				</a>
			</EmptyState>
		{/if}
	</section>
</main>
