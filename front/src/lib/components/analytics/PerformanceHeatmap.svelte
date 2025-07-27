<script>
	import { onMount } from 'svelte';
	import { fade, scale } from 'svelte/transition';
	import { tweened } from 'svelte/motion';
	import { cubicOut } from 'svelte/easing';

	export let data = [];
	export let title = 'Performance Heatmap';
	export let metrics = ['revenue', 'expenses', 'occupancy', 'maintenance'];
	export let height = 400;
	export let loading = false;

	let heatmapContainer;
	let hoveredCell = null;
	let mounted = false;

	const animationProgress = tweened(0, {
		duration: 1500,
		easing: cubicOut
	});

	onMount(() => {
		mounted = true;
		animationProgress.set(1);
	});

	$: processedData = processHeatmapData(data, metrics);
	$: maxValue = Math.max(...processedData.flatMap((row) => row.values));

	function processHeatmapData(rawData, selectedMetrics) {
		if (!rawData || rawData.length === 0) return [];

		return rawData.map((item) => ({
			label: item.title || item.name || 'Property',
			values: selectedMetrics.map((metric) => {
				const value = item[metric] || 0;
				return typeof value === 'number' ? value : 0;
			})
		}));
	}

	function getHeatmapColor(value, max) {
		if (max === 0) return 'rgba(156, 163, 175, 0.3)';

		const intensity = value / max;
		const hue = intensity * 120; // Green (120) to Red (0)
		const saturation = 70 + intensity * 30; // 70% to 100%
		const lightness = 95 - intensity * 45; // 95% to 50%

		return `hsl(${hue}, ${saturation}%, ${lightness}%)`;
	}

	function formatValue(value, metric) {
		if (metric.includes('rate') || metric.includes('percentage')) {
			return `${value.toFixed(1)}%`;
		}
		if (metric.includes('revenue') || metric.includes('expense') || metric.includes('income')) {
			return `${value.toLocaleString()} SAR`;
		}
		return value.toLocaleString();
	}

	function handleCellHover(rowIndex, colIndex, value, metric) {
		hoveredCell = {
			row: rowIndex,
			col: colIndex,
			value,
			metric: metrics[colIndex],
			property: processedData[rowIndex]?.label || 'Unknown'
		};
	}

	function handleCellLeave() {
		hoveredCell = null;
	}

	const metricLabels = {
		revenue: 'Revenue',
		expenses: 'Expenses',
		occupancy: 'Occupancy',
		maintenance: 'Maintenance',
		roi: 'ROI',
		profit: 'Profit'
	};
</script>

