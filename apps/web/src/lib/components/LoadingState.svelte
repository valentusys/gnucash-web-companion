<script lang="ts">
	interface Props {
		message?: string;
		children?: import('svelte').Snippet;
	}

	let { message = 'Loading…', children }: Props = $props();
</script>

<div
	class="flex flex-col items-center justify-center rounded-2xl border px-6 py-12 text-center"
	style="border-color: var(--app-border); background-color: var(--app-panel);"
	aria-live="polite"
	aria-busy="true"
>
	<div class="mb-3 h-8 w-8 animate-spin rounded-full border-4 border-t-transparent" style="border-color: var(--app-border); border-top-color: var(--app-accent);" aria-hidden="true"></div>
	<p class="text-sm font-medium" style="color: var(--app-muted);">{message}</p>
	{#if children}
		<div class="mt-4">
			{@render children()}
		</div>
	{/if}
</div>
