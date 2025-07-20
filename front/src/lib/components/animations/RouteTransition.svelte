<script>
	import { beforeNavigate, afterNavigate } from '$app/navigation';
	import { navigating } from '$app/stores';
	import { onMount } from 'svelte';
	import LoadingSpinner from './LoadingSpinner.svelte';

	/** @type {string} */
	export let variant = 'slide'; // 'slide', 'fade', 'scale', 'blur'
	/** @type {number} */
	export let duration = 400;
	/** @type {boolean} */
	export let showLoadingIndicator = true;
	/** @type {string} */
	export let loadingText = 'Loading...';

	let isNavigating = false;
	let navigationProgress = 0;
	let routeContainer;
	let reduceMotion = false;

	onMount(() => {
		// Check for reduced motion preference
		if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
			reduceMotion = true;
		}

		// Set CSS custom properties for animations
		if (routeContainer) {
			routeContainer.style.setProperty('--transition-duration', `${duration}ms`);
		}
	});

	// Handle navigation state
	$: isNavigating = $navigating !== null;

	beforeNavigate((navigation) => {
		if (!reduceMotion && routeContainer) {
			// Add exit animation
			routeContainer.classList.add(`route-exit-${variant}`);
		}
		navigationProgress = 0;
	});

	afterNavigate((navigation) => {
		if (!reduceMotion && routeContainer) {
			// Remove exit animation and add enter animation
			routeContainer.classList.remove(`route-exit-${variant}`);
			routeContainer.classList.add(`route-enter-${variant}`);

			// Remove enter animation after duration
			setTimeout(() => {
				if (routeContainer) {
					routeContainer.classList.remove(`route-enter-${variant}`);
				}
			}, duration);
		}
		navigationProgress = 100;
	});

	// Simulate progress for better UX
	$: if (isNavigating) {
		const interval = setInterval(() => {
			navigationProgress = Math.min(navigationProgress + Math.random() * 10, 90);
		}, 100);

		setTimeout(() => clearInterval(interval), duration * 0.8);
	}
</script>

<!-- Loading Indicator -->
{#if isNavigating && showLoadingIndicator && !reduceMotion}
	<div class="route-loading-overlay">
		<div class="loading-content">
			<LoadingSpinner size="md" variant="spinner" />
			<p class="loading-text">{loadingText}</p>
			<div class="progress-bar">
				<div class="progress-fill" style="width: {navigationProgress}%"></div>
			</div>
		</div>
	</div>
{/if}

<!-- Route Content -->
<div
	bind:this={routeContainer}
	class="route-transition-container {variant}"
	class:reduce-motion={reduceMotion}
	class:navigating={isNavigating}
>
	<slot />
</div>

<style>
	.route-transition-container {
		position: relative;
		width: 100%;
		min-height: 100vh;
		transition-property: transform, opacity, filter;
		transition-duration: var(--transition-duration, 400ms);
		transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
	}

	/* Loading Overlay */
	.route-loading-overlay {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background: rgba(255, 255, 255, 0.9);
		backdrop-filter: blur(8px);
		z-index: 9999;
		display: flex;
		align-items: center;
		justify-content: center;
		animation: fadeIn 200ms ease-out;
	}

	.loading-content {
		text-align: center;
		padding: 2rem;
		background: white;
		border-radius: 1rem;
		box-shadow:
			0 20px 25px -5px rgba(0, 0, 0, 0.1),
			0 10px 10px -5px rgba(0, 0, 0, 0.04);
		border: 1px solid rgba(0, 0, 0, 0.05);
		max-width: 300px;
		width: 90%;
	}

	.loading-text {
		margin: 1rem 0 0.5rem 0;
		color: #374151;
		font-weight: 500;
		font-size: 0.875rem;
	}

	.progress-bar {
		width: 100%;
		height: 4px;
		background: #e5e7eb;
		border-radius: 2px;
		overflow: hidden;
		margin-top: 1rem;
	}

	.progress-fill {
		height: 100%;
		background: linear-gradient(90deg, #3b82f6, #06b6d4);
		border-radius: 2px;
		transition: width 200ms ease-out;
	}

	/* Slide Transitions */
	.slide :global(.route-exit-slide) {
		transform: translateX(-100%);
		opacity: 0.8;
	}

	.slide :global(.route-enter-slide) {
		transform: translateX(100%);
		opacity: 0.8;
		animation: routeSlideIn var(--transition-duration) cubic-bezier(0.4, 0, 0.2, 1) forwards;
	}

	@keyframes routeSlideIn {
		to {
			transform: translateX(0);
			opacity: 1;
		}
	}

	/* Fade Transitions */
	.fade :global(.route-exit-fade) {
		opacity: 0;
		transform: scale(0.95);
	}

	.fade :global(.route-enter-fade) {
		opacity: 0;
		transform: scale(1.05);
		animation: routeFadeIn var(--transition-duration) cubic-bezier(0.4, 0, 0.2, 1) forwards;
	}

	@keyframes routeFadeIn {
		to {
			opacity: 1;
			transform: scale(1);
		}
	}

	/* Scale Transitions */
	.scale :global(.route-exit-scale) {
		transform: scale(0.8);
		opacity: 0;
	}

	.scale :global(.route-enter-scale) {
		transform: scale(1.2);
		opacity: 0;
		animation: routeScaleIn var(--transition-duration) cubic-bezier(0.4, 0, 0.2, 1) forwards;
	}

	@keyframes routeScaleIn {
		to {
			transform: scale(1);
			opacity: 1;
		}
	}

	/* Blur Transitions */
	.blur :global(.route-exit-blur) {
		filter: blur(8px);
		opacity: 0.5;
		transform: translateY(-20px);
	}

	.blur :global(.route-enter-blur) {
		filter: blur(8px);
		opacity: 0.5;
		transform: translateY(20px);
		animation: routeBlurIn var(--transition-duration) cubic-bezier(0.4, 0, 0.2, 1) forwards;
	}

	@keyframes routeBlurIn {
		to {
			filter: blur(0);
			opacity: 1;
			transform: translateY(0);
		}
	}

	/* Reduced Motion */
	.reduce-motion,
	.reduce-motion * {
		animation-duration: 0.01ms !important;
		transition-duration: 0.01ms !important;
	}

	.reduce-motion .route-loading-overlay {
		display: none;
	}

	/* Dark mode support */
	@media (prefers-color-scheme: dark) {
		.route-loading-overlay {
			background: rgba(17, 24, 39, 0.9);
		}

		.loading-content {
			background: #1f2937;
			color: #f9fafb;
		}

		.loading-text {
			color: #d1d5db;
		}
	}

	/* High contrast mode */
	@media (prefers-contrast: high) {
		.route-loading-overlay {
			background: rgba(255, 255, 255, 0.95);
		}

		.loading-content {
			border: 2px solid #000;
		}
	}

	/* Mobile optimizations */
	@media (max-width: 768px) {
		.slide :global(.route-exit-slide) {
			transform: translateX(-50%);
		}

		.slide :global(.route-enter-slide) {
			transform: translateX(50%);
		}

		.loading-content {
			padding: 1.5rem;
		}
	}

	@keyframes fadeIn {
		from {
			opacity: 0;
		}
		to {
			opacity: 1;
		}
	}
</style>
