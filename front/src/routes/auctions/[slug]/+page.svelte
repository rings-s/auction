<!-- src/routes/auctions/[slug]/+page.svelte -->
<script>
  import { onMount, onDestroy } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
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
  import AuctionStatus from '$lib/components/auction/AuctionStatus.svelte';
  import PropertyCard from '$lib/components/properties/PropertyCard.svelte';
  import CountdownTimer from '$lib/components/auction/CountdownTimer.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Tabs from '$lib/components/ui/Tabs.svelte';
  import Modal from '$lib/components/ui/Modal.svelte';
  import Alert from '$lib/components/ui/Alert.svelte';
  import LoadingSkeleton from '$lib/components/ui/LoadingSkeleton.svelte';
  import ShareButtons from '$lib/components/shared/ShareButtons.svelte';
  import FormField from '$lib/components/ui/FormField.svelte';
  import Gallery from '$lib/components/ui/Gallery.svelte';
  
  let auction = null;
  let property = null;
  let bids = [];
  let loading = true;
  let bidsLoading = false;
  let error = null;
  let bidError = '';
  let bidSuccess = '';
  let activeTab = 'details';
  let showBidModal = false;
  let showLoginModal = false;
  let showExtendModal = false;
  let showRegisterModal = false;
  let refreshInterval;
  
  // Enhanced bidding state
  let bidAmount = '';
  let maxBidAmount = '';
  let placingBid = false;
  let quickBidAmounts = [];
  let enableAutoBidding = false;
  let bidNotes = '';
  let isRegistered = true; // Default to true for testing - in real app, check registration status
  
  // Auction extension
  let extensionHours = 24;
  let extensionReason = '';
  
  $: slug = $page.params.slug;
  $: isLiveAuction = auction?.status === 'live';
  $: isScheduledAuction = auction?.status === 'scheduled';
  $: isActiveAuction = auction?.status === 'live' || auction?.status === 'scheduled';
  


