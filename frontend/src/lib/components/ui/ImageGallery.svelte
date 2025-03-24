<!-- src/lib/components/ui/ImageGallery.svelte -->
<script>
    /**
     * ImageGallery Component
     * A streamlined, responsive image gallery with thumbnails and lightbox.
     */
    import { onMount, onDestroy, createEventDispatcher } from 'svelte';
    import { fade, fly, scale } from 'svelte/transition';
    import { quintOut } from 'svelte/easing';
    
    const dispatch = createEventDispatcher();
    
    // Props
    export let images = []; // Array of image URLs or objects with src, alt, caption
    export let aspectRatio = '16/9'; // Image aspect ratio: 1/1, 4/3, 16/9, 21/9
    export let showThumbnails = true; // Show thumbnails
    export let thumbnailPosition = 'bottom'; // bottom, left, right
    export let enableLightbox = true; // Enable lightbox view
    export let enableZoom = false; // Enable image zoom in lightbox
    export let autoplay = false; // Auto-rotate images
    export let autoplaySpeed = 5000; // Autoplay speed in ms
    export let showArrows = true; // Show navigation arrows
    export let showDots = false; // Show pagination dots
    export let showCounter = true; // Show image counter in lightbox
    export let infinite = true; // Infinite scrolling
    export let lazyLoad = true; // Lazy load images
    export let gap = 'gap-2'; // Gap between thumbnails
    export let maxHeight = undefined; // Max height for the gallery
    export let rounded = 'rounded-lg'; // Rounded corners
    
    // Local state
    let activeIndex = 0;
    let lightboxActive = false;
    let loadedImages = new Set();
    let imageErrors = new Set();
    let currentZoom = 1;
    let dragStartX = 0;
    let dragStartY = 0;
    let isSwiping = false;
    let swipeThreshold = 50;
    let galleryElement;
    let timer;
    
    // Normalize images array to ensure objects with src, alt, caption
    $: normalizedImages = images.map(img => {
      if (typeof img === 'string') {
        return { src: img, alt: '', caption: '' };
      } else if (typeof img === 'object') {
        return {
          src: img.src || img.url || img,
          alt: img.alt || '',
          caption: img.caption || ''
        };
      }
      return img;
    });
    
    // Handle autoplay
    $: if (autoplay && normalizedImages.length > 1) {
      startAutoplay();
    } else {
      stopAutoplay();
    }
    
    function startAutoplay() {
      stopAutoplay();
      timer = setInterval(() => {
        if (!lightboxActive) {
          goToNext();
        }
      }, autoplaySpeed);
    }
    
    function stopAutoplay() {
      if (timer) {
        clearInterval(timer);
        timer = null;
      }
    }
    
    // Navigation functions
    function goToNext() {
      if (normalizedImages.length <= 1) return;
      
      activeIndex = infinite
        ? (activeIndex + 1) % normalizedImages.length
        : Math.min(activeIndex + 1, normalizedImages.length - 1);
        
      dispatch('change', { index: activeIndex, image: normalizedImages[activeIndex] });
      
      // Preload next image
      if (lazyLoad && activeIndex + 1 < normalizedImages.length) {
        preloadImage(activeIndex + 1);
      }
    }
    
    function goToPrev() {
      if (normalizedImages.length <= 1) return;
      
      activeIndex = infinite
        ? (activeIndex - 1 + normalizedImages.length) % normalizedImages.length
        : Math.max(activeIndex - 1, 0);
        
      dispatch('change', { index: activeIndex, image: normalizedImages[activeIndex] });
      
      // Preload previous image
      if (lazyLoad && activeIndex - 1 >= 0) {
        preloadImage(activeIndex - 1);
      }
    }
    
    function goToIndex(index) {
      if (index === activeIndex || index < 0 || index >= normalizedImages.length) return;
      
      activeIndex = index;
      dispatch('change', { index: activeIndex, image: normalizedImages[activeIndex] });
      
      // Preload adjacent images
      if (lazyLoad) {
        preloadImage(index);
        if (index + 1 < normalizedImages.length) preloadImage(index + 1);
        if (index - 1 >= 0) preloadImage(index - 1);
      }
    }
    
    function preloadImage(index) {
      if (index < 0 || index >= normalizedImages.length || loadedImages.has(index)) return;
      
      const img = new Image();
      img.src = normalizedImages[index].src;
      img.onload = () => {
        loadedImages.add(index);
        loadedImages = loadedImages; // Trigger reactivity
      };
      img.onerror = () => {
        imageErrors.add(index);
        imageErrors = imageErrors; // Trigger reactivity
      };
    }
    
    // Lightbox functions
    function toggleLightbox() {
      if (!enableLightbox) return;
      
      lightboxActive = !lightboxActive;
      
      if (lightboxActive) {
        stopAutoplay();
        document.body.style.overflow = 'hidden';
        currentZoom = 1;
      } else {
        if (autoplay) startAutoplay();
        document.body.style.overflow = '';
      }
      
      dispatch(lightboxActive ? 'lightboxOpen' : 'lightboxClose');
    }
    
    function resetZoom() {
      currentZoom = 1;
    }
    
    function zoomIn() {
      currentZoom = Math.min(currentZoom + 0.25, 3);
    }
    
    function zoomOut() {
      currentZoom = Math.max(currentZoom - 0.25, 0.5);
    }
    
    // Touch/swipe handling
    function handleTouchStart(e) {
      if (normalizedImages.length <= 1) return;
      
      dragStartX = e.touches[0].clientX;
      dragStartY = e.touches[0].clientY;
      isSwiping = true;
    }
    
    function handleTouchMove(e) {
      if (!isSwiping) return;
      
      // Prevent page scrolling during swipe
      e.preventDefault();
    }
    
    function handleTouchEnd(e) {
      if (!isSwiping) return;
      
      const dragEndX = e.changedTouches[0].clientX;
      const dragDistance = dragStartX - dragEndX;
      
      if (Math.abs(dragDistance) > swipeThreshold) {
        if (dragDistance > 0) {
          goToNext();
        } else {
          goToPrev();
        }
      }
      
      isSwiping = false;
    }
    
    // Keyboard navigation
    function handleKeydown(e) {
      if (lightboxActive) {
        switch (e.key) {
          case 'ArrowLeft':
            goToPrev();
            e.preventDefault();
            break;
          case 'ArrowRight':
            goToNext();
            e.preventDefault();
            break;
          case 'Escape':
            toggleLightbox();
            e.preventDefault();
            break;
          case '+':
            if (enableZoom) zoomIn();
            e.preventDefault();
            break;
          case '-':
            if (enableZoom) zoomOut();
            e.preventDefault();
            break;
          case '0':
            if (enableZoom) resetZoom();
            e.preventDefault();
            break;
        }
      }
    }
    
    // Handle image load events
    function handleImageLoad(index) {
      loadedImages.add(index);
      loadedImages = loadedImages; // Trigger reactivity
    }
    
    function handleImageError(index) {
      imageErrors.add(index);
      imageErrors = imageErrors; // Trigger reactivity
    }
    
    onMount(() => {
      // Preload visible and adjacent images
      preloadImage(activeIndex);
      if (activeIndex + 1 < normalizedImages.length) preloadImage(activeIndex + 1);
      if (activeIndex - 1 >= 0) preloadImage(activeIndex - 1);
      
      // Add keyboard listener
      window.addEventListener('keydown', handleKeydown);
    });
    
    onDestroy(() => {
      stopAutoplay();
      window.removeEventListener('keydown', handleKeydown);
      
      // Ensure body overflow is restored
      if (lightboxActive) {
        document.body.style.overflow = '';
      }
    });
    
    // Thumbnail container styles based on position
    $: thumbnailContainerClasses = thumbnailPosition === 'bottom' ? 'flex-col' : 
                                 thumbnailPosition === 'left' ? 'flex-row-reverse' : 
                                 thumbnailPosition === 'right' ? 'flex-row' : 'flex-col';
    
    $: thumbnailsClasses = thumbnailPosition === 'bottom' ? 'flex-row mt-2 w-full' : 
                         thumbnailPosition === 'left' ? 'flex-col mr-2 h-full' : 
                         thumbnailPosition === 'right' ? 'flex-col ml-2 h-full' : 'flex-row mt-2 w-full';
    
    $: thumbnailSize = thumbnailPosition === 'bottom' ? 'w-16 flex-shrink-0' : 
                      (thumbnailPosition === 'left' || thumbnailPosition === 'right') ? 'h-16 w-full flex-shrink-0' : 'w-16 flex-shrink-0';
  </script>
  
  <div 
    class="image-gallery w-full {maxHeight ? 'max-h-['+maxHeight+']' : ''}" 
    bind:this={galleryElement}
    {...$$restProps}
  >
    <div class="flex {thumbnailContainerClasses}">
      <!-- Main image container -->
      <div class="relative flex-grow overflow-hidden {rounded}" style="aspect-ratio: {aspectRatio};">
        {#if normalizedImages.length === 0}
          <!-- Empty state -->
          <div class="absolute inset-0 flex items-center justify-center bg-neutral-100 dark:bg-neutral-800">
            <div class="text-center text-neutral-500 dark:text-neutral-400">
              <svg xmlns="http://www.w3.org/2000/svg" class="mx-auto h-12 w-12 mb-2 opacity-50" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                <circle cx="8.5" cy="8.5" r="1.5" />
                <path d="m21 15-5-5L5 21" />
              </svg>
              <p class="mt-1">No images to display</p>
            </div>
          </div>
        {:else}
          <!-- Image display -->
          <div class="absolute inset-0">
            {#each normalizedImages as image, index}
              {#if index === activeIndex}
                <div 
                  class="absolute inset-0 transition-opacity duration-300 flex items-center justify-center"
                  class:opacity-100={index === activeIndex}
                  class:opacity-0={index !== activeIndex}
                >
                  <!-- Image with loading and error states -->
                  {#if lazyLoad ? loadedImages.has(index) || index === activeIndex : true}
                    <img
                      src={image.src}
                      alt={image.alt}
                      class="h-full w-full object-contain"
                      on:load={() => handleImageLoad(index)}
                      on:error={() => handleImageError(index)}
                      on:click={enableLightbox ? toggleLightbox : undefined}
                      class:cursor-zoom-in={enableLightbox}
                    />
                  {/if}
                  
                  <!-- Loading indicator -->
                  {#if lazyLoad && !loadedImages.has(index) && !imageErrors.has(index)}
                    <div class="absolute inset-0 flex items-center justify-center bg-neutral-100 dark:bg-neutral-800">
                      <div class="h-8 w-8 animate-spin rounded-full border-4 border-neutral-300 border-t-primary dark:border-neutral-600 dark:border-t-primary"></div>
                    </div>
                  {/if}
                  
                  <!-- Error state -->
                  {#if imageErrors.has(index)}
                    <div class="absolute inset-0 flex flex-col items-center justify-center bg-neutral-100 dark:bg-neutral-800">
                      <svg xmlns="http://www.w3.org/2000/svg" class="mb-2 h-12 w-12 text-neutral-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
                        <line x1="12" y1="9" x2="12" y2="13" />
                        <line x1="12" y1="17" x2="12.01" y2="17" />
                      </svg>
                      <p class="text-sm text-neutral-500 dark:text-neutral-400">Failed to load image</p>
                    </div>
                  {/if}
                  
                  <!-- Caption -->
                  {#if image.caption}
                    <div class="absolute bottom-0 left-0 right-0 bg-black bg-opacity-50 p-2 text-white text-sm">
                      {image.caption}
                    </div>
                  {/if}
                </div>
              {/if}
            {/each}
          </div>
          
          <!-- Navigation arrows -->
          {#if showArrows && normalizedImages.length > 1}
            <button
              type="button"
              class="absolute left-2 top-1/2 -translate-y-1/2 z-10 bg-white/70 dark:bg-black/70 p-2 rounded-full shadow-md hover:bg-white/90 dark:hover:bg-black/90 opacity-0 group-hover:opacity-100 transition-opacity"
              aria-label="Previous image"
              on:click|preventDefault={() => goToPrev()}
            >
              <svg class="h-5 w-5 text-neutral-800 dark:text-white" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="m15 18-6-6 6-6" />
              </svg>
            </button>
            
            <button
              type="button"
              class="absolute right-2 top-1/2 -translate-y-1/2 z-10 bg-white/70 dark:bg-black/70 p-2 rounded-full shadow-md hover:bg-white/90 dark:hover:bg-black/90 opacity-0 group-hover:opacity-100 transition-opacity"
              aria-label="Next image"
              on:click|preventDefault={() => goToNext()}
            >
              <svg class="h-5 w-5 text-neutral-800 dark:text-white" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="m9 18 6-6-6-6" />
              </svg>
            </button>
          {/if}
          
          <!-- Pagination dots -->
          {#if showDots && normalizedImages.length > 1}
            <div class="absolute bottom-2 left-0 right-0 flex justify-center space-x-2">
              {#each normalizedImages as _, index}
                <button
                  type="button"
                  class="h-2 w-2 rounded-full transition-colors focus:outline-none"
                  class:bg-white={index === activeIndex}
                  class:bg-white/30={index !== activeIndex}
                  aria-label={`Go to image ${index + 1}`}
                  aria-current={index === activeIndex ? 'true' : 'false'}
                  on:click={() => goToIndex(index)}
                ></button>
              {/each}
            </div>
          {/if}
        {/if}
      </div>
      
      <!-- Thumbnails -->
      {#if showThumbnails && normalizedImages.length > 1}
        <div class="flex {thumbnailsClasses} {gap} overflow-auto scrollbar-thin">
          {#each normalizedImages as image, index}
            <button
              type="button"
              class="{thumbnailSize} overflow-hidden {rounded} border-2 transition-colors focus:outline-none"
              class:border-primary={index === activeIndex}
              class:border-transparent={index !== activeIndex}
              aria-label={`View image ${index + 1}`}
              aria-current={index === activeIndex ? 'true' : 'false'}
              on:click={() => goToIndex(index)}
            >
              <div style="aspect-ratio: {aspectRatio};" class="relative">
                <img
                  src={image.src}
                  alt={`Thumbnail ${index + 1}`}
                  class="h-full w-full object-cover"
                  loading="lazy"
                />
              </div>
            </button>
          {/each}
        </div>
      {/if}
    </div>
  </div>
  
  <!-- Lightbox -->
  {#if enableLightbox && lightboxActive && normalizedImages.length > 0}
    <div 
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/90 p-4"
      transition:fade={{ duration: 200 }}
      on:click|self={toggleLightbox}
      on:touchstart={handleTouchStart}
      on:touchmove={handleTouchMove}
      on:touchend={handleTouchEnd}
    >
      <!-- Close button -->
      <button 
        type="button"
        class="absolute top-4 right-4 z-50 rounded-full bg-white/10 p-2 text-white hover:bg-white/20 focus:outline-none"
        aria-label="Close lightbox"
        on:click={toggleLightbox}
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="18" y1="6" x2="6" y2="18"></line>
          <line x1="6" y1="6" x2="18" y2="18"></line>
        </svg>
      </button>
      
      <!-- Image -->
      <div class="relative h-full w-full flex items-center justify-center" in:fade={{ duration: 200 }}>
        <img
          src={normalizedImages[activeIndex].src}
          alt={normalizedImages[activeIndex].alt}
          class="max-h-full max-w-full object-contain transition-transform"
          style="transform: scale({currentZoom})"
        />
        
        <!-- Caption -->
        {#if normalizedImages[activeIndex].caption}
          <div class="absolute bottom-12 left-0 right-0 bg-black bg-opacity-50 p-4 text-center text-white">
            {normalizedImages[activeIndex].caption}
          </div>
        {/if}
      </div>
      
      <!-- Lightbox controls -->
      <div class="absolute bottom-4 left-0 right-0 flex justify-center gap-4 text-white/80">
        {#if showCounter}
          <div class="bg-black/50 rounded-full px-3 py-1 text-sm">
            {activeIndex + 1} / {normalizedImages.length}
          </div>
        {/if}
        
        {#if enableZoom}
          <div class="flex items-center gap-2 bg-black/50 rounded-full px-3 py-1">
            <button
              type="button"
              class="p-1 hover:text-white"
              aria-label="Zoom out"
              disabled={currentZoom <= 0.5}
              on:click={zoomOut}
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="11" cy="11" r="8"></circle>
                <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                <line x1="8" y1="11" x2="14" y2="11"></line>
              </svg>
            </button>
            
            <button
              type="button"
              class="p-1 hover:text-white"
              aria-label="Reset zoom"
              disabled={currentZoom === 1}
              on:click={resetZoom}
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M3 12a9 9 0 1 0 18 0 9 9 0 0 0-18 0z"/>
                <path d="M12 8v4l3 3"/>
              </svg>
            </button>
            
            <button
              type="button"
              class="p-1 hover:text-white"
              aria-label="Zoom in"
              disabled={currentZoom >= 3}
              on:click={zoomIn}
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="11" cy="11" r="8"></circle>
                <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                <line x1="11" y1="8" x2="11" y2="14"></line>
                <line x1="8" y1="11" x2="14" y2="11"></line>
              </svg>
            </button>
          </div>
        {/if}
      </div>
      
      <!-- Navigation buttons -->
      {#if normalizedImages.length > 1}
        <button
          type="button"
          class="absolute left-4 top-1/2 -translate-y-1/2 z-50 bg-white/10 p-3 rounded-full text-white hover:bg-white/20 focus:outline-none"
          aria-label="Previous image"
          on:click|stopPropagation={() => goToPrev()}
        >
          <svg class="h-6 w-6" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="m15 18-6-6 6-6" />
          </svg>
        </button>
        
        <button
          type="button"
          class="absolute right-4 top-1/2 -translate-y-1/2 z-50 bg-white/10 p-3 rounded-full text-white hover:bg-white/20 focus:outline-none"
          aria-label="Next image"
          on:click|stopPropagation={() => goToNext()}
        >
          <svg class="h-6 w-6" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="m9 18 6-6-6-6" />
          </svg>
        </button>
      {/if}
    </div>
  {/if}
  
  <style>
    /* Hide scrollbar but keep functionality */
    .scrollbar-thin {
      scrollbar-width: thin;
    }
    
    .scrollbar-thin::-webkit-scrollbar {
      height: 4px;
      width: 4px;
    }
    
    .scrollbar-thin::-webkit-scrollbar-thumb {
      background-color: rgba(100, 100, 100, 0.4);
      border-radius: 2px;
    }
    
    .scrollbar-thin::-webkit-scrollbar-track {
      background-color: rgba(100, 100, 100, 0.1);
    }
  </style>