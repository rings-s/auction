<script>
	import { onMount, createEventDispatcher } from 'svelte';
	import { getProperties } from '$lib/api/property.js';
	import { t } from '$lib/i18n';
	import RentalPropertyCard from './RentalPropertyCard.svelte';
	import LoadingSkeleton from '$lib/components/ui/LoadingSkeleton.svelte';
	import EmptyState from '$lib/components/ui/EmptyState.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import FormField from '$lib/components/ui/FormField.svelte';
	import Alert from '$lib/components/ui/Alert.svelte';

	const dispatch = createEventDispatcher();

	/** @type {Array} */
	export let properties = [];
	/** @type {boolean} */
	export let loading = false;
	/** @type {string} */
	export let error = '';
	/** @type {Object} */
	export let filters = {};
	/** @type {boolean} */
	export let showCreateButton = true;

	// Filter state
	let searchQuery = '';
	let occupancyFilter = '';
	let propertyTypeFilter = '';
	let minPrice = '';
	let maxPrice = '';
	let sortBy = 'created_at';
	let sortOrder = 'desc';

	// Pagination
	let currentPage = 1;
	let pageSize = 12;
	let totalCount = 0;
	let totalPages = 0;

	$: hasFilters = searchQuery || occupancyFilter || propertyTypeFilter || minPrice || maxPrice;

	onMount(() => {
		loadProperties();
	});

	async function loadProperties() {
		try {
			loading = true;
			error = '';

			const params = {
				page: currentPage,
				page_size: pageSize,
				search: searchQuery || undefined,
				property_type: propertyTypeFilter || undefined,
				min_price: minPrice || undefined,
				max_price: maxPrice || undefined,
				ordering: sortOrder === 'desc' ? `-${sortBy}` : sortBy
			};

			// Clean up undefined params
			Object.keys(params).forEach((key) => {
				if (params[key] === undefined) {
					delete params[key];
				}
			});

			const response = await getProperties(params);

			// Handle different response formats
			if (response.results) {
				properties = response.results;
				totalCount = response.count || 0;
				totalPages = Math.ceil(totalCount / pageSize);
			} else if (Array.isArray(response)) {
				properties = response;
				totalCount = response.length;
				totalPages = 1;
			} else {
				const results = response.data?.results || [];
				properties = results;
				totalCount = response.data?.count || results.length;
				totalPages = Math.ceil(totalCount / pageSize);
			}
		} catch (err) {
			error = err.message || $t('errors.loadingFailed');
			console.error('Failed to load rental properties:', err);
		} finally {
			loading = false;
		}
	}

	function handleSearch() {
		currentPage = 1;
		loadProperties();
	}

	function handleClearFilters() {
		searchQuery = '';
		occupancyFilter = '';
		propertyTypeFilter = '';
		minPrice = '';
		maxPrice = '';
		currentPage = 1;
		loadProperties();
	}

	function handleSortChange(field) {
		if (sortBy === field) {
			sortOrder = sortOrder === 'asc' ? 'desc' : 'asc';
		} else {
			sortBy = field;
			sortOrder = 'asc';
		}
		loadProperties();
	}

	function handlePageChange(page) {
		currentPage = page;
		loadProperties();
	}

	// Event handlers for property card actions
	function handleViewProperty(event) {
		dispatch('viewProperty', event.detail);
	}

	function handleEditProperty(event) {
		dispatch('editProperty', event.detail);
	}

	function handleViewTenants(event) {
		dispatch('viewTenants', event.detail);
	}

	function handleViewMaintenance(event) {
		dispatch('viewMaintenance', event.detail);
	}

	function handleViewExpenses(event) {
		dispatch('viewExpenses', event.detail);
	}

	function handleCreateProperty() {
		dispatch('createProperty');
	}

	// Generate page numbers for pagination
	function getPageNumbers() {
		const pages = [];
		const maxVisible = 5;

		if (totalPages <= maxVisible) {
			for (let i = 1; i <= totalPages; i++) {
				pages.push(i);
			}
		} else {
			const start = Math.max(1, currentPage - 2);
			const end = Math.min(totalPages, start + maxVisible - 1);

			for (let i = start; i <= end; i++) {
				pages.push(i);
			}
		}

		return pages;
	}
</script>

