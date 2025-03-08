<!-- src/lib/components/auction/BiddingComponent.svelte -->
<script>
  import { onMount, onDestroy } from 'svelte';
  import { createBiddingConnection } from '$lib/websocketService';
  import { authStore, isAuthenticated } from '$lib/stores/authStore';
  import { api } from '$lib/api';
  import { notificationStore } from '$lib/stores/notificationStore';
  import Button from '$lib/components/ui/Button.svelte';
  import Spinner from '$lib/components/ui/Spinner.svelte';
  import Alert from '$lib/components/ui/Alert.svelte';
  
  // Props
  export let auction = null;
  export let autoBidEnabled = false;
  export let isSellerView = false;
  
  // Reactive state with safety checks
  $: auctionId = auction?.id;
  $: currentPrice = parseFloat(auction?.current_price || 0);
  $: minIncrement = parseFloat(auction?.minimum_bid_increment || 1);
  $: currency = auction?.currency || 'SAR';
  $: isActive = auction?.status === 'ACTIVE';
  
  // Ensure seller view check is properly boolean
  $: canBid = isActive && $isAuthenticated && !isSellerView;
  
  // Internal state
  let bidAmount = 0;
  let autoBidLimit = 0;
  let loading = false;
  let error = '';
  let success = '';
  let realTimeBids = [];
  let connection = null;
  let connectionStatus = 'disconnected';
  let lastBidTimestamp = null;
  let bidRefreshInterval = null;
  
  // Confirmation modal state
  let showConfirmation = false;
  let confirmed = false;
  
  // Set default bid amount to current price + minimum increment
  $: {
    if (currentPrice > 0 && minIncrement > 0) {
      bidAmount = currentPrice + minIncrement;
      
      // Set auto-bid limit to 5 increments higher if not set
      if (!autoBidLimit || autoBidLimit < bidAmount) {
        autoBidLimit = currentPrice + (minIncrement * 5);
      }
    }
  }
  
  // Format currency with safety
  function formatCurrency(amount) {
    if (amount === undefined || amount === null) {
      amount = 0;
    }
    
    // Ensure amount is a proper number
    amount = typeof amount === 'string' ? parseFloat(amount) : amount;
    if (isNaN(amount)) amount = 0;
    
    try {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency || 'SAR',
        maximumFractionDigits: 2
      }).format(amount);
    } catch (e) {
      console.error('Error formatting currency:', e);
      return `${currency || 'SAR'} ${amount.toFixed(2)}`;
    }
  }
  
  // Format date with safety
  function formatDate(dateStr) {
    if (!dateStr) return 'N/A';
    
    try {
      const date = new Date(dateStr);
      if (isNaN(date.getTime())) return 'Invalid date';
      
      return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      }).format(date);
    } catch (e) {
      console.error('Error formatting date:', e);
      return dateStr || 'N/A';
    }
  }
  
  // Initialize bidding WebSocket connection safely
  onMount(() => {
    if (!auctionId) return; // Guard against null auction
    
    // First, load existing bids via API to avoid empty state
    loadExistingBids();
    
    // Setup a regular polling interval as a fallback
    bidRefreshInterval = setInterval(() => loadExistingBids(), 5000);
    
    // Initialize WebSocket with timeout
    try {
      connection = createBiddingConnection(auctionId);
      
      // Add connection timeout
      const connectionTimeout = setTimeout(() => {
        if (connectionStatus !== 'connected') {
          connectionStatus = 'failed';
          console.warn('WebSocket connection timed out, using API fallback');
        }
      }, 5000); // 5 second timeout
      
      // Subscribe to real-time bids
      const unsubscribeBids = connection.bids.subscribe(bids => {
        if (!Array.isArray(bids)) {
          console.error('Expected bids to be an array');
          return;
        }
        
        console.log('Received bids update via WebSocket:', bids);
        realTimeBids = bids;
        
        // Update auction current price if there are new bids
        if (bids.length > 0) {
          const highestBidAmount = parseFloat(bids[0]?.amount || 0);
          if (!isNaN(highestBidAmount) && highestBidAmount > currentPrice) {
            currentPrice = highestBidAmount;
            
            // If the price has been updated, recalculate minimum bid
            bidAmount = currentPrice + minIncrement;
          }
        }
      });
      
      // Subscribe to connection status
      const unsubscribeStatus = connection.status.subscribe(status => {
        connectionStatus = status;
        if (status === 'connected') {
          clearTimeout(connectionTimeout);
        }
      });
      
      return () => {
        if (unsubscribeBids) unsubscribeBids();
        if (unsubscribeStatus) unsubscribeStatus();
        clearTimeout(connectionTimeout);
        if (bidRefreshInterval) clearInterval(bidRefreshInterval);
      };
    } catch (err) {
      console.error('Error initializing bidding connection:', err);
      connectionStatus = 'error';
    }
  });
  
  // Add this function to load existing bids via API
  async function loadExistingBids() {
    try {
      if (!auctionId) return;
      
      console.log('Loading bids for auction:', auctionId);
      
      // Use the API to get existing bids
      const response = await api.auction.getBids(auctionId);
      console.log('API response for bids:', response);
      
      if (response && Array.isArray(response.results)) {
        // Check if we have received new data by comparing timestamps
        const newestBidTimestamp = response.results.length > 0 
          ? new Date(response.results[0].created_at).getTime() 
          : null;
          
        // Only update if we have new bids or if this is the first load
        if (!lastBidTimestamp || (newestBidTimestamp && newestBidTimestamp > lastBidTimestamp)) {
          console.log('Updating bids from API response');
          realTimeBids = response.results;
          
          // Update last timestamp to track for future comparisons
          if (newestBidTimestamp) {
            lastBidTimestamp = newestBidTimestamp;
          }
          
          // Update current price if needed
          if (realTimeBids.length > 0) {
            const highestBidAmount = parseFloat(realTimeBids[0]?.amount || 0);
            if (!isNaN(highestBidAmount) && highestBidAmount > currentPrice) {
              console.log('Updating current price based on API data:', highestBidAmount);
              currentPrice = highestBidAmount;
              bidAmount = currentPrice + minIncrement;
              
              // If we're editing this component directly and the auction price changed
              // we can optionally update the parent auction object as well
              if (auction) {
                auction.current_price = highestBidAmount;
              }
            }
          }
        } else {
          console.log('No new bids found in API response');
        }
      }
    } catch (err) {
      console.error('Error loading bids from API:', err);
    }
  }
  
  // Clean up WebSocket connection
  onDestroy(() => {
    if (bidRefreshInterval) {
      clearInterval(bidRefreshInterval);
    }
    
    if (connection) {
      try {
        connection.close();
      } catch (err) {
        console.error('Error closing connection:', err);
      }
    }
  });
  
  // Open confirmation modal
  function confirmBid() {
    if (!auctionId || !$isAuthenticated) {
      error = 'You must be logged in to place a bid';
      return;
    }
    
    if (isSellerView) {
      error = 'You cannot bid on your own auction';
      return;
    }
    
    // Ensure bidAmount is a proper number
    const bidAmountNum = parseFloat(bidAmount);
    if (isNaN(bidAmountNum) || bidAmountNum <= 0) {
      error = 'Please enter a valid bid amount';
      return;
    }
    
    if (bidAmountNum <= currentPrice) {
      error = `Bid must be greater than ${formatCurrency(currentPrice)}`;
      return;
    }
    
    if (autoBidEnabled) {
      const autoBidLimitNum = parseFloat(autoBidLimit);
      if (isNaN(autoBidLimitNum) || autoBidLimitNum < bidAmountNum) {
        error = 'Auto-bid limit must be greater than or equal to your bid amount';
        return;
      }
    }
    
    error = '';
    success = '';
    showConfirmation = true;
  }
  
  // Cancel bid confirmation
  function cancelBid() {
    showConfirmation = false;
  }
  
  // Place a bid both via API and WebSocket for reliability
  async function placeBid() {
    if (!confirmed && !showConfirmation) {
      // If not coming from confirmation modal, show it first
      confirmBid();
      return;
    }
    
    // Close confirmation modal if open
    showConfirmation = false;
    confirmed = false;
    
    loading = true;
    error = '';
    success = '';
    
    try {
      // First, refresh the bid list to make sure we have the latest data
      try {
        await loadExistingBids();
      } catch (refreshError) {
        console.warn('Failed to refresh bids before placing bid:', refreshError);
      }
      
      // Double-check that the bid amount is still valid
      if (parseFloat(bidAmount) <= currentPrice) {
        error = `Your bid of ${formatCurrency(bidAmount)} is no longer valid. The current price is now ${formatCurrency(currentPrice)}`;
        loading = false;
        return;
      }
      
      // Prepare bid data with proper numeric values
      const bidAmountNum = parseFloat(bidAmount);
      const bidData = {
        amount: bidAmountNum,
        auto_bid_limit: autoBidEnabled ? parseFloat(autoBidLimit) : null
      };
      
      console.log('Placing bid with data:', bidData);
      
      // Use the API service to place the bid
      const response = await api.auction.createBid(auctionId, bidData);
      console.log('Bid placed successfully via API:', response);
      
      // Also send via WebSocket for real-time updates if connected
      if (connection && connectionStatus === 'connected' && $authStore.user) {
        try {
          connection.placeBid({
            amount: bidAmountNum,
            auto_bid_limit: autoBidEnabled ? parseFloat(autoBidLimit) : null,
            bidder: $authStore.user.id
          });
          console.log('Bid also sent via WebSocket');
        } catch (wsError) {
          console.warn('WebSocket bid placement failed, but API call succeeded:', wsError);
          // We continue since the API call worked
        }
      }
      
      // Force reload bids after a short delay to ensure UI is updated
      setTimeout(async () => {
        await loadExistingBids();
      }, 500);
      
      // Update local UI state
      if (response) {
        // If we got a response with the new bid, add it to our list
        if (!realTimeBids.some(bid => bid.id === response.id)) {
          realTimeBids = [response, ...realTimeBids];
        }
        
        // Update current price if this is the highest bid
        if (parseFloat(response.amount) > currentPrice) {
          currentPrice = parseFloat(response.amount);
          
          // If we're editing this component directly
          if (auction) {
            auction.current_price = currentPrice;
          }
        }
      }
      
      // Clear bidding form
      success = `Bid of ${formatCurrency(bidAmountNum)} placed successfully!`;
      bidAmount = currentPrice + minIncrement;
      
      // Show notification
      notificationStore.success(success);
      
      // Show success alert and automatically close it after 5 seconds
      setTimeout(() => {
        if (success) success = '';
      }, 5000);
    } catch (err) {
      console.error('Error placing bid:', err);
      error = err.error || 'Failed to place bid. Please try again.';
      notificationStore.error(error);
      
      // Try to refresh bids to get the latest state
      try {
        await loadExistingBids();
      } catch (refreshError) {
        console.warn('Failed to refresh bids after error:', refreshError);
      }
    } finally {
      loading = false;
    }
  }
