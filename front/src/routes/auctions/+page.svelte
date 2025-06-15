<!-- src/routes/auctions/+page.svelte -->
<script>
  import { onMount, onDestroy } from 'svelte';
  import { fade, slide, fly } from 'svelte/transition';
  import { t, locale } from '$lib/i18n';
  import { user } from '$lib/stores/user';
  import { fetchAuctions } from '$lib/api/auction';
  import { auctions as auctionsStore } from '$lib/stores/auctions';

  // Components
  import AuctionCard from '$lib/components/auction/AuctionCard.svelte';
  import LoadingSkeleton from '$lib/components/ui/LoadingSkeleton.svelte';
  import EmptyState from '$lib/components/ui/EmptyState.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import QuickBidPopover from '$lib/components/auction/QuickBidPopover.svelte';
  import RealtimeBidFeed from '$lib/components/auction/RealtimeBidFeed.svelte';
  import BidActivityIndicator from '$lib/components/auction/BidActivityIndicator.svelte';

  // State
  let auctions = [];
  let loading = true;
  let error = null;
  let currentPage = 1;
  let totalPages = 1;
  let loadingMore = false;
  let debounceTimer;
  let showMobileFilters = false;
  let showFilterDropdown = { sort: false, price: false, type: false, status: false };
  let activeFiltersCount = 0;
  let refreshInterval;
  
  // Quick bid state
  let selectedAuctionForQuickBid = null;
  let showQuickBidModal = false;
  
  // Live auction stats
  let liveAuctionCount = 0;
  let totalActiveBids = 0;
  let showBidFeed = true;

  // Computed value for RTL mode
  $: isRTL = $locale === 'ar';

  // Filter state
  let filters = {
    search: '',
    status: '',
    type: '',
    sort: 'newest',
    minPrice: '',
    maxPrice: ''
  };

  // Status filter options
  const statusOptions = [
    { value: '', label: 'auction.allStatuses' },
    { value: 'live', label: 'auction.statusLive', icon: '🔴' },
    { value: 'scheduled', label: 'auction.statusScheduled', icon: '📅' },
    { value: 'ended', label: 'auction.statusEnded', icon: '🏁' },
    { value: 'completed', label: 'auction.statusCompleted', icon: '✅' }
  ];

  // Type filter options
  const typeOptions = [
    { value: '', label: 'auction.allTypes' },
    { value: 'sealed', label: 'auction.typeSealed', icon: '🔒' },
    { value: 'private', label: 'auction.typeReserve', icon: '🏷️' },
    { value: 'public', label: 'auction.typeNoReserve', icon: '🎯' }
  ];

  // Sort options
  const sortOptions = [
    { value: 'newest', label: 'search.sortOptions.newest', icon: '🆕' },
    { value: 'endingSoon', label: 'auction.endingSoon', icon: '⏰' },
    { value: 'mostActive', label: 'auction.mostActive', icon: '🔥' },
    { value: 'priceAsc', label: 'search.sortOptions.priceAsc', icon: '💰' },
    { value: 'priceDesc', label: 'search.sortOptions.priceDesc', icon: '💸' },
    { value: 'bidCount', label: 'auction.totalBids', icon: '📊' }
  ];

  // Check permissions for creating auctions
  $: canCreateAuction = $user && ($user.role === 'owner' || $user.role === 'appraiser' || $user.is_staff || $user.is_superuser);

  // Calculate active filters count
  $: {
    activeFiltersCount = 0;
    if (filters.search) activeFiltersCount++;
    if (filters.status) activeFiltersCount++;
    if (filters.type) activeFiltersCount++;
    if (filters.sort !== 'newest') activeFiltersCount++;
    if (filters.minPrice) activeFiltersCount++;
    if (filters.maxPrice) activeFiltersCount++;
  }
  
  // Calculate live stats
  $: {
    liveAuctionCount = auctions.filter(a => a.status === 'live').length;
    totalActiveBids = auctions.reduce((sum, a) => sum + (a.bid_count || 0), 0);
  }

  // Toggle dropdown visibility
  function toggleDropdown(name) {
    showFilterDropdown = Object.keys(showFilterDropdown).reduce((acc, key) => {
      acc[key] = key === name ? !showFilterDropdown[key] : false;
      return acc;
    }, {});
  }

  // Close all dropdowns when clicking outside
  function handleClickOutside(event) {
    if (!event.target.closest('.filter-dropdown')) {
      showFilterDropdown = Object.keys(showFilterDropdown).reduce((acc, key) => {
        acc[key] = false;
        return acc;
      }, {});
    }
  }

  // Handle filter changes with debounce
  function handleFilterChange(name, value) {
    clearTimeout(debounceTimer);
    filters[name] = value;
    
    if (name === 'search') {
      debounceTimer = setTimeout(() => {
        loadAuctions();
      }, 500);
    } else {
      loadAuctions();
    }
    
    // Close dropdown if it's a dropdown selection
    if (name !== 'search' && name !== 'minPrice' && name !== 'maxPrice') {
      showFilterDropdown = Object.keys(showFilterDropdown).reduce((acc, key) => {
        acc[key] = false;
        return acc;
      }, {});
    }
  }

  // Convert filter state to API parameters
  function getApiParams() {
    const params = {
      page: currentPage
    };

    if (filters.search) params.search = filters.search;
    if (filters.status) params.status = filters.status;
    if (filters.type) params.auction_type = filters.type;
    
    if (filters.minPrice) params.min_price = filters.minPrice;
    if (filters.maxPrice) params.max_price = filters.maxPrice;
    
    switch (filters.sort) {
      case 'newest':
        params.ordering = '-created_at';
        break;
      case 'endingSoon':
        params.ordering = 'end_date';
        params.status = params.status || 'live'; // Only show live auctions
        break;
      case 'mostActive':
        params.ordering = '-bid_count,-view_count';
        break;
      case 'priceAsc':
        params.ordering = 'starting_bid';
        break;
      case 'priceDesc':
        params.ordering = '-starting_bid';
        break;
      case 'bidCount':
        params.ordering = '-bid_count';
        break;
      default:
        params.ordering = '-created_at';
    }

    return params;
  }

  // Load auctions with current filters
  async function loadAuctions(reset = true) {
    try {
      if (reset) {
        loading = true;
        currentPage = 1;
      } else {
        loadingMore = true;
      }
      
      error = null;
      const apiParams = getApiParams();
      const response = await fetchAuctions(apiParams);

      if (response.results) {
        if (reset) {
          auctions = response.results;
        } else {
          auctions = [...auctions, ...response.results];
        }
        totalPages = Math.ceil(response.count / (response.page_size || 10));
      } else if (Array.isArray(response)) {
        if (reset) {
          auctions = response;
        } else {
          auctions = [...auctions, ...response];
        }
        totalPages = 1;
      } else {
        const results = response.data?.results || [];
        if (reset) {
          auctions = results;
        } else {
          auctions = [...auctions, ...results];
        }
        totalPages = Math.ceil((response.data?.count || results.length) / (response.data?.page_size || 10));
      }
      
      auctionsStore.set(auctions);
    } catch (err) {
      error = err.message || $t('error.fetchFailed');
      auctions = [];
    } finally {
      loading = false;
      loadingMore = false;
    }
  }

  // Clear all filters
  function clearFilters() {
    filters = {
      search: '',
      status: '',
      type: '',
      sort: 'newest',
      minPrice: '',
      maxPrice: ''
    };
    loadAuctions();
  }

  // Load more auctions
  function loadMore() {
    if (currentPage < totalPages && !loadingMore) {
      currentPage++;
      loadAuctions(false);
    }
  }

  // Toggle mobile filters
  function toggleMobileFilters() {
    showMobileFilters = !showMobileFilters;
    document.body.style.overflow = showMobileFilters ? 'hidden' : '';
  }
  
  // Handle quick bid click
  function handleQuickBidClick(auction) {
    selectedAuctionForQuickBid = auction;
    showQuickBidModal = true;
  }
  
  // Handle bid placed
  function handleBidPlaced(event) {
    const { detail } = event;
    // Refresh the auction data
    loadAuctions();
    
    // Show success notification
    // You can add a toast notification here
  }
  
  // Auto-refresh for live auctions
  function startAutoRefresh() {
    refreshInterval = setInterval(() => {
      if (liveAuctionCount > 0 && !loading && !loadingMore) {
        loadAuctions();
      }
    }, 30000); // Refresh every 30 seconds if there are live auctions
  }

  // Cleanup on component destroy
  onDestroy(() => {
    clearTimeout(debounceTimer);
    document.body.style.overflow = '';
    window.removeEventListener('click', handleClickOutside);
    if (refreshInterval) clearInterval(refreshInterval);
  });

  // Initial load
  onMount(() => {
    loadAuctions();
    window.addEventListener('click', handleClickOutside);
    startAutoRefresh();
  });
