<script>
  import { t } from '$lib/i18n';
  import Tabs from '$lib/components/ui/Tabs.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Gallery from '$lib/components/ui/Gallery.svelte';
  import PropertyCard from '$lib/components/properties/PropertyCard.svelte';
  import AuctionStatus from '$lib/components/auction/AuctionStatus.svelte';
  
  export let auction;
  export let property;
  export let bids;
  export let bidsLoading;
  export let canBid;
  export let user;
  export let onLoadBids;
  export let onOpenBidModal;
  
  let activeTab = 'details';
  
  // Fix: Properly reactive tabs calculation
  $: tabs = [
    { id: 'details', label: $t('auction.tabDetails') },
    { id: 'property', label: $t('auction.tabProperty') },
    { id: 'bids', label: `${$t('auction.tabBids')} (${Array.isArray(bids) ? bids.length : 0})` },
    { id: 'terms', label: $t('auction.tabTerms') }
  ];
  
  // Debug logging for bids data
  $: if (bids && bids.length > 0) {
    console.log('🔍 BIDS DEBUG - Raw bids data:', bids);
    console.log('🔍 BIDS DEBUG - First bid structure:', JSON.stringify(bids[0], null, 2));
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
    
    if (diffInSeconds < 60) return $t('auction.justNow') || 'Just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}${$t('auction.minutesAgo') || 'm ago'}`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}${$t('auction.hoursAgo') || 'h ago'}`;
    return `${Math.floor(diffInSeconds / 86400)}${$t('auction.daysAgo') || 'd ago'}`;
  }
  
  // COMPLETELY REWRITTEN: Ultra-safe bidder name function
  function getBidderName(bid) {
    console.log('🔍 getBidderName called with bid:', bid);
    
    if (!bid || typeof bid !== 'object') {
      console.log('❌ Invalid bid object, returning anonymous');
      return $t('auction.anonymousBidder') || 'Anonymous Bidder';
    }
    
    // Log all available properties for debugging
    console.log('🔍 Available bid properties:', Object.keys(bid));
    
    // Method 1: Try user_display_name (from backend serializer)
    if (bid.user_display_name) {
      const displayName = String(bid.user_display_name).trim();
      console.log('🔍 Found user_display_name:', displayName);
      if (isValidName(displayName)) {
        console.log('✅ Using user_display_name:', displayName);
        return displayName;
      }
    }
    
    // Method 2: Try bidder_info object
    if (bid.bidder_info && typeof bid.bidder_info === 'object') {
      const bidderInfo = bid.bidder_info;
      console.log('🔍 Processing bidder_info:', bidderInfo);
      
      // Try name field from bidder_info
      if (bidderInfo.name) {
        const name = String(bidderInfo.name).trim();
        console.log('🔍 Found bidder_info.name:', name);
        if (isValidName(name)) {
          console.log('✅ Using bidder_info.name:', name);
          return name;
        }
      }
      
      // Try username from bidder_info
      if (bidderInfo.username) {
        const username = String(bidderInfo.username).trim();
        console.log('🔍 Found bidder_info.username:', username);
        if (isValidName(username)) {
          console.log('✅ Using bidder_info.username:', username);
          return username;
        }
      }
      
      // Try first_name + last_name combination
      if (bidderInfo.first_name) {
        const firstName = String(bidderInfo.first_name).trim();
        console.log('🔍 Found bidder_info.first_name:', firstName);
        if (isValidName(firstName)) {
          const lastName = bidderInfo.last_name ? String(bidderInfo.last_name).trim() : '';
          if (isValidName(lastName)) {
            const fullName = `${firstName} ${lastName}`;
            console.log('✅ Using full name:', fullName);
            return fullName;
          } else {
            console.log('✅ Using first name only:', firstName);
            return firstName;
          }
        }
      }
      
      // Try email prefix
      if (bidderInfo.email && String(bidderInfo.email).includes('@')) {
        const emailPrefix = String(bidderInfo.email).split('@')[0];
        console.log('🔍 Found email prefix:', emailPrefix);
        if (isValidName(emailPrefix)) {
          console.log('✅ Using email prefix:', emailPrefix);
          return emailPrefix;
        }
      }
      
      // Try ID as last resort
      if (bidderInfo.id) {
        const userId = `User ${bidderInfo.id}`;
        console.log('✅ Using user ID fallback:', userId);
        return userId;
      }
    }
    
    // Method 3: Try direct bid properties as fallback
    if (bid.bidder && typeof bid.bidder === 'string') {
      const bidder = String(bid.bidder).trim();
      console.log('🔍 Found direct bidder field:', bidder);
      if (isValidName(bidder)) {
        console.log('✅ Using direct bidder field:', bidder);
        return bidder;
      }
    }
    
    // Method 4: Try user object if present
    if (bid.user && typeof bid.user === 'object') {
      if (bid.user.username) {
        const username = String(bid.user.username).trim();
        console.log('🔍 Found user.username:', username);
        if (isValidName(username)) {
          console.log('✅ Using user.username:', username);
          return username;
        }
      }
    }
    
    console.log('❌ No valid bidder name found, using anonymous fallback');
    return $t('auction.anonymousBidder') || 'Anonymous Bidder';
  }
  
  // Helper function to validate if a name is valid
  function isValidName(name) {
    if (!name || typeof name !== 'string') return false;
    const trimmed = name.trim();
    const invalid = ['undefined', 'null', 'NaN', '[object Object]', '', 'Anonymous'];
    return trimmed.length > 0 && !invalid.includes(trimmed);
  }
  
  // Function to handle tab change and update parent
  function handleTabChange(event) {
    const tabId = event && event.id ? event.id : event;
    activeTab = tabId;
    
    console.log(`Tab changed to: ${tabId}`);
    
    if (tabId === 'bids' && (!Array.isArray(bids) || bids.length === 0) && !bidsLoading) {
      onLoadBids();
    }
  }
