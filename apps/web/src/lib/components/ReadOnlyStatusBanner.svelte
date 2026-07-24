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
	class="border-b px-4 py-2 text-xs md:text-sm"
	style="background: color-mix(in srgb, var(--app-accent) 8%, var(--app-panel)); border-color: var(--app-border); color: var(--app-text);"
	aria-label={t(locale, 'safety.statusLabel')}
>
	<div class="mx-auto flex max-w-5xl flex-col gap-2 md:flex-row md:items-start md:justify-between">
		<div class="flex min-w-0 flex-col gap-1 font-medium sm:flex-row sm:flex-wrap sm:items-center sm:gap-2">
			<span class="inline-flex items-center gap-2 rounded-full border px-2 py-1" style="border-color: var(--app-border); background: var(--app-panel);">
				<span
					class="inline-flex h-2 w-2 rounded-full shrink-0"
					style="background: var(--app-success);"
					aria-hidden="true"
				></span>
				<span>{t(locale, 'safety.badge')}</span>
			</span>
			<span class="inline-flex rounded-full border px-2 py-1" style="border-color: var(--app-border); background: var(--app-panel); color: var(--app-muted);">
				{t(locale, 'safety.writeDisabled')}
			</span>
			<span class="min-w-0 truncate rounded-full border px-2 py-1" style="border-color: var(--app-border); background: var(--app-panel);" title={currentBookLabel}>
				{currentBookLabel}
			</span>
			<a class="rounded-full border px-2 py-1 underline-offset-2 hover:underline focus:outline-none focus:ring-2" style="border-color: var(--app-border); color: var(--app-accent);" href="/books">
				{t(locale, 'safety.reviewBooks')}
			</a>
		</div>
		<div class="min-w-0 leading-snug" style="color: var(--app-muted);">
			<p class="break-words">{t(locale, 'safety.shortBoundary')}</p>
			<details class="mt-1 max-w-3xl">
				<summary class="cursor-pointer font-medium underline-offset-2 hover:underline" style="color: var(--app-accent);">
					{t(locale, 'safety.detailsLabel')}
				</summary>
				<p class="mt-1 text-[0.72rem] md:text-xs">{bannerMessage}</p>
				<p class="mt-1 text-[0.72rem] md:text-xs">{t(locale, 'safety.releaseCritical')}</p>
			</details>
		</div>
	</div>
</section>
