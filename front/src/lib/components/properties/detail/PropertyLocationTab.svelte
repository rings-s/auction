<script>
    import { t } from '$lib/i18n';
    import { onMount, onDestroy } from 'svelte';
    
    export let property;
    export let mapElement;
    export let onInitializeMap;
    
    let map;
    let marker;
    let mapInitialized = false;
    let showNearbyServices = false;
    
    // Format currency display
    function formatCurrency(value) {
      if (!value) return '$0';
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        maximumFractionDigits: 0
      }).format(value);
    }
    
    // Toggle nearby services
    function toggleNearbyServices() {
      showNearbyServices = !showNearbyServices;
    }
    
    // Initialize map with property location
    function initializeMap() {
      if (typeof window === 'undefined' || !property?.location || mapInitialized) return;
      
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
      
      if (!lat || !lng) return;
      
      // Create map with custom zoom control position
      map = L.map(mapElement, {
        scrollWheelZoom: false,
        dragging: !L.Browser.mobile,
        zoomControl: false // Disable default zoom control to reposition it
      }).setView([lat, lng], 15);
      
      // Add zoom control to bottom right
      L.control.zoom({
        position: 'bottomright'
      }).addTo(map);
      
      // Use CARTO Light map tiles for a clean, modern look
      L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        subdomains: 'abcd',
        maxZoom: 19
      }).addTo(map);
      
      // Create a modern, animated marker
      const customIcon = L.divIcon({
        className: 'custom-map-marker',
        html: `<div class="marker-pin">
                <div class="marker-pulse"></div>
               </div>
               <span class="marker-icon">
                 <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="14" height="14">
                   <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
                 </svg>
               </span>
               ${property.location.house_number ? `<div class="house-number">${property.location.house_number}</div>` : ''}
               `,
        iconSize: [40, 52],
        iconAnchor: [20, 52],
        popupAnchor: [0, -48]
      });
      
      // Add marker with enhanced popup
      marker = L.marker([lat, lng], { icon: customIcon }).addTo(map)
        .bindPopup(`
          <div class="map-popup">
            <h3 class="popup-title">${property.title}</h3>
            <div class="popup-address">
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                <circle cx="12" cy="10" r="3"></circle>
              </svg>
              <span>${property.location.address}</span>
            </div>
            <div class="popup-city-region">
              <span>${property.location.city}, ${property.location.state}</span>
              ${property.location.postal_code ? `<span>${property.location.postal_code}</span>` : ''}
            </div>
            <div class="popup-coords">
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6"></polygon>
                <line x1="8" y1="2" x2="8" y2="18"></line>
                <line x1="16" y1="6" x2="16" y2="22"></line>
              </svg>
              <span>${lat.toFixed(6)}, ${lng.toFixed(6)}</span>
            </div>
            <div class="popup-price">${formatCurrency(property.market_value)}</div>
          </div>
        `, { className: 'custom-popup', maxWidth: 300 });
      
      // Add tooltip that shows on hover (before clicking)
      marker.bindTooltip(`
        <div class="marker-tooltip">
          <strong>${property.location.city}, ${property.location.state}</strong>
          <div>${lat.toFixed(4)}, ${lng.toFixed(4)}</div>
        </div>
      `, { offset: [0, -40], direction: 'top' });
      
      // Add a subtle blue radius circle
      L.circle([lat, lng], {
        radius: 500,
        fillColor: '#3b82f6',
        fillOpacity: 0.08,
        color: '#3b82f6',
        weight: 1
      }).addTo(map);
      
      // Enable scroll wheel zoom when clicking on map
      map.on('click', function() {
        if (!map.scrollWheelZoom.enabled()) {
          map.scrollWheelZoom.enable();
          L.DomUtil.addClass(mapElement, 'active-map');
        }
      });
      
      // Disable scroll wheel zoom when clicking outside map
      document.addEventListener('click', function(e) {
        if (mapElement && !mapElement.contains(e.target)) {
          map.scrollWheelZoom.disable();
          L.DomUtil.removeClass(mapElement, 'active-map');
        }
      });
      
      // Animate marker on load
      setTimeout(() => {
        if (marker) {
          const markerElement = marker.getElement();
          if (markerElement) {
            markerElement.classList.add('marker-bounce');
            setTimeout(() => {
              markerElement.classList.remove('marker-bounce');
            }, 1000);
          }
        }
      }, 500);
      
      mapInitialized = true;
      
      // Make sure map renders correctly
      setTimeout(() => {
        if (map) map.invalidateSize();
      }, 400);
    }
    
    // Expose the initializeMap function to parent
    $: if (onInitializeMap) {
      onInitializeMap(initializeMap);
    }
    
    onDestroy(() => {
      if (map) {
        map.remove();
        mapInitialized = false;
      }
    });
</script>
  
