<!-- src/routes/auctions/+page.svelte (Refactored) -->
<script>
  import { onMount } from 'svelte';
  import { t } from '$lib/i18n/i18n';
  import { fetchAuctions } from '$lib/api/auction';
  import { auctions as auctionsStore } from '$lib/stores/auctions';
  import AuctionCard from '$lib/components/AuctionCard.svelte';
  import Breadcrumb from '$lib/components/Breadcrumb.svelte';
  import FilterPanel from '$lib/components/FilterPanel.svelte';
  import LoadingSkeleton from '$lib/components/LoadingSkeleton.svelte';
  import EmptyState from '$lib/components/EmptyState.svelte';
  import Button from '$lib/components/Button.svelte';
  
  let auctions = [];
  let loading = true;
  let error = '';
  let filters = {
    status: 'all',
    type: 'all',
    sortBy: 'newest'
  };
  let page = 1;
  let hasMore = false;
  
  // Define breadcrumb items
  const breadcrumbItems = [
    { label: $t('nav.home'), href: '/' },
    { label: $t('nav.auctions'), href: '/auctions', active: true }
  ];

  // Sorting options
  const sortOptions = [
    { value: 'newest', label: $t('search.sortOptions.newest') },
    { value: 'endingSoon', label: $t('auction.endingSoon') },
    { value: 'priceAsc', label: $t('search.sortOptions.priceAsc') },
    { value: 'priceDesc', label: $t('search.sortOptions.priceDesc') }
  ];
  
  // Status filter options
  const statusOptions = [
    { value: 'all', label: $t('auctions.allStatuses') },
    { value: 'live', label: $t('auction.statusLive') },
    { value: 'scheduled', label: $t('auction.statusScheduled') },
    { value: 'ended', label: $t('auction.statusEnded') },
    { value: 'completed', label: $t('auction.statusCompleted') }
  ];
  
  // Type filter options
  const typeOptions = [
    { value: 'all', label: $t('auctions.allTypes') },
    { value: 'sealed', label: $t('auction.typeSealed') },
    { value: 'reserve', label: $t('auction.typeReserve') },
    { value: 'no_reserve', label: $t('auction.typeNoReserve') }
  ];
  
  async function loadAuctions(reset = false) {
    try {
      if (reset) {
        page = 1;
        loading = true;
      } else {
        // Show loading more indicator instead of full screen loader
        hasMore = true;
      }
      error = '';
      
      const apiFilters = {
        page: page,
        limit: 9,  // Items per page
      };
      
      // Add filters
      if (filters.status !== 'all') {
        apiFilters.status = filters.status;
      }
      if (filters.type !== 'all') {
        apiFilters.auction_type = filters.type;
      }
      
      // Add sorting
      if (filters.sortBy) {
        apiFilters.sort = filters.sortBy;
      }
      
      const response = await fetchAuctions(apiFilters);
      
      if (reset) {
        auctions = response.results || [];
      } else {
        auctions = [...auctions, ...(response.results || [])];
      }
      
      // Update pagination
      hasMore = response.has_next || false;
      
      // Update global store
      auctionsStore.set(auctions);
      
    } catch (err) {
      console.error('Error loading auctions:', err);
      error = err.message || $t('error.fetchFailed');
    } finally {
      loading = false;
    }
  }
  
  function updateFilter(field, value) {
    filters[field] = value;
    loadAuctions(true); // Reset pagination when filter changes
  }
  
  function loadMore() {
    if (hasMore) {
      page += 1;
      loadAuctions(false);
    }
  }
  
  onMount(() => {
    loadAuctions(true);
  });
</script>

<svelte:head>
  <title>{$t('nav.auctions')} | Real Estate Platform</title>
  <meta name="description" content={$t('auctions.subtitle')} />
</svelte:head>

