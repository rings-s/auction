<!-- src/routes/dashboard/system/+page.svelte -->
<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { t } from '$lib/i18n';
	import { user } from '$lib/stores/user.svelte.js';
	import { getCanAccessSystemDashboard } from '$lib/stores/dashboard.svelte.js';
	import { getSystemDashboardStats } from '$lib/api/dashboard';
	import { toast } from '$lib/stores/toastStore.svelte.js';

	// Components
	import StatCard from '$lib/components/dashboard/StatCard.svelte';
	import LoadingSkeleton from '$lib/components/ui/LoadingSkeleton.svelte';
	import Alert from '$lib/components/ui/Alert.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Breadcrumb from '$lib/components/ui/Breadcrumb.svelte';

	let systemStats = null;
	let loading = false;
	let error = null;

	// Breadcrumb items
	$: breadcrumbItems = [
		{ label: $t('nav.home'), href: '/' },
		{ label: $t('dashboard.title'), href: '/dashboard' },
		{ label: $t('dashboard.systemDashboard'), href: '/dashboard/system', active: true }
	];

	// Icons
	const userIcon = `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
      <path d="M9 6a3 3 0 11-6 0 3 3 0 016 0zM17 6a3 3 0 11-6 0 3 3 0 016 0zM12.93 17c.046-.327.07-.66.07-1a6.97 6.97 0 00-1.5-4.33A5 5 0 0119 16v1h-6.07zM6 11a5 5 0 015 5v1H1v-1a5 5 0 015-5z"/>
    </svg>`;

	const propertyIcon = `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
      <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z"/>
    </svg>`;

	const auctionIcon = `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
      <path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z"/>
    </svg>`;

	const bidIcon = `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-13a1 1 0 10-2 0v.092a4.535 4.535 0 00-1.676.662C6.602 6.234 6 7.009 6 8c0 .99.602 1.765 1.324 2.246.48.32 1.054.545 1.676.662v1.941c-.391-.127-.68-.317-.843-.504a1 1 0 10-1.51 1.31c.562.649 1.413 1.076 2.353 1.253V15a1 1 0 102 0v-.092a4.535 4.535 0 001.676-.662C13.398 13.766 14 12.991 14 12c0-.99-.602-1.765-1.324-2.246A4.535 4.535 0 0011 9.092V7.151c.391.127.68.317.843.504a1 1 0 101.511-1.31c-.563-.649-1.413-1.076-2.354-1.253V5z" clip-rule="evenodd"/>
    </svg>`;

	const alertIcon = `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
      <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
    </svg>`;

	// Check permissions and load data
	async function loadSystemStats() {
		if (!getCanAccessSystemDashboard()) {
			goto('/dashboard');
			return;
		}

		loading = true;
		error = null;

		try {
			systemStats = await getSystemDashboardStats();
		} catch (err) {
			console.error('Failed to load system stats:', err);
			error = err.message;
			toast.error($t('dashboard.loadError'));
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		loadSystemStats();
	});
</script>

<svelte:head>
	<title>{$t('dashboard.systemDashboard')} - {$t('app.name')}</title>
</svelte:head>

