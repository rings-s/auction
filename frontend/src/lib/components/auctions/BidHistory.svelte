<!-- src/lib/components/auctions/BidHistory.svelte -->
<script>
  import { format, formatDistance } from 'date-fns';
  import { ar } from 'date-fns/locale';
  import { formatCurrency, isRTL } from '$lib/i18n';
  import { authStore } from '$lib/stores/auth';
  
  // Components
  import Table from '$lib/components/ui/Table.svelte';
  import Badge from '$lib/components/ui/Badge.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Spinner from '$lib/components/ui/Spinner.svelte';
  
  // Props
  export let auctionId = null;
  export let bids = [];
  export let isLoading = false;
  export let pageCount = 1;
  export let currentPage = 1;
  export let onPageChange = (page) => {};
  export let onRefresh = () => {};
  export let winningBid = null;
  export let compact = false; // For compact view in smaller containers
  
  // Format date for display
  function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return format(date, 'dd MMM yyyy, HH:mm', { locale: isRTL() ? ar : undefined });
  }
  
  // Format time ago
  function timeAgo(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return formatDistance(date, new Date(), { addSuffix: true, locale: isRTL() ? ar : undefined });
  }
  
  // Check if user is the bidder
  function isCurrentUser(bidderId) {
    return $authStore?.user?.id === bidderId;
  }
  
  // Status colors for badges
  const bidStatusColors = {
    'winning': 'success',
    'outbid': 'warning',
    'pending': 'info',
    'rejected': 'error',
    'accepted': 'success',
    'cancelled': 'error'
  };
  
  // Generate pagination numbers
  $: paginationItems = generatePaginationItems(currentPage, pageCount);
  
  function generatePaginationItems(currentPage, pageCount) {
    const items = [];
    
    // If no pages, return empty array
    if (pageCount <= 0) return items;
    
    // Always include first page
    items.push(1);
    
    // Calculate range to show
    let rangeStart = Math.max(2, currentPage - 1);
    let rangeEnd = Math.min(pageCount - 1, currentPage + 1);
    
    // Add ellipsis if needed before range
    if (rangeStart > 2) {
      items.push('...');
    }
    
    // Add pages in range
    for (let i = rangeStart; i <= rangeEnd; i++) {
      items.push(i);
    }
    
    // Add ellipsis if needed after range
    if (rangeEnd < pageCount - 1) {
      items.push('...');
    }
    
    // Always include last page if more than one page
    if (pageCount > 1) {
      items.push(pageCount);
    }
    
    return items;
  }
</script>