<div class="bg-gray-50 dark:bg-gray-900 min-h-screen py-8 px-4 sm:px-6 lg:px-8">
  <div class="max-w-7xl mx-auto">
    <!-- Breadcrumbs -->
    <Breadcrumb items={breadcrumbItems} class="mb-6" />
    
    <!-- Hero section -->
    <div class="text-center mb-12">
      <h1 class="text-3xl font-extrabold text-gray-900 dark:text-white sm:text-4xl md:text-5xl">
        {$t('auctions.title')}
      </h1>
      <p class="mt-4 max-w-2xl mx-auto text-xl text-gray-500 dark:text-gray-400">
        {$t('auctions.subtitle')}
      </p>
    </div>
    
    <!-- Filter controls -->
    <div class="mb-8 bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <div class="md:flex md:items-center md:justify-between mb-4">
        <h2 class="text-lg font-medium text-gray-900 dark:text-white mb-4 md:mb-0">
          {$t('search.filterAndSort')}
        </h2>
        
        <!-- Sort Dropdown -->
        <div class="flex items-center space-x-2">
          <label for="sort-by" class="text-sm font-medium text-gray-700 dark:text-gray-300">
            {$t('search.sort')}
          </label>
          <select
            id="sort-by"
            value={filters.sortBy}
            on:change={(e) => updateFilter('sortBy', e.target.value)}
            class="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            aria-label={$t('search.sort')}
          >
            {#each sortOptions as option}
              <option value={option.value}>{option.label}</option>
            {/each}
          </select>
        </div>
      </div>
      
      <!-- Filter Panels -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <!-- Status Filter -->
        <FilterPanel 
          title={$t('auctions.filterByStatus')} 
          options={statusOptions}
          value={filters.status}
          onChange={(value) => updateFilter('status', value)}
        />
        
        <!-- Type Filter -->
        <FilterPanel 
          title={$t('auctions.filterByType')} 
          options={typeOptions}
          value={filters.type}
          onChange={(value) => updateFilter('type', value)}
        />
        
        <!-- Price Range Filter could be added here -->
      </div>
    </div>
  
    <!-- Auction listings -->
    {#if loading && page === 1}
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {#each Array(6) as _, i}
          <LoadingSkeleton type="auctionCard" />
        {/each}
      </div>
    {:else if error}
      <div class="bg-red-50 dark:bg-red-900/20 p-6 rounded-lg text-red-800 dark:text-red-200 max-w-3xl mx-auto my-12">
        <h2 class="text-xl font-semibold mb-2">{$t('error.title')}</h2>
        <p>{error}</p>
        <Button 
          variant="primary"
          onClick={() => loadAuctions(true)}
          class="mt-4"
        >
          {$t('auction.tryAgain')}
        </Button>
      </div>
    {:else if auctions.length === 0}
      <EmptyState
        icon="auction"
        title={$t('auctions.noResults')}
        description={$t('auctions.tryAdjusting')}
        actionLabel={$t('properties.browseProperties')}
        actionUrl="/properties"
      />
    {:else}
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {#each auctions as auction (auction.id)}
          <AuctionCard {auction} />
        {/each}
      </div>
      
      <!-- Loading more indicator -->
      {#if page > 1 && loading}
        <div class="flex justify-center my-8">
          <div class="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-primary-500"></div>
        </div>
      {/if}
      
      <!-- Load More Button -->
      {#if hasMore && !loading}
        <div class="mt-12 text-center">
          <Button
            variant="secondary"
            onClick={loadMore}
            aria-label={$t('auctions.loadMore')}
          >
            {$t('auctions.loadMore')}
          </Button>
        </div>
      {/if}
      
      <!-- Create New Auction CTA -->
      <div class="mt-16 text-center">
        <p class="mb-4 text-gray-600 dark:text-gray-400">{$t('auctions.createNewPrompt')}</p>
        <Button
          variant="primary"
          href="/auctions/create"
          aria-label={$t('auction.createAuction')}
        >
          {$t('auction.createAuction')}
        </Button>
      </div>
    {/if}
  </div>
</div>