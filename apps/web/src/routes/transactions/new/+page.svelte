<script lang="ts">
	import WriteModeWarning from '$lib/components/WriteModeWarning.svelte';
	import { DEFAULT_LOCALE, t, type Locale } from '$lib/i18n';

	let { data, form } = $props();
	let locale = $derived<Locale>(data.locale ?? DEFAULT_LOCALE);

	type SplitPayload = {
		account_id?: string;
		amount?: string;
		currency?: string;
		memo?: string;
	};
	type PreviousPayload = {
		date?: string;
		description?: string;
		splits?: SplitPayload[];
	};

	const today = new Date().toISOString().slice(0, 10);
	let confirmed = $state(false);

	const previous = $derived((form?.payload ?? {}) as PreviousPayload);
	const validation = $derived(form?.validation);
	const hasBlockingErrors = $derived(Boolean(validation && !validation.valid));
	let writeAcknowledged = $state(false);

	function confirmSubmit() {
		if (hasBlockingErrors) return false;
		if (!writeAcknowledged) return true;
		confirmed = window.confirm(t(locale, 'writeMode.finalConfirm'));
		return confirmed;
	}
</script>

<svelte:head>
	<title>New transaction — GnuCash Web Companion</title>
</svelte:head>

<main class="mx-auto max-w-3xl px-4 py-8">
	<div class="mb-6 flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
		<div>
			<p class="text-sm font-medium uppercase tracking-wide" style="color: var(--app-accent);">{t(locale, 'writeMode.kicker')}</p>
			<h1 class="mt-1 text-3xl font-bold" style="color: var(--app-text);">{t(locale, 'writeMode.newTransactionTitle')}</h1>
			<p class="mt-2 text-sm" style="color: var(--app-muted);">
				{t(locale, 'writeMode.newTransactionHelp')}
			</p>
		</div>
		<a class="rounded-xl px-4 py-2 text-sm font-semibold" style="border: 1px solid var(--app-border); color: var(--app-text);" href="/transactions">Back</a>
	</div>

	{#if form?.error}
		<div class="mb-4 rounded-2xl p-4 text-sm" role="alert" style="border: 1px solid #fecaca; background: #fef2f2; color: #991b1b;">
			{form.error}
		</div>
	{/if}

	<div class="mb-4">
		<WriteModeWarning {locale} />
	</div>

	{#if validation}
		<div class="mb-4 rounded-2xl p-4 text-sm" role="status" style="border: 1px solid var(--app-border); background: var(--app-panel); color: var(--app-text);">
			<p class="font-semibold">Validation: {validation.valid ? 'passed' : 'failed'}</p>
			{#if validation.errors.length}
				<ul class="mt-2 list-disc pl-5" style="color: #b91c1c;">
					{#each validation.errors as error}
						<li>{error}</li>
					{/each}
				</ul>
			{/if}
			{#if validation.warnings.length}
				<ul class="mt-2 list-disc pl-5" style="color: #b45309;">
					{#each validation.warnings as warning}
						<li>{warning}</li>
					{/each}
				</ul>
			{/if}
		</div>
	{/if}

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
				<input name="currency" maxlength="3" required value={previous.splits?.[0]?.currency ?? data.activeBook?.base_currency ?? 'SEK'} class="mt-1 w-full rounded-xl px-3 py-2 uppercase" style="background: var(--app-bg); color: var(--app-text); border: 1px solid var(--app-border);" />
			</label>
		</div>

		<label class="block text-sm font-medium" style="color: var(--app-text);">
			Description
			<input name="description" required value={previous.description ?? ''} class="mt-1 w-full rounded-xl px-3 py-2" style="background: var(--app-bg); color: var(--app-text); border: 1px solid var(--app-border);" />
		</label>

		<label class="block text-sm font-medium" style="color: var(--app-text);">
			Amount
			<input name="amount" inputmode="decimal" required placeholder="320.00" value={previous.splits?.[1]?.amount ?? ''} class="mt-1 w-full rounded-xl px-3 py-2" style="background: var(--app-bg); color: var(--app-text); border: 1px solid var(--app-border);" />
		</label>

		<div class="grid gap-4 md:grid-cols-2">
			<label class="block text-sm font-medium" style="color: var(--app-text);">
				From account
				<select name="from_account_id" required class="mt-1 w-full rounded-xl px-3 py-2" style="background: var(--app-bg); color: var(--app-text); border: 1px solid var(--app-border);">
					<option value="">Select source</option>
					{#each data.accounts as account}
						<option value={account.id} selected={account.id === previous.splits?.[0]?.account_id}>{account.full_name}</option>
					{/each}
				</select>
				<input name="from_memo" placeholder="Memo" value={previous.splits?.[0]?.memo ?? ''} class="mt-2 w-full rounded-xl px-3 py-2" style="background: var(--app-bg); color: var(--app-text); border: 1px solid var(--app-border);" />
			</label>

			<label class="block text-sm font-medium" style="color: var(--app-text);">
				To account
				<select name="to_account_id" required class="mt-1 w-full rounded-xl px-3 py-2" style="background: var(--app-bg); color: var(--app-text); border: 1px solid var(--app-border);">
					<option value="">Select destination</option>
					{#each data.accounts as account}
						<option value={account.id} selected={account.id === previous.splits?.[1]?.account_id}>{account.full_name}</option>
					{/each}
				</select>
				<input name="to_memo" placeholder="Memo" value={previous.splits?.[1]?.memo ?? ''} class="mt-2 w-full rounded-xl px-3 py-2" style="background: var(--app-bg); color: var(--app-text); border: 1px solid var(--app-border);" />
			</label>
		</div>

		<label class="flex gap-3 rounded-2xl p-4 text-sm" style="border: 1px solid #f59e0b; background: #fffbeb; color: #78350f;">
			<input
				name="write_acknowledgement"
				type="checkbox"
				value="experimental-write-mode-acknowledged"
				bind:checked={writeAcknowledged}
				class="mt-1 h-4 w-4"
				required
			/>
			<span>{t(locale, 'writeMode.acknowledgement')}</span>
		</label>

		<div class="flex flex-col gap-3 md:flex-row md:justify-end">
			<button formaction="?/validate" formnovalidate class="rounded-xl px-4 py-2 font-semibold" style="border: 1px solid var(--app-border); color: var(--app-text);" type="submit">Validate</button>
			<button
				formaction="?/create"
				onclick={(event) => {
					if (!confirmSubmit()) event.preventDefault();
				}}
				class="rounded-xl px-4 py-2 font-semibold text-white"
				style="background: var(--app-accent);"
				type="submit"
			>
				Create transaction
			</button>
		</div>
	</form>
</main>
