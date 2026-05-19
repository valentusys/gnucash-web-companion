<script lang="ts">
	interface Props {
		statusCode?: number;
		title?: string;
		message?: string;
		retryHref?: string;
		backHref?: string;
		retryLabel?: string;
		backLabel?: string;
		children?: import('svelte').Snippet;
	}

	let {
		statusCode,
		title,
		message,
		retryHref,
		backHref = '/dashboard',
		retryLabel = 'Retry',
		backLabel = 'Back to dashboard',
		children
	}: Props = $props();

	const defaultTitle = $derived(
		statusCode === 403
			? 'Access denied'
			: statusCode === 404
				? 'Page or book not found'
				: statusCode && statusCode >= 500
					? 'Service temporarily unavailable'
					: 'Something went wrong'
	);

	const defaultMessage = $derived(
		statusCode === 403
			? 'Your account cannot access this read-only view or book. Check the selected book or sign in with an account that has access.'
			: statusCode === 404
				? 'The requested page, book, account, or transaction was not found. It may be unavailable, archived, or hidden by access rules.'
				: statusCode && statusCode >= 500
					? 'The API or network request failed while loading this read-only view. Verify the service is running and try again.'
					: 'An unexpected API or network error occurred. Please try again or return to a safe read-only page.'
	);
</script>

<section
	class="flex flex-col items-center justify-center rounded-2xl border px-6 py-12 text-center"
	style="border-color: var(--app-danger); background-color: color-mix(in srgb, var(--app-danger) 8%, var(--app-panel));"
	role="alert"
	aria-label={title ?? defaultTitle}
>
	<div class="mb-3 text-4xl" aria-hidden="true">⚠️</div>
	<p class="text-sm font-semibold uppercase tracking-wide" style="color: var(--app-muted);">
		{statusCode ? `Error ${statusCode}` : 'API/network error'}
	</p>
	<h1 class="mt-2 text-2xl font-bold" style="color: var(--app-danger);">{title ?? defaultTitle}</h1>
	<p class="mt-2 max-w-2xl text-sm" style="color: var(--app-muted);">{message ?? defaultMessage}</p>
	<div class="mt-5 flex flex-wrap justify-center gap-2">
		{#if retryHref}
			<a
				href={retryHref}
				aria-label={`${retryLabel}: ${title ?? defaultTitle}`}
				class="rounded-xl px-4 py-2 text-sm font-semibold text-white"
				style="background-color: var(--app-accent);"
			>
				{retryLabel}
			</a>
		{/if}
		{#if backHref}
			<a
				href={backHref}
				aria-label={`${backLabel}: ${title ?? defaultTitle}`}
				class="rounded-xl border px-4 py-2 text-sm font-semibold"
				style="border-color: var(--app-border); color: var(--app-text);"
			>
				{backLabel}
			</a>
		{/if}
		{#if children}
			{@render children()}
		{/if}
	</div>
</section>
