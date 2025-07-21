<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { t } from '$lib/i18n';
	import { userStore } from '$lib/stores/user.js';
	import Button from '$lib/components/ui/Button.svelte';
	import StatCard from '$lib/components/dashboard/StatCard.svelte';
	import RentalPropertyCard from '$lib/components/property-management/RentalPropertyCard.svelte';
	import TenantCard from '$lib/components/property-management/TenantCard.svelte';
	import MaintenanceRequestCard from '$lib/components/property-management/MaintenanceRequestCard.svelte';
	import LoadingSkeleton from '$lib/components/ui/LoadingSkeleton.svelte';
	import Alert from '$lib/components/ui/Alert.svelte';
	import {
		rentalPropertyAPI,
		tenantsAPI,
		maintenanceAPI
	} from '$lib/api/propertyManagement.js';

	// State
	let loading = true;
	let error = '';
	let recentProperties = [];
	let recentTenants = [];
	let pendingMaintenance = [];
	let stats = {
		totalProperties: 0,
		totalTenants: 0,
		pendingMaintenance: 0,
		monthlyRevenue: 0
	};

		$: user = $userStore;

	// Check if user has permission to access property management
	$: hasAccess =
		(user && ['owner', 'appraiser', 'data_entry'].includes(user.role)) || user?.is_superuser;

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

			// Load dashboard data in parallel
			const [propertiesResponse, tenantsResponse, maintenanceResponse] = await Promise.all([
				rentalPropertyAPI.getAll({ page_size: 6, ordering: '-created_at' }),
				tenantsAPI.getAll({ page_size: 6, ordering: '-created_at' }),
				maintenanceAPI.requests.getAll({
					status: 'pending',
					page_size: 6,
					ordering: '-reported_date'
				})
			]);

			recentProperties = propertiesResponse.data.results || [];
			recentTenants = tenantsResponse.data.results || [];
			pendingMaintenance = maintenanceResponse.data.results || [];

			// Calculate stats
			stats = {
				totalProperties: propertiesResponse.data.count || 0,
				totalTenants: tenantsResponse.data.count || 0,
				pendingMaintenance: maintenanceResponse.data.count || 0,
				monthlyRevenue: calculateMonthlyRevenue(recentProperties)
			};
		} catch (err) {
			error = err.message || $t('errors.loadingFailed');
			console.error('Failed to load property management dashboard:', err);
		} finally {
			loading = false;
		}
	}

	function calculateMonthlyRevenue(properties) {
		return properties.reduce((total, property) => {
			return total + (property.rental_info?.monthly_rent || 0);
		}, 0);
	}

	// Navigation handlers
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

	function handleViewTenant(event) {
		goto(`/property-management/tenants/${event.detail.tenant.id}`);
	}

	function handleEditTenant(event) {
		goto(`/property-management/tenants/${event.detail.tenant.id}/edit`);
	}

	function handleViewMaintenanceRequest(event) {
		goto(`/property-management/maintenance/${event.detail.request.id}`);
	}

	function handleEditMaintenanceRequest(event) {
		goto(`/property-management/maintenance/${event.detail.request.id}/edit`);
	}
</script>

<svelte:head>
	<title>{$t('propertyManagement.title')} | {$t('app.name')}</title>
	<meta name="description" content={$t('propertyManagement.description')} />
</svelte:head>

