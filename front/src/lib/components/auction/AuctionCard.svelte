<!-- src/lib/components/auction/AuctionCard.svelte -->
<script>
  import { t } from '$lib/i18n';
  import { onMount, onDestroy } from 'svelte';
  import { getAuctionStatus } from '$lib/api/auction';
  
  export let auction;
  export let enhanced = false;
  
  let timeRemaining = { days: 0, hours: 0, minutes: 0, seconds: 0 };
  let interval;
  let statusInfo = null;
  let loading = false;
  
  // Enhanced auction state
  $: isLive = auction?.status === 'live';
  $: isScheduled = auction?.status === 'scheduled';
  $: isEnded = auction?.status === 'ended' || auction?.status === 'completed';
  $: isActive = isLive || isScheduled;
  
  function updateTimeRemaining() {
    if (!auction?.end_date) {
      timeRemaining = { days: 0, hours: 0, minutes: 0, seconds: 0 };
      return;
    }
    
    const endDate = new Date(auction.end_date);
    const startDate = new Date(auction.start_date);
    const now = new Date();
    
    const targetDate = isScheduled ? startDate : endDate;
    const diff = targetDate - now;
    
    if (diff <= 0) {
      timeRemaining = { days: 0, hours: 0, minutes: 0, seconds: 0 };
      if (isScheduled && now >= startDate) {
        refreshAuctionStatus();
      }
      clearInterval(interval);
      return;
    }
    
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((diff % (1000 * 60)) / 1000);
    
    timeRemaining = { days, hours, minutes, seconds };
  }
  
  async function refreshAuctionStatus() {
    if (!auction?.id || loading) return;
    
    try {
      loading = true;
      const newStatusInfo = await getAuctionStatus(auction.id);
      
      auction = {
        ...auction,
        status: newStatusInfo.status,
        current_bid: newStatusInfo.current_bid,
        is_biddable: newStatusInfo.is_biddable,
        is_active: newStatusInfo.is_active,
        time_remaining: newStatusInfo.time_remaining
      };
      
      statusInfo = newStatusInfo;
      updateTimeRemaining();
      
    } catch (error) {
      console.error('Failed to refresh auction status:', error);
    } finally {
      loading = false;
    }
  }
  
  onMount(() => {
    updateTimeRemaining();
    interval = setInterval(() => {
      updateTimeRemaining();
    }, 1000);
    
    let statusInterval;
    if (isActive) {
      statusInterval = setInterval(refreshAuctionStatus, 30000);
    }
    
    return () => {
      clearInterval(interval);
      if (statusInterval) clearInterval(statusInterval);
    };
  });
  
  onDestroy(() => {
    if (interval) clearInterval(interval);
  });
  
  function getPropertyImageUrl(property) {
    if (!property) return '/images/auction-placeholder.jpg';
    
    if (property.main_image) {
      if (typeof property.main_image === 'string') {
        return property.main_image;
      }
      if (property.main_image.url) {
        return property.main_image.url;
      }
      if (property.main_image.file) {
        return property.main_image.file;
      }
    }
    
    if (property.media && property.media.length > 0) {
      const firstImage = property.media.find(m => 
        m.media_type === 'image' || 
        (m.url && typeof m.url === 'string')
      );
      
      if (firstImage) {
        return firstImage.url || firstImage.file || '/images/auction-placeholder.jpg';
      }
    }
    
    return '/images/auction-placeholder.jpg';
  }
  
  function getAuctionImage() {
    if (auction.media && auction.media.length > 0) {
      const auctionImage = auction.media.find(m => 
        m.media_type === 'image' || 
        (m.url && typeof m.url === 'string')
      );
      
      if (auctionImage) {
        return auctionImage.url || auctionImage.file;
      }
    }
    
    if (auction.related_property) {
      return getPropertyImageUrl(auction.related_property);
    }
    
    return '/images/auction-placeholder.jpg';
  }
  
  function getStatusBadgeClass(status) {
    const baseClasses = 'inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium';
    
    switch (status) {
      case 'live':
        return `${baseClasses} bg-success-100 text-success-800 dark:bg-success-900 dark:text-success-200`;
      case 'scheduled':
        return `${baseClasses} bg-primary-100 text-primary-800 dark:bg-primary-900 dark:text-primary-200`;
      case 'ended':
        return `${baseClasses} bg-danger-100 text-danger-800 dark:bg-danger-900 dark:text-danger-200`;
      case 'completed':
        return `${baseClasses} bg-secondary-100 text-secondary-800 dark:bg-secondary-900 dark:text-secondary-200`;
      case 'cancelled':
        return `${baseClasses} bg-neutral-100 text-neutral-800 dark:bg-neutral-700 dark:text-neutral-200`;
      default:
        return `${baseClasses} bg-neutral-100 text-neutral-800 dark:bg-neutral-700 dark:text-neutral-200`;
    }
  }
  
  function getStatusText(status) {
    switch (status) {
      case 'live':
        return $t('auction.statusLive');
      case 'scheduled':
        return $t('auction.statusScheduled');
      case 'ended':
        return $t('auction.statusEnded');
      case 'completed':
        return $t('auction.statusCompleted');
      case 'cancelled':
        return $t('auction.statusCancelled');
      default:
        return $t('auction.statusDraft');
    }
  }
  
  function formatCurrency(amount) {
    if (!amount) return '$0';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  }
