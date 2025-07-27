<script>
	import { onMount, onDestroy } from 'svelte';
	import { Chart, registerables } from 'chart.js';
	import { fade, scale } from 'svelte/transition';

	export let type = 'bar';
	export let data = {};
	export let options = {};
	export let height = 400;
	export let title = '';
	export let className = '';
	export let loading = false;

	let chartContainer;
	let chartInstance;
	let mounted = false;

	Chart.register(...registerables);

	onMount(() => {
		mounted = true;
		if (data && Object.keys(data).length > 0) {
			createChart();
		}
	});

	onDestroy(() => {
		if (chartInstance) {
			chartInstance.destroy();
		}
	});

	$: if (mounted && data && Object.keys(data).length > 0) {
		updateChart();
	}

	function createChart() {
		if (!chartContainer || !data || Object.keys(data).length === 0) return;

		if (chartInstance) {
			chartInstance.destroy();
		}

		const ctx = chartContainer.getContext('2d');

		const defaultOptions = {
			responsive: true,
			maintainAspectRatio: false,
			interaction: {
				mode: 'index',
				intersect: false
			},
			plugins: {
				legend: {
					position: 'top',
					labels: {
						usePointStyle: true,
						padding: 20,
						font: {
							size: 12,
							family: "'Inter', sans-serif"
						}
					}
				},
				tooltip: {
					backgroundColor: 'rgba(17, 24, 39, 0.95)',
					titleColor: '#F9FAFB',
					bodyColor: '#F9FAFB',
					borderColor: '#374151',
					borderWidth: 1,
					cornerRadius: 8,
					padding: 12,
					titleFont: {
						size: 14,
						weight: '600'
					},
					bodyFont: {
						size: 13
					}
				}
			},
			scales:
				type !== 'pie' && type !== 'doughnut'
					? {
							x: {
								grid: {
									color: 'rgba(156, 163, 175, 0.1)',
									drawBorder: false
								},
								ticks: {
									color: '#6B7280',
									font: {
										size: 11
									}
								}
							},
							y: {
								grid: {
									color: 'rgba(156, 163, 175, 0.1)',
									drawBorder: false
								},
								ticks: {
									color: '#6B7280',
									font: {
										size: 11
									}
								}
							}
						}
					: {},
			animation: {
				duration: 1000,
				easing: 'easeInOutQuart'
			}
		};

		chartInstance = new Chart(ctx, {
			type,
			data,
			options: { ...defaultOptions, ...options }
		});
	}

	function updateChart() {
		if (!chartInstance) {
			createChart();
			return;
		}

		chartInstance.data = data;
		chartInstance.update('active');
	}
</script>

<div class="analytics-chart {className}" in:fade={{ duration: 300 }}>
	{#if title}
		<div class="chart-header mb-4">
			<h3 class="font-sans text-lg font-semibold tracking-tight text-gray-900 dark:text-gray-100">
				{title}
			</h3>
		</div>
	{/if}

	<div class="chart-container relative" style="height: {height}px;">
		{#if loading}
			<div
				class="absolute inset-0 flex items-center justify-center rounded-xl bg-white/80 backdrop-blur-sm dark:bg-gray-800/80"
				in:scale={{ duration: 200 }}
			>
				<div class="flex flex-col items-center space-y-3">
					<div
						class="h-8 w-8 animate-spin rounded-full border-3 border-indigo-200 border-t-indigo-600"
					></div>
					<p class="text-sm text-gray-600 dark:text-gray-400">Loading chart...</p>
				</div>
			</div>
		{:else}
			<canvas bind:this={chartContainer} class="rounded-xl"></canvas>
		{/if}
	</div>
</div>

<style>
	.analytics-chart {
		background: linear-gradient(
			135deg,
			rgba(255, 255, 255, 0.95) 0%,
			rgba(249, 250, 251, 0.9) 100%
		);
		border: 1px solid rgba(229, 231, 235, 0.8);
		border-radius: 1rem;
		padding: 1.5rem;
		box-shadow:
			0 4px 6px -1px rgba(0, 0, 0, 0.05),
			0 2px 4px -1px rgba(0, 0, 0, 0.03);
		transition: all 0.3s ease;
	}

	.analytics-chart:hover {
		transform: translateY(-2px);
		box-shadow:
			0 10px 25px -3px rgba(0, 0, 0, 0.1),
			0 4px 6px -2px rgba(0, 0, 0, 0.05);
	}

	:global(.dark) .analytics-chart {
		background: linear-gradient(135deg, rgba(31, 41, 55, 0.95) 0%, rgba(17, 24, 39, 0.9) 100%);
		border-color: rgba(75, 85, 99, 0.8);
	}

	.chart-container {
		overflow: hidden;
		border-radius: 0.75rem;
	}

	.chart-header {
		border-bottom: 1px solid rgba(229, 231, 235, 0.5);
		padding-bottom: 0.75rem;
	}

	:global(.dark) .chart-header {
		border-bottom-color: rgba(75, 85, 99, 0.5);
	}
</style>
