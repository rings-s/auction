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
  
  // Import the enhanced LiveBidding component
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
  
  // Bidding state
  let bidAmount = '';
  let placingBid = false;
  let quickBidAmounts = [];
  
  // Auction extension
  let extensionHours = 24;
  let extensionReason = '';
  
  $: slug = $page.params.slug;
  $: isLiveAuction = auction?.status === 'live';
  $: canBid = isLiveAuction && $user && new Date(auction?.end_date) > new Date();
  $: isOwner = $user && auction?.created_by?.id === $user?.id;
  $: minimumBidAmount = calculateMinimumBid();
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
  
  function generateQuickBidAmounts() {
    if (!auction) return [];
    
    const minBid = minimumBidAmount;
    const increment = parseFloat(auction.minimum_increment) || 100;
    
    return [
      { amount: minBid, label: 'Min Bid' },
      { amount: minBid + increment, label: '+1 Inc' },
      { amount: minBid + (increment * 2), label: '+2 Inc' },
      { amount: minBid + (increment * 5), label: '+5 Inc' }
    ];
  }
  
  // Get all available images for gallery
  function getAllImages() {
    let images = [];
    
    // Add auction media first
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
    
    // Add property media if no auction images or to supplement
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
  
  // Initialize WebSocket connection for live updates
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
        
        if (data.type === 'auction_data' || data.type === 'auction_update') {
          // Update auction data from WebSocket
          if (data.auction) {
            auction = { ...auction, ...data.auction };
            quickBidAmounts = generateQuickBidAmounts();
          }
          
          // Update bids
          if (data.bids) {
            bids = data.bids;
          }
        } else if (data.type === 'bid_success') {
          bidSuccess = data.message;
          bidError = '';
          // Refresh the auction data
          loadAuctionData();
        } else if (data.type === 'error') {
          bidError = data.message;
          bidSuccess = '';
        }
      };
      
      websocket.onerror = function(error) {
        console.error('WebSocket error:', error);
      };
      
      websocket.onclose = function(event) {
        console.log('WebSocket closed');
        // Attempt to reconnect after a delay for live auctions
        if (isLiveAuction) {
          setTimeout(initializeWebSocket, 5000);
        }
      };
    } catch (error) {
      console.error('Failed to initialize WebSocket:', error);
    }
  }
  
  async function loadAuctionData() {
    loading = true;
    error = null;
    
    try {
      // Fetch auction details
      const auctionData = await fetchAuctionBySlug(slug);
      auction = auctionData;
      
      // Set property data if available
      if (auction.related_property) {
        property = auction.related_property;
      }
      
      // Generate quick bid amounts
      quickBidAmounts = generateQuickBidAmounts();
      
      // Initialize WebSocket for live auctions
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
      
    } catch (err) {
      console.error('Error loading auction bids:', err);
      // Don't show error for bids loading failure, just log it
    } finally {
      bidsLoading = false;
    }
  }
  
  // Handle bid placed from LiveBidding component
  function handleBidPlaced() {
    // Refresh auction and bids data
    loadAuctionData();
    loadAuctionBids();
    
    // Update quick bid amounts
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
  
  // Handle auction ended event from LiveBidding
  function handleAuctionEnded(event) {
    const { winningBid, notes } = event.detail;
    console.log('Auction ended with winner:', winningBid, 'Notes:', notes);
    
    // Update auction status
    auction = { ...auction, status: 'completed' };
    bidSuccess = `Auction completed! Winner: ${winningBid.bidder_info?.name || 'Anonymous'}`;
  }
  
  // Handle modal bid submission
  async function handleModalBidSubmit() {
    const bidValue = parseFloat(bidAmount);
    
    // Validate bid amount
    if (isNaN(bidValue) || bidValue < minimumBidAmount) {
      bidError = $t('auction.bidTooLow', { amount: minimumBidAmount.toLocaleString() });
      return;
    }
    
    try {
      bidError = '';
      bidSuccess = '';
      placingBid = true;
      
      // Try WebSocket first for live auctions
      if (websocket && websocket.readyState === WebSocket.OPEN) {
        websocket.send(JSON.stringify({
          type: 'place_bid',
          amount: bidValue
        }));
      } else {
        // Fallback to HTTP API
        await placeBid(auction.id, bidValue);
        
        // Show success message
        bidSuccess = $t('auction.bidPlaced');
        
        // Reload auction and bids data
        await Promise.all([
          loadAuctionData(),
          loadAuctionBids()
        ]);
      }
      
      // Reset form and close modal
      bidAmount = minimumBidAmount.toString();
      showBidModal = false;
      
      // Update quick bid amounts
      quickBidAmounts = generateQuickBidAmounts();
      
    } catch (err) {
      console.error('Error placing bid:', err);
      bidError = err.message || $t('error.bidFailed');
    } finally {
      placingBid = false;
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
  
  function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  }
  
  function handleTimerEnd() {
    // Reload auction data when timer ends
    loadAuctionData();
    loadAuctionBids();
    
    // Close WebSocket connection
    if (websocket) {
      websocket.close();
      websocket = null;
    }
  }
  
  onMount(async () => {
    await loadAuctionData();
    await loadAuctionBids();
    
    // Set up refresh interval for non-live auctions
    if (!isLiveAuction) {
      refreshInterval = setInterval(async () => {
        if (!placingBid) {
          await Promise.all([
            loadAuctionData(),
            loadAuctionBids()
          ]);
          quickBidAmounts = generateQuickBidAmounts();
        }
      }, 30000); // Refresh every 30 seconds for non-live auctions
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
  
  // Define tabs
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
              <!-- Use the enhanced LiveBidding component for the bids tab -->
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
                    class="w-full"
                    on:click={() => {
                      bidError = '';
                      bidSuccess = '';
                      bidAmount = minimumBidAmount.toString();
                      showBidModal = true;
                    }}
                    aria-label={$t('auction.placeBid')}
                  >
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

<!-- Bid Modal -->
<Modal
  bind:show={showBidModal}
  title={$t('auction.placeBid')}
  maxWidth="md"
>
  <form on:submit|preventDefault={handleModalBidSubmit} class="space-y-6 p-6">
    {#if bidError}
      <Alert type="error" message={bidError} />
    {/if}
    
    <div>
      <div class="mb-6 p-4 bg-primary-50 dark:bg-primary-900/20 rounded-lg border border-primary-200 dark:border-primary-800">
        <div class="flex justify-between items-center mb-2">
          <span class="text-sm text-primary-700 dark:text-primary-300">
            {$t('auction.currentBid')}:
          </span>
          <span class="text-xl font-bold text-primary-600 dark:text-primary-400">
            {formatCurrency(auction?.current_bid || auction?.starting_bid)}
          </span>
        </div>
        <div class="flex justify-between items-center">
          <span class="text-sm text-primary-700 dark:text-primary-300">
            {$t('auction.minimumBid')}:
          </span>
          <span class="text-lg font-medium text-primary-800 dark:text-primary-200">
            {formatCurrency(minimumBidAmount)}
          </span>
        </div>
      </div>
      
      <FormField
        type="currency"
        id="bid_amount"
        label={$t('auction.yourBid')}
        bind:value={bidAmount}
        currencySymbol="$"
        min={minimumBidAmount}
        required={true}
        helpText={$t('auction.bidDisclaimer')}
      />
    </div>
    
    <div class="flex justify-end space-x-3">
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
        disabled={placingBid}
        aria-label={$t('auction.confirmBid')}
      >
        {$t('auction.confirmBid')}
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