<!-- src/lib/components/dashboard/RecentAuctionsDashboard.svelte -->
<script>
    import { onMount } from 'svelte';
    import { api } from '$lib/api';
    import { formatCurrency, formatDate } from '$lib/utils/formatters';
    import Spinner from '$lib/components/ui/Spinner.svelte';
    import Alert from '$lib/components/ui/Alert.svelte';
    
    // Props
    export let title = "Recent Auctions";
    export let viewAllLink = "/auctions";
    export let viewAllLabel = "View All Auctions";
    export let limit = 5;
    export let showHeader = true;
    export let isSellerView = false; // To show seller-specific data
    
    // State variables
    let auctions = [];
    let loading = true;
    let error = null;
    
    // Load auctions
    async function loadAuctions() {
      try {
        loading = true;
        error = null;
        
        // Prepare API parameters
        const params = {
          page_size: limit,
          sort_by: 'created_at',
          direction: 'desc'
        };
        
        // If viewing as a seller, filter to only show user's auctions
        if (isSellerView) {
          params.seller = 'current';
        } else {
          params.status = 'ACTIVE';
        }
        
        // Call API
        const response = await api.auction.list({ params });
        auctions = response.results || [];
        
        loading = false;
      } catch (err) {
        console.error('Error loading auctions:', err);
        error = 'Failed to load recent auctions';
        loading = false;
      }
    }
    
    // Get badge variant based on status
    function getStatusBadge(status) {
      switch (status) {
        case 'ACTIVE':
          return 'success';
        case 'ENDED':
          return 'info';
        case 'CANCELLED':
          return 'error';
        case 'DRAFT':
          return 'warning';
        default:
          return 'default';
      }
    }
    
    // Initialize on mount
    onMount(() => {
      loadAuctions();
    });
    
    // Format end time
    function formatEndTimeRelative(endTime) {
      if (!endTime) return 'No end date';
      
      const endDate = new Date(endTime);
      const now = new Date();
      
      // Check if auction has ended
      if (endDate < now) {
        return 'Ended';
      }
      
      // Calculate difference in days
      const diffTime = Math.abs(endDate - now);
      const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
      
      if (diffDays > 0) {
        return `${diffDays} day${diffDays > 1 ? 's' : ''} left`;
      }
      
      // Calculate hours and minutes
      const diffHours = Math.floor((diffTime % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
      const diffMinutes = Math.floor((diffTime % (1000 * 60 * 60)) / (1000 * 60));
      
      if (diffHours > 0) {
        return `${diffHours} hour${diffHours > 1 ? 's' : ''} left`;
      }
      
      return `${diffMinutes} minute${diffMinutes > 1 ? 's' : ''} left`;
    }
  </script>
  
  {#if showHeader}
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-medium text-text-dark">{title}</h3>
      <a 
        href={viewAllLink} 
        class="inline-flex items-center justify-center px-3 py-1.5 border border-primary-blue text-xs font-medium rounded text-primary-blue bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-blue"
      >
        {viewAllLabel}
      </a>
    </div>
  {/if}
  
  {#if loading}
    <div class="flex justify-center items-center py-6">
      <Spinner size="md" />
    </div>
  {:else if error}
    <Alert variant="error" class="mb-4">
      {error}
      <div class="mt-2">
        <button 
          class="inline-flex items-center justify-center px-3 py-1.5 border border-primary-blue text-xs font-medium rounded text-primary-blue bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-blue"
          on:click={loadAuctions}
        >
          Try Again
        </button>
      </div>
    </Alert>
  {:else if auctions.length === 0}
    <div class="text-center py-4 text-text-medium bg-neutral-50 rounded-md">
      <p>No auctions found</p>
    </div>
  {:else}
    <div class="divide-y divide-primary-blue/10">
      {#each auctions as auction}
        <div class="py-4">
          <div class="flex justify-between items-start">
            <div>
              <a href="/auctions/{auction.id}" class="font-medium text-text-dark hover:text-primary-blue">
                {auction.title}
              </a>
              <div class="text-sm text-text-medium mt-1">
                {formatDate(auction.created_at)}
              </div>
            </div>
            <div>
              <span class="badge {getStatusBadge(auction.status)}">
                {auction.status}
              </span>
            </div>
          </div>
          <div class="mt-2 flex justify-between items-center">
            <div>
              <span class="font-medium text-secondary-blue">
                {formatCurrency(auction.current_price, auction.currency)}
              </span>
              <span class="text-sm text-text-medium ml-2">
                {auction.bids_count || 0} bid{auction.bids_count !== 1 ? 's' : ''}
              </span>
            </div>
            <div>
              {#if auction.status === 'ACTIVE' && auction.end_time}
                <span class="text-xs bg-primary-blue/10 text-primary-blue px-2 py-1 rounded-full">
                  {formatEndTimeRelative(auction.end_time)}
                </span>
              {/if}
            </div>
          </div>
        </div>
      {/each}
    </div>
  {/if}
  
  <style>
    .badge {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 0.25rem 0.75rem;
      border-radius: 9999px;
      font-size: 0.75rem;
      font-weight: 500;
    }
    
    .badge.success {
      background-color: rgba(16, 185, 129, 0.1);
      color: rgb(16, 185, 129);
    }
    
    .badge.info {
      background-color: rgba(59, 130, 246, 0.1);
      color: rgb(59, 130, 246);
    }
    
    .badge.warning {
      background-color: rgba(245, 158, 11, 0.1);
      color: rgb(245, 158, 11);
    }
    
    .badge.error {
      background-color: rgba(239, 68, 68, 0.1);
      color: rgb(239, 68, 68);
    }
    
    .badge.default {
      background-color: rgba(107, 114, 128, 0.1);
      color: rgb(107, 114, 128);
    }
  </style>