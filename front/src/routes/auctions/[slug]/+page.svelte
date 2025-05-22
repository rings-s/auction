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
  import LiveBidding from '$lib/components/auction/LiveBidding.svelte';
  
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
  let refreshInterval;
  let websocket = null;
  
  // Enhanced bidding state
  let bidAmount = '';
  let maxBidAmount = '';
  let placingBid = false;
  let quickBidAmounts = [];
  let enableAutoBidding = false;
  let bidNotes = '';
  
  // Real-time updates
  let newBidNotifications = [];
  let lastBidCount = 0;
  
  // Auction extension
  let extensionHours = 24;
  let extensionReason = '';
  
  $: slug = $page.params.slug;
  $: isLiveAuction = auction?.status === 'live';
  $: canBid = isLiveAuction && $user && new Date(auction?.end_date) > new Date() && !isOwner;
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
  
  // Initialize WebSocket connection for real-time updates
  function initializeWebSocket() {
    if (!auction || !isLiveAuction) return;
    
    try {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.host}/ws/auctions/${auction.id}/`;
      
      websocket = new WebSocket(wsUrl);
      
      websocket.onopen = function(event) {
        console.log('WebSocket connected to auction:', auction.id);
      };
      
      websocket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
      };
      
      websocket.onerror = function(error) {
        console.error('WebSocket error:', error);
      };
      
      websocket.onclose = function(event) {
        console.log('WebSocket closed');
        if (isLiveAuction) {
          setTimeout(initializeWebSocket, 5000);
        }
      };
    } catch (error) {
      console.error('Failed to initialize WebSocket:', error);
    }
  }
  
  function handleWebSocketMessage(data) {
    if (data.type === 'auction_data' || data.type === 'auction_update') {
      if (data.auction) {
        auction = { ...auction, ...data.auction };
        quickBidAmounts = generateQuickBidAmounts();
      }
      
      if (data.bids) {
        const newBidCount = data.bids.length;
        if (newBidCount > lastBidCount && lastBidCount > 0) {
          // New bids arrived
          const newBids = data.bids.slice(0, newBidCount - lastBidCount);
          newBids.forEach(bid => {
            if (bid.bidder_info?.id !== $user?.id) {
              addBidNotification(bid);
            }
          });
        }
        bids = data.bids;
        lastBidCount = newBidCount;
      }
    } else if (data.type === 'bid_success') {
      bidSuccess = data.message;
      bidError = '';
      showBidModal = false;
      loadAuctionData();
    } else if (data.type === 'error') {
      bidError = data.message;
      bidSuccess = '';
    }
  }
  
  function addBidNotification(bid) {
    const notification = {
      id: Date.now() + Math.random(),
      bid,
      timestamp: new Date()
    };
    
    newBidNotifications = [notification, ...newBidNotifications.slice(0, 4)];
    
    setTimeout(() => {
      newBidNotifications = newBidNotifications.filter(n => n.id !== notification.id);
    }, 5000);
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
      
      if (isLiveAuction) {
        initializeWebSocket();
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
      bids = response.results || response;
      lastBidCount = bids.length;
      
    } catch (err) {
      console.error('Error loading auction bids:', err);
    } finally {
      bidsLoading = false;
    }
  }
  
  // Enhanced bid submission with validation
  async function handleBidSubmission() {
    const bidValue = parseFloat(bidAmount);
    const maxBidValue = maxBidAmount ? parseFloat(maxBidAmount) : null;
    
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
      bidError = '';
      bidSuccess = '';
      placingBid = true;
      
      // Use WebSocket for live auctions, API for others
      if (websocket && websocket.readyState === WebSocket.OPEN) {
        websocket.send(JSON.stringify({
          type: 'place_bid',
          amount: bidValue,
          max_bid: maxBidValue,
          notes: bidNotes,
          auto_bidding: enableAutoBidding
        }));
      } else {
        await placeBid(auction.id, bidValue);
        bidSuccess = $t('auction.bidPlaced');
        showBidModal = false;
        await Promise.all([loadAuctionData(), loadAuctionBids()]);
      }
      
      // Reset form
      bidAmount = '';
      maxBidAmount = '';
      bidNotes = '';
      enableAutoBidding = false;
      quickBidAmounts = generateQuickBidAmounts();
      
    } catch (err) {
      console.error('Error placing bid:', err);
      bidError = err.message || $t('error.bidFailed');
    } finally {
      placingBid = false;
    }
  }
  
  // Quick bid functionality
  async function handleQuickBid(amount) {
    if (placingBid) return;
    
    bidAmount = amount.toString();
    await handleBidSubmission();
  }
  
  // Open bid modal with prefilled minimum amount
  function openBidModal() {
    if (!$user) {
      showLoginModal = true;
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
  
  function handleBidPlaced() {
    loadAuctionData();
    loadAuctionBids();
    quickBidAmounts = generateQuickBidAmounts();
  }
  
  // Handle auction extension
  async function handleExtendAuction() {
    try {
      if (!extensionHours || extensionHours < 1) {
        error = 'Please enter a valid extension time';
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
  
  function handleAuctionEnded(event) {
    const { winningBid, notes } = event.detail;
    console.log('Auction ended with winner:', winningBid, 'Notes:', notes);
    auction = { ...auction, status: 'completed' };
    bidSuccess = `Auction completed! Winner: ${winningBid.bidder_info?.name || 'Anonymous'}`;
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
  
  function handleTimerEnd() {
    loadAuctionData();
    loadAuctionBids();
    
    if (websocket) {
      websocket.close();
      websocket = null;
    }
  }
  
  onMount(async () => {
    await loadAuctionData();
    await loadAuctionBids();
    
    if (!isLiveAuction) {
      refreshInterval = setInterval(async () => {
        if (!placingBid) {
          await Promise.all([loadAuctionData(), loadAuctionBids()]);
          quickBidAmounts = generateQuickBidAmounts();
        }
      }, 30000);
    }
  });
  
  onDestroy(() => {
    if (refreshInterval) {
      clearInterval(refreshInterval);
    }
    
    if (websocket) {
      websocket.close();
    }
  });
  
  const tabs = [
    { id: 'details', label: $t('auction.tabDetails') },
    { id: 'property', label: $t('auction.tabProperty') },
    { id: 'bids', label: $t('auction.tabBids') },
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
    
    <!-- Bid Notifications -->
    {#if newBidNotifications.length > 0}
      <div class="fixed top-20 right-4 z-50 space-y-2">
        {#each newBidNotifications as notification (notification.id)}
          <div 
            class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg p-4 max-w-sm transform transition-all duration-300 ease-in-out"
            style="animation: slideIn 0.3s ease-out;"
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
      
      <!-- Enhanced Quick Bidding Section for Live Auctions -->
      {#if canBid && isLiveAuction}
        <div class="mb-8 bg-gradient-to-r from-primary-500 to-blue-600 rounded-xl shadow-lg overflow-hidden">
          <div class="px-6 py-4 bg-black bg-opacity-20">
            <div class="flex items-center justify-between">
              <div>
                <h2 class="text-xl font-bold text-white flex items-center">
                  <span class="w-3 h-3 bg-red-500 rounded-full mr-2 animate-pulse"></span>
                  {$t('auction.liveBidding')}
                </h2>
                <p class="text-primary-100 text-sm">
                  Current: {formatCurrency(auction.current_bid || auction.starting_bid)} • 
                  Min Bid: {formatCurrency(minimumBidAmount)}
                </p>
              </div>
              <div class="text-right text-white">
                <div class="text-2xl font-bold">
                  {auction.bid_count || bids.length}
                </div>
                <div class="text-sm opacity-90">Total Bids</div>
              </div>
            </div>
          </div>
          
          <!-- Quick Bid Buttons -->
          <div class="p-6">
            <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
              {#each quickBidAmounts as option}
                <button
                  type="button"
                  class="group relative overflow-hidden rounded-lg p-4 border-2 border-white border-opacity-20 hover:border-opacity-40 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-white focus:ring-opacity-50 bg-white bg-opacity-10 hover:bg-opacity-20"
                  disabled={placingBid}
                  on:click={() => handleQuickBid(option.amount)}
                >
                  <div class="flex flex-col items-center space-y-1">
                    <span class="text-lg font-bold text-white">
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
            
            <!-- Advanced Bid Button -->
            <div class="flex space-x-3">
              <Button
                variant="secondary"
                class="flex-1"
                on:click={openBidModal}
                disabled={placingBid}
              >
                <svg class="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4" />
                </svg>
                {$t('auction.advancedBidding')}
              </Button>
              
              {#if userHighestBid}
                <div class="flex-1 bg-white bg-opacity-10 rounded-lg p-3 text-center">
                  <div class="text-sm text-white text-opacity-80">Your Highest Bid</div>
                  <div class="text-lg font-bold text-white">
                    {formatCurrency(userHighestBid.amount)}
                  </div>
                  <div class="text-xs text-white text-opacity-60">
                    {userHighestBid.status === 'winning' ? '🎉 Winning!' : '⚠️ Outbid'}
                  </div>
                </div>
              {/if}
            </div>
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
                <p>{auction.description || $t('auction.noDescription')}</p>
                
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
              <!-- Enhanced LiveBidding Component -->
              <LiveBidding 
                {auction}
                {isOwner}
                onBidPlaced={handleBidPlaced}
                on:extendAuction={() => showExtendModal = true}
                on:auctionEnded={handleAuctionEnded}
              />
              
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
              
              {#if canBid}
                <div class="space-y-3">
                  <Button
                    variant="primary"
                    class="w-full text-lg py-3"
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
                      <svg class="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                      </svg>
                    {/if}
                    {$t('auction.placeBid')}
                  </Button>
                  <p class="text-xs text-gray-500 dark:text-gray-400 text-center">
                    {$t('auction.minimumBid')}: {formatCurrency(minimumBidAmount)}
                  </p>
                </div>
              {:else if auction.status === 'scheduled'}
                {#if $user}
                  <Button
                    variant="secondary" 
                    class="w-full"
                    on:click={() => alert('Registration successful!')}
                    aria-label={$t('auction.registerForAuction')}
                  >
                    {$t('auction.registerForAuction')}
                  </Button>
                {:else}
                  <Button
                    variant="secondary"
                    class="w-full"
                    href="/login?redirect=/auctions/{auction.slug}"
                    aria-label={$t('auction.loginToRegister')}
                  >
                    {$t('auction.loginToRegister')}
                  </Button>
                {/if}
              {:else if !$user}
                <Button
                  variant="primary"
                  class="w-full"
                  href="/login?redirect=/auctions/{auction.slug}"
                  aria-label={$t('auction.loginToPlaceBid')}
                >
                  {$t('auction.loginToPlaceBid')}
                </Button>
              {:else}
                <Button
                  variant="outline"
                  class="w-full"
                  href="/auctions"
                  aria-label={$t('auctions.backToAuctions')}
                >
                  {$t('auctions.backToAuctions')}
                </Button>
              {/if}
            </div>
            
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
                {#each bids.slice(0, 5) as bid}
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
                        {formatDateTime(bid.bid_time)}
                      </p>
                      <AuctionStatus status={bid.status} isCompact={true} />
                    </div>
                  </div>
                {/each}
                
                {#if bids.length > 5}
                  <Button
                    variant="outline"
                    size="small"
                    on:click={() => activeTab = 'bids'}
                    class="w-full mt-3"
                  >
                    {$t('auction.viewAllBids')} ({bids.length})
                  </Button>
                {/if}
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
        type="currency"
        id="bid_amount"
        label={$t('auction.bidAmount')}
        bind:value={bidAmount}
        currencySymbol="$"
        min={minimumBidAmount}
        required={true}
        class="text-lg font-semibold"
      />
      
      <FormField
        type="currency"
        id="max_bid_amount"
        label="Maximum Auto-Bid (Optional)"
        bind:value={maxBidAmount}
        currencySymbol="$"
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

<style>
@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}
</style>