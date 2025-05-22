<!-- src/lib/components/auction/LiveBiddingPanel.svelte -->
<script>
  import { createEventDispatcher } from 'svelte';
  import { t } from '$lib/i18n/i18n';
  import { user } from '$lib/stores/user';
  import Button from '$lib/components/ui/Button.svelte';
  import FormField from '$lib/components/ui/FormField.svelte';
  import Alert from '$lib/components/ui/Alert.svelte';
  
  const dispatch = createEventDispatcher();
  
  export let auction;
  export let quickBidAmounts = [];
  export let minimumBidAmount = 0;
  export let placingBid = false;
  
  let customBidAmount = '';
  let bidError = '';
  
  $: canBid = auction?.status === 'live' && $user && new Date(auction?.end_date) > new Date();
  
  function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  }
  
  function handleQuickBid(amount) {
    if (placingBid) return;
    
    bidError = '';
    dispatch('placeBid', { amount });
  }
  
  function handleCustomBid() {
    if (placingBid) return;
    
    const amount = parseFloat(customBidAmount);
    
    if (isNaN(amount) || amount < minimumBidAmount) {
      bidError = $t('auction.bidTooLow', { amount: minimumBidAmount.toLocaleString() });
      return;
    }
    
    bidError = '';
    dispatch('placeBid', { amount });
    customBidAmount = '';
  }
  
  function openBidModal() {
    dispatch('openModal');
  }
  
  $: currentBid = auction?.current_bid || auction?.starting_bid || 0;
</script>

{#if canBid}
<div class="bg-white dark:bg-gray-800 rounded-lg shadow-md border-l-4 border-green-500" role="region" aria-labelledby="live-bidding-title">
  <div class="p-6">
    <h2 id="live-bidding-title" class="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
      <span class="w-3 h-3 bg-green-500 rounded-full mr-2 animate-pulse" aria-hidden="true"></span>
      {$t('auction.liveBidding')}
    </h2>
    
    {#if bidError}
      <Alert type="error" message={bidError} class="mb-4" dismissible={true} />
    {/if}
    
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
    {#if quickBidAmounts && quickBidAmounts.length > 0}
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
    {/if}
    
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
      class="w-full text-sm mb-4"
      disabled={placingBid}
      aria-label={$t('auction.openAdvancedBidding')}
    >
      {$t('auction.advancedBidding')}
    </Button>
    
    <!-- Bidding Tips -->
    <div class="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
      <h4 class="text-xs font-medium text-blue-800 dark:text-blue-200 mb-1">
        {$t('auction.biddingTips')}
      </h4>
      <ul class="text-xs text-blue-700 dark:text-blue-300 space-y-1">
        <li>• Bids are binding and cannot be retracted</li>
        <li>• You will be notified if you are outbid</li>
        <li>• The auction may extend if bids are placed in the final minutes</li>
      </ul>
    </div>
  </div>
</div>
{:else if !$user}
<!-- Login prompt for non-authenticated users -->
<div class="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-6 text-center">
  <div class="flex items-center justify-center mb-4">
    <svg class="w-8 h-8 text-yellow-600 dark:text-yellow-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
    </svg>
  </div>
  <h3 class="text-lg font-semibold text-yellow-800 dark:text-yellow-200 mb-2">
    {$t('auction.loginToBid')}
  </h3>
  <p class="text-yellow-700 dark:text-yellow-300 mb-4">
    {$t('auction.loginToBidMessage')}
  </p>
  <Button
    variant="primary"
    href={`/login?redirect=/auctions/${auction.slug || auction.id}`}
  >
    {$t('nav.login')}
  </Button>
</div>
{:else}
<!-- Auction not active for bidding -->
<div class="bg-gray-100 dark:bg-gray-700 rounded-lg p-6 text-center">
  <svg class="w-12 h-12 mx-auto text-gray-400 dark:text-gray-500 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
  <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
    {auction?.status === 'scheduled' ? $t('auction.auctionNotStarted') : $t('auction.biddingNotActive')}
  </h3>
  <p class="text-gray-500 dark:text-gray-400">
    {auction?.status === 'scheduled' 
      ? $t('auction.auctionWillStart') 
      : auction?.status === 'ended' 
        ? $t('auction.auctionHasEnded') 
        : $t('auction.biddingCurrentlyUnavailable')}
  </p>
</div>
{/if}