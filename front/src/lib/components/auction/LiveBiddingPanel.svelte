<!-- src/lib/components/auction/LiveBiddingPanel.svelte -->
<script>
    import { createEventDispatcher } from 'svelte';
    import { t } from '$lib/i18n/i18n';
    import Button from '$lib/components/ui/Button.svelte';
    import FormField from '$lib/components/ui/FormField.svelte';
    
    const dispatch = createEventDispatcher();
    
    export let auction;
    export let quickBidAmounts = [];
    export let minimumBidAmount = 0;
    export let placingBid = false;
    
    let customBidAmount = '';
    
    function formatCurrency(amount) {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
      }).format(amount);
    }
    
    function handleQuickBid(amount) {
      dispatch('placeBid', { amount });
    }
    
    function handleCustomBid() {
      const amount = parseFloat(customBidAmount);
      if (amount >= minimumBidAmount) {
        dispatch('placeBid', { amount });
        customBidAmount = '';
      }
    }
    
    function openBidModal() {
      dispatch('openModal');
    }
    
    $: currentBid = auction?.current_bid || auction?.starting_bid || 0;
  </script>
  
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md border-l-4 border-green-500" role="region" aria-labelledby="live-bidding-title">
    <div class="p-6">
      <h2 id="live-bidding-title" class="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
        <span class="w-3 h-3 bg-green-500 rounded-full mr-2 animate-pulse" aria-hidden="true"></span>
        {$t('auction.liveBidding')}
      </h2>
      
      <!-- Current Bid Display -->
      <div class="mb-6 p-4 bg-gradient-to-r from-green-50 to-primary-50 dark:from-green-900/20 dark:to-primary-900/20 rounded-lg border border-green-200 dark:border-green-800">
        <div class="flex justify-between items-center mb-2">
          <span class="text-sm font-medium text-green-700 dark:text-green-300">
            {$t('auction.currentBid')}
          </span>
          <span class="text-2xl font-bold text-green-600 dark:text-green-400" aria-live="polite">
            {formatCurrency(currentBid)}
          </span>
        </div>
        <div class="flex justify-between items-center">
          <span class="text-xs text-green-600 dark:text-green-400">
            {$t('auction.minimumBid')}:
          </span>
          <span class="text-sm font-medium text-green-700 dark:text-green-300">
            {formatCurrency(minimumBidAmount)}
          </span>
        </div>
      </div>
      
      <!-- Quick Bid Buttons -->
      <div class="mb-4">
        <h3 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          {$t('auction.quickBids')}
        </h3>
        
        <div class="grid grid-cols-2 gap-2">
          {#each quickBidAmounts as { amount, label }}
            <Button
              variant="outline"
              size="small"
              loading={placingBid}
              disabled={placingBid}
              onClick={() => handleQuickBid(amount)}
              class="text-xs font-medium hover:bg-green-50 hover:border-green-500 hover:text-green-700 dark:hover:bg-green-900/20 transition-colors"
              aria-label={$t('auction.quickBidFor', { amount: formatCurrency(amount) })}
            >
              <div class="flex flex-col items-center">
                <span class="font-semibold">{formatCurrency(amount)}</span>
                <span class="text-xs opacity-75">{label}</span>
              </div>
            </Button>
          {/each}
        </div>
      </div>
      
      <!-- Custom Bid Form -->
      <form on:submit|preventDefault={handleCustomBid} class="mb-4">
        <div class="flex gap-2">
          <div class="flex-1">
            <FormField
              type="number"
              id="custom-bid-amount"
              placeholder={minimumBidAmount.toString()}
              bind:value={customBidAmount}
              min={minimumBidAmount}
              step="1"
              disabled={placingBid}
              class="text-sm"
              aria-label={$t('auction.enterCustomBid')}
            />
          </div>
          <Button
            type="submit"
            variant="primary"
            loading={placingBid}
            disabled={placingBid || !customBidAmount || parseFloat(customBidAmount) < minimumBidAmount}
            class="px-4 py-2 text-sm font-medium"
            aria-label={$t('auction.submitCustomBid')}
          >
            {#if placingBid}
              <svg class="animate-spin -ml-1 mr-1 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" aria-hidden="true">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            {/if}
            {$t('auction.bid')}
          </Button>
        </div>
      </form>
      
      <!-- Alternative Bid Modal Button -->
      <Button
        variant="secondary"
        onClick={openBidModal}
        class="w-full text-sm"
        aria-label={$t('auction.openAdvancedBidding')}
      >
        {$t('auction.advancedBidding')}
      </Button>
      
      <!-- Bidding Tips -->
      <div class="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
        <h4 class="text-xs font-medium text-blue-800 dark:text-blue-200 mb-1">
          {$t('auction.biddingTips')}
        </h4>
        <ul class="text-xs text-blue-700 dark:text-blue-300 space-y-1">
          <li>• {$t('auction.tip1')}</li>
          <li>• {$t('auction.tip2')}</li>
          <li>• {$t('auction.tip3')}</li>
        </ul>
      </div>
    </div>
  </div>