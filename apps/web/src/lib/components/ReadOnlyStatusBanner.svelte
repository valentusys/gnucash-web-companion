<script lang="ts">
	import { DEFAULT_LOCALE, t, type Locale } from '$lib/i18n';
	import type { Book } from '$lib/api/types';

	let {
		locale = DEFAULT_LOCALE,
		activeBook = null,
		message
	}: { locale?: Locale; activeBook?: Book | null; message?: string } = $props();

	const bannerMessage = $derived(message ?? t(locale, 'safety.message'));
	const currentBookName = $derived(activeBook?.name ?? t(locale, 'safety.noActiveBook'));
	const currentBookLabel = $derived(`${t(locale, 'safety.currentBook')}: ${currentBookName}`);
</script>

<section
	data-read-only-banner
	class="border-b px-3 py-1.5 text-xs md:px-4 md:text-sm"
	style="background: color-mix(in srgb, var(--app-accent) 8%, var(--app-panel)); border-color: var(--app-border); color: var(--app-text);"
	aria-label={t(locale, 'safety.statusLabel')}
>
	<div class="mx-auto flex min-w-0 items-center flex-wrap gap-2 whitespace-nowrap md:max-w-5xl">
		<span class="inline-flex shrink-0 items-center gap-1.5 rounded-full border px-2 py-1 font-semibold" style="border-color: var(--app-border); background: var(--app-panel);">
			<span class="inline-flex h-2 w-2 shrink-0 rounded-full" style="background: var(--app-success);" aria-hidden="true"></span>
			<span>{t(locale, 'safety.badge')}</span>
		</span>
		<span class="hidden shrink-0 rounded-full border px-2 py-1 sm:inline-flex" style="border-color: var(--app-border); background: var(--app-panel); color: var(--app-muted);">
			{t(locale, 'safety.writeDisabled')}
		</span>
		<span class="min-w-0 flex-1 truncate" title={currentBookLabel}>{currentBookLabel}</span>
		<details class="min-w-0 shrink-0 whitespace-normal open:basis-full open:w-full">
			<summary class="cursor-pointer font-semibold underline-offset-2 hover:underline focus:outline-none focus:ring-2" style="color: var(--app-accent);">
				{t(locale, 'safety.detailsLabel')}
			</summary>
			<div class="mt-2 max-w-3xl space-y-1 pb-1 text-[0.72rem] leading-snug md:text-xs" style="color: var(--app-muted);">
				<p class="break-words">{t(locale, 'safety.shortBoundary')}</p>
				<p class="break-words">{bannerMessage}</p>
				<p class="break-words">{t(locale, 'safety.releaseCritical')}</p>
				<a class="inline-block font-semibold underline-offset-2 hover:underline focus:outline-none focus:ring-2" style="color: var(--app-accent);" href="/books">
					{t(locale, 'safety.reviewBooks')}
				</a>
			</div>
		</details>
	</div>
</section>
