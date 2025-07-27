<script>
	import { onMount, createEventDispatcher } from 'svelte';
	import { rentalPropertyAPI } from '$lib/api/propertyManagement.js';
	import { t } from '$lib/i18n';
	import { toast } from '$lib/stores/toastStore.svelte.js';

	// Responsive components
	import ResponsiveGrid from '$lib/components/responsive/ResponsiveGrid.svelte';
	import MobileDrawer from '$lib/components/responsive/MobileDrawer.svelte';
	import {
		isMobile,
		isTablet,
		isDesktop
	} from '$lib/components/responsive/BreakpointHelper.svelte';

	// Enhanced components
	import PropertyCardAdvanced from './PropertyCardAdvanced.svelte';
	import FilterPanelAdvanced from './FilterPanelAdvanced.svelte';
	import SearchBarAdvanced from './SearchBarAdvanced.svelte';
	import LoadingSpinner from '$lib/components/animations/LoadingSpinner.svelte';
	import FadeInUp from '$lib/components/animations/FadeInUp.svelte';
	import StaggeredList from '$lib/components/animations/StaggeredList.svelte';
	import Button from '$lib/components/ui/Button.svelte';

	const dispatch = createEventDispatcher();

	/** @type {Array} */
	export let properties = [];
	/** @type {boolean} */
	export let loading = false;
	/** @type {string} */
	export let error = '';
	/** @type {boolean} */
	export let showCreateButton = true;

	// Mobile-first state management
	let searchQuery = '';
	let activeFilters = {};
	let sortBy = 'created_at';
	let sortOrder = 'desc';
	let viewMode = 'grid'; // 'grid', 'list', 'compact'
	let showFilterDrawer = false;
	let showSortDrawer = false;
	let savedSearches = [];

	// Pagination for mobile infinite scroll
	let currentPage = 1;
	let pageSize = 10; // Smaller page size for mobile
	let totalCount = 0;
	let hasMore = true;
	let loadingMore = false;

	// Performance optimization
	let searchTimeout;
	let intersectionObserver;
	let loadMoreElement;

	$: hasActiveFilters = Object.keys(activeFilters).length > 0 || searchQuery;
	$: filteredProperties = filterAndSortProperties(
		properties,
		searchQuery,
		activeFilters,
		sortBy,
		sortOrder
	);

	// Responsive grid configuration
	$: gridConfig = {
		minItemWidth: $isMobile ? 280 : $isTablet ? 320 : 360,
		gap: $isMobile ? 12 : $isTablet ? 16 : 20,
		maxColumns: $isMobile ? 1 : $isTablet ? 2 : 3
	};

	const sortOptions = [
		{ value: 'created_at', label: $t('common.sort.newest'), order: 'desc' },
		{ value: 'created_at', label: $t('common.sort.oldest'), order: 'asc' },
		{ value: 'monthly_rent', label: $t('common.sort.priceHigh'), order: 'desc' },
		{ value: 'monthly_rent', label: $t('common.sort.priceLow'), order: 'asc' },
		{ value: 'title', label: $t('common.sort.nameAZ'), order: 'asc' },
		{ value: 'title', label: $t('common.sort.nameZA'), order: 'desc' }
	];

	const viewModeOptions = [
		{ value: 'grid', label: $t('common.view.grid'), icon: '⊞' },
		{ value: 'list', label: $t('common.view.list'), icon: '☰' },
		{ value: 'compact', label: $t('common.view.compact'), icon: '▤' }
	];

	onMount(() => {
		loadSavedSearches();
		setupInfiniteScroll();

		return () => {
			if (intersectionObserver) {
				intersectionObserver.disconnect();
			}
		};
	});

	function setupInfiniteScroll() {
		if (!$isMobile) return;

		intersectionObserver = new IntersectionObserver(
			(entries) => {
				if (entries[0].isIntersecting && hasMore && !loadingMore) {
					loadMoreProperties();
				}
			},
			{ threshold: 0.1 }
		);
	}

	function loadSavedSearches() {
		try {
			const saved = localStorage.getItem('saved_property_searches');
			if (saved) {
				savedSearches = JSON.parse(saved);
			}
		} catch (e) {
			console.warn('Failed to load saved searches');
		}
	}

	function saveSearch(searchData) {
		try {
			const newSearch = {
				id: Date.now().toString(),
				name: searchData.name || `Search ${savedSearches.length + 1}`,
				query: searchQuery,
				filters: activeFilters,
				createdAt: new Date().toISOString()
			};

			savedSearches = [newSearch, ...savedSearches.slice(0, 9)]; // Keep max 10
			localStorage.setItem('saved_property_searches', JSON.stringify(savedSearches));

			toast.success($t('search.searchSaved'));
		} catch (e) {
			toast.error($t('search.saveFailed'));
		}
	}

	function loadSavedSearch(search) {
		searchQuery = search.query;
		activeFilters = search.filters;
		showFilterDrawer = false;

		toast.info($t('search.searchLoaded', { name: search.name }));
	}

	function handleSearch(event) {
		const query = event.detail.query;
		searchQuery = query;
		currentPage = 1;

		// Reset pagination for new search
		hasMore = true;

		// Debounced search
		clearTimeout(searchTimeout);
		searchTimeout = setTimeout(() => {
			dispatch('search', { query, filters: activeFilters });
		}, 300);
	}

	function handleFilterChange(event) {
		activeFilters = { ...event.detail };
		currentPage = 1;
		hasMore = true;
		dispatch('filterChange', activeFilters);
	}

	function clearFilters() {
		activeFilters = {};
		searchQuery = '';
		currentPage = 1;
		hasMore = true;
		dispatch('clearFilters');
	}

	function handleSort(sortOption) {
		sortBy = sortOption.value;
		sortOrder = sortOption.order;
		showSortDrawer = false;

		toast.info($t('common.sortApplied'));
	}

	function handleViewModeChange(mode) {
		viewMode = mode;
	}

	function filterAndSortProperties(props, query, filters, sortField, sortDir) {
		if (!props.length) return props;

		let filtered = [...props];

		// Apply search query
		if (query) {
			const searchLower = query.toLowerCase();
			filtered = filtered.filter(
				(prop) =>
					prop.title?.toLowerCase().includes(searchLower) ||
					prop.description?.toLowerCase().includes(searchLower) ||
					prop.location?.toLowerCase().includes(searchLower)
			);
		}

		// Apply filters (basic client-side filtering)
		if (filters.property_type) {
			filtered = filtered.filter((prop) => prop.property_type === filters.property_type);
		}

		if (filters.monthly_rent__gte) {
			filtered = filtered.filter((prop) => prop.monthly_rent >= filters.monthly_rent__gte);
		}

		if (filters.monthly_rent__lte) {
			filtered = filtered.filter((prop) => prop.monthly_rent <= filters.monthly_rent__lte);
		}

		// Apply sorting
		filtered.sort((a, b) => {
			let aVal = a[sortField];
			let bVal = b[sortField];

			if (typeof aVal === 'string') {
				aVal = aVal.toLowerCase();
				bVal = bVal.toLowerCase();
			}

			if (sortDir === 'asc') {
				return aVal > bVal ? 1 : -1;
			} else {
				return aVal < bVal ? 1 : -1;
			}
		});

		return filtered;
	}

	async function loadMoreProperties() {
		if (loadingMore || !hasMore) return;

		loadingMore = true;
		currentPage += 1;

		try {
			// Simulate API call for more properties
			await new Promise((resolve) => setTimeout(resolve, 1000));

			// In real app, this would make an API call
			// const response = await rentalPropertyAPI.getProperties({
			//     page: currentPage,
			//     page_size: pageSize,
			//     search: searchQuery,
			//     ...activeFilters
			// });

			// For demo, stop loading after page 3
			if (currentPage >= 3) {
				hasMore = false;
			}
		} catch (err) {
			toast.error($t('errors.loadingFailed'));
			currentPage -= 1; // Revert page increment
		} finally {
			loadingMore = false;
		}
	}

	function handleCreateProperty() {
		dispatch('create');
	}

	function handlePropertySelect(property) {
		dispatch('select', property);
	}

	function handlePropertyEdit(property) {
		dispatch('edit', property);
	}

	function handlePropertyDelete(property) {
		dispatch('delete', property);
	}

	// Mobile pull-to-refresh simulation
	function handleRefresh() {
		currentPage = 1;
		hasMore = true;
		dispatch('refresh');
		toast.info($t('common.refreshed'));
	}