<div class="bg-white dark:bg-neutral-800 rounded-xl shadow-sm border border-neutral-200 dark:border-neutral-700 overflow-hidden">
  <div class="flex justify-between items-center p-4 border-b border-neutral-200 dark:border-neutral-700">
    <h3 class="text-lg font-bold text-neutral-800 dark:text-neutral-200">
      {#if isRTL()}سجل المزايدات{:else}Bid History{/if}
    </h3>
    
    <Button 
      variant="ghost" 
      size="sm" 
      on:click={onRefresh}
      disabled={isLoading}
      class="flex items-center"
    >
      <svg 
        xmlns="http://www.w3.org/2000/svg" 
        class="h-4 w-4 {isRTL() ? 'ml-1' : 'mr-1'} {isLoading ? 'animate-spin' : ''}" 
        viewBox="0 0 20 20" 
        fill="currentColor"
      >
        <path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd" />
      </svg>
      {isRTL() ? 'تحديث' : 'Refresh'}
    </Button>
  </div>
  
  <div class={`${compact ? 'max-h-80' : 'max-h-96'} overflow-y-auto`}>
    {#if isLoading}
      <div class="flex justify-center items-center p-8">
        <Spinner size="md" />
      </div>
    {:else if bids.length === 0}
      <div class="text-center p-8 text-neutral-500 dark:text-neutral-400">
        <svg 
          xmlns="http://www.w3.org/2000/svg" 
          class="h-12 w-12 mx-auto text-neutral-400 dark:text-neutral-600 mb-4" 
          fill="none" 
          viewBox="0 0 24 24" 
          stroke="currentColor"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <p>{isRTL() ? 'لم يتم تقديم أي مزايدات بعد' : 'No bids have been placed yet'}</p>
        <p class="text-sm mt-2">
          {isRTL() ? 'كن أول من يقدم مزايدة على هذا العقار' : 'Be the first to bid on this property'}
        </p>
      </div>
    {:else}
      <table class="min-w-full divide-y divide-neutral-200 dark:divide-neutral-700">
        <thead class="bg-neutral-50 dark:bg-neutral-800">
          <tr>
            <th scope="col" class="px-4 py-3 text-left text-xs font-medium text-neutral-500 dark:text-neutral-400 uppercase tracking-wider">
              {isRTL() ? 'المزايد' : 'Bidder'}
            </th>
            <th scope="col" class="px-4 py-3 text-right text-xs font-medium text-neutral-500 dark:text-neutral-400 uppercase tracking-wider">
              {isRTL() ? 'قيمة المزايدة' : 'Bid Amount'}
            </th>
            <th scope="col" class="px-4 py-3 text-left text-xs font-medium text-neutral-500 dark:text-neutral-400 uppercase tracking-wider">
              {isRTL() ? 'وقت المزايدة' : 'Bid Time'}
            </th>
            <th scope="col" class="px-4 py-3 text-center text-xs font-medium text-neutral-500 dark:text-neutral-400 uppercase tracking-wider">
              {isRTL() ? 'الحالة' : 'Status'}
            </th>
          </tr>
        </thead>
        <tbody class="bg-white dark:bg-neutral-800 divide-y divide-neutral-200 dark:divide-neutral-700">
          {#each bids as bid}
            <tr class={winningBid && bid.id === winningBid.id ? 'bg-success-50 dark:bg-success-900/10' : ''}>
              <!-- Bidder -->
              <td class="px-4 py-3 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="flex-shrink-0 h-8 w-8 bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 rounded-full flex items-center justify-center mr-2">
                    <span class="text-sm font-bold">
                      {bid.bidder?.name?.charAt(0) || 'U'}
                    </span>
                  </div>
                  <div class={isCurrentUser(bid.bidder?.id) ? 'font-medium' : ''}>
                    {bid.bidder?.name || (isRTL() ? 'مزايد مجهول' : 'Anonymous Bidder')}
                    {#if isCurrentUser(bid.bidder?.id)}
                      <span class="ml-2 text-xs bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300 px-2 py-0.5 rounded-full">
                        {isRTL() ? 'أنت' : 'You'}
                      </span>
                    {/if}
                  </div>
                </div>
              </td>
              
              <!-- Bid Amount -->
              <td class="px-4 py-3 text-right whitespace-nowrap font-semibold text-neutral-800 dark:text-neutral-200">
                {formatCurrency(bid.bid_amount)}
              </td>
              
              <!-- Bid Time -->
              <td class="px-4 py-3 whitespace-nowrap">
                <div>
                  <div class="text-sm text-neutral-800 dark:text-neutral-200">
                    {formatDate(bid.bid_time)}
                  </div>
                  <div class="text-xs text-neutral-500 dark:text-neutral-400">
                    {timeAgo(bid.bid_time)}
                  </div>
                </div>
              </td>
              
              <!-- Status -->
              <td class="px-4 py-3 whitespace-nowrap text-center">
                <Badge 
                  text={bid.status === 'winning' ? (isRTL() ? 'فائز' : 'Winning') : 
                        bid.status === 'outbid' ? (isRTL() ? 'تم تجاوزه' : 'Outbid') :
                        bid.status === 'pending' ? (isRTL() ? 'قيد المعالجة' : 'Pending') :
                        bid.status === 'rejected' ? (isRTL() ? 'مرفوض' : 'Rejected') :
                        bid.status === 'accepted' ? (isRTL() ? 'مقبول' : 'Accepted') :
                        bid.status === 'cancelled' ? (isRTL() ? 'ملغي' : 'Cancelled') : bid.status}
                  color={bidStatusColors[bid.status] || 'neutral'}
                />
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    {/if}
  </div>
  
  <!-- Pagination -->
  {#if pageCount > 1 && !isLoading}
    <div class="border-t border-neutral-200 dark:border-neutral-700 px-4 py-3 flex items-center justify-between">
      <!-- Desktop pagination -->
      <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
        <div>
          <p class="text-sm text-neutral-700 dark:text-neutral-300">
            {isRTL() ? 
              `صفحة ${currentPage} من ${pageCount}` :
              `Page ${currentPage} of ${pageCount}`
            }
          </p>
        </div>
        <div>
          <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
            <!-- Previous page -->
            <button
              on:click={() => onPageChange(Math.max(1, currentPage - 1))}
              disabled={currentPage === 1}
              class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-800 text-sm font-medium text-neutral-500 dark:text-neutral-400 hover:bg-neutral-50 dark:hover:bg-neutral-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span class="sr-only">{isRTL() ? 'السابق' : 'Previous'}</span>
              <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" />
              </svg>
            </button>
            
            <!-- Page numbers -->
            {#each paginationItems as item}
              {#if item === '...'}
                <span class="relative inline-flex items-center px-4 py-2 border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-800 text-sm font-medium text-neutral-700 dark:text-neutral-300">
                  ...
                </span>
              {:else}
                <button
                  on:click={() => onPageChange(item)}
                  class={`relative inline-flex items-center px-4 py-2 border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-800 text-sm font-medium ${
                    currentPage === item 
                      ? 'z-10 bg-primary-50 dark:bg-primary-900/20 border-primary-500 dark:border-primary-500 text-primary-600 dark:text-primary-300' 
                      : 'text-neutral-700 dark:text-neutral-300 hover:bg-neutral-50 dark:hover:bg-neutral-700'
                  }`}
                  aria-current={currentPage === item ? 'page' : undefined}
                >
                  {item}
                </button>
              {/if}
            {/each}
            
            <!-- Next page -->
            <button
              on:click={() => onPageChange(Math.min(pageCount, currentPage + 1))}
              disabled={currentPage === pageCount}
              class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-800 text-sm font-medium text-neutral-500 dark:text-neutral-400 hover:bg-neutral-50 dark:hover:bg-neutral-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span class="sr-only">{isRTL() ? 'التالي' : 'Next'}</span>
              <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
              </svg>
            </button>
          </nav>
        </div>
      </div>
      
      <!-- Mobile pagination -->
      <div class="flex justify-between w-full sm:hidden">
        <button
          on:click={() => onPageChange(Math.max(1, currentPage - 1))}
          disabled={currentPage === 1}
          class="relative inline-flex items-center px-4 py-2 border border-neutral-300 dark:border-neutral-700 text-sm font-medium rounded-md bg-white dark:bg-neutral-800 
            {currentPage === 1 ? 'text-neutral-300 dark:text-neutral-600' : 'text-neutral-700 dark:text-neutral-300 hover:bg-neutral-50 dark:hover:bg-neutral-700'}"
        >
          {isRTL() ? 'السابق' : 'Previous'}
        </button>
        <span class="text-sm text-neutral-700 dark:text-neutral-300">
          {isRTL() ? 
            `صفحة ${currentPage} من ${pageCount}` :
            `Page ${currentPage} of ${pageCount}`
          }
        </span>
        <button
          on:click={() => onPageChange(Math.min(pageCount, currentPage + 1))}
          disabled={currentPage === pageCount}
          class="relative inline-flex items-center px-4 py-2 border border-neutral-300 dark:border-neutral-700 text-sm font-medium rounded-md bg-white dark:bg-neutral-800
            {currentPage === pageCount ? 'text-neutral-300 dark:text-neutral-600' : 'text-neutral-700 dark:text-neutral-300 hover:bg-neutral-50 dark:hover:bg-neutral-700'}"
        >
          {isRTL() ? 'التالي' : 'Next'}
        </button>
      </div>
    </div>
  {/if}
</div>