</script>

<a 
  href={`/auctions/${auction.slug}`} 
  class="block h-full group transform transition-all duration-300 hover:scale-[1.02] hover:shadow-xl"
>
  <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden transition-all duration-300 hover:shadow-2xl h-full flex flex-col border border-neutral-200 dark:border-neutral-700">
    
    <!-- Image Section -->
    <div class="relative h-48 overflow-hidden">
      <img 
        src={getAuctionImage()} 
        alt={auction.title}
        class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
        loading="lazy"
      />
      
      <!-- Status Badge -->
      <div class="absolute top-3 right-3">
        <span class={getStatusBadgeClass(auction.status)}>
          {#if isLive}
            <span class="w-2 h-2 bg-success-500 rounded-full mr-1.5 animate-pulse"></span>
          {:else if isScheduled}
            <span class="w-2 h-2 bg-primary-500 rounded-full mr-1.5"></span>
          {:else if isEnded}
            <span class="w-2 h-2 bg-danger-500 rounded-full mr-1.5"></span>
          {/if}
          {getStatusText(auction.status)}
        </span>
      </div>
      
      <!-- Featured Badge -->
      {#if auction.is_featured}
        <div class="absolute top-3 left-3">
          <span class="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium bg-warning-100 text-warning-800 dark:bg-warning-900 dark:text-warning-200">
            ⭐ {$t('auction.featured')}
          </span>
        </div>
      {/if}
      
      <!-- Live Indicator for Enhanced Mode -->
      {#if enhanced && isLive && !auction.is_featured}
        <div class="absolute top-3 left-3">
          <div class="flex items-center space-x-1 bg-danger-500 text-white px-2 py-1 rounded-full text-xs font-bold">
            <span class="w-2 h-2 bg-white rounded-full animate-pulse"></span>
            <span>LIVE</span>
          </div>
        </div>
      {/if}
      
      <!-- Image Overlay with Title -->
      <div class="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent">
        <div class="absolute bottom-0 left-0 right-0 p-4">
          <h3 class="text-lg font-bold text-white line-clamp-2 group-hover:text-primary-300 transition-colors">
            {auction.title}
          </h3>
          <p class="text-sm text-gray-200 truncate mt-1">
            {auction.related_property?.location?.city || ''}{auction.related_property?.location?.state ? `, ${auction.related_property.location.state}` : ''}
          </p>
        </div>
      </div>
    </div>
    
    <!-- Content Section -->
    <div class="p-4 flex-grow flex flex-col">
      
      <!-- Auction Type Badge -->
      <div class="mb-4">
        <span class="inline-block bg-neutral-100 dark:bg-neutral-700 rounded-full px-3 py-1 text-sm font-medium text-neutral-700 dark:text-neutral-300">
          {auction.auction_type === 'sealed' ? $t('auction.typeSealed') :
           auction.auction_type === 'private' ? $t('auction.typeReserve') :
           $t('auction.typeNoReserve')}
        </span>
      </div>
      
      <!-- Current Bid Section -->
      <div class="mb-4 flex-grow">
        <div class="flex items-baseline justify-between mb-2">
          <p class="text-sm text-neutral-500 dark:text-neutral-400">
            {auction.current_bid ? $t('auction.currentBid') : $t('auction.startingBid')}
          </p>
          {#if isLive}
            <span class="text-xs text-success-600 dark:text-success-400 font-medium animate-pulse">
              • {$t('auction.live')}
            </span>
          {/if}
        </div>
        <p class="text-2xl font-bold text-gray-900 dark:text-white group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
          {formatCurrency(auction.current_bid || auction.starting_bid)}
        </p>
        
        {#if auction.bid_count > 0}
          <p class="text-sm text-neutral-500 dark:text-neutral-400 mt-1">
            {auction.bid_count} {auction.bid_count === 1 ? 'bid' : 'bids'}
          </p>
        {/if}
      </div>
      
      <!-- Time Remaining Section -->
      {#if isActive}
        <div class="bg-gradient-to-r from-primary-50 to-secondary-50 dark:from-primary-900/20 dark:to-secondary-900/20 rounded-lg p-3 border border-primary-200 dark:border-primary-800">
          <p class="text-xs text-center text-primary-700 dark:text-primary-300 mb-2 font-medium">
            {isLive ? $t('auction.timeRemaining') : $t('auction.startsIn')}
          </p>
          <div class="grid grid-cols-4 gap-1 text-center">
            <div>
              <span class="block text-lg font-bold text-primary-800 dark:text-primary-200">
                {timeRemaining.days}
              </span>
              <span class="text-xs text-primary-600 dark:text-primary-400">
                {$t('auction.days')}
              </span>
            </div>
            <div>
              <span class="block text-lg font-bold text-primary-800 dark:text-primary-200">
                {timeRemaining.hours}
              </span>
              <span class="text-xs text-primary-600 dark:text-primary-400">
                {$t('auction.hours')}
              </span>
            </div>
            <div>
              <span class="block text-lg font-bold text-primary-800 dark:text-primary-200">
                {timeRemaining.minutes}
              </span>
              <span class="text-xs text-primary-600 dark:text-primary-400">
                {$t('auction.minutes')}
              </span>
            </div>
            <div>
              <span class="block text-lg font-bold text-primary-800 dark:text-primary-200">
                {timeRemaining.seconds}
              </span>
              <span class="text-xs text-primary-600 dark:text-primary-400">
                {$t('auction.seconds')}
              </span>
            </div>
          </div>
          
          <!-- Enhanced Live Auction Indicator -->
          {#if isLive && enhanced}
            <div class="mt-2 pt-2 border-t border-primary-200 dark:border-primary-700">
              <div class="flex items-center justify-center space-x-1 text-xs">
                <div class="w-2 h-2 bg-danger-500 rounded-full animate-pulse"></div>
                <span class="text-danger-600 dark:text-danger-400 font-bold">
                  {$t('auction.biddingActive')}
                </span>
              </div>
            </div>
          {/if}
        </div>
      {:else if isEnded}
        <!-- Ended Auction Info -->
        <div class="bg-neutral-50 dark:bg-neutral-700 rounded-lg p-3">
          <p class="text-sm text-center text-neutral-600 dark:text-neutral-400 mb-1">
            {$t('auction.auctionEnded')}
          </p>
          {#if auction.status === 'completed' && auction.bid_count > 0}
            <p class="text-xs text-center text-success-600 dark:text-success-400 font-medium">
              🎉 {$t('auction.soldSuccessfully')}
            </p>
          {:else if auction.bid_count === 0}
            <p class="text-xs text-center text-neutral-500 dark:text-neutral-400">
              {$t('auction.noBidsReceived')}
            </p>
          {/if}
        </div>
      {/if}
    </div>
    
    <!-- Footer Section -->
    <div class="border-t border-neutral-200 dark:border-neutral-700 p-4 bg-neutral-50 dark:bg-neutral-900/50">
      <div class="flex items-center justify-between">
        <!-- Auction Stats -->
        <div class="flex items-center space-x-4 text-sm text-neutral-500 dark:text-neutral-400">
          <div class="flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8h2a2 2 0 012 2v6a2 2 0 01-2 2h-2v4l-4-4H9a1.994 1.994 0 01-1.414-.586m0 0L11 14h4a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2v4l.586-.586z" />
            </svg>
            <span>{auction.bid_count || 0}</span>
          </div>
          
          <div class="flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
            <span>{auction.view_count || 0}</span>
          </div>
        </div>
        
        <!-- Action Button/Link -->
        <div class="flex items-center text-sm text-primary-600 dark:text-primary-400 font-medium group-hover:text-primary-700 dark:group-hover:text-primary-300 transition-colors">
          {#if isLive}
            <span class="font-bold">
              {$t('auction.bidNow')}
            </span>
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 ml-1 transform group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          {:else if isScheduled}
            <span>{$t('auction.register')}</span>
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 ml-1 transform group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
            </svg>
          {:else}
            <span>{$t('auction.viewDetails')}</span>
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 ml-1 transform group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          {/if}
        </div>
      </div>
      
      <!-- Enhanced Enhanced Mode Footer -->
      {#if enhanced}
        <div class="mt-3 pt-3 border-t border-neutral-200 dark:border-neutral-600">
          <div class="flex items-center justify-between text-xs">
            <span class="text-neutral-500 dark:text-neutral-400">
              ID: #{auction.id}
            </span>
            {#if loading}
              <div class="flex items-center text-primary-500">
                <div class="animate-spin rounded-full h-3 w-3 border-b-2 border-primary-500 mr-1"></div>
                <span>Updating...</span>
              </div>
            {:else if statusInfo}
              <span class="text-success-600 dark:text-success-400">
                ✓ Live Data
              </span>
            {/if}
          </div>
        </div>
      {/if}
    </div>
  </div>
</a>

<style>
  .line-clamp-2 {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
</style>