<script lang="ts">
	let {
		message = 'Read-only MVP by default. GnuCash Desktop remains the authoritative editor; web writes require an explicit post-MVP feature flag.'
	}: { message?: string } = $props();
</script>

<section
	class="border-b px-4 py-2 text-xs md:text-sm"
	style="background: color-mix(in srgb, var(--app-accent) 8%, var(--app-panel)); border-color: var(--app-border); color: var(--app-text);"
	aria-label="Read-only safety status"
>
	<div class="mx-auto flex max-w-5xl flex-col gap-1 md:flex-row md:items-center md:justify-between">
		<div class="flex items-center gap-2 font-medium">
			<span
				class="inline-flex h-2 w-2 rounded-full"
				style="background: var(--app-success);"
				aria-hidden="true"
			></span>
			<span>Read-only by default</span>
		</div>
		<p class="leading-snug" style="color: var(--app-muted);">{message}</p>
	</div>
</section>
