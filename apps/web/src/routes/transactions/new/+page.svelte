<script lang="ts">
	import WriteModeWarning from '$lib/components/WriteModeWarning.svelte';
	import type { Account, Book } from '$lib/api/types';
	import { DEFAULT_LOCALE, t, type Locale } from '$lib/i18n';

	let { data, form } = $props();
	let locale = $derived<Locale>(data.locale ?? DEFAULT_LOCALE);

	type PreviousPayload = {
		book_id?: string;
		date?: string;
		debit_account_id?: string;
		credit_account_id?: string;
		amount?: string;
		currency?: string;
		description?: string;
		memo?: string;
	};
	type TargetClass = 'test_copy' | 'owner_selected_target';
	type WriteSessionGate = {
		writes_enabled: boolean;
		session_armed: boolean;
		create_execution_allowed: boolean;
		create_execution_reason: string;
		allowed_create_count: number;
		target_class: TargetClass | null;
	};
	type TargetPreflightCheck = {
		id: string;
		label: string;
		status: 'pending';
		note: string;
	};
	type TargetPreflight = {
		required: true;
		status: 'not_checked';
		target_class: TargetClass | null;
		checks: TargetPreflightCheck[];
	};
	type ExecutionReadinessCheck = {
		id: string;
		label: string;
		status: 'pending';
		note: string;
	};
	type ExecutionReadiness = {
		required: true;
		status: 'not_checked';
		backup_state: 'pending';
		read_back_state: 'pending';
		audit_state: 'pending';
		reset_state: 'pending';
		probe_state: 'pending';
		checks: ExecutionReadinessCheck[];
	};
	type CreateReadinessStatus = {
		readiness_state: {
			writes_enabled: { enabled: boolean; status: 'disabled' | 'enabled_but_blocked'; redacted: true };
			session_armed: { armed: false; status: 'not_armed'; redacted: true };
			allowed_create_count: { count: 0; status: 'blocked'; redacted: true };
			target: { target_class: TargetClass | null; status: 'not_selected'; private_target_probed: false; redacted: true };
			preflight: { required: true; status: 'not_checked'; private_target_probed: false; redacted: true };
			backup: { required: true; status: 'not_checked'; backup_helper_called: false; redacted: true };
			allowed_execution: { allowed: false; status: 'blocked'; reason: string; redacted: true };
		};
	};
	type PreviewFieldErrors = Partial<Record<keyof PreviousPayload | 'book_id', string>>;

	const today = new Date().toISOString().slice(0, 10);
	const defaultWriteSessionGate: WriteSessionGate = {
		writes_enabled: false,
		session_armed: false,
		create_execution_allowed: false,
		create_execution_reason: 'GNUCASH_WRITES_ENABLED=false; write session not armed.',
		allowed_create_count: 0,
		target_class: null
	};
	const defaultTargetPreflight: TargetPreflight = {
		required: true,
		status: 'not_checked',
		target_class: null,
		checks: [
			{ id: 'target_class_selected', label: 'Target class selected', status: 'pending', note: 'Pending: target class is not selected.' },
			{ id: 'target_file_exists_readable', label: 'Target file exists/readable', status: 'pending', note: 'Pending: no private file probe was executed.' },
			{ id: 'target_outside_repo', label: 'Target is outside repo', status: 'pending', note: 'Pending: outside-repo proof is required.' },
			{ id: 'desktop_closed', label: 'GnuCash Desktop closed', status: 'pending', note: 'Pending: owner must close Desktop before mutation.' },
			{ id: 'no_concurrent_writer_lock', label: 'No concurrent writer/lock', status: 'pending', note: 'Pending: no writer/lock probe was executed.' },
			{ id: 'no_lck_lnk', label: 'No .LCK/.LNK lock', status: 'pending', note: 'Pending: lock-file probe was not run.' },
			{ id: 'no_syncthing_conflict_before', label: 'No Syncthing conflict copy before session if applicable', status: 'pending', note: 'Pending: Syncthing conflict check was not run.' },
			{ id: 'independent_backup_exists', label: 'Independent backup exists', status: 'pending', note: 'Pending: backup evidence is required before CREATE.' },
			{ id: 'restore_proof_available', label: 'Restore proof available', status: 'pending', note: 'Pending: restore proof is required before CREATE.' },
			{ id: 'reviewed_non_stale_preview', label: 'Reviewed non-stale preview', status: 'pending', note: 'Pending: current preview must be reviewed.' },
			{ id: 'exact_create_count_one', label: 'Exact CREATE count = 1', status: 'pending', note: 'Pending: first trial remains exactly one CREATE.' },
			{ id: 'reset_disabled_probes_required', label: 'Writes reset/disabled probes required after session', status: 'pending', note: 'Pending: post-session reset/probes are required.' },
			{ id: 'manual_desktop_verification_required', label: 'Manual Desktop verification required', status: 'pending', note: 'Pending: owner Desktop verification is required.' }
		]
	};
	const defaultCreateReadinessStatus: CreateReadinessStatus = {
		readiness_state: {
			writes_enabled: { enabled: false, status: 'disabled', redacted: true },
			session_armed: { armed: false, status: 'not_armed', redacted: true },
			allowed_create_count: { count: 0, status: 'blocked', redacted: true },
			target: { target_class: null, status: 'not_selected', private_target_probed: false, redacted: true },
			preflight: { required: true, status: 'not_checked', private_target_probed: false, redacted: true },
			backup: { required: true, status: 'not_checked', backup_helper_called: false, redacted: true },
			allowed_execution: { allowed: false, status: 'blocked', reason: 'GNUCASH_WRITES_ENABLED=false; write session not armed.', redacted: true }
		}
	};
	const defaultExecutionReadiness: ExecutionReadiness = {
		required: true,
		status: 'not_checked',
		backup_state: 'pending',
		read_back_state: 'pending',
		audit_state: 'pending',
		reset_state: 'pending',
		probe_state: 'pending',
		checks: [
			{ id: 'backup_plan_required', label: 'Independent backup plan required', status: 'pending', note: 'Pending: backup planning evidence is required before CREATE.' },
			{ id: 'backup_readable_copy_required', label: 'Backup readable copy proof required', status: 'pending', note: 'Pending: no backup path or copied book is opened.' },
			{ id: 'post_create_read_back_required', label: 'Post-CREATE read-back required', status: 'pending', note: 'Pending: future private read-back must prove the created transaction.' },
			{ id: 'redacted_audit_required', label: 'Redacted audit evidence required', status: 'pending', note: 'Pending: no audit execution occurs in this shell.' },
			{ id: 'writes_reset_required', label: 'Writes reset to disabled required', status: 'pending', note: 'Pending: reset proof is required after a future approved session.' },
			{ id: 'disabled_create_probe_required', label: 'Disabled CREATE probe required', status: 'pending', note: 'Pending: prove CREATE is blocked again after reset.' },
			{ id: 'disabled_validate_preflight_probe_required', label: 'Disabled validate/preflight probes required', status: 'pending', note: 'Pending: prove validate/preflight route families remain blocked or unavailable after reset.' },
			{ id: 'disabled_patch_delete_batch_probes_required', label: 'Disabled PATCH/DELETE/batch probes required', status: 'pending', note: 'Pending: prove PATCH, DELETE, and batch remain blocked.' },
			{ id: 'manual_desktop_verification_record_required', label: 'Manual Desktop verification record required', status: 'pending', note: 'Pending: owner verification remains private.' }
		]
	};
	const previous = $derived((form?.payload ?? {}) as PreviousPayload);
	const preview = $derived((form as any)?.preview);
	const writeSessionGate = $derived(((data.writeSessionGate ?? defaultWriteSessionGate) as WriteSessionGate));
	const targetPreflight = $derived(((data.targetPreflight ?? defaultTargetPreflight) as TargetPreflight));
	const executionReadiness = $derived(((data.executionReadiness ?? defaultExecutionReadiness) as ExecutionReadiness));
	const createReadinessStatus = $derived(((data.createReadinessStatus ?? defaultCreateReadinessStatus) as CreateReadinessStatus));
	const readinessState = $derived(createReadinessStatus.readiness_state);
	const fieldErrors = $derived(((form as any)?.fieldErrors ?? {}) as PreviewFieldErrors);
	const fieldErrorLinks = $derived(
		([
			{ field: 'book_id', label: 'Book', href: '#preview-book' },
			{ field: 'date', label: 'Date', href: '#preview-date' },
			{ field: 'debit_account_id', label: 'Source account', href: '#debit-account-select' },
			{ field: 'credit_account_id', label: 'Destination account', href: '#credit-account-select' },
			{ field: 'amount', label: 'Amount', href: '#preview-amount' },
			{ field: 'currency', label: 'Currency', href: '#preview-currency' },
			{ field: 'description', label: 'Description', href: '#preview-description' },
			{ field: 'memo', label: 'Memo', href: '#preview-memo' }
		] as const)
			.filter((item) => Boolean(fieldErrors[item.field]))
			.map((item) => ({ ...item, message: fieldErrors[item.field] ?? '' }))
	);
	const currentBookId = $derived(previous.book_id || String(data.activeBook?.id ?? ''));
	const selectedBook = $derived((data.books as Book[]).find((book) => String(book.id) === currentBookId) ?? data.activeBook);
	const selectableAccounts = $derived((data.accounts as Account[]).filter((account) => !account.placeholder && !account.hidden));
	let debitAccountQuery = $state('');
	let creditAccountQuery = $state('');
	let selectedDebitAccountId = $state('');
	let selectedCreditAccountId = $state('');
	let clientAccountError = $state('');
	let draftChangedAfterPreview = $state(false);
	let previewReviewed = $state(false);
	let approvalTemplateCopied = $state(false);
	const safeApprovalTemplate = `Owner approval request (redacted template)
Target book: <selected book in web UI>
CREATE count: 1
Source/debit account: <selected source account>
Destination/credit account: <selected destination account>
Amount/currency: <amount and currency>
Date: <YYYY-MM-DD>
Description: <description>
Memo: <memo or empty>
Safety checklist: preview reviewed; no stale preview; write session armed only after fresh same-context approval; target class and exact CREATE count approved; target preflight passed; backup/read-back/audit/reset/probes required; manual Desktop verification required; no PATCH, DELETE, or batch.`;
	const currentDebitAccountId = $derived(selectedDebitAccountId || previous.debit_account_id || '');
	const currentCreditAccountId = $derived(selectedCreditAccountId || previous.credit_account_id || '');
	const previewIsStale = $derived(Boolean(preview) && draftChangedAfterPreview);
	const sameAccountError = $derived(
		currentDebitAccountId && currentCreditAccountId && currentDebitAccountId === currentCreditAccountId
			? 'Source and destination accounts must be different. No write was executed.'
			: ''
	);
	const debitAccountError = $derived(clientAccountError || sameAccountError || fieldErrors.debit_account_id || '');
	const creditAccountError = $derived(clientAccountError || sameAccountError || fieldErrors.credit_account_id || '');
	const dateError = $derived(fieldErrors.date ?? '');
	const amountError = $derived(fieldErrors.amount ?? '');
	const currencyError = $derived(fieldErrors.currency ?? '');
	const bookError = $derived(fieldErrors.book_id ?? '');
	const descriptionError = $derived(fieldErrors.description ?? '');
	const memoError = $derived(fieldErrors.memo ?? '');
	const selectedDebitAccount = $derived(selectableAccounts.find((account) => account.id === currentDebitAccountId));
	const selectedCreditAccount = $derived(selectableAccounts.find((account) => account.id === currentCreditAccountId));
	const noSelectableAccounts = $derived(selectableAccounts.length === 0);

	function describedBy(...ids: Array<string | false | null | undefined>): string | undefined {
		const value = ids.filter(Boolean).join(' ');
		return value || undefined;
	}

	function normalizeAccountSearch(value: string): string {
		return value.trim().toLowerCase();
	}

	function accountMatches(account: Account, query: string): boolean {
		const normalizedQuery = normalizeAccountSearch(query);
		if (!normalizedQuery) return true;
		return [account.full_name, account.name, account.type, account.currency]
			.filter(Boolean)
			.some((value) => String(value).toLowerCase().includes(normalizedQuery));
	}

	function filteredAccounts(query: string, selectedAccountId: string): Account[] {
		const matches = selectableAccounts.filter((account) => accountMatches(account, query));
		const selected = selectableAccounts.find((account) => account.id === selectedAccountId);
		if (selected && !matches.some((account) => account.id === selected.id)) {
			return [selected, ...matches];
		}
		return matches;
	}

	const debitAccountOptions = $derived(filteredAccounts(debitAccountQuery, currentDebitAccountId));
	const creditAccountOptions = $derived(filteredAccounts(creditAccountQuery, currentCreditAccountId));

	function handleDebitAccountChange(event: Event) {
		selectedDebitAccountId = (event.currentTarget as HTMLSelectElement).value;
		clientAccountError = '';
	}

	function handleCreditAccountChange(event: Event) {
		selectedCreditAccountId = (event.currentTarget as HTMLSelectElement).value;
		clientAccountError = '';
	}

	function handleDraftChange() {
		if (!preview) return;
		draftChangedAfterPreview = true;
		previewReviewed = false;
		approvalTemplateCopied = false;
	}

	async function copySafeApprovalTemplate() {
		if (typeof navigator === 'undefined' || !navigator.clipboard) {
			approvalTemplateCopied = false;
			return;
		}
		try {
			await navigator.clipboard.writeText(safeApprovalTemplate);
			approvalTemplateCopied = true;
		} catch {
			approvalTemplateCopied = false;
		}
	}

	function handlePreviewSubmit(event: SubmitEvent) {
		const formElement = event.currentTarget as HTMLFormElement;
		const formData = new FormData(formElement);
		const debitAccountId = String(formData.get('debit_account_id') ?? '');
		const creditAccountId = String(formData.get('credit_account_id') ?? '');
		if (debitAccountId && creditAccountId && debitAccountId === creditAccountId) {
			event.preventDefault();
			clientAccountError = 'Source and destination accounts must be different. No write was executed.';
			handleDraftChange();
			return;
		}
		clientAccountError = '';
		draftChangedAfterPreview = false;
		previewReviewed = false;
		approvalTemplateCopied = false;
	}
