<script lang="ts">
	import { DEFAULT_LOCALE, t, type Locale } from '$lib/i18n';

	let {
		locale = DEFAULT_LOCALE,
		message
	}: { locale?: Locale; message?: string } = $props();

	const bannerMessage = $derived(message ?? t(locale, 'safety.message'));
</script>

<section
	class="border-b px-4 py-2 text-xs md:text-sm"
	style="background: color-mix(in srgb, var(--app-accent) 8%, var(--app-panel)); border-color: var(--app-border); color: var(--app-text);"
	aria-label={t(locale, 'safety.statusLabel')}
>
	<div class="mx-auto flex max-w-5xl flex-col gap-1 md:flex-row md:items-center md:justify-between">
		<div class="flex items-center gap-2 font-medium">
			<span
				class="inline-flex h-2 w-2 rounded-full"
				style="background: var(--app-success);"
				aria-hidden="true"
			></span>
			<span>{t(locale, 'safety.badge')}</span>
		</div>
		<p class="leading-snug" style="color: var(--app-muted);">{bannerMessage}</p>
	</div>
</section>
