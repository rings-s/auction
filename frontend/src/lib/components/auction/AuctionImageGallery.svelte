<!-- src/lib/components/auction/AuctionImageGallery.svelte -->
<script>
  import { onMount } from 'svelte';
  
  // Props
  export let mainImage = '';
  export let images = [];
  export let aspectRatio = '3/2';
  
  // State
  let currentImage = '';
  let thumbnails = [];
  let lightboxOpen = false;
  let lightboxIndex = 0;
  let loading = true;
  
  // Helper function to validate image URLs
  function getValidImageUrl(url) {
    if (!url || url === '' || url === 'null' || url === 'undefined') {
      return 'https://via.placeholder.com/600x400?text=No+Image';
    }
    return url;
  }
  
  // Create full images array and prepare thumbnails
  onMount(() => {
    // Handle case where images is not an array
    const imagesArray = Array.isArray(images) ? images : [];
    
    // Filter out invalid images and deduplicate
    const validImages = [mainImage, ...imagesArray]
      .filter(img => img && img !== '' && img !== 'null' && img !== 'undefined')
      .filter((img, index, self) => self.indexOf(img) === index);  // Remove duplicates
    
    // Create a valid array of images or use a placeholder if none exist
    const fullImageArray = validImages.length > 0 
      ? validImages 
      : ['https://via.placeholder.com/600x400?text=No+Image'];
    
    // Set default current image
    currentImage = getValidImageUrl(fullImageArray[0]);
    
    // Prepare thumbnails array
    thumbnails = fullImageArray.map(img => ({
      src: getValidImageUrl(img),
      active: getValidImageUrl(img) === currentImage
    }));
    
    loading = false;
  });
  
  // Set the selected image as current
  function selectImage(src, index) {
    currentImage = src;
    
    // Update active state in thumbnails
    thumbnails = thumbnails.map((thumbnail, i) => ({
      ...thumbnail,
      active: i === index
    }));
  }
  
  // Handle image load error
  function handleImageError(event) {
    event.target.src = 'https://via.placeholder.com/600x400?text=Image+Not+Found';
  }
  
  // Open lightbox
  function openLightbox(index = 0) {
    lightboxIndex = index;
    lightboxOpen = true;
    
    // Lock body scroll when lightbox is open
    document.body.style.overflow = 'hidden';
  }
  
  // Close lightbox
  function closeLightbox() {
    lightboxOpen = false;
    
    // Restore body scroll
    document.body.style.overflow = '';
  }
  
  // Navigate through lightbox images
  function navigate(direction) {
    const newIndex = lightboxIndex + direction;
    if (newIndex >= 0 && newIndex < thumbnails.length) {
      lightboxIndex = newIndex;
    }
  }
  
  // Handle keyboard navigation in lightbox
  function handleKeydown(event) {
    if (!lightboxOpen) return;
    
    switch (event.key) {
      case 'Escape':
        closeLightbox();
        break;
      case 'ArrowLeft':
        navigate(-1);
        break;
      case 'ArrowRight':
        navigate(1);
        break;
      default:
        break;
    }
  }
  
  // Handle main image keyboard events
  function handleMainImageKeydown(event) {
    if (event.key === 'Enter' || event.key === ' ') {
      thumbnails.length > 0 && openLightbox(thumbnails.findIndex(t => t.src === currentImage));
    }
  }
</script>

<svelte:window on:keydown={handleKeydown} />

