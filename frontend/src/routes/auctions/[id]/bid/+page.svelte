<!-- src/routes/auctions/[id]/bid/+page.svelte -->
<script>
  import { onMount, onDestroy } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { isAuthenticated, user } from '$lib/stores/authStore';
  import { auctionStore } from '$lib/stores/auctionStore';
  import { bidStore } from '$lib/stores/bidStore';
  import { notificationStore } from '$lib/stores/notificationStore';
  import { createAuctionConnection } from '$lib/websocketService';
  import Button from '$lib/components/ui/Button.svelte';
  import Spinner from '$lib/components/ui/Spinner.svelte';
  import Alert from '$lib/components/ui/Alert.svelte';
  import AuctionTimer from '$lib/components/auction/AuctionTimer.svelte';
  import { formatDate, formatCurrency } from '$lib/utils/formatters';
  
  // Get auction ID from URL
  $: auctionId = $page.params.id;
  
  // Reactive state
  $: auction = $auctionStore.currentAuction;
  $: loading = $auctionStore.loading.details;
  $: error = $auctionStore.error;
  $: currentUser = $user;
  $: auctionEnded = isAuctionEnded(auction);
  
  // Form state
  let bidAmount = 0;
  let autoBidEnabled = false;
  let autoBidLimit = 0;
  let submitting = false;
  let formError = '';
  let formSuccess = '';
  
  // WebSocket connection for real-time updates
  let connection = null;
  let liveUpdates = [];
  let connectionStatus = 'disconnected';
  let recentBids = [];
  
  // Helper function to check if auction has ended
  function isAuctionEnded(auction) {
    if (!auction || !auction.end_time) return true;
    
    const now = new Date();
    const end = new Date(auction.end_time);
    return now >= end || auction.status !== 'ACTIVE';
  }
  
  // Calculate minimum bid amount based on current price
  $: minimumBid = calculateMinimumBid(auction);
  
  function calculateMinimumBid(auction) {
    if (!auction) return 0;
    
    const currentPrice = parseFloat(auction.current_price) || 0;
    const increment = parseFloat(auction.minimum_bid_increment) || 1;
    
    return currentPrice + increment;
  }
  
  // Update bid amount when minimum bid changes
  $: if (minimumBid > 0 && (!bidAmount || bidAmount < minimumBid)) {
    bidAmount = minimumBid;
    
    // Also update auto-bid limit if it's too low
    if (autoBidEnabled && autoBidLimit < bidAmount) {
      autoBidLimit = bidAmount + (auction?.minimum_bid_increment || 1) * 5;
    }
  }
  
  // Handle form submission
  async function submitBid() {
    // Reset status
    formError = '';
    formSuccess = '';
    
    // Validate form
    if (!$isAuthenticated) {
      formError = 'You must be logged in to place a bid';
      return;
    }
    
    if (auctionEnded) {
      formError = 'This auction has ended';
      return;
    }
    
    if (auction?.seller === $user?.id) {
      formError = 'You cannot bid on your own auction';
      return;
    }
    
    if (!bidAmount || bidAmount < minimumBid) {
      formError = `Bid amount must be at least ${formatCurrency(minimumBid, auction.currency)}`;
      return;
    }
    
    if (autoBidEnabled && (!autoBidLimit || autoBidLimit < bidAmount)) {
      formError = 'Auto-bid limit must be greater than or equal to your bid amount';
      return;
    }
    
    // Submit bid
    submitting = true;
    
    try {
      // Prepare bid data
      const bidData = {
        amount: bidAmount,
        auto_bid_limit: autoBidEnabled ? autoBidLimit : null
      };
      
      // Use the bidStore to place the bid
      await bidStore.placeBid(auctionId, bidAmount, autoBidEnabled ? autoBidLimit : null);
      
      // Success!
      formSuccess = `Your bid of ${formatCurrency(bidAmount, auction.currency)} was placed successfully!`;
      notificationStore.success(formSuccess);
      
      // Reload auction data to get updated price
      auctionStore.loadAuctionDetails(auctionId);
      
      // Reset form
      bidAmount = minimumBid;
      if (autoBidEnabled) {
        autoBidLimit = minimumBid + (auction?.minimum_bid_increment || 1) * 5;
      }
    } catch (err) {
      console.error('Error placing bid:', err);
      formError = err.error || 'Failed to place bid';
      notificationStore.error(formError);
    } finally {
      submitting = false;
    }
  }
  
  // Load auction data and initialize WebSocket connection
  onMount(async () => {
    if (!$isAuthenticated) {
      // Redirect to login if not authenticated
      notificationStore.info('Please log in to place a bid');
      goto('/login?redirect=' + encodeURIComponent('/auctions/' + auctionId + '/bid'));
      return;
    }
    
    if (auctionId) {
      try {
        // Load auction details
        await auctionStore.loadAuctionDetails(auctionId);
        
        // Set initial bid amount
        bidAmount = minimumBid;
        autoBidLimit = minimumBid + (auction?.minimum_bid_increment || 1) * 5;
        
        // Initialize WebSocket connection for real-time updates
        connection = createAuctionConnection(auctionId);
        
        // Subscribe to auction updates
        const unsubscribeUpdates = connection.updates.subscribe(updates => {
          liveUpdates = updates;
          
          // Process updates
          if (updates.length > 0) {
            // Handle specific updates like price changes
            const latestUpdate = updates[0];
            if (latestUpdate.action === 'price_update') {
              notificationStore.info(`The price has been updated to ${formatCurrency(latestUpdate.data.price)}`);
              // Refresh auction details to get the latest state
              auctionStore.loadAuctionDetails(auctionId);
            } else if (latestUpdate.action === 'timer_extended') {
              notificationStore.info(`Auction time has been extended by ${latestUpdate.data.minutes} minutes`);
              // Refresh auction details to get the latest state
              auctionStore.loadAuctionDetails(auctionId);
            }
          }
        });
        
        // Subscribe to connection status
        const unsubscribeStatus = connection.status.subscribe(status => {
          connectionStatus = status;
        });
        
        // Subscribe to bids
        const unsubscribeBids = connection.bids.subscribe(bids => {
          recentBids = bids;
        });
        
        // Clean up on unmount
        return () => {
          unsubscribeUpdates();
          unsubscribeStatus();
          unsubscribeBids();
        };
      } catch (err) {
        console.error('Error loading auction details:', err);
      }
    }
  });
  
  // Clean up WebSocket connection
  onDestroy(() => {
    if (connection) {
      connection.close();
    }
  });