</script>

<div class="bg-white rounded-lg border border-primary-blue/20 overflow-hidden">
  <!-- Bidding header -->
  <div class="px-5 py-4 border-b border-primary-blue/10 bg-gradient-to-r from-primary-blue/5 to-primary-peach/5">
    <h3 class="text-lg font-medium text-text-dark">Place Your Bid</h3>
  </div>

  <div class="p-5">
    {#if !$isAuthenticated}
      <Alert variant="info">
        Please <a href="/login?redirect=/auctions/{auctionId}" class="font-medium underline">sign in</a> to place a bid.
      </Alert>
    {:else if isSellerView}
      <Alert variant="info">You cannot bid on your own auction.</Alert>
    {:else if !isActive}
      <Alert variant="warning">This auction is not currently active.</Alert>
    {:else}
      {#if error}
        <Alert variant="error">{error}</Alert>
      {/if}
      
      {#if success}
        <Alert variant="success" class="bid-success">
          <div class="flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 mr-2 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>{success}</span>
          </div>
        </Alert>
      {/if}
      
      <div class="mb-4">
        <div class="flex justify-between mb-1">
          <div class="text-sm font-medium text-text-medium">Current Price</div>
          <div class="font-bold text-text-dark">{formatCurrency(currentPrice)}</div>
        </div>
        <div class="flex justify-between text-xs text-text-medium">
          <div>Minimum Increment: {formatCurrency(minIncrement)}</div>
          <div>Minimum Next Bid: {formatCurrency(currentPrice + minIncrement)}</div>
        </div>
      </div>
      
      <div class="space-y-4">
        <!-- Bid amount input with clearer instructions -->
        <div>
          <label for="bid-amount" class="block text-sm font-medium text-text-dark mb-1">
            Your Bid Amount <span class="text-secondary-blue">*</span>
          </label>
          <div class="relative rounded-md">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center">
              <span class="text-text-medium sm:text-sm">
                <!-- Currency display -->
                {currency === 'SAR' ? '﷼' : currency}
              </span>
            </div>
            <input
              type="number"
              id="bid-amount"
              name="bid-amount"
              bind:value={bidAmount}
              min={currentPrice + minIncrement}
              step={minIncrement}
              class="block w-full pl-10 pr-4 py-2 border border-primary-blue/30 focus:ring-secondary-blue focus:border-secondary-blue rounded-md text-right"
              placeholder={`${(currentPrice + minIncrement).toFixed(2)}`}
              required
            />
          </div>
          <p class="mt-1 text-xs text-text-medium">
            Minimum bid must be {formatCurrency(currentPrice + minIncrement)} or higher
          </p>
        </div>
        
        <!-- Quick bid buttons -->
        <div class="flex flex-wrap gap-2">
          <button 
            type="button"
            class="px-3 py-1 text-sm bg-primary-blue/10 text-secondary-blue rounded-md hover:bg-primary-blue/20"
            on:click={() => bidAmount = currentPrice + minIncrement}
          >
            Minimum ({formatCurrency(currentPrice + minIncrement)})
          </button>
          <button 
            type="button"
            class="px-3 py-1 text-sm bg-primary-blue/10 text-secondary-blue rounded-md hover:bg-primary-blue/20"
            on:click={() => bidAmount = currentPrice + (minIncrement * 2)}
          >
            +{formatCurrency(minIncrement * 2)}
          </button>
          <button 
            type="button"
            class="px-3 py-1 text-sm bg-primary-blue/10 text-secondary-blue rounded-md hover:bg-primary-blue/20"
            on:click={() => bidAmount = currentPrice + (minIncrement * 5)}
          >
            +{formatCurrency(minIncrement * 5)}
          </button>
        </div>
        
        <!-- Auto-bid toggle with improved explanation -->
        <div class="bg-primary-blue/5 p-4 rounded-lg">
          <div class="flex items-start">
            <div class="flex items-center h-5">
              <input
                id="auto-bid"
                name="auto-bid"
                type="checkbox"
                bind:checked={autoBidEnabled}
                class="h-4 w-4 text-secondary-blue border-primary-blue/30 rounded focus:ring-secondary-blue "
              />
            </div>
            <div class="ml-3 text-sm">
              <label for="auto-bid" class="font-medium text-text-dark">Enable Auto-Bidding</label>
              <p class="text-text-medium">
                Our system will automatically bid on your behalf to keep you as the highest bidder up to your set limit. 
                This helps you win auctions without constantly monitoring.
              </p>
            </div>
          </div>
          
          <!-- Auto-bid limit input (shown if auto-bid is enabled) -->
          {#if autoBidEnabled}
            <div class="mt-4">
              <label for="auto-bid-limit" class="block text-sm font-medium text-text-dark mb-1">
                Maximum Auto-Bid Limit <span class="text-secondary-blue">*</span>
              </label>
              <div class="relative rounded-md">
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center">
                  <span class="text-text-medium sm:text-sm">
                    {currency === 'SAR' ? '﷼' : currency}
                  </span>
                </div>
                <input
                  type="number"
                  id="auto-bid-limit"
                  name="auto-bid-limit"
                  bind:value={autoBidLimit}
                  min={bidAmount}
                  step={minIncrement}
                  class="block w-full text-text-dark  pl-10 pr-4 py-2 border border-primary-blue/30 focus:ring-secondary-blue focus:border-secondary-blue rounded-md text-right"
                  placeholder="0.00"
                  required
                />
              </div>
              <p class="mt-1 text-sm text-text-medium flex items-start">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1 flex-shrink-0 text-secondary-blue" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
                </svg>
                <span>
                  How it works: If someone outbids you, we'll automatically place a new bid just above theirs, up to this maximum limit. Must be at least {formatCurrency(bidAmount)}.
                </span>
              </p>
            </div>
          {/if}
        </div>
        
        <!-- Place Bid button -->
        <div>
          <button
            type="button"
            class="w-full inline-flex justify-center items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-text-dark bg-primary-blue hover:bg-primary-blue/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-blue disabled:opacity-50 disabled:cursor-not-allowed"
            on:click={placeBid}
            disabled={loading || !canBid || parseFloat(bidAmount) <= currentPrice || (autoBidEnabled && parseFloat(autoBidLimit) < parseFloat(bidAmount))}
          >
            {#if loading}
              <Spinner size="sm" class="mr-2" />
              Processing Bid...
            {:else}
              Place Bid {formatCurrency(bidAmount)}
            {/if}
          </button>
          {#if autoBidEnabled}
            <p class="mt-2 text-xs text-center text-text-medium">
              Auto-bid enabled up to {formatCurrency(autoBidLimit)}
            </p>
          {/if}
        </div>
      </div>
    {/if}
  </div>

  <!-- Real-time bids section -->
  <div class="border-t border-primary-blue/10">
    <div class="px-5 py-3 bg-primary-blue/5">
      <div class="flex items-center justify-between">
        <h4 class="text-sm font-medium text-text-dark">Bid History</h4>
        <div class="flex items-center">
          {#if connectionStatus === 'connected'}
            <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
              <span class="h-2 w-2 mr-1 bg-green-400 rounded-full"></span>
              Live Updates
            </span>
          {:else if connectionStatus === 'connecting'}
            <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-yellow-100 text-yellow-800">
              <Spinner size="xs" class="mr-1" />
              Connecting
            </span>
          {:else if connectionStatus === 'failed' || connectionStatus === 'error'}
            <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Auto-refreshing
            </span>
          {:else}
            <span class="inline-flex text-text-dark  items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800">
              <span class="h-2 w-2 mr-1 bg-red-400 rounded-full"></span>
              Disconnected
            </span>
          {/if}
        </div>
      </div>
    </div>
    
    <div class="max-h-60 overflow-y-auto">
      {#if realTimeBids.length === 0}
        <div class="px-5 py-8 text-center text-text-medium">
          {#if connectionStatus === 'connecting' && auction?.total_bids === 0}
            <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto mb-2 text-primary-blue/30" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2z" />
            </svg>
            <p>No bids placed yet. Be the first to bid!</p>
          {:else if connectionStatus === 'connecting' && auction?.total_bids > 0}
            <Spinner size="md" class="mx-auto mb-3" />
            <p>Loading bid history...</p>
          {:else if connectionStatus === 'failed' || connectionStatus === 'error'}
            <button 
              class="flex items-center justify-center mx-auto mb-2 text-primary-blue/70 hover:text-primary-blue"
              on:click={loadExistingBids}
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Refresh bids
            </button>
            <p>Could not load real-time updates. Click to manually refresh.</p>
          {:else if auction?.total_bids === 0}
            <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto mb-2 text-primary-blue/30" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2z" />
            </svg>
            <p>No bids placed yet. Be the first to bid!</p>
          {:else}
            <button 
              class="flex items-center justify-center mx-auto mb-2 text-primary-blue/70 hover:text-primary-blue"
              on:click={loadExistingBids}
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Refresh bids
            </button>
            <p>Loading bid history...</p>
          {/if}
        </div>
      {:else}
        <ul class="divide-y divide-primary-blue/10">
          {#each realTimeBids as bid (bid.id)}
            <li class="px-5 py-3 text-sm hover:bg-neutral-50">
              <div class="flex items-center justify-between">
                <div>
                  <span class="font-medium text-text-dark">
                    {bid.bidder_details?.first_name || 'Anonymous'} {bid.bidder_details?.last_name?.charAt(0) || ''}
                  </span>
                  <span class="text-text-medium">placed a bid of</span>
                  <span class="font-semibold text-secondary-blue">{formatCurrency(bid.amount)}</span>
                </div>
                <div class="text-xs text-text-medium">
                  {formatDate(bid.created_at || bid.timestamp)}
                </div>
              </div>
              {#if bid.auto_bid_limit}
                <div class="mt-1 text-xs text-text-medium flex items-center">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 mr-1 text-secondary-blue" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  Auto-bid enabled up to {formatCurrency(bid.auto_bid_limit)}
                </div>
              {/if}
            </li>
          {/each}
        </ul>
      {/if}
    </div>
    
    <!-- Refresh button for bid history -->
    <div class="px-5 py-3 border-t border-primary-blue/10 flex justify-center">
      <button 
        class="text-sm text-secondary-blue flex items-center hover:text-secondary-blue/80 focus:outline-none"
        on:click={loadExistingBids}
        aria-label="Refresh bid history"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        Refresh Bids
      </button>
    </div>
  </div>
</div>

<!-- Confirmation Modal -->
{#if showConfirmation}
  <div class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center">
    <div class="bg-white text-text-dark rounded-lg max-w-md w-full p-6 shadow-xl transform transition-all">
      <div class="mb-4">
        <h3 class="text-lg font-medium text-text-dark">Confirm Your Bid</h3>
        <p class="mt-2 text-sm text-text-medium">
          You are about to place a bid on <span class="font-medium">{auction?.title}</span>.
        </p>
      </div>
      
      <div class="bg-primary-blue/5 p-4 rounded-lg mb-4">
        <div class="flex justify-between mb-2">
          <span class="text-sm text-text-medium">Your bid amount:</span>
          <span class="text-lg font-semibold text-secondary-blue">{formatCurrency(bidAmount)}</span>
        </div>
        
        <div class="flex justify-between">
          <span class="text-sm text-text-medium">Current price:</span>
          <span class="text-sm font-medium">{formatCurrency(currentPrice)}</span>
        </div>
        
        {#if autoBidEnabled}
          <div class="flex justify-between mt-2 pt-2 border-t border-primary-blue/10">
            <span class="text-sm text-text-medium">Auto-bid maximum:</span>
            <span class="text-sm font-medium">{formatCurrency(autoBidLimit)}</span>
          </div>
          <p class="mt-2 text-xs text-text-medium">
            Auto-bidding is enabled. The system will bid on your behalf up to your maximum limit.
          </p>
        {/if}
      </div>
      
      <div class="py-2 text-xs text-text-medium">
        <p class="mb-1 flex items-start">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1 text-amber-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          All bids are final and legally binding. If you win, you are obligated to complete the purchase.
        </p>
      </div>
      
      <div class="mt-5 sm:mt-6 grid grid-cols-2 gap-3">
        <button
          type="button"
          class="inline-flex justify-center px-4 py-2 bg-white text-secondary-blue border border-secondary-blue text-sm font-medium rounded-md hover:bg-secondary-blue/5 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-secondary-blue"
          on:click={cancelBid}
        >
          Cancel
        </button>
        <button
          type="button"
          class="inline-flex justify-center px-4 py-2 bg-primary-blue text-text-dark text-sm font-medium rounded-md shadow-sm hover:bg-primary-blue/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-blue"
          on:click={() => { confirmed = true; placeBid(); }}
        >
          Confirm Bid
        </button>
      </div>
    </div>
  </div>
{/if}

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

/* Animation for status indicators */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.bg-green-400, .bg-red-400 {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

/* Animation for success message */
.bid-success {
  animation: fadeIn 0.3s ease-out forwards;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>