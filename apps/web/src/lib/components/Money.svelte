<script lang="ts">
	let { amount, currency }: { amount: string; currency: string } = $props();
</script>

<span class="tabular-nums">
	{amount}
	<span class="ml-1 text-xs font-medium uppercase" style="color: var(--app-muted);">{currency}</span>
</span>
