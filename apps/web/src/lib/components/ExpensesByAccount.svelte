<script lang="ts">
	type Expense = import('$lib/api/types').ExpenseByAccount;

	let { expenses, loading = false }: { expenses: Expense[]; loading?: boolean } = $props();

	function barWidth(total: string, all: Expense[]): string {
		const max = Math.max(...all.map((e) => Math.abs(Number(e.total))), 1);
		const pct = Math.min((Math.abs(Number(total)) / max) * 100, 100);
		return `${pct}%`;
	}
</script>

<section class="rounded-xl p-5" style="background-color: var(--app-panel); box-shadow: 0 1px 3px var(--app-panel-shadow); border: 1px solid var(--app-border);">
	<h2 class="text-lg font-semibold" style="color: var(--app-text);">Expenses by Account</h2>

	{#if loading}
		<div class="mt-4 space-y-3">
			{#each Array(4) as _}
				<div class="animate-pulse">
					<div class="h-3 w-32 rounded" style="background-color: var(--app-border);"></div>
					<div class="mt-2 h-2 w-full rounded" style="background-color: var(--app-elevated-bg);"></div>
				</div>
			{/each}
		</div>
	{:else if expenses.length === 0}
		<p class="mt-4 text-sm" style="color: var(--app-muted);">No expenses found for the selected period.</p>
	{:else}
		<ul class="mt-4 space-y-3">
			{#each expenses as exp (exp.account_id)}
				<li>
					<div class="flex items-center justify-between text-sm">
						<span class="truncate font-medium" style="color: var(--app-text);">{exp.account_name}</span>
						<span class="ml-4 whitespace-nowrap tabular-nums" style="color: var(--app-text);">
							{exp.total}
							<span class="ml-0.5 text-xs" style="color: var(--app-muted);">{exp.currency}</span>
						</span>
					</div>
					<div class="mt-1 h-1.5 w-full overflow-hidden rounded-full" style="background-color: var(--app-elevated-bg);">
						<div
							class="h-full rounded-full"
							style="width: {barWidth(exp.total, expenses)}; background-color: var(--app-danger);"
						></div>
					</div>
				</li>
			{/each}
		</ul>
	{/if}
</section>
