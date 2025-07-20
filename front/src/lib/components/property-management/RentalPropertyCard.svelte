<script>
	import { createEventDispatcher } from 'svelte';
	import { formatCurrency } from '$lib/utils/currency.js';
	import { t } from '$lib/i18n';
	import Button from '$lib/components/ui/Button.svelte';
	import Alert from '$lib/components/ui/Alert.svelte';

	const dispatch = createEventDispatcher();

	/** @type {Object} */
	export let property;
	/** @type {string} */
	export let variant = 'default'; // 'default', 'compact', 'dashboard'
	/** @type {boolean} */
	export let showActions = true;
	/** @type {boolean} */
	export let loading = false;

	$: rentalInfo = property?.rental_info;
	$: occupancyStatus = rentalInfo?.occupancy_rate >= 100 ? 'occupied' : 'available';
	$: tenantCount = rentalInfo?.current_tenant_count || 0;
	$: maxTenants = rentalInfo?.max_tenants || 1;

	function handleViewDetails() {
		dispatch('view', { property });
	}

	function handleEdit() {
		dispatch('edit', { property });
	}

	function handleViewTenants() {
		dispatch('viewTenants', { property });
	}

	function handleViewMaintenance() {
		dispatch('viewMaintenance', { property });
	}

	function handleViewExpenses() {
		dispatch('viewExpenses', { property });
	}

	function getOccupancyBadgeClass(status) {
		switch (status) {
			case 'occupied':
				return 'bg-green-100 text-green-800 border-green-200';
			case 'available':
				return 'bg-blue-100 text-blue-800 border-blue-200';
			default:
				return 'bg-gray-100 text-gray-800 border-gray-200';
		}
	}

	function getPropertyTypeBadge(type) {
		const typeMap = {
			apartment: '🏠',
			villa: '🏡',
			commercial: '🏢',
			land: '🏞️',
			warehouse: '🏭'
		};
		return typeMap[type] || '🏘️';
	}
</script>

<div
	class="rounded-lg border border-gray-200 bg-white shadow-sm transition-all duration-200 hover:border-gray-300 hover:shadow-md"
>
	<!-- Property Image -->
	<div class="relative h-48 overflow-hidden rounded-t-lg">
		{#if property.featured_image}
			<img
				src={property.featured_image}
				alt={property.title}
				class="h-full w-full object-cover"
				loading="lazy"
			/>
		{:else}
			<div
				class="flex h-full w-full items-center justify-center bg-gradient-to-br from-gray-100 to-gray-200"
			>
				<span class="text-4xl">{getPropertyTypeBadge(property.property_type)}</span>
			</div>
		{/if}

		<!-- Occupancy Status Badge -->
		<div class="absolute top-3 left-3">
			<span
				class="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium {getOccupancyBadgeClass(
					occupancyStatus
				)}"
			>
				{$t(`property.occupancy.${occupancyStatus}`)}
			</span>
		</div>

		<!-- Property Type Badge -->
		<div class="absolute top-3 right-3">
			<span
				class="inline-flex items-center rounded-full border border-gray-200 bg-white px-2.5 py-0.5 text-xs font-medium text-gray-700"
			>
				{$t(`property.type.${property.property_type}`)}
			</span>
		</div>
	</div>

	<div class="p-4">
		<!-- Property Title & Address -->
		<div class="mb-3">
			<h3 class="mb-1 line-clamp-1 text-lg font-semibold text-gray-900">
				{property.title}
			</h3>
			<p class="line-clamp-1 text-sm text-gray-600">
				📍 {property.address}
			</p>
		</div>

		<!-- Rental Information Grid -->
		{#if rentalInfo}
			<div class="mb-4 grid grid-cols-2 gap-3">
				<!-- Monthly Rent -->
				<div class="rounded-lg bg-green-50 p-2">
					<p class="text-xs font-medium text-green-700">{$t('rental.monthlyRent')}</p>
					<p class="text-sm font-bold text-green-800">
						{formatCurrency(rentalInfo.monthly_rent)}
					</p>
				</div>

				<!-- Occupancy Rate -->
				<div class="rounded-lg bg-blue-50 p-2">
					<p class="text-xs font-medium text-blue-700">{$t('rental.occupancy')}</p>
					<p class="text-sm font-bold text-blue-800">
						{Math.round(rentalInfo.occupancy_rate)}%
					</p>
				</div>

				<!-- Tenant Count -->
				<div class="rounded-lg bg-purple-50 p-2">
					<p class="text-xs font-medium text-purple-700">{$t('rental.tenants')}</p>
					<p class="text-sm font-bold text-purple-800">
						{tenantCount}/{maxTenants}
					</p>
				</div>

				<!-- Annual Income -->
				<div class="rounded-lg bg-orange-50 p-2">
					<p class="text-xs font-medium text-orange-700">{$t('rental.annualIncome')}</p>
					<p class="text-sm font-bold text-orange-800">
						{formatCurrency(rentalInfo.monthly_rent * 12)}
					</p>
				</div>
			</div>
		{:else}
			<Alert type="warning" message={$t('rental.noRentalInfo')} class="mb-4" />
		{/if}

		<!-- Property Stats -->
		<div class="mb-4 flex items-center gap-4 text-sm text-gray-600">
			{#if property.rooms?.length}
				<span>🛏️ {property.rooms.length} {$t('property.rooms')}</span>
			{/if}
			{#if property.area}
				<span>📐 {property.area} {$t('property.sqm')}</span>
			{/if}
			{#if property.year_built}
				<span>📅 {property.year_built}</span>
			{/if}
		</div>

		<!-- Action Buttons -->
		{#if showActions}
			<div class="flex flex-wrap gap-2">
				<Button variant="primary" size="sm" {loading} on:click={handleViewDetails}>
					{$t('common.viewDetails')}
				</Button>

				<Button variant="outline" size="sm" on:click={handleEdit}>
					{$t('common.edit')}
				</Button>

				{#if rentalInfo}
					<Button variant="ghost" size="sm" on:click={handleViewTenants}>
						👥 {$t('rental.tenants')}
					</Button>

					<Button variant="ghost" size="sm" on:click={handleViewMaintenance}>
						🔧 {$t('maintenance.title')}
					</Button>

					<Button variant="ghost" size="sm" on:click={handleViewExpenses}>
						💰 {$t('expenses.title')}
					</Button>
				{/if}
			</div>
		{/if}
	</div>
</div>

<style>
	.line-clamp-1 {
		display: -webkit-box;
		-webkit-line-clamp: 1;
		-webkit-box-orient: vertical;
		overflow: hidden;
	}
</style>
