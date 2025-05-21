<!-- src/routes/auctions/[slug]/+page.svelte (Refactored) -->
<script>
  import { onMount, onDestroy } from 'svelte';
  import { page } from '$app/stores';
  import { t } from '$lib/i18n/i18n';
  import { user } from '$lib/stores/user';
  import { fetchAuctionBySlug, placeBid } from '$lib/api/auction';
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
  
  let auction = null;
  let property = null;
  let loading = true;
  let error = null;
  let bidAmount = '';
  let placingBid = false;
  let bidError = '';
  let bidSuccess = '';
  let activeTab = 'details';
  let showBidModal = false;
  let showLoginModal = false;
  
  $: slug = $page.params.slug;
  $: isLiveAuction = auction?.status === 'live';
  $: canBid = isLiveAuction && $user && auction?.end_date > new Date().toISOString();
  $: minimumBidAmount = calculateMinimumBid();
  $: breadcrumbItems = [
    { label: $t('nav.home'), href: '/' },
    { label: $t('nav.auctions'), href: '/auctions' },
    { label: auction?.title || $t('auction.loading'), href: `/auctions/${slug}`, active: true }
  ];
  
  function calculateMinimumBid() {
    if (!auction) return 0;
    
    // If there's a current bid, the minimum is current bid + increment
    if (auction.current_bid) {
      return parseFloat(auction.current_bid) + parseFloat(auction.minimum_increment);
    }
    
    // Otherwise, use the starting bid
    return parseFloat(auction.starting_bid);
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
        bidError = $t('auction.bidTooLow', { amount: minimumBidAmount.toLocaleString() });
        return;
      }
      
      // Submit bid
      await placeBid(auction.id, amount);
      
      // Show success message
      bidSuccess = $t('auction.bidPlaced');
      
      // Reset bid amount
      bidAmount = '';
      
      // Close the modal
      showBidModal = false;
      
      // Reload auction data to get updated bids
      await loadAuctionData();
      
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
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      }).format(date);
    } catch (e) {
      return dateString;
    }
  }
  
  function openBidModal() {
    if ($user) {
      showBidModal = true;
    } else {
      showLoginModal = true;
    }
  }
  
  onMount(() => {
    loadAuctionData();
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
      <!-- Auction header -->
      <div class="mb-8">
        <div class="flex flex-wrap items-start justify-between">
          <div class="mb-4 md:mb-0">
            <div class="flex flex-wrap items-center space-x-2 mb-2">
              <AuctionStatus status={auction.status} />
              <span class="inline-flex items-center px-2.5 py-0.5 rounded-md text-sm font-medium bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200">
                {auction.auction_type === 'sealed' ? $t('auction.typeSealed') :
                 auction.auction_type === 'reserve' ? $t('auction.typeReserve') :
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
          
          <!-- Tabs Navigation -->
          <Tabs {tabs} bind:activeTab />
          
          <!-- Tab Content -->
          <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
            {#if activeTab === 'details'}
              <div class="prose dark:prose-invert max-w-none text-gray-600 dark:text-gray-300">
                <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                  {$t('auction.description')}
                </h2>
                <p>{auction.description}</p>
                
                <div class="mt-8 grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">
                      {$t('auction.startEndDates')}
                    </h3>
                    <dl class="grid grid-cols-2 gap-x-4 gap-y-2">
                      <dt class="text-sm text-gray-500 dark:text-gray-400">
                        {$t('auction.startDate')}
                      </dt>
                      <dd class="text-sm font-medium text-gray-900 dark:text-white">
                        {formatDateTime(auction.start_date)}
                      </dd>
                      <dt class="text-sm text-gray-500 dark:text-gray-400">
                        {$t('auction.endDate')}
                      </dt>
                      <dd class="text-sm font-medium text-gray-900 dark:text-white">
                        {formatDateTime(auction.end_date)}
                      </dd>
                      {#if auction.registration_deadline}
                        <dt class="text-sm text-gray-500 dark:text-gray-400">
                          {$t('auction.registrationDeadline')}
                        </dt>
                        <dd class="text-sm font-medium text-gray-900 dark:text-white">
                          {formatDateTime(auction.registration_deadline)}
                        </dd>
                      {/if}
                    </dl>
                  </div>
                  
                  <div>
                    <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">
                      {$t('auction.bidding')}
                    </h3>
                    <dl class="grid grid-cols-2 gap-x-4 gap-y-2">
                      <dt class="text-sm text-gray-500 dark:text-gray-400">
                        {$t('auction.startingBid')}
                      </dt>
                      <dd class="text-sm font-medium text-gray-900 dark:text-white">
                        ${auction.starting_bid.toLocaleString()}
                      </dd>
                      <dt class="text-sm text-gray-500 dark:text-gray-400">
                        {$t('auction.currentBid')}
                      </dt>
                      <dd class="text-sm font-medium text-gray-900 dark:text-white">
                        ${auction.current_bid ? auction.current_bid.toLocaleString() : 
                          auction.starting_bid.toLocaleString()}
                      </dd>
                      <dt class="text-sm text-gray-500 dark:text-gray-400">
                        {$t('auction.minimumIncrement')}
                      </dt>
                      <dd class="text-sm font-medium text-gray-900 dark:text-white">
                        ${auction.minimum_increment.toLocaleString()}
                      </dd>
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
                  >
                    {$t('property.viewDetails')}
                    <svg class="h-4 w-4 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                    </svg>
                  </a>
                </div>
                
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
                  <div>
                    <PropertyCard {property} isCompact={true} />
                  </div>
                  
                  <div class="space-y-4">
                    <div class="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                      <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        {$t('property.keyDetails')}
                      </h4>
                      <dl class="grid grid-cols-2 gap-x-4 gap-y-2">
                        <dt class="text-sm text-gray-500 dark:text-gray-400">
                          {$t('property.propertyType')}
                        </dt>
                        <dd class="text-sm font-medium text-gray-900 dark:text-white">
                          {property.property_type_display}
                        </dd>
                        <dt class="text-sm text-gray-500 dark:text-gray-400">
                          {$t('property.size')}
                        </dt>
                        <dd class="text-sm font-medium text-gray-900 dark:text-white">
                          {property.size_sqm} {$t('property.sqm')}
                        </dd>
                        <dt class="text-sm text-gray-500 dark:text-gray-400">
                          {$t('property.location')}
                        </dt>
                        <dd class="text-sm font-medium text-gray-900 dark:text-white">
                          {property.location?.city}, {property.location?.state}
                        </dd>
                        <dt class="text-sm text-gray-500 dark:text-gray-400">
                          {$t('property.marketValue')}
                        </dt>
                        <dd class="text-sm font-medium text-gray-900 dark:text-white">
                          ${property.market_value?.toLocaleString()}
                        </dd>
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
                <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                  {$t('auction.bidHistory')}
                </h2>
                
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
                              <AuctionStatus status={bid.status} isCompact={true} />
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
              
            {:else if activeTab === 'terms'}
              <div>
                <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                  {$t('auction.termsConditions')}
                </h2>
                
                {#if auction.terms_conditions}
                  <div class="prose dark:prose-invert max-w-none text-gray-600 dark:text-gray-300">
                    <p>{auction.terms_conditions}</p>
                  </div>
                {:else}
                  <div class="text-center py-8 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-gray-400 dark:text-gray-500 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-1">
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
        <div class="space-y-8">
          <!-- Auction status and time remaining -->
          <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
            {#if isLiveAuction}
              <div class="mb-4">
                <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">
                  {$t('auction.timeRemaining')}
                </h3>
                <CountdownTimer 
                  endDate={auction.end_date}
                  onEnd={loadAuctionData}
                />
              </div>
            {:else if auction.status === 'scheduled'}
              <div class="mb-4">
                <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">
                  {$t('auction.startsIn')}
                </h3>
                <CountdownTimer 
                  endDate={auction.start_date}
                  onEnd={loadAuctionData}
                  variant="secondary"
                />
                <p class="text-gray-700 dark:text-gray-300 mt-2">
                  {formatDateTime(auction.start_date)}
                </p>
              </div>
            {:else if auction.status === 'ended' || auction.status === 'completed'}
              <div class="mb-4">
                <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">
                  {$t('auction.auctionEnded')}
                </h3>
                <p class="text-gray-700 dark:text-gray-300">
                  {formatDateTime(auction.end_date)}
                </p>
              </div>
            {/if}
            
            <div class="border-t border-gray-200 dark:border-gray-700 pt-4 mb-4">
              <div class="flex justify-between items-baseline mb-1">
                <h3 class="text-lg font-medium text-gray-900 dark:text-white">
                  {$t('auction.currentBid')}
                </h3>
                <span class="text-2xl font-bold text-primary-600 dark:text-primary-400">
                  ${auction.current_bid ? auction.current_bid.toLocaleString() : 
                    auction.starting_bid.toLocaleString()}
                </span>
              </div>
              <p class="text-sm text-gray-500 dark:text-gray-400 mb-4">
                {$t('auction.totalBids')}: {auction.bid_count}
              </p>
              
              {#if isLiveAuction}
                <Button
                  variant="primary"
                  class="w-full"
                  onClick={openBidModal}
                  aria-label={$t('auction.placeBid')}
                >
                  {$t('auction.placeBid')}
                </Button>
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
                  variant="secondary"
                  class="w-full"
                  href="/auctions"
                  aria-label={$t('auctions.backToAuctions')}
                >
                  {$t('auctions.backToAuctions')}
                </Button>
              {/if}
            </div>
            
            <!-- Contact info -->
            <div class="border-t border-gray-200 dark:border-gray-700 pt-4">
              <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">
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
              <div class="p-4">
                <div class="flex justify-between items-center mb-4">
                  <h3 class="text-lg font-medium text-gray-900 dark:text-white">
                    {$t('auction.propertyInfo')}
                  </h3>
                  <a 
                    href={`/properties/${property.slug}`} 
                    class="text-sm text-primary-600 dark:text-primary-400 hover:underline"
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
                
                <h4 class="font-medium text-gray-900 dark:text-white mb-2">
                  {property.title}
                </h4>
                
                <dl class="grid grid-cols-2 gap-y-2 text-sm mb-4">
                  <dt class="text-gray-500 dark:text-gray-400">{$t('property.location')}</dt>
                  <dd class="text-gray-900 dark:text-white">{property.location?.city}, {property.location?.state}</dd>
                  
                  <dt class="text-gray-500 dark:text-gray-400">{$t('property.propertyType')}</dt>
                  <dd class="text-gray-900 dark:text-white">{property.property_type_display}</dd>
                  
                  <dt class="text-gray-500 dark:text-gray-400">{$t('property.size')}</dt>
                  <dd class="text-gray-900 dark:text-white">{property.size_sqm} {$t('property.sqm')}</dd>
                  
                  <dt class="text-gray-500 dark:text-gray-400">{$t('property.marketValue')}</dt>
                  <dd class="text-gray-900 dark:text-white">${property.market_value?.toLocaleString()}</dd>
                </dl>
              </div>
            </div>
          {/if}
          
          <!-- Bidding Tips -->
          <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
            <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">
              {$t('auction.biddingTips')}
            </h3>
            <ul class="space-y-3 text-sm text-gray-600 dark:text-gray-300">
              <li class="flex">
                <svg class="h-5 w-5 text-primary-500 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                </svg>
                {$t('auction.tip1')}
              </li>
              <li class="flex">
                <svg class="h-5 w-5 text-primary-500 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                </svg>
                {$t('auction.tip2')}
              </li>
              <li class="flex">
                <svg class="h-5 w-5 text-primary-500 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                </svg>
                {$t('auction.tip3')}
              </li>
            </ul>
          </div>
        </div>
      </div>
    {/if}
  </div>
</div>

<!-- Bid Modal -->
<Modal
  bind:show={showBidModal}
  title={$t('auction.placeBid')}
  maxWidth="sm"
>
  <form on:submit|preventDefault={handlePlaceBid} class="space-y-4">
    {#if bidError}
      <Alert type="error" message={bidError} />
    {/if}
    
    {#if bidSuccess}
      <Alert type="success" message={bidSuccess} />
    {/if}
    
    <div>
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
    
    <div class="mt-2 text-sm text-gray-500 dark:text-gray-400">
      {$t('auction.bidDisclaimer')}
    </div>
    
    <div class="flex justify-end space-x-3 mt-6">
      <Button
        variant="outline"
        type="button"
        onClick={() => showBidModal = false}
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
  <div class="text-center py-4">
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