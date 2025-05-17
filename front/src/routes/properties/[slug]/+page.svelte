<!-- src/routes/properties/[slug]/+page.svelte -->
<script>
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { goto } from '$app/navigation';
    import { t } from '$lib/i18n/i18n';
    import { user } from '$lib/stores/user';
    import { getPropertyBySlug } from '$lib/api/property';
    import { createEventDispatcher } from 'svelte';
    
    // Components import
    import TagSelector from '$lib/components/TagSelector.svelte';
    
    // Event dispatcher for any custom events
    const dispatch = createEventDispatcher();
    
    // State variables
    let property = null;
    let loading = true;
    let error = null;
    let activeImageIndex = 0;
    let showFullScreenGallery = false;
    let mapInitialized = false;
    let mapElement;
    let map;
    let marker;
    
    // Get the slug from the URL parameters
    $: slug = $page.params.slug;
    
    // Load property data
    async function loadProperty() {
      try {
        loading = true;
        error = null;
        
        // Fetch property by slug
        const response = await getPropertyBySlug(slug);
        property = response;
        
        // Initialize map on property load
        if (property && property.location && property.location.latitude && property.location.longitude) {
          initializeMap();
        }
      } catch (err) {
        console.error('Error loading property:', err);
        error = err.message || $t('error.fetchFailed');
      } finally {
        loading = false;
      }
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
    
    // Initialize map if needed
    function initializeMap() {
      if (typeof window === 'undefined' || !property || mapInitialized) return;
      
      // Load Leaflet if not already loaded
      if (!window.L) {
        const cssLink = document.createElement('link');
        cssLink.rel = 'stylesheet';
        cssLink.href = 'https://unpkg.com/leaflet@1.9.3/dist/leaflet.css';
        document.head.appendChild(cssLink);
        
        const script = document.createElement('script');
        script.src = 'https://unpkg.com/leaflet@1.9.3/dist/leaflet.js';
        script.onload = createMap;
        document.head.appendChild(script);
      } else {
        createMap();
      }
    }
    
    // Create the map with property location
    function createMap() {
      if (!mapElement || !property?.location) return;
      
      const lat = property.location.latitude || 0;
      const lng = property.location.longitude || 0;
      
      // Don't create map if coordinates are missing
      if (!lat || !lng) return;
      
      // Initialize the map
      map = L.map(mapElement).setView([lat, lng], 15);
      
      // Add OpenStreetMap layer
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      }).addTo(map);
      
      // Add marker for the property location
      marker = L.marker([lat, lng]).addTo(map)
        .bindPopup(`<strong>${property.title}</strong><br>${property.location.address}`);
      
      // Mark as initialized
      mapInitialized = true;
    }
    
    // Navigate to the image at the specified index
    function showImage(index) {
      activeImageIndex = index;
    }
    
    // Toggle full-screen gallery
    function toggleGallery() {
      showFullScreenGallery = !showFullScreenGallery;
    }
    
    // Navigate to next image
    function nextImage() {
      if (property?.media?.length) {
        activeImageIndex = (activeImageIndex + 1) % property.media.length;
      }
    }
    
    // Navigate to previous image
    function prevImage() {
      if (property?.media?.length) {
        activeImageIndex = (activeImageIndex - 1 + property.media.length) % property.media.length;
      }
    }
    
    // Check if user is owner or has permission to edit
    $: canEdit = $user && (
      $user.is_staff || 
      ($user.role === 'appraiser') || 
      (property?.owner?.id === $user.id)
    );
    
    // Contact property owner
    function contactOwner() {
      if (!$user) {
        goto('/login');
        return;
      }
      
      // Implement contact functionality here
      // You could use a modal for a contact form
    }
    
    // Check for keyboard shortcuts for gallery navigation
    function handleKeydown(event) {
      if (showFullScreenGallery) {
        if (event.key === 'ArrowRight' || event.key === 'ArrowDown') {
          nextImage();
        } else if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') {
          prevImage();
        } else if (event.key === 'Escape') {
          showFullScreenGallery = false;
        }
      }
    }
    
    // Load property on mount and when slug changes
    $: if (slug) {
      loadProperty();
    }
    
    onMount(() => {
      // Load property data on mount
      loadProperty();
      
      // Add keyboard listener for gallery navigation
      window.addEventListener('keydown', handleKeydown);
      
      // Cleanup on unmount
      return () => {
        window.removeEventListener('keydown', handleKeydown);
        if (map) {
          map.remove();
          mapInitialized = false;
        }
      };
    });
  </script>
  
  <svelte:head>
    <title>{property?.title || $t('property.loading')} | Real Estate Platform</title>
    <meta name="description" content={property?.meta_description || property?.description?.substr(0, 160) || ''} />
  </svelte:head>
  
  <div class="bg-gray-50 dark:bg-gray-900 min-h-screen py-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Loading State -->
      {#if loading && !property}
        <div class="flex justify-center items-center py-20">
          <div class="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-primary-500"></div>
        </div>
      
      <!-- Error State -->
      {:else if error}
        <div class="bg-red-50 dark:bg-red-900/20 p-6 rounded-lg text-red-800 dark:text-red-200 max-w-3xl mx-auto my-12">
          <h2 class="text-xl font-semibold mb-2">{$t('error.title')}</h2>
          <p>{error}</p>
          <div class="mt-4 flex space-x-4">
            <button
              class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
              on:click={loadProperty}
            >
              {$t('auction.tryAgain')}
            </button>
            <a 
              href="/properties" 
              class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-gray-200 dark:border-gray-600 dark:hover:bg-gray-600"
            >
              {$t('properties.backToProperties')}
            </a>
          </div>
        </div>
      
      <!-- Property Details -->
      {:else if property}
        <div class="mb-6">
          <a 
            href="/properties" 
            class="inline-flex items-center text-sm font-medium text-primary-600 dark:text-primary-400 hover:text-primary-500 dark:hover:text-primary-300"
          >
            <svg class="mr-2 w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            {$t('properties.backToProperties')}
          </a>
        </div>
        
        <!-- Property Header -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden mb-8">
          <div class="p-6 sm:p-8">
            <div class="flex flex-col lg:flex-row justify-between items-start">
              <div>
                <div class="flex items-center">
                  <!-- Status Badge -->
                  <span class={`inline-flex items-center px-2.5 py-0.5 rounded-md text-sm font-medium 
                    ${property.status === 'available' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
                      property.status === 'under_contract' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' :
                      property.status === 'sold' ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' :
                      'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'}`}
                  >
                    {property.status_display}
                  </span>
                  
                  <!-- Featured Badge -->
                  {#if property.is_featured}
                    <span class="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-md text-sm font-medium bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200">
                      {$t('property.featured')}
                    </span>
                  {/if}
                  
                  <!-- Property Type Badge -->
                  <span class="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-md text-sm font-medium bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200">
                    {property.property_type_display}
                  </span>
                </div>
                
                <h1 class="mt-2 text-3xl font-bold text-gray-900 dark:text-white">
                  {property.title}
                </h1>
                
                <p class="mt-2 text-lg text-gray-500 dark:text-gray-400">
                  {property.location?.address}, {property.location?.city}, {property.location?.state}
                </p>
              </div>
              
              <div class="mt-4 lg:mt-0 flex flex-col items-end">
                <p class="text-sm text-gray-500 dark:text-gray-400">{$t('property.marketValue')}</p>
                <p class="text-3xl font-bold text-primary-600 dark:text-primary-400">
                  {formatCurrency(property.market_value)}
                </p>
                
                <!-- Action Buttons -->
                <div class="mt-4 flex space-x-3">
                  {#if canEdit}
                    <a 
                      href={`/properties/edit/${property.id}`} 
                      class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-gray-200 dark:border-gray-600 dark:hover:bg-gray-600"
                    >
                      <svg class="mr-2 -ml-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                      {$t('property.edit')}
                    </a>
                  {/if}
                  
                  <button
                    on:click={contactOwner}
                    class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                  >
                    <svg class="mr-2 -ml-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                    {$t('property.contactOwner')}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Property Content -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <!-- Main Content -->
          <div class="lg:col-span-2">
            <!-- Image Gallery -->
            <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden mb-8">
              <div class="relative">
                {#if property.media && property.media.length > 0}
                  <!-- Main Image -->
                  <div class="aspect-w-16 aspect-h-9 sm:aspect-w-3 sm:aspect-h-2">
                    <img 
                      src={property.media[activeImageIndex]?.url || '/images/property-placeholder.jpg'} 
                      alt={property.title}
                      class="w-full h-full object-cover cursor-pointer"
                      on:click={toggleGallery}
                    />
                  </div>
                  
                  <!-- Gallery Navigation -->
                  {#if property.media.length > 1}
                    <button 
                      class="absolute left-2 top-1/2 transform -translate-y-1/2 bg-white dark:bg-gray-800 rounded-full p-2 shadow-md hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none"
                      on:click={(e) => { e.stopPropagation(); prevImage(); }}
                      aria-label="Previous image"
                    >
                      <svg class="h-5 w-5 text-gray-600 dark:text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                      </svg>
                    </button>
                    <button 
                      class="absolute right-2 top-1/2 transform -translate-y-1/2 bg-white dark:bg-gray-800 rounded-full p-2 shadow-md hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none"
                      on:click={(e) => { e.stopPropagation(); nextImage(); }}
                      aria-label="Next image"
                    >
                      <svg class="h-5 w-5 text-gray-600 dark:text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                      </svg>
                    </button>
                  {/if}
                  
                  <!-- Expand Button -->
                  <button 
                    class="absolute right-2 top-2 bg-white dark:bg-gray-800 rounded-full p-2 shadow-md hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none"
                    on:click={toggleGallery}
                    aria-label="Expand gallery"
                  >
                    <svg class="h-5 w-5 text-gray-600 dark:text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5v-4m0 4h-4m4 0l-5-5" />
                    </svg>
                  </button>
                  
                  <!-- Thumbnails -->
                  {#if property.media.length > 1}
                    <div class="flex overflow-x-auto p-2 space-x-2 border-t border-gray-200 dark:border-gray-700">
                      {#each property.media as image, index}
                        <button 
                          class={`flex-shrink-0 w-16 h-16 rounded-md overflow-hidden border-2 focus:outline-none transition-all duration-200 ${activeImageIndex === index ? 'border-primary-500 transform scale-105' : 'border-transparent'}`}
                          on:click={() => showImage(index)}
                        >
                          <img 
                            src={image.url} 
                            alt={`${property.title} - Image ${index+1}`}
                            class="w-full h-full object-cover"
                          />
                        </button>
                      {/each}
                    </div>
                  {/if}
                {:else}
                  <!-- Placeholder when no images -->
                  <div class="aspect-w-16 aspect-h-9 sm:aspect-w-3 sm:aspect-h-2 bg-gray-100 dark:bg-gray-700 flex items-center justify-center">
                    <svg class="h-16 w-16 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                  </div>
                {/if}
              </div>
            </div>
            
            <!-- Property Description -->
            <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden mb-8">
              <div class="p-6">
                <h2 class="text-xl font-bold text-gray-900 dark:text-white border-b border-gray-200 dark:border-gray-700 pb-3 mb-4">
                  {$t('property.description')}
                </h2>
                <div class="prose dark:prose-invert prose-sm sm:prose sm:max-w-none">
                  <p>{property.description}</p>
                </div>
              </div>
            </div>
            
            <!-- Property Features and Amenities -->
            {#if (property.features && property.features.length > 0) || (property.amenities && property.amenities.length > 0)}
              <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden mb-8">
                <div class="p-6">
                  <h2 class="text-xl font-bold text-gray-900 dark:text-white border-b border-gray-200 dark:border-gray-700 pb-3 mb-4">
                    {$t('property.features')} & {$t('property.amenities')}
                  </h2>
                  
                  {#if property.features && property.features.length > 0}
                    <div class="mb-4">
                      <h3 class="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-2">
                        {$t('property.features')}
                      </h3>
                      <TagSelector 
                        tags={property.features} 
                        selectedTags={property.features} 
                        readonly={true} 
                        variant="pill"
                      />
                    </div>
                  {/if}
                  
                  {#if property.amenities && property.amenities.length > 0}
                    <div>
                      <h3 class="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-2">
                        {$t('property.amenities')}
                      </h3>
                      <TagSelector 
                        tags={property.amenities} 
                        selectedTags={property.amenities} 
                        readonly={true} 
                        variant="pill"
                      />
                    </div>
                  {/if}
                </div>
              </div>
            {/if}
            
            <!-- Rooms List -->
            {#if property.rooms && property.rooms.length > 0}
              <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden mb-8">
                <div class="p-6">
                  <h2 class="text-xl font-bold text-gray-900 dark:text-white border-b border-gray-200 dark:border-gray-700 pb-3 mb-4">
                    {$t('property.roomList')}
                  </h2>
                  
                  <div class="space-y-4">
                    {#each property.rooms as room}
                      <div class="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-750 transition-colors">
                        <div class="flex justify-between">
                          <h3 class="text-lg font-semibold text-gray-800 dark:text-gray-200">
                            {room.name} 
                            <span class="text-sm font-normal text-gray-500 dark:text-gray-400">
                              ({room.room_type_display})
                            </span>
                          </h3>
                          <div>
                            <span class="text-sm text-gray-500 dark:text-gray-400">
                              {$t('property.floor')} {room.floor}
                            </span>
                            {#if room.area_sqm}
                              <span class="ml-3 text-sm text-gray-500 dark:text-gray-400">
                                {room.area_sqm} {$t('property.sqm')}
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
                            <TagSelector 
                              tags={room.features} 
                              selectedTags={room.features} 
                              readonly={true} 
                              size="small"
                            />
                          </div>
                        {/if}
                      </div>
                    {/each}
                  </div>
                </div>
              </div>
            {/if}
            
            <!-- Map -->
            <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden mb-8">
              <div class="p-6">
                <h2 class="text-xl font-bold text-gray-900 dark:text-white border-b border-gray-200 dark:border-gray-700 pb-3 mb-4">
                  {$t('property.location')}
                </h2>
                
                {#if property.location && (property.location.latitude || property.location.longitude)}
                  <div 
                    bind:this={mapElement} 
                    class="h-96 w-full bg-gray-100 dark:bg-gray-700 rounded-lg overflow-hidden"
                  ></div>
                {:else}
                  <div class="h-48 w-full bg-gray-100 dark:bg-gray-700 rounded-lg flex items-center justify-center">
                    <p class="text-gray-500 dark:text-gray-400">
                      {$t('property.noLocationData')}
                    </p>
                  </div>
                {/if}
                
                {#if property.location}
                  <div class="mt-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <p class="text-gray-700 dark:text-gray-300">
                      <strong>{$t('property.location')}:</strong> {property.location.address}, {property.location.city}, {property.location.state}, {property.location.postal_code}, {property.location.country}
                    </p>
                  </div>
                {/if}
              </div>
            </div>
          </div>
          
          <!-- Sidebar -->
          <div class="lg:col-span-1">
            <!-- Property Details Card -->
            <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden mb-8">
              <div class="p-6">
                <h2 class="text-xl font-bold text-gray-900 dark:text-white border-b border-gray-200 dark:border-gray-700 pb-3 mb-4">
                  {$t('property.propertyDetails')}
                </h2>
                
                <div class="space-y-3">
                  <div class="flex justify-between">
                    <span class="text-gray-500 dark:text-gray-400">{$t('property.propertyType')}:</span>
                    <span class="text-gray-900 dark:text-white font-medium">{property.property_type_display}</span>
                  </div>
                  
                  {#if property.building_type}
                    <div class="flex justify-between">
                      <span class="text-gray-500 dark:text-gray-400">{$t('property.buildingType')}:</span>
                      <span class="text-gray-900 dark:text-white font-medium">{property.building_type_display}</span>
                    </div>
                  {/if}
                  
                  <div class="flex justify-between">
                    <span class="text-gray-500 dark:text-gray-400">{$t('property.size')}:</span>
                    <span class="text-gray-900 dark:text-white font-medium">{property.size_sqm} {$t('property.sqm')}</span>
                  </div>
                  
                  {#if property.rooms}
                    <div class="flex justify-between">
                      <span class="text-gray-500 dark:text-gray-400">{$t('property.rooms')}:</span>
                      <span class="text-gray-900 dark:text-white font-medium">{property.rooms.length}</span>
                    </div>
                  {/if}
                  
                  {#if property.floors}
                    <div class="flex justify-between">
                      <span class="text-gray-500 dark:text-gray-400">{$t('property.floors')}:</span>
                      <span class="text-gray-900 dark:text-white font-medium">{property.floors}</span>
                    </div>
                  {/if}
                  
                  {#if property.year_built}
                    <div class="flex justify-between">
                      <span class="text-gray-500 dark:text-gray-400">{$t('property.yearBuilt')}:</span>
                      <span class="text-gray-900 dark:text-white font-medium">{property.year_built}</span>
                    </div>
                  {/if}
                  
                  <div class="flex justify-between">
                    <span class="text-gray-500 dark:text-gray-400">{$t('property.deed_number')}:</span>
                    <span class="text-gray-900 dark:text-white font-medium">{property.deed_number}</span>
                  </div>
                  
                  <div class="pt-3 border-t border-gray-200 dark:border-gray-700">
                    <div class="flex justify-between items-baseline">
                      <span class="text-gray-500 dark:text-gray-400">{$t('property.marketValue')}:</span>
                      <span class="text-xl text-primary-600 dark:text-primary-400 font-bold">{formatCurrency(property.market_value)}</span>
                    </div>
                    
                    {#if property.minimum_bid}
                      <div class="flex justify-between items-baseline mt-1">
                        <span class="text-gray-500 dark:text-gray-400">{$t('property.minimumBid')}:</span>
                        <span class="text-lg text-gray-900 dark:text-white font-semibold">{formatCurrency(property.minimum_bid)}</span>
                      </div>
                    {/if}
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Contact Owner Card -->
            <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden mb-8">
              <div class="p-6">
                <h2 class="text-xl font-bold text-gray-900 dark:text-white border-b border-gray-200 dark:border-gray-700 pb-3 mb-4">
                  {$t('property.contactOwner')}
                </h2>
                
                {#if $user}
                  <form class="space-y-4">
                    <div>
                      <label for="name" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                        {$t('property.name')}
                      </label>
                      <input 
                        type="text" 
                        id="name" 
                        value={`${$user.first_name} ${$user.last_name}`}
                        readonly
                        class="mt-1 block w-full py-2 px-3 border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 rounded-md shadow-sm text-gray-900 dark:text-white sm:text-sm"
                      />
                    </div>
                    
                    <div>
                      <label for="message" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                        {$t('property.message')}
                      </label>
                      <textarea 
                        id="message" 
                        rows="4" 
                        placeholder={$t('property.messagePlaceholder')}
                        class="mt-1 block w-full py-2 px-3 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 text-gray-900 dark:text-white sm:text-sm"
                      ></textarea>
                    </div>
                    
                    <button
                      type="submit"
                      class="w-full inline-flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                    >
                      {$t('property.sendMessage')}
                    </button>
                  </form>
                {:else}
                  <div class="text-center py-6">
                    <p class="text-gray-500 dark:text-gray-400 mb-4">
                      {$t('property.loginToContact')}
                    </p>
                    <a 
                      href="/login" 
                      class="inline-flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                    >
                      {$t('nav.login')}
                    </a>
                  </div>
                {/if}
              </div>
            </div>
          </div>
        </div>
        
        <!-- Related Auctions Section -->
        {#if property.auctions && property.auctions.length > 0}
          <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden mb-8">
            <div class="p-6">
              <h2 class="text-xl font-bold text-gray-900 dark:text-white border-b border-gray-200 dark:border-gray-700 pb-3 mb-4">
                {$t('property.relatedAuctions')}
              </h2>
              
              <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {#each property.auctions as auction}
                  <a href={`/auctions/${auction.slug}`} class="block transform transition-all duration-300 hover:scale-105">
                    <div class="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
                      <div class="p-4">
                        <div class="flex justify-between items-start">
                          <div>
                            <span class={`inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium 
                              ${auction.status === 'live' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
                                auction.status === 'scheduled' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200' :
                                'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'}`}
                            >
                              {auction.status_display}
                            </span>
                            <h3 class="mt-1 text-lg font-semibold text-gray-900 dark:text-white">
                              {auction.title}
                            </h3>
                          </div>
                          <p class="text-lg font-bold text-primary-600 dark:text-primary-400">
                            {formatCurrency(auction.current_bid || auction.starting_bid)}
                          </p>
                        </div>
                        
                        <div class="mt-2 flex justify-between text-sm">
                          <span class="text-gray-500 dark:text-gray-400">
                            {auction.bid_count} {$t('auction.bids')}
                          </span>
                          <span class="text-gray-500 dark:text-gray-400">
                            {new Date(auction.end_date).toLocaleDateString()}
                          </span>
                        </div>
                      </div>
                    </div>
                  </a>
                {/each}
              </div>
            </div>
          </div>
        {:else if property.status === 'available'}
          <div class="bg-gradient-to-r from-primary-50 to-secondary-50 dark:from-primary-900/20 dark:to-secondary-900/20 rounded-lg shadow-md overflow-hidden mb-8">
            <div class="p-6 text-center">
              <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-2">
                {$t('property.startAuction')}
              </h2>
              <p class="text-gray-600 dark:text-gray-300 mb-4">
                {$t('property.startAuctionDesc')}
              </p>
              
              <a 
                href={`/auctions/create?property=${property.id}`} 
                class="inline-flex items-center justify-center px-5 py-3 border border-transparent text-base font-medium rounded-md text-white bg-gradient-to-r from-primary-600 to-secondary-600 hover:from-primary-700 hover:to-secondary-700"
              >
                <svg class="mr-2 -ml-1 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
                {$t('auction.createAuction')}
              </a>
            </div>
          </div>
        {/if}
      {/if}
    </div>
  </div>
  
  <!-- Full Screen Gallery Modal -->
  {#if showFullScreenGallery && property?.media?.length > 0}
    <div 
      class="fixed inset-0 bg-black bg-opacity-90 z-50 flex items-center justify-center p-4 animate-fadeIn"
      on:click={toggleGallery}
    >
      <div class="relative w-full max-w-6xl mx-auto">
        <!-- Close Button -->
        <button 
          class="absolute top-4 right-4 text-white hover:text-gray-300 focus:outline-none z-10"
          on:click={toggleGallery}
          aria-label="Close gallery"
        >
          <svg class="h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
        
        <div class="relative w-full">
          <!-- Main Image -->
          <div 
            class="animate-fadeIn"
            on:click={(e) => e.stopPropagation()}
          >
            <img 
              src={property.media[activeImageIndex]?.url} 
              alt={`${property.title} - Image ${activeImageIndex + 1}`}
              class="mx-auto max-h-[80vh] object-contain"
            />
          </div>
          
          <!-- Navigation Controls -->
          {#if property.media.length > 1}
            <button 
              class="absolute left-2 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-50 rounded-full p-3 text-white hover:bg-opacity-70 focus:outline-none"
              on:click={(e) => { e.stopPropagation(); prevImage(); }}
              aria-label="Previous image"
            >
              <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <button 
              class="absolute right-2 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-50 rounded-full p-3 text-white hover:bg-opacity-70 focus:outline-none"
              on:click={(e) => { e.stopPropagation(); nextImage(); }}
              aria-label="Next image"
            >
              <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </button>
          {/if}
        </div>
        
        <!-- Image Counter -->
        <div class="text-center mt-4 text-white">
          {activeImageIndex + 1} / {property.media.length}
        </div>
      </div>
    </div>
  {/if}
  
  <style>
    .animate-fadeIn {
      animation: fadeIn 0.3s ease-in-out;
    }
    
    .aspect-w-16 {
      position: relative;
      padding-bottom: 56.25%;
    }
    
    .aspect-w-3 {
      position: relative;
      padding-bottom: 66.66%;
    }
    
    .aspect-h-9, .aspect-h-2 {
      position: absolute;
      height: 100%;
      width: 100%;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
    }
    
    @keyframes fadeIn {
      from {
        opacity: 0;
      }
      to {
        opacity: 1;
      }
    }
    
    /* Leaflet dark mode styling */
    :global(.dark .leaflet-tile) {
      filter: invert(1) hue-rotate(180deg) brightness(0.8) contrast(0.8);
    }
    
    :global(.dark .leaflet-container) {
      background: #333;
    }
  </style>