<script lang="ts">
	import TransactionSplits from '$lib/components/TransactionSplits.svelte';
	import { DEFAULT_LOCALE, t, type Locale } from '$lib/i18n';

	let { data, form }: { data: any; form?: { error?: string } } = $props();
	let locale = $derived<Locale>(data.locale ?? DEFAULT_LOCALE);
	const tx = $derived(data.transaction);
	const splitCountLabel = $derived(`${tx.splits.length} ${tx.splits.length === 1 ? t(locale, 'transactionDetail.splitSingular') : t(locale, 'transactionDetail.splitPlural')}`);
</script>

<svelte:head>
	<title>Transaction {tx.id.slice(0, 8)} — GnuCash Web Companion</title>
</svelte:head>

<main class="mx-auto max-w-4xl px-4 py-8">
	<a href="/transactions" class="text-sm font-medium hover:underline" style="color: var(--app-accent);">
		← {t(locale, 'transactionDetail.back')}
	</a>

	<section
		class="mt-4 min-w-0 rounded-2xl p-4 sm:p-6"
		aria-labelledby="transaction-detail-heading"
		style="background-color: var(--app-panel); box-shadow: 0 1px 3px var(--app-panel-shadow); border: 1px solid var(--app-border);"
	>
		<div class="flex min-w-0 flex-col gap-4 md:flex-row md:items-start md:justify-between">
			<div class="min-w-0">
				<p class="text-sm font-medium uppercase tracking-wide" style="color: var(--app-accent);">{t(locale, 'transactionDetail.kicker')}</p>
				<h1 id="transaction-detail-heading" class="mt-1 break-words text-2xl font-bold" style="color: var(--app-text);">{tx.description || t(locale, 'transactionDetail.noDescription')}</h1>
				<p class="mt-2 max-w-2xl text-sm" style="color: var(--app-muted);">
					{t(locale, 'transactionDetail.helper')}
				</p>
			</div>
			<div class="grid min-w-0 grid-cols-2 gap-2 rounded-xl px-4 py-3 text-sm sm:grid-cols-4 md:max-w-md" style="background-color: var(--app-elevated-bg);">
				<div class="min-w-0">
					<p class="text-xs font-semibold uppercase tracking-wide" style="color: var(--app-muted);">{t(locale, 'transactionDetail.date')}</p>
					<p class="mt-1 truncate" style="color: var(--app-text);">{tx.date}</p>
				</div>
				<div class="min-w-0">
					<p class="text-xs font-semibold uppercase tracking-wide" style="color: var(--app-muted);">{t(locale, 'transactionDetail.currency')}</p>
					<p class="mt-1 truncate" style="color: var(--app-text);">{tx.currency}</p>
				</div>
				<div class="min-w-0">
					<p class="text-xs font-semibold uppercase tracking-wide" style="color: var(--app-muted);">{t(locale, 'transactionDetail.splits')}</p>
					<p class="mt-1 truncate" style="color: var(--app-text);">{splitCountLabel}</p>
				</div>
				<div class="min-w-0">
					<p class="text-xs font-semibold uppercase tracking-wide" style="color: var(--app-muted);">{t(locale, 'transactionDetail.id')}</p>
					<p class="mt-1 truncate font-mono text-xs" style="color: var(--app-text);" title={tx.id}>{tx.id.slice(0, 8)}</p>
				</div>
			</div>
		</div>

		<TransactionSplits splits={tx.splits} {locale} />

		{#if form?.error}
			<p class="mt-6 rounded-xl px-4 py-3 text-sm" role="alert" style="background: #fef2f2; color: #991b1b; border: 1px solid #fecaca;">
				{form.error}
			</p>
		{/if}

		{#if data.writesEnabled && data.activeBook}
			<form
				method="POST"
				action="?/delete"
				class="mt-6 rounded-2xl p-4"
				style="background: #fffbeb; border: 1px solid #fcd34d;"
				onsubmit={(event) => {
					if (!confirm(t(locale, 'transactionDetail.deleteConfirm'))) {
						event.preventDefault();
					}
				}}
			>
				<input type="hidden" name="book_id" value={data.activeBook.id} />
				<p class="text-sm font-semibold" style="color: #92400e;">{t(locale, 'transactionDetail.deleteTitle')}</p>
				<p class="mt-2 text-sm" style="color: #92400e;">
					{t(locale, 'transactionDetail.deleteHelper')}
				</p>
				<label class="mt-3 flex gap-2 text-sm" style="color: #92400e;">
					<input
						type="checkbox"
						name="delete_acknowledgement"
						value="experimental-delete-acknowledged"
						required
					/>
					<span>{t(locale, 'transactionDetail.deleteAcknowledgement')}</span>
				</label>
				<button class="mt-4 rounded-xl px-4 py-2 text-sm font-semibold text-white" style="background: #b91c1c;" type="submit">
					{t(locale, 'transactionDetail.deleteButton')}
				</button>
			</form>
		{/if}
	</section>
</main>
