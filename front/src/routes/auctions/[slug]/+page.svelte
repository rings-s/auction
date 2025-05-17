<!-- src/routes/auctions/[slug]/+page.svelte -->
<script>
    import { onMount, onDestroy } from 'svelte';
    import { page } from '$app/stores';
    import { t } from '$lib/i18n/i18n';
    import { user } from '$lib/stores/user';
    import { fetchAuctionBySlug, placeBid } from '$lib/api/auction';
    import { fetchPropertyById } from '$lib/api/property';
    import TagList from '$lib/components/TagSelector.svelte';
    import PropertyMap from '$lib/components/PropertyMap.svelte';
  
    let auction = null;
    let property = null;
    let loading = true;
    let error = null;
    let bidAmount = '';
    let placingBid = false;
    let bidError = '';
    let bidSuccess = '';
    let timeRemaining = { days: 0, hours: 0, minutes: 0, seconds: 0 };
    let timer;
  
    $: slug = $page.params.slug;
    $: isLiveAuction = auction?.status === 'live';
    $: canBid = isLiveAuction && $user && auction?.end_date > new Date().toISOString();
    $: minimumBidAmount = calculateMinimumBid();
  
    function calculateMinimumBid() {
      if (!auction) return 0;
      
      // If there's a current bid, the minimum is current bid + increment
      if (auction.current_bid) {
        return parseFloat(auction.current_bid) + parseFloat(auction.minimum_increment);
      }
      
      // Otherwise, use the starting bid
      return parseFloat(auction.starting_bid);
    }
  
    function updateTimeRemaining() {
      if (!auction) return;
      
      const endDate = new Date(auction.end_date);
      const now = new Date();
      const diff = endDate - now;
      
      if (diff <= 0) {
        timeRemaining = { days: 0, hours: 0, minutes: 0, seconds: 0 };
        clearInterval(timer);
        return;
      }
      
      const days = Math.floor(diff / (1000 * 60 * 60 * 24));
      const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
      const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
      const seconds = Math.floor((diff % (1000 * 60)) / 1000);
      
      timeRemaining = { days, hours, minutes, seconds };
    }
  
    async function loadAuctionData() {
      loading = true;
      error = null;
      
      try {
        // Fetch auction details
        const auctionData = await fetchAuctionBySlug(slug);
        auction = auctionData;
        
        // Initialize bid amount to minimum bid
        bidAmount = calculateMinimumBid().toString();
        
        // Start timer update
        updateTimeRemaining();
        timer = setInterval(updateTimeRemaining, 1000);
        
        // If auction has a related property, fetch its details
        if (auction.related_property) {
          property = auction.related_property;
        }
        
      } catch (err) {
        console.error('Error loading auction details:', err);
        error = err.message;
      } finally {
        loading = false;
      }
    }
  
    async function handlePlaceBid() {
      try {
        bidError = '';
        bidSuccess = '';
        placingBid = true;
        
        // Validate bid amount
        const amount = parseFloat(bidAmount);
        if (isNaN(amount) || amount < minimumBidAmount) {
          bidError = $t('auction.bidTooLow', { amount: minimumBidAmount });
          return;
        }
        
        // Submit bid
        await placeBid(auction.id, amount);
        
        // Show success message
        bidSuccess = $t('auction.bidPlaced');
        
        // Reset bid amount
        bidAmount = '';
        
        // Reload auction data to get updated bids
        await loadAuctionData();
        
      } catch (err) {
        console.error('Error placing bid:', err);
        bidError = err.message || $t('error.bidFailed');
      } finally {
        placingBid = false;
      }
    }
  
    onMount(() => {
      loadAuctionData();
    });
  
    onDestroy(() => {
      if (timer) clearInterval(timer);
    });
  
    function formatDateTime(dateString) {
      try {
        const date = new Date(dateString);
        return new Intl.DateTimeFormat('default', {
          year: 'numeric',
          month: 'long',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        }).format(date);
      } catch (e) {
        return dateString;
      }
    }
  </script>
  
  <svelte:head>
    <title>{auction?.title || 'Auction'} | Real Estate Platform</title>
  </svelte:head>
  
  <div class="bg-gray-50 dark:bg-gray-900 py-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      
      {#if loading}
        <div class="flex justify-center py-24">
          <div class="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-primary-500"></div>
        </div>
      {:else if error}
        <div class="bg-red-50 dark:bg-red-900/20 p-6 rounded-lg text-red-800 dark:text-red-200 max-w-3xl mx-auto my-12">
          <h2 class="text-xl font-semibold mb-2">{$t('error.title')}</h2>
          <p>{error}</p>
          <a href="/auctions" class="mt-4 inline-block text-primary-600 dark:text-primary-400 hover:underline">
            &larr; {$t('auctions.backToAuctions')}
          </a>
        </div>
      {:else if auction}
        <!-- Breadcrumbs -->
        <nav class="mb-6 text-sm">
          <ol class="flex flex-wrap items-center space-x-2">
            <li>
              <a href="/" class="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300">{$t('nav.home')}</a>
            </li>
            <li class="flex items-center">
              <span class="text-gray-400 mx-1">/</span>
              <a href="/auctions" class="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300">{$t('nav.auctions')}</a>
            </li>
            <li class="flex items-center">
              <span class="text-gray-400 mx-1">/</span>
              <span class="text-gray-700 dark:text-gray-300 truncate">{auction.title}</span>
            </li>
          </ol>
        </nav>
        
        <!-- Auction header -->
        <div class="mb-8">
          <div class="flex flex-wrap items-start justify-between">
            <div>
              <div class="flex items-center space-x-2">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-md text-sm font-medium 
                  {auction.status === 'live' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' : 
                  auction.status === 'scheduled' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200' : 
                  auction.status === 'ended' ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' : 
                  'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'}"
                >
                  {auction.status === 'live' ? $t('auction.statusLive') : 
                  auction.status === 'scheduled' ? $t('auction.statusScheduled') : 
                  auction.status === 'ended' ? $t('auction.statusEnded') : 
                  auction.status === 'completed' ? $t('auction.statusCompleted') : 
                  $t('auction.statusDraft')}
                </span>
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-md text-sm font-medium bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200">
                  {auction.auction_type === 'sealed' ? $t('auction.typeSealed') :
                  auction.auction_type === 'reserve' ? $t('auction.typeReserve') :
                  $t('auction.typeNoReserve')}
                </span>
              </div>
              <h1 class="text-3xl font-bold text-gray-900 dark:text-white mt-2 mb-2">{auction.title}</h1>
            </div>
          </div>
        </div>
        
        <!-- Auction content -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <!-- Main content (left and center) -->
          <div class="lg:col-span-2 space-y-8">
            <!-- Gallery -->
            <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
              <div class="bg-gray-200 dark:bg-gray-700 aspect-w-16 aspect-h-9">
                {#if property && property.media && property.media.length > 0}
                  <img 
                    src={property.media[0]?.file || '/images/property-placeholder.jpg'} 
                    alt={property.title}
                    class="w-full h-full object-cover"
                  />
                {:else}
                  <img 
                    src="/images/auction-placeholder.jpg" 
                    alt={auction.title}
                    class="w-full h-full object-cover"
                  />
                {/if}
              </div>
            </div>
            
            <!-- Description -->
            <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
              <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">{$t('auction.description')}</h2>
              <div class="prose dark:prose-invert max-w-none text-gray-600 dark:text-gray-300">
                <p>{auction.description}</p>
              </div>
            </div>
            
            <!-- Auction Details -->
            <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
              <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">{$t('auction.auctionDetails')}</h2>
              
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
                <div>
                  <p class="text-sm text-gray-500 dark:text-gray-400">{$t('auction.startDate')}</p>
                  <p class="font-medium text-gray-900 dark:text-white">{formatDateTime(auction.start_date)}</p>
                </div>
                <div>
                  <p class="text-sm text-gray-500 dark:text-gray-400">{$t('auction.endDate')}</p>
                  <p class="font-medium text-gray-900 dark:text-white">{formatDateTime(auction.end_date)}</p>
                </div>
                <div>
                  <p class="text-sm text-gray-500 dark:text-gray-400">{$t('auction.registrationDeadline')}</p>
                  <p class="font-medium text-gray-900 dark:text-white">
                    {auction.registration_deadline ? formatDateTime(auction.registration_deadline) : '-'}
                  </p>
                </div>
                <div>
                  <p class="text-sm text-gray-500 dark:text-gray-400">{$t('auction.startingBid')}</p>
                  <p class="font-medium text-gray-900 dark:text-white">${auction.starting_bid.toLocaleString()}</p>
                </div>
                <div>
                  <p class="text-sm text-gray-500 dark:text-gray-400">{$t('auction.currentBid')}</p>
                  <p class="font-medium text-gray-900 dark:text-white">
                    ${auction.current_bid ? auction.current_bid.toLocaleString() : auction.starting_bid.toLocaleString()}
                  </p>
                </div>
                <div>
                  <p class="text-sm text-gray-500 dark:text-gray-400">{$t('auction.minimumIncrement')}</p>
                  <p class="font-medium text-gray-900 dark:text-white">${auction.minimum_increment.toLocaleString()}</p>
                </div>
              </div>
              
              <!-- Terms and Conditions -->
              {#if auction.terms_conditions}
                <div>
                  <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">{$t('auction.termsConditions')}</h3>
                  <div class="p-4 bg-gray-50 dark:bg-gray-700 rounded-md text-sm text-gray-700 dark:text-gray-300">
                    <p>{auction.terms_conditions}</p>
                  </div>
                </div>
              {/if}
            </div>
            
            <!-- Property Details -->
            {#if property}
              <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
                <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">{$t('auction.auctionProperty')}</h2>
                
                <div class="flex items-center mb-4">
                  <h3 class="text-lg font-medium text-gray-900 dark:text-white">{property.title}</h3>
                  <a 
                    href={`/properties/${property.slug}`} 
                    class="ml-auto text-sm text-primary-600 dark:text-primary-400 hover:underline"
                  >
                    {$t('property.viewDetails')}
                  </a>
                </div>
                
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
                  <div>
                    <p class="text-sm text-gray-500 dark:text-gray-400">{$t('property.address')}</p>
                    <p class="font-medium text-gray-900 dark:text-white">{property.address}</p>
                  </div>
                  <div>
                    <p class="text-sm text-gray-500 dark:text-gray-400">{$t('property.city')}, {$t('property.state')}</p>
                    <p class="font-medium text-gray-900 dark:text-white">{property.city}, {property.state}</p>
                  </div>
                  <div>
                    <p class="text-sm text-gray-500 dark:text-gray-400">{$t('property.propertyType')}</p>
                    <p class="font-medium text-gray-900 dark:text-white">{property.property_type_display}</p>
                  </div>
                  <div>
                    <p class="text-sm text-gray-500 dark:text-gray-400">{$t('property.size')}</p>
                    <p class="font-medium text-gray-900 dark:text-white">{property.size_sqm} {$t('property.sqm')}</p>
                  </div>
                </div>
                
                <!-- Property location map -->
                {#if property.latitude && property.longitude}
                  <div class="h-60">
                    <PropertyMap 
                      latitude={property.latitude} 
                      longitude={property.longitude} 
                      title={property.title}
                      zoom={13}
                    />
                  </div>
                {/if}
              </div>
            {/if}
            
            <!-- Bid History -->
            <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
              <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">{$t('auction.bidHistory')}</h2>
              
              {#if auction.bids && auction.bids.length > 0}
                <div class="overflow-x-auto">
                  <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                    <thead class="bg-gray-50 dark:bg-gray-700">
                      <tr>
                        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                          {$t('auction.bidderName')}
                        </th>
                        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                          {$t('auction.bidAmount')}
                        </th>
                        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                          {$t('auction.bidTime')}
                        </th>
                        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                          {$t('auction.bidStatus')}
                        </th>
                      </tr>
                    </thead>
                    <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                      {#each auction.bids as bid}
                        <tr class={bid.bidder === $user?.email ? 'bg-primary-50 dark:bg-primary-900/20' : ''}>
                          <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                            {bid.bidder || 'Anonymous'}
                            {#if bid.bidder === $user?.email}
                              <span class="ml-1 text-xs text-primary-600 dark:text-primary-400">({$t('auction.you')})</span>
                            {/if}
                          </td>
                          <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700 dark:text-gray-300">
                            ${bid.bid_amount.toLocaleString()}
                          </td>
                          <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                            {formatDateTime(bid.bid_time)}
                          </td>
                          <td class="px-6 py-4 whitespace-nowrap">
                            <span class="inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium 
                              {bid.status === 'winning' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' : 
                               bid.status === 'outbid' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' :
                               bid.status === 'accepted' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200' :
                               bid.status === 'rejected' ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' :
                               'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'}"
                            >
                              {bid.status === 'winning' ? $t('auction.winning') : 
                               bid.status === 'outbid' ? $t('auction.outbid') :
                               bid.status === 'accepted' ? $t('auction.accepted') :
                               bid.status === 'rejected' ? $t('auction.rejected') :
                               bid.status === 'pending' ? $t('auction.pending') : bid.status}
                            </span>
                          </td>
                        </tr>
                      {/each}
                    </tbody>
                  </table>
                </div>
              {:else}
                <div class="text-center py-8 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-gray-400 dark:text-gray-500 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-1">{$t('auction.noBids')}</h3>
                  <p class="text-gray-500 dark:text-gray-400">{$t('auction.beTheFirst')}</p>
                </div>
              {/if}
            </div>
          </div>
          
          <!-- Sidebar (right) -->
          <div class="space-y-8">
            <!-- Auction status and time remaining -->
            <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
              {#if isLiveAuction && timeRemaining.days >= 0}
                <div class="mb-4">
                  <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">{$t('auction.timeRemaining')}</h3>
                  <div class="grid grid-cols-4 gap-2 text-center bg-gray-50 dark:bg-gray-700 rounded-lg p-3">
                    <div>
                      <span class="block text-2xl font-bold text-gray-900 dark:text-white">{timeRemaining.days}</span>
                      <span class="text-xs text-gray-500 dark:text-gray-400">{$t('auction.days')}</span>
                    </div>
                    <div>
                      <span class="block text-2xl font-bold text-gray-900 dark:text-white">{timeRemaining.hours}</span>
                      <span class="text-xs text-gray-500 dark:text-gray-400">{$t('auction.hours')}</span>
                    </div>
                    <div>
                      <span class="block text-2xl font-bold text-gray-900 dark:text-white">{timeRemaining.minutes}</span>
                      <span class="text-xs text-gray-500 dark:text-gray-400">{$t('auction.minutes')}</span>
                    </div>
                    <div>
                      <span class="block text-2xl font-bold text-gray-900 dark:text-white">{timeRemaining.seconds}</span>
                      <span class="text-xs text-gray-500 dark:text-gray-400">{$t('auction.seconds')}</span>
                    </div>
                  </div>
                </div>
              {:else if auction.status === 'scheduled'}
                <div class="mb-4">
                  <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">{$t('auction.startsIn')}</h3>
                  <p class="text-gray-700 dark:text-gray-300">{formatDateTime(auction.start_date)}</p>
                </div>
              {:else if auction.status === 'ended' || auction.status === 'completed'}
                <div class="mb-4">
                  <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">{$t('auction.auctionEnded')}</h3>
                  <p class="text-gray-700 dark:text-gray-300">{formatDateTime(auction.end_date)}</p>
                </div>
              {/if}
              
              <div class="border-t border-gray-200 dark:border-gray-700 pt-4 mb-4">
                <div class="flex justify-between items-baseline">
                  <h3 class="text-lg font-medium text-gray-900 dark:text-white">{$t('auction.currentBid')}</h3>
                  <span class="text-2xl font-bold text-primary-600 dark:text-primary-400">
                    ${auction.current_bid ? auction.current_bid.toLocaleString() : auction.starting_bid.toLocaleString()}
                  </span>
                </div>
                <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
                  {$t('auction.totalBids')}: {auction.bid_count}
                </p>
              </div>
              
              {#if isLiveAuction && timeRemaining.days >= 0}
                {#if $user}
                  <form on:submit|preventDefault={handlePlaceBid} class="border-t border-gray-200 dark:border-gray-700 pt-4">
                    <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">{$t('auction.placeBid')}</h3>
                    
                    {#if bidError}
                      <div class="mb-4 p-3 bg-red-50 dark:bg-red-900/20 text-red-800 dark:text-red-200 text-sm rounded">
                        {bidError}
                      </div>
                    {/if}
                    
                    {#if bidSuccess}
                      <div class="mb-4 p-3 bg-green-50 dark:bg-green-900/20 text-green-800 dark:text-green-200 text-sm rounded">
                        {bidSuccess}
                      </div>
                    {/if}
                    
                    <div class="mb-4">
                      <label for="bid-amount" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        {$t('auction.bidAmount')} 
                        <span class="text-gray-500 dark:text-gray-400">
                          ({$t('auction.minimumBid')}: ${minimumBidAmount.toLocaleString()})
                        </span>
                      </label>
                      <div class="mt-1 relative rounded-md shadow-sm">
                        <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                          <span class="text-gray-500 dark:text-gray-400 sm:text-sm">$</span>
                        </div>
                        <input
                          type="number"
                          name="price"
                          id="bid-amount"
                          bind:value={bidAmount}
                          min={minimumBidAmount}
                          step="0.01"
                          class="focus:ring-primary-500 focus:border-primary-500 block w-full pl-7 pr-12 sm:text-sm border-gray-300 dark:border-gray-600 rounded-md dark:bg-gray-700 dark:text-white"
                          placeholder="0.00"
                        />
                        <div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                          <span class="text-gray-500 dark:text-gray-400 sm:text-sm">USD</span>
                        </div>
                      </div>
                    </div>
                    
                    <button
                      type="submit"
                      disabled={placingBid}
                      class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {#if placingBid}
                        <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                      {/if}
                      {$t('auction.placeBid')}
                    </button>
                  </form>
                {:else}
                  <div class="border-t border-gray-200 dark:border-gray-700 pt-4">
                    <p class="text-gray-700 dark:text-gray-300 mb-4">{$t('auction.loginToPlaceBid')}</p>
                    <a 
                      href="/login" 
                      class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                    >
                      {$t('nav.login')}
                    </a>
                  </div>
                {/if}
              {:else if auction.status === 'scheduled'}
                <div class="border-t border-gray-200 dark:border-gray-700 pt-4">
                  <p class="text-gray-700 dark:text-gray-300 mb-4">{$t('auction.auctionNotStarted')}</p>
                  {#if $user}
                    <button 
                      type="button" 
                      class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                    >
                      {$t('auction.registerForAuction')}
                    </button>
                  {:else}
                    <a 
                      href="/login" 
                      class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                    >
                      {$t('auction.loginToRegister')}
                    </a>
                  {/if}
                </div>
              {:else}
                <div class="border-t border-gray-200 dark:border-gray-700 pt-4">
                  <p class="text-gray-700 dark:text-gray-300 mb-4">
                    {#if auction.status === 'completed' && auction.highest_bid}
                      {$t('auction.wonBy', { name: auction.highest_bid.bidder.name, amount: auction.highest_bid.amount.toLocaleString() })}
                    {:else}
                      {$t('auction.auctionEnded')}
                    {/if}
                  </p>
                  <a 
                    href="/auctions" 
                    class="w-full flex justify-center py-2 px-4 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                  >
                    {$t('auctions.browseAuctions')}
                  </a>
                </div>
              {/if}
            </div>
            
            <!-- Property thumbnail and quick info -->
            {#if property}
              <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
                <div class="bg-gray-200 dark:bg-gray-700 aspect-w-3 aspect-h-2">
                  {#if property.media && property.media.length > 0}
                    <img 
                      src={property.media[0]?.file || '/images/property-placeholder.jpg'} 
                      alt={property.title}
                      class="w-full h-full object-cover"
                    />
                  {:else}
                    <img 
                      src="/images/property-placeholder.jpg" 
                      alt={property.title}
                      class="w-full h-full object-cover"
                    />
                  {/if}
                </div>
                <div class="p-4">
                  <h3 class="font-medium text-gray-900 dark:text-white mb-2">{property.title}</h3>
                  <div class="flex justify-between text-sm mb-1">
                    <span class="text-gray-500 dark:text-gray-400">{$t('property.propertyType')}</span>
                    <span class="text-gray-900 dark:text-white">{property.property_type_display}</span>
                  </div>
                  <div class="flex justify-between text-sm mb-1">
                    <span class="text-gray-500 dark:text-gray-400">{$t('property.size')}</span>
                    <span class="text-gray-900 dark:text-white">{property.size_sqm} {$t('property.sqm')}</span>
                  </div>
                  <div class="flex justify-between text-sm mb-1">
                    <span class="text-gray-500 dark:text-gray-400">{$t('property.location')}</span>
                    <span class="text-gray-900 dark:text-white">{property.city}, {property.state}</span>
                  </div>
                  <div class="mt-4">
                    <a 
                      href={`/properties/${property.slug}`} 
                      class="text-primary-600 dark:text-primary-400 hover:underline text-sm font-medium"
                    >
                      {$t('property.viewDetails')} &rarr;
                    </a>
                  </div>
                </div>
              </div>
            {/if}
            
            <!-- Share and contact -->
            <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
              <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">{$t('auction.shareAuction')}</h3>
              <div class="flex space-x-4">
                <button class="text-blue-600 hover:text-blue-700">
                  <svg class="h-6 w-6" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path fill-rule="evenodd" d="M22 12c0-5.523-4.477-10-10-10S2 6.477 2 12c0 4.991 3.657 9.128 8.438 9.878v-6.987h-2.54V12h2.54V9.797c0-2.506 1.492-3.89 3.777-3.89 1.094 0 2.238.195 2.238.195v2.46h-1.26c-1.243 0-1.63.771-1.63 1.562V12h2.773l-.443 2.89h-2.33v6.988C18.343 21.128 22 16.991 22 12z" clip-rule="evenodd" />
                  </svg>
                  <span class="sr-only">Facebook</span>
                </button>
                <button class="text-blue-400 hover:text-blue-500">
                  <svg class="h-6 w-6" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path d="M8.29 20.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0022 5.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.106 4.106 0 001.27 5.477A4.072 4.072 0 012.8 9.713v.052a4.105 4.105 0 003.292 4.022 4.095 4.095 0 01-1.853.07 4.108 4.108 0 003.834 2.85A8.233 8.233 0 012 18.407a11.616 11.616 0 006.29 1.84" />
                  </svg>
                  <span class="sr-only">Twitter</span>
                </button>
                <button class="text-green-600 hover:text-green-700">
                  <svg class="h-6 w-6" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path fill-rule="evenodd" d="M3.5 3.5a.5.5 0 0 1 .5-.5h12a.5.5 0 0 1 .5.5v13a.5.5 0 0 1-.5.5h-12a.5.5 0 0 1-.5-.5v-13zm1 .5v12h11V4h-11z"/>
                    <path d="M3.5 14.5a.5.5 0 0 1 .5-.5h4a.5.5 0 0 1 0 1H4a.5.5 0 0 1-.5-.5zm0-3a.5.5 0 0 1 .5-.5h9a.5.5 0 0 1 0 1h-9a.5.5 0 0 1-.5-.5zm0-3a.5.5 0 0 1 .5-.5h9a.5.5 0 0 1 0 1h-9a.5.5 0 0 1-.5-.5zm0-3a.5.5 0 0 1 .5-.5h9a.5.5 0 0 1 0 1h-9a.5.5 0 0 1-.5-.5z"/>
                  </svg>
                  <span class="sr-only">WhatsApp</span>
                </button>
                <button class="text-blue-700 hover:text-blue-800">
                  <svg class="h-6 w-6" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14m-.5 15.5v-5.3a3.26 3.26 0 0 0-3.26-3.26c-.85 0-1.84.52-2.32 1.3v-1.11h-2.79v8.37h2.79v-4.93c0-.77.62-1.4 1.39-1.4a1.4 1.4 0 0 1 1.4 1.4v4.93h2.79M6.88 8.56a1.68 1.68 0 0 0 1.68-1.68c0-.93-.75-1.69-1.68-1.69a1.69 1.69 0 0 0-1.69 1.69c0 .93.76 1.68 1.69 1.68m1.39 9.94v-8.37H5.5v8.37h2.77z"/>
                  </svg>
                  <span class="sr-only">LinkedIn</span>
                </button>
              </div>
              
              <div class="mt-6">
                <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">{$t('auction.needHelp')}</h3>
                <a 
                  href="/contact" 
                  class="w-full flex justify-center py-2 px-4 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                >
                  {$t('auction.contactSupport')}
                </a>
              </div>
            </div>
          </div>
        </div>
      {/if}
    </div>
  </div>