<script>
	import { createEventDispatcher, onMount } from 'svelte';
	import { browser } from '$app/environment';
	import FadeInUp from '$lib/components/animations/FadeInUp.svelte';

	const dispatch = createEventDispatcher();

	/** @type {boolean} */
	export let isOpen = false;
	/** @type {string} */
	export let title = '';
	/** @type {string} */
	export let position = 'bottom'; // 'bottom', 'top', 'left', 'right'
	/** @type {boolean} */
	export let showOverlay = true;
	/** @type {boolean} */
	export let closeOnOverlayClick = true;
	/** @type {string} */
	export let maxHeight = '80vh';
	/** @type {string} */
	export let className = '';

	let drawerElement;
	let overlayElement;
	let startY = 0;
	let currentY = 0;
	let isDragging = false;
	let translateY = 0;

	onMount(() => {
		if (browser) {
			// Prevent body scroll when drawer is open
			if (isOpen) {
				document.body.style.overflow = 'hidden';
			}

			return () => {
				document.body.style.overflow = '';
			};
		}
	});

	// Handle body scroll prevention
	$: if (browser) {
		if (isOpen) {
			document.body.style.overflow = 'hidden';
		} else {
			document.body.style.overflow = '';
		}
	}

	function handleOverlayClick() {
		if (closeOnOverlayClick) {
			closeDrawer();
		}
	}

	function closeDrawer() {
		isOpen = false;
		dispatch('close');
	}

	function handleKeydown(event) {
		if (event.key === 'Escape') {
			closeDrawer();
		}
	}

	// Touch event handlers for swipe-to-close
	function handleTouchStart(event) {
		if (position !== 'bottom') return;

		isDragging = true;
		startY = event.touches[0].clientY;
		currentY = startY;
		translateY = 0;
	}

	function handleTouchMove(event) {
		if (!isDragging || position !== 'bottom') return;

		currentY = event.touches[0].clientY;
		const deltaY = currentY - startY;

		// Only allow downward swipes
		if (deltaY > 0) {
			translateY = deltaY;
			if (drawerElement) {
				drawerElement.style.transform = `translateY(${translateY}px)`;
			}
		}
	}

	function handleTouchEnd() {
		if (!isDragging || position !== 'bottom') return;

		isDragging = false;

		// Close drawer if swiped down more than 100px
		if (translateY > 100) {
			closeDrawer();
		} else {
			// Snap back to original position
			if (drawerElement) {
				drawerElement.style.transform = 'translateY(0)';
			}
		}

		translateY = 0;
	}

	function getDrawerClasses() {
		const baseClasses = 'mobile-drawer';
		const positionClass = `drawer-${position}`;
		const stateClass = isOpen ? 'drawer-open' : 'drawer-closed';

		return `${baseClasses} ${positionClass} ${stateClass} ${className}`.trim();
	}

	function getOverlayClasses() {
		return `drawer-overlay ${isOpen ? 'overlay-visible' : 'overlay-hidden'}`;
	}
</script>