</script>

<!-- Mobile-First Property List -->
<div class="property-list-mobile">
	<!-- Mobile Header with Search -->
	<div class="mobile-header">
		<FadeInUp>
			<div class="header-content">
				<h1 class="page-title">{$t('property.management.title')}</h1>

				<!-- Search Bar -->
				<SearchBarAdvanced
					placeholder={$t('property.searchPlaceholder')}
					{savedSearches}
					on:search={handleSearch}
					on:saveSearch={saveSearch}
					on:loadSavedSearch={loadSavedSearch}
				/>

				<!-- Mobile Action Bar -->
				<div class="action-bar">
					<!-- Filter Button -->
					<button
						class="action-button"
						class:active={hasActiveFilters}
						on:click={() => (showFilterDrawer = true)}
					>
						<span class="action-icon">🔍</span>
						<span class="action-label">{$t('common.filter')}</span>
						{#if hasActiveFilters}
							<span class="filter-badge">{Object.keys(activeFilters).length}</span>
						{/if}
					</button>

					<!-- Sort Button -->
					<button class="action-button" on:click={() => (showSortDrawer = true)}>
						<span class="action-icon">↕️</span>
						<span class="action-label">{$t('common.sort')}</span>
					</button>

					<!-- View Mode Toggle (Tablet+) -->
					{#if !$isMobile}
						<div class="view-mode-toggle">
							{#each viewModeOptions as option}
								<button
									class="view-button"
									class:active={viewMode === option.value}
									on:click={() => handleViewModeChange(option.value)}
									title={option.label}
								>
									{option.icon}
								</button>
							{/each}
						</div>
					{/if}

					<!-- Create Button -->
					{#if showCreateButton}
						<Button
							variant="primary"
							size={$isMobile ? 'sm' : 'md'}
							on:click={handleCreateProperty}
							className="create-button"
						>
							<span class="flex items-center gap-2">
								<span>+</span>
								{#if !$isMobile}<span>{$t('property.create')}</span>{/if}
							</span>
						</Button>
					{/if}
				</div>
			</div>
		</FadeInUp>
	</div>

	<!-- Error Display -->
	{#if error}
		<FadeInUp delay={100}>
			<div class="px-4">
				<div class="mb-6 rounded-2xl border border-red-200 bg-red-50 p-4">
					<p class="text-sm text-red-700">{error}</p>
				</div>
			</div>
		</FadeInUp>
	{/if}

	<!-- Active Filters Display -->
	{#if hasActiveFilters}
		<FadeInUp delay={200}>
			<div class="active-filters">
				<div class="filter-chips">
					{#if searchQuery}
						<div class="filter-chip">
							<span class="chip-label">"{searchQuery}"</span>
							<button class="chip-remove" on:click={() => (searchQuery = '')}>×</button>
						</div>
					{/if}

					{#each Object.entries(activeFilters) as [key, value]}
						<div class="filter-chip">
							<span class="chip-label">{value}</span>
							<button class="chip-remove" on:click={() => delete activeFilters[key]}>×</button>
						</div>
					{/each}

					<button class="clear-all-button" on:click={clearFilters}>
						{$t('common.clearAll')}
					</button>
				</div>
			</div>
		</FadeInUp>
	{/if}

	<!-- Property Grid -->
	<div class="property-grid-container">
		{#if loading && !filteredProperties.length}
			<div class="loading-container">
				<LoadingSpinner size="lg" variant="spinner" />
			</div>
		{:else if filteredProperties.length === 0}
			<!-- Empty State -->
			<FadeInUp delay={300}>
				<div class="empty-state">
					<div class="empty-icon">🏠</div>
					<h3 class="empty-title">{$t('property.noPropertiesFound')}</h3>
					<p class="empty-description">{$t('property.noPropertiesDescription')}</p>
					{#if hasActiveFilters}
						<Button variant="outline" size="sm" on:click={clearFilters}>
							{$t('common.clearFilters')}
						</Button>
					{/if}
				</div>
			</FadeInUp>
		{:else}
			<!-- Properties List -->
			<ResponsiveGrid
				minItemWidth={gridConfig.minItemWidth}
				gap={gridConfig.gap}
				maxColumns={gridConfig.maxColumns}
				className="properties-grid"
			>
				<StaggeredList staggerDelay={50}>
					{#each filteredProperties as property (property.id)}
						<PropertyCardAdvanced
							{property}
							variant={viewMode}
							on:select={() => handlePropertySelect(property)}
							on:edit={() => handlePropertyEdit(property)}
							on:delete={() => handlePropertyDelete(property)}
						/>
					{/each}
				</StaggeredList>
			</ResponsiveGrid>

			<!-- Infinite Scroll Trigger (Mobile) -->
			{#if $isMobile && hasMore}
				<div bind:this={loadMoreElement} class="load-more-trigger">
					{#if loadingMore}
						<LoadingSpinner size="sm" variant="dots" />
						<p class="loading-text">{$t('common.loadingMore')}</p>
					{/if}
				</div>
			{/if}
		{/if}
	</div>

	<!-- Pull to Refresh Indicator (Mobile) -->
	{#if $isMobile}
		<div class="pull-refresh-hint">
			<p class="refresh-text">{$t('common.pullToRefresh')}</p>
		</div>
	{/if}
</div>

<!-- Filter Drawer -->
<MobileDrawer
	bind:isOpen={showFilterDrawer}
	title={$t('common.filters')}
	position="bottom"
	maxHeight="85vh"
>
	<FilterPanelAdvanced
		{activeFilters}
		on:filterChange={handleFilterChange}
		on:clearFilters={clearFilters}
	/>
</MobileDrawer>

<!-- Sort Drawer -->
<MobileDrawer
	bind:isOpen={showSortDrawer}
	title={$t('common.sortBy')}
	position="bottom"
	maxHeight="50vh"
>
	<div class="sort-options">
		{#each sortOptions as option}
			<button
				class="sort-option"
				class:active={sortBy === option.value && sortOrder === option.order}
				on:click={() => handleSort(option)}
			>
				<span class="sort-label">{option.label}</span>
				{#if sortBy === option.value && sortOrder === option.order}
					<span class="sort-check">✓</span>
				{/if}
			</button>
		{/each}
	</div>
</MobileDrawer>

<style>
	.property-list-mobile {
		min-height: 100vh;
		background: #f8fafc;
	}

	.mobile-header {
		background: white;
		border-bottom: 1px solid #e2e8f0;
		position: sticky;
		top: 0;
		z-index: 10;
	}

	.header-content {
		padding: 1rem;
		space-y: 1rem;
	}

	.page-title {
		font-size: 1.75rem;
		font-weight: 700;
		color: #1e293b;
		margin-bottom: 1rem;
	}

	.action-bar {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		margin-top: 1rem;
		flex-wrap: wrap;
	}

	.action-button {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.5rem 0.75rem;
		background: #f1f5f9;
		border: 1px solid #e2e8f0;
		border-radius: 0.75rem;
		color: #475569;
		font-size: 0.875rem;
		font-weight: 500;
		transition: all 200ms;
		position: relative;
	}

	.action-button:hover {
		background: #e2e8f0;
		border-color: #cbd5e1;
	}

	.action-button.active {
		background: #dbeafe;
		border-color: #3b82f6;
		color: #1d4ed8;
	}

	.action-icon {
		font-size: 1rem;
	}

	.filter-badge {
		position: absolute;
		top: -0.25rem;
		right: -0.25rem;
		background: #ef4444;
		color: white;
		font-size: 0.75rem;
		padding: 0.125rem 0.375rem;
		border-radius: 0.5rem;
		min-width: 1.25rem;
		text-align: center;
	}

	.view-mode-toggle {
		display: flex;
		background: #f1f5f9;
		border-radius: 0.5rem;
		padding: 0.25rem;
		border: 1px solid #e2e8f0;
	}

	.view-button {
		padding: 0.375rem 0.5rem;
		border: none;
		background: transparent;
		border-radius: 0.375rem;
		color: #64748b;
		transition: all 200ms;
	}

	.view-button.active {
		background: white;
		color: #3b82f6;
		box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
	}

	.active-filters {
		padding: 0 1rem;
		margin-bottom: 1rem;
	}

	.filter-chips {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
		align-items: center;
	}

	.filter-chip {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		background: #dbeafe;
		color: #1e40af;
		padding: 0.375rem 0.75rem;
		border-radius: 1rem;
		font-size: 0.875rem;
	}

	.chip-remove {
		background: none;
		border: none;
		color: #1e40af;
		font-size: 1.25rem;
		line-height: 1;
		cursor: pointer;
		padding: 0;
		width: 1.25rem;
		height: 1.25rem;
		display: flex;
		align-items: center;
		justify-content: center;
		border-radius: 50%;
	}

	.chip-remove:hover {
		background: rgba(30, 64, 175, 0.1);
	}

	.clear-all-button {
		background: #fee2e2;
		color: #dc2626;
		border: none;
		padding: 0.375rem 0.75rem;
		border-radius: 1rem;
		font-size: 0.875rem;
		font-weight: 500;
		cursor: pointer;
		transition: background 200ms;
	}

	.clear-all-button:hover {
		background: #fecaca;
	}

	.property-grid-container {
		padding: 1rem;
	}

	.loading-container {
		display: flex;
		justify-content: center;
		padding: 3rem 0;
	}

	.empty-state {
		text-align: center;
		padding: 3rem 1rem;
	}

	.empty-icon {
		font-size: 4rem;
		margin-bottom: 1rem;
	}

	.empty-title {
		font-size: 1.5rem;
		font-weight: 600;
		color: #374151;
		margin-bottom: 0.5rem;
	}

	.empty-description {
		color: #6b7280;
		margin-bottom: 2rem;
		max-width: 24rem;
		margin-left: auto;
		margin-right: auto;
	}

	.load-more-trigger {
		display: flex;
		flex-direction: column;
		align-items: center;
		padding: 2rem 0;
		gap: 0.5rem;
	}

	.loading-text {
		color: #6b7280;
		font-size: 0.875rem;
	}

	.pull-refresh-hint {
		position: fixed;
		bottom: 1rem;
		left: 50%;
		transform: translateX(-50%);
		background: rgba(0, 0, 0, 0.7);
		color: white;
		padding: 0.5rem 1rem;
		border-radius: 1rem;
		font-size: 0.75rem;
		pointer-events: none;
		opacity: 0.7;
	}

	.sort-options {
		padding: 0.5rem 0;
	}

	.sort-option {
		display: flex;
		align-items: center;
		justify-content: space-between;
		width: 100%;
		padding: 1rem;
		border: none;
		background: none;
		text-align: left;
		cursor: pointer;
		transition: background 200ms;
	}

	.sort-option:hover {
		background: #f8fafc;
	}

	.sort-option.active {
		background: #dbeafe;
		color: #1d4ed8;
	}

	.sort-label {
		font-weight: 500;
	}

	.sort-check {
		color: #10b981;
		font-weight: bold;
	}

	/* Responsive adjustments */
	@media (max-width: 640px) {
		.page-title {
			font-size: 1.5rem;
		}

		.action-bar {
			gap: 0.5rem;
		}

		.action-button {
			font-size: 0.8125rem;
			padding: 0.375rem 0.625rem;
		}

		.create-button {
			margin-left: auto;
		}
	}

	@media (min-width: 768px) {
		.mobile-header {
			position: static;
		}

		.pull-refresh-hint {
			display: none;
		}
	}

	/* Dark mode support */
	@media (prefers-color-scheme: dark) {
		.property-list-mobile {
			background: #0f172a;
		}

		.mobile-header {
			background: #1e293b;
			border-bottom-color: #334155;
		}

		.page-title {
			color: #f1f5f9;
		}

		.action-button {
			background: #334155;
			border-color: #475569;
			color: #cbd5e1;
		}

		.action-button:hover {
			background: #475569;
		}

		.empty-title {
			color: #f9fafb;
		}

		.empty-description {
			color: #9ca3af;
		}
	}
</style>
