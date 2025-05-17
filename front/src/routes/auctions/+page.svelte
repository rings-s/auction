<!-- src/routes/auctions/+page.svelte -->
<script>
    import { onMount } from 'svelte';
    import { t } from '$lib/i18n/i18n';
    import { fetchAuctions } from '$lib/api/auction';
    import { auctions as auctionsStore } from '$lib/stores/auctions';
    import AuctionCard from '$lib/components/AuctionCard.svelte';
  
    let auctions = [];
    let loading = true;
    let error = '';
    let filters = {
      status: 'all',
      type: 'all',
    };
  
    async function loadAuctions() {
      try {
        loading = true;
        error = '';
  
        const apiFilters = {};
        if (filters.status !== 'all') {
          apiFilters.status = filters.status;
        }
        if (filters.type !== 'all') {
          apiFilters.auction_type = filters.type;
        }
  
        const response = await fetchAuctions(apiFilters);
        auctions = response.results || [];
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
      loadAuctions();
    }
  
    onMount(() => {
      loadAuctions();
    });
  </script>
  
  <svelte:head>
    <title>{$t('nav.auctions')} | Real Estate Platform</title>
  </svelte:head>
  
  <div class="bg-gray-50 dark:bg-gray-900 py-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Hero section -->
      <div class="text-center mb-12">
        <h1 class="text-3xl font-extrabold text-gray-900 dark:text-white sm:text-4xl">
          {$t('auctions.title')}
        </h1>
        <p class="mt-3 max-w-2xl mx-auto text-xl text-gray-500 dark:text-gray-400">
          {$t('auctions.subtitle')}
        </p>
      </div>
  
      <!-- Filter controls -->
      <div class="mb-8 bg-white dark:bg-gray-800 rounded-lg shadow p-4">
        <div class="flex flex-wrap gap-4">
          <div>
            <label for="status-filter" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              {$t('auctions.filterByStatus')}
            </label>
            <select
              id="status-filter"
              value={filters.status}
              on:change={(e) => updateFilter('status', e.target.value)}
              class="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            >
              <option value="all">{$t('auctions.allStatuses')}</option>
              <option value="live">{$t('auction.statusLive')}</option>
              <option value="scheduled">{$t('auction.statusScheduled')}</option>
              <option value="ended">{$t('auction.statusEnded')}</option>
              <option value="completed">{$t('auction.statusCompleted')}</option>
            </select>
          </div>
          <div>
            <label for="type-filter" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              {$t('auctions.filterByType')}
            </label>
            <select
              id="type-filter"
              value={filters.type}
              on:change={(e) => updateFilter('type', e.target.value)}
              class="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            >
              <option value="all">{$t('auctions.allTypes')}</option>
              <option value="sealed">{$t('auction.typeSealed')}</option>
              <option value="reserve">{$t('auction.typeReserve')}</option>
              <option value="no_reserve">{$t('auction.typeNoReserve')}</option>
            </select>
          </div>
        </div>
      </div>
  
      <!-- Auction listings -->
      {#if loading}
        <div class="flex justify-center py-24">
          <div class="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-primary-500"></div>
        </div>
      {:else if error}
        <div class="bg-red-50 dark:bg-red-900/20 p-6 rounded-lg text-red-800 dark:text-red-200 max-w-3xl mx-auto my-12">
          <h2 class="text-xl font-semibold mb-2">{$t('error.title')}</h2>
          <p>{error}</p>
        </div>
      {:else if auctions.length === 0}
        <div class="text-center py-16 bg-white dark:bg-gray-800 rounded-lg shadow">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-gray-400 dark:text-gray-500 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-1">{$t('auctions.noResults')}</h3>
          <p class="text-gray-500 dark:text-gray-400">{$t('auctions.tryAdjusting')}</p>
        </div>
      {:else}
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {#each auctions as auction}
          <AuctionCard {auction} />
        {/each}
      </div>
    {/if}
    
    {#if auctions.length > 0 && !loading}
      <div class="mt-12 text-center">
        <a 
          href="/properties" 
          class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
        >
          {$t('auctions.browseProperties')}
        </a>
      </div>
    {/if}
  </div>
</div>