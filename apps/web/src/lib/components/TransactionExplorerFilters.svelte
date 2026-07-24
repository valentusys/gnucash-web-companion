<script lang="ts">
	import type { Account } from '$lib/api/types';
	import { DEFAULT_LOCALE, t, type Locale } from '$lib/i18n';
	import type { TransactionExplorerValidatedInput } from '$lib/transactions/explorer';

	type DatePreset = { label: string; href: string; active: boolean };
	type ActiveFilterChip = { key: string; label: string; href: string };

	let {
		filters,
		accounts = [],
		accountOptionsLimited = false,
		datePresets = [],
		activeFilters = [],
		resetHref,
		pageSizeOptions = [],
		locale = DEFAULT_LOCALE
	}: {
		filters: TransactionExplorerValidatedInput;
		accounts?: Account[];
		accountOptionsLimited?: boolean;
		datePresets?: DatePreset[];
		activeFilters?: ActiveFilterChip[];
		resetHref: string;
		pageSizeOptions?: readonly number[];
		locale?: Locale;
	} = $props();

	const selectedAccounts = $derived(new Set(filters.accountIds));
	const hasAccountMode = $derived(filters.accountIds.length > 0);
	const hasTypeMode = $derived(Boolean(filters.type));
	const hasActiveFilters = $derived(activeFilters.length > 0);

	function accountOptionLabel(account: Account): string {
		return account.display_name || account.name || account.full_name;
	}
</script>

<form
	method="GET"
	action="/transactions"
	class="mb-4 flex flex-col gap-4 rounded-xl p-4"
	style="background-color: var(--app-panel); box-shadow: 0 1px 3px var(--app-panel-shadow); border: 1px solid var(--app-border);"
	aria-describedby="transactions-explorer-form-help"
