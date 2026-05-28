<svelte:head>
	<title>Owner-writebeta state machine</title>
</svelte:head>

<section class="mx-auto max-w-3xl space-y-6 px-4 py-6">
	<div class="rounded-2xl border border-amber-300 bg-amber-50 p-4 text-amber-950">
		<p class="text-xs font-semibold uppercase tracking-wide">Owner-only experimental workflow</p>
		<h1 class="mt-2 text-2xl font-bold">Owner-writebeta routed state machine</h1>
		<p class="mt-2 text-sm">
			This screen documents the routed backend workflow without exposing write controls by default.
			Use only outside-git copied/restorable test books in APP_ENV=test. Real working, original,
			private, shared, or only-copy books remain blocked.
		</p>
	</div>

	<div class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
		<h2 class="text-lg font-semibold text-slate-900">State sequence</h2>
		<ol class="mt-3 list-decimal space-y-2 pl-5 text-sm text-slate-700">
			<li>Preflight: backend reports redacted pass/block reasons.</li>
			<li>Preview: CREATE/PATCH/DELETE intent is reduced to an opaque preview hash.</li>
			<li>Confirmation: exact preview hash is armed with a short-lived confirmation token.</li>
			<li>Mutation: existing write-alpha routes require old gates and the active state-machine guard.</li>
			<li>Verification/reset: read-back, audit, restore, lock release, and default-disabled reset must be recorded.</li>
			<li>Hard stop: failed verification blocks further owner-writebeta mutation until reviewed.</li>
		</ol>
	</div>

	<div class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
		<h2 class="text-lg font-semibold text-slate-900">Safety posture</h2>
		<ul class="mt-3 list-disc space-y-2 pl-5 text-sm text-slate-700">
			<li>GNUCASH_WRITES_ENABLED=false remains the default.</li>
			<li>APP_ENV=test remains required for explicit write-alpha/writebeta mutation.</li>
			<li>PATCH/DELETE are limited to state-machine/write-alpha-created disposable transactions.</li>
			<li>Amounts, account/split structure, raw paths, account names, memos, descriptions, and private evidence must not be committed or shown as evidence.</li>
			<li>This is not a public write beta, stable release, production mode, or security-audited feature.</li>
		</ul>
	</div>
</section>
