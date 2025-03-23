<!-- src/lib/components/auctions/AuctionFilters.svelte -->
<script>
  import { createEventDispatcher } from 'svelte';
  import { t, isRTL } from '$lib/i18n';
  
  // Components
  import { 
    TextField, 
    Select, 
    RangeSlider, 
    DatePicker,
    Switch, 
    Button 
  } from '$lib/components/ui';
  
  // Props
  export let currentFilters = {};
  export let isExpanded = false;
  export let showResetButton = true;
  export let showFilterButton = true;
  export let compact = false;
  
  // Local state
  let filters = { ...currentFilters };
  
  // Event dispatcher
  const dispatch = createEventDispatcher();
  
  // Property type options
  const propertyTypeOptions = [
    { value: '', label: t('general.all') },
    { value: 'land', label: t('properties.types.land') },
    { value: 'apartment', label: t('properties.types.apartment') },
    { value: 'villa', label: t('properties.types.villa') },
    { value: 'commercial', label: t('properties.types.commercial') },
    { value: 'building', label: t('properties.types.building') },
    { value: 'farm', label: t('properties.types.farm') },
    { value: 'industrial', label: t('properties.types.industrial') }
  ];
  
  // Auction type options
  const auctionTypeOptions = [
    { value: '', label: t('general.all') },
    { value: 'public', label: t('auctions.types.public') },
    { value: 'private', label: t('auctions.types.private') },
    { value: 'online', label: t('auctions.types.online') },
    { value: 'onsite', label: t('auctions.types.onsite') },
    { value: 'hybrid', label: t('auctions.types.hybrid') }
  ];
  
  // Auction status options
  const statusOptions = [
    { value: '', label: t('general.all') },
    { value: 'active', label: t('auctions.status.active') },
    { value: 'upcoming', label: t('auctions.status.upcoming') },
    { value: 'closed', label: t('auctions.status.closed') },
    { value: 'sold', label: t('auctions.status.sold') }
  ];
  
  // Sorting options
  const sortOptions = [
    { value: 'start_date', label: t('auctions.sort_options.newest') },
    { value: 'end_date', label: t('auctions.sort_options.ending_soon') },
    { value: 'starting_price', label: t('auctions.sort_options.price_low') },
    { value: '-starting_price', label: t('auctions.sort_options.price_high') },
    { value: 'bid_count', label: t('auctions.sort_options.most_bids') }
  ];
  
  // Handle filter changes
  function applyFilters() {
    // Remove empty filters
    const cleanedFilters = {};
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== '' && value !== null && value !== undefined) {
        cleanedFilters[key] = value;
      }
    });
    
    // Dispatch event with cleaned filters
    dispatch('change', cleanedFilters);
  }
  
  // Reset filters
  function resetFilters() {
    filters = {
      status: '',
      auction_type: '',
      property_type: '',
      min_price: '',
      max_price: '',
      city: '',
      district: '',
      is_featured: null,
      sort_by: 'start_date',
      order: 'desc'
    };
    
    // Apply reset filters
    applyFilters();
  }
  
  // Close filters
  function close() {
    dispatch('close');
  }
  
  // Toggle expanded state
  function toggleExpanded() {
    isExpanded = !isExpanded;
  }
  
  function handleKeyDown(event) {
    if (event.key === 'Enter') {
      applyFilters();
    }
  }
</script>

<div 
  class="auction-filters bg-white dark:bg-neutral-800 rounded-xl border border-neutral-200 dark:border-neutral-700 shadow-sm overflow-hidden"
  on:keydown={handleKeyDown}
