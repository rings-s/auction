<!-- src/lib/components/property/PropertyMap.svelte -->
<script>
    import { onMount, onDestroy } from 'svelte';
    import { t } from '$lib/i18n';
    
    // Props
    export let latitude;
    export let longitude;
    export let address = '';
    export let title = '';
    export let zoom = 15;
    export let markerColor = '#3B4CCA'; // primary color
    
    // State
    let mapContainer;
    let map;
    let marker;
    let mapLibrary;
    let isMapLoaded = false;
    let errorLoading = false;
    
    // Initialize map when component mounts
    onMount(async () => {
      // Initialize map if coordinates are valid
      if (isValidCoordinate(latitude) && isValidCoordinate(longitude)) {
        await loadMap();
      } else {
        errorLoading = true;
      }
    });
    
    // Clean up map instance on component destroy
    onDestroy(() => {
      if (map) {
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
        // Check if leaflet is already loaded
        if (window.L) {
          mapLibrary = window.L;
          initializeMap();
          return;
        }
        
        // Dynamically load Leaflet CSS
        const linkElement = document.createElement('link');
        linkElement.rel = 'stylesheet';
        linkElement.href = 'https://unpkg.com/leaflet@1.7.1/dist/leaflet.css';
        linkElement.integrity = 'sha512-xodZBNTC5n17Xt2atTPuE1HxjVMSvLVW9ocqUKLsCC5CXdbqCmblAshOMAS6/keqq/sMZMZ19scR4PsZChSR7A==';
        linkElement.crossOrigin = '';
        document.head.appendChild(linkElement);
        
        // Load Leaflet JS
        const script = document.createElement('script');
        script.src = 'https://unpkg.com/leaflet@1.7.1/dist/leaflet.js';
        script.integrity = 'sha512-XQoYMqMTK8LvdxXYG3nZ448hOEQiglfqkJs1NOQV44cWnUrBc8PkAOcXy20w0vlaXaVUearIOBhiXZ5V3ynxwA==';
        script.crossOrigin = '';
        
        // Initialize map after script loads
        script.onload = () => {
          mapLibrary = window.L;
          initializeMap();
        };
        
        script.onerror = () => {
          errorLoading = true;
          console.error('Failed to load Leaflet library');
        };
        
        document.body.appendChild(script);
      } catch (error) {
        errorLoading = true;
        console.error('Error loading map:', error);
      }
    }
    
    // Initialize the map instance
    function initializeMap() {
      if (!mapContainer || !mapLibrary) return;
      
      try {
        // Create map instance
        map = mapLibrary.map(mapContainer).setView(
          [latitude, longitude],
          zoom
        );
        
        // Add tile layer (OpenStreetMap)
        mapLibrary.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
          attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);
        
        // Add marker with popup
        marker = mapLibrary.marker([latitude, longitude], {
          title: title || address,
          alt: title || address
        }).addTo(map);
        
        // Add popup with information
        if (title || address) {
          const popupContent = `
            <div>
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
      } catch (error) {
        errorLoading = true;
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
  
  <div class="property-map h-full w-full">
    {#if errorLoading}
      <div class="flex h-full items-center justify-center bg-cosmos-bg-light">
        <div class="text-center">
          <svg class="mx-auto h-12 w-12 text-cosmos-text-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <p class="mt-2 text-cosmos-text-muted">{$t('properties.map_error')}</p>
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
    }
    
    :global(.leaflet-popup-content) {
      font-size: 14px;
      padding: 4px;
    }
  </style>