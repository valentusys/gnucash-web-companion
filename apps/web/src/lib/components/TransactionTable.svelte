<script lang="ts">
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

<div class="hidden overflow-x-hidden md:block">
	<table class="w-full table-fixed text-left text-sm">
		<thead>
			<tr class="border-b text-xs font-semibold uppercase" style="border-color: var(--app-border); color: var(--app-muted);">
				<th class="w-28 px-4 py-3">{t(locale, 'transactionDetail.date')}</th>
				<th class="w-[30%] px-4 py-3">{t(locale, 'transactionCreate.descriptionLabel')}</th>
				<th class="w-[40%] px-4 py-3">{t(locale, 'transactions.explorer.direction')}</th>
				<th class="w-40 px-4 py-3 text-right">{t(locale, 'transactions.filters.summary.amount')}</th>
			</tr>
		</thead>
		<tbody>
			{#each transactions as tx (tx.id)}
				{@const representative = tx.direction?.status === 'resolved' ? (tx.representative_amount ?? tx.matched_amount ?? null) : null}
				<tr
					class="cursor-pointer border-b hover:opacity-80"
					style="border-color: var(--app-border);"
					onclick={() => onSelect(tx.id)}
					onkeydown={(e) => { if (e.key === 'Enter') onSelect(tx.id); }}
					role="button"
					tabindex="0"
				>
					<td class="w-28 px-4 py-3 whitespace-nowrap" style="color: var(--app-muted);">{tx.date}</td>
					<td class="w-[30%] px-4 py-3" style="color: var(--app-text);">
						<div class="min-w-0">
							{#if detailHref}
								<a class="block truncate font-medium hover:underline" style="color: var(--app-accent);" href={detailHref(tx.id)} title={tx.description || t(locale, 'transactionDetail.noDescription')}>{tx.description || t(locale, 'transactionDetail.noDescription')}</a>
							{:else}
								<div class="truncate font-medium" title={tx.description || t(locale, 'transactionDetail.noDescription')}>{tx.description || t(locale, 'transactionDetail.noDescription')}</div>
							{/if}
							{#if tx.is_write_alpha_owned}
								<span class="mt-1 inline-flex max-w-full items-center rounded-full px-2 py-0.5 text-xs font-semibold" style="background: #fffbeb; color: #92400e; border: 1px solid #fcd34d;" title={t(locale, 'transactions.writeAlphaHistoryTitle')}>
									{t(locale, 'transactions.writeAlphaHistoryBadge')}
								</span>
							{/if}
						</div>
					</td>
					<td class="w-[40%] px-4 py-3" style="color: var(--app-muted);">
						<TransactionDirection direction={tx.direction ?? null} {locale} compact />
					</td>
					<td class="w-40 px-4 py-3 text-right">
						{#if representative}
							<Money amount={representative.amount} currency={representative.currency} />
						{:else if tx.direction}
							<span class="text-xs" style="color: var(--app-muted);">{t(locale, 'transactions.direction.amountHidden')}</span>
						{:else}
							<Money amount={tx.amount} currency={tx.currency} />
						{/if}
					</td>
				</tr>
			{:else}
				<tr>
					<td colspan="4" class="px-4 py-10 text-center">
						<p class="font-medium" style="color: var(--app-text);">{t(locale, 'transactions.explorer.trueEmptyTitle')}</p>
						<p class="mt-1 text-sm" style="color: var(--app-muted);">{t(locale, 'transactions.explorer.trueEmptyMessage')}</p>
					</td>
				</tr>
			{/each}
		</tbody>
	</table>
</div>
