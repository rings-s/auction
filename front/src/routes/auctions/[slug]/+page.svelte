<script>
  import { onMount, onDestroy } from 'svelte';
  import { page } from '$app/stores';
  import { t } from '$lib/i18n';
  import { user } from '$lib/stores/user';
  import { 
    fetchAuctionBySlug, 
    fetchAuctionBidsBySlug, 
    placeBid,
    updateAuction,
    canAuctionAcceptBids,  
    debugAuctionBiddingState,
    getAuctionStatus
  } from '$lib/api/auction';
  
  import Breadcrumb from '$lib/components/ui/Breadcrumb.svelte';
  import LoadingSkeleton from '$lib/components/ui/LoadingSkeleton.svelte';
  import Alert from '$lib/components/ui/Alert.svelte';
  
  // Auction-specific components
  import AuctionHeader from '$lib/components/auction/detail/AuctionHeader.svelte';
  import AuctionBiddingSection from '$lib/components/auction/detail/AuctionBiddingSection.svelte';
  import AuctionContentTabs from '$lib/components/auction/detail/AuctionContentTabs.svelte';
  import AuctionSidebar from '$lib/components/auction/detail/AuctionSidebar.svelte';
  import AuctionModals from '$lib/components/auction/detail/AuctionModals.svelte';
  
  // State management
  let auction = null;
  let property = null;
  let bids = [];
  let loading = true;
  let bidsLoading = false;
  let error = null;
  let bidError = '';
  let bidSuccess = '';
  let refreshInterval;
  
  // Enhanced bidding state
  let bidAmount = '';
  let maxBidAmount = '';
  let placingBid = false;
  let enableAutoBidding = false;
  let bidNotes = '';
  let isRegistered = true;
  
  // Modal states
  let showBidModal = false;
  let showLoginModal = false;
  let showExtendModal = false;
  let showRegisterModal = false;
  
  // Auction extension
  let extensionHours = 24;
  let extensionReason = '';
  
  // Reactive variables
  $: slug = $page.params.slug;
  $: isLiveAuction = auction?.status === 'live';
  $: isScheduledAuction = auction?.status === 'scheduled';
  $: isActiveAuction = auction?.status === 'live' || auction?.status === 'scheduled';
  $: canBid = (
    $user && 
    auction?.is_biddable &&
    !isOwner && 
    isRegistered
  );
  $: canRegister = (isLiveAuction || isScheduledAuction) && $user && !isOwner && !isRegistered;
  $: showBidSection = (isLiveAuction || isScheduledAuction);
  $: isOwner = $user && auction?.created_by?.id === $user?.id;
  $: minimumBidAmount = calculateMinimumBid();
  $: userHighestBid = getUserHighestBid();
  $: breadcrumbItems = [
    { label: $t('nav.home'), href: '/' },
    { label: $t('nav.auctions'), href: '/auctions' },
    { label: auction?.title || 'Loading...', href: `/auctions/${slug}`, active: true }
  ];
  
  // Helper functions
  function calculateMinimumBid() {
    if (!auction) return 0;
    const currentBid = auction.current_bid || auction.starting_bid;
    const increment = auction.minimum_increment || 100;
    return parseFloat(currentBid) + parseFloat(increment);
  }
  
  function getUserHighestBid() {
    if (!$user || !bids.length) return null;
    return bids.find(bid => bid.bidder_info?.id === $user.id);
  }
  

  
  async function loadAuctionData() {
    loading = true;
    error = null;
    
    try {
      const auctionData = await fetchAuctionBySlug(slug);
      auction = auctionData;
      
      if (auction.id) {
        const statusInfo = await getAuctionStatus(auction.id);
        auction = { 
          ...auction, 
          is_biddable: statusInfo.is_biddable,
          is_active: statusInfo.is_active,
          time_remaining: statusInfo.time_remaining,
          current_bid: statusInfo.current_bid,
          minimum_next_bid: statusInfo.minimum_next_bid
        };
      }
      
      if (auction.related_property) {
        property = auction.related_property;
      }
      
      
      if ($user) {
        isRegistered = true;
      }
      
    } catch (err) {
      console.error('Error loading auction details:', err);
      error = err.message;
    } finally {
      loading = false;
    }
  }
  
  async function loadAuctionBids() {
    if (!auction) return;
    
    bidsLoading = true;
    
    try {
      const response = await fetchAuctionBidsBySlug(slug);
      bids = Array.isArray(response) ? response : (response.results || []);
    } catch (err) {
      console.error('Error loading auction bids:', err);
      bids = [];
    } finally {
      bidsLoading = false;
    }
  }
  
  async function handleBidSubmission() {
    const bidValue = parseFloat(bidAmount);
    const maxBidValue = maxBidAmount ? parseFloat(maxBidAmount) : null;
    
    bidError = '';
    bidSuccess = '';
    
    if (isNaN(bidValue)) {
      bidError = 'Please enter a valid bid amount';
      return;
    }
    
    if (bidValue <= 0) {
      bidError = 'Bid amount must be greater than zero';
      return;
    }
    
    try {
      const statusCheck = await getAuctionStatus(auction.id);
      const realTimeMinBid = statusCheck.minimum_next_bid;
      
      if (bidValue < realTimeMinBid) {
        bidError = `Bid must be at least $${realTimeMinBid.toLocaleString()}`;
        return;
      }
      
      if (!statusCheck.is_biddable) {
        bidError = `Cannot place bid: Auction is ${statusCheck.status_display}`;
        return;
      }
    } catch (error) {
      bidError = 'Unable to verify auction status. Please try again.';
      return;
    }
    
    if (maxBidValue && maxBidValue < bidValue) {
      bidError = 'Maximum bid cannot be less than current bid';
      return;
    }
    
    try {
      placingBid = true;
      
      const bidResponse = await placeBid(auction.id, bidValue, maxBidValue);
      
      bidSuccess = 'Bid placed successfully!';
      showBidModal = false;
      
      bidAmount = '';
      maxBidAmount = '';
      bidNotes = '';
      enableAutoBidding = false;
      
      await Promise.all([loadAuctionData(), loadAuctionBids()]);
      quickBidAmounts = generateQuickBidAmounts();
      
    } catch (err) {
      console.error('❌ BID ERROR:', err);
      bidError = err.message || 'Failed to place bid. Please try again.';
    } finally {
      placingBid = false;
    }
  }
  
  async function handleQuickBid(amount) {
    if (placingBid) return;
    
    if (!$user) {
      showLoginModal = true;
      return;
    }
    
    if (!isRegistered) {
      showRegisterModal = true;
      return;
    }
    
    if (!canBid) {
      bidError = 'Cannot place bid at this time';
      return;
    }
    
    bidAmount = amount.toString();
    await handleBidSubmission();
  }
  
  function openBidModal() {
    if (!$user) {
      showLoginModal = true;
      return;
    }
    
    if (!isRegistered) {
      showRegisterModal = true;
      return;
    }
    
    bidError = '';
    bidSuccess = '';
    bidAmount = minimumBidAmount.toString();
    maxBidAmount = '';
    bidNotes = '';
    enableAutoBidding = false;
    showBidModal = true;
  }
  
  async function handleAuctionRegistration() {
    try {
      isRegistered = true;
      showRegisterModal = false;
      bidSuccess = 'Successfully registered for auction! You can now place bids.';
    } catch (err) {
      console.error('Error registering for auction:', err);
      bidError = 'Failed to register for auction. Please try again.';
    }
  }
  
  async function handleExtendAuction() {
    try {
      if (!extensionHours || extensionHours < 1) {
        bidError = 'Please enter a valid extension time';
        return;
      }
      
      const currentEndDate = new Date(auction.end_date);
      const newEndDate = new Date(currentEndDate.getTime() + (extensionHours * 60 * 60 * 1000));
      
      const updatedAuction = await updateAuction(auction.id, {
        end_date: newEndDate.toISOString(),
        extension_reason: extensionReason
      });
      
      auction = { ...auction, ...updatedAuction };
      showExtendModal = false;
      bidSuccess = `Auction extended by ${extensionHours} hours`;
      
    } catch (err) {
      console.error('Error extending auction:', err);
      bidError = err.message || 'Failed to extend auction';
    }
  }
  
  function handleTimerEnd() {
    loadAuctionData();
    loadAuctionBids();
  }
  
  onMount(async () => {
    await loadAuctionData();
    await loadAuctionBids();
    
    refreshInterval = setInterval(async () => {
      if (!placingBid) {
        await Promise.all([loadAuctionData(), loadAuctionBids()]);
        quickBidAmounts = generateQuickBidAmounts();
      }
    }, 30000);
  });
  
  onDestroy(() => {
    if (refreshInterval) {
      clearInterval(refreshInterval);
    }
  });
