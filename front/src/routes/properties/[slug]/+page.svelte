<!-- src/routes/properties/[slug]/+page.svelte -->
<script>
  import { onMount, tick } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { t } from '$lib/i18n';
  import { getFeatureKey, getAmenityKey, getRoomTypeKey } from '$lib/i18n/mappings';
  import { user } from '$lib/stores/user';
  import { getPropertyBySlug } from '$lib/api/property';
  import { fade, fly, slide } from 'svelte/transition';
  import { quintOut, cubicOut } from 'svelte/easing';
  import TagSelector from '$lib/components/ui/TagSelector.svelte';
  import ContactForm from '$lib/components/messages/ContactForm.svelte';
  
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
  let activeMediaType = 'image'; // Default to image for gallery filter
  let touchStartX = 0;
  let touchEndX = 0;
  let isImagesLoading = true;
  let imagesLoaded = 0;
  let thumbnailsContainer;
  
  // Filter media by type
  $: filteredMedia = property?.media?.filter(item => item.media_type === activeMediaType) || [];
  $: images = property?.media?.filter(item => item.media_type === 'image') || [];
  $: videos = property?.media?.filter(item => item.media_type === 'video') || [];
  $: documents = property?.media?.filter(item => item.media_type === 'document') || [];
  $: otherFiles = property?.media?.filter(item => item.media_type === 'other') || [];
  
  // Get main image
  $: mainImage = property?.main_image || (images.length > 0 ? images.find(img => img.is_primary) || images[0] : null);
  
  // Tabs management
  let activeTab = 'overview';
  const tabs = [
    { id: 'overview', label: $t('property.tab.overview'), icon: 'home' },
    { id: 'rooms', label: $t('property.tab.rooms'), icon: 'layout' },
    { id: 'location', label: $t('property.tab.location'), icon: 'map-pin' },
    { id: 'gallery', label: $t('property.tab.gallery'), icon: 'image' }
  ];
  
  // Gallery tabs
  const mediaTabs = [
    { id: 'image', label: $t('property.galleryTabs.photos') },
    { id: 'video', label: $t('property.galleryTabs.videos') },
    { id: 'document', label: $t('property.galleryTabs.documents') },
    { id: 'other', label: $t('property.galleryTabs.otherFiles') }
  ];
  
  // Sticky header control
  let scrollY = 0;
  let headerHeight = 0;
  let headerElement;
  let isHeaderSticky = false;
  $: isHeaderSticky = scrollY > headerHeight;
  
  // Get slug from URL and ensure it's properly decoded
  $: slug = decodeURIComponent($page.params.slug);
  
  // Check edit permissions
  $: canEdit = $user && (
    $user.is_staff || 
    ($user.role === 'appraiser') || 
    (property?.owner?.id === $user.id)
  );
  
  // Track image loading progress
  function handleImageLoad() {
    imagesLoaded++;
    console.log(`Image loaded: ${imagesLoaded} of ${images.length}`);
    // Force loading to complete if at least one image is loaded
    // This ensures we show something even if not all images load
    if (imagesLoaded >= 1) {
      isImagesLoading = false;
    }
  }

  // Load property data
  async function loadProperty() {
    try {
      loading = true;
      error = null;
      imagesLoaded = 0;
      isImagesLoading = true;
      
      const response = await getPropertyBySlug(slug);
      property = response;
      
      // Initialize after data loads
      await tick();
      if (headerElement) {
        headerHeight = headerElement.offsetHeight;
      }
      
      // Initialize map if location tab is active
      if (activeTab === 'location' && property?.location?.latitude && property?.location?.longitude) {
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
    
    // Convert room type to a key format (lowercase, no spaces)
    const normalizedType = roomType.toLowerCase().replace(/\s+/g, '');
    
    // Try direct mapping first using the centralized room type map
    const mappedKey = getRoomTypeKey(roomType);
    if (mappedKey) {
      const translationKey = `property.roomTypes.${mappedKey}`;
      const translation = $t(translationKey);
      if (translation !== translationKey) {
        return translation;
      }
    }
    
    // Try with normalized key
    const translationKey = `property.roomTypes.${normalizedType}`;
    const translation = $t(translationKey);
    if (translation !== translationKey) {
      return translation;
    }
    
    // Return original if no translation found
    return roomType;
  }
  
  // Translate feature or amenity
  function translateFeatureOrAmenity(item, type) {
    if (!item) return '';
    
    // Determine the correct translation key prefix based on type
    let translationPrefix = 'property.';
    let itemsKey = '';
    
    if (type === 'feature') {
      itemsKey = 'featureItems';
    } else if (type === 'amenity') {
      itemsKey = 'amenityItems';
    } else if (type === 'roomFeature') {
      itemsKey = 'roomFeatureItems';
    } else {
      return item; // Unknown type
    }
    
    // We now use the centralized feature map from i18n.js
    
    // Check if we have a direct mapping using the centralized feature map
    const mappedKey = getFeatureKey(item);
    if (mappedKey) {
      const mappedTranslationKey = `${translationPrefix}${itemsKey}.${mappedKey}`;
      const mappedTranslation = $t(mappedTranslationKey);
      if (mappedTranslation !== mappedTranslationKey) {
        return mappedTranslation;
      }
    }
    
    // Try to find a match in the translation keys using normalized item
    const normalizedItem = item.toLowerCase().replace(/\s+/g, '');
    const translationKey = `${translationPrefix}${itemsKey}.${normalizedItem}`;
    const translation = $t(translationKey);
    
    // If the translation key returns the key itself, it wasn't found
    if (translation === translationKey) {
      // Try some common variations
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
      
      // Just return the original item if no direct translation is found
      return item;
    }
    
    return translation;
  }
  
  // Switch tabs with smooth transitions
  async function setActiveTab(tabId) {
    if (activeTab === tabId) return;
    activeTab = tabId;
    
    // Initialize map if switching to location tab
    if (tabId === 'location' && property?.location?.latitude && property?.location?.longitude) {
      await tick();
      initializeMap();
    }
    
    // Scroll to tab content on mobile
    if (window.innerWidth < 768) {
      const tabContent = document.getElementById(`tab-${tabId}`);
      if (tabContent) {
        const offset = isHeaderSticky ? 60 : 0;
        window.scrollTo({
          top: tabContent.offsetTop - offset,
          behavior: 'smooth'
        });
      }
    }
  }
  
  // Switch media type for gallery
  function setActiveMediaType(mediaType) {
    activeMediaType = mediaType;
    activeImageIndex = 0; // Reset active index when changing media types
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
    
    // Don't create map if coordinates are missing
    if (!lat || !lng) return;
    
    // Initialize the map
    map = L.map(mapElement, {
      scrollWheelZoom: false,
      dragging: !L.Browser.mobile
    }).setView([lat, lng], 15);
    
    // Add modern map tiles
    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
      subdomains: 'abcd',
      maxZoom: 19
    }).addTo(map);
    
    // Custom styled marker
    const customIcon = L.divIcon({
      className: 'custom-map-marker',
      html: `<div class="marker-pin"></div>
             <span class="marker-icon">
               <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="14" height="14">
                 <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
               </svg>
             </span>
             ${property.location.house_number ? `<div class="house-number">${property.location.house_number}</div>` : ''}
             `,
      iconSize: [30, 42],
      iconAnchor: [15, 42]
    });
    
    marker = L.marker([lat, lng], { icon: customIcon }).addTo(map)
      .bindPopup(`
        <div class="map-popup">
          <h3 class="text-base font-semibold">${property.title}</h3>
          <p class="text-sm mt-1">${property.location.address}</p>
          <p class="text-primary-600 font-bold mt-2">${formatCurrency(property.market_value)}</p>
        </div>
      `, { className: 'custom-popup' });
    
    // Add radius circle
    L.circle([lat, lng], {
      radius: 500,
      fillColor: '#3b82f6',
      fillOpacity: 0.1,
      color: '#3b82f6',
      weight: 1
    }).addTo(map);
    
    // Enable map interaction when clicked
    map.on('click', function() {
      if (!map.scrollWheelZoom.enabled()) {
        map.scrollWheelZoom.enable();
        L.DomUtil.addClass(mapElement, 'active-map');
      }
    });
    
    // Disable interaction when clicking outside
    document.addEventListener('click', function(e) {
      if (mapElement && !mapElement.contains(e.target)) {
        map.scrollWheelZoom.disable();
        L.DomUtil.removeClass(mapElement, 'active-map');
      }
    });
    
    mapInitialized = true;
    
    // Fix map rendering
    setTimeout(() => {
      if (map) map.invalidateSize();
    }, 400);
  }
  
  // Gallery navigation functions
  function showMedia(index) {
    activeImageIndex = index;
    
    // Scroll thumbnails to keep active thumbnail visible
    if (thumbnailsContainer && showFullScreenGallery) {
      const thumbnailWidth = 72; // 16px width + 2px border*2 + 4px margin*2
      thumbnailsContainer.scrollTo({
        left: index * thumbnailWidth - thumbnailsContainer.clientWidth / 2 + thumbnailWidth / 2,
        behavior: 'smooth'
      });
    }
  }
  
  function toggleGallery(index = 0) {
    if (typeof index === 'number') {
      activeImageIndex = index;
    }
    showFullScreenGallery = !showFullScreenGallery;
    document.body.style.overflow = showFullScreenGallery ? 'hidden' : '';
  }
  
  function nextMedia() {
    if (filteredMedia.length) {
      activeImageIndex = (activeImageIndex + 1) % filteredMedia.length;
      showMedia(activeImageIndex);
    }
  }
  
  function prevMedia() {
    if (filteredMedia.length) {
      activeImageIndex = (activeImageIndex - 1 + filteredMedia.length) % filteredMedia.length;
      showMedia(activeImageIndex);
    }
  }
  
  // Touch events for swipe on gallery
  function handleTouchStart(e) {
    touchStartX = e.touches[0].clientX;
  }
  
  function handleTouchEnd(e) {
    touchEndX = e.changedTouches[0].clientX;
    if (touchStartX - touchEndX > 50) {
      // Swipe left
      nextMedia();
    } else if (touchEndX - touchStartX > 50) {
      // Swipe right
      prevMedia();
    }
  }
  
  // Contact property owner
  function contactOwner() {
    if (!$user) {
      goto('/login');
      return;
    }
    
    // Implement contact functionality here
  }
  
  // Render media item
  function renderMediaItem(item) {
    if (!item) return null;
    
    switch (item.media_type) {
      case 'image':
        return `<img src="${item.url}" alt="${item.name || 'Property image'}" class="mx-auto max-h-[80vh] object-contain" />`;
      case 'video':
        return `<video controls class="mx-auto max-h-[80vh]">
                  <source src="${item.url}" type="video/mp4">
                  Your browser does not support the video tag.
                </video>`;
      case 'document':
        if (item.url.endsWith('.pdf')) {
          return `<div class="text-center text-white">
                    <svg class="mx-auto h-20 w-20 text-gray-200" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6zm-1 5V3.5L18.5 9H13v-2z"/>
                    </svg>
                    <p class="mt-4 text-lg">${$t('property.pdfDocument')}: ${item.name}</p>
                    <a href="${item.url}" download class="mt-2 inline-block px-4 py-2 bg-white text-gray-900 rounded-md hover:bg-gray-200 transition-colors">
                      ${$t('property.downloadPdf')}
                    </a>
                  </div>`;
        } else {
          return `<div class="text-center text-white">
                    <svg class="mx-auto h-20 w-20 text-gray-200" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6zm-1 5V3.5L18.5 9H13v-2z"/>
                    </svg>
                    <p class="mt-4 text-lg">${$t('property.document')}: ${item.name}</p>
                    <a href="${item.url}" download class="mt-2 inline-block px-4 py-2 bg-white text-gray-900 rounded-md hover:bg-gray-200 transition-colors">
                      ${$t('property.downloadDocument')}
                    </a>
                  </div>`;
        }
      default:
        return `<div class="text-center text-white">
                  <svg class="mx-auto h-20 w-20 text-gray-200" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6zm-1 5V3.5L18.5 9H13v-2z"/>
                  </svg>
                  <p class="mt-4 text-lg">${$t('property.file')}: ${item.name}</p>
                  <a href="${item.url}" download class="mt-2 inline-block px-4 py-2 bg-white text-gray-900 rounded-md hover:bg-gray-200 transition-colors">
                    ${$t('property.downloadFile')}
                  </a>
                </div>`;
    }
  }
  
  // Get media thumbnail
  function getMediaThumbnail(item) {
    if (!item) return '';
    
    switch (item.media_type) {
      case 'image':
        return item.url;
      case 'video':
        return '/images/video-thumbnail.jpg'; // Replace with actual thumbnail or placeholder
      case 'document':
        if (item.url.endsWith('.pdf')) {
          return '/images/pdf-thumbnail.jpg'; // Replace with actual PDF icon
        } else {
          return '/images/document-thumbnail.jpg'; // Replace with actual document icon
        }
      default:
        return '/images/file-thumbnail.jpg'; // Replace with actual file icon
    }
  }
  
  // Get media icon based on type
  function getMediaTypeIcon(type) {
    switch (type) {
      case 'image':
        return `<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>`;
      case 'video':
        return `<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8v6a1 1 0 01-1 1v6a1 1 0 01-1-1v-6a1 1 0 00-1-1H9a1 1 0 00-1 1v6a1 1 0 001 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1V7a1 1 0 011-1h5m0 0V5a2 2 0 012-2h2a2 2 0 012 2v2m-6 3h6m-6 2h6a2 2 0 012 2v3m0 0h-9"></path></svg>`;
      case 'document':
        return `<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0112.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"></path></svg>`;
      default:
        return `<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>`;
    }
  }
  
  // Keyboard shortcuts for gallery
  function handleKeydown(event) {
    if (showFullScreenGallery) {
      if (event.key === 'ArrowRight' || event.key === 'ArrowDown') {
        nextMedia();
      } else if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') {
        prevMedia();
      } else if (event.key === 'Escape') {
        showFullScreenGallery = false;
        document.body.style.overflow = '';
      }
    }
  }
  
  // Get icon SVG by name
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
      case 'gavel':
        return `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h9a2 2 0 002 2v1.41a2 2 0 01-2 2H5a2 2 0 00-2-2V7a2 2 0 00-2-2h9m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path></svg>`;
      default:
        return '';
    }
  }
  
  // Load property on mount and when slug changes
  $: if (slug) {
    loadProperty();
  }
  
  onMount(() => {
    loadProperty();
    
    // Setup keyboard listener
    window.addEventListener('keydown', handleKeydown);
    
    // Cleanup on unmount
    return () => {
      window.removeEventListener('keydown', handleKeydown);
      if (map) {
        map.remove();
        mapInitialized = false;
      }
      document.body.style.overflow = '';
    };
  });
