<script lang="ts">
	import { goto } from '$app/navigation';
	import type { Book } from '$lib/api/types';

	let {
		books,
		activeBook,
		compact = false
	}: { books: Book[]; activeBook: Book | null; compact?: boolean } = $props();

	function handleChange(event: Event) {
		const select = event.target as HTMLSelectElement;
		const bookId = select.value;
		if (bookId) {
			document.cookie = `selected_book_id=${bookId};path=/;max-age=2592000;samesite=lax`;
			goto(`${window.location.pathname}${window.location.search}`);
		}
	}
</script>

{#if books.length > 1}
	<label
		class="flex max-w-full min-w-0 flex-wrap items-center gap-2 text-sm"
		style="color: var(--app-muted);"
	>
		<span class={compact ? 'sr-only' : 'shrink-0 font-medium'} style="color: var(--app-text);">Current book:</span>
		<select
			value={activeBook?.id ?? ''}
			onchange={handleChange}
			aria-label="Select book"
			class="min-h-11 min-w-0 max-w-full truncate rounded-lg border px-3 py-2 text-sm"
			style="border-color: var(--app-border); background-color: var(--app-input-bg); color: var(--app-text);"
		>
			{#each books as book (book.id)}
				<option value={book.id}>{book.name}{book.is_default ? ' (default)' : ''}</option>
			{/each}
		</select>
		{#if !compact}
			<span class="text-xs" style="color: var(--app-muted);">independent read-only books</span>
		{/if}
	</label>
{:else if activeBook}
	<span class="block max-w-full truncate text-sm font-medium" style="color: var(--app-muted);" aria-label="Current book">
		Current book: <span style="color: var(--app-text);">{activeBook.name}</span>
	</span>
{/if}
