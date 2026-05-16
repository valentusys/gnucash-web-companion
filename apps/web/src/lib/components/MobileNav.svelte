<script lang="ts">
	const navLinks = [
		{ href: '/dashboard', label: 'Dashboard', icon: 'home' },
		{ href: '/accounts', label: 'Accounts', icon: 'accounts' },
		{ href: '/transactions', label: 'Transactions', icon: 'transactions' },
	] as const;

	function iconFor(name: string, active: boolean) {
		const c = active ? 'var(--app-accent)' : 'var(--app-muted)';
		switch (name) {
			case 'home':
				return `<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="${c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>`;
			case 'accounts':
				return `<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="${c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>`;
			case 'transactions':
				return `<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="${c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>`;
			default:
				return '';
		}
	}
</script>

<nav
	class="fixed bottom-0 left-0 right-0 z-40 border-t md:hidden"
	style="background-color: var(--app-nav-bg); border-color: var(--app-nav-border);"
	aria-label="Mobile navigation"
>
	<div class="flex items-stretch justify-around safe-bottom">
		{#each navLinks as link}
			<a
				href={link.href}
				class="flex flex-1 flex-col items-center gap-0.5 py-2 text-[10px] font-medium transition-colors"
				style="color: var(--app-muted);"
			>
				<span class="h-[22px] w-[22px]" aria-hidden="true">
					{@html iconFor(link.icon, false)}
				</span>
				<span>{link.label}</span>
			</a>
		{/each}
	</div>
</nav>
