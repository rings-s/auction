<!-- src/lib/components/ui/Pagination.svelte -->
<script>
    /**
     * Pagination Component
     * A flexible pagination component for navigating through multi-page content.
     */
    import { createEventDispatcher } from 'svelte';
    import { language } from '$lib/i18n';
    import Button from './Button.svelte';
    
    const dispatch = createEventDispatcher();
    
    // Props
    export let currentPage = 1;
    export let totalPages = 1;
    export let totalItems = 0;
    export let pageSize = 10;
    export let showPageSize = false;
    export let pageSizeOptions = [10, 25, 50, 100];
    export let showItemCount = true;
    export let siblingsCount = 1; // Number of pages to show on each side of current page
    export let alwaysShowFirstAndLast = true;
    export let disabled = false;
    export let size = "md"; // sm, md, lg
    export let variant = "default"; // default, simple, rounded, minimal
    
    // Local state
    let isRTL;
    
    // Set RTL based on language
    $: isRTL = $language === 'ar';
    
    // Size classes
    $: sizeClasses = {
      sm: {
        button: "h-8 w-8",
        text: "text-xs",
        item: "px-2 py-1"
      },
      md: {
        button: "h-10 w-10",
        text: "text-sm",
        item: "px-3 py-2"
      },
      lg: {
        button: "h-12 w-12",
        text: "text-base",
        item: "px-4 py-3"
      }
    }[size] || sizeClasses.md;
    
    // Calculate displayed page range
    $: pageRangeDisplayed = 2 * siblingsCount + 1;
    
    // Generate page items for display
    $: pageItems = generatePageItems(currentPage, totalPages, pageRangeDisplayed, alwaysShowFirstAndLast);
    
    // Calculate item count text
    $: itemCountStart = Math.min(totalItems, (currentPage - 1) * pageSize + 1);
    $: itemCountEnd = Math.min(totalItems, currentPage * pageSize);
    $: itemCountText = totalItems > 0 
      ? isRTL 
        ? `${totalItems} من ${itemCountEnd}-${itemCountStart} عرض` 
        : `Showing ${itemCountStart}-${itemCountEnd} of ${totalItems}`
      : isRTL
        ? 'لا توجد عناصر'
        : 'No items to display';
    
    // Generate page items array
    function generatePageItems(current, total, displayed, showEnds) {
      if (total <= 1) return [{ type: 'page', value: 1 }];
      
      let items = [];
      
      // Calculate range of pages to show
      let startPage = Math.max(1, current - siblingsCount);
      let endPage = Math.min(total, current + siblingsCount);
      
      // Adjust for edge cases
      if (endPage - startPage + 1 < Math.min(displayed, total)) {
        if (current <= total / 2) {
          endPage = Math.min(total, startPage + displayed - 1);
        } else {
          startPage = Math.max(1, endPage - displayed + 1);
        }
      }
      
      // Always show first page
      if (showEnds && startPage > 1) {
        items.push({ type: 'page', value: 1 });
        
        // Add ellipsis if needed
        if (startPage > 2) {
          items.push({ type: 'ellipsis', value: 'start' });
        }
      }
      
      // Add page numbers
      for (let i = startPage; i <= endPage; i++) {
        items.push({ type: 'page', value: i });
      }
      
      // Always show last page
      if (showEnds && endPage < total) {
        // Add ellipsis if needed
        if (endPage < total - 1) {
          items.push({ type: 'ellipsis', value: 'end' });
        }
        
        items.push({ type: 'page', value: total });
      }
      
      return items;
    }
    
    // Handle page change
    function changePage(page) {
      if (page === currentPage || page < 1 || page > totalPages || disabled) return;
      
      currentPage = page;
      dispatch('change', { page });
    }
    
    // Handle page size change
    function changePageSize(event) {
      const newSize = parseInt(event.target.value);
      
      if (newSize !== pageSize) {
        pageSize = newSize;
        // Reset to first page when changing page size
        currentPage = 1;
        dispatch('pageSizeChange', { pageSize, page: 1 });
      }
    }
  </script>
  
  <div class="flex flex-col sm:flex-row items-center justify-between gap-4" dir={isRTL ? 'rtl' : 'ltr'}>
    {#if showItemCount}
      <div class={`text-neutral-500 dark:text-neutral-400 ${sizeClasses.text}`}>
        {itemCountText}
      </div>
    {/if}
    
    <div class="flex items-center">
      {#if showPageSize}
        <div class="flex items-center mr-4 rtl:mr-0 rtl:ml-4">
          <label for="page-size" class={`mr-2 rtl:mr-0 rtl:ml-2 ${sizeClasses.text} text-neutral-500 dark:text-neutral-400`}>
            {isRTL ? 'لكل صفحة:' : 'Per page:'}
          </label>
          <select
            id="page-size"
            class={`bg-white dark:bg-neutral-800 border border-neutral-300 dark:border-neutral-700 rounded-md ${sizeClasses.text} ${sizeClasses.item}`}
            value={pageSize.toString()}
            on:change={changePageSize}
            disabled={disabled}
          >
            {#each pageSizeOptions as option}
              <option value={option.toString()}>{option}</option>
            {/each}
          </select>
        </div>
      {/if}
      
      <nav class="relative z-0 inline-flex rounded-md shadow-sm">
        <!-- Previous page button -->
        <button
          type="button"
          class={`relative inline-flex items-center justify-center rounded-l-md border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-800 text-neutral-500 dark:text-neutral-400 hover:bg-neutral-50 dark:hover:bg-neutral-700 ${sizeClasses.item} ${sizeClasses.text}`}
          class:opacity-50={currentPage === 1 || disabled}
          class:cursor-not-allowed={currentPage === 1 || disabled}
          on:click={() => changePage(currentPage - 1)}
          disabled={currentPage === 1 || disabled}
          aria-label={isRTL ? 'الصفحة التالية' : 'Previous page'}
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
            <path fill-rule="evenodd" class:transform={isRTL} class:rotate-180={isRTL} d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" />
          </svg>
        </button>
        
        <!-- Page numbers -->
        {#if variant !== 'simple'}
          {#each pageItems as item}
            {#if item.type === 'page'}
              <button
                type="button"
                class={`relative inline-flex items-center justify-center border border-neutral-300 dark:border-neutral-700 ${sizeClasses.text} ${sizeClasses.item} ${currentPage === item.value ? 'z-10 bg-primary text-white border-primary' : 'bg-white dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300 hover:bg-neutral-50 dark:hover:bg-neutral-700'} -ml-px first:ml-0 rtl:-mr-px rtl:first:mr-0`}
                on:click={() => changePage(item.value)}
                aria-current={currentPage === item.value ? 'page' : undefined}
                disabled={disabled}
              >
                {item.value}
              </button>
            {:else if item.type === 'ellipsis'}
              <span class={`relative inline-flex items-center justify-center border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300 ${sizeClasses.text} ${sizeClasses.item} -ml-px rtl:-mr-px`}>
                &hellip;
              </span>
            {/if}
          {/each}
        {:else}
          <!-- Simple variant just shows current/total -->
          <span class={`relative inline-flex items-center justify-center border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300 ${sizeClasses.text} ${sizeClasses.item} -ml-px rtl:-mr-px`}>
            {currentPage} / {totalPages}
          </span>
        {/if}
        
        <!-- Next page button -->
        <button
          type="button"
          class={`relative inline-flex items-center justify-center rounded-r-md border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-800 text-neutral-500 dark:text-neutral-400 hover:bg-neutral-50 dark:hover:bg-neutral-700 ${sizeClasses.item} ${sizeClasses.text}`}
          class:opacity-50={currentPage === totalPages || disabled}
          class:cursor-not-allowed={currentPage === totalPages || disabled}
          on:click={() => changePage(currentPage + 1)}
          disabled={currentPage === totalPages || disabled}
          aria-label={isRTL ? 'الصفحة السابقة' : 'Next page'}
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
            <path fill-rule="evenodd" class:transform={isRTL} class:rotate-180={isRTL} d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
          </svg>
        </button>
      </nav>
    </div>
  </div>