<script lang="ts">
	let { label, value, currency, trend }: {
		label: string;
		value: string;
		currency: string;
		trend?: 'up' | 'down' | 'neutral';
	} = $props();

	function trendColor() {
		if (trend === 'up') return 'text-emerald-600';
		if (trend === 'down') return 'text-red-600';
		return 'text-gray-900';
	}
</script>

<div class="rounded-xl bg-white p-5 shadow-sm ring-1 ring-gray-200">
	<p class="text-xs font-medium uppercase tracking-wide text-gray-500">{label}</p>
	<p class="mt-2 text-2xl font-bold {trendColor()} tabular-nums">
		{value}
		<span class="ml-1 text-sm font-medium text-gray-400">{currency}</span>
	</p>
</div>
