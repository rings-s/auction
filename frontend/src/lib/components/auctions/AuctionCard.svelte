<!-- src/lib/components/auctions/AuctionCard.svelte -->
<script>
  import { onMount, onDestroy } from 'svelte';
  import { t, language } from '$lib/i18n';
  
  // Props
  export let auction = {
    id: '',
    uuid: '',
    title: '',
    status: 'active',
    status_display: '',
    start_date: '',
    end_date: '',
    current_bid: 0,
    starting_price: 0,
    min_bid_increment: 0,
    bid_count: 0,
    time_remaining: 0,
    featured_image_url: '',
    property_title: '',
    property_type: '',
    property_type_display: '',
    is_featured: false
  };
  
  // State
  let timeLeft = auction.time_remaining || 0;
  let days = 0;
  let hours = 0;
  let minutes = 0;
  let seconds = 0;
  let intervalId;
  
  // Derived values
  $: isActive = auction.status === 'active';
  $: isPending = auction.status === 'pending';
  $: isEnded = ['closed', 'sold', 'cancelled'].includes(auction.status);
  
  // Format currency using Intl
  function formatCurrency(amount) {
    return new Intl.NumberFormat($language === 'ar' ? 'ar-SA' : 'en-US', {
      style: 'currency',
      currency: 'SAR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  }
  
  // Update countdown timer
  function updateTimer() {
    if (timeLeft <= 0) {
      clearInterval(intervalId);
      isActive = false;
      isEnded = true;
      return;
    }
    
    days = Math.floor(timeLeft / (60 * 60 * 24));
    hours = Math.floor((timeLeft % (60 * 60 * 24)) / (60 * 60));
    minutes = Math.floor((timeLeft % (60 * 60)) / 60);
    seconds = Math.floor(timeLeft % 60);
    
    timeLeft--;
  }
  
  // Get color class based on auction status
  function getStatusColor(status) {
    const colors = {
      'active': 'bg-success text-white',
      'pending': 'bg-warning text-white',
      'extended': 'bg-info text-white',
      'closed': 'bg-neutral-500 text-white',
      'sold': 'bg-accent text-white',
      'cancelled': 'bg-error text-white'
    };
    
    return colors[status] || 'bg-neutral-500 text-white';
  }
  
  // Get time display format
  function getTimeDisplay() {
    if (isEnded) {
      return $t('auctions.ended');
    }
    
    if (isPending) {
      return $t('auctions.starts_in');
    }
    
    if (days > 0) {
      return `${days} ${$t('auctions.days')}`;
    }
    
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
  }
  
  // Default image if none provided
  const fallbackImage = '/images/placeholders/auction-placeholder.jpg';
  
  onMount(() => {
    // Start countdown timer
    updateTimer();
    intervalId = setInterval(updateTimer, 1000);
  });
  
  onDestroy(() => {
    // Clean up timer on component destroy
    if (intervalId) clearInterval(intervalId);
  });
</script>

<a
  href={`/auctions/${auction.id}`}
  class="group relative flex flex-col w-full overflow-hidden rounded-xl bg-surface-light dark:bg-surface-dark backdrop-blur-md transition-all duration-300 hover:-translate-y-1 hover:shadow-glass {auction.is_featured ? 'ring-2 ring-primary ring-opacity-60' : ''}"
>
  <!-- Auction Image -->
  <div class="relative aspect-[4/3] w-full overflow-hidden rounded-t-xl">
    <img
      src={auction.featured_image_url || fallbackImage}
      alt={auction.title}
      class="h-full w-full object-cover transition-transform duration-700 group-hover:scale-105"
      loading="lazy"
    />
    
    <!-- Property Type Badge -->
    <div class="absolute top-3 {$language === 'ar' ? 'right-3' : 'left-3'} z-10">
      <span class="rounded-full bg-primary-600 bg-opacity-80 px-3 py-1 text-xs font-medium text-white backdrop-blur-sm">
        {auction.property_type_display || $t(`properties.types.${auction.property_type}`)}
      </span>
    </div>
    
    <!-- Featured Badge -->
    {#if auction.is_featured}
      <div class="absolute top-3 {$language === 'ar' ? 'left-3' : 'right-3'} z-10">
        <span class="rounded-full bg-accent px-3 py-1 text-xs font-medium text-white">
          {$t('general.featured')}
        </span>
      </div>
    {/if}
    
    <!-- Timer Overlay -->
    <div class="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-neutral-900 to-transparent p-4">
      <div class="flex items-center justify-between">
        <div>
          <span class={`rounded-full px-3 py-1 text-xs font-medium ${getStatusColor(auction.status)}`}>
            {auction.status_display || $t(`auctions.status.${auction.status}`)}
          </span>
        </div>
        
        <div class="rounded-full bg-neutral-900 bg-opacity-60 px-3 py-1 backdrop-blur-sm">
          <span class="text-xs font-mono font-medium {isEnded ? 'text-error' : isActive ? 'text-success' : 'text-warning'}">
            {isActive ? $t('auctions.ends_in') : isPending ? $t('auctions.starts_in') : ''} {getTimeDisplay()}
          </span>
        </div>
      </div>
    </div>
  </div>
  
  <!-- Auction Info -->
  <div class="flex flex-col flex-grow p-4">
    <h3 class="mb-2 text-lg font-bold text-neutral-900 dark:text-neutral-50 group-hover:text-primary line-clamp-2">
      {auction.title}
    </h3>
    
    <p class="mb-3 text-sm text-neutral-600 dark:text-neutral-300 line-clamp-1">
      {auction.property_title}
    </p>
    
    <!-- Bid Info -->
    <div class="mb-4 flex flex-wrap justify-between gap-3 mt-auto">
      <!-- Current Bid -->
      <div>
        <p class="text-xs text-neutral-500 dark:text-neutral-400">
          {$t('auctions.current_bid')}
        </p>
        <p class="text-lg font-bold text-primary-600 dark:text-primary-400">
          {formatCurrency(auction.current_bid)}
        </p>
      </div>
      
      <!-- Bid Count -->
      <div class="text-right">
        <p class="text-xs text-neutral-500 dark:text-neutral-400">
          {$t('auctions.bid_count')}
        </p>
        <p class="text-lg font-bold text-neutral-800 dark:text-neutral-200">
          {auction.bid_count}
        </p>
      </div>
    </div>
    
    <!-- Bid Button Row -->
    <div class="flex items-center justify-between mt-auto">
      <span class="text-sm text-neutral-500 dark:text-neutral-400">
        {$t('auctions.min_increment')}: {formatCurrency(auction.min_bid_increment)}
      </span>
      
      <span class="rounded-full bg-primary-50 dark:bg-primary-900/30 px-4 py-2 text-sm font-medium text-primary-600 dark:text-primary-400 transition group-hover:bg-primary group-hover:text-white">
        {isActive ? $t('auctions.bid_now') : $t('general.view')}
      </span>
    </div>
  </div>
</a>