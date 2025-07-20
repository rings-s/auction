<!-- src/routes/dashboard/+page.svelte -->
<script>
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { t } from '$lib/i18n';
	import { user } from '$lib/stores/user';
	import {
		dashboardStats,
		dashboardActivity,
		dashboardLoading,
		dashboardError,
		userPriority,
		canAccessSystemDashboard
	} from '$lib/stores/dashboard';
	import {
		getUserDashboardStats,
		getRecentActivity,
		refreshDashboardData
	} from '$lib/api/dashboard';
	import { getComprehensiveAnalytics } from '$lib/api/analytics';
	import { getPayments } from '$lib/api/payment';
	import { getWorkers } from '$lib/api/worker';
	import { getBankAccounts } from '$lib/api/bankAccount';
	import { toast } from '$lib/stores/toastStore.svelte.js';

	// Components
	import StatCard from '$lib/components/dashboard/StatCard.svelte';
	import ActivityFeed from '$lib/components/dashboard/ActivityFeed.svelte';
	import QuickActions from '$lib/components/dashboard/QuickActions.svelte';
	import LoadingSkeleton from '$lib/components/ui/LoadingSkeleton.svelte';
	import Alert from '$lib/components/ui/Alert.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Breadcrumb from '$lib/components/ui/Breadcrumb.svelte';

	let refreshing = false;
	let mounted = false;

	// Property management data
	let propertyManagementStats = null;
	let recentPayments = [];
	let recentWorkers = [];
	let bankAccounts = [];
	let pmLoading = false;

	// Breadcrumb items
	$: breadcrumbItems = [
		{ label: $t('nav.home'), href: '/' },
		{ label: $t('dashboard.title'), href: '/dashboard', active: true }
	];

	const propertyIcon = `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
        <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z"/>
    </svg>`;

	const auctionIcon = `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
        <path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z"/>
    </svg>`;

	const bidIcon = `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
    <path d="M8.433 7.418c.155-.103.346-.196.567-.267v1.698a2.305 2.305 0 01-.567-.267C8.07 8.34 8 8.114 8 8c0-.114.07-.34.433-.582zM11 12.849v-1.698c.22.071.412.164.567.267.364.243.433.468.433.582 0 .114-.07.34-.433.582a2.305 2.305 0 01-.567.267z"/>
        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-13a1 1 0 10-2 0v.092a4.535 4.535 0 00-1.676.662C6.602 6.234 6 7.009 6 8c0 .99.602 1.765 1.324 2.246.48.32 1.054.545 1.676.662v1.941c-.391-.127-.68-.317-.843-.504a1 1 0 10-1.51 1.31c.562.649 1.413 1.076 2.353 1.253V15a1 1 0 102 0v-.092a4.535 4.535 0 001.676-.662C13.398 13.766 14 12.991 14 12c0-.99-.602-1.765-1.324-2.246A4.535 4.535 0 0011 9.092V7.151c.391.127.68.317.843.504a1 1 0 101.511-1.31c-.563-.649-1.413-1.076-2.354-1.253V5z" clip-rule="evenodd"/>
    </svg>`;

	const messageIcon = `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
    <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z"/>
        <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z"/>
    </svg>`;

	// Property Management Icons
	const bankIcon = `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
		<path d="M4 4a2 2 0 00-2 2v4a2 2 0 002 2V6h10a2 2 0 00-2-2H4zm2 6a2 2 0 012-2h8a2 2 0 012 2v4a2 2 0 01-2 2H8a2 2 0 01-2-2v-4zm6 4a2 2 0 100-4 2 2 0 000 4z"/>
	</svg>`;

	const paymentIcon = `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
		<path d="M4 4a2 2 0 00-2 2v1h16V6a2 2 0 00-2-2H4z"/>
		<path fill-rule="evenodd" d="M18 9H2v5a2 2 0 002 2h12a2 2 0 002-2V9zM4 13a1 1 0 011-1h1a1 1 0 110 2H5a1 1 0 01-1-1zm5-1a1 1 0 100 2h1a1 1 0 100-2H9z" clip-rule="evenodd"/>
	</svg>`;

	const workerIcon = `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
		<path d="M9 6a3 3 0 11-6 0 3 3 0 016 0zM17 6a3 3 0 11-6 0 3 3 0 016 0zM12.93 17c.046-.327.07-.66.07-1a6.97 6.97 0 00-1.5-4.33A5 5 0 0119 16v1h-6.07zM6 11a5 5 0 015 5v1H1v-1a5 5 0 015-5z"/>
	</svg>`;

	const analyticsIcon = `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
		<path d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5zM8 7a1 1 0 011-1h2a1 1 0 011 1v9a1 1 0 01-1 1H9a1 1 0 01-1-1V7zM14 4a1 1 0 011-1h2a1 1 0 011 1v12a1 1 0 01-1 1h-2a1 1 0 01-1-1V4z"/>
	</svg>`;

	// Load property management data
	async function loadPropertyManagementData() {
		try {
			pmLoading = true;
			
			const [analytics, payments, workers, accounts] = await Promise.all([
				getComprehensiveAnalytics({ timeRange: '30d' }),
				getPayments({ limit: 5 }),
				getWorkers({ limit: 5, status: 'active' }),
				getBankAccounts()
			]);

			propertyManagementStats = analytics;
			recentPayments = payments;
			recentWorkers = workers;
			bankAccounts = accounts;
		} catch (error) {
			console.error('Error loading property management data:', error);
			// Don't show error for property management data as it's optional
		} finally {
			pmLoading = false;
		}
	}

	// Load dashboard data
	async function loadDashboardData() {
		if (!$user) {
			goto('/login');
			return;
		}

		dashboardLoading.set(true);
		dashboardError.set(null);

		try {
			const [stats, activity] = await Promise.all([
				getUserDashboardStats(), 
				getRecentActivity(10),
				loadPropertyManagementData() // Load property management data in parallel
			]);

			dashboardStats.set(stats);
			dashboardActivity.set(activity);
		} catch (error) {
			dashboardError.set(error.message);
			toast.error($t('dashboard.loadError'));
		} finally {
			dashboardLoading.set(false);
		}
	}

	// Refresh dashboard data
	async function handleRefresh() {
		if (refreshing) return;

		refreshing = true;
		try {
			await loadDashboardData();
			toast.success($t('dashboard.refreshed'));
		} catch (error) {
			toast.error($t('dashboard.refreshError'));
		} finally {
			refreshing = false;
		}
	}

	// Auto-refresh every 5 minutes
	let refreshInterval;
	onMount(() => {
		mounted = true;
		loadDashboardData();

		refreshInterval = setInterval(
			() => {
				if (document.visibilityState === 'visible') {
					loadDashboardData();
				}
			},
			5 * 60 * 1000
		); // 5 minutes

		return () => {
			if (refreshInterval) {
				clearInterval(refreshInterval);
			}
		};
	});

	// Computed values
	$: stats = $dashboardStats;
	$: activities = $dashboardActivity;
	$: isLoading = $dashboardLoading;
	$: error = $dashboardError;
