<!-- src/routes/properties/+page.svelte -->
<script>
	import { onMount, onDestroy } from 'svelte';
	import { fade, slide, fly } from 'svelte/transition';
	import { t, locale } from '$lib/i18n';
	import { user } from '$lib/stores/user.svelte.js';
	import { getProperties } from '$lib/api/property';
	import { properties as propertiesStore } from '$lib/stores/properties.svelte.js';

	// Components
	import PropertyCard from '$lib/components/properties/PropertyCard.svelte';
	import PropertySearch from '$lib/components/properties/PropertySearch.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import LoadingSkeleton from '$lib/components/ui/LoadingSkeleton.svelte';
	import EmptyState from '$lib/components/ui/EmptyState.svelte';

	// State using Svelte 5 runes
	let properties = $state([]);
	let loading = $state(true);
	let error = $state(null);
	let currentPage = $state(1);
	let totalPages = $state(1);
	let totalCount = $state(0);
	let loadingMore = $state(false);
	let debounceTimer;
	let showMobileFilters = $state(false);

	// Search parameters using $state
	let searchParams = $state({
		query: '',
		propertyType: '',
		minPrice: '',
		maxPrice: '',
		city: '',
		minSize: '',
		maxSize: '',
		sort: 'newest'
	});

	// Computed value for RTL mode
	let isRTL = $derived($locale === 'ar');

	// Check permissions for creating properties
	let canCreateProperty = $derived(
		$user &&
			($user.role === 'owner' || $user.role === 'appraiser' || $user.is_staff || $user.is_superuser)
	);

	// Display all loaded properties
	let displayedProperties = $derived(properties);

	// Calculate statistics
	let featuredCount = $derived(properties.filter((p) => p.is_featured).length);
	let averagePrice = $derived(
		properties.length > 0
			? properties.reduce((sum, p) => sum + (p.market_value || 0), 0) / properties.length
			: 0
	);

	// Format currency
	function formatCurrency(value) {
		if (!value) return '$0';
		return new Intl.NumberFormat($locale === 'ar' ? 'ar-SA' : 'en-US', {
			style: 'currency',
			currency: $locale === 'ar' ? 'SAR' : 'USD',
			maximumFractionDigits: 0
		}).format(value);
	}

	// Convert search params to API params
	function getApiParams() {
		const params = {
			page: currentPage
		};

		// Add filters that have values
		if (searchParams.query) params.search = searchParams.query;
		if (searchParams.propertyType) params.property_type = searchParams.propertyType;
		if (searchParams.city) params.city = searchParams.city;

		if (searchParams.minPrice) params.min_price = searchParams.minPrice;
		if (searchParams.maxPrice) params.max_price = searchParams.maxPrice;
		if (searchParams.minSize) params.min_size = searchParams.minSize;
		if (searchParams.maxSize) params.max_size = searchParams.maxSize;

		// Handle sort ordering
		switch (searchParams.sort) {
			case 'newest':
				params.ordering = '-created_at';
				break;
			case 'priceAsc':
				params.ordering = 'market_value';
				break;
			case 'priceDesc':
				params.ordering = '-market_value';
				break;
			case 'sizeAsc':
				params.ordering = 'size_sqm';
				break;
			case 'sizeDesc':
				params.ordering = '-size_sqm';
				break;
			default:
				params.ordering = '-created_at';
		}

		return params;
	}

	// Handle search submission (using PropertySearch component approach)
	async function handleSearch(event) {
		if (event) {
			searchParams = event.detail;
		}
		currentPage = 1; // Reset to first page on new search
		await loadProperties();
	}

	// Load properties
	async function loadProperties(reset = true) {
		try {
			if (reset) {
				loading = true;
				currentPage = 1;
			} else {
				loadingMore = true;
			}

			error = null;
			const apiParams = getApiParams();
			const response = await getProperties(apiParams);

			if (response.results) {
				if (reset) {
					properties = response.results;
				} else {
					properties = [...properties, ...response.results];
				}
				totalCount = response.count || 0;
				totalPages = Math.ceil(response.count / (response.page_size || 10));
			} else if (Array.isArray(response)) {
				if (reset) {
					properties = response;
				} else {
					properties = [...properties, ...response];
				}
				totalCount = response.length;
				totalPages = 1;
			} else {
				const results = response.data?.results || [];
				if (reset) {
					properties = results;
				} else {
					properties = [...properties, ...results];
				}
				totalCount = response.data?.count || results.length;
				totalPages = Math.ceil(
					(response.data?.count || results.length) / (response.data?.page_size || 10)
				);
			}

			propertiesStore.set(properties);
		} catch (err) {
			// console.error('Error loading properties:', err);
			error = err.message || $t('error.fetchFailed');
			properties = [];
		} finally {
			loading = false;
			loadingMore = false;
		}
	}

	// Load more properties
	function loadMore() {
		if (currentPage < totalPages && !loadingMore) {
			currentPage++;
			loadProperties(false);
		}
	}

	// Toggle mobile filters
	function toggleMobileFilters() {
		showMobileFilters = !showMobileFilters;
		document.body.style.overflow = showMobileFilters ? 'hidden' : '';
	}

	// Cleanup on component destroy
	onDestroy(() => {
		clearTimeout(debounceTimer);
		document.body.style.overflow = '';
	});

	// Initial load
	onMount(() => {
		loadProperties();
	});
