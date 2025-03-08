<!-- src/lib/components/auction/AuctionCard.svelte -->
<script>
  import { onMount } from 'svelte';
  import AuctionTimer from './AuctionTimer.svelte';
  import Button from '$lib/components/ui/Button.svelte';

  // Props
  export let auction = {};
  export let featured = false;
  export let compact = false;

  // Current price and timer
  let currentPrice = auction.current_price || 0;
  let endTime = auction.end_time;
  let isActive = auction.status === 'ACTIVE';
  let totalBids = auction.bids?.length || auction.total_bids || 0;
  let imageLoading = true;
  let imageError = false;

  // Calculate responsive image height based on props
  $: imageHeight = featured ? 'h-52' : compact ? 'h-40' : 'h-48';

  // Get the main image URL with fallback
  $: imageUrl = getImageUrl(auction);

  function getImageUrl(auction) {
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
    
    // Default fallback
    return 'https://via.placeholder.com/400x300?text=No+Image';
  }

  // Format currency
  function formatCurrency(amount, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency || 'USD'
    }).format(amount);
  }

  // Get formatted date
  function formatDate(dateStr) {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    }).format(date);
  }

  // Get status badge style
  function getStatusBadge(status) {
    switch (status) {
      case 'ACTIVE':
        return 'bg-green-100 text-green-800';
      case 'ENDED':
        return 'bg-blue-100 text-blue-800';
      case 'CANCELLED':
        return 'bg-red-100 text-red-800';
      case 'DRAFT':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  }

  // Handle image load error
  function handleImageError() {
    imageError = true;
    imageLoading = false;
  }

  // Handle image load success
  function handleImageLoad() {
    imageLoading = false;
  }

  // Handle auction updates (e.g., from WebSocket)
  function updateAuctionData(data) {
    if (data.current_price) {
      currentPrice = data.current_price;
    }
    if (data.status) {
      isActive = data.status === 'ACTIVE';
    }
    if (data.end_time) {
      endTime = data.end_time;
    }
    if (data.bids) {
      totalBids = data.bids.length;
    } else if (data.total_bids !== undefined) {
      totalBids = data.total_bids;
    }
  }

  // Truncate description to avoid cards with varying heights
  function truncateDescription(text, maxLength = 100) {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  }

  onMount(() => {
    // Could subscribe to WebSocket updates for this auction
  });
</script>

<div 
  class="group bg-white rounded-xl overflow-hidden shadow-sm hover:shadow-md transition-all duration-300 border border-primary-blue/10 flex flex-col h-full {featured ? 'transform hover:-translate-y-1' : ''}"
>
  <!-- Image and Status Badge -->
  <div class="relative {imageHeight} overflow-hidden bg-neutral-50">
    <a href="/auctions/{auction.id}" class="block w-full h-full">
      {#if imageLoading}
        <div class="absolute inset-0 flex items-center justify-center">
          <div class="w-6 h-6 border-2 border-primary-blue/30 border-t-secondary-blue rounded-full animate-spin"></div>
        </div>
      {/if}
      
      <!-- Add loading="lazy" to images in AuctionCard.svelte -->
      <img 
        src={imageUrl} 
        alt={auction.title || "Auction item"}
        class="object-cover w-full h-full transform group-hover:scale-105   transition-transform duration-300 {imageError ? 'opacity-60' : ''}"
        on:error={handleImageError}
        on:load={handleImageLoad}
      loading="lazy"
      />
      
      {#if imageError}
        <div class="absolute inset-0 flex items-center justify-center">
          <span class="text-sm text-gray-500">Image unavailable</span>
        </div>
      {/if}
    </a>
    
    <div class="absolute top-2 right-2">
      <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {getStatusBadge(auction.status)}">
        {auction.status}
      </span>
    </div>
    
    {#if auction.category?.name}
      <div class="absolute top-2 left-2">
        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-blue/20 text-secondary-blue">
          {auction.category.name}
        </span>
      </div>
    {/if}
  </div>

  <!-- Content -->
  <div class="flex-1 p-4 flex flex-col">
    <!-- Title and Price -->
    <div class="mb-2">
      <h3 class="text-lg font-medium text-text-dark group-hover:text-secondary-blue transition-colors">
        <a href="/auctions/{auction.id}" class="hover:underline">
          {auction.title || 'Untitled Auction'}
        </a>
      </h3>
      <div class="flex justify-between items-center mt-1">
        <span class="text-sm text-text-medium">{formatDate(auction.created_at)}</span>
        <span class="text-sm text-text-medium">{totalBids} {totalBids === 1 ? 'bid' : 'bids'}</span>
      </div>
    </div>

    <!-- Description if not compact -->
    {#if !compact}
      <div class="text-sm text-text-medium mb-3 line-clamp-2">
        {truncateDescription(auction.description, 100)}
      </div>
    {/if}

    <!-- Timer and Price -->
    <div class="mt-auto">
      {#if isActive}
        <div class="mb-3">
          <AuctionTimer auction={auction} size={compact ? 'small' : 'normal'} />
        </div>
      {/if}

      <div class="flex justify-between items-end">
        <div>
          <p class="text-xs text-text-medium">Current Bid</p>
          <p class="text-lg font-semibold text-secondary-blue">
            {formatCurrency(currentPrice, auction.currency)}
          </p>
        </div>
        <Button 
          href="/auctions/{auction.id}" 
          variant={featured ? "primary" : "outline"}
          size="sm"
        >
          {isActive ? 'Bid Now' : 'View Details'}
        </Button>
      </div>
    </div>
  </div>
</div>

<style>
  /* Truncate text to 2 lines */
  .line-clamp-2 {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
</style>