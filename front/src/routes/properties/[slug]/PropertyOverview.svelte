<script>
    import { t } from '$lib/i18n';
    import Gallery from '$lib/components/ui/Gallery.svelte';
    import { translateFeatures } from '$lib/i18n';
  
    export let property;
  
    $: mainImages = property.media?.filter(m => m.media_type === 'image') || [];
    $: galleryImages = mainImages.map(img => ({
      url: img.url || img.file,
      alt: img.name || property.title,
      caption: img.name
    }));
  
    $: keyFeatures = [
      ...(property.features || []).map(f => ({ type: 'feature', value: f })),
      ...(property.amenities || []).slice(0, 6).map(a => ({ type: 'amenity', value: a }))
    ];
  </script>
  
  <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
    <!-- Main Content -->
    <div class="lg:col-span-2 space-y-4">
      <!-- Property Gallery - Responsive Image Sizing -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
        {#if galleryImages.length > 0}
          <div class="h-45 sm:h-75 lg:h-100">
            <Gallery
              images={galleryImages}
              showThumbnails={true}
              autoPlay={false}
              thumbnailSize="sm"
              class="h-full"
            />
          </div>
        {:else}
          <div class="h-45 sm:h-75 lg:h-100 bg-gray-100 dark:bg-gray-700 flex items-center justify-center">
            <div class="text-center">
              <svg class="h-12 w-12 mx-auto text-gray-400 dark:text-gray-500 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <p class="text-sm text-gray-500 dark:text-gray-400">{$t('property.noImages')}</p>
            </div>
          </div>
        {/if}
      </div>
  
      <!-- Description - Compact -->
      {#if property.description}
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4">
          <h2 class="text-lg font-bold text-gray-900 dark:text-white mb-3">
            {$t('property.description')}
          </h2>
          <div class="prose dark:prose-invert max-w-none">
            <p class="text-sm text-gray-600 dark:text-gray-300 leading-relaxed">
              {property.description}
            </p>
          </div>
        </div>
      {/if}
  
      <!-- Key Features Grid - Compact Design -->
      {#if keyFeatures.length > 0}
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4">
          <h2 class="text-lg font-bold text-gray-900 dark:text-white mb-4">
            {$t('property.keyFeatures')}
          </h2>
          <div class="grid grid-cols-2 sm:grid-cols-3 gap-2">
            {#each keyFeatures as feature}
              <div class="flex items-center gap-2 p-2 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div class="w-6 h-6 bg-primary-100 dark:bg-primary-900 rounded-md flex items-center justify-center">
                  <svg class="w-3 h-3 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <span class="text-xs font-medium text-gray-700 dark:text-gray-300 truncate">
                  {translateFeatures([feature.value])[0]}
                </span>
              </div>
            {/each}
          </div>
        </div>
      {/if}
    </div>
  
    <!-- Sidebar - Compact -->
    <div class="space-y-4">
      <!-- Property Details Card - Compact -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4">
        <h3 class="text-base font-bold text-gray-900 dark:text-white mb-3">
          {$t('property.propertyDetails')}
        </h3>
        
        <div class="space-y-3">
          {#if property.market_value}
            <div class="flex justify-between items-center pb-2 border-b border-gray-100 dark:border-gray-700">
              <span class="text-sm text-gray-600 dark:text-gray-400">{$t('property.marketValue')}</span>
              <span class="text-base font-bold text-primary-600 dark:text-primary-400">
                ${property.market_value.toLocaleString()}
              </span>
            </div>
          {/if}
          
          {#if property.size_sqm}
            <div class="flex justify-between items-center pb-2 border-b border-gray-100 dark:border-gray-700">
              <span class="text-sm text-gray-600 dark:text-gray-400">{$t('property.size')}</span>
              <span class="text-sm font-semibold text-gray-900 dark:text-white">
                {property.size_sqm} {$t('property.sqm')}
              </span>
            </div>
          {/if}
          
          {#if property.property_type_display}
            <div class="flex justify-between items-center pb-2 border-b border-gray-100 dark:border-gray-700">
              <span class="text-sm text-gray-600 dark:text-gray-400">{$t('property.propertyType')}</span>
              <span class="text-sm font-semibold text-gray-900 dark:text-white">
                {property.property_type_display}
              </span>
            </div>
          {/if}
          
          {#if property.building_type_display}
            <div class="flex justify-between items-center pb-2 border-b border-gray-100 dark:border-gray-700">
              <span class="text-sm text-gray-600 dark:text-gray-400">{$t('property.buildingType')}</span>
              <span class="text-sm font-semibold text-gray-900 dark:text-white">
                {property.building_type_display}
              </span>
            </div>
          {/if}
          
          {#if property.year_built}
            <div class="flex justify-between items-center pb-2 border-b border-gray-100 dark:border-gray-700">
              <span class="text-sm text-gray-600 dark:text-gray-400">{$t('property.yearBuilt')}</span>
              <span class="text-sm font-semibold text-gray-900 dark:text-white">
                {property.year_built}
              </span>
            </div>
          {/if}
          
          {#if property.floors}
            <div class="flex justify-between items-center">
              <span class="text-sm text-gray-600 dark:text-gray-400">{$t('property.floors')}</span>
              <span class="text-sm font-semibold text-gray-900 dark:text-white">
                {property.floors}
              </span>
            </div>
          {/if}
        </div>
      </div>
  
      <!-- Property Status - Compact -->
      <div class="bg-gradient-to-r from-primary-50 to-blue-50 dark:from-primary-900/20 dark:to-blue-900/20 rounded-lg p-4 border border-primary-200 dark:border-primary-800">
        <div class="flex items-center gap-2 mb-2">
          <div class="w-8 h-8 bg-primary-100 dark:bg-primary-900/50 rounded-lg flex items-center justify-center">
            <svg class="w-4 h-4 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div>
            <h3 class="text-sm font-bold text-primary-900 dark:text-primary-100">
              {$t('property.featured')}
            </h3>
            <p class="text-xs text-primary-700 dark:text-primary-300">
              {property.status_display || $t('property.statusTypes.available')}
            </p>
          </div>
        </div>
        
        {#if property.deed_number}
          <div class="text-xs text-primary-600 dark:text-primary-400">
            {$t('property.deedNumber')}: {property.deed_number}
          </div>
        {/if}
      </div>
    </div>
  </div>
  
  <style>
    /* Responsive image heights */
    .h-45 { height: 11.25rem; } /* 180px */
    .h-75 { height: 18.75rem; } /* 300px */  
    .h-100 { height: 25rem; }   /* 400px */
    
    @media (min-width: 640px) {
      .sm\:h-75 { height: 18.75rem; }
    }
    
    @media (min-width: 1024px) {
      .lg\:h-100 { height: 25rem; }
    }
  </style>