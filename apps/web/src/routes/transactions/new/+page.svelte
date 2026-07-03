<script lang="ts">
	import WriteModeWarning from '$lib/components/WriteModeWarning.svelte';
	import { DEFAULT_LOCALE, t, type Locale } from '$lib/i18n';

	let { data, form } = $props();
	let locale = $derived<Locale>(data.locale ?? DEFAULT_LOCALE);

	type PreviousPayload = {
		date?: string;
		debit_account_id?: string;
		credit_account_id?: string;
		amount?: string;
		currency?: string;
		description?: string;
		memo?: string;
	};

	const today = new Date().toISOString().slice(0, 10);
	const previous = $derived((form?.payload ?? {}) as PreviousPayload);
	const preview = $derived((form as any)?.preview);
</script>

<svelte:head>
	<title>Preview transaction — GnuCash Web Companion</title>
</svelte:head>

<main class="mx-auto max-w-4xl px-4 py-8">
	<div class="mb-6 flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
		<div>
			<p class="text-sm font-medium uppercase tracking-wide" style="color: var(--app-accent);">{t(locale, 'writeMode.kicker')}</p>
			<h1 class="mt-1 text-3xl font-bold" style="color: var(--app-text);">Transaction entry preview</h1>
			<p class="mt-2 text-sm" style="color: var(--app-muted);">
				Owner-only browser/mobile form for validating one future CREATE. This slice is preview only; no write is executed.
			</p>
		</div>
		<a class="rounded-xl px-4 py-2 text-sm font-semibold" style="border: 1px solid var(--app-border); color: var(--app-text);" href="/transactions">Back</a>
	</div>

	{#if form?.error}
		<div class="mb-4 rounded-2xl p-4 text-sm" role="alert" style="border: 1px solid #fecaca; background: #fef2f2; color: #991b1b;">
			<p class="font-semibold">Preview validation failed</p>
			<p class="mt-1">{form.error}</p>
			<p class="mt-1">No CREATE, PATCH, DELETE, or batch operation was executed.</p>
		</div>
	{/if}

	<div class="mb-4 rounded-2xl p-4 text-sm" role="status" style="border: 1px solid #93c5fd; background: #eff6ff; color: #1e3a8a;">
		<p class="font-semibold">Preview only / no write executed</p>
		<p class="mt-1">
			This page calls only POST /books/&lbrace;book_id&rbrace;/transactions/create-preview, a non-mutating backend preview endpoint.
			No CREATE, PATCH, DELETE, or batch operation is executed. A future CREATE still requires fresh owner approval,
			exact CREATE count, enabled write gates, backup/read-back/audit/reset/probes, and private verification.
		</p>
	</div>

	<div class="mb-4">
		<WriteModeWarning {locale} compact />
	</div>

	<form method="POST" class="space-y-5 rounded-2xl p-5" style="background: var(--app-panel); border: 1px solid var(--app-border); box-shadow: 0 1px 3px var(--app-panel-shadow);">
		<label class="block text-sm font-medium" style="color: var(--app-text);">
			Book
			<select name="book_id" class="mt-1 w-full rounded-xl px-3 py-2" style="background: var(--app-bg); color: var(--app-text); border: 1px solid var(--app-border);">
				{#each data.books as book}
					<option value={book.id} selected={book.id === data.activeBook?.id}>{book.name}</option>
				{/each}
			</select>
		</label>

		<div class="grid gap-4 md:grid-cols-2">
			<label class="block text-sm font-medium" style="color: var(--app-text);">
				Date
				<input name="date" type="date" required value={previous.date ?? today} class="mt-1 w-full rounded-xl px-3 py-2" style="background: var(--app-bg); color: var(--app-text); border: 1px solid var(--app-border);" />
			</label>
			<label class="block text-sm font-medium" style="color: var(--app-text);">
				Currency
				<input name="currency" maxlength="3" required value={previous.currency ?? data.activeBook?.base_currency ?? 'SEK'} class="mt-1 w-full rounded-xl px-3 py-2 uppercase" style="background: var(--app-bg); color: var(--app-text); border: 1px solid var(--app-border);" />
			</label>
		</div>

		<label class="block text-sm font-medium" style="color: var(--app-text);">
			Description
			<input name="description" required value={previous.description ?? ''} class="mt-1 w-full rounded-xl px-3 py-2" style="background: var(--app-bg); color: var(--app-text); border: 1px solid var(--app-border);" />
		</label>

		<div class="grid gap-4 md:grid-cols-2">
			<label class="block text-sm font-medium" style="color: var(--app-text);">
				Amount
				<input name="amount" inputmode="decimal" required placeholder="320.00" value={previous.amount ?? ''} class="mt-1 w-full rounded-xl px-3 py-2" style="background: var(--app-bg); color: var(--app-text); border: 1px solid var(--app-border);" />
			</label>
			<label class="block text-sm font-medium" style="color: var(--app-text);">
				Memo (optional)
				<input name="memo" placeholder="Optional metadata only" value={previous.memo ?? ''} class="mt-1 w-full rounded-xl px-3 py-2" style="background: var(--app-bg); color: var(--app-text); border: 1px solid var(--app-border);" />
			</label>
		</div>

		<div class="grid gap-4 md:grid-cols-2">
			<label class="block text-sm font-medium" style="color: var(--app-text);">
				Debit/source account
				<select name="debit_account_id" required class="mt-1 w-full rounded-xl px-3 py-2" style="background: var(--app-bg); color: var(--app-text); border: 1px solid var(--app-border);">
					<option value="">Select source</option>
					{#each data.accounts as account}
						<option value={account.id} selected={account.id === previous.debit_account_id}>{account.full_name}</option>
					{/each}
				</select>
			</label>

			<label class="block text-sm font-medium" style="color: var(--app-text);">
				Credit/destination account
				<select name="credit_account_id" required class="mt-1 w-full rounded-xl px-3 py-2" style="background: var(--app-bg); color: var(--app-text); border: 1px solid var(--app-border);">
					<option value="">Select destination</option>
					{#each data.accounts as account}
						<option value={account.id} selected={account.id === previous.credit_account_id}>{account.full_name}</option>
					{/each}
				</select>
			</label>
		</div>

		<div class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
			<p class="text-sm" style="color: var(--app-muted);">Create/Submit mutation action is intentionally disabled in this preview slice.</p>
			<div class="flex flex-col gap-3 sm:flex-row">
				<button formaction="?/preview" formnovalidate class="rounded-xl px-4 py-2 font-semibold" style="border: 1px solid var(--app-border); color: var(--app-text);" type="submit">Preview transaction</button>
				<button class="cursor-not-allowed rounded-xl px-4 py-2 font-semibold text-white opacity-60" style="background: #6b7280;" type="button" disabled>Create disabled</button>
			</div>
		</div>
	</form>

	{#if preview}
		<section class="mt-6 rounded-2xl p-5" aria-label="Transaction preview" style="background: var(--app-panel); border: 1px solid var(--app-border);">
			<div class="flex flex-col gap-2 md:flex-row md:items-start md:justify-between">
				<div>
					<h2 class="text-xl font-semibold" style="color: var(--app-text);">Normalized preview</h2>
					<p class="mt-1 text-sm" style="color: var(--app-muted);">Preview only / no write executed. CREATE count represented: {preview.create_count}.</p>
				</div>
				<span class="rounded-full px-3 py-1 text-xs font-semibold" style="background: #dcfce7; color: #166534;">no mutation</span>
			</div>

			<dl class="mt-4 grid gap-3 md:grid-cols-2">
				<div><dt class="text-xs uppercase" style="color: var(--app-muted);">Date</dt><dd style="color: var(--app-text);">{preview.date}</dd></div>
				<div><dt class="text-xs uppercase" style="color: var(--app-muted);">Amount</dt><dd style="color: var(--app-text);">{preview.amount} {preview.currency}</dd></div>
				<div><dt class="text-xs uppercase" style="color: var(--app-muted);">Debit/source</dt><dd style="color: var(--app-text);">{preview.debit_account.full_name}</dd></div>
				<div><dt class="text-xs uppercase" style="color: var(--app-muted);">Credit/destination</dt><dd style="color: var(--app-text);">{preview.credit_account.full_name}</dd></div>
				<div><dt class="text-xs uppercase" style="color: var(--app-muted);">Description</dt><dd style="color: var(--app-text);">{preview.description}</dd></div>
				<div><dt class="text-xs uppercase" style="color: var(--app-muted);">Memo</dt><dd style="color: var(--app-text);">{preview.memo || '—'}</dd></div>
			</dl>

			{#if preview.warnings?.length}
				<ul class="mt-4 list-disc pl-5 text-sm" style="color: #92400e;">
					{#each preview.warnings as warning}
						<li>{warning}</li>
					{/each}
				</ul>
			{/if}
		</section>
	{/if}
</main>
