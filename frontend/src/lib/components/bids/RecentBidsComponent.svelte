<!-- src/lib/components/bids/RecentBidsComponent.svelte -->
<script>
  import { onMount } from 'svelte';
  import { api } from '$lib/api';
  import { bidStore } from '$lib/stores/bidStore';
  import Button from '$lib/components/ui/Button.svelte';
  import Spinner from '$lib/components/ui/Spinner.svelte';
  import Alert from '$lib/components/ui/Alert.svelte';
  import { formatCurrency, formatDate } from '$lib/utils/formatters';
  
  // Props
  export let title = "Recent Bids";
  export let viewAllLink = "/user/bids"; // Fixed URL to match correct backend endpoint
  export let viewAllLabel = "View All Bids";
  export let limit = 5;
  export let showHeader = true;
  export let userId = null; // Optional: specific user's bids
  export let auctionId = null; // Optional: specific auction's bids
  export let compact = false; // Compact display mode
  export let passedBids = null; // Optional: bids passed directly from parent component

  // State variables
  let loading = true;
  let error = null;
  let bids = [];
  
  // Safe currency formatting function
  function safeCurrency(value, currency = 'USD') {
    if (value === undefined || value === null) return formatCurrency(0, currency);
    
    // Ensure the value is a proper number
    const numValue = typeof value === 'string' ? parseFloat(value) : value;
    if (isNaN(numValue)) return formatCurrency(0, currency);
    
    return formatCurrency(numValue, currency);
  }
  
  // Load bids from API or store
  async function loadBids() {
    // If bids are passed directly from parent, use those
    if (passedBids && Array.isArray(passedBids) && passedBids.length > 0) {
      console.log('Using bids passed from parent:', passedBids.length);
      bids = passedBids.slice(0, limit);
      loading = false;
      return;
    }
    
    try {
      loading = true;
      error = null;
      console.log('Loading bids with parameters:', { userId, auctionId, limit });
      
      // Prepare filter parameters
      const params = {
        limit,
        sort_by: 'created_at',
        direction: 'desc'
      };
      
      // Add filters if provided
      if (userId) params.bidder = userId;
      if (auctionId) params.auction = auctionId;
      
      // If showing user's own bids, use the bidStore
      if (!userId && !auctionId && bidStore) {
        try {
          console.log('Attempting to load bids from bidStore');
          await bidStore.loadUserBids(params);
          
          if (typeof bidStore.getUserBids === 'function') {
            console.log('Using bidStore.getUserBids method');
            const userBids = bidStore.getUserBids();
            bids = Array.isArray(userBids) ? userBids.slice(0, limit) : [];
          } else {
            console.log('Direct access to bidStore.userBids');
            // Fall back to direct access if getUserBids method isn't available
            const userBids = bidStore.userBids || [];
            bids = Array.isArray(userBids) ? userBids.slice(0, limit) : [];
          }
          
          console.log(`Loaded ${bids.length} bids from bidStore`);
        } catch (err) {
          console.error('Error loading bids from store:', err);
          // Fall back to direct API call if store method fails
          console.log('Falling back to direct API call');
          const response = await api.bid.listUserBids({ params });
          bids = response?.results || [];
          console.log(`Loaded ${bids.length} bids via direct API call`);
        }
      } else {
        // For specific users or auctions, make a direct API call
        let response;
        
        try {
          if (auctionId) {
            // Fetch bids for a specific auction
            console.log(`Fetching bids for auction ${auctionId}`);
            response = await api.auction.listBids(auctionId, { params });
          } else {
            // Fetch user bids - uses the correct endpoint
            console.log('Fetching user bids via API');
            response = await api.bid.listUserBids({ params });
          }
          
          if (response && response.results) {
            bids = response.results;
            console.log(`Loaded ${bids.length} bids via API`);
          } else {
            bids = [];
            console.log('No bids found in API response');
          }
        } catch (err) {
          console.error('API call failed:', err);
          bids = [];
          throw err; // Rethrow to be caught by the outer try/catch
        }
      }
      
      loading = false;
    } catch (err) {
      console.error('Error loading bids:', err);
      error = err.error || 'Failed to load recent bids';
      loading = false;
    }
  }
  
  // External refresh method - can be called by parent components
  export function refresh() {
    console.log('Refresh requested by parent component');
    loadBids();
  }
  
  // Get bid status badge style
  function getBidStatusClass(bid) {
    if (!bid?.auction_details) return 'bg-gray-100 text-gray-800';
    
    // Convert values to numbers for safe comparison
    const bidAmount = parseFloat(bid.amount) || 0;
    const currentPrice = parseFloat(bid.auction_details.current_price) || 0;
    
    const isHighestBidder = Math.abs(bidAmount - currentPrice) < 0.01; // Allow for floating point imprecision
    const isActive = bid.auction_details.status === 'ACTIVE';
    const hasEnded = new Date(bid.auction_details.end_time) < new Date();
    
    if (isActive) {
      if (isHighestBidder) {
        return 'bg-green-100 text-green-800'; // Winning
      } else {
        return 'bg-yellow-100 text-yellow-800'; // Outbid
      }
    } else if (hasEnded) {
      if (isHighestBidder) {
        return 'bg-blue-100 text-blue-800'; // Won
      } else {
        return 'bg-red-100 text-red-800'; // Lost
      }
    }
    
    return 'bg-gray-100 text-gray-800';
  }
  
  // Get bid status text
  function getBidStatus(bid) {
    if (!bid?.auction_details) return 'Unknown';
    
    // Convert values to numbers for safe comparison
    const bidAmount = parseFloat(bid.amount) || 0;
    const currentPrice = parseFloat(bid.auction_details.current_price) || 0;
    
    const isHighestBidder = Math.abs(bidAmount - currentPrice) < 0.01; // Allow for floating point imprecision
    const isActive = bid.auction_details.status === 'ACTIVE';
    const hasEnded = new Date(bid.auction_details.end_time) < new Date();
    
    if (isActive) {
      if (isHighestBidder) {
        return 'Winning';
      } else {
        return 'Outbid';
      }
    } else if (hasEnded) {
      if (isHighestBidder) {
        return 'Won';
      } else {
        return 'Lost';
      }
    }
    
    return 'Unknown';
  }
  
  // Watch for changes to passedBids
  $: if (passedBids && Array.isArray(passedBids)) {
    bids = passedBids.slice(0, limit);
    loading = false;
  }
  
  onMount(() => {
    console.log('RecentBidsComponent mounted');
    loadBids();
  });
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
        on:click={loadBids}
      >
        Try Again
      </button>
    </div>
  </Alert>
{:else if !bids || bids.length === 0}
  <div class="text-center py-4 text-text-medium bg-neutral-50 rounded-md">
    <p>No bids found</p>
  </div>
{:else if compact}
  <!-- Compact View -->
  <div class="space-y-2">
    {#each bids as bid}
      <div class="flex justify-between items-center p-3 bg-white border border-primary-blue/10 rounded-lg hover:bg-primary-blue/5 transition-colors">
        <div>
          <div class="font-medium text-text-dark">
            {bid.auction_details?.title || `Auction #${bid.auction}`}
          </div>
          <div class="text-sm text-text-medium">
            {formatDate(bid.created_at)}
          </div>
        </div>
        <div class="text-right">
          <div class="font-medium text-secondary-blue">
            {safeCurrency(bid.amount, bid.auction_details?.currency || 'USD')}
          </div>
          <div class="mt-1">
            <span class="px-2 py-0.5 rounded-full text-xs font-medium {getBidStatusClass(bid)}">
              {getBidStatus(bid)}
            </span>
          </div>
        </div>
      </div>
    {/each}
  </div>
{:else}
  <!-- Full View -->
  <div class="overflow-x-auto border border-primary-blue/10 rounded-lg">
    <table class="min-w-full divide-y divide-primary-blue/10">
      <thead class="bg-primary-blue/5">
        <tr>
          <th scope="col" class="px-4 py-3 text-left text-xs font-medium text-text-medium tracking-wider">
            Auction
          </th>
          <th scope="col" class="px-4 py-3 text-left text-xs font-medium text-text-medium tracking-wider">
            Bid Amount
          </th>
          <th scope="col" class="px-4 py-3 text-left text-xs font-medium text-text-medium tracking-wider">
            Date
          </th>
          <th scope="col" class="px-4 py-3 text-left text-xs font-medium text-text-medium tracking-wider">
            Status
          </th>
          <th scope="col" class="px-4 py-3 text-right text-xs font-medium text-text-medium tracking-wider">
            Actions
          </th>
        </tr>
      </thead>
      <tbody class="bg-white divide-y divide-primary-blue/10">
        {#each bids as bid}
          <tr class="hover:bg-neutral-50">
            <td class="px-4 py-3 whitespace-nowrap">
              <a 
                href="/auctions/{bid.auction}" 
                class="text-sm font-medium text-text-dark hover:text-secondary-blue"
              >
                {bid.auction_details?.title || `Auction #${bid.auction}`}
              </a>
            </td>
            <td class="px-4 py-3 whitespace-nowrap">
              <span class="text-sm font-medium text-secondary-blue">
                {safeCurrency(bid.amount, bid.auction_details?.currency || 'USD')}
              </span>
              {#if bid.auto_bid_limit}
                <div class="text-xs text-text-medium">
                  Auto up to {safeCurrency(bid.auto_bid_limit, bid.auction_details?.currency || 'USD')}
                </div>
              {/if}
            </td>
            <td class="px-4 py-3 whitespace-nowrap text-sm text-text-medium">
              {formatDate(bid.created_at)}
            </td>
            <td class="px-4 py-3 whitespace-nowrap">
              <span class="px-2 inline-flex text-xs leading-5 font-medium rounded-full {getBidStatusClass(bid)}">
                {getBidStatus(bid)}
              </span>
            </td>
            <td class="px-4 py-3 whitespace-nowrap text-right text-sm font-medium">
              <a 
                href="/auctions/{bid.auction}" 
                class="inline-flex items-center px-2.5 py-1.5 border border-gray-300 text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-blue"
              >
                View
              </a>
              
              {#if getBidStatus(bid) === 'Outbid' && bid.auction_details?.status === 'ACTIVE'}
                <a 
                  href={`/auctions/${bid.auction}/bid`} 
                  class="ml-2 inline-flex items-center px-2.5 py-1.5 border border-transparent text-xs font-medium rounded shadow-sm text-white bg-primary-blue hover:bg-primary-blue/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-blue"
                >
                  Bid Again
                </a>
              {/if}
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
{/if}