<script lang="ts">
	import { page } from '$app/state';
	import ErrorState from '$lib/components/ErrorState.svelte';
	import { DEFAULT_LOCALE, t, type Locale } from '$lib/i18n';

	let locale = $derived<Locale>(page.data.locale ?? DEFAULT_LOCALE);
</script>

<main class="mx-auto flex min-h-[70vh] max-w-3xl flex-col justify-center px-4 py-12">
	<ErrorState
		statusCode={page.status}
		{locale}
		retryHref={page.url.pathname + page.url.search}
		backHref="/dashboard"
		retryLabel={t(locale, 'error.retryPage')}
		backLabel={t(locale, 'error.backDashboard')}
	/>
</main>
