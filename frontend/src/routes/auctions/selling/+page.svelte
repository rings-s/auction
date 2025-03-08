<!-- src/routes/auctions/selling/+page.svelte -->
<script>
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import { isAuthenticated, primaryRole, user } from '$lib/stores/authStore';
    import { notificationStore } from '$lib/stores/notificationStore';
    import { api } from '$lib/api';
    import Button from '$lib/components/ui/Button.svelte';
    import Spinner from '$lib/components/ui/Spinner.svelte';
    import Alert from '$lib/components/ui/Alert.svelte';
    import Tabs from '$lib/components/ui/Tabs.svelte';
    import { formatDate, formatCurrency } from '$lib/utils/formatters';
    
    // State variables
    let loading = true;
    let error = null;
    let auctions = [];
    let activeAuctions = [];
    let endedAuctions = [];
    let draftAuctions = [];
    
    // Filter and sort options
    let sortBy = 'created_at';
    let sortDirection = 'desc';
    let searchQuery = '';
    
    // Tabs
    const tabs = [
      { id: 'active', label: 'Active Auctions' },
      { id: 'ended', label: 'Ended Auctions' },
      { id: 'draft', label: 'Drafts' },
      { id: 'all', label: 'All Auctions' }
    ];
    let activeTab = 'active';
    
    // Load all auctions where the current user is a seller
    async function loadSellerAuctions() {
      if (!$isAuthenticated) {
        goto('/login?redirect=/auctions/selling');
        return;
      }
      
      try {
        loading = true;
        error = null;
        
        // Fetch auctions where the user is a seller
        const response = await api.auction.list({
          params: {
            seller: $user?.id,
            sort_by: sortBy,
            direction: sortDirection,
            search: searchQuery,
          }
        });
        
        // Handle response
        if (response && response.results) {
          auctions = response.results;
          
          // Process auctions to categorize them
          processAndCategorize();
        } else {
          auctions = [];
          activeAuctions = [];
          endedAuctions = [];
          draftAuctions = [];
        }
        
        loading = false;
      } catch (err) {
        console.error('Error loading seller auctions:', err);
        error = err.message || 'Failed to load auctions';
        loading = false;
      }
    }
    
    // Process and categorize auctions
    function processAndCategorize() {
      // Reset categories
      activeAuctions = [];
      endedAuctions = [];
      draftAuctions = [];
      
      // Categorize auctions by status
      auctions.forEach(auction => {
        switch(auction.status) {
          case 'ACTIVE':
            activeAuctions.push(auction);
            break;
          case 'ENDED':
            endedAuctions.push(auction);
            break;
          case 'DRAFT':
            draftAuctions.push(auction);
            break;
        }
      });
      
      // Sort the categories
      const sortFunction = getSortFunction();
      activeAuctions.sort(sortFunction);
      endedAuctions.sort(sortFunction);
      draftAuctions.sort(sortFunction);
      auctions.sort(sortFunction);
    }
    
    // Get sort function based on current sorting preferences
    function getSortFunction() {
      return (a, b) => {
        let valueA, valueB;
        
        switch (sortBy) {
          case 'title':
            valueA = a.title || '';
            valueB = b.title || '';
            break;
          case 'current_price':
            valueA = parseFloat(a.current_price) || 0;
            valueB = parseFloat(b.current_price) || 0;
            break;
          case 'end_time':
            valueA = new Date(a.end_time || 0);
            valueB = new Date(b.end_time || 0);
            break;
          case 'total_bids':
            valueA = a.total_bids || 0;
            valueB = b.total_bids || 0;
            break;
          case 'created_at':
          default:
            valueA = new Date(a.created_at || 0);
            valueB = new Date(b.created_at || 0);
            break;
        }
        
        // Apply direction
        if (typeof valueA === 'string' && typeof valueB === 'string') {
          return sortDirection === 'desc' ? 
            valueB.localeCompare(valueA) : 
            valueA.localeCompare(valueB);
        } else {
          return sortDirection === 'desc' ? 
            (valueB > valueA ? 1 : -1) : 
            (valueA > valueB ? 1 : -1);
        }
      };
    }
    
    // Handle sorting change
    function handleSortChange() {
      processAndCategorize();
    }
    
    // Handle search
    function handleSearch() {
      loadSellerAuctions();
    }
    
    // Format time remaining
    function formatTimeRemaining(endTime) {
      if (!endTime) return 'Not set';
      
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
    
    // Get status badge class
    function getStatusBadgeClass(status) {
      switch (status) {
        case 'ACTIVE':
          return 'bg-green-100 text-green-800';
        case 'ENDED':
          return 'bg-blue-100 text-blue-800';
        case 'DRAFT':
          return 'bg-yellow-100 text-yellow-800';
        case 'CANCELLED':
          return 'bg-red-100 text-red-800';
        default:
          return 'bg-gray-100 text-gray-800';
      }
    }
    
    // Delete auction
    async function deleteAuction(auctionId) {
      if (!confirm('Are you sure you want to delete this auction? This cannot be undone.')) {
        return;
      }
      
      try {
        await api.auction.delete(auctionId);
        notificationStore.success('Auction deleted successfully');
        // Reload auctions
        loadSellerAuctions();
      } catch (err) {
        console.error('Error deleting auction:', err);
        notificationStore.error('Failed to delete auction');
      }
    }
    
    // Cancel auction
    async function cancelAuction(auctionId) {
      if (!confirm('Are you sure you want to cancel this auction?')) {
        return;
      }
      
      try {
        await api.auction.update(auctionId, { status: 'CANCELLED' });
        notificationStore.success('Auction cancelled successfully');
        // Reload auctions
        loadSellerAuctions();
      } catch (err) {
        console.error('Error cancelling auction:', err);
        notificationStore.error('Failed to cancel auction');
      }
    }
    
    // Publish draft auction
    async function publishAuction(auctionId) {
      try {
        await api.auction.update(auctionId, { status: 'ACTIVE' });
        notificationStore.success('Auction published successfully');
        // Reload auctions
        loadSellerAuctions();
      } catch (err) {
        console.error('Error publishing auction:', err);
        notificationStore.error('Failed to publish auction');
      }
    }
    
    // Initialize on mount
    onMount(() => {
      // Check if user is authenticated and is a seller
      if (!$isAuthenticated) {
        goto('/login?redirect=/auctions/selling');
        return;
      }
      
      if ($primaryRole?.code !== 'seller' && $primaryRole?.code !== 'admin') {
        notificationStore.error('You do not have permission to access this page');
        goto('/');
        return;
      }
      
      loadSellerAuctions();
    });
  </script>
  
  <svelte:head>
    <title>My Selling Auctions | GUDIC</title>
    <meta name="description" content="Manage your selling auctions on GUDIC" />
  </svelte:head>
  
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Header -->
    <div class="mb-6 flex flex-col md:flex-row justify-between items-start md:items-center space-y-4 md:space-y-0">
      <div>
        <h1 class="text-3xl font-bold text-text-dark">My Selling Auctions</h1>
        <p class="text-text-medium mt-2">Manage and track the auctions you're selling</p>
      </div>
      
      <Button 
        href="/auctions/create" 
        variant="primary" 
        size="md"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" />
        </svg>
        Create Auction
      </Button>
    </div>
    
    <!-- Not authenticated -->
    {#if !$isAuthenticated}
      <div class="bg-white rounded-xl p-8 text-center shadow-sm border border-gray-200">
        <p class="text-text-medium mb-4">Please log in to view your selling auctions.</p>
        <Button 
          href="/login" 
          variant="primary" 
          size="md"
        >
          Log In
        </Button>
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
            on:click={loadSellerAuctions}
          >
            Try Again
          </Button>
        </div>
      </div>
    
    <!-- Content state -->
    {:else}
      <!-- Search and Sort controls -->
      <div class="mb-6 bg-white rounded-xl p-5 border border-gray-200 shadow-sm">
        <div class="flex flex-col md:flex-row md:items-end space-y-4 md:space-y-0 md:space-x-4">
          <!-- Search -->
          <div class="flex-1">
            <label for="search" class="block text-sm font-medium text-gray-700 mb-1">
              Search Auctions
            </label>
            <div class="relative rounded-md shadow-sm">
              <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" />
                </svg>
              </div>
              <input
                type="text"
                id="search"
                bind:value={searchQuery}
                placeholder="Search by title, description..."
                class="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              />
            </div>
          </div>
          
          <!-- Sort By -->
          <div>
            <label for="sort-by" class="block text-sm font-medium text-gray-700 mb-1">
              Sort By
            </label>
            <select
              id="sort-by"
              bind:value={sortBy}
              on:change={handleSortChange}
              class="block w-full rounded-md border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            >
              <option value="created_at">Date Created</option>
              <option value="title">Title</option>
              <option value="current_price">Current Price</option>
              <option value="end_time">End Time</option>
              <option value="total_bids">Total Bids</option>
            </select>
          </div>
          
          <!-- Sort Direction -->
          <div>
            <label for="sort-direction" class="block text-sm font-medium text-gray-700 mb-1">
              Order
            </label>
            <select
              id="sort-direction"
              bind:value={sortDirection}
              on:change={handleSortChange}
              class="block w-full rounded-md border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            >
              <option value="desc">Descending</option>
              <option value="asc">Ascending</option>
            </select>
          </div>
          
          <!-- Search Button -->
          <div>
            <Button 
              variant="primary" 
              size="md" 
              on:click={handleSearch}
            >
              Search
            </Button>
          </div>
        </div>
      </div>
      
      <!-- Tabs and content -->
      <div class="bg-white rounded-lg border border-primary-blue/20 overflow-hidden">
        <Tabs {tabs} bind:activeTab />
        
        <div class="p-6">
          {#if (activeTab === 'active' && activeAuctions.length === 0) || 
              (activeTab === 'ended' && endedAuctions.length === 0) || 
              (activeTab === 'draft' && draftAuctions.length === 0) || 
              (activeTab === 'all' && auctions.length === 0)}
            <div class="text-center py-8">
              <p class="text-text-medium mb-4">
                {#if activeTab === 'active'}
                  You don't have any active auctions at the moment.
                {:else if activeTab === 'ended'}
                  You don't have any ended auctions.
                {:else if activeTab === 'draft'}
                  You don't have any draft auctions.
                {:else}
                  You haven't created any auctions yet.
                {/if}
              </p>
              <Button 
                href="/auctions/create" 
                variant="primary" 
                size="md"
              >
                Create Auction
              </Button>
            </div>
          {:else}
            <!-- Auctions table -->
            <div class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Auction
                    </th>
                    <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Current Price
                    </th>
                    <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Bids
                    </th>
                    <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Time Remaining
                    </th>
                    <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Created
                    </th>
                    <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  {#each activeTab === 'active' ? activeAuctions : activeTab === 'ended' ? endedAuctions : activeTab === 'draft' ? draftAuctions : auctions as auction}
                    <tr class="hover:bg-gray-50">
                      <td class="px-6 py-4 whitespace-nowrap">
                        <div class="flex items-center">
                          <div class="h-10 w-10 flex-shrink-0 bg-gray-100 rounded-md overflow-hidden">
                            {#if auction.image_url || auction.main_image}
                              <img src={auction.image_url || auction.main_image} alt="" class="h-10 w-10 object-cover" />
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
                              {auction.title || 'Untitled Auction'}
                            </div>
                            <div class="text-xs text-text-medium">
                              ID: {auction.id}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap">
                        <div class="text-sm font-medium text-secondary-blue">
                          {formatCurrency(auction.current_price || auction.starting_price || 0, auction.currency || 'USD')}
                        </div>
                        {#if auction.reserve_price && auction.reserve_price > 0}
                          <div class="text-xs text-text-medium">
                            Reserve: {formatCurrency(auction.reserve_price, auction.currency || 'USD')}
                          </div>
                        {/if}
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap">
                        <div class="text-sm text-text-dark">
                          {auction.total_bids || 0}
                        </div>
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap">
                        <span class="px-2 inline-flex text-xs leading-5 font-medium rounded-full {getStatusBadgeClass(auction.status)}">
                          {auction.status}
                        </span>
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap text-sm text-text-medium">
                        {formatTimeRemaining(auction.end_time)}
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap text-sm text-text-medium">
                        {formatDate(auction.created_at)}
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div class="flex flex-col sm:flex-row gap-2 justify-end">
                          <Button 
                            href={`/auctions/${auction.id}`} 
                            variant="outline" 
                            size="xs"
                          >
                            View
                          </Button>
                          
                          {#if auction.status === 'DRAFT'}
                            <Button 
                              href={`/auctions/${auction.id}/edit`} 
                              variant="outline" 
                              size="xs"
                            >
                              Edit
                            </Button>
                            
                            <Button 
                              on:click={() => publishAuction(auction.id)} 
                              variant="primary" 
                              size="xs"
                            >
                              Publish
                            </Button>
                            
                            <Button 
                              on:click={() => deleteAuction(auction.id)} 
                              variant="outline" 
                              size="xs"
                              class="text-red-600 hover:bg-red-50"
                            >
                              Delete
                            </Button>
                          {:else if auction.status === 'ACTIVE'}
                            <Button 
                              href={`/auctions/${auction.id}/edit`} 
                              variant="outline" 
                              size="xs"
                            >
                              Edit
                            </Button>
                            
                            <Button 
                              on:click={() => cancelAuction(auction.id)} 
                              variant="outline" 
                              size="xs"
                              class="text-red-600 hover:bg-red-50"
                            >
                              Cancel
                            </Button>
                          {:else if auction.status === 'ENDED'}
                            {#if auction.total_bids > 0}
                              <Button 
                                href={`/auctions/${auction.id}/transactions`} 
                                variant="primary" 
                                size="xs"
                              >
                                Transactions
                              </Button>
                            {/if}
                            
                            <Button 
                              href={`/auctions/${auction.id}/relist`} 
                              variant="outline" 
                              size="xs"
                            >
                              Relist
                            </Button>
                          {/if}
                        </div>
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
  
  <style>
    /* Custom styles for the selling page */
    :global(td .badge) {
      font-size: 0.7rem !important;
      padding: 0.15rem 0.5rem !important;
    }
    
    /* Responsive adjustments for the actions column */
    @media (max-width: 640px) {
      :global(td .flex-col > *) {
        width: 100%;
      }
    }
  </style>