</script>

<svelte:window bind:scrollY={scrollY} />

<svelte:head>
  <title>{property?.title || $t('property.loading')} | Real Estate Platform</title>
  <meta name="description" content={property?.meta_description || property?.description?.substr(0, 160) || ''} />
</svelte:head>

<div class="min-h-screen pb-16">
  <!-- Back Button -->
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-6">
    <a 
      href="/properties" 
      class="inline-flex items-center text-sm font-medium text-primary-600 dark:text-primary-400 hover:text-primary-500 dark:hover:text-primary-300 transition-colors"
    >
      <svg class="mr-2 w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
      </svg>
      {$t('properties.backToProperties')}
    </a>
  </div>

  <!-- Main Content -->
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
    <!-- Loading State -->
    {#if loading && !property}
      <div class="flex flex-col justify-center items-center py-20">
        <div class="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-primary-500"></div>
        <p class="mt-4 text-gray-500 dark:text-gray-400">{$t('common.loading')}</p>
      </div>
    
    <!-- Error State -->
    {:else if error}
      <div class="bg-red-50 dark:bg-red-900/20 p-6 rounded-lg text-red-800 dark:text-red-200 max-w-3xl mx-auto my-12">
        <h2 class="text-xl font-semibold mb-2 flex items-center">
          <svg class="w-6 h-6 mr-2 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          {$t('error.title')}
        </h2>
        <p>{error}</p>
        <div class="mt-4 flex space-x-4">
          <button
            class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-all"
            on:click={loadProperty}
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            {$t('auction.tryAgain')}
          </button>
          <a 
            href="/properties" 
            class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-gray-200 dark:border-gray-600 dark:hover:bg-gray-600 transition-colors"
          >
            {$t('properties.backToProperties')}
          </a>
        </div>
      </div>
    
    <!-- Property Details -->
    {:else if property}
      <!-- Property Header with sticky capability -->
      <div 
        bind:this={headerElement}
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
                on:click={contactOwner}
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
              on:click={() => setActiveTab(tab.id)}
              aria-selected={activeTab === tab.id}
              role="tab"
            >
              {@html getIcon(tab.icon)}
              <span class="ml-2">{tab.label}</span>
            </button>
          {/each}
        </div>
      </div>
      
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
            <!-- Main Image and Gallery Preview - REFACTORED -->
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
                      on:load={handleImageLoad}
                      on:error={(e) => { 
                        console.log('Image failed to load, using placeholder');
                        e.currentTarget.src = '/images/placeholder-property.jpg'; 
                        // Mark as loaded even if we're using the placeholder
                        isImagesLoading = false;
                      }}
                    />
                  
                  <!-- Gradient overlay at bottom -->
                  <div class="absolute inset-x-0 bottom-0 h-24 bg-gradient-to-t from-black/60 to-transparent pointer-events-none"></div>
                  
                  <!-- Gallery Overlay Button -->
                  <button 
                    class="absolute bottom-4 right-4 bg-white/90 dark:bg-gray-800/90 rounded-full p-2 shadow-lg hover:bg-white dark:hover:bg-gray-700 transition-colors z-10"
                    on:click={toggleGallery}
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
              
              <!-- Thumbnail Preview Gallery - NEW -->
              {#if images.length > 1}
                <div class="mt-4 relative">
                  <div class="overflow-x-auto scrollbar-thin py-2">
                    <div class="flex gap-2">
                      {#each images.slice(0, Math.min(6, images.length)) as image, idx}
                        <button
                          class={`flex-shrink-0 h-16 w-24 rounded-md overflow-hidden border-2 transition-all ${idx === activeImageIndex ? 'border-primary-500 dark:border-primary-400' : 'border-transparent'}`}
                          on:click={() => { activeImageIndex = idx; toggleGallery(); }}
                        >
                          <img src={image.url} alt={image.name || `Property image ${idx+1}`} class="h-full w-full object-cover" loading="lazy" />
                        </button>
                      {/each}
                      
                      {#if images.length > 6}
                        <button
                          class="flex-shrink-0 h-16 w-24 rounded-md overflow-hidden border-2 border-transparent bg-gray-100 dark:bg-gray-750 flex items-center justify-center group"
                          on:click={toggleGallery}
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
              <!-- Property Details Card - REFACTORED -->
              <div class="bg-gray-50 dark:bg-gray-750 rounded-xl shadow-md overflow-hidden border border-gray-100 dark:border-gray-700">
                <div class="p-5">
                  <h2 class="text-lg font-bold text-gray-900 dark:text-white mb-4 flex items-center">
                    <svg class="w-5 h-5 mr-2 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    {$t('property.propertyDetails')}
                  </h2>
                  
                  <!-- Details Grid - REFACTORED with nicer cards -->
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
                    console.log('Message sent successfully:', e.detail);
                  }}
                  on:error={(e) => {
                    // Handle error
                    console.error('Failed to send message:', e.detail);
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
          class="p-8" 
          style="display: {activeTab === 'location' ? 'block' : 'none'}"
          transition:fade={{ duration: 200 }}
        >
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
        
        <!-- Gallery Tab - REFACTORED -->
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
          
          <!-- Media Type Tabs - REFACTORED -->
          <div class="flex overflow-x-auto mb-6 bg-gray-50 dark:bg-gray-750 rounded-lg p-1">
            {#each mediaTabs as tab}
              <button 
                class={`py-2 px-4 font-medium text-sm whitespace-nowrap rounded-md flex items-center
                  ${activeMediaType === tab.id 
                    ? 'bg-white dark:bg-gray-800 text-primary-600 dark:text-primary-400 shadow-sm' 
                    : 'bg-transparent text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-200'
                  } transition-colors duration-200 mx-1`}
                on:click={() => setActiveMediaType(tab.id)}
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
                  on:click={() => { activeImageIndex = index; toggleGallery(); }}
                  on:keydown={(e) => { if (e.key === 'Enter' || e.key === ' ') { activeImageIndex = index; toggleGallery(); } }}
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
    {/if}
  </div>
</div>

<!-- Full Screen Gallery Modal - REFACTORED -->
{#if showFullScreenGallery && filteredMedia.length > 0}
  <div 
    class="fixed inset-0 bg-black bg-opacity-95 z-50 flex flex-col items-center justify-center p-4 animate-fadeIn"
    on:click={toggleGallery}
    on:keydown={(e) => { if (e.key === 'Escape') toggleGallery(); }}
    on:touchstart={handleTouchStart}
    on:touchend={handleTouchEnd}
    role="dialog"
    tabindex="0"
    aria-modal="true"
    aria-label={$t('property.viewImage')}
  >
    <!-- Header with title and close button -->
    <div class="w-full max-w-6xl flex items-center justify-between mb-4 text-white">
      <h3 class="text-xl font-medium">
        {filteredMedia[activeImageIndex]?.name || `${property.title} - ${activeMediaType} ${activeImageIndex + 1}/${filteredMedia.length}`}
      </h3>
      
      <!-- Close Button - Improved visibility -->
      <button 
        class="rounded-full bg-red-600 hover:bg-red-700 p-3 focus:outline-none transition-colors shadow-lg"
        on:click={(e) => { e.stopPropagation(); toggleGallery(); }}
        aria-label={$t('property.closeGallery')}
      >
        <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
    
    <div class="relative w-full max-w-6xl mx-auto flex-grow flex items-center justify-center">
      <!-- Main Media Item - Now with Fade transition -->
      <div class="transition-opacity duration-300 w-full h-full flex items-center justify-center" in:fade={{ duration: 200 }}>
        <div 
          role="button"
          tabindex="0"
          class="w-full h-full flex items-center justify-center"
          on:click={(e) => e.stopPropagation()}
          on:keydown={(e) => { if (e.key === 'Enter' || e.key === ' ') e.stopPropagation(); }}
          aria-label={filteredMedia[activeImageIndex]?.name || t('property.mediaItem')}
        >
          {@html renderMediaItem(filteredMedia[activeImageIndex])}
        </div>
      </div>
      
      <!-- Navigation Controls - Enhanced with better UI -->
      {#if filteredMedia.length > 1}
        <button 
          class="absolute left-4 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-50 rounded-full p-3 text-white hover:bg-opacity-80 focus:outline-none focus:ring-2 focus:ring-white focus:ring-opacity-50 transition-all backdrop-blur-sm"
          on:click={(e) => { e.stopPropagation(); prevMedia(); }}
          aria-label="Previous item"
        >
          <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7m0 0l-7 7m-7 7h18" />
          </svg>
        </button>
        <button 
          class="absolute right-4 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-50 rounded-full p-3 text-white hover:bg-opacity-80 focus:outline-none focus:ring-2 focus:ring-white focus:ring-opacity-50 transition-all backdrop-blur-sm"
          on:click={(e) => { e.stopPropagation(); nextMedia(); }}
          aria-label="Next item"
        >
          <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </button>
      {/if}
    </div>
    
    <!-- Media Info and Counter -->
    <div class="w-full max-w-6xl text-center mt-4 mb-4 text-white flex items-center justify-center space-x-4">
      <!-- Counter info -->
      <div class="px-3 py-1 bg-black bg-opacity-50 rounded-md text-sm backdrop-blur-sm">
        {activeImageIndex + 1} / {filteredMedia.length}
      </div>
      
      <!-- File size if available -->
      {#if filteredMedia[activeImageIndex]?.file_size}
        <div class="px-3 py-1 bg-black bg-opacity-50 rounded-md text-sm backdrop-blur-sm">
          {formatFileSize(filteredMedia[activeImageIndex].file_size)}
        </div>
      {/if}
      
      <!-- Media type badge -->
      <div class="px-3 py-1 bg-black bg-opacity-50 rounded-md text-sm flex items-center backdrop-blur-sm">
        <span class="capitalize">{activeMediaType}</span>
      </div>
    </div>
    
    <!-- Thumbnails for quick navigation - REFACTORED -->
    {#if filteredMedia.length > 1}
      <div class="w-full max-w-6xl mt-2">
        <div 
          class="flex justify-center overflow-x-auto pb-2 px-2 scrollbar-thin scrollbar-thumb-gray-600 scrollbar-track-transparent"
          bind:this={thumbnailsContainer}
        >
          {#each filteredMedia as item, index}
            <button
              class={`relative mx-1 rounded-lg overflow-hidden flex-shrink-0 h-16 w-16 border-2 transition-all ${activeImageIndex === index ? 'border-primary-500 scale-110 z-10' : 'border-transparent opacity-60 hover:opacity-100'}`}
              on:click={() => { activeImageIndex = index; toggleGallery(); }}
              aria-label={`View media ${index + 1}`}
            >
              <div class="h-full w-full bg-gray-800 flex items-center justify-center overflow-hidden">
                {#if item.media_type === 'image'}
                  <img src={item.url} alt={item.name} class="w-full h-full object-cover" />
                {:else if item.media_type === 'video'}
                  <svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" />
                  </svg>
                {:else if item.media_type === 'document'}
                  <svg class="w-6 h-6 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M4 4a2 2 0 00-2 2v8a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2H4zm2 3a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" />
                  </svg>
                {:else}
                  <svg class="w-6 h-6 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M4 4a2 2 0 00-2 2v8a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2H4zm12 12H4V6h12v10z" clip-rule="evenodd" />
                  </svg>
                {/if}
              </div>
              
              <!-- Index number overlay -->
              <span class="absolute bottom-0 right-0 bg-black bg-opacity-70 text-white text-xs px-1 rounded-tl-md">
                {index + 1}
              </span>
            </button>
          {/each}
        </div>
      </div>
    {/if}
    
    <!-- Keyboard shortcuts guide -->
    <div class="text-gray-400 text-xs mt-4 text-center">
      <span class="hidden sm:inline">Use arrow keys to navigate</span>
      <span class="sm:hidden">Swipe to navigate</span>
      | Press ESC to close
    </div>
  </div>
{/if}

<style>
  /* Sticky header styling */
  .sticky-header {
    position: sticky;
    top: 0;
    z-index: 20;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  }
  
  /* Hide scrollbar for tab navigation */
  .scrollbar-hide {
    -ms-overflow-style: none;  /* IE and Edge */
    scrollbar-width: none;  /* Firefox */
  }
  
  .scrollbar-hide::-webkit-scrollbar {
    display: none; /* Chrome, Safari, Opera */
  }
  
  /* Custom scrollbar styling */
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
  
  /* Tooltip styling */
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
  
  /* Map styling */
  .active-map {
    border: 2px solid #3b82f6;
  }
  
  /* Ensure map container stays in back layer */
  :global(.leaflet-container) {
    z-index: 1 !important;
  }
  
  /* Custom map marker */
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
  
  /* Animations */
  .animate-fadeIn {
    animation: fadeIn 0.3s ease-in-out;
  }
  
  @keyframes fadeIn {
    from {
      opacity: 0;
    }
    to {
      opacity: 1;
    }
  }
  

</style>