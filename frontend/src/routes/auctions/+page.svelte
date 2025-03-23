<!-- src/routes/auctions/+page.svelte -->
<script>
    import { onMount } from 'svelte';
    import { t } from '$lib/i18n';
    import { page } from '$app/stores';
    import { auctionActions, auctionsList, loading, errors, auctionsMetadata } from '$lib/stores/auction';
    import { authStore } from '$lib/stores/auth';
    import AuctionCard from './components/auctions/AuctionCard.svelte';
    import AuctionFilters from './components/auctions/AuctionFilters.svelte';
    import { 
      Button, 
      Loading, 
      Alert, 
      Pagination,
      Icon, 
      Empty 
    } from '$lib/components/ui';
    
    // Component state
    let filters = {
      status: null,
      auction_type: null,
      property_type: null,
      min_price: null,
      max_price: null,
      city: null,
      district: null,
      is_featured: null,
      sort_by: 'start_date',
      order: 'desc'
    };
    
    let showFilters = false;
    let isInitialLoad = true;
    
    // Load auctions with current filters
    async function loadAuctions(appendMode = false) {
      try {
        const result = await auctionActions.loadAuctions(filters, appendMode);
        isInitialLoad = false;
        return result;
      } catch (error) {
        console.error('Error loading auctions:', error);
        isInitialLoad = false;
        return { success: false, error: error.message };
      }
    }
    
    // Handle filter changes
    function handleFilterChange(event) {
      const updatedFilters = event.detail;
      filters = { ...filters, ...updatedFilters };
      
      // Update URL with filters
      updateUrl();
      
      // Reload auctions with new filters
      loadAuctions();
    }
    
    // Handle pagination
    function handlePageChange(event) {
      const page = event.detail;
      filters = { ...filters, page };
      
      // Update URL with page
      updateUrl();
      
      // Reload auctions with new page
      loadAuctions();
    }
    
    // Handle "load more" button
    function handleLoadMore() {
      loadAuctions(true);
    }
    
    // Update URL with current filters
    function updateUrl() {
      // Don't update URL if not in browser
      if (typeof window === 'undefined') return;
      
      const url = new URL(window.location);
      
      // Add non-null filters to URL
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== null && value !== undefined && value !== '') {
          url.searchParams.set(key, value);
        } else {
          url.searchParams.delete(key);
        }
      });
      
      // Update URL without reloading the page
      history.pushState({}, '', url);
    }
    
    // Extract filters from URL
    function extractFiltersFromUrl() {
      if (!$page || !$page.url) return;
      
      const urlParams = $page.url.searchParams;
      const filtersFromUrl = {};
      
      // Gather all filter parameters from URL
      Object.keys(filters).forEach(key => {
        const value = urlParams.get(key);
        if (value !== null) {
          // Convert values to appropriate types
          if (value === 'true') filtersFromUrl[key] = true;
          else if (value === 'false') filtersFromUrl[key] = false;
          else if (/^\d+$/.test(value)) filtersFromUrl[key] = parseInt(value, 10);
          else if (/^\d+\.\d+$/.test(value)) filtersFromUrl[key] = parseFloat(value);
          else filtersFromUrl[key] = value;
        }
      });
      
      // Update filters state
      if (Object.keys(filtersFromUrl).length > 0) {
        filters = { ...filters, ...filtersFromUrl };
      }
    }
    
    // Initialize component
    onMount(() => {
      // Extract filters from URL
      extractFiltersFromUrl();
      
      // Load auctions
      loadAuctions();
    });
  </script>
  
  <svelte:head>
    <title>{t('auctions.browse')} | {t('site.name')}</title>
    <meta name="description" content={t('auctions.meta_description')} />
  </svelte:head>
  
  <div class="auctions-list">
    <!-- Page header -->
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center mb-6">
      <div>
        <h1 class="text-2xl md:text-3xl font-bold">{t('auctions.browse')}</h1>
        <p class="text-gray-600 mt-1">
          {t('auctions.browse_description')}
        </p>
      </div>
      
      <div class="flex gap-3 mt-4 md:mt-0">
        <!-- Filter toggle button -->
        <Button 
          variant="outline" 
          on:click={() => showFilters = !showFilters}
        >
          <Icon name="filter" />
          {t('general.filters')}
          {#if Object.values(filters).some(v => v !== null && v !== undefined && v !== '')}
            <span class="ml-1 bg-primary text-white rounded-full w-5 h-5 inline-flex items-center justify-center text-xs">
              {Object.values(filters).filter(v => v !== null && v !== undefined && v !== '').length}
            </span>
          {/if}
        </Button>
        
        <!-- Create auction button (for authenticated users) -->
        {#if $authStore.isAuthenticated}
          <Button 
            variant="primary" 
            href="/auctions/create"
          >
            <Icon name="plus" />
            {t('auctions.create')}
          </Button>
        {/if}
      </div>
    </div>
    
    <!-- Filters section -->
    {#if showFilters}
      <div class="mb-6">
        <AuctionFilters 
          currentFilters={filters} 
          on:change={handleFilterChange}
          on:close={() => showFilters = false}
        />
      </div>
    {/if}
    
    <!-- Loading state -->
    {#if $loading.auctionsLoading && isInitialLoad}
      <div class="flex flex-col items-center justify-center p-10">
        <Loading size="large" />
        <p class="mt-4 text-lg">{t('auctions.loading')}</p>
      </div>
    <!-- Error state -->
    {:else if $errors.listError}
      <Alert 
        type="error" 
        message={$errors.listError} 
        class="mb-6"
      />
    <!-- No results -->
    {:else if $auctionsList.length === 0}
      <Empty 
        title={t('auctions.no_results')}
        description={t('auctions.no_results_description')}
        actionText={t('auctions.clear_filters')}
        actionHref="/auctions"
        imageSrc="/images/no-auctions.svg"
      />
    <!-- Auctions grid -->
    {:else}
      <!-- Results count and sort options -->
      <div class="flex justify-between items-center mb-4">
        <p class="text-gray-600">
          {t('auctions.showing_results', { count: $auctionsList.length, total: $auctionsMetadata.totalCount })}
        </p>
        
        <!-- Sort options -->
        <div class="flex items-center gap-2">
          <span class="text-gray-600 text-sm">{t('general.sort_by')}:</span>
          <select 
            class="border border-gray-300 rounded-md text-sm px-2 py-1"
            bind:value={filters.sort_by}
            on:change={() => {
              updateUrl();
              loadAuctions();
            }}
          >
            <option value="start_date">{t('auctions.start_date')}</option>
            <option value="end_date">{t('auctions.end_date')}</option>
            <option value="current_bid">{t('auctions.current_bid')}</option>
            <option value="title">{t('general.title')}</option>
            <option value="created_at">{t('general.created_at')}</option>
          </select>
          
          <select 
            class="border border-gray-300 rounded-md text-sm px-2 py-1"
            bind:value={filters.order}
            on:change={() => {
              updateUrl();
              loadAuctions();
            }}
          >
            <option value="desc">{t('general.descending')}</option>
            <option value="asc">{t('general.ascending')}</option>
          </select>
        </div>
      </div>
      
      <!-- Auctions grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        {#each $auctionsList as auction (auction.id)}
          <AuctionCard {auction} />
        {/each}
      </div>
      
      <!-- Loading spinner for "load more" -->
      {#if $loading.loadingMore}
        <div class="flex justify-center my-6">
          <Loading />
        </div>
      {/if}
      
      <!-- Pagination options -->
      <div class="flex flex-col md:flex-row justify-between items-center">
        <!-- Load more button -->
        {#if $auctionsMetadata.hasMore}
          <Button 
            variant="outline" 
            on:click={handleLoadMore} 
            disabled={$loading.loadingMore}
            class="w-full md:w-auto mb-4 md:mb-0"
          >
            {t('general.load_more')}
          </Button>
        {:else}
          <div class="text-gray-500 text-sm mb-4 md:mb-0">
            {t('auctions.end_of_results')}
          </div>
        {/if}
        
        <!-- Pagination controls -->
        <Pagination 
          currentPage={$auctionsMetadata.currentPage} 
          totalPages={$auctionsMetadata.totalPages}
          on:change={handlePageChange}
        />
      </div>
    {/if}
  </div>