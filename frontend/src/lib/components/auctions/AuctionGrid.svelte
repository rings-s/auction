<!-- src/lib/components/auctions/AuctionGrid.svelte -->
<script>
  import { onMount, onDestroy } from 'svelte';
  import { t } from '$lib/i18n';
  import { auctionActions, loading } from '$lib/stores/auction';
  import AuctionCard from './AuctionCard.svelte';
  import AuctionFilters from './AuctionFilters.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  
  // Props
  export let initialFilters = {
    status: '',
    property_type: '',
    auction_type: '',
    city: '',
    min_price: '',
    max_price: '',
    sort_by: 'start_date',
    order: 'desc'
  };
  export let title = $t('auctions.title');
  export let showFilters = true;
  export let showTitle = true;
  export let pageSize = 12;
  export let loadingPlaceholders = 6;
  export let autoPaginate = true;
  export let filtersExpanded = false;
  export let emptyStateMessage = $t('auctions.no_auctions_found');
  export let compact = false;
  
  // State
  let auctions = [];
  let loadingAuctions = false;
  let loadingMore = false;
  let error = null;
  let page = 1;
  let totalPages = 1;
  let totalAuctions = 0;
  let hasMoreAuctions = false;
  let filters = { ...initialFilters };
  let showFilterPanel = false;
  
  // Element ref for infinite scroll detection
  let gridContainer;
  let observer;
  
  // Load auctions with current filters and pagination
  async function loadAuctions(pageNum = 1, append = false) {
    if ((loadingAuctions && !append) || (loadingMore && append)) return;
    
    if (append) {
      loadingMore = true;
    } else {
      loadingAuctions = true;
      error = null;
    }
    
    try {
      // Build query params from filters
      const params = {
        page: pageNum,
        page_size: pageSize,
        sort_by: filters.sort_by,
        order: filters.order || 'desc',
        ...filters
      };
      
      const result = await auctionActions.loadAuctions(params, append);
      
      if (result.success) {
        // Update auction data based on append mode
        if (append) {
          auctions = [...auctions, ...result.data.results];
        } else {
          auctions = result.data.results;
          
          // Scroll to top when filters change
          if (pageNum === 1 && window) {
            window.scrollTo({ top: 0, behavior: 'smooth' });
          }
        }
        
        // Update pagination info
        page = pageNum;
        totalPages = result.data.total_pages || 1;
        totalAuctions = result.data.count || 0;
        hasMoreAuctions = page < totalPages;
      } else {
        error = result.error || $t('system_messages.error_occurred');
      }
    } catch (err) {
      console.error('Error loading auctions:', err);
      error = err.message || $t('system_messages.error_occurred');
    } finally {
      loadingAuctions = false;
      loadingMore = false;
    }
  }
  
  // Handle filter changes
  function handleFilterChange(event) {
    filters = event.detail;
    page = 1; // Reset to first page
    loadAuctions(1, false);
    
    // Close filter panel on mobile
    if (window.innerWidth < 768) {
      showFilterPanel = false;
    }
  }
  
  // Toggle filter panel
  function toggleFilters() {
    showFilterPanel = !showFilterPanel;
  }
  
  // Load more auctions (for pagination)
  function loadMore() {
    if (hasMoreAuctions && !loadingMore) {
      loadAuctions(page + 1, true);
    }
  }
  
  // Set up infinite scroll
  function setupInfiniteScroll() {
    if (!autoPaginate || !window) return;
    
    observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && hasMoreAuctions && !loadingAuctions && !loadingMore) {
          loadMore();
        }
      },
      {
        rootMargin: '200px'
      }
    );
    
    if (gridContainer) {
      observer.observe(gridContainer);
    }
  }
  
  // Cleanup intersection observer
  function cleanupInfiniteScroll() {
    if (observer && gridContainer) {
      observer.unobserve(gridContainer);
      observer.disconnect();
    }
  }
  
  // Create loading placeholders
  function placeholders() {
    return Array(loadingPlaceholders).fill().map((_, i) => i);
  }
  
  // Initialize component
  onMount(() => {
    loadAuctions();
    setupInfiniteScroll();
  });
  
  // Cleanup on component destroy
  onDestroy(() => {
    cleanupInfiniteScroll();
  });
</script>

