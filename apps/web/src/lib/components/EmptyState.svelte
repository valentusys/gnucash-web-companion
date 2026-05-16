<script lang="ts">
	interface Props {
		title?: string;
		message?: string;
		children?: import('svelte').Snippet;
	}

	let {
		title = 'Nothing here yet',
		message = 'There are no items to display.',
		children
	}: Props = $props();
</script>

<div
	class="flex flex-col items-center justify-center rounded-2xl border px-6 py-12 text-center"
	style="border-color: var(--app-border); background-color: var(--app-panel);"
	role="status"
>
	<div class="mb-3 text-4xl" aria-hidden="true">📭</div>
	<p class="text-lg font-semibold" style="color: var(--app-text);">{title}</p>
	<p class="mt-1 text-sm" style="color: var(--app-muted);">{message}</p>
	{#if children}
		<div class="mt-4">
			{@render children()}
		</div>
	{/if}
</div>
