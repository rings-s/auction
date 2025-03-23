<!-- src/lib/components/property/PropertyImages.svelte -->
<script>
    import { onMount } from 'svelte';
    import { t } from '$lib/i18n';
    
    // Props
    export let images = [];
    export let mainImageUrl = '';
    export let title = '';
    export let showThumbnails = true;
    
    // State
    let currentImageIndex = 0;
    let imageGallery = [];
    let lightboxOpen = false;
    let lightboxIndex = 0;
    
    // Preprocessed images array
    function processImages() {
      // Add main image to the beginning if it's not already included
      const processedImages = [];
      
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
        <div class="aspect-[16/9] w-full">
          <img 
            src={imageGallery[currentImageIndex].path} 
            alt={imageGallery[currentImageIndex].caption || title}
            class="h-full w-full object-cover cursor-pointer"
            on:click={() => openLightbox(currentImageIndex)}
            loading="eager"
          />
        </div>
        
        <!-- Navigation Arrows (Only if more than one image) -->
        {#if imageGallery.length > 1}
          <button 
            class="absolute top-1/2 left-4 -translate-y-1/2 rounded-full bg-cosmos-bg-dark bg-opacity-50 p-2 text-white backdrop-blur-sm transition hover:bg-opacity-70 focus:outline-none"
            on:click|stopPropagation={prevImage}
            aria-label={$t('general.previous')}
          >
            <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          
          <button 
            class="absolute top-1/2 right-4 -translate-y-1/2 rounded-full bg-cosmos-bg-dark bg-opacity-50 p-2 text-white backdrop-blur-sm transition hover:bg-opacity-70 focus:outline-none"
            on:click|stopPropagation={nextImage}
            aria-label={$t('general.next')}
          >
            <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </button>
          
          <!-- Image Counter -->
          <div class="absolute bottom-4 right-4 rounded-full bg-cosmos-bg-dark bg-opacity-50 px-3 py-1 text-sm text-white backdrop-blur-sm">
            {currentImageIndex + 1} / {imageGallery.length}
          </div>
        {/if}
      {:else}
        <!-- Placeholder if no images -->
        <div class="aspect-[16/9] w-full bg-cosmos-bg-light">
          <div class="flex h-full w-full items-center justify-center">
            <p class="text-cosmos-text-muted">{$t('properties.no_images')}</p>
          </div>
        </div>
      {/if}
    </div>
    
    <!-- Thumbnails -->
    {#if showThumbnails && imageGallery && imageGallery.length > 1}
      <div class="mt-4 grid grid-cols-6 gap-2">
        {#each imageGallery as image, i}
          <button 
            class="overflow-hidden rounded-lg {i === currentImageIndex ? 'ring-2 ring-primary' : 'opacity-70 hover:opacity-100'}"
            on:click={() => currentImageIndex = i}
          >
            <div class="aspect-[4/3]">
              <img 
                src={image.path} 
                alt={image.caption || `${title} - ${i + 1}`}
                class="h-full w-full object-cover"
                loading="lazy"
              />
            </div>
          </button>
        {/each}
      </div>
    {/if}
    
    <!-- Lightbox -->
    {#if lightboxOpen}
      <div 
        class="fixed inset-0 z-modal flex items-center justify-center bg-cosmos-bg-dark bg-opacity-90 p-4"
        on:click={closeLightbox}
      >
        <div class="relative max-h-screen max-w-screen-xl" on:click|stopPropagation>
          <!-- Close Button -->
          <button 
            class="absolute top-4 right-4 z-modal rounded-full bg-cosmos-bg-dark bg-opacity-50 p-2 text-white backdrop-blur-sm transition hover:bg-opacity-70 focus:outline-none"
            on:click={closeLightbox}
            aria-label={$t('general.close')}
          >
            <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
          
          <!-- Main Image -->
          <div class="h-[calc(100vh-8rem)] w-auto">
            <img 
              src={imageGallery[lightboxIndex].path} 
              alt={imageGallery[lightboxIndex].caption || title}
              class="h-full w-auto object-contain"
            />
          </div>
          
          <!-- Navigation Arrows -->
          <button 
            class="absolute top-1/2 left-4 -translate-y-1/2 rounded-full bg-cosmos-bg-dark bg-opacity-50 p-2 text-white backdrop-blur-sm transition hover:bg-opacity-70 focus:outline-none"
            on:click|stopPropagation={prevLightboxImage}
            aria-label={$t('general.previous')}
          >
            <svg class="h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          
          <button 
            class="absolute top-1/2 right-4 -translate-y-1/2 rounded-full bg-cosmos-bg-dark bg-opacity-50 p-2 text-white backdrop-blur-sm transition hover:bg-opacity-70 focus:outline-none"
            on:click|stopPropagation={nextLightboxImage}
            aria-label={$t('general.next')}
          >
            <svg class="h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </button>
          
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
        </div>
      </div>
    {/if}
  </div>