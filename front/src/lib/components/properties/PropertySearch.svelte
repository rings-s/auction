<!-- PropertySearch.svelte - Advanced property search component with filters -->
<script>
	import { createEventDispatcher } from 'svelte';
	import { t, locale } from '$lib/i18n';
	import { fade, fly } from 'svelte/transition';
	import { clickOutside } from '$lib/actions/clickOutside';

	// Default search parameters
	export let searchParams = {
		query: '',
		propertyType: '',
		minPrice: '',
		maxPrice: '',
		city: '',
		minSize: '',
		maxSize: '',
		sort: 'newest'
	};

	const dispatch = createEventDispatcher();

	// Property types with i18n support
	const propertyTypes = [
		{ value: 'residential', label: 'nav.propertyTypes.residential' },
		{ value: 'commercial', label: 'nav.propertyTypes.commercial' },
		{ value: 'land', label: 'nav.propertyTypes.land' },
		{ value: 'industrial', label: 'nav.propertyTypes.industrial' },
		{ value: 'mixed_use', label: 'nav.propertyTypes.mixedUse' }
	];

	// Sort options
	const sortOptions = [
		{ value: 'newest', label: 'search.sortOptions.newest' },
		{ value: 'priceAsc', label: 'search.sortOptions.priceAsc' },
		{ value: 'priceDesc', label: 'search.sortOptions.priceDesc' },
		{ value: 'sizeAsc', label: 'search.sortOptions.sizeAsc' },
		{ value: 'sizeDesc', label: 'search.sortOptions.sizeDesc' }
	];

	// Handle search submission
	function handleSearch() {
		dispatch('search', searchParams);
	}

	// Clear all filters
	function clearFilters() {
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
		dispatch('search', searchParams);
	}

	// Dropdown management
	let showFilterDropdown = { sort: false, price: false, type: false, size: false };
	let showMobileFilters = false; // For mobile view toggle

	// Toggle dropdown visibility
	function toggleDropdown(name) {
		showFilterDropdown = Object.keys(showFilterDropdown).reduce((acc, key) => {
			acc[key] = key === name ? !showFilterDropdown[key] : false;
			return acc;
		}, {});
	}

	// Close all dropdowns when clicking outside
	function handleClickOutside() {
		showFilterDropdown = Object.keys(showFilterDropdown).reduce((acc, key) => {
			acc[key] = false;
			return acc;
		}, {});
	}

	// Toggle mobile filters visibility
	function toggleMobileFilters() {
		showMobileFilters = !showMobileFilters;
	}

	// Computed value for RTL mode
	$: isRTL = $locale === 'ar';

	// Calculate active filters count
	$: activeFiltersCount = [
		searchParams.query,
		searchParams.propertyType,
		searchParams.city,
		searchParams.minPrice,
		searchParams.maxPrice,
		searchParams.minSize,
		searchParams.maxSize,
		searchParams.sort !== 'newest' ? searchParams.sort : ''
	].filter(Boolean).length;

	// Format price for display
	function formatPrice(value) {
		if (!value) return '0';
		return new Intl.NumberFormat().format(Number(value));
	}

	// Initialize debounce for search inputs
	let searchTimeout;
	function debounceSearch(delay = 500) {
		clearTimeout(searchTimeout);
		searchTimeout = setTimeout(() => {
			handleSearch();
		}, delay);
	}
</script>

<div
	class="search-container rounded-xl bg-white shadow-lg transition-all duration-300 hover:shadow-xl dark:bg-gray-800"