<div class="p-6">
	<!-- Header -->
	<div class="mb-6">
		<Breadcrumb items={breadcrumbItems} class="mb-4" />

		<div class="flex flex-col sm:flex-row sm:items-center sm:justify-between">
			<div>
				<h1 class="text-xl font-semibold text-gray-900">
					{$t('dashboard.systemDashboard')}
				</h1>
				<p class="mt-1 text-sm text-gray-600">
					{$t('dashboard.systemOverview')}
				</p>
			</div>

			<div class="mt-4 sm:mt-0">
				<Button variant="outline" size="compact" onClick={loadSystemStats} {loading}>
					{$t('common.refresh')}
				</Button>
			</div>
		</div>
	</div>

	<!-- Error Alert -->
	{#if error}
		<Alert type="error" title={$t('error.title')} message={error} dismissible class="mb-6" />
	{/if}

	<!-- System Stats -->
	{#if loading}
		<div class="mb-8 grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
			{#each Array(8) as _}
				<LoadingSkeleton type="rect" height="100px" />
			{/each}
		</div>
	{:else if systemStats}
		<!-- User Statistics -->
		<div class="mb-8">
			<h2 class="mb-4 text-lg font-medium text-gray-900">
				{$t('dashboard.userStatistics')}
			</h2>
			<div class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
				<StatCard
					title={$t('dashboard.totalUsers')}
					value={systemStats.total_users}
					icon={userIcon}
					color="primary"
				/>

				<StatCard
					title={$t('dashboard.verifiedUsers')}
					value={systemStats.verified_users}
					icon={userIcon}
					color="success"
				/>

				<StatCard
					title={$t('dashboard.activeToday')}
					value={systemStats.active_users_today}
					icon={userIcon}
					color="info"
				/>

				<StatCard
					title={$t('dashboard.newThisWeek')}
					value={systemStats.new_users_this_week}
					icon={userIcon}
					color="warning"
				/>
			</div>
		</div>

		<!-- Property Statistics -->
		<div class="mb-8">
			<h2 class="mb-4 text-lg font-medium text-gray-900">
				{$t('dashboard.propertyStatistics')}
			</h2>
			<div class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
				<StatCard
					title={$t('dashboard.totalProperties')}
					value={systemStats.total_properties}
					icon={propertyIcon}
					color="primary"
				/>

				<StatCard
					title={$t('dashboard.publishedProperties')}
					value={systemStats.published_properties}
					icon={propertyIcon}
					color="success"
				/>

				<StatCard
					title={$t('dashboard.propertiesThisMonth')}
					value={systemStats.properties_this_month}
					icon={propertyIcon}
					color="info"
				/>

				<StatCard
					title={$t('dashboard.avgPropertyValue')}
					value={`$${systemStats.avg_property_value?.toLocaleString() || 0}`}
					icon={propertyIcon}
					color="secondary"
				/>
			</div>
		</div>

		<!-- Auction Statistics -->
		<div class="mb-8">
			<h2 class="mb-4 text-lg font-medium text-gray-900">
				{$t('dashboard.auctionStatistics')}
			</h2>
			<div class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
				<StatCard
					title={$t('dashboard.totalAuctions')}
					value={systemStats.total_auctions}
					icon={auctionIcon}
					color="primary"
				/>

				<StatCard
					title={$t('dashboard.activeAuctions')}
					value={systemStats.active_auctions}
					icon={auctionIcon}
					color="success"
				/>

				<StatCard
					title={$t('dashboard.completedAuctions')}
					value={systemStats.completed_auctions}
					icon={auctionIcon}
					color="info"
				/>

				<StatCard
					title={$t('dashboard.totalAuctionValue')}
					value={`$${systemStats.total_auction_value?.toLocaleString() || 0}`}
					icon={auctionIcon}
					color="secondary"
				/>
			</div>
		</div>

		<!-- Bidding Statistics -->
		<div class="mb-8">
			<h2 class="mb-4 text-lg font-medium text-gray-900">
				{$t('dashboard.biddingStatistics')}
			</h2>
			<div class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
				<StatCard
					title={$t('dashboard.totalBids')}
					value={systemStats.total_bids}
					icon={bidIcon}
					color="primary"
				/>

				<StatCard
					title={$t('dashboard.uniqueBidders')}
					value={systemStats.unique_bidders}
					icon={bidIcon}
					color="success"
				/>

				<StatCard
					title={$t('dashboard.totalBidValue')}
					value={`$${systemStats.total_bid_value?.toLocaleString() || 0}`}
					icon={bidIcon}
					color="warning"
				/>

				<StatCard
					title={$t('dashboard.avgBidAmount')}
					value={`$${systemStats.avg_bid_amount?.toLocaleString() || 0}`}
					icon={bidIcon}
					color="info"
				/>
			</div>
		</div>

		<!-- Activity & Alerts -->
		<div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
			<!-- Recent Activity -->
			<div class="rounded-lg border border-gray-200 bg-white p-4">
				<h3 class="mb-4 text-sm font-medium text-gray-900">
					{$t('dashboard.todayActivity')}
				</h3>

				<div class="space-y-3">
					<div class="flex items-center justify-between">
						<span class="text-sm text-gray-600">{$t('dashboard.bidsToday')}</span>
						<span class="text-sm font-medium text-gray-900">
							{systemStats.bids_today}
						</span>
					</div>

					<div class="flex items-center justify-between">
						<span class="text-sm text-gray-600">{$t('dashboard.auctionsEndingSoon')}</span>
						<span class="text-sm font-medium text-gray-900">
							{systemStats.auctions_ending_soon}
						</span>
					</div>

					<div class="flex items-center justify-between">
						<span class="text-sm text-gray-600">{$t('dashboard.pendingVerifications')}</span>
						<span class="text-sm font-medium text-gray-900">
							{systemStats.pending_verifications}
						</span>
					</div>
				</div>
			</div>

			<!-- Top Cities -->
			<div class="rounded-lg border border-gray-200 bg-white p-4">
				<h3 class="mb-4 text-sm font-medium text-gray-900">
					{$t('dashboard.topCities')}
				</h3>

				{#if systemStats.top_cities && systemStats.top_cities.length > 0}
					<div class="space-y-2">
						{#each systemStats.top_cities as city}
							<div class="flex items-center justify-between">
								<span class="text-sm text-gray-600">
									{city.city}, {city.state}
								</span>
								<span class="text-sm font-medium text-gray-900">
									{city.count}
									{$t('dashboard.properties')}
								</span>
							</div>
						{/each}
					</div>
				{:else}
					<p class="text-sm text-gray-500">
						{$t('dashboard.noData')}
					</p>
				{/if}
			</div>
		</div>
	{/if}
</div>
