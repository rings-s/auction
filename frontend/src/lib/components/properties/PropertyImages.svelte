<!-- src/lib/components/properties/PropertyImages.svelte -->
<script>
  /**
   * Property Images Component
   * An image gallery for property photos with lightbox functionality.
   */
  import { onMount, onDestroy } from 'svelte';
  import { fade, scale } from 'svelte/transition';
  import { t } from '$lib/i18n';
  import Button from '$lib/components/ui/Button.svelte';
  import Spinner from '$lib/components/ui/Spinner.svelte';
  
  // Props
  export let images = [];
  export let mainImageUrl = '';
  export let title = '';
  export let showThumbnails = true;
  export let maxThumbnails = 6;
  
  // State
  let currentImageIndex = 0;
  let imageGallery = [];
  let lightboxOpen = false;
  let lightboxIndex = 0;
  let isLoading = true;
  let touchStartX = 0;
  let touchEndX = 0;
  
  // Preprocessed images array
  function processImages() {
    const processedImages = [];
    
    // Add main image to the beginning if it's not already included
    if (mainImageUrl) {
      const mainImageExists = images.some(img => img.path === mainImageUrl);
      
      if (!mainImageExists) {
        processedImages.push({
          path: mainImageUrl,
          caption: title,
          is_primary: true
        });
      }
    }
    
    // Add the rest of the images
    images.forEach(img => {
      processedImages.push(img);
    });
    
    // Fallback to placeholder if no images
    if (processedImages.length === 0) {
      processedImages.push({
        path: '/images/placeholders/property-placeholder.jpg',
        caption: title,
        is_primary: true
      });
    }
    
    return processedImages;
  }
  
  // Navigate to next image
  function nextImage() {
    if (currentImageIndex < imageGallery.length - 1) {
      currentImageIndex++;
    } else {
      currentImageIndex = 0; // Loop back to first image
    }
  }
  
  // Navigate to previous image
  function prevImage() {
    if (currentImageIndex > 0) {
      currentImageIndex--;
    } else {
      currentImageIndex = imageGallery.length - 1; // Loop to last image
    }
  }
  
  // Open lightbox
  function openLightbox(index) {
    lightboxIndex = index;
    lightboxOpen = true;
    
    // Add event listener for keyboard navigation
    document.addEventListener('keydown', handleKeyDown);
    
    // Prevent scrolling when lightbox is open
    document.body.style.overflow = 'hidden';
  }
  
  // Close lightbox
  function closeLightbox() {
    lightboxOpen = false;
    
    // Remove event listener and restore scrolling
    document.removeEventListener('keydown', handleKeyDown);
    document.body.style.overflow = '';
  }
  
  // Lightbox navigation
  function nextLightboxImage() {
    if (lightboxIndex < imageGallery.length - 1) {
      lightboxIndex++;
    } else {
      lightboxIndex = 0;
    }
  }
  
  function prevLightboxImage() {
    if (lightboxIndex > 0) {
      lightboxIndex--;
    } else {
      lightboxIndex = imageGallery.length - 1;
    }
  }
  
  // Touch handlers for swipe gestures
  function handleTouchStart(event) {
    touchStartX = event.touches[0].clientX;
  }
  
  function handleTouchEnd(event) {
    touchEndX = event.changedTouches[0].clientX;
    handleSwipe();
  }
  
  function handleSwipe() {
    const swipeThreshold = 50;
    if (touchEndX < touchStartX - swipeThreshold) {
      // Swipe left - next image
      lightboxOpen ? nextLightboxImage() : nextImage();
    } else if (touchEndX > touchStartX + swipeThreshold) {
      // Swipe right - previous image
      lightboxOpen ? prevLightboxImage() : prevImage();
    }
  }
  
  // Keyboard navigation handler
  function handleKeyDown(event) {
    if (!lightboxOpen) return;
    
    switch(event.key) {
      case 'ArrowRight':
        nextLightboxImage();
        break;
      case 'ArrowLeft':
        prevLightboxImage();
        break;
      case 'Escape':
        closeLightbox();
        break;
    }
  }
  
  // Handle image load
  function imageLoaded() {
    isLoading = false;
  }
  
  // Initialize component
  onMount(() => {
    imageGallery = processImages();
    
    // Clean up event listener on component destroy
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      
      // Make sure scrolling is restored
      document.body.style.overflow = '';
    };
  });
  
  onDestroy(() => {
    // Ensure scrolling is restored when component is destroyed
    document.body.style.overflow = '';
    document.removeEventListener('keydown', handleKeyDown);
  });
  
  // Reactive declaration to update gallery when props change
  $: {
    // Refresh image gallery when images or mainImageUrl changes
    if (images || mainImageUrl) {
      imageGallery = processImages();
    }
  }
