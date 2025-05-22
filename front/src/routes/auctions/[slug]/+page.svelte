<!-- src/routes/auctions/[slug]/+page.svelte -->
<script>
  import { onMount, onDestroy } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { t } from '$lib/i18n/i18n';
  import { user } from '$lib/stores/user';
  import { 
    fetchAuctionBySlug, 
    fetchAuctionBidsBySlug, 
    placeBid,
    updateAuction
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
  let isRegistered = false;
  
  // Auction extension
  let extensionHours = 24;
  let extensionReason = '';
  
  $: slug = $page.params.slug;
  $: isLiveAuction = auction?.status === 'live';
  $: isScheduledAuction = auction?.status === 'scheduled';
  $: isActiveAuction = auction?.status === 'live' || auction?.status === 'scheduled';
  $: canBid = isActiveAuction && $user && new Date(auction?.end_date) > new Date() && !isOwner && isRegistered;
  $: canRegister = (isLiveAuction || isScheduledAuction) && $user && !isOwner && !isRegistered;
  $: showBidSection = (isLiveAuction || isScheduledAuction) && $user && !isOwner;
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
      { amount: minBid, label: $t('auction.minimumBid'), color: 'bg-blue-500' },
      { amount: minBid + increment, label: `+${formatCurrency(increment)}`, color: 'bg-green-500' },
      { amount: minBid + (increment * 2), label: `+${formatCurrency(increment * 2)}`, color: 'bg-yellow-500' },
      { amount: minBid + (increment * 5), label: `+${formatCurrency(increment * 5)}`, color: 'bg-red-500' }
    ];
  }
  
  async function loadAuctionData() {
    loading = true;
    error = null;
    
    try {
      const auctionData = await fetchAuctionBySlug(slug);
      auction = auctionData;
      
      if (auction.related_property) {
        property = auction.related_property;
      }
      
      quickBidAmounts = generateQuickBidAmounts();
      
      // Check if user is registered (mock check for now)
      if ($user) {
        isRegistered = true; // In real app, check if user is registered for this auction
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
      bids = []; // Set empty array on error
    } finally {
      bidsLoading = false;
    }
  }
  
  // Enhanced bid submission with proper error handling
  async function handleBidSubmission() {
    const bidValue = parseFloat(bidAmount);
    const maxBidValue = maxBidAmount ? parseFloat(maxBidAmount) : null;
    
    // Clear previous errors
    bidError = '';
    bidSuccess = '';
    
    // Validation
    if (isNaN(bidValue) || bidValue < minimumBidAmount) {
      bidError = $t('auction.bidTooLow', { amount: minimumBidAmount.toLocaleString() });
      return;
    }
    
    if (maxBidValue && maxBidValue < bidValue) {
      bidError = 'Maximum bid cannot be less than current bid';
      return;
    }
    
    // Check if bid is significantly higher (show warning)
    const currentBid = auction.current_bid || auction.starting_bid;
    const isLargeBid = bidValue > (currentBid * 1.5);
    
    if (isLargeBid) {
      const confirmed = confirm($t('auction.largeBidWarning', { amount: formatCurrency(bidValue) }));
      if (!confirmed) return;
    }
    
    try {
      placingBid = true;
      
      // Check authentication token
      const token = localStorage.getItem('accessToken');
      if (!token) {
        throw new Error('Please log in to place a bid');
      }
      
      console.log('Placing bid:', {
        auctionId: auction.id,
        bidValue,
        token: token ? 'Present' : 'Missing'
      });
      
      // Place bid using API
      const bidResponse = await placeBid(auction.id, bidValue);
      
      console.log('Bid response:', bidResponse);
      
      bidSuccess = $t('auction.bidPlaced');
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
      console.error('Error placing bid:', err);
      
      // Handle specific error cases
      if (err.message.includes('Authentication')) {
        bidError = 'Please log in to place a bid';
        showBidModal = false;
        showLoginModal = true;
      } else if (err.message.includes('verification')) {
        bidError = 'Please verify your email address to place bids';
      } else if (err.message.includes('inactive')) {
        bidError = 'Your account is inactive. Please contact support.';
      } else {
        bidError = err.message || $t('error.bidFailed');
      }
    } finally {
      placingBid = false;
    }
  }
  
  // Quick bid functionality
  async function handleQuickBid(amount) {
    if (placingBid) return;
    
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
      // In a real app, you would call an API endpoint to register for the auction
      // For now, we'll just set the registration status
      isRegistered = true;
      showRegisterModal = false;
      bidSuccess = 'Successfully registered for auction! You can now place bids.';
      
      // In a real implementation:
      // await registerForAuction(auction.id);
      
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
    }, 30000); // Refresh every 30 seconds
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

