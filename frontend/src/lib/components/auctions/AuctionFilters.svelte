<!-- src/lib/components/auction/AuctionFilters.svelte -->
<script>
    import { createEventDispatcher } from 'svelte';
    import { t } from '$lib/i18n';
    
    // Props - initial filter values
    export let filters = {
      status: '',
      property_type: '',
      auction_type: '',
      city: '',
      min_price: '',
      max_price: '',
      sort_by: 'start_date',
      order: 'desc'
    };
    
    // Filter options
    const statusOptions = [
      { value: '', label: $t('general.all') },
      { value: 'active', label: $t('auctions.status.active') },
      { value: 'pending', label: $t('auctions.status.pending') },
      { value: 'extended', label: $t('auctions.status.extended') },
      { value: 'closed', label: $t('auctions.status.closed') },
      { value: 'sold', label: $t('auctions.status.sold') }
    ];
    
    const propertyTypeOptions = [
      { value: '', label: $t('general.all') },
      { value: 'land', label: $t('properties.types.land') },
      { value: 'apartment', label: $t('properties.types.apartment') },
      { value: 'villa', label: $t('properties.types.villa') },
      { value: 'commercial', label: $t('properties.types.commercial') },
      { value: 'industrial', label: $t('properties.types.industrial') },
      { value: 'mixed_use', label: $t('properties.types.mixed_use') }
    ];
    
    const auctionTypeOptions = [
      { value: '', label: $t('general.all') },
      { value: 'public', label: $t('auctions.types.public') },
      { value: 'private', label: $t('auctions.types.private') },
      { value: 'online', label: $t('auctions.types.online') },
      { value: 'onsite', label: $t('auctions.types.onsite') },
      { value: 'hybrid', label: $t('auctions.types.hybrid') }
    ];
    
    const sortOptions = [
      { value: 'start_date', label: $t('auctions.sort_options.newest') },
      { value: 'end_date', label: $t('auctions.sort_options.ending_soon') },
      { value: 'starting_price', label: $t('auctions.sort_options.price_low') },
      { value: 'bid_count', label: $t('auctions.sort_options.most_bids') }
    ];
    
    // State
    let isExpanded = false;
    let showMobileFilters = false;
    let localFilters = { ...filters };
    let isSearching = false;
    
    // Event dispatcher
    const dispatch = createEventDispatcher();
    
    // Apply filters
    function applyFilters() {
      isSearching = true;
      dispatch('filter', localFilters);
      
      // Close mobile filters if open
      if (showMobileFilters) {
        showMobileFilters = false;
      }
      
      // Reset searching state after a short delay
      setTimeout(() => {
        isSearching = false;
      }, 500);
    }
    
    // Reset filters
    function resetFilters() {
      localFilters = {
        status: '',
        property_type: '',
        auction_type: '',
        city: '',
        min_price: '',
        max_price: '',
        sort_by: 'start_date',
        order: 'desc'
      };
      
      applyFilters();
    }
    
    // Handle sort change
    function handleSortChange(value) {
      const [sortBy, order] = value.split('-');
      localFilters.sort_by = sortBy;
      localFilters.order = order;
      applyFilters();
    }
    
    // Toggle order (asc/desc)
    function toggleOrder() {
      localFilters.order = localFilters.order === 'asc' ? 'desc' : 'asc';
      applyFilters();
    }
    
    // Derived values
    $: sortValue = `${localFilters.sort_by}-${localFilters.order}`;
    $: activeFiltersCount = Object.entries(localFilters).filter(([key, value]) => {
      return value && key !== 'sort_by' && key !== 'order';
    }).length;
  </script>
  
  <!-- Desktop Filters -->
  <div class="mb-6 hidden rounded-xl bg-cosmos-bg-light bg-opacity-30 p-4 backdrop-blur-sm md:block">
    <div class="flex items-center justify-between">
      <div class="flex items-center space-x-4">
        <h3 class="text-lg font-bold text-cosmos-text">{$t('auctions.filter_auctions')}</h3>
        
        {#if activeFiltersCount > 0}
          <span class="rounded-full bg-primary bg-opacity-20 px-2 py-1 text-xs font-medium text-primary">
            {activeFiltersCount} {$t('general.active_filters')}
          </span>
        {/if}
      </div>
      
      <button 
        class="flex items-center text-sm text-cosmos-text-muted hover:text-primary"
        on:click={() => isExpanded = !isExpanded}
      >
        {isExpanded ? $t('general.less') : $t('general.more')}
        <svg 
          class="ml-1 h-4 w-4 transform transition-transform {isExpanded ? 'rotate-180' : ''}"
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
      </button>
    </div>
    
    <!-- Basic Filters (Always Visible) -->
    <div class="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-3">
      <!-- Status Filter -->
      <div>
        <label for="status" class="mb-1 block text-sm font-medium text-cosmos-text-muted">
          {$t('auctions.filter_options.status')}
        </label>
        <select
          id="status"
          bind:value={localFilters.status}
          on:change={applyFilters}
          class="w-full rounded-lg border border-cosmos-bg-light bg-cosmos-bg p-2 text-cosmos-text outline-none focus:border-primary"
        >
          {#each statusOptions as option}
            <option value={option.value}>{option.label}</option>
          {/each}
        </select>
      </div>
      
      <!-- Property Type Filter -->
      <div>
        <label for="property_type" class="mb-1 block text-sm font-medium text-cosmos-text-muted">
          {$t('auctions.filter_options.property_type')}
        </label>
        <select
          id="property_type"
          bind:value={localFilters.property_type}
          on:change={applyFilters}
          class="w-full rounded-lg border border-cosmos-bg-light bg-cosmos-bg p-2 text-cosmos-text outline-none focus:border-primary"
        >
          {#each propertyTypeOptions as option}
            <option value={option.value}>{option.label}</option>
          {/each}
        </select>
      </div>
      
      <!-- Sorting -->
      <div>
        <label for="sort_by" class="mb-1 block text-sm font-medium text-cosmos-text-muted">
          {$t('general.sort')}
        </label>
        <div class="flex">
          <select
            id="sort_by"
            bind:value={sortValue}
            on:change={e => handleSortChange(e.target.value)}
            class="flex-grow rounded-l-lg border border-cosmos-bg-light bg-cosmos-bg p-2 text-cosmos-text outline-none focus:border-primary"
          >
            {#each sortOptions as option}
              <option value={`${option.value}-asc`}>{option.label} ({$t('general.asc')})</option>
              <option value={`${option.value}-desc`}>{option.label} ({$t('general.desc')})</option>
            {/each}
          </select>
          <button
            on:click={toggleOrder}
            class="flex items-center justify-center rounded-r-lg border border-l-0 border-cosmos-bg-light bg-cosmos-bg px-3 text-cosmos-text-muted hover:text-primary"
            title={localFilters.order === 'asc' ? $t('general.sort_descending') : $t('general.sort_ascending')}
          >
            <svg 
              class="h-4 w-4 transform {localFilters.order === 'asc' ? 'rotate-180' : ''}"
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </button>
        </div>
      </div>
    </div>
    
    <!-- Advanced Filters (Expandable) -->
    {#if isExpanded}
      <div class="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-3" transition:slide={{ duration: 300 }}>
        <!-- Auction Type Filter -->
        <div>
          <label for="auction_type" class="mb-1 block text-sm font-medium text-cosmos-text-muted">
            {$t('auctions.filter_options.auction_type')}
          </label>
          <select
            id="auction_type"
            bind:value={localFilters.auction_type}
            on:change={applyFilters}
            class="w-full rounded-lg border border-cosmos-bg-light bg-cosmos-bg p-2 text-cosmos-text outline-none focus:border-primary"
          >
            {#each auctionTypeOptions as option}
              <option value={option.value}>{option.label}</option>
            {/each}
          </select>
        </div>
        
        <!-- City Filter -->
        <div>
          <label for="city" class="mb-1 block text-sm font-medium text-cosmos-text-muted">
            {$t('auctions.filter_options.location')}
          </label>
          <input
            type="text"
            id="city"
            bind:value={localFilters.city}
            on:change={applyFilters}
            placeholder={$t('properties.property_city')}
            class="w-full rounded-lg border border-cosmos-bg-light bg-cosmos-bg p-2 text-cosmos-text outline-none focus:border-primary"
          />
        </div>
        
        <!-- Price Range -->
        <div>
          <label class="mb-1 block text-sm font-medium text-cosmos-text-muted">
            {$t('auctions.filter_options.price_range')}
          </label>
          <div class="flex space-x-2">
            <input
              type="number"
              bind:value={localFilters.min_price}
              on:change={applyFilters}
              placeholder={$t('general.min')}
              class="w-1/2 rounded-lg border border-cosmos-bg-light bg-cosmos-bg p-2 text-cosmos-text outline-none focus:border-primary"
            />
            <input
              type="number"
              bind:value={localFilters.max_price}
              on:change={applyFilters}
              placeholder={$t('general.max')}
              class="w-1/2 rounded-lg border border-cosmos-bg-light bg-cosmos-bg p-2 text-cosmos-text outline-none focus:border-primary"
            />
          </div>
        </div>
      </div>
      
      <!-- Filter Actions -->
      <div class="mt-4 flex justify-end space-x-2">
        <button
          on:click={resetFilters}
          class="rounded-lg border border-cosmos-bg-light px-4 py-2 text-sm text-cosmos-text-muted hover:text-cosmos-text"
        >
          {$t('general.reset')}
        </button>
        
        <button
          on:click={applyFilters}
          class="rounded-lg bg-primary px-4 py-2 text-sm text-white hover:bg-primary-dark"
        >
          {$t('general.apply')}
        </button>
      </div>
    {/if}
  </div>
  
  <!-- Mobile Filters Toggle -->
  <div class="mb-4 flex items-center justify-between md:hidden">
    <button
      on:click={() => showMobileFilters = !showMobileFilters}
      class="flex items-center rounded-lg bg-cosmos-bg-light px-3 py-2 text-sm text-cosmos-text"
    >
      <svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
      </svg>
      {$t('general.filter')}
      
      {#if activeFiltersCount > 0}
        <span class="ml-2 rounded-full bg-primary bg-opacity-20 px-2 py-0.5 text-xs font-medium text-primary">
          {activeFiltersCount}
        </span>
      {/if}
    </button>
    
    <!-- Mobile Sort -->
    <div class="relative">
      <select
        bind:value={sortValue}
        on:change={e => handleSortChange(e.target.value)}
        class="rounded-lg border border-cosmos-bg-light bg-cosmos-bg py-2 pl-8 pr-8 text-sm text-cosmos-text"
      >
        {#each sortOptions as option}
          <option value={`${option.value}-asc`}>{option.label} ↑</option>
          <option value={`${option.value}-desc`}>{option.label} ↓</option>
        {/each}
      </select>
      <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-2">
        <svg class="h-4 w-4 text-cosmos-text-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
        </svg>
      </div>
    </div>
  </div>
  
  <!-- Mobile Filters Modal -->
  {#if showMobileFilters}
    <div class="fixed inset-0 z-modal flex items-end bg-cosmos-bg-dark bg-opacity-80 p-4 md:hidden" transition:fade={{ duration: 200 }}>
      <div 
        class="w-full rounded-t-xl bg-cosmos-bg p-4"
        transition:slide={{ duration: 300 }}
      >
        <div class="flex items-center justify-between border-b border-cosmos-bg-light pb-4">
          <h3 class="text-lg font-bold text-cosmos-text">{$t('auctions.filter_auctions')}</h3>
          
          <button
            on:click={() => showMobileFilters = false}
            class="rounded-full p-1 text-cosmos-text-muted hover:bg-cosmos-bg-light hover:text-cosmos-text"
          >
            <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <div class="max-h-[70vh] overflow-y-auto py-4">
          <div class="space-y-4">
            <!-- Status Filter -->
            <div>
              <label for="m-status" class="mb-1 block text-sm font-medium text-cosmos-text-muted">
                {$t('auctions.filter_options.status')}
              </label>
              <select
                id="m-status"
                bind:value={localFilters.status}
                class="w-full rounded-lg border border-cosmos-bg-light bg-cosmos-bg-light p-3 text-cosmos-text outline-none focus:border-primary"
              >
                {#each statusOptions as option}
                  <option value={option.value}>{option.label}</option>
                {/each}
              </select>
            </div>
            
            <!-- Property Type Filter -->
            <div>
              <label for="m-property_type" class="mb-1 block text-sm font-medium text-cosmos-text-muted">
                {$t('auctions.filter_options.property_type')}
              </label>
              <select
                id="m-property_type"
                bind:value={localFilters.property_type}
                class="w-full rounded-lg border border-cosmos-bg-light bg-cosmos-bg-light p-3 text-cosmos-text outline-none focus:border-primary"
              >
                {#each propertyTypeOptions as option}
                  <option value={option.value}>{option.label}</option>
                {/each}
              </select>
            </div>
            
            <!-- Auction Type Filter -->
            <div>
              <label for="m-auction_type" class="mb-1 block text-sm font-medium text-cosmos-text-muted">
                {$t('auctions.filter_options.auction_type')}
              </label>
              <select
                id="m-auction_type"
                bind:value={localFilters.auction_type}
                class="w-full rounded-lg border border-cosmos-bg-light bg-cosmos-bg-light p-3 text-cosmos-text outline-none focus:border-primary"
              >
                {#each auctionTypeOptions as option}
                  <option value={option.value}>{option.label}</option>
                {/each}
              </select>
            </div>
            
            <!-- City Filter -->
            <div>
              <label for="m-city" class="mb-1 block text-sm font-medium text-cosmos-text-muted">
                {$t('auctions.filter_options.location')}
              </label>
              <input
                type="text"
                id="m-city"
                bind:value={localFilters.city}
                placeholder={$t('properties.property_city')}
                class="w-full rounded-lg border border-cosmos-bg-light bg-cosmos-bg-light p-3 text-cosmos-text outline-none focus:border-primary"
              />
            </div>
            
            <!-- Price Range -->
            <div>
              <label class="mb-1 block text-sm font-medium text-cosmos-text-muted">
                {$t('auctions.filter_options.price_range')}
              </label>
              <div class="flex space-x-2">
                <input
                  type="number"
                  bind:value={localFilters.min_price}
                  placeholder={$t('general.min')}
                  class="w-1/2 rounded-lg border border-cosmos-bg-light bg-cosmos-bg-light p-3 text-cosmos-text outline-none focus:border-primary"
                />
                <input
                  type="number"
                  bind:value={localFilters.max_price}
                  placeholder={$t('general.max')}
                  class="w-1/2 rounded-lg border border-cosmos-bg-light bg-cosmos-bg-light p-3 text-cosmos-text outline-none focus:border-primary"
                />
              </div>
            </div>
          </div>
        </div>
        
        <!-- Filter Actions -->
        <div class="mt-4 flex space-x-2 border-t border-cosmos-bg-light pt-4">
          <button
            on:click={resetFilters}
            class="flex-1 rounded-lg border border-cosmos-bg-light py-3 text-cosmos-text-muted hover:text-cosmos-text"
          >
            {$t('general.reset')}
          </button>
          
          <button
            on:click={applyFilters}
            class="flex-1 rounded-lg bg-primary py-3 text-white hover:bg-primary-dark"
            disabled={isSearching}
          >
            {#if isSearching}
              <span class="flex items-center justify-center space-x-2">
                <span class="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent"></span>
                <span>{$t('general.applying')}</span>
              </span>
            {:else}
              {$t('general.apply_filters')}
            {/if}
          </button>
        </div>
      </div>
    </div>
  {/if}