<div class="bg-white rounded-xl border border-primary-blue/20 overflow-hidden">
  <!-- Main Image - Simplified without any overlays -->
  <div 
    class="relative transition-all duration-300"
    style="aspect-ratio: {aspectRatio};"
  >
    {#if loading}
      <div class="absolute inset-0 flex items-center justify-center bg-neutral-100">
        <div class="w-8 h-8 border-4 border-primary-blue/30 border-t-secondary-blue rounded-full animate-spin"></div>
      </div>
    {/if}
    
    <!-- Wrap the image in a button for better accessibility -->
    <button 
      class="w-full h-full p-0 border-0 bg-transparent cursor-pointer"
      on:click={() => thumbnails.length > 0 && openLightbox(thumbnails.findIndex(t => t.src === currentImage))}
      on:keydown={handleMainImageKeydown}
      aria-label="View image in lightbox"
    >
      <img 
        src={currentImage} 
        alt="Auction item" 
        class="w-full h-full object-contain p-2"
        on:error={handleImageError}
        on:load={() => loading = false}
      />
    </button>
  </div>
  
  <!-- Thumbnails -->
  {#if thumbnails.length > 1}
    <div class="flex p-2 gap-2 overflow-x-auto scrollbar-thin">
      {#each thumbnails as thumbnail, index}
        <button 
          class="flex-shrink-0 w-16 h-16 rounded-md overflow-hidden focus:outline-none focus:ring-2 focus:ring-secondary-blue transition-all duration-200"
          class:ring-2={thumbnail.active}
          class:ring-secondary-blue={thumbnail.active}
          on:click={() => selectImage(thumbnail.src, index)}
          aria-label={`View thumbnail ${index+1}`}
        >
          <img 
            src={thumbnail.src} 
            alt={`Thumbnail ${index+1}`}
            class="w-full h-full object-cover"
            on:error={handleImageError}
          />
        </button>
      {/each}
    </div>
  {/if}
</div>

<!-- Lightbox -->
{#if lightboxOpen}
  <div 
    role="dialog"
    aria-modal="true"
    aria-label="Image lightbox"
    class="fixed inset-0 z-50 bg-black/90 flex items-center justify-center"
  >
    <!-- Close button -->
    <button 
      class="absolute top-4 right-4 z-10 bg-white/10 rounded-full p-2 hover:bg-white/20 transition-all duration-200"
      on:click={closeLightbox}
      aria-label="Close lightbox"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
      </svg>
    </button>
    
    <!-- Navigation buttons -->
    {#if thumbnails.length > 1}
      <button 
        class="absolute left-4 z-10 bg-white/10 rounded-full p-2 hover:bg-white/20 transition-all duration-200"
        on:click={() => navigate(-1)}
        disabled={lightboxIndex === 0}
        class:opacity-50={lightboxIndex === 0}
        class:cursor-not-allowed={lightboxIndex === 0}
        aria-label="Previous image"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
      </button>
      
      <button 
        class="absolute right-4 z-10 bg-white/10 rounded-full p-2 hover:bg-white/20 transition-all duration-200"
        on:click={() => navigate(1)}
        disabled={lightboxIndex === thumbnails.length - 1}
        class:opacity-50={lightboxIndex === thumbnails.length - 1}
        class:cursor-not-allowed={lightboxIndex === thumbnails.length - 1}
        aria-label="Next image"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
      </button>
    {/if}
    
    <!-- Main lightbox image container -->
    <div class="max-w-4xl max-h-full p-4">
      <img 
        src={thumbnails[lightboxIndex]?.src || 'https://via.placeholder.com/600x400?text=No+Image'}
        alt={`Image ${lightboxIndex + 1}`}
        class="max-w-full max-h-full object-contain"
        on:error={handleImageError}
      />
    </div>
    
    <!-- Counter indicator -->
    {#if thumbnails.length > 1}
      <div class="absolute bottom-4 left-1/2 transform -translate-x-1/2 bg-black/50 text-white text-sm py-1 px-3 rounded-full">
        {lightboxIndex + 1} / {thumbnails.length}
      </div>
    {/if}
  </div>
{/if}

<style>
  /* Custom scrollbar for thumbnails */
  .scrollbar-thin::-webkit-scrollbar {
    height: 4px;
  }
  
  .scrollbar-thin::-webkit-scrollbar-track {
    background: #f3f4f6;
    border-radius: 2px;
  }
  
  .scrollbar-thin::-webkit-scrollbar-thumb {
    background-color: #9ca3af;
    border-radius: 2px;
  }
  
  .scrollbar-thin {
    scrollbar-width: thin;
    scrollbar-color: #9ca3af #f3f4f6;
  }
</style>