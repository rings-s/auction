<script>
	import { createEventDispatcher } from 'svelte';
	import { t } from '$lib/i18n';
	import Button from '$lib/components/ui/Button.svelte';
	import FormField from '$lib/components/ui/FormField.svelte';

	const dispatch = createEventDispatcher();

	/** @type {Object} */
	export let activeFilters = {};

	// Filter state
	let occupancyFilter = activeFilters.occupancy_status || '';
	let propertyTypeFilter = activeFilters.property_type || '';
	let minRent = activeFilters.monthly_rent__gte || '';
	let maxRent = activeFilters.monthly_rent__lte || '';
	let locationFilter = activeFilters.location || '';
	let bedroomsFilter = activeFilters.bedrooms__gte || '';
	let bathroomsFilter = activeFilters.bathrooms__gte || '';
	let areaMinFilter = activeFilters.area__gte || '';
	let areaMaxFilter = activeFilters.area__lte || '';
	let yearBuiltMinFilter = activeFilters.year_built__gte || '';
	let yearBuiltMaxFilter = activeFilters.year_built__lte || '';
	let amenitiesFilter = activeFilters.amenities || [];

	// Predefined filter options
	const occupancyOptions = [
		{ value: '', label: $t('common.all') },
		{ value: 'available', label: $t('property.occupancy.available') },
		{ value: 'occupied', label: $t('property.occupancy.occupied') },
		{ value: 'maintenance', label: $t('property.occupancy.maintenance') }
	];

	const propertyTypeOptions = [
		{ value: '', label: $t('common.all') },
		{ value: 'apartment', label: $t('property.type.apartment') },
		{ value: 'villa', label: $t('property.type.villa') },
		{ value: 'commercial', label: $t('property.type.commercial') },
		{ value: 'warehouse', label: $t('property.type.warehouse') },
		{ value: 'land', label: $t('property.type.land') }
	];

	const bedroomOptions = [
		{ value: '', label: $t('common.any') },
		{ value: '1', label: '1+' },
		{ value: '2', label: '2+' },
		{ value: '3', label: '3+' },
		{ value: '4', label: '4+' },
		{ value: '5', label: '5+' }
	];

	const bathroomOptions = [
		{ value: '', label: $t('common.any') },
		{ value: '1', label: '1+' },
		{ value: '2', label: '2+' },
		{ value: '3', label: '3+' },
		{ value: '4', label: '4+' }
	];

	const amenityOptions = [
		{ value: 'parking', label: $t('property.amenities.parking') },
		{ value: 'swimming_pool', label: $t('property.amenities.swimming_pool') },
		{ value: 'gym', label: $t('property.amenities.gym') },
		{ value: 'garden', label: $t('property.amenities.garden') },
		{ value: 'balcony', label: $t('property.amenities.balcony') },
		{ value: 'elevator', label: $t('property.amenities.elevator') },
		{ value: 'security', label: $t('property.amenities.security') },
		{ value: 'air_conditioning', label: $t('property.amenities.air_conditioning') }
	];

	function applyFilters() {
		const filters = {};

		if (occupancyFilter) filters.occupancy_status = occupancyFilter;
		if (propertyTypeFilter) filters.property_type = propertyTypeFilter;
		if (minRent) filters.monthly_rent__gte = parseFloat(minRent);
		if (maxRent) filters.monthly_rent__lte = parseFloat(maxRent);
		if (locationFilter) filters.location = locationFilter;
		if (bedroomsFilter) filters.bedrooms__gte = parseInt(bedroomsFilter);
		if (bathroomsFilter) filters.bathrooms__gte = parseInt(bathroomsFilter);
		if (areaMinFilter) filters.area__gte = parseFloat(areaMinFilter);
		if (areaMaxFilter) filters.area__lte = parseFloat(areaMaxFilter);
		if (yearBuiltMinFilter) filters.year_built__gte = parseInt(yearBuiltMinFilter);
		if (yearBuiltMaxFilter) filters.year_built__lte = parseInt(yearBuiltMaxFilter);
		if (amenitiesFilter.length > 0) filters.amenities = amenitiesFilter;

		dispatch('filterChange', filters);
	}

	function clearAllFilters() {
		occupancyFilter = '';
		propertyTypeFilter = '';
		minRent = '';
		maxRent = '';
		locationFilter = '';
		bedroomsFilter = '';
		bathroomsFilter = '';
		areaMinFilter = '';
		areaMaxFilter = '';
		yearBuiltMinFilter = '';
		yearBuiltMaxFilter = '';
		amenitiesFilter = [];

		dispatch('clearFilters');
	}

	function handleAmenityToggle(amenity) {
		if (amenitiesFilter.includes(amenity)) {
			amenitiesFilter = amenitiesFilter.filter((a) => a !== amenity);
		} else {
			amenitiesFilter = [...amenitiesFilter, amenity];
		}
		applyFilters();
	}

	// Reactive updates
	$: if (occupancyFilter !== activeFilters.occupancy_status) applyFilters();
	$: if (propertyTypeFilter !== activeFilters.property_type) applyFilters();
	$: if (bedroomsFilter !== activeFilters.bedrooms__gte) applyFilters();
	$: if (bathroomsFilter !== activeFilters.bathrooms__gte) applyFilters();

	// Check if any filters are active
	$: hasActiveFilters =
		occupancyFilter ||
		propertyTypeFilter ||
		minRent ||
		maxRent ||
		locationFilter ||
		bedroomsFilter ||
		bathroomsFilter ||
		areaMinFilter ||
		areaMaxFilter ||
		yearBuiltMinFilter ||
		yearBuiltMaxFilter ||
		amenitiesFilter.length > 0;
