<!-- src/lib/components/auction/QuickBidPopover.svelte -->
<script>
    import { createEventDispatcher } from 'svelte';
    import { t } from '$lib/i18n';
    import { user } from '$lib/stores/user';
    import { placeBid } from '$lib/api/auction';
    import Button from '$lib/components/ui/Button.svelte';
    
    export let auction;
    export let show = false;
    
    const dispatch = createEventDispatcher();
    
    let bidAmount = '';
    let submitting = false;
    let error = '';
    
    $: minimumBid = (auction?.current_bid || auction?.starting_bid || 0) + (auction?.minimum_increment || 100);
    $: quickBidOptions = [
      minimumBid,
      minimumBid + 100,
      minimumBid + 500,
      minimumBid + 1000
    ];
    
    async function handleQuickBid(amount) {
      if (!$user) {
        window.location.href = `/login?redirect=/auctions/${auction.slug}`;
        return;
      }
      
      try {
        submitting = true;
        error = '';
        
        await placeBid(auction.id, amount);
        dispatch('bidPlaced', { amount });
        close();
        
      } catch (err) {
        error = err.message || 'Failed to place bid';
      } finally {
        submitting = false;
      }
    }
    
    function close() {
      show = false;
      error = '';
      bidAmount = '';
      dispatch('close');
    }
    
    function handleBackdropClick(e) {
      if (e.target === e.currentTarget) {
        close();
      }
    }
  </script>
  
  {#if show}
    <div 
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50"
      on:click={handleBackdropClick}
    >
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-md w-full p-6 transform transition-all">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-bold text-gray-900 dark:text-white">
            Quick Bid - {auction.title}
          </h3>
          <button
            on:click={close}
            class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          >
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        {#if error}
          <div class="mb-4 p-3 bg-red-50 dark:bg-red-900/20 rounded-lg text-sm text-red-700 dark:text-red-300">
            {error}
          </div>
        {/if}
        
        <div class="mb-4">
          <p class="text-sm text-gray-600 dark:text-gray-400 mb-1">Current Bid</p>
          <p class="text-2xl font-bold text-gray-900 dark:text-white">
            ${(auction.current_bid || auction.starting_bid || 0).toLocaleString()}
          </p>
        </div>
        
        <div class="space-y-2 mb-4">
          <p class="text-sm font-medium text-gray-700 dark:text-gray-300">Select bid amount:</p>
          <div class="grid grid-cols-2 gap-2">
            {#each quickBidOptions as amount}
              <button
                on:click={() => handleQuickBid(amount)}
                disabled={submitting}
                class="p-3 border border-gray-300 dark:border-gray-600 rounded-lg hover:border-primary-500 hover:bg-primary-50 dark:hover:bg-primary-900/20 transition-colors text-center disabled:opacity-50"
              >
                <span class="block text-lg font-bold text-gray-900 dark:text-white">
                  ${amount.toLocaleString()}
                </span>
              </button>
            {/each}
          </div>
        </div>
        
        <div class="pt-4 border-t border-gray-200 dark:border-gray-700">
          <Button
            variant="primary"
            href={`/auctions/${auction.slug}`}
            class="w-full"
          >
            View Full Auction
          </Button>
        </div>
      </div>
    </div>
  {/if}