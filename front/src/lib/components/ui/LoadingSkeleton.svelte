<!-- src/lib/components/LoadingSkeleton.svelte -->
<script>
    export let type = 'default'; // 'default', 'text', 'rect', 'circle', 'auctionCard', 'auctionHeader', 'auctionContent', 'auctionSidebar', 'auctionForm', 'propertyCard'
    export let width = '100%';
    export let height = '1rem';
    export let borderRadius = '0.25rem';
    export let class_ = '';
    
    // Export class as class_ because "class" is a reserved word
    export { class_ as class };
    
    // Helper function to generate skeleton items
    function renderItems(count) {
      return Array(count).fill(null);
    }
  </script>
  
  <div class={`skeleton-wrapper ${class_}`}>
    {#if type === 'auctionCard'}
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden h-full animate-pulse">
        <div class="bg-gray-200 dark:bg-gray-700 h-56 w-full"></div>
        <div class="p-4">
          <div class="flex justify-between mb-3">
            <div class="h-6 bg-gray-200 dark:bg-gray-700 rounded w-1/4"></div>
            <div class="h-6 bg-gray-200 dark:bg-gray-700 rounded w-1/4"></div>
          </div>
          <div class="h-5 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mb-2"></div>
          <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-2/3 mb-4"></div>
          <div class="h-16 bg-gray-200 dark:bg-gray-700 rounded mb-3"></div>
          <div class="flex justify-between items-center">
            <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/4"></div>
            <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/3"></div>
          </div>
        </div>
      </div>
    
    {:else if type === 'auctionHeader'}
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 animate-pulse">
        <div class="flex flex-wrap justify-between">
          <div class="w-3/4">
            <div class="flex space-x-2 mb-3">
              <div class="h-6 bg-gray-200 dark:bg-gray-700 rounded-md w-20"></div>
              <div class="h-6 bg-gray-200 dark:bg-gray-700 rounded-md w-32"></div>
            </div>
            <div class="h-8 bg-gray-200 dark:bg-gray-700 rounded w-full max-w-md mb-2"></div>
            <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-48"></div>
          </div>
          <div class="w-1/4 flex justify-end">
            <div class="h-10 bg-gray-200 dark:bg-gray-700 rounded-md w-32"></div>
          </div>
        </div>
      </div>
    
    {:else if type === 'auctionContent'}
      <div class="space-y-6 animate-pulse">
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
          <div class="aspect-w-16 aspect-h-9 bg-gray-200 dark:bg-gray-700"></div>
        </div>
        
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
          <div class="h-6 bg-gray-200 dark:bg-gray-700 rounded w-48 mb-4"></div>
          <div class="space-y-2">
            <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-full"></div>
            <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-full"></div>
            <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-2/3"></div>
          </div>
          
          <div class="mt-8 grid grid-cols-2 gap-4">
            <div>
              <div class="h-5 bg-gray-200 dark:bg-gray-700 rounded w-32 mb-3"></div>
              <div class="grid grid-cols-2 gap-2">
                {#each renderItems(4) as _, i}
                  <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded"></div>
                  <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded"></div>
                {/each}
              </div>
            </div>
            <div>
              <div class="h-5 bg-gray-200 dark:bg-gray-700 rounded w-32 mb-3"></div>
              <div class="grid grid-cols-2 gap-2">
                {#each renderItems(3) as _, i}
                  <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded"></div>
                  <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded"></div>
                {/each}
              </div>
            </div>
          </div>
        </div>
      </div>
    
    {:else if type === 'auctionSidebar'}
      <div class="space-y-6 animate-pulse">
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
          <div class="h-5 bg-gray-200 dark:bg-gray-700 rounded w-40 mb-3"></div>
          <div class="grid grid-cols-4 gap-2 bg-gray-100 dark:bg-gray-700 p-3 rounded-lg mb-4">
            {#each renderItems(4) as _, i}
              <div class="flex flex-col items-center">
                <div class="h-8 bg-gray-200 dark:bg-gray-600 rounded w-12 mb-1"></div>
                <div class="h-3 bg-gray-200 dark:bg-gray-600 rounded w-8"></div>
              </div>
            {/each}
          </div>
          
          <div class="border-t border-gray-200 dark:border-gray-700 pt-4 mb-4">
            <div class="flex justify-between mb-2">
              <div class="h-5 bg-gray-200 dark:bg-gray-700 rounded w-32"></div>
              <div class="h-6 bg-gray-200 dark:bg-gray-700 rounded w-20"></div>
            </div>
            <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-24 mb-4"></div>
            <div class="h-10 bg-gray-200 dark:bg-gray-700 rounded w-full"></div>
          </div>
        </div>
        
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
          <div class="h-40 bg-gray-200 dark:bg-gray-700"></div>
          <div class="p-4">
            <div class="h-5 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mb-3"></div>
            <div class="grid grid-cols-2 gap-2 mb-4">
              {#each renderItems(4) as _, i}
                <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded"></div>
                <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded"></div>
              {/each}
            </div>
          </div>
        </div>
      </div>
    
    {:else if type === 'auctionForm'}
      <div class="space-y-6 animate-pulse">
        <div class="h-7 bg-gray-200 dark:bg-gray-700 rounded w-48 mb-4"></div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="space-y-4">
            <div class="h-5 bg-gray-200 dark:bg-gray-700 rounded w-32 mb-2"></div>
            <div class="h-10 bg-gray-200 dark:bg-gray-700 rounded w-full"></div>
          </div>
          <div class="space-y-4">
            <div class="h-5 bg-gray-200 dark:bg-gray-700 rounded w-32 mb-2"></div>
            <div class="h-10 bg-gray-200 dark:bg-gray-700 rounded w-full"></div>
          </div>
        </div>
        
        <div class="space-y-4">
          <div class="h-5 bg-gray-200 dark:bg-gray-700 rounded w-32 mb-2"></div>
          <div class="h-32 bg-gray-200 dark:bg-gray-700 rounded w-full"></div>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="space-y-4">
            <div class="h-5 bg-gray-200 dark:bg-gray-700 rounded w-32 mb-2"></div>
            <div class="h-10 bg-gray-200 dark:bg-gray-700 rounded w-full"></div>
          </div>
          <div class="space-y-4">
            <div class="h-5 bg-gray-200 dark:bg-gray-700 rounded w-32 mb-2"></div>
            <div class="h-10 bg-gray-200 dark:bg-gray-700 rounded w-full"></div>
          </div>
          <div class="space-y-4">
            <div class="h-5 bg-gray-200 dark:bg-gray-700 rounded w-32 mb-2"></div>
            <div class="h-10 bg-gray-200 dark:bg-gray-700 rounded w-full"></div>
          </div>
        </div>
        
        <div class="h-48 bg-gray-200 dark:bg-gray-700 rounded w-full"></div>
        
        <div class="flex justify-end space-x-4">
          <div class="h-10 bg-gray-200 dark:bg-gray-700 rounded w-24"></div>
          <div class="h-10 bg-gray-200 dark:bg-gray-700 rounded w-24"></div>
        </div>
      </div>
    
    {:else if type === 'propertyCard'}
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden h-full animate-pulse">
        <div class="bg-gray-200 dark:bg-gray-700 h-48 w-full"></div>
        <div class="p-4">
          <div class="flex justify-between mb-3">
            <div class="h-5 bg-gray-200 dark:bg-gray-700 rounded w-1/3"></div>
            <div class="h-5 bg-gray-200 dark:bg-gray-700 rounded w-1/4"></div>
          </div>
          <div class="h-6 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mb-2"></div>
          <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2 mb-4"></div>
          <div class="grid grid-cols-2 gap-2 mb-3">
            <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded"></div>
            <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded"></div>
          </div>
        </div>
      </div>
    
    {:else if type === 'default' || type === 'rect'}
      <div 
        class="bg-gray-200 dark:bg-gray-700 animate-pulse rounded"
        style="width: {width}; height: {height}; border-radius: {borderRadius};"
      ></div>
    
    {:else if type === 'circle'}
      <div 
        class="bg-gray-200 dark:bg-gray-700 animate-pulse rounded-full"
        style="width: {width}; height: {height};"
      ></div>
    
    {:else if type === 'text'}
      <div class="space-y-2 animate-pulse">
        <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-5/6"></div>
        <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded"></div>
        <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-4/6"></div>
      </div>
    {/if}
  </div>
  
  <style>
    .skeleton-wrapper {
      display: block;
    }
    
    @keyframes pulse {
      0%, 100% {
        opacity: 1;
      }
      50% {
        opacity: 0.5;
      }
    }
    
    .animate-pulse {
      animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }
  </style>