<div class="bg-gray-50 dark:bg-gray-900 min-h-screen py-8 px-4 sm:px-6 lg:px-8">
  <div class="max-w-7xl mx-auto">
    <!-- Breadcrumbs -->
    <Breadcrumb items={breadcrumbItems} class="mb-6" />
    
    {#if loading}
      <div class="space-y-8">
        <LoadingSkeleton type="auctionHeader" />
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div class="lg:col-span-2">
            <LoadingSkeleton type="auctionContent" />
          </div>
          <div>
            <LoadingSkeleton type="auctionSidebar" />
          </div>
        </div>
      </div>
    {:else if error}
      <Alert 
        type="error"
        title={$t('error.title')}
        message={error}
        action={{
          label: $t('auctions.backToAuctions'),
          href: '/auctions'
        }}
      />
    {:else if auction}
      <!-- Success/Error Messages -->
      {#if bidSuccess}
        <Alert type="success" message={bidSuccess} class="mb-6" dismissible={true} />
      {/if}
      
      {#if bidError}
        <Alert type="error" message={bidError} class="mb-6" dismissible={true} />
      {/if}
      
      <!-- Auction header -->
      <div class="mb-8">
        <div class="flex flex-wrap items-start justify-between">
          <div class="mb-4 md:mb-0">
            <div class="flex flex-wrap items-center space-x-2 mb-2">
              <AuctionStatus status={auction.status} />
              <span class="inline-flex items-center px-2.5 py-0.5 rounded-md text-sm font-medium bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200">
                {auction.auction_type === 'sealed' ? $t('auction.typeSealed') :
                 auction.auction_type === 'private' ? $t('auction.typeReserve') :
                 $t('auction.typeNoReserve')}
              </span>
              {#if auction.is_featured}
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-md text-sm font-medium bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200">
                  {$t('auction.featured')}
                </span>
              {/if}
            </div>
            <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">
              {auction.title}
            </h1>
            <p class="text-gray-600 dark:text-gray-400">
              Auction ID: {auction.id} • Views: {auction.view_count || 0}
            </p>
          </div>
          <div class="flex space-x-2">
            <ShareButtons 
              url={`/auctions/${auction.slug}`} 
              title={auction.title}
              description={auction.description}
            />
            {#if isOwner}
              <Button 
                variant="outline"
                href={`/auctions/${auction.id}/edit`}
                aria-label={$t('auction.edit')}
              >
                <svg class="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
                {$t('auction.edit')}
              </Button>
            {/if}
          </div>
        </div>
      </div>
      
      <!-- PROMINENT BIDDING SECTION - Always visible when user can bid -->
      {#if showBidSection}
        <div class="mb-8 bg-gradient-to-r from-primary-500 to-blue-600 rounded-xl shadow-xl overflow-hidden border-4 border-primary-300">
          <div class="px-6 py-4 bg-black bg-opacity-20">
            <div class="flex items-center justify-between">
              <div>
                <h2 class="text-2xl font-bold text-white flex items-center">
                  {#if isLiveAuction}
                    <span class="w-3 h-3 bg-red-500 rounded-full mr-2 animate-pulse"></span>
                    🔥 LIVE BIDDING
                  {:else if isScheduledAuction}
                    <span class="w-3 h-3 bg-yellow-500 rounded-full mr-2 animate-pulse"></span>
                    ⏰ AUCTION STARTING SOON
                  {/if}
                </h2>
                <p class="text-primary-100 text-sm">
                  Current: {formatCurrency(auction.current_bid || auction.starting_bid)} • 
                  Next Bid: {formatCurrency(minimumBidAmount)}
                </p>
              </div>
              <div class="text-right text-white">
                <div class="text-3xl font-bold">
                  {auction.bid_count || bids.length}
                </div>
                <div class="text-sm opacity-90">Total Bids</div>
              </div>
            </div>
          </div>
          
          <div class="p-6">
            {#if canBid}
              <!-- LIVE/SCHEDULED BIDDING INTERFACE -->
              <div class="space-y-6">
                <!-- Quick Bid Buttons -->
                <div>
                  <h3 class="text-lg font-semibold text-white mb-3">Quick Bid Options</h3>
                  <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
                    {#each quickBidAmounts as option}
                      <button
                        type="button"
                        class="group relative overflow-hidden rounded-lg p-4 border-2 border-white border-opacity-30 hover:border-opacity-60 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-white focus:ring-opacity-50 bg-white bg-opacity-10 hover:bg-opacity-20 disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-105"
                        disabled={placingBid}
                        on:click={() => handleQuickBid(option.amount)}
                      >
                        <div class="flex flex-col items-center space-y-1">
                          <span class="text-xl font-bold text-white">
                            {formatCurrency(option.amount)}
                          </span>
                          <span class="text-xs text-white text-opacity-80">
                            {option.label}
                          </span>
                        </div>
                        
                        {#if placingBid}
                          <div class="absolute inset-0 bg-white bg-opacity-20 flex items-center justify-center">
                            <div class="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                          </div>
                        {/if}
                      </button>
                    {/each}
                  </div>
                </div>
                
                <!-- Main Bid Button & Advanced Options -->
                <div class="flex flex-col md:flex-row gap-4">
                  <Button
                    variant="secondary"
                    size="large"
                    class="flex-1 text-lg py-4 font-bold"
                    on:click={openBidModal}
                    disabled={placingBid}
                  >
                    <svg class="w-6 h-6 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                    PLACE CUSTOM BID
                  </Button>
                  
                  {#if userHighestBid}
                    <div class="flex-1 bg-white bg-opacity-15 rounded-lg p-4 text-center">
                      <div class="text-sm text-white text-opacity-80">Your Highest Bid</div>
                      <div class="text-xl font-bold text-white">
                        {formatCurrency(userHighestBid.amount)}
                      </div>
                      <div class="text-sm text-white text-opacity-70">
                        {userHighestBid.status === 'winning' ? '🎉 Currently Winning!' : '⚠️ You\'ve been outbid'}
                      </div>
                    </div>
                  {/if}
                </div>
                
                {#if isScheduledAuction}
                  <div class="bg-yellow-500 bg-opacity-20 rounded-lg p-4 border border-yellow-400">
                    <div class="flex items-center">
                      <svg class="h-5 w-5 text-yellow-300 mr-2" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                      </svg>
                      <span class="text-yellow-100 font-medium">
                        Auction starts soon! You can place pre-bids that will be active when the auction begins.
                      </span>
                    </div>
                  </div>
                {/if}
              </div>
              
            {:else if canRegister}
              <!-- REGISTRATION REQUIRED -->
              <div class="text-center py-8">
                <div class="bg-white bg-opacity-15 rounded-lg p-6 mb-6">
                  <svg class="w-16 h-16 mx-auto text-white mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
                  </svg>
                  <h3 class="text-2xl font-bold text-white mb-2">
                    Registration Required
                  </h3>
                  <p class="text-white text-opacity-80 mb-6">
                    Register for this auction to start bidding on this amazing property
                  </p>
                  <Button
                    variant="secondary"
                    size="large"
                    class="px-8 py-3 text-lg font-bold"
                    on:click={() => showRegisterModal = true}
                  >
                    <svg class="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
                    </svg>
                    REGISTER FOR AUCTION
                  </Button>
                </div>
              </div>
              
            {:else if !$user}
              <!-- LOGIN REQUIRED -->
              <div class="text-center py-8">
                <div class="bg-white bg-opacity-15 rounded-lg p-6">
                  <svg class="w-16 h-16 mx-auto text-white mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                  <h3 class="text-2xl font-bold text-white mb-2">
                    Sign In to Bid
                  </h3>
                  <p class="text-white text-opacity-80 mb-6">
                    Create an account or sign in to participate in this auction
                  </p>
                  <Button
                    variant="secondary"
                    size="large"
                    class="px-8 py-3 text-lg font-bold"
                    href={`/login?redirect=/auctions/${auction.slug}`}
                  >
                    <svg class="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
                    </svg>
                    SIGN IN TO BID
                  </Button>
                </div>
              </div>
            {/if}
          </div>
        </div>
      {/if}
      
      <!-- Auction content -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Main content (left and center) -->
        <div class="lg:col-span-2 space-y-8">
          <!-- Image Gallery -->
          <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
            <Gallery 
              images={getAllImages()} 
              alt={auction.title}
              showThumbnails={true}
            />
          </div>
          
          <!-- Tabs Navigation -->
          <Tabs {tabs} bind:activeTab />
          
          <!-- Tab Content -->
          <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
            {#if activeTab === 'details'}
              <div class="prose dark:prose-invert max-w-none text-gray-600 dark:text-gray-300">
                <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                  {$t('auction.description')}
                </h2>
                <p class="whitespace-pre-wrap">{auction.description || $t('auction.noDescription')}</p>
                
                <div class="mt-8 grid grid-cols-1 sm:grid-cols-2 gap-6">
                  <div class="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                    <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-3">
                      {$t('auction.schedule')}
                    </h3>
                    <dl class="space-y-2">
                      <div class="flex justify-between">
                        <dt class="text-sm text-gray-500 dark:text-gray-400">
                          {$t('auction.startDate')}:
                        </dt>
                        <dd class="text-sm font-medium text-gray-900 dark:text-white">
                          {formatDateTime(auction.start_date)}
                        </dd>
                      </div>
                      <div class="flex justify-between">
                        <dt class="text-sm text-gray-500 dark:text-gray-400">
                          {$t('auction.endDate')}:
                        </dt>
                        <dd class="text-sm font-medium text-gray-900 dark:text-white">
                          {formatDateTime(auction.end_date)}
                        </dd>
                      </div>
                      {#if auction.registration_deadline}
                        <div class="flex justify-between">
                          <dt class="text-sm text-gray-500 dark:text-gray-400">
                            {$t('auction.registrationDeadline')}:
                          </dt>
                          <dd class="text-sm font-medium text-gray-900 dark:text-white">
                            {formatDateTime(auction.registration_deadline)}
                          </dd>
                        </div>
                      {/if}
                    </dl>
                  </div>
                  
                  <div class="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                    <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-3">
                      {$t('auction.keyDetails')}
                    </h3>
                    <dl class="space-y-2">
                      <div class="flex justify-between">
                        <dt class="text-sm text-gray-500 dark:text-gray-400">
                          {$t('auction.startingBid')}:
                        </dt>
                        <dd class="text-sm font-medium text-gray-900 dark:text-white">
                          {formatCurrency(auction.starting_bid)}
                        </dd>
                      </div>
                      <div class="flex justify-between">
                        <dt class="text-sm text-gray-500 dark:text-gray-400">
                          {$t('auction.currentBid')}:
                        </dt>
                        <dd class="text-sm font-medium text-green-600 dark:text-green-400">
                          {formatCurrency(auction.current_bid || auction.starting_bid)}
                        </dd>
                      </div>
                      <div class="flex justify-between">
                        <dt class="text-sm text-gray-500 dark:text-gray-400">
                          {$t('auction.minimumIncrement')}:
                        </dt>
                        <dd class="text-sm font-medium text-gray-900 dark:text-white">
                          {formatCurrency(auction.minimum_increment)}
                        </dd>
                      </div>
                    </dl>
                  </div>
                </div>
              </div>
              
            {:else if activeTab === 'property' && property}
              <div>
                <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                  {$t('auction.auctionProperty')}
                </h2>
                
                <div class="mb-4 flex justify-between items-center">
                  <h3 class="text-lg font-medium text-gray-900 dark:text-white">
                    {property.title}
                  </h3>
                  <a 
                    href={`/properties/${property.slug}`} 
                    class="text-sm text-primary-600 dark:text-primary-400 hover:underline flex items-center"
                    target="_blank"
                  >
                    {$t('property.viewDetails')}
                    <svg class="h-4 w-4 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                  </a>
                </div>
                
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-6 mb-6">
                  <div>
                    <PropertyCard property={property} isCompact={true} />
                  </div>
                  
                  <div class="space-y-4">
                    <div class="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                      <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                        {$t('property.keyDetails')}
                      </h4>
                      <dl class="space-y-2">
                        <div class="flex justify-between">
                          <dt class="text-sm text-gray-500 dark:text-gray-400">
                            {$t('property.propertyType')}:
                          </dt>
                          <dd class="text-sm font-medium text-gray-900 dark:text-white">
                            {property.property_type_display}
                          </dd>
                        </div>
                        <div class="flex justify-between">
                          <dt class="text-sm text-gray-500 dark:text-gray-400">
                            {$t('property.size')}:
                          </dt>
                          <dd class="text-sm font-medium text-gray-900 dark:text-white">
                            {property.size_sqm} {$t('property.sqm')}
                          </dd>
                        </div>
                        <div class="flex justify-between">
                          <dt class="text-sm text-gray-500 dark:text-gray-400">
                            {$t('property.location')}:
                          </dt>
                          <dd class="text-sm font-medium text-gray-900 dark:text-white">
                            {property.location?.city}, {property.location?.state}
                          </dd>
                        </div>
                        <div class="flex justify-between">
                          <dt class="text-sm text-gray-500 dark:text-gray-400">
                            {$t('property.marketValue')}:
                          </dt>
                          <dd class="text-sm font-medium text-gray-900 dark:text-white">
                            {formatCurrency(property.market_value)}
                          </dd>
                        </div>
                      </dl>
                    </div>
                    
                    {#if property.features && property.features.length > 0}
                      <div class="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                        <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          {$t('property.features')}
                        </h4>
                        <ul class="flex flex-wrap gap-2">
                          {#each property.features as feature}
                            <li class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs bg-primary-100 text-primary-800 dark:bg-primary-900 dark:text-primary-200">
                              {feature}
                            </li>
                          {/each}
                        </ul>
                      </div>
                    {/if}
                  </div>
                </div>
              </div>
              
            {:else if activeTab === 'bids'}
              <div>
                <div class="flex justify-between items-center mb-6">
                  <div>
                    <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
                      {$t('auction.bidHistory')} ({bids.length})
                    </h2>
                    <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
                      All bids placed on this auction
                    </p>
                  </div>
                  <div class="flex space-x-2">
                    {#if showBidSection}
                      <Button
                        variant="primary"
                        size="small"
                        on:click={openBidModal}
                        disabled={!canBid}
                      >
                        <svg class="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
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
                      <svg class="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                      </svg>
                      Refresh
                    </Button>
                  </div>
                </div>
                
                {#if bidsLoading}
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
                      {$t('auction.noBids')}
                    </h3>
                    <p class="text-gray-500 dark:text-gray-400 mb-6">
                      {$t('auction.beTheFirst')}
                    </p>
                    {#if canBid}
                      <Button
                        variant="primary"
                        on:click={openBidModal}
                      >
                        <svg class="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
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
                  <div class="space-y-4">
                    {#each bids as bid, index (bid.id)}
                      <div class="p-4 rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-150 {index === 0 ? 'bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 border-green-200 dark:border-green-800' : ''} {bid.bidder_info?.id === $user?.id ? 'bg-gradient-to-r from-primary-50 to-blue-50 dark:from-primary-900/20 dark:to-blue-900/20 border-primary-200 dark:border-primary-800' : ''}">
                        <div class="flex justify-between items-start">
                          <div class="flex items-center space-x-4">
                            <div class="flex-shrink-0">
                              {#if index === 0}
                                <div class="w-10 h-10 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-full flex items-center justify-center">
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
                            </div>
                            
                            <div>
                              <div class="flex items-center space-x-3 mb-1">
                                <p class="text-xl font-bold text-gray-900 dark:text-white">
                                  {formatCurrency(bid.amount)}
                                </p>
                                {#if index === 0}
                                  <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                                    🏆 Highest Bid
                                  </span>
                                {/if}
                                {#if bid.bidder_info?.id === $user?.id}
                                  <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800 dark:bg-primary-900 dark:text-primary-200">
                                    👤 Your Bid
                                  </span>
                                {/if}
                              </div>
                              <div class="flex items-center space-x-2">
                                <p class="text-sm font-medium text-gray-700 dark:text-gray-300">
                                  {bid.bidder_info?.name || $t('auction.anonymous')}
                                </p>
                                {#if bid.is_verified}
                                  <svg class="h-4 w-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                                  </svg>
                                {/if}
                              </div>
                            </div>
                          </div>
                          
                          <div class="text-right">
                            <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">
                              {getTimeAgo(bid.bid_time)}
                            </p>
                            <p class="text-xs text-gray-400 dark:text-gray-500">
                              {formatDateTime(bid.bid_time)}
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
              <div>
                <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                  {$t('auction.termsConditions')}
                </h2>
                
                {#if auction.terms_conditions}
                  <div class="prose dark:prose-invert max-w-none text-gray-600 dark:text-gray-300 bg-gray-50 dark:bg-gray-700 p-6 rounded-lg">
                    <p class="whitespace-pre-wrap">{auction.terms_conditions}</p>
                  </div>
                {:else}
                  <div class="text-center py-12 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-gray-400 dark:text-gray-500 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
                      {$t('auction.noTerms')}
                    </h3>
                    <p class="text-gray-500 dark:text-gray-400">
                      {$t('auction.contactForTerms')}
                    </p>
                  </div>
                {/if}
              </div>
            {/if}
          </div>
        </div>
        
        <!-- Sidebar (right) -->
        <div class="space-y-6">
          <!-- Auction status and time remaining -->
          <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
            {#if isLiveAuction}
              <div class="mb-6">
                <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-3 flex items-center">
                  <span class="w-2 h-2 bg-red-500 rounded-full mr-2 animate-pulse"></span>
                  {$t('auction.timeRemaining')}
                </h3>
                <CountdownTimer 
                  endDate={auction.end_date}
                  onEnd={handleTimerEnd}
                />
              </div>
            {:else if auction.status === 'scheduled'}
              <div class="mb-6">
                <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-3">
                  {$t('auction.startsIn')}
                </h3>
                <CountdownTimer 
                  endDate={auction.start_date}
                  onEnd={handleTimerEnd}
                  variant="secondary"
                />
                <p class="text-gray-700 dark:text-gray-300 mt-2 text-sm">
                  {formatDateTime(auction.start_date)}
                </p>
              </div>
            {:else if auction.status === 'ended' || auction.status === 'completed'}
              <div class="mb-6">
                <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-3">
                  {$t('auction.auctionEnded')}
                </h3>
                <p class="text-gray-700 dark:text-gray-300">
                  {formatDateTime(auction.end_date)}
                </p>
                {#if auction.status === 'completed' && bids.length > 0}
                  <div class="mt-4 p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
                    <h4 class="text-sm font-medium text-green-800 dark:text-green-200 mb-2">
                      🎉 Auction Winner
                    </h4>
                    <p class="text-sm text-green-700 dark:text-green-300">
                      {bids[0]?.bidder_info?.name || 'Anonymous'} won with a bid of {formatCurrency(bids[0]?.amount || 0)}
                    </p>
                  </div>
                {/if}
              </div>
            {/if}
            
            <div class="border-t border-gray-200 dark:border-gray-700 pt-6 mb-6">
              <div class="flex justify-between items-baseline mb-2">
                <h3 class="text-lg font-medium text-gray-900 dark:text-white">
                  {$t('auction.currentBid')}
                </h3>
                <span class="text-3xl font-bold text-primary-600 dark:text-primary-400">
                  {formatCurrency(auction.current_bid || auction.starting_bid)}
                </span>
              </div>
              <p class="text-sm text-gray-500 dark:text-gray-400 mb-6">
                {$t('auction.totalBids')}: {auction.bid_count || bids.length}
              </p>
              
              <!-- MAIN SIDEBAR BID BUTTON -->
              {#if canBid}
                <div class="space-y-3">
                  <Button
                    variant="primary"
                    class="w-full text-lg py-4 font-bold"
                    on:click={openBidModal}
                    disabled={placingBid}
                    aria-label={$t('auction.placeBid')}
                  >
                    {#if placingBid}
                      <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                    {:else}
                      <svg class="w-6 h-6 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                      </svg>
                    {/if}
                    {$t('auction.placeBid')}
                  </Button>
                  <p class="text-xs text-gray-500 dark:text-gray-400 text-center">
                    {$t('auction.minimumBid')}: {formatCurrency(minimumBidAmount)}
                  </p>
                </div>
              {:else if canRegister}
                <Button
                  variant="secondary" 
                  class="w-full py-3"
                  on:click={() => showRegisterModal = true}
                  aria-label={$t('auction.registerForAuction')}
                >
                  <svg class="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
                  </svg>
                  {$t('auction.registerForAuction')}
                </Button>
              {:else if auction.status === 'scheduled'}
                {#if isRegistered}
                  <div class="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg border border-green-200 dark:border-green-800">
                    <div class="flex items-center">
                      <svg class="h-5 w-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                      </svg>
                      <span class="ml-2 text-sm font-medium text-green-800 dark:text-green-200">
                        ✅ Registered for Auction
                      </span>
                    </div>
                    <p class="text-xs text-green-600 dark:text-green-400 mt-1 ml-7">
                      You can bid when the auction starts
                    </p>
                  </div>
                {:else if $user}
                  <Button
                    variant="secondary"
                    class="w-full py-3"
                    on:click={() => showRegisterModal = true}
                    aria-label={$t('auction.registerForAuction')}
                  >
                    <svg class="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
                    </svg>
                    {$t('auction.registerForAuction')}
                  </Button>
                {:else}
                  <Button
                    variant="secondary"
                    class="w-full py-3"
                    href="/login?redirect=/auctions/{auction.slug}"
                    aria-label={$t('auction.loginToRegister')}
                  >
                    <svg class="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
                    </svg>
                    {$t('auction.loginToRegister')}
                  </Button>
                {/if}
              {:else if !$user}
                <Button
                  variant="primary"
                  class="w-full py-3"
                  href="/login?redirect=/auctions/{auction.slug}"
                  aria-label={$t('auction.loginToPlaceBid')}
                >
                  <svg class="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
                  </svg>
                  {$t('auction.loginToPlaceBid')}
                </Button>
              {:else}
                <Button
                  variant="outline"
                  class="w-full py-3"
                  href="/auctions"
                  aria-label={$t('auctions.backToAuctions')}
                >
                  <svg class="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                  </svg>
                  {$t('auctions.backToAuctions')}
                </Button>
              {/if}
            </div>
            
            <!-- Owner Controls -->
            {#if isOwner && isActiveAuction}
              <div class="border-t border-gray-200 dark:border-gray-700 pt-6">
                <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-3">
                  Owner Controls
                </h3>
                <div class="space-y-2">
                  <Button
                    variant="outline"
                    class="w-full"
                    on:click={() => showExtendModal = true}
                  >
                    <svg class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Extend Auction
                  </Button>
                </div>
              </div>
            {/if}
            
            <!-- Contact info -->
            <div class="border-t border-gray-200 dark:border-gray-700 pt-6">
              <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-3">
                {$t('auction.needHelp')}
              </h3>
              <Button
                variant="outline"
                class="w-full"
                href="/contact?subject=Auction%20{auction.id}"
                aria-label={$t('auction.contactSupport')}
              >
                <svg class="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
                {$t('auction.contactSupport')}
              </Button>
            </div>
          </div>
          
          <!-- Property Quick Info -->
          {#if property}
            <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
              <div class="p-6">
                <div class="flex justify-between items-center mb-4">
                  <h3 class="text-lg font-medium text-gray-900 dark:text-white">
                    {$t('auction.propertyInfo')}
                  </h3>
                  <a 
                    href={`/properties/${property.slug}`} 
                    class="text-sm text-primary-600 dark:text-primary-400 hover:underline"
                    target="_blank"
                  >
                    {$t('property.viewDetails')}
                  </a>
                </div>
                
                <div class="aspect-w-16 aspect-h-9 bg-gray-200 dark:bg-gray-700 rounded-lg overflow-hidden mb-4">
                  {#if property.main_image?.url}
                    <img 
                      src={property.main_image.url} 
                      alt={property.title}
                      class="w-full h-full object-cover"
                    />
                  {:else}
                    <div class="flex items-center justify-center h-full">
                      <svg class="h-12 w-12 text-gray-400 dark:text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                      </svg>
                    </div>
                  {/if}
                </div>
                
                <h4 class="font-medium text-gray-900 dark:text-white mb-3">
                  {property.title}
                </h4>
                
                <dl class="space-y-2 text-sm">
                  <div class="flex justify-between">
                    <dt class="text-gray-500 dark:text-gray-400">{$t('property.location')}:</dt>
                    <dd class="text-gray-900 dark:text-white">{property.location?.city}, {property.location?.state}</dd>
                  </div>
                  <div class="flex justify-between">
                    <dt class="text-gray-500 dark:text-gray-400">{$t('property.propertyType')}:</dt>
                    <dd class="text-gray-900 dark:text-white">{property.property_type_display}</dd>
                  </div>
                  <div class="flex justify-between">
                    <dt class="text-gray-500 dark:text-gray-400">{$t('property.size')}:</dt>
                    <dd class="text-gray-900 dark:text-white">{property.size_sqm} {$t('property.sqm')}</dd>
                  </div>
                  <div class="flex justify-between">
                    <dt class="text-gray-500 dark:text-gray-400">{$t('property.marketValue')}:</dt>
                    <dd class="text-gray-900 dark:text-white font-medium">{formatCurrency(property.market_value)}</dd>
                  </div>
                </dl>
              </div>
            </div>
          {/if}
          
          <!-- Recent Activity -->
          {#if bids.length > 0}
            <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
              <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">
                {$t('auction.recentActivity')}
              </h3>
              <div class="space-y-3">
                {#each bids.slice(0, 3) as bid}
                  <div class="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div>
                      <p class="text-sm font-medium text-gray-900 dark:text-white">
                        {formatCurrency(bid.amount)}
                      </p>
                      <p class="text-xs text-gray-500 dark:text-gray-400">
                        {bid.bidder_info?.name || 'Anonymous'}
                        {#if bid.bidder_info?.id === $user?.id}
                          <span class="text-primary-600 dark:text-primary-400">({$t('auction.you')})</span>
                        {/if}
                      </p>
                    </div>
                    <div class="text-right">
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
                  class="w-full mt-3"
                >
                  {$t('auction.viewAllBids')} ({bids.length})
                </Button>
              </div>
            </div>
          {/if}
        </div>
      </div>
    {/if}
  </div>
</div>

<!-- Enhanced Bid Modal -->
<Modal
  bind:show={showBidModal}
  title={$t('auction.placeBid')}
  maxWidth="lg"
>
  <form on:submit|preventDefault={handleBidSubmission} class="space-y-6 p-6">
    {#if bidError}
      <Alert type="error" message={bidError} />
    {/if}
    
    <!-- Current Auction Status -->
    <div class="bg-gradient-to-r from-primary-50 to-blue-50 dark:from-primary-900/20 dark:to-blue-900/20 p-6 rounded-lg border border-primary-200 dark:border-primary-800">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
        <div>
          <div class="text-sm text-primary-700 dark:text-primary-300 mb-1">Current Bid</div>
          <div class="text-2xl font-bold text-primary-600 dark:text-primary-400">
            {formatCurrency(auction?.current_bid || auction?.starting_bid)}
          </div>
        </div>
        <div>
          <div class="text-sm text-primary-700 dark:text-primary-300 mb-1">Minimum Bid</div>
          <div class="text-xl font-semibold text-primary-800 dark:text-primary-200">
            {formatCurrency(minimumBidAmount)}
          </div>
        </div>
        <div>
          <div class="text-sm text-primary-700 dark:text-primary-300 mb-1">Total Bids</div>
          <div class="text-xl font-semibold text-primary-800 dark:text-primary-200">
            {auction?.bid_count || bids.length}
          </div>
        </div>
      </div>
    </div>
    
    <!-- Bid Amount Input -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
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
    <div class="border-t border-gray-200 dark:border-gray-700 pt-6">
      <h4 class="text-lg font-medium text-gray-900 dark:text-white mb-4">
        Advanced Options
      </h4>
      
      <div class="space-y-4">
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
    <div class="bg-yellow-50 dark:bg-yellow-900/20 p-4 rounded-lg border border-yellow-200 dark:border-yellow-800">
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
            <p>{$t('auction.bidDisclaimer')}</p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Action Buttons -->
    <div class="flex justify-end space-x-3 pt-6 border-t border-gray-200 dark:border-gray-700">
      <Button
        variant="outline"
        type="button"
        on:click={() => showBidModal = false}
        disabled={placingBid}
        aria-label={$t('common.cancel')}
      >
        {$t('common.cancel')}
      </Button>
      
      <Button
        variant="primary"
        type="submit"
        loading={placingBid}
        disabled={placingBid || !bidAmount || parseFloat(bidAmount) < minimumBidAmount}
        aria-label={$t('auction.confirmBid')}
        class="px-8"
      >
        {#if placingBid}
          <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        {:else}
          <svg class="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        {/if}
        {enableAutoBidding ? 'Place Auto-Bid' : $t('auction.confirmBid')}
      </Button>
    </div>
  </form>
</Modal>

<!-- Login Modal -->
<Modal
  bind:show={showLoginModal}
  title={$t('auction.loginRequired')}
  maxWidth="sm"
>
  <div class="text-center py-4 p-6">
    <div class="w-16 h-16 bg-yellow-100 dark:bg-yellow-900 rounded-full flex items-center justify-center mx-auto mb-4">
      <svg class="w-8 h-8 text-yellow-600 dark:text-yellow-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
      </svg>
    </div>
    
    <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">
      Sign In Required
    </h3>
    <p class="mb-6 text-gray-600 dark:text-gray-400">
      {$t('auction.loginRequiredMessage')}
    </p>
    
    <div class="flex flex-col sm:flex-row justify-center gap-3">
      <Button
        variant="outline"
        on:click={() => showLoginModal = false}
        aria-label={$t('common.cancel')}
      >
        {$t('common.cancel')}
      </Button>
      
      <Button
        variant="primary"
        href={`/login?redirect=/auctions/${auction?.slug}`}
        aria-label={$t('nav.login')}
      >
        {$t('nav.login')}
      </Button>
    </div>
  </div>
</Modal>

<!-- Registration Modal -->
<Modal
  bind:show={showRegisterModal}
  title="Register for Auction"
  maxWidth="md"
>
  <div class="p-6">
    <div class="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg mb-6">
      <h4 class="text-lg font-semibold text-blue-900 dark:text-blue-100 mb-2">
        Auction Registration Required
      </h4>
      <p class="text-sm text-blue-700 dark:text-blue-300">
        You must register for this auction before you can place bids. Registration helps ensure serious bidders and auction integrity.
      </p>
    </div>
    
    <div class="space-y-4">
      <div class="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
        <h5 class="font-medium text-gray-900 dark:text-white mb-2">Registration Requirements:</h5>
        <ul class="text-sm text-gray-600 dark:text-gray-400 space-y-1">
          <li class="flex items-center">
            <svg class="h-4 w-4 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
            Verified email address
          </li>
          <li class="flex items-center">
            <svg class="h-4 w-4 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
            Account in good standing
          </li>
          <li class="flex items-center">
            <svg class="h-4 w-4 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
            Agreement to terms and conditions
          </li>
        </ul>
      </div>
      
      <div class="bg-yellow-50 dark:bg-yellow-900/20 p-4 rounded-lg border border-yellow-200 dark:border-yellow-800">
        <p class="text-sm text-yellow-800 dark:text-yellow-200">
          <strong>Note:</strong> Registration for this auction is free and only takes a moment. Once registered, you'll be able to place bids throughout the auction period.
        </p>
      </div>
    </div>
    
    <div class="flex justify-end space-x-3 mt-6">
      <Button
        variant="outline"
        on:click={() => showRegisterModal = false}
      >
        Cancel
      </Button>
      
      <Button
        variant="primary"
        on:click={handleAuctionRegistration}
      >
        <svg class="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
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
  <form on:submit|preventDefault={handleExtendAuction} class="space-y-6 p-6">
    <div class="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
      <h4 class="text-lg font-semibold text-blue-900 dark:text-blue-100 mb-2">
        Extend Auction Time
      </h4>
      <p class="text-sm text-blue-700 dark:text-blue-300">
        Current end time: {formatDateTime(auction?.end_date)}
      </p>
    </div>
    
    <FormField
      type="number"
      id="extension_hours"
      label="Extension Hours"
      bind:value={extensionHours}
      min={1}
      max={168}
      step="1"
      required={true}
      helpText="Number of hours to extend the auction (max 7 days)"
    />
    
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
    
    <div class="flex justify-end space-x-3">
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
      >
        Extend Auction
      </Button>
    </div>
  </form>
</Modal>