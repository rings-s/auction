<script>
	import { onMount } from 'svelte';
	import { fade, scale, fly } from 'svelte/transition';
	import { t } from '$lib/i18n';
	import { analyticsAPI } from '$lib/api/propertyManagement.js';
	import InteractiveChart from './InteractiveChart.svelte';
	import MetricCard from './MetricCard.svelte';
	import PerformanceHeatmap from './PerformanceHeatmap.svelte';
	import LoadingSkeleton from '$lib/components/ui/LoadingSkeleton.svelte';
	import Alert from '$lib/components/ui/Alert.svelte';

	export let selectedPeriod = 'month';
	export let selectedProperty = 'all';

	let loading = true;
	let error = '';
	let analytics = null;
	let activeTab = 'overview';

	onMount(() => {
		loadAnalytics();
	});

	async function loadAnalytics() {
		try {
			loading = true;
			error = '';

			const response = await analyticsAPI.getAnalytics(
				selectedProperty === 'all' ? null : selectedProperty
			);

			if (response.data) {
				analytics = response.data;
			}
		} catch (err) {
			error = err.message || $t('errors.loadingFailed');
			console.error('Failed to load analytics:', err);

			// Enhanced fallback data for better visualization
			analytics = {
				revenue: {
					total: 850000,
					monthly: 75000,
					growth: 12.5,
					previous_month: 67000
				},
				expenses: {
					total: 320000,
					monthly: 28000,
					growth: -8.2,
					previous_month: 30500
				},
				properties: {
					total: 25,
					occupied: 22,
					vacant: 3,
					occupancy_rate: 88.0,
					previous_occupancy: 84.0
				},
				tenants: {
					total: 22,
					active: 20,
					pending: 2,
					satisfaction_rate: 94.5
				},
				maintenance: {
					total: 45,
					pending: 8,
					in_progress: 5,
					completed: 32,
					average_completion_time: 3.2
				},
				financial_summary: {
					net_income: 530000,
					profit_margin: 62.4,
					average_rent: 3200,
					roi: 8.9
				},
				charts: generateMockChartData(),
				trends: generateTrendData()
			};
		} finally {
			loading = false;
		}
	}

	function generateMockChartData() {
		return {
			revenue_trend: {
				labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
				datasets: [
					{
						label: 'Revenue',
						data: [65000, 72000, 68000, 78000, 82000, 75000],
						borderColor: 'rgb(99, 102, 241)',
						backgroundColor: 'rgba(99, 102, 241, 0.1)',
						tension: 0.4
					}
				]
			},
			expense_breakdown: {
				labels: ['Maintenance', 'Utilities', 'Insurance', 'Management', 'Marketing'],
				datasets: [
					{
						data: [35, 25, 15, 15, 10],
						backgroundColor: [
							'rgba(239, 68, 68, 0.8)',
							'rgba(245, 158, 11, 0.8)',
							'rgba(34, 197, 94, 0.8)',
							'rgba(99, 102, 241, 0.8)',
							'rgba(236, 72, 153, 0.8)'
						],
						borderWidth: 2,
						borderColor: '#fff'
					}
				]
			},
			occupancy_performance: {
				labels: ['Property A', 'Property B', 'Property C', 'Property D', 'Property E'],
				datasets: [
					{
						label: 'Occupancy Rate (%)',
						data: [92, 88, 95, 78, 85],
						backgroundColor: 'rgba(34, 197, 94, 0.8)',
						borderColor: 'rgb(34, 197, 94)',
						borderWidth: 2
					}
				]
			}
		};
	}

	function generateTrendData() {
		return [
			{ title: 'Building A', revenue: 45000, expenses: 18000, occupancy: 92, maintenance: 3 },
			{ title: 'Building B', revenue: 38000, expenses: 15000, occupancy: 88, maintenance: 5 },
			{ title: 'Building C', revenue: 52000, expenses: 22000, occupancy: 95, maintenance: 2 },
			{ title: 'Building D', revenue: 35000, expenses: 16000, occupancy: 78, maintenance: 8 },
			{ title: 'Building E', revenue: 41000, expenses: 19000, occupancy: 85, maintenance: 4 }
		];
	}

	function formatCurrency(amount) {
		return `${amount?.toLocaleString() || 0} SAR`;
	}

	function formatPercentage(value) {
		return `${value?.toFixed(1) || 0}%`;
	}

	const tabs = [
		{ id: 'overview', label: 'Overview', icon: '📊' },
		{ id: 'financial', label: 'Financial', icon: '💰' },
		{ id: 'performance', label: 'Performance', icon: '⚡' },
		{ id: 'trends', label: 'Trends', icon: '📈' }
	];
