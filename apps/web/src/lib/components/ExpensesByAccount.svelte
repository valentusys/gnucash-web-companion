<script lang="ts">
	type Expense = import('$lib/api/types').ExpenseByAccount;

	let { expenses, loading = false }: { expenses: Expense[]; loading?: boolean } = $props();

	function barWidth(total: string, all: Expense[]): string {
		const max = Math.max(...all.map((e) => Math.abs(Number(e.total))), 1);
		const pct = Math.min((Math.abs(Number(total)) / max) * 100, 100);
		return `${pct}%`;
	}
</script>

<section class="rounded-xl bg-white p-5 shadow-sm ring-1 ring-gray-200">
	<h2 class="text-lg font-semibold text-gray-900">Expenses by Account</h2>

	{#if loading}
		<div class="mt-4 space-y-3">
			{#each Array(4) as _}
				<div class="animate-pulse">
					<div class="h-3 w-32 rounded bg-gray-200"></div>
					<div class="mt-2 h-2 w-full rounded bg-gray-100"></div>
				</div>
			{/each}
		</div>
	{:else if expenses.length === 0}
		<p class="mt-4 text-sm text-gray-500">No expenses found for the selected period.</p>
	{:else}
		<ul class="mt-4 space-y-3">
			{#each expenses as exp (exp.account_id)}
				<li>
					<div class="flex items-center justify-between text-sm">
						<span class="truncate font-medium text-gray-700">{exp.account_name}</span>
						<span class="ml-4 whitespace-nowrap tabular-nums text-gray-900">
							{exp.total}
							<span class="ml-0.5 text-xs text-gray-400">{exp.currency}</span>
						</span>
					</div>
					<div class="mt-1 h-1.5 w-full overflow-hidden rounded-full bg-gray-100">
						<div
							class="h-full rounded-full bg-red-400"
							style="width: {barWidth(exp.total, expenses)}"
						></div>
					</div>
				</li>
			{/each}
		</ul>
	{/if}
</section>
