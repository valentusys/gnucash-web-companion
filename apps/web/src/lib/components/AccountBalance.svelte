<script lang="ts">
	import Money from './Money.svelte';

	let { balance, currency }: { balance: string; currency: string } = $props();
	const negative = $derived(balance.trim().startsWith('-'));
</script>

<span class={negative ? 'font-semibold text-red-700' : 'font-semibold text-gray-900'}>
	<Money amount={balance} {currency} />
</span>
