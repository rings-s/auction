<!-- src/routes/auctions/[id]/+page.svelte -->
<script>
  import { onMount, onDestroy } from 'svelte';
  import { page } from '$app/stores';
  import { isAuthenticated, primaryRole, user } from '$lib/stores/authStore';
  import { auctionStore } from '$lib/stores/auctionStore';
  import { notificationStore } from '$lib/stores/notificationStore';
  import { createAuctionConnection } from '$lib/websocketService';
  import BiddingComponent from '$lib/components/auction/BiddingComponent.svelte';
  import AuctionTimer from '$lib/components/auction/AuctionTimer.svelte';
  import PropertyDetails from '$lib/components/auction/PropertyDetails.svelte';
  import VehicleDetails from '$lib/components/auction/VehicleDetails.svelte';
  import MachineryDetails from '$lib/components/auction/MachineryDetails.svelte';
  import FactoryDetails from '$lib/components/auction/FactoryDetails.svelte';
  import HeavyVehicleDetails from '$lib/components/auction/HeavyVehicleDetails.svelte';
  // Remove Button import as we're replacing with <a> tags
  import Spinner from '$lib/components/ui/Spinner.svelte';
  import Alert from '$lib/components/ui/Alert.svelte';
  import Tabs from '$lib/components/ui/Tabs.svelte';
  import Gallery from '$lib/components/ui/Gallery.svelte';
  import ShareButton from '$lib/components/ui/ShareButton.svelte';
  import { formatDate, formatCurrency } from '$lib/utils/formatters';
  import AuctionImageGallery from '$lib/components/auction/AuctionImageGallery.svelte';
  import RecentAuctions from '$lib/components/auction/RecentAuctions.svelte';
  
  // Get auction ID from URL
  $: auctionId = $page.params.id;
  
  // Reactive state
  $: auction = $auctionStore.currentAuction;
  $: loading = $auctionStore.loading.details;
  $: error = $auctionStore.error;
  $: currentUser = $user;
  
  // Helper function to safely format currency
  function safeCurrency(value, currency = 'USD') {
    if (value === undefined || value === null) return formatCurrency(0, currency);
    
    // Ensure the value is a proper number
    const numValue = typeof value === 'string' ? parseFloat(value) : value;
    if (isNaN(numValue)) return formatCurrency(0, currency);
    
    return formatCurrency(numValue, currency);
  }
  
  // Helper function to get the main image URL with fallback
  function getMainImageUrl(auction) {
    if (!auction) return null;
    
    // Try all possible image field names with fallbacks
    if (auction.image_url && auction.image_url !== 'null' && auction.image_url !== 'undefined') {
      return auction.image_url;
    }
    
    // Check if there's an images array
    if (Array.isArray(auction.images) && auction.images.length > 0 && auction.images[0]) {
      return auction.images[0];
    }
    
    // Try main_image
    if (auction.main_image && auction.main_image !== 'null' && auction.main_image !== 'undefined') {
      return auction.main_image;
    }
    
    // Try image_1 through image_5
    for (let i = 1; i <= 5; i++) {
      const imageField = `image_${i}`;
      if (auction[imageField] && auction[imageField] !== 'null' && auction[imageField] !== 'undefined') {
        return auction[imageField];
      }
    }
    
    return null;
  }
  
  // Helper function to collect all images from auction
  function getAllAuctionImages(auction) {
    if (!auction) return [];
    
    const imagesList = [];
    
    // Add from images array if it exists
    if (Array.isArray(auction.images)) {
      imagesList.push(...auction.images.filter(img => img && img !== 'null' && img !== 'undefined'));
    }
    
    // Add main_image if not already in array
    if (auction.main_image && auction.main_image !== 'null' && auction.main_image !== 'undefined') {
      if (!imagesList.includes(auction.main_image)) {
        imagesList.push(auction.main_image);
      }
    }
    
    // Add image_url if not already in array and it exists
    if (auction.image_url && auction.image_url !== 'null' && auction.image_url !== 'undefined') {
      if (!imagesList.includes(auction.image_url)) {
        imagesList.push(auction.image_url);
      }
    }
    
    // Add image_1 through image_5 if they exist and aren't already in array
    for (let i = 1; i <= 5; i++) {
      const imageField = `image_${i}`;
      if (auction[imageField] && auction[imageField] !== 'null' && auction[imageField] !== 'undefined') {
        if (!imagesList.includes(auction[imageField])) {
          imagesList.push(auction[imageField]);
        }
      }
    }
    
    // Remove duplicates
    return [...new Set(imagesList)];
  }
  
  // Create reactive values for image handling
  $: mainImageUrl = getMainImageUrl(auction);
  $: allAuctionImages = getAllAuctionImages(auction);
  
  // Timer state
  let remaining = {
    days: 0,
    hours: 0,
    minutes: 0,
    seconds: 0,
    total_seconds: 0
  };
  
  // WebSocket connection for real-time updates
  let connection = null;
  let liveUpdates = [];
  let connectionStatus = 'disconnected';
  
  // Tabs
  const tabs = [
    { id: 'details', label: 'Details' },
    { id: 'images', label: 'Gallery' },
    { id: 'documents', label: 'Documents' },
    { id: 'bids', label: 'Bid History' }
  ];
  let activeTab = 'details';
  
  // Helper methods
  function getSpecificDetailsComponent(auction) {
    if (!auction?.specific_data) return null;
    
    // Return the appropriate component based on auction_type
    switch (auction.specific_data.auction_type || auction.auction_type) {
      case 'real_estate':
        return PropertyDetails;
      case 'vehicle':
        return VehicleDetails;
      case 'machinery':
        return MachineryDetails;
      case 'factory':
        return FactoryDetails;
      case 'heavy_vehicle':
        return HeavyVehicleDetails;
      default:
        return null;
    }
  }
  
  // Calculate remaining time
  function calculateRemainingTime() {
    if (!auction) return;
    
    const now = new Date();
    const end = new Date(auction.end_time);
    
    // If auction has ended
    if (now >= end) {
      remaining = {
        days: 0,
        hours: 0,
        minutes: 0,
        seconds: 0,
        total_seconds: 0
      };
      return;
    }
    
    const totalSeconds = Math.floor((end - now) / 1000);
    const days = Math.floor(totalSeconds / 86400);
    const hours = Math.floor((totalSeconds % 86400) / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = totalSeconds % 60;
    
    remaining = {
      days,
      hours,
      minutes,
      seconds,
      total_seconds: totalSeconds
    };
  }
  
  // Check if the current user is the seller
  $: isUserTheSeller = $isAuthenticated && currentUser && auction && 
      String(auction.seller) === String(currentUser.id);
  
  // Load auction data
  onMount(async () => {
    if (auctionId) {
      try {
        // Load auction details
        await auctionStore.loadAuctionDetails(auctionId);
        
        // Start timer updates
        calculateRemainingTime();
        const timerInterval = setInterval(calculateRemainingTime, 1000);
        
        // Initialize WebSocket connection for real-time updates
        connection = createAuctionConnection(auctionId);
        
        // Subscribe to auction updates
        const unsubscribeUpdates = connection.updates.subscribe(updates => {
          liveUpdates = updates;
          
          // Process updates
          if (updates.length > 0) {
            // Handle specific updates like price changes
            const latestUpdate = updates[0];
            if (latestUpdate.action === 'price_update') {
              notificationStore.info(`The price has been updated to ${safeCurrency(latestUpdate.data.price)}`);
              // Refresh auction details to get the latest state
              auctionStore.loadAuctionDetails(auctionId);
            } else if (latestUpdate.action === 'timer_extended') {
              notificationStore.info(`Auction time has been extended by ${latestUpdate.data.minutes} minutes`);
              // Refresh auction details to get the latest state
              auctionStore.loadAuctionDetails(auctionId);
            }
          }
        });
        
        // Subscribe to connection status
        const unsubscribeStatus = connection.status.subscribe(status => {
          connectionStatus = status;
        });
        
        // Clean up on unmount
        return () => {
          clearInterval(timerInterval);
          if (unsubscribeUpdates) unsubscribeUpdates();
          if (unsubscribeStatus) unsubscribeStatus();
        };
      } catch (err) {
        console.error('Error loading auction details:', err);
      }
    }
  });
  
  // Clean up WebSocket connection
  onDestroy(() => {
    if (connection) {
      connection.close();
    }
  });
</script>

<svelte:head>
  <title>{auction ? auction.title : 'Auction Details'} | GUDIC</title>
  <meta name="description" content={auction?.description || 'View auction details and place bids'} />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
  <!-- Loading state -->
  {#if loading}
    <div class="flex justify-center items-center py-12">
      <Spinner size="lg" />
    </div>
  <!-- Error state -->
  {:else if error}
    <div class="bg-red-50 p-4 rounded-md text-red-600 mb-8">
      <p class="text-center">{error}</p>
      <div class="flex justify-center mt-4">
        <a 
          href="/auctions/{auctionId}"
          class="inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-blue hover:bg-primary-blue-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-blue"
          on:click|preventDefault={() => {
            auctionStore.clearError();
            auctionStore.loadAuctionDetails(auctionId);
          }}
        >
          Try Again
        </a>
      </div>
    </div>
  <!-- Content state -->
  {:else if auction}
    <div class="mb-6 flex flex-col sm:flex-row items-start sm:items-center justify-between space-y-4 sm:space-y-0">
      <div>
        <div class="flex flex-wrap items-center gap-2 mb-2">
          <a 
            href={`/categories/${auction.category?.slug || ''}`} 
            class="text-xs font-medium px-2 py-1 bg-primary-blue/10 text-secondary-blue rounded-full hover:bg-primary-blue/20 transition-colors"
          >
            {auction.category?.name || 'Uncategorized'}
          </a>
          
          <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium {auction.status === 'ACTIVE' ? 'bg-green-100 text-green-800' : auction.status === 'ENDED' ? 'bg-gray-100 text-gray-800' : 'bg-yellow-100 text-yellow-800'}">
            {auction.status || 'Unknown'}
          </span>
          
          {#if connectionStatus === 'connected'}
            <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
              <span class="h-2 w-2 mr-1 bg-green-400 rounded-full"></span>
              Live Updates
            </span>
          {/if}
        </div>
        
        <h1 class="text-3xl font-bold text-text-dark">{auction.title || 'Auction Details'}</h1>
        
        <div class="mt-1 text-sm text-text-medium">
          <span>Listed by {auction.seller_details?.first_name || 'Unknown'} {auction.seller_details?.last_name || ''}</span>
          <span class="mx-2">•</span>
          <span>Posted on {formatDate(auction.created_at)}</span>
        </div>
      </div>
      
      <div class="flex space-x-2">
        <ShareButton 
          title={auction.title || 'Auction'} 
          text={`Check out this auction: ${auction.title || 'Auction'}`} 
          url={`/auctions/${auction.id}`} 
        />
        
        {#if $isAuthenticated && ($primaryRole?.code === 'seller' || $primaryRole?.code === 'admin') && isUserTheSeller}
          <a 
            href={`/auctions/${auction.id}/edit`} 
            class="inline-flex items-center justify-center px-4 py-2 text-sm font-medium rounded-md border border-primary-blue text-primary-blue bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-blue"
          >
            Edit Auction
          </a>
        {/if}
      </div>
    </div>
    
    <!-- Main content area -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Left column: Auction details -->
      <div class="lg:col-span-2 space-y-6">
        <!-- Main image and gallery -->
        <div class="bg-white rounded-lg border border-primary-blue/20 overflow-hidden">
          <div class="aspect-w-16 aspect-h-9 bg-neutral-100">
            {#if mainImageUrl}
              <img 
                src={mainImageUrl} 
                alt={auction?.title || "Auction item"}
                class="object-cover h-full w-full"
                on:error={(e) => e.target.src = 'https://via.placeholder.com/800x450?text=No+Image'}
              />
            {:else}
              <div class="flex items-center justify-center h-full bg-gray-100 text-gray-400">
                <span>No image available</span>
              </div>
            {/if}
          </div>
        </div>
        
        <!-- Tabs for details, gallery, documents, etc. -->
        <div class="bg-white rounded-lg border border-primary-blue/20 overflow-hidden">
          <Tabs {tabs} bind:activeTab>
            <!-- Details Tab -->
            {#if activeTab === 'details'}
              <div class="p-6">
                <h2 class="text-xl font-semibold text-text-dark mb-4">Description</h2>
                <div class="prose max-w-none text-text-medium">
                  <p>{auction.description || 'No description available.'}</p>
                </div>
                
                <!-- Specific details based on auction type -->
                {#if auction.specific_data}
                  <div class="mt-8">
                    <h2 class="text-xl font-semibold text-text-dark mb-4">Specifications</h2>
                    <svelte:component 
                      this={getSpecificDetailsComponent(auction)} 
                      data={auction.specific_data} 
                    />
                  </div>
                {/if}
              </div>
            <!-- Images Tab -->
            {:else if activeTab === 'images'}
              <div class="p-6">
                <h2 class="text-xl font-semibold text-text-dark mb-4">Gallery</h2>
                
                {#if allAuctionImages.length > 0}
                  <AuctionImageGallery
                    mainImage={mainImageUrl || ''}
                    images={allAuctionImages}
                  />
                {:else}
                  <div class="text-center py-8 text-text-medium">
                    <p>No images available for this auction.</p>
                  </div>
                {/if}
              </div>
            <!-- Documents Tab -->
            {:else if activeTab === 'documents'}
              <div class="p-6">
                <h2 class="text-xl font-semibold text-text-dark mb-4">Documents</h2>
                
                {#if $isAuthenticated}
                  {#if auction.documents && auction.documents.length > 0}
                    <ul class="divide-y divide-primary-blue/10">
                      {#each auction.documents as doc}
                        <li class="py-4 flex items-center justify-between">
                          <div class="flex items-center">
                            <div class="h-10 w-10 rounded-full bg-primary-blue/10 flex items-center justify-center text-secondary-blue">
                              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                <path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clip-rule="evenodd" />
                              </svg>
                            </div>
                            <div class="ml-3">
                              <p class="text-sm font-medium text-text-dark">{doc.title || 'Document'}</p>
                              <p class="text-xs text-text-medium">{formatDate(doc.created_at)}</p>
                            </div>
                          </div>
                          <a 
                            href={doc.file || '#'}
                            class="inline-flex items-center px-2.5 py-1.5 border border-primary-blue text-xs font-medium rounded text-primary-blue bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-blue"
                            target="_blank" 
                            rel="noopener noreferrer"
                          >
                            View
                          </a>
                        </li>
                      {/each}
                    </ul>
                  {:else}
                    <div class="text-center py-8 text-text-medium">
                      <p>No documents available for this auction.</p>
                    </div>
                  {/if}
                {:else}
                  <Alert variant="info">
                    Please <a href="/login" class="font-medium underline">sign in</a> to view auction documents.
                  </Alert>
                {/if}
              </div>
            <!-- Bid History Tab -->
            {:else if activeTab === 'bids'}
              <div class="p-6">
                <h2 class="text-xl font-semibold text-text-dark mb-4">Bid History</h2>
                
                {#if auction.recent_bids && auction.recent_bids.length > 0}
                  <ul class="divide-y divide-primary-blue/10">
                    {#each auction.recent_bids as bid}
                      <li class="py-3">
                        <div class="flex items-center justify-between">
                          <div class="flex items-center">
                            <div class="h-8 w-8 rounded-full bg-primary-blue/10 flex items-center justify-center text-secondary-blue">
                              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                                <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd" />
                              </svg>
                            </div>
                            <div class="ml-3">
                              <p class="text-sm font-medium text-text-dark">
                                {bid.bidder_details?.first_name || 'Anonymous'} {bid.bidder_details?.last_name?.charAt(0) || ''}
                              </p>
                              <p class="text-xs text-text-medium">{formatDate(bid.created_at)}</p>
                            </div>
                          </div>
                          <div class="text-sm font-semibold text-secondary-blue">
                            {safeCurrency(bid.amount, auction.currency)}
                          </div>
                        </div>
                      </li>
                    {/each}
                  </ul>
                {:else}
                  <div class="text-center py-8 text-text-medium">
                    <p>No bids have been placed yet.</p>
                  </div>
                {/if}
              </div>
            {/if}
          </Tabs>
        </div>
      </div>
      
      <!-- Right column: Bidding and current price -->
      <div class="space-y-6">
        <!-- Current price and timer -->
        <div class="bg-white rounded-lg border border-primary-blue/20 overflow-hidden">
          <div class="p-5">
            <div class="flex justify-between items-center mb-4">
              <div class="text-sm font-medium text-text-medium">Current Price</div>
              <div class="text-2xl font-bold text-secondary-blue">
                {safeCurrency(auction.current_price, auction.currency)}
              </div>
            </div>
            
            <!-- Auction timer component -->
            <AuctionTimer auction={auction} accent={true} />
            
            <!-- Starting Price -->
            <div class="mt-4 pt-4 border-t border-primary-blue/10">
              <div class="flex justify-between text-sm">
                <span class="text-text-medium">Starting price</span>
                <span class="font-medium">{safeCurrency(auction.starting_price || 0, auction.currency)}</span>
              </div>
              
              <!-- Reserve Price (if available) -->
              {#if auction.reserve_price > 0}
                <div class="flex justify-between text-sm mt-1">
                  <span class="text-text-medium">Reserve price</span>
                  <span class="font-medium">{safeCurrency(auction.reserve_price, auction.currency)}</span>
                </div>
              {/if}
              
              <!-- Minimum Bid Increment -->
              <div class="flex justify-between text-sm mt-1">
                <span class="text-text-medium">Minimum bid increment</span>
                <span class="font-medium">{safeCurrency(auction.minimum_bid_increment, auction.currency)}</span>
              </div>
              
              <!-- Bid Count -->
              <div class="flex justify-between text-sm mt-1">
                <span class="text-text-medium">Total bids</span>
                <span class="font-medium">{auction.total_bids || 0}</span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Bidding component with seller check fixed -->
        <BiddingComponent 
          auction={auction} 
          isSellerView={isUserTheSeller}
        />
        
        <!-- Seller info -->
        <div class="bg-white rounded-lg border border-primary-blue/20 overflow-hidden">
          <div class="px-5 py-4 border-b border-primary-blue/10 bg-gradient-to-r from-primary-blue/5 to-primary-peach/5">
            <h3 class="text-lg font-medium text-text-dark">Seller Information</h3>
          </div>
          
          <div class="p-5">
            <div class="flex items-center">
              <div class="h-12 w-12 rounded-full bg-primary-blue/10 overflow-hidden">
                <img 
                  src={auction.seller_details?.avatar || `https://ui-avatars.com/api/?name=${auction.seller_details?.first_name || 'User'}+${auction.seller_details?.last_name || ''}&background=6366F1&color=fff`}
                  alt="Seller"
                  class="h-full w-full object-cover"
                />
              </div>
              <div class="ml-4">
                <p class="text-sm font-medium text-text-dark">
                  {auction.seller_details?.first_name || 'User'} {auction.seller_details?.last_name || ''}
                </p>
                {#if auction.seller_details?.company_name}
                  <p class="text-xs text-text-medium">{auction.seller_details.company_name}</p>
                {/if}
              </div>
            </div>
            
            <div class="mt-4 pt-4 border-t border-primary-blue/10">
              <a 
                href={`/messages/${auction.seller}`}
                class="flex justify-center items-center w-full px-4 py-2 border border-primary-blue rounded-md text-sm font-medium text-primary-blue bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-blue"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z" clip-rule="evenodd" />
                </svg>
                Contact Seller
              </a>
            </div>
          </div>
        </div>
        
        <!-- Latest Updates (from WebSocket) -->
        {#if liveUpdates.length > 0}
          <div class="bg-white rounded-lg border border-primary-blue/20 overflow-hidden">
            <div class="px-5 py-4 border-b border-primary-blue/10 bg-gradient-to-r from-primary-blue/5 to-primary-peach/5">
              <div class="flex items-center justify-between">
                <h3 class="text-lg font-medium text-text-dark">Latest Updates</h3>
                {#if connectionStatus === 'connected'}
                  <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                    <span class="h-2 w-2 mr-1 bg-green-400 rounded-full animate-pulse"></span>
                    Live
                  </span>
                {/if}
              </div>
            </div>
            
            <ul class="divide-y divide-primary-blue/10">
              {#each liveUpdates.slice(0, 5) as update}
                <li class="p-4 text-sm">
                  <div class="flex items-start">
                    <div class="h-8 w-8 rounded-full bg-primary-blue/10 flex items-center justify-center text-secondary-blue flex-shrink-0 mt-0.5">
                      {#if update.action === 'price_update'}
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                      {:else if update.action === 'status_change'}
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                        </svg>
                      {:else if update.action === 'timer_extended'}
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                      {:else}
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                      {/if}
                    </div>
                    
                    <div class="ml-3 flex-1">
                      <div class="flex justify-between">
                        <p class="font-medium text-text-dark">
                          {#if update.action === 'price_update'}
                            Price updated to {safeCurrency(update.data?.price || 0, auction.currency)}
                          {:else if update.action === 'status_change'}
                            Auction status changed to {update.data?.status || 'Unknown'}
                          {:else if update.action === 'timer_extended'}
                            Auction extended by {update.data?.minutes || 0} minutes
                          {:else}
                            {update.action ? update.action.replace('_', ' ') : 'Update'}
                          {/if}
                        </p>
                        <span class="text-xs text-text-medium">{formatDate(update.timestamp)}</span>
                      </div>
                    </div>
                  </div>
                </li>
              {/each}
            </ul>
          </div>
        {/if}
      </div>
    </div>
    
    <!-- Related auctions section -->
    <div class="mt-12">
      <RecentAuctions 
        title="Related Auctions" 
        viewAllLink="/auctions"
        limit={4}
        params={{
          category: auction.category?.id,
          status: 'ACTIVE',
          exclude_id: auction.id
        }}
        emptyStateMessage="No related auctions found"
      />
    </div>
  {:else}
    <!-- Empty state -->
    <div class="text-center py-12">
      <p class="text-text-medium">Auction not found or has been removed.</p>
      <a 
        href="/auctions" 
        class="inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-blue hover:bg-primary-blue-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-blue mt-4"
      >
        Browse Auctions
      </a>
    </div>
  {/if}
</div>

<style>
  /* Fix for aspect ratio */
  .aspect-w-16 {
    position: relative;
    padding-bottom: 56.25%;
  }
  
  .aspect-w-16 > * {
    position: absolute;
    height: 100%;
    width: 100%;
    top: 0;
    right: 0;
    bottom: 0;
    left: 0;
  }
  
  /* Animation for live indicator */
  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }
  
  .animate-pulse {
    animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
  }
</style>