</script>

<div class="advanced-analytics-dashboard" in:fade={{ duration: 400 }}>
	<!-- Error Display -->
	{#if error}
		<Alert type="warning" message={error} />
	{/if}

	<!-- Tab Navigation -->
	<div class="tab-navigation mb-8" in:fly={{ y: -20, duration: 500, delay: 200 }}>
		<div class="tab-container">
			{#each tabs as tab, index}
				<button
					class="tab-button"
					class:active={activeTab === tab.id}
					on:click={() => (activeTab = tab.id)}
					in:scale={{ duration: 300, delay: index * 100 }}
				>
					<span class="tab-icon">{tab.icon}</span>
					<span class="tab-label">{tab.label}</span>
				</button>
			{/each}
		</div>
	</div>

	{#if loading}
		<div class="loading-grid">
			{#each Array(6) as _}
				<LoadingSkeleton height="200px" />
			{/each}
		</div>
	{:else if analytics}
		<!-- Overview Tab -->
		{#if activeTab === 'overview'}
			<div class="tab-content" in:fade={{ duration: 400 }}>
				<!-- Key Metrics Grid -->
				<div class="metrics-grid mb-8" in:fly={{ y: 20, duration: 600, delay: 100 }}>
					<MetricCard
						title={$t('analytics.totalRevenue')}
						value={analytics?.revenue?.total || 0}
						previousValue={analytics?.revenue
							? analytics.revenue.total -
								(analytics.revenue.monthly * analytics.revenue.growth) / 100
							: 0}
						formatter={formatCurrency}
						icon="💰"
						color="green"
					/>
					<MetricCard
						title={$t('analytics.totalExpenses')}
						value={analytics?.expenses?.total || 0}
						previousValue={analytics?.expenses
							? analytics.expenses.total -
								(analytics.expenses.monthly * Math.abs(analytics.expenses.growth)) / 100
							: 0}
						formatter={formatCurrency}
						icon="📊"
						color="red"
					/>
					<MetricCard
						title={$t('analytics.netIncome')}
						value={analytics?.financial_summary?.net_income || 0}
						previousValue={analytics?.financial_summary
							? analytics.financial_summary.net_income * 0.92
							: 0}
						formatter={formatCurrency}
						icon="💎"
						color="indigo"
						subtitle={`${formatPercentage(analytics?.financial_summary?.profit_margin || 0)} margin`}
					/>
					<MetricCard
						title={$t('analytics.occupancyRate')}
						value={analytics?.properties?.occupancy_rate || 0}
						previousValue={analytics?.properties?.previous_occupancy || 80}
						formatter={formatPercentage}
						icon="🏠"
						color="blue"
						subtitle={`${analytics?.properties?.occupied || 0}/${analytics?.properties?.total || 0} properties`}
					/>
				</div>

				<!-- Charts Row -->
				<div class="charts-grid mb-8" in:fly={{ y: 20, duration: 600, delay: 300 }}>
					<InteractiveChart
						type="line"
						title="Revenue Trend (6 months)"
						data={analytics?.charts?.revenue_trend || { labels: [], datasets: [] }}
						height={300}
						options={{
							plugins: {
								legend: { display: false }
							},
							scales: {
								y: {
									ticks: {
										callback: function (value) {
											return formatCurrency(value);
										}
									}
								}
							}
						}}
					/>
					<InteractiveChart
						type="doughnut"
						title="Expense Breakdown"
						data={analytics?.charts?.expense_breakdown || { labels: [], datasets: [] }}
						height={300}
						options={{
							plugins: {
								legend: { position: 'right' }
							}
						}}
					/>
				</div>
			</div>
		{/if}

		<!-- Financial Tab -->
		{#if activeTab === 'financial'}
			<div class="tab-content" in:fade={{ duration: 400 }}>
				<div class="financial-overview mb-8" in:fly={{ y: 20, duration: 600, delay: 100 }}>
					<div class="metrics-grid">
						<MetricCard
							title="Monthly Revenue"
							value={analytics?.revenue?.monthly || 0}
							previousValue={analytics?.revenue?.previous_month ||
								(analytics?.revenue?.monthly || 0) * 0.9}
							formatter={formatCurrency}
							icon="📈"
							color="green"
						/>
						<MetricCard
							title="Monthly Expenses"
							value={analytics?.expenses?.monthly || 0}
							previousValue={analytics?.expenses?.previous_month ||
								(analytics?.expenses?.monthly || 0) * 1.1}
							formatter={formatCurrency}
							icon="📉"
							color="red"
						/>
						<MetricCard
							title="Average Rent"
							value={analytics?.financial_summary?.average_rent || 0}
							previousValue={(analytics?.financial_summary?.average_rent || 0) * 0.95}
							formatter={formatCurrency}
							icon="🏠"
							color="blue"
						/>
						<MetricCard
							title="ROI"
							value={analytics?.financial_summary?.roi || 0}
							previousValue={(analytics?.financial_summary?.roi || 0) * 0.88}
							formatter={formatPercentage}
							icon="📊"
							color="indigo"
						/>
					</div>
				</div>

				<div class="charts-grid" in:fly={{ y: 20, duration: 600, delay: 300 }}>
					<InteractiveChart
						type="bar"
						title="Monthly Income vs Expenses"
						data={{
							labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
							datasets: [
								{
									label: 'Income',
									data: [75000, 78000, 72000, 81000, 85000, 75000],
									backgroundColor: 'rgba(34, 197, 94, 0.8)'
								},
								{
									label: 'Expenses',
									data: [28000, 30000, 26000, 32000, 29000, 28000],
									backgroundColor: 'rgba(239, 68, 68, 0.8)'
								}
							]
						}}
						height={350}
					/>
				</div>
			</div>
		{/if}

		<!-- Performance Tab -->
		{#if activeTab === 'performance'}
			<div class="tab-content" in:fade={{ duration: 400 }}>
				<PerformanceHeatmap
					data={analytics?.trends || []}
					title="Property Performance Matrix"
					metrics={['revenue', 'expenses', 'occupancy', 'maintenance']}
					height={400}
				/>

				<div class="charts-grid mt-8" in:fly={{ y: 20, duration: 600, delay: 300 }}>
					<InteractiveChart
						type="bar"
						title="Occupancy Performance by Property"
						data={analytics?.charts?.occupancy_performance || { labels: [], datasets: [] }}
						height={300}
					/>
					<MetricCard
						title="Maintenance Efficiency"
						value={analytics?.maintenance?.average_completion_time || 0}
						previousValue={4.1}
						formatter={(val) => `${val} days`}
						icon="🔧"
						color="yellow"
						subtitle={`${analytics?.maintenance?.completed || 0} completed requests`}
					/>
				</div>
			</div>
		{/if}

		<!-- Trends Tab -->
		{#if activeTab === 'trends'}
			<div class="tab-content" in:fade={{ duration: 400 }}>
				<div class="trends-overview mb-8" in:fly={{ y: 20, duration: 600, delay: 100 }}>
					<div class="metrics-grid">
						<MetricCard
							title="Revenue Growth"
							value={analytics?.revenue?.growth || 0}
							formatter={formatPercentage}
							icon="📈"
							color="green"
							subtitle="Month over month"
						/>
						<MetricCard
							title="Expense Reduction"
							value={Math.abs(analytics?.expenses?.growth || 0)}
							formatter={formatPercentage}
							icon="📉"
							color="green"
							subtitle="Cost optimization"
						/>
						<MetricCard
							title="Tenant Satisfaction"
							value={analytics?.tenants?.satisfaction_rate || 94.5}
							formatter={formatPercentage}
							icon="😊"
							color="blue"
							subtitle="Survey results"
						/>
						<MetricCard
							title="Portfolio Growth"
							value={analytics?.properties?.total || 0}
							previousValue={23}
							formatter={(val) => `${val} properties`}
							icon="🏢"
							color="indigo"
						/>
					</div>
				</div>

				<div class="charts-grid" in:fly={{ y: 20, duration: 600, delay: 300 }}>
					<InteractiveChart
						type="line"
						title="6-Month Performance Trends"
						data={{
							labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
							datasets: [
								{
									label: 'Revenue Growth %',
									data: [8.2, 9.1, 7.8, 10.5, 12.1, 12.5],
									borderColor: 'rgb(34, 197, 94)',
									backgroundColor: 'rgba(34, 197, 94, 0.1)',
									tension: 0.4
								},
								{
									label: 'Occupancy Rate %',
									data: [82, 84, 85, 87, 86, 88],
									borderColor: 'rgb(99, 102, 241)',
									backgroundColor: 'rgba(99, 102, 241, 0.1)',
									tension: 0.4
								}
							]
						}}
						height={350}
					/>
				</div>
			</div>
		{/if}
	{/if}
</div>

<style>
	.advanced-analytics-dashboard {
		display: flex;
		flex-direction: column;
		gap: 2rem;
	}

	.tab-navigation {
		border-bottom: 1px solid #e5e7eb;
	}

	:global(.dark) .tab-navigation {
		border-bottom-color: #374151;
	}

	.tab-container {
		display: flex;
		gap: 0.25rem;
		overflow-x: auto;
	}

	.tab-button {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.75rem 1.5rem;
		border-top-left-radius: 0.75rem;
		border-top-right-radius: 0.75rem;
		font-weight: 500;
		font-size: 0.875rem;
		transition: all 0.2s;
		white-space: nowrap;
		color: #4b5563;
		border-bottom: 2px solid transparent;
	}

	.tab-button:hover {
		color: #111827;
		border-bottom-color: #d1d5db;
	}

	:global(.dark) .tab-button {
		color: #9ca3af;
	}

	:global(.dark) .tab-button:hover {
		color: #f9fafb;
		border-bottom-color: #4b5563;
	}

	.tab-button.active {
		color: #4f46e5;
		border-bottom-color: #6366f1;
		background: #eef2ff;
	}

	:global(.dark) .tab-button.active {
		color: #818cf8;
		background: rgba(79, 70, 229, 0.2);
	}

	.tab-icon {
		font-size: 1.125rem;
	}

	.tab-label {
		font-weight: 600;
	}

	.tab-content {
		display: flex;
		flex-direction: column;
		gap: 2rem;
	}

	.metrics-grid {
		display: grid;
		grid-template-columns: 1fr;
		gap: 1.5rem;
	}

	@media (min-width: 768px) {
		.metrics-grid {
			grid-template-columns: repeat(2, 1fr);
		}
	}

	@media (min-width: 1024px) {
		.metrics-grid {
			grid-template-columns: repeat(4, 1fr);
		}
	}

	.charts-grid {
		display: grid;
		grid-template-columns: 1fr;
		gap: 2rem;
	}

	@media (min-width: 1024px) {
		.charts-grid {
			grid-template-columns: repeat(2, 1fr);
		}
	}

	.loading-grid {
		display: grid;
		grid-template-columns: 1fr;
		gap: 1.5rem;
	}

	@media (min-width: 768px) {
		.loading-grid {
			grid-template-columns: repeat(2, 1fr);
		}
	}

	@media (min-width: 1024px) {
		.loading-grid {
			grid-template-columns: repeat(3, 1fr);
		}
	}

	.financial-overview {
		background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%);
		border-radius: 1rem;
		padding: 1.5rem;
		border: 1px solid #bbf7d0;
	}

	:global(.dark) .financial-overview {
		background: linear-gradient(135deg, rgba(34, 197, 94, 0.2) 0%, rgba(16, 185, 129, 0.2) 100%);
		border-color: #166534;
	}

	.trends-overview {
		background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
		border-radius: 1rem;
		padding: 1.5rem;
		border: 1px solid #93c5fd;
	}

	:global(.dark) .trends-overview {
		background: linear-gradient(135deg, rgba(59, 130, 246, 0.2) 0%, rgba(79, 70, 229, 0.2) 100%);
		border-color: #1e40af;
	}
</style>
