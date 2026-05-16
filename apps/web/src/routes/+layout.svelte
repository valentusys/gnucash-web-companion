<script lang="ts">
	import '../app.css';

	let { data, children } = $props();
</script>

<div class="min-h-screen bg-gray-50 text-gray-900">
	{#if data.authenticated}
		<header class="border-b border-gray-200 bg-white">
			<div class="mx-auto flex max-w-5xl items-center justify-between px-4 py-3">
				<a href="/dashboard" class="text-sm font-semibold text-gray-900">GnuCash Web Companion</a>
				<nav class="flex items-center gap-3">
					<a href="/accounts" class="text-sm font-medium text-gray-700 hover:text-gray-950">Accounts</a>
					<a href="/transactions" class="text-sm font-medium text-gray-700 hover:text-gray-950">Transactions</a>
					<form method="POST" action="/logout">
						<button
							type="submit"
							class="rounded-lg border border-gray-300 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
						>
							Logout
						</button>
					</form>
				</nav>
			</div>
		</header>
	{/if}

	{@render children()}
</div>