{#if isOpen}
	<!-- Overlay -->
	{#if showOverlay}
		<div
			bind:this={overlayElement}
			class={getOverlayClasses()}
			on:click={handleOverlayClick}
			on:keydown={handleKeydown}
			role="button"
			tabindex="-1"
		></div>
	{/if}

	<!-- Drawer -->
	<div
		bind:this={drawerElement}
		class={getDrawerClasses()}
		style="max-height: {maxHeight};"
		on:touchstart={handleTouchStart}
		on:touchmove={handleTouchMove}
		on:touchend={handleTouchEnd}
		on:keydown={handleKeydown}
		role="dialog"
		aria-modal="true"
		aria-label={title}
	>
		{#if position === 'bottom'}
			<!-- Drag handle for bottom drawer -->
			<div class="drag-handle">
				<div class="drag-indicator"></div>
			</div>
		{/if}

		<!-- Header -->
		{#if title}
			<div class="drawer-header">
				<h3 class="drawer-title">{title}</h3>
				<button class="close-button" on:click={closeDrawer} aria-label="Close drawer">
					<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M6 18L18 6M6 6l12 12"
						/>
					</svg>
				</button>
			</div>
		{/if}

		<!-- Content -->
		<div class="drawer-content">
			<FadeInUp delay={100}>
				<slot />
			</FadeInUp>
		</div>
	</div>
{/if}

<style>
	.drawer-overlay {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background: rgba(0, 0, 0, 0.5);
		backdrop-filter: blur(4px);
		z-index: 9998;
		transition: opacity 300ms ease-out;
	}

	.overlay-visible {
		opacity: 1;
	}

	.overlay-hidden {
		opacity: 0;
		pointer-events: none;
	}

	.mobile-drawer {
		position: fixed;
		background: white;
		z-index: 9999;
		transition: transform 300ms cubic-bezier(0.4, 0, 0.2, 1);
		overflow-y: auto;
		overscroll-behavior: contain;
	}

	/* Bottom drawer (default) */
	.drawer-bottom {
		bottom: 0;
		left: 0;
		right: 0;
		border-radius: 1rem 1rem 0 0;
		box-shadow:
			0 -20px 25px -5px rgba(0, 0, 0, 0.1),
			0 -10px 10px -5px rgba(0, 0, 0, 0.04);
	}

	.drawer-bottom.drawer-open {
		transform: translateY(0);
	}

	.drawer-bottom.drawer-closed {
		transform: translateY(100%);
	}

	/* Top drawer */
	.drawer-top {
		top: 0;
		left: 0;
		right: 0;
		border-radius: 0 0 1rem 1rem;
		box-shadow:
			0 20px 25px -5px rgba(0, 0, 0, 0.1),
			0 10px 10px -5px rgba(0, 0, 0, 0.04);
	}

	.drawer-top.drawer-open {
		transform: translateY(0);
	}

	.drawer-top.drawer-closed {
		transform: translateY(-100%);
	}

	/* Left drawer */
	.drawer-left {
		top: 0;
		bottom: 0;
		left: 0;
		width: 85%;
		max-width: 400px;
		border-radius: 0 1rem 1rem 0;
		box-shadow:
			20px 0 25px -5px rgba(0, 0, 0, 0.1),
			10px 0 10px -5px rgba(0, 0, 0, 0.04);
	}

	.drawer-left.drawer-open {
		transform: translateX(0);
	}

	.drawer-left.drawer-closed {
		transform: translateX(-100%);
	}

	/* Right drawer */
	.drawer-right {
		top: 0;
		bottom: 0;
		right: 0;
		width: 85%;
		max-width: 400px;
		border-radius: 1rem 0 0 1rem;
		box-shadow:
			-20px 0 25px -5px rgba(0, 0, 0, 0.1),
			-10px 0 10px -5px rgba(0, 0, 0, 0.04);
	}

	.drawer-right.drawer-open {
		transform: translateX(0);
	}

	.drawer-right.drawer-closed {
		transform: translateX(100%);
	}

	.drag-handle {
		display: flex;
		justify-content: center;
		padding: 0.75rem;
		cursor: grab;
	}

	.drag-handle:active {
		cursor: grabbing;
	}

	.drag-indicator {
		width: 3rem;
		height: 0.25rem;
		background: #d1d5db;
		border-radius: 0.125rem;
	}

	.drawer-header {
		display: flex;
		align-items: center;
		justify-content: between;
		padding: 1rem 1.5rem;
		border-bottom: 1px solid #e5e7eb;
	}

	.drawer-title {
		font-size: 1.25rem;
		font-weight: 600;
		color: #111827;
		margin: 0;
		flex: 1;
	}

	.close-button {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 2rem;
		height: 2rem;
		border: none;
		background: none;
		color: #6b7280;
		border-radius: 0.5rem;
		cursor: pointer;
		transition: all 200ms;
	}

	.close-button:hover {
		background: #f3f4f6;
		color: #374151;
	}

	.drawer-content {
		padding: 1.5rem;
		flex: 1;
		overflow-y: auto;
	}

	/* Dark mode support */
	@media (prefers-color-scheme: dark) {
		.mobile-drawer {
			background: #1f2937;
		}

		.drawer-header {
			border-bottom-color: #374151;
		}

		.drawer-title {
			color: #f9fafb;
		}

		.drag-indicator {
			background: #6b7280;
		}

		.close-button {
			color: #9ca3af;
		}

		.close-button:hover {
			background: #374151;
			color: #d1d5db;
		}
	}

	/* Reduced motion */
	@media (prefers-reduced-motion: reduce) {
		.mobile-drawer,
		.drawer-overlay {
			transition: none;
		}
	}

	/* Large screens - convert to modal */
	@media (min-width: 1024px) {
		.drawer-bottom,
		.drawer-top {
			position: fixed;
			top: 50%;
			left: 50%;
			transform: translate(-50%, -50%);
			width: 90%;
			max-width: 600px;
			max-height: 80vh;
			border-radius: 1rem;
			box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
		}

		.drawer-bottom.drawer-open,
		.drawer-top.drawer-open {
			transform: translate(-50%, -50%) scale(1);
		}

		.drawer-bottom.drawer-closed,
		.drawer-top.drawer-closed {
			transform: translate(-50%, -50%) scale(0.95);
			opacity: 0;
		}
	}

	/* Print styles */
	@media print {
		.mobile-drawer,
		.drawer-overlay {
			display: none;
		}
	}
</style>
