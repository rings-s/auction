<script>
    import { t } from '$lib/i18n';
    import { fade } from 'svelte/transition';
    
    export let showFullScreenGallery;
    export let filteredMedia;
    export let activeImageIndex;
    export let activeMediaType;
    export let property;
    export let thumbnailsContainer;
    export let onToggleGallery;
    export let onNextMedia;
    export let onPrevMedia;
    export let onShowMedia;
    export let onHandleTouchStart;
    export let onHandleTouchEnd;
    
    // Format file size
    function formatFileSize(bytes) {
      if (!bytes) return '0 Bytes';
      const k = 1024;
      const sizes = ['Bytes', 'KB', 'MB', 'GB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
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
</script>
  
  <!-- Full Screen Gallery Modal -->
{#if showFullScreenGallery && filteredMedia.length > 0}
  <div 
      class="fixed inset-0 bg-black bg-opacity-95 z-50 flex flex-col items-center justify-center p-4 animate-fadeIn"
      on:click={onToggleGallery}
      on:keydown={(e) => { if (e.key === 'Escape') onToggleGallery(); }}
      on:touchstart={onHandleTouchStart}
      on:touchend={onHandleTouchEnd}
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
        
        <!-- Close Button -->
        <button 
          class="rounded-full bg-red-600 hover:bg-red-700 p-3 focus:outline-none transition-colors shadow-lg"
          on:click={(e) => { e.stopPropagation(); onToggleGallery(); }}
          aria-label={$t('property.closeGallery')}
        >
          <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      
      <div class="relative w-full max-w-6xl mx-auto flex-grow flex items-center justify-center">
        <!-- Main Media Item -->
        <div class="transition-opacity duration-300 w-full h-full flex items-center justify-center" in:fade={{ duration: 200 }}>
          <div 
            role="button"
            tabindex="0"
            class="w-full h-full flex items-center justify-center"
            on:click={(e) => e.stopPropagation()}
            on:keydown={(e) => { if (e.key === 'Enter' || e.key === ' ') e.stopPropagation(); }}
            aria-label={filteredMedia[activeImageIndex]?.name || $t('property.mediaItem')}
          >
            {@html renderMediaItem(filteredMedia[activeImageIndex])}
          </div>
        </div>
        
        <!-- Navigation Controls -->
        {#if filteredMedia.length > 1}
          <button 
            class="absolute left-4 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-50 rounded-full p-3 text-white hover:bg-opacity-80 focus:outline-none focus:ring-2 focus:ring-white focus:ring-opacity-50 transition-all backdrop-blur-sm"
            on:click={(e) => { e.stopPropagation(); onPrevMedia(); }}
            aria-label="Previous item"
          >
            <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7m0 0l-7 7m-7 7h18" />
            </svg>
          </button>
          <button 
            class="absolute right-4 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-50 rounded-full p-3 text-white hover:bg-opacity-80 focus:outline-none focus:ring-2 focus:ring-white focus:ring-opacity-50 transition-all backdrop-blur-sm"
            on:click={(e) => { e.stopPropagation(); onNextMedia(); }}
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
      
      <!-- Thumbnails for quick navigation -->
      {#if filteredMedia.length > 1}
        <div class="w-full max-w-6xl mt-2">
          <div 
            class="flex justify-center overflow-x-auto pb-2 px-2 scrollbar-thin scrollbar-thumb-gray-600 scrollbar-track-transparent"
            bind:this={thumbnailsContainer}
          >
            {#each filteredMedia as item, index}
              <button
                class={`relative mx-1 rounded-lg overflow-hidden flex-shrink-0 h-16 w-16 border-2 transition-all ${activeImageIndex === index ? 'border-primary-500 scale-110 z-10' : 'border-transparent opacity-60 hover:opacity-100'}`}
                on:click={() => { activeImageIndex = index; onToggleGallery(); }}
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
</style>