<script lang="ts">
	interface Props {
		title?: string;
		message?: string;
		icon?: string;
		role?: 'status' | 'note' | 'alert';
		ariaLabel?: string;
		children?: import('svelte').Snippet;
	}

	let {
		title = 'Nothing here yet',
		message = 'There are no items to display.',
		icon = '📭',
		role = 'status',
		ariaLabel = title,
		children
	}: Props = $props();
</script>

<div
	class="flex flex-col items-center justify-center rounded-2xl border px-6 py-12 text-center"
	style="border-color: var(--app-border); background-color: var(--app-panel);"
	role={role}
	aria-label={ariaLabel}
>
	<div class="mb-3 text-4xl" aria-hidden="true">{icon}</div>
	<p class="text-lg font-semibold" style="color: var(--app-text);">{title}</p>
	<p class="mt-1 max-w-2xl text-sm" style="color: var(--app-muted);">{message}</p>
	{#if children}
		<div class="mt-4 flex flex-wrap justify-center gap-2">
			{@render children()}
		</div>
	{/if}
</div>
