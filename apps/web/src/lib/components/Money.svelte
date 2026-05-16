<script lang="ts">
	let { amount, currency }: { amount: string; currency: string } = $props();
</script>

<span class="tabular-nums">
	{amount}
	<span class="ml-1 text-xs font-medium uppercase text-gray-500">{currency}</span>
</span>
