<!-- src/lib/components/properties/PropertyGrid.svelte -->
<script>
  /**
   * Property Grid Component
   * Displays a filterable, sortable grid of property listings with pagination.
   */
  import { onMount } from 'svelte';
  import { t } from '$lib/i18n';
  import { fade, slide } from 'svelte/transition';
  
  import PropertyCard from './PropertyCard.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import Select from '$lib/components/ui/Select.svelte';
  import Card from '$lib/components/ui/Card.svelte';
  import Alert from '$lib/components/ui/Alert.svelte';
  import Spinner from '$lib/components/ui/Spinner.svelte';
  import api from '$lib/services/api';

  // Props with default values
  export let initialFilters = {
    status: '',
    property_type: '',
    bedrooms: '',
    bathrooms: '',
    city: '',
    district: '',
    min_price: '',
    max_price: '',
    min_area: '',
    max_area: '',
    sort_by: 'created_at',
    order: 'desc'
  };
  export let title = $t('properties.title');
  export let showFilters = true;
  export let pageSize = 12;
  export let loadingPlaceholders = 6;
  export let autoPaginate = true;
  export let apiEndpoint = 'properties/';
  
  // State
  let properties = [];
  let loading = true;
  let loadingMore = false;
  let error = null;
  let page = 1;
  let totalPages = 1;
  let totalProperties = 0;
  let hasMoreProperties = false;
  let filters = { ...initialFilters };
  let showMobileFilters = false;
  
  // Element ref for infinite scroll detection
  let gridContainer;
  
  // Filter options
  const statusOptions = [
    { value: '', label: $t('general.all') },
    { value: 'active', label: $t('properties.status.available') },
    { value: 'under_contract', label: $t('properties.status.under_contract') },
    { value: 'sold', label: $t('properties.status.sold') },
    { value: 'inactive', label: $t('properties.status.inactive') }
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
  
  const bedroomOptions = [
    { value: '', label: $t('general.any') },
    { value: '1', label: '1+' },
    { value: '2', label: '2+' },
    { value: '3', label: '3+' },
    { value: '4', label: '4+' },
    { value: '5', label: '5+' }
  ];
  
  const bathroomOptions = [
    { value: '', label: $t('general.any') },
    { value: '1', label: '1+' },
    { value: '2', label: '2+' },
    { value: '3', label: '3+' },
    { value: '4', label: '4+' }
  ];
  
  const sortOptions = [
    { value: 'created_at-desc', label: $t('properties.sort_options.newest') },
    { value: 'created_at-asc', label: $t('properties.sort_options.oldest') },
    { value: 'estimated_value-asc', label: $t('properties.sort_options.price_low') },
    { value: 'estimated_value-desc', label: $t('properties.sort_options.price_high') },
    { value: 'area-asc', label: $t('properties.sort_options.area_small') },
    { value: 'area-desc', label: $t('properties.sort_options.area_large') },
    { value: 'views_count-desc', label: $t('properties.sort_options.popular') }
  ];
  
  // Load properties with current filters and pagination
  async function loadProperties(pageNum = 1, append = false) {
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
      Object.entries(filters).forEach(([key, value]) => {
        if (value && !['sort_by', 'order'].includes(key)) {
          params[key] = value;
        }
      });
      
      const response = await api.get(apiEndpoint, params);
      
      if (response?.data?.results) {
        // Update properties data based on append mode
        if (append) {
          properties = [...properties, ...response.data.results];
        } else {
          properties = response.data.results;
          
          // Scroll to top when filters change
          if (pageNum === 1 && typeof window !== 'undefined') {
            window.scrollTo({ top: 0, behavior: 'smooth' });
          }
        }
        
        // Update pagination info
        page = pageNum;
        totalPages = response.data.total_pages || 1;
        totalProperties = response.data.count || 0;
        hasMoreProperties = page < totalPages;
      } else {
        throw new Error('Invalid response format');
      }
    } catch (err) {
      console.error('Error fetching properties:', err);
      error = err.message || $t('system_messages.error_occurred');
    } finally {
      loading = false;
      loadingMore = false;
    }
  }
  
  // Handle filter changes
  function applyFilters() {
    page = 1; // Reset to first page
    loadProperties(1, false);
    
    // Close mobile filters if open
    if (showMobileFilters) {
      showMobileFilters = false;
    }
  }
  
  // Reset filters
  function resetFilters() {
    filters = {
      status: '',
      property_type: '',
      bedrooms: '',
      bathrooms: '',
      city: '',
      district: '',
      min_price: '',
      max_price: '',
      min_area: '',
      max_area: '',
      sort_by: 'created_at',
      order: 'desc'
    };
    
    applyFilters();
  }
  
  // Handle sort changes
  function handleSortChange(event) {
    const value = event.target.value;
    const [sortField, sortOrder] = value.split('-');
    
    filters.sort_by = sortField;
    filters.order = sortOrder;
    applyFilters();
  }
  
  // Load more properties (for pagination)
  function loadMore() {
    if (hasMoreProperties && !loadingMore) {
      loadProperties(page + 1, true);
    }
  }
  
  // Set up infinite scroll
  function setupInfiniteScroll() {
    if (!autoPaginate || typeof window === 'undefined' || !window.IntersectionObserver) return;
    
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && hasMoreProperties && !loading && !loadingMore) {
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
  
  // Check if filters are active
  $: activeFiltersCount = Object.entries(filters).filter(([key, value]) => {
    return value && key !== 'sort_by' && key !== 'order';
  }).length;
  
  // Sort value for select element
  $: sortValue = `${filters.sort_by}-${filters.order}`;
  
  // Initialize component
  onMount(() => {
    loadProperties();
    return setupInfiniteScroll();
  });
</script>

<div class="property-grid">
  <!-- Header -->
  {#if title}
    <div class="mb-6 flex items-center justify-between">
      <h2 class="text-2xl font-bold text-cosmos-text">{title}</h2>
      
      {#if !loading && properties.length > 0}
        <p class="text-sm text-cosmos-text-muted">
          {$t('properties.showing_results').replace('{0}', properties.length).replace('{1}', totalProperties)}
        </p>
      {/if}
    </div>
  {/if}
  
  {#if showFilters}
    <!-- Desktop Filters -->
    <Card bordered={true} padding={true} class="mb-6 hidden md:block">
      <div class="mb-4 flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <h3 class="text-lg font-bold text-cosmos-text">{$t('properties.filter_properties')}</h3>
          
          {#if activeFiltersCount > 0}
            <span class="rounded-full bg-primary bg-opacity-20 px-2 py-1 text-xs font-medium text-primary">
              {activeFiltersCount} {$t('general.active_filters')}
            </span>
          {/if}
        </div>
        
        <div class="flex space-x-2">
          <Button
            variant="secondary"
            size="sm"
            onClick={resetFilters}
          >
            {$t('general.reset')}
          </Button>
          
          <Button
            variant="primary"
            size="sm"
            onClick={applyFilters}
          >
            {$t('general.apply')}
          </Button>
        </div>
      </div>
      
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
        <!-- Property Type -->
        <Select
          name="property_type"
          label={$t('properties.property_type')}
          options={propertyTypeOptions}
          value={filters.property_type}
        />
        
        <!-- Status -->
        <Select
          name="status"
          label={$t('properties.property_status')}
          options={statusOptions}
          value={filters.status}
        />
        
        <!-- Bedrooms -->
        <Select
          name="bedrooms"
          label={$t('properties.bedrooms')}
          options={bedroomOptions}
          value={filters.bedrooms}
        />
        
        <!-- Bathrooms -->
        <Select
          name="bathrooms"
          label={$t('properties.bathrooms')}
          options={bathroomOptions}
          value={filters.bathrooms}
        />
        
        <!-- City -->
        <Input
          type="text"
          name="city"
          label={$t('properties.property_city')}
          placeholder={$t('properties.enter_city')}
          bind:value={filters.city}
        />
        
        <!-- District -->
        <Input
          type="text"
          name="district"
          label={$t('properties.property_district')}
          placeholder={$t('properties.enter_district')}
          bind:value={filters.district}
        />
        
        <!-- Price Range -->
        <div>
          <label class="mb-1.5 block text-sm font-medium text-cosmos-text">
            {$t('properties.price_range')}
          </label>
          <div class="flex space-x-2">
            <Input
              type="number"
              placeholder={$t('general.min')}
              bind:value={filters.min_price}
              class="w-1/2"
            />
            <Input
              type="number"
              placeholder={$t('general.max')}
              bind:value={filters.max_price}
              class="w-1/2"
            />
          </div>
        </div>
        
        <!-- Area Range -->
        <div>
          <label class="mb-1.5 block text-sm font-medium text-cosmos-text">
            {$t('properties.area_range')} (m²)
          </label>
          <div class="flex space-x-2">
            <Input
              type="number"
              placeholder={$t('general.min')}
              bind:value={filters.min_area}
              class="w-1/2"
            />
            <Input
              type="number"
              placeholder={$t('general.max')}
              bind:value={filters.max_area}
              class="w-1/2"
            />
          </div>
        </div>
        
        <!-- Sorting -->
        <Select
          name="sort_by"
          label={$t('general.sort')}
          options={sortOptions}
          value={sortValue}
          onChange={handleSortChange}
        />
      </div>
    </Card>
    
    <!-- Mobile Filters Toggle -->
    <div class="mb-4 flex items-center justify-between md:hidden">
      <Button
        variant="secondary"
        onClick={() => showMobileFilters = !showMobileFilters}
        size="sm"
      >
        <svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
        </svg>
        {$t('general.filter')}
        
        {#if activeFiltersCount > 0}
          <span class="ml-2 rounded-full bg-primary bg-opacity-20 px-2 py-0.5 text-xs font-medium text-primary">
            {activeFiltersCount}
          </span>
        {/if}
      </Button>
      
      <!-- Mobile Sort -->
      <Select
        name="sort_mobile"
        options={sortOptions}
        value={sortValue}
        onChange={handleSortChange}
        size="sm"
        className="w-auto min-w-[180px]"
      />
    </div>
    
    <!-- Mobile Filters Modal -->
    {#if showMobileFilters}
      <div class="fixed inset-0 z-50 flex items-end bg-cosmos-bg-dark bg-opacity-80 p-4 md:hidden" transition:fade={{ duration: 200 }}>
        <div 
          class="w-full rounded-t-xl bg-cosmos-bg p-4"
          transition:slide={{ duration: 300 }}
        >
          <div class="flex items-center justify-between border-b border-cosmos-bg-light pb-4">
            <h3 class="text-lg font-bold text-cosmos-text">{$t('properties.filter_properties')}</h3>
            
            <Button
              variant="ghost"
              size="sm"
              onClick={() => showMobileFilters = false}
              ariaLabel={$t('general.close')}
            >
              <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </Button>
          </div>
          
          <div class="max-h-[70vh] overflow-y-auto py-4">
            <div class="space-y-4">
              <!-- Property Type -->
              <Select
                name="property_type_mobile"
                label={$t('properties.property_type')}
                options={propertyTypeOptions}
                value={filters.property_type}
                bind:value={filters.property_type}
              />
              
              <!-- Status -->
              <Select
                name="status_mobile"
                label={$t('properties.property_status')}
                options={statusOptions}
                value={filters.status}
                bind:value={filters.status}
              />
              
              <!-- Bedrooms and Bathrooms -->
              <div class="grid grid-cols-2 gap-4">
                <Select
                  name="bedrooms_mobile"
                  label={$t('properties.bedrooms')}
                  options={bedroomOptions}
                  value={filters.bedrooms}
                  bind:value={filters.bedrooms}
                />
                
                <Select
                  name="bathrooms_mobile"
                  label={$t('properties.bathrooms')}
                  options={bathroomOptions}
                  value={filters.bathrooms}
                  bind:value={filters.bathrooms}
                />
              </div>
              
              <!-- City -->
              <Input
                type="text"
                name="city_mobile"
                label={$t('properties.property_city')}
                placeholder={$t('properties.enter_city')}
                bind:value={filters.city}
              />
              
              <!-- District -->
              <Input
                type="text"
                name="district_mobile"
                label={$t('properties.property_district')}
                placeholder={$t('properties.enter_district')}
                bind:value={filters.district}
              />
              
              <!-- Price Range -->
              <div>
                <label class="mb-1.5 block text-sm font-medium text-cosmos-text">
                  {$t('properties.price_range')}
                </label>
                <div class="flex space-x-2">
                  <Input
                    type="number"
                    placeholder={$t('general.min')}
                    bind:value={filters.min_price}
                    class="w-1/2"
                  />
                  <Input
                    type="number"
                    placeholder={$t('general.max')}
                    bind:value={filters.max_price}
                    class="w-1/2"
                  />
                </div>
              </div>
              
              <!-- Area Range -->
              <div>
                <label class="mb-1.5 block text-sm font-medium text-cosmos-text">
                  {$t('properties.area_range')} (m²)
                </label>
                <div class="flex space-x-2">
                  <Input
                    type="number"
                    placeholder={$t('general.min')}
                    bind:value={filters.min_area}
                    class="w-1/2"
                  />
                  <Input
                    type="number"
                    placeholder={$t('general.max')}
                    bind:value={filters.max_area}
                    class="w-1/2"
                  />
                </div>
              </div>
            </div>
          </div>
          
          <!-- Filter Actions -->
          <div class="mt-4 flex space-x-2 border-t border-cosmos-bg-light pt-4">
            <Button
              variant="secondary"
              onClick={resetFilters}
              fullWidth={true}
            >
              {$t('general.reset')}
            </Button>
            
            <Button
              variant="primary"
              onClick={applyFilters}
              fullWidth={true}
            >
              {$t('general.apply_filters')}
            </Button>
          </div>
        </div>
      </div>
    {/if}
  {/if}
  
  <!-- Main Content Area -->
  {#if error}
    <!-- Error State -->
    <Alert type="error" title={$t('general.error')} class="my-8">
      <p>{error}</p>
      <div class="mt-4">
        <Button 
          variant="primary"
          onClick={() => loadProperties(1, false)}
        >
          {$t('general.retry')}
        </Button>
      </div>
    </Alert>
  {:else if loading && properties.length === 0}
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
  {:else if properties.length === 0}
    <!-- Empty State -->
    <div class="my-12 rounded-xl bg-cosmos-bg-light bg-opacity-10 p-8 text-center">
      <div class="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-cosmos-bg-light bg-opacity-30">
        <svg class="h-8 w-8 text-cosmos-text-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      <h3 class="mb-2 text-lg font-medium text-cosmos-text">{$t('properties.no_properties_found')}</h3>
      <p class="text-cosmos-text-muted">{$t('properties.try_different_filters')}</p>
      
      {#if activeFiltersCount > 0}
        <Button 
          variant="primary"
          onClick={resetFilters}
          class="mt-4"
        >
          {$t('general.reset_filters')}
        </Button>
      {/if}
    </div>
  {:else}
    <!-- Property Grid -->
    <div 
      bind:this={gridContainer}
      class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4"
    >
      {#each properties as property (property.id)}
        <PropertyCard {property} />
      {/each}
    </div>
    
    <!-- Loading More Indicator -->
    {#if loadingMore}
      <div class="col-span-full my-6 flex justify-center">
        <Spinner color="primary" size="md" text={$t('general.loading_more')} />
      </div>
    {/if}
    
    <!-- Manual Load More Button (when autoPaginate is false) -->
    {#if !autoPaginate && hasMoreProperties && !loadingMore}
      <div class="mt-8 flex justify-center">
        <Button
          variant="outline"
          onClick={loadMore}
        >
          {$t('general.load_more')}
        </Button>
      </div>
    {/if}
    
    <!-- End of Results Message -->
    {#if !hasMoreProperties && properties.length > 0 && !loading && !loadingMore}
      <div class="mt-8 text-center">
        <p class="text-sm text-cosmos-text-muted">
          {$t('properties.end_of_results')}
        </p>
      </div>
    {/if}
  {/if}
</div>