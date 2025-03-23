<!-- src/lib/components/auction/AuctionGrid.svelte -->
<script>
    import { onMount } from 'svelte';
    import { t } from '$lib/i18n';
    import { api } from '$lib/services/api';
    import AuctionCard from './AuctionCard.svelte';
    import AuctionFilters from './AuctionFilters.svelte';
    
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
    export let pageSize = 12;
    export let loadingPlaceholders = 6;
    export let autoPaginate = true;
    
    // State
    let auctions = [];
    let loading = true;
    let loadingMore = false;
    let error = null;
    let page = 1;
    let totalPages = 1;
    let totalAuctions = 0;
    let hasMoreAuctions = false;
    let filters = { ...initialFilters };
    
    // Element ref for infinite scroll detection
    let gridContainer;
    
    // Load auctions with current filters and pagination
    async function loadAuctions(pageNum = 1, append = false) {
      if ((loading && !append) || (loadingMore && append)) return;
      
      if (append) {
        loadingMore = true;
      } else {
        loading = true;
        error = null;
      }
      
      try {
        // Build query params from filters
        const params = {
          page: pageNum,
          page_size: pageSize,
          sort_by: filters.sort_by,
          order: filters.order
        };
        
        // Add filter params if they have values
        if (filters.status) params.status = filters.status;
        if (filters.property_type) params.property_type = filters.property_type;
        if (filters.auction_type) params.auction_type = filters.auction_type;
        if (filters.city) params.city = filters.city;
        if (filters.min_price) params.min_price = filters.min_price;
        if (filters.max_price) params.max_price = filters.max_price;
        
        const response = await api.get('auctions/', params);
        
        if (response && response.data && response.data.results) {
          // Update auction data based on append mode
          if (append) {
            auctions = [...auctions, ...response.data.results];
          } else {
            auctions = response.data.results;
            
            // Scroll to top when filters change
            if (pageNum === 1 && window) {
              window.scrollTo({ top: 0, behavior: 'smooth' });
            }
          }
          
          // Update pagination info
          page = pageNum;
          totalPages = response.data.total_pages || 1;
          totalAuctions = response.data.count || 0;
          hasMoreAuctions = page < totalPages;
        } else {
          throw new Error('Invalid response format');
        }
      } catch (err) {
        console.error('Error fetching auctions:', err);
        error = err.message || $t('system_messages.error_occurred');
      } finally {
        loading = false;
        loadingMore = false;
      }
    }
    
    // Handle filter changes
    function handleFilterChange(event) {
      filters = event.detail;
      page = 1; // Reset to first page
      loadAuctions(1, false);
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
      
      const observer = new IntersectionObserver(
        (entries) => {
          if (entries[0].isIntersecting && hasMoreAuctions && !loading && !loadingMore) {
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
      
      return () => {
        if (gridContainer) {
          observer.unobserve(gridContainer);
        }
      };
    }
    
    // Create loading placeholders
    function placeholders() {
      return Array(loadingPlaceholders).fill().map((_, i) => i);
    }
    
    // Initialize component
    onMount(() => {
      loadAuctions();
      return setupInfiniteScroll();
    });
  </script>
  
  <div class="auction-grid">
    <div class="mb-6 flex items-center justify-between">
      <h2 class="text-2xl font-bold text-cosmos-text">{title}</h2>
      
      {#if !loading && auctions.length > 0}
        <p class="text-sm text-cosmos-text-muted">
          {$t('auctions.showing_results').replace('{0}', auctions.length).replace('{1}', totalAuctions)}
        </p>
      {/if}
    </div>
    
    {#if showFilters}
      <AuctionFilters filters={filters} on:filter={handleFilterChange} />
    {/if}
    
    {#if error}
      <div class="my-8 rounded-xl bg-status-error bg-opacity-10 p-6 text-center">
        <p class="text-status-error">{error}</p>
        <button 
          class="mt-4 rounded-lg bg-primary px-4 py-2 text-white hover:bg-primary-dark"
          on:click={() => loadAuctions(1, false)}
        >
          {$t('general.retry')}
        </button>
      </div>
    {:else if loading && auctions.length === 0}
      <!-- Loading Placeholders -->
      <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {#each placeholders() as placeholder}
          <div class="animate-pulse rounded-xl bg-cosmos-bg-light bg-opacity-30 p-4">
            <div class="aspect-[4/3] w-full rounded-lg bg-cosmos-bg-light"></div>
            <div class="mt-4 h-6 w-3/4 rounded bg-cosmos-bg-light"></div>
            <div class="mt-2 h-4 w-1/2 rounded bg-cosmos-bg-light"></div>
            <div class="mt-4 flex justify-between">
              <div class="h-8 w-1/3 rounded bg-cosmos-bg-light"></div>
              <div class="h-8 w-1/3 rounded bg-cosmos-bg-light"></div>
            </div>
          </div>
        {/each}
      </div>
    {:else if auctions.length === 0}
      <!-- Empty State -->
      <div class="my-12 rounded-xl bg-cosmos-bg-light bg-opacity-10 p-8 text-center">
        <div class="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-cosmos-bg-light bg-opacity-30">
          <svg class="h-8 w-8 text-cosmos-text-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h3 class="mb-2 text-lg font-medium text-cosmos-text">{$t('auctions.no_auctions_found')}</h3>
        <p class="text-cosmos-text-muted">{$t('auctions.try_different_filters')}</p>
      </div>
    {:else}
      <!-- Auction Grid -->
      <div 
        bind:this={gridContainer}
        class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4"
      >
        {#each auctions as auction (auction.id)}
          <AuctionCard {auction} />
        {/each}
        
        <!-- Loading More Indicator -->
        {#if loadingMore}
          <div class="col-span-full my-6 flex justify-center">
            <div class="flex items-center space-x-2">
              <div class="h-5 w-5 animate-spin rounded-full border-2 border-primary border-t-transparent"></div>
              <span class="text-sm text-cosmos-text-muted">{$t('general.loading_more')}</span>
            </div>
          </div>
        {/if}
      </div>
      
      <!-- Manual Load More Button (when autoPaginate is false) -->
      {#if !autoPaginate && hasMoreAuctions && !loadingMore}
        <div class="mt-8 flex justify-center">
          <button
            on:click={loadMore}
            class="rounded-lg bg-primary bg-opacity-10 px-6 py-3 text-primary transition hover:bg-primary hover:text-white"
          >
            {$t('general.load_more')}
          </button>
        </div>
      {/if}
      
      <!-- End of Results Message -->
      {#if !hasMoreAuctions && auctions.length > 0 && !loading && !loadingMore}
        <div class="mt-8 text-center">
          <p class="text-sm text-cosmos-text-muted">
            {$t('auctions.end_of_results')}
          </p>
        </div>
      {/if}
    {/if}
  </div>