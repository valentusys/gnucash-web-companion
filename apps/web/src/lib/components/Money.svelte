<script lang="ts">
	let { amount, currency }: { amount: string; currency: string } = $props();
</script>

<span class="inline-flex max-w-full min-w-0 flex-wrap justify-end gap-x-1 tabular-nums">
	<span class="min-w-0 break-all">{amount}</span>
	<span class="shrink-0 text-xs font-medium uppercase" style="color: var(--app-muted);">{currency}</span>
</span>
