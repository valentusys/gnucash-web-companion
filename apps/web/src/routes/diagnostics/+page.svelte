<script lang="ts">
	import ThemeSwitcher from '$lib/components/ThemeSwitcher.svelte';
	import type { FirstRunCheck, HealthPayload } from '$lib/api/types';

	let { data }: { data: { diagnostics: HealthPayload | null; apiReachable: boolean; errorMessage: string | null } } = $props();
	const checkLabels: Record<string, string> = {
		jwt_secret: 'JWT secret',
		admin_bootstrap: 'Admin bootstrap',
		default_book: 'Default book',
		cors: 'CORS posture',
		write_mode: 'Write mode'
	};
	let diagnostics = $derived(data.diagnostics);
	let firstRun = $derived(diagnostics?.first_run ?? null);
	let checks = $derived(firstRun ? Object.entries(firstRun.checks) : []);

	function badgeClass(status: FirstRunCheck['status']): string {
		if (status === 'ok') return 'border-green-500/40 bg-green-500/10 text-green-700 dark:text-green-300';
		if (status === 'warning') return 'border-yellow-500/40 bg-yellow-500/10 text-yellow-700 dark:text-yellow-300';
		return 'border-red-500/40 bg-red-500/10 text-red-700 dark:text-red-300';
	}
</script>

<main class="min-h-screen px-4 py-6 md:py-10" style="background-color: var(--app-bg); color: var(--app-text);">
	<div class="mx-auto flex max-w-5xl items-start justify-between gap-4">
		<div>
			<p class="text-sm font-semibold uppercase tracking-wide" style="color: var(--app-accent);">Public read-only beta</p>
			<h1 class="mt-2 text-3xl font-bold">First-run diagnostics</h1>
			<p class="mt-3 max-w-3xl" style="color: var(--app-muted);">
				Safe setup checks for external testers. This page shows booleans, status labels, and next actions only;
				it does not expose book paths, account names, amounts, memos, exports, screenshots, or secrets.
			</p>
		</div>
		<ThemeSwitcher />
	</div>

	<section class="mx-auto mt-6 max-w-5xl rounded-2xl border p-4 shadow-sm" style="border-color: var(--app-border); background: var(--app-panel);">
		{#if !data.apiReachable || !diagnostics}
			<div class="rounded-xl border border-red-500/40 bg-red-500/10 p-4">
				<h2 class="text-lg font-semibold">API diagnostics unavailable</h2>
				<p class="mt-2 text-sm" style="color: var(--app-muted);">{data.errorMessage}</p>
				<p class="mt-3 text-sm">Check that the API container is running, then reload this page. Do not paste logs that contain private paths or financial data into public issues.</p>
			</div>
		{:else}
			<div class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
				<div>
					<h2 class="text-xl font-semibold">Service status: {diagnostics.status}</h2>
					<p class="text-sm" style="color: var(--app-muted);">Service: {diagnostics.service}</p>
				</div>
				<a class="rounded-xl border px-4 py-2 text-sm font-semibold hover:underline" style="border-color: var(--app-border); color: var(--app-accent);" href="/login">Go to login</a>
			</div>

			{#if firstRun}
				<div class="mt-5 rounded-xl border p-4" style="border-color: var(--app-border);">
					<h3 class="font-semibold">{firstRun.summary}</h3>
					{#if firstRun.action_required.length > 0}
						<p class="mt-2 text-sm" style="color: var(--app-muted);">Action required: {firstRun.action_required.join(', ')}</p>
					{:else}
						<p class="mt-2 text-sm" style="color: var(--app-muted);">No required first-run actions detected.</p>
					{/if}
				</div>

				<div class="mt-5 grid gap-4 md:grid-cols-2">
					{#each checks as [key, check]}
						<article class="rounded-xl border p-4" style="border-color: var(--app-border);">
							<div class="flex items-center justify-between gap-3">
								<h3 class="font-semibold">{checkLabels[key] ?? key}</h3>
								<span class={`rounded-full border px-2 py-1 text-xs font-semibold ${badgeClass(check.status)}`}>{check.status}</span>
							</div>
							<p class="mt-3 text-sm" style="color: var(--app-muted);">{check.message}</p>
							{#if check.safe_next_actions?.length}
								<ul class="mt-3 list-disc space-y-1 pl-5 text-sm">
									{#each check.safe_next_actions as action}
										<li>{action}</li>
									{/each}
								</ul>
							{/if}
						</article>
					{/each}
				</div>
			{/if}

			{#if diagnostics.warnings.length > 0}
				<div class="mt-5 rounded-xl border border-yellow-500/40 bg-yellow-500/10 p-4">
					<h3 class="font-semibold">Warnings</h3>
					<ul class="mt-2 list-disc space-y-1 pl-5 text-sm">
						{#each diagnostics.warnings as warning}
							<li>{warning}</li>
						{/each}
					</ul>
				</div>
			{/if}
		{/if}
	</section>

	<section class="mx-auto mt-6 max-w-5xl rounded-2xl border p-4 text-sm" style="border-color: var(--app-border); background: var(--app-panel); color: var(--app-muted);">
		<strong style="color: var(--app-text);">Privacy boundary:</strong> share only these status labels and messages in public issues. Never upload a GnuCash book, app DB, backup, CSV export, screenshot, .env, token, private path, account name, memo, description, or amount.
	</section>
</main>
