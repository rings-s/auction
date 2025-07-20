<script>
	/** @type {string} */
	let size = $props('md'); // 'sm', 'md', 'lg', 'xl'
	/** @type {string} */
	let color = $props('blue'); // 'blue', 'white', 'gray', 'green', 'red'
	/** @type {string} */
	let variant = $props('spinner'); // 'spinner', 'dots', 'pulse', 'bars'
	/** @type {string} */
	let className = $props('');
	/** @type {boolean} */
	let overlay = $props(false);

	const sizeClasses = {
		sm: 'w-4 h-4',
		md: 'w-6 h-6',
		lg: 'w-8 h-8',
		xl: 'w-12 h-12'
	};

	const colorClasses = {
		blue: 'text-blue-600',
		white: 'text-white',
		gray: 'text-gray-600',
		green: 'text-green-600',
		red: 'text-red-600'
	};

	let sizeClass = $derived(sizeClasses[size] || sizeClasses.md);
	let colorClass = $derived(colorClasses[color] || colorClasses.blue);
</script>

{#if overlay}
	<div
		class="bg-opacity-50 fixed inset-0 z-50 flex items-center justify-center bg-black backdrop-blur-sm"
	>
		<div class="rounded-2xl bg-white p-6 shadow-2xl">
			<svelte:self {size} {color} {variant} />
		</div>
	</div>
{:else if variant === 'spinner'}
	<div
		class="loading-spinner {sizeClass} {colorClass} {className}"
		role="status"
		aria-label="Loading"
	>
		<svg class="animate-spin" fill="none" viewBox="0 0 24 24">
			<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"
			></circle>
			<path
				class="opacity-75"
				fill="currentColor"
				d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
			></path>
		</svg>
		<span class="sr-only">Loading...</span>
	</div>
{:else if variant === 'dots'}
	<div class="loading-dots flex space-x-1 {className}" role="status" aria-label="Loading">
		<div class="h-2 w-2 animate-pulse rounded-full bg-current" style="animation-delay: 0ms;"></div>
		<div
			class="h-2 w-2 animate-pulse rounded-full bg-current"
			style="animation-delay: 150ms;"
		></div>
		<div
			class="h-2 w-2 animate-pulse rounded-full bg-current"
			style="animation-delay: 300ms;"
		></div>
		<span class="sr-only">Loading...</span>
	</div>
{:else if variant === 'pulse'}
	<div
		class="loading-pulse {sizeClass} {colorClass} {className}"
		role="status"
		aria-label="Loading"
	>
		<div class="h-full w-full animate-ping rounded-full bg-current"></div>
		<span class="sr-only">Loading...</span>
	</div>
{:else if variant === 'bars'}
	<div class="loading-bars flex items-end space-x-1 {className}" role="status" aria-label="Loading">
		<div
			class="w-1 animate-bounce rounded-full bg-current"
			style="height: 16px; animation-delay: 0ms;"
		></div>
		<div
			class="w-1 animate-bounce rounded-full bg-current"
			style="height: 20px; animation-delay: 100ms;"
		></div>
		<div
			class="w-1 animate-bounce rounded-full bg-current"
			style="height: 12px; animation-delay: 200ms;"
		></div>
		<div
			class="w-1 animate-bounce rounded-full bg-current"
			style="height: 18px; animation-delay: 300ms;"
		></div>
		<span class="sr-only">Loading...</span>
	</div>
{/if}

<style>
	.loading-spinner {
		display: inline-block;
	}

	.loading-dots {
		display: inline-flex;
	}

	.loading-pulse {
		display: inline-block;
		position: relative;
	}

	.loading-bars {
		display: inline-flex;
		height: 24px;
	}

	/* Custom animation for dots */
	.loading-dots > div {
		animation: dot-pulse 1.4s ease-in-out infinite both;
	}

	.loading-dots > div:nth-child(1) {
		animation-delay: -0.32s;
	}
	.loading-dots > div:nth-child(2) {
		animation-delay: -0.16s;
	}

	@keyframes dot-pulse {
		0%,
		80%,
		100% {
			transform: scale(0.8);
			opacity: 0.5;
		}
		40% {
			transform: scale(1);
			opacity: 1;
		}
	}

	/* Custom animation for bars */
	.loading-bars > div {
		animation: bar-bounce 1.2s ease-in-out infinite;
	}

	@keyframes bar-bounce {
		0%,
		80%,
		100% {
			transform: scaleY(0.6);
		}
		40% {
			transform: scaleY(1);
		}
	}
</style>
