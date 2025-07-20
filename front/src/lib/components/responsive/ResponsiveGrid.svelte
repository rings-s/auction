<script>
	import { browser } from '$app/environment';

	/** @type {number} */
	let minItemWidth = $props(280); // Minimum width for each grid item
	/** @type {number} */
	let gap = $props(16); // Gap between items in pixels
	/** @type {string} */
	let className = $props('');
	/** @type {boolean} */
	let autoFit = $props(true); // Auto-fit items to available space
	/** @type {number} */
	let maxColumns = $props(4); // Maximum number of columns
	/** @type {number} */
	let minColumns = $props(1); // Minimum number of columns

	let gridElement = $state();
	let columns = $state(1);
	let containerWidth = $state(0);

	$effect(() => {
		if (browser && gridElement) {
			updateLayout();

			// Set up resize observer
			const resizeObserver = new ResizeObserver((entries) => {
				for (let entry of entries) {
					containerWidth = entry.contentRect.width;
					updateLayout();
				}
			});

			resizeObserver.observe(gridElement);

			return () => {
				resizeObserver.disconnect();
			};
		}
	});

	// Update layout when props change
	$effect(() => {
		if (browser && gridElement && (minItemWidth || gap || maxColumns || minColumns)) {
			updateLayout();
		}
	});

	function updateLayout() {
		if (!gridElement || containerWidth === 0) return;

		if (autoFit) {
			// Calculate optimal number of columns
			const availableWidth = containerWidth - gap;
			const itemsPerRow = Math.floor(availableWidth / (minItemWidth + gap));
			columns = Math.max(minColumns, Math.min(maxColumns, itemsPerRow));
		}

		// Update CSS custom properties
		gridElement.style.setProperty('--grid-columns', columns.toString());
		gridElement.style.setProperty('--grid-gap', `${gap}px`);
		gridElement.style.setProperty('--min-item-width', `${minItemWidth}px`);
	}
</script>

<div bind:this={gridElement} class="responsive-grid {className}" bind:clientWidth={containerWidth}>
	<slot {columns} {containerWidth} />
</div>

<style>
	.responsive-grid {
		display: grid;
		grid-template-columns: repeat(var(--grid-columns, 1), 1fr);
		gap: var(--grid-gap, 16px);
		width: 100%;

		/* Fallback for browsers without CSS custom properties */
		grid-template-columns: repeat(auto-fit, minmax(var(--min-item-width, 280px), 1fr));
	}

	/* Mobile-first responsive breakpoints */
	@media (max-width: 640px) {
		.responsive-grid {
			grid-template-columns: 1fr;
			gap: 12px;
		}
	}

	@media (min-width: 641px) and (max-width: 768px) {
		.responsive-grid {
			grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
			gap: 14px;
		}
	}

	@media (min-width: 769px) and (max-width: 1024px) {
		.responsive-grid {
			grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
			gap: 16px;
		}
	}

	@media (min-width: 1025px) {
		.responsive-grid {
			gap: 20px;
		}
	}

	/* Print styles */
	@media print {
		.responsive-grid {
			grid-template-columns: repeat(2, 1fr);
			gap: 8px;
			break-inside: avoid;
		}
	}
</style>
