<script lang="ts">
	let { label, value, currency, trend }: {
		label: string;
		value: string;
		currency: string;
		trend?: 'up' | 'down' | 'neutral';
	} = $props();

	function trendColor() {
		if (trend === 'up') return 'var(--app-success)';
		if (trend === 'down') return 'var(--app-danger)';
		return 'var(--app-text)';
	}
</script>

<div class="rounded-xl p-5" style="background-color: var(--app-panel); box-shadow: 0 1px 3px var(--app-panel-shadow); border: 1px solid var(--app-border);">
	<p class="text-xs font-medium uppercase tracking-wide" style="color: var(--app-muted);">{label}</p>
<p class="mt-2 text-2xl font-bold tabular-nums" style="color: {trendColor()};">
		{value}
		<span class="ml-1 text-sm font-medium" style="color: var(--app-muted);">{currency}</span>
	</p>
</div>
