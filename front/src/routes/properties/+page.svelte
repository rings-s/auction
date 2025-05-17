<!-- src/routes/properties/+page.svelte -->
<script>
  import { onMount } from 'svelte';
  import { t } from '$lib/i18n/i18n';
  import { fetchProperties } from '$lib/api/property';
  import { properties as propertiesStore } from '$lib/stores/properties';
  import PropertyCard from '$lib/components/PropertyCard.svelte';
  import PropertySearch from '$lib/components/PropertySearch.svelte';

  let properties = [];
  let loading = true;
  let error = null;
  let currentPage = 1;
  let totalPages = 1;
  let searchParams = {
    query: '',
    propertyType: '',
    minPrice: '',
    maxPrice: '',
    city: '',
    minSize: '',
    maxSize: '',
    sort: 'newest'
  };

  // Convert search params to API params
  function getApiParams() {
    const params = {
      page: currentPage,
      ordering: getSortOrder(searchParams.sort)
    };

    // Only add params that have values
    if (searchParams.query) params.search = searchParams.query;
    if (searchParams.propertyType) params.property_type = searchParams.propertyType;
    if (searchParams.city) params.location__city = searchParams.city;
    if (searchParams.minPrice) params.market_value__gte = searchParams.minPrice;
    if (searchParams.maxPrice) params.market_value__lte = searchParams.maxPrice;
    if (searchParams.minSize) params.size_sqm__gte = searchParams.minSize;
    if (searchParams.maxSize) params.size_sqm__lte = searchParams.maxSize;

    return params;
  }

  // Get sort order parameter
  function getSortOrder(sort) {
    const sortMap = {
      newest: '-created_at',
      oldest: 'created_at',
      priceAsc: 'market_value',
      priceDesc: '-market_value',
      sizeAsc: 'size_sqm',
      sizeDesc: '-size_sqm'
    };
    return sortMap[sort] || '-created_at';
  }

  // Handle search
  async function handleSearch(event) {
    searchParams = event.detail;
    currentPage = 1; // Reset to first page on new search
    await loadProperties();
  }

  // Load properties
  async function loadProperties() {
    try {
      loading = true;
      error = null;

      const apiParams = getApiParams();
      const response = await fetchProperties(apiParams);

      if (response.results) {
        properties = response.results;
        totalPages = Math.ceil(response.count / response.page_size);
        propertiesStore.set(properties);
      } else {
        throw new Error('Invalid response format');
      }
    } catch (err) {
      console.error('Error loading properties:', err);
      error = err.message || $t('error.fetchFailed');
      properties = []; // Clear properties on error
    } finally {
      loading = false;
    }
  }

  // Load more properties
  async function loadMore() {
    if (currentPage < totalPages && !loading) {
      currentPage++;
      try {
        loading = true;
        const apiParams = getApiParams();
        const response = await fetchProperties(apiParams);
        
        if (response.results) {
          properties = [...properties, ...response.results];
          propertiesStore.set(properties);
        }
      } catch (err) {
        console.error('Error loading more properties:', err);
        currentPage--; // Revert page increment on error
      } finally {
        loading = false;
      }
    }
  }

  // Initial load
  onMount(() => {
    loadProperties();
  });
</script>

<svelte:head>
  <title>{$t('properties.title')} | Real Estate Platform</title>
</svelte:head>

<div class="bg-gray-50 dark:bg-gray-900 min-h-screen py-8">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <!-- Hero Section -->
    <div class="text-center mb-12">
      <h1 class="text-3xl font-extrabold text-gray-900 dark:text-white sm:text-4xl">
        {$t('properties.title')}
      </h1>
      <p class="mt-3 max-w-2xl mx-auto text-xl text-gray-500 dark:text-gray-400">
        {$t('properties.subtitle')}
      </p>
    </div>

    <!-- Search Section -->
    <div class="mb-8">
      <PropertySearch
        {searchParams}
        on:search={handleSearch}
      />
    </div>

    <!-- Loading State (Initial) -->
    {#if loading && !properties.length}
      <div class="flex justify-center py-12">
        <div class="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-primary-500"></div>
      </div>
    
    <!-- Error State -->
    {:else if error}
      <div class="bg-red-50 dark:bg-red-900/20 p-6 rounded-lg text-red-800 dark:text-red-200 max-w-3xl mx-auto my-12">
        <h2 class="text-xl font-semibold mb-2">{$t('error.title')}</h2>
        <p>{error}</p>
        <button
          class="mt-4 inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
          on:click={loadProperties}
        >
          {$t('error.tryAgain')}
        </button>
      </div>

    <!-- Empty State -->
    {:else if !properties.length}
      <div class="text-center py-16 bg-white dark:bg-gray-800 rounded-lg shadow">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-gray-400 dark:text-gray-500 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
        </svg>
        <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-1">
          {$t('properties.noResults')}
        </h3>
        <p class="text-gray-500 dark:text-gray-400">
          {$t('properties.tryAdjusting')}
        </p>
      </div>

    <!-- Property Grid -->
    {:else}
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {#each properties as property (property.id)}
          <PropertyCard {property} />
        {/each}
      </div>

      <!-- Load More -->
      {#if currentPage < totalPages && !loading}
        <div class="flex justify-center mt-8">
          <button
            class="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            on:click={loadMore}
          >
            {$t('properties.loadMore')}
          </button>
        </div>
      {/if}

      <!-- Loading More Indicator -->
      {#if loading && properties.length}
        <div class="flex justify-center mt-8">
          <div class="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary-500"></div>
        </div>
      {/if}
    {/if}
  </div>
</div>