</script>

<!-- Image Gallery -->
<section class="bg-white dark:bg-gray-800 rounded-lg shadow-sm overflow-hidden">
  <Gallery 
    images={getAllImages()} 
    alt={auction.title}
    showThumbnails={true}
  />
</section>

<!-- Navigation Tabs -->
<div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm overflow-hidden">
  <div class="border-b border-gray-200 dark:border-gray-700">
    <Tabs {tabs} bind:activeTab on:change={(e) => handleTabChange(e.detail)} />
  </div>
  
  <!-- Tab Content -->
  <div class="p-4 sm:p-6">
    {#if activeTab === 'details'}
      <div class="prose dark:prose-invert max-w-none">
        <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-4">
          {$t('auction.description')}
        </h2>
        
        {#if auction.description}
          <div class="text-gray-600 dark:text-gray-300 leading-relaxed mb-6">
            <p class="whitespace-pre-wrap">{auction.description}</p>
          </div>
        {:else}
          <div class="text-center py-6 text-gray-500 dark:text-gray-400">
            <svg class="w-10 h-10 mx-auto mb-2 opacity-40" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p class="text-sm">{$t('auction.noDescription')}</p>
          </div>
        {/if}
        
        <!-- Key Information Cards -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Schedule Card -->
          <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
            <h3 class="text-base font-semibold text-gray-900 dark:text-white mb-3 flex items-center">
              <svg class="w-4 h-4 mr-2 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {$t('auction.schedule')}
            </h3>
            <dl class="space-y-2">
              <div class="flex justify-between items-center">
                <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
                  {$t('auction.startDate')}
                </dt>
                <dd class="text-sm font-semibold text-gray-900 dark:text-white">
                  {formatDateTime(auction.start_date)}
                </dd>
              </div>
              <div class="flex justify-between items-center">
                <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
                  {$t('auction.endDate')}
                </dt>
                <dd class="text-sm font-semibold text-gray-900 dark:text-white">
                  {formatDateTime(auction.end_date)}
                </dd>
              </div>
              {#if auction.registration_deadline}
                <div class="flex justify-between items-center">
                  <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
                    {$t('auction.registrationDeadline')}
                  </dt>
                  <dd class="text-sm font-semibold text-gray-900 dark:text-white">
                    {formatDateTime(auction.registration_deadline)}
                  </dd>
                </div>
              {/if}
            </dl>
          </div>
          
          <!-- Financial Details Card -->
          <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
            <h3 class="text-base font-semibold text-gray-900 dark:text-white mb-3 flex items-center">
              <svg class="w-4 h-4 mr-2 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
              </svg>
              {$t('auction.keyDetails')}
            </h3>
            <dl class="space-y-2">
              <div class="flex justify-between items-center">
                <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
                  {$t('auction.startingBid')}
                </dt>
                <dd class="text-sm font-semibold text-gray-900 dark:text-white">
                  {formatCurrency(auction.starting_bid)}
                </dd>
              </div>
              <div class="flex justify-between items-center">
                <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
                  {$t('auction.currentBid')}
                </dt>
                <dd class="text-sm font-semibold text-green-600 dark:text-green-400">
                  {formatCurrency(auction.current_bid || auction.starting_bid)}
                </dd>
              </div>
              <div class="flex justify-between items-center">
                <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
                  {$t('auction.minimumIncrement')}
                </dt>
                <dd class="text-sm font-semibold text-gray-900 dark:text-white">
                  {formatCurrency(auction.minimum_increment)}
                </dd>
              </div>
            </dl>
          </div>
        </div>
      </div>
      
    {:else if activeTab === 'property'}
      <div class="space-y-6">
        <div class="flex items-center justify-between">
          <h2 class="text-xl font-bold text-gray-900 dark:text-white">
            {$t('auction.auctionProperty')}
          </h2>
          {#if property && property.slug}
            <a 
              href={`/properties/${property.slug}`} 
              target="_blank"
              class="inline-flex items-center text-sm font-medium text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 transition-colors"
            >
              {$t('property.viewDetails')}
              <svg class="h-4 w-4 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
            </a>
          {/if}
        </div>
        
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- Property Card -->
          <div>
            {#if property}
              <PropertyCard property={property} isCompact={true} />
            {:else}
              <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-6 text-center">
                <p class="text-gray-500 dark:text-gray-400">{$t('property.noPropertyData') || 'Property data not available'}</p>
              </div>
            {/if}
          </div>
          
          <!-- Property Details -->
          <div class="space-y-4">
            {#if property}
              <!-- Key Details -->
              <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                <h4 class="text-base font-semibold text-gray-900 dark:text-white mb-3">
                  {$t('property.keyDetails')}
                </h4>
                <dl class="space-y-2">
                  <div class="flex justify-between items-center">
                    <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
                      {$t('property.propertyType')}
                    </dt>
                    <dd class="text-sm font-semibold text-gray-900 dark:text-white">
                      {property.property_type_display || 'N/A'}
                    </dd>
                  </div>
                  <div class="flex justify-between items-center">
                    <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
                      {$t('property.size')}
                    </dt>
                    <dd class="text-sm font-semibold text-gray-900 dark:text-white">
                      {property.size_sqm || 'N/A'} {property.size_sqm ? $t('property.sqm') : ''}
                    </dd>
                  </div>
                  <div class="flex justify-between items-center">
                    <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
                      {$t('property.location')}
                    </dt>
                    <dd class="text-sm font-semibold text-gray-900 dark:text-white">
                      {property.location?.city ? `${property.location.city}, ${property.location.state || ''}` : 'N/A'}
                    </dd>
                  </div>
                  <div class="flex justify-between items-center">
                    <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
                      {$t('property.marketValue')}
                    </dt>
                    <dd class="text-sm font-semibold text-green-600 dark:text-green-400">
                      {property.market_value ? formatCurrency(property.market_value) : 'N/A'}
                    </dd>
                  </div>
                </dl>
              </div>
            {:else}
              <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 text-center">
                <p class="text-gray-500 dark:text-gray-400">{$t('property.noPropertyDetails') || 'Property details not available'}</p>
              </div>
            {/if}
            
            <!-- Features -->
            {#if property && property.features && property.features.length > 0}
              <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                <h4 class="text-base font-semibold text-gray-900 dark:text-white mb-3">
                  {$t('property.features')}
                </h4>
                <div class="flex flex-wrap gap-1.5">
                  {#each property.features as feature}
                    <span class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                      {feature}
                    </span>
                  {/each}
                </div>
              </div>
            {/if}
          </div>
        </div>
      </div>
      
    {:else if activeTab === 'bids'}
      <div class="space-y-4">
        <!-- DEBUG: Show raw bid data for first bid (remove this in production) -->
        {#if bids && bids.length > 0}
          <details class="bg-yellow-50 dark:bg-yellow-900/20 p-3 rounded-lg border border-yellow-200 dark:border-yellow-800 text-xs">
            <summary class="cursor-pointer font-semibold text-yellow-800 dark:text-yellow-200">
              🔍 Debug: Click to see raw bid data structure
            </summary>
            <div class="mt-2 space-y-2">
              <p class="font-semibold">First bid object keys:</p>
              <p class="bg-white dark:bg-gray-800 p-2 rounded font-mono">{Object.keys(bids[0]).join(', ')}</p>
              <p class="font-semibold">Full first bid object:</p>
              <pre class="bg-white dark:bg-gray-800 p-2 rounded overflow-auto max-h-40">{JSON.stringify(bids[0], null, 2)}</pre>
           </div>
         </details>
       {/if}
       
       <!-- Bid History Header -->
       <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
         <div>
           <h2 class="text-xl font-bold text-gray-900 dark:text-white">
             {$t('auction.bidHistory')}
           </h2>
           <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
             {Array.isArray(bids) ? bids.length : 0} {$t('auction.bidsPlaced')}
           </p>
         </div>
         <div class="flex items-center gap-2">
           {#if canBid}
             <Button
               variant="primary"
               size="small"
               on:click={onOpenBidModal}
             >
               <svg class="w-4 h-4 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                 <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
               </svg>
               {$t('auction.placeBid')}
             </Button>
           {/if}
           <Button
             variant="outline"
             size="small"
             loading={bidsLoading}
             on:click={onLoadBids}
           >
             <svg class="w-4 h-4 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
               <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
             </svg>
             {$t('auction.refresh')}
           </Button>
         </div>
       </div>
       
       {#if bidsLoading}
         <!-- Loading State -->
         <div class="flex items-center justify-center py-12">
           <div class="text-center">
             <div class="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500 mb-3"></div>
             <p class="text-sm text-gray-500 dark:text-gray-400">{$t('auction.loadingBids')}</p>
           </div>
         </div>
         
       {:else if !Array.isArray(bids) || bids.length === 0}
         <!-- Empty State -->
         <div class="text-center py-12">
           <div class="w-12 h-12 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-3">
             <svg class="w-6 h-6 text-gray-400 dark:text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
               <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
             </svg>
           </div>
           <h3 class="text-base font-semibold text-gray-900 dark:text-gray-100 mb-2">
             {$t('auction.noBids')}
           </h3>
           <p class="text-gray-500 dark:text-gray-400 mb-4 text-sm">
             {$t('auction.beTheFirst')}
           </p>
           {#if canBid}
             <Button
               variant="primary"
               on:click={onOpenBidModal}
             >
               <svg class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                 <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
               </svg>
               {$t('auction.placeFirstBid')}
             </Button>
           {:else if !user}
             <Button
               variant="primary"
               href={`/login?redirect=/auctions/${auction.slug}`}
             >
               {$t('auction.signInToPlaceFirstBid')}
             </Button>
           {/if}
         </div>
         
       {:else}
         <!-- Bid List -->
         <div class="space-y-3">
           {#each bids as bid, index (bid.id || `bid-${index}`)}
             <div class="group relative rounded-lg border border-gray-200 dark:border-gray-700 p-4 hover:border-gray-300 dark:hover:border-gray-600 transition-all duration-200 {index === 0 ? 'bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/10 dark:to-emerald-900/10 border-green-200 dark:border-green-800' : 'bg-white dark:bg-gray-800'} {bid.bidder_info?.id === user?.id ? 'ring-1 ring-blue-200 dark:ring-blue-800' : ''}">
               <div class="flex items-center justify-between">
                 <div class="flex-1 min-w-0">
                   <div class="flex items-center gap-2 mb-1">
                     <p class="text-sm font-semibold text-gray-900 dark:text-white">
                       {formatCurrency(bid.amount)}
                     </p>
                     {#if index === 0}
                       <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                         {$t('auction.highestBid')}
                       </span>
                     {/if}
                   </div>
                   <div class="text-xs text-gray-500 dark:text-gray-400 truncate">
                     <!-- FIXED: Use the ultra-safe getBidderName function -->
                     <span class="font-medium">
                       {getBidderName(bid)}
                     </span>
                     {#if bid.bidder_info?.id === user?.id}
                       <span class="text-blue-600 dark:text-blue-400 font-medium ml-1">({$t('auction.you')})</span>
                     {/if}
                   </div>
                 </div>
                 <div class="text-right flex-shrink-0 ml-2">
                   <p class="text-xs text-gray-500 dark:text-gray-400 mb-1">
                     {getTimeAgo(bid.bid_time)}
                   </p>
                   {#if bid.status}
                     <AuctionStatus status={bid.status} isCompact={true} />
                   {:else}
                     <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                       {$t('auction.activeBid')}
                     </span>
                   {/if}
                 </div>
               </div>
               
               <!-- Additional bid info if available -->
               {#if bid.auto_bid || bid.max_amount}
                 <div class="mt-2 pt-2 border-t border-gray-200 dark:border-gray-600">
                   <div class="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
                     {#if bid.auto_bid}
                       <span class="inline-flex items-center gap-1">
                         <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                           <path fill-rule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clip-rule="evenodd" />
                         </svg>
                         {$t('auction.autoBid')}
                       </span>
                     {/if}
                     {#if bid.max_amount}
                       <span>{$t('auction.maxBid')}: {formatCurrency(bid.max_amount)}</span>
                     {/if}
                   </div>
                 </div>
               {/if}
             </div>
           {/each}
         </div>
         
         <!-- Load More Button if there are many bids -->
         {#if bids.length >= 10}
           <div class="text-center pt-4">
             <Button
               variant="outline"
               size="small"
               on:click={onLoadBids}
               loading={bidsLoading}
             >
               {$t('auction.loadMoreBids')}
             </Button>
           </div>
         {/if}
       {/if}
     </div>
     
   {:else if activeTab === 'terms'}
     <div class="space-y-4">
       <h2 class="text-xl font-bold text-gray-900 dark:text-white">
         {$t('auction.termsConditions')}
       </h2>
       
       {#if auction && auction.terms_conditions}
         <div class="prose dark:prose-invert max-w-none bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
           <div class="text-gray-600 dark:text-gray-300 whitespace-pre-wrap leading-relaxed">
             {auction.terms_conditions}
           </div>
         </div>
       {:else}
         <div class="text-center py-12 bg-gray-50 dark:bg-gray-700 rounded-lg">
           <div class="w-12 h-12 bg-gray-200 dark:bg-gray-600 rounded-full flex items-center justify-center mx-auto mb-3">
             <svg class="w-6 h-6 text-gray-400 dark:text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
               <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
             </svg>
           </div>
           <h3 class="text-base font-semibold text-gray-900 dark:text-gray-100 mb-1">
             {$t('auction.noTerms')}
           </h3>
           <p class="text-gray-500 dark:text-gray-400 text-sm">
             {$t('auction.contactForTerms')}
           </p>
         </div>
       {/if}
       
       <!-- Standard auction terms if no custom terms -->
       {#if auction && !auction.terms_conditions}
         <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
           <h4 class="text-sm font-semibold text-blue-900 dark:text-blue-200 mb-2">
             {$t('auction.standardTerms')}
           </h4>
           <ul class="text-sm text-blue-800 dark:text-blue-300 space-y-1">
             <li>• {$t('auction.term1')}</li>
             <li>• {$t('auction.term2')}</li>
             <li>• {$t('auction.term3')}</li>
             <li>• {$t('auction.term4')}</li>
           </ul>
         </div>
       {:else if !auction}
         <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-6 text-center">
           <p class="text-gray-500 dark:text-gray-400">{$t('auction.noAuctionData') || 'Auction data not available'}</p>
         </div>
       {/if}
     </div>
   {/if}
 </div>
</div>
