<script>
	/** @type {string} */
	let tag = $props('span');
	/** @type {string} */
	let className = $props('');
</script>

<svelte:element this={tag} class="sr-only {className}" role={tag === 'div' ? 'none' : undefined}>
	<slot />
</svelte:element>

<style>
	.sr-only {
		position: absolute;
		width: 1px;
		height: 1px;
		padding: 0;
		margin: -1px;
		overflow: hidden;
		clip: rect(0, 0, 0, 0);
		white-space: nowrap;
		border: 0;
	}

	/* Ensure content is still selectable by screen readers */
	.sr-only:not(:focus):not(:active) {
		clip-path: inset(50%);
	}
</style>
