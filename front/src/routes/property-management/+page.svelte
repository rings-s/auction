<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { t, locale } from '$lib/i18n';
	import { user } from '$lib/stores/user.svelte.js';
	import Button from '$lib/components/ui/Button.svelte';
	import LoadingSpinner from '$lib/components/animations/LoadingSpinner.svelte';
	import PropertyCard from '$lib/components/property-management/PropertyCard.svelte';
	import { getProperties } from '$lib/api/property.js';

	let isRTL = $derived($locale === 'ar');

	// State using Svelte 5 runes
	let loading = $state(true);
	let error = $state('');
	let recentProperties = $state([]);
	let stats = $state({
		totalProperties: 0,
		totalTenants: 0,
		pendingMaintenance: 0,
		monthlyRevenue: 0
	});

	// Check if user has permission to access property management
	let hasAccess = $derived(
		($user && ['owner', 'appraiser', 'data_entry'].includes($user.role)) || $user?.is_superuser
	);

	onMount(() => {
		if (!hasAccess) {
			goto('/dashboard');
			return;
		}
		loadDashboardData();
	});

	async function loadDashboardData() {
		try {
			loading = true;
			error = '';

			// Load recent properties
			const propertiesResponse = await getProperties({
				page_size: 6,
				ordering: '-created_at'
			});

			// Handle different response formats
			if (propertiesResponse.results) {
				recentProperties = propertiesResponse.results;
				stats.totalProperties = propertiesResponse.count || 0;
			} else if (Array.isArray(propertiesResponse)) {
				recentProperties = propertiesResponse.slice(0, 6);
				stats.totalProperties = propertiesResponse.length;
			} else {
				const results = propertiesResponse.data?.results || propertiesResponse || [];
				recentProperties = results.slice(0, 6);
				stats.totalProperties = propertiesResponse.data?.count || results.length;
			}

			// Calculate basic stats (simplified for now)
			stats.monthlyRevenue = calculateEstimatedRental(recentProperties);
			stats.totalTenants = 0; // Will be updated when tenant API is integrated
			stats.pendingMaintenance = 0; // Will be updated when maintenance API is integrated
		} catch (err) {
			error = err.message || $t('errors.loadingFailed');
			console.error('Failed to load property management dashboard:', err);
		} finally {
			loading = false;
		}
	}

	function calculateEstimatedRental(properties) {
		return properties.reduce((total, property) => {
			// Estimate rental as 8% of market value annually, divided by 12 for monthly
			const estimatedMonthlyRent = property.market_value
				? Math.round((property.market_value * 0.08) / 12)
				: 0;
			return total + estimatedMonthlyRent;
		}, 0);
	}

	// Navigation handlers using Svelte 5 patterns
	function handleViewAllProperties() {
		goto('/property-management/properties');
	}

	function handleViewAllTenants() {
		goto('/property-management/tenants');
	}

	function handleViewAllMaintenance() {
		goto('/property-management/maintenance');
	}

	function handleViewAnalytics() {
		goto('/property-management/analytics');
	}

	function handleCreateProperty() {
		goto('/property-management/properties/create');
	}

	function handleCreateTenant() {
		goto('/property-management/tenants/create');
	}

	// Card event handlers
	function handleViewProperty(event) {
		goto(`/property-management/properties/${event.detail.property.id}`);
	}

	function handleEditProperty(event) {
		goto(`/property-management/properties/${event.detail.property.id}/edit`);
	}
</script>

<svelte:head>
	<title>{$t('propertyManagement.title')} | {$t('app.name')}</title>
	<meta name="description" content={$t('propertyManagement.description')} />
</svelte:head>

