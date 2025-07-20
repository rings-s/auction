<script>
	import { onMount, createEventDispatcher } from 'svelte';
	import { rentalPropertyAPI } from '$lib/api/propertyManagement.js';
	import { getTranslation } from '$lib/i18n/index.js';
	import PropertyCardAdvanced from './PropertyCardAdvanced.svelte';
	import FilterPanelAdvanced from './FilterPanelAdvanced.svelte';
	import SearchBarAdvanced from './SearchBarAdvanced.svelte';
	import LoadingSpinner from '$lib/components/animations/LoadingSpinner.svelte';
	import FadeInUp from '$lib/components/animations/FadeInUp.svelte';
	import StaggeredList from '$lib/components/animations/StaggeredList.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import EmptyState from '$lib/components/ui/EmptyState.svelte';
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

	// Advanced filtering and search state
	let searchQuery = '';
	let activeFilters = {};
	let sortBy = 'created_at';
	let sortOrder = 'desc';
	let viewMode = 'grid'; // 'grid', 'list', 'masonry'
	let showFilters = false;
	let savedSearches = [];

	// Pagination
	let currentPage = 1;
	let pageSize = 12;
	let totalCount = 0;
	let totalPages = 0;

	// Performance optimization
	let searchTimeout;
	let lastSearchQuery = '';

	$: t = getTranslation;
	$: hasActiveFilters = Object.keys(activeFilters).length > 0 || searchQuery;
	$: gridClasses = getGridClasses(viewMode);

	onMount(() => {
		loadProperties();
		loadSavedSearches();
	});

	function getGridClasses(mode) {
		switch (mode) {
			case 'list':
				return 'grid grid-cols-1 gap-4';
			case 'masonry':
				return 'columns-1 md:columns-2 lg:columns-3 xl:columns-4 gap-6 space-y-6';
			case 'grid':
			default:
				return 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6';
		}
	}

	async function loadProperties() {
		try {
			loading = true;
			error = '';

			const params = {
				page: currentPage,
				page_size: pageSize,
				search: searchQuery || undefined,
				ordering: sortOrder === 'desc' ? `-${sortBy}` : sortBy,
				...activeFilters
			};

			// Clean up undefined params
			Object.keys(params).forEach((key) => {
				if (params[key] === undefined) {
					delete params[key];
				}
			});

			const response = await rentalPropertyAPI.getAll(params);
			properties = response.data.results || [];
			totalCount = response.data.count || 0;
			totalPages = Math.ceil(totalCount / pageSize);
		} catch (err) {
			error = err.message || $t('errors.loadingFailed');
			console.error('Failed to load rental properties:', err);
		} finally {
			loading = false;
		}
	}

	function loadSavedSearches() {
		const saved = localStorage.getItem('property_saved_searches');
		if (saved) {
			try {
				savedSearches = JSON.parse(saved);
			} catch (e) {
				console.warn('Failed to parse saved searches');
			}
		}
	}

	function handleSearch(event) {
		const query = event.detail?.query || event.target?.value || '';

		// Debounce search
		clearTimeout(searchTimeout);
		searchTimeout = setTimeout(() => {
			if (query !== lastSearchQuery) {
				searchQuery = query;
				lastSearchQuery = query;
				currentPage = 1;
				loadProperties();
			}
		}, 300);
	}

	function handleFilterChange(event) {
		activeFilters = { ...activeFilters, ...event.detail };
		currentPage = 1;
		loadProperties();
	}

	function handleClearFilters() {
		searchQuery = '';
		activeFilters = {};
		currentPage = 1;
		loadProperties();
	}

	function handleSortChange(field) {
		if (sortBy === field) {
			sortOrder = sortOrder === 'asc' ? 'desc' : 'asc';
		} else {
			sortBy = field;
			sortOrder = 'desc';
		}
		loadProperties();
	}

	function handlePageChange(page) {
		currentPage = page;
		loadProperties();

		// Smooth scroll to top
		window.scrollTo({ top: 0, behavior: 'smooth' });
	}

	function handleViewModeChange(mode) {
		viewMode = mode;
	}

	function handleSaveSearch() {
		if (!searchQuery && !hasActiveFilters) return;

		const searchName = prompt($t('search.saveSearchName'));
		if (!searchName) return;

		const newSearch = {
			id: Date.now(),
			name: searchName,
			query: searchQuery,
			filters: activeFilters,
			createdAt: new Date().toISOString()
		};

		savedSearches = [newSearch, ...savedSearches.slice(0, 9)]; // Keep last 10
		localStorage.setItem('property_saved_searches', JSON.stringify(savedSearches));
	}

	function handleLoadSavedSearch(search) {
		searchQuery = search.query;
		activeFilters = search.filters;
		currentPage = 1;
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

	function getSortIcon(field) {
		if (sortBy !== field) return '↕️';
		return sortOrder === 'asc' ? '⬆️' : '⬇️';
	}
</script>

<div class="property-list-advanced space-y-8">
	<!-- Enhanced Header -->
	<FadeInUp>
		<div class="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
			<div class="space-y-2">
				<h1
					class="bg-gradient-to-r from-gray-900 to-gray-600 bg-clip-text text-4xl font-bold text-transparent"
				>
					{$t('rental.title')}
				</h1>
				<p class="text-lg text-gray-600">{$t('rental.subtitle')}</p>
				{#if !loading && totalCount > 0}
					<p class="text-sm text-gray-500">
						{$t('common.showingResults', { count: properties.length, total: totalCount })}
					</p>
				{/if}
			</div>

			<div class="flex items-center gap-3">
				<!-- View Mode Toggle -->
				<div class="flex items-center rounded-xl bg-gray-100 p-1">
					<button
						class="rounded-lg p-2 transition-all duration-200 {viewMode === 'grid'
							? 'bg-white text-blue-600 shadow-sm'
							: 'text-gray-600 hover:text-gray-900'}"
						on:click={() => handleViewModeChange('grid')}
						title="Grid View"
					>
						<svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
							<path
								d="M5 3a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2V5a2 2 0 00-2-2H5zM5 11a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2v-2a2 2 0 00-2-2H5zM11 5a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V5zM11 13a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"
							/>
						</svg>
					</button>
					<button
						class="rounded-lg p-2 transition-all duration-200 {viewMode === 'list'
							? 'bg-white text-blue-600 shadow-sm'
							: 'text-gray-600 hover:text-gray-900'}"
						on:click={() => handleViewModeChange('list')}
						title="List View"
					>
						<svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
							<path
								fill-rule="evenodd"
								d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z"
								clip-rule="evenodd"
							/>
						</svg>
					</button>
				</div>

				{#if showCreateButton}
					<Button
						variant="primary"
						on:click={handleCreateProperty}
						className="bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 shadow-lg"
					>
						<span class="flex items-center gap-2">
							<span>✨</span>
							{$t('rental.create')}
						</span>
					</Button>
				{/if}
			</div>
		</div>
	</FadeInUp>

	<!-- Advanced Search and Filters -->
	<FadeInUp delay={100}>
		<div class="shadow-soft overflow-hidden rounded-3xl border border-gray-100 bg-white">
			<!-- Search Bar -->
			<div class="border-b border-gray-100 p-6">
				<SearchBarAdvanced
					placeholder={$t('rental.searchPlaceholder')}
					{savedSearches}
					on:search={handleSearch}
					on:loadSavedSearch={handleLoadSavedSearch}
					on:saveSearch={handleSaveSearch}
				/>
			</div>

			<!-- Filter Panel -->
			<div class="border-b border-gray-100">
				<button
					class="flex w-full items-center justify-between p-4 text-left transition-colors duration-200 hover:bg-gray-50"
					on:click={() => (showFilters = !showFilters)}
				>
					<span class="flex items-center gap-2 font-medium text-gray-900">
						<span>🔍</span>
						{$t('common.filters')}
						{#if hasActiveFilters}
							<span class="rounded-full bg-blue-100 px-2 py-1 text-xs text-blue-800">
								{Object.keys(activeFilters).length + (searchQuery ? 1 : 0)}
							</span>
						{/if}
					</span>
					<span
						class="transform transition-transform duration-200 {showFilters ? 'rotate-180' : ''}"
					>
						⬇️
					</span>
				</button>

				{#if showFilters}
					<div class="bg-gray-50 p-6">
						<FilterPanelAdvanced
							{activeFilters}
							on:filterChange={handleFilterChange}
							on:clearFilters={handleClearFilters}
						/>
					</div>
				{/if}
			</div>

			<!-- Sort Options -->
			<div class="bg-gray-50 p-4">
				<div class="flex flex-wrap items-center gap-2">
					<span class="text-sm font-medium text-gray-700">{$t('common.sortBy')}:</span>

					<button
						class="rounded-lg px-3 py-1.5 text-sm transition-all duration-200 {sortBy === 'title'
							? 'bg-blue-100 text-blue-800 shadow-sm'
							: 'bg-white text-gray-700 hover:bg-gray-100'}"
						on:click={() => handleSortChange('title')}
					>
						{$t('property.title')}
						{getSortIcon('title')}
					</button>

					<button
						class="rounded-lg px-3 py-1.5 text-sm transition-all duration-200 {sortBy ===
						'monthly_rent'
							? 'bg-blue-100 text-blue-800 shadow-sm'
							: 'bg-white text-gray-700 hover:bg-gray-100'}"
						on:click={() => handleSortChange('monthly_rent')}
					>
						{$t('rental.monthlyRent')}
						{getSortIcon('monthly_rent')}
					</button>

					<button
						class="rounded-lg px-3 py-1.5 text-sm transition-all duration-200 {sortBy ===
						'occupancy_rate'
							? 'bg-blue-100 text-blue-800 shadow-sm'
							: 'bg-white text-gray-700 hover:bg-gray-100'}"
						on:click={() => handleSortChange('occupancy_rate')}
					>
						{$t('rental.occupancy')}
						{getSortIcon('occupancy_rate')}
					</button>

					<button
						class="rounded-lg px-3 py-1.5 text-sm transition-all duration-200 {sortBy ===
						'created_at'
							? 'bg-blue-100 text-blue-800 shadow-sm'
							: 'bg-white text-gray-700 hover:bg-gray-100'}"
						on:click={() => handleSortChange('created_at')}
					>
						{$t('common.dateCreated')}
						{getSortIcon('created_at')}
					</button>
				</div>
			</div>
		</div>
	</FadeInUp>

	<!-- Error Display -->
	{#if error}
		<FadeInUp delay={200}>
			<Alert type="error" message={error} />
		</FadeInUp>
	{/if}

	<!-- Loading State -->
	{#if loading}
		<div class="flex justify-center py-12">
			<LoadingSpinner size="lg" variant="spinner" />
		</div>
	{:else if properties.length === 0 && !error}
		<!-- Empty State -->
		<FadeInUp delay={200}>
			<EmptyState
				title={hasActiveFilters ? $t('rental.noResultsFound') : $t('rental.noPropertiesYet')}
				description={hasActiveFilters
					? $t('rental.tryDifferentFilters')
					: $t('rental.addFirstProperty')}
				actionLabel={hasActiveFilters ? $t('common.clearFilters') : $t('rental.create')}
				on:action={hasActiveFilters ? handleClearFilters : handleCreateProperty}
			/>
		</FadeInUp>
	{:else}
		<!-- Properties Grid/List -->
		<StaggeredList staggerDelay={100}>
			<div class={gridClasses}>
				{#each properties as property, index (property.id)}
					<PropertyCardAdvanced
						{property}
						{index}
						variant={index === 0 && viewMode === 'grid' ? 'featured' : 'default'}
						on:view={handleViewProperty}
						on:edit={handleEditProperty}
						on:viewTenants={handleViewTenants}
						on:viewMaintenance={handleViewMaintenance}
						on:viewExpenses={handleViewExpenses}
					/>
				{/each}
			</div>
		</StaggeredList>

		<!-- Enhanced Pagination -->
		{#if totalPages > 1}
			<FadeInUp delay={300}>
				<div class="mt-12 flex items-center justify-center gap-3">
					<!-- Previous Button -->
					<Button
						variant="outline"
						size="sm"
						disabled={currentPage === 1}
						on:click={() => handlePageChange(currentPage - 1)}
						className="hover:bg-blue-50 hover:border-blue-300"
					>
						← {$t('common.previous')}
					</Button>

					<!-- Page Numbers -->
					{#each getPageNumbers() as page}
						<Button
							variant={currentPage === page ? 'primary' : 'ghost'}
							size="sm"
							on:click={() => handlePageChange(page)}
							className={currentPage === page
								? 'bg-gradient-to-r from-blue-600 to-cyan-600'
								: 'hover:bg-blue-50'}
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
						className="hover:bg-blue-50 hover:border-blue-300"
					>
						{$t('common.next')} →
					</Button>
				</div>
			</FadeInUp>
		{/if}
	{/if}
</div>

<style>
	.property-list-advanced {
		min-height: 50vh;
	}

	/* Masonry layout support */
	.columns-1 > :global(*) {
		break-inside: avoid;
		margin-bottom: 1.5rem;
	}

	@media (max-width: 768px) {
		.columns-1 {
			columns: 1 !important;
		}
	}
</style>
