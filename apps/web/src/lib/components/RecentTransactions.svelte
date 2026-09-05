<script lang="ts">
	import Money from '$lib/components/Money.svelte';
	import TransactionDirection from '$lib/components/TransactionDirection.svelte';
	import { DEFAULT_LOCALE, t, type Locale } from '$lib/i18n';

	type Transaction = import('$lib/api/types').RecentTransaction;
	type DashboardTransactionKind = 'ordinary' | 'composite' | 'ambiguous';

	let { transactions, loading = false, drilldownHref = '/transactions', locale = DEFAULT_LOCALE }: { transactions: Transaction[]; loading?: boolean; drilldownHref?: string; locale?: Locale } = $props();

	function ordinaryTwoSplit(tx: Transaction): boolean {
		const direction = tx.direction;
		return Boolean(
			direction?.status === 'resolved' &&
				direction.from_accounts.length === 1 &&
				direction.to_accounts.length === 1 &&
				direction.from_accounts[0].split_count === 1 &&
				direction.to_accounts[0].split_count === 1
		);
	}

	function transactionKind(tx: Transaction): DashboardTransactionKind {
		if (ordinaryTwoSplit(tx)) return 'ordinary';
		return tx.direction?.status === 'composite' ? 'composite' : 'ambiguous';
	}

	function entryLabel(entry: { account_id: string; display_name: string; full_name: string }): string {
		return entry.display_name || entry.full_name || entry.account_id;
	}

	function friendlyDirection(tx: Transaction): string {
		const direction = tx.direction;
		if (!direction) return t(locale, 'transactions.direction.ambiguous');
		return t(locale, 'dashboard.transactionFromTo', {
			from: entryLabel(direction.from_accounts[0]),
			to: entryLabel(direction.to_accounts[0])
		});
	}
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
				{@const kind = transactionKind(tx)}
				{@const representative = tx.amount_is_unambiguous ? { amount: tx.amount.replace(/^[+-]/, ''), currency: tx.currency } : null}
				<li
					data-dashboard-recent-kind={kind}
					class="flex min-w-0 flex-col gap-2 py-3 sm:flex-row sm:items-start sm:justify-between"
					style="border-color: var(--app-border);"
				>
					<div class="min-w-0 flex-1">
						<p class="truncate text-sm font-medium" style="color: var(--app-text);" title={tx.description || t(locale, 'transactionDetail.noDescription')}>{tx.description || t(locale, 'transactionDetail.noDescription')}</p>
						<time data-dashboard-date class="whitespace-nowrap text-xs" style="color: var(--app-muted);" datetime={tx.date}>{tx.date}</time>
						<div class="mt-2 min-w-0">
							{#if kind === 'ordinary'}
								<p class="truncate text-xs" style="color: var(--app-muted);" title={friendlyDirection(tx)}>{friendlyDirection(tx)}</p>
							{:else}
								<TransactionDirection direction={tx.direction ?? null} {locale} compact />
							{/if}
						</div>
					</div>
					{#if representative}
						<span class="shrink-0 text-sm font-semibold tabular-nums"><Money amount={representative.amount} currency={representative.currency} /></span>
					{:else if tx.direction}
						<span class="shrink-0 text-xs" style="color: var(--app-muted);">{t(locale, 'dashboard.amountNotShown')}</span>
					{/if}
				</li>
			{/each}
		</ul>
	{/if}
</section>
