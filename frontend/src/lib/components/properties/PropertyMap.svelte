<!-- src/lib/components/properties/PropertyMap.svelte -->
<script>
  /**
   * Property Map Component
   * Displays a map with the property location using Leaflet
   */
  import { onMount, onDestroy } from 'svelte';
  import { t, language } from '$lib/i18n';
  import Spinner from '$lib/components/ui/Spinner.svelte';
  import Alert from '$lib/components/ui/Alert.svelte';
  
  // Props
  export let latitude;
  export let longitude;
  export let address = '';
  export let title = '';
  export let zoom = 15;
  export let markerColor = '#3B82F6'; // primary color
  export let height = '100%';
  export let interactive = true;
  
  // State
  let mapContainer;
  let map;
  let marker;
  let mapLibrary;
  let isMapLoaded = false;
  let isLoading = true;
  let errorLoading = false;
  let errorMessage = '';
  
  // Initialize map when component mounts
  onMount(async () => {
    // Initialize map if coordinates are valid
    if (isValidCoordinate(latitude) && isValidCoordinate(longitude)) {
      await loadMap();
    } else {
      errorLoading = true;
      errorMessage = $t('properties.invalid_coordinates');
    }
  });
  
  // Clean up map instance on component destroy
  onDestroy(() => {
    if (map) {
      map.remove();
      map = null;
    }
  });
  
  // Validate coordinate
  function isValidCoordinate(coord) {
    return coord !== null && 
           coord !== undefined && 
           !isNaN(parseFloat(coord)) && 
           isFinite(coord);
  }
  
  // Load the map library
  async function loadMap() {
    try {
      isLoading = true;
      
      // Check if leaflet is already loaded
      if (window.L) {
        mapLibrary = window.L;
        initializeMap();
        return;
      }
      
      // Dynamically load Leaflet CSS
      const linkElement = document.createElement('link');
      linkElement.rel = 'stylesheet';
      linkElement.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
      linkElement.integrity = 'sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=';
      linkElement.crossOrigin = '';
      document.head.appendChild(linkElement);
      
      // Load Leaflet JS
      const script = document.createElement('script');
      script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
      script.integrity = 'sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=';
      script.crossOrigin = '';
      
      // Initialize map after script loads
      script.onload = () => {
        mapLibrary = window.L;
        initializeMap();
      };
      
      script.onerror = (e) => {
        errorLoading = true;
        errorMessage = $t('properties.map_failed_load');
        isLoading = false;
        console.error('Failed to load Leaflet library', e);
      };
      
      document.body.appendChild(script);
    } catch (error) {
      errorLoading = true;
      errorMessage = $t('properties.map_error');
      isLoading = false;
      console.error('Error loading map:', error);
    }
  }
  
  // Initialize the map instance
  function initializeMap() {
    if (!mapContainer || !mapLibrary) return;
    
    try {
      // Create map instance with options
      map = mapLibrary.map(mapContainer, {
        center: [latitude, longitude],
        zoom: zoom,
        scrollWheelZoom: interactive,
        dragging: interactive,
        tap: interactive,
        zoomControl: interactive
      });
      
      // Add tile layer (OpenStreetMap)
      mapLibrary.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 19
      }).addTo(map);
      
      // Create custom icon for marker
      const customIcon = mapLibrary.icon({
        iconUrl: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(`
          <svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="${markerColor}" stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
            <circle cx="12" cy="10" r="3"></circle>
          </svg>
        `),
        iconSize: [36, 36],
        iconAnchor: [18, 36],
        popupAnchor: [0, -36]
      });
      
      // Add marker with popup
      marker = mapLibrary.marker([latitude, longitude], {
        icon: customIcon,
        title: title || address,
        alt: title || address,
        keyboard: true
      }).addTo(map);
      
      // Add popup with information
      if (title || address) {
        const popupContent = `
          <div class="map-popup">
            ${title ? `<strong>${title}</strong>` : ''}
            ${title && address ? '<br>' : ''}
            ${address ? address : ''}
          </div>
        `;
        marker.bindPopup(popupContent);
      }
      
      // Invalidate map size after rendering to ensure proper display
      setTimeout(() => {
        if (map) map.invalidateSize();
      }, 100);
      
      isMapLoaded = true;
      isLoading = false;
    } catch (error) {
      errorLoading = true;
      errorMessage = $t('properties.map_error');
      isLoading = false;
      console.error('Error initializing map:', error);
    }
  }
  
  // Update marker when coordinates change
  $: if (isMapLoaded && map && isValidCoordinate(latitude) && isValidCoordinate(longitude)) {
    map.setView([latitude, longitude], zoom);
    
    if (marker) {
      marker.setLatLng([latitude, longitude]);
    } else {
      marker = mapLibrary.marker([latitude, longitude], {
        title: title || address,
        alt: title || address
      }).addTo(map);
    }
  }
</script>

<div class="property-map h-full w-full relative rounded-lg overflow-hidden" style={`height: ${height};`}>
  {#if isLoading}
    <div class="absolute inset-0 flex items-center justify-center bg-cosmos-bg-light bg-opacity-50 z-10">
      <Spinner color="primary" size="lg" text={$t('general.loading_map')} />
    </div>
  {/if}
  
  {#if errorLoading}
    <div class="flex h-full items-center justify-center bg-cosmos-bg-light p-4">
      <div class="text-center max-w-md">
        <svg class="mx-auto h-12 w-12 text-cosmos-text-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <p class="mt-2 text-cosmos-text-muted">{errorMessage || $t('properties.map_error')}</p>
      </div>
    </div>
  {:else}
    <div bind:this={mapContainer} class="h-full w-full"></div>
  {/if}
</div>

<style>
  /* Additional styling for the map */
  :global(.leaflet-control-attribution) {
    font-size: 10px;
    background-color: rgba(255, 255, 255, 0.7) !important;
  }
  
  :global(.leaflet-popup-content) {
    font-size: 14px;
    padding: 4px;
  }
  
  :global(.map-popup) {
    padding: 4px;
    max-width: 200px;
  }
  
  :global(.leaflet-popup-content-wrapper) {
    border-radius: 8px;
  }
</style>