</script>

<svelte:head>
  <title>{auction?.title || 'Loading...'} | {$t('nav.auctions')}</title>
  <meta name="description" content={auction?.description || 'Loading auction details...'} />
  {#if auction}
    <meta property="og:title" content={auction.title} />
    <meta property="og:description" content={auction.description} />
    <meta property="og:type" content="website" />
    <meta property="og:url" content={`${$page.url.origin}/auctions/${auction.slug}`} />
    {#if auction.related_property?.main_image?.url}
      <meta property="og:image" content={auction.related_property.main_image.url} />
    {/if}
  {/if}
</svelte:head>

<!-- Main Container -->
<div class="min-h-screen  ">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
    
    <!-- Breadcrumbs -->
    <div class="mb-6">
      <Breadcrumb items={breadcrumbItems} />
    </div>
    
    {#if loading}
      <!-- Loading State -->
      <div class="space-y-6">
        <LoadingSkeleton type="auctionHeader" />
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div class="lg:col-span-2 space-y-6">
            <LoadingSkeleton type="auctionContent" />
          </div>
          <div class="space-y-4">
            <LoadingSkeleton type="auctionSidebar" />
          </div>
        </div>
      </div>
      
    {:else if error}
      <!-- Error State -->
      <div class="text-center py-12">
        <Alert 
          type="error"
          title={$t('error.title')}
          message={error}
          action={{
            label: $t('auctions.backToAuctions'),
            href: '/auctions'
          }}
        />
      </div>
      
    {:else if auction}
      <!-- Success/Error Messages -->
      {#if bidSuccess}
        <div class="mb-6">
          <Alert type="success" message={bidSuccess} dismissible={true} />
        </div>
      {/if}
      
      {#if bidError}
        <div class="mb-6">
          <Alert type="error" message={bidError} dismissible={true} />
        </div>
      {/if}
      
      <!-- Auction Header -->
      <AuctionHeader 
        {auction} 
        {isOwner}
        viewCount={auction.view_count || 0}
        bidCount={auction.bid_count || bids.length}
      />
      
      <!-- Bidding Section -->
      {#if showBidSection}
      <AuctionBiddingSection
        {auction}
        {bids}
        {canBid}
        {canRegister}
        {isLiveAuction}
        {isScheduledAuction}
        {placingBid}
        {userHighestBid}
        {minimumBidAmount}
        user={$user}
        onOpenBidModal={openBidModal}
        onShowRegisterModal={() => showRegisterModal = true}
      />
      {/if}
      
      <!-- Main Content Grid -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        <!-- Content Area -->
        <div class="lg:col-span-2 space-y-6">
          <AuctionContentTabs 
            {auction}
            {property}
            {bids}
            {bidsLoading}
            {canBid}
            user={$user}
            onLoadBids={loadAuctionBids}
            onOpenBidModal={openBidModal}
          />
        </div>
        
        <!-- Sidebar -->
        <div class="space-y-4">
          <AuctionSidebar
            {auction}
            {property}
            {bids}
            {canBid}
            {canRegister}
            {isOwner}
            {isLiveAuction}
            {isScheduledAuction}
            {isActiveAuction}
            {isRegistered}
            {placingBid}
            {minimumBidAmount}
            user={$user}
            onTimerEnd={handleTimerEnd}
            onOpenBidModal={openBidModal}
            onShowRegisterModal={() => showRegisterModal = true}
            onShowExtendModal={() => showExtendModal = true}
          />
        </div>
      </div>
    {/if}
  </div>
</div>

<!-- Modals -->
<AuctionModals
  {auction}
  {bidError}
  {minimumBidAmount}
  {placingBid}
  bind:showBidModal
  bind:showLoginModal
  bind:showRegisterModal
  bind:showExtendModal
  bind:bidAmount
  bind:maxBidAmount
  bind:bidNotes
  bind:enableAutoBidding
  bind:extensionHours
  bind:extensionReason
  onBidSubmission={handleBidSubmission}
  onAuctionRegistration={handleAuctionRegistration}
  onExtendAuction={handleExtendAuction}
/>