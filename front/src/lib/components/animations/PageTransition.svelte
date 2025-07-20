<script>
	import { onMount } from 'svelte';
	import { page } from '$app/stores';

	/** @type {string} */
	export let transitionType = 'slide'; // 'slide', 'fade', 'scale', 'blur'
	/** @type {number} */
	export let duration = 300;
	/** @type {string} */
	export let easing = 'cubic-bezier(0.4, 0, 0.2, 1)';
	/** @type {boolean} */
	export let reduceMotion = false;

	let pageContainer;
	let isTransitioning = false;
	let currentPath = '';

	// Check for reduced motion preference
	onMount(() => {
		if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
			reduceMotion = true;
		}
	});

	// Watch for page changes
	$: if ($page?.url?.pathname && $page.url.pathname !== currentPath) {
		handlePageChange($page.url.pathname);
	}

	function handlePageChange(newPath) {
		if (currentPath && newPath !== currentPath && !reduceMotion) {
			performTransition(newPath);
		}
		currentPath = newPath;
	}

	async function performTransition(newPath) {
		if (isTransitioning || !pageContainer) return;

		isTransitioning = true;

		// Add exit animation class
		pageContainer.classList.add(`page-exit-${transitionType}`);

		// Wait for exit animation to complete
		await new Promise((resolve) => setTimeout(resolve, duration));

		// Remove exit class and add enter class
		pageContainer.classList.remove(`page-exit-${transitionType}`);
		pageContainer.classList.add(`page-enter-${transitionType}`);

		// Wait for enter animation to complete
		await new Promise((resolve) => setTimeout(resolve, duration));

		// Cleanup
		pageContainer.classList.remove(`page-enter-${transitionType}`);
		isTransitioning = false;
	}

	function getTransitionStyles() {
		if (reduceMotion) return '';

		return `
            transition-duration: ${duration}ms;
            transition-timing-function: ${easing};
        `;
	}
</script>

<div
	bind:this={pageContainer}
	class="page-transition-container"
	style={getTransitionStyles()}
	class:reduce-motion={reduceMotion}
>
	<slot />
</div>

<style>
	.page-transition-container {
		position: relative;
		width: 100%;
		height: 100%;
		overflow-x: hidden;
	}

	/* Slide Transitions */
	:global(.page-exit-slide) {
		transform: translateX(-100%);
		opacity: 0.8;
	}

	:global(.page-enter-slide) {
		transform: translateX(100%);
		opacity: 0.8;
		animation: slideEnter var(--duration, 300ms) var(--easing, cubic-bezier(0.4, 0, 0.2, 1))
			forwards;
	}

	@keyframes slideEnter {
		to {
			transform: translateX(0);
			opacity: 1;
		}
	}

	/* Fade Transitions */
	:global(.page-exit-fade) {
		opacity: 0;
		transform: scale(0.98);
	}

	:global(.page-enter-fade) {
		opacity: 0;
		transform: scale(1.02);
		animation: fadeEnter var(--duration, 300ms) var(--easing, cubic-bezier(0.4, 0, 0.2, 1)) forwards;
	}

	@keyframes fadeEnter {
		to {
			opacity: 1;
			transform: scale(1);
		}
	}

	/* Scale Transitions */
	:global(.page-exit-scale) {
		transform: scale(0.9);
		opacity: 0.5;
	}

	:global(.page-enter-scale) {
		transform: scale(1.1);
		opacity: 0.5;
		animation: scaleEnter var(--duration, 300ms) var(--easing, cubic-bezier(0.4, 0, 0.2, 1))
			forwards;
	}

	@keyframes scaleEnter {
		to {
			transform: scale(1);
			opacity: 1;
		}
	}

	/* Blur Transitions */
	:global(.page-exit-blur) {
		filter: blur(4px);
		opacity: 0.7;
		transform: translateY(-10px);
	}

	:global(.page-enter-blur) {
		filter: blur(4px);
		opacity: 0.7;
		transform: translateY(10px);
		animation: blurEnter var(--duration, 300ms) var(--easing, cubic-bezier(0.4, 0, 0.2, 1)) forwards;
	}

	@keyframes blurEnter {
		to {
			filter: blur(0);
			opacity: 1;
			transform: translateY(0);
		}
	}

	/* Reduced motion support */
	.reduce-motion,
	.reduce-motion :global(*) {
		animation-duration: 0.01ms !important;
		animation-iteration-count: 1 !important;
		transition-duration: 0.01ms !important;
	}

	/* Mobile optimizations */
	@media (max-width: 768px) {
		:global(.page-exit-slide) {
			transform: translateX(-50%);
		}

		:global(.page-enter-slide) {
			transform: translateX(50%);
		}
	}

	/* High contrast mode support */
	@media (prefers-contrast: high) {
		:global(.page-exit-blur),
		:global(.page-enter-blur) {
			filter: none !important;
		}
	}

	/* Print styles */
	@media print {
		.page-transition-container,
		.page-transition-container :global(*) {
			animation: none !important;
			transition: none !important;
			transform: none !important;
			filter: none !important;
		}
	}
</style>
