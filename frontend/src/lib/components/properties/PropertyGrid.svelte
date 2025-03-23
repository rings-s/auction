<!-- src/lib/components/property/PropertyGrid.svelte -->
<script>
    import { onMount } from 'svelte';
    import { t } from '$lib/i18n';
    import { api } from '$lib/services/api';
    import PropertyCard from './PropertyCard.svelte';
    
    // Props
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
    
    const sortOptions = [
      { value: 'created_at', label: $t('properties.sort_options.newest') },
      { value: 'estimated_value', label: $t('properties.sort_options.price') },
      { value: 'area', label: $t('properties.sort_options.area') },
      { value: 'views_count', label: $t('properties.sort_options.popular') }
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
        if (filters.status) params.status = filters.status;
        if (filters.property_type) params.property_type = filters.property_type;
        if (filters.bedrooms) params.bedrooms = filters.bedrooms;
        if (filters.bathrooms) params.bathrooms = filters.bathrooms;
        if (filters.city) params.city = filters.city;
        if (filters.district) params.district = filters.district;
        if (filters.min_price) params.min_price = filters.min_price;
        if (filters.max_price) params.max_price = filters.max_price;
        if (filters.min_area) params.min_area = filters.min_area;
        if (filters.max_area) params.max_area = filters.max_area;
        
        const response = await api.get('properties/', params);
        
        if (response && response.data && response.data.results) {
          // Update properties data based on append mode
          if (append) {
            properties = [...properties, ...response.data.results];
          } else {
            properties = response.data.results;
            
            // Scroll to top when filters change
            if (pageNum === 1 && window) {
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
      if (!autoPaginate || !window) return;
      
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
    <div class="mb-6 flex items-center justify-between">
      <h2 class="text-2xl font-bold text-cosmos-text">{title}</h2>
      
      {#if !loading && properties.length > 0}
        <p class="text-sm text-cosmos-text-muted">
          {$t('properties.showing_results').replace('{0}', properties.length).replace('{1}', totalProperties)}
        </p>
      {/if}
    </div>
    
    {#if showFilters}
      <!-- Desktop Filters -->
      <div class="mb-6 hidden rounded-xl bg-cosmos-bg-light bg-opacity-30 p-4 backdrop-blur-sm md:block">
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
            <button
              on:click={resetFilters}
              class="rounded-lg border border-cosmos-bg-light px-3 py-1 text-sm text-cosmos-text-muted hover:text-cosmos-text"
            >
              {$t('general.reset')}
            </button>
            
            <button
              on:click={applyFilters}
              class="rounded-lg bg-primary px-3 py-1 text-sm text-white hover:bg-primary-dark"
            >
              {$t('general.apply')}
            </button>
          </div>
        </div>
        
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
          <!-- Property Type -->
          <div>
            <label for="property_type" class="mb-1 block text-sm font-medium text-cosmos-text-muted">
              {$t('properties.property_type')}
            </label>
            <select
              id="property_type"
              bind:value={filters.property_type}
              class="w-full rounded-lg border border-cosmos-bg-light bg-cosmos-bg p-2 text-cosmos-text outline-none focus:border-primary"
            >
              {#each propertyTypeOptions as option}
                <option value={option.value}>{option.label}</option>
              {/each}
            </select>
          </div>
          
          <!-- Status -->
          <div>
            <label for="status" class="mb-1 block text-sm font-medium text-cosmos-text-muted">
              {$t('properties.property_status')}
            </label>
            <select
              id="status"
              bind:value={filters.status}
              class="w-full rounded-lg border border-cosmos-bg-light bg-cosmos-bg p-2 text-cosmos-text outline-none focus:border-primary"
            >
              {#each statusOptions as option}
                <option value={option.value}>{option.label}</option>
              {/each}
            </select>
          </div>
          
          <!-- Bedrooms -->
          <div>
            <label for="bedrooms" class="mb-1 block text-sm font-medium text-cosmos-text-muted">
              {$t('properties.bedrooms')}
            </label>
            <select
              id="bedrooms"
              bind:value={filters.bedrooms}
              class="w-full rounded-lg border border-cosmos-bg-light bg-cosmos-bg p-2 text-cosmos-text outline-none focus:border-primary"
            >
              <option value="">{$t('general.any')}</option>
              <option value="1">1+</option>
              <option value="2">2+</option>
              <option value="3">3+</option>
              <option value="4">4+</option>
              <option value="5">5+</option>
            </select>
          </div>
          
          <!-- Bathrooms -->
          <div>
            <label for="bathrooms" class="mb-1 block text-sm font-medium text-cosmos-text-muted">
              {$t('properties.bathrooms')}
            </label>
            <select
              id="bathrooms"
              bind:value={filters.bathrooms}
              class="w-full rounded-lg border border-cosmos-bg-light bg-cosmos-bg p-2 text-cosmos-text outline-none focus:border-primary"
            >
              <option value="">{$t('general.any')}</option>
              <option value="1">1+</option>
              <option value="2">2+</option>
              <option value="3">3+</option>
              <option value="4">4+</option>
            </select>
          </div>
          
          <!-- City -->
          <div>
            <label for="city" class="mb-1 block text-sm font-medium text-cosmos-text-muted">
              {$t('properties.property_city')}
            </label>
            <input
              type="text"
              id="city"
              bind:value={filters.city}
              placeholder={$t('properties.enter_city')}
              class="w-full rounded-lg border border-cosmos-bg-light bg-cosmos-bg p-2 text-cosmos-text outline-none focus:border-primary"
            />
          </div>
          
          <!-- District -->
          <div>
            <label for="district" class="mb-1 block text-sm font-medium text-cosmos-text-muted">
              {$t('properties.property_district')}
            </label>
            <input
              type="text"
              id="district"
              bind:value={filters.district}
              placeholder={$t('properties.enter_district')}
              class="w-full rounded-lg border border-cosmos-bg-light bg-cosmos-bg p-2 text-cosmos-text outline-none focus:border-primary"
            />
          </div>
          
          <!-- Price Range -->
          <div>
            <label class="mb-1 block text-sm font-medium text-cosmos-text-muted">
              {$t('properties.price_range')}
            </label>
            <div class="flex space-x-2">
              <input
                type="number"
                bind:value={filters.min_price}
                placeholder={$t('general.min')}
                class="w-1/2 rounded-lg border border-cosmos-bg-light bg-cosmos-bg p-2 text-cosmos-text outline-none focus:border-primary"
              />
              <input
                type="number"
                bind:value={filters.max_price}
                placeholder={$t('general.max')}
                class="w-1/2 rounded-lg border border-cosmos-bg-light bg-cosmos-bg p-2 text-cosmos-text outline-none focus:border-primary"
              />
            </div>
          </div>
          
          <!-- Area Range -->
          <div>
            <label class="mb-1 block text-sm font-medium text-cosmos-text-muted">
              {$t('properties.area_range')} (m²)
            </label>
            <div class="flex space-x-2">
              <input
                type="number"
                bind:value={filters.min_area}
                placeholder={$t('general.min')}
                class="w-1/2 rounded-lg border border-cosmos-bg-light bg-cosmos-bg p-2 text-cosmos-text outline-none focus:border-primary"
              />
              <input
                type="number"
                bind:value={filters.max_area}
                placeholder={$t('general.max')}
                class="w-1/2 rounded-lg border border-cosmos-bg-light bg-cosmos-bg p-2 text-cosmos-text outline-none focus:border-primary"
              />
            </div>
          </div>
          
          <!-- Sorting -->
          <div>
            <label for="sort_by" class="mb-1 block text-sm font-medium text-cosmos-text-muted">
              {$t('general.sort')}
            </label>
            <select
              id="sort_by"
              bind:value={sortValue}
              on:change={handleSortChange}
              class="w-full rounded-lg border border-cosmos-bg-light bg-cosmos-bg p-2 text-cosmos-text outline-none focus:border-primary"
            >
              {#each sortOptions as option}
                <option value={`${option.value}-asc`}>{option.label} ({$t('general.asc')})</option>
                <option value={`${option.value}-desc`}>{option.label} ({$t('general.desc')})</option>
              {/each}
            </select>
          </div>
        </div>
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
            on:change={handleSortChange}
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
              <h3 class="text-lg font-bold text-cosmos-text">{$t('properties.filter_properties')}</h3>
              
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
                <!-- Property Type -->
                <div>
                  <label for="m-property_type" class="mb-1 block text-sm font-medium text-cosmos-text-muted">
                    {$t('properties.property_type')}
                  </label>
                  <select
                    id="m-property_type"
                    bind:value={filters.property_type}
                    class="w-full rounded-lg border border-cosmos-bg-light bg-cosmos-bg-light p-3 text-cosmos-text outline-none focus:border-primary"
                  >
                    {#each propertyTypeOptions as option}
                      <option value={option.value}>{option.label}</option>
                    {/each}
                  </select>
                </div>
                
                <!-- Status -->
                <div>
                  <label for="m-status" class="mb-1 block text-sm font-medium text-cosmos-text-muted">
                    {$t('properties.property_status')}
                  </label>
                  <select
                    id="m-status"
                    bind:value={filters.status}
                    class="w-full rounded-lg border border-cosmos-bg-light bg-cosmos-bg-light p-3 text-cosmos-text outline-none focus:border-primary"
                  >
                    {#each statusOptions as option}
                      <option value={option.value}>{option.label}</option>
                    {/each}
                  </select>
                </div>
                
                <!-- Bedrooms and Bathrooms -->
                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label for="m-bedrooms" class="mb-1 block text-sm font-medium text-cosmos-text-muted">
                      {$t('properties.bedrooms')}
                    </label>
                    <select
                      id="m-bedrooms"
                      bind:value={filters.bedrooms}
                      class="w-full rounded-lg border border-cosmos-bg-light bg-cosmos-bg-light p-3 text-cosmos-text outline-none focus:border-primary"
                    >
                      <option value="">{$t('general.any')}</option>
                      <option value="1">1+</option>
                      <option value="2">2+</option>
                      <option value="3">3+</option>
                      <option value="4">4+</option>
                      <option value="5">5+</option>
                    </select>
                  </div>
                  
                  <div>
                    <label for="m-bathrooms" class="mb-1 block text-sm font-medium text-cosmos-text-muted">
                      {$t('properties.bathrooms')}
                    </label>
                    <select
                      id="m-bathrooms"
                      bind:value={filters.bathrooms}
                      class="w-full rounded-lg border border-cosmos-bg-light bg-cosmos-bg-light p-3 text-cosmos-text outline-none focus:border-primary"
                    >
                      <option value="">{$t('general.any')}</option>
                      <option value="1">1+</option>
                      <option value="2">2+</option>
                      <option value="3">3+</option>
                      <option value="4">4+</option>
                    </select>
                  </div>
                </div>
                
                <!-- City -->
                <div>
                  <label for="m-city" class="mb-1 block text-sm font-medium text-cosmos-text-muted">
                    {$t('properties.property_city')}
                  </label>
                  <input
                    type="text"
                    id="m-city"
                    bind:value={filters.city}
                    placeholder={$t('properties.enter_city')}
                    class="w-full rounded-lg border border-cosmos-bg-light bg-cosmos-bg-light p-3 text-cosmos-text outline-none focus:border-primary"
                  />
                </div>
                
                <!-- District -->
                <div>
                  <label for="m-district" class="mb-1 block text-sm font-medium text-cosmos-text-muted">
                    {$t('properties.property_district')}
                  </label>
                  <input
                    type="text"
                    id="m-district"
                    bind:value={filters.district}
                    placeholder={$t('properties.enter_district')}
                    class="w-full rounded-lg border border-cosmos-bg-light bg-cosmos-bg-light p-3 text-cosmos-text outline-none focus:border-primary"
                  />
                </div>
                
                <!-- Price Range -->
                <div>
                  <label class="mb-1 block text-sm font-medium text-cosmos-text-muted">
                    {$t('properties.price_range')}
                  </label>
                  <div class="flex space-x-2">
                    <input
                      type="number"
                      bind:value={filters.min_price}
                      placeholder={$t('general.min')}
                      class="w-1/2 rounded-lg border border-cosmos-bg-light bg-cosmos-bg-light p-3 text-cosmos-text outline-none focus:border-primary"
                    />
                    <input
                      type="number"
                      bind:value={filters.max_price}
                      placeholder={$t('general.max')}
                      class="w-1/2 rounded-lg border border-cosmos-bg-light bg-cosmos-bg-light p-3 text-cosmos-text outline-none focus:border-primary"
                    />
                  </div>
                </div>
                
                <!-- Area Range -->
                <div>
                  <label class="mb-1 block text-sm font-medium text-cosmos-text-muted">
                    {$t('properties.area_range')} (m²)
                  </label>
                  <div class="flex space-x-2">
                    <input
                      type="number"
                      bind:value={filters.min_area}
                      placeholder={$t('general.min')}
                      class="w-1/2 rounded-lg border border-cosmos-bg-light bg-cosmos-bg-light p-3 text-cosmos-text outline-none focus:border-primary"
                    />
                    <input
                      type="number"
                      bind:value={filters.max_area}
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
              >
                {$t('general.apply_filters')}
              </button>
            </div>
          </div>
        </div>
      {/if}
    {/if}
    
    {#if error}
      <div class="my-8 rounded-xl bg-status-error bg-opacity-10 p-6 text-center">
        <p class="text-status-error">{error}</p>
        <button 
          class="mt-4 rounded-lg bg-primary px-4 py-2 text-white hover:bg-primary-dark"
          on:click={() => loadProperties(1, false)}
        >
          {$t('general.retry')}
        </button>
      </div>
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
          <svg class="h-8 w-8 text-cosmos-text-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h3 class="mb-2 text-lg font-medium text-cosmos-text">{$t('properties.no_properties_found')}</h3>
        <p class="text-cosmos-text-muted">{$t('properties.try_different_filters')}</p>
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
      {#if !autoPaginate && hasMoreProperties && !loadingMore}
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
      {#if !hasMoreProperties && properties.length > 0 && !loading && !loadingMore}
        <div class="mt-8 text-center">
          <p class="text-sm text-cosmos-text-muted">
            {$t('properties.end_of_results')}
          </p>
        </div>
      {/if}