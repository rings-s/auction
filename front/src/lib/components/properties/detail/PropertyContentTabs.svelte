<script>
    import { t } from '$lib/i18n';
    import { tick } from 'svelte';
    import { fade } from 'svelte/transition';
    import Gallery from '$lib/components/ui/Gallery.svelte';
    import PropertyCard from '$lib/components/properties/PropertyCard.svelte';
    import ContactForm from '$lib/components/messages/ContactForm.svelte';
    import PropertyLocationTab from '$lib/components/properties/detail/PropertyLocationTab.svelte';
    import { getFeatureKey, getRoomTypeKey } from '$lib/i18n/mappings';
    
    export let property;
    export let activeTab;
    export let activeImageIndex;
    export let showFullScreenGallery;
    export let filteredMedia;
    export let images;
    export let videos;
    export let documents;
    export let otherFiles;
    export let isImagesLoading;
    export let mapElement;
    export let activeMediaType;
    export let mediaTabs;
    export let mainImage;
    export let onToggleGallery;
    export let onHandleImageLoad;
    export let onSetActiveMediaType;
    
    let initializeMapFunction;
    
    // Handle the location tab initialization
    function handleInitializeMap(fn) {
      initializeMapFunction = fn;
    }
    
    // Initialize map when location tab becomes active
    $: if (activeTab === 'location' && property?.location?.latitude && property?.location?.longitude && initializeMapFunction) {
      tick().then(() => {
        initializeMapFunction();
      });
    }
    
    // Format currency display
    function formatCurrency(value) {
      if (!value) return '$0';
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        maximumFractionDigits: 0
      }).format(value);
    }
    
    // Format file size
    function formatFileSize(bytes) {
      if (!bytes) return '0 Bytes';
      const k = 1024;
      const sizes = ['Bytes', 'KB', 'MB', 'GB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    // Translate room type
    function translateRoomType(roomType) {
      if (!roomType) return '';
      
      const mappedKey = getRoomTypeKey(roomType);
      if (mappedKey) {
        const translationKey = `property.roomTypes.${mappedKey}`;
        const translation = $t(translationKey);
        if (translation !== translationKey) {
          return translation;
        }
      }
      
      const normalizedType = roomType.toLowerCase().replace(/\s+/g, '');
      const translationKey = `property.roomTypes.${normalizedType}`;
      const translation = $t(translationKey);
      if (translation !== translationKey) {
        return translation;
      }
      
      return roomType;
    }
    
    // Translate feature or amenity
    function translateFeatureOrAmenity(item, type) {
      if (!item) return '';
      
      let translationPrefix = 'property.';
      let itemsKey = '';
      
      if (type === 'feature') {
        itemsKey = 'featureItems';
      } else if (type === 'amenity') {
        itemsKey = 'amenityItems';
      } else if (type === 'roomFeature') {
        itemsKey = 'roomFeatureItems';
      } else {
        return item;
      }
      
      const mappedKey = getFeatureKey(item);
      if (mappedKey) {
        const mappedTranslationKey = `${translationPrefix}${itemsKey}.${mappedKey}`;
        const mappedTranslation = $t(mappedTranslationKey);
        if (mappedTranslation !== mappedTranslationKey) {
          return mappedTranslation;
        }
      }
      
      const normalizedItem = item.toLowerCase().replace(/\s+/g, '');
      const translationKey = `${translationPrefix}${itemsKey}.${normalizedItem}`;
      const translation = $t(translationKey);
      
      if (translation === translationKey) {
        const variations = [
          normalizedItem,
          item.toLowerCase(),
          item.replace(/\s+/g, '')
        ];
        
        for (const variation of variations) {
          const variationKey = `property.${type}Items.${variation}`;
          const variationTranslation = $t(variationKey);
          if (variationTranslation !== variationKey) {
            return variationTranslation;
          }
        }
        
        return item;
      }
      
      return translation;
    }
    
    // Get media icon based on type
    function getMediaTypeIcon(type) {
      switch (type) {
        case 'image':
          return `<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>`;
        case 'video':
          return `<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8v6a1 1 0 01-1 1v6a1 1 0 01-1-1v-6a1 1 0 00-1-1H9a1 1 0 00-1 1v6a1 1 0 001 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1V7a1 1 0 011-1h5m0 0V5a2 2 0 012-2h2a2 2 0 012 2v2m-6 3h6m-6 2h6a2 2 0 012 2v3m0 0h-9"></path></svg>`;
        case 'document':
          return `<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"></path></svg>`;
        default:
          return `<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>`;
      }
    }
  </script>
  
  <!-- Tab Content Container -->
<div class="bg-white dark:bg-gray-800 rounded-b-xl shadow-md overflow-hidden">
    <!-- Overview Tab -->
    <div 
      id="tab-overview"
      class="p-8 bg-white dark:bg-gray-800"  
      style="display: {activeTab === 'overview' ? 'block' : 'none'}"
      transition:fade={{ duration: 200 }}
    >
      <div class="grid grid-cols-1 md:grid-cols-3 gap-10">
        <!-- Main Image and Gallery Preview -->
        <div class="md:col-span-2">
          <div class="relative mb-6 rounded-xl overflow-hidden shadow-lg bg-gray-100 dark:bg-gray-800" style="height: 400px;">
            {#if isImagesLoading && images.length > 0}
              <div class="absolute inset-0 flex items-center justify-center bg-gray-100 dark:bg-gray-750">
                <div class="animate-pulse flex flex-col items-center">
                  <div class="rounded-full bg-gray-300 dark:bg-gray-600 h-12 w-12 mb-2"></div>
                  <div class="text-gray-500 dark:text-gray-400">{$t('common.loading')}</div>
                </div>
              </div>
            {/if}
            
            {#if mainImage}
                <img 
                  src="{mainImage?.url}" 
                  alt="{mainImage?.name || property.title}" 
                  class="w-full h-full object-cover transition-opacity duration-300 {isImagesLoading ? 'opacity-0' : 'opacity-100 loaded'}" 
                  on:load={onHandleImageLoad}
                  on:error={(e) => { 
                    e.currentTarget.src = '/images/placeholder-property.jpg'; 
                    isImagesLoading = false;
                  }}
                />
              
              <!-- Gradient overlay at bottom -->
              <div class="absolute inset-x-0 bottom-0 h-24 bg-gradient-to-t from-black/60 to-transparent pointer-events-none"></div>
              
              <!-- Gallery Overlay Button -->
              <button 
                class="absolute bottom-4 right-4 bg-white/90 dark:bg-gray-800/90 rounded-full p-2 shadow-lg hover:bg-white dark:hover:bg-gray-700 transition-colors z-10"
                on:click={onToggleGallery}
                aria-label="View gallery"
              >
                <svg class="h-5 w-5 text-gray-700 dark:text-gray-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5v-4m0 4h-4m4 0l-5-5" />
                </svg>
              </button>
              
              <!-- Image Counter -->
              <div class="absolute bottom-4 left-4 bg-black/70 backdrop-blur-sm text-white text-sm px-3 py-1.5 rounded-md flex items-center z-10">
                <svg class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                {images.length} {$t('property.photos')}
              </div>
            {:else if videos.length > 0}
              <div class="w-full h-full bg-black flex items-center justify-center">
                <video 
                  src={videos[0].url} 
                  controls 
                  class="max-h-full max-w-full"
                  poster={videos[0].thumbnail}
                >
                  <track kind="captions" src="" label="{$t('common.captions')}" />
                  <p>{$t('common.videoNotSupported')}</p>
                </video>
              </div>
            {:else}
              <div class="flex items-center justify-center h-full bg-gray-100 dark:bg-gray-700">
                <svg class="h-16 w-16 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
            {/if}
          </div>
          
          <!-- Thumbnail Preview Gallery -->
          {#if images.length > 1}
            <div class="mt-4 relative">
              <div class="overflow-x-auto scrollbar-thin py-2">
                <div class="flex gap-2">
                  {#each images.slice(0, Math.min(6, images.length)) as image, idx}
                    <button
                      class={`flex-shrink-0 h-16 w-24 rounded-md overflow-hidden border-2 transition-all ${idx === activeImageIndex ? 'border-primary-500 dark:border-primary-400' : 'border-transparent'}`}
                      on:click={() => { activeImageIndex = idx; onToggleGallery(); }}
                    >
                      <img src={image.url} alt={image.name || `Property image ${idx+1}`} class="h-full w-full object-cover" loading="lazy" />
                    </button>
                  {/each}
                  
                  {#if images.length > 6}
                    <button
                      class="flex-shrink-0 h-16 w-24 rounded-md overflow-hidden border-2 border-transparent bg-gray-100 dark:bg-gray-750 flex items-center justify-center group"
                      on:click={onToggleGallery}
                    >
                      <div class="text-center">
                        <span class="block text-sm font-semibold text-gray-800 dark:text-gray-200 group-hover:text-primary-600 dark:group-hover:text-primary-400">+{images.length - 6}</span>
                        <span class="text-xs text-gray-500 dark:text-gray-400">More</span>
                      </div>
                    </button>
                  {/if}
                </div>
              </div>
            </div>
          {/if}
          
          <!-- Description -->
          <div class="mt-10">
            <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center">
              <svg class="w-5 h-5 mr-2 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {$t('property.description')}
            </h2>
            <div class="prose dark:prose-invert max-w-none">
              <p class="text-gray-600 dark:text-gray-300 leading-relaxed text-base">{property.description}</p>
            </div>
          </div>
          
          <!-- Key Features -->
          {#if (property.features && property.features.length > 0) || (property.amenities && property.amenities.length > 0)}
            <div class="mt-10 pb-4">
              <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center">
                <svg class="w-5 h-5 mr-2 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                </svg>
                {$t('property.keyFeatures')}
              </h2>
              
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-8">
                {#if property.features && property.features.length > 0}
                  <div>
                    <h3 class="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-3">
                      {$t('property.features')}
                    </h3>
                    <ul class="space-y-2">
                      {#each property.features as feature}
                        <li class="flex items-center text-gray-600 dark:text-gray-300">
                          <svg class="w-5 h-5 mr-2 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                          </svg>
                          {translateFeatureOrAmenity(feature, 'feature')}
                        </li>
                      {/each}
                    </ul>
                  </div>
                {/if}
                
                {#if property.amenities && property.amenities.length > 0}
                  <div>
                    <h3 class="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-3">
                      {$t('property.amenities')}
                    </h3>
                    <ul class="space-y-2">
                      {#each property.amenities as amenity}
                        <li class="flex items-center text-gray-600 dark:text-gray-300">
                          <svg class="w-5 h-5 mr-2 text-secondary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                          </svg>
                          {translateFeatureOrAmenity(amenity, 'amenity')}
                        </li>
                      {/each}
                    </ul>
                  </div>
                {/if}
              </div>
            </div>
          {/if}
        </div>
        
        <!-- Sidebar -->
        <div class="md:col-span-1">
          <!-- Property Details Card -->
          <div class="bg-gray-50 dark:bg-gray-750 rounded-xl shadow-md overflow-hidden border border-gray-100 dark:border-gray-700">
            <div class="p-5">
              <h2 class="text-lg font-bold text-gray-900 dark:text-white mb-4 flex items-center">
                <svg class="w-5 h-5 mr-2 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                {$t('property.propertyDetails')}
              </h2>
              
              <!-- Details Grid -->
              <div class="space-y-5">
                <div class="grid grid-cols-2 gap-5">
                  <!-- Size -->
                  <div class="bg-white dark:bg-gray-800 p-4 rounded-lg flex flex-col items-center shadow-sm hover:shadow-md transition-shadow border border-gray-100 dark:border-gray-700">
                    <svg class="w-6 h-6 text-primary-500 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    <span class="text-sm text-gray-500 dark:text-gray-400">{$t('property.size')}</span>
                    <span class="text-lg font-bold text-gray-900 dark:text-white">{property.size_sqm} {$t('property.sqm')}</span>
                  </div>
                  
                  <!-- Floors -->
                  <div class="bg-white dark:bg-gray-800 p-4 rounded-lg flex flex-col items-center shadow-sm hover:shadow-md transition-shadow border border-gray-100 dark:border-gray-700">
                    <svg class="w-6 h-6 text-primary-500 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                    </svg>
                    <span class="text-sm text-gray-500 dark:text-gray-400">{$t('property.floors')}</span>
                    <span class="text-lg font-bold text-gray-900 dark:text-white">{property.floors || '1'}</span>
                  </div>
                  
                  <!-- Rooms -->
                  <div class="bg-white dark:bg-gray-800 p-4 rounded-lg flex flex-col items-center shadow-sm hover:shadow-md transition-shadow border border-gray-100 dark:border-gray-700">
                    <svg class="w-6 h-6 text-primary-500 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1V13z" />
                    </svg>
                    <span class="text-sm text-gray-500 dark:text-gray-400">{$t('property.rooms')}</span>
                    <span class="text-lg font-bold text-gray-900 dark:text-white">{property.rooms?.length || 0}</span>
                  </div>
                  
                  <!-- Year Built -->
                  <div class="bg-white dark:bg-gray-800 p-4 rounded-lg flex flex-col items-center shadow-sm hover:shadow-md transition-shadow border border-gray-100 dark:border-gray-700">
                    <svg class="w-6 h-6 text-primary-500 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002 2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    <span class="text-sm text-gray-500 dark:text-gray-400">{$t('property.yearBuilt')}</span>
                    <span class="text-lg font-bold text-gray-900 dark:text-white">{property.year_built || 'N/A'}</span>
                  </div>
                </div>
                
                <!-- Deed Number -->
                <div class="flex justify-between items-center py-2 border-t border-gray-200 dark:border-gray-700">
                  <span class="text-gray-500 dark:text-gray-400">{$t('property.deedNumber')}</span>
                  <span class="text-gray-900 dark:text-white font-medium">{property.deed_number}</span>
                </div>
                
                <!-- Financial Info -->
                <div class="mt-4 bg-gradient-to-r from-primary-50 to-primary-100 dark:from-primary-900/20 dark:to-primary-900/30 p-4 rounded-lg">
                  <div class="flex justify-between items-baseline">
                    <span class="text-gray-600 dark:text-gray-300">{$t('property.marketValue')}</span>
                    <span class="text-xl text-primary-600 dark:text-primary-400 font-bold">{formatCurrency(property.market_value)}</span>
                  </div>
                  
                  {#if property.minimum_bid}
                    <div class="flex justify-between items-baseline mt-2">
                      <span class="text-gray-600 dark:text-gray-300">{$t('property.minimumBid')}</span>
                      <span class="text-lg text-gray-900 dark:text-white font-semibold">{formatCurrency(property.minimum_bid)}</span>
                    </div>
                  {/if}
                </div>
              </div>
            </div>
          </div>
          
          <!-- Contact Owner Card -->
          <div class="mt-8">
            <ContactForm 
              {property} 
              compact={true}
              on:success={(e) => {
                // Handle success
              }}
              on:error={(e) => {
                // Handle error
              }}
            />
          </div>
        </div>
      </div>
    </div>
    
    <!-- Rooms & Features Tab -->
    <div 
      id="tab-rooms"
      class="p-6"
      style="display: {activeTab === 'rooms' ? 'block' : 'none'}"
      transition:fade={{ duration: 200 }}
    >
      {#if property.rooms && property.rooms.length > 0}
        <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-6 flex items-center">
          <svg class="w-6 h-6 mr-2 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
          </svg>
          {$t('property.roomList')}
        </h2>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          {#each property.rooms as room}
            <div class="bg-white dark:bg-gray-750 rounded-xl shadow-sm transition-transform duration-300 hover:scale-[1.02] border border-gray-100 dark:border-gray-700">
              <div class="p-5">
                <div class="flex justify-between items-start">
                  <div>
                    <!-- Room Type Badge -->
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800 dark:bg-primary-900 dark:text-primary-200">
                      {translateRoomType(room.room_type_display)}
                    </span>
                    
                    <!-- Floor Badge -->
                    <span class="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300">
                      {$t('property.floor')} {room.floor}
                    </span>
                    
                    <h3 class="mt-2 text-lg font-semibold text-gray-900 dark:text-white">
                        {room.name}
                      </h3>
                      
                      {#if room.area_sqm}
                        <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
                          {$t('property.area')}: {room.area_sqm} {$t('property.sqm')}
                        </p>
                      {/if}
                    </div>
                    
                    <!-- Room Features Icons -->
                    <div class="flex flex-wrap gap-1 justify-end">
                      {#if room.has_window}
                        <span class="tooltip" data-tooltip={$t('property.hasWindow')}>
                          <svg class="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16m-7 6h7" />
                          </svg>
                        </span>
                      {/if}
                      
                      {#if room.has_bathroom}
                        <span class="tooltip" data-tooltip={$t('property.hasBathroom')}>
                          <svg class="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                          </svg>
                        </span>
                      {/if}
                    </div>
                  </div>
                  
                  {#if room.description}
                    <p class="mt-2 text-sm text-gray-600 dark:text-gray-300">
                      {room.description}
                    </p>
                  {/if}
                  
                  {#if room.features && room.features.length > 0}
                    <div class="mt-3">
                      <h5 class="text-xs font-medium text-gray-500 dark:text-gray-400 mb-1.5">
                        {$t('property.features')}
                      </h5>
                      <div class="flex flex-wrap gap-1.5">
                        {#each room.features as feature}
                          <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-secondary-100 text-secondary-800 dark:bg-secondary-900 dark:text-secondary-200">
                            {translateFeatureOrAmenity(feature, 'roomFeature')}
                          </span>
                        {/each}
                      </div>
                    </div>
                  {/if}
                  
                  <!-- Room Media Thumbnails -->
                  {#if room.media && room.media.length > 0}
                    <div class="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
                      <h5 class="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2">
                        {$t('property.gallery')}
                      </h5>
                      <div class="flex space-x-2 overflow-x-auto pb-2">
                        {#each room.media as mediaItem}
                          {#if mediaItem.media_type === 'image'}
                            <div class="flex-shrink-0 w-16 h-16 rounded-md overflow-hidden">
                              <img src={mediaItem.url} alt={mediaItem.name} class="w-full h-full object-cover" />
                            </div>
                          {:else if mediaItem.media_type === 'video'}
                            <div class="flex-shrink-0 w-16 h-16 rounded-md overflow-hidden bg-black relative">
                              <svg class="absolute inset-0 m-auto w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" />
                              </svg>
                            </div>
                          {/if}
                        {/each}
                      </div>
                    </div>
                  {/if}
                </div>
              </div>
            {/each}
          </div>
        {:else}
          <div class="text-center py-12 bg-gray-50 dark:bg-gray-750 rounded-lg">
            <svg class="mx-auto h-12 w-12 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
            </svg>
            <h3 class="mt-2 text-base font-medium text-gray-900 dark:text-white">
              {$t('property.noRooms')}
            </h3>
            <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
              {$t('property.noRoomsInfo')}
            </p>
          </div>
        {/if}
        
        <!-- Features & Amenities Section -->
        {#if (property.features && property.features.length > 0) || (property.amenities && property.amenities.length > 0)}
          <div class="mt-10">
            <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-6 flex items-center">
              <svg class="w-6 h-6 mr-2 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
              </svg>
              {$t('property.featuresAndAmenities')}
            </h2>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
              {#if property.features && property.features.length > 0}
                <div class="bg-gradient-to-br from-white to-gray-50 dark:from-gray-800 dark:to-gray-750 rounded-xl p-6 shadow-sm border border-gray-100 dark:border-gray-700">
                  <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                    {$t('property.features')}
                  </h3>
                  <div class="grid grid-cols-2 gap-3">
                    {#each property.features as feature}
                      <div class="flex items-center">
                        <svg class="h-5 w-5 text-primary-500 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <span class="text-gray-700 dark:text-gray-300 text-sm">{feature}</span>
                      </div>
                    {/each}
                  </div>
                </div>
              {/if}
              
              {#if property.amenities && property.amenities.length > 0}
                <div class="bg-gradient-to-br from-white to-gray-50 dark:from-gray-800 dark:to-gray-750 rounded-xl p-6 shadow-sm border border-gray-100 dark:border-gray-700">
                  <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                    {$t('property.amenities')}
                  </h3>
                  <div class="grid grid-cols-2 gap-3">
                    {#each property.amenities as amenity}
                      <div class="flex items-center">
                        <svg class="h-5 w-5 text-secondary-500 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <span class="text-gray-700 dark:text-gray-300 text-sm">{amenity}</span>
                      </div>
                    {/each}
                  </div>
                </div>
              {/if}
            </div>
          </div>
        {/if}
    </div>
      
      <!-- Location Tab -->
    <div 
        id="tab-location"
        style="display: {activeTab === 'location' ? 'block' : 'none'}"
        transition:fade={{ duration: 200 }}
    >
        <PropertyLocationTab 
          {property}
          bind:mapElement
          onInitializeMap={handleInitializeMap}
        />
    </div>
      
      <!-- Gallery Tab -->
    <div 
        id="tab-gallery"
        class="p-6" 
        style="display: {activeTab === 'gallery' ? 'block' : 'none'}"
        transition:fade={{ duration: 200 }}
    >
        <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-6 flex items-center">
          <svg class="w-6 h-6 mr-2 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          {$t('property.gallery')}
        </h2>
        
        <!-- Media Type Tabs -->
        <div class="flex overflow-x-auto mb-6 bg-gray-50 dark:bg-gray-750 rounded-lg p-1">
          {#each mediaTabs as tab}
            <button 
              class={`py-2 px-4 font-medium text-sm whitespace-nowrap rounded-md flex items-center
                ${activeMediaType === tab.id 
                  ? 'bg-white dark:bg-gray-800 text-primary-600 dark:text-primary-400 shadow-sm' 
                  : 'bg-transparent text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-200'
                } transition-colors duration-200 mx-1`}
              on:click={() => onSetActiveMediaType(tab.id)}
              disabled={property?.media?.filter(item => item.media_type === tab.id).length === 0}
              class:opacity-50={property?.media?.filter(item => item.media_type === tab.id).length === 0}
            >
              {@html getMediaTypeIcon(tab.id)}
              <span class="ml-2">{tab.label}</span>
              <span class="ml-1.5 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 px-1.5 py-0.5 rounded-full text-xs">
                {property?.media?.filter(item => item.media_type === tab.id).length || 0}
              </span>
            </button>
          {/each}
        </div>
        
        {#if filteredMedia.length > 0}
          <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-5">
            {#each filteredMedia as mediaItem, index}
              <div 
                class="rounded-lg overflow-hidden shadow-md group relative transition-all hover:shadow-lg hover:-translate-y-1 cursor-pointer border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800"
                on:click={() => { activeImageIndex = index; onToggleGallery(); }}
                on:keydown={(e) => { if (e.key === 'Enter' || e.key === ' ') { activeImageIndex = index; onToggleGallery(); } }}
                role="button"
                tabindex="0"
                aria-label={`View ${mediaItem.name || 'media item'}`}
              >
                <!-- Media Preview based on type -->
                <div class="aspect-w-4 aspect-h-3 bg-gray-100 dark:bg-gray-700 relative">
                  {#if mediaItem.media_type === 'image'}
                    <img 
                      src={mediaItem.url} 
                      alt={mediaItem.name || `${property.title} - Image ${index+1}`}
                      class="object-cover w-full h-full transition-transform duration-300 group-hover:scale-105"
                      loading="lazy"
                    />
                    <!-- Dark overlay on hover -->
                    <div class="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-30 transition-opacity"></div>
                  {:else if mediaItem.media_type === 'video'}
                    <div class="w-full h-full flex items-center justify-center bg-black">
                      <svg class="w-12 h-12 text-white opacity-80 group-hover:opacity-100 transition-opacity" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" />
                      </svg>
                    </div>
                  {:else if mediaItem.media_type === 'document'}
                    <div class="w-full h-full flex items-center justify-center bg-blue-50 dark:bg-blue-900/20">
                      <svg class="w-12 h-12 text-blue-400 dark:text-blue-400 group-hover:scale-110 transition-transform" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M4 4a2 2 0 00-2 2v8a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2H4zm2 3a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" />
                      </svg>
                    </div>
                  {:else}
                    <div class="w-full h-full flex items-center justify-center bg-gray-100 dark:bg-gray-800">
                      <svg class="w-12 h-12 text-gray-400 group-hover:text-gray-500 transition-colors" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M4 4a2 2 0 00-2 2v8a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2H4zm12 12H4V6h12v10z" clip-rule="evenodd" />
                      </svg>
                    </div>
                  {/if}
                  
                  <!-- View icon overlay -->
                  <div class="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                    <div class="bg-black bg-opacity-50 rounded-full p-3 backdrop-blur-sm">
                      <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                    </div>
                  </div>
                </div>
                
                <!-- Media Info -->
                <div class="p-3">
                  <h3 class="text-sm font-medium text-gray-900 dark:text-white truncate">
                    {mediaItem.name || `${activeMediaType} ${index+1}`}
                  </h3>
                  
                  <div class="flex justify-between items-center mt-1">
                    {#if mediaItem.dimensions}
                      <span class="text-xs text-gray-500 dark:text-gray-400">
                        {mediaItem.dimensions.width}×{mediaItem.dimensions.height}
                      </span>
                    {/if}
                    
                    {#if mediaItem.file_size}
                      <span class="text-xs text-gray-500 dark:text-gray-400">
                        {formatFileSize(mediaItem.file_size)}
                      </span>
                    {/if}
                  </div>
                </div>
              </div>
            {/each}
          </div>
        {:else}
          <div class="text-center py-12 bg-gray-50 dark:bg-gray-750 rounded-lg">
            <svg class="mx-auto h-12 w-12 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <h3 class="mt-2 text-base font-medium text-gray-900 dark:text-white">
              {$t('property.noImages')}
            </h3>
            <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
              {$t('property.noImagesInfo')}
            </p>
          </div>
        {/if}
      </div>
    </div>
    
<style>
  .scrollbar-thin {
    scrollbar-width: thin;
  }
  
  .scrollbar-thin::-webkit-scrollbar {
    width: 5px;
    height: 5px;
  }
  
  .scrollbar-thin::-webkit-scrollbar-track {
    background: transparent;
  }
  
  .scrollbar-thin::-webkit-scrollbar-thumb {
    background-color: rgba(107, 114, 128, 0.5);
    border-radius: 9999px;
  }
  
  .tooltip {
    position: relative;
    display: inline-block;
  }
  
  .tooltip::before {
    content: attr(data-tooltip);
    position: absolute;
    bottom: 100%;
    left: 50%;
    transform: translateX(-50%);
    padding: 4px 8px;
    background-color: rgba(0, 0, 0, 0.8);
    color: white;
    border-radius: 4px;
    white-space: nowrap;
    visibility: hidden;
    opacity: 0;
    transition: opacity 0.3s, visibility 0.3s;
    font-size: 12px;
    pointer-events: none;
    z-index: 10;
  }
  
  .tooltip:hover::before {
    visibility: visible;
    opacity: 1;
  }
</style>