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
  let recentBidAnimation = false;
  
  // Enhanced auction state
  $: isLive = auction?.status === 'live';
  $: isScheduled = auction?.status === 'scheduled';
  $: isEnded = auction?.status === 'ended' || auction?.status === 'completed';
  $: isActive = isLive || isScheduled;
  $: hasActiveBidding = isLive && auction.bid_count > 0;
  
  // Calculate bid activity level
  $: bidActivityLevel = getBidActivityLevel();
  
  function getBidActivityLevel() {
    if (!auction?.bid_count) return 'low';
    if (auction.bid_count > 20) return 'hot';
    if (auction.bid_count > 10) return 'active';
    return 'moderate';
  }
  
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
      
      // Check if bid count increased
      if (newStatusInfo.bid_count > auction.bid_count) {
        recentBidAnimation = true;
        setTimeout(() => recentBidAnimation = false, 3000);
      }
      
      auction = {
        ...auction,
        status: newStatusInfo.status,
        current_bid: newStatusInfo.current_bid,
        bid_count: newStatusInfo.bid_count || auction.bid_count,
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
      statusInterval = setInterval(refreshAuctionStatus, 15000); // More frequent updates for active auctions
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
  
  function getTimeRemainingDisplay() {
    if (timeRemaining.days > 0) {
      return `${timeRemaining.days}d ${timeRemaining.hours}h`;
    } else if (timeRemaining.hours > 0) {
      return `${timeRemaining.hours}h ${timeRemaining.minutes}m`;
    } else if (timeRemaining.minutes > 0) {
      return `${timeRemaining.minutes}m ${timeRemaining.seconds}s`;
    } else {
      return `${timeRemaining.seconds}s`;
    }
  }
</script>

<a 
  href={`/auctions/${auction.slug}`} 
  class="block h-full group transform transition-all duration-300 hover:scale-[1.02] hover:shadow-xl"
>
  <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden transition-all duration-300 hover:shadow-2xl h-full flex flex-col border border-neutral-200 dark:border-neutral-700 {hasActiveBidding ? 'ring-2 ring-primary-500 ring-opacity-50' : ''}">
    
    <!-- Image Section with Enhanced Overlays -->
    <div class="relative h-56 overflow-hidden">
      <img 
        src={getAuctionImage()} 
        alt={auction.title}
        class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
        loading="lazy"
      />
      
      <!-- Gradient Overlay -->
      <div class="absolute inset-0 bg-gradient-to-t from-black/70 via-black/20 to-transparent"></div>
      
      <!-- Top Badges Row -->
      <div class="absolute top-3 left-3 right-3 flex items-start justify-between">
        <div class="flex flex-wrap gap-2">
          <!-- Status Badge -->
          <span class={getStatusBadgeClass(auction.status)}>
            {#if isLive}
              <span class="w-2 h-2 bg-success-500 rounded-full mr-1.5 animate-pulse"></span>
            {/if}
            {getStatusText(auction.status)}
          </span>
          
          <!-- Featured Badge -->
          {#if auction.is_featured}
            <span class="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium bg-warning-100 text-warning-800 dark:bg-warning-900 dark:text-warning-200">
              ⭐ {$t('auction.featured')}
            </span>
          {/if}
        </div>
        
        <!-- Bid Activity Indicator -->
        {#if isLive && hasActiveBidding}
          <div class="flex items-center space-x-1">
            {#if bidActivityLevel === 'hot'}
              <span class="bg-red-500 text-white px-2 py-1 rounded-full text-xs font-bold flex items-center">
                🔥 HOT
              </span>
            {:else if recentBidAnimation}
              <span class="bg-green-500 text-white px-2 py-1 rounded-full text-xs font-bold animate-bounce">
                NEW BID!
              </span>
            {/if}
          </div>
        {/if}
      </div>
      
      <!-- Title and Location Overlay -->
      <div class="absolute bottom-0 left-0 right-0 p-4">
        <h3 class="text-xl font-bold text-white line-clamp-2 group-hover:text-primary-300 transition-colors mb-1">
          {auction.title}
        </h3>
        <p class="text-sm text-gray-200 truncate">
          {#if auction.related_property?.location}
            📍 {auction.related_property.location.city || ''}{auction.related_property.location.state ? `, ${auction.related_property.location.state}` : ''}
          {/if}
        </p>
      </div>
    </div>
    
    <!-- Content Section - Focused on Bidding Info -->
    <div class="p-5 flex-grow flex flex-col">
      
      <!-- Auction Type and Quick Stats -->
      <div class="flex items-center justify-between mb-4">
        <span class="inline-block bg-neutral-100 dark:bg-neutral-700 rounded-full px-3 py-1 text-sm font-medium text-neutral-700 dark:text-neutral-300">
          {auction.auction_type === 'sealed' ? '🔒 ' + $t('auction.typeSealed') :
           auction.auction_type === 'private' ? '🏷️ ' + $t('auction.typeReserve') :
           '🎯 ' + $t('auction.typeNoReserve')}
        </span>
        
        <div class="flex items-center space-x-3 text-sm text-neutral-500 dark:text-neutral-400">
          <div class="flex items-center">
            <svg class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8h2a2 2 0 012 2v6a2 2 0 01-2 2h-2v4l-4-4H9a1.994 1.994 0 01-1.414-.586m0 0L11 14h4a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2v4l.586-.586z" />
            </svg>
            <span class="font-medium">{auction.bid_count || 0}</span>
          </div>
          <div class="flex items-center">
            <svg class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
            <span>{auction.view_count || 0}</span>
          </div>
        </div>
      </div>
      
      <!-- Current Bid Section - Enhanced -->
      <div class="mb-4 bg-gradient-to-r from-primary-50 to-secondary-50 dark:from-primary-900/20 dark:to-secondary-900/20 rounded-lg p-4 border border-primary-200 dark:border-primary-800">
        <div class="flex items-baseline justify-between mb-2">
          <p class="text-sm font-medium text-neutral-600 dark:text-neutral-400">
            {auction.current_bid ? $t('auction.currentBid') : $t('auction.startingBid')}
          </p>
          {#if isLive}
            <span class="text-xs text-success-600 dark:text-success-400 font-medium animate-pulse">
              • {$t('auction.acceptingBids')}
            </span>
          {/if}
        </div>
        
        <div class="flex items-end justify-between">
          <div>
            <p class="text-3xl font-bold text-gray-900 dark:text-white group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
              {formatCurrency(auction.current_bid || auction.starting_bid)}
            </p>
            {#if auction.current_bid && auction.minimum_increment}
              <p class="text-xs text-neutral-500 dark:text-neutral-400 mt-1">
                Next min: {formatCurrency((auction.current_bid || auction.starting_bid) + auction.minimum_increment)}
              </p>
            {/if}
          </div>
          
          {#if auction.bid_count > 0 && isLive}
            <div class="text-right">
              <p class="text-xs text-neutral-500 dark:text-neutral-400">
                {auction.bid_count} {auction.bid_count === 1 ? 'bid' : 'bids'}
              </p>
              {#if recentBidAnimation}
                <p class="text-xs text-success-600 dark:text-success-400 font-medium animate-pulse">
                  ↑ New bid!
                </p>
              {/if}
            </div>
          {/if}
        </div>
      </div>
      
      <!-- Time Display - Compact and Clear -->
      {#if isActive}
        <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-3 mb-4">
          <div class="flex items-center justify-between">
            <span class="text-xs font-medium text-neutral-600 dark:text-neutral-400">
              {isLive ? '⏱️ ' + $t('auction.endsIn') : '🕐 ' + $t('auction.startsIn')}
            </span>
            <span class="text-sm font-bold text-primary-800 dark:text-primary-200">
              {getTimeRemainingDisplay()}
            </span>
          </div>
          
          {#if isLive && timeRemaining.hours === 0 && timeRemaining.days === 0}
            <div class="mt-2 text-center">
              <span class="text-xs text-danger-600 dark:text-danger-400 font-medium animate-pulse">
                ⚡ {$t('auction.endingSoon')}
              </span>
            </div>
          {/if}
        </div>
      {:else if isEnded}
        <div class="bg-neutral-50 dark:bg-neutral-700 rounded-lg p-3 mb-4">
          <p class="text-sm text-center text-neutral-600 dark:text-neutral-400">
            {$t('auction.auctionEnded')}
          </p>
          {#if auction.status === 'completed' && auction.bid_count > 0}
            <p class="text-xs text-center text-success-600 dark:text-success-400 font-medium mt-1">
              🎉 {$t('auction.soldSuccessfully')}
            </p>
          {/if}
        </div>
      {/if}
      
      <!-- Quick Property Info -->
      {#if auction.related_property}
        <div class="mt-auto pt-3 border-t border-neutral-200 dark:border-neutral-700">
          <div class="grid grid-cols-2 gap-2 text-xs">
            {#if auction.related_property.property_type_display}
              <div class="flex items-center text-neutral-600 dark:text-neutral-400">
                <svg class="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
                <span>{auction.related_property.property_type_display}</span>
              </div>
            {/if}
            {#if auction.related_property.size_sqm}
              <div class="flex items-center text-neutral-600 dark:text-neutral-400">
                <svg class="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
                </svg>
                <span>{auction.related_property.size_sqm} sqm</span>
              </div>
            {/if}
          </div>
        </div>
      {/if}
    </div>
    
    <!-- Action Footer -->
    <div class="border-t border-neutral-200 dark:border-neutral-700 px-5 py-3 bg-neutral-50 dark:bg-neutral-900/50">
      <div class="flex items-center justify-between">
        <div class="flex items-center text-sm font-medium">
          {#if isLive}
            <span class="text-primary-600 dark:text-primary-400 font-bold flex items-center">
              <svg class="w-4 h-4 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              {$t('auction.bidNow')}
            </span>
          {:else if isScheduled}
            <span class="text-neutral-600 dark:text-neutral-400 flex items-center">
              <svg class="w-4 h-4 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {$t('auction.register')}
            </span>
          {:else}
            <span class="text-neutral-600 dark:text-neutral-400 flex items-center">
              {$t('auction.viewDetails')}
            </span>
          {/if}
        </div>
        
        <svg class="w-5 h-5 text-neutral-400 dark:text-neutral-500 transform group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
      </div>
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