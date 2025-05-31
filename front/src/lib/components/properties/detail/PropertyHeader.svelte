<script>
    import { t } from '$lib/i18n';
    
    export let property;
    export let canEdit;
    export let isHeaderSticky;
    export let activeTab;
    export let tabs;
    export let onSetActiveTab;
    export let onContactOwner;
    
    function formatCurrency(value) {
      if (!value) return '$0';
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        maximumFractionDigits: 0
      }).format(value);
    }
    
    function getIcon(name) {
      switch(name) {
        case 'home':
          return `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path></svg>`;
        case 'layout':
          return `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z"></path></svg>`;
        case 'map-pin':
          return `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>`;
        case 'image':
          return `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>`;
        default:
          return '';
      }
    }
  </script>
  
  <div 
    class={`bg-white dark:bg-gray-800 rounded-t-xl shadow-md ${isHeaderSticky ? 'sticky-header' : ''}`}
  >
    <div class="p-6 flex flex-col lg:flex-row gap-4 justify-between">
      <div class="flex-grow">
        <!-- Status Badges -->
        <div class="flex flex-wrap gap-2">
          <span class={`inline-flex items-center px-2.5 py-0.5 rounded-md text-sm font-medium 
            ${property.status === 'available' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
              property.status === 'under_contract' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' :
              property.status === 'sold' ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' :
              'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'}`}
          >
            {$t(property.status_display)}
          </span>
          
          {#if property.is_featured}
            <span class="inline-flex items-center px-2.5 py-0.5 rounded-md text-sm font-medium bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200">
              <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
              </svg>
              {$t('property.featured')}
            </span>
          {/if}
          
          <span class="inline-flex items-center px-2.5 py-0.5 rounded-md text-sm font-medium bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300">
            {property.property_type_display || property.property_type?.name}
          </span>
          
          {#if property.building_type_display || property.building_type?.name}
            <span class="inline-flex items-center px-2.5 py-0.5 rounded-md text-sm font-medium bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300">
              {property.building_type_display || property.building_type?.name}
            </span>
          {/if}
        </div>
        
        <!-- Property Title -->
        <h1 class="mt-2 text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">
          {property.title}
        </h1>
        
        <!-- Location -->
        <p class="mt-4 text-base sm:text-lg text-gray-500 dark:text-gray-400 flex items-center gap-2">
          <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          {property.location?.address}, {property.location?.city}, {property.location?.state}
        </p>            
      </div>
      
      <!-- Price and Action Buttons -->
      <div class="flex flex-col items-start lg:items-end justify-center">
        <div class="flex flex-col items-center lg:items-end">
          <p class="text-sm text-gray-500 dark:text-gray-400">{$t('property.marketValue')}</p>
          <p class="text-2xl sm:text-3xl font-bold text-primary-600 dark:text-primary-400">
            {formatCurrency(property.market_value)}
          </p>
        </div>
        
        <!-- Action Buttons -->
        <div class="mt-4 flex flex-wrap gap-3">
          {#if canEdit}
            <a 
              href={`/properties/edit/${property.id}`} 
              class="inline-flex items-center px-3 py-1.5 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-gray-200 dark:border-gray-600 dark:hover:bg-gray-600 transition-colors"
            >
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9L9 10L3.414 6.586A2 2 0 013.414 5H6a2 2 0 012 2v11a2 2 0 01-2 2H5a2 2 0 00-2 2v-5m5.586 0l-1.621 1.621a1.5 1.5 0 01-2.121.879 2 2 0 00-1.749 2.037l-.879 2.121a4 4 0 00-.621 3.677v.105c0 1.795.697 3.511 1.75 4.385A4.002 4.002 0 009 18c0 1.216-.876 2.271-2.121 2.62l2.121.879a4 4 0 0017.5-6.844 4 4 0 00-6.879-7.5l2.121-.879a4.002 4.002 0 002.121-2.62 4 4 0 001.75-4.385V16a4 4 0 00-.879-3.677c0-1.795.697-3.511 1.75-4.385a4.002 4.002 0 002.121-2.62l-.879-2.121a1.5 1.5 0 012.121-2.121l1.621-1.621a2 2 0 012 2v5m-5 4H6a2 2 0 002 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9l1.621 1.621a1.5 1.5 0 002.121 2.121l-1.621 1.621a2 2 0 01-2.828 0l-1.621-1.621a4 4 0 00-3.677-.621V10a4 4 0 00-4.385-1.75t-4.385 1.75V6a2 2 0 012-2h2a2 2 0 012 2v12a2 2 0 01-2 2h-2a2 2 0 01-2-2V10a4 4 0 00-.621-3.677l2.121-.879a4.002 4.002 0 01.879-2.121 4 4 0 00-6.844-7.5l-.879-2.121a4 4 0 00-7.5-6.844V0C2 4.477 4.477 0 9 0h6c4.523 0 8 4.477 8 10v6a4 4 0 01-.879 3.677l-2.121.879z" />
              </svg>
              {$t('property.edit')}
            </a>
          {/if}
          
          <button
            on:click={onContactOwner}
            class="inline-flex items-center px-3 py-1.5 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:ring-2 focus:ring-primary-500 transition-colors"
          >
            <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h9a2 2 0 002 2v1.41a2 2 0 01-2 2H5a2 2 0 00-2-2V7a2 2 0 00-2-2h9m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            {$t('property.contactOwner')}
          </button>
        </div>
      </div>
    </div>
    
    <!-- Tab Navigation -->
    <div class="border-t border-gray-200 dark:border-gray-700 pt-1 px-4 flex overflow-x-auto scrollbar-hide">
      {#each tabs as tab}
        <button 
          class={`flex items-center whitespace-nowrap py-4 px-4 border-b-2 font-medium text-sm
            ${activeTab === tab.id 
              ? 'border-primary-500 text-primary-600 dark:text-primary-400' 
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300 dark:hover:border-gray-600'
            } transition-colors duration-200`}
          on:click={() => onSetActiveTab(tab.id)}
          aria-selected={activeTab === tab.id}
          role="tab"
        >
          {@html getIcon(tab.icon)}
          <span class="ml-2">{tab.label}</span>
        </button>
      {/each}
    </div>
  </div>
  
  <style>
    .sticky-header {
      position: sticky;
      top: 0;
      z-index: 20;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    
    .scrollbar-hide {
      -ms-overflow-style: none;
      scrollbar-width: none;
    }
    
    .scrollbar-hide::-webkit-scrollbar {
      display: none;
    }
  </style>