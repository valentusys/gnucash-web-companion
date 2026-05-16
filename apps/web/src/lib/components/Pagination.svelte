<script lang="ts">
	let {
		offset,
		limit,
		total,
		onChange
	}: {
		offset: number;
		limit: number;
		total: number;
		onChange: (offset: number) => void;
	} = $props();

	const currentPage = $derived(Math.floor(offset / limit) + 1);
	const totalPages = $derived(Math.max(1, Math.ceil(total / limit)));
	const hasPrev = $derived(offset > 0);
	const hasNext = $derived(offset + limit < total);

	function prev() {
		if (hasPrev) onChange(Math.max(0, offset - limit));
	}

	function next() {
		if (hasNext) onChange(offset + limit);
	}
</script>

<div class="flex items-center justify-between gap-4 py-3">
	<p class="text-sm" style="color: var(--app-muted);">
		{total === 0 ? 'No results' : `${offset + 1}–${Math.min(offset + limit, total)} of ${total}`}
	</p>
	<div class="flex items-center gap-2">
		<button
			type="button"
			class="rounded-lg border px-3 py-1.5 text-sm font-medium transition-colors hover:opacity-80 disabled:cursor-not-allowed disabled:opacity-40"
			style="border-color: var(--app-border); color: var(--app-text);"
			disabled={!hasPrev}
			onclick={prev}
		>
			Previous
		</button>
		<span class="text-sm" style="color: var(--app-muted);">Page {currentPage} of {totalPages}</span>
		<button
			type="button"
			class="rounded-lg border px-3 py-1.5 text-sm font-medium transition-colors hover:opacity-80 disabled:cursor-not-allowed disabled:opacity-40"
			style="border-color: var(--app-border); color: var(--app-text);"
			disabled={!hasNext}
			onclick={next}
		>
			Next
		</button>
	</div>
</div>
