<script lang="ts">
	import EmptyState from '$lib/components/EmptyState.svelte';
	import Money from '$lib/components/Money.svelte';
	import TransactionDirection from '$lib/components/TransactionDirection.svelte';
	import type { TransactionListItem } from '$lib/api/types';
	import { DEFAULT_LOCALE, t, type Locale } from '$lib/i18n';

	let {
		transactions,
		onSelect,
		detailHref,
		locale = DEFAULT_LOCALE
	}: {
		transactions: TransactionListItem[];
		onSelect: (id: string) => void;
		detailHref?: (id: string) => string;
		locale?: Locale;
	} = $props();
</script>

<div class="space-y-3 md:hidden">
	{#each transactions as tx (tx.id)}
		{@const representative = tx.direction?.status === 'resolved' ? (tx.representative_amount ?? tx.matched_amount ?? null) : null}
		<div
			class="cursor-pointer rounded-xl p-4"
			style="background-color: var(--app-panel); box-shadow: 0 1px 3px var(--app-panel-shadow); border: 1px solid var(--app-border);"
			onclick={() => onSelect(tx.id)}
			onkeydown={(e) => { if (e.key === 'Enter') onSelect(tx.id); }}
			role="button"
			tabindex="0"
		>
			<div class="flex items-start justify-between gap-3">
				<div class="min-w-0">
					{#if detailHref}
						<a class="block truncate text-sm font-medium hover:underline" style="color: var(--app-accent);" href={detailHref(tx.id)}>{tx.description || t(locale, 'transactionDetail.noDescription')}</a>
					{:else}
						<p class="truncate text-sm font-medium" style="color: var(--app-text);">{tx.description || t(locale, 'transactionDetail.noDescription')}</p>
					{/if}
					<p class="mt-1 text-xs" style="color: var(--app-muted);">{tx.date}</p>
					{#if tx.is_write_alpha_owned}
						<span class="mt-2 inline-flex max-w-full items-center rounded-full px-2 py-0.5 text-xs font-semibold" style="background: #fffbeb; color: #92400e; border: 1px solid #fcd34d;" title={t(locale, 'transactions.writeAlphaHistoryTitle')}>
							{t(locale, 'transactions.writeAlphaHistoryBadge')}
						</span>
					{/if}
				</div>
				<div class="shrink-0 text-right">
					{#if representative}
						<p class="text-sm font-semibold"><Money amount={representative.amount} currency={representative.currency} /></p>
					{:else if tx.direction}
						<p class="max-w-32 text-xs" style="color: var(--app-muted);">{t(locale, 'transactions.direction.amountHidden')}</p>
					{:else}
						<p class="text-sm font-semibold"><Money amount={tx.amount} currency={tx.currency} /></p>
					{/if}
				</div>
			</div>
			<div class="mt-2 min-w-0">
				<TransactionDirection direction={tx.direction ?? null} {locale} compact />
			</div>
		</div>
	{:else}
		<EmptyState
			title={t(locale, 'transactions.explorer.trueEmptyTitle')}
			message={t(locale, 'transactions.explorer.trueEmptyMessage')}
		/>
	{/each}
</div>
