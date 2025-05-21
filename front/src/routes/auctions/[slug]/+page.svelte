<!-- src/routes/auctions/[slug]/+page.svelte -->
<script>
  import { onMount, onDestroy } from 'svelte';
  import { page } from '$app/stores';
  import { t } from '$lib/i18n/i18n';
  import { user } from '$lib/stores/user';
  import { 
    fetchAuctionBySlug, 
    fetchAuctionBidsBySlug, 
    placeBid 
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
  import Gallery from '$lib/components/ui/Gallery.svelte';
  import ShareButtons from '$lib/components/shared/ShareButtons.svelte';
  import FormField from '$lib/components/ui/FormField.svelte';
  
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
  let refreshInterval;
  
  // Bidding state
  let bidAmount = '';
  let placingBid = false;
  let quickBidAmounts = [];
  
  $: slug = $page.params.slug;
  $: isLiveAuction = auction?.status === 'live';
  $: canBid = isLiveAuction && $user && new Date(auction?.end_date) > new Date();
  $: minimumBidAmount = calculateMinimumBid();
  $: breadcrumbItems = [
    { label: $t('nav.home'), href: '/' },
    { label: $t('nav.auctions'), href: '/auctions' },
    { label: auction?.title || $t('auction.loading'), href: `/auctions/${slug}`, active: true }
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
      minBid,
      minBid + increment,
      minBid + (increment * 2),
      minBid + (increment * 5)
    ];
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
      
      // Initialize bid amount
      bidAmount = minimumBidAmount.toString();
      
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
  
  async function handlePlaceBid(amount = null) {
    try {
      bidError = '';
      bidSuccess = '';
      placingBid = true;
      
      // Use provided amount or form input
      const bidValue = amount || parseFloat(bidAmount);
      
      // Validate bid amount
      if (isNaN(bidValue) || bidValue < minimumBidAmount) {
        bidError = $t('auction.bidTooLow', { amount: minimumBidAmount.toLocaleString() });
        return;
      }
      
      // Submit bid using auction ID directly
      await placeBid(auction.id, bidValue);
      
      // Show success message
      bidSuccess = $t('auction.bidPlaced');
      
      // Reset form
      bidAmount = minimumBidAmount.toString();
      
      // Close modal if open
      showBidModal = false;
      
      // Reload auction and bids data
      await Promise.all([
        loadAuctionData(),
        loadAuctionBids()
      ]);
      
      // Update quick bid amounts
      quickBidAmounts = generateQuickBidAmounts();
      
    } catch (err) {
      console.error('Error placing bid:', err);
      bidError = err.message || $t('error.bidFailed');
    } finally {
      placingBid = false;
    }
  }
  
  function openBidModal() {
    if ($user) {
      bidError = '';
      bidSuccess = '';
      bidAmount = minimumBidAmount.toString();
      showBidModal = true;
    } else {
      showLoginModal = true;
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
  }
  
  onMount(async () => {
    await loadAuctionData();
    await loadAuctionBids();
    
    // Set up refresh interval for live auctions
    if (isLiveAuction) {
      refreshInterval = setInterval(async () => {
        if (!placingBid) {
          await Promise.all([
            loadAuctionData(),
            loadAuctionBids()
          ]);
          // Update quick bid amounts after refresh
          quickBidAmounts = generateQuickBidAmounts();
        }
      }, 15000); // Refresh every 15 seconds for live auctions
    }
  });
  
  onDestroy(() => {
    if (refreshInterval) {
      clearInterval(refreshInterval);
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
  <title>{auction?.title || $t('auction.loading')} | {$t('nav.auctions')}</title>
  <meta name="description" content={auction?.description || $t('auction.loading')} />
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
              {$t('auction.idLabel')}: {auction.id}
            </p>
          </div>
          <div class="flex space-x-2">
            <ShareButtons 
              url={`/auctions/${auction.slug}`} 
              title={auction.title}
            />
            {#if $user?.id === auction.created_by?.id || $user?.is_admin}
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
          <!-- Gallery -->
          <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
            <Gallery 
              images={auction.media || []} 
              fallbackImage="/images/auction-placeholder.jpg"
              alt={auction.title}
            />
          </div>
          
          <!-- Quick Bidding Section (for live auctions) -->
          {#if canBid}
            <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border-l-4 border-green-500">
              <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                <span class="w-3 h-3 bg-green-500 rounded-full mr-2 animate-pulse"></span>
                {$t('auction.quickBid')}
              </h2>
              
              <div class="mb-4 p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                <div class="flex justify-between items-center mb-2">
                  <span class="text-sm text-gray-600 dark:text-gray-400">
                    {$t('auction.currentBid')}:
                  </span>
                  <span class="text-xl font-bold text-green-600 dark:text-green-400">
                    {formatCurrency(auction.current_bid || auction.starting_bid)}
                  </span>
                </div>
                <div class="flex justify-between items-center">
                  <span class="text-xs text-gray-500 dark:text-gray-500">
                    {$t('auction.minimumBid')}:
                  </span>
                  <span class="text-sm font-medium text-gray-700 dark:text-gray-300">
                    {formatCurrency(minimumBidAmount)}
                  </span>
                </div>
              </div>
              
              <!-- Quick Bid Buttons -->
              <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 mb-4">
                {#each quickBidAmounts as amount}
                  <Button
                    variant="outline"
                    size="small" 
                    loading={placingBid}
                    disabled={placingBid}
                    onClick={() => handlePlaceBid(amount)}
                    class="text-xs hover:bg-green-50 hover:border-green-500 hover:text-green-700 dark:hover:bg-green-900/20"
                  >
                    {formatCurrency(amount)}
                  </Button>
                {/each}
              </div>
              
              <!-- Custom Bid Form -->
              <form on:submit|preventDefault={() => handlePlaceBid()} class="flex gap-2">
                <div class="flex-1">
                  <FormField
                    type="number"
                    id="custom-bid"
                    placeholder={minimumBidAmount.toString()}
                    bind:value={bidAmount}
                    min={minimumBidAmount}
                    step="1"
                    disabled={placingBid}
                  />
                </div>
                <Button
                  type="submit"
                  variant="primary"
                  loading={placingBid}
                  disabled={placingBid || !bidAmount}
                  class="px-6"
                >
                  {#if placingBid}
                    <svg class="animate-spin -ml-1 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                  {/if}
                  {$t('auction.placeBid')}
                </Button>
              </form>
            </div>
          {/if}
          
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
                      {$t('auction.startEndDates')}
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
                      {$t('auction.bidding')}
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
                    <PropertyCard {property} isCompact={true} />
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
                  <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
                    {$t('auction.bidHistory')}
                    <span class="text-sm font-normal text-gray-500 dark:text-gray-400 ml-2">
                      ({bids.length} {$t('auction.bids')})
                    </span>
                  </h2>
                  
                  <Button
                    variant="outline"
                    size="small"
                    loading={bidsLoading}
                    onClick={loadAuctionBids}
                    aria-label={$t('auction.refreshBids')}
                  >
                    <svg class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                    {$t('auction.refresh')}
                  </Button>
                </div>
                
                {#if bidsLoading}
                  <div class="py-8 text-center">
                    <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
                    <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">
                      {$t('common.loading')}
                    </p>
                  </div>
                {:else if bids.length === 0}
                  <div class="text-center py-12 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-gray-400 dark:text-gray-500 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
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
                        onClick={openBidModal}
                        aria-label={$t('auction.placeBid')}
                      >
                        {$t('auction.placeBid')}
                      </Button>
                    {/if}
                  </div>
                {:else}
                  <div class="overflow-x-auto">
                    <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                      <thead class="bg-gray-50 dark:bg-gray-700">
                        <tr>
                          <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                            {$t('auction.bidder')}
                          </th>
                          <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                            {$t('auction.bidAmount')}
                          </th>
                          <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                            {$t('auction.bidTime')}
                          </th>
                          <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                            {$t('auction.status')}
                          </th>
                        </tr>
                      </thead>
                      <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                        {#each bids as bid}
                          <tr class={bid.bidder_info?.id === $user?.id ? 'bg-primary-50 dark:bg-primary-900/20' : ''}>
                            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                              {bid.bidder_info?.name || 'Anonymous'}
                              {#if bid.bidder_info?.id === $user?.id}
                                <span class="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800 dark:bg-primary-900 dark:text-primary-200">
                                  {$t('auction.you')}
                                </span>
                              {/if}
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700 dark:text-gray-300">
                              <span class="font-medium">
                                {formatCurrency(bid.amount)}
                              </span>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                              {formatDateTime(bid.bid_time)}
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap">
                              <AuctionStatus status={bid.status} isCompact={true} />
                            </td>
                          </tr>
                        {/each}
                      </tbody>
                    </table>
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
                    onClick={openBidModal}
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
                    onClick={() => alert($t('auction.registrationSuccessful'))}
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
                  <img 
                    src={property.main_image?.url || '/images/property-placeholder.jpg'} 
                    alt={property.title}
                    class="w-full h-full object-cover"
                  />
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
                    onClick={() => activeTab = 'bids'}
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
  <form on:submit|preventDefault={() => handlePlaceBid()} class="space-y-6 p-6">
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
        onClick={() => showBidModal = false}
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
        onClick={() => showLoginModal = false}
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