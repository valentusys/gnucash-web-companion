<script lang="ts">
	import { isNonNegativeDecimalString } from '$lib/money.js';
	import { DEFAULT_LOCALE, t, type Locale } from '$lib/i18n';

	type Transaction = import('$lib/api/types').TransactionListItem;

	let { transactions, loading = false, drilldownHref = '/transactions?limit=50&offset=0', locale = DEFAULT_LOCALE }: { transactions: Transaction[]; loading?: boolean; drilldownHref?: string; locale?: Locale } = $props();
</script>

<section class="rounded-xl p-5" style="background-color: var(--app-panel); box-shadow: 0 1px 3px var(--app-panel-shadow); border: 1px solid var(--app-border);">
	<div class="flex items-start justify-between gap-3">
		<div>
			<h2 class="text-lg font-semibold" style="color: var(--app-text);">{t(locale, 'dashboard.recentTransactions')}</h2>
			<p class="mt-1 text-xs" style="color: var(--app-muted);">{t(locale, 'dashboard.recentTransactionsHelp')}</p>
		</div>
		<a class="text-sm font-semibold" style="color: var(--app-accent);" href={drilldownHref}>{t(locale, 'dashboard.viewTransactions')}</a>
	</div>

	{#if loading}
		<div class="mt-4 space-y-3">
			{#each Array(5) as _}
				<div class="animate-pulse flex items-center justify-between">
					<div class="space-y-2">
						<div class="h-4 w-40 rounded" style="background-color: var(--app-border);"></div>
						<div class="h-3 w-24 rounded" style="background-color: var(--app-elevated-bg);"></div>
					</div>
					<div class="h-4 w-20 rounded" style="background-color: var(--app-border);"></div>
				</div>
			{/each}
		</div>
	{:else if transactions.length === 0}
		<p class="mt-4 text-sm" style="color: var(--app-muted);">{t(locale, 'dashboard.noRecentTransactions')}</p>
	{:else}
		<ul class="mt-4 divide-y" style="border-color: var(--app-border);">
			{#each transactions as tx (tx.id)}
				<li class="flex items-center justify-between py-3" style="border-color: var(--app-border);">
					<div class="min-w-0">
						<p class="truncate text-sm font-medium" style="color: var(--app-text);">{tx.description || '—'}</p>
						<p class="text-xs" style="color: var(--app-muted);">{tx.date} · {tx.account_name}</p>
					</div>
					<span
						class="ml-4 whitespace-nowrap text-sm font-semibold tabular-nums"
						style="color: {isNonNegativeDecimalString(tx.amount) ? 'var(--app-success)' : 'var(--app-danger)'};"
					>
						{tx.amount}
						<span class="ml-0.5 text-xs font-normal" style="color: var(--app-muted);">{tx.currency}</span>
					</span>
				</li>
			{/each}
		</ul>
	{/if}
</section>
