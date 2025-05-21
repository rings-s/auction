<!-- src/lib/components/EmptyState.svelte -->
<script>
    export let icon = 'default'; // 'default', 'search', 'auction', 'property', 'user'
    export let title = '';
    export let description = '';
    export let actionLabel = '';
    export let actionUrl = '';
    
    // Define icons based on the type
    const icons = {
      default: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />`,
      
      search: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />`,
      
      auction: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />`,
      
      property: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />`,
      
      user: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />`
    };
  </script>
  
  <div class="text-center py-12 px-4 sm:px-6 lg:px-8 bg-white dark:bg-gray-800 rounded-lg shadow-md">
    <div class="inline-flex items-center justify-center h-16 w-16 rounded-full bg-primary-100 dark:bg-primary-900 text-primary-600 dark:text-primary-300 mb-6">
      <svg class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        {@html icons[icon] || icons.default}
      </svg>
    </div>
    
    <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">
      {title}
    </h3>
    
    <p class="max-w-md mx-auto text-base text-gray-500 dark:text-gray-400 mb-6">
      {description}
    </p>
    
    {#if actionLabel && actionUrl}
      <a 
        href={actionUrl} 
        class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors duration-200"
      >
        {actionLabel}
      </a>
    {/if}
  </div>