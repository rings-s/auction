<!-- src/routes/auctions/bidding/+page.svelte -->
<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { isAuthenticated, user } from '$lib/stores/authStore';
  import { notificationStore } from '$lib/stores/notificationStore';
  import { bidStore } from '$lib/stores/bidStore';
  import Button from '$lib/components/ui/Button.svelte';
  import Spinner from '$lib/components/ui/Spinner.svelte';
  import Alert from '$lib/components/ui/Alert.svelte';
  import Tabs from '$lib/components/ui/Tabs.svelte';
  import { formatDate, formatCurrency } from '$lib/utils/formatters';
  
  // State variables
  let loading = true;
  let error = null;
  let bids = [];
  let activeBids = [];
  let wonBids = [];
  let outbidBids = [];
  let activeAuctionIds = new Set();
  
  // Filter and sort options
  let sortBy = 'created_at';
  let sortDirection = 'desc';
  let filterStatus = 'all';
  
  // Tabs
  const tabs = [
    { id: 'active', label: 'Active Bids' },
    { id: 'won', label: 'Won Auctions' },
    { id: 'outbid', label: 'Outbid' },
    { id: 'all', label: 'All Bids' }
  ];
  let activeTab = 'active';
  
  // Load all bids for the current user
  async function loadBids() {
    if (!$isAuthenticated) {
      goto('/login');
      return;
    }
    
    try {
      loading = true;
      error = null;
      
      // Use the bidStore to fetch user bids
      await bidStore.loadUserBids();
      bids = $bidStore.userBids;
      
      // Process bids to categorize them
      processAndCategorize();
      
      loading = false;
    } catch (err) {
      console.error('Error loading bids:', err);
      error = err.error || 'Failed to load bids';
      loading = false;
    }
  }
  
  // Process and categorize bids
  function processAndCategorize() {
    // Reset categories
    activeBids = [];
    wonBids = [];
    outbidBids = [];
    activeAuctionIds = new Set();
    
    // Group bids by auction to find the highest bid per auction
    const auctionBids = {};
    
    bids.forEach(bid => {
      const auctionId = bid.auction;
      
      if (!auctionBids[auctionId]) {
        auctionBids[auctionId] = [];
      }
      
      auctionBids[auctionId].push(bid);
    });
    
    // Process each auction's bids
    Object.entries(auctionBids).forEach(([auctionId, auctionBidList]) => {
      // Sort bids by amount (highest first)
      auctionBidList.sort((a, b) => b.amount - a.amount);
      
      const highestBid = auctionBidList[0];
      const userHighestBid = auctionBidList.find(bid => bid.bidder === $user?.id);
      
      if (!userHighestBid) return;
      
      // Check if auction is still active
      const isActive = userHighestBid.auction_details?.status === 'ACTIVE';
      
      // Check if user is the highest bidder
      const isHighestBidder = highestBid.bidder === $user?.id;
      
      // Check if auction has ended
      const hasEnded = new Date(userHighestBid.auction_details?.end_time) < new Date();
      
      // Categorize the bids
      if (isActive) {
        if (isHighestBidder) {
          // User is currently winning
          activeBids.push(userHighestBid);
          activeAuctionIds.add(auctionId);
        } else {
          // User has been outbid
          outbidBids.push(userHighestBid);
        }
      } else if (hasEnded) {
        if (isHighestBidder) {
          // User won the auction
          wonBids.push(userHighestBid);
        } else {
          // User lost the auction
          outbidBids.push(userHighestBid);
        }
      }
    });
    
    // Sort the categories
    const sortFunction = getSortFunction();
    activeBids.sort(sortFunction);
    wonBids.sort(sortFunction);
    outbidBids.sort(sortFunction);
  }
  
  // Get sort function based on current sorting preferences
  function getSortFunction() {
    return (a, b) => {
      let valueA, valueB;
      
      switch (sortBy) {
        case 'amount':
          valueA = a.amount;
          valueB = b.amount;
          break;
        case 'end_time':
          valueA = new Date(a.auction_details?.end_time);
          valueB = new Date(b.auction_details?.end_time);
          break;
        case 'created_at':
        default:
          valueA = new Date(a.created_at);
          valueB = new Date(b.created_at);
          break;
      }
      
      // Apply direction
      return sortDirection === 'desc' ? 
        (valueB > valueA ? 1 : -1) : 
        (valueA > valueB ? 1 : -1);
    };
  }
  
  // Handle sorting change
  function handleSortChange() {
    processAndCategorize();
  }
  
  // Format time remaining
  function formatTimeRemaining(endTime) {
    if (!endTime) return 'Unknown';
    
    const end = new Date(endTime);
    const now = new Date();
    
    if (now >= end) return 'Ended';
    
    const diffMs = end - now;
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    const diffHours = Math.floor((diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const diffMinutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
    
    if (diffDays > 0) {
      return `${diffDays}d ${diffHours}h`;
    } else if (diffHours > 0) {
      return `${diffHours}h ${diffMinutes}m`;
    } else {
      return `${diffMinutes}m`;
    }
  }
  
  // Get bid status badge class
  function getBidStatusClass(bid) {
    if (!bid.auction_details) return 'bg-gray-100 text-gray-800';
    
    const isHighestBidder = bid.amount === bid.auction_details.current_price;
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
    if (!bid.auction_details) return 'Unknown';
    
    const isHighestBidder = bid.amount === bid.auction_details.current_price;
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
  
  // Initialize on mount
  onMount(() => {
    loadBids();
  });
</script>

<svelte:head>
  <title>My Bids | GUDIC</title>
  <meta name="description" content="View and manage your active bids" />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
  <!-- Header -->
  <div class="mb-6">
    <h1 class="text-3xl font-bold text-text-dark">My Bids</h1>
    <p class="text-text-medium mt-2">View and manage your auction bids</p>
  </div>
  
  <!-- Not authenticated -->
  {#if !$isAuthenticated}
    <div class="bg-white rounded-xl p-8 text-center shadow-sm border border-gray-200">
      <p class="text-text-medium mb-4">Please log in to view your bids.</p>
      <a 
        href="/login" 
        class="inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-blue hover:bg-primary-blue/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-blue"
      >
        Log In
      </a>
    </div>
  
  <!-- Loading state -->
  {:else if loading}
    <div class="flex justify-center items-center py-12">
      <Spinner size="lg" />
    </div>
  
  <!-- Error state -->
  {:else if error}
    <div class="bg-red-50 p-4 rounded-md text-red-600 mb-8">
      <p class="text-center">{error}</p>
      <div class="flex justify-center mt-4">
        <Button 
          variant="primary" 
          size="sm"
          on:click={loadBids}
        >
          Try Again
        </Button>
      </div>
    </div>
  
  <!-- Content state -->
  {:else}
    <!-- Sort controls -->
    <div class="flex justify-between items-center mb-6">
      <div class="flex space-x-4 items-center">
        <span class="text-sm text-text-medium">Sort by:</span>
        <select
          bind:value={sortBy}
          on:change={handleSortChange}
          class="text-sm border border-gray-300 rounded-md shadow-sm focus:ring-primary-blue focus:border-primary-blue"
        >
          <option value="created_at">Date Bid</option>
          <option value="amount">Bid Amount</option>
          <option value="end_time">End Time</option>
        </select>
        
        <select
          bind:value={sortDirection}
          on:change={handleSortChange}
          class="text-sm border border-gray-300 rounded-md shadow-sm focus:ring-primary-blue focus:border-primary-blue"
        >
          <option value="desc">Descending</option>
          <option value="asc">Ascending</option>
        </select>
      </div>
      
      <Button 
        on:click={loadBids}
        variant="outline"
        size="sm"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd" />
        </svg>
        Refresh
      </Button>
    </div>
    
    <!-- Tabs and content -->
    <div class="bg-white rounded-lg border border-primary-blue/20 overflow-hidden">
      <Tabs {tabs} bind:activeTab />
      
      <div class="p-6">
        {#if activeTab === 'active' && activeBids.length === 0}
          <div class="text-center py-8">
            <p class="text-text-medium mb-4">You don't have any active bids at the moment.</p>
            <a 
              href="/auctions" 
              class="inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-blue hover:bg-primary-blue/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-blue"
            >
              Browse Auctions
            </a>
          </div>
        {:else if activeTab === 'won' && wonBids.length === 0}
          <div class="text-center py-8">
            <p class="text-text-medium mb-4">You haven't won any auctions yet.</p>
            <a 
              href="/auctions" 
              class="inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-blue hover:bg-primary-blue/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-blue"
            >
              Browse Auctions
            </a>
          </div>
        {:else if activeTab === 'outbid' && outbidBids.length === 0}
          <div class="text-center py-8">
            <p class="text-text-medium mb-4">You don't have any outbid bids.</p>
            <a 
              href="/auctions" 
              class="inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-blue hover:bg-primary-blue/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-blue"
            >
              Browse Auctions
            </a>
          </div>
        {:else if activeTab === 'all' && bids.length === 0}
          <div class="text-center py-8">
            <p class="text-text-medium mb-4">You haven't placed any bids yet.</p>
            <a 
              href="/auctions" 
              class="inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-blue hover:bg-primary-blue/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-blue"
            >
              Browse Auctions
            </a>
          </div>
        {:else}
          <!-- Bids table -->
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Auction
                  </th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Your Bid
                  </th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Current Price
                  </th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Time Remaining
                  </th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Bid Date
                  </th>
                  <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                {#each activeTab === 'active' ? activeBids : activeTab === 'won' ? wonBids : activeTab === 'outbid' ? outbidBids : bids as bid}
                  <tr class="hover:bg-gray-50">
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="flex items-center">
                        <div class="h-10 w-10 flex-shrink-0 bg-gray-100 rounded-md overflow-hidden">
                          {#if bid.auction_details?.image_url}
                            <img src={bid.auction_details.image_url} alt="" class="h-10 w-10 object-cover" />
                          {:else}
                            <div class="h-10 w-10 flex items-center justify-center text-gray-400">
                              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                              </svg>
                            </div>
                          {/if}
                        </div>
                        <div class="ml-4">
                          <div class="text-sm font-medium text-text-dark">
                            {bid.auction_details?.title || 'Unknown Auction'}
                          </div>
                          <div class="text-xs text-text-medium">
                            ID: {bid.auction}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="text-sm font-medium text-secondary-blue">
                        {formatCurrency(bid.amount, bid.auction_details?.currency || 'USD')}
                      </div>
                      {#if bid.auto_bid_limit}
                        <div class="text-xs text-text-medium">
                          Auto up to {formatCurrency(bid.auto_bid_limit, bid.auction_details?.currency || 'USD')}
                        </div>
                      {/if}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="text-sm text-text-dark">
                        {bid.auction_details 
                          ? formatCurrency(bid.auction_details.current_price, bid.auction_details.currency || 'USD') 
                          : '-'}
                      </div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <span class="px-2 inline-flex text-xs leading-5 font-medium rounded-full {getBidStatusClass(bid)}">
                        {getBidStatus(bid)}
                      </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-text-medium">
                      {bid.auction_details 
                        ? formatTimeRemaining(bid.auction_details.end_time) 
                        : '-'}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-text-medium">
                      {formatDate(bid.created_at)}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <a 
                        href={`/auctions/${bid.auction}`} 
                        class="inline-flex items-center px-2.5 py-1.5 border border-gray-300 text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-blue"
                        aria-label={`View auction ${bid.auction_details?.title || `Auction #${bid.auction}`}`}
                      >
                        View
                      </a>
                      
                      {#if getBidStatus(bid) === 'Outbid' && bid.auction_details?.status === 'ACTIVE'}
                        <a 
                          href={`/auctions/${bid.auction}#bidding`} 
                          class="ml-2 inline-flex items-center px-2.5 py-1.5 border border-transparent text-xs font-medium rounded shadow-sm text-white bg-primary-blue hover:bg-primary-blue/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-blue"
                          aria-label={`Bid again on auction ${bid.auction_details?.title || `Auction #${bid.auction}`}`}
                        >
                          Bid Again
                        </a>
                      {/if}
                      
                      {#if getBidStatus(bid) === 'Won'}
                        <a 
                          href={`/auctions/${bid.auction}/checkout`} 
                          class="ml-2 inline-flex items-center px-2.5 py-1.5 border border-transparent text-xs font-medium rounded shadow-sm text-white bg-primary-blue hover:bg-primary-blue/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-blue"
                          aria-label={`Checkout auction ${bid.auction_details?.title || `Auction #${bid.auction}`}`}
                        >
                          Checkout
                        </a>
                      {/if}
                    </td>
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>
        {/if}
      </div>
    </div>
  {/if}
</div>