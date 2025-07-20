<!-- src/lib/components/analytics/AnalyticsDashboard.svelte -->
<script>
	import { onMount } from 'svelte';
	import { t } from '$lib/i18n';
	import { 
		getComprehensiveAnalytics,
		getAdvancedPropertyAnalytics,
		getPaymentAnalytics,
		getWorkerAnalytics,
		getPropertyHeatMap,
		processBarChartData,
		processHeatMapData
	} from '$lib/api/analytics';
	import { toast } from '$lib/stores/toastStore.svelte.js';
	import Button from '$lib/components/ui/Button.svelte';
	import LoadingSkeleton from '$lib/components/ui/LoadingSkeleton.svelte';
	import Alert from '$lib/components/ui/Alert.svelte';
	import StatCard from '$lib/components/dashboard/StatCard.svelte';

	// Svelte 5 runes for reactive state
	let analytics = $state(null);
	let propertyAnalytics = $state(null);
	let paymentAnalytics = $state(null);
	let workerAnalytics = $state(null);
	let heatMapData = $state(null);
	let loading = $state(true);
	let error = $state(null);
	let selectedTimeRange = $state('30d');
	let selectedChart = $state('overview');
	let refreshing = $state(false);

	// Chart containers
	let propertyChartRef = $state(null);
	let paymentChartRef = $state(null);
	let workerChartRef = $state(null);
	let heatMapRef = $state(null);

	// Derived state for charts
	let chartData = $derived(() => {
		if (!analytics) return null;
		
		return {
			properties: processBarChartData(propertyAnalytics?.chartData || []),
			payments: processBarChartData(paymentAnalytics?.chartData || []),
			workers: processBarChartData(workerAnalytics?.chartData || []),
			heatMap: processHeatMapData(heatMapData || {})
		};
	});

	// Filter options
	let timeRangeOptions = $derived([
		{ value: '7d', label: $t('common.last7days') },
		{ value: '30d', label: $t('common.last30days') },
		{ value: '90d', label: $t('common.last90days') },
		{ value: '6m', label: $t('common.last6months') },
		{ value: '1y', label: $t('common.lastYear') }
	]);

	let chartOptions = $derived([
		{ value: 'overview', label: $t('analytics.overview') },
		{ value: 'properties', label: $t('analytics.propertyTrends') },
		{ value: 'payments', label: $t('analytics.paymentTrends') },
		{ value: 'workers', label: $t('analytics.workerPerformance') },
		{ value: 'heatmap', label: $t('analytics.heatMap') }
	]);

	// Load data on mount and when filters change
	onMount(async () => {
		await loadAnalyticsData();
	});

	// Watch for filter changes
	$effect(() => {
		if (selectedTimeRange) {
			loadAnalyticsData();
		}
	});

	// Load analytics data
	async function loadAnalyticsData() {
		try {
			loading = true;
			error = null;

			const filters = { timeRange: selectedTimeRange };
			
			const [overview, properties, payments, workers, heatMap] = await Promise.all([
				getComprehensiveAnalytics(filters),
				getAdvancedPropertyAnalytics(filters),
				getPaymentAnalytics(filters),
				getWorkerAnalytics(filters),
				getPropertyHeatMap(filters)
			]);

			analytics = overview;
			propertyAnalytics = properties;
			paymentAnalytics = payments;
			workerAnalytics = workers;
			heatMapData = heatMap;

			// Render charts after data is loaded
			await renderCharts();
		} catch (err) {
			error = err.message;
			toast.error($t('analytics.loadError'));
		} finally {
			loading = false;
		}
	}

	// Refresh data
	async function refreshData() {
		try {
			refreshing = true;
			await loadAnalyticsData();
			toast.success($t('analytics.dataRefreshed'));
		} finally {
			refreshing = false;
		}
	}

	// Render charts using dynamic imports to avoid SSR issues
	async function renderCharts() {
		if (typeof window === 'undefined') return;

		try {
			// Dynamically import Plotly for client-side rendering
			const Plotly = await import('plotly.js-dist-min');
			
			// Render property chart
			if (propertyChartRef && chartData?.properties) {
				await Plotly.newPlot(propertyChartRef, chartData.properties.data, chartData.properties.layout, chartData.properties.config);
			}

			// Render payment chart
			if (paymentChartRef && chartData?.payments) {
				await Plotly.newPlot(paymentChartRef, chartData.payments.data, chartData.payments.layout, chartData.payments.config);
			}

			// Render worker chart
			if (workerChartRef && chartData?.workers) {
				await Plotly.newPlot(workerChartRef, chartData.workers.data, chartData.workers.layout, chartData.workers.config);
			}

			// Render heat map
			if (heatMapRef && chartData?.heatMap) {
				await Plotly.newPlot(heatMapRef, chartData.heatMap.data, chartData.heatMap.layout, chartData.heatMap.config);
			}
		} catch (err) {
			console.error('Error rendering charts:', err);
			toast.error($t('analytics.chartError'));
		}
	}

	// Re-render charts when data changes
	$effect(() => {
		if (chartData) {
			renderCharts();
		}
	});

	// Export analytics report
	async function exportReport() {
		try {
			const reportData = {
				overview: analytics,
				properties: propertyAnalytics,
				payments: paymentAnalytics,
				workers: workerAnalytics,
				generatedAt: new Date().toISOString(),
				timeRange: selectedTimeRange
			};

			const blob = new Blob([JSON.stringify(reportData, null, 2)], {
				type: 'application/json'
			});
			
			const url = URL.createObjectURL(blob);
			const a = document.createElement('a');
			a.href = url;
			a.download = `analytics-report-${selectedTimeRange}-${new Date().toISOString().split('T')[0]}.json`;
			document.body.appendChild(a);
			a.click();
			document.body.removeChild(a);
			URL.revokeObjectURL(url);

			toast.success($t('analytics.reportExported'));
		} catch (err) {
			toast.error($t('analytics.exportError'));
		}
	}

	// Get growth indicator
	function getGrowthIndicator(current, previous) {
		if (!previous || previous === 0) return { direction: 'none', percentage: 0 };
		
		const change = ((current - previous) / previous) * 100;
		return {
			direction: change > 0 ? 'up' : change < 0 ? 'down' : 'none',
			percentage: Math.abs(change).toFixed(1)
		};
	}

	// Get trend color
	function getTrendColor(direction) {
		switch (direction) {
			case 'up': return 'green';
			case 'down': return 'red';
			default: return 'gray';
		}
	}
