<script lang="ts">
	import type { TransactionDirection, TransactionDirectionEntry } from '$lib/api/types';
	import { DEFAULT_LOCALE, t, type Locale } from '$lib/i18n';

	let {
		direction = null,
		locale = DEFAULT_LOCALE,
		compact = false,
		maxEntries = 3
	}: {
		direction?: TransactionDirection | null;
		locale?: Locale;
		compact?: boolean;
		maxEntries?: number;
	} = $props();

	const fromEntries = $derived(direction?.from_accounts ?? []);
	const toEntries = $derived(direction?.to_accounts ?? []);
	const canShowSides = $derived(Boolean(direction && direction.status !== 'ambiguous' && (fromEntries.length || toEntries.length)));
	const hiddenFromCount = $derived(Math.max(0, fromEntries.length - maxEntries));
	const hiddenToCount = $derived(Math.max(0, toEntries.length - maxEntries));

	function entryLabel(entry: TransactionDirectionEntry): string {
		return entry.display_name || entry.full_name || entry.account_id;
	}

	function entryTitle(entry: TransactionDirectionEntry): string {
		const full = entry.full_name || entry.display_name || entry.account_id;
		const splits = entry.split_count > 1 ? ` · ${entry.split_count} ${t(locale, 'transactionDetail.splitPlural')}` : '';
		return `${full} · ${entry.value} ${direction?.currency ?? ''}${splits}`.trim();
	}
</script>

{#if !direction || direction.status === 'ambiguous'}
	<p class="break-words text-xs" style="color: var(--app-muted);" data-transaction-direction-status="ambiguous">
		{t(locale, 'transactions.direction.ambiguous')}
	</p>
{:else if canShowSides}
	<div class={compact ? 'space-y-1 text-xs' : 'space-y-2 text-sm'} data-transaction-direction-status={direction.status}>
		<div class="grid min-w-0 gap-1 sm:grid-cols-[auto_minmax(0,1fr)] sm:items-start">
			<span class="font-semibold" style="color: var(--app-muted);">{t(locale, 'transactions.direction.from')}</span>
			<div class="flex min-w-0 flex-wrap gap-1">
				{#each fromEntries.slice(0, maxEntries) as entry (`from-${entry.account_id}-${entry.value}`)}
					<span class="inline-flex max-w-full min-w-0 items-center gap-1 rounded-lg border px-2 py-0.5" style="border-color: var(--app-border); background: var(--app-elevated-bg);" title={entryTitle(entry)}>
						<span class="truncate">{entryLabel(entry)}</span>
						<span class="shrink-0 tabular-nums" style="color: var(--app-muted);">{entry.value} {direction.currency}</span>
					</span>
				{/each}
				{#if hiddenFromCount > 0}
					<span class="inline-flex rounded-lg border px-2 py-0.5" style="border-color: var(--app-border); color: var(--app-muted);">{t(locale, 'transactions.direction.more').replace('{count}', String(hiddenFromCount))}</span>
				{/if}
			</div>
		</div>
		<div class="grid min-w-0 gap-1 sm:grid-cols-[auto_minmax(0,1fr)] sm:items-start">
			<span class="font-semibold" style="color: var(--app-muted);">{t(locale, 'transactions.direction.to')}</span>
			<div class="flex min-w-0 flex-wrap gap-1">
				{#each toEntries.slice(0, maxEntries) as entry (`to-${entry.account_id}-${entry.value}`)}
					<span class="inline-flex max-w-full min-w-0 items-center gap-1 rounded-lg border px-2 py-0.5" style="border-color: var(--app-border); background: var(--app-elevated-bg);" title={entryTitle(entry)}>
						<span class="truncate">{entryLabel(entry)}</span>
						<span class="shrink-0 tabular-nums" style="color: var(--app-muted);">{entry.value} {direction.currency}</span>
					</span>
				{/each}
				{#if hiddenToCount > 0}
					<span class="inline-flex rounded-lg border px-2 py-0.5" style="border-color: var(--app-border); color: var(--app-muted);">{t(locale, 'transactions.direction.more').replace('{count}', String(hiddenToCount))}</span>
				{/if}
			</div>
		</div>
		{#if direction.status === 'composite'}
			<p class="text-xs" style="color: var(--app-muted);">{t(locale, 'transactions.direction.composite')}</p>
		{/if}
	</div>
{:else}
	<p class="break-words text-xs" style="color: var(--app-muted);" data-transaction-direction-status="ambiguous">
		{t(locale, 'transactions.direction.ambiguous')}
	</p>
{/if}
