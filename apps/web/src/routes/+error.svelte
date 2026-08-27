<script lang="ts">
	import { page } from '$app/state';
	import ErrorState from '$lib/components/ErrorState.svelte';
	import { DEFAULT_LOCALE, t, type Locale } from '$lib/i18n';

	let locale = $derived<Locale>(page.data.locale ?? DEFAULT_LOCALE);
	const errorTitle = $derived(
		page.status === 403
			? t(locale, 'error.forbiddenTitle')
			: page.status === 404
				? t(locale, 'error.notFoundTitle')
				: page.status >= 500
					? t(locale, 'error.serviceTitle')
					: t(locale, 'error.genericTitle')
	);
</script>

<svelte:head>
	<title>{errorTitle} — GnuCash Web Companion</title>
</svelte:head>

<main class="mx-auto flex min-h-[70vh] max-w-3xl flex-col justify-center px-4 py-12">
	<ErrorState
		statusCode={page.status}
		title={errorTitle}
		{locale}
		retryHref={page.url.pathname + page.url.search}
		backHref={page.status === 403 || page.status === 503 ? '/books' : '/dashboard'}
		retryLabel={t(locale, 'error.retryPage')}
		backLabel={page.status === 403 || page.status === 503 ? t(locale, 'error.reviewBooks') : t(locale, 'error.backDashboard')}
	>
		{#if page.status >= 500}
			<a
				href="/diagnostics"
				aria-label={t(locale, 'error.openDiagnostics')}
				class="rounded-xl border px-4 py-2 text-sm font-semibold"
				style="border-color: var(--app-border); color: var(--app-text);"
			>
				{t(locale, 'error.openDiagnostics')}
			</a>
		{/if}
	</ErrorState>
</main>
