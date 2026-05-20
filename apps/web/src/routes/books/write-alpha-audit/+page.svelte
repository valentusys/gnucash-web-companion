<script lang="ts">
	import EmptyState from '$lib/components/EmptyState.svelte';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();
</script>

<svelte:head>
	<title>Write-alpha audit evidence</title>
</svelte:head>

<section class="space-y-6">
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

	<div class="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
		<div>
			<p class="text-xs uppercase tracking-wide text-slate-500">Active book</p>
			<h1 class="text-2xl font-semibold text-slate-900">{data.activeBook?.name ?? 'No accessible book'}</h1>
		</div>
		<a class="inline-flex min-h-11 items-center rounded-full border border-slate-300 px-4 text-sm font-medium text-slate-700" href="/books">
			Review books
		</a>
	</div>

	{#if !data.auditSummary || data.auditSummary.items.length === 0}
		<EmptyState
			title="No write-alpha audit rows"
			message="No create/PATCH/DELETE write-alpha app-metadata audit entries are available for the active book. Run only explicit disposable APP_ENV=test write-alpha smokes before expecting evidence here."
		>
			<a class="inline-flex min-h-11 items-center rounded-full border border-slate-300 px-4 text-sm font-medium text-slate-700" href="/transactions">
				Browse transactions
			</a>
		</EmptyState>
	{:else}
		<div class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
			<div class="border-b border-slate-100 px-4 py-3 text-sm text-slate-600">
				Showing the latest {data.auditSummary.items.length} redacted audit entries. Backup is represented only as present/missing.
			</div>
			<ul class="divide-y divide-slate-100">
				{#each data.auditSummary.items as item}
					<li class="grid gap-3 p-4 text-sm md:grid-cols-[10rem_7rem_11rem_8rem_minmax(0,1fr)] md:items-center">
						<div>
							<p class="text-xs uppercase tracking-wide text-slate-500">Action</p>
							<p class="font-medium text-slate-900">{item.action}</p>
						</div>
						<div>
							<p class="text-xs uppercase tracking-wide text-slate-500">Result</p>
							<p class="font-medium text-slate-900">{item.result}</p>
						</div>
						<div>
							<p class="text-xs uppercase tracking-wide text-slate-500">Timestamp</p>
							<p class="break-words text-slate-700">{item.timestamp}</p>
						</div>
						<div>
							<p class="text-xs uppercase tracking-wide text-slate-500">Txn prefix</p>
							<p class="font-mono text-slate-700">{item.transaction_id_prefix ?? 'not set'}</p>
						</div>
						<div>
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
