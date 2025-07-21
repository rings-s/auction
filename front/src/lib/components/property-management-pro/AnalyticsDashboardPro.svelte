<script>
	import { onMount, onDestroy } from 'svelte';
	import { analyticsAPI } from '$lib/api/propertyManagement.js';
	import { t } from '$lib/i18n';
	import { formatCurrency } from '$lib/utils/currency.js';
	import LoadingSpinner from '$lib/components/animations/LoadingSpinner.svelte';
	import FadeInUp from '$lib/components/animations/FadeInUp.svelte';
	import StaggeredList from '$lib/components/animations/StaggeredList.svelte';
	import CountUp from '$lib/components/animations/CountUp.svelte';
	import ProgressRing from '$lib/components/animations/ProgressRing.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Alert from '$lib/components/ui/Alert.svelte';

	/** @type {number|null} */
	export let propertyId = null;
	/** @type {string} */
	export let title = '';

	// State
	let loading = false;
	let error = '';
	let analyticsData = [];
	let charts = {};
	let summary = {};
	let refreshInterval;
	let selectedTimeRange = '12m'; // '1m', '3m', '6m', '12m', 'all'
	let selectedMetric = 'revenue'; // 'revenue', 'occupancy', 'roi', 'maintenance'

	// Chart containers
	let revenueChart;
	let occupancyChart;
	let roiChart;
	let isChartsLoaded = false;

	// Enhanced metrics
	let kpiMetrics = {};
	let trends = {};
	let comparisons = {};

	$: pageTitle =
		title || (propertyId ? $t('analytics.propertyAnalytics') : $t('analytics.portfolioAnalytics'));

	const timeRangeOptions = [
		{ value: '1m', label: $t('analytics.timeRange.1month') },
		{ value: '3m', label: $t('analytics.timeRange.3months') },
		{ value: '6m', label: $t('analytics.timeRange.6months') },
		{ value: '12m', label: $t('analytics.timeRange.12months') },
		{ value: 'all', label: $t('analytics.timeRange.allTime') }
	];

	const metricOptions = [
		{ value: 'revenue', label: $t('analytics.metrics.revenue'), icon: '💰', color: 'emerald' },
		{ value: 'occupancy', label: $t('analytics.metrics.occupancy'), icon: '📊', color: 'blue' },
		{ value: 'roi', label: $t('analytics.metrics.roi'), icon: '📈', color: 'purple' },
		{
			value: 'maintenance',
			label: $t('analytics.metrics.maintenance'),
			icon: '🔧',
			color: 'orange'
		}
	];

	onMount(() => {
		loadAnalytics();
		loadPlotlyCharts();

		// Set up auto-refresh every 5 minutes
		refreshInterval = setInterval(loadAnalytics, 5 * 60 * 1000);
	});

	onDestroy(() => {
		if (refreshInterval) {
			clearInterval(refreshInterval);
		}
	});

	async function loadAnalytics() {
		try {
			loading = true;
			error = '';

			const response = await analyticsAPI.getAnalytics(propertyId);
			analyticsData = response.data.analytics_data || [];
			charts = response.data.charts || {};
			summary = response.data.summary || {};

			// Calculate enhanced metrics
			calculateEnhancedMetrics();

			// Render charts after data is loaded
			if (isChartsLoaded && Object.keys(charts).length > 0) {
				setTimeout(renderCharts, 100);
			}
		} catch (err) {
			error = err.message || $t('errors.loadingFailed');
			console.error('Failed to load analytics:', err);
		} finally {
			loading = false;
		}
	}

	async function loadPlotlyCharts() {
		try {
			const Plotly = await import('plotly.js-dist-min');
			window.Plotly = Plotly.default;
			isChartsLoaded = true;

			if (Object.keys(charts).length > 0) {
				renderCharts();
			}
		} catch (err) {
			console.warn('Plotly not available, falling back to basic charts');
		}
	}

	function calculateEnhancedMetrics() {
		if (!analyticsData.length) return;

		// Calculate KPI metrics
		const totalRevenue = summary.total_annual_income || 0;
		const totalExpenses = summary.total_expenses || 0;
		const netIncome = totalRevenue - totalExpenses;
		const averageOccupancy = summary.average_occupancy || 0;
		const averageROI = summary.average_roi || 0;

		kpiMetrics = {
			revenue: {
				current: totalRevenue,
				change: calculateChange(totalRevenue, totalRevenue * 0.9), // Mock previous period
				trend: 'up'
			},
			netIncome: {
				current: netIncome,
				change: calculateChange(netIncome, netIncome * 0.85),
				trend: netIncome > netIncome * 0.85 ? 'up' : 'down'
			},
			occupancy: {
				current: averageOccupancy,
				change: calculateChange(averageOccupancy, averageOccupancy * 0.95),
				trend: 'up'
			},
			roi: {
				current: averageROI,
				change: calculateChange(averageROI, averageROI * 0.88),
				trend: 'up'
			}
		};

		// Calculate trends and insights
		trends = {
			bestPerforming: analyticsData.reduce(
				(best, current) => (current.roi > (best?.roi || 0) ? current : best),
				null
			),
			worstPerforming: analyticsData.reduce(
				(worst, current) => (current.roi < (worst?.roi || Infinity) ? current : worst),
				null
			),
			highestRevenue: analyticsData.reduce(
				(highest, current) =>
					current.annual_income > (highest?.annual_income || 0) ? current : highest,
				null
			),
			mostExpensive: analyticsData.reduce(
				(most, current) => (current.total_expenses > (most?.total_expenses || 0) ? current : most),
				null
			)
		};
	}

	function calculateChange(current, previous) {
		if (!previous || previous === 0) return 0;
		return ((current - previous) / previous) * 100;
	}

	function renderCharts() {
		if (!window.Plotly || !charts) return;

		const chartConfig = {
			responsive: true,
			displayModeBar: false,
			showTips: false
		};

		try {
			// Enhanced Revenue Chart
			if (charts.revenue_expenses && revenueChart) {
				const chartData = JSON.parse(charts.revenue_expenses);

				// Enhance chart styling
				chartData.layout = {
					...chartData.layout,
					font: { family: 'Inter, system-ui, sans-serif', size: 12 },
					plot_bgcolor: 'rgba(0,0,0,0)',
					paper_bgcolor: 'rgba(0,0,0,0)',
					margin: { t: 40, b: 60, l: 80, r: 40 },
					showlegend: true,
					legend: { orientation: 'h', y: -0.2 },
					hovermode: 'x unified',
					annotations: [
						{
							text: $t('analytics.revenueVsExpenses'),
							x: 0.5,
							y: 1.1,
							xref: 'paper',
							yref: 'paper',
							showarrow: false,
							font: { size: 16, color: '#374151' }
						}
					]
				};

				window.Plotly.newPlot(revenueChart, chartData.data, chartData.layout, chartConfig);
			}

			// Enhanced Occupancy Chart
			if (charts.occupancy && occupancyChart) {
				const chartData = JSON.parse(charts.occupancy);

				chartData.layout = {
					...chartData.layout,
					font: { family: 'Inter, system-ui, sans-serif', size: 12 },
					plot_bgcolor: 'rgba(0,0,0,0)',
					paper_bgcolor: 'rgba(0,0,0,0)',
					margin: { t: 40, b: 60, l: 60, r: 40 },
					hovermode: 'closest'
				};

				window.Plotly.newPlot(occupancyChart, chartData.data, chartData.layout, chartConfig);
			}

			// Enhanced ROI Chart
			if (charts.roi && roiChart) {
				const chartData = JSON.parse(charts.roi);

				chartData.layout = {
					...chartData.layout,
					font: { family: 'Inter, system-ui, sans-serif', size: 12 },
					plot_bgcolor: 'rgba(0,0,0,0)',
					paper_bgcolor: 'rgba(0,0,0,0)',
					margin: { t: 40, b: 60, l: 60, r: 40 }
				};

				window.Plotly.newPlot(roiChart, chartData.data, chartData.layout, chartConfig);
			}
		} catch (err) {
			console.error('Error rendering charts:', err);
		}
	}

	function handleRefresh() {
		loadAnalytics();
	}

	function handleTimeRangeChange(range) {
		selectedTimeRange = range;
		loadAnalytics();
	}

	function handleExportData() {
		const csvContent = convertToCSV(analyticsData);
		const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
		const link = document.createElement('a');

		if (link.download !== undefined) {
			const url = URL.createObjectURL(blob);
			link.setAttribute('href', url);
			link.setAttribute(
				'download',
				`property-analytics-${selectedTimeRange}-${new Date().toISOString().split('T')[0]}.csv`
			);
			link.style.visibility = 'hidden';
			document.body.appendChild(link);
			link.click();
			document.body.removeChild(link);
		}
	}

	function convertToCSV(data) {
		if (!data.length) return '';

		const headers = Object.keys(data[0]);
		const csvHeaders = headers.join(',');
		const csvRows = data.map((row) =>
			headers
				.map((header) => {
					const value = row[header];
					return typeof value === 'string' && value.includes(',') ? `"${value}"` : value;
				})
				.join(',')
		);

		return [csvHeaders, ...csvRows].join('\n');
	}

	function getTrendIcon(trend) {
		return trend === 'up' ? '📈' : trend === 'down' ? '📉' : '➡️';
	}

	function getTrendColor(change) {
		return change > 0 ? 'text-green-600' : change < 0 ? 'text-red-600' : 'text-gray-600';
	}
