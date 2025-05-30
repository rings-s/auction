<script>
    import { t } from '$lib/i18n';
    import Button from '$lib/components/ui/Button.svelte';
    import CountdownTimer from '$lib/components/auction/CountdownTimer.svelte';
    import AuctionStatus from '$lib/components/auction/AuctionStatus.svelte';
    
    export let auction;
    export let property;
    export let bids;
    export let canBid;
    export let canRegister;
    export let isOwner;
    export let isLiveAuction;
    export let isScheduledAuction;
    export let isActiveAuction;
    export let isRegistered;
    export let placingBid;
    export let minimumBidAmount;
    export let user;
    export let onTimerEnd;
    export let onOpenBidModal;
    export let onShowRegisterModal;
    export let onShowExtendModal;
    
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
      
      if (diffInSeconds < 60) return 'Just now';
      if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
      if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
      return `${Math.floor(diffInSeconds / 86400)}d ago`;
    }
  </script>
  
  <!-- Auction Status Card -->
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-4">
    
    {#if isLiveAuction}
      <!-- Live Auction Timer -->
      <div class="mb-4">
        <h3 class="text-base font-semibold text-gray-900 dark:text-white mb-3 flex items-center">
          <span class="w-2 h-2 bg-danger-500 rounded-full mr-2 animate-pulse"></span>
          {$t('auction.timeRemaining')}
        </h3>
        <CountdownTimer 
          endDate={auction.end_date}
          onEnd={onTimerEnd}
        />
      </div>
      
    {:else if auction.status === 'scheduled'}
      <!-- Scheduled Auction Timer -->
      <div class="mb-4">
        <h3 class="text-base font-semibold text-gray-900 dark:text-white mb-3 flex items-center">
          <span class="w-2 h-2 bg-warning-500 rounded-full mr-2 animate-pulse"></span>
          {$t('auction.startsIn')}
        </h3>
        <CountdownTimer 
          endDate={auction.start_date}
          onEnd={onTimerEnd}
          variant="secondary"
        />
        <p class="text-gray-600 dark:text-gray-400 mt-2 text-sm">
          {formatDateTime(auction.start_date)}
        </p>
      </div>
      
    {:else if auction.status === 'ended' || auction.status === 'completed'}
      <!-- Ended Auction -->
      <div class="mb-4">
        <h3 class="text-base font-semibold text-gray-900 dark:text-white mb-2">
          {$t('auction.auctionEnded')}
        </h3>
        <p class="text-gray-600 dark:text-gray-400 text-sm">
          {formatDateTime(auction.end_date)}
        </p>
        {#if auction.status === 'completed' && bids.length > 0}
          <div class="mt-3 p-3 bg-success-50 dark:bg-success-900/20 rounded-lg border border-success-200 dark:border-success-800">
            <h4 class="text-sm font-semibold text-success-800 dark:text-success-200 mb-1 flex items-center">
                🎉 Auction Winner
              </h4>
              <p class="text-sm text-success-700 dark:text-success-300">
                {bids[0]?.bidder_info?.name || 'Anonymous'} won with {formatCurrency(bids[0]?.amount || 0)}
              </p>
            </div>
          {/if}
        </div>
      {/if}
      
      <!-- Current Bid Display -->
      <div class="border-t border-gray-200 dark:border-gray-700 pt-4 mb-4">
        <div class="text-center">
          <div class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
            {$t('auction.currentBid')}
          </div>
          <div class="text-2xl font-bold text-primary-600 dark:text-primary-400 mb-1">
            {formatCurrency(auction.current_bid || auction.starting_bid)}
          </div>
          <div class="text-sm text-gray-500 dark:text-gray-400">
            {$t('auction.totalBids')}: {auction.bid_count || bids.length}
          </div>
        </div>
      </div>
      
      <!-- Main Action Button -->
      <div class="space-y-3">
        {#if canBid}
          <Button
            variant="primary"
            class="w-full font-semibold"
            on:click={onOpenBidModal}
            disabled={placingBid}
          >
            {#if placingBid}
              <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            {:else}
              <svg class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            {/if}
            {$t('auction.placeBid')}
          </Button>
          <p class="text-xs text-gray-500 dark:text-gray-400 text-center">
            {$t('auction.minimumBid')}: {formatCurrency(minimumBidAmount)}
          </p>
          
        {:else if canRegister}
          <Button
            variant="secondary" 
            class="w-full font-semibold"
            on:click={onShowRegisterModal}
          >
            <svg class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
            </svg>
            {$t('auction.registerForAuction')}
          </Button>
          
        {:else if auction.status === 'scheduled'}
          {#if isRegistered}
            <div class="bg-success-50 dark:bg-success-900/20 p-3 rounded-lg border border-success-200 dark:border-success-800">
              <div class="flex items-center">
                <svg class="h-4 w-4 text-success-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                </svg>
                <div class="ml-2">
                  <p class="text-sm font-semibold text-success-800 dark:text-success-200">
                    ✅ Registered
                  </p>
                  <p class="text-xs text-success-600 dark:text-success-400">
                    Ready to bid when auction starts
                  </p>
                </div>
              </div>
            </div>
          {:else if user}
            <Button
              variant="secondary"
              class="w-full font-semibold"
              on:click={onShowRegisterModal}
            >
              <svg class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
              </svg>
              {$t('auction.registerForAuction')}
            </Button>
          {:else}
            <Button
              variant="secondary"
              class="w-full font-semibold"
              href="/login?redirect=/auctions/{auction.slug}"
            >
              <svg class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
              </svg>
              {$t('auction.loginToRegister')}
            </Button>
          {/if}
          
        {:else if !user}
          <Button
            variant="primary"
            class="w-full font-semibold"
            href="/login?redirect=/auctions/{auction.slug}"
          >
            <svg class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
            </svg>
            {$t('auction.loginToPlaceBid')}
          </Button>
          
        {:else}
          <Button
            variant="outline"
            class="w-full font-semibold"
            href="/auctions"
          >
            <svg class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            {$t('auctions.backToAuctions')}
          </Button>
        {/if}
      </div>
      
      <!-- Owner Controls -->
      {#if isOwner && isActiveAuction}
        <div class="border-t border-gray-200 dark:border-gray-700 pt-4 mt-4">
          <h3 class="text-base font-semibold text-gray-900 dark:text-white mb-2">
            Owner Controls
          </h3>
          <div class="space-y-2">
            <Button
              variant="outline"
              size="small"
              class="w-full"
              on:click={onShowExtendModal}
            >
              <svg class="w-4 h-4 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Extend Auction
            </Button>
          </div>
        </div>
      {/if}
    </div>
    
    <!-- Property Quick Info Card -->
    {#if property}
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm overflow-hidden">
        <div class="p-4">
          <div class="flex items-center justify-between mb-3">
            <h3 class="text-base font-semibold text-gray-900 dark:text-white">
              {$t('auction.propertyInfo')}
            </h3>
            <a 
              href={`/properties/${property.slug}`} 
              target="_blank"
              class="text-sm font-medium text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 transition-colors"
            >
              {$t('property.viewDetails')}
            </a>
          </div>
          
          <!-- Property Image -->
          <div class="aspect-video bg-gray-200 dark:bg-gray-700 rounded-lg overflow-hidden mb-3">
            {#if property.main_image?.url}
              <img 
                src={property.main_image.url} 
                alt={property.title}
                class="w-full h-full object-cover"
              />
            {:else}
              <div class="flex items-center justify-center h-full">
                <svg class="h-8 w-8 text-gray-400 dark:text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
              </div>
            {/if}
          </div>
          
          <h4 class="font-semibold text-gray-900 dark:text-white mb-3 text-sm">
            {property.title}
          </h4>
          
          <!-- Property Details -->
          <dl class="space-y-2 text-sm">
            <div class="flex justify-between items-center">
              <dt class="font-medium text-gray-500 dark:text-gray-400">{$t('property.location')}</dt>
              <dd class="font-semibold text-gray-900 dark:text-white text-right">{property.location?.city}, {property.location?.state}</dd>
            </div>
            <div class="flex justify-between items-center">
              <dt class="font-medium text-gray-500 dark:text-gray-400">{$t('property.propertyType')}</dt>
              <dd class="font-semibold text-gray-900 dark:text-white">{property.property_type_display}</dd>
            </div>
            <div class="flex justify-between items-center">
              <dt class="font-medium text-gray-500 dark:text-gray-400">{$t('property.size')}</dt>
              <dd class="font-semibold text-gray-900 dark:text-white">{property.size_sqm} {$t('property.sqm')}</dd>
            </div>
            <div class="flex justify-between items-center">
              <dt class="font-medium text-gray-500 dark:text-gray-400">{$t('property.marketValue')}</dt>
              <dd class="font-semibold text-success-600 dark:text-success-400">{formatCurrency(property.market_value)}</dd>
            </div>
          </dl>
        </div>
      </div>
    {/if}
    
    <!-- Recent Activity Card -->
    {#if bids.length > 0}
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-4">
        <div class="flex items-center justify-between mb-3">
          <h3 class="text-base font-semibold text-gray-900 dark:text-white">
            {$t('auction.recentActivity')}
          </h3>
          <span class="text-sm text-gray-500 dark:text-gray-400">
            Latest 3
          </span>
        </div>
        
        <div class="space-y-2">
          {#each bids.slice(0, 3) as bid}
            <div class="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <div class="flex-1 min-w-0">
                <p class="text-sm font-semibold text-gray-900 dark:text-white">
                  {formatCurrency(bid.amount)}
                </p>
                <p class="text-xs text-gray-500 dark:text-gray-400 truncate">
                  {bid.bidder_info?.name || 'Anonymous'}
                  {#if bid.bidder_info?.id === user?.id}
                    <span class="text-primary-600 dark:text-primary-400 font-medium">({$t('auction.you')})</span>
                  {/if}
                </p>
              </div>
              <div class="text-right flex-shrink-0 ml-2">
                <p class="text-xs text-gray-500 dark:text-gray-400">
                  {getTimeAgo(bid.bid_time)}
                </p>
                <AuctionStatus status={bid.status} isCompact={true} />
              </div>
            </div>
          {/each}
          
          <Button
            variant="outline"
            size="small"
            on:click={() => activeTab = 'bids'}
            class="w-full mt-2"
          >
            {$t('auction.viewAllBids')} ({bids.length})
          </Button>
        </div>
      </div>
    {/if}
    
    <!-- Help Card -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-4">
      <h3 class="text-base font-semibold text-gray-900 dark:text-white mb-2">
        {$t('auction.needHelp')}
      </h3>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-3">
        Questions about this auction? Contact support.
      </p>
      <Button
        variant="outline"
        size="small"
        class="w-full"
        href="/contact?subject=Auction%20{auction.id}"
      >
        <svg class="w-4 h-4 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
        </svg>
        {$t('auction.contactSupport')}
      </Button>
    </div>