<div class="p-8">
  <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-8 flex items-center">
    <svg class="w-6 h-6 mr-3 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
    </svg>
    {$t('property.location')}
  </h2>
  
  <div class="grid grid-cols-1 md:grid-cols-12 gap-10">
    <!-- Map Container -->
    <div class="md:col-span-8">
      {#if property.location && (property.location.latitude || property.location.longitude)}
        <div class="relative">
          <div 
            bind:this={mapElement} 
            class="h-96 w-full rounded-xl overflow-hidden shadow-lg bg-gray-100 dark:bg-gray-700 border-2 border-gray-200 dark:border-gray-600"
          ></div>
          
          <!-- Map Interaction Notice -->
          <div class="absolute bottom-4 right-4 bg-white dark:bg-gray-800 rounded-lg shadow-lg p-3 max-w-xs opacity-90">
            <p class="text-sm text-gray-600 dark:text-gray-400 font-medium">
              {$t('property.clickToInteract')}
            </p>
          </div>
        </div>
      {:else}
        <div class="h-96 w-full bg-gray-100 dark:bg-gray-700 rounded-xl flex items-center justify-center shadow-lg border-2 border-gray-200 dark:border-gray-600">
          <div class="text-center p-8">
            <svg class="mx-auto h-12 w-12 text-gray-400 dark:text-gray-500 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16l-7-7m0 0l7-7m-7 7h18m-6 4h-5m6 4h5m-6 4h-5m-6-7h11m-6 7h6m6-7v-1a1 1 0 00-1-1H8a1 1 0 00-1 1v12a1 1 0 001 1h2.5a1 1 0 001-1V10a1 1 0 00-1-1H6a1 1 0 001-1h2a1 1 0 001 1v7.5a1 1 0 001 1V10a1 1 0 001 1h2a1 1 0 001-1V4a1 1 0 011-1h1z" />
            </svg>
            <p class="text-gray-500 dark:text-gray-400">
              {$t('property.noLocationData')}
            </p>
          </div>
        </div>
      {/if}
    </div>
    
    <!-- Location Details -->
    <div class="md:col-span-4">
      {#if property.location}
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 h-full border border-gray-100 dark:border-gray-700">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-5 flex items-center">
            <svg class="w-5 h-5 mr-2 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            {$t('property.addressInfo')}
          </h3>
          
          <div class="space-y-4">
            <div class="flex items-center py-2 px-3 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
              <span class="text-gray-600 dark:text-gray-400 w-28 flex-shrink-0 font-medium">{$t('property.address')}:</span>
              <span class="text-gray-900 dark:text-white flex-grow ml-2">{property.location.address}</span>
            </div>
            
            <div class="flex items-center py-2 px-3 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
              <span class="text-gray-600 dark:text-gray-400 w-28 flex-shrink-0 font-medium">{$t('property.city')}:</span>
              <span class="text-gray-900 dark:text-white flex-grow ml-2">{property.location.city}</span>
            </div>
            
            <div class="flex items-center py-2 px-3 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
              <span class="text-gray-600 dark:text-gray-400 w-28 flex-shrink-0 font-medium">{$t('property.state')}:</span>
              <span class="text-gray-900 dark:text-white flex-grow ml-2">{property.location.state}</span>
            </div>
            
            {#if property.location.postal_code}
              <div class="flex items-center py-2 px-3 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
                <span class="text-gray-600 dark:text-gray-400 w-28 flex-shrink-0 font-medium">{$t('property.postalCode')}:</span>
                <span class="text-gray-900 dark:text-white flex-grow ml-2">{property.location.postal_code}</span>
              </div>
            {/if}
            
            <div class="flex items-center py-2 px-3 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
              <span class="text-gray-600 dark:text-gray-400 w-28 flex-shrink-0 font-medium">{$t('property.country')}:</span>
              <span class="text-gray-900 dark:text-white flex-grow ml-2">{property.location.country}</span>
            </div>
            
            {#if property.location.latitude && property.location.longitude}
              <div class="flex items-center py-1.5 px-2 mt-1 border-t border-gray-200 dark:border-gray-700 pt-3 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
                <span class="text-gray-600 dark:text-gray-400 w-28 flex-shrink-0 font-medium">{$t('property.coordinates')}:</span>
                <span class="text-gray-900 dark:text-white flex-grow ml-2 font-mono text-sm">
                  {property.location.latitude}, {property.location.longitude}
                </span>
              </div>
            {/if}
          </div>
          
          <!-- Nearby Services Placeholder -->
          <div class="mt-7 pt-4 border-t border-gray-200 dark:border-gray-700">
            <h4 class="text-base font-medium text-gray-900 dark:text-white mb-3 flex items-center">
              <svg class="w-4 h-4 mr-2 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {$t('property.nearbyServices')}
            </h4>
            <p class="text-sm text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-750 p-3 rounded-lg">
              {$t('property.nearbyServicesInfo')}
            </p>
          </div>
        </div>
      {/if}
    </div>
  </div>
</div>
  
<style>
  /* Map styling */
  :global(.active-map) {
    border: 2px solid #3b82f6;
  }
  
  :global(.leaflet-container) {
    z-index: 1 !important;
  }
  
  :global(.custom-map-marker) {
    width: 30px;
    height: 42px;
    position: relative;
  }
  
  :global(.marker-pin) {
    width: 30px;
    height: 30px;
    border-radius: 50% 50% 50% 0;
    background: #3b82f6;
    position: absolute;
    transform: rotate(-45deg);
    left: 50%;
    top: 50%;
    margin: -15px 0 0 -15px;
    border: 2px solid white;
    box-shadow: 0 1px 3px rgba(0,0,0,0.2);
  }
  
  :global(.marker-icon) {
    background: white;
    width: 14px;
    height: 14px;
    position: absolute;
    margin: 8px 0 0 8px;
    border-radius: 50%;
    left: 0;
    top: 0;
    color: #3b82f6;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  :global(.custom-popup .leaflet-popup-content-wrapper) {
    background: white;
    border-radius: 8px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    padding: 12px;
  }
  
  :global(.map-popup h3) {
    margin: 0 0 5px 0;
    color: #1f2937;
  }
  
  :global(.map-popup p) {
    margin: 0;
    color: #6b7280;
  }
</style>