</script>

<svelte:head>
	<title>{$t('dashboard.title')} - {$t('app.name')}</title>
	<meta name="description" content={$t('dashboard.description')} />
</svelte:head>

<div class="min-h-screen">
	<div class="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
		<!-- Header -->
		<div class="mb-6">
			<div class="flex flex-col sm:flex-row sm:items-center sm:justify-between">
				<div>
					<h1 class="text-xl font-semibold text-gray-900">
						{$t('dashboard.title')}
					</h1>
					<p class="mt-1 text-sm text-gray-600">
						{$t('dashboard.welcome', { name: $user?.first_name || $user?.email })}
					</p>
				</div>

				<div class="mt-4 flex items-center space-x-3 sm:mt-0">
					{#if $canAccessSystemDashboard}
						<Button variant="outline" size="compact" href="/dashboard/system">
							{$t('dashboard.systemDashboard')}
						</Button>
					{/if}

					<Button variant="outline" size="compact" loading={refreshing} onClick={handleRefresh}>
						{$t('common.refresh')}
					</Button>
				</div>
			</div>
		</div>

		<!-- Error Alert -->
		{#if error}
			<Alert type="error" title={$t('error.title')} message={error} dismissible class="mb-6" />
		{/if}

		<!-- Main Dashboard Content -->
		<div class="grid grid-cols-1 gap-6 lg:grid-cols-4">
			<!-- Stats Overview -->
			<div class="space-y-6 lg:col-span-3">
				<!-- Key Metrics -->
				<div class="grid grid-cols-2 gap-4 md:grid-cols-4 lg:grid-cols-6">
					{#if isLoading}
						{#each Array(6) as _, i}
							<LoadingSkeleton type="rect" height="80px" />
						{/each}
					{:else if stats}
						<!-- Auction Platform Metrics -->
						<StatCard
							title={$t('dashboard.totalProperties')}
							value={stats.total_properties || 0}
							icon={propertyIcon}
							color="primary"
							href="/dashboard/properties"
						/>

						<StatCard
							title={$t('dashboard.totalAuctions')}
							value={stats.total_auctions || 0}
							icon={auctionIcon}
							color="success"
							href="/dashboard/auctions"
						/>

						<StatCard
							title={$t('dashboard.totalBids')}
							value={stats.total_bids || 0}
							icon={bidIcon}
							color="warning"
							href="/dashboard/bids"
						/>

						<!-- Property Management Metrics -->
						{#if propertyManagementStats}
							<StatCard
								title={$t('dashboard.totalPayments')}
								value={propertyManagementStats.totalPayments || 0}
								icon={paymentIcon}
								color="info"
								href="/dashboard/payments"
							/>

							<StatCard
								title={$t('dashboard.activeWorkers')}
								value={propertyManagementStats.activeWorkers || 0}
								icon={workerIcon}
								color="success"
								href="/dashboard/workers"
							/>

							<StatCard
								title={$t('dashboard.bankAccounts')}
								value={bankAccounts.length || 0}
								icon={bankIcon}
								color="primary"
								href="/dashboard/bank-accounts"
							/>
						{:else}
							<StatCard
								title={$t('dashboard.unreadMessages')}
								value={stats.messages_unread || 0}
								icon={messageIcon}
								color="info"
								href="/messages?filter=unread"
							/>
						{/if}
					{/if}
				</div>

				<!-- Additional Stats for Advanced Users -->
				{#if stats && $userPriority >= 3}
					<div class="grid grid-cols-1 gap-4 md:grid-cols-3">
						<StatCard
							title={$t('dashboard.publishedProperties')}
							value={stats.published_properties || 0}
							color="success"
							compact
						/>

						<StatCard
							title={$t('dashboard.activeAuctions')}
							value={stats.active_auctions || 0}
							color="primary"
							compact
						/>

						<StatCard
							title={$t('dashboard.winningBids')}
							value={stats.winning_bids || 0}
							color="warning"
							compact
						/>
					</div>
				{/if}

				<!-- Property Management Analytics -->
				{#if propertyManagementStats}
					<div class="grid grid-cols-1 gap-4 md:grid-cols-4">
						<StatCard
							title={$t('dashboard.totalRevenue')}
							value="${propertyManagementStats.totalRevenue?.toLocaleString() || '0'}"
							color="success"
							compact
						/>

						<StatCard
							title={$t('dashboard.occupancyRate')}
							value="{propertyManagementStats.occupancyRate?.toFixed(1) || '0'}%"
							color={propertyManagementStats.occupancyRate >= 80 ? 'success' : propertyManagementStats.occupancyRate >= 60 ? 'warning' : 'error'}
							compact
						/>

						<StatCard
							title={$t('dashboard.pendingPayments')}
							value={propertyManagementStats.pendingPayments || 0}
							color={propertyManagementStats.pendingPayments > 0 ? 'warning' : 'success'}
							compact
						/>

						<StatCard
							title={$t('dashboard.utilizationRate')}
							value="{propertyManagementStats.workerUtilization?.toFixed(1) || '0'}%"
							color={propertyManagementStats.workerUtilization >= 80 ? 'success' : propertyManagementStats.workerUtilization >= 60 ? 'warning' : 'error'}
							compact
						/>
					</div>

					<!-- Quick Access Cards -->
					<div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
						<!-- Recent Payments -->
						<div class="rounded-lg border border-gray-200 bg-white p-4 dark:bg-gray-800 dark:border-gray-700">
							<div class="flex items-center justify-between mb-4">
								<h3 class="text-sm font-medium text-gray-900 dark:text-white">
									{$t('dashboard.recentPayments')}
								</h3>
								<Button variant="outline" size="compact" href="/dashboard/payments">
									{$t('common.viewAll')}
								</Button>
							</div>
							
							{#if pmLoading}
								<div class="space-y-2">
									{#each Array(3) as _}
										<LoadingSkeleton type="rect" height="40px" />
									{/each}
								</div>
							{:else if recentPayments.length > 0}
								<div class="space-y-3">
									{#each recentPayments.slice(0, 3) as payment}
										<div class="flex items-center justify-between">
											<div class="min-w-0 flex-1">
												<p class="text-sm font-medium text-gray-900 dark:text-white font-mono">
													{payment.payment_id}
												</p>
												<p class="text-xs text-gray-500 dark:text-gray-400">
													{payment.payment_type} • {new Date(payment.due_date || payment.created_at).toLocaleDateString()}
												</p>
											</div>
											<div class="text-right">
												<p class="text-sm font-medium text-gray-900 dark:text-white">
													${payment.amount}
												</p>
												<span class="inline-flex items-center px-1.5 py-0.5 rounded-full text-xs font-medium bg-{payment.status === 'completed' ? 'green' : payment.status === 'pending' ? 'yellow' : 'red'}-100 text-{payment.status === 'completed' ? 'green' : payment.status === 'pending' ? 'yellow' : 'red'}-800">
													{payment.status}
												</span>
											</div>
										</div>
									{/each}
								</div>
							{:else}
								<p class="text-sm text-gray-500 dark:text-gray-400">{$t('payment.noPayments')}</p>
							{/if}
							
							<div class="mt-4 pt-3 border-t border-gray-200 dark:border-gray-600">
								<Button variant="primary" size="compact" href="/create/payment" class="w-full">
									{$t('payment.add')}
								</Button>
							</div>
						</div>

						<!-- Recent Workers -->
						<div class="rounded-lg border border-gray-200 bg-white p-4 dark:bg-gray-800 dark:border-gray-700">
							<div class="flex items-center justify-between mb-4">
								<h3 class="text-sm font-medium text-gray-900 dark:text-white">
									{$t('dashboard.recentWorkers')}
								</h3>
								<Button variant="outline" size="compact" href="/dashboard/workers">
									{$t('common.viewAll')}
								</Button>
							</div>
							
							{#if pmLoading}
								<div class="space-y-2">
									{#each Array(3) as _}
										<LoadingSkeleton type="rect" height="40px" />
									{/each}
								</div>
							{:else if recentWorkers.length > 0}
								<div class="space-y-3">
									{#each recentWorkers.slice(0, 3) as worker}
										<div class="flex items-center justify-between">
											<div class="flex items-center min-w-0 flex-1">
												<div class="bg-primary-100 dark:bg-primary-800 flex h-8 w-8 items-center justify-center rounded-full">
													<span class="text-primary-600 dark:text-primary-200 text-xs font-medium">
														{worker.first_name?.[0] || 'W'}
													</span>
												</div>
												<div class="ml-3 min-w-0 flex-1">
													<p class="text-sm font-medium text-gray-900 dark:text-white">
														{worker.first_name} {worker.last_name}
													</p>
													<p class="text-xs text-gray-500 dark:text-gray-400">
														{worker.categories?.map(c => c.name).join(', ') || $t('worker.noCategories')}
													</p>
												</div>
											</div>
											<div class="text-right">
												<span class="inline-flex items-center px-1.5 py-0.5 rounded-full text-xs font-medium bg-{worker.status === 'active' ? 'green' : 'gray'}-100 text-{worker.status === 'active' ? 'green' : 'gray'}-800">
													{worker.status}
												</span>
												{#if worker.is_available}
													<p class="text-xs text-green-600 dark:text-green-400 mt-1">
														{$t('worker.available')}
													</p>
												{/if}
											</div>
										</div>
									{/each}
								</div>
							{:else}
								<p class="text-sm text-gray-500 dark:text-gray-400">{$t('worker.noWorkers')}</p>
							{/if}
							
							<div class="mt-4 pt-3 border-t border-gray-200 dark:border-gray-600">
								<Button variant="primary" size="compact" href="/create/worker" class="w-full">
									{$t('worker.add')}
								</Button>
							</div>
						</div>

						<!-- Analytics Quick Access -->
						<div class="rounded-lg border border-gray-200 bg-white p-4 dark:bg-gray-800 dark:border-gray-700">
							<div class="flex items-center justify-between mb-4">
								<h3 class="text-sm font-medium text-gray-900 dark:text-white">
									{$t('dashboard.analytics')}
								</h3>
								<Button variant="outline" size="compact" href="/dashboard/analytics">
									{$t('common.viewAll')}
								</Button>
							</div>
							
							<div class="space-y-4">
								<div class="flex items-center">
									<div class="flex-shrink-0">
										{@html analyticsIcon}
									</div>
									<div class="ml-3">
										<p class="text-sm font-medium text-gray-900 dark:text-white">
											{$t('dashboard.comprehensiveAnalytics')}
										</p>
										<p class="text-xs text-gray-500 dark:text-gray-400">
											{$t('dashboard.analyticsDescription')}
										</p>
									</div>
								</div>
								
								{#if propertyManagementStats?.insights}
									<div class="text-xs text-gray-600 dark:text-gray-400">
										{propertyManagementStats.insights.length} {$t('dashboard.activeInsights')}
									</div>
								{/if}
							</div>
							
							<div class="mt-4 pt-3 border-t border-gray-200 dark:border-gray-600">
								<Button variant="primary" size="compact" href="/dashboard/analytics" class="w-full">
									{$t('dashboard.viewAnalytics')}
								</Button>
							</div>
						</div>
					</div>
				{/if}

				<!-- Performance Metrics (for appraisers/data entry) -->
				{#if stats && ($user?.role === 'appraiser' || $user?.role === 'data_entry')}
					<div class="rounded-lg border border-gray-200 bg-white p-4">
						<h3 class="mb-4 text-sm font-medium text-gray-900">
							{$t('dashboard.performanceMetrics')}
						</h3>

						<div class="grid grid-cols-1 gap-4 md:grid-cols-3">
							<div class="text-center">
								<p class="text-lg font-semibold text-gray-900">
									{stats.properties_this_month || 0}
								</p>
								<p class="text-xs text-gray-600">
									{$t('dashboard.propertiesThisMonth')}
								</p>
							</div>

							<div class="text-center">
								<p class="text-lg font-semibold text-gray-900">
									{stats.auctions_this_month || 0}
								</p>
								<p class="text-xs text-gray-600">
									{$t('dashboard.auctionsThisMonth')}
								</p>
							</div>

							<div class="text-center">
								<p class="text-lg font-semibold text-gray-900">
									{stats.avg_property_value
										? `$${stats.avg_property_value.toLocaleString()}`
										: '$0'}
								</p>
								<p class="text-xs text-gray-600">
									{$t('dashboard.avgPropertyValue')}
								</p>
							</div>
						</div>
					</div>
				{/if}

				<!-- Recent Activity -->
				<div class="lg:hidden">
					<ActivityFeed {activities} loading={isLoading} maxItems={5} compact />
				</div>
			</div>

			<!-- Sidebar -->
			<div class="space-y-6 lg:col-span-1">
				<!-- Quick Actions -->
				<QuickActions />

				<!-- Recent Activity (Desktop) -->
				<div class="hidden lg:block">
					<ActivityFeed {activities} loading={isLoading} maxItems={8} />
				</div>

				<!-- User Info Card -->
				<div class="rounded-lg border border-gray-200 bg-white p-4">
					<div class="flex items-center space-x-3">
						<div class="bg-primary-100 flex h-10 w-10 items-center justify-center rounded-full">
							<span class="text-primary-600 text-sm font-medium">
								{$user?.first_name?.[0] || $user?.email?.[0] || 'U'}
							</span>
						</div>

						<div class="min-w-0 flex-1">
							<p class="truncate text-sm font-medium text-gray-900">
								{$user?.first_name}
								{$user?.last_name}
							</p>
							<p class="text-xs text-gray-600">
								{$t(`auth.role${$user?.role?.charAt(0)?.toUpperCase()}${$user?.role?.slice(1)}`)}
							</p>
						</div>
					</div>

					{#if $userPriority > 1}
						<div class="mt-3 border-t border-gray-200 pt-3">
							<div class="flex items-center justify-between">
								<span class="text-xs text-gray-600">
									{$t('dashboard.userPriority')}
								</span>
								<div class="flex items-center space-x-1">
									{#each Array(5) as _, i}
										<div
											class="h-2 w-2 rounded-full {i < $userPriority
												? 'bg-primary-500'
												: 'bg-gray-200'}"
										></div>
									{/each}
								</div>
							</div>
						</div>
					{/if}
				</div>
			</div>
		</div>
	</div>
</div>
