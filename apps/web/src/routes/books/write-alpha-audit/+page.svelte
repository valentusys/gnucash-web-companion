<script lang="ts">
	import EmptyState from '$lib/components/EmptyState.svelte';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();
	const appliedFilters = $derived(data.auditSummary?.filters ?? {});

	const actionOptions = [
		{ value: '', label: 'All actions' },
		{ value: 'transaction.create', label: 'Create' },
		{ value: 'transaction.patch', label: 'PATCH' },
		{ value: 'transaction.delete', label: 'DELETE' }
	];
	const resultOptions = [
		{ value: '', label: 'All results' },
		{ value: 'success', label: 'Success' },
		{ value: 'failed', label: 'Failed' },
		{ value: 'started', label: 'Started' },
		{ value: 'unknown', label: 'Unknown' }
	];
</script>

<svelte:head>
	<title>Write-alpha audit evidence</title>
</svelte:head>

<section class="min-w-0 space-y-6 overflow-x-hidden">
	<div class="rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-950 shadow-sm">
		<p class="font-semibold">Write-alpha audit evidence for disposable runs</p>
		<p class="mt-2">
			Read-only app metadata summary for the active book. This operator view is for synthetic/disposable
			write-alpha runs only; it is not a production audit log product.
		</p>
		<p class="mt-2">
			Raw request payloads, backup paths, private file paths, account names, memos, and amounts are not shown.
		</p>
	</div>

	<div class="flex min-w-0 flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
		<div class="min-w-0">
			<p class="text-xs uppercase tracking-wide text-slate-500">Active book</p>
			<h1 class="truncate text-2xl font-semibold text-slate-900">{data.activeBook?.name ?? 'No accessible book'}</h1>
		</div>
		<a class="inline-flex min-h-11 items-center justify-center rounded-full border border-slate-300 px-4 text-sm font-medium text-slate-700" href="/books">
			Review books
		</a>
	</div>

	<form method="GET" class="grid min-w-0 gap-3 rounded-2xl border border-slate-200 bg-white p-4 text-sm shadow-sm md:grid-cols-4" aria-label="Audit summary filters">
		<label class="min-w-0 space-y-1">
			<span class="font-medium text-slate-700">Action</span>
			<select name="action" class="min-h-11 w-full min-w-0 rounded-xl border border-slate-300 bg-white px-3" autocomplete="off">
				{#each actionOptions as option}
					<option value={option.value} selected={appliedFilters.action === option.value || (!appliedFilters.action && option.value === '')}>{option.label}</option>
				{/each}
			</select>
		</label>
		<label class="min-w-0 space-y-1">
			<span class="font-medium text-slate-700">Result</span>
			<select name="result" class="min-h-11 w-full min-w-0 rounded-xl border border-slate-300 bg-white px-3" autocomplete="off">
				{#each resultOptions as option}
					<option value={option.value} selected={appliedFilters.result === option.value || (!appliedFilters.result && option.value === '')}>{option.label}</option>
				{/each}
			</select>
		</label>
		<label class="min-w-0 space-y-1">
			<span class="font-medium text-slate-700">Since ISO</span>
			<input name="since" value={appliedFilters.since ?? ''} class="min-h-11 w-full min-w-0 rounded-xl border border-slate-300 px-3" placeholder="2026-05-20T10:00:00Z" autocomplete="off" />
		</label>
		<label class="min-w-0 space-y-1">
			<span class="font-medium text-slate-700">Until ISO</span>
			<input name="until" value={appliedFilters.until ?? ''} class="min-h-11 w-full min-w-0 rounded-xl border border-slate-300 px-3" placeholder="2026-05-20T11:00:00Z" autocomplete="off" />
		</label>
		<div class="flex flex-col gap-2 md:col-span-4 sm:flex-row">
			<button type="submit" class="inline-flex min-h-11 items-center justify-center rounded-full bg-slate-900 px-4 font-medium text-white">Apply filters</button>
			<a href="/books/write-alpha-audit" class="inline-flex min-h-11 items-center justify-center rounded-full border border-slate-300 px-4 font-medium text-slate-700">Clear filters</a>
		</div>
	</form>

	{#if data.auditSummary}
		<div class="grid min-w-0 gap-3 text-sm sm:grid-cols-2 lg:grid-cols-4" aria-label="Audit summary counts">
			<div class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
				<p class="text-xs uppercase tracking-wide text-slate-500">Filtered rows</p>
				<p class="mt-1 text-2xl font-semibold text-slate-900">{data.auditSummary.total_count}</p>
				<p class="text-slate-600">Returned: {data.auditSummary.returned_count}</p>
			</div>
			<div class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
				<p class="text-xs uppercase tracking-wide text-slate-500">Actions</p>
				<p class="break-words text-slate-700">Create {data.auditSummary.counts_by_action['transaction.create'] ?? 0} · PATCH {data.auditSummary.counts_by_action['transaction.patch'] ?? 0} · DELETE {data.auditSummary.counts_by_action['transaction.delete'] ?? 0}</p>
			</div>
			<div class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
				<p class="text-xs uppercase tracking-wide text-slate-500">Results</p>
				<p class="break-words text-slate-700">Success {data.auditSummary.counts_by_result.success ?? 0} · Failed {data.auditSummary.counts_by_result.failed ?? 0}</p>
			</div>
			<div class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
				<p class="text-xs uppercase tracking-wide text-slate-500">Window</p>
				<p class="break-words text-slate-700">Requested: {data.auditSummary.time_window.requested_since ?? 'No start'} → {data.auditSummary.time_window.requested_until ?? 'No end'}</p>
				<p class="mt-1 break-words text-slate-600">Returned: {data.auditSummary.time_window.oldest_returned ?? 'none'} → {data.auditSummary.time_window.newest_returned ?? 'none'}</p>
			</div>
		</div>
	{/if}

	{#if !data.auditSummary || data.auditSummary.items.length === 0}
		<EmptyState
			title="No write-alpha audit rows"
			message="No create/PATCH/DELETE write-alpha app-metadata audit entries match the current filters for the active book. Run only explicit disposable APP_ENV=test write-alpha smokes before expecting evidence here."
		>
			<a class="inline-flex min-h-11 items-center justify-center rounded-full border border-slate-300 px-4 text-sm font-medium text-slate-700" href="/transactions">
				Browse transactions
			</a>
		</EmptyState>
	{:else}
		<div class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
			<div class="border-b border-slate-100 px-4 py-3 text-sm text-slate-600">
				<p>Showing {data.auditSummary.returned_count} of {data.auditSummary.total_count} redacted audit entries. Backup is represented only as present/missing.</p>
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
							<p class="text-xs uppercase tracking-wide text-slate-500">Action</p>
							<p class="truncate font-medium text-slate-900">{item.action}</p>
						</div>
						<div class="min-w-0">
							<p class="text-xs uppercase tracking-wide text-slate-500">Result</p>
							<p class="truncate font-medium text-slate-900">{item.result}</p>
						</div>
						<div class="min-w-0">
							<p class="text-xs uppercase tracking-wide text-slate-500">Timestamp</p>
							<p class="break-words text-slate-700">{item.timestamp}</p>
						</div>
						<div class="min-w-0">
							<p class="text-xs uppercase tracking-wide text-slate-500">Txn prefix</p>
							<p class="truncate font-mono text-slate-700">{item.transaction_id_prefix ?? 'not set'}</p>
						</div>
						<div class="min-w-0">
							<p class="text-xs uppercase tracking-wide text-slate-500">Backup / safe error</p>
							<p class="text-slate-700">Backup: {item.backup_present ? 'present' : 'not recorded'}</p>
							{#if item.error}
								<p class="mt-1 break-words text-slate-700">{item.error}</p>
							{/if}
						</div>
					</li>
				{/each}
			</ul>
		</div>
	{/if}

	{#if data.auditSummary?.limitations.length}
		<div class="rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700">
			<p class="font-semibold text-slate-900">Limitations</p>
			<ul class="mt-2 list-disc space-y-1 pl-5">
				{#each data.auditSummary.limitations as limitation}
					<li>{limitation}</li>
				{/each}
			</ul>
		</div>
	{/if}
</section>
