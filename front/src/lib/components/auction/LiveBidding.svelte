<!-- src/lib/components/auction/LiveBidding.svelte -->
<script>
  import { onMount, onDestroy } from 'svelte';
  import { user } from '$lib/stores/user';
  import { t } from '$lib/i18n/i18n';
  import { fetchAuctionBids, placeBid } from '$lib/api/auction';
  import Button from '$lib/components/ui/Button.svelte';
  import FormField from '$lib/components/ui/FormField.svelte';
  import Alert from '$lib/components/ui/Alert.svelte';
  import AuctionStatus from './AuctionStatus.svelte';
  
  export let auction;
  export let onBidPlaced = () => {};
  
  let bidAmount = '';
  let bids = [];
  let loading = true;
  let submitting = false;
  let error = '';
  let success = '';
  let refreshInterval;
  
  $: minimumBidAmount = calculateMinimumBid();
  $: canBid = auction?.status === 'live' && $user && auction?.end_date > new Date().toISOString();
  
  function calculateMinimumBid() {
    if (!auction) return 0;
    
    // If there's a current bid, the minimum is current bid + increment
    if (auction.current_bid) {
      return parseFloat(auction.current_bid) + parseFloat(auction.minimum_increment);
    }
    
    // Otherwise, use the starting bid
    return parseFloat(auction.starting_bid);
  }
  
  async function loadBids() {
    try {
      loading = true;
      
      if (!auction || !auction.id) return;
      
      const response = await fetchAuctionBids(auction.id);
      
      // Sort bids by bid_time (newest first)
      bids = (response.results || response).sort((a, b) => {
        return new Date(b.bid_time) - new Date(a.bid_time);
      });
      
    } catch (err) {
      console.error('Error loading bids:', err);
      error = err.message || $t('error.loadingBids');
    } finally {
      loading = false;
    }
  }
  
  async function handlePlaceBid() {
    try {
      error = '';
      success = '';
      submitting = true;
      
      // Validate bid amount
      const amount = parseFloat(bidAmount);
      if (isNaN(amount) || amount < minimumBidAmount) {
        error = $t('auction.bidTooLow', { amount: minimumBidAmount.toLocaleString() });
        return;
      }
      
      // Submit bid
      await placeBid(auction.id, amount);
      
      // Show success message
      success = $t('auction.bidPlaced');
      
      // Reset bid amount to new minimum
      bidAmount = calculateMinimumBid().toString();
      
      // Refresh bids
      await loadBids();
      
      // Notify parent component
      onBidPlaced();
      
    } catch (err) {
      console.error('Error placing bid:', err);
      error = err.message || $t('error.bidFailed');
    } finally {
      submitting = false;
    }
  }
  
  function formatDateTime(dateString) {
    try {
      const date = new Date(dateString);
      return new Intl.DateTimeFormat('default', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      }).format(date);
    } catch (e) {
      return dateString;
    }
  }
  
  function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  }
  
  onMount(() => {
    // Initialize bid amount to minimum
    bidAmount = minimumBidAmount.toString();
    
    // Load initial bids
    loadBids();
    
    // Set up refresh interval for live auctions
    if (auction?.status === 'live') {
      refreshInterval = setInterval(() => {
        if (!submitting) {
          loadBids();
        }
      }, 10000); // Refresh every 10 seconds
    }
  });
  
  onDestroy(() => {
    if (refreshInterval) {
      clearInterval(refreshInterval);
    }
  });
</script>

