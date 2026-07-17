<script lang="ts">
	import type {
		Book,
		BookCapabilityFlags,
		BookHealth,
		BookPreflightResponse,
		BookProblemCode,
		BookSectionStatus,
		TransactionCreateSettings
	} from '$lib/api/types';
	import { DEFAULT_LOCALE, t, type Locale, type MessageKey } from '$lib/i18n';

	type LifecycleSuccessCode = 'recheck' | 'rename' | 'set_default' | 'disable' | 'enable' | 'transaction_create_settings';
	type PageForm = {
		lifecycleSuccessCode?: LifecycleSuccessCode;
		lifecycleErrorCode?: BookProblemCode;
		enablePreflight?: BookPreflightResponse;
		enablePreflightErrorCode?: BookProblemCode;
		enableMakeDefault?: boolean;
		transactionCreateSettings?: TransactionCreateSettings;
	} | null;

	let { data, form }: { data: { locale?: Locale; book: Book; isAdmin: boolean; transactionCreateSettings: TransactionCreateSettings }; form?: PageForm } = $props();
	let locale = $derived<Locale>(data.locale ?? DEFAULT_LOCALE);
	const transactionCreateSettings = $derived(form?.transactionCreateSettings ?? data.transactionCreateSettings);

	const knownStatusCodes = new Set([
		'ready',
		'available',
		'ok',
		'warning',
		'rejected',
		'unavailable',
		'unknown',
		'missing_file',
		'not_configured',
		'remote_or_unchecked',
		'invalid_gnucash_schema',
		'action_required',
		'not_checked',
		'disabled',
		'failed',
		'empty',
		'blocked',
		'unsupported'
	]);

	const openLinkDefinitions: Array<{
		capability: keyof Pick<BookCapabilityFlags, 'can_open_accounts' | 'can_open_transactions' | 'can_open_reports'>;
		next: '/accounts' | '/transactions' | '/reports';
		labelKey: MessageKey;
	}> = [
		{ capability: 'can_open_accounts', next: '/accounts', labelKey: 'books.viewAccounts' },
		{ capability: 'can_open_transactions', next: '/transactions', labelKey: 'books.browseTransactions' },
		{ capability: 'can_open_reports', next: '/reports', labelKey: 'books.reportsLink' }
	];

	const healthRows: Array<{ field: keyof BookHealth; labelKey: MessageKey }> = [
		{ field: 'status', labelKey: 'books.status' },
		{ field: 'safe_code', labelKey: 'books.healthSafeCode' },
		{ field: 'source_status', labelKey: 'books.healthSourceStatus' },
		{ field: 'open_status', labelKey: 'books.healthOpenStatus' },
		{ field: 'accounts_status', labelKey: 'books.healthAccountsStatus' },
		{ field: 'transactions_status', labelKey: 'books.healthTransactionsStatus' },
		{ field: 'reports_status', labelKey: 'books.healthReportsStatus' }
	];

	function capabilityRows(book: Book): Array<{ labelKey: MessageKey; value: boolean | undefined }> {
		return [
			{ labelKey: 'books.capabilityReadOnly', value: book.capabilities?.read_only ?? book.read_only },
			{ labelKey: 'books.capabilityAccounts', value: book.capabilities?.can_open_accounts },
			{ labelKey: 'books.capabilityTransactions', value: book.capabilities?.can_open_transactions },
			{ labelKey: 'books.capabilityReports', value: book.capabilities?.can_open_reports },
			{ labelKey: 'books.capabilityUpload', value: book.capabilities?.can_upload },
			{ labelKey: 'books.capabilityEdit', value: book.capabilities?.can_edit },
			{ labelKey: 'books.capabilityDelete', value: book.capabilities?.can_delete }
		];
	}

	type ChecklistSection = 'source' | 'open' | 'accounts' | 'transactions' | 'reports';
	type SectionMessageStatus = 'ready' | 'rejected' | 'unavailable';
	const sectionStatusMessageKeys: Record<ChecklistSection, Record<SectionMessageStatus, MessageKey>> = {
		source: {
			ready: 'books.sectionStatus.source.ready',
			rejected: 'books.sectionStatus.source.rejected',
			unavailable: 'books.sectionStatus.source.unavailable'
		},
		open: {
			ready: 'books.sectionStatus.open.ready',
			rejected: 'books.sectionStatus.open.rejected',
			unavailable: 'books.sectionStatus.open.unavailable'
		},
		accounts: {
			ready: 'books.sectionStatus.accounts.ready',
			rejected: 'books.sectionStatus.accounts.rejected',
			unavailable: 'books.sectionStatus.accounts.unavailable'
		},
		transactions: {
			ready: 'books.sectionStatus.transactions.ready',
			rejected: 'books.sectionStatus.transactions.rejected',
			unavailable: 'books.sectionStatus.transactions.unavailable'
		},
		reports: {
			ready: 'books.sectionStatus.reports.ready',
			rejected: 'books.sectionStatus.reports.rejected',
			unavailable: 'books.sectionStatus.reports.unavailable'
		}
	};

	const checklistSections: Array<{
		section: ChecklistSection;
		field: 'source_status' | 'open_status' | 'accounts' | 'transactions' | 'reports';
	}> = [
		{ section: 'source', field: 'source_status' },
		{ section: 'open', field: 'open_status' },
		{ section: 'accounts', field: 'accounts' },
		{ section: 'transactions', field: 'transactions' },
		{ section: 'reports', field: 'reports' }
	];

	function isBookEnabled(book: Book): boolean {
		return book.is_enabled !== false;
	}

	function boolLabel(value: boolean | undefined): string {
		return value ? t(locale, 'books.yes') : t(locale, 'books.no');
	}

	function formatValue(value: string | null | undefined): string {
		return value?.trim() || t(locale, 'books.notConfigured');
	}

	function statusLabel(status: string | null | undefined): string {
		const safeStatus = status && knownStatusCodes.has(status) ? status : 'unknown';
		return t(locale, `books.status.${safeStatus}` as MessageKey);
	}

	function bookProblemMessage(code: BookProblemCode | undefined): string {
		return t(locale, `books.problem.${code ?? 'unknown_book_problem'}` as MessageKey);
	}

	function successMessage(code: LifecycleSuccessCode | undefined): string {
		if (code === 'recheck') return t(locale, 'books.manageSuccessRecheck');
		if (code === 'rename') return t(locale, 'books.manageSuccessRename');
		if (code === 'set_default') return t(locale, 'books.manageSuccessSetDefault');
		if (code === 'disable') return t(locale, 'books.manageSuccessDisable');
		if (code === 'enable') return t(locale, 'books.manageSuccessEnable');
		if (code === 'transaction_create_settings') return t(locale, 'books.transactionCreateSettingsSuccess');
		return '';
	}

	function canOpenCapability(book: Book, capability: 'can_open_accounts' | 'can_open_transactions' | 'can_open_reports'): boolean {
		return isBookEnabled(book) && book.can_open_read_only_views && book.capabilities?.[capability] === true;
	}

	function capabilityLinks(book: Book) {
		return openLinkDefinitions
			.filter((link) => canOpenCapability(book, link.capability))
			.map((link) => ({
				...link,
				href: `/books/${book.id}/select?next=${link.next}`,
				label: t(locale, link.labelKey)
			}));
	}

	function normalizedSectionStatus(status: string | null | undefined): SectionMessageStatus {
		if (status === 'ready' || status === 'available' || status === 'ok') return 'ready';
		if (status === 'rejected' || status === 'failed') return 'rejected';
		return 'unavailable';
	}

	function sectionStatusMessage(section: ChecklistSection, status: string | null | undefined): string {
		return t(locale, sectionStatusMessageKeys[section][normalizedSectionStatus(status)]);
	}

	function sectionLabel(section: string): string {
		return t(locale, `books.section.${section}` as MessageKey);
	}

	function sectionStatus(
		preflight: BookPreflightResponse,
		field: 'source_status' | 'open_status' | 'accounts' | 'transactions' | 'reports'
	): BookSectionStatus {
		return preflight[field];
	}

	function canConfirmEnable(preflight: BookPreflightResponse | undefined): boolean {
		return preflight?.status === 'ready' && Boolean(preflight.preflight_token);
	}

	let links = $derived(capabilityLinks(data.book));