</script>

<div class="filter-panel-advanced space-y-6">
	<!-- Quick Filters Row -->
	<div class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
		<!-- Occupancy Status -->
		<FormField label={$t('rental.occupancyStatus')}>
			<select
				bind:value={occupancyFilter}
				class="w-full rounded-xl border border-gray-300 px-4 py-2.5 transition-all duration-200 focus:border-transparent focus:ring-2 focus:ring-blue-500 focus:outline-none"
			>
				{#each occupancyOptions as option}
					<option value={option.value}>{option.label}</option>
				{/each}
			</select>
		</FormField>

		<!-- Property Type -->
		<FormField label={$t('property.type.label')}>
			<select
				bind:value={propertyTypeFilter}
				class="w-full rounded-xl border border-gray-300 px-4 py-2.5 transition-all duration-200 focus:border-transparent focus:ring-2 focus:ring-blue-500 focus:outline-none"
			>
				{#each propertyTypeOptions as option}
					<option value={option.value}>{option.label}</option>
				{/each}
			</select>
		</FormField>

		<!-- Bedrooms -->
		<FormField label={$t('property.bedrooms')}>
			<select
				bind:value={bedroomsFilter}
				class="w-full rounded-xl border border-gray-300 px-4 py-2.5 transition-all duration-200 focus:border-transparent focus:ring-2 focus:ring-blue-500 focus:outline-none"
			>
				{#each bedroomOptions as option}
					<option value={option.value}>{option.label}</option>
				{/each}
			</select>
		</FormField>

		<!-- Bathrooms -->
		<FormField label={$t('property.bathrooms')}>
			<select
				bind:value={bathroomsFilter}
				class="w-full rounded-xl border border-gray-300 px-4 py-2.5 transition-all duration-200 focus:border-transparent focus:ring-2 focus:ring-blue-500 focus:outline-none"
			>
				{#each bathroomOptions as option}
					<option value={option.value}>{option.label}</option>
				{/each}
			</select>
		</FormField>
	</div>

	<!-- Price Range -->
	<div class="space-y-3">
		<h4 class="flex items-center gap-2 font-medium text-gray-900">
			<span>💰</span>
			{$t('rental.priceRange')}
		</h4>
		<div class="grid grid-cols-2 gap-4">
			<FormField label={$t('rental.minRent')}>
				<input
					type="number"
					bind:value={minRent}
					placeholder="0"
					min="0"
					step="100"
					class="w-full rounded-xl border border-gray-300 px-4 py-2.5 transition-all duration-200 focus:border-transparent focus:ring-2 focus:ring-blue-500 focus:outline-none"
					on:blur={applyFilters}
				/>
			</FormField>
			<FormField label={$t('rental.maxRent')}>
				<input
					type="number"
					bind:value={maxRent}
					placeholder="999999"
					min="0"
					step="100"
					class="w-full rounded-xl border border-gray-300 px-4 py-2.5 transition-all duration-200 focus:border-transparent focus:ring-2 focus:ring-blue-500 focus:outline-none"
					on:blur={applyFilters}
				/>
			</FormField>
		</div>
	</div>

	<!-- Area Range -->
	<div class="space-y-3">
		<h4 class="flex items-center gap-2 font-medium text-gray-900">
			<span>📐</span>
			{$t('property.area')} (m²)
		</h4>
		<div class="grid grid-cols-2 gap-4">
			<FormField label={$t('property.minArea')}>
				<input
					type="number"
					bind:value={areaMinFilter}
					placeholder="0"
					min="0"
					step="10"
					class="w-full rounded-xl border border-gray-300 px-4 py-2.5 transition-all duration-200 focus:border-transparent focus:ring-2 focus:ring-blue-500 focus:outline-none"
					on:blur={applyFilters}
				/>
			</FormField>
			<FormField label={$t('property.maxArea')}>
				<input
					type="number"
					bind:value={areaMaxFilter}
					placeholder="9999"
					min="0"
					step="10"
					class="w-full rounded-xl border border-gray-300 px-4 py-2.5 transition-all duration-200 focus:border-transparent focus:ring-2 focus:ring-blue-500 focus:outline-none"
					on:blur={applyFilters}
				/>
			</FormField>
		</div>
	</div>

	<!-- Year Built Range -->
	<div class="space-y-3">
		<h4 class="flex items-center gap-2 font-medium text-gray-900">
			<span>📅</span>
			{$t('property.yearBuilt')}
		</h4>
		<div class="grid grid-cols-2 gap-4">
			<FormField label={$t('property.fromYear')}>
				<input
					type="number"
					bind:value={yearBuiltMinFilter}
					placeholder="1950"
					min="1950"
					max={new Date().getFullYear()}
					class="w-full rounded-xl border border-gray-300 px-4 py-2.5 transition-all duration-200 focus:border-transparent focus:ring-2 focus:ring-blue-500 focus:outline-none"
					on:blur={applyFilters}
				/>
			</FormField>
			<FormField label={$t('property.toYear')}>
				<input
					type="number"
					bind:value={yearBuiltMaxFilter}
					placeholder={new Date().getFullYear()}
					min="1950"
					max={new Date().getFullYear()}
					class="w-full rounded-xl border border-gray-300 px-4 py-2.5 transition-all duration-200 focus:border-transparent focus:ring-2 focus:ring-blue-500 focus:outline-none"
					on:blur={applyFilters}
				/>
			</FormField>
		</div>
	</div>

	<!-- Location Filter -->
	<div class="space-y-3">
		<FormField label={$t('property.location')}>
			<input
				type="text"
				bind:value={locationFilter}
				placeholder={$t('property.locationPlaceholder')}
				class="w-full rounded-xl border border-gray-300 px-4 py-2.5 transition-all duration-200 focus:border-transparent focus:ring-2 focus:ring-blue-500 focus:outline-none"
				on:blur={applyFilters}
			/>
		</FormField>
	</div>

	<!-- Amenities -->
	<div class="space-y-3">
		<h4 class="flex items-center gap-2 font-medium text-gray-900">
			<span>✨</span>
			{$t('property.amenities.title')}
		</h4>
		<div class="grid grid-cols-2 gap-3 md:grid-cols-3 lg:grid-cols-4">
			{#each amenityOptions as amenity}
				<label class="group flex cursor-pointer items-center space-x-3">
					<input
						type="checkbox"
						checked={amenitiesFilter.includes(amenity.value)}
						on:change={() => handleAmenityToggle(amenity.value)}
						class="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-2 focus:ring-blue-500"
					/>
					<span
						class="text-sm text-gray-700 transition-colors duration-200 group-hover:text-gray-900"
					>
						{amenity.label}
					</span>
				</label>
			{/each}
		</div>
	</div>

	<!-- Filter Actions -->
	<div class="flex items-center justify-between border-t border-gray-200 pt-4">
		<div class="text-sm text-gray-600">
			{#if hasActiveFilters}
				{$t('common.filtersActive')}
			{:else}
				{$t('common.noFiltersActive')}
			{/if}
		</div>

		<div class="flex gap-3">
			{#if hasActiveFilters}
				<Button
					variant="outline"
					size="sm"
					on:click={clearAllFilters}
					className="hover:bg-red-50 hover:border-red-300 hover:text-red-700"
				>
					<span class="flex items-center gap-2">
						<span>🗑️</span>
						{$t('common.clearAll')}
					</span>
				</Button>
			{/if}

			<Button
				variant="primary"
				size="sm"
				on:click={applyFilters}
				className="bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700"
			>
				<span class="flex items-center gap-2">
					<span>🔍</span>
					{$t('common.applyFilters')}
				</span>
			</Button>
		</div>
	</div>
</div>

<style>
	.filter-panel-advanced {
		max-height: 80vh;
		overflow-y: auto;
	}

	/* Custom scrollbar */
	.filter-panel-advanced::-webkit-scrollbar {
		width: 6px;
	}

	.filter-panel-advanced::-webkit-scrollbar-track {
		background: #f1f5f9;
		border-radius: 3px;
	}

	.filter-panel-advanced::-webkit-scrollbar-thumb {
		background: #cbd5e1;
		border-radius: 3px;
	}

	.filter-panel-advanced::-webkit-scrollbar-thumb:hover {
		background: #94a3b8;
	}
</style>
