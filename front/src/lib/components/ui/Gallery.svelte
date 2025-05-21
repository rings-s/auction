<!-- src/lib/components/Gallery.svelte -->
<script>
    import { onMount } from 'svelte';
    
    export let images = [];
    export let fallbackImage = '';
    export let alt = 'Gallery image';
    export let showThumbnails = true;
    export let aspectRatio = '16:9'; // '16:9', '4:3', '1:1'
    
    let selectedImage = null;
    let thumbnailsContainer;
    
    // Process images to ensure consistent format
    $: processedImages = processImages(images);
    $: selectedImage = selectedImage || (processedImages.length > 0 ? processedImages[0] : null);
    
    // Generate aspect ratio class
    $: aspectClass = getAspectClass(aspectRatio);
    
    function processImages(images) {
      if (!images || images.length === 0) {
        return fallbackImage ? [{ url: fallbackImage, alt }] : [];
      }
      
      return images.map(img => {
        // Handle various image formats
        if (typeof img === 'string') {
          return { url: img, alt };
        }
        
        if (img.url) {
          return { url: img.url, alt: img.alt || img.name || alt };
        }
        
        if (img.file) {
          return { url: img.file, alt: img.alt || img.name || alt };
        }
        
        return { url: fallbackImage, alt };
      });
    }
    
    function getAspectClass(ratio) {
      switch (ratio) {
        case '1:1': return 'aspect-w-1 aspect-h-1';
        case '4:3': return 'aspect-w-4 aspect-h-3';
        case '16:9': 
        default: return 'aspect-w-16 aspect-h-9';
      }
    }
    
    function selectImage(image) {
      selectedImage = image;
    }
    
    function nextImage() {
      const currentIndex = processedImages.findIndex(img => img.url === selectedImage.url);
      const nextIndex = (currentIndex + 1) % processedImages.length;
      selectedImage = processedImages[nextIndex];
    }
    
    function prevImage() {
      const currentIndex = processedImages.findIndex(img => img.url === selectedImage.url);
      const prevIndex = (currentIndex - 1 + processedImages.length) % processedImages.length;
      selectedImage = processedImages[prevIndex];
    }
    
    onMount(() => {
      // Initialize selected image
      if (processedImages.length > 0) {
        selectedImage = processedImages[0];
      }
    });
  </script>
  
  <div class="gallery">
    <!-- Main image display -->
    <div class="{aspectClass} bg-gray-100 dark:bg-gray-800 rounded-lg overflow-hidden relative">
      {#if selectedImage}
        <img
          src={selectedImage.url}
          alt={selectedImage.alt}
          class="w-full h-full object-cover transition-opacity duration-300"
        />
      {:else}
        <div class="w-full h-full flex items-center justify-center text-gray-400 dark:text-gray-600">
          <svg class="h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        </div>
      {/if}
      
      {#if processedImages.length > 1}
        <!-- Navigation arrows -->
        <button
          class="absolute left-2 top-1/2 transform -translate-y-1/2 bg-white dark:bg-gray-900 bg-opacity-80 dark:bg-opacity-80 rounded-full p-1.5 shadow-md text-gray-800 dark:text-gray-200 hover:bg-opacity-100 focus:outline-none transition-all duration-200"
          on:click={prevImage}
          aria-label="Previous image"
        >
          <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        <button
          class="absolute right-2 top-1/2 transform -translate-y-1/2 bg-white dark:bg-gray-900 bg-opacity-80 dark:bg-opacity-80 rounded-full p-1.5 shadow-md text-gray-800 dark:text-gray-200 hover:bg-opacity-100 focus:outline-none transition-all duration-200"
          on:click={nextImage}
          aria-label="Next image"
        >
          <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </button>
      {/if}
    </div>
    
    <!-- Thumbnails -->
    {#if showThumbnails && processedImages.length > 1}
      <div 
        class="flex overflow-x-auto space-x-2 mt-2 pb-2 thumbnail-container" 
        bind:this={thumbnailsContainer}
      >
        {#each processedImages as image, index}
          <button
            class="flex-shrink-0 w-16 h-16 bg-gray-100 dark:bg-gray-800 rounded-md overflow-hidden transition-all duration-200 
              {selectedImage && selectedImage.url === image.url 
                ? 'ring-2 ring-primary-500 dark:ring-primary-400' 
                : 'opacity-70 hover:opacity-100'}"
            on:click={() => selectImage(image)}
            aria-label={`Select image ${index + 1}`}
          >
            <img 
              src={image.url} 
              alt={`Thumbnail ${index + 1}`}
              class="w-full h-full object-cover" 
            />
          </button>
        {/each}
      </div>
    {/if}
  </div>
  
  <style>
    .thumbnail-container {
      scrollbar-width: thin;
      scrollbar-color: var(--color-gray-400) transparent;
    }
    
    .thumbnail-container::-webkit-scrollbar {
      height: 6px;
    }
    
    .thumbnail-container::-webkit-scrollbar-track {
      background: transparent;
    }
    
    .thumbnail-container::-webkit-scrollbar-thumb {
      background-color: var(--color-gray-400);
      border-radius: 3px;
    }
    
    .thumbnail-container::-webkit-scrollbar-thumb:hover {
      background-color: var(--color-gray-500);
    }
  </style>