<div class="space-y-6">
  <!-- Bidding Form for Authenticated Users -->
  {#if $user}
    <div class="bg-gradient-to-r from-primary-50 to-blue-50 dark:from-primary-900/20 dark:to-blue-900/20 rounded-lg p-6 border border-primary-200 dark:border-primary-800">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
        <svg class="w-5 h-5 mr-2 text-primary-600 dark:text-primary-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        {$t('auction.placeBid')}
      </h3>
      
      {#if error}
        <Alert type="error" message={error} class="mb-4" />
      {/if}
      
      {#if success}
        <Alert type="success" message={success} class="mb-4" />
      {/if}
      
      <div class="mb-4 p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
        <div class="flex justify-between items-center mb-2">
          <span class="text-sm font-medium text-gray-700 dark:text-gray-300">
            {$t('auction.currentBid')}:
          </span>
          <span class="text-xl font-bold text-primary-600 dark:text-primary-400">
            {formatCurrency(auction?.current_bid || auction?.starting_bid)}
          </span>
        </div>
        <div class="flex justify-between items-center">
          <span class="text-sm text-gray-500 dark:text-gray-400">
            {$t('auction.minimumBid')}:
          </span>
          <span class="text-lg font-semibold text-gray-900 dark:text-white">
            {formatCurrency(minimumBidAmount)}
          </span>
        </div>
      </div>
      
      {#if canBid}
        <form on:submit|preventDefault={handlePlaceBid} class="space-y-4">
          <FormField
            type="currency"
            id="bid_amount"
            label={$t('auction.yourBid')}
            bind:value={bidAmount}
            currencySymbol="$"
            min={minimumBidAmount}
            required={true}
            disabled={submitting}
            helpText={$t('auction.enterBidAmount')}
          />
          
          <Button
            type="submit"
            variant="primary"
            size="large"
            loading={submitting}
            disabled={submitting}
            class="w-full"
          >
            {#if submitting}
              <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            {/if}
            {$t('auction.placeBid')}
          </Button>
        </form>
      {:else if !$user}
        <div class="text-center py-4">
          <p class="text-gray-700 dark:text-gray-300 mb-4">
            {$t('auction.loginToBidMessage')}
          </p>
          <Button
            variant="primary"
            href={`/login?redirect=/auctions/${auction.slug || auction.id}`}
          >
            {$t('auction.loginToBid')}
          </Button>
        </div>
      {:else if auction?.status !== 'live'}
        <div class="bg-gray-100 dark:bg-gray-700 p-4 rounded-lg text-center">
          <p class="text-gray-700 dark:text-gray-300">
            {$t('auction.biddingNotActive')}
          </p>
        </div>
      {:else}
        <div class="bg-gray-100 dark:bg-gray-700 p-4 rounded-lg text-center">
          <p class="text-gray-700 dark:text-gray-300">
            {$t('auction.auctionEnded')}
          </p>
        </div>
      {/if}
    </div>
  {:else}
    <!-- Login Prompt for Anonymous Users -->
    <div class="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-6 text-center">
      <div class="flex items-center justify-center mb-4">
        <svg class="w-8 h-8 text-yellow-600 dark:text-yellow-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      </div>
      <h3 class="text-lg font-semibold text-yellow-800 dark:text-yellow-200 mb-2">
        {$t('auction.loginRequired')}
      </h3>
      <p class="text-yellow-700 dark:text-yellow-300 mb-4">
        {$t('auction.loginRequiredMessage')}
      </p>
      <Button
        variant="primary"
        href={`/login?redirect=/auctions/${auction.slug || auction.id}`}
      >
        {$t('nav.login')}
      </Button>
    </div>
  {/if}
  
  <!-- Bid History -->
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
    <div class="flex justify-between items-center mb-6">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
        {$t('auction.bidHistory')}
        <span class="text-sm font-normal text-gray-500 dark:text-gray-400 ml-2">
          ({bids.length} {$t('auction.bids')})
        </span>
      </h3>
      
      <Button
        variant="outline"
        size="small"
        loading={loading}
        onClick={loadBids}
        aria-label={$t('auction.refreshBids')}
      >
        <svg class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        {$t('auction.refresh')}
      </Button>
    </div>
    
    {#if loading}
      <div class="py-8 text-center">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
        <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">
          {$t('common.loading')}
        </p>
      </div>
    {:else if bids.length === 0}
      <div class="text-center py-12 bg-gray-50 dark:bg-gray-700 rounded-lg">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-gray-400 dark:text-gray-500 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
          {$t('auction.noBidsYet')}
        </h3>
        <p class="text-gray-500 dark:text-gray-400 mb-6">
          {$t('auction.beTheFirst')}
        </p>
        
        {#if canBid}
          <p class="text-sm text-gray-600 dark:text-gray-400">
            {$t('auction.useFormAbove')}
          </p>
        {/if}
      </div>
    {:else}
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                {$t('auction.bidder')}
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                {$t('auction.bidAmount')}
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                {$t('auction.bidTime')}
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                {$t('auction.status')}
              </th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            {#each bids as bid}
              <tr class={bid.bidder_info?.id === $user?.id ? 'bg-primary-50 dark:bg-primary-900/20' : ''}>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                  {bid.bidder_info?.name || 'Anonymous'}
                  {#if bid.bidder_info?.id === $user?.id}
                    <span class="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800 dark:bg-primary-900 dark:text-primary-200">
                      {$t('auction.you')}
                    </span>
                  {/if}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700 dark:text-gray-300">
                  <span class="font-medium text-lg">
                    {formatCurrency(bid.bid_amount || bid.amount)}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                  {formatDateTime(bid.bid_time)}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <AuctionStatus status={bid.status} isCompact={true} />
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {/if}
  </div>
</div>