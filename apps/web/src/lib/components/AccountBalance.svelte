<script lang="ts">
	import Money from './Money.svelte';

	let { balance, currency }: { balance: string; currency: string } = $props();
	const negative = $derived(balance.trim().startsWith('-'));
</script>

<span class="font-semibold" style="color: {negative ? 'var(--app-danger)' : 'var(--app-text)'};">
	<Money amount={balance} {currency} />
</span>
