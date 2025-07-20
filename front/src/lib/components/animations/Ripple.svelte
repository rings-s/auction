<script>
	/** @type {string} */
	let color = $props('rgba(255, 255, 255, 0.6)');
	/** @type {number} */
	let duration = $props(600);
	/** @type {string} */
	let className = $props('');
	/** @type {boolean} */
	let disabled = $props(false);

	// Event handlers
	let onclick = $props();
	let onkeydown = $props();

	let element = $state();
	let ripples = $state([]);
	let nextId = $state(0);

	function createRipple(event) {
		if (disabled) return;

		const rect = element.getBoundingClientRect();
		const size = Math.max(rect.width, rect.height);
		const x = event.clientX - rect.left - size / 2;
		const y = event.clientY - rect.top - size / 2;

		const ripple = {
			id: nextId++,
			x,
			y,
			size,
			color,
			duration
		};

		ripples = [...ripples, ripple];

		// Remove ripple after animation completes
		setTimeout(() => {
			ripples = ripples.filter((r) => r.id !== ripple.id);
		}, duration);

		// Dispatch click event
		onclick?.(event);
	}

	function handleKeydown(event) {
		if (event.key === 'Enter' || event.key === ' ') {
			event.preventDefault();

			// Create ripple at center for keyboard interaction
			const rect = element.getBoundingClientRect();
			const centerX = rect.width / 2;
			const centerY = rect.height / 2;

			const syntheticEvent = {
				clientX: rect.left + centerX,
				clientY: rect.top + centerY
			};

			createRipple(syntheticEvent);
			onkeydown?.(event);
		}
	}
</script>

<div
	bind:this={element}
	class="ripple-container relative overflow-hidden {className}"
	class:disabled
	on:click={createRipple}
	on:keydown={handleKeydown}
	role="button"
	tabindex="0"
>
	<slot />

	{#each ripples as ripple (ripple.id)}
		<span
			class="ripple pointer-events-none absolute rounded-full"
			style="
                left: {ripple.x}px;
                top: {ripple.y}px;
                width: {ripple.size}px;
                height: {ripple.size}px;
                background-color: {ripple.color};
                animation: ripple {ripple.duration}ms ease-out forwards;
            "
		></span>
	{/each}
</div>

<style>
	.ripple-container {
		cursor: pointer;
		user-select: none;
		-webkit-tap-highlight-color: transparent;
	}

	.ripple-container:focus {
		outline: 2px solid #3b82f6;
		outline-offset: 2px;
	}

	.ripple-container.disabled {
		cursor: not-allowed;
		opacity: 0.6;
	}

	.ripple {
		transform: scale(0);
		opacity: 0.6;
	}

	@keyframes ripple {
		to {
			transform: scale(4);
			opacity: 0;
		}
	}
</style>
