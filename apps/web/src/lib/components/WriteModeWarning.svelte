<script lang="ts">
	import { DEFAULT_LOCALE, t, type Locale } from '$lib/i18n';

	type Props = {
		compact?: boolean;
		locale?: Locale;
	};

	let { compact = false, locale = DEFAULT_LOCALE }: Props = $props();
</script>

<div
	class={compact ? 'rounded-2xl p-4 text-sm' : 'rounded-2xl p-5 text-sm'}
	role="alert"
	style="border: 1px solid #f59e0b; background: #fffbeb; color: #78350f;"
>
	<p class="font-semibold">{t(locale, 'writeMode.title')}</p>
	<p class="mt-2">
		{t(locale, 'writeMode.message')}
	</p>
	<ul class="mt-2 list-disc space-y-1 pl-5">
		<li>{t(locale, 'writeMode.desktop')}</li>
		<li>{t(locale, 'writeMode.disposableOnly')}</li>
		<li>{t(locale, 'writeMode.evidence')}</li>
		<li>{t(locale, 'writeMode.staleLock')}</li>
		<li>{t(locale, 'writeMode.neverRealBook')}</li>
	</ul>
</div>