</script>

<svelte:head>
	<title>{$t('analytics.dashboard')} - {$t('app.name')}</title>
</svelte:head>

<div class="space-y-6">
	<!-- Header -->
	<div class="flex flex-col sm:flex-row sm:items-center sm:justify-between">
		<div>
			<h1 class="text-2xl font-bold text-gray-900 dark:text-white">
				{$t('analytics.dashboard')}
			</h1>
			<p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
				{$t('analytics.dashboardDescription')}
			</p>
		</div>
		
		<div class="mt-4 sm:mt-0 flex space-x-3">
			<Button 
				onClick={refreshData}
				variant="outline"
				loading={refreshing}
			>
				<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
				</svg>
				{$t('common.refresh')}
			</Button>
			
			<Button 
				onClick={exportReport}
				variant="outline"
			>
				<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
				</svg>
				{$t('analytics.exportReport')}
			</Button>
		</div>
	</div>

	<!-- Filters -->
	<div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4">
		<div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
			<!-- Time Range Filter -->
			<div>
				<label for="timeRange" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
					{$t('common.timeRange')}
				</label>
				<select
					id="timeRange"
					bind:value={selectedTimeRange}
					class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white sm:text-sm"
				>
					{#each timeRangeOptions as option}
						<option value={option.value}>{option.label}</option>
					{/each}
				</select>
			</div>

			<!-- Chart Selection -->
			<div>
				<label for="chartType" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
					{$t('analytics.focusChart')}
				</label>
				<select
					id="chartType"
					bind:value={selectedChart}
					class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white sm:text-sm"
				>
					{#each chartOptions as option}
						<option value={option.value}>{option.label}</option>
					{/each}
				</select>
			</div>
		</div>
	</div>

	<!-- Error Alert -->
	{#if error}
		<Alert type="error" title={$t('error.title')} message={error} dismissible />
	{/if}

	<!-- Loading State -->
	{#if loading}
		<div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
			{#each Array(8) as _}
				<LoadingSkeleton type="rect" height="120px" />
			{/each}
		</div>
	
	<!-- Analytics Overview -->
	{:else if analytics}
		<!-- Key Metrics -->
		<div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
			<!-- Total Properties -->
			{#key analytics.totalProperties}
				{@const propertyGrowth = getGrowthIndicator(analytics.totalProperties, analytics.previousProperties)}
				<StatCard
					title={$t('analytics.totalProperties')}
					value={analytics.totalProperties}
					icon='<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z"></path></svg>'
					color="primary"
					trend={propertyGrowth.direction}
					trendValue="{propertyGrowth.percentage}%"
					href="/dashboard/properties"
				/>
			{/key}

			<!-- Total Revenue -->
			{#key analytics.totalRevenue}
				{@const revenueGrowth = getGrowthIndicator(analytics.totalRevenue, analytics.previousRevenue)}
				<StatCard
					title={$t('analytics.totalRevenue')}
					value="${analytics.totalRevenue?.toLocaleString() || '0'}"
					icon='<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path d="M8.433 7.418c.155-.103.346-.196.567-.267v1.698a2.305 2.305 0 01-.567-.267C8.07 8.34 8 8.114 8 8c0-.114.07-.34.433-.582zM11 12.849v-1.698c.22.071.412.164.567.267.364.243.433.468.433.582 0 .114-.07.34-.433.582a2.305 2.305 0 01-.567.267z"></path><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-13a1 1 0 10-2 0v.092a4.535 4.535 0 00-1.676.662C6.602 6.234 6 7.009 6 8c0 .99.602 1.765 1.324 2.246.48.32 1.054.545 1.676.662v1.941c-.391-.127-.68-.317-.843-.504a1 1 0 10-1.51 1.31c.562.649 1.413 1.076 2.353 1.253V15a1 1 0 102 0v-.092a4.535 4.535 0 001.676-.662C13.398 13.766 14 12.991 14 12c0-.99-.602-1.765-1.324-2.246A4.535 4.535 0 0011 9.092V7.151c.391.127.68.317.843.504a1 1 0 101.511-1.31c-.563-.649-1.413-1.076-2.354-1.253V5z" clip-rule="evenodd"></path></svg>'
					color={getTrendColor(revenueGrowth.direction)}
					trend={revenueGrowth.direction}
					trendValue="{revenueGrowth.percentage}%"
					href="/dashboard/payments"
				/>
			{/key}

			<!-- Active Workers -->
			{#key analytics.activeWorkers}
				{@const workerGrowth = getGrowthIndicator(analytics.activeWorkers, analytics.previousWorkers)}
				<StatCard
					title={$t('analytics.activeWorkers')}
					value={analytics.activeWorkers}
					icon='<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path d="M9 6a3 3 0 11-6 0 3 3 0 016 0zM17 6a3 3 0 11-6 0 3 3 0 016 0zM12.93 17c.046-.327.07-.66.07-1a6.97 6.97 0 00-1.5-4.33A5 5 0 0119 16v1h-6.07zM6 11a5 5 0 015 5v1H1v-1a5 5 0 015-5z"></path></svg>'
					color="success"
					trend={workerGrowth.direction}
					trendValue="{workerGrowth.percentage}%"
					href="/dashboard/workers"
				/>
			{/key}

			<!-- Occupancy Rate -->
			<StatCard
				title={$t('analytics.occupancyRate')}
				value="{analytics.occupancyRate?.toFixed(1) || '0'}%"
				icon='<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clip-rule="evenodd"></path></svg>'
				color={analytics.occupancyRate >= 80 ? 'success' : analytics.occupancyRate >= 60 ? 'warning' : 'error'}
			/>

			<!-- Pending Payments -->
			<StatCard
				title={$t('analytics.pendingPayments')}
				value={analytics.pendingPayments}
				icon='<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd"></path></svg>'
				color={analytics.pendingPayments > 0 ? 'warning' : 'success'}
				href="/dashboard/payments?filter=pending"
			/>

			<!-- Worker Utilization -->
			<StatCard
				title={$t('analytics.workerUtilization')}
				value="{analytics.workerUtilization?.toFixed(1) || '0'}%"
				icon='<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M6 6V5a3 3 0 013-3h2a3 3 0 013 3v1h2a2 2 0 012 2v3.57A22.952 22.952 0 0110 13a22.95 22.95 0 01-8-1.43V8a2 2 0 012-2h2zm2-1a1 1 0 011-1h2a1 1 0 011 1v1H8V5zm1 5a1 1 0 011-1h.01a1 1 0 110 2H10a1 1 0 01-1-1z" clip-rule="evenodd"></path><path d="M2 13.692V16a2 2 0 002 2h12a2 2 0 002-2v-2.308A24.974 24.974 0 0110 15c-2.796 0-5.487-.46-8-1.308z"></path></svg>'
				color={analytics.workerUtilization >= 80 ? 'success' : analytics.workerUtilization >= 60 ? 'warning' : 'error'}
				href="/dashboard/workers"
			/>

			<!-- Average Property Value -->
			<StatCard
				title={$t('analytics.avgPropertyValue')}
				value="${analytics.avgPropertyValue?.toLocaleString() || '0'}"
				icon='<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M4 4a2 2 0 00-2 2v4a2 2 0 002 2V6h10a2 2 0 00-2-2H4zm2 6a2 2 0 012-2h8a2 2 0 012 2v4a2 2 0 01-2 2H8a2 2 0 01-2-2v-4zm6 4a2 2 0 100-4 2 2 0 000 4z" clip-rule="evenodd"></path></svg>'
				color="primary"
			/>

			<!-- Monthly Growth Rate -->
			<StatCard
				title={$t('analytics.monthlyGrowth')}
				value="{analytics.monthlyGrowthRate?.toFixed(1) || '0'}%"
				icon='<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M12 7a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0V8.414l-4.293 4.293a1 1 0 01-1.414 0L8 10.414l-4.293 4.293a1 1 0 01-1.414-1.414l5-5a1 1 0 011.414 0L11 10.586 14.586 7H12z" clip-rule="evenodd"></path></svg>'
				color={analytics.monthlyGrowthRate > 0 ? 'success' : 'error'}
				trend={analytics.monthlyGrowthRate > 0 ? 'up' : 'down'}
				trendValue="{Math.abs(analytics.monthlyGrowthRate).toFixed(1)}%"
			/>
		</div>

		<!-- Charts Section -->
		<div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
			<!-- Property Analytics Chart -->
			{#if (selectedChart === 'overview' || selectedChart === 'properties') && propertyAnalytics}
				<div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
					<div class="flex items-center justify-between mb-4">
						<h3 class="text-lg font-medium text-gray-900 dark:text-white">
							{$t('analytics.propertyTrends')}
						</h3>
						<Button 
							href="/dashboard/properties"
							variant="outline"
							size="compact"
						>
							{$t('common.viewDetails')}
						</Button>
					</div>
					<div bind:this={propertyChartRef} class="h-80"></div>
				</div>
			{/if}

			<!-- Payment Analytics Chart -->
			{#if (selectedChart === 'overview' || selectedChart === 'payments') && paymentAnalytics}
				<div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
					<div class="flex items-center justify-between mb-4">
						<h3 class="text-lg font-medium text-gray-900 dark:text-white">
							{$t('analytics.paymentTrends')}
						</h3>
						<Button 
							href="/dashboard/payments"
							variant="outline"
							size="compact"
						>
							{$t('common.viewDetails')}
						</Button>
					</div>
					<div bind:this={paymentChartRef} class="h-80"></div>
				</div>
			{/if}

			<!-- Worker Performance Chart -->
			{#if (selectedChart === 'overview' || selectedChart === 'workers') && workerAnalytics}
				<div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
					<div class="flex items-center justify-between mb-4">
						<h3 class="text-lg font-medium text-gray-900 dark:text-white">
							{$t('analytics.workerPerformance')}
						</h3>
						<Button 
							href="/dashboard/workers"
							variant="outline"
							size="compact"
						>
							{$t('common.viewDetails')}
						</Button>
					</div>
					<div bind:this={workerChartRef} class="h-80"></div>
				</div>
			{/if}

			<!-- Heat Map -->
			{#if (selectedChart === 'overview' || selectedChart === 'heatmap') && heatMapData}
				<div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 lg:col-span-2">
					<div class="flex items-center justify-between mb-4">
						<h3 class="text-lg font-medium text-gray-900 dark:text-white">
							{$t('analytics.activityHeatMap')}
						</h3>
						<div class="text-sm text-gray-600 dark:text-gray-400">
							{$t('analytics.heatMapDescription')}
						</div>
					</div>
					<div bind:this={heatMapRef} class="h-96"></div>
				</div>
			{/if}
		</div>

		<!-- Insights Section -->
		{#if analytics.insights && analytics.insights.length > 0}
			<div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
				<h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">
					{$t('analytics.keyInsights')}
				</h3>
				
				<div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
					{#each analytics.insights as insight}
						<div class="p-4 rounded-md bg-{insight.type === 'positive' ? 'green' : insight.type === 'warning' ? 'yellow' : 'blue'}-50 dark:bg-{insight.type === 'positive' ? 'green' : insight.type === 'warning' ? 'yellow' : 'blue'}-900/20">
							<div class="flex items-start">
								<div class="flex-shrink-0">
									{#if insight.type === 'positive'}
										<svg class="h-5 w-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
											<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
										</svg>
									{:else if insight.type === 'warning'}
										<svg class="h-5 w-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
											<path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path>
										</svg>
									{:else}
										<svg class="h-5 w-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
											<path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path>
										</svg>
									{/if}
								</div>
								<div class="ml-3">
									<h4 class="text-sm font-medium text-gray-900 dark:text-white">
										{insight.title}
									</h4>
									<p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
										{insight.description}
									</p>
									{#if insight.action}
										<Button 
											href={insight.actionUrl}
											variant="outline"
											size="compact"
											class="mt-2"
										>
											{insight.action}
										</Button>
									{/if}
								</div>
							</div>
						</div>
					{/each}
				</div>
			</div>
		{/if}
	{/if}
</div>