</script>

<div class="property-images">
  <!-- Main Image Carousel -->
  <div class="relative rounded-xl overflow-hidden">
    {#if imageGallery && imageGallery.length > 0}
      <!-- Loading indicator -->
      {#if isLoading}
        <div class="absolute inset-0 flex items-center justify-center bg-cosmos-bg-dark bg-opacity-40 z-10">
          <Spinner color="white" size="lg" />
        </div>
      {/if}
      
      <div class="aspect-[16/9] w-full bg-cosmos-bg-light">
        <img 
          src={imageGallery[currentImageIndex].path} 
          alt={imageGallery[currentImageIndex].caption || title}
          class="h-full w-full object-cover cursor-pointer"
          on:click={() => openLightbox(currentImageIndex)}
          on:load={imageLoaded}
          on:touchstart={handleTouchStart}
          on:touchend={handleTouchEnd}
          loading="eager"
        />
      </div>
      
      <!-- Navigation Arrows (only if more than one image) -->
      {#if imageGallery.length > 1}
        <button 
          class="absolute top-1/2 left-4 -translate-y-1/2 rounded-full bg-cosmos-bg-dark bg-opacity-50 p-2 text-white backdrop-blur-sm transition hover:bg-opacity-70 focus:outline-none focus:ring-2 focus:ring-white focus:ring-opacity-50"
          on:click|stopPropagation|preventDefault={prevImage}
          aria-label={$t('general.previous')}
        >
          <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        
        <button 
          class="absolute top-1/2 right-4 -translate-y-1/2 rounded-full bg-cosmos-bg-dark bg-opacity-50 p-2 text-white backdrop-blur-sm transition hover:bg-opacity-70 focus:outline-none focus:ring-2 focus:ring-white focus:ring-opacity-50"
          on:click|stopPropagation|preventDefault={nextImage}
          aria-label={$t('general.next')}
        >
          <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </button>
        
        <!-- Image Counter -->
        <div class="absolute bottom-4 right-4 rounded-full bg-cosmos-bg-dark bg-opacity-60 px-3 py-1 text-sm text-white backdrop-blur-sm">
          {currentImageIndex + 1} / {imageGallery.length}
        </div>
      {/if}
    {:else}
      <!-- Placeholder if no images -->
      <div class="aspect-[16/9] w-full bg-cosmos-bg-light flex items-center justify-center">
        <p class="text-cosmos-text-muted">{$t('properties.no_images')}</p>
      </div>
    {/if}
  </div>
  
  <!-- Thumbnails -->
  {#if showThumbnails && imageGallery && imageGallery.length > 1}
    <div class="mt-4 grid grid-cols-6 gap-2">
      {#each imageGallery.slice(0, maxThumbnails) as image, i}
        <button 
          class="overflow-hidden rounded-lg border transition-all {i === currentImageIndex ? 'ring-2 ring-primary border-primary' : 'opacity-70 hover:opacity-100 border-transparent'}"
          on:click={() => currentImageIndex = i}
          aria-label={`${$t('properties.view_image')} ${i + 1}`}
          aria-current={i === currentImageIndex ? 'true' : 'false'}
        >
          <div class="aspect-[4/3] bg-cosmos-bg-light">
            <img 
              src={image.path} 
              alt={image.caption || `${title} - ${i + 1}`}
              class="h-full w-full object-cover"
              loading="lazy"
            />
          </div>
        </button>
      {/each}
      
      {#if imageGallery.length > maxThumbnails}
        <button
          class="flex items-center justify-center rounded-lg border border-cosmos-bg-light bg-cosmos-bg-light bg-opacity-40 backdrop-blur-sm transition hover:bg-opacity-60"
          on:click={() => openLightbox(maxThumbnails)}
          aria-label={$t('properties.view_all_images')}
        >
          <div class="flex flex-col items-center text-cosmos-text">
            <span class="text-xl font-medium">+{imageGallery.length - maxThumbnails}</span>
            <span class="text-xs">{$t('properties.more')}</span>
          </div>
        </button>
      {/if}
    </div>
  {/if}
  
  <!-- Lightbox -->
  {#if lightboxOpen}
    <div 
      class="fixed inset-0 z-50 flex items-center justify-center bg-cosmos-bg-dark bg-opacity-90 p-4"
      on:click={closeLightbox}
      transition:fade={{ duration: 200 }}
      on:touchstart={handleTouchStart}
      on:touchend={handleTouchEnd}
      role="dialog"
      aria-modal="true"
      aria-label={$t('properties.image_gallery')}
    >
      <div 
        class="relative max-h-screen max-w-screen-xl"
        on:click|stopPropagation
        transition:scale={{ duration: 300, start: 0.9 }}
      >
        <!-- Close Button -->
        <Button
          variant="ghost"
          size="lg"
          ariaLabel={$t('general.close')}
          class="absolute top-4 right-4 z-50 rounded-full bg-cosmos-bg-dark bg-opacity-50 p-2 text-white backdrop-blur-sm"
          onClick={closeLightbox}
        >
          <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </Button>
        
        <!-- Main Image -->
        <div class="h-[calc(100vh-8rem)] w-auto flex items-center justify-center">
          {#key lightboxIndex}
            <img 
              src={imageGallery[lightboxIndex].path} 
              alt={imageGallery[lightboxIndex].caption || title}
              class="h-full w-auto max-w-full object-contain"
              on:load={() => {}}
              transition:fade={{ duration: 150 }}
            />
          {/key}
        </div>
        
        <!-- Navigation Arrows -->
        <Button
          variant="ghost"
          size="lg"
          ariaLabel={$t('general.previous')}
          class="absolute top-1/2 left-4 -translate-y-1/2 rounded-full bg-cosmos-bg-dark bg-opacity-50 p-2 text-white backdrop-blur-sm"
          onClick={prevLightboxImage}
        >
          <svg class="h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
        </Button>
        
        <Button
          variant="ghost"
          size="lg"
          ariaLabel={$t('general.next')}
          class="absolute top-1/2 right-4 -translate-y-1/2 rounded-full bg-cosmos-bg-dark bg-opacity-50 p-2 text-white backdrop-blur-sm"
          onClick={nextLightboxImage}
        >
          <svg class="h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </Button>
        
        <!-- Image Caption -->
        {#if imageGallery[lightboxIndex].caption}
          <div class="absolute bottom-4 left-1/2 -translate-x-1/2 rounded-lg bg-cosmos-bg-dark bg-opacity-70 px-4 py-2 backdrop-blur-sm">
            <p class="text-center text-white">{imageGallery[lightboxIndex].caption}</p>
          </div>
        {/if}
        
        <!-- Image Counter -->
        <div class="absolute bottom-4 right-4 rounded-full bg-cosmos-bg-dark bg-opacity-70 px-3 py-1 text-white backdrop-blur-sm">
          {lightboxIndex + 1} / {imageGallery.length}
        </div>
        
        <!-- Thumbnails Strip -->
        {#if imageGallery.length > 1}
          <div class="absolute bottom-16 left-1/2 -translate-x-1/2 flex space-x-2 overflow-x-auto bg-cosmos-bg-dark bg-opacity-60 p-2 rounded-lg backdrop-blur-sm" style="max-width: 80vw;">
            {#each imageGallery as image, i}
              <button 
                class="h-16 w-16 flex-shrink-0 overflow-hidden rounded transition {i === lightboxIndex ? 'ring-2 ring-primary border-primary' : 'opacity-60 hover:opacity-100'}" 
                on:click={() => lightboxIndex = i}
                aria-label={`${$t('properties.view_image')} ${i + 1}`}
                aria-current={i === lightboxIndex ? 'true' : 'false'}
              >
                <img 
                  src={image.path} 
                  alt=""
                  class="h-full w-full object-cover"
                  loading="lazy"
                />
              </button>
            {/each}
          </div>
        {/if}
      </div>
    </div>
  {/if}
</div>