<script lang="ts">
	import { page } from '$app/state';
	import ErrorState from '$lib/components/ErrorState.svelte';
</script>

<main class="mx-auto flex min-h-[70vh] max-w-3xl flex-col justify-center px-4 py-12">
	<ErrorState
		statusCode={page.status}
		title={page.error?.message}
		retryHref={page.url.pathname + page.url.search}
		backHref="/dashboard"
		retryLabel="Retry this page"
		backLabel="Back to dashboard"
	/>
</main>
