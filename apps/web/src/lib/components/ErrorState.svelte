<script lang="ts">
	interface Props {
		title?: string;
		message?: string;
		children?: import('svelte').Snippet;
	}

	let {
		title = 'Something went wrong',
		message = 'An unexpected error occurred. Please try again.',
		children
	}: Props = $props();
</script>

<div
	class="flex flex-col items-center justify-center rounded-2xl border px-6 py-12 text-center"
	style="border-color: var(--app-danger); background-color: color-mix(in srgb, var(--app-danger) 8%, var(--app-panel));"
	role="alert"
>
	<div class="mb-3 text-4xl" aria-hidden="true">⚠️</div>
	<p class="text-lg font-semibold" style="color: var(--app-danger);">{title}</p>
	<p class="mt-1 text-sm" style="color: var(--app-muted);">{message}</p>
	{#if children}
		<div class="mt-4">
			{@render children()}
		</div>
	{/if}
</div>
