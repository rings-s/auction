<script>
    import { onMount, onDestroy } from 'svelte';
    import { browser } from '$app/environment';
    import { t } from '$lib/i18n';
  
    export let property;
  
    let mapContainer;
    let map = null;
    let marker = null;
    let mounted = false;
    let mapLoaded = false;
    let mapError = false;
  
    $: location = property.location;
    $: hasCoordinates = location?.latitude && location?.longitude;
  
    onMount(async () => {
      mounted = true;
      if (hasCoordinates && browser) {
        // Add a small delay to ensure DOM is ready
        setTimeout(async () => {
          await initializeMap();
        }, 100);
      }
    });
  
    onDestroy(() => {
      if (map) {
        map.remove();
        map = null;
        marker = null;
      }
    });
  
    async function initializeMap() {
      try {
        mapError = false;
        
        // Make sure container exists and has dimensions
        if (!mapContainer) {
          console.error('Map container not found');
          mapError = true;
          return;
        }
  
        // Dynamic import to avoid SSR issues
        const L = await import('leaflet');
        
        // Fix for default markers - more comprehensive fix
        if (L.Icon && L.Icon.Default) {
          delete L.Icon.Default.prototype._getIconUrl;
          L.Icon.Default.mergeOptions({
            iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
            iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
          });
        }
  
        const lat = parseFloat(location.latitude);
        const lng = parseFloat(location.longitude);
  
        console.log('Initializing map with coordinates:', { lat, lng });
  
        // Initialize map with error handling
        map = L.map(mapContainer, {
          center: [lat, lng],
          zoom: 13,
          zoomControl: true,
          attributionControl: true,
          scrollWheelZoom: true,
          dragging: true,
          touchZoom: true,
          doubleClickZoom: true
        });
  
        // Add multiple tile layer options for better reliability
        const tileLayerOptions = [
          {
            url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
            options: {
              attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
              maxZoom: 19
            }
          },
          {
            url: 'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png',
            options: {
              attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>, © <a href="https://carto.com/attributions">CARTO</a>',
              maxZoom: 19,
              subdomains: 'abcd'
            }
          }
        ];
  
        // Try to add the first available tile layer
        let tileLayerAdded = false;
        for (const tileLayerConfig of tileLayerOptions) {
          try {
            const tileLayer = L.tileLayer(tileLayerConfig.url, tileLayerConfig.options);
            tileLayer.addTo(map);
            tileLayerAdded = true;
            console.log('Tile layer added successfully');
            break;
          } catch (error) {
            console.warn('Failed to add tile layer:', error);
          }
        }
  
        if (!tileLayerAdded) {
          throw new Error('Failed to load map tiles');
        }
  
        // Add marker for property location
        marker = L.marker([lat, lng])
          .addTo(map)
          .bindPopup(`
            <div style="padding: 8px; font-family: system-ui, -apple-system, sans-serif;">
              <h3 style="margin: 0 0 4px 0; font-size: 14px; font-weight: 600;">${property.title || 'Property Location'}</h3>
              ${property.address ? `<p style="margin: 2px 0; font-size: 12px; color: #666;">${property.address}</p>` : ''}
              ${location.city ? `<p style="margin: 2px 0; font-size: 12px; color: #888;">${location.city}, ${location.state || ''}</p>` : ''}
            </div>
          `, {
            maxWidth: 250,
            className: 'custom-popup'
          });
  
        // Handle map events
        map.on('load', () => {
          console.log('Map loaded successfully');
          mapLoaded = true;
        });
  
        map.on('error', (e) => {
          console.error('Map error:', e);
          mapError = true;
        });
  
        // Force map to recognize its size
        setTimeout(() => {
          if (map) {
            map.invalidateSize();
            console.log('Map size invalidated');
          }
        }, 250);
  
        // Auto-open popup after a delay
        setTimeout(() => {
          if (marker) {
            marker.openPopup();
          }
        }, 500);
  
        mapLoaded = true;
        console.log('Map initialization completed');
  
      } catch (error) {
        console.error('Error initializing map:', error);
        mapError = true;
      }
    }
  
    // Function to retry map initialization
    function retryMap() {
      mapError = false;
      mapLoaded = false;
      if (map) {
        map.remove();
        map = null;
        marker = null;
      }
      initializeMap();
    }
  </script>
  
  <svelte:head>
    <!-- Try multiple CDN sources for better reliability -->
    <link 
      rel="stylesheet" 
      href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
      integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY="
      crossorigin=""
    />
    <!-- Fallback CSS -->
    <link 
      rel="stylesheet" 
      href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.css"
      crossorigin=""
    />
  </svelte:head>
  
  <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
    <!-- Map Section - Compact & Responsive -->
    <div class="lg:col-span-2">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
        <div 
          class="h-48 sm:h-64 lg:h-80 relative bg-gray-100 dark:bg-gray-700"
          bind:this={mapContainer}
          style="min-height: 200px;"
        >
          <!-- Loading State -->
          {#if !hasCoordinates}
            <div class="absolute inset-0 flex items-center justify-center">
              <div class="text-center">
                <svg class="h-12 w-12 mx-auto text-gray-400 dark:text-gray-500 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6-4h6m-9 0h12a2 2 0 012 2v12a2 2 0 01-2 2H5a2 2 0 01-2-2V10a2 2 0 012-2z" />
                </svg>
                <p class="text-sm text-gray-500 dark:text-gray-400">
                  {$t('property.noLocationData')}
                </p>
              </div>
            </div>
          {:else if mapError}
            <div class="absolute inset-0 flex items-center justify-center">
              <div class="text-center">
                <svg class="h-12 w-12 mx-auto text-red-400 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">
                  {$t('location.mapLoadFailed')}
                </p>
                <button
                  type="button"
                  on:click={retryMap}
                  class="px-3 py-1 text-xs bg-primary-600 text-white rounded hover:bg-primary-700 transition-colors"
                >
                  {$t('common.tryAgain')}
                </button>
              </div>
            </div>
          {:else if !mapLoaded && mounted}
            <div class="absolute inset-0 flex items-center justify-center">
              <div class="text-center">
                <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto mb-2"></div>
                <p class="text-sm text-gray-500 dark:text-gray-400">
                  {$t('common.loading')}...
                </p>
              </div>
            </div>
          {/if}
          
          <!-- Debug Info (remove in production) -->
          {#if hasCoordinates}
            <div class="absolute top-2 left-2 bg-black bg-opacity-75 text-white text-xs p-2 rounded z-[1000]">
              Lat: {location.latitude}, Lng: {location.longitude}
            </div>
          {/if}
        </div>
      </div>
    </div>
  
    <!-- Location Details - Same as before but with debug info -->
    <div class="space-y-4">
      <!-- Address Information -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4">
        <h3 class="text-base font-bold text-gray-900 dark:text-white mb-3">
          {$t('property.addressInfo')}
        </h3>
        
        <div class="space-y-3">
          {#if property.address}
            <div>
              <span class="text-xs text-gray-600 dark:text-gray-400 block mb-1">{$t('location.address')}</span>
              <span class="text-sm font-medium text-gray-900 dark:text-white">{property.address}</span>
            </div>
          {/if}
          
          {#if location}
            <div class="grid grid-cols-1 gap-3">
              {#if location.city}
                <div>
                  <span class="text-xs text-gray-600 dark:text-gray-400 block mb-1">{$t('location.city')}</span>
                  <span class="text-sm font-medium text-gray-900 dark:text-white">{location.city}</span>
                </div>
              {/if}
              
              {#if location.state}
                <div>
                  <span class="text-xs text-gray-600 dark:text-gray-400 block mb-1">{$t('location.state')}</span>
                  <span class="text-sm font-medium text-gray-900 dark:text-white">{location.state}</span>
                </div>
              {/if}
              
              <div class="grid grid-cols-2 gap-3">
                {#if location.country}
                  <div>
                    <span class="text-xs text-gray-600 dark:text-gray-400 block mb-1">{$t('location.country')}</span>
                    <span class="text-sm font-medium text-gray-900 dark:text-white">{location.country}</span>
                  </div>
                {/if}
                
                {#if location.postal_code}
                  <div>
                    <span class="text-xs text-gray-600 dark:text-gray-400 block mb-1">{$t('location.postalCode')}</span>
                    <span class="text-sm font-medium text-gray-900 dark:text-white">{location.postal_code}</span>
                  </div>
                {/if}
              </div>
            </div>
          {/if}
          
          {#if hasCoordinates}
            <div class="pt-3 border-t border-gray-200 dark:border-gray-700">
              <span class="text-xs text-gray-600 dark:text-gray-400 block mb-2">{$t('property.coordinates')}</span>
              <div class="grid grid-cols-1 gap-2 text-xs">
                <div class="flex justify-between">
                  <span class="text-gray-500 dark:text-gray-400">{$t('location.latitude')}:</span>
                  <span class="font-mono font-medium text-gray-900 dark:text-white">
                    {parseFloat(location.latitude).toFixed(6)}
                  </span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-500 dark:text-gray-400">{$t('location.longitude')}:</span>
                  <span class="font-mono font-medium text-gray-900 dark:text-white">
                    {parseFloat(location.longitude).toFixed(6)}
                  </span>
                </div>
              </div>
            </div>
          {/if}
  
        
        </div>
      </div>
  
      <!-- Map Controls -->
      {#if hasCoordinates && map && mapLoaded}
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4">
          <h3 class="text-base font-bold text-gray-900 dark:text-white mb-3">
            Map Controls
          </h3>
          <div class="grid grid-cols-3 gap-2">
            <button
              type="button"
              on:click={() => map.zoomIn()}
              class="px-2 py-1 text-xs bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors"
            >
              Zoom In
            </button>
            <button
              type="button"
              on:click={() => map.zoomOut()}
              class="px-2 py-1 text-xs bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors"
            >
              Zoom Out
            </button>
            <button
              type="button"
              on:click={() => map.setView([parseFloat(location.latitude), parseFloat(location.longitude)], 13)}
              class="px-2 py-1 text-xs bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 border border-primary-200 dark:border-primary-800 rounded hover:bg-primary-200 dark:hover:bg-primary-900/50 transition-colors"
            >
              Reset
            </button>
          </div>
        </div>
      {/if}
    </div>
  </div>
  
  <style>
    /* Ensure map container has proper styling */
    :global(.leaflet-container) {
      height: 100% !important;
      width: 100% !important;
      border-radius: 0.5rem;
    }
    
    /* Custom popup styling */
    :global(.custom-popup .leaflet-popup-content-wrapper) {
      border-radius: 0.5rem;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    /* Fix for map controls */
    :global(.leaflet-control-container) {
      font-family: inherit;
    }
  </style>