</script>

<svelte:head>
  <title>Place Bid | {auction ? auction.title : 'Auction'} | GUDIC</title>
  <meta name="description" content="Place a bid on this auction" />
</svelte:head>

<div class="max-w-4xl mx-auto px-4 sm:px-6 py-8">
  <!-- Loading state -->
  {#if loading}
    <div class="flex justify-center items-center py-12">
      <Spinner size="lg" />
    </div>
  <!-- Error state -->
  {:else if error}
    <div class="bg-red-50 p-4 rounded-md text-red-600 mb-8">
      <p class="text-center">{error}</p>
      <div class="flex justify-center mt-4">
        <Button 
          variant="primary" 
          size="sm"
          on:click={() => {
            auctionStore.clearError();
            auctionStore.loadAuctionDetails(auctionId);
          }}
        >
          Try Again
        </Button>
      </div>
    </div>
  <!-- Content state -->
  {:else if auction}
    <!-- Auction Header -->
    <div class="mb-6">
      <div class="flex items-center justify-between">
        <h1 class="text-2xl font-bold text-text-dark">Place a Bid</h1>
        
        <Button 
          href={`/auctions/${auctionId}`} 
          variant="outline"
          size="sm"
        >
          Back to Auction
        </Button>
      </div>
    </div>
    
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- Auction Details -->
      <div class="space-y-6">
        <!-- Auction Card -->
        <div class="bg-white rounded-lg border border-primary-blue/20 overflow-hidden">
          <div class="p-5">
            <!-- Auction title -->
            <h2 class="font-semibold text-lg text-text-dark mb-2">
              {auction.title}
            </h2>
            
            <!-- Current price -->
            <div class="flex justify-between items-center mb-4">
              <div class="text-sm font-medium text-text-medium">Current Price</div>
              <div class="text-2xl font-bold text-secondary-blue">
                {formatCurrency(auction.current_price, auction.currency)}
              </div>
            </div>
            
            <!-- Auction timer -->
            <AuctionTimer auction={auction} accent={true} />
            
            <!-- Bid details -->
            <div class="mt-4 pt-4 border-t border-primary-blue/10">
              <div class="flex justify-between text-sm">
                <span class="text-text-medium">Minimum bid increment</span>
                <span class="font-medium">{formatCurrency(auction.minimum_bid_increment, auction.currency)}</span>
              </div>
              
              <div class="flex justify-between text-sm mt-1">
                <span class="text-text-medium">Minimum next bid</span>
                <span class="font-medium">{formatCurrency(minimumBid, auction.currency)}</span>
              </div>
              
              <div class="flex justify-between text-sm mt-1">
                <span class="text-text-medium">Total bids</span>
                <span class="font-medium">{auction.total_bids || 0}</span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Recent Bids -->
        <div class="bg-white rounded-lg border border-primary-blue/20 overflow-hidden">
          <div class="px-5 py-4 border-b border-primary-blue/10 bg-gradient-to-r from-primary-blue/5 to-primary-peach/5">
            <div class="flex items-center justify-between">
              <h3 class="text-lg font-medium text-text-dark">Recent Bids</h3>
              {#if connectionStatus === 'connected'}
                <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                  <span class="h-2 w-2 mr-1 bg-green-400 rounded-full animate-pulse"></span>
                  Live
                </span>
              {/if}
            </div>
          </div>
          
          <div class="overflow-y-auto max-h-60">
            {#if recentBids.length > 0}
              <ul class="divide-y divide-primary-blue/10">
                {#each recentBids as bid}
                  <li class="p-4 text-sm">
                    <div class="flex items-start">
                      <div class="text-secondary-blue flex-shrink-0 mt-0.5">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                          <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd" />
                        </svg>
                      </div>
                      
                      <div class="ml-3 flex-1">
                        <div class="flex justify-between">
                          <span class="font-medium text-text-dark">
                            {bid.bidder_details?.first_name || 'Anonymous'} {bid.bidder_details?.last_name?.charAt(0) || ''}
                          </span>
                          <span class="text-text-medium">{formatDate(bid.created_at || bid.timestamp)}</span>
                        </div>
                        <div class="flex justify-between mt-1">
                          <span class="text-text-medium">Bid amount</span>
                          <span class="font-medium text-secondary-blue">{formatCurrency(bid.amount, auction.currency)}</span>
                        </div>
                        {#if bid.auto_bid_limit}
                          <div class="text-xs text-text-medium mt-1">
                            Auto-bid enabled up to {formatCurrency(bid.auto_bid_limit, auction.currency)}
                          </div>
                        {/if}
                      </div>
                    </div>
                  </li>
                {/each}
              </ul>
            {:else if auction.recent_bids && auction.recent_bids.length > 0}
              <ul class="divide-y divide-primary-blue/10">
                {#each auction.recent_bids as bid}
                  <li class="p-4 text-sm">
                    <div class="flex items-start">
                      <div class="text-secondary-blue flex-shrink-0 mt-0.5">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                          <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd" />
                        </svg>
                      </div>
                      
                      <div class="ml-3 flex-1">
                        <div class="flex justify-between">
                          <span class="font-medium text-text-dark">
                            {bid.bidder_details?.first_name || 'Anonymous'} {bid.bidder_details?.last_name?.charAt(0) || ''}
                          </span>
                          <span class="text-text-medium">{formatDate(bid.created_at)}</span>
                        </div>
                        <div class="flex justify-between mt-1">
                          <span class="text-text-medium">Bid amount</span>
                          <span class="font-medium text-secondary-blue">{formatCurrency(bid.amount, auction.currency)}</span>
                        </div>
                      </div>
                    </div>
                  </li>
                {/each}
              </ul>
            {:else}
              <div class="text-center py-8 text-text-medium">
                <p>No bids have been placed yet. Be the first to bid!</p>
              </div>
            {/if}
          </div>
        </div>
      </div>
      
      <!-- Bidding Form -->
      <div class="bg-white rounded-lg border border-primary-blue/20 overflow-hidden">
        <div class="px-5 py-4 border-b border-primary-blue/10 bg-gradient-to-r from-primary-blue/5 to-primary-peach/5">
          <h3 class="text-lg font-medium text-text-dark">Your Bid</h3>
        </div>
        
        <div class="p-5">
          {#if auctionEnded}
            <Alert variant="warning">
              This auction has ended and is no longer accepting bids.
            </Alert>
          {:else if auction.seller === $user?.id}
            <Alert variant="info">
              You cannot bid on your own auction.
            </Alert>
          {:else}
            {#if formError}
              <Alert variant="error" class="mb-4">
                {formError}
              </Alert>
            {/if}
            
            {#if formSuccess}
              <Alert variant="success" class="mb-4">
                {formSuccess}
              </Alert>
            {/if}
            
            <form on:submit|preventDefault={submitBid} class="space-y-6">
              <!-- Bid Amount with improved controls -->
              <div>
                <label for="bid-amount" class="block text-sm font-medium text-text-dark mb-1">
                  Bid Amount <span class="text-red-500">*</span>
                </label>
                <div class="relative rounded-md">
                  <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <span class="text-gray-500 sm:text-sm">
                      {auction.currency === 'USD' ? '$' : auction.currency}
                    </span>
                  </div>
                  <input
                    type="number"
                    id="bid-amount"
                    bind:value={bidAmount}
                    min={minimumBid}
                    step="0.01"
                    class="w-full pl-10 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-blue focus:border-primary-blue"
                    required
                  />
                </div>
                <p class="mt-1 text-xs text-text-medium">
                  Minimum bid: {formatCurrency(minimumBid, auction.currency)}
                </p>
              </div>
              
              <!-- Quick bid options -->
              <div class="flex flex-wrap gap-2">
                <button 
                  type="button"
                  class="px-3 py-1 text-sm bg-primary-blue/10 text-secondary-blue rounded-md hover:bg-primary-blue/20 transition-colors"
                  on:click={() => bidAmount = minimumBid}
                >
                  Minimum Bid ({formatCurrency(minimumBid, auction.currency)})
                </button>
                <button 
                  type="button"
                  class="px-3 py-1 text-sm bg-primary-blue/10 text-secondary-blue rounded-md hover:bg-primary-blue/20 transition-colors"
                  on:click={() => bidAmount = minimumBid + (auction?.minimum_bid_increment || 1) * 2}
                >
                  +{formatCurrency((auction?.minimum_bid_increment || 1) * 2, auction.currency)}
                </button>
                <button 
                  type="button"
                  class="px-3 py-1 text-sm bg-primary-blue/10 text-secondary-blue rounded-md hover:bg-primary-blue/20 transition-colors"
                  on:click={() => bidAmount = minimumBid + (auction?.minimum_bid_increment || 1) * 5}
                >
                  +{formatCurrency((auction?.minimum_bid_increment || 1) * 5, auction.currency)}
                </button>
              </div>
              
              <!-- Auto-bid Option with clear explanation -->
              <div class="bg-primary-blue/5 p-5 rounded-lg">
                <div class="flex items-start">
                  <div class="flex items-center h-5">
                    <input
                      id="auto-bid"
                      type="checkbox"
                      bind:checked={autoBidEnabled}
                      class="h-4 w-4 text-primary-blue focus:ring-primary-blue border-gray-300 rounded"
                    />
                  </div>
                  <div class="ml-3">
                    <label for="auto-bid" class="text-sm font-medium text-text-dark">
                      Enable Auto-bidding
                    </label>
                    <p class="text-xs text-text-medium mt-1">
                      Our system will automatically bid on your behalf up to your maximum limit to keep you as the highest bidder.
                    </p>
                  </div>
                </div>
                
                <!-- Auto-bid diagram -->
                <div class="mt-4 border-t border-primary-blue/10 pt-4">
                  <h4 class="text-sm font-medium text-text-dark mb-2">How Auto-bidding Works:</h4>
                  <div class="text-xs space-y-2 text-text-medium">
                    <div class="flex items-start">
                      <div class="h-5 w-5 text-primary-blue flex-shrink-0">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
                        </svg>
                      </div>
                      <p class="ml-2">You set your <b>starting bid</b> and <b>maximum limit</b></p>
                    </div>
                    <div class="flex items-start">
                      <div class="h-5 w-5 text-primary-blue flex-shrink-0">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
                        </svg>
                      </div>
                      <p class="ml-2">If someone outbids you, we place the minimum necessary bid on your behalf</p>
                    </div>
                    <div class="flex items-start">
                      <div class="h-5 w-5 text-primary-blue flex-shrink-0">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
                        </svg>
                      </div>
                      <p class="ml-2">We continue bidding automatically until you win or reach your limit</p>
                    </div>
                    <div class="flex items-start">
                      <div class="h-5 w-5 text-primary-blue flex-shrink-0">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
                        </svg>
                      </div>
                      <p class="ml-2">You're notified if you're outbid beyond your maximum limit</p>
                    </div>
                  </div>
                </div>
                
                {#if autoBidEnabled}
                  <div class="mt-4">
                    <label for="auto-bid-limit" class="block text-sm font-medium text-text-dark mb-1">
                      Maximum Bid Limit <span class="text-red-500">*</span>
                    </label>
                    <div class="relative rounded-md">
                      <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <span class="text-gray-500 sm:text-sm">
                          {auction.currency === 'USD' ? '$' : auction.currency}
                        </span>
                      </div>
                      <input
                        type="number"
                        id="auto-bid-limit"
                        bind:value={autoBidLimit}
                        min={bidAmount}
                        step="0.01"
                        class="w-full pl-10 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-blue focus:border-primary-blue"
                        required={autoBidEnabled}
                      />
                    </div>
                    <p class="mt-1 text-xs text-text-medium">
                      This is the maximum amount you're willing to bid automatically. You'll only pay the minimum needed to stay ahead of other bidders.
                    </p>
                  </div>
                {/if}
              </div>
              
              <!-- Bid summary if auto-bid is enabled -->
              {#if autoBidEnabled && bidAmount > 0 && autoBidLimit >= bidAmount}
                <div class="border border-primary-blue/20 rounded-lg p-4 bg-primary-blue/5">
                  <h4 class="text-sm font-medium text-text-dark mb-2">Your Bid Summary</h4>
                  <div class="space-y-1 text-sm">
                    <div class="flex justify-between">
                      <span class="text-text-medium">Initial bid:</span>
                      <span class="font-medium">{formatCurrency(bidAmount, auction.currency)}</span>
                    </div>
                    <div class="flex justify-between">
                      <span class="text-text-medium">Auto-bid maximum:</span>
                      <span class="font-medium">{formatCurrency(autoBidLimit, auction.currency)}</span>
                    </div>
                    <div class="flex justify-between border-t border-primary-blue/10 pt-1 mt-1">
                      <span class="text-text-medium">Current price:</span>
                      <span class="font-medium">{formatCurrency(auction.current_price, auction.currency)}</span>
                    </div>
                  </div>
                </div>
              {/if}
              
              <!-- Terms Agreement -->
              <div class="text-sm text-text-medium">
                By placing a bid, you agree to the <a href="/terms" class="text-secondary-blue hover:underline">Terms and Conditions</a> and understand that all bids are binding.
              </div>
              
              <!-- Submit Button -->
              <Button
                type="submit"
                variant="primary"
                size="lg"
                fullWidth={true}
                disabled={submitting || auctionEnded || auction.seller === $user?.id}
                loading={submitting}
              >
                {submitting ? 'Processing...' : autoBidEnabled 
                  ? `Place Bid with Auto-bidding (Up to ${formatCurrency(autoBidLimit, auction.currency)})` 
                  : `Place Bid (${formatCurrency(bidAmount, auction.currency)})`
                }
              </Button>
            </form>
          {/if}
        </div>
      </div>
    </div>
  {:else}
    <!-- Empty state -->
    <div class="text-center py-12">
      <p class="text-text-medium">Auction not found or has been removed.</p>
      <Button 
        href="/auctions" 
        variant="primary" 
        size="md"
        class="mt-4"
      >
        Browse Auctions
      </Button>
    </div>
  {/if}
</div>

<style>
  /* Custom scrollbar for bid list */
  .overflow-y-auto {
    scrollbar-width: thin;
    scrollbar-color: #9ca3af #f3f4f6;
  }

  .overflow-y-auto::-webkit-scrollbar {
    width: 6px;
  }

  .overflow-y-auto::-webkit-scrollbar-track {
    background: #f3f4f6;
  }

  .overflow-y-auto::-webkit-scrollbar-thumb {
    background-color: #9ca3af;
    border-radius: 3px;
  }

  /* Animation for live indicator */
  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }
  
  .animate-pulse {
    animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
  }
</style>