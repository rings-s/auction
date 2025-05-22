<!-- src/lib/components/auction/LiveBidding.svelte -->
<script>
  import { onMount, onDestroy, createEventDispatcher } from 'svelte';
  import { user } from '$lib/stores/user';
  import { t } from '$lib/i18n/i18n';
  import { fetchAuctionBids, placeBid } from '$lib/api/auction';
  import Button from '$lib/components/ui/Button.svelte';
  import FormField from '$lib/components/ui/FormField.svelte';
  import Alert from '$lib/components/ui/Alert.svelte';
  import Modal from '$lib/components/ui/Modal.svelte';
  import AuctionStatus from './AuctionStatus.svelte';
  import { fly, scale } from 'svelte/transition';
  import { quintOut } from 'svelte/easing';
  
  const dispatch = createEventDispatcher();
  
  export let auction;
  export let isOwner = false;
  export let onBidPlaced = () => {};
  
  let bidAmount = '';
  let maxBidAmount = '';
  let bids = [];
  let activeBidders = 0;
  let loading = true;
  let submitting = false;
  let error = '';
  let success = '';
  let refreshInterval;
  let websocket = null;
  let showAdvancedBidModal = false;
  let showOwnerControlsModal = false;
  let autoBiddingEnabled = false;
  let newBidNotifications = [];
  
  // Quick bid increments
  let quickBidOptions = [];
  
  // Owner controls
  let selectedWinningBid = null;
  let auctionNotes = '';
  
  $: minimumBidAmount = calculateMinimumBid();
  $: canBid = auction?.status === 'live' && $user && !isOwner && auction?.end_date > new Date().toISOString();
  $: highestBid = bids.length > 0 ? bids[0] : null;
  $: userBids = bids.filter(bid => bid.bidder_info?.id === $user?.id);
  $: userHighestBid = userBids.length > 0 ? userBids[0] : null;
  
  function calculateMinimumBid() {
    if (!auction) return 0;
    const currentBid = auction.current_bid || auction.starting_bid;
    const increment = auction.minimum_increment || 100;
    return parseFloat(currentBid) + parseFloat(increment);
  }
  
  function generateQuickBidOptions() {
    const minBid = minimumBidAmount;
    const increment = parseFloat(auction.minimum_increment) || 100;
    
    quickBidOptions = [
      { amount: minBid, label: $t('auction.minimumBid'), color: 'bg-blue-500' },
      { amount: minBid + increment, label: `+${formatCurrency(increment)}`, color: 'bg-green-500' },
      { amount: minBid + (increment * 2), label: `+${formatCurrency(increment * 2)}`, color: 'bg-yellow-500' },
      { amount: minBid + (increment * 5), label: `+${formatCurrency(increment * 5)}`, color: 'bg-red-500' }
    ];
  }
  
  async function loadBids() {
    try {
      loading = true;
      if (!auction?.id) return;
      
      const response = await fetchAuctionBids(auction.id);
      const newBids = (response.results || response).sort((a, b) => {
        return new Date(b.bid_time) - new Date(a.bid_time);
      });
      
      // Check for new bids and create notifications
      if (bids.length > 0) {
        const newBidCount = newBids.length - bids.length;
        if (newBidCount > 0) {
          const latestBids = newBids.slice(0, newBidCount);
          latestBids.forEach(bid => {
            if (bid.bidder_info?.id !== $user?.id) {
              addBidNotification(bid);
            }
          });
        }
      }
      
      bids = newBids;
      activeBidders = new Set(bids.map(bid => bid.bidder_info?.id)).size;
      
    } catch (err) {
      console.error('Error loading bids:', err);
      error = err.message || $t('error.loadingBids');
    } finally {
      loading = false;
    }
  }
  
  function addBidNotification(bid) {
    const notification = {
      id: Date.now() + Math.random(),
      bid,
      timestamp: new Date()
    };
    
    newBidNotifications = [notification, ...newBidNotifications.slice(0, 4)];
    
    // Auto remove after 5 seconds
    setTimeout(() => {
      newBidNotifications = newBidNotifications.filter(n => n.id !== notification.id);
    }, 5000);
  }
  
  async function handleQuickBid(amount) {
    if (submitting) return;
    
    try {
      error = '';
      success = '';
      submitting = true;
      
      await placeBid(auction.id, amount);
      
      success = $t('auction.bidPlaced');
      bidAmount = (minimumBidAmount + parseFloat(auction.minimum_increment)).toString();
      
      await loadBids();
      onBidPlaced();
      generateQuickBidOptions();
      
    } catch (err) {
      console.error('Error placing bid:', err);
      error = err.message || $t('error.bidFailed');
    } finally {
      submitting = false;
    }
  }
  
  async function handleCustomBid() {
    const amount = parseFloat(bidAmount);
    
    if (isNaN(amount) || amount < minimumBidAmount) {
      error = $t('auction.bidTooLow', { amount: minimumBidAmount.toLocaleString() });
      return;
    }
    
    try {
      error = '';
      success = '';
      submitting = true;
      
      await placeBid(auction.id, amount);
      
      success = $t('auction.bidPlaced');
      bidAmount = '';
      
      await loadBids();
      onBidPlaced();
      generateQuickBidOptions();
      
    } catch (err) {
      console.error('Error placing bid:', err);
      error = err.message || $t('error.bidFailed');
    } finally {
      submitting = false;
    }
  }
  
  async function handleAdvancedBid() {
    const amount = parseFloat(bidAmount);
    const maxAmount = maxBidAmount ? parseFloat(maxBidAmount) : null;
    
    if (isNaN(amount) || amount < minimumBidAmount) {
      error = $t('auction.bidTooLow', { amount: minimumBidAmount.toLocaleString() });
      return;
    }
    
    if (maxAmount && maxAmount < amount) {
      error = 'Maximum bid cannot be less than current bid';
      return;
    }
    
    try {
      error = '';
      success = '';
      submitting = true;
      
      await placeBid(auction.id, amount);
      
      success = autoBiddingEnabled ? 
        'Auto-bidding enabled! You will be notified of outbids.' : 
        $t('auction.bidPlaced');
      
      bidAmount = '';
      maxBidAmount = '';
      showAdvancedBidModal = false;
      
      await loadBids();
      onBidPlaced();
      generateQuickBidOptions();
      
    } catch (err) {
      console.error('Error placing advanced bid:', err);
      error = err.message || $t('error.bidFailed');
    } finally {
      submitting = false;
    }
  }
  
  async function handleEndAuction() {
    if (!selectedWinningBid) {
      error = 'Please select a winning bid';
      return;
    }
    
    try {
      // In a real implementation, you would call an API to end the auction
      // and mark the selected bid as the winner
      console.log('Ending auction with winning bid:', selectedWinningBid);
      success = 'Auction ended successfully!';
      showOwnerControlsModal = false;
      dispatch('auctionEnded', { winningBid: selectedWinningBid, notes: auctionNotes });
      
    } catch (err) {
      error = 'Failed to end auction';
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
  
  function formatDateTime(dateString) {
    try {
      const date = new Date(dateString);
      return new Intl.DateTimeFormat('default', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      }).format(date);
    } catch (e) {
      return dateString;
    }
  }
  
  function getTimeAgo(dateString) {
    const now = new Date();
    const past = new Date(dateString);
    const diffInSeconds = Math.floor((now - past) / 1000);
    
    if (diffInSeconds < 60) return 'Just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
    return `${Math.floor(diffInSeconds / 86400)}d ago`;
  }
  
  onMount(() => {
    bidAmount = minimumBidAmount.toString();
    generateQuickBidOptions();
    loadBids();
    
    // Set up refresh interval
    refreshInterval = setInterval(() => {
      if (!submitting) {
        loadBids();
        generateQuickBidOptions();
      }
    }, 5000);
  });
  
  onDestroy(() => {
    if (refreshInterval) {
      clearInterval(refreshInterval);
    }
    if (websocket) {
      websocket.close();
    }
  });
</script>

<div class="space-y-6">
  <!-- Bid Notifications -->
  {#if newBidNotifications.length > 0}
    <div class="fixed top-20 right-4 z-50 space-y-2">
      {#each newBidNotifications as notification (notification.id)}
        <div 
          class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg p-4 max-w-sm"
          transition:fly="{{ x: 300, duration: 300, easing: quintOut }}"
        >
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <svg class="h-5 w-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
              </svg>
            </div>
            <div class="ml-3">
              <p class="text-sm font-medium text-gray-900 dark:text-white">
                New Bid: {formatCurrency(notification.bid.amount)}
              </p>
              <p class="text-xs text-gray-500 dark:text-gray-400">
                by {notification.bid.bidder_info?.name || 'Anonymous'}
              </p>
            </div>
          </div>
        </div>
      {/each}
    </div>
  {/if}
  
  <!-- Success/Error Messages -->
  {#if success}
    <Alert type="success" message={success} dismissible={true} />
  {/if}
  
  {#if error}
    <Alert type="error" message={error} dismissible={true} />
  {/if}
  
  <!-- Current Auction Status -->
  <div class="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-xl p-6 border border-blue-200 dark:border-blue-800">
    <div class="flex justify-between items-start mb-4">
      <div>
        <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-1">
          {formatCurrency(auction?.current_bid || auction?.starting_bid)}
        </h2>
        <p class="text-sm text-gray-600 dark:text-gray-400">
          Current Highest Bid
        </p>
      </div>
      <div class="text-right">
        <div class="flex items-center space-x-2 mb-1">
          <span class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
          <span class="text-sm font-medium text-gray-900 dark:text-white">
            {activeBidders} Active Bidders
          </span>
        </div>
        <p class="text-xs text-gray-500 dark:text-gray-400">
          {bids.length} Total Bids
        </p>
      </div>
    </div>
    
    {#if highestBid}
      <div class="flex items-center justify-between p-3 bg-white/50 dark:bg-gray-800/50 rounded-lg">
        <div class="flex items-center space-x-3">
          <div class="w-8 h-8 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-full flex items-center justify-center">
            <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M5 2a1 1 0 011 1v1h1a1 1 0 010 2H6v1a1 1 0 01-2 0V6H3a1 1 0 010-2h1V3a1 1 0 011-1zm0 10a1 1 0 011 1v1h1a1 1 0 110 2H6v1a1 1 0 11-2 0v-1H3a1 1 0 110-2h1v-1a1 1 0 011-1zM12 2a1 1 0 01.967.744L14.146 7.2 17.5 9.134a1 1 0 010 1.732L14.146 12.8l-1.179 4.456a1 1 0 01-1.934 0L9.854 12.8 6.5 10.866a1 1 0 010-1.732L9.854 7.2l1.179-4.456A1 1 0 0112 2z" clip-rule="evenodd" />
            </svg>
          </div>
          <div>
            <p class="font-semibold text-gray-900 dark:text-white text-sm">
              Leading: {highestBid.bidder_info?.name || 'Anonymous'}
              {#if highestBid.bidder_info?.id === $user?.id}
                <span class="text-green-600 dark:text-green-400">(You)</span>
              {/if}
            </p>
            <p class="text-xs text-gray-500 dark:text-gray-400">
              {getTimeAgo(highestBid.bid_time)}
            </p>
          </div>
        </div>
        <AuctionStatus status={highestBid.status} isCompact={true} />
      </div>
    {/if}
  </div>
  
  <!-- User's Bidding Status -->
  {#if $user && userHighestBid}
    <div class="bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-lg p-4 border border-green-200 dark:border-green-800">
      <div class="flex items-center justify-between">
        <div>
          <p class="font-medium text-green-800 dark:text-green-200">
            Your Highest Bid: {formatCurrency(userHighestBid.amount)}
          </p>
          <p class="text-sm text-green-600 dark:text-green-400">
            {userHighestBid.bidder_info?.id === highestBid?.bidder_info?.id ? 
              '🎉 You are currently winning!' : 
              '⚠️ You have been outbid'}
          </p>
        </div>
        <AuctionStatus status={userHighestBid.status} />
      </div>
    </div>
  {/if}
  
  <!-- Bidding Interface -->
  {#if canBid}
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
      <div class="bg-gradient-to-r from-primary-500 to-blue-600 px-6 py-4">
        <h3 class="text-lg font-semibold text-white flex items-center">
          <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clip-rule="evenodd" />
          </svg>
          Place Your Bid
        </h3>
        <p class="text-primary-100 text-sm mt-1">
          Minimum bid: {formatCurrency(minimumBidAmount)}
        </p>
      </div>
      
      <div class="p-6 space-y-6">
        <!-- Quick Bid Options -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
            Quick Bid Options
          </label>
          <div class="grid grid-cols-2 gap-3">
            {#each quickBidOptions as option}
              <button
                type="button"
                class="group relative overflow-hidden rounded-lg p-4 border-2 border-gray-200 dark:border-gray-700 hover:border-primary-500 dark:hover:border-primary-400 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500 {submitting ? 'border-primary-500 dark:border-primary-400' : ''}"
                disabled={submitting}
                on:click={() => handleQuickBid(option.amount)}
                transition:scale="{{ duration: 200, start: 0.95 }}"
              >
                <div class="flex flex-col items-center space-y-1">
                  <span class="text-lg font-bold text-gray-900 dark:text-white">
                    {formatCurrency(option.amount)}
                  </span>
                  <span class="text-xs text-gray-500 dark:text-gray-400">
                    {option.label}
                  </span>
                </div>
                <div class="absolute inset-0 {option.color} opacity-0 group-hover:opacity-5 transition-opacity duration-200"></div>
                
                {#if submitting}
                  <div class="absolute inset-0 bg-gray-200 dark:bg-gray-700 bg-opacity-50 flex items-center justify-center">
                    <div class="animate-spin rounded-full h-5 w-5 border-b-2 border-primary-500"></div>
                  </div>
                {/if}
              </button>
            {/each}
          </div>
        </div>
        
        <!-- Custom Bid Input -->
        <div class="border-t border-gray-200 dark:border-gray-700 pt-6">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
            Custom Bid Amount
          </label>
          <form on:submit|preventDefault={handleCustomBid} class="flex space-x-3">
            <div class="flex-1">
              <FormField
                type="number"
                id="custom-bid"
                placeholder={minimumBidAmount.toString()}
                bind:value={bidAmount}
                min={minimumBidAmount}
                step="1"
                disabled={submitting}
                class="text-lg font-semibold"
              />
            </div>
            <Button
              type="submit"
              variant="primary"
              size="large"
              loading={submitting}
              disabled={submitting || !bidAmount || parseFloat(bidAmount) < minimumBidAmount}
              class="px-8"
            >
              Bid Now
            </Button>
          </form>
        </div>
        
        <!-- Advanced Bidding -->
        <div class="border-t border-gray-200 dark:border-gray-700 pt-4">
          <Button
            variant="outline"
            on:click={() => showAdvancedBidModal = true}
            class="w-full"
            disabled={submitting}
          >
            <svg class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            Advanced Bidding & Auto-Bid
          </Button>
        </div>
      </div>
    </div>
  {:else if isOwner}
    <!-- Owner Controls -->
    <div class="bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 rounded-xl p-6 border border-purple-200 dark:border-purple-800">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
            Auction Owner Controls
          </h3>
          <p class="text-sm text-gray-600 dark:text-gray-400">
            Manage your auction and select the winning bid
          </p>
        </div>
        <svg class="w-8 h-8 text-purple-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
        </svg>
      </div>
      
      <div class="grid grid-cols-2 gap-4">
        <div class="text-center">
          <p class="text-2xl font-bold text-gray-900 dark:text-white">
            {bids.length}
          </p>
          <p class="text-sm text-gray-600 dark:text-gray-400">Total Bids</p>
        </div>
        <div class="text-center">
          <p class="text-2xl font-bold text-gray-900 dark:text-white">
            {activeBidders}
          </p>
          <p class="text-sm text-gray-600 dark:text-gray-400">Unique Bidders</p>
        </div>
      </div>
      
      <div class="mt-6 flex space-x-3">
        <Button
          variant="primary"
          on:click={() => showOwnerControlsModal = true}
          class="flex-1"
          disabled={bids.length === 0}
        >
          <svg class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
          Select Winner & End Auction
        </Button>
        <Button
          variant="outline"
          on:click={() => dispatch('extendAuction')}
        >
          <svg class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Extend
        </Button>
      </div>
    </div>
  {:else if !$user}
    <!-- Login Prompt -->
    <div class="bg-gradient-to-r from-yellow-50 to-orange-50 dark:from-yellow-900/20 dark:to-orange-900/20 rounded-xl p-6 border border-yellow-200 dark:border-yellow-800 text-center">
      <div class="w-16 h-16 bg-yellow-100 dark:bg-yellow-900 rounded-full flex items-center justify-center mx-auto mb-4">
        <svg class="w-8 h-8 text-yellow-600 dark:text-yellow-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
        </svg>
      </div>
      <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">
        Join the Bidding!
      </h3>
      <p class="text-gray-600 dark:text-gray-400 mb-6">
        Sign in to place bids and compete for this amazing property
      </p>
      <Button
        variant="primary"
        size="large"
        href={`/login?redirect=/auctions/${auction.slug || auction.id}`}
        class="px-8"
      >
        Sign In to Bid
      </Button>
    </div>
  {:else}
    <!-- Auction Not Active -->
    <div class="bg-gray-100 dark:bg-gray-700 rounded-xl p-6 text-center">
      <svg class="w-16 h-16 mx-auto text-gray-400 dark:text-gray-500 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
        {auction?.status === 'scheduled' ? 'Auction Not Started' : 'Bidding Not Active'}
      </h3>
      <p class="text-gray-500 dark:text-gray-400">
        {auction?.status === 'scheduled' 
          ? 'This auction will start soon. Check back later!' 
          : 'This auction is no longer accepting bids.'}
      </p>
    </div>
  {/if}
  
  <!-- Bid History -->
  <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
    <div class="bg-gray-50 dark:bg-gray-700 px-6 py-4 border-b border-gray-200 dark:border-gray-600">
      <div class="flex justify-between items-center">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
          Bid History ({bids.length})
        </h3>
        <Button
          variant="outline"
          size="small"
          loading={loading}
          on:click={loadBids}
        >
          <svg class="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Refresh
        </Button>
      </div>
    </div>
    
    <div class="max-h-96 overflow-y-auto">
      {#if loading}
        <div class="py-12 text-center">
          <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
          <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">Loading bids...</p>
        </div>
      {:else if bids.length === 0}
        <div class="py-12 text-center">
          <svg class="w-16 h-16 mx-auto text-gray-400 dark:text-gray-500 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 4V2a1 1 0 011-1h8a1 1 0 011 1v2h4a1 1 0 011 1v1a1 1 0 01-1 1v9a2 2 0 01-2 2H5a2 2 0 01-2-2V7a1 1 0 01-1-1V5a1 1 0 011-1h4zM9 4h6V3H9v1zm5 8a1 1 0 11-2 0V9a1 1 0 112 0v3z" />
          </svg>
          <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
            No Bids Yet
          </h3>
          <p class="text-gray-500 dark:text-gray-400">
            Be the first to place a bid on this auction!
          </p>
        </div>
      {:else}
        <div class="divide-y divide-gray-200 dark:divide-gray-700">
          {#each bids as bid, index (bid.id)}
            <div 
              class="p-4 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-150 {index === 0 ? 'bg-green-50 dark:bg-green-900/20' : ''} {bid.bidder_info?.id === $user?.id ? 'bg-primary-50 dark:bg-primary-900/20' : ''}"
              transition:fly="{{ y: 20, duration: 300, delay: index * 50 }}"
            >
              <div class="flex justify-between items-start">
                <div class="flex items-center space-x-3">
                  {#if index === 0}
                    <div class="w-8 h-8 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-full flex items-center justify-center">
                      <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M5 2a1 1 0 011 1v1h1a1 1 0 010 2H6v1a1 1 0 01-2 0V6H3a1 1 0 010-2h1V3a1 1 0 011-1zm0 10a1 1 0 011 1v1h1a1 1 0 110 2H6v1a1 1 0 11-2 0v-1H3a1 1 0 110-2h1v-1a1 1 0 011-1zM12 2a1 1 0 01.967.744L14.146 7.2 17.5 9.134a1 1 0 010 1.732L14.146 12.8l-1.179 4.456a1 1 0 01-1.934 0L9.854 12.8 6.5 10.866a1 1 0 010-1.732L9.854 7.2l1.179-4.456A1 1 0 0112 2z" clip-rule="evenodd" />
                      </svg>
                    </div>
                  {:else}
                    <div class="w-8 h-8 bg-gray-100 dark:bg-gray-600 rounded-full flex items-center justify-center">
                      <span class="text-sm font-medium text-gray-600 dark:text-gray-300">
                        #{index + 1}
                      </span>
                    </div>
                  {/if}
                  
                  <div>
                    <div class="flex items-center space-x-2">
                      <p class="text-lg font-bold text-gray-900 dark:text-white">
                        {formatCurrency(bid.amount)}
                      </p>
                      {#if index === 0}
                        <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                          Leading
                        </span>
                      {/if}
                      {#if bid.bidder_info?.id === $user?.id}
                        <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-primary-100 text-primary-800 dark:bg-primary-900 dark:text-primary-200">
                          Your Bid
                        </span>
                      {/if}
                    </div>
                    <p class="text-sm text-gray-600 dark:text-gray-400">
                      {bid.bidder_info?.name || 'Anonymous Bidder'}
                    </p>
                  </div>
                </div>
                
                <div class="text-right">
                  <p class="text-sm text-gray-500 dark:text-gray-400">
                    {getTimeAgo(bid.bid_time)}
                  </p>
                  <AuctionStatus status={bid.status} isCompact={true} />
                </div>
              </div>
            </div>
          {/each}
        </div>
      {/if}
    </div>
  </div>
</div>

<!-- Advanced Bidding Modal -->
<Modal
  bind:show={showAdvancedBidModal}
  title="Advanced Bidding Options"
  maxWidth="lg"
>
  <form on:submit|preventDefault={handleAdvancedBid} class="space-y-6 p-6">
    <div class="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
      <h4 class="text-lg font-semibold text-blue-900 dark:text-blue-100 mb-2">
        Smart Bidding Features
      </h4>
      <p class="text-sm text-blue-700 dark:text-blue-300">
        Set your maximum bid and let our system automatically bid for you up to that amount.
      </p>
    </div>
    
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <FormField
        type="currency"
        id="bid_amount"
        label="Current Bid Amount"
        bind:value={bidAmount}
        currencySymbol="$"
        min={minimumBidAmount}
        required={true}
        helpText="Your immediate bid amount"
      />
      
      <FormField
        type="currency"
        id="max_bid_amount"
        label="Maximum Bid (Optional)"
        bind:value={maxBidAmount}
        currencySymbol="$"
        helpText="Auto-bid up to this amount"
      />
    </div>
    
    <div class="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
      <label class="flex items-center">
        <input
          type="checkbox"
          bind:checked={autoBiddingEnabled}
          class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
        />
        <span class="ml-2 text-sm font-medium text-gray-700 dark:text-gray-300">
          Enable Auto-Bidding
        </span>
      </label>
      <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
        Automatically place bids when you're outbid, up to your maximum amount
      </p>
    </div>
    
    {#if error}
      <Alert type="error" message={error} />
    {/if}
    
    <div class="flex justify-end space-x-3">
      <Button
        variant="outline"
        type="button"
        on:click={() => showAdvancedBidModal = false}
        disabled={submitting}
      >
        Cancel
      </Button>
      
      <Button
        variant="primary"
        type="submit"
        loading={submitting}
        disabled={submitting}
      >
        Place Advanced Bid
      </Button>
    </div>
  </form>
</Modal>

<!-- Owner Controls Modal -->
<Modal
  bind:show={showOwnerControlsModal}
  title="Select Auction Winner"
  maxWidth="xl"
>
  <div class="p-6 space-y-6">
    <div class="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg">
      <h4 class="text-lg font-semibold text-purple-900 dark:text-purple-100 mb-2">
        Choose Your Winning Bid
      </h4>
      <p class="text-sm text-purple-700 dark:text-purple-300">
        Review all bids and select the winner. This action will end the auction and notify the winning bidder.
      </p>
    </div>
    
    <div class="max-h-64 overflow-y-auto border border-gray-200 dark:border-gray-700 rounded-lg">
      <div class="divide-y divide-gray-200 dark:divide-gray-700">
        {#each bids as bid (bid.id)}
          <label class="flex items-center p-4 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer">
            <input
              type="radio"
              bind:group={selectedWinningBid}
              value={bid}
              class="mr-3 h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300"
            />
            <div class="flex-1 flex justify-between items-center">
              <div>
                <p class="text-lg font-bold text-gray-900 dark:text-white">
                  {formatCurrency(bid.amount)}
                </p>
                <p class="text-sm text-gray-600 dark:text-gray-400">
                  {bid.bidder_info?.name || 'Anonymous'} • {formatDateTime(bid.bid_time)}
                </p>
              </div>
              <AuctionStatus status={bid.status} isCompact={true} />
            </div>
          </label>
        {/each}
      </div>
    </div>
    
    <FormField
      type="textarea"
      id="auction_notes"
      label="Closing Notes (Optional)"
      bind:value={auctionNotes}
      rows={3}
      helpText="Add any notes or terms for the winning bidder"
    />
    
    {#if error}
      <Alert type="error" message={error} />
    {/if}
    
    <div class="flex justify-end space-x-3">
      <Button
        variant="outline"
        on:click={() => showOwnerControlsModal = false}
      >
        Cancel
      </Button>
      
      <Button
        variant="primary"
        on:click={handleEndAuction}
        disabled={!selectedWinningBid}
      >
        <svg class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
        </svg>
        End Auction & Select Winner
      </Button>
    </div>
  </div>
</Modal>