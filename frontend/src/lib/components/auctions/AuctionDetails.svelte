<!-- src/lib/components/auctions/AuctionDetails.svelte -->
<script>
  import { onMount, onDestroy } from 'svelte';
  import { t } from '$lib/i18n';
  import { formatCurrency, formatDate } from '$lib/utils/format';
  import auctionService from '$lib/services/auction';
  import { websocket } from '$lib/services/websocket';
  import { fade } from 'svelte/transition';
  import { toast } from '$lib/stores/toast';
  import { authStore } from '$lib/stores/auth';
  
  // Components
  import AuctionTimer from './AuctionTimer.svelte';
  import BidForm from './BidForm.svelte';
  import BidHistory from './BidHistory.svelte';
  import PropertyCard from '../properties/PropertyCard.svelte';
  import ImageGallery from '../ui/ImageGallery.svelte';
  import TabGroup from '../ui/TabGroup.svelte';
  import Button from '../ui/Button.svelte';
  import Loader from '../ui/Loader.svelte';
  
  // Props
  export let auctionId;
  
  // State
  let auction = null;
  let property = null;
  let bids = [];
  let loading = true;
  let error = null;
  let activeTab = 'details'; // details, property, history
  let imageModalOpen = false;
  let selectedImageIndex = 0;
  let watchStatus = false;
  let watchLoading = false;
  let wsConnection = null;
  
  // Derived state
  $: isActive = auction?.status === 'active';
  $: isEnded = ['closed', 'sold', 'cancelled'].includes(auction?.status);
  $: isPending = auction?.status === 'pending';
  $: canBid = isActive && !loading && $authStore.isAuthenticated;
  $: isAuthenticated = $authStore.isAuthenticated;
  
  // Status badge styling
  function getStatusColor(status) {
    const colors = {
      'active': 'bg-success-500 text-white',
      'pending': 'bg-warning-500 text-white',
      'extended': 'bg-info-500 text-white',
      'closed': 'bg-neutral-500 text-white',
      'sold': 'bg-accent-500 text-white',
      'cancelled': 'bg-error-500 text-white'
    };
    
    return colors[status] || 'bg-neutral-500 text-white';
  }
  
  // Tab definitions
  const tabs = [
    { id: 'details', label: 'auctions.auction_details' },
    { id: 'property', label: 'properties.property_details' },
    { id: 'history', label: 'auctions.bid_history' }
  ];
  
  // Load auction data
  async function loadAuction() {
    loading = true;
    error = null;
    
    try {
      const response = await auctionService.getAuctionDetails(auctionId, {
        include_property: true,
        include_bids: true,
        include_documents: true
      });
      
      if (response.success) {
        auction = response.data.auction;
        property = response.data.auction.related_property;
        bids = response.data.auction.recent_bids || [];
        
        // Set document title
        if (typeof document !== 'undefined') {
          document.title = `${auction.title} | ${t('site.title')}`;
        }
        
        // Initialize WebSocket connection
        initWebSocketConnection();
      } else {
        throw new Error(response.error || t('system_messages.error_occurred'));
      }
    } catch (err) {
      console.error('Error fetching auction details:', err);
      error = err.message || t('system_messages.error_occurred');
    } finally {
      loading = false;
    }
  }
  
  // Initialize WebSocket connection for real-time updates
  function initWebSocketConnection() {
    if (!auction || !auction.id) return;
    
    // Close existing connection if any
    if (wsConnection) {
      wsConnection.close();
    }
    
    // Create new connection
    try {
      // Auction updates WebSocket
      const { AuctionService, BiddingService } = websocket;
      
      wsConnection = {
        auction: new AuctionService(auction.id),
        bidding: new BiddingService(auction.id)
      };
      
      // Subscribe to auction updates
      wsConnection.auction.subscribe(handleAuctionUpdate);
      
      // Subscribe to bidding updates
      wsConnection.bidding.subscribe(handleBiddingUpdate);
      
      // Get watch status if authenticated
      if (isAuthenticated) {
        getWatchStatus();
      }
    } catch (error) {
      console.error('WebSocket connection error:', error);
    }
  }
  
  // Handle auction updates from WebSocket
  function handleAuctionUpdate(data) {
    if (!data) return;
    
    if (data.type === 'auction_state' || data.type === 'initial_state') {
      // Update auction data
      auction = {
        ...auction,
        ...data
      };
    } else if (data.type === 'price_update') {
      // Update current bid
      auction.current_bid = data.data.current_bid;
      auction.bid_count = data.data.bid_count;
    } else if (data.type === 'status_update') {
      // Update auction status
      auction.status = data.status;
      auction.status_display = data.status_display;
      
      // Show toast notification
      toast.info(data.message || t('auctions.status_changed'));
    } else if (data.type === 'time_update') {
      // Update time remaining
      auction.time_remaining = data.time_remaining;
      auction.end_date = data.end_date;
    } else if (data.type === 'extension_update') {
      // Handle auction extension
      auction.end_date = data.new_end_date;
      auction.time_remaining = data.time_remaining;
      auction.status = 'extended';
      
      // Show toast notification
      toast.info(t('auctions.extended_message', { minutes: data.extension_minutes }));
    } else if (data.type === 'watch_status') {
      // Update watch status
      watchStatus = data.is_watching;
      watchLoading = false;
    }
  }
  
  // Handle bidding updates from WebSocket
  function handleBiddingUpdate(data) {
    if (!data) return;
    
    if (data.type === 'new_bid') {
      // Add new bid to the bids list
      bids = [data.bid, ...bids];
      
      // Update auction current bid
      if (auction) {
        auction.current_bid = data.bid.bid_amount;
        auction.bid_count = (auction.bid_count || 0) + 1;
      }
      
      // Show toast notification for others' bids
      if (data.bid.bidder?.id !== $authStore.user?.id) {
        toast.info(t('auctions.new_bid_placed', { amount: formatCurrency(data.bid.bid_amount) }));
      }
    } else if (data.type === 'bidding_init' && data.recent_bids) {
      // Initialize with recent bids
      bids = data.recent_bids;
    } else if (data.type === 'recent_bids') {
      // Update bids list
      bids = data.bids;
    }
  }
  
  // Handle bid placement
  async function handleBidPlaced(event) {
    const { bid, amount } = event.detail;
    
    // Show success message
    toast.success(t('auctions.bid_placed_success', { amount: formatCurrency(amount) }));
    
    // Refresh auction data (should now happen automatically via WebSocket)
  }
  
  // Get auction watch status
  async function getWatchStatus() {
    if (!isAuthenticated || !wsConnection?.auction) return;
    
    watchLoading = true;
    wsConnection.auction.getWatchStatus().catch(err => {
      console.error('Error getting watch status:', err);
      watchLoading = false;
    });
  }
  
  // Toggle auction watch status
  async function toggleWatchStatus() {
    if (!isAuthenticated) {
      toast.warning(t('auth.login_required'));
      return;
    }
    
    if (!wsConnection?.auction) return;
    
    watchLoading = true;
    
    try {
      if (watchStatus) {
        await wsConnection.auction.unwatch();
      } else {
        await wsConnection.auction.watch();
      }
    } catch (error) {
      console.error('Error toggling watch status:', error);
      watchLoading = false;
      toast.error(t('system_messages.error_occurred'));
    }
  }
  
  // Handle image click
  function handleImageClick(index) {
    selectedImageIndex = index;
    imageModalOpen = true;
  }
  
  // Initialize on mount
  onMount(() => {
    loadAuction();
    
    // Return cleanup function
    return () => {
      if (wsConnection) {
        if (wsConnection.auction) wsConnection.auction.close();
        if (wsConnection.bidding) wsConnection.bidding.close();
      }
    };
  });
  
  onDestroy(() => {
    // Cleanup WebSocket connections
    if (wsConnection) {
      if (wsConnection.auction) wsConnection.auction.close();
      if (wsConnection.bidding) wsConnection.bidding.close();
    }
  });
