<script lang="ts">
	import Money from '$lib/components/Money.svelte';
	import type { TransactionSplit } from '$lib/api/types';
	import { DEFAULT_LOCALE, t, type Locale } from '$lib/i18n';

	let { splits, locale = DEFAULT_LOCALE }: { splits: TransactionSplit[]; locale?: Locale } = $props();

	const reconcileLabelKeys: Record<string, Parameters<typeof t>[1]> = {
		n: 'transactions.filters.stateUnreconciled',
		c: 'transactions.filters.stateCleared',
		y: 'transactions.filters.stateReconciled',
		v: 'transactions.filters.stateVoided'
	};

	function reconcileLabel(state?: string) {
		const normalized = String(state ?? '').trim().toLowerCase();
		if (!normalized) return t(locale, 'transactionSplits.stateNotProvided');
		const labelKey = reconcileLabelKeys[normalized];
		return labelKey ? t(locale, labelKey) : t(locale, 'transactionSplits.stateUnknown').replace('{state}', normalized);
	}

	function shortAccountId(accountId: string) {
		return accountId ? accountId.slice(0, 8) : '—';
	}
</script>

<section
	class="mt-6 min-w-0 rounded-xl p-4"
	aria-labelledby="transaction-splits-heading"
	style="background-color: var(--app-elevated-bg);"
>
	<div class="flex min-w-0 flex-col gap-1 md:flex-row md:items-start md:justify-between">
		<div class="min-w-0">
			<h2 id="transaction-splits-heading" class="text-sm font-semibold" style="color: var(--app-text);">{t(locale, 'transactionSplits.title')}</h2>
			<p class="mt-1 text-xs" style="color: var(--app-muted);">
				{t(locale, 'transactionSplits.helper')}
			</p>
		</div>
		<p class="shrink-0 text-xs font-medium" style="color: var(--app-muted);">
			{splits.length} {splits.length === 1 ? t(locale, 'transactionDetail.splitSingular') : t(locale, 'transactionDetail.splitPlural')}
		</p>
	</div>

	{#if splits.length === 0}
		<div class="mt-4 rounded-lg border p-4 text-sm" role="status" style="border-color: var(--app-border); color: var(--app-muted); background-color: var(--app-panel);">
			{t(locale, 'transactionSplits.empty')}
		</div>
	{:else}
		<div class="mt-3 space-y-3 md:hidden">
			{#each splits as split, index}
				<article class="min-w-0 rounded-lg border p-3" style="border-color: var(--app-border); background-color: var(--app-panel);">
					<div class="flex min-w-0 items-start justify-between gap-3">
						<div class="min-w-0">
							<div class="text-xs font-semibold uppercase" style="color: var(--app-muted);">{t(locale, 'transactionSplits.splitAccount').replace('{index}', String(index + 1))}</div>
							<div class="break-words text-sm font-medium" style="color: var(--app-text);" title={split.account_name}>{split.account_name}</div>
						</div>
						<div class="shrink-0 text-right text-sm font-semibold">
							<Money amount={split.amount} currency={split.currency} />
						</div>
					</div>
					<dl class="mt-3 grid min-w-0 grid-cols-1 gap-2 text-sm">
						<div class="min-w-0">
							<dt class="text-xs font-semibold uppercase" style="color: var(--app-muted);">{t(locale, 'transactionSplits.memo')}</dt>
							<dd class="break-words" style="color: var(--app-muted);">{split.memo || t(locale, 'transactionSplits.noMemo')}</dd>
						</div>
						<div class="grid min-w-0 grid-cols-2 gap-2">
							<div class="min-w-0">
								<dt class="text-xs font-semibold uppercase" style="color: var(--app-muted);">{t(locale, 'transactionSplits.reconciliation')}</dt>
								<dd class="truncate" style="color: var(--app-text);" title={reconcileLabel(split.reconcile_state)}>{reconcileLabel(split.reconcile_state)}</dd>
							</div>
							<div class="min-w-0">
								<dt class="text-xs font-semibold uppercase" style="color: var(--app-muted);">{t(locale, 'transactionSplits.accountId')}</dt>
								<dd class="truncate font-mono text-xs" style="color: var(--app-muted);" title={split.account_id}>{shortAccountId(split.account_id)}</dd>
							</div>
						</div>
					</dl>
				</article>
			{/each}
		</div>

		<div class="mt-3 hidden overflow-x-hidden md:block">
			<table class="w-full table-fixed text-left text-sm">
				<caption class="sr-only">{t(locale, 'transactionSplits.caption')}</caption>
				<thead>
					<tr class="border-b text-xs font-semibold uppercase" style="border-color: var(--app-border); color: var(--app-muted);">
						<th class="w-[32%] px-3 py-2">{t(locale, 'transactions.filters.account')}</th>
						<th class="w-[28%] px-3 py-2">{t(locale, 'transactionSplits.memo')}</th>
						<th class="w-[18%] px-3 py-2">{t(locale, 'transactionSplits.reconciliation')}</th>
						<th class="w-[22%] px-3 py-2 text-right">{t(locale, 'transactions.filters.summary.amount')}</th>
					</tr>
				</thead>
				<tbody>
					{#each splits as split}
						<tr class="border-b last:border-0" style="border-color: var(--app-border);">
							<td class="min-w-0 px-3 py-3" style="color: var(--app-text);">
								<div class="truncate font-medium" title={split.account_name}>{split.account_name}</div>
								<div class="truncate font-mono text-xs" style="color: var(--app-muted);" title={split.account_id}>{t(locale, 'transactionDetail.id')} {shortAccountId(split.account_id)}</div>
							</td>
							<td class="truncate px-3 py-3" style="color: var(--app-muted);" title={split.memo || t(locale, 'transactionSplits.noMemo')}>{split.memo || t(locale, 'transactionSplits.noMemo')}</td>
							<td class="truncate px-3 py-3" style="color: var(--app-text);" title={reconcileLabel(split.reconcile_state)}>{reconcileLabel(split.reconcile_state)}</td>
							<td class="px-3 py-3 text-right">
								<Money amount={split.amount} currency={split.currency} />
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	{/if}
</section>