>
  <!-- Filters header -->
  <div class="flex justify-between items-center p-4 border-b border-neutral-200 dark:border-neutral-700">
    <h3 class="text-lg font-medium text-neutral-800 dark:text-neutral-200">
      {t('auctions.filter_auctions')}
    </h3>
    
    <div class="flex gap-2">
      {#if showResetButton}
        <button 
          type="button" 
          class="text-neutral-500 hover:text-neutral-700 dark:text-neutral-400 dark:hover:text-neutral-300"
          on:click={resetFilters}
          aria-label={t('general.reset')}
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd" />
          </svg>
        </button>
      {/if}
      
      <button 
        type="button" 
        class="text-neutral-500 hover:text-neutral-700 dark:text-neutral-400 dark:hover:text-neutral-300"
        on:click={close}
        aria-label={t('general.close')}
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
        </svg>
      </button>
    </div>
  </div>
  
  <div class="p-4">
    <!-- Main filters -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
      <!-- Status -->
      <div>
        <Select
          label={t('auctions.status')}
          options={statusOptions}
          bind:value={filters.status}
          placeholder={t('general.select_status')}
        />
      </div>
      
      <!-- Auction type -->
      <div>
        <Select
          label={t('auctions.auction_type')}
          options={auctionTypeOptions}
          bind:value={filters.auction_type}
          placeholder={t('auctions.select_type')}
        />
      </div>
      
      <!-- Property type -->
      <div>
        <Select
          label={t('properties.property_type')}
          options={propertyTypeOptions}
          bind:value={filters.property_type}
          placeholder={t('properties.select_type')}
        />
      </div>
    </div>
    
    <!-- Price range -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
      <TextField
        label={t('general.min_price')}
        bind:value={filters.min_price}
        placeholder={t('general.min_price')}
        type="number"
        min="0"
        prefix="SAR"
      />
      
      <TextField
        label={t('general.max_price')}
        bind:value={filters.max_price}
        placeholder={t('general.max_price')}
        type="number"
        min="0"
        prefix="SAR"
      />
    </div>
    
    <!-- Location -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
      <TextField
        label={t('general.city')}
        bind:value={filters.city}
        placeholder={t('general.enter_city')}
      />
      
      <TextField
        label={t('general.district')}
        bind:value={filters.district}
        placeholder={t('general.enter_district')}
      />
    </div>
    
    <!-- Additional filters toggle -->
    <button 
      type="button"
      class="text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300 flex items-center mb-4"
      on:click={toggleExpanded}
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
        <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
      </svg>
      {isExpanded ? t('general.less_filters') : t('general.more_filters')}
    </button>
    
    <!-- Advanced filters (expandable) -->
    {#if isExpanded}
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4 border-t border-neutral-200 dark:border-neutral-700 pt-4">
        <!-- Date range -->
        <DatePicker
          label={t('auctions.start_date_from')}
          bind:value={filters.start_date_from}
          placeholder={t('general.select_date')}
        />
        
        <DatePicker
          label={t('auctions.start_date_to')}
          bind:value={filters.start_date_to}
          placeholder={t('general.select_date')}
        />
        
        <DatePicker
          label={t('auctions.end_date_from')}
          bind:value={filters.end_date_from}
          placeholder={t('general.select_date')}
        />
        
        <DatePicker
          label={t('auctions.end_date_to')}
          bind:value={filters.end_date_to}
          placeholder={t('general.select_date')}
        />
        
        <!-- Featured toggle -->
        <div class="md:col-span-2">
          <Switch
            label={t('general.featured_only')}
            bind:checked={filters.is_featured}
          />
        </div>
        
        <!-- Sort options -->
        <div class="md:col-span-2">
          <Select
            label={t('general.sort_by')}
            options={sortOptions}
            bind:value={filters.sort_by}
          />
        </div>
      </div>
    {/if}
    
    <!-- Filter actions -->
    {#if showFilterButton}
      <div class="flex justify-end">
        <Button 
          variant="primary" 
          on:click={applyFilters}
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M3 3a1 1 0 011-1h12a1 1 0 011 1v3a1 1 0 01-.293.707L12 11.414V15a1 1 0 01-.293.707l-2 2A1 1 0 018 17v-5.586L3.293 6.707A1 1 0 013 6V3z" clip-rule="evenodd" />
          </svg>
          {t('general.apply_filters')}
        </Button>
      </div>
    {/if}
  </div>
</div>