>
	<div class="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
		<div>
			<p class="text-sm font-semibold" style="color: var(--app-text);">{t(locale, 'transactions.filters.title')}</p>
			<p id="transactions-explorer-form-help" class="mt-1 text-xs" style="color: var(--app-muted);">
				{t(locale, 'transactions.explorer.formHelp')}
			</p>
		</div>
		<a
			class="inline-flex min-h-11 items-center justify-center rounded-xl border px-4 py-2 text-sm font-semibold"
			style="border-color: var(--app-border); color: var(--app-text); background: var(--app-bg);"
			href={resetHref}
		>
			{t(locale, 'transactions.explorer.reset')}
		</a>
	</div>

	{#if datePresets.length}
		<section aria-labelledby="transactions-date-presets-title">
			<p id="transactions-date-presets-title" class="text-xs font-semibold uppercase tracking-wide" style="color: var(--app-muted);">
				{t(locale, 'transactions.filters.datePresets')}
			</p>
			<div class="mt-2 flex flex-wrap gap-2" aria-label={t(locale, 'transactions.filters.datePresetAria')}>
				{#each datePresets as preset}
					<a
						href={preset.href}
						class="inline-flex min-h-11 items-center rounded-xl border px-3 py-2 text-sm font-semibold"
						style={preset.active
							? 'border-color: var(--app-accent); color: white; background: var(--app-accent);'
							: 'border-color: var(--app-border); color: var(--app-text); background: var(--app-bg);'}
						aria-current={preset.active ? 'page' : undefined}
					>
						{preset.label}
					</a>
				{/each}
			</div>
			<p class="mt-2 text-xs" style="color: var(--app-muted);">{t(locale, 'transactions.explorer.datePresetHelp')}</p>
		</section>
	{/if}

	{#if hasActiveFilters}
		<section
			class="rounded-xl border px-3 py-3"
			style="border-color: var(--app-border); background: var(--app-bg);"
			aria-labelledby="transactions-active-filters-title"
			aria-live="polite"
		>
			<p id="transactions-active-filters-title" class="text-xs font-semibold uppercase tracking-wide" style="color: var(--app-muted);">
				{t(locale, 'transactions.filters.activeSummaryTitle')}
			</p>
			<ul class="mt-2 flex flex-wrap gap-2">
				{#each activeFilters as chip (chip.key)}
					<li>
						<a
							class="inline-flex min-h-11 items-center rounded-full border px-3 py-2 text-sm font-medium"
							style="border-color: var(--app-border); color: var(--app-text); background: var(--app-panel);"
							href={chip.href}
							aria-label={`${t(locale, 'transactions.explorer.removeFilter')}: ${chip.label}`}
						>
							<span>{chip.label}</span>
							<span class="ml-2" aria-hidden="true">×</span>
						</a>
					</li>
				{/each}
			</ul>
		</section>
	{/if}

	<div class="grid gap-4 lg:grid-cols-2">
		<fieldset class="min-w-0 rounded-xl border p-3" style="border-color: var(--app-border);">
			<legend class="px-1 text-sm font-semibold" style="color: var(--app-text);">{t(locale, 'transactions.explorer.dateTextLegend')}</legend>
			<div class="mt-2 grid gap-3 sm:grid-cols-2">
				<label class="text-sm font-medium" for="tx-date-from">
					<span>{t(locale, 'transactions.filters.from')}</span>
					<input
						id="tx-date-from"
						name="date_from"
						type="date"
						value={filters.dateFrom}
						class="mt-1 min-h-11 w-full rounded-xl border px-3 py-2"
						style="border-color: var(--app-input-border); background-color: var(--app-input-bg); color: var(--app-text);"
					/>
				</label>
				<label class="text-sm font-medium" for="tx-date-to">
					<span>{t(locale, 'transactions.filters.to')}</span>
					<input
						id="tx-date-to"
						name="date_to"
						type="date"
						value={filters.dateTo}
						class="mt-1 min-h-11 w-full rounded-xl border px-3 py-2"
						style="border-color: var(--app-input-border); background-color: var(--app-input-bg); color: var(--app-text);"
					/>
				</label>
				<label class="text-sm font-medium sm:col-span-2" for="tx-query">
					<span>{t(locale, 'transactions.filters.search')}</span>
					<input
						id="tx-query"
						name="query"
						type="text"
						maxlength="120"
						value={filters.query}
						placeholder={t(locale, 'transactions.filters.searchPlaceholder')}
						class="mt-1 min-h-11 w-full rounded-xl border px-3 py-2"
						style="border-color: var(--app-input-border); background-color: var(--app-input-bg); color: var(--app-text);"
					/>
				</label>
				<label class="text-sm font-medium" for="tx-state">
					<span>{t(locale, 'transactions.filters.state')}</span>
					<select
						id="tx-state"
						name="transaction_state"
						class="mt-1 min-h-11 w-full rounded-xl border px-3 py-2"
						style="border-color: var(--app-input-border); background-color: var(--app-input-bg); color: var(--app-text);"
						aria-describedby="tx-state-help"
					>
						<option value="" selected={!filters.transactionState}>{t(locale, 'transactions.filters.anyState')}</option>
						<option value="unreconciled" selected={filters.transactionState === 'unreconciled'}>{t(locale, 'transactions.filters.stateUnreconciled')}</option>
						<option value="cleared" selected={filters.transactionState === 'cleared'}>{t(locale, 'transactions.filters.stateCleared')}</option>
						<option value="reconciled" selected={filters.transactionState === 'reconciled'}>{t(locale, 'transactions.filters.stateReconciled')}</option>
						<option value="voided" selected={filters.transactionState === 'voided'}>{t(locale, 'transactions.filters.stateVoided')}</option>
					</select>
					<span id="tx-state-help" class="mt-1 block text-xs" style="color: var(--app-muted);">{t(locale, 'transactions.filters.stateHelp')}</span>
				</label>
			</div>
		</fieldset>

		<fieldset class="min-w-0 rounded-xl border p-3" style="border-color: var(--app-border);">
			<legend class="px-1 text-sm font-semibold" style="color: var(--app-text);">{t(locale, 'transactions.explorer.scopeLegend')}</legend>
			<p class="mt-1 text-xs" style="color: var(--app-muted);">{t(locale, 'transactions.explorer.scopeHelp')}</p>
			<div class="mt-2 grid gap-3 sm:grid-cols-2">
				<label class="text-sm font-medium sm:col-span-2" for="tx-account-ids">
					<span>{t(locale, 'transactions.explorer.accountIds')}</span>
					<select
						id="tx-account-ids"
						name="account_ids"
						multiple
						size="6"
						disabled={hasTypeMode}
						class="mt-1 min-h-11 w-full rounded-xl border px-3 py-2"
						style="border-color: var(--app-input-border); background-color: var(--app-input-bg); color: var(--app-text);"
						aria-describedby="tx-account-ids-help"
					>
						{#each accounts as account (account.id)}
							<option value={account.id.toLowerCase()} selected={selectedAccounts.has(account.id.toLowerCase())} title={account.full_name}>{accountOptionLabel(account)}</option>
						{/each}
					</select>
					<span id="tx-account-ids-help" class="mt-1 block text-xs" style="color: var(--app-muted);">
						{hasTypeMode ? t(locale, 'transactions.explorer.accountsDisabledByType') : t(locale, 'transactions.explorer.accountIdsHelp')}
						{#if accountOptionsLimited} {t(locale, 'transactions.explorer.accountOptionsLimited')}{/if}
					</span>
				</label>
				<label class="text-sm font-medium" for="tx-type">
					<span>{t(locale, 'transactions.explorer.type')}</span>
					<select
						id="tx-type"
						name="type"
						disabled={hasAccountMode}
						class="mt-1 min-h-11 w-full rounded-xl border px-3 py-2"
						style="border-color: var(--app-input-border); background-color: var(--app-input-bg); color: var(--app-text);"
					>
						<option value="" selected={!filters.type}>{t(locale, 'transactions.explorer.typeAny')}</option>
						<option value="income" selected={filters.type === 'income'}>{t(locale, 'transactions.explorer.typeIncome')}</option>
						<option value="expense" selected={filters.type === 'expense'}>{t(locale, 'transactions.explorer.typeExpense')}</option>
					</select>
				</label>
				<label class="text-sm font-medium" for="tx-direction">
					<span>{t(locale, 'transactions.explorer.direction')}</span>
					<select
						id="tx-direction"
						name="direction"
						disabled={!hasAccountMode}
						class="mt-1 min-h-11 w-full rounded-xl border px-3 py-2"
						style="border-color: var(--app-input-border); background-color: var(--app-input-bg); color: var(--app-text);"
						aria-describedby="tx-direction-help"
					>
						<option value="" selected={!filters.direction}>{t(locale, 'transactions.explorer.directionAny')}</option>
						<option value="increase" selected={filters.direction === 'increase'}>{t(locale, 'transactions.explorer.directionIncrease')}</option>
						<option value="decrease" selected={filters.direction === 'decrease'}>{t(locale, 'transactions.explorer.directionDecrease')}</option>
					</select>
					<span id="tx-direction-help" class="mt-1 block text-xs" style="color: var(--app-muted);">{t(locale, 'transactions.explorer.directionHelp')}</span>
				</label>
			</div>
		</fieldset>

		<fieldset class="min-w-0 rounded-xl border p-3 lg:col-span-2" style="border-color: var(--app-border);">
			<legend class="px-1 text-sm font-semibold" style="color: var(--app-text);">{t(locale, 'transactions.explorer.amountPagingLegend')}</legend>
			<div class="mt-2 grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
				<label class="text-sm font-medium" for="tx-min-amount">
					<span>{t(locale, 'transactions.filters.minAmount')}</span>
					<input
						id="tx-min-amount"
						name="min_amount"
						type="text"
						inputmode="decimal"
						pattern="[0-9]+(\.[0-9]+)?"
						value={filters.minAmount}
						placeholder="0.00"
						class="mt-1 min-h-11 w-full rounded-xl border px-3 py-2"
						style="border-color: var(--app-input-border); background-color: var(--app-input-bg); color: var(--app-text);"
					/>
				</label>
				<label class="text-sm font-medium" for="tx-max-amount">
					<span>{t(locale, 'transactions.filters.maxAmount')}</span>
					<input
						id="tx-max-amount"
						name="max_amount"
						type="text"
						inputmode="decimal"
						pattern="[0-9]+(\.[0-9]+)?"
						value={filters.maxAmount}
						placeholder="1000.00"
						class="mt-1 min-h-11 w-full rounded-xl border px-3 py-2"
						style="border-color: var(--app-input-border); background-color: var(--app-input-bg); color: var(--app-text);"
					/>
				</label>
				<label class="text-sm font-medium" for="tx-sort">
					<span>{t(locale, 'transactions.explorer.sort')}</span>
					<select id="tx-sort" name="sort" class="mt-1 min-h-11 w-full rounded-xl border px-3 py-2" style="border-color: var(--app-input-border); background-color: var(--app-input-bg); color: var(--app-text);">
						<option value="date_desc" selected={filters.sort === 'date_desc'}>{t(locale, 'transactions.explorer.sortDateDesc')}</option>
						<option value="date_asc" selected={filters.sort === 'date_asc'}>{t(locale, 'transactions.explorer.sortDateAsc')}</option>
					</select>
				</label>
				<label class="text-sm font-medium" for="tx-page-size">
					<span>{t(locale, 'transactions.explorer.pageSize')}</span>
					<input
						id="tx-page-size"
						name="page_size"
						type="number"
						min="1"
						max="100"
						step="1"
						list="tx-page-size-options"
						value={filters.pageSize}
						class="mt-1 min-h-11 w-full rounded-xl border px-3 py-2"
						style="border-color: var(--app-input-border); background-color: var(--app-input-bg); color: var(--app-text);"
					/>
					<datalist id="tx-page-size-options">
						{#each pageSizeOptions as pageSize}
							<option value={pageSize}>{pageSize}</option>
						{/each}
					</datalist>
				</label>
				<div class="flex items-end gap-2">
					<button class="inline-flex min-h-11 w-full items-center justify-center rounded-xl px-4 py-2 text-sm font-semibold text-white" style="background: var(--app-accent);" type="submit">
						{t(locale, 'transactions.filters.submit')}
					</button>
				</div>
			</div>
			<p class="mt-2 text-xs" style="color: var(--app-muted);">{t(locale, 'transactions.explorer.amountPagingHelp')}</p>
		</fieldset>
	</div>
</form>