>
	<div use:clickOutside on:clickoutside={handleClickOutside} class="relative">
		<div class="p-6 md:p-8">
			<form on:submit|preventDefault={handleSearch} class="space-y-6">
				<!-- Main Search Area: Keyword search and primary filters -->
				<div class="grid grid-cols-1 gap-4 md:grid-cols-12">
					<!-- Keyword Search -->
					<div class="md:col-span-5">
						<div class="relative">
							<div
								class="absolute inset-y-0 {isRTL
									? 'right-0 pr-4'
									: 'left-0 pl-4'} pointer-events-none flex items-center"
							>
								<svg
									class="h-5 w-5 text-gray-400"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
									/>
								</svg>
							</div>
							<input
								type="text"
								bind:value={searchParams.query}
								on:input={() => debounceSearch()}
								placeholder={$t('search.keywordPlaceholder')}
								class="block w-full {isRTL
									? 'pr-12'
									: 'pl-12'} focus:border-primary-400 focus:ring-primary-200 focus:ring-opacity-50 rounded-full border-gray-200 py-3 text-sm shadow-sm transition-all focus:ring dark:border-gray-600 dark:bg-gray-700 dark:text-white"
								aria-label={$t('search.keyword')}
							/>
							{#if searchParams.query}
								<button
									type="button"
									class="absolute inset-y-0 {isRTL
										? 'left-0 pl-4'
										: 'right-0 pr-4'} flex items-center text-gray-400 transition-colors hover:text-gray-600 dark:hover:text-gray-300"
									on:click={() => {
										searchParams.query = '';
										debounceSearch(0);
									}}
									aria-label={$t('search.removeFilter')}
								>
									<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M6 18L18 6M6 6l12 12"
										/>
									</svg>
								</button>
							{/if}
						</div>
					</div>

					<!-- Property Type Dropdown -->
					<div class="relative md:col-span-3">
						<button
							type="button"
							on:click={() => toggleDropdown('type')}
							class="relative inline-flex min-h-[44px]
                  w-full transform cursor-pointer
                  items-center
                  justify-center gap-2 overflow-hidden
                  rounded-xl border-0 bg-gradient-to-b
                  from-blue-500
                  to-blue-600 px-4 py-2.5
                  text-sm leading-tight
                  font-semibold
                  font-semibold tracking-wide text-white
                  shadow-sm transition-all
                  duration-200 ease-out
                  select-none hover:-translate-y-0.5
                  hover:scale-[1.02] hover:from-blue-600 hover:to-blue-700
                  hover:shadow-md focus:ring-2 focus:ring-blue-500/40
                  focus:ring-offset-2 focus:outline-none
                  active:translate-y-0 active:scale-[0.98]
                  active:from-blue-700
                  active:to-blue-800 active:shadow-sm dark:from-blue-600
                  dark:to-blue-700 dark:hover:from-blue-700
                  dark:hover:to-blue-800"
							aria-haspopup="true"
							aria-expanded={showFilterDropdown.type}
						>
							<div
								aria-hidden="true"
								class="absolute inset-0 rounded-xl bg-gradient-to-b from-white/20 to-transparent opacity-0 transition-opacity duration-200 hover:opacity-100"
							></div>
							<div class="gap-inherit relative z-10 flex items-center justify-center">
								<span class="truncate"
									>{searchParams.propertyType
										? $t(
												propertyTypes.find((type) => type.value === searchParams.propertyType)
													?.label
											)
										: $t('search.propertyType')}</span
								>
								<svg
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
									class="-mr-1 ml-2 h-5 w-5 text-gray-400 transition-all duration-300 group-hover:text-blue-600 dark:group-hover:text-blue-400"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M19 9l-7 7-7-7"
									/>
								</svg>
							</div>
						</button>

						{#if showFilterDropdown.type}
							<div
								class="absolute {isRTL
									? 'right-0'
									: 'left-0'} ring-opacity-5 z-10 mt-3 w-full overflow-hidden rounded-xl bg-white shadow-xl ring-1 ring-black focus:outline-none dark:bg-gray-800"
								transition:fade={{ duration: 200 }}
							>
								<div class="py-2">
									<button
										type="button"
										class="w-full px-5 py-2.5 text-start text-sm {!searchParams.propertyType
											? 'bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300 font-medium'
											: 'text-gray-700 hover:bg-gray-50 dark:text-gray-200 dark:hover:bg-gray-700'} transition-colors"
										on:click={() => {
											searchParams.propertyType = '';
											toggleDropdown('type');
											handleSearch();
										}}
									>
										{$t('search.allPropertyTypes')}
									</button>
									{#each propertyTypes as type}
										<button
											type="button"
											class="w-full px-5 py-2.5 text-start text-sm {searchParams.propertyType ===
											type.value
												? 'bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300 font-medium'
												: 'text-gray-700 hover:bg-gray-50 dark:text-gray-200 dark:hover:bg-gray-700'} transition-colors"
											on:click={() => {
												searchParams.propertyType = type.value;
												toggleDropdown('type');
												handleSearch();
											}}
										>
											{$t(type.label)}
										</button>
									{/each}
								</div>
							</div>
						{/if}
					</div>

					<!-- City Input -->
					<div class="md:col-span-2">
						<div class="relative">
							<input
								type="text"
								bind:value={searchParams.city}
								on:input={() => debounceSearch()}
								placeholder={$t('search.cityPlaceholder')}
								class="focus:border-primary-400 focus:ring-primary-200 focus:ring-opacity-50 block w-full rounded-full border-gray-200 px-4 py-3 text-sm shadow-sm transition-all focus:ring dark:border-gray-600 dark:bg-gray-700 dark:text-white"
								aria-label={$t('search.city')}
							/>
							{#if searchParams.city}
								<button
									type="button"
									class="absolute inset-y-0 {isRTL
										? 'left-0 pl-4'
										: 'right-0 pr-4'} flex items-center text-gray-400 transition-colors hover:text-gray-600 dark:hover:text-gray-300"
									on:click={() => {
										searchParams.city = '';
										debounceSearch(0);
									}}
									aria-label={$t('search.removeFilter')}
								>
									<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M6 18L18 6M6 6l12 12"
										/>
									</svg>
								</button>
							{/if}
						</div>
					</div>

					<!-- Search Button -->
					<div class="md:col-span-2">
						<button
							type="submit"
							class="bg-primary-600 hover:bg-primary-700 focus:ring-primary-500 inline-flex w-full transform items-center justify-center rounded-full border border-transparent px-5 py-3 text-sm font-medium text-white shadow-md transition-all hover:scale-[1.02] focus:ring-2 focus:ring-offset-2 focus:outline-none active:scale-[0.98]"
						>
							<svg
								class="h-5 w-5 {isRTL ? '-mr-1 ml-1.5' : 'mr-1.5 -ml-1'}"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
								/>
							</svg>
							{$t('search.search')}
						</button>
					</div>
				</div>

				<!-- Mobile Toggle Button (visible only on small screens) -->
				<div class="mb-2 md:hidden">
					<button
						type="button"
						on:click={toggleMobileFilters}
						class="flex w-full items-center justify-between rounded-full border border-gray-200 bg-gray-50 px-4 py-3 text-sm font-medium transition-colors hover:bg-gray-100 dark:border-gray-600 dark:bg-gray-700 dark:hover:bg-gray-600"
					>
						<span class="flex items-center">
							<svg
								class="h-5 w-5 text-gray-500 dark:text-gray-300 {isRTL ? 'ml-2' : 'mr-2'}"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"
								/>
							</svg>
							{$t('search.advancedFilters')}
							{activeFiltersCount > 0 ? `(${activeFiltersCount})` : ''}
						</span>
						<svg
							class="h-5 w-5 transform text-gray-500 transition-transform duration-200 dark:text-gray-300 {showMobileFilters
								? 'rotate-180'
								: ''}"
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
					</button>
				</div>

				<!-- Advanced Filters (Collapsible) -->
				<div
					class="grid grid-cols-1 gap-4 md:grid-cols-12 {!showMobileFilters
						? 'hidden md:grid'
						: ''}"
				>
					<!-- Price Range -->
					<div class="relative md:col-span-4">
						<button
							type="button"
							on:click={() => toggleDropdown('price')}
							class="inline-flex w-full items-center justify-between rounded-full border border-gray-200 bg-white px-5 py-3 text-sm font-medium text-gray-700 shadow-sm transition-all hover:bg-gray-50 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100 dark:hover:bg-gray-600 {searchParams.minPrice ||
							searchParams.maxPrice
								? 'border-primary-300 dark:border-primary-600 ring-primary-100 dark:ring-primary-900 ring-2'
								: ''}"
						>
							<span class="flex items-center">
								<svg
									class="h-5 w-5 text-gray-400 {isRTL ? 'ml-2' : 'mr-2'}"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
									/>
								</svg>
								{#if searchParams.minPrice || searchParams.maxPrice}
									${formatPrice(searchParams.minPrice) || '0'} - ${searchParams.maxPrice
										? formatPrice(searchParams.maxPrice)
										: '∞'}
								{:else}
									{$t('search.price')}
								{/if}
							</span>
							<svg
								class="h-5 w-5 text-gray-400"
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
						</button>

						{#if showFilterDropdown.price}
							<div
								class="absolute {isRTL
									? 'right-0'
									: 'left-0'} ring-opacity-5 z-10 mt-3 w-72 rounded-xl bg-white p-5 shadow-xl ring-1 ring-black focus:outline-none dark:bg-gray-800"
								transition:fade={{ duration: 200 }}
							>
								<div class="space-y-4">
									<!-- Min Price -->
									<div>
										<label
											for="min-price"
											class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300"
										>
											{$t('search.min')}
										</label>
										<div class="relative">
											<div
												class="absolute inset-y-0 {isRTL
													? 'right-0 pr-3'
													: 'left-0 pl-3'} pointer-events-none flex items-center"
											>
												<span class="text-gray-500 sm:text-sm dark:text-gray-400">$</span>
											</div>
											<input
												id="min-price"
												type="number"
												bind:value={searchParams.minPrice}
												placeholder="0"
												class="block w-full {isRTL
													? 'pr-8'
													: 'pl-8'} focus:ring-primary-500 focus:border-primary-500 rounded-lg border border-gray-200 py-2.5 text-sm placeholder-gray-400 transition-all focus:outline-none dark:border-gray-600 dark:bg-gray-700 dark:text-white"
												min="0"
											/>
										</div>
									</div>

									<!-- Max Price -->
									<div>
										<label
											for="max-price"
											class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300"
										>
											{$t('search.max')}
										</label>
										<div class="relative">
											<div
												class="absolute inset-y-0 {isRTL
													? 'right-0 pr-3'
													: 'left-0 pl-3'} pointer-events-none flex items-center"
											>
												<span class="text-gray-500 sm:text-sm dark:text-gray-400">$</span>
											</div>
											<input
												id="max-price"
												type="number"
												bind:value={searchParams.maxPrice}
												placeholder="100000"
												class="block w-full {isRTL
													? 'pr-8'
													: 'pl-8'} focus:ring-primary-500 focus:border-primary-500 rounded-lg border border-gray-200 py-2.5 text-sm placeholder-gray-400 transition-all focus:outline-none dark:border-gray-600 dark:bg-gray-700 dark:text-white"
												min="0"
											/>
										</div>
									</div>

									<!-- Apply Button -->
									<button
										type="button"
										class="bg-primary-600 hover:bg-primary-700 mt-3 w-full transform rounded-lg px-4 py-2.5 text-sm font-medium text-white transition-all hover:scale-[1.02] active:scale-[0.98]"
										on:click={() => {
											toggleDropdown('price');
											handleSearch();
										}}
									>
										{$t('common.select')}
									</button>
								</div>
							</div>
						{/if}
					</div>

					<!-- Size Range -->
					<div class="relative md:col-span-4">
						<button
							type="button"
							on:click={() => toggleDropdown('size')}
							class="inline-flex w-full items-center justify-between rounded-full border border-gray-200 bg-white px-5 py-3 text-sm font-medium text-gray-700 shadow-sm transition-all hover:bg-gray-50 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100 dark:hover:bg-gray-600 {searchParams.minSize ||
							searchParams.maxSize
								? 'border-primary-300 dark:border-primary-600 ring-primary-100 dark:ring-primary-900 ring-2'
								: ''}"
						>
							<span class="flex items-center">
								<svg
									class="h-5 w-5 text-gray-400 {isRTL ? 'ml-2' : 'mr-2'}"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"
									/>
								</svg>
								{#if searchParams.minSize || searchParams.maxSize}
									{searchParams.minSize || '0'} - {searchParams.maxSize || '∞'} m²
								{:else}
									{$t('search.size')}
								{/if}
							</span>
							<svg
								class="h-5 w-5 text-gray-400"
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
						</button>

						{#if showFilterDropdown.size}
							<div
								class="absolute {isRTL
									? 'right-0'
									: 'left-0'} ring-opacity-5 z-10 mt-3 w-72 rounded-xl bg-white p-5 shadow-xl ring-1 ring-black focus:outline-none dark:bg-gray-800"
								transition:fade={{ duration: 200 }}
							>
								<div class="space-y-4">
									<!-- Min Size -->
									<div>
										<label
											for="min-size"
											class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300"
										>
											{$t('search.min')} (m²)
										</label>
										<div class="relative">
											<input
												id="min-size"
												type="number"
												bind:value={searchParams.minSize}
												placeholder="0"
												class="focus:ring-primary-500 focus:border-primary-500 block w-full rounded-lg border border-gray-200 px-4 py-2.5 text-sm placeholder-gray-400 transition-all focus:outline-none dark:border-gray-600 dark:bg-gray-700 dark:text-white"
												min="0"
											/>
										</div>
									</div>

									<!-- Max Size -->
									<div>
										<label
											for="max-size"
											class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300"
										>
											{$t('search.max')} (m²)
										</label>
										<div class="relative">
											<input
												id="max-size"
												type="number"
												bind:value={searchParams.maxSize}
												placeholder="1000"
												class="focus:ring-primary-500 focus:border-primary-500 block w-full rounded-lg border border-gray-200 px-4 py-2.5 text-sm placeholder-gray-400 transition-all focus:outline-none dark:border-gray-600 dark:bg-gray-700 dark:text-white"
												min="0"
											/>
										</div>
									</div>

									<!-- Apply Button -->
									<button
										type="button"
										class="bg-primary-600 hover:bg-primary-700 mt-3 w-full transform rounded-lg px-4 py-2.5 text-sm font-medium text-white transition-all hover:scale-[1.02] active:scale-[0.98]"
										on:click={() => {
											toggleDropdown('size');
											handleSearch();
										}}
									>
										{$t('common.select')}
									</button>
								</div>
							</div>
						{/if}
					</div>

					<!-- Sort Dropdown -->
					<div class="relative md:col-span-2">
						<button
							type="button"
							on:click={() => toggleDropdown('sort')}
							class="inline-flex w-full items-center justify-between rounded-full border border-gray-200 bg-white px-5 py-3 text-sm font-medium text-gray-700 shadow-sm transition-all hover:bg-gray-50 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100 dark:hover:bg-gray-600 {searchParams.sort !==
							'newest'
								? 'border-primary-300 dark:border-primary-600 ring-primary-100 dark:ring-primary-900 ring-2'
								: ''}"
						>
							<span class="flex items-center">
								<svg
									class="h-5 w-5 text-gray-400 {isRTL ? 'ml-1' : 'mr-1'}"
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
								<span class="truncate"
									>{$t(sortOptions.find((o) => o.value === searchParams.sort)?.label)}</span
								>
							</span>
							<svg
								class="h-5 w-5 text-gray-400"
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
						</button>

						{#if showFilterDropdown.sort}
							<div
								class="absolute {isRTL
									? 'right-0'
									: 'left-0'} ring-opacity-5 z-10 mt-3 w-56 overflow-hidden rounded-xl bg-white shadow-xl ring-1 ring-black focus:outline-none dark:bg-gray-800"
								transition:fade={{ duration: 200 }}
							>
								<div class="py-2">
									{#each sortOptions as option}
										<button
											type="button"
											class="w-full px-5 py-2.5 text-start text-sm {searchParams.sort ===
											option.value
												? 'bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300 font-medium'
												: 'text-gray-700 hover:bg-gray-50 dark:text-gray-200 dark:hover:bg-gray-700'} transition-colors"
											on:click={() => {
												searchParams.sort = option.value;
												toggleDropdown('sort');
												handleSearch();
											}}
										>
											{$t(option.label)}
										</button>
									{/each}
								</div>
							</div>
						{/if}
					</div>

					<!-- Clear Filters Button -->
					<div class="md:col-span-2">
						<button
							type="button"
							on:click={clearFilters}
							disabled={activeFiltersCount === 0}
							class="inline-flex w-full items-center justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm transition-colors hover:bg-gray-50 focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50 dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600"
						>
							<svg
								class="h-5 w-5 {isRTL ? '-mr-1 ml-1.5' : 'mr-1.5 -ml-1'}"
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
							{#if activeFiltersCount > 0}
								<span
									class="ml-1 inline-flex h-5 w-5 items-center justify-center rounded-full bg-gray-200 text-xs text-gray-800 dark:bg-gray-600 dark:text-gray-200"
								>
									{activeFiltersCount}
								</span>
							{/if}
						</button>
					</div>
				</div>
			</form>
		</div>
	</div>

	<!-- Active Filters (visible when there are filters applied) -->
	{#if activeFiltersCount > 0}
		<div
			class="dark:bg-gray-750 rounded-b-lg border-t border-gray-100 bg-gray-50 px-6 py-3 dark:border-gray-700"
		>
			<div class="flex flex-wrap items-center gap-2">
				<!-- Property Type Filter -->
				{#if searchParams.propertyType}
					<div
						class="inline-flex items-center rounded-full bg-teal-100 px-3 py-1 text-xs text-teal-800 dark:bg-teal-900/50 dark:text-teal-300"
					>
						<span
							>{$t(propertyTypes.find((p) => p.value === searchParams.propertyType)?.label)}</span
						>
						<button
							class="ml-1.5 text-teal-500 hover:text-teal-700 dark:text-teal-400 dark:hover:text-teal-200"
							on:click={() => {
								searchParams.propertyType = '';
								handleSearch();
							}}
							aria-label={$t('search.removeFilter')}
						>
							<svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M6 18L18 6M6 6l12 12"
								/>
							</svg>
						</button>
					</div>
				{/if}

				<!-- City Filter -->
				{#if searchParams.city}
					<div
						class="inline-flex items-center rounded-full bg-cyan-100 px-3 py-1 text-xs text-cyan-800 dark:bg-cyan-900/50 dark:text-cyan-300"
					>
						<span>{searchParams.city}</span>
						<button
							class="ml-1.5 text-cyan-500 hover:text-cyan-700 dark:text-cyan-400 dark:hover:text-cyan-200"
							on:click={() => {
								searchParams.city = '';
								handleSearch();
							}}
							aria-label={$t('search.removeFilter')}
						>
							<svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M6 18L18 6M6 6l12 12"
								/>
							</svg>
						</button>
					</div>
				{/if}

				<!-- Price Range Filter -->
				{#if searchParams.minPrice || searchParams.maxPrice}
					<div
						class="inline-flex items-center rounded-full bg-purple-100 px-3 py-1 text-xs text-purple-800 dark:bg-purple-900/50 dark:text-purple-300"
					>
						<span>${searchParams.minPrice || '0'} - ${searchParams.maxPrice || '∞'}</span>
						<button
							class="ml-1.5 text-purple-500 hover:text-purple-700 dark:text-purple-400 dark:hover:text-purple-200"
							on:click={() => {
								searchParams.minPrice = '';
								searchParams.maxPrice = '';
								handleSearch();
							}}
							aria-label={$t('search.removeFilter')}
						>
							<svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M6 18L18 6M6 6l12 12"
								/>
							</svg>
						</button>
					</div>
				{/if}

				<!-- Size Range Filter -->
				{#if searchParams.minSize || searchParams.maxSize}
					<div
						class="inline-flex items-center rounded-full bg-amber-100 px-3 py-1 text-xs text-amber-800 dark:bg-amber-900/50 dark:text-amber-300"
					>
						<span>{searchParams.minSize || '0'} - {searchParams.maxSize || '∞'} m²</span>
						<button
							class="ml-1.5 text-amber-500 hover:text-amber-700 dark:text-amber-400 dark:hover:text-amber-200"
							on:click={() => {
								searchParams.minSize = '';
								searchParams.maxSize = '';
								handleSearch();
							}}
							aria-label={$t('search.removeFilter')}
						>
							<svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M6 18L18 6M6 6l12 12"
								/>
							</svg>
						</button>
					</div>
				{/if}

				<!-- Query Filter -->
				{#if searchParams.query}
					<div
						class="inline-flex items-center rounded-full bg-indigo-100 px-3 py-1 text-xs text-indigo-800 dark:bg-indigo-900/50 dark:text-indigo-300"
					>
						<span>"{searchParams.query}"</span>
						<button
							class="ml-1.5 text-indigo-500 hover:text-indigo-700 dark:text-indigo-400 dark:hover:text-indigo-200"
							on:click={() => {
								searchParams.query = '';
								handleSearch();
							}}
							aria-label={$t('search.removeFilter')}
						>
							<svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M6 18L18 6M6 6l12 12"
								/>
							</svg>
						</button>
					</div>
				{/if}

				<!-- Sort Filter -->
				{#if searchParams.sort !== 'newest'}
					<div
						class="inline-flex items-center rounded-full bg-red-100 px-3 py-1 text-xs text-red-800 dark:bg-red-900/50 dark:text-red-300"
					>
						<span>{$t(sortOptions.find((o) => o.value === searchParams.sort)?.label)}</span>
						<button
							class="ml-1.5 text-red-500 hover:text-red-700 dark:text-red-400 dark:hover:text-red-200"
							on:click={() => {
								searchParams.sort = 'newest';
								handleSearch();
							}}
							aria-label={$t('search.removeFilter')}
						>
							<svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M6 18L18 6M6 6l12 12"
								/>
							</svg>
						</button>
					</div>
				{/if}
			</div>
		</div>
	{/if}
</div>

<style>
	/* Ensure proper animation for filter tags */
	.inline-flex {
		animation: fadeIn 0.2s ease-out;
	}

	@keyframes fadeIn {
		from {
			opacity: 0;
			transform: translateY(-4px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}
</style>
