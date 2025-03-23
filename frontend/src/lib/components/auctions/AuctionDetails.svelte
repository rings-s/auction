<!-- src/lib/components/auction/AuctionDetails.svelte -->
<script>
    import { onMount } from 'svelte';
    import { t, formatCurrency, formatDate } from '$lib/i18n';
    import { api } from '$lib/services/api';
    import AuctionTimer from './AuctionTimer.svelte';
    import BidForm from './BidForm.svelte';
    import BidHistory from './BidHistory.svelte';
    
    // Props - Auction ID to load
    export let auctionId;
    
    // State
    let auction = null;
    let property = null;
    let loading = true;
    let error = null;
    let activeTab = 'details'; // details, property, history
    
    // Derived values
    $: isActive = auction?.status === 'active';
    $: isEnded = ['closed', 'sold', 'cancelled'].includes(auction?.status);
    $: isPending = auction?.status === 'pending';
    $: canBid = isActive && !loading;
    
    // Status badge color
    function getStatusColor(status) {
      const colors = {
        'active': 'bg-status-success',
        'pending': 'bg-status-warning',
        'extended': 'bg-status-info',
        'closed': 'bg-cosmos-text-dim',
        'sold': 'bg-status-error',
        'cancelled': 'bg-status-error'
      };
      
      return colors[status] || 'bg-cosmos-text-dim';
    }
    
    // Load auction data
    async function loadAuction() {
      loading = true;
      error = null;
      
      try {
        // Fetch auction details with property details included
        const response = await api.get(`auctions/${auctionId}/`, {
          include_property: true,
          include_bids: true,
          include_documents: true
        });
        
        if (response && response.data) {
          auction = response.data.auction;
          property = response.data.auction.related_property;
        } else {
          throw new Error('Invalid response format');
        }
      } catch (err) {
        console.error('Error fetching auction details:', err);
        error = err.message || $t('system_messages.error_occurred');
      } finally {
        loading = false;
      }
    }
    
    // Handle successful bid placement
    function handleBidPlaced(event) {
      // Refresh auction data after bid is placed
      loadAuction();
    }
    
    onMount(() => {
      loadAuction();
    });
  </script>
  
  <div class="min-h-screen bg-cosmos-bg">
    {#if loading}
      <div class="flex justify-center p-20">
        <div class="animate-pulse-slow flex flex-col items-center">
          <div class="h-16 w-16 rounded-full bg-primary bg-opacity-20"></div>
          <p class="mt-4 text-cosmos-text-muted">{$t('general.loading')}</p>
        </div>
      </div>
    {:else if error}
      <div class="rounded-xl bg-status-error bg-opacity-10 p-6 text-center">
        <p class="text-status-error">{error}</p>
        <button 
          class="mt-4 rounded-lg bg-primary px-4 py-2 text-white hover:bg-primary-dark"
          on:click={loadAuction}
        >
          {$t('general.retry')}
        </button>
      </div>
    {:else if auction}
      <div class="container mx-auto px-4 py-8">
        <!-- Auction Header -->
        <div class="mb-8 flex flex-col lg:flex-row lg:items-center lg:justify-between">
          <div>
            <h1 class="text-3xl font-bold text-cosmos-text">{auction.title}</h1>
            <p class="mt-2 text-cosmos-text-muted">{property.title}</p>
            
            <div class="mt-4 flex flex-wrap gap-3">
              <span class={`rounded-full px-3 py-1 text-sm text-white ${getStatusColor(auction.status)}`}>
                {auction.status_display || $t(`auctions.status.${auction.status}`)}
              </span>
              
              <span class="rounded-full bg-property-{property.property_type} bg-opacity-80 px-3 py-1 text-sm text-white">
                {property.property_type_display || $t(`properties.types.${property.property_type}`)}
              </span>
              
              {#if auction.is_featured}
                <span class="rounded-full bg-[#FFD700] px-3 py-1 text-sm text-cosmos-bg-dark">
                  {$t('general.featured')}
                </span>
              {/if}
            </div>
          </div>
          
          <div class="mt-6 lg:mt-0">
            {#if isActive}
              <div class="rounded-xl bg-primary bg-opacity-5 p-4">
                <AuctionTimer 
                  endTime={auction.end_date}
                  status={auction.status}
                  on:end={loadAuction}
                />
              </div>
            {:else if isPending}
              <div class="rounded-xl bg-status-warning bg-opacity-5 p-4">
                <AuctionTimer 
                  endTime={auction.start_date}
                  status={auction.status}
                  on:end={loadAuction}
                />
              </div>
            {:else}
              <div class="rounded-xl bg-cosmos-bg-light p-4 text-center">
                <p class="text-cosmos-text-muted">
                  {$t('auctions.ended')}
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
                class="w-full object-cover"
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
                      class="h-24 w-full cursor-pointer object-cover hover:opacity-90"
                    />
                  </div>
                {/each}
              </div>
            {/if}
            
            <!-- Tab Navigation -->
            <div class="mb-6 border-b border-cosmos-bg-light">
              <div class="flex">
                <button 
                  class="px-4 py-3 text-sm font-medium {activeTab === 'details' ? 'border-b-2 border-primary text-primary' : 'text-cosmos-text-muted hover:text-cosmos-text'}"
                  on:click={() => activeTab = 'details'}
                >
                  {$t('auctions.auction_details')}
                </button>
                
                <button 
                  class="px-4 py-3 text-sm font-medium {activeTab === 'property' ? 'border-b-2 border-primary text-primary' : 'text-cosmos-text-muted hover:text-cosmos-text'}"
                  on:click={() => activeTab = 'property'}
                >
                  {$t('properties.property_details')}
                </button>
                
                <button 
                  class="px-4 py-3 text-sm font-medium {activeTab === 'history' ? 'border-b-2 border-primary text-primary' : 'text-cosmos-text-muted hover:text-cosmos-text'}"
                  on:click={() => activeTab = 'history'}
                >
                  {$t('auctions.bid_history')}
                </button>
              </div>
            </div>
            
            <!-- Tab Content -->
            <div class="mb-8 rounded-xl bg-cosmos-bg-light bg-opacity-20 p-6 backdrop-blur-sm">
              {#if activeTab === 'details'}
                <!-- Auction Details -->
                <div class="space-y-6">
                  <div>
                    <h3 class="text-xl font-bold text-cosmos-text">{auction.title}</h3>
                    <p class="mt-3 text-cosmos-text">{auction.description}</p>
                  </div>
                  
                  <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                    <div>
                      <p class="text-sm text-cosmos-text-muted">{$t('auctions.auction_type')}</p>
                      <p class="font-medium text-cosmos-text">{auction.auction_type_display}</p>
                    </div>
                    
                    <div>
                      <p class="text-sm text-cosmos-text-muted">{$t('auctions.start_date')}</p>
                      <p class="font-medium text-cosmos-text">{formatDate(auction.start_date)}</p>
                    </div>
                    
                    <div>
                      <p class="text-sm text-cosmos-text-muted">{$t('auctions.end_date')}</p>
                      <p class="font-medium text-cosmos-text">{formatDate(auction.end_date)}</p>
                    </div>
                    
                    <div>
                      <p class="text-sm text-cosmos-text-muted">{$t('auctions.starting_price')}</p>
                      <p class="font-medium text-cosmos-text">{formatCurrency(auction.starting_price)}</p>
                    </div>
                    
                    <div>
                      <p class="text-sm text-cosmos-text-muted">{$t('auctions.current_bid')}</p>
                      <p class="font-bold text-primary">{formatCurrency(auction.current_bid)}</p>
                    </div>
                    
                    <div>
                      <p class="text-sm text-cosmos-text-muted">{$t('auctions.min_increment')}</p>
                      <p class="font-medium text-cosmos-text">{formatCurrency(auction.min_bid_increment)}</p>
                    </div>
                  </div>
                  
                  {#if auction.auction_terms}
                    <div>
                      <h4 class="mb-2 text-lg font-medium text-cosmos-text">{$t('auctions.auction_terms')}</h4>
                      <div class="rounded-lg bg-cosmos-bg-light p-4 text-cosmos-text">
                        <p>{auction.auction_terms}</p>
                      </div>
                    </div>
                  {/if}
                </div>
              {:else if activeTab === 'property'}
                <!-- Property Details -->
                <div class="space-y-6">
                  <div>
                    <h3 class="text-xl font-bold text-cosmos-text">{property.title}</h3>
                    <p class="mt-3 text-cosmos-text">{property.description}</p>
                  </div>
                  
                  <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                    <div>
                      <p class="text-sm text-cosmos-text-muted">{$t('properties.property_type')}</p>
                      <p class="font-medium text-cosmos-text">{property.property_type_display}</p>
                    </div>
                    
                    <div>
                      <p class="text-sm text-cosmos-text-muted">{$t('properties.property_area')}</p>
                      <p class="font-medium text-cosmos-text">{property.area} m²</p>
                    </div>
                    
                    <div>
                      <p class="text-sm text-cosmos-text-muted">{$t('properties.property_location')}</p>
                      <p class="font-medium text-cosmos-text">{property.city}, {property.district}</p>
                    </div>
                    
                    {#if property.bedrooms > 0}
                      <div>
                        <p class="text-sm text-cosmos-text-muted">{$t('properties.bedrooms')}</p>
                        <p class="font-medium text-cosmos-text">{property.bedrooms}</p>
                      </div>
                    {/if}
                    
                    {#if property.bathrooms > 0}
                      <div>
                        <p class="text-sm text-cosmos-text-muted">{$t('properties.bathrooms')}</p>
                        <p class="font-medium text-cosmos-text">{property.bathrooms}</p>
                      </div>
                    {/if}
                    
                    {#if property.year_built}
                      <div>
                        <p class="text-sm text-cosmos-text-muted">{$t('properties.build_year')}</p>
                        <p class="font-medium text-cosmos-text">{property.year_built}</p>
                      </div>
                    {/if}
                  </div>
                  
                  {#if property.features && property.features.length > 0}
                    <div>
                      <h4 class="mb-2 text-lg font-medium text-cosmos-text">{$t('properties.property_features')}</h4>
                      <div class="flex flex-wrap gap-2">
                        {#each property.features as feature}
                          <span class="rounded-full bg-cosmos-bg px-3 py-1 text-sm text-cosmos-text">
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
                  bids={auction.recent_bids || []}
                  on:refresh={loadAuction}
                />
              {/if}
            </div>
          </div>
          
          <!-- Right Column - Bid Form and Summary -->
          <div>
            <!-- Bid Form Card -->
            <div class="mb-6 rounded-xl bg-cosmos-bg-light bg-opacity-30 p-6 backdrop-blur-sm">
              <h3 class="mb-4 text-xl font-bold text-cosmos-text">{$t('auctions.place_bid')}</h3>
              
              <div class="mb-4 space-y-4">
                <div>
                  <p class="text-sm text-cosmos-text-muted">{$t('auctions.current_bid')}</p>
                  <p class="text-2xl font-bold text-primary">{formatCurrency(auction.current_bid)}</p>
                </div>
                
                <div class="flex items-center justify-between">
                  <div>
                    <p class="text-sm text-cosmos-text-muted">{$t('auctions.bid_count')}</p>
                    <p class="text-lg font-medium text-cosmos-text">{auction.bid_count}</p>
                  </div>
                  
                  <div>
                    <p class="text-sm text-cosmos-text-muted">{$t('auctions.min_increment')}</p>
                    <p class="text-lg font-medium text-cosmos-text">{formatCurrency(auction.min_bid_increment)}</p>
                  </div>
                </div>
              </div>
              
              <div class="mt-6">
                <!-- Bid Form or Status Message based on auction status -->
                {#if canBid}
                  <BidForm 
                    auction={auction}
                    on:bid-placed={handleBidPlaced}
                  />
                {:else if isPending}
                  <div class="rounded-lg bg-status-warning bg-opacity-10 p-4 text-center">
                    <p class="text-status-warning">
                      {$t('auctions.starts_in')}
                    </p>
                  </div>
                {:else if isEnded}
                  <div class="rounded-lg bg-cosmos-text-dim bg-opacity-10 p-4 text-center">
                    <p class="text-cosmos-text-dim">
                      {$t('auctions.ended')}
                    </p>
                  </div>
                {/if}
              </div>
            </div>
            
            <!-- Property Summary Card -->
            <div class="rounded-xl bg-cosmos-bg-light bg-opacity-30 p-6 backdrop-blur-sm">
              <h3 class="mb-4 text-lg font-bold text-cosmos-text">{$t('properties.property_details')}</h3>
              
              <div class="space-y-4">
                <div class="flex items-center">
                  <div class="mr-3 h-10 w-10 flex-shrink-0 rounded-full bg-property-{property.property_type} bg-opacity-20 p-2">
                    <!-- Icon based on property type -->
                    <svg class="h-full w-full text-property-{property.property_type}" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z" />
                    </svg>
                  </div>
                  
                  <div class="flex-grow">
                    <p class="text-sm text-cosmos-text-muted">{$t('properties.property_type')}</p>
                    <p class="font-medium text-cosmos-text">{property.property_type_display}</p>
                  </div>
                </div>
                
                <div class="flex items-center">
                  <div class="mr-3 h-10 w-10 flex-shrink-0 rounded-full bg-primary bg-opacity-20 p-2">
                    <!-- Location icon -->
                    <svg class="h-full w-full text-primary" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clip-rule="evenodd" />
                    </svg>
                  </div>
                  
                  <div class="flex-grow">
                    <p class="text-sm text-cosmos-text-muted">{$t('properties.property_location')}</p>
                    <p class="font-medium text-cosmos-text">{property.city}, {property.district}</p>
                  </div>
                </div>
                
                <div class="flex items-center">
                  <div class="mr-3 h-10 w-10 flex-shrink-0 rounded-full bg-primary bg-opacity-20 p-2">
                    <!-- Area icon -->
                    <svg class="h-full w-full text-primary" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M4 4a2 2 0 012-2h8a2 2 0 012 2v12a1 1 0 01-1 1h-2a1 1 0 01-1-1v-2a1 1 0 00-1-1H9a1 1 0 00-1 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V4zm3 1h2v2H7V5zm2 4H7v2h2V9zm2-4h2v2h-2V5zm2 4h-2v2h2V9z" clip-rule="evenodd" />
                    </svg>
                  </div>
                  
                  <div class="flex-grow">
                    <p class="text-sm text-cosmos-text-muted">{$t('properties.property_area')}</p>
                    <p class="font-medium text-cosmos-text">{property.area} m²</p>
                  </div>
                </div>
              </div>
              
              <div class="mt-6">
                <a 
                  href={`/properties/${property.id}`}
                  class="block w-full rounded-lg bg-primary bg-opacity-10 py-3 text-center text-sm font-medium text-primary transition hover:bg-primary hover:text-white"
                >
                  {$t('properties.view_property')}
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    {:else}
      <div class="flex h-32 items-center justify-center">
        <p class="text-cosmos-text-muted">{$t('general.not_found')}</p>
      </div>
    {/if}
  </div>