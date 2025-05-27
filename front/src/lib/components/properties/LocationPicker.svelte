<!-- src/lib/components/LocationPicker.svelte -->
<script>
  import { onMount, createEventDispatcher } from 'svelte';
  import { t } from '$lib/i18n';
  
  // Exported props with defaults
  export let latitude = null;
  export let longitude = null;
  export let address = '';
  export let city = '';
  export let state = '';
  export let postalCode = '';
  export let country = 'المملكة العربية السعودية';
  export let zoom = 13;
  export let height = '400px';
  export let readonly = false;
  
  // Internal state
  const dispatch = createEventDispatcher();
  let mapElement;
  let map;
  let marker;
  let searchControl;
  let locationLoading = false;
  let locationError = '';
  let locationSuccess = '';
  let locationMode = 'manual';
  
  let initAttempts = 0;
  let observer;
  
  onMount(() => {
    // Use a longer delay for initial load
    setTimeout(() => {
      // First try to load the script
      loadMapScript();
      
      // Set up a mutation observer to watch for visibility changes
      setupVisibilityObserver();
      
      // Also set up an interval to keep trying initialization
      const initInterval = setInterval(() => {
        if (map) {
          clearInterval(initInterval);
          return;
        }
        
        if (initAttempts > 20) { // Give up after ~10 seconds
          clearInterval(initInterval);
          console.error('Gave up trying to initialize map after multiple attempts');
          return;
        }
        
        console.log('Attempting map initialization again...');
        initAttempts++;
        loadMapScript();
      }, 500);
    }, 1000);
    
    return () => {
      if (map) {
        map.remove();
      }
      if (observer) {
        observer.disconnect();
      }
    };
  });
  
  function setupVisibilityObserver() {
    // Create a visibility observer to detect when the map container becomes visible
    if (typeof MutationObserver !== 'undefined') {
      observer = new MutationObserver((mutations) => {
        for (const mutation of mutations) {
          if (mutation.type === 'attributes' && 
              (mutation.attributeName === 'style' || mutation.attributeName === 'class')) {
            console.log('Map container attributes changed, checking visibility...');
            checkAndInitializeMap();
          }
        }
      });
      
      // Start observing the document body for DOM changes
      observer.observe(document.body, { 
        attributes: true, 
        childList: true, 
        subtree: true 
      });
    }
  }
  
  function loadMapScript() {
    console.log('Loading map scripts...');
    // Add CSS if not already present
    if (!document.getElementById('leaflet-css')) {
      const cssLink = document.createElement('link');
      cssLink.id = 'leaflet-css';
      cssLink.rel = 'stylesheet';
      cssLink.href = 'https://unpkg.com/leaflet@1.9.3/dist/leaflet.css';
      document.head.appendChild(cssLink);
    }
    
    // Add script if not already loaded
    if (!window.L) {
      console.log('Leaflet not loaded, loading script...');
      const script = document.createElement('script');
      script.id = 'leaflet-js';
      script.src = 'https://unpkg.com/leaflet@1.9.3/dist/leaflet.js';
      script.onload = () => {
        console.log('Leaflet script loaded successfully');
        // Add a longer delay to ensure DOM is ready
        setTimeout(checkAndInitializeMap, 500);
      };
      document.head.appendChild(script);
    } else {
      console.log('Leaflet already loaded');
      // If already loaded, still use a delay
      setTimeout(checkAndInitializeMap, 300);
    }
  }
  
  function checkAndInitializeMap() {
    console.log('Checking if map element is ready...');
    if (!mapElement) {
      // Only log once per attempt
      if (!window._lastMapErrorLogged || window._lastMapErrorLogged !== initAttempts) {
        console.error('Map element not available yet, retrying in 500ms...');
        window._lastMapErrorLogged = initAttempts;
      }
      // Also show a user-friendly error after several failed attempts
      if (initAttempts > 10) {
        locationError = $t('location.mapInitFailed') || 'Unable to initialize map. Please make sure the map section is visible.';
      }
      return false;
    }
    // Only initialize if the element is visible
    if (mapElement.offsetParent === null || mapElement.offsetWidth === 0 || mapElement.offsetHeight === 0) {
      if (!window._lastMapErrorLogged || window._lastMapErrorLogged !== initAttempts) {
        console.error('Map element is not visible, retrying later...');
        window._lastMapErrorLogged = initAttempts;
      }
      if (initAttempts > 10) {
        locationError = $t('location.mapInitFailed') || 'Unable to initialize map. Please make sure the map section is visible.';
      }
      return false;
    }
    
    if (!window.L) {
      console.error('Leaflet library not available yet, retrying in 500ms...');
      return false;
    }
    
    // Check if the map element has dimensions
    const rect = mapElement.getBoundingClientRect();
    console.log('Map element dimensions:', rect.width, 'x', rect.height);
    
    if (rect.width === 0 || rect.height === 0) {
      console.error('Map element has zero dimensions, forcing dimensions...');
      // Force dimensions
      forceMapDimensions();
      return false;
    }
    
    // Check if the element is visible
    const style = window.getComputedStyle(mapElement);
    if (style.display === 'none' || style.visibility === 'hidden' || !isElementInViewport(mapElement)) {
      console.error('Map element is not visible, retrying later...');
      return false;
    }
    
    // If we already have a map, don't initialize again
    if (map) {
      console.log('Map already initialized, refreshing size...');
      map.invalidateSize();
      return true;
    }
    
    console.log('Map element and Leaflet available, initializing map...');
    initializeMap();
    return true;
  }
  
  function forceMapDimensions() {
    if (!mapElement) return;
    
    // Force dimensions on the map element
    mapElement.style.width = '100%';
    mapElement.style.height = '400px';
    mapElement.style.minHeight = '400px';
    mapElement.style.display = 'block';
    mapElement.style.position = 'relative';
    mapElement.style.visibility = 'visible';
    
    // Force dimensions on parent containers too
    let parent = mapElement.parentElement;
    while (parent) {
      const style = window.getComputedStyle(parent);
      if (style.display === 'none' || style.height === '0px') {
        parent.style.display = 'block';
        parent.style.minHeight = '400px';
        parent.style.height = 'auto';
      }
      parent = parent.parentElement;
    }
  }
  
  function isElementInViewport(el) {
    if (!el) return false;
    
    const rect = el.getBoundingClientRect();
    return (
      rect.top >= 0 &&
      rect.left >= 0 &&
      rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
      rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
  }
  
  function initializeMap() {
    if (!window.L || !mapElement) {
      console.error('Cannot initialize map: Leaflet or map element not available');
      return;
    }
    
    try {
      // If map already exists, just refresh it
      if (map) {
        console.log('Map already exists, refreshing size');
        map.invalidateSize();
        return;
      }
      
      console.log('Initializing map with element:', mapElement);
      const defaultLat = latitude || 24.7136;
      const defaultLng = longitude || 46.6753;
      
      // Make sure the map container is visible and has dimensions
      mapElement.style.width = '100%';
      mapElement.style.height = '100%';
      mapElement.style.minHeight = '400px';
      
      map = window.L.map(mapElement, {
        center: [defaultLat, defaultLng],
        zoom,
        scrollWheelZoom: true,
        dragging: !readonly,
        zoomControl: !readonly
      });
      
      window.L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      }).addTo(map);
      
      // Add a delay and then invalidate size to handle any rendering issues
      setTimeout(() => {
        if (map) {
          console.log('Invalidating map size after delay');
          map.invalidateSize();
        }
      }, 1000);
      
      marker = window.L.marker([defaultLat, defaultLng], {
        draggable: !readonly
      }).addTo(map);
      
      if (!readonly) {
        marker.on('dragend', (event) => {
          const position = event.target.getLatLng();
          updateCoordinates(position.lat, position.lng);
          reverseGeocode(position.lat, position.lng);
        });
        
        map.on('click', (e) => {
          marker.setLatLng(e.latlng);
          updateCoordinates(e.latlng.lat, e.latlng.lng);
          reverseGeocode(e.latlng.lat, e.latlng.lng);
        });
        
        addSearchControl();
      }
      
      // Force map to update its size with a longer delay
      setTimeout(() => {
        if (map) {
          console.log('Invalidating map size');
          map.invalidateSize(true);
        }
      }, 500);
      
      // Add another size update when tab becomes visible
      document.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'visible' && map) {
          setTimeout(() => map.invalidateSize(true), 300);
        }
      });
      
      // Automatically try to detect location when map is initialized
      if (!latitude && !longitude && !readonly) {
        // Add a short delay to ensure map is fully initialized
        setTimeout(() => {
          detectLocation();
        }, 1000);
      }
    } catch (error) {
      console.error('Error initializing map:', error);
      locationError = $t('location.mapInitFailed');
    }
  }
  
  async function detectLocation() {
    if (!navigator.geolocation) {
      locationError = $t('location.geolocationNotSupported') || 'Geolocation is not supported by your browser.';
      return;
    }
    
    locationLoading = true;
    locationError = '';
    locationSuccess = '';
    
    try {
      // Use a promise with a longer timeout for better reliability
      const position = await new Promise((resolve, reject) => {
        const timeoutId = setTimeout(() => {
          reject(new Error('Geolocation request timed out. Please check your browser settings.'));
        }, 10000); // 10 second timeout
        
        navigator.geolocation.getCurrentPosition(
          (position) => {
            clearTimeout(timeoutId);
            resolve(position);
          },
          (error) => {
            clearTimeout(timeoutId);
            reject(error);
          },
          {
            enableHighAccuracy: true,
            timeout: 8000,
            maximumAge: 0
          }
        );
      });
      
      const { latitude: lat, longitude: lng } = position.coords;
      console.log('Location detected:', lat, lng);
      
      if (map && marker) {
        // Update map view and marker
        map.setView([lat, lng], zoom);
        marker.setLatLng([lat, lng]);
      }
      
      // Update coordinates
      updateCoordinates(lat, lng);
      
      // Perform reverse geocoding to get address details
      await reverseGeocode(lat, lng);
      
      locationSuccess = $t('location.detectionSuccess') || 'Location detected successfully!';
    } catch (error) {
      console.error('Geolocation error:', error);
      
      // Provide more helpful error messages based on error code
      if (error.code === 1) {
        locationError = $t('location.permissionDenied') || 'Location permission denied. Please allow location access in your browser settings.';
      } else if (error.code === 2) {
        locationError = $t('location.positionUnavailable') || 'Unable to determine your location. Try again or enter your location manually.';
      } else if (error.code === 3) {
        locationError = $t('location.timeout') || 'Location request timed out. Please try again.';
      } else {
        locationError = $t('location.detectionFailed') || 'Failed to detect location: ' + (error.message || 'Unknown error');
      }
    } finally {
      locationLoading = false;
    }
  }
  
  async function reverseGeocode(lat, lng) {
    try {
      console.log('Reverse geocoding coordinates:', lat, lng);
      
      // Use OpenStreetMap Nominatim for reverse geocoding with proper error handling
      const response = await fetch(
        `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&addressdetails=1&accept-language=en`,
        {
          headers: {
            'Accept-Language': 'en' // Request English results for consistency
          }
        }
      );
      
      if (!response.ok) {
        throw new Error(`Geocoding failed with status: ${response.status}`);
      }
      
      const data = await response.json();
      
      if (!data || !data.address) {
        throw new Error('No address data returned from geocoding service');
      }
      
      console.log('Geocoding result:', data);
      
      // Extract address components with fallbacks for better reliability
      address = [
        data.address.road || data.address.street || '',
        data.address.house_number || '',
        data.address.suburb || data.address.neighbourhood || ''
      ].filter(Boolean).join(', ');
      
      // Set city with fallbacks
      city = data.address.city || 
             data.address.town || 
             data.address.village || 
             data.address.hamlet || 
             data.address.county ||
             '';
      
      // Set state with fallbacks
      state = data.address.state || 
              data.address.province || 
              data.address.region || 
              '';
      
      // Set postal code
      postalCode = data.address.postcode || '';
      
      // Set country (keep default if not provided)
      if (data.address.country) {
        country = data.address.country;
      }
      
      // Dispatch event to update parent component
      dispatch('locationChange', {
        latitude,
        longitude,
        address,
        city,
        state,
        postalCode,
        country
      });
      
      console.log('Location fields updated:', { address, city, state, postalCode, country });
    } catch (error) {
      console.error('Reverse geocoding error:', error);
      locationError = $t('location.geocodingFailed') || 'Failed to get address details from coordinates';
      
      // Even if geocoding fails, still update coordinates
      dispatch('locationChange', {
        latitude,
        longitude,
        address,
        city,
        state,
        postalCode,
        country
      });
    }
  }
  
  function updateCoordinates(lat, lng) {
    latitude = parseFloat(lat.toFixed(6));
    longitude = parseFloat(lng.toFixed(6));
    
    dispatch('locationChange', {
      latitude,
      longitude,
      address,
      city,
      state,
      postalCode,
      country
    });
  }
  
  function addSearchControl() {
    if (!map) return;
    
    const searchBox = L.control({ position: 'topleft' });
    
    searchBox.onAdd = function() {
      const div = L.DomUtil.create('div', 'leaflet-control leaflet-bar');
      div.innerHTML = `
        <div class="p-2 bg-white dark:bg-gray-800 rounded-lg shadow">
          <input
            type="text"
            placeholder="${$t('location.searchPlaceholder') || 'Search for a location...'}"
            class="w-64 px-3 py-2 text-sm border rounded-md focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
          />
        </div>
      `;
      
      const input = div.querySelector('input');
      
      // Prevent map zoom when scrolling the search box
      L.DomEvent.disableScrollPropagation(div);
      
      input.addEventListener('keypress', async (e) => {
        if (e.key === 'Enter') {
          try {
            const response = await fetch(
              `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(input.value)}`
            );
            
            if (!response.ok) throw new Error('Search failed');
            
            const data = await response.json();
            
            if (data && data[0]) {
              const { lat, lon } = data[0];
              map.setView([lat, lon], zoom);
              marker.setLatLng([lat, lon]);
              updateCoordinates(lat, lon);
              reverseGeocode(lat, lon);
            }
          } catch (error) {
            console.error('Search error:', error);
            locationError = $t('location.searchFailed') || 'Location search failed';
          }
        }
      });
      
      return div;
    };
    
    searchBox.addTo(map);
  }
  
  $: if (map && latitude && longitude) {
    map.setView([latitude, longitude], zoom);
    marker.setLatLng([latitude, longitude]);
  }