</script>

<div class="min-h-screen bg-neutral-50 dark:bg-neutral-900">
  {#if loading}
    <div class="flex justify-center p-20">
      <Loader size="xl" />
    </div>
  {:else if error}
    <div class="container mx-auto px-4 py-8">
      <div class="rounded-xl bg-error-100 dark:bg-error-900/20 p-6 text-center">
        <p class="text-error-700 dark:text-error-400">{error}</p>
        <Button 
          variant="primary"
          class="mt-4"
          on:click={loadAuction}
        >
          {t('general.retry')}
        </Button>
      </div>
    </div>
  {:else if auction}
    <div class="container mx-auto px-4 py-8">
      <!-- Auction Header -->
      <div class="mb-8 flex flex-col lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h1 class="text-3xl font-bold text-neutral-900 dark:text-white">{auction.title}</h1>
          <p class="mt-2 text-neutral-600 dark:text-neutral-400">{property.title}</p>
          
          <div class="mt-4 flex flex-wrap gap-3">
            <span class={`rounded-full px-3 py-1 text-sm font-medium ${getStatusColor(auction.status)}`}>
              {auction.status_display || t(`auctions.status.${auction.status}`)}
            </span>
            
            <span class="rounded-full bg-primary-100 dark:bg-primary-900/30 px-3 py-1 text-sm font-medium text-primary-700 dark:text-primary-300">
              {property.property_type_display || t(`properties.types.${property.property_type}`)}
            </span>
            
            {#if auction.is_featured}
              <span class="rounded-full bg-accent-100 dark:bg-accent-900/30 px-3 py-1 text-sm font-medium text-accent-700 dark:text-accent-300">
                {t('general.featured')}
              </span>
            {/if}

            <!-- Watch/unwatch button -->
            {#if isAuthenticated}
              <button 
                on:click={toggleWatchStatus}
                disabled={watchLoading}
                class="inline-flex items-center rounded-full px-3 py-1 text-sm font-medium border border-neutral-200 dark:border-neutral-700 text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-800 transition-colors duration-200"
              >
                {#if watchLoading}
                  <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-neutral-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                {:else if watchStatus}
                  <svg class="-ml-1 mr-2 h-4 w-4" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                    <path d="M10 12a2 2 0 100-4 2 2 0 000 4z"></path>
                    <path fill-rule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clip-rule="evenodd"></path>
                  </svg>
                  {t('auctions.watching')}
                {:else}
                  <svg class="-ml-1 mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                  </svg>
                  {t('auctions.watch')}
                {/if}
              </button>
            {/if}
          </div>
        </div>
        
        <div class="mt-6 lg:mt-0">
          {#if isActive}
            <div class="rounded-xl bg-primary-50 dark:bg-primary-900/20 p-4">
              <AuctionTimer 
                endTime={auction.end_date}
                status={auction.status}
                size="large"
                on:end={loadAuction}
              />
            </div>
          {:else if isPending}
            <div class="rounded-xl bg-warning-50 dark:bg-warning-900/20 p-4">
              <AuctionTimer 
                endTime={auction.start_date}
                status={auction.status}
                size="large"
                on:end={loadAuction}
              />
            </div>
          {:else}
            <div class="rounded-xl bg-neutral-100 dark:bg-neutral-800 p-4 text-center">
              <p class="text-neutral-600 dark:text-neutral-400">
                {t('auctions.ended')}
              </p>
            </div>
          {/if}
        </div>
      </div>
      
      <!-- Main Content -->
      <div class="grid grid-cols-1 gap-8 lg:grid-cols-3">
        <!-- Left Column - Images and Description -->
        <div class="lg:col-span-2">
          <!-- Main Image -->
          <div class="mb-6 overflow-hidden rounded-xl">
            <img 
              src={auction.featured_image_url || '/images/placeholders/auction-placeholder.jpg'} 
              alt={auction.title}
              class="w-full h-80 object-cover cursor-pointer hover:opacity-95 transition-opacity"
              on:click={() => handleImageClick(0)}
            />
          </div>
          
          <!-- Image Gallery -->
          {#if property.images && property.images.length > 1}
            <div class="mb-8 grid grid-cols-4 gap-2">
              {#each property.images.slice(0, 4) as image, i}
                <div class="overflow-hidden rounded-lg">
                  <img 
                    src={image.path} 
                    alt={`${property.title} - ${i + 1}`}
                    class="h-24 w-full cursor-pointer object-cover hover:opacity-90 transition-opacity"
                    on:click={() => handleImageClick(i)}
                  />
                </div>
              {/each}
            </div>
          {/if}
          
          <!-- Tab Navigation -->
          <div class="mb-6">
            <TabGroup 
              {tabs} 
              bind:activeTab
              labels={t}
            />
          </div>
          
          <!-- Tab Content -->
          <div class="mb-8 rounded-xl bg-white dark:bg-neutral-800 shadow-sm p-6">
            {#if activeTab === 'details'}
              <!-- Auction Details -->
              <div class="space-y-6">
                <div>
                  <h3 class="text-xl font-bold text-neutral-900 dark:text-white">{auction.title}</h3>
                  <p class="mt-3 text-neutral-700 dark:text-neutral-300">{auction.description}</p>
                </div>
                
                <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                  <div>
                    <p class="text-sm text-neutral-500 dark:text-neutral-400">{t('auctions.auction_type')}</p>
                    <p class="font-medium text-neutral-800 dark:text-neutral-200">{auction.auction_type_display}</p>
                  </div>
                  
                  <div>
                    <p class="text-sm text-neutral-500 dark:text-neutral-400">{t('auctions.start_date')}</p>
                    <p class="font-medium text-neutral-800 dark:text-neutral-200">{formatDate(auction.start_date)}</p>
                  </div>
                  
                  <div>
                    <p class="text-sm text-neutral-500 dark:text-neutral-400">{t('auctions.end_date')}</p>
                    <p class="font-medium text-neutral-800 dark:text-neutral-200">{formatDate(auction.end_date)}</p>
                  </div>
                  
                  <div>
                    <p class="text-sm text-neutral-500 dark:text-neutral-400">{t('auctions.starting_price')}</p>
                    <p class="font-medium text-neutral-800 dark:text-neutral-200">{formatCurrency(auction.starting_price)}</p>
                  </div>
                  
                  <div>
                    <p class="text-sm text-neutral-500 dark:text-neutral-400">{t('auctions.current_bid')}</p>
                    <p class="font-bold text-primary-600 dark:text-primary-400">{formatCurrency(auction.current_bid)}</p>
                  </div>
                  
                  <div>
                    <p class="text-sm text-neutral-500 dark:text-neutral-400">{t('auctions.min_increment')}</p>
                    <p class="font-medium text-neutral-800 dark:text-neutral-200">{formatCurrency(auction.min_bid_increment)}</p>
                  </div>
                </div>
                
                {#if auction.terms_conditions}
                  <div>
                    <h4 class="mb-2 text-lg font-medium text-neutral-900 dark:text-white">{t('auctions.auction_terms')}</h4>
                    <div class="rounded-lg bg-neutral-50 dark:bg-neutral-700/30 p-4 text-neutral-700 dark:text-neutral-300">
                      <p>{auction.terms_conditions}</p>
                    </div>
                  </div>
                {/if}
              </div>
            {:else if activeTab === 'property'}
              <!-- Property Details -->
              <div class="space-y-6">
                <div>
                  <h3 class="text-xl font-bold text-neutral-900 dark:text-white">{property.title}</h3>
                  <p class="mt-3 text-neutral-700 dark:text-neutral-300">{property.description}</p>
                </div>
                
                <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                  <div>
                    <p class="text-sm text-neutral-500 dark:text-neutral-400">{t('properties.property_type')}</p>
                    <p class="font-medium text-neutral-800 dark:text-neutral-200">{property.property_type_display}</p>
                  </div>
                  
                  <div>
                    <p class="text-sm text-neutral-500 dark:text-neutral-400">{t('properties.property_area')}</p>
                    <p class="font-medium text-neutral-800 dark:text-neutral-200">{property.area} m²</p>
                  </div>
                  
                  <div>
                    <p class="text-sm text-neutral-500 dark:text-neutral-400">{t('properties.property_location')}</p>
                    <p class="font-medium text-neutral-800 dark:text-neutral-200">{property.city}, {property.district}</p>
                  </div>
                  
                  {#if property.bedrooms > 0}
                    <div>
                      <p class="text-sm text-neutral-500 dark:text-neutral-400">{t('properties.bedrooms')}</p>
                      <p class="font-medium text-neutral-800 dark:text-neutral-200">{property.bedrooms}</p>
                    </div>
                  {/if}
                  
                  {#if property.bathrooms > 0}
                    <div>
                      <p class="text-sm text-neutral-500 dark:text-neutral-400">{t('properties.bathrooms')}</p>
                      <p class="font-medium text-neutral-800 dark:text-neutral-200">{property.bathrooms}</p>
                    </div>
                  {/if}
                  
                  {#if property.year_built}
                    <div>
                      <p class="text-sm text-neutral-500 dark:text-neutral-400">{t('properties.build_year')}</p>
                      <p class="font-medium text-neutral-800 dark:text-neutral-200">{property.year_built}</p>
                    </div>
                  {/if}
                </div>
                
                {#if property.features && property.features.length > 0}
                  <div>
                    <h4 class="mb-2 text-lg font-medium text-neutral-900 dark:text-white">{t('properties.property_features')}</h4>
                    <div class="flex flex-wrap gap-2">
                      {#each property.features as feature}
                        <span class="rounded-full bg-neutral-100 dark:bg-neutral-700 px-3 py-1 text-sm text-neutral-700 dark:text-neutral-300">
                          {feature}
                        </span>
                      {/each}
                    </div>
                  </div>
                {/if}
              </div>
            {:else if activeTab === 'history'}
              <!-- Bid History -->
              <BidHistory 
                auctionId={auctionId} 
                bids={bids}
                on:refresh={() => {
                  if (wsConnection?.bidding) {
                    wsConnection.bidding.getRecentBids();
                  }
                }}
              />
            {/if}
          </div>
        </div>
        
        <!-- Right Column - Bid Form and Summary -->
        <div>
          <!-- Bid Form Card -->
          <div class="mb-6 rounded-xl bg-white dark:bg-neutral-800 shadow-sm p-6 sticky top-6">
            <h3 class="mb-4 text-xl font-bold text-neutral-900 dark:text-white">{t('auctions.place_bid')}</h3>
            
            <div class="mb-4 space-y-4">
              <div>
                <p class="text-sm text-neutral-500 dark:text-neutral-400">{t('auctions.current_bid')}</p>
                <p class="text-2xl font-bold text-primary-600 dark:text-primary-400">{formatCurrency(auction.current_bid)}</p>
              </div>
              
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-sm text-neutral-500 dark:text-neutral-400">{t('auctions.bid_count')}</p>
                  <p class="text-lg font-medium text-neutral-800 dark:text-neutral-200">{auction.bid_count}</p>
                </div>
                
                <div>
                  <p class="text-sm text-neutral-500 dark:text-neutral-400">{t('auctions.min_increment')}</p>
                  <p class="text-lg font-medium text-neutral-800 dark:text-neutral-200">{formatCurrency(auction.min_bid_increment)}</p>
                </div>
              </div>
            </div>
            
            <div class="mt-6">
              <!-- Bid Form or Status Message based on auction status -->
              {#if canBid}
                <BidForm 
                  {auction}
                  on:bid-placed={handleBidPlaced}
                />
              {:else if !isAuthenticated}
                <div class="rounded-lg bg-warning-50 dark:bg-warning-900/20 p-4 text-center">
                  <p class="text-warning-700 dark:text-warning-400 mb-3">
                    {t('auth.login_required_bid')}
                  </p>
                  <a 
                    href="/auth/login?redirect=/auctions/{auctionId}" 
                    class="inline-block w-full rounded-lg bg-primary-500 py-3 text-center text-sm font-medium text-white hover:bg-primary-600 transition"
                  >
                    {t('auth.login')}
                  </a>
                </div>
              {:else if isPending}
                <div class="rounded-lg bg-warning-50 dark:bg-warning-900/20 p-4 text-center">
                  <p class="text-warning-700 dark:text-warning-400">
                    {t('auctions.starts_in')}
                  </p>
                </div>
              {:else if isEnded}
                <div class="rounded-lg bg-neutral-100 dark:bg-neutral-700/30 p-4 text-center">
                  <p class="text-neutral-600 dark:text-neutral-400">
                    {t('auctions.ended')}
                  </p>
                </div>
              {/if}
            </div>
          </div>
          
          <!-- Property Summary Card -->
          <div class="rounded-xl bg-white dark:bg-neutral-800 shadow-sm p-6">
            <h3 class="mb-4 text-lg font-bold text-neutral-900 dark:text-white">{t('properties.property_details')}</h3>
            
            <div class="space-y-4">
              <div class="flex items-center">
                <div class="mr-3 h-10 w-10 flex-shrink-0 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center">
                  <!-- Building icon -->
                  <svg class="h-5 w-5 text-primary-600 dark:text-primary-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z" />
                  </svg>
                </div>
                
                <div class="flex-grow">
                  <p class="text-sm text-neutral-500 dark:text-neutral-400">{t('properties.property_type')}</p>
                  <p class="font-medium text-neutral-800 dark:text-neutral-200">{property.property_type_display}</p>
                </div>
              </div>
              
              <div class="flex items-center">
                <div class="mr-3 h-10 w-10 flex-shrink-0 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center">
                  <!-- Location icon -->
                  <svg class="h-5 w-5 text-primary-600 dark:text-primary-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clip-rule="evenodd" />
                  </svg>
                </div>
                
                <div class="flex-grow">
                  <p class="text-sm text-neutral-500 dark:text-neutral-400">{t('properties.property_location')}</p>
                  <p class="font-medium text-neutral-800 dark:text-neutral-200">{property.city}, {property.district}</p>
                </div>
              </div>
              
              <div class="flex items-center">
                <div class="mr-3 h-10 w-10 flex-shrink-0 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center">
                  <!-- Area icon -->
                  <svg class="h-5 w-5 text-primary-600 dark:text-primary-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M4 4a2 2 0 012-2h8a2 2 0 012 2v12a1 1 0 01-1 1h-2a1 1 0 01-1-1v-2a1 1 0 00-1-1H9a1 1 0 00-1 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V4zm3 1h2v2H7V5zm2 4H7v2h2V9zm2-4h2v2h-2V5zm2 4h-2v2h2V9z" clip-rule="evenodd" />
                  </svg>
                </div>
                
                <div class="flex-grow">
                  <p class="text-sm text-neutral-500 dark:text-neutral-400">{t('properties.property_area')}</p>
                  <p class="font-medium text-neutral-800 dark:text-neutral-200">{property.area} m²</p>
                </div>
              </div>
            </div>
            
            <div class="mt-6">
              <a 
                href={`/properties/${property.id}`}
                class="block w-full rounded-lg bg-primary-50 dark:bg-primary-900/20 py-3 text-center text-sm font-medium text-primary-600 dark:text-primary-400 transition hover:bg-primary-500 hover:text-white"
              >
                {t('properties.view_property')}
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  {:else}
    <div class="flex h-32 items-center justify-center">
      <p class="text-neutral-500 dark:text-neutral-400">{t('general.not_found')}</p>
    </div>
  {/if}
  
  <!-- Image Gallery Modal -->
  {#if imageModalOpen && property?.images?.length > 0}
    <div 
      class="fixed inset-0 z-50 bg-black bg-opacity-90 flex items-center justify-center p-4"
      on:click={() => imageModalOpen = false}
      transition:fade={{ duration: 200 }}
    >
      <div 
        class="relative max-w-5xl"
        on:click|stopPropagation
      >
        <button 
          class="absolute top-4 right-4 bg-white/10 rounded-full p-2 text-white hover:bg-white/20 transition-colors"
          on:click={() => imageModalOpen = false}
        >
          <svg class="h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
        
        <ImageGallery 
          images={property.images.map(img => img.path)} 
          startIndex={selectedImageIndex}
        />
      </div>
    </div>
  {/if}
</div>