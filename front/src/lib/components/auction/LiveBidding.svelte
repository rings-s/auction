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
      
      // Reset bid amount
      bidAmount = minimumBidAmount.toString();
      
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

<div class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
  <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">
    {$t('auction.liveBidding')}
  </h2>
  
  {#if error}
    <Alert type="error" message={error} class="mb-4" />
  {/if}
  
  {#if success}
    <Alert type="success" message={success} class="mb-4" />
  {/if}
  
  <div class="mb-6">
    <div class="flex justify-between items-baseline mb-3">
      <h3 class="text-sm font-medium text-gray-700 dark:text-gray-300">
        {$t('auction.currentBid')}
      </h3>
      <span class="text-2xl font-bold text-primary-600 dark:text-primary-400">
        ${(auction?.current_bid || auction?.starting_bid).toLocaleString()}
      </span>
    </div>
    
    <p class="text-sm text-gray-500 dark:text-gray-400 mb-4">
      {$t('auction.minimumBid')}: ${minimumBidAmount.toLocaleString()}
    </p>
    
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
        />
        
        <Button
          type="submit"
          variant="primary"
          loading={submitting}
          disabled={submitting}
          class="w-full"
        >
          {$t('auction.placeBid')}
        </Button>
      </form>
    {:else if !$user}
      <Button
        variant="primary"
        href={`/login?redirect=/auctions/${auction.slug || auction.id}`}
        class="w-full"
      >
        {$t('auction.loginToBid')}
      </Button>
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
  
  <!-- Bid History -->
  <div class="border-t border-gray-200 dark:border-gray-700 pt-4">
    <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-3">
      {$t('auction.bidHistory')}
      <span class="text-sm font-normal text-gray-500 dark:text-gray-400 ml-2">
        ({bids.length} {$t('auction.bids')})
      </span>
    </h3>
    
    {#if loading}
      <div class="py-4 text-center">
        <div class="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-primary-500"></div>
        <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">
          {$t('common.loading')}
        </p>
      </div>
    {:else if bids.length === 0}
      <div class="text-center py-6 bg-gray-50 dark:bg-gray-700 rounded-lg">
        <p class="text-gray-500 dark:text-gray-400">
          {$t('auction.noBidsYet')}
        </p>
      </div>
    {:else}
      <ul class="divide-y divide-gray-200 dark:divide-gray-700">
        {#each bids as bid}
          <li class="py-3 flex justify-between items-center">
            <div>
              <p class="text-sm font-medium text-gray-900 dark:text-white">
                ${parseFloat(bid.bid_amount).toLocaleString()}
              </p>
              <p class="text-xs text-gray-500 dark:text-gray-400">
                {formatDateTime(bid.bid_time)}
              </p>
            </div>
            <div class="flex items-center space-x-3">
              <span class="text-sm text-gray-700 dark:text-gray-300">
                {bid.bidder_info?.name || 'Anonymous'}
                {#if $user && bid.bidder_info?.id === $user.id}
                  <span class="text-xs text-primary-600 dark:text-primary-400 ml-1">
                    ({$t('auction.you')})
                  </span>
                {/if}
              </span>
              <AuctionStatus status={bid.status} isCompact={true} />
            </div>
          </li>
        {/each}
      </ul>
      
      {#if bids.length > 5}
        <div class="mt-4 text-center">
          <Button
            variant="outline"
            size="small"
            onClick={() => loadBids()}
          >
            {$t('auction.refreshBids')}
          </Button>
        </div>
      {/if}
    {/if}
  </div>
</div>