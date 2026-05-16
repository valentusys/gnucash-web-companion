<script lang="ts">
	import { page } from '$app/state';
</script>

<main class="mx-auto flex min-h-[70vh] max-w-3xl flex-col justify-center px-4 py-12">
	<section
		class="rounded-3xl border p-6 shadow-sm"
		style="border-color: var(--app-border); background-color: var(--app-panel);"
		role="alert"
	>
		<p class="text-sm font-semibold uppercase tracking-wide" style="color: var(--app-muted);">
			{page.status}
		</p>
		<h1 class="mt-2 text-2xl font-bold" style="color: var(--app-text);">
			{page.error?.message ?? 'Something went wrong'}
		</h1>
		<p class="mt-3" style="color: var(--app-muted);">
			If this is a GnuCash book error, verify that the configured book path exists and that
			the app is pointed at a test copy of the book during pre-alpha testing.
		</p>
		<div class="mt-6 flex flex-wrap gap-3">
			<a
				href="/dashboard"
				class="rounded-xl px-4 py-2 text-sm font-semibold text-white"
				style="background-color: var(--app-accent);"
			>
				Back to dashboard
			</a>
			<a
				href="/login"
				class="rounded-xl border px-4 py-2 text-sm font-semibold"
				style="border-color: var(--app-border); color: var(--app-text);"
			>
				Sign in again
			</a>
		</div>
	</section>
</main>
