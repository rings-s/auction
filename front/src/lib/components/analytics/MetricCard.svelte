<script>
	import { fade, scale } from 'svelte/transition';
	import { tweened } from 'svelte/motion';
	import { cubicOut } from 'svelte/easing';

	export let title = '';
	export let value = 0;
	export let previousValue = 0;
	export let formatter = (val) => val.toLocaleString();
	export let icon = '📊';
	export let color = 'indigo';
	export let trend = null; // 'up', 'down', or null
	export let subtitle = '';
	export let loading = false;

	const animatedValue = tweened(0, {
		duration: 1200,
		easing: cubicOut
	});

	$: if (typeof value === 'number') {
		animatedValue.set(value);
	}

	$: percentageChange = previousValue > 0 ? ((value - previousValue) / previousValue) * 100 : 0;
	$: changeDirection = percentageChange > 0 ? 'up' : percentageChange < 0 ? 'down' : 'neutral';

	const colorClasses = {
		indigo: {
			gradient: 'from-indigo-500 to-purple-600',
			bg: 'bg-indigo-50 dark:bg-indigo-900/20',
			text: 'text-indigo-600 dark:text-indigo-400',
			border: 'border-indigo-200 dark:border-indigo-800'
		},
		green: {
			gradient: 'from-green-500 to-emerald-600',
			bg: 'bg-green-50 dark:bg-green-900/20',
			text: 'text-green-600 dark:text-green-400',
			border: 'border-green-200 dark:border-green-800'
		},
		red: {
			gradient: 'from-red-500 to-rose-600',
			bg: 'bg-red-50 dark:bg-red-900/20',
			text: 'text-red-600 dark:text-red-400',
			border: 'border-red-200 dark:border-red-800'
		},
		blue: {
			gradient: 'from-blue-500 to-cyan-600',
			bg: 'bg-blue-50 dark:bg-blue-900/20',
			text: 'text-blue-600 dark:text-blue-400',
			border: 'border-blue-200 dark:border-blue-800'
		},
		yellow: {
			gradient: 'from-yellow-500 to-orange-600',
			bg: 'bg-yellow-50 dark:bg-yellow-900/20',
			text: 'text-yellow-600 dark:text-yellow-400',
			border: 'border-yellow-200 dark:border-yellow-800'
		}
	};

	$: selectedColor = colorClasses[color] || colorClasses.indigo;
</script>