</script>

<svelte:head>
	<title>{$t('properties.title')} | {$t('app.name')}</title>
	<meta name="description" content={$t('properties.subtitle')} />
</svelte:head>

<div class="min-h-screen bg-gray-50 dark:bg-gray-900">
	<!-- Enhanced Hero Section with Stats -->
	<div
		class="from-primary-600 via-primary-700 to-secondary-700 relative bg-gradient-to-br text-white"
	>
		<div class="absolute inset-0 bg-black/20"></div>
		<div class="relative mx-auto max-w-7xl px-4 py-8 sm:px-6 md:py-12 lg:px-8">
			<div class="md:flex md:items-center md:justify-between">
				<div>
					<h1 class="flex items-center text-3xl font-bold md:text-4xl">
						{$t('properties.title')}
						{#if featuredCount > 0}
							<span
								class="ml-3 inline-flex items-center rounded-full bg-yellow-500 px-3 py-1 text-sm font-medium text-white"
							>
								<span class="mr-2 h-2 w-2 rounded-full bg-white"></span>
								{featuredCount} Featured
							</span>
						{/if}
					</h1>
					<p class="mt-2 max-w-2xl text-base text-white/90 md:text-lg">
						{$t('properties.subtitle')}
					</p>

					<!-- Live Stats Bar -->
					{#if totalCount > 0}
						<div class="mt-4 flex flex-wrap gap-4">
							<div class="rounded-lg bg-white/10 px-4 py-2 backdrop-blur-sm">
								<p class="text-xs text-white/70">{$t('properties.totalProperties')}</p>
								<p class="text-xl font-bold">{totalCount}</p>
							</div>
							<div class="rounded-lg bg-white/10 px-4 py-2 backdrop-blur-sm">
								<p class="text-xs text-white/70">{$t('properties.averagePrice')}</p>
								<p class="text-xl font-bold">{formatCurrency(averagePrice)}</p>
							</div>
							<div class="rounded-lg bg-white/10 px-4 py-2 backdrop-blur-sm">
								<p class="text-xs text-white/70">{$t('property.featured')}</p>
								<p class="text-xl font-bold">{featuredCount}</p>
							</div>
						</div>
					{/if}
				</div>

				<!-- Create Property Button -->
				{#if canCreateProperty}
					<div class="mt-6 md:mt-0">
						<a
							href="/properties/create"
							class="text-primary-600 inline-flex transform items-center rounded-full border border-transparent bg-white px-6 py-3 text-base font-medium shadow-lg transition-all duration-300 hover:-translate-y-0.5 hover:bg-gray-50 hover:shadow-xl focus:ring-2 focus:ring-white focus:ring-offset-2 focus:outline-none"
						>
							<svg
								class="h-5 w-5 {isRTL ? 'ml-2' : 'mr-2'}"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M12 6v6m0 0v6m0-6h6m-6 0H6"
								/>
							</svg>
							{$t('property.createProperty')}
						</a>
					</div>
				{/if}
			</div>

			<!-- Mobile Filter Toggle -->
			<div class="mt-6 md:hidden">
				<button
					type="button"
					onclick={toggleMobileFilters}
					class="flex items-center justify-center rounded-full border border-white/30 bg-white/20 px-4 py-2 text-sm font-medium text-white shadow-sm backdrop-blur-sm transition-colors hover:bg-white/30"
				>
					<svg
						class="h-4 w-4 {isRTL ? 'ml-2' : 'mr-2'}"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12"
						/>
					</svg>
					<span>{$t('search.advancedFilters')}</span>
				</button>
			</div>
		</div>
	</div>

	<!-- Main Content Area -->
	<div class="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
		<!-- Search Filters - Desktop (Using PropertySearch component) -->
		<div class="mb-8 hidden md:block">
			<PropertySearch {searchParams} onsearch={handleSearch} />
		</div>

		<!-- Content Area -->
		{#if loading && !properties.length}
			<!-- Loading Skeleton - Only 3 cards -->
			<div in:fade={{ duration: 200 }} out:fade={{ duration: 150 }}>
				<div class="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-3">
					{#each Array(3) as _, i}
						<LoadingSkeleton type="propertyCard" />
					{/each}
				</div>
			</div>
		{:else if error}
			<!-- Error State -->
			<div
				class="mx-auto max-w-2xl rounded-xl bg-white p-8 shadow-lg dark:bg-gray-800"
				in:fly={{ y: 20, duration: 300 }}
				out:fade={{ duration: 200 }}
			>
				<div class="flex items-start {isRTL ? 'space-x-reverse' : ''} space-x-5">
					<div class="flex-shrink-0 rounded-full bg-red-100 p-3 dark:bg-red-900/30">
						<svg
							class="h-8 w-8 text-red-600 dark:text-red-400"
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
					</div>
					<div>
						<h3 class="text-xl font-bold text-gray-900 dark:text-white">{$t('error.title')}</h3>
						<p class="mt-2 text-base text-gray-600 dark:text-gray-300">{error}</p>

						<div class="mt-6 flex flex-wrap gap-3">
							<Button
								variant="outline"
								onclick={() => {
									searchParams = {
										query: '',
										propertyType: '',
										minPrice: '',
										maxPrice: '',
										city: '',
										minSize: '',
										maxSize: '',
										sort: 'newest'
									};
									handleSearch();
								}}
								size="default"
								class="w-full sm:w-auto"
							>
								<svg
									class="h-4 w-4 {isRTL ? 'ml-2' : 'mr-2'}"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M6 18L18 6M6 6l12 12"
									/>
								</svg>
								{$t('search.clear')}
							</Button>

							<Button
								variant="primary"
								onclick={() => loadProperties()}
								size="default"
								class="w-full sm:w-auto"
							>
								<svg
									class="h-4 w-4 {isRTL ? 'ml-2' : 'mr-2'}"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
									/>
								</svg>
								{$t('common.tryAgain')}
							</Button>
						</div>
					</div>
				</div>
			</div>
		{:else if !displayedProperties.length}
			<!-- Empty State -->
			<div in:fade={{ duration: 300 }} out:fade={{ duration: 200 }}>
				<EmptyState
					icon="property"
					title={$t('properties.noResults')}
					description={$t('properties.tryAdjusting')}
					actionLabel={$t('properties.backToProperties')}
					actionUrl="/properties"
				/>
			</div>
		{:else}
			<!-- Properties Grid - Only 3 Bigger Cards with Updated Responsive Layout -->
			<div class="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-3">
				{#each displayedProperties as property, index (property.id)}
					<div
						in:fly={{ y: 20, duration: 300, delay: 50 * (index % 3) }}
						out:fade={{ duration: 200 }}
					>
						<PropertyCard {property} />
					</div>
				{/each}
			</div>

			<!-- Load More Button -->
			{#if currentPage < totalPages && !loadingMore}
				<div class="mt-10 flex justify-center">
					<Button
						variant="outline"
						onclick={loadMore}
						size="large"
						class="rounded-full px-8 py-3 transition-all hover:bg-gray-50 dark:hover:bg-gray-700"
					>
						<div class="flex items-center">
							<span
								>{$t('properties.viewMore')} ({totalCount - properties.length}
								{$t('properties.more')})</span
							>
							<svg
								class="{isRTL ? 'mr-2' : 'ml-2'} h-4 w-4"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M19 9l-7 7-7-7"
								/>
							</svg>
						</div>
					</Button>
				</div>
			{/if}

			<!-- Loading More Indicator -->
			{#if loadingMore}
				<div class="mt-10 flex justify-center">
					<div
						class="flex items-center justify-center {isRTL
							? 'space-x-reverse'
							: ''} text-primary-600 dark:text-primary-400 space-x-2"
					>
						<div
							class="bg-primary-600 dark:bg-primary-400 h-3 w-3 animate-bounce rounded-full"
						></div>
						<div
							class="bg-primary-600 dark:bg-primary-400 h-3 w-3 animate-bounce rounded-full delay-150"
						></div>
						<div
							class="bg-primary-600 dark:bg-primary-400 h-3 w-3 animate-bounce rounded-full delay-300"
						></div>
						<span class="{isRTL ? 'mr-2' : 'ml-2'} text-sm font-medium">{$t('common.loading')}</span
						>
					</div>
				</div>
			{/if}
		{/if}

		<!-- Create Property Info Box for Non-Authorized Users -->
		{#if !canCreateProperty && !loading && displayedProperties.length > 0 && $user}
			<div
				class="mt-10 rounded-xl border border-gray-200 bg-white p-6 shadow-md dark:border-gray-700 dark:bg-gray-800"
			>
				<div class="sm:flex sm:items-center sm:justify-between">
					<div class="max-w-md">
						<h3 class="text-lg font-semibold text-gray-900 dark:text-white">
							{$t('auction.createNewPrompt')}
						</h3>
						<p class="mt-2 text-sm text-gray-600 dark:text-gray-300">
							{$t('property.unauthorizedMessage')}
						</p>
					</div>
					<div class="mt-4 sm:mt-0 sm:ml-4">
						<Button
							href="/properties"
							variant="primary"
							size="default"
							class="w-full shadow-md transition-all hover:shadow-lg sm:w-auto"
						>
							<div class="flex items-center">
								<svg
									class="h-4 w-4 {isRTL ? 'ml-2' : 'mr-2'}"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
									/>
								</svg>
								{$t('properties.backToProperties')}
							</div>
						</Button>
					</div>
				</div>
			</div>
		{/if}
	</div>

	<!-- Mobile Filters Drawer -->
	{#if showMobileFilters}
		<div
			class="fixed inset-0 z-40 flex md:hidden"
			in:fade={{ duration: 200 }}
			out:fade={{ duration: 150 }}
		>
			<!-- Backdrop -->
			<div
				class="bg-opacity-50 fixed inset-0 bg-black backdrop-blur-sm"
				onclick={toggleMobileFilters}
				onkeydown={(e) => {
					if (e.key === 'Enter' || e.key === ' ') toggleMobileFilters();
				}}
				role="button"
				tabindex="0"
				aria-label="Close filter panel"
			></div>

			<!-- Drawer panel -->
			<div
				class="scrollbar-hide relative flex h-full w-full max-w-xs flex-col overflow-y-auto bg-white shadow-2xl dark:bg-gray-800 {isRTL
					? 'right-0'
					: 'left-0'}"
				in:slide={{ duration: 300, axis: 'x' }}
				out:slide={{ duration: 250, axis: 'x', easing: (x) => 1 - Math.pow(1 - x, 3) }}
			>
				<div
					class="flex items-center justify-between border-b border-gray-200 px-4 py-5 dark:border-gray-700"
				>
					<h2 class="flex items-center text-lg font-semibold text-gray-900 dark:text-white">
						<svg
							class="h-5 w-5 {isRTL ? 'ml-2' : 'mr-2'}"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12"
							/>
						</svg>
						{$t('search.advancedFilters')}
					</h2>
					<button
						type="button"
						class="rounded-full p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-500 dark:text-gray-300 dark:hover:bg-gray-700 dark:hover:text-white"
						onclick={toggleMobileFilters}
						aria-label="Close filter panel"
					>
						<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M6 18L18 6M6 6l12 12"
							/>
						</svg>
					</button>
				</div>

				<!-- Mobile Search Component (Using PropertySearch component) -->
				<div class="flex-1 p-4">
					<PropertySearch
						{searchParams}
						onsearch={(e) => {
							handleSearch(e);
							toggleMobileFilters();
						}}
					/>
				</div>
			</div>
		</div>
	{/if}
</div>

<style>
	/* Scrollbar styling */
	.scrollbar-hide {
		-ms-overflow-style: none;
		scrollbar-width: none;
	}

	.scrollbar-hide::-webkit-scrollbar {
		display: none;
	}
</style>
