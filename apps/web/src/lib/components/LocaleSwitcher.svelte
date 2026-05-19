<script lang="ts">
	import { messages, supportedLocales, t, type Locale } from '$lib/i18n';

	let {
		locale,
		returnTo = '/',
		compact = false
	}: { locale: Locale; returnTo?: string; compact?: boolean } = $props();
</script>

<form method="POST" action="/locale" class="flex items-center gap-2 text-xs">
	<input type="hidden" name="returnTo" value={returnTo} />
	<label class="sr-only" for="locale-switcher">{t(locale, 'locale.switcherLabel')}</label>
	<select
		id="locale-switcher"
		name="locale"
		class="min-h-11 min-w-[44px] rounded-lg border px-3 py-2 text-xs"
		style="border-color: var(--app-input-border); background-color: var(--app-input-bg); color: var(--app-text);"
		aria-label={t(locale, 'locale.switcherLabel')}
		onchange={(event) => event.currentTarget.form?.requestSubmit()}
	>
		{#each supportedLocales as option}
			<option value={option} selected={option === locale}>
				{messages[locale][option === 'en' ? 'locale.english' : 'locale.russian']}
			</option>
		{/each}
	</select>
	{#if !compact}
		<noscript><button type="submit">OK</button></noscript>
	{/if}
</form>