</script>

<div class="analytics-dashboard-pro space-y-8">
	<!-- Enhanced Header -->
	<FadeInUp>
		<div class="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
			<div>
				<h1
					class="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-4xl font-bold text-transparent"
				>
					{pageTitle}
				</h1>
				<p class="mt-2 text-lg text-gray-600">{$t('analytics.subtitle')}</p>
			</div>

			<div class="flex items-center gap-3">
				<!-- Time Range Selector -->
				<div class="flex items-center rounded-xl bg-gray-100 p-1">
					{#each timeRangeOptions as option}
						<button
							class="rounded-lg px-3 py-1.5 text-sm font-medium transition-all duration-200 {selectedTimeRange ===
							option.value
								? 'bg-white text-blue-600 shadow-sm'
								: 'text-gray-600 hover:text-gray-900'}"
							on:click={() => handleTimeRangeChange(option.value)}
						>
							{option.label}
						</button>
					{/each}
				</div>

				<Button variant="outline" size="sm" on:click={handleRefresh} disabled={loading}>
					<span class="flex items-center gap-2">
						<span class={loading ? 'animate-spin' : ''}>🔄</span>
						{$t('common.refresh')}
					</span>
				</Button>

				<Button
					variant="outline"
					size="sm"
					on:click={handleExportData}
					disabled={loading || !analyticsData.length}
				>
					<span class="flex items-center gap-2">
						<span>📊</span>
						{$t('analytics.exportData')}
					</span>
				</Button>
			</div>
		</div>
	</FadeInUp>

	<!-- Error Display -->
	{#if error}
		<FadeInUp delay={100}>
			<Alert type="error" message={error} />
		</FadeInUp>
	{/if}

	<!-- Loading State -->
	{#if loading && !analyticsData.length}
		<div class="flex justify-center py-12">
			<LoadingSpinner size="xl" variant="spinner" />
		</div>
	{:else if analyticsData.length === 0 && !loading}
		<!-- Empty State -->
		<FadeInUp delay={200}>
			<div class="py-16 text-center">
				<div class="mb-6 text-8xl">📊</div>
				<h3 class="mb-4 text-2xl font-bold text-gray-900">{$t('analytics.noData')}</h3>
				<p class="mx-auto max-w-md text-lg text-gray-600">{$t('analytics.noDataDescription')}</p>
			</div>
		</FadeInUp>
	{:else}
		<!-- Enhanced KPI Cards -->
		<StaggeredList staggerDelay={100}>
			<div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
				<!-- Total Revenue Card -->
				<div
					class="rounded-3xl bg-gradient-to-br from-emerald-500 to-teal-600 p-6 text-white shadow-xl"
				>
					<div class="mb-4 flex items-center justify-between">
						<div class="rounded-2xl bg-white/20 p-3 backdrop-blur-sm">
							<span class="text-2xl">💰</span>
						</div>
						<div class="text-right">
							<span class="flex items-center gap-1 text-sm font-medium text-emerald-100">
								{getTrendIcon(kpiMetrics.revenue?.trend)}
								<CountUp value={kpiMetrics.revenue?.change || 0} decimals={1} suffix="%" />
							</span>
						</div>
					</div>
					<h3 class="mb-2 text-lg font-medium text-emerald-100">
						{$t('analytics.totalAnnualIncome')}
					</h3>
					<p class="text-3xl font-bold">
						<CountUp value={summary.total_annual_income || 0} format="compact" />
					</p>
				</div>

				<!-- Net Income Card -->
				<div
					class="rounded-3xl bg-gradient-to-br from-blue-500 to-cyan-600 p-6 text-white shadow-xl"
				>
					<div class="mb-4 flex items-center justify-between">
						<div class="rounded-2xl bg-white/20 p-3 backdrop-blur-sm">
							<span class="text-2xl">📈</span>
						</div>
						<div class="text-right">
							<span class="flex items-center gap-1 text-sm font-medium text-blue-100">
								{getTrendIcon(kpiMetrics.netIncome?.trend)}
								<CountUp value={kpiMetrics.netIncome?.change || 0} decimals={1} suffix="%" />
							</span>
						</div>
					</div>
					<h3 class="mb-2 text-lg font-medium text-blue-100">{$t('analytics.netIncome')}</h3>
					<p class="text-3xl font-bold">
						<CountUp
							value={(summary.total_annual_income || 0) - (summary.total_expenses || 0)}
							format="compact"
						/>
					</p>
				</div>

				<!-- Average Occupancy Card -->
				<div
					class="rounded-3xl bg-gradient-to-br from-purple-500 to-violet-600 p-6 text-white shadow-xl"
				>
					<div class="mb-4 flex items-center justify-between">
						<div class="rounded-2xl bg-white/20 p-3 backdrop-blur-sm">
							<ProgressRing
								progress={summary.average_occupancy || 0}
								size={40}
								strokeWidth={4}
								color="#ffffff"
								backgroundColor="rgba(255,255,255,0.3)"
								showText={false}
							/>
						</div>
						<div class="text-right">
							<span class="flex items-center gap-1 text-sm font-medium text-purple-100">
								{getTrendIcon(kpiMetrics.occupancy?.trend)}
								<CountUp value={kpiMetrics.occupancy?.change || 0} decimals={1} suffix="%" />
							</span>
						</div>
					</div>
					<h3 class="mb-2 text-lg font-medium text-purple-100">
						{$t('analytics.averageOccupancy')}
					</h3>
					<p class="text-3xl font-bold">
						<CountUp value={summary.average_occupancy || 0} decimals={1} suffix="%" />
					</p>
				</div>

				<!-- Average ROI Card -->
				<div
					class="rounded-3xl bg-gradient-to-br from-orange-500 to-red-500 p-6 text-white shadow-xl"
				>
					<div class="mb-4 flex items-center justify-between">
						<div class="rounded-2xl bg-white/20 p-3 backdrop-blur-sm">
							<span class="text-2xl">🎯</span>
						</div>
						<div class="text-right">
							<span class="flex items-center gap-1 text-sm font-medium text-orange-100">
								{getTrendIcon(kpiMetrics.roi?.trend)}
								<CountUp value={kpiMetrics.roi?.change || 0} decimals={1} suffix="%" />
							</span>
						</div>
					</div>
					<h3 class="mb-2 text-lg font-medium text-orange-100">{$t('analytics.averageROI')}</h3>
					<p class="text-3xl font-bold">
						<CountUp value={summary.average_roi || 0} decimals={1} suffix="%" />
					</p>
				</div>
			</div>
		</StaggeredList>

		<!-- Enhanced Charts Section -->
		<StaggeredList staggerDelay={150}>
			<div class="grid grid-cols-1 gap-8 lg:grid-cols-2">
				<!-- Revenue vs Expenses Chart -->
				{#if charts.revenue_expenses}
					<div class="rounded-3xl border border-gray-100 bg-white p-8 shadow-lg">
						<div class="mb-6 flex items-center justify-between">
							<h3 class="text-xl font-bold text-gray-900">{$t('analytics.revenueVsExpenses')}</h3>
							<div class="flex items-center gap-2 text-sm text-gray-600">
								<span class="h-3 w-3 rounded-full bg-green-500"></span>
								<span>Income</span>
								<span class="ml-3 h-3 w-3 rounded-full bg-red-500"></span>
								<span>Expenses</span>
							</div>
						</div>
						<div bind:this={revenueChart} class="h-80"></div>
					</div>
				{/if}

				<!-- Occupancy Rate Chart -->
				{#if charts.occupancy}
					<div class="rounded-3xl border border-gray-100 bg-white p-8 shadow-lg">
						<div class="mb-6 flex items-center justify-between">
							<h3 class="text-xl font-bold text-gray-900">{$t('analytics.occupancyRates')}</h3>
							<div class="text-sm text-gray-600">
								<span>📊 {$t('analytics.byProperty')}</span>
							</div>
						</div>
						<div bind:this={occupancyChart} class="h-80"></div>
					</div>
				{/if}
			</div>
		</StaggeredList>

		<!-- ROI Chart (Full Width) -->
		{#if charts.roi}
			<FadeInUp delay={300}>
				<div class="rounded-3xl border border-gray-100 bg-white p-8 shadow-lg">
					<div class="mb-6 flex items-center justify-between">
						<h3 class="text-2xl font-bold text-gray-900">{$t('analytics.returnOnInvestment')}</h3>
						<div class="text-sm text-gray-600">
							<span>🎯 {$t('analytics.performanceIndicator')}</span>
						</div>
					</div>
					<div bind:this={roiChart} class="h-96"></div>
				</div>
			</FadeInUp>
		{/if}

		<!-- Insights and Trends -->
		<StaggeredList staggerDelay={100}>
			<div class="grid grid-cols-1 gap-8 lg:grid-cols-2">
				<!-- Best Performers -->
				<div
					class="rounded-3xl border border-green-200 bg-gradient-to-br from-green-50 to-emerald-50 p-8"
				>
					<h3 class="mb-6 flex items-center gap-2 text-xl font-bold text-green-900">
						<span>🏆</span>
						{$t('analytics.topPerformers')}
					</h3>

					{#if trends.bestPerforming}
						<div class="space-y-4">
							<div class="rounded-2xl bg-white p-4">
								<h4 class="mb-2 font-semibold text-gray-900">{$t('analytics.highestROI')}</h4>
								<p class="text-lg font-bold text-green-600">
									{trends.bestPerforming.property_title}
								</p>
								<p class="text-2xl font-bold text-green-700">
									<CountUp value={trends.bestPerforming.roi} decimals={1} suffix="% ROI" />
								</p>
							</div>

							{#if trends.highestRevenue}
								<div class="rounded-2xl bg-white p-4">
									<h4 class="mb-2 font-semibold text-gray-900">{$t('analytics.highestRevenue')}</h4>
									<p class="text-lg font-bold text-blue-600">
										{trends.highestRevenue.property_title}
									</p>
									<p class="text-2xl font-bold text-blue-700">
										<CountUp value={trends.highestRevenue.annual_income} format="compact" />
									</p>
								</div>
							{/if}
						</div>
					{/if}
				</div>

				<!-- Areas for Improvement -->
				<div
					class="rounded-3xl border border-orange-200 bg-gradient-to-br from-orange-50 to-red-50 p-8"
				>
					<h3 class="mb-6 flex items-center gap-2 text-xl font-bold text-orange-900">
						<span>🎯</span>
						{$t('analytics.improvementAreas')}
					</h3>

					{#if trends.worstPerforming}
						<div class="space-y-4">
							<div class="rounded-2xl bg-white p-4">
								<h4 class="mb-2 font-semibold text-gray-900">{$t('analytics.lowestROI')}</h4>
								<p class="text-lg font-bold text-orange-600">
									{trends.worstPerforming.property_title}
								</p>
								<p class="text-2xl font-bold text-orange-700">
									<CountUp value={trends.worstPerforming.roi} decimals={1} suffix="% ROI" />
								</p>
							</div>

							{#if trends.mostExpensive}
								<div class="rounded-2xl bg-white p-4">
									<h4 class="mb-2 font-semibold text-gray-900">
										{$t('analytics.highestExpenses')}
									</h4>
									<p class="text-lg font-bold text-red-600">
										{trends.mostExpensive.property_title}
									</p>
									<p class="text-2xl font-bold text-red-700">
										<CountUp value={trends.mostExpensive.total_expenses} format="compact" />
									</p>
								</div>
							{/if}
						</div>
					{/if}
				</div>
			</div>
		</StaggeredList>

		<!-- Enhanced Data Table -->
		{#if analyticsData.length > 0}
			<FadeInUp delay={400}>
				<div class="overflow-hidden rounded-3xl border border-gray-100 bg-white shadow-lg">
					<div class="border-b border-gray-200 px-8 py-6">
						<h3 class="flex items-center gap-2 text-2xl font-bold text-gray-900">
							<span>📋</span>
							{$t('analytics.detailedBreakdown')}
						</h3>
					</div>

					<div class="overflow-x-auto">
						<table class="min-w-full divide-y divide-gray-200">
							<thead class="bg-gray-50">
								<tr>
									<th
										class="px-6 py-4 text-left text-xs font-bold tracking-wider text-gray-700 uppercase"
									>
										{$t('property.title')}
									</th>
									<th
										class="px-6 py-4 text-left text-xs font-bold tracking-wider text-gray-700 uppercase"
									>
										{$t('rental.monthlyRent')}
									</th>
									<th
										class="px-6 py-4 text-left text-xs font-bold tracking-wider text-gray-700 uppercase"
									>
										{$t('analytics.annualIncome')}
									</th>
									<th
										class="px-6 py-4 text-left text-xs font-bold tracking-wider text-gray-700 uppercase"
									>
										{$t('analytics.totalExpenses')}
									</th>
									<th
										class="px-6 py-4 text-left text-xs font-bold tracking-wider text-gray-700 uppercase"
									>
										{$t('analytics.netIncome')}
									</th>
									<th
										class="px-6 py-4 text-left text-xs font-bold tracking-wider text-gray-700 uppercase"
									>
										{$t('analytics.occupancy')}
									</th>
									<th
										class="px-6 py-4 text-left text-xs font-bold tracking-wider text-gray-700 uppercase"
									>
										{$t('analytics.roi')}
									</th>
								</tr>
							</thead>
							<tbody class="divide-y divide-gray-200 bg-white">
								{#each analyticsData as property, index}
									<tr class="transition-colors duration-200 hover:bg-gray-50">
										<td class="px-6 py-4 whitespace-nowrap">
											<div class="text-sm font-bold text-gray-900">{property.property_title}</div>
										</td>
										<td class="px-6 py-4 font-mono text-sm whitespace-nowrap text-gray-900">
											<CountUp value={property.monthly_rent} format="currency" />
										</td>
										<td class="px-6 py-4 font-mono text-sm whitespace-nowrap text-gray-900">
											<CountUp value={property.annual_income} format="currency" />
										</td>
										<td class="px-6 py-4 font-mono text-sm whitespace-nowrap text-gray-900">
											<CountUp value={property.total_expenses} format="currency" />
										</td>
										<td
											class="px-6 py-4 font-mono text-sm font-bold whitespace-nowrap {property.net_income >=
											0
												? 'text-green-600'
												: 'text-red-600'}"
										>
											<CountUp value={property.net_income} format="currency" />
										</td>
										<td class="px-6 py-4 whitespace-nowrap">
											<div class="flex items-center gap-2">
												<ProgressRing
													progress={property.occupancy_rate}
													size={30}
													strokeWidth={3}
													color="#3b82f6"
													showText={false}
												/>
												<span class="font-mono text-sm text-gray-900">
													<CountUp value={property.occupancy_rate} decimals={0} suffix="%" />
												</span>
											</div>
										</td>
										<td
											class="px-6 py-4 font-mono text-sm font-bold whitespace-nowrap {property.roi >=
											0
												? 'text-green-600'
												: 'text-red-600'}"
										>
											<CountUp value={property.roi} decimals={1} suffix="%" />
										</td>
									</tr>
								{/each}
							</tbody>
						</table>
					</div>
				</div>
			</FadeInUp>
		{/if}

		<!-- Last Updated -->
		<FadeInUp delay={500}>
			<div class="py-4 text-center text-sm text-gray-500">
				<span class="flex items-center justify-center gap-2">
					<span>🕒</span>
					{$t('analytics.lastUpdated')}: {new Date().toLocaleString()}
				</span>
			</div>
		</FadeInUp>
	{/if}
</div>

<style>
	.analytics-dashboard-pro {
		min-height: 50vh;
	}

	/* Enhanced table styling */
	table {
		font-variant-numeric: tabular-nums;
	}

	/* Custom scrollbar for table */
	.overflow-x-auto::-webkit-scrollbar {
		height: 8px;
	}

	.overflow-x-auto::-webkit-scrollbar-track {
		background: #f1f5f9;
		border-radius: 4px;
	}

	.overflow-x-auto::-webkit-scrollbar-thumb {
		background: #cbd5e1;
		border-radius: 4px;
	}

	.overflow-x-auto::-webkit-scrollbar-thumb:hover {
		background: #94a3b8;
	}
</style>
