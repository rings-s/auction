<!-- src/routes/auctions/[id]/+page.svelte -->
<script>
    import { onMount, onDestroy } from 'svelte';
    import { t, isRTL } from '$lib/i18n';
    import {formatCurrency, formatDate } from '$lib/utils/formatters';
    import { page } from '$app/stores';
    import { goto } from '$app/navigation';
    import { auctionActions, loading, currentAuction, currentBids, errors } from '$lib/stores/auction';
    import { authStore } from '$lib/stores/auth';
    
    // Components
    import AuctionTimer from '$lib/components/auctions/AuctionTimer.svelte';
    import BidForm from '$lib/components/auctions/BidForm.svelte';
    import BidHistory from '$lib/components/auctions/BidHistory.svelte';
    import Breadcrumb from '$lib/components/ui/Breadcrumb.svelte';
    import Button from '$lib/components/ui/Button.svelte';
    import Alert from '$lib/components/ui/Alert.svelte';
    import Spinner from '$lib/components/ui/Spinner.svelte';
    import Tabs from '$lib/components/ui/Tabs.svelte';
    import TabItem from '$lib/components/ui/TabItem.svelte';
    import Badge from '$lib/components/ui/Badge.svelte';
    
    // Get auction ID from page params
    const auctionId = $page.params.id;
    
    // State
    let activeTabIndex = 0;
    let imageIndex = 0;
    let bidHistory = [];
    let bidHistoryPage = 1;
    let bidHistoryPageCount = 1;
    let auction = null;
    let isOwner = false;
    let isAdmin = false;
    let canBid = false;
    
    // Define tabs
    const tabs = [
      { id: 'details', label: $t('auctions.details') },
      { id: 'bid-history', label: $t('auctions.bid_history') },
      { id: 'property', label: $t('properties.property_details') },
      { id: 'documents', label: $t('auctions.documents') }
    ];
    
    // Status colors for badges
    const statusColors = {
      active: 'success',
      pending: 'warning',
      extended: 'info',
      closed: 'neutral',
      sold: 'primary',
      cancelled: 'error'
    };
    
    // Load auction details and handle update
    async function loadAuctionDetails(refresh = false) {
      try {
        await auctionActions.loadAuctionDetail(auctionId, true, true, refresh);
      } catch (error) {
        console.error('Error loading auction details:', error);
      }
    }
    
    // Load bid history for a specific page
    async function loadBidHistory(page = 1) {
      bidHistoryPage = page;
      await auctionActions.loadAuctionBids(auctionId, { 
        page: page, 
        page_size: 10
      });
    }
    
    // Handle bid submission
    function handleBidPlaced(event) {
      // Refresh auction details and bid history
      loadAuctionDetails(true);
      loadBidHistory(1);
    }
    
    // Handle tab change
    function handleTabChange(index) {
      activeTabIndex = index;
      
      // Load bid history when switching to that tab
      if (tabs[index].id === 'bid-history') {
        loadBidHistory(1);
      }
    }
    
    // Navigate to image
    function setImage(index) {
      imageIndex = index;
    }
    
    // Next image
    function nextImage() {
      const images = getAuctionImages();
      imageIndex = (imageIndex + 1) % images.length;
    }
    
    // Previous image
    function prevImage() {
      const images = getAuctionImages();
      imageIndex = (imageIndex - 1 + images.length) % images.length;
    }
    
    // Get images from auction
    function getAuctionImages() {
      if (!$currentAuction) return [];
      
      // Collect all available images
      const allImages = [
        $currentAuction.featured_image_url,
        ...$currentAuction.images || [],
        ...$currentAuction.related_property?.images || []
      ].filter(Boolean);
      
      // Add fallback if no images
      if (allImages.length === 0) {
        allImages.push('/images/placeholder-property.jpg');
      }
      
      return allImages;
    }
    
    // Check permissions based on role and ownership
    function checkPermissions() {
      if (!$currentAuction || !$authStore?.user) return;
      
      // Check if user is owner
      if ($currentAuction.created_by?.id === $authStore?.user?.id ||
          $currentAuction.auctioneer?.id === $authStore?.user?.id ||
          $currentAuction.related_property?.owner?.id === $authStore?.user?.id) {
        isOwner = true;
      } else {
        isOwner = false;
      }
      
      // Check if user is admin
      isAdmin = $authStore?.user?.role === 'admin';
      
      // Check if user can bid
      canBid = !isOwner && 
               $authStore?.isAuthenticated && 
               ($currentAuction.status === 'active');
    }
    
    // Handle auction edit
    function editAuction() {
      goto(`/auctions/${auctionId}/edit`);
    }
    
    // Handle property view
    function viewProperty() {
      if ($currentAuction?.related_property?.id) {
        goto(`/properties/${$currentAuction.related_property.id}`);
      }
    }
    
    // Initialize component
    onMount(() => {
      loadAuctionDetails();
      loadBidHistory(1);
    });
    
    // Update from store
    $: {
      auction = $currentAuction;
      bidHistory = $currentBids;
      checkPermissions();
    }
  </script>
  
  <svelte:head>
    <title>
      {$currentAuction?.title || $t('auctions.auction_details')} | {$t('general.app_name')}
    </title>
    <meta name="description" content={$currentAuction?.description || $t('auctions.auction_details')} />
  </svelte:head>
  
  <div class="auction-detail container mx-auto px-4 py-8">
    <!-- Breadcrumb -->
    <div class="mb-6">
      <Breadcrumb
        items={[
          { label: $t('navigation.home'), href: '/' },
          { label: $t('auctions.title'), href: '/auctions' },
          { label: $currentAuction?.title || $t('auctions.auction_details'), href: `/auctions/${auctionId}`, active: true }
        ]}
      />
    </div>
    
    {#if $loading.currentAuctionLoading}
      <!-- Loading state -->
      <div class="flex flex-col items-center justify-center py-16">
        <Spinner size="lg" />
        <p class="mt-4 text-neutral-600 dark:text-neutral-400">{$t('general.loading')}</p>
      </div>
    {:else if $errors.detailError}
      <!-- Error state -->
      <Alert 
        type="error" 
        title={$t('general.error')}
        message={$errors.detailError} 
      />
    {:else if $currentAuction}
      <!-- Auction Detail Layout -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Main Content (2/3) -->
        <div class="lg:col-span-2">
          <!-- Image Gallery -->
          <div class="relative mb-6 rounded-xl overflow-hidden bg-neutral-100 dark:bg-neutral-800">
            <div style="aspect-ratio: 16/9;" class="relative">
              {#if getAuctionImages().length > 0}
                <img 
                  src={getAuctionImages()[imageIndex]} 
                  alt={$currentAuction.title}
                  class="w-full h-full object-cover"
                />
              {/if}
              
              <!-- Auction status badge -->
              <div class="absolute top-4 {isRTL() ? 'left-4' : 'right-4'} z-10">
                <Badge 
                  text={$currentAuction.status_display || $currentAuction.status}
                  color={statusColors[$currentAuction.status] || 'neutral'}
                  size="lg"
                />
              </div>
              
              <!-- Navigation buttons -->
              {#if getAuctionImages().length > 1}
                <button 
                  class="absolute top-1/2 left-4 transform -translate-y-1/2 bg-black bg-opacity-50 hover:bg-opacity-70 text-white rounded-full p-2 transition-opacity"
                  on:click={prevImage}
                  aria-label="Previous image"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                  </svg>
                </button>
                <button 
                  class="absolute top-1/2 right-4 transform -translate-y-1/2 bg-black bg-opacity-50 hover:bg-opacity-70 text-white rounded-full p-2 transition-opacity"
                  on:click={nextImage}
                  aria-label="Next image"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                  </svg>
                </button>
              {/if}
            </div>
            
            <!-- Thumbnails -->
            {#if getAuctionImages().length > 1}
              <div class="flex p-2 overflow-x-auto space-x-2">
                {#each getAuctionImages() as image, i}
                  <button 
                    class={`rounded overflow-hidden flex-shrink-0 w-16 h-16 border-2 ${imageIndex === i ? 'border-primary-600 dark:border-primary-400' : 'border-transparent'}`}
                    on:click={() => setImage(i)}
                  >
                    <img src={image} alt="" class="w-full h-full object-cover" />
                  </button>
                {/each}
              </div>
            {/if}
          </div>
          
          <!-- Title and Key Details -->
          <div class="mb-6">
            <h1 class="text-2xl md:text-3xl font-bold text-neutral-900 dark:text-neutral-100 mb-4">
              {$currentAuction.title}
            </h1>
            
            <div class="flex flex-wrap items-center gap-3 mb-4">
              <!-- Property Type Badge -->
              <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-neutral-100 text-neutral-800 dark:bg-neutral-700 dark:text-neutral-200">
                {$currentAuction.related_property?.property_type_display || 
                 $currentAuction.related_property?.property_type || 
                 $t('properties.property')}
              </span>
              
              <!-- Auction Type Badge -->
              <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800 dark:bg-primary-900/20 dark:text-primary-300">
                {$currentAuction.auction_type_display || $currentAuction.auction_type}
              </span>
              
              <!-- Featured Badge (if applicable) -->
              {#if $currentAuction.is_featured}
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-accent-100 text-accent-800 dark:bg-accent-900/20 dark:text-accent-300">
                  {$t('general.featured')}
                </span>
              {/if}
            </div>
            
            <!-- Price & Timer -->
            <div class="flex flex-col md:flex-row md:items-center md:justify-between mt-4 gap-4 py-4 border-t border-b border-neutral-200 dark:border-neutral-700">
              <div>
                <div class="text-sm text-neutral-600 dark:text-neutral-400">
                  {$currentAuction.bid_count > 0 ? $t('auctions.current_bid') : $t('auctions.starting_price')}
                </div>
                <div class="text-2xl font-bold text-neutral-900 dark:text-neutral-100">
                  {formatCurrency($currentAuction.current_bid || $currentAuction.starting_price)}
                </div>
                {#if $currentAuction.bid_count > 0}
                  <div class="text-sm text-neutral-600 dark:text-neutral-400">
                    {$currentAuction.bid_count} {$currentAuction.bid_count === 1 ? $t('auctions.bid') : $t('auctions.bids')}
                  </div>
                {/if}
              </div>
              
              <div class="bg-neutral-50 dark:bg-neutral-800 rounded-lg px-4 py-3 border border-neutral-200 dark:border-neutral-700">
                <AuctionTimer
                  endTime={$currentAuction.end_date}
                  status={$currentAuction.status}
                  size="large"
                  showLabels={true}
                />
              </div>
            </div>
          </div>
          
          <!-- Tabs Navigation -->
          <Tabs activeIndex={activeTabIndex} on:change={e => handleTabChange(e.detail)}>
            {#each tabs as tab, i}
              <TabItem title={tab.label} />
            {/each}
          </Tabs>
          
          <!-- Tab Content -->
          <div class="bg-white dark:bg-neutral-800 rounded-b-xl border border-t-0 border-neutral-200 dark:border-neutral-700 p-6">
            <!-- Details Tab -->
            {#if activeTabIndex === 0}
              <div class="space-y-6">
                <div>
                  <h3 class="text-lg font-semibold text-neutral-800 dark:text-neutral-200 mb-3">
                    {$t('auctions.description')}
                  </h3>
                  <div class="prose dark:prose-invert max-w-none">
                    <p>{$currentAuction.description}</p>
                  </div>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h3 class="text-lg font-semibold text-neutral-800 dark:text-neutral-200 mb-3">
                      {$t('auctions.auction_details')}
                    </h3>
                    <dl class="space-y-2">
                      <div class="flex justify-between">
                        <dt class="text-neutral-600 dark:text-neutral-400">{$t('auctions.auction_type')}</dt>
                        <dd class="font-medium text-neutral-900 dark:text-neutral-100">{$currentAuction.auction_type_display}</dd>
                      </div>
                      <div class="flex justify-between">
                        <dt class="text-neutral-600 dark:text-neutral-400">{$t('auctions.start_date')}</dt>
                        <dd class="font-medium text-neutral-900 dark:text-neutral-100">{formatDate($currentAuction.start_date)}</dd>
                      </div>
                      <div class="flex justify-between">
                        <dt class="text-neutral-600 dark:text-neutral-400">{$t('auctions.end_date')}</dt>
                        <dd class="font-medium text-neutral-900 dark:text-neutral-100">{formatDate($currentAuction.end_date)}</dd>
                      </div>
                      <div class="flex justify-between">
                        <dt class="text-neutral-600 dark:text-neutral-400">{$t('auctions.starting_price')}</dt>
                        <dd class="font-medium text-neutral-900 dark:text-neutral-100">{formatCurrency($currentAuction.starting_price)}</dd>
                      </div>
                      <div class="flex justify-between">
                        <dt class="text-neutral-600 dark:text-neutral-400">{$t('auctions.current_bid')}</dt>
                        <dd class="font-medium text-neutral-900 dark:text-neutral-100">{formatCurrency($currentAuction.current_bid)}</dd>
                      </div>
                      <div class="flex justify-between">
                        <dt class="text-neutral-600 dark:text-neutral-400">{$t('auctions.min_increment')}</dt>
                        <dd class="font-medium text-neutral-900 dark:text-neutral-100">{formatCurrency($currentAuction.min_bid_increment)}</dd>
                      </div>
                    </dl>
                  </div>
                  
                  <div>
                    <h3 class="text-lg font-semibold text-neutral-800 dark:text-neutral-200 mb-3">
                      {$t('auctions.additional_information')}
                    </h3>
                    <dl class="space-y-2">
                      <div class="flex justify-between">
                        <dt class="text-neutral-600 dark:text-neutral-400">{$t('auctions.bid_count')}</dt>
                        <dd class="font-medium text-neutral-900 dark:text-neutral-100">{$currentAuction.bid_count}</dd>
                      </div>
                      <div class="flex justify-between">
                        <dt class="text-neutral-600 dark:text-neutral-400">{$t('auctions.unique_bidders')}</dt>
                        <dd class="font-medium text-neutral-900 dark:text-neutral-100">{$currentAuction.unique_bidders_count || 0}</dd>
                      </div>
                      <div class="flex justify-between">
                        <dt class="text-neutral-600 dark:text-neutral-400">{$t('auctions.auto_extend')}</dt>
                        <dd class="font-medium text-neutral-900 dark:text-neutral-100">
                          {$currentAuction.auto_extend ? $t('general.yes') : $t('general.no')}
                        </dd>
                      </div>
                      {#if $currentAuction.auto_extend}
                        <div class="flex justify-between">
                          <dt class="text-neutral-600 dark:text-neutral-400">{$t('auctions.extension_minutes')}</dt>
                          <dd class="font-medium text-neutral-900 dark:text-neutral-100">{$currentAuction.extension_minutes}</dd>
                        </div>
                      {/if}
                      <div class="flex justify-between">
                        <dt class="text-neutral-600 dark:text-neutral-400">{$t('auctions.deposit_required')}</dt>
                        <dd class="font-medium text-neutral-900 dark:text-neutral-100">
                          {$currentAuction.deposit_required ? $t('general.yes') : $t('general.no')}
                        </dd>
                      </div>
                      {#if $currentAuction.deposit_required}
                        <div class="flex justify-between">
                          <dt class="text-neutral-600 dark:text-neutral-400">{$t('auctions.deposit_amount')}</dt>
                          <dd class="font-medium text-neutral-900 dark:text-neutral-100">
                            {formatCurrency($currentAuction.deposit_amount)}
                          </dd>
                        </div>
                      {/if}
                    </dl>
                  </div>
                </div>
                
                {#if $currentAuction.terms_conditions}
                  <div>
                    <h3 class="text-lg font-semibold text-neutral-800 dark:text-neutral-200 mb-3">
                      {$t('auctions.terms_and_conditions')}
                    </h3>
                    <div class="bg-neutral-50 dark:bg-neutral-900/30 rounded-lg p-4 border border-neutral-200 dark:border-neutral-700">
                      <div class="prose dark:prose-invert max-w-none">
                        <p>{$currentAuction.terms_conditions}</p>
                      </div>
                    </div>
                  </div>
                {/if}
              </div>
            {/if}
            
            <!-- Bid History Tab -->
            {#if activeTabIndex === 1}
              <BidHistory
                auctionId={auctionId}
                bids={bidHistory}
                isLoading={$loading.bidsLoading}
                pageCount={bidHistoryPageCount}
                currentPage={bidHistoryPage}
                onPageChange={loadBidHistory}
                onRefresh={() => loadBidHistory(bidHistoryPage)}
                winningBid={$currentAuction.highest_bid}
              />
            {/if}
            
            <!-- Property Details Tab -->
            {#if activeTabIndex === 2 && $currentAuction.related_property}
              <div class="space-y-6">
                <div>
                  <h3 class="text-lg font-semibold text-neutral-800 dark:text-neutral-200 mb-3">
                    {$t('properties.property_details')}
                  </h3>
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <dl class="space-y-2">
                      <div class="flex justify-between">
                        <dt class="text-neutral-600 dark:text-neutral-400">{$t('properties.property_type')}</dt>
                        <dd class="font-medium text-neutral-900 dark:text-neutral-100">
                          {$currentAuction.related_property.property_type_display || $currentAuction.related_property.property_type}
                        </dd>
                      </div>
                      <div class="flex justify-between">
                        <dt class="text-neutral-600 dark:text-neutral-400">{$t('properties.property_area')}</dt>
                        <dd class="font-medium text-neutral-900 dark:text-neutral-100">
                          {$currentAuction.related_property.area} m²
                        </dd>
                      </div>
                      <div class="flex justify-between">
                        <dt class="text-neutral-600 dark:text-neutral-400">{$t('properties.property_city')}</dt>
                        <dd class="font-medium text-neutral-900 dark:text-neutral-100">
                          {$currentAuction.related_property.city}
                        </dd>
                      </div>
                      <div class="flex justify-between">
                        <dt class="text-neutral-600 dark:text-neutral-400">{$t('properties.property_district')}</dt>
                        <dd class="font-medium text-neutral-900 dark:text-neutral-100">
                          {$currentAuction.related_property.district || '-'}
                        </dd>
                      </div>
                      {#if $currentAuction.related_property.bedrooms !== null && $currentAuction.related_property.bedrooms !== undefined}
                        <div class="flex justify-between">
                          <dt class="text-neutral-600 dark:text-neutral-400">{$t('properties.bedrooms')}</dt>
                          <dd class="font-medium text-neutral-900 dark:text-neutral-100">
                            {$currentAuction.related_property.bedrooms}
                          </dd>
                        </div>
                      {/if}
                      {#if $currentAuction.related_property.bathrooms !== null && $currentAuction.related_property.bathrooms !== undefined}
                        <div class="flex justify-between">
                          <dt class="text-neutral-600 dark:text-neutral-400">{$t('properties.bathrooms')}</dt>
                          <dd class="font-medium text-neutral-900 dark:text-neutral-100">
                            {$currentAuction.related_property.bathrooms}
                          </dd>
                        </div>
                      {/if}
                    </dl>
                    
                    <dl class="space-y-2">
                      <div class="flex justify-between">
                        <dt class="text-neutral-600 dark:text-neutral-400">{$t('properties.estimated_value')}</dt>
                        <dd class="font-medium text-neutral-900 dark:text-neutral-100">
                          {formatCurrency($currentAuction.related_property.estimated_value)}
                        </dd>
                      </div>
                      <div class="flex justify-between">
                        <dt class="text-neutral-600 dark:text-neutral-400">{$t('properties.property_status')}</dt>
                        <dd class="font-medium text-neutral-900 dark:text-neutral-100">
                          {$currentAuction.related_property.status_display || $currentAuction.related_property.status}
                        </dd>
                      </div>
                      {#if $currentAuction.related_property.year_built}
                        <div class="flex justify-between">
                          <dt class="text-neutral-600 dark:text-neutral-400">{$t('properties.build_year')}</dt>
                          <dd class="font-medium text-neutral-900 dark:text-neutral-100">
                            {$currentAuction.related_property.year_built}
                          </dd>
                        </div>
                      {/if}
                      {#if $currentAuction.related_property.property_condition}
                        <div class="flex justify-between">
                          <dt class="text-neutral-600 dark:text-neutral-400">{$t('properties.property_condition')}</dt>
                          <dd class="font-medium text-neutral-900 dark:text-neutral-100">
                            {$currentAuction.related_property.property_condition}
                          </dd>
                        </div>
                      {/if}
                    </dl>
                  </div>
                </div>
                
                {#if $currentAuction.related_property.description}
                  <div>
                    <h3 class="text-lg font-semibold text-neutral-800 dark:text-neutral-200 mb-3">
                      {$t('properties.property_description')}
                    </h3>
                    <div class="prose dark:prose-invert max-w-none">
                      <p>{$currentAuction.related_property.description}</p>
                    </div>
                  </div>
                {/if}
                
                <div class="flex justify-center">
                  <Button 
                    variant="outline" 
                    on:click={viewProperty}
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 {isRTL() ? 'ml-1.5' : 'mr-1.5'}" viewBox="0 0 20 20" fill="currentColor">
                      <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                      <path fill-rule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clip-rule="evenodd" />
                    </svg>
                    {$t('properties.view_property_details')}
                  </Button>
                </div>
              </div>
            {/if}
            
            <!-- Documents Tab -->
            {#if activeTabIndex === 3}
              <div class="space-y-6">
                {#if $currentAuction.documents && $currentAuction.documents.length > 0}
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {#each $currentAuction.documents as doc}
                      <a href={doc.main_file_url} target="_blank" rel="noopener noreferrer" 
                        class="flex items-center p-4 bg-neutral-50 dark:bg-neutral-900/30 rounded-lg border border-neutral-200 dark:border-neutral-700 hover:border-primary-300 dark:hover:border-primary-700 transition-colors">
                        <div class="flex-shrink-0 mr-3">
                          <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-neutral-500 dark:text-neutral-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                          </svg>
                        </div>
                        <div class="flex-grow">
                          <h4 class="text-sm font-medium text-neutral-900 dark:text-neutral-100">{doc.document_type_display || doc.title || doc.document_number}</h4>
                          <p class="text-xs text-neutral-500 dark:text-neutral-400">{formatDate(doc.created_at)}</p>
                        </div>
                        <div class="flex-shrink-0">
                          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-neutral-400 dark:text-neutral-500" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clip-rule="evenodd" />
                          </svg>
                        </div>
                      </a>
                    {/each}
                  </div>
                {:else}
                  <div class="text-center p-6 bg-neutral-50 dark:bg-neutral-900/30 rounded-lg border border-neutral-200 dark:border-neutral-700">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 mx-auto mb-4 text-neutral-400 dark:text-neutral-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <p class="text-neutral-600 dark:text-neutral-400">
                      {$t('auctions.no_documents_available')}
                    </p>
                  </div>
                {/if}
              </div>
            {/if}
          </div>
        </div>
        
        <!-- Sidebar (1/3) -->
        <div class="space-y-6">
          <!-- Bid placement card -->
          {#if canBid}
            <BidForm
              auction={$currentAuction}
              disabled={$currentAuction.status !== 'active'}
              on:bid-placed={handleBidPlaced}
            />
          {:else if $currentAuction.status === 'active'}
            <div class="bg-white dark:bg-neutral-800 rounded-xl border border-neutral-200 dark:border-neutral-700 shadow-sm p-4">
              <h3 class="text-lg font-semibold text-neutral-800 dark:text-neutral-200 mb-4">
                {$t('auctions.place_bid')}
              </h3>
              
              {#if !$authStore?.isAuthenticated}
                <Alert
                  type="info"
                  title={$t('auth.login_required')}
                  message={$t('auctions.login_to_bid')}
                  class="mb-4"
                />
                <Button
                  variant="primary"
                  fullWidth={true}
                  href="/auth/login?redirect=/auctions/{auctionId}"
                >
                  {$t('auth.login')}
                </Button>
              {:else if isOwner}
                <Alert
                  type="info"
                  title={$t('auctions.bid_restricted')}
                  message={$t('auctions.owner_cannot_bid')}
                />
              {/if}
            </div>
          {:else}
            <!-- Auction status card -->
            <div class="bg-white dark:bg-neutral-800 rounded-xl border border-neutral-200 dark:border-neutral-700 shadow-sm p-4">
              <h3 class="text-lg font-semibold text-neutral-800 dark:text-neutral-200 mb-4">
                {$t('auctions.auction_status')}
              </h3>
              
              <div class="mb-4">
                <Badge 
                  text={$currentAuction.status_display || $currentAuction.status}
                  color={statusColors[$currentAuction.status] || 'neutral'}
                  size="lg"
                />
              </div>
              
              {#if $currentAuction.status === 'pending'}
                <p class="text-neutral-600 dark:text-neutral-400">
                  {$t('auctions.pending_message')}
                </p>
              {:else if $currentAuction.status === 'closed' || $currentAuction.status === 'sold'}
                <p class="text-neutral-600 dark:text-neutral-400">
                  {$t('auctions.closed_message')}
                </p>
                
                {#if $currentAuction.winning_bidder}
                  <div class="mt-4 p-3 bg-success-50 dark:bg-success-900/20 rounded-lg border border-success-200 dark:border-success-800/30">
                    <h4 class="font-medium text-success-800 dark:text-success-300">
                      {$t('auctions.winning_bidder')}
                    </h4>
                    <p class="text-success-700 dark:text-success-400">
                      {$currentAuction.winning_bidder.full_name || $currentAuction.winning_bidder.name}
                    </p>
                    <p class="text-success-700 dark:text-success-400">
                      {$t('auctions.winning_bid')}: {formatCurrency($currentAuction.winning_bid)}
                    </p>
                  </div>
                {/if}
              {:else if $currentAuction.status === 'cancelled'}
                <p class="text-neutral-600 dark:text-neutral-400">
                  {$t('auctions.cancelled_message')}
                </p>
              {/if}
            </div>
          {/if}
          
          <!-- Auctioneer Info -->
          <div class="bg-white dark:bg-neutral-800 rounded-xl border border-neutral-200 dark:border-neutral-700 shadow-sm p-4">
            <h3 class="text-lg font-semibold text-neutral-800 dark:text-neutral-200 mb-4">
              {$t('auctions.auctioneer')}
            </h3>
            
            <div class="flex items-center mb-4">
              <div class="flex-shrink-0 h-12 w-12 bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 rounded-full flex items-center justify-center mr-3">
                <span class="text-xl font-bold">
                  {$currentAuction.auctioneer?.full_name?.charAt(0) || 'A'}
                </span>
              </div>
              <div>
                <h4 class="font-medium text-neutral-900 dark:text-neutral-100">
                  {$currentAuction.auctioneer?.full_name || $currentAuction.auctioneer?.name || $t('auctions.anonymous_auctioneer')}
                </h4>
                <p class="text-sm text-neutral-500 dark:text-neutral-400">
                  {$t('auctions.auctioneer')}
                </p>
              </div>
            </div>
            
            {#if isOwner || isAdmin}
              <div class="mt-4">
                <Button 
                  variant="outline" 
                  fullWidth={true}
                  on:click={editAuction}
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 {isRTL() ? 'ml-1.5' : 'mr-1.5'}" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                  </svg>
                  {$t('auctions.edit_auction')}
                </Button>
              </div>
            {/if}
          </div>
          
          <!-- Location -->
          {#if $currentAuction.related_property?.city}
            <div class="bg-white dark:bg-neutral-800 rounded-xl border border-neutral-200 dark:border-neutral-700 shadow-sm p-4">
              <h3 class="text-lg font-semibold text-neutral-800 dark:text-neutral-200 mb-4">
                {$t('properties.property_location')}
              </h3>
              
              <div class="flex items-center gap-2 mb-2">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-neutral-500 dark:text-neutral-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clip-rule="evenodd" />
                </svg>
                <span class="text-neutral-800 dark:text-neutral-200">
                  {[
                    $currentAuction.related_property.district,
                    $currentAuction.related_property.city,
                    $currentAuction.related_property.country
                  ].filter(Boolean).join(', ')}
                </span>
              </div>
              
              <!-- Map placeholder -->
              <div class="aspect-video bg-neutral-100 dark:bg-neutral-700 rounded-lg overflow-hidden mt-3">
                <img 
                  src={`https://api.mapbox.com/styles/v1/mapbox/streets-v11/static/pin-l+3B82F6(${$currentAuction.related_property.longitude || 45},${$currentAuction.related_property.latitude || 24})/45,24,12,0/600x300@2x?access_token=example`} 
                  alt="Property location map"
                  class="w-full h-full object-cover"
                />
              </div>
            </div>
          {/if}
          
          <!-- Share -->
          <div class="bg-white dark:bg-neutral-800 rounded-xl border border-neutral-200 dark:border-neutral-700 shadow-sm p-4">
            <h3 class="text-lg font-semibold text-neutral-800 dark:text-neutral-200 mb-4">
              {$t('general.share')}
            </h3>
            
            <div class="flex justify-between">
              <button class="p-2 bg-neutral-50 dark:bg-neutral-700 rounded-full hover:bg-neutral-100 dark:hover:bg-neutral-600 transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-neutral-700 dark:text-neutral-300" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14m-.5 15.5v-5.3a3.26 3.26 0 0 0-3.26-3.26c-.85 0-1.84.52-2.32 1.3v-1.11h-2.79v8.37h2.79v-4.93c0-.77.62-1.4 1.39-1.4a1.4 1.4 0 0 1 1.4 1.4v4.93h2.79M6.88 8.56a1.68 1.68 0 0 0 1.68-1.68c0-.93-.75-1.69-1.68-1.69a1.69 1.69 0 0 0-1.69 1.69c0 .93.76 1.68 1.69 1.68m1.39 9.94v-8.37H5.5v8.37h2.77Z"></path>
                </svg>
              </button>
              <button class="p-2 bg-neutral-50 dark:bg-neutral-700 rounded-full hover:bg-neutral-100 dark:hover:bg-neutral-600 transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-neutral-700 dark:text-neutral-300" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M22.46 6c-.77.35-1.6.58-2.46.69.88-.53 1.56-1.37 1.88-2.38-.83.5-1.75.85-2.72 1.05C18.37 4.5 17.26 4 16 4c-2.35 0-4.27 1.92-4.27 4.29 0 .34.04.67.11.98C8.28 9.09 5.11 7.38 3 4.79c-.37.63-.58 1.37-.58 2.15 0 1.49.75 2.81 1.91 3.56-.71 0-1.37-.2-1.95-.5v.03c0 2.08 1.48 3.82 3.44 4.21a4.22 4.22 0 0 1-1.93.07 4.28 4.28 0 0 0 4 2.98 8.521 8.521 0 0 1-5.33 1.84c-.34 0-.68-.02-1.02-.06C3.44 20.29 5.7 21 8.12 21 16 21 20.33 14.46 20.33 8.79c0-.19 0-.37-.01-.56.84-.6 1.56-1.36 2.14-2.23Z"></path>
                </svg>
              </button>
              <button class="p-2 bg-neutral-50 dark:bg-neutral-700 rounded-full hover:bg-neutral-100 dark:hover:bg-neutral-600 transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-neutral-700 dark:text-neutral-300" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2.04c-5.5 0-10 4.49-10 10.02 0 5 3.66 9.15 8.44 9.9v-7H7.9v-2.9h2.54V9.85c0-2.51 1.49-3.89 3.78-3.89 1.09 0 2.23.19 2.23.19v2.47h-1.26c-1.24 0-1.63.77-1.63 1.56v1.88h2.78l-.45 2.9h-2.33v7a10 10 0 0 0 8.44-9.9c0-5.53-4.5-10.02-10-10.02Z"></path>
                </svg>
              </button>
              <button class="p-2 bg-neutral-50 dark:bg-neutral-700 rounded-full hover:bg-neutral-100 dark:hover:bg-neutral-600 transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-neutral-700 dark:text-neutral-300" fill="currentColor" viewBox="0 0 24 24">
                  <path fill-rule="evenodd" d="M5 3a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0
                  002-2V5a2 2 0 00-2-2H5zm0 2h10v7h-2l-1 2H8l-1-2H5V5z" clip-rule="evenodd"></path>
                </svg>
              </button>
              <button class="p-2 bg-neutral-50 dark:bg-neutral-700 rounded-full hover:bg-neutral-100 dark:hover:bg-neutral-600 transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-neutral-700 dark:text-neutral-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    {/if}
  </div>