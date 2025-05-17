<!-- src/lib/components/PropertySearch.svelte -->
<script>
  import { createEventDispatcher } from 'svelte';
  import { t } from '$lib/i18n/i18n';
  
  export let searchParams = {
    query: '',
    propertyType: '',
    minPrice: '',
    maxPrice: '',
    city: '',
    minSize: '',
    maxSize: ''
  };
  
  const dispatch = createEventDispatcher();
  
  const propertyTypes = [
    { value: 'residential', label: 'nav.propertyTypes.residential' },
    { value: 'commercial', label: 'nav.propertyTypes.commercial' },
    { value: 'land', label: 'nav.propertyTypes.land' },
    { value: 'industrial', label: 'nav.propertyTypes.industrial' },
    { value: 'mixed_use', label: 'nav.propertyTypes.mixedUse' }
  ];
  
  function handleSearch() {
    dispatch('search', searchParams);
  }
  
  function clearFilters() {
    searchParams = {
      query: '',
      propertyType: '',
      minPrice: '',
      maxPrice: '',
      city: '',
      minSize: '',
      maxSize: ''
    };
    dispatch('search', searchParams);
  }
</script>

<div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
<form on:submit|preventDefault={handleSearch} class="space-y-6">
  <!-- Keyword Search -->
  <div class="mb-4">
    <label for="search-query" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
      {$t('search.keyword')}
    </label>
    <div class="mt-1 relative rounded-md shadow-sm">
      <input
        type="text"
        id="search-query"
        bind:value={searchParams.query}
        class="block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
        placeholder={$t('search.keywordPlaceholder')}
        aria-label={$t('search.keyword')}
      />
    </div>
  </div>
  
  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
    <!-- Property Type -->
    <div>
      <label for="property-type" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
        {$t('search.propertyType')}
      </label>
      <select
        id="property-type"
        bind:value={searchParams.propertyType}
        class="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
        aria-label={$t('search.propertyType')}
      >
        <option value="">{$t('search.all')}</option>
        {#each propertyTypes as type}
          <option value={type.value}>{$t(type.label)}</option>
        {/each}
      </select>
    </div>
    
    <!-- City -->
    <div>
      <label for="city-search" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
        {$t('search.city')}
      </label>
      <input
        type="text"
        id="city-search"
        bind:value={searchParams.city}
        class="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
        placeholder={$t('search.cityPlaceholder')}
        aria-label={$t('search.city')}
      />
    </div>
  </div>
  
  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
    <!-- Price Range -->
    <div>
      <fieldset>
        <legend class="block text-sm font-medium text-gray-700 dark:text-gray-300">
          {$t('search.price')}
        </legend>
        <div class="mt-1 flex items-center space-x-2">
          <div class="flex-1">
            <label for="min-price" class="sr-only">{$t('search.minPrice')}</label>
            <input
              type="number"
              id="min-price"
              bind:value={searchParams.minPrice}
              min="0"
              class="block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              placeholder={$t('search.min')}
              aria-label={$t('search.minPrice')}
            />
          </div>
          <span class="text-gray-500 dark:text-gray-400">-</span>
          <div class="flex-1">
            <label for="max-price" class="sr-only">{$t('search.maxPrice')}</label>
            <input
              type="number"
              id="max-price"
              bind:value={searchParams.maxPrice}
              min="0"
              class="block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              placeholder={$t('search.max')}
              aria-label={$t('search.maxPrice')}
            />
          </div>
        </div>
      </fieldset>
    </div>
    
    <!-- Size Range -->
    <div>
      <fieldset>
        <legend class="block text-sm font-medium text-gray-700 dark:text-gray-300">
          {$t('search.size')} (m²)
        </legend>
        <div class="mt-1 flex items-center space-x-2">
          <div class="flex-1">
            <label for="min-size" class="sr-only">{$t('search.minSize')}</label>
            <input
              type="number"
              id="min-size"
              bind:value={searchParams.minSize}
              min="0"
              class="block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              placeholder={$t('search.min')}
              aria-label={$t('search.minSize')}
            />
          </div>
          <span class="text-gray-500 dark:text-gray-400">-</span>
          <div class="flex-1">
            <label for="max-size" class="sr-only">{$t('search.maxSize')}</label>
            <input
              type="number"
              id="max-size"
              bind:value={searchParams.maxSize}
              min="0"
              class="block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              placeholder={$t('search.max')}
              aria-label={$t('search.maxSize')}
            />
          </div>
        </div>
      </fieldset>
    </div>
  </div>
  
  <div class="flex justify-between">
    <button
      type="button"
      on:click={clearFilters}
      class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
      aria-label={$t('search.clearFilters')}
    >
      {$t('search.clear')}
    </button>
    <button
      type="submit"
      class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
      aria-label={$t('search.search')}
    >
      {$t('search.search')}
    </button>
  </div>
</form>
</div>