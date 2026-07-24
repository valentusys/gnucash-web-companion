<script lang="ts">
	import { goto } from '$app/navigation';
	import type { Book } from '$lib/api/types';
	import { DEFAULT_LOCALE, t, type Locale } from '$lib/i18n';

	let {
		books,
		activeBook,
		compact = false,
		locale = DEFAULT_LOCALE
	}: { books: Book[]; activeBook: Book | null; compact?: boolean; locale?: Locale } = $props();
	const openableBooks = $derived(books.filter((book) => book.can_open_read_only_views));

	function currentRouteNext(): string {
		return `${window.location.pathname}${window.location.search}`;
	}

	function safeBookSelectHref(bookId: string): string {
		return `/books/${encodeURIComponent(bookId)}/select?next=${encodeURIComponent(currentRouteNext())}`;
	}

	function handleChange(event: Event) {
		const select = event.target as HTMLSelectElement;
		const bookId = select.value;
		if (bookId) {
			goto(safeBookSelectHref(bookId));
		}
	}
</script>

{#if openableBooks.length > 1}
	<label
		class="flex max-w-full min-w-0 flex-wrap items-center gap-2 text-sm"
		style="color: var(--app-muted);"
	>
		<span class={compact ? 'sr-only' : 'shrink-0 font-medium'} style="color: var(--app-text);">{t(locale, 'safety.currentBook')}:</span>
		<select
			value={activeBook?.id ?? ''}
			onchange={handleChange}
			aria-label={t(locale, 'safety.currentBook')}
			data-testid="book-switcher-select"
			class="min-h-11 min-w-0 max-w-full truncate rounded-lg border px-3 py-2 text-sm"
			style="border-color: var(--app-border); background-color: var(--app-input-bg); color: var(--app-text);"
		>
			{#each openableBooks as book (book.id)}
				<option value={book.id}>{book.name}{book.is_default ? ` (${t(locale, 'books.defaultBook')})` : ''}</option>
			{/each}
		</select>
		{#if !compact}
			<span class="text-xs" style="color: var(--app-muted);">{t(locale, 'books.hiddenPolicy')}</span>
		{/if}
	</label>
{:else if activeBook}
	<span class="block max-w-full truncate text-sm font-medium" style="color: var(--app-muted);" aria-label={t(locale, 'safety.currentBook')}>
		{t(locale, 'safety.currentBook')}: <span style="color: var(--app-text);">{activeBook.name}</span>
	</span>
{/if}
