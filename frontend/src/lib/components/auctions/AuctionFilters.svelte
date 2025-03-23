<!-- src/routes/auctions/components/AuctionFilters.svelte -->
<script>
  import { createEventDispatcher } from 'svelte';
  import { t } from '$lib/i18n';
  import { 
    TextInput, 
    Dropdown, 
    NumericInput, 
    DatePicker,
    Switch, 
    Button, 
    Icon 
  } from '$lib/components/ui';
  
  // Props
  export let currentFilters = {};
  
  // Local state
  let filters = { ...currentFilters };
  let isExpanded = false;
  
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
</script>

<div class="auction-filters bg-white rounded-lg border p-5 shadow-sm">
  <!-- Filters header -->
  <div class="flex justify-between items-center mb-4">
    <h3 class="text-lg font-medium">
      {t('auctions.filter_auctions')}
    </h3>
    
    <div class="flex gap-2">
      <button 
        type="button" 
        class="text-gray-400 hover:text-gray-500"
        on:click={resetFilters}
        aria-label={t('general.reset')}
      >
        <Icon name="refresh-cw" />
      </button>
      
      <button 
        type="button" 
        class="text-gray-400 hover:text-gray-500"
        on:click={close}
        aria-label={t('general.close')}
      >
        <Icon name="x" />
      </button>
    </div>
  </div>
  
  <!-- Main filters -->
  <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
    <!-- Status -->
    <div>
      <Dropdown
        label={t('auctions.status')}
        options={statusOptions}
        bind:value={filters.status}
        placeholder={t('general.select_status')}
      />
    </div>
    
    <!-- Auction type -->
    <div>
      <Dropdown
        label={t('auctions.auction_type')}
        options={auctionTypeOptions}
        bind:value={filters.auction_type}
        placeholder={t('auctions.select_type')}
      />
    </div>
    
    <!-- Property type -->
    <div>
      <Dropdown
        label={t('properties.property_type')}
        options={propertyTypeOptions}
        bind:value={filters.property_type}
        placeholder={t('properties.select_type')}
      />
    </div>
  </div>
  
  <!-- Price range -->
  <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
    <NumericInput
      label={t('general.min_price')}
      bind:value={filters.min_price}
      placeholder={t('general.min_price')}
      currency={true}
    />
    
    <NumericInput
      label={t('general.max_price')}
      bind:value={filters.max_price}
      placeholder={t('general.max_price')}
      currency={true}
    />
  </div>
  
  <!-- Location -->
  <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
    <TextInput
      label={t('general.city')}
      bind:value={filters.city}
      placeholder={t('general.enter_city')}
    />
    
    <TextInput
      label={t('general.district')}
      bind:value={filters.district}
      placeholder={t('general.enter_district')}
    />
  </div>
  
  <!-- Additional filters toggle -->
  <button 
    type="button"
    class="text-primary hover:text-primary-dark flex items-center mb-4"
    on:click={() => isExpanded = !isExpanded}
  >
    <Icon name={isExpanded ? 'chevron-up' : 'chevron-down'} class="mr-1" />
    {isExpanded ? t('general.less_filters') : t('general.more_filters')}
  </button>
  
  <!-- Advanced filters (expandable) -->
  {#if isExpanded}
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4 border-t pt-4">
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
    </div>
  {/if}
  
  <!-- Filter actions -->
  <div class="flex justify-end">
    <Button 
      variant="primary" 
      on:click={applyFilters}
    >
      <Icon name="filter" />
      {t('general.apply_filters')}
    </Button>
  </div>
</div>