$: canBid = (
  $user && 
  auction?.is_biddable && // Use backend-determined biddability
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
  
  function generateQuickBidAmounts() {
    if (!auction) return [];
    const minBid = minimumBidAmount;
    const increment = parseFloat(auction.minimum_increment) || 100;
    
    return [
      { amount: minBid, label: 'Minimum Bid', color: 'primary' },
      { amount: minBid + increment, label: `+$${increment}`, color: 'secondary' },
      { amount: minBid + (increment * 2), label: `+$${increment * 2}`, color: 'warning' },
      { amount: minBid + (increment * 5), label: `+$${increment * 5}`, color: 'danger' }
    ];
  }
  
  async function loadAuctionData() {
    loading = true;
    error = null;
    
    try {
      const auctionData = await fetchAuctionBySlug(slug);
      auction = auctionData;
      
      // Get real-time status using the backend endpoint
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
        
        console.log('✅ AUCTION LOADED WITH STATUS:', {
          id: auction.id,
          status: auction.status,
          is_biddable: auction.is_biddable,
          is_active: auction.is_active,
          current_bid: auction.current_bid,
          minimum_next_bid: auction.minimum_next_bid
        });
      }
      
      if (auction.related_property) {
        property = auction.related_property;
      }
      
      quickBidAmounts = generateQuickBidAmounts();
      
      // Auto-register user for testing
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
      console.log('Loaded bids:', bids);
      
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
    
    // Clear previous errors
    bidError = '';
    bidSuccess = '';
    
    // Enhanced validation
    if (isNaN(bidValue)) {
      bidError = 'Please enter a valid bid amount';
      return;
    }
    
    if (bidValue <= 0) {
      bidError = 'Bid amount must be greater than zero';
      return;
    }
    
    // Get real-time minimum bid from backend
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
      
      console.log('🚀 STARTING ENHANCED BID PROCESS');
      console.log('Auction ID:', auction.id);
      console.log('Bid Amount:', bidValue);
      console.log('User:', $user?.email);
      
      // Place bid using enhanced API
      const bidResponse = await placeBid(auction.id, bidValue, maxBidValue);
      
      console.log('✅ BID SUCCESS:', bidResponse);
      
      bidSuccess = 'Bid placed successfully!';
      showBidModal = false;
      
      // Reset form
      bidAmount = '';
      maxBidAmount = '';
      bidNotes = '';
      enableAutoBidding = false;
      
      // Reload data
      await Promise.all([loadAuctionData(), loadAuctionBids()]);
      quickBidAmounts = generateQuickBidAmounts();
      
    } catch (err) {
      console.error('❌ BID ERROR:', err);
      bidError = err.message || 'Failed to place bid. Please try again.';
    } finally {
      placingBid = false;
    }
  }
  
  // Reactive logger for bid modal state
  $: {
    if (showBidModal) { // Only log when the modal is open
      console.log('--- Bid Modal Debug ---');
      console.log('bidAmount (raw):', bidAmount);
      console.log('typeof bidAmount:', typeof bidAmount);
      const parsedBidAmount = parseFloat(bidAmount);
      console.log('parseFloat(bidAmount):', parsedBidAmount);
      console.log('minimumBidAmount:', minimumBidAmount);
      console.log('typeof minimumBidAmount:', typeof minimumBidAmount);
      console.log('placingBid:', placingBid);
      
      const isBidAmountEmpty = !bidAmount || String(bidAmount).trim() === '';
      const isBidTooLow = parsedBidAmount < minimumBidAmount;
      
      console.log('Condition !bidAmount (is empty?):', isBidAmountEmpty);
      console.log('Condition parseFloat(bidAmount) < minimumBidAmount (is too low?):', isBidTooLow);
      
      const isDisabled = placingBid || isBidAmountEmpty || isBidTooLow;
      console.log('Button should be disabled:', isDisabled);
      console.log('--- End Bid Modal Debug ---');
    }
  }
  
  // FIXED: Quick bid functionality
  async function handleQuickBid(amount) {
    if (placingBid) return;
    
    console.log('Quick bid clicked:', { amount, canBid, user: $user });
    
    // Check authentication first
    if (!$user) {
      showLoginModal = true;
      return;
    }
    
    // Check registration
    if (!isRegistered) {
      showRegisterModal = true;
      return;
    }
    
    // Check if can bid
    if (!canBid) {
      bidError = 'Cannot place bid at this time';
      return;
    }
    
    bidAmount = amount.toString();
    await handleBidSubmission();
  }
  
  // Open bid modal with prefilled minimum amount
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
  
  // Handle auction registration
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
  
  // Handle auction extension (for owners)
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
  
  function getAllImages() {
    let images = [];
    
    if (auction?.media) {
      const auctionImages = auction.media
        .filter(m => m.media_type === 'image')
        .map(m => ({
          url: m.url || m.file,
          alt: m.name || auction.title,
          caption: m.name || 'Auction Image'
        }));
      images = [...images, ...auctionImages];
    }
    
    if (auction?.related_property?.media) {
      const propertyImages = auction.related_property.media
        .filter(m => m.media_type === 'image')
        .map(m => ({
          url: m.url || m.file,
          alt: m.name || auction.related_property.title,
          caption: m.name || 'Property Image'
        }));
      images = [...images, ...propertyImages];
    }
    
    return images;
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
  
  function getTimeAgo(dateString) {
    const now = new Date();
    const past = new Date(dateString);
    const diffInSeconds = Math.floor((now - past) / 1000);
    
    if (diffInSeconds < 60) return 'Just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
    return `${Math.floor(diffInSeconds / 86400)}d ago`;
  }
  
  function handleTimerEnd() {
    loadAuctionData();
    loadAuctionBids();
  }
  
  onMount(async () => {
    await loadAuctionData();
    await loadAuctionBids();
    
    // Set up refresh interval
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
  
  const tabs = [
    { id: 'details', label: $t('auction.tabDetails') },
    { id: 'property', label: $t('auction.tabProperty') },
    { id: 'bids', label: `${$t('auction.tabBids')} (${bids.length})` },
    { id: 'terms', label: $t('auction.tabTerms') }
  ];
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
<div class="min-h-screen bg-gray-50 dark:bg-gray-900">
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
      
      <!-- Page Header -->
      <header class="mb-8">
        <div class="flex flex-col lg:flex-row lg:items-start justify-between gap-4">
          <div class="flex-1 min-w-0">
            <!-- Status Badges -->
            <div class="flex flex-wrap items-center gap-2 mb-3">
              <AuctionStatus status={auction.status} />
              <span class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200">
                {auction.auction_type === 'sealed' ? $t('auction.typeSealed') :
                 auction.auction_type === 'private' ? $t('auction.typeReserve') :
                 $t('auction.typeNoReserve')}
              </span>
              {#if auction.is_featured}
                <span class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-warning-100 text-warning-800 dark:bg-warning-900 dark:text-warning-200">
                  ⭐ {$t('auction.featured')}
                </span>
              {/if}
            </div>
            
            <!-- Title -->
            <h1 class="text-2xl lg:text-3xl font-bold leading-tight text-gray-900 dark:text-white mb-2">
              {auction.title}
            </h1>
            
            <!-- Metadata -->
            <div class="flex flex-wrap items-center gap-3 text-sm text-gray-500 dark:text-gray-400">
              <span>Auction #{auction.id}</span>
              <span>•</span>
              <span>{auction.view_count || 0} views</span>
              <span>•</span>
              <span>{auction.bid_count || bids.length} bids</span>
            </div>
          </div>
          
          <!-- Action Buttons -->
          <div class="flex flex-wrap items-center gap-2">
            <ShareButtons 
              url={`/auctions/${auction.slug}`} 
              title={auction.title}
              description={auction.description}
            />
            {#if isOwner}
              <Button 
                variant="outline"
                size="small"
                href={`/auctions/${auction.id}/edit`}
                class="inline-flex items-center"
              >
                <svg class="h-4 w-4 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
                {$t('auction.edit')}
              </Button>
            {/if}
          </div>
        </div>
      </header>
      
      <!-- ENHANCED BIDDING SECTION with Fixed Colors and Typography -->
      {#if showBidSection}
        <section class="mb-8">
          <div class="relative overflow-hidden rounded-xl bg-gray-900 dark:bg-gray-800 shadow-lg border border-gray-700">
            <!-- Background Pattern -->
            <div class="absolute inset-0 bg-gradient-to-br from-primary-900/20 via-transparent to-secondary-900/20"></div>
            
            <!-- Content -->
            <div class="relative">
              <!-- Header Section with Improved Typography -->
              <div class="px-4 sm:px-6 py-4 border-b border-gray-700">
                <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div>
                    <h2 class="text-lg sm:text-xl font-bold text-white flex items-center gap-2">
                      {#if isLiveAuction}
                        <span class="flex items-center gap-1.5">
                          <span class="w-2 h-2 bg-danger-400 rounded-full animate-pulse"></span>
                          <span class="text-danger-300 text-sm">🔥</span>
                          LIVE AUCTION
                        </span>
                      {:else if isScheduledAuction}
                        <span class="flex items-center gap-1.5">
                          <span class="w-2 h-2 bg-warning-400 rounded-full animate-pulse"></span>
                          <span class="text-warning-300 text-sm">⏰</span>
                          STARTS SOON
                        </span>
                      {/if}
                    </h2>
                    <div class="flex flex-wrap items-center gap-3 mt-1 text-sm text-gray-300">
                      <span>Current: <span class="font-semibold text-white">{formatCurrency(auction.current_bid || auction.starting_bid)}</span></span>
                      <span>Next: <span class="font-semibold text-primary-300">{formatCurrency(minimumBidAmount)}</span></span>
                    </div>
                  </div>
                  
                  <!-- Bid Count Display -->
                  <div class="text-center sm:text-right">
                    <div class="text-2xl sm:text-3xl font-bold text-white leading-none">
                      {auction.bid_count || bids.length}
                    </div>
                    <div class="text-gray-400 text-xs uppercase tracking-wide font-medium">
                      Total Bids
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Bidding Interface -->
              <div class="p-4 sm:p-6">
                {#if canBid}
                  <div class="space-y-6">
                    <!-- Quick Bid Grid with Improved Design -->
                    <div>
                      <h3 class="text-base font-semibold text-white mb-3">Quick Bid Options</h3>
                      <div class="grid grid-cols-2 lg:grid-cols-4 gap-3">
                        {#each quickBidAmounts as option}
                          <button
                            type="button"
                            class="group relative overflow-hidden rounded-lg p-3 sm:p-4 border border-gray-600 hover:border-primary-400 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-opacity-50 bg-gray-800 hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-105"
                            disabled={placingBid}
                            on:click={() => handleQuickBid(option.amount)}
                          >
                            <div class="flex flex-col items-center space-y-1">
                              <span class="text-base sm:text-lg font-bold text-white">
                                {formatCurrency(option.amount)}
                              </span>
                              <span class="text-xs text-gray-400 font-medium">
                                {option.label}
                              </span>
                            </div>
                            
                            {#if placingBid}
                              <div class="absolute inset-0 bg-gray-900 bg-opacity-50 flex items-center justify-center">
                                <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                              </div>
                            {/if}
                          </button>
                        {/each}
                      </div>
                    </div>
                    
                    <!-- Main Actions -->
                    <div class="flex flex-col sm:flex-row gap-3">
                      <Button
                        variant="primary"
                        size="default"
                        class="flex-1 font-semibold bg-primary-600 hover:bg-primary-700 border-0"
                        on:click={openBidModal}
                        disabled={placingBid}
                      >
                        <svg class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                        </svg>
                        PLACE CUSTOM BID
                      </Button>
                      
                      {#if userHighestBid}
                        <div class="flex-1 bg-gray-800 border border-gray-600 rounded-lg p-3 text-center">
                          <div class="text-xs text-gray-400 mb-1">Your Highest Bid</div>
                          <div class="text-lg font-bold text-white mb-1">
                            {formatCurrency(userHighestBid.amount)}
                          </div>
                          <div class="text-xs font-medium">
                            {#if userHighestBid.status === 'winning'}
                              <span class="text-success-400">🎉 Winning!</span>
                            {:else}
                              <span class="text-warning-400">⚠️ Outbid</span>
                            {/if}
                          </div>
                        </div>
                      {/if}
                    </div>
                    
                    <!-- Scheduled Auction Notice -->
                    {#if isScheduledAuction}
                      <div class="bg-warning-900/30 border border-warning-600/30 rounded-lg p-3">
                        <div class="flex items-start gap-2">
                          <svg class="h-4 w-4 text-warning-400 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          <div>
                            <h4 class="text-warning-200 font-medium text-sm mb-1">Pre-Bidding Available</h4>
                            <p class="text-warning-300 text-xs">
                              Place bids now that will become active when the auction starts.
                            </p>
                          </div>
                        </div>
                      </div>
                    {/if}
                  </div>
                  
                {:else if canRegister}
                  <!-- Registration CTA -->
                  <div class="text-center py-6">
                    <div class="bg-gray-800 border border-gray-600 rounded-lg p-4 max-w-sm mx-auto">
                      <div class="w-12 h-12 bg-primary-600/20 rounded-full flex items-center justify-center mx-auto mb-3">
                        <svg class="w-6 h-6 text-primary-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                      </div>
                      <h3 class="text-lg font-bold text-white mb-2">
                        Join This Auction
                      </h3>
                      <p class="text-gray-400 mb-4 text-sm">
                        Register to participate in this auction
                      </p>
                      <Button
                        variant="primary"
                        size="default"
                        class="font-semibold bg-primary-600 hover:bg-primary-700"
                        on:click={() => showRegisterModal = true}
                      >
                        <svg class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
                        </svg>
                        REGISTER FOR AUCTION
                      </Button>
                    </div>
                  </div>
                  
                {:else if !$user}
                  <!-- Sign In CTA -->
                  <div class="text-center py-6">
                    <div class="bg-gray-800 border border-gray-600 rounded-lg p-4 max-w-sm mx-auto">
                      <div class="w-12 h-12 bg-primary-600/20 rounded-full flex items-center justify-center mx-auto mb-3">
                        <svg class="w-6 h-6 text-primary-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                        </svg>
                      </div>
                      <h3 class="text-lg font-bold text-white mb-2">
                        Sign In to Bid
                      </h3>
                      <p class="text-gray-400 mb-4 text-sm">
                        Create an account to participate
                      </p>
                      <Button
                        variant="primary"
                        size="default"
                        class="font-semibold bg-primary-600 hover:bg-primary-700"
                        href={`/login?redirect=/auctions/${auction.slug}`}
                      >
                        <svg class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
                        </svg>
                        SIGN IN TO BID
                      </Button>
                    </div>
                  </div>
                {/if}
              </div>
            </div>
          </div>
        </section>
      {/if}
      
      <!-- Main Content Grid -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        <!-- Content Area -->
        <div class="lg:col-span-2 space-y-6">
          
          <!-- Image Gallery -->
          <section class="bg-white dark:bg-gray-800 rounded-lg shadow-sm overflow-hidden">
            <Gallery 
              images={getAllImages()} 
              alt={auction.title}
              showThumbnails={true}
            />
          </section>
          
          <!-- Navigation Tabs -->
          <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm overflow-hidden">
            <div class="border-b border-gray-200 dark:border-gray-700">
              <Tabs {tabs} bind:activeTab />
            </div>
            
            <!-- Tab Content -->
            <div class="p-4 sm:p-6">
              {#if activeTab === 'details'}
                <div class="prose dark:prose-invert max-w-none">
                  <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-4">
                    {$t('auction.description')}
                  </h2>
                  
                  {#if auction.description}
                    <div class="text-gray-600 dark:text-gray-300 leading-relaxed mb-6">
                      <p class="whitespace-pre-wrap">{auction.description}</p>
                    </div>
                  {:else}
                    <div class="text-center py-6 text-gray-500 dark:text-gray-400">
                      <svg class="w-10 h-10 mx-auto mb-2 opacity-40" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                      <p class="text-sm">{$t('auction.noDescription')}</p>
                    </div>
                  {/if}
                  
                  <!-- Key Information Cards -->
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <!-- Schedule Card -->
                    <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                      <h3 class="text-base font-semibold text-gray-900 dark:text-white mb-3 flex items-center">
                        <svg class="w-4 h-4 mr-2 text-primary-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        {$t('auction.schedule')}
                      </h3>
                      <dl class="space-y-2">
                        <div class="flex justify-between items-center">
                          <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
                            {$t('auction.startDate')}
                          </dt>
                          <dd class="text-sm font-semibold text-gray-900 dark:text-white">
                            {formatDateTime(auction.start_date)}
                          </dd>
                        </div>
                        <div class="flex justify-between items-center">
                          <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
                            {$t('auction.endDate')}
                          </dt>
                          <dd class="text-sm font-semibold text-gray-900 dark:text-white">
                            {formatDateTime(auction.end_date)}
                          </dd>
                        </div>
                        {#if auction.registration_deadline}
                          <div class="flex justify-between items-center">
                            <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
                              {$t('auction.registrationDeadline')}
                            </dt>
                            <dd class="text-sm font-semibold text-gray-900 dark:text-white">
                              {formatDateTime(auction.registration_deadline)}
                            </dd>
                          </div>
                        {/if}
                      </dl>
                    </div>
                    
                    <!-- Financial Details Card -->
                    <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                      <h3 class="text-base font-semibold text-gray-900 dark:text-white mb-3 flex items-center">
                        <svg class="w-4 h-4 mr-2 text-success-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                        </svg>
                        {$t('auction.keyDetails')}
                      </h3>
                      <dl class="space-y-2">
                        <div class="flex justify-between items-center">
                          <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
                            {$t('auction.startingBid')}
                          </dt>
                          <dd class="text-sm font-semibold text-gray-900 dark:text-white">
                            {formatCurrency(auction.starting_bid)}
                          </dd>
                        </div>
                        <div class="flex justify-between items-center">
                          <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
                            {$t('auction.currentBid')}
                          </dt>
                          <dd class="text-sm font-semibold text-success-600 dark:text-success-400">
                            {formatCurrency(auction.current_bid || auction.starting_bid)}
                          </dd>
                        </div>
                        <div class="flex justify-between items-center">
                          <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
                            {$t('auction.minimumIncrement')}
                          </dt>
                          <dd class="text-sm font-semibold text-gray-900 dark:text-white">
                            {formatCurrency(auction.minimum_increment)}
                          </dd>
                        </div>
                      </dl>
                    </div>
                  </div>
                </div>
                
              {:else if activeTab === 'property' && property}
                <div class="space-y-6">
                  <div class="flex items-center justify-between">
                    <h2 class="text-xl font-bold text-gray-900 dark:text-white">
                      {$t('auction.auctionProperty')}
                    </h2>
                    <a 
                      href={`/properties/${property.slug}`} 
                      target="_blank"
                      class="inline-flex items-center text-sm font-medium text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 transition-colors"
                    >
                      {$t('property.viewDetails')}
                      <svg class="h-4 w-4 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                      </svg>
                    </a>
                  </div>
                  
                  <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <!-- Property Card -->
                    <div>
                      <PropertyCard property={property} isCompact={true} />
                    </div>
                    
                    <!-- Property Details -->
                    <div class="space-y-4">
                      <!-- Key Details -->
                      <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                        <h4 class="text-base font-semibold text-gray-900 dark:text-white mb-3">
                          {$t('property.keyDetails')}
                        </h4>
                        <dl class="space-y-2">
                          <div class="flex justify-between items-center">
                            <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
                              {$t('property.propertyType')}
                            </dt>
                            <dd class="text-sm font-semibold text-gray-900 dark:text-white">
                              {property.property_type_display}
                            </dd>
                          </div>
                          <div class="flex justify-between items-center">
                            <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
                              {$t('property.size')}
                            </dt>
                            <dd class="text-sm font-semibold text-gray-900 dark:text-white">
                              {property.size_sqm} {$t('property.sqm')}
                            </dd>
                          </div>
                          <div class="flex justify-between items-center">
                            <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
                              {$t('property.location')}
                            </dt>
                            <dd class="text-sm font-semibold text-gray-900 dark:text-white">
                              {property.location?.city}, {property.location?.state}
                            </dd>
                          </div>
                          <div class="flex justify-between items-center">
                            <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
                              {$t('property.marketValue')}
                            </dt>
                            <dd class="text-sm font-semibold text-success-600 dark:text-success-400">
                              {formatCurrency(property.market_value)}
                            </dd>
                          </div>
                        </dl>
                      </div>
                      
                      <!-- Features -->
                      {#if property.features && property.features.length > 0}
                        <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                          <h4 class="text-base font-semibold text-gray-900 dark:text-white mb-3">
                            {$t('property.features')}
                          </h4>
                          <div class="flex flex-wrap gap-1.5">
                            {#each property.features as feature}
                              <span class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-primary-100 text-primary-800 dark:bg-primary-900 dark:text-primary-200">
                                {feature}
                              </span>
                            {/each}
                          </div>
                        </div>
                      {/if}
                    </div>
                  </div>
                </div>
                
              {:else if activeTab === 'bids'}
                <div class="space-y-4">
                  <!-- Bid History Header -->
                  <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                    <div>
                      <h2 class="text-xl font-bold text-gray-900 dark:text-white">
                        {$t('auction.bidHistory')}
                      </h2>
                      <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
                        {bids.length} {bids.length === 1 ? 'bid' : 'bids'} placed on this auction
                      </p>
                    </div>
                    <div class="flex items-center gap-2">
                      {#if showBidSection && canBid}
                        <Button
                          variant="primary"
                          size="small"
                          on:click={openBidModal}
                        >
                          <svg class="w-4 h-4 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                          </svg>
                          Place Bid
                        </Button>
                      {/if}
                      <Button
                        variant="outline"
                        size="small"
                        loading={bidsLoading}
                        on:click={loadAuctionBids}
                      >
                        <svg class="w-4 h-4 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                        </svg>
                        Refresh
                      </Button>
                    </div>
                  </div>
                  
                  {#if bidsLoading}
                    <!-- Loading State -->
                    <div class="flex items-center justify-center py-12">
                      <div class="text-center">
                        <div class="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-primary-500 mb-3"></div>
                        <p class="text-sm text-gray-500 dark:text-gray-400">Loading bids...</p>
                      </div>
                    </div>
                    
                  {:else if bids.length === 0}
                    <!-- Empty State -->
                    <div class="text-center py-12">
                      <div class="w-12 h-12 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-3">
                        <svg class="w-6 h-6 text-gray-400 dark:text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                        </svg>
                      </div>
                      <h3 class="text-base font-semibold text-gray-900 dark:text-gray-100 mb-2">
                        {$t('auction.noBids')}
                      </h3>
                      <p class="text-gray-500 dark:text-gray-400 mb-4 text-sm">
                        {$t('auction.beTheFirst')}
                      </p>
                      {#if canBid}
                        <Button
                          variant="primary"
                          on:click={openBidModal}
                        >
                          <svg class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                          </svg>
                          Place First Bid
                        </Button>
                      {:else if !$user}
                        <Button
                          variant="primary"
                          href={`/login?redirect=/auctions/${auction.slug}`}
                        >
                          Sign In to Place First Bid
                        </Button>
                      {/if}
                    </div>
                    
                  {:else}
                    <!-- Bid List -->
                    <div class="space-y-3">
                      {#each bids as bid, index (bid.id)}
                        <div class="group relative rounded-lg border border-gray-200 dark:border-gray-700 p-4 hover:border-gray-300 dark:hover:border-gray-600 transition-all duration-200 {index === 0 ? 'bg-gradient-to-r from-success-50 to-emerald-50 dark:from-success-900/10 dark:to-emerald-900/10 border-success-200 dark:border-success-800' : 'bg-white dark:bg-gray-800'} {bid.bidder_info?.id === $user?.id ? 'ring-1 ring-primary-200 dark:ring-primary-800' : ''}">
                          <div class="flex items-center justify-between">
                            <div class="flex-1 min-w-0">
                              <p class="text-sm font-semibold text-gray-900 dark:text-white">
                                {formatCurrency(bid.amount)}
                              </p>
                              <p class="text-xs text-gray-500 dark:text-gray-400 truncate">
                                {bid.bidder_info?.name || 'Anonymous'}
                                {#if bid.bidder_info?.id === $user?.id}
                                  <span class="text-primary-600 dark:text-primary-400 font-medium">({$t('auction.you')})</span>
                                {/if}
                              </p>
                            </div>
                            <div class="text-right flex-shrink-0 ml-2">
                              <p class="text-xs text-gray-500 dark:text-gray-400">
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
                
              {:else if activeTab === 'terms'}
                <div class="space-y-4">
                  <h2 class="text-xl font-bold text-gray-900 dark:text-white">
                    {$t('auction.termsConditions')}
                  </h2>
                  
                  {#if auction.terms_conditions}
                    <div class="prose dark:prose-invert max-w-none bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                      <p class="whitespace-pre-wrap text-gray-600 dark:text-gray-300">{auction.terms_conditions}</p>
                    </div>
                  {:else}
                    <div class="text-center py-12 bg-gray-50 dark:bg-gray-700 rounded-lg">
                      <div class="w-12 h-12 bg-gray-200 dark:bg-gray-600 rounded-full flex items-center justify-center mx-auto mb-3">
                        <svg class="w-6 h-6 text-gray-400 dark:text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                      </div>
                      <h3 class="text-base font-semibold text-gray-900 dark:text-gray-100 mb-1">
                        {$t('auction.noTerms')}
                      </h3>
                      <p class="text-gray-500 dark:text-gray-400 text-sm">
                        {$t('auction.contactForTerms')}
                      </p>
                    </div>
                  {/if}
                </div>
              {/if}
            </div>
          </div>
        </div>
        
        <!-- Sidebar -->
        <div class="space-y-4">
          
          <!-- Auction Status Card -->
          <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-4">
            
            {#if isLiveAuction}
              <!-- Live Auction Timer -->
              <div class="mb-4">
                <h3 class="text-base font-semibold text-gray-900 dark:text-white mb-3 flex items-center">
                  <span class="w-2 h-2 bg-danger-500 rounded-full mr-2 animate-pulse"></span>
                  {$t('auction.timeRemaining')}
                </h3>
                <CountdownTimer 
                  endDate={auction.end_date}
                  onEnd={handleTimerEnd}
                />
              </div>
              
            {:else if auction.status === 'scheduled'}
              <!-- Scheduled Auction Timer -->
              <div class="mb-4">
                <h3 class="text-base font-semibold text-gray-900 dark:text-white mb-3 flex items-center">
                  <span class="w-2 h-2 bg-warning-500 rounded-full mr-2 animate-pulse"></span>
                  {$t('auction.startsIn')}
                </h3>
                <CountdownTimer 
                  endDate={auction.start_date}
                  onEnd={handleTimerEnd}
                  variant="secondary"
                />
                <p class="text-gray-600 dark:text-gray-400 mt-2 text-sm">
                  {formatDateTime(auction.start_date)}
                </p>
              </div>
              
            {:else if auction.status === 'ended' || auction.status === 'completed'}
              <!-- Ended Auction -->
              <div class="mb-4">
                <h3 class="text-base font-semibold text-gray-900 dark:text-white mb-2">
                  {$t('auction.auctionEnded')}
                </h3>
                <p class="text-gray-600 dark:text-gray-400 text-sm">
                  {formatDateTime(auction.end_date)}
                </p>
                {#if auction.status === 'completed' && bids.length > 0}
                  <div class="mt-3 p-3 bg-success-50 dark:bg-success-900/20 rounded-lg border border-success-200 dark:border-success-800">
                    <h4 class="text-sm font-semibold text-success-800 dark:text-success-200 mb-1 flex items-center">
                      🎉 Auction Winner
                    </h4>
                    <p class="text-sm text-success-700 dark:text-success-300">
                      {bids[0]?.bidder_info?.name || 'Anonymous'} won with {formatCurrency(bids[0]?.amount || 0)}
                    </p>
                  </div>
                {/if}
              </div>
            {/if}
            
            <!-- Current Bid Display -->
            <div class="border-t border-gray-200 dark:border-gray-700 pt-4 mb-4">
              <div class="text-center">
                <div class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
                  {$t('auction.currentBid')}
                </div>
                <div class="text-2xl font-bold text-primary-600 dark:text-primary-400 mb-1">
                  {formatCurrency(auction.current_bid || auction.starting_bid)}
                </div>
                <div class="text-sm text-gray-500 dark:text-gray-400">
                  {$t('auction.totalBids')}: {auction.bid_count || bids.length}
                </div>
              </div>
            </div>
            
            <!-- Main Action Button -->
            <div class="space-y-3">
              {#if canBid}
                <Button
                  variant="primary"
                  class="w-full font-semibold"
                  on:click={openBidModal}
                  disabled={placingBid}
                >
                  {#if placingBid}
                    <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                  {:else}
                    <svg class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  {/if}
                  {$t('auction.placeBid')}
                </Button>
                <p class="text-xs text-gray-500 dark:text-gray-400 text-center">
                  {$t('auction.minimumBid')}: {formatCurrency(minimumBidAmount)}
                </p>
                
              {:else if canRegister}
                <Button
                  variant="secondary" 
                  class="w-full font-semibold"
                  on:click={() => showRegisterModal = true}
                >
                  <svg class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
                  </svg>
                  {$t('auction.registerForAuction')}
                </Button>
                
              {:else if auction.status === 'scheduled'}
                {#if isRegistered}
                  <div class="bg-success-50 dark:bg-success-900/20 p-3 rounded-lg border border-success-200 dark:border-success-800">
                    <div class="flex items-center">
                      <svg class="h-4 w-4 text-success-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                      </svg>
                      <div class="ml-2">
                        <p class="text-sm font-semibold text-success-800 dark:text-success-200">
                          ✅ Registered
                        </p>
                        <p class="text-xs text-success-600 dark:text-success-400">
                          Ready to bid when auction starts
                        </p>
                      </div>
                    </div>
                  </div>
                {:else if $user}
                  <Button
                    variant="secondary"
                    class="w-full font-semibold"
                    on:click={() => showRegisterModal = true}
                  >
                    <svg class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
                    </svg>
                    {$t('auction.registerForAuction')}
                  </Button>
                {:else}
                  <Button
                    variant="secondary"
                    class="w-full font-semibold"
                    href="/login?redirect=/auctions/{auction.slug}"
                  >
                    <svg class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
                    </svg>
                    {$t('auction.loginToRegister')}
                  </Button>
                {/if}
                
              {:else if !$user}
                <Button
                  variant="primary"
                  class="w-full font-semibold"
                  href="/login?redirect=/auctions/{auction.slug}"
                >
                  <svg class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
                  </svg>
                  {$t('auction.loginToPlaceBid')}
                </Button>
                
              {:else}
                <Button
                  variant="outline"
                  class="w-full font-semibold"
                  href="/auctions"
                >
                  <svg class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                  </svg>
                  {$t('auctions.backToAuctions')}
                </Button>
              {/if}
            </div>
            
            <!-- Owner Controls -->
            {#if isOwner && isActiveAuction}
              <div class="border-t border-gray-200 dark:border-gray-700 pt-4 mt-4">
                <h3 class="text-base font-semibold text-gray-900 dark:text-white mb-2">
                  Owner Controls
                </h3>
                <div class="space-y-2">
                  <Button
                    variant="outline"
                    size="small"
                    class="w-full"
                    on:click={() => showExtendModal = true}
                  >
                    <svg class="w-4 h-4 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Extend Auction
                  </Button>
                </div>
              </div>
            {/if}
          </div>
          
          <!-- Property Quick Info Card -->
          {#if property}
            <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm overflow-hidden">
              <div class="p-4">
                <div class="flex items-center justify-between mb-3">
                  <h3 class="text-base font-semibold text-gray-900 dark:text-white">
                    {$t('auction.propertyInfo')}
                  </h3>
                  <a 
                    href={`/properties/${property.slug}`} 
                    target="_blank"
                    class="text-sm font-medium text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 transition-colors"
                  >
                    {$t('property.viewDetails')}
                  </a>
                </div>
                
                <!-- Property Image -->
                <div class="aspect-video bg-gray-200 dark:bg-gray-700 rounded-lg overflow-hidden mb-3">
                  {#if property.main_image?.url}
                    <img 
                      src={property.main_image.url} 
                      alt={property.title}
                      class="w-full h-full object-cover"
                    />
                  {:else}
                    <div class="flex items-center justify-center h-full">
                      <svg class="h-8 w-8 text-gray-400 dark:text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                      </svg>
                    </div>
                  {/if}
                </div>
                
                <h4 class="font-semibold text-gray-900 dark:text-white mb-3 text-sm">
                  {property.title}
                </h4>
                
                <!-- Property Details -->
                <dl class="space-y-2 text-sm">
                  <div class="flex justify-between items-center">
                    <dt class="font-medium text-gray-500 dark:text-gray-400">{$t('property.location')}</dt>
                    <dd class="font-semibold text-gray-900 dark:text-white text-right">{property.location?.city}, {property.location?.state}</dd>
                  </div>
                  <div class="flex justify-between items-center">
                    <dt class="font-medium text-gray-500 dark:text-gray-400">{$t('property.propertyType')}</dt>
                    <dd class="font-semibold text-gray-900 dark:text-white">{property.property_type_display}</dd>
                  </div>
                  <div class="flex justify-between items-center">
                    <dt class="font-medium text-gray-500 dark:text-gray-400">{$t('property.size')}</dt>
                    <dd class="font-semibold text-gray-900 dark:text-white">{property.size_sqm} {$t('property.sqm')}</dd>
                  </div>
                  <div class="flex justify-between items-center">
                    <dt class="font-medium text-gray-500 dark:text-gray-400">{$t('property.marketValue')}</dt>
                    <dd class="font-semibold text-success-600 dark:text-success-400">{formatCurrency(property.market_value)}</dd>
                  </div>
                </dl>
              </div>
            </div>
          {/if}
          
          <!-- Recent Activity Card -->
          {#if bids.length > 0}
            <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-4">
              <div class="flex items-center justify-between mb-3">
                <h3 class="text-base font-semibold text-gray-900 dark:text-white">
                  {$t('auction.recentActivity')}
                </h3>
                <span class="text-sm text-gray-500 dark:text-gray-400">
                  Latest 3
                </span>
              </div>
              
              <div class="space-y-2">
                {#each bids.slice(0, 3) as bid}
                  <div class="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div class="flex-1 min-w-0">
                      <p class="text-sm font-semibold text-gray-900 dark:text-white">
                        {formatCurrency(bid.amount)}
                      </p>
                      <p class="text-xs text-gray-500 dark:text-gray-400 truncate">
                        {bid.bidder_info?.name || 'Anonymous'}
                        {#if bid.bidder_info?.id === $user?.id}
                          <span class="text-primary-600 dark:text-primary-400 font-medium">({$t('auction.you')})</span>
                        {/if}
                      </p>
                    </div>
                    <div class="text-right flex-shrink-0 ml-2">
                      <p class="text-xs text-gray-500 dark:text-gray-400">
                        {getTimeAgo(bid.bid_time)}
                      </p>
                      <AuctionStatus status={bid.status} isCompact={true} />
                    </div>
                  </div>
                {/each}
                
                <Button
                  variant="outline"
                  size="small"
                  on:click={() => activeTab = 'bids'}
                  class="w-full mt-2"
                >
                  {$t('auction.viewAllBids')} ({bids.length})
                </Button>
              </div>
            </div>
          {/if}
          
          <!-- Help Card -->
          <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-4">
            <h3 class="text-base font-semibold text-gray-900 dark:text-white mb-2">
              {$t('auction.needHelp')}
            </h3>
            <p class="text-sm text-gray-600 dark:text-gray-400 mb-3">
              Questions about this auction? Contact support.
            </p>
            <Button
              variant="outline"
              size="small"
              class="w-full"
              href="/contact?subject=Auction%20{auction.id}"
            >
              <svg class="w-4 h-4 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
              {$t('auction.contactSupport')}
            </Button>
          </div>
          
        </div>
      </div>
    {/if}
  </div>
</div>

<!-- Enhanced Bid Modal with Fixed Styling -->
<Modal
  bind:show={showBidModal}
  title={$t('auction.placeBid')}
  maxWidth="lg"
>
  <form on:submit|preventDefault={handleBidSubmission} class="space-y-4 p-4">
    {#if bidError}
      <Alert type="error" message={bidError} />
    {/if}
    
    <!-- Current Auction Status -->
    <div class="bg-gradient-to-r from-primary-50 to-blue-50 dark:from-primary-900/20 dark:to-blue-900/20 p-4 rounded-lg border border-primary-200 dark:border-primary-800">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-3 text-center">
        <div>
          <div class="text-sm font-medium text-primary-700 dark:text-primary-300 mb-1">Current Bid</div>
          <div class="text-xl font-bold text-primary-600 dark:text-primary-400">
            {formatCurrency(auction?.current_bid || auction?.starting_bid)}
          </div>
        </div>
        <div>
          <div class="text-sm font-medium text-primary-700 dark:text-primary-300 mb-1">Minimum Bid</div>
          <div class="text-lg font-bold text-primary-800 dark:text-primary-200">
            {formatCurrency(minimumBidAmount)}
          </div>
        </div>
        <div>
          <div class="text-sm font-medium text-primary-700 dark:text-primary-300 mb-1">Total Bids</div>
          <div class="text-lg font-bold text-primary-800 dark:text-primary-200">
            {auction?.bid_count || bids.length}
          </div>
        </div>
      </div>
    </div>
    
    <!-- Bid Amount Input -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <FormField
        type="number"
        id="bid_amount"
        label={$t('auction.bidAmount')}
        bind:value={bidAmount}
        min={minimumBidAmount}
        step="1"
        required={true}
        class="text-lg font-semibold"
      />
      
      <FormField
        type="number"
        id="max_bid_amount"
        label="Maximum Auto-Bid (Optional)"
        bind:value={maxBidAmount}
        step="1"
        helpText="Set a maximum amount for automatic bidding"
      />
    </div>
    
    <!-- Advanced Options -->
    <div class="border-t border-gray-200 dark:border-gray-700 pt-4">
      <h4 class="text-base font-semibold text-gray-900 dark:text-white mb-3">
        Advanced Options
      </h4>
      
      <div class="space-y-3">
        <label class="flex items-center">
          <input
            type="checkbox"
            bind:checked={enableAutoBidding}
            class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
          />
          <span class="ml-2 text-sm font-medium text-gray-700 dark:text-gray-300">
            Enable Auto-Bidding
          </span>
        </label>
        <p class="text-xs text-gray-500 dark:text-gray-400 ml-6">
          Automatically place bids when you're outbid, up to your maximum amount
        </p>
        
        <FormField
          type="textarea"
          id="bid_notes"
          label="Notes (Optional)"
          bind:value={bidNotes}
          rows={2}
          helpText="Add any notes with your bid"
        />
      </div>
    </div>
    
    <!-- Bid Disclaimer -->
    <div class="bg-warning-50 dark:bg-warning-900/20 p-3 rounded-lg border border-warning-200 dark:border-warning-800">
      <div class="flex">
        <div class="flex-shrink-0">
          <svg class="h-4 w-4 text-warning-500" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
          </svg>
        </div>
        <div class="ml-2">
          <h3 class="text-sm font-semibold text-warning-800 dark:text-warning-200">
            Bid Agreement
          </h3>
          <div class="mt-1 text-sm text-warning-700 dark:text-warning-300">
            <p>{$t('auction.bidDisclaimer')}</p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Action Buttons -->
    <div class="flex justify-end space-x-2 pt-4 border-t border-gray-200 dark:border-gray-700">
      <Button
        variant="outline"
        type="button"
        on:click={() => showBidModal = false}
        disabled={placingBid}
      >
        {$t('common.cancel')}
      </Button>
      
      <Button
        variant="primary"
        type="submit"
        loading={placingBid}
        disabled={placingBid || !bidAmount || parseFloat(bidAmount) < minimumBidAmount}
        class="px-6"
      >
        {#if placingBid}
          <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        {:else}
          <svg class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        {/if}
        {enableAutoBidding ? 'Place Auto-Bid' : $t('auction.confirmBid')}
      </Button>
    </div>
  </form>
</Modal>

<!-- Remaining modals with improved styling -->
<!-- Login Modal -->
<Modal
  bind:show={showLoginModal}
  title={$t('auction.loginRequired')}
  maxWidth="sm"
>
  <div class="text-center py-4 p-4">
    <div class="w-12 h-12 bg-warning-100 dark:bg-warning-900 rounded-full flex items-center justify-center mx-auto mb-3">
      <svg class="w-6 h-6 text-warning-600 dark:text-warning-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zM3 20a6 6 0 0112 0v1H3v-1z" />
      </svg>
    </div>
    
    <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-2">
      Sign In Required
    </h3>
    <p class="mb-4 text-gray-600 dark:text-gray-400 text-sm">
      {$t('auction.loginRequiredMessage')}
    </p>
    
    <div class="flex flex-col sm:flex-row justify-center gap-2">
      <Button
        variant="outline"
        on:click={() => showLoginModal = false}
      >
        {$t('common.cancel')}
      </Button>
      
      <Button
        variant="primary"
        href={`/login?redirect=/auctions/${auction.slug}`}
      >
        {$t('nav.login')}
      </Button>
    </div>
  </div>
</Modal>
<!-- Registration Modal - Continued -->
<Modal
  bind:show={showRegisterModal}
  title="Register for Auction"
  maxWidth="md"
>
  <div class="p-4">
    <div class="bg-primary-50 dark:bg-primary-900/20 p-3 rounded-lg mb-4">
      <h4 class="text-base font-bold text-primary-900 dark:text-primary-100 mb-1">
        Auction Registration Required
      </h4>
      <p class="text-sm text-primary-700 dark:text-primary-300">
        You must register for this auction before you can place bids.
      </p>
    </div>
    
    <div class="space-y-4">
      <div class="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
        <h5 class="font-semibold text-gray-900 dark:text-white mb-3">Registration Requirements:</h5>
        <ul class="space-y-2">
          <li class="flex items-center text-sm text-gray-600 dark:text-gray-400">
            <svg class="h-4 w-4 text-success-500 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
            <span>Verified email address</span>
          </li>
          <li class="flex items-center text-sm text-gray-600 dark:text-gray-400">
            <svg class="h-4 w-4 text-success-500 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
            <span>Account in good standing</span>
          </li>
          <li class="flex items-center text-sm text-gray-600 dark:text-gray-400">
            <svg class="h-4 w-4 text-success-500 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
            <span>Agreement to terms and conditions</span>
          </li>
        </ul>
      </div>
      
      <div class="bg-warning-50 dark:bg-warning-900/20 p-3 rounded-lg border border-warning-200 dark:border-warning-800">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-4 w-4 text-warning-500" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-2">
            <p class="text-sm text-warning-800 dark:text-warning-200">
              <strong>Note:</strong> Registration is free and takes only a moment. Once registered, you'll be able to place bids throughout the auction period.
            </p>
          </div>
        </div>
      </div>
    </div>
    
    <div class="flex justify-end space-x-2 mt-6">
      <Button
        variant="outline"
        on:click={() => showRegisterModal = false}
      >
        Cancel
      </Button>
      
      <Button
        variant="primary"
        on:click={handleAuctionRegistration}
        class="px-6"
      >
        <svg class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        Register for Auction
      </Button>
    </div>
  </div>
</Modal>

<!-- Extend Auction Modal -->
<Modal
  bind:show={showExtendModal}
  title="Extend Auction"
  maxWidth="md"
>
  <form on:submit|preventDefault={handleExtendAuction} class="space-y-4 p-4">
    <div class="bg-primary-50 dark:bg-primary-900/20 p-4 rounded-lg">
      <h4 class="text-base font-bold text-primary-900 dark:text-primary-100 mb-1">
        Extend Auction Time
      </h4>
      <p class="text-sm text-primary-700 dark:text-primary-300">
        Current end time: <span class="font-semibold">{formatDateTime(auction?.end_date)}</span>
      </p>
    </div>
    
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <FormField
        type="number"
        id="extension_hours"
        label="Extension Hours"
        bind:value={extensionHours}
        min={1}
        max={168}
        step={1}
        required={true}
        helpText="Number of hours to extend (max 7 days)"
      />
      
      <div class="flex items-center justify-center bg-gray-50 dark:bg-gray-700 rounded-lg p-3">
        <div class="text-center">
          <div class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">New End Time</div>
          <div class="text-base font-bold text-gray-900 dark:text-white">
            {#if extensionHours && auction?.end_date}
              {formatDateTime(new Date(new Date(auction.end_date).getTime() + (extensionHours * 60 * 60 * 1000)).toISOString())}
            {:else}
              --
            {/if}
          </div>
        </div>
      </div>
    </div>
    
    <FormField
      type="textarea"
      id="extension_reason"
      label="Reason for Extension (Optional)"
      bind:value={extensionReason}
      rows={3}
      helpText="Optional reason for extending the auction"
    />
    
    {#if bidError}
      <Alert type="error" message={bidError} />
    {/if}
    
    <div class="bg-warning-50 dark:bg-warning-900/20 p-3 rounded-lg border border-warning-200 dark:border-warning-800">
      <div class="flex">
        <div class="flex-shrink-0">
          <svg class="h-4 w-4 text-warning-500" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
          </svg>
        </div>
        <div class="ml-2">
          <h3 class="text-sm font-semibold text-warning-800 dark:text-warning-200">
            Extension Notice
          </h3>
          <div class="mt-1 text-sm text-warning-700 dark:text-warning-300">
            <p>All registered bidders will be notified of the auction extension. This action cannot be undone.</p>
          </div>
        </div>
      </div>
    </div>
    
    <div class="flex justify-end space-x-2 pt-4 border-t border-gray-200 dark:border-gray-700">
      <Button
        variant="outline"
        type="button"
        on:click={() => showExtendModal = false}
      >
        Cancel
      </Button>
      
      <Button
        variant="primary"
        type="submit"
        class="px-6"
      >
        <svg class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        Extend Auction
      </Button>
    </div>
  </form>
</Modal>