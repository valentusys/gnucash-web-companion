<script lang="ts">
	interface Props {
		message?: string;
		variant?: 'default' | 'dashboard' | 'accounts' | 'transactions' | 'books';
		children?: import('svelte').Snippet;
	}

	let { message = 'Loading read-only data…', variant = 'default', children }: Props = $props();

	const blockStyle = 'background-color: var(--app-border);';
	const softBlockStyle = 'background-color: var(--app-elevated-bg);';
</script>

<div
	class="rounded-2xl border p-4"
	style="border-color: var(--app-border); background-color: var(--app-panel);"
	aria-live="polite"
	aria-busy="true"
	role="status"
	data-skeleton-variant={variant}
>
	<span class="sr-only">{message}</span>
	{#if variant === 'dashboard'}
		<div class="space-y-6 animate-pulse" aria-hidden="true">
			<div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
				{#each Array(5) as _}
					<div class="min-h-28 rounded-xl p-5" style="background-color: var(--app-elevated-bg);">
						<div class="h-3 w-24 rounded" style={blockStyle}></div>
						<div class="mt-4 h-7 w-36 rounded" style={blockStyle}></div>
						<div class="mt-4 h-2 w-20 rounded" style={softBlockStyle}></div>
					</div>
				{/each}
			</div>
			<div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
				<div class="min-h-72 rounded-xl p-5" style="background-color: var(--app-panel); border: 1px solid var(--app-border);">
					<div class="h-5 w-40 rounded" style={blockStyle}></div>
					<div class="mt-5 space-y-4">
						{#each Array(5) as _}
							<div class="flex items-center justify-between gap-4">
								<div class="space-y-2">
									<div class="h-4 w-44 rounded" style={blockStyle}></div>
									<div class="h-3 w-28 rounded" style={softBlockStyle}></div>
								</div>
								<div class="h-4 w-20 rounded" style={blockStyle}></div>
							</div>
						{/each}
					</div>
				</div>
				<div class="min-h-72 rounded-xl p-5" style="background-color: var(--app-panel); border: 1px solid var(--app-border);">
					<div class="h-5 w-36 rounded" style={blockStyle}></div>
					<div class="mt-5 space-y-4">
						{#each Array(4) as _}
							<div>
								<div class="flex justify-between gap-4">
									<div class="h-3 w-32 rounded" style={blockStyle}></div>
									<div class="h-3 w-20 rounded" style={blockStyle}></div>
								</div>
								<div class="mt-3 h-2 w-full rounded" style={softBlockStyle}></div>
							</div>
						{/each}
					</div>
				</div>
			</div>
			<div class="min-h-52 rounded-xl p-5" style="background-color: var(--app-panel); border: 1px solid var(--app-border);">
				<div class="h-5 w-24 rounded" style={blockStyle}></div>
				<div class="mt-5 grid grid-cols-3 gap-4">
					{#each Array(6) as _}
						<div class="h-16 rounded" style={softBlockStyle}></div>
					{/each}
				</div>
			</div>
		</div>
	{:else if variant === 'accounts'}
		<div class="overflow-hidden rounded-2xl animate-pulse" style="background-color: var(--app-panel); border: 1px solid var(--app-border);" aria-hidden="true">
			<div class="hidden grid-cols-[minmax(0,1fr)_7rem_9rem_4rem] gap-3 px-4 py-2 md:grid" style="background-color: var(--app-elevated-bg);">
				{#each Array(4) as _}
					<div class="h-3 rounded" style={blockStyle}></div>
				{/each}
			</div>
			<div class="divide-y" style="border-color: var(--app-border);">
				{#each Array(7) as _, index}
					<div class="grid grid-cols-1 gap-2 px-4 py-4 md:grid-cols-[minmax(0,1fr)_7rem_9rem_4rem] md:gap-3">
						<div class="min-w-0" style={`padding-left: ${Math.min(index % 3, 2) * 1.25}rem`}>
							<div class="h-4 rounded" style={`${blockStyle} width: ${index % 2 ? '55%' : '72%'};`}></div>
							<div class="mt-2 h-3 w-40 rounded" style={softBlockStyle}></div>
						</div>
						<div class="h-4 w-20 rounded" style={blockStyle}></div>
						<div class="h-4 w-24 rounded md:ml-auto" style={blockStyle}></div>
						<div class="h-4 w-12 rounded md:ml-auto" style={blockStyle}></div>
					</div>
				{/each}
			</div>
		</div>
	{:else if variant === 'transactions'}
		<div class="space-y-4 animate-pulse" aria-hidden="true">
			<div class="rounded-2xl p-4" style="background-color: var(--app-card-bg); border: 1px solid var(--app-border);">
				<div class="h-5 w-40 rounded" style={blockStyle}></div>
				<div class="mt-4 grid gap-3 md:grid-cols-3">
					{#each Array(6) as _}
						<div class="h-10 rounded-lg" style={softBlockStyle}></div>
					{/each}
				</div>
			</div>
			<div class="rounded-2xl p-4" style="background-color: var(--app-panel); border: 1px solid var(--app-border);">
				<div class="hidden md:block">
					<div class="grid grid-cols-[7rem_32%_22%_22%_9rem] gap-4 border-b pb-3" style="border-color: var(--app-border);">
						{#each Array(5) as _}
							<div class="h-3 rounded" style={blockStyle}></div>
						{/each}
					</div>
					{#each Array(6) as _}
						<div class="grid grid-cols-[7rem_32%_22%_22%_9rem] gap-4 border-b py-4" style="border-color: var(--app-border);">
							{#each Array(5) as __}
								<div class="h-4 rounded" style={blockStyle}></div>
							{/each}
						</div>
					{/each}
				</div>
				<div class="space-y-3 md:hidden">
					{#each Array(5) as _}
						<div class="rounded-xl p-4" style="background-color: var(--app-card-bg); border: 1px solid var(--app-border);">
							<div class="h-4 w-44 rounded" style={blockStyle}></div>
							<div class="mt-3 h-3 w-28 rounded" style={softBlockStyle}></div>
							<div class="mt-4 h-5 w-24 rounded" style={blockStyle}></div>
						</div>
					{/each}
				</div>
			</div>
		</div>
	{:else if variant === 'books'}
		<div class="grid gap-3 animate-pulse" aria-hidden="true">
			{#each Array(3) as _}
				<article class="min-h-64 rounded-xl border p-4" style="border-color: var(--app-border); background-color: var(--app-bg);">
					<div class="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
						<div class="space-y-3">
							<div class="h-5 w-52 rounded" style={blockStyle}></div>
							<div class="flex gap-2">
								<div class="h-6 w-24 rounded-full" style={softBlockStyle}></div>
								<div class="h-6 w-20 rounded-full" style={softBlockStyle}></div>
							</div>
						</div>
					</div>
					<div class="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
						{#each Array(5) as _}
							<div>
								<div class="h-3 w-24 rounded" style={blockStyle}></div>
								<div class="mt-2 h-4 w-28 rounded" style={softBlockStyle}></div>
							</div>
						{/each}
					</div>
					<div class="mt-5 rounded-xl border p-3" style="border-color: var(--app-border); background-color: var(--app-card-bg);">
						<div class="h-4 w-36 rounded" style={blockStyle}></div>
						<div class="mt-3 flex flex-wrap gap-2">
							{#each Array(4) as _}
								<div class="h-9 w-32 rounded-lg" style={softBlockStyle}></div>
							{/each}
						</div>
					</div>
				</article>
			{/each}
		</div>
	{:else}
		<div class="flex flex-col items-center justify-center px-6 py-12 text-center">
			<div class="mb-3 h-8 w-8 animate-spin rounded-full border-4 border-t-transparent" style="border-color: var(--app-border); border-top-color: var(--app-accent);" aria-hidden="true"></div>
			<p class="text-sm font-medium" style="color: var(--app-muted);">{message}</p>
		</div>
	{/if}
	{#if children}
		<div class="mt-4">
			{@render children()}
		</div>
	{/if}
</div>
