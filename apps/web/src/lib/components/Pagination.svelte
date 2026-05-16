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
	<p class="text-sm text-gray-600">
		{total === 0 ? 'No results' : `${offset + 1}–${Math.min(offset + limit, total)} of ${total}`}
	</p>
	<div class="flex items-center gap-2">
		<button
			type="button"
			class="rounded-lg border border-gray-300 px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-40"
			disabled={!hasPrev}
			onclick={prev}
		>
			Previous
		</button>
		<span class="text-sm text-gray-500">Page {currentPage} of {totalPages}</span>
		<button
			type="button"
			class="rounded-lg border border-gray-300 px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-40"
			disabled={!hasNext}
			onclick={next}
		>
			Next
		</button>
	</div>
</div>
