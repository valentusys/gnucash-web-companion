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
		<li>{t(locale, 'writeMode.createOnlyDogfood')}</li>
		<li>{t(locale, 'writeMode.evidence')}</li>
		<li>{t(locale, 'writeMode.staleLock')}</li>
		<li>{t(locale, 'writeMode.neverRealBook')}</li>
	</ul>
	<div class="mt-4 rounded-xl p-3" style="border: 1px solid #d97706; background: #fef3c7;">
		<p class="font-semibold">Owner-writebeta session gate prototype</p>
		<ul class="mt-2 list-disc space-y-1 pl-5">
			<li>Preflight, outside-git copied/working target fingerprint, independent backup readiness, and restore readiness must pass before any future write.</li>
			<li>Exact operation preview and confirmation are required; failed preflight keeps mutation controls disabled.</li>
			<li>This banner is a warning prototype only; it does not make real, only-copy, production, or public write use safe.</li>
		</ul>
	</div>
</div>
