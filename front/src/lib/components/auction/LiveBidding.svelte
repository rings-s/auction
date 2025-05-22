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
  import { fly, scale, fade } from 'svelte/transition';
  import { quintOut } from 'svelte/easing';
  
  const dispatch = createEventDispatcher();
  
  export let auction;
  export let isOwner = false;
  export let onBidPlaced = () => {};
  
  // State management
  let bidAmount = '';
  let maxBidAmount = '';
  let bids = [];
  let activeBidders = 0;
  let loading = true;
  let submitting = false;
  let error = '';
  let success = '';
  let refreshInterval;
  let newBidNotifications = [];
  
  // UI state
  let showAdvancedBidModal = false;
  let showOwnerControlsModal = false;
  let showQuickBidConfirm = false;
  let selectedQuickBid = null;
  let autoBiddingEnabled = false;
  
  // Owner controls
  let selectedWinningBid = null;
  let auctionNotes = '';
  
  // Quick bid options
  let quickBidOptions = [];
  
  // Computed values
  $: minimumBidAmount = calculateMinimumBid();
  $: canBid = auction?.status === 'live' && $user && !isOwner && auction?.end_date > new Date().toISOString();
  $: highestBid = bids.length > 0 ? bids[0] : null;
  $: userBids = bids.filter(bid => bid.bidder_info?.id === $user?.id);
  $: userHighestBid = userBids.length > 0 ? userBids[0] : null;
  $: bidIncrement = parseFloat(auction?.minimum_increment) || 100;
  $: isUserWinning = userHighestBid?.id === highestBid?.id;
  
  function calculateMinimumBid() {
    if (!auction) return 0;
    const currentBid = auction.current_bid || auction.starting_bid;
    const increment = auction.minimum_increment || 100;
    return parseFloat(currentBid) + parseFloat(increment);
  }
  
  function generateQuickBidOptions() {
    const minBid = minimumBidAmount;
    
    quickBidOptions = [
      { 
        amount: minBid, 
        label: 'Min Bid', 
        description: `${formatCurrency(minBid)}`,
        icon: '⚡',
        gradient: 'from-blue-500 to-blue-600'
      },
      { 
        amount: minBid + bidIncrement, 
        label: '+1 Inc', 
        description: `${formatCurrency(minBid + bidIncrement)}`,
        icon: '🎯',
        gradient: 'from-emerald-500 to-emerald-600'
      },
      { 
        amount: minBid + (bidIncrement * 2), 
        label: '+2 Inc', 
        description: `${formatCurrency(minBid + (bidIncrement * 2))}`,
        icon: '🚀',
        gradient: 'from-amber-500 to-orange-500'
      },
      { 
        amount: minBid + (bidIncrement * 5), 
        label: 'Power', 
        description: `${formatCurrency(minBid + (bidIncrement * 5))}`,
        icon: '💪',
        gradient: 'from-red-500 to-pink-600'
      }
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
    
    newBidNotifications = [notification, ...newBidNotifications.slice(0, 2)];
    
    // Auto remove after 4 seconds
    setTimeout(() => {
      newBidNotifications = newBidNotifications.filter(n => n.id !== notification.id);
    }, 4000);
  }
  
  async function handleQuickBid(option) {
    if (submitting) return;
    
    selectedQuickBid = option;
    showQuickBidConfirm = true;
  }
  
  async function confirmQuickBid() {
    if (!selectedQuickBid || submitting) return;
    
    try {
      error = '';
      success = '';
      submitting = true;
      showQuickBidConfirm = false;
      
      await placeBid(auction.id, selectedQuickBid.amount);
      
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
      selectedQuickBid = null;
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
      showAdvancedBidModal = false;
      
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
  
  async function handleEndAuction() {
    if (!selectedWinningBid) {
      error = 'Please select a winning bid';
      return;
    }
    
    try {
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
  });
</script>

<!-- Bid Notifications -->
{#if newBidNotifications.length > 0}
  <div class="fixed top-20 right-4 z-50 space-y-3" role="alert" aria-live="polite">
    {#each newBidNotifications as notification (notification.id)}
      <div 
        class="bg-white dark:bg-gray-800 border-l-4 border-primary-500 rounded-r-xl shadow-xl p-4 max-w-sm backdrop-blur-sm"
        transition:fly="{{ x: 300, duration: 400, easing: quintOut }}"
      >
        <div class="flex items-start space-x-3">
          <div class="flex-shrink-0 mt-0.5">
            <div class="w-8 h-8 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center">
              <svg class="w-4 h-4 text-primary-600 dark:text-primary-400" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
              </svg>
            </div>
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-gray-900 dark:text-white">
              New Bid Placed
            </p>
            <p class="text-xl font-bold text-primary-600 dark:text-primary-400 mt-1">
              {formatCurrency(notification.bid.amount)}
            </p>
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-1 truncate">
              by {notification.bid.bidder_info?.name || 'Anonymous Bidder'}
            </p>
          </div>
        </div>
      </div>
    {/each}
  </div>
{/if}

<div class="space-y-8">
  <!-- Alert Messages -->
  {#if success}
    <div transition:fade>
      <Alert type="success" message={success} dismissible={true} />
    </div>
  {/if}
  
  {#if error}
    <div transition:fade>
      <Alert type="error" message={error} dismissible={true} />
    </div>
  {/if}
  
  <!-- Main Auction Status Card -->
  <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
    <!-- Header -->
    <div class="bg-gradient-to-r from-primary-50 to-blue-50 dark:from-primary-900/20 dark:to-blue-900/20 px-6 py-5 border-b border-gray-200 dark:border-gray-700">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <div class="relative">
            <div class="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
            <div class="absolute inset-0 w-3 h-3 bg-red-500 rounded-full animate-ping opacity-75"></div>
          </div>
          <div>
            <h2 class="text-xl font-bold text-gray-900 dark:text-white">
              Live Bidding
            </h2>
            <p class="text-sm text-gray-600 dark:text-gray-400">
              Real-time auction activity
            </p>
          </div>
        </div>
        <button
          type="button"
          class="inline-flex items-center px-3 py-2 text-sm font-medium text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 hover:bg-primary-50 dark:hover:bg-primary-900/20 rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
          on:click={loadBids}
          disabled={loading}
          aria-label="Refresh bids"
        >
          <svg class="w-4 h-4 mr-1 {loading ? 'animate-spin' : ''}" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Refresh
        </button>
      </div>
    </div>
    
    <!-- Stats Grid -->
    <div class="p-6">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <!-- Current Bid -->
        <div class="text-center p-4 bg-gray-50 dark:bg-gray-700/50 rounded-xl">
          <div class="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            {formatCurrency(auction?.current_bid || auction?.starting_bid)}
          </div>
          <div class="text-sm font-medium text-gray-600 dark:text-gray-400">
            Current Highest Bid
          </div>
        </div>
        
        <!-- Total Bids -->
        <div class="text-center p-4 bg-primary-50 dark:bg-primary-900/20 rounded-xl">
          <div class="text-3xl font-bold text-primary-600 dark:text-primary-400 mb-2">
            {bids.length}
          </div>
          <div class="text-sm font-medium text-primary-700 dark:text-primary-300">
            Total Bids Placed
          </div>
        </div>
        
        <!-- Active Bidders -->
        <div class="text-center p-4 bg-emerald-50 dark:bg-emerald-900/20 rounded-xl">
          <div class="text-3xl font-bold text-emerald-600 dark:text-emerald-400 mb-2">
            {activeBidders}
          </div>
          <div class="text-sm font-medium text-emerald-700 dark:text-emerald-300">
            Active Bidders
          </div>
        </div>
      </div>
      
      <!-- Current Leader Card -->
      {#if highestBid}
        <div class="bg-gradient-to-r from-amber-50 to-yellow-50 dark:from-amber-900/20 dark:to-yellow-900/20 rounded-xl p-5 mb-6 border border-amber-200 dark:border-amber-800">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-4">
              <div class="w-12 h-12 bg-gradient-to-r from-amber-400 to-yellow-500 rounded-full flex items-center justify-center shadow-lg">
                <svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M5 2a1 1 0 011 1v1h1a1 1 0 010 2H6v1a1 1 0 01-2 0V6H3a1 1 0 010-2h1V3a1 1 0 011-1zm0 10a1 1 0 011 1v1h1a1 1 0 110 2H6v1a1 1 0 11-2 0v-1H3a1 1 0 110-2h1v-1a1 1 0 011-1zM12 2a1 1 0 01.967.744L14.146 7.2 17.5 9.134a1 1 0 010 1.732L14.146 12.8l-1.179 4.456a1 1 0 01-1.934 0L9.854 12.8 6.5 10.866a1 1 0 010-1.732L9.854 7.2l1.179-4.456A1 1 0 0112 2z" clip-rule="evenodd" />
                </svg>
              </div>
              <div>
                <p class="text-lg font-bold text-gray-900 dark:text-white">
                  Current Leader
                </p>
                <p class="text-sm text-gray-600 dark:text-gray-400">
                  {highestBid.bidder_info?.name || 'Anonymous Bidder'}
                  {#if highestBid.bidder_info?.id === $user?.id}
                    <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200 ml-2">
                      You
                    </span>
                  {/if}
                </p>
              </div>
            </div>
            <div class="text-right">
              <p class="text-2xl font-bold text-amber-600 dark:text-amber-400">
                {formatCurrency(highestBid.amount)}
              </p>
              <p class="text-sm text-gray-500 dark:text-gray-400">
                {getTimeAgo(highestBid.bid_time)}
              </p>
            </div>
          </div>
        </div>
      {/if}
      
      <!-- User Status Card -->
      {#if $user && userHighestBid}
        <div class="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-xl p-5 mb-6 border border-blue-200 dark:border-blue-800">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-3">
              <div class="w-10 h-10 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center">
                <svg class="w-5 h-5 text-blue-600 dark:text-blue-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd" />
                </svg>
              </div>
              <div>
                <p class="font-semibold text-gray-900 dark:text-white">
                  Your Status
                </p>
                <p class="text-sm text-gray-600 dark:text-gray-400">
                  Highest bid: {formatCurrency(userHighestBid.amount)}
                </p>
              </div>
            </div>
            <div class="text-right">
              {#if isUserWinning}
                <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200">
                  🏆 Winning
                </span>
              {:else}
                <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200">
                  ⚠️ Outbid
                </span>
              {/if}
            </div>
          </div>
        </div>
      {/if}
    </div>
  </div>
  
  <!-- Bidding Interface -->
  {#if canBid}
    <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
      <div class="bg-gradient-to-r from-primary-500 to-blue-600 px-6 py-5">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-xl font-bold text-white">
              Place Your Bid
            </h3>
            <p class="text-primary-100 text-sm mt-1">
              Minimum bid: {formatCurrency(minimumBidAmount)}
            </p>
          </div>
          <div class="text-right text-white">
            <p class="text-lg font-semibold">
              Next Increment
            </p>
            <p class="text-2xl font-bold">
              {formatCurrency(bidIncrement)}
            </p>
          </div>
        </div>
      </div>
      
      <div class="p-6 space-y-8">
        <!-- Quick Bid Options -->
        <div>
          <h4 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Quick Bid Options
          </h4>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            {#each quickBidOptions as option, index}
              <button
                type="button"
                class="group relative overflow-hidden rounded-xl p-4 bg-gradient-to-r {option.gradient} hover:shadow-lg transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
                disabled={submitting}
                on:click={() => handleQuickBid(option)}
                transition:scale="{{ duration: 200, delay: index * 100 }}"
              >
                <div class="flex flex-col items-center space-y-2 text-white">
                  <div class="text-2xl">
                    {option.icon}
                  </div>
                  <div class="text-sm font-medium opacity-90">
                    {option.label}
                  </div>
                  <div class="text-lg font-bold">
                    {option.description}
                  </div>
                </div>
                
                {#if submitting}
                  <div class="absolute inset-0 bg-black bg-opacity-20 flex items-center justify-center">
                    <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>
                  </div>
                {/if}
              </button>
            {/each}
          </div>
        </div>
        
        <!-- Custom Bid Section -->
        <div class="border-t border-gray-200 dark:border-gray-700 pt-8">
          <h4 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Custom Bid Amount
          </h4>
          <div class="flex space-x-4">
            <div class="flex-1">
              <div class="relative">
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <span class="text-gray-500 dark:text-gray-400 sm:text-lg">$</span>
                </div>
                <input
                  type="number"
                  bind:value={bidAmount}
                  min={minimumBidAmount}
                  step="1"
                  placeholder={minimumBidAmount.toString()}
                  class="block w-full pl-8 pr-12 py-4 text-lg font-semibold border border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
                  disabled={submitting}
                />
                <div class="absolute inset-y-0 right-0 flex items-center pr-3">
                  <span class="text-gray-500 dark:text-gray-400 text-sm">USD</span>
                </div>
              </div>
            </div>
            <Button
              variant="primary"
              size="large"
              class="px-8 py-4 text-lg font-semibold"
              loading={submitting}
              disabled={submitting || !bidAmount || parseFloat(bidAmount) < minimumBidAmount}
              on:click={handleCustomBid}
            >
              <svg class="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              Place Bid
            </Button>
          </div>
        </div>
        
        <!-- Advanced Options -->
        <div class="border-t border-gray-200 dark:border-gray-700 pt-6">
          <Button
            variant="outline"
            class="w-full"
            on:click={() => showAdvancedBidModal = true}
            disabled={submitting}
          >
            <svg class="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            Advanced Bidding Options
          </Button>
        </div>
      </div>
    </div>
    
  {:else if isOwner}
    <!-- Owner Controls -->
    <div class="bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 rounded-2xl p-6 border border-purple-200 dark:border-purple-800">
      <div class="flex items-center justify-between mb-6">
        <div class="flex items-center space-x-3">
          <div class="w-12 h-12 bg-purple-100 dark:bg-purple-900 rounded-full flex items-center justify-center">
            <svg class="w-6 h-6 text-purple-600 dark:text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
            </svg>
          </div>
          <div>
            <h3 class="text-xl font-bold text-gray-900 dark:text-white">
              Auction Owner Controls
            </h3>
            <p class="text-sm text-gray-600 dark:text-gray-400">
              Manage your auction and select the winning bid
            </p>
          </div>
        </div>
      </div>
      
      <div class="grid grid-cols-2 gap-6 mb-6">
        <div class="text-center p-4 bg-white dark:bg-gray-800 rounded-xl">
          <p class="text-3xl font-bold text-gray-900 dark:text-white">
            {bids.length}
          </p>
          <p class="text-sm text-gray-600 dark:text-gray-400">Total Bids</p>
        </div>
        <div class="text-center p-4 bg-white dark:bg-gray-800 rounded-xl">
          <p class="text-3xl font-bold text-gray-900 dark:text-white">
            {activeBidders}
          </p>
          <p class="text-sm text-gray-600 dark:text-gray-400">Unique Bidders</p>
        </div>
      </div>
      
      <div class="flex space-x-3">
        <Button
          variant="primary"
          class="flex-1"
          on:click={() => showOwnerControlsModal = true}
          disabled={bids.length === 0}
        >
          <svg class="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
          Select Winner & End Auction
        </Button>
        <Button
          variant="outline"
          on:click={() => dispatch('extendAuction')}
        >
          <svg class="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Extend
        </Button>
      </div>
    </div>
    
  {:else if !$user}
    <!-- Login Prompt -->
    <div class="bg-gradient-to-r from-amber-50 to-orange-50 dark:from-amber-900/20 dark:to-orange-900/20 rounded-2xl p-8 border border-amber-200 dark:border-amber-800 text-center">
      <div class="w-16 h-16 bg-amber-100 dark:bg-amber-900 rounded-full flex items-center justify-center mx-auto mb-4">
        <svg class="w-8 h-8 text-amber-600 dark:text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
        </svg>
      </div>
      <h3 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">
        Join the Bidding!
      </h3>
      <p class="text-gray-600 dark:text-gray-400 mb-6">
        Sign in to place bids and compete for this amazing property
      </p>
      <Button
        variant="primary"
        size="large"
        href={`/login?redirect=/auctions/${auction.slug || auction.id}`}
        class="px-8 py-3"
      >
        <svg class="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
        </svg>
        Sign In to Bid
      </Button>
    </div>
    
  {:else}
    <!-- Auction Not Active -->
    <div class="bg-gray-50 dark:bg-gray-700 rounded-2xl p-8 text-center">
      <svg class="w-16 h-16 mx-auto text-gray-400 dark:text-gray-500 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-2">
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
  <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
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
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
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
              class="p-4 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-150 {index === 0 ? 'bg-gradient-to-r from-emerald-50 to-green-50 dark:from-emerald-900/20 dark:to-green-900/20' : ''} {bid.bidder_info?.id === $user?.id ? 'bg-gradient-to-r from-primary-50 to-blue-50 dark:from-primary-900/20 dark:to-blue-900/20' : ''}"
              transition:fly="{{ y: 20, duration: 300, delay: index * 50 }}"
            >
              <div class="flex justify-between items-start">
                <div class="flex items-center space-x-3">
                  {#if index === 0}
                    <div class="w-10 h-10 bg-gradient-to-r from-amber-400 to-orange-500 rounded-full flex items-center justify-center shadow-md">
                      <svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M5 2a1 1 0 011 1v1h1a1 1 0 010 2H6v1a1 1 0 01-2 0V6H3a1 1 0 010-2h1V3a1 1 0 011-1zm0 10a1 1 0 011 1v1h1a1 1 0 110 2H6v1a1 1 0 11-2 0v-1H3a1 1 0 110-2h1v-1a1 1 0 011-1zM12 2a1 1 0 01.967.744L14.146 7.2 17.5 9.134a1 1 0 010 1.732L14.146 12.8l-1.179 4.456a1 1 0 01-1.934 0L9.854 12.8 6.5 10.866a1 1 0 010-1.732L9.854 7.2l1.179-4.456A1 1 0 0112 2z" clip-rule="evenodd" />
                      </svg>
                    </div>
                  {:else}
                    <div class="w-10 h-10 bg-gray-100 dark:bg-gray-600 rounded-full flex items-center justify-center">
                      <span class="text-sm font-medium text-gray-600 dark:text-gray-300">
                        #{index + 1}
                      </span>
                    </div>
                  {/if}
                  
                  <div>
                    <div class="flex items-center space-x-2 mb-1">
                      <p class="text-lg font-bold text-gray-900 dark:text-white">
                        {formatCurrency(bid.amount)}
                      </p>
                      {#if index === 0}
                        <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200">
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
                  <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">
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

<!-- Quick Bid Confirmation Modal -->
<Modal
  bind:show={showQuickBidConfirm}
  title="Confirm Your Bid"
  maxWidth="md"
>
  {#if selectedQuickBid}
    <div class="p-6">
      <div class="text-center mb-6">
        <div class="w-16 h-16 bg-gradient-to-r {selectedQuickBid.gradient} rounded-full flex items-center justify-center mx-auto mb-4">
          <span class="text-2xl">{selectedQuickBid.icon}</span>
        </div>
        <h3 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          {formatCurrency(selectedQuickBid.amount)}
        </h3>
        <p class="text-gray-600 dark:text-gray-400">
          Are you sure you want to place this bid?
        </p>
      </div>
      
      <div class="bg-yellow-50 dark:bg-yellow-900/20 p-4 rounded-lg border border-yellow-200 dark:border-yellow-800 mb-6">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-3">
            <h3 class="text-sm font-medium text-yellow-800 dark:text-yellow-200">
              Bid Agreement
            </h3>
            <div class="mt-1 text-sm text-yellow-700 dark:text-yellow-300">
              <p>By placing this bid, you agree to the terms and conditions of this auction.</p>
            </div>
          </div>
        </div>
      </div>
      
      <div class="flex justify-end space-x-3">
        <Button
          variant="outline"
          on:click={() => showQuickBidConfirm = false}
          disabled={submitting}
        >
          Cancel
        </Button>
        
        <Button
          variant="primary"
          loading={submitting}
          disabled={submitting}
          on:click={confirmQuickBid}
        >
          {#if submitting}
            Placing Bid...
          {:else}
            Confirm Bid
          {/if}
        </Button>
      </div>
    </div>
  {/if}
</Modal>

<!-- Advanced Bidding Modal -->
<Modal
  bind:show={showAdvancedBidModal}
  title="Advanced Bidding Options"
  maxWidth="lg"
>
  <form on:submit|preventDefault={handleCustomBid} class="space-y-6 p-6">
    <div class="bg-primary-50 dark:bg-primary-900/20 p-4 rounded-lg">
      <h4 class="text-lg font-semibold text-primary-900 dark:text-primary-100 mb-2">
        Smart Bidding Features
      </h4>
      <p class="text-sm text-primary-700 dark:text-primary-300">
        Set your maximum bid and let our system automatically bid for you up to that amount.
      </p>
    </div>
    
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <FormField
        type="number"
        id="bid_amount"
        label="Current Bid Amount"
        bind:value={bidAmount}
        min={minimumBidAmount}
        step="1"
        required={true}
        helpText="Your immediate bid amount"
      />
      
      <FormField
        type="number"
        id="max_bid_amount"
        label="Maximum Bid (Optional)"
        bind:value={maxBidAmount}
        step="1"
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