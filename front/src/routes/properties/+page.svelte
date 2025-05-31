<!-- src/routes/properties/+page.svelte -->
<script>
  import { onMount, onDestroy } from 'svelte';
  import { fade, slide, fly } from 'svelte/transition';
  import { t, locale } from '$lib/i18n'; // Fixed import path
  import { user } from '$lib/stores/user';
  import { getProperties } from '$lib/api/property';
  import { properties as propertiesStore } from '$lib/stores/properties';
  
  // Components
  import PropertyCard from '$lib/components/properties/PropertyCard.svelte';
  import PropertySearch from '$lib/components/properties/PropertySearch.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import LoadingSkeleton from '$lib/components/ui/LoadingSkeleton.svelte';
  import EmptyState from '$lib/components/ui/EmptyState.svelte';

  // State
  let properties = [];
  let loading = true;
  let error = null;
  let currentPage = 1;
  let totalPages = 1;
  let loadingMore = false;
  let debounceTimer;
  let showMobileFilters = false;
  
  // Search parameters
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
  
  // Computed value for RTL mode
  $: isRTL = $locale === 'ar';
  
  // Check permissions for creating properties
  $: canCreateProperty = $user && ($user.role === 'owner' || $user.role === 'appraiser' || $user.is_staff || $user.is_superuser);

  // Convert search params to API params
  function getApiParams() {
    const params = {
      page: currentPage
    };

    // Add filters that have values
    if (searchParams.query) params.search = searchParams.query;
    if (searchParams.propertyType) params.property_type = searchParams.propertyType;
    if (searchParams.city) params.location__city = searchParams.city;
    if (searchParams.minPrice) params.market_value__gte = searchParams.minPrice;
    if (searchParams.maxPrice) params.market_value__lte = searchParams.maxPrice;
    if (searchParams.minSize) params.size_sqm__gte = searchParams.minSize;
    if (searchParams.maxSize) params.size_sqm__lte = searchParams.maxSize;
    
    // Handle sort ordering
    switch(searchParams.sort) {
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

  // Handle search submission
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
        totalPages = Math.ceil(response.count / (response.page_size || 10));
      } else if (Array.isArray(response)) {
        if (reset) {
          properties = response;
        } else {
          properties = [...properties, ...response];
        }
        totalPages = 1;
      } else {
        const results = response.data?.results || [];
        if (reset) {
          properties = results;
        } else {
          properties = [...properties, ...results];
        }
        totalPages = Math.ceil((response.data?.count || results.length) / (response.data?.page_size || 10));
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

<div class="min-h-screen" dir={isRTL ? 'rtl' : 'ltr'}>
  <div class="relative ">
    <div class="absolute inset-0"></div>
    <div class="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 md:py-12">
      <div class="md:flex md:items-center md:justify-between">
        <div>
          <h1 class="text-2xl md:text-3xl font-bold text-gray-900 dark:text-white">
            {$t('properties.title')}
          </h1>
          <p class="mt-2 text-sm md:text-base text-gray-600 dark:text-gray-300 max-w-2xl">
            {$t('properties.subtitle')}
          </p>
        </div>
        
        <!-- Create Property Link -->
        {#if canCreateProperty}
          <div class="mt-4 md:mt-0">
            <a 
              href="/properties/create" 
              class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-full shadow-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-all duration-300 hover:shadow-lg transform hover:-translate-y-0.5"
            >
              <svg class="w-5 h-5 {isRTL ? 'ml-2' : 'mr-2'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
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
          on:click={toggleMobileFilters}
          class="flex items-center justify-center px-4 py-2 rounded-full bg-white dark:bg-gray-700 shadow-sm border border-gray-200 dark:border-gray-600 text-sm font-medium text-gray-700 dark:text-gray-100 hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors"
        >
          <svg class="w-4 h-4 {isRTL ? 'ml-2' : 'mr-2'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12" />
          </svg>
          <span>{$t('search.advancedFilters')}</span>
        </button>
      </div>
    </div>
  </div>
  
  <!-- Main Content Area -->
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Search Filters - Desktop -->
    <div class="hidden md:block mb-8">
      <PropertySearch
        {searchParams}
        on:search={handleSearch}
      />
    </div>
    
    <!-- Content Area -->
    {#if loading && !properties.length}
      <!-- Loading Skeleton -->
      <div in:fade={{ duration: 200 }} out:fade={{ duration: 150 }}>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {#each Array(6) as _, i}
            <LoadingSkeleton type="propertyCard" />
          {/each}
        </div>
      </div>
    
    {:else if error}
      <!-- Error State -->
      <div 
        class="bg-white dark:bg-gray-800 shadow-lg rounded-xl p-8 max-w-2xl mx-auto"
        in:fly={{ y: 20, duration: 300 }}
        out:fade={{ duration: 200 }}
      >
        <div class="flex items-start {isRTL ? 'space-x-reverse' : ''} space-x-5">
          <div class="flex-shrink-0 bg-red-100 dark:bg-red-900/30 p-3 rounded-full">
            <svg class="h-8 w-8 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <div>
            <h3 class="text-xl font-bold text-gray-900 dark:text-white">{$t('error.title')}</h3>
            <p class="mt-2 text-base text-gray-600 dark:text-gray-300">{error}</p>
            
            <div class="mt-6 flex flex-wrap gap-3">
              <Button
                variant="outline"
                onClick={() => {
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
                <svg class="w-4 h-4 {isRTL ? 'ml-2' : 'mr-2'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
                {$t('search.clear')}
              </Button>
              
              <Button
                variant="primary"
                onClick={() => loadProperties()}
                size="default"
                class="w-full sm:w-auto"
              >
                <svg class="w-4 h-4 {isRTL ? 'ml-2' : 'mr-2'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                {$t('common.tryAgain')}
              </Button>
            </div>
          </div>
        </div>
      </div>

    {:else if !properties.length}
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
      <!-- Properties Grid -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {#each properties as property, index (property.id)}
          <div in:fly={{ y: 20, duration: 300, delay: 50 * (index % 6) }} out:fade={{ duration: 200 }}>
            <PropertyCard {property} />
          </div>
        {/each}
      </div>

      <!-- Load More Button -->
      {#if currentPage < totalPages && !loadingMore}
        <div class="mt-10 flex justify-center">
          <Button
            variant="outline"
            onClick={loadMore}
            size="large"
            class="px-8 py-3 transition-all hover:bg-gray-50 dark:hover:bg-gray-700 rounded-full"
          >
            <div class="flex items-center">
              <span>{$t('auction.loadMore')}</span>
              <svg class="{isRTL ? 'mr-2' : 'ml-2'} w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </div>
          </Button>
        </div>
      {/if}

      <!-- Loading More Indicator -->
      {#if loadingMore}
        <div class="mt-10 flex justify-center">
          <div class="flex items-center justify-center {isRTL ? 'space-x-reverse' : ''} space-x-2 text-primary-600 dark:text-primary-400">
            <div class="w-3 h-3 rounded-full bg-primary-600 dark:bg-primary-400 animate-bounce"></div>
            <div class="w-3 h-3 rounded-full bg-primary-600 dark:bg-primary-400 animate-bounce delay-150"></div>
            <div class="w-3 h-3 rounded-full bg-primary-600 dark:bg-primary-400 animate-bounce delay-300"></div>
            <span class="{isRTL ? 'mr-2' : 'ml-2'} text-sm font-medium">{$t('common.loading')}</span>
          </div>
        </div>
      {/if}
    {/if}
    
    <!-- Create Property Info Box for Non-Authorized Users -->
    {#if !canCreateProperty && !loading && properties.length > 0 && $user}
      <div class="mt-10 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl shadow-md p-6">
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
              class="w-full sm:w-auto shadow-md hover:shadow-lg transition-all"
            >
              <div class="flex items-center">
                <svg class="w-4 h-4 {isRTL ? 'ml-2' : 'mr-2'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
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
    <div class="fixed inset-0 z-40 flex md:hidden" in:fade={{ duration: 200 }} out:fade={{ duration: 150 }}>
      <!-- Backdrop -->
      <div class="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm" on:click={toggleMobileFilters} on:keydown={(e) => { if (e.key === 'Enter' || e.key === ' ') toggleMobileFilters(); }} role="button" tabindex="0" aria-label="Close filter panel"></div>
      
      <!-- Drawer panel -->
      <div 
        class="relative max-w-xs w-full h-full bg-white dark:bg-gray-800 shadow-2xl flex flex-col overflow-y-auto scrollbar-hide {isRTL ? 'right-0' : 'left-0'}"
        in:slide={{ duration: 300, axis: 'x' }}
        out:slide={{ duration: 250, axis: 'x', easing: x => 1 - Math.pow(1 - x, 3) }}
      >
        <div class="px-4 py-5 flex items-center justify-between border-b border-gray-200 dark:border-gray-700">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
            <svg class="w-5 h-5 {isRTL ? 'ml-2' : 'mr-2'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12" />
            </svg>
            {$t('search.advancedFilters')}
          </h2>
          <button
            type="button"
            class="rounded-full p-2 text-gray-400 hover:text-gray-500 hover:bg-gray-100 dark:text-gray-300 dark:hover:text-white dark:hover:bg-gray-700"
            on:click={toggleMobileFilters}
            aria-label="Close filter panel"
          >
            <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <!-- Mobile Search Component -->
        <div class="p-4 flex-1">
          <PropertySearch
            {searchParams}
            on:search={(e) => {
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