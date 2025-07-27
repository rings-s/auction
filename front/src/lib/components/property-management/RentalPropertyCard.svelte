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

	// Map actual property data structure from backend API
	$: primaryImage = property?.media?.find((m) => m.is_primary)?.file || property?.media?.[0]?.file;
	$: propertyAddress = property?.location_data
		? `${property.location_data.city}, ${property.location_data.state}`
		: property?.address || '-';
	$: propertyArea = property?.size_sqm || property?.area || 0;
	$: propertyRooms = property?.rooms || [];
	$: estimatedRent = property?.market_value ? Math.round((property.market_value * 0.08) / 12) : 0;

	// Rental status - derived from property status or defaults
	$: occupancyStatus =
		property?.status === 'rented' || property?.is_occupied ? 'occupied' : 'available';
	$: tenantCount = property?.current_tenants || 0;
	$: maxTenants = Math.max(1, Math.floor(propertyRooms.length / 2)) || 1;

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
		{#if primaryImage}
			<img
				src={primaryImage}
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
				📍 {propertyAddress}
			</p>
		</div>

		<!-- Property Information Grid -->
		<div class="mb-4 grid grid-cols-2 gap-3">
			<!-- Market Value -->
			<div class="rounded-lg bg-green-50 p-2">
				<p class="text-xs font-medium text-green-700">{$t('property.marketValue')}</p>
				<p class="text-sm font-bold text-green-800">
					{formatCurrency(property.market_value || 0)}
				</p>
			</div>

			<!-- Estimated Monthly Rent -->
			<div class="rounded-lg bg-blue-50 p-2">
				<p class="text-xs font-medium text-blue-700">{$t('rental.estimatedRent')}</p>
				<p class="text-sm font-bold text-blue-800">
					{formatCurrency(estimatedRent)}
				</p>
			</div>

			<!-- Occupancy Status -->
			<div class="rounded-lg bg-purple-50 p-2">
				<p class="text-xs font-medium text-purple-700">{$t('property.status')}</p>
				<p class="text-sm font-bold text-purple-800">
					{$t(`property.occupancy.${occupancyStatus}`)}
				</p>
			</div>

			<!-- Property Area -->
			<div class="rounded-lg bg-orange-50 p-2">
				<p class="text-xs font-medium text-orange-700">{$t('property.area')}</p>
				<p class="text-sm font-bold text-orange-800">
					{propertyArea}
					{$t('property.sqm')}
				</p>
			</div>
		</div>

		<!-- Property Stats -->
		<div class="mb-4 flex items-center gap-4 text-sm text-gray-600">
			{#if propertyRooms.length}
				<span>🛏️ {propertyRooms.length} {$t('property.rooms')}</span>
			{/if}
			{#if property.floors}
				<span>🏢 {property.floors} {$t('property.floors')}</span>
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

				<Button variant="ghost" size="sm" on:click={handleViewTenants}>
					👥 {$t('rental.tenants')}
				</Button>

				<Button variant="ghost" size="sm" on:click={handleViewMaintenance}>
					🔧 {$t('maintenance.title')}
				</Button>

				<Button variant="ghost" size="sm" on:click={handleViewExpenses}>
					💰 {$t('expenses.title')}
				</Button>
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