</script>

<svelte:head>
	<title>Preview transaction — GnuCash Web Companion</title>
</svelte:head>

<main class="mx-auto max-w-5xl min-w-0 px-4 py-8">
	<div class="mb-6 flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
		<div class="min-w-0">
			<p class="text-sm font-medium uppercase tracking-wide" style="color: var(--app-accent);">{t(locale, 'writeMode.kicker')}</p>
			<h1 class="mt-1 text-3xl font-bold" style="color: var(--app-text);">Transaction entry preview</h1>
			<p class="mt-2 text-sm" style="color: var(--app-muted);">
				Owner-only browser/mobile form for validating one future CREATE. This slice is preview only; no write is executed.
			</p>
		</div>
		<a class="rounded-xl px-4 py-2 text-sm font-semibold" style="border: 1px solid var(--app-border); color: var(--app-text);" href="/transactions" aria-label="Back to transactions list; no draft is saved">Back to transactions list</a>
	</div>

	<nav id="transaction-entry-workflow-nav" class="mb-4 rounded-2xl p-4 text-sm" aria-label="Transaction entry preview workflow" aria-describedby="transaction-entry-workflow-help" style="border: 1px solid var(--app-border); background: var(--app-panel); color: var(--app-text);">
		<p class="font-semibold">Preview workflow</p>
		<p id="transaction-entry-workflow-help" class="mt-1" style="color: var(--app-muted);">
			Use these in-page jumps to keep the preview-only flow clear on mobile. Links only move within this page; they do not save a draft or execute a write.
		</p>
		<ol class="mt-3 grid min-w-0 gap-2 md:grid-cols-4">
			<li><a class="block rounded-xl px-3 py-2 font-semibold" style="border: 1px solid var(--app-border); color: var(--app-accent);" href="#preview-no-write-warning">1. Confirm no-write boundary</a></li>
			<li><a class="block rounded-xl px-3 py-2 font-semibold" style="border: 1px solid var(--app-border); color: var(--app-accent);" href="#transaction-preview-form">2. Enter details</a></li>
			<li><a class="block rounded-xl px-3 py-2 font-semibold" style="border: 1px solid var(--app-border); color: var(--app-accent);" href="#transaction-preview-form">3. Run preview</a></li>
			<li><a class="block rounded-xl px-3 py-2 font-semibold" style="border: 1px solid var(--app-border); color: var(--app-accent);" href="#normalized-preview">4. Review disabled Future Create</a></li>
		</ol>
	</nav>

	{#if form?.error}
		<div id="preview-error-summary" class="mb-4 rounded-2xl p-4 text-sm" role="alert" aria-live="assertive" aria-labelledby="preview-error-summary-title" style="border: 1px solid #fecaca; background: #fef2f2; color: #991b1b;">
			<p id="preview-error-summary-title" class="font-semibold">Preview validation failed safely</p>
			<p class="mt-1">{form.error}</p>
			<p class="mt-1 font-semibold">No CREATE/PATCH/DELETE/batch executed.</p>
			{#if fieldErrorLinks.length}
				<nav id="preview-error-jump-list" class="mt-3 rounded-xl p-3" aria-label="Preview field errors" style="border: 1px solid #fecaca; background: #fff7f7;">
					<p class="font-semibold">Jump to fields to fix:</p>
					<ul class="mt-2 space-y-1">
						{#each fieldErrorLinks as item (item.field)}
							<li><a class="break-words underline" href={item.href}>{item.label}: {item.message}</a></li>
						{/each}
					</ul>
				</nav>
			{/if}
			<p class="mt-1">Review the highlighted fields below. Raw private paths, secrets, and runtime internals are not shown.</p>
		</div>
	{/if}

	<div id="preview-no-write-warning" class="mb-4 rounded-2xl p-4 text-sm" role="status" aria-labelledby="preview-no-write-title" style="border: 1px solid #93c5fd; background: #eff6ff; color: #1e3a8a;">
		<p id="preview-no-write-title" class="font-semibold">Preview only / no write executed</p>
		<p class="mt-1">
			This page calls only POST /books/&lbrace;book_id&rbrace;/transactions/create-preview, a non-mutating backend preview endpoint.
			No CREATE, PATCH, DELETE, or batch operation is executed. A future CREATE still requires fresh owner approval,
			exact CREATE count, enabled write gates, backup/read-back/audit/reset/probes, and private verification.
		</p>
	</div>

	<section id="write-session-gate" class="mb-4 rounded-2xl p-4 text-sm" role="status" aria-labelledby="write-session-gate-title" aria-describedby="write-session-gate-summary write-session-gate-reason armed-session-requirements" style="border: 1px solid #fde68a; background: #fffbeb; color: #92400e;">
		<div class="flex min-w-0 flex-col gap-3 md:flex-row md:items-start md:justify-between">
			<div class="min-w-0">
				<p class="text-xs font-semibold uppercase tracking-wide">Preview mode</p>
				<h2 id="write-session-gate-title" class="mt-1 text-base font-semibold">Write session not armed</h2>
				<p id="write-session-gate-summary" class="mt-1">
					CREATE execution unavailable without fresh owner approval. This gate is server-rendered, redacted, and defaults off.
				</p>
				<p id="write-session-gate-reason" class="mt-1 font-semibold">{writeSessionGate.create_execution_reason}</p>
			</div>
			<div class="grid min-w-0 gap-2 text-xs sm:grid-cols-2">
				<span class="rounded-full px-3 py-1 font-semibold" style="background: #fff7ed; color: #9a3412;">writes_enabled: {String(writeSessionGate.writes_enabled)}</span>
				<span class="rounded-full px-3 py-1 font-semibold" style="background: #fff7ed; color: #9a3412;">session_armed: {String(writeSessionGate.session_armed)}</span>
				<span class="rounded-full px-3 py-1 font-semibold" style="background: #fff7ed; color: #9a3412;">create_execution_allowed: {String(writeSessionGate.create_execution_allowed)}</span>
				<span class="rounded-full px-3 py-1 font-semibold" style="background: #fff7ed; color: #9a3412;">allowed_create_count: {writeSessionGate.allowed_create_count}</span>
				<span class="rounded-full px-3 py-1 font-semibold sm:col-span-2" style="background: #fff7ed; color: #9a3412;">target_class: {writeSessionGate.target_class ?? 'required'}</span>
			</div>
		</div>
		<div id="armed-session-requirements" class="mt-4 rounded-xl p-3" aria-label="Disabled armed-session requirements" style="border: 1px solid #fbbf24; background: #fff7ed;">
			<p class="font-semibold">Armed-session requirements panel (disabled placeholder)</p>
			<ul class="mt-2 list-disc pl-5">
				<li>Target class required: test copy or owner-selected target only.</li>
				<li>Exact CREATE count required; first trial remains CREATE 1.</li>
				<li>Reviewed non-stale preview required; preview-reviewed checkbox alone is not enough.</li>
				<li>Backup, read-back, audit, reset, and disabled-write probes required; all remain pending in this shell.</li>
				<li>Manual Desktop verification required for the first UI CREATE trial.</li>
			</ul>
			<p class="mt-2 font-semibold">PATCH 0 / DELETE 0 / batch 0. Default state remains disabled/inert.</p>
		</div>
		<div id="redacted-create-readiness-state" class="mt-4 rounded-xl p-3" aria-label="Redacted read-only CREATE readiness state" style="border: 1px solid #fbbf24; background: #fff7ed;">
			<p class="font-semibold">Redacted read-only readiness state</p>
			<p class="mt-1 text-xs">Loaded from the read-only status endpoint when owner access allows it; otherwise safe defaults are used. No private target, backup path, account name, amount, memo, or transaction data is shown.</p>
			<dl class="mt-3 grid min-w-0 gap-2 text-xs md:grid-cols-2">
				<div class="rounded-lg px-3 py-2" style="background: #fffbeb;"><dt class="font-semibold">writes_enabled status</dt><dd>{readinessState.writes_enabled.status}</dd></div>
				<div class="rounded-lg px-3 py-2" style="background: #fffbeb;"><dt class="font-semibold">session_armed status</dt><dd>{readinessState.session_armed.status}</dd></div>
				<div class="rounded-lg px-3 py-2" style="background: #fffbeb;"><dt class="font-semibold">allowed_create_count status</dt><dd>{readinessState.allowed_create_count.status}; count {readinessState.allowed_create_count.count}</dd></div>
				<div class="rounded-lg px-3 py-2" style="background: #fffbeb;"><dt class="font-semibold">target status</dt><dd>{readinessState.target.status}; class {readinessState.target.target_class ?? 'redacted/unset'}</dd></div>
				<div class="rounded-lg px-3 py-2" style="background: #fffbeb;"><dt class="font-semibold">preflight status</dt><dd>{readinessState.preflight.status}; private probe {String(readinessState.preflight.private_target_probed)}</dd></div>
				<div class="rounded-lg px-3 py-2" style="background: #fffbeb;"><dt class="font-semibold">backup status</dt><dd>{readinessState.backup.status}; helper called {String(readinessState.backup.backup_helper_called)}</dd></div>
				<div class="rounded-lg px-3 py-2 md:col-span-2" style="background: #fffbeb;"><dt class="font-semibold">allowed execution status</dt><dd>{readinessState.allowed_execution.status}; allowed {String(readinessState.allowed_execution.allowed)}</dd></div>
			</dl>
		</div>
	</section>

	<section id="target-preflight-readiness" class="mb-4 rounded-2xl p-4 text-sm" role="status" aria-labelledby="target-preflight-title" aria-describedby="target-preflight-summary target-preflight-default-state target-preflight-checklist" style="border: 1px solid #c4b5fd; background: #f5f3ff; color: #4c1d95;">
		<div class="flex min-w-0 flex-col gap-3 md:flex-row md:items-start md:justify-between">
			<div class="min-w-0">
				<p class="text-xs font-semibold uppercase tracking-wide">Target preflight required</p>
				<h2 id="target-preflight-title" class="mt-1 text-base font-semibold">Target readiness not checked</h2>
				<p id="target-preflight-summary" class="mt-1">
					This is a UI/status shell only. No private target preflight, file probe, book open, backup, lock check, or write helper runs in this slice.
				</p>
			</div>
			<div class="grid min-w-0 gap-2 text-xs sm:grid-cols-2">
				<span class="rounded-full px-3 py-1 font-semibold" style="background: #ede9fe; color: #5b21b6;">target_preflight.required: {String(targetPreflight.required)}</span>
				<span class="rounded-full px-3 py-1 font-semibold" style="background: #ede9fe; color: #5b21b6;">target_preflight.status: {targetPreflight.status}</span>
				<span class="rounded-full px-3 py-1 font-semibold sm:col-span-2" style="background: #ede9fe; color: #5b21b6;">target_preflight.target_class: {targetPreflight.target_class ?? 'pending'}</span>
			</div>
		</div>
		<p id="target-preflight-default-state" class="mt-3 font-semibold">Default state: all target readiness checks are pending / not checked / not armed.</p>
		<ul id="target-preflight-checklist" class="mt-3 grid min-w-0 gap-2 md:grid-cols-2" aria-label="Future target preflight checklist">
			{#each targetPreflight.checks as check (check.id)}
				<li class="min-w-0 rounded-xl p-3" data-preflight-check={check.id} data-preflight-status={check.status} style="border: 1px solid #ddd6fe; background: #faf5ff;">
					<div class="flex min-w-0 items-start justify-between gap-3">
						<span class="font-semibold">{check.label}</span>
						<span class="shrink-0 rounded-full px-2 py-0.5 text-xs font-semibold" style="background: #fffbeb; color: #92400e;">{check.status}</span>
					</div>
					<p class="mt-1 text-xs">{check.note}</p>
				</li>
			{/each}
		</ul>
		<p class="mt-3 font-semibold">Future Create remains disabled until target preflight is passed in a fresh owner-approved bounded session.</p>
	</section>

	<section id="execution-readiness-shell" class="mb-4 rounded-2xl p-4 text-sm" role="status" aria-labelledby="execution-readiness-title" aria-describedby="execution-readiness-summary execution-readiness-default-state execution-readiness-checklist" style="border: 1px solid #99f6e4; background: #f0fdfa; color: #134e4a;">
		<div class="flex min-w-0 flex-col gap-3 md:flex-row md:items-start md:justify-between">
			<div class="min-w-0">
				<p class="text-xs font-semibold uppercase tracking-wide">Backup/read-back/audit/reset/probes required</p>
				<h2 id="execution-readiness-title" class="mt-1 text-base font-semibold">Execution readiness not checked</h2>
				<p id="execution-readiness-summary" class="mt-1">
					This is a non-mutating readiness shell only. No backup is created, no backup/read-back/audit is executed, no reset or probe runs, and no GnuCash book is opened.
				</p>
			</div>
			<div class="grid min-w-0 gap-2 text-xs sm:grid-cols-2">
				<span class="rounded-full px-3 py-1 font-semibold" style="background: #ccfbf1; color: #115e59;">execution_readiness.required: {String(executionReadiness.required)}</span>
				<span class="rounded-full px-3 py-1 font-semibold" style="background: #ccfbf1; color: #115e59;">execution_readiness.status: {executionReadiness.status}</span>
				<span class="rounded-full px-3 py-1 font-semibold" style="background: #ccfbf1; color: #115e59;">backup_state: {executionReadiness.backup_state}</span>
				<span class="rounded-full px-3 py-1 font-semibold" style="background: #ccfbf1; color: #115e59;">read_back_state: {executionReadiness.read_back_state}</span>
				<span class="rounded-full px-3 py-1 font-semibold" style="background: #ccfbf1; color: #115e59;">audit_state: {executionReadiness.audit_state}</span>
				<span class="rounded-full px-3 py-1 font-semibold" style="background: #ccfbf1; color: #115e59;">reset_state: {executionReadiness.reset_state}</span>
				<span class="rounded-full px-3 py-1 font-semibold sm:col-span-2" style="background: #ccfbf1; color: #115e59;">probe_state: {executionReadiness.probe_state}</span>
			</div>
		</div>
		<p id="execution-readiness-default-state" class="mt-3 font-semibold">Default state: backup, read-back, audit, reset, and probe readiness are pending / not checked / not armed.</p>
		<ul id="execution-readiness-checklist" class="mt-3 grid min-w-0 gap-2 md:grid-cols-2" aria-label="Future execution readiness checklist">
			{#each executionReadiness.checks as check (check.id)}
				<li class="min-w-0 rounded-xl p-3" data-execution-readiness-check={check.id} data-execution-readiness-status={check.status} style="border: 1px solid #99f6e4; background: #ecfeff;">
					<div class="flex min-w-0 items-start justify-between gap-3">
						<span class="font-semibold">{check.label}</span>
						<span class="shrink-0 rounded-full px-2 py-0.5 text-xs font-semibold" style="background: #fffbeb; color: #92400e;">{check.status}</span>
					</div>
					<p class="mt-1 text-xs">{check.note}</p>
				</li>
			{/each}
		</ul>
		<p class="mt-3 font-semibold">Future Create remains disabled until backup/read-back/audit/reset/probes readiness is completed in a fresh owner-approved bounded session.</p>
	</section>

	<div class="mb-4">
		<WriteModeWarning {locale} compact />
	</div>

	<form id="transaction-preview-form" method="POST" onsubmit={handlePreviewSubmit} oninput={handleDraftChange} onchange={handleDraftChange} aria-describedby={describedBy('preview-no-write-warning', 'write-session-gate', 'target-preflight-readiness', 'execution-readiness-shell', 'preview-create-disabled-explanation', form?.error && 'preview-error-summary')} class="min-w-0 space-y-5 rounded-2xl p-5" style="background: var(--app-panel); border: 1px solid var(--app-border); box-shadow: 0 1px 3px var(--app-panel-shadow);">
		<div class="min-w-0 text-sm font-medium" style="color: var(--app-text);">
			<label for="preview-book">Book</label>
			<select id="preview-book" name="book_id" aria-invalid={bookError ? 'true' : undefined} aria-describedby={describedBy('book-help', 'preview-no-write-warning', bookError && 'preview-book-error')} class="mt-1 w-full min-w-0 rounded-xl px-3 py-2" style="background: var(--app-bg); color: var(--app-text); border: 1px solid var(--app-border);">
				{#each data.books as book}
					<option value={book.id} selected={String(book.id) === currentBookId}>{book.name}</option>
				{/each}
			</select>
			<p id="book-help" class="mt-1 text-xs" style="color: var(--app-muted);">Select the book context for this non-mutating preview only.</p>
			{#if bookError}
				<p id="preview-book-error" class="mt-1 text-xs" style="color: #dc2626;">{bookError}</p>
			{/if}
		</div>

		<div class="grid gap-4 md:grid-cols-2">
			<div class="min-w-0 text-sm font-medium" style="color: var(--app-text);">
				<label for="preview-date">Date</label>
				<input id="preview-date" name="date" type="date" required value={previous.date ?? today} aria-invalid={dateError ? 'true' : undefined} aria-describedby={describedBy('date-help', dateError && 'preview-date-error')} class="mt-1 w-full min-w-0 rounded-xl px-3 py-2" style="background: var(--app-bg); color: var(--app-text); border: 1px solid var(--app-border);" />
				<p id="date-help" class="mt-1 text-xs" style="color: var(--app-muted);">Use an explicit calendar date; the preview validates the submitted date before any future approval step.</p>
				{#if dateError}
					<p id="preview-date-error" class="mt-1 text-xs" style="color: #dc2626;">{dateError}</p>
				{/if}
			</div>
			<div class="min-w-0 text-sm font-medium" style="color: var(--app-text);">
				<label for="preview-currency">Currency</label>
				<input id="preview-currency" name="currency" maxlength="3" pattern="[A-Za-z]{3}" autocomplete="off" spellcheck="false" required value={previous.currency ?? data.activeBook?.base_currency ?? 'SEK'} aria-invalid={currencyError ? 'true' : undefined} aria-describedby={describedBy('currency-help', currencyError && 'preview-currency-error')} class="mt-1 w-full min-w-0 rounded-xl px-3 py-2 uppercase" style="background: var(--app-bg); color: var(--app-text); border: 1px solid var(--app-border);" />
				<p id="currency-help" class="mt-1 text-xs" style="color: var(--app-muted);">Use a three-letter currency code; no currency conversion is performed.</p>
				{#if currencyError}
					<p id="preview-currency-error" class="mt-1 text-xs" style="color: #dc2626;">{currencyError}</p>
				{/if}
			</div>
		</div>

		<div class="min-w-0 text-sm font-medium" style="color: var(--app-text);">
			<label for="preview-description">Description</label>
			<input id="preview-description" name="description" required value={previous.description ?? ''} aria-invalid={descriptionError ? 'true' : undefined} aria-describedby={describedBy('description-help', descriptionError && 'preview-description-error')} class="mt-1 w-full min-w-0 rounded-xl px-3 py-2" style="background: var(--app-bg); color: var(--app-text); border: 1px solid var(--app-border);" />
			<p id="description-help" class="mt-1 text-xs" style="color: var(--app-muted);">Required local description for the normalized preview; tracked/GitHub reports must remain redacted.</p>
			{#if descriptionError}
				<p id="preview-description-error" class="mt-1 text-xs" style="color: #dc2626;">{descriptionError}</p>
			{/if}
		</div>

		<div class="grid gap-4 md:grid-cols-2">
			<div class="min-w-0 text-sm font-medium" style="color: var(--app-text);">
				<label for="preview-amount">Amount</label>
				<input id="preview-amount" name="amount" type="text" inputmode="decimal" pattern="[0-9]+(\.[0-9]+)?" required placeholder="320.00" value={previous.amount ?? ''} aria-invalid={amountError ? 'true' : undefined} aria-describedby={describedBy('amount-help', amountError && 'preview-amount-error')} class="mt-1 w-full min-w-0 rounded-xl px-3 py-2" style="background: var(--app-bg); color: var(--app-text); border: 1px solid var(--app-border);" />
				<p id="amount-help" class="mt-1 text-xs" style="color: var(--app-muted);">Use a positive decimal string such as 320.00; zero is rejected by preview validation.</p>
				{#if amountError}
					<p id="preview-amount-error" class="mt-1 text-xs" style="color: #dc2626;">{amountError}</p>
				{/if}
			</div>
			<div class="min-w-0 text-sm font-medium" style="color: var(--app-text);">
				<label for="preview-memo">Memo (optional)</label>
				<input id="preview-memo" name="memo" placeholder="Optional metadata only" value={previous.memo ?? ''} aria-invalid={memoError ? 'true' : undefined} aria-describedby={describedBy('memo-help', memoError && 'preview-memo-error')} class="mt-1 w-full min-w-0 rounded-xl px-3 py-2" style="background: var(--app-bg); color: var(--app-text); border: 1px solid var(--app-border);" />
				<p id="memo-help" class="mt-1 text-xs" style="color: var(--app-muted);">Optional metadata shown in preview only; this slice does not write it.</p>
				{#if memoError}
					<p id="preview-memo-error" class="mt-1 text-xs" style="color: #dc2626;">{memoError}</p>
				{/if}
			</div>
		</div>

		<section class="min-w-0 rounded-2xl border p-4" aria-labelledby="account-selector-title" aria-describedby="account-selector-help preview-no-write-warning" style="border-color: var(--app-border); background: var(--app-bg);">
			<div class="mb-4">
				<h2 id="account-selector-title" class="text-base font-semibold" style="color: var(--app-text);">Account selectors</h2>
				<p id="account-selector-help" class="mt-1 text-xs" style="color: var(--app-muted);">
					Search filters the account list by full account path, account name, type, or currency. The submitted value remains the selected account id; free-text is never submitted as the final account reference. Placeholder/hidden accounts are excluded.
				</p>
				{#if noSelectableAccounts}
					<p id="no-selectable-accounts-warning" class="mt-2 rounded-xl p-3 text-xs" role="status" style="border: 1px solid #fde68a; background: #fffbeb; color: #92400e;">
						No selectable accounts are available for this book. Choose another book or add non-placeholder accounts in GnuCash Desktop, then run preview again. No write was executed.
					</p>
				{/if}
			</div>

			<div class="grid min-w-0 gap-4 md:grid-cols-2">
				<div class="min-w-0">
					<label class="block text-sm font-medium" style="color: var(--app-text);" for="debit-account-search">Search source account</label>
					<input id="debit-account-search" data-account-filter="debit" type="search" bind:value={debitAccountQuery} autocomplete="off" aria-describedby="debit-account-search-help debit-account-count account-selector-help" placeholder="Filter by full account path" class="mt-1 w-full min-w-0 rounded-xl px-3 py-2" style="background: var(--app-panel); color: var(--app-text); border: 1px solid var(--app-border);" />
					<p id="debit-account-search-help" class="mt-1 text-xs" style="color: var(--app-muted);">Filters visible source accounts only; it is not submitted as account text.</p>
					<p id="debit-account-count" class="mt-1 text-xs" style="color: var(--app-muted);">Showing {debitAccountOptions.length} of {selectableAccounts.length} visible selectable accounts.</p>
					<label class="mt-3 block text-sm font-medium" style="color: var(--app-text);" for="debit-account-select">Debit/source account</label>
					<select id="debit-account-select" name="debit_account_id" required value={currentDebitAccountId} onchange={handleDebitAccountChange} aria-invalid={debitAccountError ? 'true' : undefined} aria-describedby={describedBy('debit-account-help', 'debit-account-count', 'debit-account-selected', 'preview-no-write-warning', debitAccountError && 'debit-account-error')} class="mt-1 w-full min-w-0 max-w-full rounded-xl px-3 py-2" style="background: var(--app-panel); color: var(--app-text); border: 1px solid var(--app-border);">
						<option value="">Select source account</option>
						{#each debitAccountOptions as account (account.id)}
							<option value={account.id} selected={account.id === currentDebitAccountId} disabled={Boolean(currentCreditAccountId && account.id === currentCreditAccountId && account.id !== currentDebitAccountId)}>{account.full_name} · {account.currency}</option>
						{/each}
					</select>
					<p id="debit-account-help" class="mt-1 text-xs" style="color: var(--app-muted);">Source must be a selectable account and cannot match destination.</p>
					<p id="debit-account-selected" class="mt-1 break-words text-xs" style="color: var(--app-muted);">
						Selected source: {selectedDebitAccount?.full_name ?? 'none'}{#if selectedDebitAccount} · account type {selectedDebitAccount?.type} · {selectedDebitAccount?.currency}{/if}
					</p>
					{#if debitAccountError}
						<p id="debit-account-error" class="mt-1 text-xs" style="color: #dc2626;">{debitAccountError}</p>
					{/if}
				</div>

				<div class="min-w-0">
					<label class="block text-sm font-medium" style="color: var(--app-text);" for="credit-account-search">Search destination account</label>
					<input id="credit-account-search" data-account-filter="credit" type="search" bind:value={creditAccountQuery} autocomplete="off" aria-describedby="credit-account-search-help credit-account-count account-selector-help" placeholder="Filter by full account path" class="mt-1 w-full min-w-0 rounded-xl px-3 py-2" style="background: var(--app-panel); color: var(--app-text); border: 1px solid var(--app-border);" />
					<p id="credit-account-search-help" class="mt-1 text-xs" style="color: var(--app-muted);">Filters visible destination accounts only; it is not submitted as account text.</p>
					<p id="credit-account-count" class="mt-1 text-xs" style="color: var(--app-muted);">Showing {creditAccountOptions.length} of {selectableAccounts.length} visible selectable accounts.</p>
					<label class="mt-3 block text-sm font-medium" style="color: var(--app-text);" for="credit-account-select">Credit/destination account</label>
					<select id="credit-account-select" name="credit_account_id" required value={currentCreditAccountId} onchange={handleCreditAccountChange} aria-invalid={creditAccountError ? 'true' : undefined} aria-describedby={describedBy('credit-account-help', 'credit-account-count', 'credit-account-selected', 'preview-no-write-warning', creditAccountError && 'credit-account-error')} class="mt-1 w-full min-w-0 max-w-full rounded-xl px-3 py-2" style="background: var(--app-panel); color: var(--app-text); border: 1px solid var(--app-border);">
						<option value="">Select destination account</option>
						{#each creditAccountOptions as account (account.id)}
							<option value={account.id} selected={account.id === currentCreditAccountId} disabled={Boolean(currentDebitAccountId && account.id === currentDebitAccountId && account.id !== currentCreditAccountId)}>{account.full_name} · {account.currency}</option>
						{/each}
					</select>
					<p id="credit-account-help" class="mt-1 text-xs" style="color: var(--app-muted);">Destination must be a selectable account and cannot match source.</p>
					<p id="credit-account-selected" class="mt-1 break-words text-xs" style="color: var(--app-muted);">
						Selected destination: {selectedCreditAccount?.full_name ?? 'none'}{#if selectedCreditAccount} · account type {selectedCreditAccount?.type} · {selectedCreditAccount?.currency}{/if}
					</p>
					{#if creditAccountError}
						<p id="credit-account-error" class="mt-1 text-xs" style="color: #dc2626;">{creditAccountError}</p>
					{/if}
				</div>
			</div>
		</section>

		<div class="flex min-w-0 flex-col gap-3 md:flex-row md:items-center md:justify-between">
			<p id="preview-create-disabled-explanation" class="text-sm" style="color: var(--app-muted);">Create/Submit mutation action is intentionally disabled: preview mode is active, write session is not armed, target readiness is not checked, backup/read-back/audit/reset/probes readiness is not checked, and CREATE execution is unavailable without fresh owner approval; only the preview action is available.</p>
			<div class="flex min-w-0 flex-col gap-3 sm:flex-row">
				<button formaction="?/preview" formnovalidate class="rounded-xl px-4 py-2 font-semibold" style="border: 1px solid var(--app-border); color: var(--app-text);" type="submit">Preview transaction</button>
				<button class="cursor-not-allowed rounded-xl px-4 py-2 font-semibold text-white opacity-60" style="background: #6b7280;" type="button" disabled aria-describedby="preview-create-disabled-explanation preview-no-write-warning write-session-gate target-preflight-readiness execution-readiness-shell">Create disabled</button>
			</div>
		</div>
	</form>

	{#if previewIsStale}
		<div id="preview-stale-warning" class="mt-6 rounded-2xl p-4 text-sm" role="status" aria-live="polite" style="border: 1px solid #f59e0b; background: #fffbeb; color: #92400e;">
			<p class="font-semibold">Draft changed after preview</p>
			<p class="mt-1">
				Run Preview transaction again before any future approval step. The previous preview remains visible for comparison,
				but it is stale and cannot support a future owner-approved CREATE. No write was executed.
			</p>
		</div>
	{/if}

	{#if preview}
		<section id="normalized-preview" class="mt-6 min-w-0 rounded-2xl p-5" aria-label="Transaction preview" aria-describedby={describedBy('preview-create-disabled-explanation', 'preview-no-write-warning', 'write-session-gate', 'target-preflight-readiness', 'execution-readiness-shell', previewIsStale && 'preview-stale-warning')} style="background: var(--app-panel); border: 1px solid var(--app-border);">
			<div class="flex min-w-0 flex-col gap-2 md:flex-row md:items-start md:justify-between">
				<div class="min-w-0">
					<h2 class="text-xl font-semibold" style="color: var(--app-text);">Normalized preview</h2>
					<p class="mt-1 text-sm" style="color: var(--app-muted);">Preview only / no write executed. Create remains disabled in this slice.</p>
				</div>
				<span class="rounded-full px-3 py-1 text-xs font-semibold" style="background: #dcfce7; color: #166534;">no mutation</span>
			</div>

			<section id="preview-confirmation-shell" class="mt-4 min-w-0 rounded-2xl border p-4" aria-labelledby="preview-confirmation-shell-title" aria-describedby="preview-confirmation-shell-help preview-create-disabled-explanation" style="border-color: var(--app-border); background: var(--app-bg);">
				<div class="flex min-w-0 flex-col gap-4 md:flex-row md:items-start md:justify-between">
					<div class="min-w-0">
						<h3 id="preview-confirmation-shell-title" class="text-base font-semibold" style="color: var(--app-text);">Future confirmation shell</h3>
						<p id="preview-confirmation-shell-help" class="mt-1 text-sm" style="color: var(--app-muted);">
							Ready for future owner-approved CREATE review after fresh same-context approval only. This shell is local and non-mutating;
							the final Create control remains disabled in this slice.
						</p>
					</div>
					<a id="clear-preview-link" class="rounded-xl px-4 py-2 text-sm font-semibold" style="border: 1px solid var(--app-border); color: var(--app-text);" href="/transactions/new">Clear preview / start over</a>
				</div>
				<div class="mt-4 rounded-xl p-3 text-sm" style="border: 1px solid #fbbf24; background: #fff7ed; color: #92400e;">
					<p class="font-semibold">CREATE readiness gate: blocked</p>
					<ul id="future-create-readiness-list" class="mt-2 list-disc pl-5">
						<li>Write session not armed: session_armed = {String(writeSessionGate.session_armed)}.</li>
						<li>CREATE execution allowed: {String(writeSessionGate.create_execution_allowed)}.</li>
						<li>Allowed CREATE count: {writeSessionGate.allowed_create_count}; first approved trial must be exactly 1.</li>
						<li>Target class is required before any future CREATE.</li>
						<li>Target preflight status: {targetPreflight.status}; every target check is pending by default.</li>
						<li>Execution readiness status: {executionReadiness.status}; backup/read-back/audit/reset/probes states remain {executionReadiness.backup_state}/{executionReadiness.read_back_state}/{executionReadiness.audit_state}/{executionReadiness.reset_state}/{executionReadiness.probe_state}.</li>
						<li>Preview-reviewed checkbox alone is not enough; the preview must also be current, non-stale, owner-approved, target-preflight-passed, backed up, read back, audited, reset, probed, and manually verified in Desktop.</li>
					</ul>
				</div>
				<div class="mt-4 flex min-w-0 flex-col gap-3 md:flex-row md:items-center md:justify-between">
					<label class="flex min-w-0 items-start gap-2 text-sm" style="color: var(--app-text);" for="preview-reviewed-confirmation">
						<input id="preview-reviewed-confirmation" type="checkbox" bind:checked={previewReviewed} disabled={previewIsStale} aria-describedby="preview-reviewed-status preview-confirmation-shell-help" class="mt-1" />
						<span>I reviewed this local preview; no write is available from this checkbox.</span>
					</label>
					<button id="future-create-disabled" class="cursor-not-allowed rounded-xl px-4 py-2 font-semibold text-white opacity-60" style="background: #6b7280;" type="button" disabled aria-describedby="preview-create-disabled-explanation preview-no-write-warning write-session-gate target-preflight-readiness execution-readiness-shell preview-reviewed-status">Future Create disabled</button>
				</div>
				<p id="preview-reviewed-status" class="mt-3 text-sm" style="color: var(--app-muted);">
					{#if previewIsStale}
						Preview is stale because the draft changed. Run Preview transaction again before any future approval step.
					{:else if previewReviewed}
						Preview reviewed locally, but preview-reviewed checkbox alone is not enough. Future owner-approved CREATE still requires a fresh approval prompt, an armed write session, exact count, target preflight, backup/read-back/audit/reset/probes including disabled validate/preflight probes, and private verification.
					{:else}
						Review the normalized fields below. Future CREATE remains disabled and cannot be executed from this page state.
					{/if}
				</p>
			</section>

			<section id="approval-packet" class="mt-4 min-w-0 rounded-2xl border p-4" aria-labelledby="approval-packet-title" aria-describedby="approval-packet-help approval-packet-copy-note preview-create-disabled-explanation" style="border-color: var(--app-border); background: var(--app-bg);">
				<div class="flex min-w-0 flex-col gap-3 md:flex-row md:items-start md:justify-between">
					<div class="min-w-0">
						<h3 id="approval-packet-title" class="text-base font-semibold" style="color: var(--app-text);">Approval packet (no-write)</h3>
						<p id="approval-packet-help" class="mt-1 text-sm" style="color: var(--app-muted);">
							This panel shows exactly what a future same-context owner-approved CREATE would need. It is review-only;
							no approval is recorded, no write path exists here, and Future Create remains disabled.
						</p>
					</div>
					<button id="copy-approval-template" class="rounded-xl px-4 py-2 text-sm font-semibold" style="border: 1px solid var(--app-border); color: var(--app-text);" type="button" onclick={copySafeApprovalTemplate} aria-describedby="approval-packet-copy-note">
						Copy redacted approval template
					</button>
				</div>
				<dl class="mt-4 grid min-w-0 gap-3 md:grid-cols-2">
					<div class="min-w-0"><dt class="text-xs uppercase" style="color: var(--app-muted);">Target book</dt><dd class="break-words" style="color: var(--app-text);">{selectedBook?.name ?? 'selected book'}</dd></div>
					<div class="min-w-0"><dt class="text-xs uppercase" style="color: var(--app-muted);">Future CREATE count</dt><dd class="break-words" style="color: var(--app-text);">1</dd></div>
					<div class="min-w-0"><dt class="text-xs uppercase" style="color: var(--app-muted);">Source/debit account</dt><dd class="break-words" style="color: var(--app-text);">{preview.debit_account.full_name}</dd></div>
					<div class="min-w-0"><dt class="text-xs uppercase" style="color: var(--app-muted);">Destination/credit account</dt><dd class="break-words" style="color: var(--app-text);">{preview.credit_account.full_name}</dd></div>
					<div class="min-w-0"><dt class="text-xs uppercase" style="color: var(--app-muted);">Amount/currency</dt><dd class="break-words" style="color: var(--app-text);">{preview.amount} {preview.currency}</dd></div>
					<div class="min-w-0"><dt class="text-xs uppercase" style="color: var(--app-muted);">Date</dt><dd class="break-words" style="color: var(--app-text);">{preview.date}</dd></div>
					<div class="min-w-0"><dt class="text-xs uppercase" style="color: var(--app-muted);">Description</dt><dd class="break-words" style="color: var(--app-text);">{preview.description}</dd></div>
					<div class="min-w-0"><dt class="text-xs uppercase" style="color: var(--app-muted);">Memo</dt><dd class="break-words" style="color: var(--app-text);">{preview.memo || '—'}</dd></div>
				</dl>
				<div class="mt-4 rounded-xl p-3 text-sm" style="border: 1px solid #fde68a; background: #fffbeb; color: #92400e;">
					<p class="font-semibold">Safety checklist before any future CREATE</p>
					<ul id="approval-packet-safety-checklist" class="mt-2 list-disc pl-5">
						<li>Fresh same-context owner approval with exact CREATE count = 1.</li>
						<li>Write session must be armed and target class/preflight must pass before CREATE is reachable.</li>
						<li>Preview must be current, reviewed, and not stale.</li>
						<li>Write gates must be explicitly enabled only for an approved run; defaults stay disabled.</li>
						<li>Backup, read-back, audit, reset, disabled-write probes for validate/preflight/CREATE/PATCH/DELETE/batch, and manual Desktop verification are required for any future mutation.</li>
						<li>DELETE, batch, and balance-affecting PATCH remain forbidden.</li>
					</ul>
				</div>
				<p id="approval-packet-copy-note" class="mt-3 text-sm" style="color: var(--app-muted);">
					{#if approvalTemplateCopied}
						Redacted placeholder template copied. Fill private details only in an owner-private context, not GitHub or tracked reports.
					{:else}
						The copy button uses placeholders only; it does not copy account names, description, memo, amount, GUIDs, book paths, screenshots, or secrets.
					{/if}
				</p>
				<pre class="mt-3 max-w-full overflow-x-auto whitespace-pre-wrap rounded-xl p-3 text-xs" style="background: var(--app-panel); color: var(--app-muted); border: 1px solid var(--app-border);">{safeApprovalTemplate}</pre>
			</section>

			<dl class="mt-4 grid min-w-0 gap-3 md:grid-cols-2">
				<div class="min-w-0"><dt class="text-xs uppercase" style="color: var(--app-muted);">preview_only</dt><dd class="break-words" style="color: var(--app-text);">{String(preview.preview_only)}</dd></div>
				<div class="min-w-0"><dt class="text-xs uppercase" style="color: var(--app-muted);">create_count</dt><dd class="break-words" style="color: var(--app-text);">{preview.create_count}</dd></div>
				<div class="min-w-0"><dt class="text-xs uppercase" style="color: var(--app-muted);">Date</dt><dd class="break-words" style="color: var(--app-text);">{preview.date}</dd></div>
				<div class="min-w-0"><dt class="text-xs uppercase" style="color: var(--app-muted);">Amount + currency</dt><dd class="break-words" style="color: var(--app-text);">{preview.amount} {preview.currency}</dd></div>
				<div class="min-w-0"><dt class="text-xs uppercase" style="color: var(--app-muted);">Source/debit account</dt><dd class="break-words" style="color: var(--app-text);">{preview.debit_account.full_name}</dd></div>
				<div class="min-w-0"><dt class="text-xs uppercase" style="color: var(--app-muted);">Destination/credit account</dt><dd class="break-words" style="color: var(--app-text);">{preview.credit_account.full_name}</dd></div>
				<div class="min-w-0"><dt class="text-xs uppercase" style="color: var(--app-muted);">Description</dt><dd class="break-words" style="color: var(--app-text);">{preview.description}</dd></div>
				<div class="min-w-0"><dt class="text-xs uppercase" style="color: var(--app-muted);">Memo</dt><dd class="break-words" style="color: var(--app-text);">{preview.memo || '—'}</dd></div>
			</dl>
			<p class="mt-4 text-sm font-semibold" style="color: #92400e;">Create remains disabled in this slice.</p>

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
