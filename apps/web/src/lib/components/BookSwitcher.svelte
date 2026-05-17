<script lang="ts">
	import { goto } from '$app/navigation';
	import type { Book } from '$lib/api/types';

	let { books, activeBook }: { books: Book[]; activeBook: Book | null } = $props();

	function handleChange(event: Event) {
		const select = event.target as HTMLSelectElement;
		const bookId = select.value;
		if (bookId) {
			document.cookie = `selected_book_id=${bookId};path=/;max-age=2592000`;
			goto(window.location.pathname);
		}
	}
</script>

{#if books.length > 1}
	<label class="flex items-center gap-2 text-sm" style="color: var(--app-muted);">
		<span class="hidden sm:inline">Book:</span>
		<select
			value={activeBook?.id ?? ''}
			onchange={handleChange}
			aria-label="Select book"
			class="rounded-lg border px-2 py-1 text-sm"
			style="border-color: var(--app-border); background-color: var(--app-input-bg); color: var(--app-text);"
		>
			{#each books as book (book.id)}
				<option value={book.id}>{book.name}</option>
			{/each}
		</select>
	</label>
{:else if activeBook}
	<span class="text-sm font-medium" style="color: var(--app-muted);">
		{activeBook.name}
	</span>
{/if}
