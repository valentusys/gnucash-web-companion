<script lang="ts">
	import { goto } from '$app/navigation';
	import type { Book } from '$lib/api/types';

	let { books, activeBook }: { books: Book[]; activeBook: Book | null } = $props();

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
	<label class="flex flex-wrap items-center gap-2 text-sm" style="color: var(--app-muted);">
		<span class="font-medium" style="color: var(--app-text);">Current book:</span>
		<select
			value={activeBook?.id ?? ''}
			onchange={handleChange}
			aria-label="Select book"
			class="rounded-lg border px-2 py-1 text-sm"
			style="border-color: var(--app-border); background-color: var(--app-input-bg); color: var(--app-text);"
		>
			{#each books as book (book.id)}
				<option value={book.id}>{book.name}{book.is_default ? ' (default)' : ''}</option>
			{/each}
		</select>
		<span class="text-xs" style="color: var(--app-muted);">independent read-only books</span>
	</label>
{:else if activeBook}
	<span class="text-sm font-medium" style="color: var(--app-muted);" aria-label="Current book">
		Current book: <span style="color: var(--app-text);">{activeBook.name}</span>
	</span>
{/if}
