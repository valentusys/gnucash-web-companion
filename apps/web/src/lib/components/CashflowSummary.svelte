<script lang="ts">
	import { isNonNegativeDecimalString } from '$lib/money.js';

	type Period = import('$lib/api/types').CashflowPeriod;

	let { periods, loading = false }: { periods: Period[]; loading?: boolean } = $props();
</script>

<section class="rounded-xl p-5" style="background-color: var(--app-panel); box-shadow: 0 1px 3px var(--app-panel-shadow); border: 1px solid var(--app-border);">
	<h2 class="text-lg font-semibold" style="color: var(--app-text);">Cashflow</h2>

	{#if loading}
		<div class="mt-4 space-y-3">
			{#each Array(3) as _}
				<div class="animate-pulse flex gap-4">
					<div class="h-16 flex-1 rounded" style="background-color: var(--app-elevated-bg);"></div>
					<div class="h-16 flex-1 rounded" style="background-color: var(--app-elevated-bg);"></div>
					<div class="h-16 flex-1 rounded" style="background-color: var(--app-elevated-bg);"></div>
				</div>
			{/each}
		</div>
	{:else if periods.length === 0}
		<p class="mt-4 text-sm" style="color: var(--app-muted);">No cashflow data for the selected period.</p>
	{:else}
		<div class="mt-4 space-y-3">
			{#each periods as period (period.month)}
				<div class="rounded-lg p-3" style="background-color: var(--app-elevated-bg);">
					<p class="text-xs font-medium uppercase tracking-wide" style="color: var(--app-muted);">{period.month}</p>
					<div class="mt-2 grid grid-cols-3 gap-2 text-sm">
						<div>
							<span style="color: var(--app-muted);">In</span>
							<p class="font-semibold tabular-nums" style="color: var(--app-success);">{period.inflow}</p>
						</div>
						<div>
							<span style="color: var(--app-muted);">Out</span>
							<p class="font-semibold tabular-nums" style="color: var(--app-danger);">{period.outflow}</p>
						</div>
						<div>
							<span style="color: var(--app-muted);">Net</span>
							<p
								class="font-semibold tabular-nums"
								style="color: {isNonNegativeDecimalString(period.net) ? 'var(--app-success)' : 'var(--app-danger)'};"
							>
								{period.net}
							</p>
						</div>
					</div>
				</div>
			{/each}
		</div>
	{/if}
</section>
