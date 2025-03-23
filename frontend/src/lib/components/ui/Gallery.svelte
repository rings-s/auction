<!-- src/lib/components/ui/Gallery.svelte -->
<script>
    import { onMount, onDestroy, createEventDispatcher } from 'svelte';
    import { fade, fly, scale } from 'svelte/transition';
    import { quintOut } from 'svelte/easing';
    import { browser } from '$app/environment';
    import { language } from '$lib/i18n';
    
    const dispatch = createEventDispatcher();
    
    // Props with defaults
    export let images = [];
    export let thumbnails = true;
    export let autoplay = false;
    export let autoplaySpeed = 5000;
    export let lightbox = true;
    export let options = {};
    export let aspectRatio = '16/9'; // Can be '1/1', '4/3', '16/9', '21/9', etc.
    export let lazyLoad = true;
    
    // React to options passed from parent
    $: mergedOptions = {
      rtl: $language === 'ar',
      showArrows: true,
      showDots: true,
      infinite: true,
      ...options
    };
    
    // Reactive states
    let activeIndex = 0;
    let lightboxActive = false;
    let thumbsContainer;
    let isMouseDown = false;
    let startX;
    let scrollLeft;
    let timer;
    let touching = false;
    let touchStartX = 0;
    let touchStartY = 0;
    let isDragging = false;
    let dragThreshold = 5;
    let dragDistance = 0;
    let loadedImages = new Set();
    let imageErrors = new Set();
    
    // Initialize loaded images state
    $: if (images && images.length > 0 && !lazyLoad) {
      // Pre-mark first few images as loaded for non-lazy loading
      for (let i = 0; i < Math.min(3, images.length); i++) {
        loadedImages.add(i);
      }
    }
    
    // Determine if the RTL mode is active
    $: isRTL = mergedOptions.rtl;
  
    // Ensure images is always an array, even if a single string is passed
    $: imagesList = Array.isArray(images) ? images : [images];
    
    // Reset active index if number of images changes
    $: if (imagesList && activeIndex >= imagesList.length) {
      activeIndex = Math.max(0, imagesList.length - 1);
    }
    
    // Handle autoplay
    $: if (autoplay && imagesList.length > 1) {
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
      if (imagesList.length <= 1) return;
      
      activeIndex = mergedOptions.infinite ?
        (activeIndex + 1) % imagesList.length :
        Math.min(activeIndex + 1, imagesList.length - 1);
        
      dispatch('change', { index: activeIndex, image: imagesList[activeIndex] });
      
      // Preload next image
      if (lazyLoad && activeIndex + 1 < imagesList.length) {
        preloadImage(activeIndex + 1);
      }
    }
    
    function goToPrev() {
      if (imagesList.length <= 1) return;
      
      activeIndex = mergedOptions.infinite ?
        (activeIndex - 1 + imagesList.length) % imagesList.length :
        Math.max(activeIndex - 1, 0);
        
      dispatch('change', { index: activeIndex, image: imagesList[activeIndex] });
      
      // Preload previous image
      if (lazyLoad && activeIndex - 1 >= 0) {
        preloadImage(activeIndex - 1);
      }
    }
    
    function goToIndex(index) {
      if (index === activeIndex || index < 0 || index >= imagesList.length) return;
      
      activeIndex = index;
      dispatch('change', { index: activeIndex, image: imagesList[activeIndex] });
      
      // Ensure the thumbnail is visible
      if (thumbnails && thumbsContainer) {
        scrollToThumbnail(index);
      }
      
      // Preload adjacent images
      if (lazyLoad) {
        preloadImage(index);
        if (index + 1 < imagesList.length) preloadImage(index + 1);
        if (index - 1 >= 0) preloadImage(index - 1);
      }
    }
    
    function preloadImage(index) {
      if (index < 0 || index >= imagesList.length || loadedImages.has(index)) return;
      
      const img = new Image();
      img.src = imagesList[index];
      img.onload = () => {
        loadedImages.add(index);
      };
      img.onerror = () => {
        imageErrors.add(index);
      };
    }
    
    function toggleLightbox() {
      if (lightbox) {
        lightboxActive = !lightboxActive;
        if (lightboxActive) {
          stopAutoplay();
          document.body.style.overflow = 'hidden';
        } else {
          if (autoplay) startAutoplay();
          document.body.style.overflow = '';
        }
      }
    }
    
    function scrollToThumbnail(index) {
      if (!thumbsContainer) return;
      
      const thumbnail = thumbsContainer.children[index];
      if (thumbnail) {
        const containerWidth = thumbsContainer.offsetWidth;
        const thumbnailLeft = thumbnail.offsetLeft;
        const thumbnailWidth = thumbnail.offsetWidth;
        
        // Adjust for RTL mode
        if (isRTL) {
          // In RTL mode, scrollLeft is negative
          const maxScroll = thumbsContainer.scrollWidth - containerWidth;
          thumbsContainer.scrollLeft = -(maxScroll - thumbnailLeft + (containerWidth - thumbnailWidth) / 2);
        } else {
          thumbsContainer.scrollLeft = thumbnailLeft - (containerWidth - thumbnailWidth) / 2;
        }
      }
    }
    
    // Mouse events for thumbnails scrolling
    function handleMouseDown(e) {
      isMouseDown = true;
      startX = e.pageX - thumbsContainer.offsetLeft;
      scrollLeft = thumbsContainer.scrollLeft;
    }
    
    function handleMouseMove(e) {
      if (!isMouseDown) return;
      e.preventDefault();
      const x = e.pageX - thumbsContainer.offsetLeft;
      const walk = (x - startX) * 2;
      thumbsContainer.scrollLeft = scrollLeft - walk;
    }
    
    function handleMouseUp() {
      isMouseDown = false;
    }
    
    // Touch events for swipe
    function handleTouchStart(e) {
      if (imagesList.length <= 1) return;
      
      touching = true;
      isDragging = false;
      dragDistance = 0;
      touchStartX = e.touches[0].clientX;
      touchStartY = e.touches[0].clientY;
    }
    
    function handleTouchMove(e) {
      if (!touching) return;
      
      const touchX = e.touches[0].clientX;
      const touchY = e.touches[0].clientY;
      
      // Calculate horizontal and vertical distance
      const deltaX = touchStartX - touchX;
      const deltaY = touchStartY - touchY;
      
      // If vertical scrolling is dominant, don't swipe the gallery
      if (Math.abs(deltaY) > Math.abs(deltaX) && !isDragging) {
        return;
      }
      
      // Set dragging if threshold is exceeded
      if (Math.abs(deltaX) > dragThreshold) {
        isDragging = true;
        dragDistance = deltaX;
        
        // Prevent page scrolling while swiping gallery
        e.preventDefault();
      }
    }
    
    function handleTouchEnd() {
      if (!touching) return;
      
      touching = false;
      
      if (isDragging) {
        if (dragDistance > 50) {
          // Swiped right-to-left (next in LTR, previous in RTL)
          isRTL ? goToPrev() : goToNext();
        } else if (dragDistance < -50) {
          // Swiped left-to-right (previous in LTR, next in RTL)
          isRTL ? goToNext() : goToPrev();
        }
      }
      
      dragDistance = 0;
      isDragging = false;
    }
    
    // Keyboard navigation
    function handleKeydown(e) {
      // Only handle keys when lightbox is active or gallery is focused
      if (!lightboxActive && !document.activeElement.closest('.gallery-container')) {
        return;
      }
      
      switch (e.key) {
        case 'ArrowLeft':
          isRTL ? goToNext() : goToPrev();
          e.preventDefault();
          break;
        case 'ArrowRight':
          isRTL ? goToPrev() : goToNext();
          e.preventDefault();
          break;
        case 'Escape':
          if (lightboxActive) {
            toggleLightbox();
            e.preventDefault();
          }
          break;
      }
    }
    
    // Handle image load and error events
    function handleImageLoad(index) {
      loadedImages.add(index);
      loadedImages = loadedImages; // Trigger reactivity
    }
    
    function handleImageError(index) {
      imageErrors.add(index);
      imageErrors = imageErrors; // Trigger reactivity
    }
    
    // Lifecycle
    onMount(() => {
      if (browser) {
        // Preload visible and adjacent images
        preloadImage(activeIndex);
        if (activeIndex + 1 < imagesList.length) preloadImage(activeIndex + 1);
        if (activeIndex - 1 >= 0) preloadImage(activeIndex - 1);
        
        // Set up keyboard listener
        window.addEventListener('keydown', handleKeydown);
        
        // Initial thumbnail scroll
        if (thumbnails && thumbsContainer) {
          setTimeout(() => scrollToThumbnail(activeIndex), 100);
        }
      }
    });
    
    onDestroy(() => {
      if (browser) {
        stopAutoplay();
        window.removeEventListener('keydown', handleKeydown);
        
        // Ensure body overflow is restored if component is destroyed while lightbox is open
        if (lightboxActive) {
          document.body.style.overflow = '';
        }
      }
    });
  </script>
  
  <div 
    class="gallery-container relative overflow-hidden rounded-lg bg-neutral-100 dark:bg-neutral-800"
    class:rtl={isRTL}
    style="--aspect-ratio: {aspectRatio};"
    role="region"
    aria-label="Image gallery"
    on:touchstart={handleTouchStart}
    on:touchmove={handleTouchMove}
    on:touchend={handleTouchEnd}
    on:touchcancel={handleTouchEnd}
  >
    <!-- Main gallery display -->
    <div 
      class="gallery-main relative overflow-hidden"
      style="aspect-ratio: {aspectRatio};"
    >
      {#if imagesList.length === 0}
        <!-- Empty gallery state -->
        <div class="absolute inset-0 flex items-center justify-center">
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
        <!-- Gallery images -->
        <div 
          class="absolute inset-0 flex"
          style="transform: translateX({(isRTL ? activeIndex : -activeIndex) * 100}%);"
          class:transition-transform={!isDragging}
          class:duration-300={!isDragging}
        >
          {#each imagesList as image, index}
            <div 
              class="gallery-slide relative h-full w-full flex-shrink-0 overflow-hidden"
              style="transform: translateX({(isRTL ? -index : index) * 100}%);"
            >
              <!-- Image container -->
              <div class="absolute inset-0 flex items-center justify-center">
                {#if lazyLoad ? loadedImages.has(index) || index === activeIndex || index === activeIndex + 1 || index === activeIndex - 1 : true}
                  <!-- Image with loading and error states -->
                  <img
                    src={image}
                    alt={`Gallery image ${index + 1}`}
                    class="h-full w-full object-cover transition-opacity duration-500"
                    class:opacity-0={!loadedImages.has(index)}
                    class:opacity-100={loadedImages.has(index)}
                    on:load={() => handleImageLoad(index)}
                    on:error={() => handleImageError(index)}
                  />
                {/if}
                
                <!-- Loading state -->
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
              </div>
              
              <!-- Lightbox button if enabled -->
              {#if lightbox && loadedImages.has(index)}
                <button
                  type="button"
                  class="absolute inset-0 h-full w-full cursor-zoom-in focus:outline-none"
                  aria-label="Open image in lightbox"
                  on:click={toggleLightbox}
                ></button>
              {/if}
            </div>
          {/each}
        </div>
      {/if}
      
      <!-- Navigation arrows -->
      {#if mergedOptions.showArrows && imagesList.length > 1}
        <button
          type="button"
          class="gallery-arrow gallery-arrow-prev absolute top-1/2 -translate-y-1/2 z-10 bg-white/60 dark:bg-black/60 backdrop-blur-sm text-neutral-800 dark:text-white p-2 rounded-full shadow-md hover:bg-white/80 dark:hover:bg-black/80 transition-all opacity-0 group-hover:opacity-100 focus:opacity-100 focus:outline-none"
          class:left-4={!isRTL}
          class:right-4={isRTL}
          aria-label="Previous image"
          on:click|preventDefault={goToPrev}
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-5 w-5"
            class:rotate-180={isRTL}
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="m15 18-6-6 6-6" />
          </svg>
        </button>
        
        <button
          type="button"
          class="gallery-arrow gallery-arrow-next absolute top-1/2 -translate-y-1/2 z-10 bg-white/60 dark:bg-black/60 backdrop-blur-sm text-neutral-800 dark:text-white p-2 rounded-full shadow-md hover:bg-white/80 dark:hover:bg-black/80 transition-all opacity-0 group-hover:opacity-100 focus:opacity-100 focus:outline-none"
          class:right-4={!isRTL}
          class:left-4={isRTL}
          aria-label="Next image"
          on:click|preventDefault={goToNext}
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-5 w-5"
            class:rotate-180={isRTL}
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="m9 18 6-6-6-6" />
          </svg>
        </button>
      {/if}
      
      <!-- Pagination dots -->
      {#if mergedOptions.showDots && imagesList.length > 1}
        <div class="absolute bottom-4 left-0 right-0 flex justify-center space-x-2">
          {#each imagesList as _, index}
            <button
              type="button"
              class="h-2 w-2 rounded-full transition-all focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
              class:bg-white={index === activeIndex}
              class:bg-white/50={index !== activeIndex}
              aria-label={`Go to image ${index + 1}`}
              aria-current={index === activeIndex ? 'true' : 'false'}
              on:click={() => goToIndex(index)}
            ></button>
          {/each}
        </div>
      {/if}
    </div>
    
    <!-- Thumbnails -->
    {#if thumbnails && imagesList.length > 1}
      <div 
        class="gallery-thumbnails mt-2 overflow-x-auto overflow-y-hidden scrollbar-thin scrollbar-thumb-neutral-400 dark:scrollbar-thumb-neutral-600 scrollbar-track-neutral-200 dark:scrollbar-track-neutral-800"
        bind:this={thumbsContainer}
        on:mousedown={handleMouseDown}
        on:mousemove={handleMouseMove}
        on:mouseup={handleMouseUp}
        on:mouseleave={handleMouseUp}
      >
        <div class="flex gap-2 pb-2" class:flex-row-reverse={isRTL}>
          {#each imagesList as image, index}
            <button
              type="button"
              class="flex-shrink-0 overflow-hidden rounded-md border-2 transition-all focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
              class:border-primary={index === activeIndex}
              class:border-transparent={index !== activeIndex}
              style="width: calc(20% - 8px);"
              aria-label={`View image ${index + 1}`}
              aria-current={index === activeIndex ? 'true' : 'false'}
              on:click={() => goToIndex(index)}
            >
              <div style="aspect-ratio: {aspectRatio};" class="relative">
                <img
                  src={image}
                  alt={`Thumbnail ${index + 1}`}
                  class="h-full w-full object-cover"
                  draggable="false"
                />
              </div>
            </button>
          {/each}
        </div>
      </div>
    {/if}
  </div>
  
  <!-- Lightbox -->
  {#if lightbox && lightboxActive && imagesList.length > 0}
    <div 
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/90 p-4"
      transition:fade={{ duration: 200 }}
      on:click|self={toggleLightbox}
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
          src={imagesList[activeIndex]}
          alt={`Lightbox image ${activeIndex + 1}`}
          class="max-h-full max-w-full object-contain"
        />
      </div>
      
      <!-- Lightbox navigation -->
      {#if imagesList.length > 1}
        <button
          type="button"
          class="absolute top-1/2 -translate-y-1/2 z-50 bg-white/10 p-3 rounded-full text-white hover:bg-white/20 focus:outline-none"
          class:left-4={!isRTL}
          class:right-4={isRTL}
          aria-label="Previous image"
          on:click|stopPropagation={goToPrev}
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-6 w-6"
            class:rotate-180={isRTL}
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="m15 18-6-6 6-6" />
          </svg>
        </button>
        
        <button
          type="button"
          class="absolute top-1/2 -translate-y-1/2 z-50 bg-white/10 p-3 rounded-full text-white hover:bg-white/20 focus:outline-none"
          class:right-4={!isRTL}
          class:left-4={isRTL}
          aria-label="Next image"
          on:click|stopPropagation={goToNext}
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-6 w-6"
            class:rotate-180={isRTL}
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="m9 18 6-6-6-6" />
          </svg>
        </button>
        
        <!-- Image counter -->
        <div class="absolute bottom-4 left-0 right-0 text-center text-white">
          <span class="bg-black/50 px-3 py-1 rounded-full text-sm">
            {activeIndex + 1} / {imagesList.length}
          </span>
        </div>
      {/if}
    </div>
  {/if}
  
  <style>
    /* Make container a flex group for hover effects */
    .gallery-container {
      @apply group relative;
    }
    
    /* Hide scrollbar but keep functionality */
    .scrollbar-thin {
      scrollbar-width: thin;
    }
    
    /* Custom scrollbar styling for webkit browsers */
    .scrollbar-thin::-webkit-scrollbar {
      height: 6px;
    }
    
    .scrollbar-thumb-neutral-400::-webkit-scrollbar-thumb {
      @apply bg-neutral-400;
      border-radius: 3px;
    }
    
    .dark .scrollbar-thumb-neutral-600::-webkit-scrollbar-thumb {
      @apply bg-neutral-600;
    }
    
    .scrollbar-track-neutral-200::-webkit-scrollbar-track {
      @apply bg-neutral-200;
    }
    
    .dark .scrollbar-track-neutral-800::-webkit-scrollbar-track {
      @apply bg-neutral-800;
    }
    
    /* RTL support */
    .rtl {
      direction: rtl;
    }
    
    /* Responsive arrow sizing */
    @media (min-width: 768px) {
      .gallery-arrow {
        @apply p-3;
      }
      
      .gallery-arrow svg {
        @apply h-6 w-6;
      }
    }
    
    /* Fix for Safari aspect ratio */
    @supports not (aspect-ratio: 16/9) {
      .gallery-main {
        position: relative;
        padding-bottom: calc(100% / (var(--aspect-ratio)));
      }
    }
  </style>