</script>

<svelte:head>
	<title>{data.book.name} — {t(locale, 'books.settingsTitle')} — GnuCash Web Companion</title>
</svelte:head>

<main class="mx-auto max-w-5xl px-4 py-8">
	<a href="/books" class="inline-flex min-h-11 items-center rounded-lg border px-3 py-2 text-sm font-medium" style="border-color: var(--app-border); color: var(--app-text);">{t(locale, 'books.backToBooks')}</a>

	<div class="mt-6 space-y-2">
		<p class="text-sm font-medium uppercase tracking-wide" style="color: var(--app-accent);">{t(locale, 'books.kicker')}</p>
		<h1 class="break-words text-3xl font-bold" style="color: var(--app-text);">{data.book.name}</h1>
		<p class="max-w-3xl text-sm" style="color: var(--app-muted);">{t(locale, 'books.settingsSubtitle')}</p>
		<div class="flex flex-wrap gap-2 pt-2">
			{#if data.book.is_default}<span class="rounded-full px-2 py-1 text-xs font-semibold" style="background-color: var(--app-accent-soft); color: var(--app-accent);">{t(locale, 'books.defaultBook')}</span>{/if}
			<span class="rounded-full px-2 py-1 text-xs font-semibold" style="background-color: var(--app-hover-bg); color: var(--app-muted);">{isBookEnabled(data.book) ? t(locale, 'books.enabledBook') : t(locale, 'books.disabledBook')}</span>
			<span class="rounded-full px-2 py-1 text-xs font-semibold" style="background-color: var(--app-hover-bg); color: var(--app-muted);">{t(locale, 'books.readOnlyBadge')}</span>
		</div>
	</div>

	{#if form?.lifecycleSuccessCode}
		<p class="mt-6 rounded-xl border p-3 text-sm" style="border-color: var(--app-accent); color: var(--app-text); background-color: var(--app-accent-soft);" role="status">{successMessage(form.lifecycleSuccessCode)}</p>
	{/if}
	{#if form?.lifecycleErrorCode}
		<p class="mt-6 rounded-xl border p-3 text-sm" style="border-color: var(--app-danger); color: var(--app-text); background-color: var(--app-card-bg);" role="alert">{bookProblemMessage(form.lifecycleErrorCode)}</p>
	{/if}

	<section class="mt-6 rounded-2xl border p-4" style="border-color: var(--app-border); background-color: var(--app-card-bg);">
		<h2 class="text-lg font-semibold" style="color: var(--app-text);">{t(locale, 'books.settingsSummaryTitle')}</h2>
		<dl class="mt-4 grid min-w-0 gap-3 text-sm sm:grid-cols-2 lg:grid-cols-4">
			<div class="min-w-0"><dt class="font-medium" style="color: var(--app-muted);">{t(locale, 'books.baseCurrency')}</dt><dd class="mt-1 break-words" style="color: var(--app-text);">{formatValue(data.book.base_currency)}</dd></div>
			<div class="min-w-0"><dt class="font-medium" style="color: var(--app-muted);">{t(locale, 'books.status')}</dt><dd class="mt-1 break-words" style="color: var(--app-text);">{statusLabel(data.book.health?.status ?? data.book.status)}</dd></div>
			<div class="min-w-0"><dt class="font-medium" style="color: var(--app-muted);">{t(locale, 'books.lastSuccessfulAt')}</dt><dd class="mt-1 break-words" style="color: var(--app-text);">{data.book.health?.last_successful_at ?? t(locale, 'books.notChecked')}</dd></div>
			<div class="min-w-0"><dt class="font-medium" style="color: var(--app-muted);">{t(locale, 'books.accessRole')}</dt><dd class="mt-1 break-words" style="color: var(--app-text);">{data.book.access_role_label || data.book.access_role || t(locale, 'books.unknown')}</dd></div>
		</dl>
	</section>

	<section class="mt-4 rounded-2xl border p-4" style="border-color: var(--app-border); background-color: var(--app-card-bg);">
		<h2 class="text-lg font-semibold" style="color: var(--app-text);">{t(locale, 'books.healthTitle')}</h2>
		<p class="mt-2 text-sm" style="color: var(--app-muted);">{t(locale, 'books.healthHelp')}</p>
		<dl class="mt-4 grid min-w-0 gap-3 text-sm sm:grid-cols-2 lg:grid-cols-3">
			{#each healthRows as row}
				<div class="min-w-0 rounded-xl p-3" style="background: var(--app-bg);">
					<dt class="font-medium" style="color: var(--app-muted);">{t(locale, row.labelKey)}</dt>
					<dd class="mt-1 break-words" style="color: var(--app-text);">{statusLabel(data.book.health?.[row.field])}</dd>
				</div>
			{/each}
			<div class="min-w-0 rounded-xl p-3" style="background: var(--app-bg);">
				<dt class="font-medium" style="color: var(--app-muted);">{t(locale, 'books.preflightCheckedAt')}</dt>
				<dd class="mt-1 break-words" style="color: var(--app-text);">{data.book.health?.checked_at ?? t(locale, 'books.notChecked')}</dd>
			</div>
			<div class="min-w-0 rounded-xl p-3" style="background: var(--app-bg);">
				<dt class="font-medium" style="color: var(--app-muted);">{t(locale, 'books.lastSuccessfulAt')}</dt>
				<dd class="mt-1 break-words" style="color: var(--app-text);">{data.book.health?.last_successful_at ?? t(locale, 'books.notChecked')}</dd>
			</div>
		</dl>
	</section>

	<section class="mt-4 rounded-2xl border p-4" style="border-color: var(--app-border); background-color: var(--app-card-bg);">
		<h2 class="text-lg font-semibold" style="color: var(--app-text);">{t(locale, 'books.capabilitiesTitle')}</h2>
		<ul class="mt-4 grid min-w-0 gap-2 text-sm sm:grid-cols-2 lg:grid-cols-3">
			{#each capabilityRows(data.book) as capability}
				<li class="min-w-0 rounded-xl p-3" style="background: var(--app-bg); color: var(--app-text);">
					<span class="font-medium">{t(locale, capability.labelKey)}</span>: {boolLabel(capability.value)}
				</li>
			{/each}
		</ul>
	</section>

	<section class="mt-4 rounded-2xl border p-4" style="border-color: var(--app-border); background-color: var(--app-card-bg);">
		<h2 class="text-lg font-semibold" style="color: var(--app-text);">{t(locale, 'books.openSafeViews')}</h2>
		{#if links.length}
			<div class="mt-3 flex flex-wrap gap-2 text-sm">
				{#each links as link}
					<a class="inline-flex min-h-11 max-w-full items-center rounded-lg border px-3 py-2 font-medium" style="border-color: var(--app-border); color: var(--app-text);" href={link.href}>{link.label}</a>
				{/each}
			</div>
		{:else}
			<p class="mt-3 text-sm" style="color: var(--app-muted);">{t(locale, 'books.unavailableViews')}</p>
		{/if}
	</section>

	<section class="mt-4 rounded-2xl border p-4" style="border-color: var(--app-border); background-color: var(--app-card-bg);">
		<h2 class="text-lg font-semibold" style="color: var(--app-text);">{t(locale, 'books.storageDiagnostics')}</h2>
		<p class="mt-2 break-words text-sm" style="color: var(--app-muted);">{data.book.storage_diagnostics.safe_summary}</p>
		<p class="mt-2 text-xs" style="color: var(--app-muted);">{t(locale, 'books.privatePathRedacted')}</p>
	</section>

	<section id="transaction-create-settings" class="mt-4 rounded-2xl border p-4" style="border-color: var(--app-border); background-color: var(--app-card-bg);" aria-labelledby="transaction-create-settings-title">
		<h2 id="transaction-create-settings-title" class="text-lg font-semibold" style="color: var(--app-text);">{t(locale, 'books.transactionCreateSettingsTitle')}</h2>
		<p class="mt-2 text-sm" style="color: var(--app-muted);">{t(locale, 'books.transactionCreateSettingsHelp')}</p>
		<dl class="mt-4 grid min-w-0 gap-3 text-sm sm:grid-cols-2 lg:grid-cols-3">
			<div class="min-w-0 rounded-xl p-3" style="background: var(--app-bg);"><dt class="font-medium" style="color: var(--app-muted);">{t(locale, 'books.transactionCreateSettingsStatus')}</dt><dd class="mt-1 break-words" style="color: var(--app-text);">enabled {boolLabel(transactionCreateSettings.enabled)}; effective {boolLabel(transactionCreateSettings.effective_enabled)}</dd></div>
			<div class="min-w-0 rounded-xl p-3" style="background: var(--app-bg);"><dt class="font-medium" style="color: var(--app-muted);">Deployment gate</dt><dd class="mt-1 break-words" style="color: var(--app-text);">{boolLabel(transactionCreateSettings.deployment_writes_enabled)}</dd></div>
			<div class="min-w-0 rounded-xl p-3" style="background: var(--app-bg);"><dt class="font-medium" style="color: var(--app-muted);">Generation</dt><dd class="mt-1 break-words" style="color: var(--app-text);">{transactionCreateSettings.create_generation}</dd></div>
		</dl>
		{#if data.isAdmin}
			<form method="POST" action="?/patchTransactionCreateSettings" class="mt-4 flex min-w-0 flex-col gap-3 rounded-xl border p-3 sm:flex-row sm:items-center" style="border-color: var(--app-border);">
				<button name="enabled" value="true" type="submit" class="min-h-11 rounded-lg border px-3 py-2 text-sm font-medium" style="border-color: var(--app-border); color: var(--app-text); background-color: var(--app-bg);">{t(locale, 'books.transactionCreateEnableAction')}</button>
				<button name="enabled" value="false" type="submit" class="min-h-11 rounded-lg border px-3 py-2 text-sm font-medium" style="border-color: var(--app-danger); color: var(--app-danger); background-color: var(--app-bg);">{t(locale, 'books.transactionCreateDisableAction')}</button>
			</form>
		{:else}
			<p class="mt-4 rounded-xl border p-3 text-sm" data-normal-user-forbidden-toggle style="border-color: var(--app-border); background: var(--app-bg); color: var(--app-muted);">{t(locale, 'books.transactionCreateNormalUserForbidden')}</p>
		{/if}
	</section>

	{#if data.isAdmin}
		<section class="mt-6 rounded-2xl border p-4" style="border-color: var(--app-border); background-color: var(--app-card-bg);" aria-label={t(locale, 'books.adminLifecycleTitle')}>
			<h2 class="text-lg font-semibold" style="color: var(--app-text);">{t(locale, 'books.adminLifecycleTitle')}</h2>
			<p class="mt-2 text-sm" style="color: var(--app-muted);">{t(locale, 'books.adminLifecycleSafety')}</p>

			<div class="mt-4 grid min-w-0 gap-4 lg:grid-cols-2">
				<form method="POST" action="?/renameBook" class="min-w-0 rounded-xl border p-3" style="border-color: var(--app-border);">
					<h3 class="font-semibold" style="color: var(--app-text);">{t(locale, 'books.renameTitle')}</h3>
					<p class="mt-1 text-sm" style="color: var(--app-muted);">{t(locale, 'books.renameHelp')}</p>
					<label class="mt-3 block text-sm font-medium" style="color: var(--app-text);">
						{t(locale, 'books.registerName')}
						<input name="name" required maxlength="256" value={data.book.name} class="mt-1 min-h-11 w-full min-w-0 rounded-lg border px-3 py-2" style="border-color: var(--app-border); background-color: var(--app-bg); color: var(--app-text);" />
					</label>
					<label class="mt-3 block text-sm font-medium" style="color: var(--app-text);">
						{t(locale, 'books.registerCurrency')}
						<input name="base_currency" required maxlength="16" value={data.book.base_currency ?? ''} class="mt-1 min-h-11 w-full min-w-0 rounded-lg border px-3 py-2 uppercase" style="border-color: var(--app-border); background-color: var(--app-bg); color: var(--app-text);" />
					</label>
					<button type="submit" class="mt-3 inline-flex min-h-11 items-center rounded-lg border px-3 py-2 text-sm font-medium" style="border-color: var(--app-border); color: var(--app-text); background-color: var(--app-bg);">{t(locale, 'books.renameAction')}</button>
				</form>

				<div class="min-w-0 rounded-xl border p-3" style="border-color: var(--app-border);">
					<h3 class="font-semibold" style="color: var(--app-text);">{t(locale, 'books.recheckTitle')}</h3>
					<p class="mt-1 text-sm" style="color: var(--app-muted);">{t(locale, 'books.recheckHelp')}</p>
					<form method="POST" action="?/recheckHealth" class="mt-3">
						<button type="submit" class="inline-flex min-h-11 items-center rounded-lg border px-3 py-2 text-sm font-medium" style="border-color: var(--app-border); color: var(--app-text); background-color: var(--app-bg);">{t(locale, 'books.recheckAction')}</button>
					</form>
					{#if data.book.management_actions.includes('set_default') && !data.book.is_default && isBookEnabled(data.book)}
						<form method="POST" action="?/setDefaultBook" class="mt-3">
							<button type="submit" class="inline-flex min-h-11 items-center rounded-lg border px-3 py-2 text-sm font-medium" style="border-color: var(--app-border); color: var(--app-text); background-color: var(--app-bg);">{t(locale, 'books.setDefaultAction')}</button>
						</form>
					{/if}
				</div>
			</div>

			{#if isBookEnabled(data.book) && data.book.management_actions.includes('disable')}
				<form method="POST" action="?/disableBook" class="mt-4 min-w-0 rounded-xl border p-3" style="border-color: var(--app-border);">
					<h3 class="font-semibold" style="color: var(--app-text);">{t(locale, 'books.disableTitle')}</h3>
					<p class="mt-1 text-sm" style="color: var(--app-muted);">{t(locale, 'books.disableHelp')}</p>
					<label class="mt-3 flex items-start gap-2 text-xs" style="color: var(--app-muted);">
						<input required type="checkbox" name="confirm_metadata_only" class="mt-1" />
						<span>{t(locale, 'books.disableMetadataConfirm')}</span>
					</label>
					<button type="submit" class="mt-3 inline-flex min-h-11 items-center rounded-lg border px-3 py-2 text-sm font-medium" style="border-color: var(--app-danger); color: var(--app-danger); background-color: var(--app-bg);">{t(locale, 'books.disableAction')}</button>
				</form>
			{/if}

			{#if !isBookEnabled(data.book) && data.book.management_actions.includes('enable')}
				<section class="mt-4 min-w-0 rounded-xl border p-3" style="border-color: var(--app-border);">
					<h3 class="font-semibold" style="color: var(--app-text);">{t(locale, 'books.enableTitle')}</h3>
					<p class="mt-1 text-sm" style="color: var(--app-muted);">{t(locale, 'books.enablePreflightHelp')}</p>
					{#if form?.enablePreflightErrorCode}
						<p class="mt-3 rounded-xl border p-3 text-sm" style="border-color: var(--app-danger); color: var(--app-text); background-color: var(--app-card-bg);" role="alert">{bookProblemMessage(form.enablePreflightErrorCode)}</p>
					{/if}
					<form method="POST" action="?/enablePreflight" class="mt-3 grid min-w-0 gap-3 md:grid-cols-2">
						<label class="text-sm font-medium" style="color: var(--app-text);">
							{t(locale, 'books.registerName')}
							<input disabled value={data.book.name} class="mt-1 min-h-11 w-full min-w-0 rounded-lg border px-3 py-2" style="border-color: var(--app-border); background-color: var(--app-bg); color: var(--app-muted);" />
						</label>
						<label class="text-sm font-medium" style="color: var(--app-text);">
							{t(locale, 'books.registerCurrency')}
							<input disabled value={data.book.base_currency ?? ''} class="mt-1 min-h-11 w-full min-w-0 rounded-lg border px-3 py-2 uppercase" style="border-color: var(--app-border); background-color: var(--app-bg); color: var(--app-muted);" />
						</label>
						<label class="text-sm font-medium md:col-span-2" style="color: var(--app-text);">
							{t(locale, 'books.enablePath')}
							<input name="mounted_path" required autocomplete="off" placeholder="/data/books/copied-test-book.gnucash.sqlite" class="mt-1 min-h-11 w-full min-w-0 rounded-lg border px-3 py-2 font-mono text-sm" style="border-color: var(--app-border); background-color: var(--app-bg); color: var(--app-text);" />
						</label>
						<label class="flex min-h-11 items-start gap-3 text-sm md:col-span-2" style="color: var(--app-muted);">
							<input name="make_default" type="checkbox" checked={form?.enableMakeDefault ?? false} class="mt-1" />
							<span>{t(locale, 'books.registerMakeDefault')}</span>
						</label>
						<div class="md:col-span-2">
							<button type="submit" class="min-h-11 rounded-xl px-4 py-2 text-sm font-semibold text-white" style="background-color: var(--app-accent);">{t(locale, 'books.enablePreflightSubmit')}</button>
						</div>
					</form>

					{#if form?.enablePreflight}
						<section class="mt-4 rounded-xl border p-3" style="border-color: var(--app-border); background-color: var(--app-bg);" aria-live="polite">
							<h4 class="font-semibold" style="color: var(--app-text);">{t(locale, 'books.enablePreviewTitle')}</h4>
							<p class="mt-2 text-sm" style="color: var(--app-muted);">{form.enablePreflight.status === 'ready' ? t(locale, 'books.preflightReady') : t(locale, 'books.preflightRejected')}</p>
							<dl class="mt-3 grid gap-3 text-sm md:grid-cols-2">
								<div class="min-w-0 rounded-xl p-3" style="background: var(--app-card-bg);">
									<dt class="font-medium" style="color: var(--app-muted);">{t(locale, 'books.preflightFormat')}</dt>
									<dd class="mt-1 break-words" style="color: var(--app-text);">{form.enablePreflight.format}</dd>
								</div>
								<div class="min-w-0 rounded-xl p-3" style="background: var(--app-card-bg);">
									<dt class="font-medium" style="color: var(--app-muted);">{t(locale, 'books.preflightCheckedAt')}</dt>
									<dd class="mt-1 break-words" style="color: var(--app-text);">{form.enablePreflight.checked_at}</dd>
								</div>
							</dl>
							<ul class="mt-4 grid gap-2">
								{#each checklistSections as itemDefinition}
									{@const item = sectionStatus(form.enablePreflight, itemDefinition.field)}
									<li class="min-w-0 rounded-xl border p-3 text-sm" style="border-color: var(--app-border); background-color: var(--app-card-bg);">
										<div class="flex min-w-0 flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
											<span class="font-semibold" style="color: var(--app-text);">{sectionLabel(itemDefinition.section)}</span>
											<span class="w-fit rounded-full px-2 py-1 text-xs font-semibold" style="background-color: var(--app-hover-bg); color: var(--app-muted);">{statusLabel(item.status)}</span>
										</div>
										<p class="mt-2 break-words" style="color: var(--app-muted);">{sectionStatusMessage(itemDefinition.section, item.status)}</p>
									</li>
								{/each}
							</ul>
							<p class="mt-4 text-xs" style="color: var(--app-muted);">{t(locale, 'books.preflightTokenOpaque')}</p>
							{#if canConfirmEnable(form.enablePreflight)}
								<form method="POST" action="?/enableBook" class="mt-4">
									<input type="hidden" name="preflight_token" value={form.enablePreflight.preflight_token} />
									{#if form.enableMakeDefault}<input type="hidden" name="make_default" value="on" />{/if}
									<p class="mb-3 text-sm" style="color: var(--app-muted);">{t(locale, 'books.enableConfirmHelp')}</p>
									<button type="submit" class="min-h-11 rounded-xl px-4 py-2 text-sm font-semibold text-white" style="background-color: var(--app-accent);">{t(locale, 'books.enableConfirmSubmit')}</button>
								</form>
							{/if}
						</section>
					{/if}
				</section>
			{/if}

			{#if data.book.management_actions.includes('remove_from_registry')}
				<form method="POST" action="?/removeBook" class="mt-4 min-w-0 rounded-xl border p-3" style="border-color: var(--app-border);">
					<h3 class="font-semibold" style="color: var(--app-text);">{t(locale, 'books.unregisterTitle')}</h3>
					<p class="mt-1 text-sm" style="color: var(--app-muted);">{t(locale, 'books.unregisterHelp')}</p>
					<label class="mt-3 flex items-start gap-2 text-xs" style="color: var(--app-muted);">
						<input required type="checkbox" name="confirm_metadata_only" class="mt-1" />
						<span>{t(locale, 'books.removeMetadataConfirm')}</span>
					</label>
					<button type="submit" class="mt-3 inline-flex min-h-11 items-center rounded-lg border px-3 py-2 text-sm font-medium" style="border-color: var(--app-danger); color: var(--app-danger); background-color: var(--app-bg);">{t(locale, 'books.removeRegistryAction')}</button>
				</form>
			{/if}
		</section>
	{/if}
</main>