<div class="heatmap-container" in:fade={{ duration: 400 }}>
	<div class="heatmap-header mb-6">
		<h3 class="font-sans text-xl font-semibold tracking-tight text-gray-900 dark:text-gray-100">
			{title}
		</h3>
		<p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
			Interactive performance comparison across properties
		</p>
	</div>

	{#if loading}
		<div class="loading-state" in:scale={{ duration: 300 }}>
			<div class="flex h-64 items-center justify-center">
				<div class="flex flex-col items-center space-y-4">
					<div
						class="h-12 w-12 animate-spin rounded-full border-4 border-indigo-200 border-t-indigo-600"
					></div>
					<p class="text-sm text-gray-600 dark:text-gray-400">Generating heatmap...</p>
				</div>
			</div>
		</div>
	{:else if processedData.length === 0}
		<div class="empty-state" in:scale={{ duration: 300 }}>
			<div class="flex h-64 flex-col items-center justify-center text-center">
				<div class="mb-4 text-6xl">📊</div>
				<h4 class="mb-2 text-lg font-medium text-gray-900 dark:text-gray-100">No Data Available</h4>
				<p class="text-gray-600 dark:text-gray-400">
					Performance data will appear here once properties are analyzed
				</p>
			</div>
		</div>
	{:else}
		<div class="heatmap-wrapper" style="height: {height}px;">
			<!-- Metric Labels -->
			<div class="metric-labels">
				{#each metrics as metric, index}
					<div class="metric-label" in:fade={{ duration: 300, delay: index * 100 }}>
						{metricLabels[metric] || metric}
					</div>
				{/each}
			</div>

			<!-- Heatmap Grid -->
			<div class="heatmap-grid" bind:this={heatmapContainer}>
				{#each processedData as row, rowIndex}
					<div class="heatmap-row" in:fade={{ duration: 400, delay: rowIndex * 50 }}>
						<!-- Property Label -->
						<div class="property-label">
							<span title={row.label}>
								{row.label.length > 15 ? row.label.substring(0, 15) + '...' : row.label}
							</span>
						</div>

						<!-- Heatmap Cells -->
						<div class="heatmap-cells">
							{#each row.values as value, colIndex}
								<div
									class="heatmap-cell"
									style="background-color: {getHeatmapColor(
										value,
										maxValue
									)}; opacity: {$animationProgress}"
									on:mouseenter={() =>
										handleCellHover(rowIndex, colIndex, value, metrics[colIndex])}
									on:mouseleave={handleCellLeave}
									in:scale={{ duration: 300, delay: (rowIndex * metrics.length + colIndex) * 50 }}
									role="gridcell"
									tabindex="0"
								>
									<span class="cell-value">
										{formatValue(value, metrics[colIndex])}
									</span>
								</div>
							{/each}
						</div>
					</div>
				{/each}
			</div>

			<!-- Tooltip -->
			{#if hoveredCell}
				<div class="heatmap-tooltip" in:scale={{ duration: 200 }}>
					<div class="tooltip-header">
						<strong>{hoveredCell.property}</strong>
					</div>
					<div class="tooltip-content">
						<span class="metric-name"
							>{metricLabels[hoveredCell.metric] || hoveredCell.metric}:</span
						>
						<span class="metric-value">{formatValue(hoveredCell.value, hoveredCell.metric)}</span>
					</div>
				</div>
			{/if}

			<!-- Color Legend -->
			<div class="color-legend mt-6" in:fade={{ duration: 500, delay: 600 }}>
				<div class="legend-label">Performance Scale:</div>
				<div class="legend-gradient">
					<div class="gradient-bar"></div>
					<div class="legend-markers">
						<span>Low</span>
						<span>High</span>
					</div>
				</div>
			</div>
		</div>
	{/if}
</div>

<style>
	.heatmap-container {
		background: white;
		border-radius: 1rem;
		border: 1px solid #e5e7eb;
		padding: 1.5rem;
		box-shadow:
			0 4px 6px -1px rgba(0, 0, 0, 0.1),
			0 2px 4px -1px rgba(0, 0, 0, 0.06);
		background: linear-gradient(
			135deg,
			rgba(255, 255, 255, 0.95) 0%,
			rgba(249, 250, 251, 0.9) 100%
		);
	}

	:global(.dark) .heatmap-container {
		background: #1f2937;
		border-color: #374151;
		background: linear-gradient(135deg, rgba(31, 41, 55, 0.95) 0%, rgba(17, 24, 39, 0.9) 100%);
	}

	.heatmap-wrapper {
		position: relative;
		overflow: auto;
	}

	.metric-labels {
		display: flex;
		margin-bottom: 0.5rem;
		margin-left: 8rem;
	}

	.metric-label {
		flex: 1;
		font-size: 0.75rem;
		font-weight: 500;
		color: #6b7280;
		text-align: center;
		padding: 0.25rem 0.5rem;
		min-width: 80px;
	}

	:global(.dark) .metric-label {
		color: #9ca3af;
	}

	.heatmap-grid {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
	}

	.heatmap-row {
		display: flex;
		align-items: center;
	}

	.property-label {
		width: 8rem;
		font-size: 0.875rem;
		font-weight: 500;
		color: #374151;
		padding-right: 1rem;
		text-align: right;
		flex-shrink: 0;
	}

	:global(.dark) .property-label {
		color: #d1d5db;
	}

	.heatmap-cells {
		display: flex;
		flex: 1;
		gap: 0.25rem;
	}

	.heatmap-cell {
		flex: 1;
		height: 3rem;
		border-radius: 0.5rem;
		border: 1px solid #e5e7eb;
		display: flex;
		align-items: center;
		justify-content: center;
		cursor: pointer;
		transition: all 0.2s;
		min-width: 80px;
	}

	.heatmap-cell:hover {
		transform: scale(1.05);
		box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
	}

	:global(.dark) .heatmap-cell {
		border-color: #4b5563;
	}

	.cell-value {
		font-size: 0.75rem;
		font-weight: 500;
		color: #1f2937;
		text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
	}

	:global(.dark) .cell-value {
		color: #e5e7eb;
	}

	.heatmap-tooltip {
		position: absolute;
		z-index: 50;
		background: #111827;
		color: white;
		padding: 0.75rem;
		border-radius: 0.5rem;
		box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
		pointer-events: none;
		top: 20px;
		right: 20px;
		min-width: 200px;
	}

	:global(.dark) .heatmap-tooltip {
		background: #f9fafb;
		color: #111827;
	}

	.tooltip-header {
		font-size: 0.875rem;
		font-weight: 600;
		margin-bottom: 0.25rem;
	}

	.tooltip-content {
		display: flex;
		justify-content: space-between;
		font-size: 0.875rem;
	}

	.metric-name {
		font-weight: 500;
	}

	.metric-value {
		font-weight: 600;
	}

	.color-legend {
		display: flex;
		align-items: center;
		gap: 1rem;
	}

	.legend-label {
		font-size: 0.875rem;
		font-weight: 500;
		color: #6b7280;
	}

	:global(.dark) .legend-label {
		color: #9ca3af;
	}

	.legend-gradient {
		flex: 1;
		max-width: 18rem;
	}

	.gradient-bar {
		height: 1rem;
		border-radius: 0.5rem;
		background: linear-gradient(
			to right,
			hsl(120, 70%, 95%),
			hsl(90, 80%, 85%),
			hsl(60, 90%, 75%),
			hsl(30, 95%, 65%),
			hsl(0, 100%, 50%)
		);
	}

	.legend-markers {
		display: flex;
		justify-content: space-between;
		font-size: 0.75rem;
		color: #6b7280;
		margin-top: 0.25rem;
	}

	:global(.dark) .legend-markers {
		color: #9ca3af;
	}

	.loading-state,
	.empty-state {
		background: #f9fafb;
		border-radius: 0.75rem;
		border: 2px dashed #d1d5db;
	}

	:global(.dark) .loading-state,
	:global(.dark) .empty-state {
		background: rgba(55, 65, 81, 0.5);
		border-color: #4b5563;
	}
</style>
