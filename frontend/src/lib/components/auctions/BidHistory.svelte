<script>
    import { format, formatDistance } from 'date-fns';
    import { ar } from 'date-fns/locale';
    import { formatCurrency } from '$lib/utils/formatters';
    import { authStore } from '$lib/stores/auth';
    
    // Components
    import Table from '$lib/components/ui/Table.svelte';
    import Badge from '$lib/components/ui/Badge.svelte';
    import Button from '$lib/components/ui/Button.svelte';
    import Loader from '$lib/components/ui/Loader.svelte';
    
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
      return format(date, 'dd MMM yyyy, HH:mm', { locale: ar });
    }
    
    // Format time ago
    function timeAgo(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return formatDistance(date, new Date(), { addSuffix: true, locale: ar });
    }
    
    // Check if user is the bidder
    function isCurrentUser(bidderId) {
      return $authStore.user?.id === bidderId;
    }
    
    // Generate table headers
    const headers = [
      { key: 'bidder', label: 'المزايد' },
      { key: 'bid_amount', label: 'قيمة المزايدة' },
      { key: 'bid_time', label: 'وقت المزايدة' },
      { key: 'status', label: 'الحالة' }
    ];
    
    // Generate rows from bids
    $: rows = bids.map(bid => ({
      id: bid.id,
      cells: [
        {
          key: 'bidder',
          value: bid.bidder?.name || 'مزايد مجهول',
          render: () => ({
            component: 'div',
            props: {
              class: `flex items-center ${isCurrentUser(bid.bidder?.id) ? 'font-semibold' : ''}`
            },
            children: [
              {
                component: 'div',
                props: {
                  class: 'flex-shrink-0 h-8 w-8 bg-primary-100 text-primary-700 rounded-full flex items-center justify-center mr-2'
                },
                children: [
                  {
                    component: 'span',
                    props: {
                      class: 'text-sm font-bold'
                    },
                    content: bid.bidder?.name?.charAt(0) || 'م'
                  }
                ]
              },
              {
                component: 'span',
                content: bid.bidder?.name || 'مزايد مجهول'
              },
              isCurrentUser(bid.bidder?.id) ? {
                component: 'span',
                props: {
                  class: 'mr-2 text-xs bg-primary-50 text-primary-700 px-2 py-0.5 rounded-full'
                },
                content: 'أنت'
              } : null
            ].filter(Boolean)
          })
        },
        {
          key: 'bid_amount',
          value: bid.bid_amount,
          render: () => ({
            component: 'span',
            props: {
              class: 'font-semibold'
            },
            content: formatCurrency(bid.bid_amount)
          })
        },
        {
          key: 'bid_time',
          value: new Date(bid.bid_time).getTime(),
          render: () => ({
            component: 'div',
            children: [
              {
                component: 'div',
                content: formatDate(bid.bid_time)
              },
              {
                component: 'div',
                props: {
                  class: 'text-xs text-gray-500'
                },
                content: timeAgo(bid.bid_time)
              }
            ]
          })
        },
        {
          key: 'status',
          value: bid.status,
          render: () => {
            const bidStatus = {
              'winning': {
                label: 'فائز',
                variant: 'success'
              },
              'outbid': {
                label: 'تم تجاوزه',
                variant: 'warning'
              },
              'pending': {
                label: 'قيد المعالجة',
                variant: 'primary'
              },
              'rejected': {
                label: 'مرفوض',
                variant: 'danger'
              },
              'accepted': {
                label: 'مقبول',
                variant: 'success'
              },
              'cancelled': {
                label: 'ملغي',
                variant: 'danger'
              }
            };
            
            const status = bidStatus[bid.status] || { label: bid.status, variant: 'gray' };
            
            return {
              component: Badge,
              props: {
                value: status.label,
                variant: status.variant,
                size: 'sm'
              }
            };
          }
        }
      ],
      isHighlighted: winningBid && bid.id === winningBid.id,
      highlightClass: 'bg-success-50'
    }));
  
    // Generate pagination numbers
    $: paginationItems = generatePaginationItems(currentPage, pageCount);
  
    function generatePaginationItems(currentPage, pageCount) {
      const items = [];
      
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
  
  <div class="bg-white rounded-lg shadow-card overflow-hidden">
    <div class="flex justify-between items-center p-4 border-b border-gray-200">
      <h3 class="text-lg font-bold text-gray-900">سجل المزايدات</h3>
      <Button 
        variant="ghost" 
        size="sm" 
        on:click={onRefresh}
        disabled={isLoading}
        class="flex items-center"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 ml-1 {isLoading ? 'animate-spin' : ''}" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd" />
        </svg>
        تحديث
      </Button>
    </div>
    
    <div class={`${compact ? 'max-h-80' : 'max-h-96'} overflow-y-auto`}>
      {#if isLoading}
        <div class="flex justify-center items-center p-8">
          <Loader size="md" />
        </div>
      {:else if bids.length === 0}
        <div class="text-center p-8 text-gray-500">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p>لم يتم تقديم أي مزايدات بعد</p>
          <p class="text-sm mt-2">كن أول من يقدم مزايدة على هذا العقار</p>
        </div>
      {:else}
        <Table {headers} {rows} compact={compact} />
      {/if}
    </div>
    
    {#if pageCount > 1 && !isLoading}
      <div class="border-t border-gray-200 px-4 py-3 flex items-center justify-between">
        <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
          <div>
            <p class="text-sm text-gray-700">
              صفحة <span class="font-medium">{currentPage}</span> من <span class="font-medium">{pageCount}</span>
            </p>
          </div>
          <div>
            <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
              <!-- Previous page -->
              <button
                on:click={() => onPageChange(Math.max(1, currentPage - 1))}
                disabled={currentPage === 1}
                class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 {currentPage === 1 ? 'opacity-50 cursor-not-allowed' : ''}"
              >
                <span class="sr-only">السابق</span>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
              </button>
              
              <!-- Page numbers -->
              {#each paginationItems as item}
                {#if item === '...'}
                  <span class="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700">
                    ...
                  </span>
                {:else}
                  <button
                    on:click={() => onPageChange(item)}
                    class="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium {currentPage === item ? 'z-10 bg-primary-50 border-primary-500 text-primary-600' : 'text-gray-700 hover:bg-gray-50'}"
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
                class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 {currentPage === pageCount ? 'opacity-50 cursor-not-allowed' : ''}"
              >
                <span class="sr-only">التالي</span>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
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
            class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md bg-white {currentPage === 1 ? 'text-gray-300' : 'text-gray-700 hover:bg-gray-50'}"
          >
            السابق
          </button>
          <span class="text-sm text-gray-700">
            صفحة <span class="font-medium">{currentPage}</span> من <span class="font-medium">{pageCount}</span>
          </span>
          <button
            on:click={() => onPageChange(Math.min(pageCount, currentPage + 1))}
            disabled={currentPage === pageCount}
            class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md bg-white {currentPage === pageCount ? 'text-gray-300' : 'text-gray-700 hover:bg-gray-50'}"
          >
            التالي
          </button>
        </div>
      </div>
    {/if}
  </div>