<div class="metric-card group" in:fade={{ duration: 400 }}>
	<div class="metric-content">
		<!-- Icon and Trend Indicator -->
		<div class="mb-4 flex items-start justify-between">
			<div class="metric-icon {selectedColor.bg} {selectedColor.border}">
				<span class="text-2xl" in:scale={{ duration: 300, delay: 200 }}>{icon}</span>
			</div>

			{#if changeDirection !== 'neutral' && previousValue > 0}
				<div
					class="trend-indicator"
					class:trend-up={changeDirection === 'up'}
					class:trend-down={changeDirection === 'down'}
					in:scale={{ duration: 300, delay: 400 }}
				>
					{#if changeDirection === 'up'}
						<svg class="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
							<path
								fill-rule="evenodd"
								d="M3.293 9.707a1 1 0 010-1.414l6-6a1 1 0 011.414 0l6 6a1 1 0 01-1.414 1.414L11 5.414V17a1 1 0 11-2 0V5.414L4.707 9.707a1 1 0 01-1.414 0z"
								clip-rule="evenodd"
							/>
						</svg>
					{:else}
						<svg class="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
							<path
								fill-rule="evenodd"
								d="M16.707 10.293a1 1 0 010 1.414l-6 6a1 1 0 01-1.414 0l-6-6a1 1 0 111.414-1.414L9 14.586V3a1 1 0 012 0v11.586l4.293-4.293a1 1 0 011.414 0z"
								clip-rule="evenodd"
							/>
						</svg>
					{/if}
					<span class="text-xs font-medium">
						{Math.abs(percentageChange).toFixed(1)}%
					</span>
				</div>
			{/if}
		</div>

		<!-- Main Content -->
		<div class="metric-data">
			{#if loading}
				<div class="animate-pulse">
					<div class="mb-2 h-8 rounded bg-gray-200 dark:bg-gray-700"></div>
					<div class="h-4 w-3/4 rounded bg-gray-200 dark:bg-gray-700"></div>
				</div>
			{:else}
				<div class="metric-value" in:fade={{ duration: 600, delay: 300 }}>
					{formatter($animatedValue)}
				</div>
				<div class="metric-title" in:fade={{ duration: 400, delay: 500 }}>
					{title}
				</div>
				{#if subtitle}
					<div class="metric-subtitle" in:fade={{ duration: 400, delay: 600 }}>
						{subtitle}
					</div>
				{/if}
			{/if}
		</div>

		<!-- Progress Bar (optional) -->
		{#if trend && previousValue > 0}
			<div class="metric-progress mt-4" in:scale={{ duration: 400, delay: 800 }}>
				<div class="progress-bar">
					<div
						class="progress-fill bg-gradient-to-r {selectedColor.gradient}"
						style="width: {Math.min(Math.abs(percentageChange), 100)}%"
					></div>
				</div>
			</div>
		{/if}
	</div>

	<!-- Hover Effect Overlay -->
	<div class="metric-overlay"></div>
</div>

<style>
	.metric-card {
		position: relative;
		overflow: hidden;
		border-radius: 1rem;
		border: 1px solid #e5e7eb;
		background: white;
		padding: 1.5rem;
		box-shadow:
			0 4px 6px -1px rgba(0, 0, 0, 0.1),
			0 2px 4px -1px rgba(0, 0, 0, 0.06);
		transition: all 0.3s;
		background: linear-gradient(
			135deg,
			rgba(255, 255, 255, 0.95) 0%,
			rgba(249, 250, 251, 0.9) 100%
		);
	}

	.metric-card:hover {
		box-shadow:
			0 20px 25px -5px rgba(0, 0, 0, 0.1),
			0 10px 10px -5px rgba(0, 0, 0, 0.04);
		transform: translateY(-0.25rem);
	}

	:global(.dark) .metric-card {
		border-color: #374151;
		background: #1f2937;
		background: linear-gradient(135deg, rgba(31, 41, 55, 0.95) 0%, rgba(17, 24, 39, 0.9) 100%);
	}

	.metric-content {
		position: relative;
		z-index: 10;
	}

	.metric-icon {
		display: flex;
		height: 3rem;
		width: 3rem;
		align-items: center;
		justify-content: center;
		border-radius: 0.75rem;
		border: 1px solid;
		transition: all 0.3s;
	}

	.group:hover .metric-icon {
		transform: scale(1.1);
	}

	.trend-indicator {
		display: flex;
		align-items: center;
		gap: 0.25rem;
		border-radius: 0.5rem;
		padding: 0.25rem 0.5rem;
		font-size: 0.75rem;
		font-weight: 500;
		transition: all 0.3s;
	}

	.trend-up {
		background: #f0fdf4;
		color: #15803d;
	}

	:global(.dark) .trend-up {
		background: rgba(34, 197, 94, 0.3);
		color: #4ade80;
	}

	.trend-down {
		background: #fef2f2;
		color: #b91c1c;
	}

	:global(.dark) .trend-down {
		background: rgba(239, 68, 68, 0.3);
		color: #f87171;
	}

	.metric-value {
		font-size: 1.875rem;
		font-weight: 700;
		color: #111827;
		font-family: ui-sans-serif, system-ui, sans-serif;
		letter-spacing: -0.025em;
	}

	:global(.dark) .metric-value {
		color: #f9fafb;
	}

	.metric-title {
		font-size: 0.875rem;
		font-weight: 500;
		color: #4b5563;
		margin-top: 0.25rem;
	}

	:global(.dark) .metric-title {
		color: #9ca3af;
	}

	.metric-subtitle {
		font-size: 0.75rem;
		color: #6b7280;
		margin-top: 0.25rem;
	}

	:global(.dark) .metric-subtitle {
		color: #6b7280;
	}

	.metric-progress {
		position: relative;
	}

	.progress-bar {
		height: 0.5rem;
		width: 100%;
		border-radius: 9999px;
		background: #e5e7eb;
		overflow: hidden;
	}

	:global(.dark) .progress-bar {
		background: #374151;
	}

	.progress-fill {
		height: 100%;
		transition: all 1s ease-out;
	}

	.metric-overlay {
		position: absolute;
		inset: 0;
		background: linear-gradient(135deg, transparent, transparent, rgba(249, 250, 251, 0.5));
		opacity: 0;
		transition: opacity 0.3s;
		border-radius: inherit;
	}

	:global(.dark) .metric-overlay {
		background: linear-gradient(135deg, transparent, transparent, rgba(31, 41, 55, 0.5));
	}

	.group:hover .metric-overlay {
		opacity: 1;
	}

	.metric-card:hover .metric-overlay {
		background: linear-gradient(135deg, transparent 0%, rgba(99, 102, 241, 0.05) 100%);
	}
</style>