</script>

<svelte:head>
  <title>{$t('auction.title')} | Real Estate Platform</title>
</svelte:head>

<div class="min-h-screen bg-gray-50 dark:bg-gray-900">
  <!-- Enhanced Hero Section with Live Stats -->
  <div class="relative bg-gradient-to-br from-primary-600 via-primary-700 to-secondary-700 text-white">
    <div class="absolute inset-0 bg-black/20"></div>
    <div class="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 md:py-12">
      <div class="md:flex md:items-center md:justify-between">
        <div>
          <h1 class="text-3xl md:text-4xl font-bold flex items-center">
            {$t('auction.title')}
            {#if liveAuctionCount > 0}
              <span class="ml-3 inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-red-500 text-white animate-pulse">
                <span class="w-2 h-2 bg-white rounded-full mr-2"></span>
                {liveAuctionCount} LIVE
              </span>
            {/if}
          </h1>
          <p class="mt-2 text-base md:text-lg text-white/90 max-w-2xl">
            {$t('auction.subtitle')}
          </p>
          
          <!-- Live Stats Bar -->
          {#if liveAuctionCount > 0 || totalActiveBids > 0}
            <div class="mt-4 flex flex-wrap gap-4">
              <div class="bg-white/10 backdrop-blur-sm rounded-lg px-4 py-2">
                <p class="text-xs text-white/70">Active Auctions</p>
                <p class="text-xl font-bold">{liveAuctionCount}</p>
              </div>
              <div class="bg-white/10 backdrop-blur-sm rounded-lg px-4 py-2">
                <p class="text-xs text-white/70">Total Bids Today</p>
                <p class="text-xl font-bold">{totalActiveBids}</p>
              </div>
              <div class="bg-white/10 backdrop-blur-sm rounded-lg px-4 py-2">
                <p class="text-xs text-white/70">Avg Bid Activity</p>
                <p class="text-xl font-bold">
                  {liveAuctionCount > 0 ? Math.round(totalActiveBids / liveAuctionCount) : 0}/auction
                </p>
              </div>
            </div>
          {/if}
        </div>
        
        <!-- Create Auction Button -->
        {#if canCreateAuction}
          <div class="mt-6 md:mt-0">
            <a 
              href="/auctions/create" 
              class="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-full shadow-lg text-primary-600 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-white transition-all duration-300 hover:shadow-xl transform hover:-translate-y-0.5"
            >
              <svg class="w-5 h-5 {isRTL ? 'ml-2' : 'mr-2'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
              {$t('auction.createAuction')}
            </a>
          </div>
        {/if}
      </div>
      
      <!-- Filter Controls -->
      <div class="mt-8 flex flex-wrap items-center gap-3">
        <!-- Mobile Filters Button -->
        <button
          type="button"
          on:click={toggleMobileFilters}
          class="md:hidden flex items-center justify-center px-4 py-2 rounded-full bg-white/20 backdrop-blur-sm shadow-sm border border-white/30 text-sm font-medium text-white hover:bg-white/30 transition-colors"
        >
          <svg class="w-4 h-4 {isRTL ? 'ml-2' : 'mr-2'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12" />
          </svg>
          <span>{$t('auction.filterAndSort')}</span>
          {#if activeFiltersCount > 0}
            <span class="{isRTL ? 'mr-2' : 'ml-2'} flex items-center justify-center w-5 h-5 text-xs font-semibold rounded-full bg-yellow-400 text-gray-900">
              {activeFiltersCount}
            </span>
          {/if}
        </button>

        <!-- Search Box -->
        <div class="relative flex-grow max-w-md">
          <div class="absolute inset-y-0 {isRTL ? 'right-0 pr-3' : 'left-0 pl-3'} flex items-center pointer-events-none">
            <svg class="h-5 w-5 text-white/50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <input
            type="text"
            bind:value={filters.search}
            on:input={(e) => handleFilterChange('search', e.target.value)}
            placeholder={$t('search.keywordPlaceholder')}
            class="{isRTL ? 'pr-10 pl-4' : 'pl-10 pr-4'} py-2.5 w-full rounded-full bg-white/20 backdrop-blur-sm border border-white/30 text-white placeholder-white/70 focus:bg-white/30 focus:border-white/50 focus:ring-2 focus:ring-white/50 transition-all"
          />
          {#if filters.search}
            <button
              type="button"
              class="absolute inset-y-0 {isRTL ? 'left-0 pl-3' : 'right-0 pr-3'} flex items-center text-white/70 hover:text-white"
              on:click={() => handleFilterChange('search', '')}
              aria-label={$t('search.removeFilter')}
            >
              <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          {/if}
        </div>
        
        <!-- Filter Controls - Desktop Only -->
        <div class="hidden md:flex flex-wrap items-center gap-2">
          <!-- Status Filter Dropdown -->
          <div class="relative filter-dropdown">
            <button
              type="button"
              on:click={() => toggleDropdown('status')}
              class="inline-flex items-center px-4 py-2.5 rounded-full bg-white/20 backdrop-blur-sm shadow-sm border border-white/30 text-sm font-medium text-white hover:bg-white/30 transition-colors {filters.status ? 'bg-white/30 border-white/50' : ''}"
            >
              <span>{filters.status ? `${statusOptions.find(o => o.value === filters.status)?.icon} ${$t(statusOptions.find(o => o.value === filters.status)?.label)}` : $t('auction.filterByStatus')}</span>
              <svg class="w-4 h-4 {isRTL ? 'mr-2' : 'ml-2'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            
            {#if showFilterDropdown.status}
              <div 
                class="absolute {isRTL ? 'right-0' : 'left-0'} mt-2 w-56 rounded-xl shadow-xl bg-white dark:bg-gray-800 ring-1 ring-black ring-opacity-5 focus:outline-none z-10 overflow-hidden"
                transition:fade={{ duration: 150 }}
              >
                <div class="py-1">
                  {#each statusOptions as option}
                    <button
                      class="w-full text-start px-4 py-3 text-sm flex items-center {filters.status === option.value ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300 font-medium' : 'text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700'} transition-colors"
                      on:click={() => handleFilterChange('status', option.value)}
                    >
                      {#if option.icon}
                        <span class="mr-2 text-lg">{option.icon}</span>
                      {/if}
                      {$t(option.label)}
                    </button>
                  {/each}
                </div>
              </div>
            {/if}
          </div>
          
          <!-- Type Filter Dropdown -->
          <div class="relative filter-dropdown">
            <button
              type="button"
              on:click={() => toggleDropdown('type')}
              class="inline-flex items-center px-4 py-2.5 rounded-full bg-white/20 backdrop-blur-sm shadow-sm border border-white/30 text-sm font-medium text-white hover:bg-white/30 transition-colors {filters.type ? 'bg-white/30 border-white/50' : ''}"
            >
              <span>{filters.type ? `${typeOptions.find(o => o.value === filters.type)?.icon} ${$t(typeOptions.find(o => o.value === filters.type)?.label)}` : $t('auction.filterByType')}</span>
              <svg class="w-4 h-4 {isRTL ? 'mr-2' : 'ml-2'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            
            {#if showFilterDropdown.type}
              <div 
                class="absolute {isRTL ? 'right-0' : 'left-0'} mt-2 w-64 rounded-xl shadow-xl bg-white dark:bg-gray-800 ring-1 ring-black ring-opacity-5 focus:outline-none z-10 overflow-hidden"
                transition:fade={{ duration: 150 }}
              >
                <div class="py-1">
                  {#each typeOptions as option}
                    <button
                      class="w-full text-start px-4 py-3 text-sm flex items-center {filters.type === option.value ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300 font-medium' : 'text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700'} transition-colors"
                      on:click={() => handleFilterChange('type', option.value)}
                    >
                      {#if option.icon}
                        <span class="mr-2 text-lg">{option.icon}</span>
                      {/if}
                      {$t(option.label)}
                    </button>
                  {/each}
                </div>
              </div>
            {/if}
          </div>
          
          <!-- Price Filter Dropdown -->
          <div class="relative filter-dropdown">
            <button
              type="button"
              on:click={() => toggleDropdown('price')}
              class="inline-flex items-center px-4 py-2.5 rounded-full bg-white/20 backdrop-blur-sm shadow-sm border border-white/30 text-sm font-medium text-white hover:bg-white/30 transition-colors {(filters.minPrice || filters.maxPrice) ? 'bg-white/30 border-white/50' : ''}"
            >
              <span>
                {#if filters.minPrice || filters.maxPrice}
                  💰 ${filters.minPrice || '0'} - ${filters.maxPrice || '∞'}
                {:else}
                  💰 {$t('search.price')}
                {/if}
              </span>
              <svg class="w-4 h-4 {isRTL ? 'mr-2' : 'ml-2'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            
            {#if showFilterDropdown.price}
              <div 
                class="absolute {isRTL ? 'right-0' : 'left-0'} mt-2 w-72 rounded-xl shadow-xl bg-white dark:bg-gray-800 ring-1 ring-black ring-opacity-5 focus:outline-none z-10 p-5"
                transition:fade={{ duration: 150 }}
              >
                <div class="space-y-4">
                  <div>
                    <label for="min-price" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      {$t('search.min')}
                    </label>
                    <div class="relative rounded-lg">
                      <div class="absolute inset-y-0 {isRTL ? 'right-0 pr-3' : 'left-0 pl-3'} flex items-center pointer-events-none">
                        <span class="text-gray-500 sm:text-sm">$</span>
                      </div>
                      <input
                        id="min-price"
                        type="number"
                        bind:value={filters.minPrice}
                        on:change={(e) => handleFilterChange('minPrice', e.target.value)}
                        placeholder="0"
                        class="block w-full {isRTL ? 'pr-7' : 'pl-7'} py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-sm dark:bg-gray-700 dark:text-white"
                        min="0"
                      />
                    </div>
                  </div>
                  <div>
                    <label for="max-price" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      {$t('search.max')}
                    </label>
                    <div class="relative rounded-lg">
                      <div class="absolute inset-y-0 {isRTL ? 'right-0 pr-3' : 'left-0 pl-3'} flex items-center pointer-events-none">
                        <span class="text-gray-500 sm:text-sm">$</span>
                      </div>
                      <input
                        id="max-price"
                        type="number"
                        bind:value={filters.maxPrice}
                        on:change={(e) => handleFilterChange('maxPrice', e.target.value)}
                        placeholder="100000"
                        class="block w-full {isRTL ? 'pr-7' : 'pl-7'} py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-sm dark:bg-gray-700 dark:text-white"
                        min="0"
                      />
                    </div>
                  </div>
                  <button
                    type="button"
                    class="w-full mt-3 px-4 py-2.5 bg-primary-600 text-white rounded-lg hover:bg-primary-700 text-sm font-medium transition-colors"
                    on:click={() => {
                      showFilterDropdown.price = false;
                    }}
                  >
                    {$t('common.apply')}
                  </button>
                </div>
              </div>
            {/if}
          </div>
          
          <!-- Sort Dropdown -->
          <div class="relative filter-dropdown">
            <button
              type="button"
              on:click={() => toggleDropdown('sort')}
              class="inline-flex items-center px-4 py-2.5 rounded-full bg-white/20 backdrop-blur-sm shadow-sm border border-white/30 text-sm font-medium text-white hover:bg-white/30 transition-colors {filters.sort !== 'newest' ? 'bg-white/30 border-white/50' : ''}"
            >
              <svg class="w-4 h-4 {isRTL ? 'ml-2' : 'mr-2'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12" />
              </svg>
              <span>{sortOptions.find(o => o.value === filters.sort)?.icon} {$t(sortOptions.find(o => o.value === filters.sort)?.label)}</span>
            </button>
            
            {#if showFilterDropdown.sort}
              <div 
                class="absolute {isRTL ? 'right-0' : 'left-0'} mt-2 w-56 rounded-xl shadow-xl bg-white dark:bg-gray-800 ring-1 ring-black ring-opacity-5 focus:outline-none z-10 overflow-hidden"
                transition:fade={{ duration: 150 }}
              >
                <div class="py-1">
                  {#each sortOptions as option}
                    <button
                      class="w-full text-start px-4 py-3 text-sm flex items-center {filters.sort === option.value ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300 font-medium' : 'text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700'} transition-colors"
                      on:click={() => handleFilterChange('sort', option.value)}
                    >
                      <span class="mr-2 text-lg">{option.icon}</span>
                      {$t(option.label)}
                    </button>
                  {/each}
                </div>
              </div>
            {/if}
          </div>
          
          <!-- Clear Filters Button -->
          {#if activeFiltersCount > 0}
            <button
              type="button"
              on:click={clearFilters}
              class="inline-flex items-center px-4 py-2.5 rounded-full bg-red-500/20 backdrop-blur-sm shadow-sm text-sm font-medium text-white hover:bg-red-500/30 transition-colors border border-red-500/30"
            >
              <svg class="w-4 h-4 {isRTL ? 'ml-1' : 'mr-1'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
              {$t('search.clear')} ({activeFiltersCount})
            </button>
          {/if}
        </div>
      </div>
    </div>
  </div>
  
  <!-- Main Content Area -->
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Active Filters Summary -->
    {#if !loading && !error && activeFiltersCount > 0}
      <div class="mb-6 bg-white dark:bg-gray-800 p-4 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
        <div class="flex flex-wrap items-center justify-between">
          <div class="flex flex-wrap gap-2 my-1">
            {#if filters.status}
              <div class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                <span>{statusOptions.find(o => o.value === filters.status)?.icon} {$t(statusOptions.find(o => o.value === filters.status)?.label)}</span>
                <button type="button" class="{isRTL ? 'mr-1.5' : 'ml-1.5'} text-blue-600 dark:text-blue-300 hover:text-blue-800 dark:hover:text-blue-100" 
                  on:click={() => handleFilterChange('status', '')}
                  aria-label={$t('search.removeFilter')}
                >
                  <svg class="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            {/if}
            
            {#if filters.type}
              <div class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200">
                <span>{typeOptions.find(o => o.value === filters.type)?.icon} {$t(typeOptions.find(o => o.value === filters.type)?.label)}</span>
                <button type="button" class="{isRTL ? 'mr-1.5' : 'ml-1.5'} text-indigo-600 dark:text-indigo-300 hover:text-indigo-800 dark:hover:text-indigo-100" 
                  on:click={() => handleFilterChange('type', '')}
                  aria-label={$t('search.removeFilter')}
                >
                  <svg class="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            {/if}
            
            {#if filters.minPrice || filters.maxPrice}
              <div class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                <span>💰 ${filters.minPrice || '0'} - ${filters.maxPrice || '∞'}</span>
                <button type="button" class="{isRTL ? 'mr-1.5' : 'ml-1.5'} text-green-600 dark:text-green-300 hover:text-green-800 dark:hover:text-green-100" 
                  on:click={() => {
                    handleFilterChange('minPrice', '');
                    handleFilterChange('maxPrice', '');
                  }}
                  aria-label={$t('search.removeFilter')}
                >
                  <svg class="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            {/if}
            
            {#if filters.search}
              <div class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200">
                <span>🔍 "{filters.search}"</span>
                <button type="button" class="{isRTL ? 'mr-1.5' : 'ml-1.5'} text-purple-600 dark:text-purple-300 hover:text-purple-800 dark:hover:text-purple-100" 
                  on:click={() => handleFilterChange('search', '')}
                  aria-label={$t('search.removeFilter')}
                >
                  <svg class="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            {/if}
            
            {#if filters.sort !== 'newest'}
              <div class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200">
                <span>{sortOptions.find(o => o.value === filters.sort)?.icon} {$t(sortOptions.find(o => o.value === filters.sort)?.label)}</span>
                <button type="button" class="{isRTL ? 'mr-1.5' : 'ml-1.5'} text-amber-600 dark:text-amber-300 hover:text-amber-800 dark:hover:text-amber-100" 
                  on:click={() => handleFilterChange('sort', 'newest')}
                  aria-label={$t('search.removeFilter')}
                >
                  <svg class="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            {/if}
          </div>
          
          <button
            type="button"
            on:click={clearFilters}
            class="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 flex items-center font-medium"
          >
            <span>{$t('search.clearAll')}</span>
            <svg class="w-4 h-4 {isRTL ? 'mr-1' : 'ml-1'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
    {/if}

    <!-- Main Content Grid with Bid Feed -->
    <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
      <!-- Auctions Grid (3 columns on lg) -->
      <div class="lg:col-span-3">
        {#if loading && !auctions.length}
          <!-- Loading Skeleton -->
          <div in:fade={{ duration: 200 }} out:fade={{ duration: 150 }}>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-6">
              {#each Array(6) as _, i}
                <div class="bg-white dark:bg-gray-800 rounded-xl overflow-hidden shadow-md animate-pulse">
                  <div class="h-56 bg-gray-200 dark:bg-gray-700"></div>
                  <div class="p-5 space-y-3">
                    <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
                    <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
                    <div class="flex justify-between items-center pt-2">
                      <div class="h-6 bg-gray-200 dark:bg-gray-700 rounded w-1/3"></div>
                      <div class="h-8 bg-gray-200 dark:bg-gray-700 rounded w-1/4"></div>
                    </div>
                  </div>
                </div>
              {/each}
            </div>
          </div>
        
        {:else if error}
          <!-- Error State -->
          <div 
            class="bg-white dark:bg-gray-800 shadow-lg rounded-xl p-8"
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
                    onClick={clearFilters}
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
                    onClick={() => loadAuctions()}
                    size="default"
                    class="w-full sm:w-auto"
                  >
                    <svg class="w-4 h-4 {isRTL ? 'ml-2' : 'mr-2'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                    {$t('auction.tryAgain')}
                  </Button>
                </div>
              </div>
            </div>
          </div>

        {:else if !auctions.length}
          <!-- Empty State -->
          <div in:fade={{ duration: 300 }} out:fade={{ duration: 200 }}>
            <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-12 text-center">
              <div class="mx-auto w-24 h-24 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center mb-6">
                <svg class="h-12 w-12 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                </svg>
              </div>
              <h3 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">{$t('auction.noResults')}</h3>
              <p class="text-base text-gray-600 dark:text-gray-300 max-w-md mx-auto mb-8">{$t('auction.tryAdjusting')}</p>
              
              <div class="flex flex-col sm:flex-row gap-3 justify-center">
                {#if activeFiltersCount > 0}
                  <Button
                    variant="outline"
                    onClick={clearFilters}
                    size="default"
                    class="w-full sm:w-auto"
                  >
                    <svg class="w-4 h-4 {isRTL ? 'ml-2' : 'mr-2'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                    {$t('search.clear')}
                  </Button>
                {/if}
                
                <Button
                  variant="primary"
                  href="/properties"
                  size="default"
                  class="w-full sm:w-auto"
                >
                  <svg class="w-4 h-4 {isRTL ? 'ml-2' : 'mr-2'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                  </svg>
                  {$t('auction.browseProperties')}
                </Button>
              </div>
            </div>
          </div>

        {:else}
          <!-- Auctions Grid -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-6">
            {#each auctions as auction, index (auction.id)}
              <div 
                in:fly={{ y: 20, duration: 300, delay: 50 * (index % 6) }} 
                out:fade={{ duration: 200 }}
                class="relative group"
              >
                <AuctionCard {auction} enhanced={true} />
                
                <!-- Quick Bid Overlay (only for live auctions) -->
                {#if auction.status === 'live' && $user}
                  <div class="absolute inset-x-4 bottom-20 opacity-0 group-hover:opacity-100 transition-all duration-300 pointer-events-none group-hover:pointer-events-auto z-10">
                    <button
                      on:click|preventDefault|stopPropagation={() => handleQuickBidClick(auction)}
                      class="w-full bg-primary-600 hover:bg-primary-700 text-white font-semibold py-3 px-4 rounded-lg shadow-xl transform translate-y-4 group-hover:translate-y-0 transition-all duration-300 flex items-center justify-center"
                    >
                      <svg class="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                      </svg>
                      Quick Bid • Min ${((auction.current_bid || auction.starting_bid) + (auction.minimum_increment || 100)).toLocaleString()}
                    </button>
                  </div>
                {/if}
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
      </div>
      
      <!-- Sidebar - Live Bid Feed -->
      <div class="lg:col-span-1">
        {#if showBidFeed && liveAuctionCount > 0}
          <div class="sticky top-6">
            <RealtimeBidFeed maxItems={8} />
            
            <!-- Quick Stats -->
            <div class="mt-6 bg-white dark:bg-gray-800 rounded-lg shadow-md p-4">
              <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-3">
                📊 Live Stats
              </h3>
              <div class="space-y-3">
                <div class="flex justify-between items-center">
                  <span class="text-sm text-gray-600 dark:text-gray-400">Active Auctions</span>
                  <span class="text-lg font-bold text-primary-600 dark:text-primary-400">{liveAuctionCount}</span>
                </div>
                <div class="flex justify-between items-center">
                  <span class="text-sm text-gray-600 dark:text-gray-400">Total Bids</span>
                  <span class="text-lg font-bold text-green-600 dark:text-green-400">{totalActiveBids}</span>
                </div>
                <div class="flex justify-between items-center">
                  <span class="text-sm text-gray-600 dark:text-gray-400">Avg per Auction</span>
                  <span class="text-lg font-bold text-blue-600 dark:text-blue-400">
                    {liveAuctionCount > 0 ? Math.round(totalActiveBids / liveAuctionCount) : 0}
                  </span>
                </div>
              </div>
            </div>
          </div>
        {/if}
      </div>
    </div>
    
    <!-- Create Auction Info Box for Non-Authorized Users -->
    {#if !canCreateAuction && !loading && auctions.length > 0 && $user}
      <div class="mt-10 bg-gradient-to-r from-primary-50 to-secondary-50 dark:from-primary-900/20 dark:to-secondary-900/20 border border-primary-200 dark:border-primary-800 rounded-xl shadow-md p-8">
        <div class="sm:flex sm:items-center sm:justify-between">
          <div class="max-w-xl">
            <h3 class="text-xl font-bold text-gray-900 dark:text-white">
              🏠 {$t('auction.createNewPrompt')}
            </h3>
            <p class="mt-3 text-base text-gray-600 dark:text-gray-300">
              {$t('property.unauthorizedMessage')}
            </p>
          </div>
          <div class="mt-5 sm:mt-0 sm:ml-6">
            <Button
              href="/properties"
              variant="primary"
              size="large"
              class="w-full sm:w-auto shadow-lg hover:shadow-xl transition-all"
            >
              <div class="flex items-center">
                <svg class="w-5 h-5 {isRTL ? 'ml-2' : 'mr-2'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                </svg>
                {$t('auction.browseProperties')}
              </div>
            </Button>
          </div>
        </div>
      </div>
    {/if}
  </div>
  
  <!-- Enhanced Mobile Filters Drawer -->
  {#if showMobileFilters}
    <div class="fixed inset-0 z-40 flex md:hidden" in:fade={{ duration: 200 }} out:fade={{ duration: 150 }}>
      <!-- Backdrop -->
      <div 
        class="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm"
        on:click={toggleMobileFilters} 
        on:keydown={(e) => { if (e.key === 'Enter' || e.key === ' ') toggleMobileFilters(); }}
        role="button"
        tabindex="0"
        aria-label={$t('auction.closeFilters')}
      ></div>
      
      <!-- Drawer panel -->
      <div 
        class="relative max-w-sm w-full h-full bg-white dark:bg-gray-800 shadow-2xl flex flex-col overflow-y-auto {isRTL ? 'right-0' : 'left-0'}"
        in:slide={{ duration: 300, axis: 'x' }}
        out:slide={{ duration: 250, axis: 'x', easing: x => 1 - Math.pow(1 - x, 3) }}
      >
        <div class="px-4 py-5 flex items-center justify-between border-b border-gray-200 dark:border-gray-700 bg-primary-600 text-white">
          <h2 class="text-lg font-semibold flex items-center">
            <svg class="w-5 h-5 {isRTL ? 'ml-2' : 'mr-2'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12" />
            </svg>
            {$t('auction.filterAndSort')}
          </h2>
          <button
            type="button"
            class="rounded-full p-2 text-white hover:bg-white/20 transition-colors"
            on:click={toggleMobileFilters}
            aria-label={$t('auction.closeFilters')}
          >
            <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <!-- Mobile Filter Sections -->
        <div class="overflow-y-auto px-4 flex-1">
          <!-- Search -->
          <div class="py-5 border-b border-gray-200 dark:border-gray-700">
            <h3 class="text-base font-medium text-gray-900 dark:text-white mb-3 flex items-center">
              <svg class="h-5 w-5 {isRTL ? 'ml-2' : 'mr-2'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              {$t('search.keyword')}
            </h3>
            <div class="relative rounded-lg">
              <input
                type="text"
                bind:value={filters.search}
                on:input={(e) => handleFilterChange('search', e.target.value)}
                placeholder={$t('search.keywordPlaceholder')}
                class="block w-full {isRTL ? 'pr-4 pl-12' : 'pl-4 pr-12'} py-3 border border-gray-300 dark:border-gray-600 rounded-lg placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-base dark:bg-gray-700 dark:text-white"
              />
              {#if filters.search}
                <div class="absolute inset-y-0 {isRTL ? 'left-0 pl-3' : 'right-0 pr-3'} flex items-center">
                  <button 
                    class="text-gray-400 hover:text-gray-500 dark:text-gray-300 dark:hover:text-white"
                    on:click={() => handleFilterChange('search', '')}
                    aria-label={$t('search.removeFilter')}
                  >
                    <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              {/if}
            </div>
          </div>
          
          <!-- Status Filter -->
          <div class="py-5 border-b border-gray-200 dark:border-gray-700">
            <h3 class="text-base font-medium text-gray-900 dark:text-white mb-3 flex items-center">
              <svg class="h-5 w-5 {isRTL ? 'ml-2' : 'mr-2'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {$t('auction.filterByStatus')}
            </h3>
            <div class="grid grid-cols-2 gap-2">
              {#each statusOptions as option}
                <button
                  class="flex items-center justify-center px-3 py-3 border text-sm font-medium rounded-lg transition-colors
                    {filters.status === option.value 
                      ? 'border-primary-400 bg-primary-50 text-primary-700 dark:border-primary-500 dark:bg-primary-900/20 dark:text-primary-300' 
                      : 'border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'}"
                  on:click={() => handleFilterChange('status', option.value)}
                >
                  {#if option.icon}
                    <span class="mr-1 text-lg">{option.icon}</span>
                  {/if}
                  <span>{$t(option.label)}</span>
                </button>
              {/each}
            </div>
          </div>
          
          <!-- Type Filter -->
          <div class="py-5 border-b border-gray-200 dark:border-gray-700">
            <h3 class="text-base font-medium text-gray-900 dark:text-white mb-3 flex items-center">
              <svg class="h-5 w-5 {isRTL ? 'ml-2' : 'mr-2'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
              </svg>
              {$t('auction.filterByType')}
            </h3>
            <div class="space-y-2">
              {#each typeOptions as option}
                <button
                  class="w-full flex items-center px-3 py-3 border text-sm font-medium rounded-lg transition-colors
                    {filters.type === option.value 
                      ? 'border-primary-400 bg-primary-50 text-primary-700 dark:border-primary-500 dark:bg-primary-900/20 dark:text-primary-300' 
                      : 'border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'}"
                  on:click={() => handleFilterChange('type', option.value)}
                >
                  {#if option.icon}
                    <span class="mr-2 text-lg">{option.icon}</span>
                  {/if}
                  <span>{$t(option.label)}</span>
                </button>
              {/each}
            </div>
          </div>
          
          <!-- Sort Filter -->
          <div class="py-5 border-b border-gray-200 dark:border-gray-700">
            <h3 class="text-base font-medium text-gray-900 dark:text-white mb-3 flex items-center">
              <svg class="h-5 w-5 {isRTL ? 'ml-2' : 'mr-2'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12" />
              </svg>
              {$t('search.sort')}
            </h3>
            <div class="grid grid-cols-1 gap-2">
              {#each sortOptions as option}
                <button
                  class="flex items-center justify-between px-4 py-3 border text-sm font-medium rounded-lg transition-colors
                    {filters.sort === option.value 
                      ? 'border-primary-400 bg-primary-50 text-primary-700 dark:border-primary-500 dark:bg-primary-900/20 dark:text-primary-300' 
                      : 'border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'}"
                  on:click={() => handleFilterChange('sort', option.value)}
                >
                  <span class="flex items-center">
                    <span class="mr-2 text-lg">{option.icon}</span>
                    {$t(option.label)}
                  </span>
                  
                  {#if filters.sort === option.value}
                    <svg class="h-5 w-5 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                  {/if}
                </button>
              {/each}
            </div>
          </div>
          
          <!-- Price Range Filter -->
          <div class="py-5 border-b border-gray-200 dark:border-gray-700">
            <h3 class="text-base font-medium text-gray-900 dark:text-white mb-3 flex items-center">
              <svg class="h-5 w-5 {isRTL ? 'ml-2' : 'mr-2'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {$t('search.price')}
            </h3>
            
            <div class="space-y-4 mt-4">
              <div class="flex items-center gap-4">
                <div class="flex-1">
                  <label for="mobile-min-price" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    {$t('search.min')}
                  </label>
                  <div class="relative rounded-lg">
                    <div class="absolute inset-y-0 {isRTL ? 'right-0 pr-3' : 'left-0 pl-3'} flex items-center pointer-events-none">
                      <span class="text-gray-500 sm:text-sm">$</span>
                    </div>
                    <input
                      id="mobile-min-price"
                      type="number"
                      bind:value={filters.minPrice}
                      on:change={(e) => handleFilterChange('minPrice', e.target.value)}
                      placeholder="0"
                      class="block w-full {isRTL ? 'pr-7' : 'pl-7'} py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-sm dark:bg-gray-700 dark:text-white"
                      min="0"
                    />
                  </div>
                </div>
                
                <div class="flex-1">
                  <label for="mobile-max-price" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    {$t('search.max')}
                  </label>
                  <div class="relative rounded-lg">
                    <div class="absolute inset-y-0 {isRTL ? 'right-0 pr-3' : 'left-0 pl-3'} flex items-center pointer-events-none">
                      <span class="text-gray-500 sm:text-sm">$</span>
                    </div>
                    <input
                      id="mobile-max-price"
                      type="number"
                      bind:value={filters.maxPrice}
                      on:change={(e) => handleFilterChange('maxPrice', e.target.value)}
                      placeholder="100000"
                      class="block w-full {isRTL ? 'pr-7' : 'pl-7'} py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-sm dark:bg-gray-700 dark:text-white"
                      min="0"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Footer Actions -->
        <div class="p-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 shadow-inner">
          <div class="grid grid-cols-2 gap-3">
            <button
              type="button"
              on:click={clearFilters}
              class="flex justify-center items-center px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm text-sm font-medium text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              disabled={!activeFiltersCount}
              aria-label={$t('search.clearAllFilters')}
            >
              <svg class="w-4 h-4 {isRTL ? 'ml-2' : 'mr-2'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
              {$t('search.clear')}
            </button>
            
            <button
              type="button"
              on:click={toggleMobileFilters}
              class="flex justify-center items-center px-4 py-3 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors"
            >
              <svg class="w-4 h-4 {isRTL ? 'ml-2' : 'mr-2'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              {$t('common.apply')}
              {#if activeFiltersCount > 0}
                <span class="{isRTL ? 'mr-1' : 'ml-1'}">({activeFiltersCount})</span>
              {/if}
            </button>
          </div>
        </div>
      </div>
    </div>
  {/if}
</div>

<!-- Quick Bid Modal -->
<QuickBidPopover 
  auction={selectedAuctionForQuickBid}
  bind:show={showQuickBidModal}
  on:bidPlaced={handleBidPlaced}
  on:close={() => {
    showQuickBidModal = false;
    selectedAuctionForQuickBid = null;
  }}
/>

<style>
  /* Apply RTL-specific styles */
  :global(.rtl) {
    direction: rtl;
    text-align: right;
  }
  
  /* Animation for badges */
  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(-4px); }
    to { opacity: 1; transform: translateY(0); }
  }
  
  .inline-flex {
    animation: fadeIn 0.2s ease-out;
  }
  
  /* Custom scrollbar for filters */
  .overflow-y-auto::-webkit-scrollbar {
    width: 4px;
  }
  
  .overflow-y-auto::-webkit-scrollbar-track {
    background: transparent;
  }
  
  .overflow-y-auto::-webkit-scrollbar-thumb {
    background-color: rgba(156, 163, 175, 0.5);
    border-radius: 2px;
  }
  
  .overflow-y-auto::-webkit-scrollbar-thumb:hover {
    background-color: rgba(156, 163, 175, 0.7);
  }
</style>