<div class="auction-grid">
  <!-- Title and controls header -->
  {#if showTitle}
    <div class="flex flex-col md:flex-row md:items-center md:justify-between mb-6 gap-4">
      <h2 class="text-2xl font-bold text-neutral-800 dark:text-neutral-200">
        {title}
      </h2>
      
      <div class="flex items-center space-x-4">
        {#if !loadingAuctions && auctions.length > 0}
          <p class="text-sm text-neutral-500 dark:text-neutral-400 hidden md:block">
            {$t('auctions.showing_results').replace('{0}', auctions.length).replace('{1}', totalAuctions)}
          </p>
        {/if}
        
        <!-- Mobile filter toggle -->
        <div class="md:hidden">
          <Button 
            variant="outline" 
            size="sm" 
            on:click={toggleFilters}
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M3 3a1 1 0 011-1h12a1 1 0 011 1v3a1 1 0 01-.293.707L12 11.414V15a1 1 0 01-.293.707l-2 2A1 1 0 018 17v-5.586L3.293 6.707A1 1 0 013 6V3z" clip-rule="evenodd" />
            </svg>
            {$t('general.filter')}
          </Button>
        </div>
      </div>
    </div>
  {/if}
  
  <!-- Main content grid with sidebar -->
  <div class="grid grid-cols-1 md:grid-cols-12 gap-6">
    <!-- Filters sidebar - desktop version -->
    {#if showFilters}
      <div class="hidden md:block md:col-span-3">
        <AuctionFilters 
          currentFilters={filters} 
          isExpanded={filtersExpanded}
          on:change={handleFilterChange}
        />
      </div>
    {/if}
    
    <!-- Mobile filter panel - shown when toggled -->
    {#if showFilters && showFilterPanel}
      <div class="fixed inset-0 z-50 bg-neutral-800 bg-opacity-75 md:hidden">
        <div class="h-full w-full max-w-md ml-auto bg-white dark:bg-neutral-800 shadow-xl flex flex-col">
          <AuctionFilters 
            currentFilters={filters} 
            isExpanded={filtersExpanded}
            on:change={handleFilterChange}
            on:close={toggleFilters}
          />
        </div>
      </div>
    {/if}
    
    <!-- Auctions grid -->
    <div class={`${showFilters ? 'md:col-span-9' : 'md:col-span-12'}`}>
      {#if error}
        <!-- Error state -->
        <div class="my-8 rounded-xl bg-error-50 dark:bg-error-900/20 p-6 text-center">
          <p class="text-error-600 dark:text-error-400">{error}</p>
          <Button 
            variant="primary" 
            class="mt-4"
            on:click={() => loadAuctions(1, false)}
          >
            {$t('general.retry')}
          </Button>
        </div>
      {:else if loadingAuctions && auctions.length === 0}
        <!-- Loading Placeholders -->
        <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {#each placeholders() as placeholder}
            <div class="animate-pulse rounded-xl bg-neutral-100 dark:bg-neutral-800 p-4">
              <div class="aspect-[4/3] w-full rounded-lg bg-neutral-200 dark:bg-neutral-700"></div>
              <div class="mt-4 h-6 w-3/4 rounded bg-neutral-200 dark:bg-neutral-700"></div>
              <div class="mt-2 h-4 w-1/2 rounded bg-neutral-200 dark:bg-neutral-700"></div>
              <div class="mt-4 flex justify-between">
                <div class="h-8 w-1/3 rounded bg-neutral-200 dark:bg-neutral-700"></div>
                <div class="h-8 w-1/3 rounded bg-neutral-200 dark:bg-neutral-700"></div>
              </div>
            </div>
          {/each}
        </div>
      {:else if auctions.length === 0}
        <!-- Empty State -->
        <div class="my-12 rounded-xl bg-neutral-50 dark:bg-neutral-800/50 p-8 text-center">
          <div class="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-neutral-100 dark:bg-neutral-700">
            <svg class="h-8 w-8 text-neutral-500 dark:text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 class="mb-2 text-lg font-medium text-neutral-800 dark:text-neutral-200">{emptyStateMessage}</h3>
          <p class="text-neutral-500 dark:text-neutral-400">{$t('auctions.try_different_filters')}</p>
        </div>
      {:else}
        <!-- Auction Grid -->
        <div 
          bind:this={gridContainer}
          class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3"
        >
          {#each auctions as auction (auction.id)}
            <AuctionCard {auction} {compact} />
          {/each}
        </div>
        
        <!-- Loading More Indicator -->
        {#if loadingMore}
          <div class="col-span-full my-6 flex justify-center">
            <div class="flex items-center space-x-2">
              <div class="h-5 w-5 animate-spin rounded-full border-2 border-primary-600 border-t-transparent"></div>
              <span class="text-sm text-neutral-500 dark:text-neutral-400">{$t('general.loading_more')}</span>
            </div>
          </div>
        {/if}
        
        <!-- Manual Load More Button (when autoPaginate is false) -->
        {#if !autoPaginate && hasMoreAuctions && !loadingMore}
          <div class="mt-8 flex justify-center">
            <Button
              variant="outline"
              on:click={loadMore}
            >
              {$t('general.load_more')}
            </Button>
          </div>
        {/if}
        
        <!-- End of Results Message -->
        {#if !hasMoreAuctions && auctions.length > 0 && !loadingAuctions && !loadingMore}
          <div class="mt-8 text-center">
            <p class="text-sm text-neutral-500 dark:text-neutral-400">
              {$t('auctions.end_of_results')}
            </p>
          </div>
        {/if}
      {/if}
    </div>
  </div>
</div>