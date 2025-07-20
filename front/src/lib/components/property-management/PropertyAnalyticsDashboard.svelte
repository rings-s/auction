<script>
	import { onMount, onDestroy } from 'svelte';
	import { analyticsAPI } from '$lib/api/propertyManagement.js';
	import { getTranslation } from '$lib/i18n/index.js';
	import { formatCurrency } from '$lib/utils/currency.js';
	import LoadingSkeleton from '$lib/components/ui/LoadingSkeleton.svelte';
	import Alert from '$lib/components/ui/Alert.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import StatCard from '$lib/components/dashboard/StatCard.svelte';

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

	// Chart containers
	let revenueChart;
	let occupancyChart;
	let roiChart;

	$: t = getTranslation;
	$: pageTitle =
		title || (propertyId ? $t('analytics.propertyAnalytics') : $t('analytics.portfolioAnalytics'));

	onMount(() => {
		loadAnalytics();
		// Set up auto-refresh every 5 minutes
		refreshInterval = setInterval(loadAnalytics, 5 * 60 * 1000);

		// Load Plotly if charts are available
		if (typeof window !== 'undefined') {
			loadPlotlyCharts();
		}
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

			// Render charts after data is loaded
			if (typeof window !== 'undefined' && Object.keys(charts).length > 0) {
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
			// Dynamically import Plotly
			const Plotly = await import('plotly.js-dist-min');
			window.Plotly = Plotly.default;
		} catch (err) {
			console.warn('Plotly not available, falling back to basic charts');
		}
	}

	function renderCharts() {
		if (!window.Plotly || !charts) return;

		try {
			// Revenue vs Expenses Chart
			if (charts.revenue_expenses && revenueChart) {
				const chartData = JSON.parse(charts.revenue_expenses);
				window.Plotly.newPlot(revenueChart, chartData.data, chartData.layout, {
					responsive: true,
					displayModeBar: false
				});
			}

			// Occupancy Chart
			if (charts.occupancy && occupancyChart) {
				const chartData = JSON.parse(charts.occupancy);
				window.Plotly.newPlot(occupancyChart, chartData.data, chartData.layout, {
					responsive: true,
					displayModeBar: false
				});
			}

			// ROI Chart
			if (charts.roi && roiChart) {
				const chartData = JSON.parse(charts.roi);
				window.Plotly.newPlot(roiChart, chartData.data, chartData.layout, {
					responsive: true,
					displayModeBar: false
				});
			}
		} catch (err) {
			console.error('Error rendering charts:', err);
		}
	}

	function handleRefresh() {
		loadAnalytics();
	}

	function handleExportData() {
		// Export analytics data as CSV
		const csvContent = convertToCSV(analyticsData);
		const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
		const link = document.createElement('a');
		if (link.download !== undefined) {
			const url = URL.createObjectURL(blob);
			link.setAttribute('href', url);
			link.setAttribute(
				'download',
				`property-analytics-${new Date().toISOString().split('T')[0]}.csv`
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

	function calculateTrendPercentage(current, previous) {
		if (!previous || previous === 0) return 0;
		return ((current - previous) / previous) * 100;
	}
</script>

<div class="space-y-6">
	<!-- Header -->
	<div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
		<div>
			<h1 class="text-2xl font-bold text-gray-900">{pageTitle}</h1>
			<p class="text-gray-600">{$t('analytics.subtitle')}</p>
		</div>

		<div class="flex gap-2">
			<Button variant="outline" size="sm" on:click={handleRefresh} disabled={loading}>
				🔄 {$t('common.refresh')}
			</Button>
			<Button
				variant="outline"
				size="sm"
				on:click={handleExportData}
				disabled={loading || !analyticsData.length}
			>
				📊 {$t('analytics.exportData')}
			</Button>
		</div>
	</div>

	<!-- Error Display -->
	{#if error}
		<Alert type="error" message={error} />
	{/if}

	<!-- Loading State -->
	{#if loading && !analyticsData.length}
		<div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
			{#each Array(4) as _}
				<LoadingSkeleton height="120px" />
			{/each}
		</div>
		<div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
			{#each Array(3) as _}
				<LoadingSkeleton height="300px" />
			{/each}
		</div>
	{:else if analyticsData.length === 0 && !loading}
		<!-- Empty State -->
		<div class="py-12 text-center">
			<div class="mb-4 text-6xl">📊</div>
			<h3 class="mb-2 text-lg font-medium text-gray-900">{$t('analytics.noData')}</h3>
			<p class="text-gray-600">{$t('analytics.noDataDescription')}</p>
		</div>
	{:else}
		<!-- Summary Stats -->
		<div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
			<StatCard
				title={$t('analytics.totalProperties')}
				value={summary.total_properties || 0}
				icon="🏠"
				variant="blue"
			/>

			<StatCard
				title={$t('analytics.totalAnnualIncome')}
				value={formatCurrency(summary.total_annual_income || 0)}
				icon="💰"
				variant="green"
			/>

			<StatCard
				title={$t('analytics.totalExpenses')}
				value={formatCurrency(summary.total_expenses || 0)}
				icon="📉"
				variant="red"
			/>

			<StatCard
				title={$t('analytics.averageOccupancy')}
				value="{Math.round(summary.average_occupancy || 0)}%"
				icon="📊"
				variant="purple"
			/>
		</div>

		<!-- Net Income and ROI -->
		<div class="grid grid-cols-1 gap-6 md:grid-cols-2">
			<div class="rounded-lg border border-gray-200 bg-white p-6">
				<h3 class="mb-2 text-lg font-semibold text-gray-900">{$t('analytics.netIncome')}</h3>
				<p class="text-3xl font-bold text-green-600">
					{formatCurrency((summary.total_annual_income || 0) - (summary.total_expenses || 0))}
				</p>
				<p class="mt-1 text-sm text-gray-600">{$t('analytics.netIncomeDescription')}</p>
			</div>

			<div class="rounded-lg border border-gray-200 bg-white p-6">
				<h3 class="mb-2 text-lg font-semibold text-gray-900">{$t('analytics.averageROI')}</h3>
				<p
					class="text-3xl font-bold {(summary.average_roi || 0) >= 0
						? 'text-green-600'
						: 'text-red-600'}"
				>
					{(summary.average_roi || 0).toFixed(1)}%
				</p>
				<p class="mt-1 text-sm text-gray-600">{$t('analytics.roiDescription')}</p>
			</div>
		</div>

		<!-- Charts Section -->
		{#if Object.keys(charts).length > 0}
			<div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
				<!-- Revenue vs Expenses Chart -->
				{#if charts.revenue_expenses}
					<div class="rounded-lg border border-gray-200 bg-white p-6">
						<h3 class="mb-4 text-lg font-semibold text-gray-900">
							{$t('analytics.revenueVsExpenses')}
						</h3>
						<div bind:this={revenueChart} class="h-64"></div>
					</div>
				{/if}

				<!-- Occupancy Rate Chart -->
				{#if charts.occupancy}
					<div class="rounded-lg border border-gray-200 bg-white p-6">
						<h3 class="mb-4 text-lg font-semibold text-gray-900">
							{$t('analytics.occupancyRates')}
						</h3>
						<div bind:this={occupancyChart} class="h-64"></div>
					</div>
				{/if}

				<!-- ROI Chart -->
				{#if charts.roi}
					<div class="rounded-lg border border-gray-200 bg-white p-6 lg:col-span-2">
						<h3 class="mb-4 text-lg font-semibold text-gray-900">
							{$t('analytics.returnOnInvestment')}
						</h3>
						<div bind:this={roiChart} class="h-64"></div>
					</div>
				{/if}
			</div>
		{/if}

		<!-- Detailed Property Analytics Table -->
		{#if analyticsData.length > 0}
			<div class="overflow-hidden rounded-lg border border-gray-200 bg-white">
				<div class="border-b border-gray-200 px-6 py-4">
					<h3 class="text-lg font-semibold text-gray-900">{$t('analytics.detailedBreakdown')}</h3>
				</div>

				<div class="overflow-x-auto">
					<table class="min-w-full divide-y divide-gray-200">
						<thead class="bg-gray-50">
							<tr>
								<th
									class="px-6 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase"
								>
									{$t('property.title')}
								</th>
								<th
									class="px-6 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase"
								>
									{$t('rental.monthlyRent')}
								</th>
								<th
									class="px-6 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase"
								>
									{$t('analytics.annualIncome')}
								</th>
								<th
									class="px-6 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase"
								>
									{$t('analytics.totalExpenses')}
								</th>
								<th
									class="px-6 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase"
								>
									{$t('analytics.netIncome')}
								</th>
								<th
									class="px-6 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase"
								>
									{$t('analytics.occupancy')}
								</th>
								<th
									class="px-6 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase"
								>
									{$t('analytics.roi')}
								</th>
							</tr>
						</thead>
						<tbody class="divide-y divide-gray-200 bg-white">
							{#each analyticsData as property}
								<tr class="hover:bg-gray-50">
									<td class="px-6 py-4 whitespace-nowrap">
										<div class="text-sm font-medium text-gray-900">{property.property_title}</div>
									</td>
									<td class="px-6 py-4 text-sm whitespace-nowrap text-gray-900">
										{formatCurrency(property.monthly_rent)}
									</td>
									<td class="px-6 py-4 text-sm whitespace-nowrap text-gray-900">
										{formatCurrency(property.annual_income)}
									</td>
									<td class="px-6 py-4 text-sm whitespace-nowrap text-gray-900">
										{formatCurrency(property.total_expenses)}
									</td>
									<td
										class="px-6 py-4 text-sm font-medium whitespace-nowrap {property.net_income >= 0
											? 'text-green-600'
											: 'text-red-600'}"
									>
										{formatCurrency(property.net_income)}
									</td>
									<td class="px-6 py-4 text-sm whitespace-nowrap text-gray-900">
										{Math.round(property.occupancy_rate)}%
									</td>
									<td
										class="px-6 py-4 text-sm font-medium whitespace-nowrap {property.roi >= 0
											? 'text-green-600'
											: 'text-red-600'}"
									>
										{property.roi.toFixed(1)}%
									</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
			</div>
		{/if}

		<!-- Last Updated -->
		<div class="text-center text-sm text-gray-500">
			{$t('analytics.lastUpdated')}: {new Date().toLocaleString()}
		</div>
	{/if}
</div>
