<!-- front/src/lib/components/auction/LiveBidding.svelte -->
<script>
  import { onMount, onDestroy, createEventDispatcher } from 'svelte';
  import { user } from '$lib/stores/user';
  import { t } from '$lib/i18n';
  import { fetchAuctionBids, placeBid } from '$lib/api/auction';
  import Button from '$lib/components/ui/Button.svelte';
  import FormField from '$lib/components/ui/FormField.svelte';
  import Alert from '$lib/components/ui/Alert.svelte';
  import Modal from '$lib/components/ui/Modal.svelte';
  import AuctionStatus from './AuctionStatus.svelte';
  import { fly, scale, fade } from 'svelte/transition';
  import { quintOut } from 'svelte/easing';
  
  // Import currency utilities
  import { formatCurrency, parseCurrencyInput, validateBidAmount } from '$lib/utils/currency.js';
  
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
  
  // Computed values with NaN protection
  $: minimumBidAmount = calculateMinimumBid();
  $: canBid = auction?.status === 'live' && $user && !isOwner && auction?.end_date > new Date().toISOString();
  $: highestBid = bids.length > 0 ? bids[0] : null;
  $: userBids = bids.filter(bid => bid.bidder_info?.id === $user?.id);
  $: userHighestBid = userBids.length > 0 ? userBids[0] : null;
  $: bidIncrement = parseFloat(auction?.minimum_increment) || 100;
  $: isUserWinning = userHighestBid?.id === highestBid?.id;
  
  function calculateMinimumBid() {
    if (!auction) return 0;
    
    const currentBid = parseCurrencyInput(auction.current_bid || auction.starting_bid || 0);
    const increment = parseCurrencyInput(auction.minimum_increment || 100);
    
    return currentBid + increment;
  }
  
  function generateQuickBidOptions() {
    const minBid = minimumBidAmount;
    
    if (minBid <= 0) {
      quickBidOptions = [];
      return;
    }
    
    quickBidOptions = [
      { 
        amount: minBid, 
        label: $t('auction.minBidLabel'), 
        description: formatCurrency(minBid),
        icon: '⚡',
        gradient: 'from-blue-500 to-blue-600'
      },
      { 
        amount: minBid + bidIncrement, 
        label: $t('auction.incrementLabel', { increment: bidIncrement }), 
        description: formatCurrency(minBid + bidIncrement),
        icon: '🎯',
        gradient: 'from-emerald-500 to-emerald-600'
      },
      { 
        amount: minBid + (bidIncrement * 2), 
        label: '+2x', 
        description: formatCurrency(minBid + (bidIncrement * 2)),
        icon: '🚀',
        gradient: 'from-amber-500 to-orange-500'
      },
      { 
        amount: minBid + (bidIncrement * 5), 
        label: $t('auction.powerLabel'), 
        description: formatCurrency(minBid + (bidIncrement * 5)),
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
      
      // Validate bid amount
      const validation = validateBidAmount(selectedQuickBid.amount, minimumBidAmount);
      if (!validation.isValid) {
        error = $t(`auction.${validation.error}`, validation.params || {});
        return;
      }
      
      await placeBid(auction.id, selectedQuickBid.amount);
      
      success = $t('auction.bidPlaced');
      bidAmount = '';
      
      await loadBids();
      onBidPlaced();
      generateQuickBidOptions();
      
    } catch (err) {
      console.error('Error placing bid:', err);
      error = err.message || $t('auction.bidFailed');
    } finally {
      submitting = false;
      selectedQuickBid = null;
    }
  }
  
  async function handleCustomBid() {
    const amount = parseCurrencyInput(bidAmount);
    
    // Validate bid amount
    const validation = validateBidAmount(amount, minimumBidAmount);
    if (!validation.isValid) {
      error = $t(`auction.${validation.error}`, validation.params || {});
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
      error = err.message || $t('auction.bidFailed');
    } finally {
      submitting = false;
    }
  }
  
  async function handleEndAuction() {
    if (!selectedWinningBid) {
      error = $t('auction.selectWinningBid');
      return;
    }
    
    try {
      success = $t('auction.auctionEndedSuccessfully');
      showOwnerControlsModal = false;
      dispatch('auctionEnded', { winningBid: selectedWinningBid, notes: auctionNotes });
      
    } catch (err) {
      error = $t('auction.endAuctionFailed');
    }
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
    
    if (diffInSeconds < 60) return $t('common.justNow');
    if (diffInSeconds < 3600) return $t('common.minutesAgo', { count: Math.floor(diffInSeconds / 60) });
    if (diffInSeconds < 86400) return $t('common.hoursAgo', { count: Math.floor(diffInSeconds / 3600) });
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

<!-- Rest of the component template with updated currency formatting -->
<!-- Bid Notifications -->
{#if newBidNotifications.length > 0}
  <div class="fixed top-20 right-4 z-50 space-y-3" role="alert" aria-live="polite">
    {#each newBidNotifications as notification (notification.id)}
      <div 
        class="bg-white dark:bg-gray-800 border-l-4 border-primary-500 rounded-r-xl shadow-xl p-4 max-w-sm backdrop-blur-sm text-xs"
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
              {$t('auction.newBidPlaced')}
            </p>
            <p class="text-lg font-bold text-primary-600 dark:text-primary-400 mt-1">
              {formatCurrency(notification.bid.amount)}
            </p>
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-1 truncate">
              {$t('auction.byBidder', { name: notification.bid.bidder_info?.name || $t('auction.anonymous') })}
            </p>
          </div>
        </div>
      </div>
    {/each}
  </div>
{/if}

<div class="space-y-3 p-3 bg-white rounded-lg shadow-sm border border-gray-100 dark:border-gray-700">
  <!-- Header -->
  <div class="flex items-center justify-between pb-1 border-b border-gray-100 dark:border-gray-700">
    <h3 class="text-xs font-semibold text-gray-700 dark:text-gray-200">
      {$t('auction.liveBidding')}
      <span class="ml-1 text-[0.7rem] font-medium text-green-600 bg-green-100 px-1.5 py-0.5 rounded-full">
        ● {$t('auction.live')}
      </span>
    </h3>
    <span class="text-[0.7rem] text-gray-500 dark:text-gray-400">
      {$t('auction.participants', { count: activeBidders })}
    </span>
  </div>

  <!-- Current Bid -->
  <div class="space-y-1">
    <div class="flex items-center justify-between text-xs">
      <span class="text-gray-500 dark:text-gray-400">{$t('auction.currentBid')}</span>
      <span class="font-semibold text-primary-600 dark:text-primary-400">
        {formatCurrency(auction?.current_bid || auction?.starting_bid)}
      </span>
    </div>
    <div class="flex items-center justify-between text-[0.7rem]">
      <span class="text-gray-400">{$t('auction.nextMinBid')}</span>
      <span class="text-gray-600 dark:text-gray-300">
        {formatCurrency(minimumBidAmount)}
      </span>
    </div>
  </div>

  <!-- Bid Input -->
  {#if canBid}
    <div class="space-y-2">
      <div class="flex gap-1.5">
        <input
          type="number"
          bind:value={bidAmount}
          class="w-full px-2 py-1.5 text-xs border border-gray-300 rounded-md focus:ring-1 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-800 dark:border-gray-600"
          placeholder={formatCurrency(minimumBidAmount)}
          min={minimumBidAmount}
          step="1"
        />
        <button
          on:click={handleCustomBid}
          disabled={submitting || !bidAmount || parseCurrencyInput(bidAmount) < minimumBidAmount}
          class="px-2.5 py-1.5 text-xs font-medium text-white bg-primary-500 hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed rounded-md transition-colors focus:ring-1 focus:ring-primary-500 focus:ring-offset-1"
        >
          {$t('auction.bid')}
        </button>
      </div>
      <div class="grid grid-cols-3 gap-1.5">
        {#each [1, 5, 10] as multiplier}
          <button
            on:click={() => handleQuickBid({ amount: minimumBidAmount + (bidIncrement * multiplier) })}
            disabled={submitting}
            class="text-[0.7rem] p-1 bg-gray-50 hover:bg-gray-100 disabled:opacity-50 text-gray-700 rounded-sm transition-colors dark:bg-gray-700 dark:text-gray-300"
          >
            +{multiplier}x
          </button>
        {/each}
      </div>
    </div>
  {:else if isOwner}
    <!-- Owner controls remain the same -->
  {:else}
    <div class="space-y-2">
      <Button
        variant="primary"
        size="large"
        href={`/login?redirect=/auctions/${auction.slug || auction.id}`}
        class="px-8 py-3"
      >
        <svg class="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
        </svg>
        {$t('auction.loginToPlaceBid')}
      </Button>
    </div>
  {/if}

  <!-- Bidding History -->
  <div class="pt-1 border-t border-gray-100 dark:border-gray-700">
    <h4 class="text-[0.7rem] font-medium text-gray-500 mb-1 dark:text-gray-400">
      {$t('auction.recentBids')}
    </h4>
    <div class="space-y-1">
      {#each bids.slice(0, 5) as bid}
        <div class="flex items-center justify-between text-[0.7rem]">
          <span class="text-gray-600 dark:text-gray-300">{bid.bidder_info?.name || $t('auction.anonymous')}</span>
          <span class="font-medium text-primary-600 dark:text-primary-400">
            {formatCurrency(bid.amount)}
          </span>
        </div>
      {/each}
    </div>
  </div>
</div>

<!-- Quick Bid Confirmation Modal -->
<Modal
  bind:show={showQuickBidConfirm}
  title={$t('auction.confirmBid')}
  maxWidth="md"
>
  {#if selectedQuickBid}
    <div class="p-6 text-xs">
      <div class="text-center mb-6">
        <div class="w-16 h-16 bg-gradient-to-r {selectedQuickBid.gradient} rounded-full flex items-center justify-center mx-auto mb-4">
          <span class="text-2xl">{selectedQuickBid.icon}</span>
        </div>
        <h3 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          {formatCurrency(selectedQuickBid.amount)}
        </h3>
        <p class="text-gray-600 dark:text-gray-400">
          {$t('auction.confirmBidMessage')}
        </p>
      </div>
      
      <div class="bg-yellow-50 dark:bg-yellow-900/20 p-4 rounded-lg border border-yellow-200 dark:border-yellow-800 mb-6">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-yellow-400" fill="currentColor" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7" />
            </svg>
          </div>
          <div class="ml-3">
            <h3 class="text-sm font-medium text-yellow-800 dark:text-yellow-200">
              {$t('auction.bidAgreement')}
            </h3>
            <div class="mt-1 text-sm text-yellow-700 dark:text-yellow-300">
              <p>{$t('auction.bidDisclaimer')}</p>
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
          {$t('common.cancel')}
        </Button>
        
        <Button
          variant="primary"
          loading={submitting}
          disabled={submitting}
          on:click={confirmQuickBid}
        >
          {#if submitting}
            {$t('auction.placingBid')}
          {:else}
            {$t('auction.confirmBid')}
          {/if}
        </Button>
      </div>
    </div>
  {/if}
</Modal>

<!-- Advanced Bidding Modal with currency formatting -->
<Modal
 bind:show={showAdvancedBidModal}
 title={$t('auction.advancedBidding')}
 maxWidth="lg"
>
 <form on:submit|preventDefault={handleCustomBid} class="space-y-6 p-6 text-xs">
   <div class="bg-primary-50 dark:bg-primary-900/20 p-4 rounded-lg">
     <h4 class="text-lg font-semibold text-primary-900 dark:text-primary-100 mb-2">
       {$t('auction.smartBiddingFeatures')}
     </h4>
     <p class="text-sm text-primary-700 dark:text-primary-300">
       {$t('auction.autoBidHelp')}
     </p>
   </div>
   
   <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
     <FormField
       type="number"
       id="bid_amount"
       label={$t('auction.bidAmount')}
       bind:value={bidAmount}
       min={minimumBidAmount}
       step="1"
       required={true}
       helpText={$t('auction.currentBidAmount')}
       placeholder={formatCurrency(minimumBidAmount)}
     />
     
     <FormField
       type="number"
       id="max_bid_amount"
       label={$t('auction.maxBidAmount')}
       bind:value={maxBidAmount}
       step="1"
       helpText={$t('auction.autoBidHelp')}
       placeholder={formatCurrency(minimumBidAmount * 2)}
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
         {$t('auction.enableAutoBidding')}
       </span>
     </label>
     <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
       {$t('auction.autoBidHelp')}
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
       {$t('common.cancel')}
     </Button>
     
     <Button
       variant="primary"
       type="submit"
       loading={submitting}
       disabled={submitting || !bidAmount || parseCurrencyInput(bidAmount) < minimumBidAmount}
     >
       {$t('auction.placeBid')}
     </Button>
   </div>
 </form>
</Modal>

<!-- Owner Controls Modal remains the same but with currency formatting -->
<Modal
 bind:show={showOwnerControlsModal}
 title={$t('auction.selectWinner')}
 maxWidth="xl"
>
 <div class="p-6 space-y-6 text-xs">
   <div class="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg">
     <h4 class="text-lg font-semibold text-purple-900 dark:text-purple-100 mb-2">
       {$t('auction.chooseWinningBid')}
     </h4>
     <p class="text-sm text-purple-700 dark:text-purple-300">
       {$t('auction.selectWinnerDescription')}
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
                 {bid.bidder_info?.name || $t('auction.anonymous')} • {formatDateTime(bid.bid_time)}
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
     label={$t('auction.closingNotes')}
     bind:value={auctionNotes}
     rows={3}
     helpText={$t('auction.closingNotesHelp')}
   />
   
   {#if error}
     <Alert type="error" message={error} />
   {/if}
   
   <div class="flex justify-end space-x-3">
     <Button
       variant="outline"
       on:click={() => showOwnerControlsModal = false}
     >
       {$t('common.cancel')}
     </Button>
     
     <Button
       variant="primary"
       on:click={handleEndAuction}
       disabled={!selectedWinningBid}
     >
       <svg class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
         <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
       </svg>
       {$t('auction.endAuctionSelectWinner')}
     </Button>
   </div>
 </div>
</Modal>