<script lang="ts">
	import { DEFAULT_LOCALE, t, type Locale } from '$lib/i18n';

	interface Props {
		statusCode?: number;
		title?: string;
		message?: string;
		retryHref?: string;
		backHref?: string;
		retryLabel?: string;
		backLabel?: string;
		locale?: Locale;
		children?: import('svelte').Snippet;
	}

	let {
		statusCode,
		title,
		message,
		retryHref,
		backHref = '/dashboard',
		retryLabel,
		backLabel,
		locale = DEFAULT_LOCALE,
		children
	}: Props = $props();

	const defaultTitle = $derived(
		statusCode === 403
			? t(locale, 'error.forbiddenTitle')
			: statusCode === 404
				? t(locale, 'error.notFoundTitle')
				: statusCode && statusCode >= 500
					? t(locale, 'error.serviceTitle')
					: t(locale, 'error.genericTitle')
	);

	const defaultMessage = $derived(
		statusCode === 403
			? t(locale, 'error.forbiddenMessage')
			: statusCode === 404
				? t(locale, 'error.notFoundMessage')
				: statusCode && statusCode >= 500
					? t(locale, 'error.serviceMessage')
					: t(locale, 'error.genericMessage')
	);
	const defaultRetryLabel = $derived(retryLabel ?? t(locale, 'error.retry'));
	const defaultBackLabel = $derived(backLabel ?? t(locale, 'error.backDashboard'));
	const statusBadge = $derived(
		statusCode ? t(locale, 'error.badgeWithCode', { statusCode }) : t(locale, 'error.badgeNetwork')
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
		{statusBadge}
	</p>
	<h1 class="mt-2 text-2xl font-bold" style="color: var(--app-danger);">{title ?? defaultTitle}</h1>
	<p class="mt-2 max-w-2xl text-sm" style="color: var(--app-muted);">{message ?? defaultMessage}</p>
	<div class="mt-5 flex flex-wrap justify-center gap-2">
		{#if retryHref}
			<a
				href={retryHref}
				aria-label={`${defaultRetryLabel}: ${title ?? defaultTitle}`}
				class="rounded-xl px-4 py-2 text-sm font-semibold text-white"
				style="background-color: var(--app-accent);"
			>
				{defaultRetryLabel}
			</a>
		{/if}
		{#if backHref}
			<a
				href={backHref}
				aria-label={`${defaultBackLabel}: ${title ?? defaultTitle}`}
				class="rounded-xl border px-4 py-2 text-sm font-semibold"
				style="border-color: var(--app-border); color: var(--app-text);"
			>
				{defaultBackLabel}
			</a>
		{/if}
		{#if children}
			{@render children()}
		{/if}
	</div>
</section>