</script>

<div class="space-y-6">
  <div>
    <h3 class="text-lg font-medium leading-6 text-gray-900 dark:text-white">
      {$t('location.title') || 'Location'}
    </h3>
    <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
      {$t('location.locationDesc') || 'Provide the property location details'}
    </p>
  </div>
  
  {#if !readonly}
    <div class="flex space-x-4">
      <button
        type="button"
        class={`px-4 py-2 text-sm font-medium rounded-md ${
          locationMode === 'map'
            ? 'bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300'
            : 'bg-white text-gray-700 dark:bg-gray-800 dark:text-gray-300 border border-gray-300 dark:border-gray-600'
        }`}
        on:click={() => (locationMode = 'map')}
      >
        <svg
          class="inline-block w-4 h-4 mr-1"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"
          />
        </svg>
        {$t('location.useMap') || 'Use Map'}
      </button>
      <button
        type="button"
        class={`px-4 py-2 text-sm font-medium rounded-md ${
          locationMode === 'manual'
            ? 'bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300'
            : 'bg-white text-gray-700 dark:bg-gray-800 dark:text-gray-300 border border-gray-300 dark:border-gray-600'
        }`}
        on:click={() => (locationMode = 'manual')}
      >
        <svg
          class="inline-block w-4 h-4 mr-1"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
          />
        </svg>
        {$t('location.enterManually') || 'Enter Manually'}
      </button>
    </div>
  {/if}
  
  <!-- Form Fields -->
  <div class="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
    <!-- Address -->
    <div class="sm:col-span-6">
      <label
        for="address"
        class="block text-sm font-medium text-gray-700 dark:text-gray-300 required"
      >
        {$t('location.address') || 'Address'} *
      </label>
      <div class="mt-1">
        <input
          type="text"
          id="address"
          bind:value={address}
          required
          {readonly}
          maxlength="255"
          class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
        />
      </div>
    </div>
    
    <!-- City -->
    <div class="sm:col-span-3">
      <label
        for="city"
        class="block text-sm font-medium text-gray-700 dark:text-gray-300 required"
      >
        {$t('location.city') || 'City'} *
      </label>
      <div class="mt-1">
        <input
          type="text"
          id="city"
          bind:value={city}
          required
          {readonly}
          maxlength="100"
          class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
        />
      </div>
    </div>
    
    <!-- State -->
    <div class="sm:col-span-3">
      <label
        for="state"
        class="block text-sm font-medium text-gray-700 dark:text-gray-300 required"
      >
        {$t('location.state') || 'State/Region'} *
      </label>
      <div class="mt-1">
        <input
          type="text"
          id="state"
          bind:value={state}
          required
          {readonly}
          maxlength="100"
          class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
        />
      </div>
    </div>
    
    <!-- Postal Code -->
    <div class="sm:col-span-3">
      <label
        for="postal_code"
        class="block text-sm font-medium text-gray-700 dark:text-gray-300"
      >
        {$t('location.postalCode') || 'Postal Code'}
      </label>
      <div class="mt-1">
        <input
          type="text"
          id="postal_code"
          bind:value={postalCode}
          {readonly}
          maxlength="20"
          class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
        />
      </div>
    </div>
    
    <!-- Country -->
    <div class="sm:col-span-3">
      <label
        for="country"
        class="block text-sm font-medium text-gray-700 dark:text-gray-300"
      >
        {$t('location.country') || 'Country'}
      </label>
      <div class="mt-1">
        <input
          type="text"
          id="country"
          bind:value={country}
          readonly
          class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white bg-gray-100 dark:bg-gray-700"
        />
      </div>
    </div>
  </div>
  
  {#if locationMode === 'map' && !readonly}
    <!-- Map View -->
    <div class="space-y-4">
      <!-- Location Detection -->
      <div class="bg-gray-50 dark:bg-gray-700 p-4 rounded-md">
        <div class="flex items-center justify-between">
          <div>
            <h4 class="text-sm font-medium text-gray-900 dark:text-white">
              {$t('location.detect') || 'Detect My Location'}
            </h4>
            <p class="text-xs text-gray-500 dark:text-gray-400">
              {$t('location.detectHelp') || 'Use your device location to automatically fill address fields'}
            </p>
          </div>
          <button
            type="button"
            on:click={detectLocation}
            disabled={locationLoading}
            class="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
          >
            {#if locationLoading}
              <svg
                class="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  class="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  stroke-width="4"
                />
                <path
                  class="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
            {:else}
              <svg
                class="h-4 w-4 mr-1"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
                />
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
                />
              </svg>
            {/if}
            {locationLoading 
              ? ($t('location.detecting') || 'Detecting...') 
              : ($t('location.detectButton') || 'Detect Location')}
          </button>
        </div>
        
        {#if locationError}
          <div class="mt-2 text-sm text-red-600 dark:text-red-400">
            {locationError}
          </div>
        {/if}
        
        {#if locationSuccess}
          <div class="mt-2 text-sm text-green-600 dark:text-green-400">
            {locationSuccess}
          </div>
        {/if}
      </div>
      
      <!-- Map -->
      <div
        class="bg-gray-100 dark:bg-gray-800 rounded-md overflow-hidden"
        style="height: {height}; min-height: 400px; display: block;"
      >
        <!-- Map container with explicit ID for easier debugging -->
        <div 
          bind:this={mapElement} 
          id="leaflet-map-container"
          class="w-full h-full" 
          style="min-height: 400px; height: 400px; position: relative; display: block; visibility: visible;"
          aria-label={$t('location.mapContainer') || 'Map container'}
        ></div>
      </div>
      
      <!-- Coordinates -->
      <div class="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-2">
        <div>
          <label
            for="latitude"
            class="block text-sm font-medium text-gray-700 dark:text-gray-300"
          >
            {$t('location.latitude') || 'Latitude'}
          </label>
          <div class="mt-1">
            <input
              type="number"
              id="latitude"
              bind:value={latitude}
              step="0.000001"
              min="-90"
              max="90"
              class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
            />
          </div>
        </div>
        
        <div>
          <label
            for="longitude"
            class="block text-sm font-medium text-gray-700 dark:text-gray-300"
          >
            {$t('location.longitude') || 'Longitude'}
          </label>
          <div class="mt-1">
            <input
              type="number"
              id="longitude"
              bind:value={longitude}
              step="0.000001"
              min="-180"
              max="180"
              class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
            />
          </div>
        </div>
      </div>
    </div>
  {/if}
</div>

<style>
  .required::after {
    content: " *";
    color: rgb(239, 68, 68);
  }
  
  :global(.leaflet-control input) {
    outline: none !important;
  }
  
  :global(.leaflet-control-container .leaflet-control) {
    margin: 10px;
  }
  
  /* Dark mode styles for the map */
  :global(.dark .leaflet-tile) {
    filter: invert(1) hue-rotate(180deg) brightness(0.8) contrast(0.8);
  }
  
  :global(.dark .leaflet-container) {
    background: #333;
  }
</style>