<div class="space-y-6">
	<!-- Header -->
	<div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
		<div>
			<h1 class="text-2xl font-bold text-gray-900">{$t('rental.title')}</h1>
			<p class="text-gray-600">{$t('rental.subtitle')}</p>
		</div>

		{#if showCreateButton}
			<Button variant="primary" on:click={handleCreateProperty}>
				+ {$t('rental.create')}
			</Button>
		{/if}
	</div>

	<!-- Filters Section -->
	<div class="rounded-lg border border-gray-200 bg-white p-6">
		<div class="mb-4 grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
			<!-- Search -->
			<FormField label={$t('common.search')}>
				<input
					type="text"
					bind:value={searchQuery}
					placeholder={$t('rental.searchPlaceholder')}
					class="w-full rounded-md border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
					on:keydown={(e) => e.key === 'Enter' && handleSearch()}
				/>
			</FormField>

			<!-- Occupancy Filter -->
			<FormField label={$t('rental.occupancyStatus')}>
				<select
					bind:value={occupancyFilter}
					class="w-full rounded-md border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
				>
					<option value="">{$t('common.all')}</option>
					<option value="available">{$t('property.occupancy.available')}</option>
					<option value="occupied">{$t('property.occupancy.occupied')}</option>
					<option value="maintenance">{$t('property.occupancy.maintenance')}</option>
				</select>
			</FormField>

			<!-- Property Type Filter -->
			<FormField label={$t('property.type.label')}>
				<select
					bind:value={propertyTypeFilter}
					class="w-full rounded-md border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
				>
					<option value="">{$t('common.all')}</option>
					<option value="apartment">{$t('property.type.apartment')}</option>
					<option value="villa">{$t('property.type.villa')}</option>
					<option value="commercial">{$t('property.type.commercial')}</option>
					<option value="warehouse">{$t('property.type.warehouse')}</option>
				</select>
			</FormField>

			<!-- Min Price -->
			<FormField label={$t('property.minPrice')}>
				<input
					type="number"
					bind:value={minPrice}
					placeholder="0"
					min="0"
					step="10000"
					class="w-full rounded-md border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
				/>
			</FormField>

			<!-- Max Price -->
			<FormField label={$t('property.maxPrice')}>
				<input
					type="number"
					bind:value={maxPrice}
					placeholder="9999999"
					min="0"
					step="10000"
					class="w-full rounded-md border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
				/>
			</FormField>
		</div>

		<!-- Filter Actions -->
		<div class="flex flex-wrap gap-2">
			<Button variant="primary" on:click={handleSearch}>
				🔍 {$t('common.search')}
			</Button>

			{#if hasFilters}
				<Button variant="outline" on:click={handleClearFilters}>
					{$t('common.clearFilters')}
				</Button>
			{/if}
		</div>
	</div>

	<!-- Sort Options -->
	<div class="flex flex-wrap items-center gap-2 text-sm">
		<span class="text-gray-600">{$t('common.sortBy')}:</span>

		<button
			class="rounded px-3 py-1 {sortBy === 'title'
				? 'bg-blue-100 text-blue-800'
				: 'bg-gray-100 text-gray-700'} hover:bg-blue-50"
			on:click={() => handleSortChange('title')}
		>
			{$t('property.title')}
			{sortBy === 'title' ? (sortOrder === 'asc' ? '↑' : '↓') : ''}
		</button>

		<button
			class="rounded px-3 py-1 {sortBy === 'market_value'
				? 'bg-blue-100 text-blue-800'
				: 'bg-gray-100 text-gray-700'} hover:bg-blue-50"
			on:click={() => handleSortChange('market_value')}
		>
			{$t('property.marketValue')}
			{sortBy === 'market_value' ? (sortOrder === 'asc' ? '↑' : '↓') : ''}
		</button>

		<button
			class="rounded px-3 py-1 {sortBy === 'size_sqm'
				? 'bg-blue-100 text-blue-800'
				: 'bg-gray-100 text-gray-700'} hover:bg-blue-50"
			on:click={() => handleSortChange('size_sqm')}
		>
			{$t('property.area')}
			{sortBy === 'size_sqm' ? (sortOrder === 'asc' ? '↑' : '↓') : ''}
		</button>

		<button
			class="rounded px-3 py-1 {sortBy === 'created_at'
				? 'bg-blue-100 text-blue-800'
				: 'bg-gray-100 text-gray-700'} hover:bg-blue-50"
			on:click={() => handleSortChange('created_at')}
		>
			{$t('common.dateCreated')}
			{sortBy === 'created_at' ? (sortOrder === 'asc' ? '↑' : '↓') : ''}
		</button>
	</div>

	<!-- Results Summary -->
	{#if !loading}
		<div class="text-sm text-gray-600">
			{$t('common.showingResults', { count: properties.length, total: totalCount })}
		</div>
	{/if}

	<!-- Error Display -->
	{#if error}
		<Alert type="error" message={error} />
	{/if}

	<!-- Loading State -->
	{#if loading}
		<div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
			{#each Array(8) as _}
				<LoadingSkeleton height="400px" />
			{/each}
		</div>
	{:else if properties.length === 0 && !error}
		<!-- Empty State -->
		<EmptyState
			title={hasFilters ? $t('rental.noResultsFound') : $t('rental.noPropertiesYet')}
			description={hasFilters ? $t('rental.tryDifferentFilters') : $t('rental.addFirstProperty')}
			actionLabel={hasFilters ? $t('common.clearFilters') : $t('rental.create')}
			on:action={hasFilters ? handleClearFilters : handleCreateProperty}
		/>
	{:else}
		<!-- Properties Grid -->
		<div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
			{#each properties as property (property.id)}
				<RentalPropertyCard
					{property}
					on:view={handleViewProperty}
					on:edit={handleEditProperty}
					on:viewTenants={handleViewTenants}
					on:viewMaintenance={handleViewMaintenance}
					on:viewExpenses={handleViewExpenses}
				/>
			{/each}
		</div>

		<!-- Pagination -->
		{#if totalPages > 1}
			<div class="mt-8 flex items-center justify-center gap-2">
				<!-- Previous Button -->
				<Button
					variant="outline"
					size="sm"
					disabled={currentPage === 1}
					on:click={() => handlePageChange(currentPage - 1)}
				>
					← {$t('common.previous')}
				</Button>

				<!-- Page Numbers -->
				{#each getPageNumbers() as page}
					<Button
						variant={currentPage === page ? 'primary' : 'ghost'}
						size="sm"
						on:click={() => handlePageChange(page)}
					>
						{page}
					</Button>
				{/each}

				<!-- Next Button -->
				<Button
					variant="outline"
					size="sm"
					disabled={currentPage === totalPages}
					on:click={() => handlePageChange(currentPage + 1)}
				>
					{$t('common.next')} →
				</Button>
			</div>
		{/if}
	{/if}
</div>
