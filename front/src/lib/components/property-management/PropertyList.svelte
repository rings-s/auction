<script>
	import { onMount, createEventDispatcher } from 'svelte';
	import { getProperties } from '$lib/api/property.js';
	import { t, locale } from '$lib/i18n';
	import PropertyCard from './PropertyCard.svelte';
	import LoadingSpinner from '$lib/components/animations/LoadingSpinner.svelte';
	import Button from '$lib/components/ui/Button.svelte';

	const dispatch = createEventDispatcher();

	/** @type {{ properties?: Array, loading?: boolean, error?: string, filters?: Object, showCreateButton?: boolean }} */
	let {
		properties = [],
		loading = false,
		error = '',
		filters = {},
		showCreateButton = true
	} = $props();

	let isRTL = $derived($locale === 'ar');

	// Filter state
	let searchQuery = '';
	let propertyTypeFilter = '';
	let statusFilter = '';
	let minPrice = '';
	let maxPrice = '';
	let sortBy = 'created_at';
	let sortOrder = 'desc';

	// Pagination
	let currentPage = 1;
	let pageSize = 12;
	let totalCount = 0;
	let totalPages = 0;

	let hasFilters = $derived(searchQuery || propertyTypeFilter || statusFilter || minPrice || maxPrice);

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
				property_status: statusFilter || undefined,
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
				const results = response.data?.results || response || [];
				properties = results;
				totalCount = response.data?.count || results.length;
				totalPages = Math.ceil(totalCount / pageSize);
			}
		} catch (err) {
			error = err.message || $t('errors.loadingFailed');
			console.error('Failed to load properties:', err);
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
		propertyTypeFilter = '';
		statusFilter = '';
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

<div class="space-y-8" dir={isRTL ? 'rtl' : 'ltr'}>
	<!-- Header -->
	<div class="flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between">
		<div>
			<h1 class="text-3xl font-bold text-gray-900 dark:text-white">
				{$t('propertyManagement.title')}
			</h1>
			<p class="mt-2 text-gray-600 dark:text-gray-300">{$t('propertyManagement.subtitle')}</p>
		</div>

		{#if showCreateButton}
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
		{/if}
	</div>

	<!-- Filters Section -->
	<div
		class="rounded-2xl border border-gray-200 bg-white p-6 shadow-lg dark:border-gray-700 dark:bg-gray-800"
	>
		<div class="mb-6 grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
			<!-- Search -->
			<div>
				<label for="search" class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">
					{$t('common.search')}
				</label>
				<input
					type="text"
					id="search"
					bind:value={searchQuery}
					placeholder={$t('property.searchPlaceholder')}
					class="w-full rounded-2xl border border-gray-300 bg-white px-4 py-3 text-gray-900 placeholder-gray-500 shadow-md transition-all duration-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:placeholder-gray-400"
					onkeydown={(e) => e.key === 'Enter' && handleSearch()}
				/>
			</div>

			<!-- Property Type Filter -->
			<div>
				<label
					for="property-type"
					class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
				>
					{$t('property.type')}
				</label>
				<select
					id="property-type"
					bind:value={propertyTypeFilter}
					class="w-full rounded-2xl border border-gray-300 bg-white px-4 py-3 text-gray-900 shadow-md transition-all duration-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
				>
					<option value="">{$t('common.all')}</option>
					<option value="apartment">{$t('property.type.apartment')}</option>
					<option value="villa">{$t('property.type.villa')}</option>
					<option value="commercial">{$t('property.type.commercial')}</option>
					<option value="land">{$t('property.type.land')}</option>
					<option value="warehouse">{$t('property.type.warehouse')}</option>
				</select>
			</div>

			<!-- Status Filter -->
			<div>
				<label for="status" class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">
					{$t('property.status')}
				</label>
				<select
					id="status"
					bind:value={statusFilter}
					class="w-full rounded-2xl border border-gray-300 bg-white px-4 py-3 text-gray-900 shadow-md transition-all duration-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
				>
					<option value="">{$t('common.all')}</option>
					<option value="available">{$t('property.status.available')}</option>
					<option value="sold">{$t('property.status.sold')}</option>
					<option value="pending">{$t('property.status.pending')}</option>
					<option value="off_market">{$t('property.status.offMarket')}</option>
				</select>
			</div>

			<!-- Min Price -->
			<div>
				<label
					for="min-price"
					class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
				>
					{$t('property.minPrice')}
				</label>
				<input
					type="number"
					id="min-price"
					bind:value={minPrice}
					placeholder="0"
					min="0"
					step="10000"
					class="w-full rounded-2xl border border-gray-300 bg-white px-4 py-3 text-gray-900 shadow-md transition-all duration-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
				/>
			</div>

			<!-- Max Price -->
			<div>
				<label
					for="max-price"
					class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
				>
					{$t('property.maxPrice')}
				</label>
				<input
					type="number"
					id="max-price"
					bind:value={maxPrice}
					placeholder="9999999"
					min="0"
					step="10000"
					class="w-full rounded-2xl border border-gray-300 bg-white px-4 py-3 text-gray-900 shadow-md transition-all duration-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
				/>
			</div>
		</div>

		<!-- Filter Actions -->
		<div class="flex flex-wrap gap-3">
			<Button
				variant="primary"
				class="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700"
				onclick={handleSearch}
			>
				<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
					/>
				</svg>
				{$t('common.search')}
			</Button>

			{#if hasFilters}
				<Button variant="outline" onclick={handleClearFilters}>
					<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
						/>
					</svg>
					{$t('common.clearFilters')}
				</Button>
			{/if}
		</div>
	</div>

	<!-- Sort Options -->
	<div
		class="flex flex-wrap items-center gap-3 rounded-2xl border border-gray-200 bg-gray-50 p-4 text-sm dark:border-gray-700 dark:bg-gray-800"
	>
		<span class="font-medium text-gray-700 dark:text-gray-300">{$t('common.sortBy')}:</span>

		<button
			class="rounded-xl px-4 py-2 transition-all duration-200 {sortBy === 'title'
				? 'bg-blue-100 text-blue-800 shadow-md dark:bg-blue-900 dark:text-blue-200'
				: 'bg-white text-gray-700 shadow-sm hover:bg-blue-50 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600'}"
			onclick={() => handleSortChange('title')}
		>
			{$t('property.title')}
			{sortBy === 'title' ? (sortOrder === 'asc' ? '↑' : '↓') : ''}
		</button>

		<button
			class="rounded-xl px-4 py-2 transition-all duration-200 {sortBy === 'market_value'
				? 'bg-blue-100 text-blue-800 shadow-md dark:bg-blue-900 dark:text-blue-200'
				: 'bg-white text-gray-700 shadow-sm hover:bg-blue-50 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600'}"
			onclick={() => handleSortChange('market_value')}
		>
			{$t('property.marketValue')}
			{sortBy === 'market_value' ? (sortOrder === 'asc' ? '↑' : '↓') : ''}
		</button>

		<button
			class="rounded-xl px-4 py-2 transition-all duration-200 {sortBy === 'size_sqm'
				? 'bg-blue-100 text-blue-800 shadow-md dark:bg-blue-900 dark:text-blue-200'
				: 'bg-white text-gray-700 shadow-sm hover:bg-blue-50 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600'}"
			onclick={() => handleSortChange('size_sqm')}
		>
			{$t('property.area')}
			{sortBy === 'size_sqm' ? (sortOrder === 'asc' ? '↑' : '↓') : ''}
		</button>

		<button
			class="rounded-xl px-4 py-2 transition-all duration-200 {sortBy === 'created_at'
				? 'bg-blue-100 text-blue-800 shadow-md dark:bg-blue-900 dark:text-blue-200'
				: 'bg-white text-gray-700 shadow-sm hover:bg-blue-50 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600'}"
			onclick={() => handleSortChange('created_at')}
		>
			{$t('common.dateCreated')}
			{sortBy === 'created_at' ? (sortOrder === 'asc' ? '↑' : '↓') : ''}
		</button>
	</div>

	<!-- Results Summary -->
	{#if !loading}
		<div
			class="rounded-2xl border border-gray-200 bg-gray-50 p-4 text-sm text-gray-600 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-400"
		>
			<div class="flex items-center">
				<svg
					class="mr-2 h-5 w-5 text-blue-500"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
					/>
				</svg>
				{$t('common.showingResults', { count: properties.length, total: totalCount })}
			</div>
		</div>
	{/if}

	<!-- Error Display -->
	{#if error}
		<div
			class="rounded-2xl border border-red-200 bg-red-50 p-6 dark:border-red-800 dark:bg-red-900/20"
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
				<Button variant="outline" onclick={loadProperties}>
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

	<!-- Loading State -->
	{#if loading}
		<div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
			{#each Array(8) as _}
				<div class="animate-pulse">
					<div class="h-80 rounded-2xl bg-gray-200 dark:bg-gray-700"></div>
				</div>
			{/each}
		</div>
	{:else if properties.length === 0 && !error}
		<!-- Empty State -->
		<div
			class="rounded-2xl border-2 border-dashed border-gray-300 bg-gray-50 py-16 text-center dark:border-gray-600 dark:bg-gray-800"
		>
			<svg
				class="mx-auto mb-4 h-16 w-16 text-gray-400"
				fill="none"
				stroke="currentColor"
				viewBox="0 0 24 24"
			>
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="1"
					d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
				/>
			</svg>
			<h3 class="mb-2 text-xl font-semibold text-gray-700 dark:text-gray-300">
				{hasFilters ? $t('property.noResultsFound') : $t('property.noPropertiesYet')}
			</h3>
			<p class="mb-6 text-gray-500 dark:text-gray-400">
				{hasFilters ? $t('property.tryDifferentFilters') : $t('property.addFirstProperty')}
			</p>
			<Button
				variant="primary"
				class="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700"
				onclick={hasFilters ? handleClearFilters : handleCreateProperty}
			>
				{hasFilters ? $t('common.clearFilters') : $t('property.create')}
			</Button>
		</div>
	{:else}
		<!-- Properties Grid -->
		<div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
			{#each properties as property (property.id)}
				<PropertyCard {property} on:view={handleViewProperty} on:edit={handleEditProperty} />
			{/each}
		</div>

		<!-- Pagination -->
		{#if totalPages > 1}
			<div
				class="mt-8 flex items-center justify-center gap-2 rounded-2xl border border-gray-200 bg-gray-50 p-4 dark:border-gray-700 dark:bg-gray-800"
			>
				<!-- Previous Button -->
				<Button
					variant="outline"
					size="sm"
					disabled={currentPage === 1}
					onclick={() => handlePageChange(currentPage - 1)}
				>
					<svg class="mr-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M15 19l-7-7 7-7"
						/>
					</svg>
					{$t('common.previous')}
				</Button>

				<!-- Page Numbers -->
				{#each getPageNumbers() as page}
					<Button
						variant={currentPage === page ? 'primary' : 'ghost'}
						size="sm"
						onclick={() => handlePageChange(page)}
					>
						{page}
					</Button>
				{/each}

				<!-- Next Button -->
				<Button
					variant="outline"
					size="sm"
					disabled={currentPage === totalPages}
					onclick={() => handlePageChange(currentPage + 1)}
				>
					{$t('common.next')}
					<svg class="ml-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M9 5l7 7-7 7"
						/>
					</svg>
				</Button>
			</div>
		{/if}
	{/if}
</div>

<style>
	/* Enhanced form field focus states */
	input:focus,
	select:focus {
		box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
		border-color: #3b82f6;
	}

	/* Custom animation for filter buttons */
	@keyframes pulse-border {
		0%,
		100% {
			border-color: theme('colors.blue.300');
		}
		50% {
			border-color: theme('colors.blue.500');
		}
	}

	.filter-active {
		animation: pulse-border 2s ease-in-out infinite;
	}
</style>
