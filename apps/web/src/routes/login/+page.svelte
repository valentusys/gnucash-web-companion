<script lang="ts">
	let { form } = $props();
</script>

<svelte:head>
	<title>Sign in — GnuCash Web Companion</title>
</svelte:head>

<main class="flex min-h-screen items-center justify-center px-4 py-12">
	<section class="w-full max-w-md rounded-2xl bg-white p-6 shadow-sm ring-1 ring-gray-200 sm:p-8">
		<div class="mb-8 text-center">
			<h1 class="text-3xl font-bold tracking-tight text-gray-900">Sign in</h1>
			<p class="mt-2 text-sm text-gray-600">Use the configured admin account to continue.</p>
		</div>

		{#if form?.error}
			<div class="mb-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
				{form.error}
			</div>
		{/if}

		<form method="POST" class="space-y-5">
			<label class="block">
				<span class="text-sm font-medium text-gray-700">Username</span>
				<input
					name="username"
					type="text"
					autocomplete="username"
					required
					value={form?.username ?? 'admin'}
					class="mt-2 block w-full rounded-xl border border-gray-300 px-4 py-3 text-base shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
				/>
			</label>

			<label class="block">
				<span class="text-sm font-medium text-gray-700">Password</span>
				<input
					name="password"
					type="password"
					autocomplete="current-password"
					required
					class="mt-2 block w-full rounded-xl border border-gray-300 px-4 py-3 text-base shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
				/>
			</label>

			<button
				type="submit"
				class="w-full rounded-xl bg-blue-600 px-4 py-3 text-base font-semibold text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
			>
				Sign in
			</button>
		</form>
	</section>
</main>
