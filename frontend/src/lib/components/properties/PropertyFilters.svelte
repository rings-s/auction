<!-- src/lib/components/properties/PropertyFilters.svelte -->
<script>
    import { createEventDispatcher } from 'svelte';
    import { t, language } from '$lib/i18n';
    import { fade } from 'svelte/transition';
    import Button from '$lib/components/ui/Button.svelte';
    import Input from '$lib/components/ui/Input.svelte';
    import Select from '$lib/components/ui/Select.svelte';
    
    // Props
    export let currentFilters = {};
    export let isExpanded = false;
    
    // Local state
    let filters = { ...currentFilters };
    let isRTL = false;
    
    // Define dispatchers
    const dispatch = createEventDispatcher();
    
    // Filter options
    const propertyTypeOptions = [
      { value: '', label: $t('general.all') },
      { value: 'apartment', label: $t('properties.types.apartment') },
      { value: 'villa', label: $t('properties.types.villa') },
      { value: 'land', label: $t('properties.types.land') },
      { value: 'commercial', label: $t('properties.types.commercial') },
      { value: 'industrial', label: $t('properties.types.industrial') },
      { value: 'mixed_use', label: $t('properties.types.mixed_use') },
      { value: 'building', label: $t('properties.types.building') },
      { value: 'farm', label: $t('properties.types.farm') },
      { value: 'office', label: $t('properties.types.office') },
      { value: 'retail', label: $t('properties.types.retail') }
    ];
    
    const statusOptions = [
      { value: '', label: $t('general.all') },
      { value: 'active', label: $t('properties.status.available') },
      { value: 'under_contract', label: $t('properties.status.under_contract') },
      { value: 'sold', label: $t('properties.status.sold') },
      { value: 'pending', label: $t('properties.status.pending') }
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
    
    // Apply filters
    function applyFilters() {
      dispatch('change', filters);
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
      
      dispatch('change', filters);
    }
    
    // Close filters (mobile)
    function closeFilters() {
      dispatch('close');
    }
    
    // Watch for language changes to update RTL status
    $: isRTL = $language === 'ar';
    
    // Update local filters when props change
    $: {
      if (JSON.stringify(currentFilters) !== JSON.stringify(filters)) {
        filters = { ...currentFilters };
      }
    }
  </script>
  
  <div class="property-filters {isRTL ? 'rtl' : ''}" class:expanded={isExpanded}>
    <!-- Filter Header -->
    <div class="mb-4 flex items-center justify-between">
      <h3 class="text-lg font-semibold text-neutral-800 dark:text-neutral-200">
        {$t('properties.filter_properties')}
      </h3>
      
      <div class="flex space-x-2 rtl:space-x-reverse">
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
        
        <!-- Mobile Close Button -->
        <div class="md:hidden">
          <Button
            variant="ghost"
            size="sm"
            onClick={closeFilters}
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
            </svg>
          </Button>
        </div>
      </div>
    </div>
    
    <!-- Filter Form -->
    <div class="space-y-4">
      <!-- Basic Filters - Always Visible -->
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <!-- Property Type -->
        <Select
          name="property_type"
          label={$t('properties.property_type')}
          options={propertyTypeOptions}
          bind:value={filters.property_type}
        />
        
        <!-- Status -->
        <Select
          name="status"
          label={$t('properties.property_status')}
          options={statusOptions}
          bind:value={filters.status}
        />
      </div>
      
      <!-- Expandable Section -->
      {#if isExpanded}
        <div transition:fade={{ duration: 200 }} class="mt-4 rounded-lg bg-neutral-50 dark:bg-neutral-800/30 p-4 space-y-4">
          <!-- Location -->
          <h4 class="font-medium text-neutral-700 dark:text-neutral-300">
            {$t('properties.property_location')}
          </h4>
          
          <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <!-- City -->
            <Input
              type="text"
              name="city"
              label={$t('properties.property_city')}
              placeholder={$t('properties.enter_city', 'Enter city name')}
              bind:value={filters.city}
            />
            
            <!-- District -->
            <Input
              type="text"
              name="district"
              label={$t('properties.property_district')}
              placeholder={$t('properties.enter_district', 'Enter district name')}
              bind:value={filters.district}
            />
          </div>
          
          <!-- Price Range -->
          <h4 class="font-medium text-neutral-700 dark:text-neutral-300 mt-4">
            {$t('properties.price_range', 'Price Range')}
          </h4>
          
          <div class="grid grid-cols-2 gap-4">
            <Input
              type="number"
              name="min_price"
              label={$t('general.min')}
              placeholder={$t('general.min')}
              bind:value={filters.min_price}
            />
            
            <Input
              type="number"
              name="max_price"
              label={$t('general.max')}
              placeholder={$t('general.max')}
              bind:value={filters.max_price}
            />
          </div>
          
          <!-- Area Range -->
          <h4 class="font-medium text-neutral-700 dark:text-neutral-300 mt-4">
            {$t('properties.property_area')} (m²)
          </h4>
          
          <div class="grid grid-cols-2 gap-4">
            <Input
              type="number"
              name="min_area"
              label={$t('general.min')}
              placeholder={$t('general.min')}
              bind:value={filters.min_area}
            />
            
            <Input
              type="number"
              name="max_area"
              label={$t('general.max')}
              placeholder={$t('general.max')}
              bind:value={filters.max_area}
            />
          </div>
          
          <!-- Bedrooms & Bathrooms -->
          <h4 class="font-medium text-neutral-700 dark:text-neutral-300 mt-4">
            {$t('properties.property_features')}
          </h4>
          
          <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <!-- Bedrooms -->
            <Select
              name="bedrooms"
              label={$t('properties.bedrooms')}
              options={bedroomOptions}
              bind:value={filters.bedrooms}
            />
            
            <!-- Bathrooms -->
            <Select
              name="bathrooms"
              label={$t('properties.bathrooms')}
              options={bathroomOptions}
              bind:value={filters.bathrooms}
            />
          </div>
        </div>
      {/if}
      
      <!-- Toggle Button to Show/Hide Advanced Filters -->
      <button
        class="mt-2 w-full py-2 text-sm text-primary hover:text-primary-dark flex items-center justify-center rounded-md hover:bg-neutral-100 dark:hover:bg-neutral-800 transition-colors"
        on:click={() => isExpanded = !isExpanded}
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1 rtl:mr-0 rtl:ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={isExpanded ? "M5 15l7-7 7 7" : "M19 9l-7 7-7-7"} />
        </svg>
        {isExpanded ? $t('general.less') : $t('general.more')} {$t('general.filter')}
      </button>
    </div>
  </div>
  
  <style>
    /* RTL support */
    .rtl {
      direction: rtl;
      text-align: right;
    }
    
    /* Additional animations */
    .property-filters {
      transition: all 0.3s ease;
    }
    
    .property-filters.expanded {
      border-radius: 0.75rem;
    }
  </style>