<!-- Access Control -->
{#if !hasAccess}
	<div class="flex min-h-screen items-center justify-center">
		<Alert type="error" message={$t('errors.accessDenied')} />
	</div>
{:else}
	<div class="container mx-auto space-y-8 px-4 py-8">
		<!-- Header -->
		<div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
			<div>
				<h1 class="text-3xl font-bold text-gray-900">{$t('propertyManagement.title')}</h1>
				<p class="mt-1 text-gray-600">{$t('propertyManagement.subtitle')}</p>
			</div>

			<div class="flex flex-wrap gap-2">
				<Button variant="primary" on:click={handleCreateProperty}>
					+ {$t('property.create')}
				</Button>
				<Button variant="outline" on:click={handleViewAnalytics}>
					📊 {$t('analytics.title')}
				</Button>
			</div>
		</div>

		<!-- Error Display -->
		{#if error}
			<Alert type="error" message={error} />
		{/if}

		<!-- Stats Overview -->
		{#if loading}
			<div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
				{#each Array(4) as _}
					<LoadingSkeleton height="120px" />
				{/each}
			</div>
		{:else}
			<div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
				<StatCard
					title={$t('propertyManagement.totalProperties')}
					value={stats.totalProperties}
					icon="🏠"
					variant="blue"
					clickable
					on:click={handleViewAllProperties}
				/>

				<StatCard
					title={$t('propertyManagement.totalTenants')}
					value={stats.totalTenants}
					icon="👥"
					variant="green"
					clickable
					on:click={handleViewAllTenants}
				/>

				<StatCard
					title={$t('propertyManagement.pendingMaintenance')}
					value={stats.pendingMaintenance}
					icon="🔧"
					variant="orange"
					clickable
					on:click={handleViewAllMaintenance}
				/>

				<StatCard
					title={$t('propertyManagement.monthlyRevenue')}
					value={`${stats.monthlyRevenue.toLocaleString()} SAR`}
					icon="💰"
					variant="purple"
					clickable
					on:click={handleViewAnalytics}
				/>
			</div>
		{/if}

		<!-- Quick Actions -->
		<div class="rounded-lg border border-gray-200 bg-white p-6">
			<h2 class="mb-4 text-xl font-semibold text-gray-900">
				{$t('propertyManagement.quickActions')}
			</h2>
			<div class="grid grid-cols-2 gap-4 md:grid-cols-4 lg:grid-cols-6">
				<Button
					variant="outline"
					class="flex flex-col items-center p-4"
					on:click={handleCreateProperty}
				>
					<span class="mb-2 text-2xl">🏠</span>
					<span class="text-sm">{$t('property.add')}</span>
				</Button>

				<Button
					variant="outline"
					class="flex flex-col items-center p-4"
					on:click={handleCreateTenant}
				>
					<span class="mb-2 text-2xl">👤</span>
					<span class="text-sm">{$t('tenant.add')}</span>
				</Button>

				<Button
					variant="outline"
					class="flex flex-col items-center p-4"
					on:click={() => goto('/property-management/leases/create')}
				>
					<span class="mb-2 text-2xl">📄</span>
					<span class="text-sm">{$t('lease.create')}</span>
				</Button>

				<Button
					variant="outline"
					class="flex flex-col items-center p-4"
					on:click={() => goto('/property-management/maintenance/create')}
				>
					<span class="mb-2 text-2xl">🔧</span>
					<span class="text-sm">{$t('maintenance.create')}</span>
				</Button>

				<Button
					variant="outline"
					class="flex flex-col items-center p-4"
					on:click={() => goto('/property-management/expenses/create')}
				>
					<span class="mb-2 text-2xl">💰</span>
					<span class="text-sm">{$t('expense.add')}</span>
				</Button>

				<Button
					variant="outline"
					class="flex flex-col items-center p-4"
					on:click={() => goto('/property-management/reports')}
				>
					<span class="mb-2 text-2xl">📊</span>
					<span class="text-sm">{$t('reports.generate')}</span>
				</Button>
			</div>
		</div>

		<!-- Recent Properties -->
		<div class="rounded-lg border border-gray-200 bg-white">
			<div class="flex items-center justify-between border-b border-gray-200 p-6">
				<h2 class="text-xl font-semibold text-gray-900">
					{$t('propertyManagement.recentProperties')}
				</h2>
				<Button variant="ghost" size="sm" on:click={handleViewAllProperties}>
					{$t('common.viewAll')} →
				</Button>
			</div>

			<div class="p-6">
				{#if loading}
					<div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
						{#each Array(3) as _}
							<LoadingSkeleton height="300px" />
						{/each}
					</div>
				{:else if recentProperties.length === 0}
					<div class="py-8 text-center">
						<div class="mb-2 text-4xl">🏠</div>
						<p class="text-gray-600">{$t('propertyManagement.noPropertiesYet')}</p>
						<Button variant="primary" class="mt-4" on:click={handleCreateProperty}>
							{$t('property.createFirst')}
						</Button>
					</div>
				{:else}
					<div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
						{#each recentProperties as property (property.id)}
							<RentalPropertyCard
								{property}
								variant="compact"
								on:view={handleViewProperty}
								on:edit={handleEditProperty}
							/>
						{/each}
					</div>
				{/if}
			</div>
		</div>

		<!-- Recent Tenants -->
		<div class="rounded-lg border border-gray-200 bg-white">
			<div class="flex items-center justify-between border-b border-gray-200 p-6">
				<h2 class="text-xl font-semibold text-gray-900">
					{$t('propertyManagement.recentTenants')}
				</h2>
				<Button variant="ghost" size="sm" on:click={handleViewAllTenants}>
					{$t('common.viewAll')} →
				</Button>
			</div>

			<div class="p-6">
				{#if loading}
					<div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
						{#each Array(3) as _}
							<LoadingSkeleton height="200px" />
						{/each}
					</div>
				{:else if recentTenants.length === 0}
					<div class="py-8 text-center">
						<div class="mb-2 text-4xl">👥</div>
						<p class="text-gray-600">{$t('propertyManagement.noTenantsYet')}</p>
						<Button variant="primary" class="mt-4" on:click={handleCreateTenant}>
							{$t('tenant.addFirst')}
						</Button>
					</div>
				{:else}
					<div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
						{#each recentTenants as tenant (tenant.id)}
							<TenantCard
								{tenant}
								variant="compact"
								on:view={handleViewTenant}
								on:edit={handleEditTenant}
							/>
						{/each}
					</div>
				{/if}
			</div>
		</div>

		<!-- Pending Maintenance -->
		<div class="rounded-lg border border-gray-200 bg-white">
			<div class="flex items-center justify-between border-b border-gray-200 p-6">
				<h2 class="text-xl font-semibold text-gray-900">
					{$t('propertyManagement.pendingMaintenance')}
				</h2>
				<Button variant="ghost" size="sm" on:click={handleViewAllMaintenance}>
					{$t('common.viewAll')} →
				</Button>
			</div>

			<div class="p-6">
				{#if loading}
					<div class="grid grid-cols-1 gap-6 md:grid-cols-2">
						{#each Array(2) as _}
							<LoadingSkeleton height="250px" />
						{/each}
					</div>
				{:else if pendingMaintenance.length === 0}
					<div class="py-8 text-center">
						<div class="mb-2 text-4xl">✅</div>
						<p class="text-gray-600">{$t('propertyManagement.noPendingMaintenance')}</p>
					</div>
				{:else}
					<div class="grid grid-cols-1 gap-6 md:grid-cols-2">
						{#each pendingMaintenance as request (request.id)}
							<MaintenanceRequestCard
								{request}
								variant="compact"
								on:view={handleViewMaintenanceRequest}
								on:edit={handleEditMaintenanceRequest}
							/>
						{/each}
					</div>
				{/if}
			</div>
		</div>
	</div>
{/if}