<!-- Access Control -->
{#if !hasAccess}
	<div
		class="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 dark:from-gray-900 dark:via-blue-900 dark:to-indigo-900"
	>
		<div
			class="mx-auto max-w-md rounded-2xl border border-red-200 bg-red-50 p-8 text-red-800 shadow-xl dark:border-red-800 dark:bg-red-900/20 dark:text-red-200"
		>
			<div class="flex items-center">
				<svg
					class="mr-3 h-8 w-8 text-red-500"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
					/>
				</svg>
				<div>
					<h2 class="mb-2 text-xl font-semibold">{$t('error.accessDenied')}</h2>
					<p class="text-base">{$t('error.insufficientPermissions')}</p>
				</div>
			</div>
		</div>
	</div>
{:else}
	<div
		class="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 dark:from-gray-900 dark:via-blue-900 dark:to-indigo-900"
		dir={isRTL ? 'rtl' : 'ltr'}
	>
		<div class="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
			<!-- Header -->
			<div class="mb-8 flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between">
				<div>
					<h1 class="text-4xl font-bold text-gray-900 dark:text-white">
						{$t('propertyManagement.title')}
					</h1>
					<p class="mt-2 text-lg text-gray-600 dark:text-gray-300">
						{$t('propertyManagement.subtitle')}
					</p>
				</div>

				<div class="flex flex-wrap gap-3">
					<Button
						variant="primary"
						class="bg-gradient-to-r from-blue-600 to-indigo-600 shadow-lg hover:from-blue-700 hover:to-indigo-700"
						onclick={handleCreateProperty}
					>
						<svg class="mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 6v6m0 0v6m0-6h6m-6 0H6"
							/>
						</svg>
						{$t('property.create')}
					</Button>
					<Button variant="outline" class="shadow-md" onclick={handleViewAnalytics}>
						<svg class="mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
							/>
						</svg>
						{$t('analytics.title')}
					</Button>
				</div>
			</div>

			<!-- Error Display -->
			{#if error}
				<div
					class="mb-8 rounded-2xl border border-red-200 bg-red-50 p-6 shadow-lg dark:border-red-800 dark:bg-red-900/20"
				>
					<div class="flex items-center">
						<svg
							class="mr-3 h-6 w-6 text-red-500"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
							/>
						</svg>
						<div>
							<h3 class="mb-1 text-lg font-semibold text-red-800 dark:text-red-200">
								{$t('error.title')}
							</h3>
							<p class="text-red-700 dark:text-red-300">{error}</p>
						</div>
					</div>
					<div class="mt-4">
						<Button variant="outline" onclick={loadDashboardData}>
							<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
								/>
							</svg>
							{$t('common.retry')}
						</Button>
					</div>
				</div>
			{/if}

			<!-- Stats Overview -->
			{#if loading}
				<div class="mb-8 grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
					{#each Array(4) as _}
						<div
							class="h-32 animate-pulse rounded-2xl border border-gray-200 bg-white shadow-xl dark:border-gray-700 dark:bg-gray-800"
						></div>
					{/each}
				</div>
			{:else}
				<div class="mb-8 grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
					<!-- Total Properties -->
					<div
						class="group cursor-pointer rounded-2xl border border-gray-200 bg-white p-6 shadow-xl transition-all duration-300 hover:shadow-2xl dark:border-gray-700 dark:bg-gray-800"
						onclick={handleViewAllProperties}
					>
						<div class="flex items-center">
							<div class="flex-shrink-0">
								<div
									class="flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-100 transition-transform group-hover:scale-110 dark:bg-blue-900"
								>
									<span class="text-2xl">🏠</span>
								</div>
							</div>
							<div class="ml-4">
								<p class="text-sm font-medium text-gray-600 dark:text-gray-400">
									{$t('propertyManagement.totalProperties')}
								</p>
								<p class="text-2xl font-bold text-gray-900 dark:text-white">
									{stats.totalProperties}
								</p>
							</div>
						</div>
					</div>

					<!-- Estimated Monthly Revenue -->
					<div
						class="group cursor-pointer rounded-2xl border border-gray-200 bg-white p-6 shadow-xl transition-all duration-300 hover:shadow-2xl dark:border-gray-700 dark:bg-gray-800"
						onclick={handleViewAnalytics}
					>
						<div class="flex items-center">
							<div class="flex-shrink-0">
								<div
									class="flex h-12 w-12 items-center justify-center rounded-2xl bg-green-100 transition-transform group-hover:scale-110 dark:bg-green-900"
								>
									<span class="text-2xl">💰</span>
								</div>
							</div>
							<div class="ml-4">
								<p class="text-sm font-medium text-gray-600 dark:text-gray-400">
									{$t('propertyManagement.estimatedRevenue')}
								</p>
								<p class="text-2xl font-bold text-gray-900 dark:text-white">
									{stats.monthlyRevenue.toLocaleString()}
									{$t('currency.sar')}
								</p>
							</div>
						</div>
					</div>

					<!-- Total Tenants (Placeholder) -->
					<div
						class="group cursor-pointer rounded-2xl border border-gray-200 bg-white p-6 shadow-xl transition-all duration-300 hover:shadow-2xl dark:border-gray-700 dark:bg-gray-800"
						onclick={handleViewAllTenants}
					>
						<div class="flex items-center">
							<div class="flex-shrink-0">
								<div
									class="flex h-12 w-12 items-center justify-center rounded-2xl bg-purple-100 transition-transform group-hover:scale-110 dark:bg-purple-900"
								>
									<span class="text-2xl">👥</span>
								</div>
							</div>
							<div class="ml-4">
								<p class="text-sm font-medium text-gray-600 dark:text-gray-400">
									{$t('propertyManagement.totalTenants')}
								</p>
								<p class="text-2xl font-bold text-gray-900 dark:text-white">{stats.totalTenants}</p>
							</div>
						</div>
					</div>

					<!-- Pending Maintenance (Placeholder) -->
					<div
						class="group cursor-pointer rounded-2xl border border-gray-200 bg-white p-6 shadow-xl transition-all duration-300 hover:shadow-2xl dark:border-gray-700 dark:bg-gray-800"
						onclick={handleViewAllMaintenance}
					>
						<div class="flex items-center">
							<div class="flex-shrink-0">
								<div
									class="flex h-12 w-12 items-center justify-center rounded-2xl bg-orange-100 transition-transform group-hover:scale-110 dark:bg-orange-900"
								>
									<span class="text-2xl">🔧</span>
								</div>
							</div>
							<div class="ml-4">
								<p class="text-sm font-medium text-gray-600 dark:text-gray-400">
									{$t('propertyManagement.pendingMaintenance')}
								</p>
								<p class="text-2xl font-bold text-gray-900 dark:text-white">
									{stats.pendingMaintenance}
								</p>
							</div>
						</div>
					</div>
				</div>
			{/if}

			<!-- Quick Actions -->
			<div
				class="mb-8 rounded-2xl border border-gray-200 bg-white p-6 shadow-xl dark:border-gray-700 dark:bg-gray-800"
			>
				<h2 class="mb-6 text-2xl font-semibold text-gray-900 dark:text-white">
					{$t('propertyManagement.quickActions')}
				</h2>
				<div class="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-6">
					<Button
						variant="outline"
						class="flex h-24 flex-col items-center p-6 shadow-md transition-all duration-300 hover:shadow-lg"
						onclick={handleCreateProperty}
					>
						<span class="mb-2 text-3xl">🏠</span>
						<span class="text-sm font-medium">{$t('property.add')}</span>
					</Button>

					<Button
						variant="outline"
						class="flex h-24 flex-col items-center p-6 shadow-md transition-all duration-300 hover:shadow-lg"
						onclick={handleCreateTenant}
					>
						<span class="mb-2 text-3xl">👤</span>
						<span class="text-sm font-medium">{$t('tenant.add')}</span>
					</Button>

					<Button
						variant="outline"
						class="flex h-24 flex-col items-center p-6 shadow-md transition-all duration-300 hover:shadow-lg"
						onclick={() => goto('/property-management/leases/create')}
					>
						<span class="mb-2 text-3xl">📄</span>
						<span class="text-sm font-medium">{$t('lease.create')}</span>
					</Button>

					<Button
						variant="outline"
						class="flex h-24 flex-col items-center p-6 shadow-md transition-all duration-300 hover:shadow-lg"
						onclick={() => goto('/property-management/maintenance/create')}
					>
						<span class="mb-2 text-3xl">🔧</span>
						<span class="text-sm font-medium">{$t('maintenance.create')}</span>
					</Button>

					<Button
						variant="outline"
						class="flex h-24 flex-col items-center p-6 shadow-md transition-all duration-300 hover:shadow-lg"
						onclick={() => goto('/property-management/expenses/create')}
					>
						<span class="mb-2 text-3xl">💰</span>
						<span class="text-sm font-medium">{$t('expense.add')}</span>
					</Button>

					<Button
						variant="outline"
						class="flex h-24 flex-col items-center p-6 shadow-md transition-all duration-300 hover:shadow-lg"
						onclick={() => goto('/property-management/reports')}
					>
						<span class="mb-2 text-3xl">📊</span>
						<span class="text-sm font-medium">{$t('reports.generate')}</span>
					</Button>
				</div>
			</div>

			<!-- Recent Properties -->
			<div
				class="rounded-2xl border border-gray-200 bg-white shadow-xl dark:border-gray-700 dark:bg-gray-800"
			>
				<div
					class="flex items-center justify-between border-b border-gray-200 p-6 dark:border-gray-700"
				>
					<h2 class="text-2xl font-semibold text-gray-900 dark:text-white">
						{$t('propertyManagement.recentProperties')}
					</h2>
					<Button variant="ghost" size="sm" onclick={handleViewAllProperties}>
						{$t('common.viewAll')} →
					</Button>
				</div>

				<div class="p-6">
					{#if loading}
						<div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
							{#each Array(3) as _}
								<div class="h-80 animate-pulse rounded-2xl bg-gray-200 dark:bg-gray-700"></div>
							{/each}
						</div>
					{:else if recentProperties.length === 0}
						<div class="py-12 text-center">
							<div class="mb-4 text-6xl">🏠</div>
							<h3 class="mb-2 text-xl font-semibold text-gray-700 dark:text-gray-300">
								{$t('propertyManagement.noPropertiesYet')}
							</h3>
							<p class="mb-6 text-gray-500 dark:text-gray-400">
								{$t('propertyManagement.addFirstProperty')}
							</p>
							<Button
								variant="primary"
								class="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700"
								onclick={handleCreateProperty}
							>
								{$t('property.createFirst')}
							</Button>
						</div>
					{:else}
						<div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
							{#each recentProperties as property (property.id)}
								<PropertyCard
									{property}
									on:view={handleViewProperty}
									on:edit={handleEditProperty}
								/>
							{/each}
						</div>
					{/if}
				</div>
			</div>
		</div>
	</div>
{/if}

<style>
	/* Enhanced hover effects */
	.group:hover {
		transform: translateY(-2px);
	}

	/* Custom gradient animations */
	@keyframes gradient-shift {
		0%,
		100% {
			background-position: 0% 50%;
		}
		50% {
			background-position: 100% 50%;
		}
	}

	.bg-gradient-to-br {
		background-size: 200% 200%;
		animation: gradient-shift 8s ease infinite;
	}
</style>
