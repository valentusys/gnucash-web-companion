<script lang="ts">
	type Period = import('$lib/api/types').CashflowPeriod;

	let { periods, loading = false }: { periods: Period[]; loading?: boolean } = $props();
</script>

<section class="rounded-xl bg-white p-5 shadow-sm ring-1 ring-gray-200">
	<h2 class="text-lg font-semibold text-gray-900">Cashflow</h2>

	{#if loading}
		<div class="mt-4 space-y-3">
			{#each Array(3) as _}
				<div class="animate-pulse flex gap-4">
					<div class="h-16 flex-1 rounded bg-gray-100"></div>
					<div class="h-16 flex-1 rounded bg-gray-100"></div>
					<div class="h-16 flex-1 rounded bg-gray-100"></div>
				</div>
			{/each}
		</div>
	{:else if periods.length === 0}
		<p class="mt-4 text-sm text-gray-500">No cashflow data for the selected period.</p>
	{:else}
		<div class="mt-4 space-y-3">
			{#each periods as period (period.month)}
				<div class="rounded-lg bg-gray-50 p-3">
					<p class="text-xs font-medium uppercase tracking-wide text-gray-500">{period.month}</p>
					<div class="mt-2 grid grid-cols-3 gap-2 text-sm">
						<div>
							<span class="text-gray-500">In</span>
							<p class="font-semibold tabular-nums text-emerald-600">{period.inflow}</p>
						</div>
						<div>
							<span class="text-gray-500">Out</span>
							<p class="font-semibold tabular-nums text-red-600">{period.outflow}</p>
						</div>
						<div>
							<span class="text-gray-500">Net</span>
							<p
								class="font-semibold tabular-nums"
								class:text-emerald-600={Number(period.net) >= 0}
								class:text-red-600={Number(period.net) < 0}
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
