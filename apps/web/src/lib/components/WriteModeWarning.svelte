<script lang="ts">
	type Props = {
		compact?: boolean;
	};

	let { compact = false }: Props = $props();
</script>

<div
	class={compact ? 'rounded-2xl p-4 text-sm' : 'rounded-2xl p-5 text-sm'}
	role="alert"
	style="border: 1px solid #f59e0b; background: #fffbeb; color: #78350f;"
>
	<p class="font-semibold">Experimental controlled write mode — not part of MVP v0.1</p>
	<p class="mt-2">
		MVP v0.1 remains read-only by default and <code>GNUCASH_WRITES_ENABLED=false</code> is the safe default.
		This write form is experimental post-MVP functionality only and should be reachable only in an explicit
		<code>APP_ENV=test</code> disposable run.
	</p>
	<ul class="mt-2 list-disc space-y-1 pl-5">
		<li>GnuCash Desktop remains the authoritative editor.</li>
		<li>Use only disposable/test copies copied into ignored runtime storage; never point this at the source or only copy.</li>
		<li>Confirm backup, audit, and lock-release evidence before treating a write-alpha run as complete.</li>
		<li>If a stale lock file remains, stop the runtime first and follow the recovery runbook; never assume a host permission error means an active writer.</li>
		<li>Never use this experimental path with your only real financial book.</li>
	</ul>
</div>
