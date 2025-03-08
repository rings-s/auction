<!-- src/routes/auctions/sold/+page.svelte -->
<script>
    import { onMount, onDestroy } from 'svelte';
    import { auctionStore } from '$lib/stores/auctionStore';
    import AuctionCard from '$lib/components/auction/AuctionCard.svelte';
    import Button from '$lib/components/ui/Button.svelte';
    import Spinner from '$lib/components/ui/Spinner.svelte';
    import Alert from '$lib/components/ui/Alert.svelte';
    import { isAuthenticated, primaryRole, user } from '$lib/stores/authStore';
    import { browser } from '$app/environment';
    import { goto } from '$app/navigation';
    import { api } from '$lib/api';
    import { notificationStore } from '$lib/stores/notificationStore';
    
    // State variables
    let auctions = [];
    let loading = true;
    let error = null;
    let filters = {
      status: 'ENDED', // Default to show ended auctions
      seller: '', // Will be filled with current user's ID
      sort_by: 'end_time',
      direction: 'desc',
      has_winner: true, // Only show auctions with winners
      min_price: '',
      max_price: '',
      search: ''
    };
    let pagination = {
      page: 1,
      total_pages: 1,
      count: 0,
      next: null,
      previous: null
    };
    let searchTimeout;
    
    // Status options
    const statusOptions = [
      { value: 'ENDED', label: 'Ended' },
      { value: 'ACTIVE', label: 'Active' },
      { value: 'DRAFT', label: 'Draft' },
      { value: 'CANCELLED', label: 'Cancelled' }
    ];
    
    // Sort options
    const sortOptions = [
      { value: 'end_time', label: 'End Time' },
      { value: 'created_at', label: 'Date Created' },
      { value: 'current_price', label: 'Price' }
    ];
    
    // Direction options
    const directionOptions = [
      { value: 'desc', label: 'Descending' },
      { value: 'asc', label: 'Ascending' }
    ];
    
    // Load auctions
    async function loadAuctions(page = 1) {
      if (!$isAuthenticated || !$user) {
        goto('/login?redirect=/auctions/sold');
        return;
      }
      
      // Ensure seller filter is set to current user
      filters.seller = $user.id;
      
      loading = true;
      
      try {
        // Filter out empty parameters
        const cleanFilters = Object.fromEntries(
          Object.entries(filters).filter(([_, v]) => v !== '')
        );
        
        const params = {
          page: page,
          page_size: 12,
          ...cleanFilters
        };
        
        const response = await api.auction.list({ params });
        
        if (response && Array.isArray(response.results)) {
          auctions = response.results || [];
          pagination = {
            page: page,
            total_pages: response.total_pages || 1,
            count: response.count || 0,
            next: response.next ? page + 1 : null,
            previous: page > 1 ? page - 1 : null
          };
        } else {
          console.warn('Unexpected auctions response format:', response);
          auctions = [];
          pagination = {
            page: 1,
            total_pages: 1,
            count: 0,
            next: null,
            previous: null
          };
        }
        
        error = null;
      } catch (err) {
        console.error('Error loading sold auctions:', err);
        error = 'Failed to load sold auctions. Please try again.';
        auctions = [];
      } finally {
        loading = false;
      }
    }
    
    // Handle filter changes
    function handleFilterChange(event) {
      const { name, value } = event.target;
      filters = { ...filters, [name]: value };
      loadAuctions(1); // Reset to first page when filter changes
    }
    
    // Handle search with debouncing
    function handleSearch(event) {
      if (searchTimeout) clearTimeout(searchTimeout);
      
      searchTimeout = setTimeout(() => {
        filters = { ...filters, search: event.target.value };
        loadAuctions(1);
      }, 300); // 300ms debounce
    }
    
    // Clear all filters except seller
    function clearFilters() {
      filters = {
        status: 'ENDED',
        seller: $user?.id || '',
        sort_by: 'end_time',
        direction: 'desc',
        has_winner: true,
        min_price: '',
        max_price: '',
        search: ''
      };
      loadAuctions(1);
    }
    
    // Handle pagination
    function goToPage(page) {
      if (page < 1 || page > pagination.total_pages) return;
      loadAuctions(page);
      // Scroll to top of auctions section
      if (browser) {
        setTimeout(() => {
          document.getElementById('auctions-section')?.scrollIntoView({ behavior: 'smooth' });
        }, 100);
      }
    }
    
    // Format currency
    function formatCurrency(amount, currency = 'USD') {
      if (amount === undefined || amount === null) return '$0.00';
      
      try {
        // Ensure amount is a number
        const numericAmount = typeof amount === 'string' ? parseFloat(amount) : amount;
        
        if (isNaN(numericAmount)) {
          console.warn('Invalid amount for formatting:', amount);
          return '$0.00';
        }
        
        return new Intl.NumberFormat('en-US', {
          style: 'currency',
          currency: currency
        }).format(numericAmount);
      } catch (err) {
        console.error('Error formatting currency:', err);
        return '$0.00';
      }
    }
    
    // Format date
    function formatDate(dateStr) {
      if (!dateStr) return 'Unknown date';
      const date = new Date(dateStr);
      return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      }).format(date);
    }
    
    // Initialize on mount
    onMount(async () => {
      if (!$isAuthenticated) {
        notificationStore.error('You must be logged in to view your sold auctions');
        goto('/login?redirect=/auctions/sold');
        return;
      }
      
      // Check if user is a seller
      if (!($primaryRole?.code === 'seller' || $primaryRole?.code === 'admin')) {
        notificationStore.error('Only sellers can access this page');
        goto('/dashboard');
        return;
      }
      
      // Set seller filter to current user
      if ($user) {
        filters.seller = $user.id;
      }
      
      // Load auctions with default filters
      await loadAuctions();
    });
    
    // Clean up on destroy
    onDestroy(() => {
      if (searchTimeout) clearTimeout(searchTimeout);
    });
  </script>
  
  <svelte:head>
    <title>My Sold Auctions | GUDIC</title>
    <meta name="description" content="View all your sold auctions on the GUDIC platform." />
  </svelte:head>
  
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
    <!-- Header Section -->
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center mb-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 tracking-tight">My Sold Auctions</h1>
        <p class="mt-1 text-gray-600">Manage and track all auctions you have sold</p>
      </div>
      
      <!-- Create Auction button for sellers -->
      {#if browser && $isAuthenticated && ($primaryRole?.code === 'seller' || $primaryRole?.code === 'admin')}
        <a 
          href="/auctions/create" 
          class="mt-3 md:mt-0 shadow-sm hover:shadow transition-shadow duration-200 inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          Create Auction
        </a>
      {/if}
    </div>
    
    <!-- Filters -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-5 mb-6 transition-all duration-200 hover:shadow">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-lg font-semibold text-gray-900">Filters</h2>
        <button 
          type="button"
          class="text-gray-600 hover:text-gray-800 hover:bg-gray-50 inline-flex items-center justify-center px-3 py-1.5 border border-gray-300 text-sm font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          on:click={clearFilters}
        >
          Clear Filters
        </button>
      </div>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <!-- Status filter -->
        <div class="space-y-1">
          <label for="status" class="block text-sm font-medium text-gray-700">
            Status
          </label>
          <select
            id="status"
            name="status"
            value={filters.status || 'ENDED'}
            on:change={handleFilterChange}
            class="block w-full rounded-lg border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          >
            {#each statusOptions as option}
              <option value={option.value}>{option.label}</option>
            {/each}
          </select>
        </div>
        
        <!-- Has Winner filter -->
        <div class="space-y-1">
          <label for="has_winner" class="block text-sm font-medium text-gray-700">
            Auction Result
          </label>
          <select
            id="has_winner"
            name="has_winner"
            bind:value={filters.has_winner}
            on:change={handleFilterChange}
            class="block w-full rounded-lg border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          >
            <option value={true}>With Winner</option>
            <option value={false}>No Winner</option>
            <option value="">All</option>
          </select>
        </div>
        
        <!-- Price range filters -->
        <div class="space-y-1">
          <label for="min_price" class="block text-sm font-medium text-gray-700">
            Min Price
          </label>
          <input
            type="number"
            id="min_price"
            name="min_price"
            value={filters.min_price || ''}
            on:change={handleFilterChange}
            min="0"
            placeholder="Min Price"
            class="block w-full rounded-lg border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          />
        </div>
        
        <div class="space-y-1">
          <label for="max_price" class="block text-sm font-medium text-gray-700">
            Max Price
          </label>
          <input
            type="number"
            id="max_price"
            name="max_price"
            value={filters.max_price || ''}
            on:change={handleFilterChange}
            min="0"
            placeholder="Max Price"
            class="block w-full rounded-lg border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          />
        </div>
        
        <!-- Search -->
        <div class="md:col-span-2 space-y-1">
          <label for="search" class="block text-sm font-medium text-gray-700">
            Search
          </label>
          <div class="relative">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <input
              type="text"
              id="search"
              name="search"
              value={filters.search || ''}
              on:input={handleSearch}
              placeholder="Search your sold auctions..."
              class="block w-full pl-10 pr-3 py-2 rounded-lg border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            />
          </div>
        </div>
        
        <!-- Sort options -->
        <div class="space-y-1">
          <label for="sort_by" class="block text-sm font-medium text-gray-700">
            Sort By
          </label>
          <select
            id="sort_by"
            name="sort_by"
            value={filters.sort_by || 'end_time'}
            on:change={handleFilterChange}
            class="block w-full rounded-lg border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          >
            {#each sortOptions as option}
              <option value={option.value}>{option.label}</option>
            {/each}
          </select>
        </div>
        
        <!-- Direction -->
        <div class="space-y-1">
          <label for="direction" class="block text-sm font-medium text-gray-700">
            Order
          </label>
          <select
            id="direction"
            name="direction"
            value={filters.direction || 'desc'}
            on:change={handleFilterChange}
            class="block w-full rounded-lg border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          >
            {#each directionOptions as option}
              <option value={option.value}>{option.label}</option>
            {/each}
          </select>
        </div>
      </div>
    </div>
    
    <!-- Auctions list -->
    <div id="auctions-section" class="min-h-[400px]">
      {#if loading}
        <div class="flex justify-center items-center py-12">
          <Spinner size="lg" />
        </div>
      {:else if error}
        <div class="bg-red-50 border border-red-200 p-6 rounded-xl text-red-600 mb-6">
          <div class="flex flex-col items-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-red-500 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <p class="text-center font-medium mb-2">{error}</p>
            <p class="text-sm text-red-500 mb-4">There was a problem loading your sold auctions.</p>
            <button 
              type="button"
              class="inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              on:click={() => loadAuctions(1)}
            >
              Try Again
            </button>
          </div>
        </div>
      {:else if auctions.length === 0}
        <div class="bg-white border border-gray-200 rounded-xl p-8 text-center shadow-sm">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-14 w-14 text-gray-400 mx-auto mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
          </svg>
          <h3 class="text-xl font-medium text-gray-900 mb-2">No sold auctions found</h3>
          <p class="text-gray-500 max-w-md mx-auto mb-5">You haven't sold any auctions matching the current filters.</p>
          <div class="flex flex-col sm:flex-row justify-center gap-3">
            <button 
              type="button"
              class="inline-flex items-center justify-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              on:click={clearFilters}
            >
              Clear Filters
            </button>
            
            <a 
              href="/auctions/create" 
              class="inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Create New Auction
            </a>
          </div>
        </div>
      {:else}
        <!-- Results Summary -->
        <div class="text-sm text-gray-500 mb-4">
          Showing <span class="font-medium text-gray-700">{auctions.length}</span> of <span class="font-medium text-gray-700">{pagination.count}</span> sold auctions
        </div>
        
        <!-- Enhanced Auction Grid for Sold Auctions -->
        <div class="grid grid-cols-1 gap-5">
          {#each auctions as auction (auction.id)}
            <div class="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm hover:shadow transition-shadow duration-200">
              <div class="p-5 flex flex-col md:flex-row gap-5">
                <!-- Auction Image -->
                <div class="w-full md:w-48 h-48 bg-gray-100 rounded-lg overflow-hidden flex-shrink-0">
                  {#if auction.image_url || auction.main_image}
                    <img 
                      src={auction.image_url || auction.main_image} 
                      alt={auction.title} 
                      class="w-full h-full object-cover"
                      on:error={(e) => e.target.src = 'https://via.placeholder.com/400x400?text=No+Image'}
                    />
                  {:else}
                    <div class="flex items-center justify-center h-full bg-gray-200">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                    </div>
                  {/if}
                </div>
                
                <!-- Auction Details -->
                <div class="flex-1">
                  <div class="flex flex-wrap items-center gap-2 mb-2">
                    <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium {auction.status === 'ACTIVE' ? 'bg-green-100 text-green-800' : auction.status === 'ENDED' ? 'bg-blue-100 text-blue-800' : auction.status === 'CANCELLED' ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-800'}">
                      {auction.status}
                    </span>
                    
                    {#if auction.winning_bidder}
                      <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        Sold
                      </span>
                    {:else if auction.status === 'ENDED'}
                      <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                        No Winner
                      </span>
                    {/if}
                    
                    {#if auction.category?.name}
                      <a 
                        href={`/categories/${auction.category?.slug || ''}`} 
                        class="text-xs font-medium px-2 py-1 bg-primary-blue/10 text-secondary-blue rounded-full hover:bg-primary-blue/20 transition-colors"
                      >
                        {auction.category.name}
                      </a>
                    {/if}
                  </div>
                  
                  <h2 class="text-xl font-semibold text-gray-900 mb-2">
                    <a href={`/auctions/${auction.id}`} class="hover:text-blue-600">{auction.title}</a>
                  </h2>
                  
                  <p class="text-sm text-gray-500 mb-4 line-clamp-2">{auction.description}</p>
                  
                  <div class="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-2 mb-4">
                    <div class="flex flex-col">
                      <span class="text-xs text-gray-500">Final Price</span>
                      <span class="text-base font-semibold text-blue-600">{formatCurrency(auction.current_price, auction.currency)}</span>
                    </div>
                    
                    <div class="flex flex-col">
                      <span class="text-xs text-gray-500">Winning Bidder</span>
                      <span class="text-base">
                        {#if auction.winning_bidder_details?.first_name}
                          {auction.winning_bidder_details.first_name} {auction.winning_bidder_details.last_name?.charAt(0) || ''}
                        {:else}
                          No winner
                        {/if}
                      </span>
                    </div>
                    
                    <div class="flex flex-col">
                      <span class="text-xs text-gray-500">End Date</span>
                      <span class="text-base">{formatDate(auction.end_time)}</span>
                    </div>
                    
                    <div class="flex flex-col">
                      <span class="text-xs text-gray-500">Total Bids</span>
                      <span class="text-base">{auction.total_bids || 0} bids</span>
                    </div>
                  </div>
                  
                  <div class="flex flex-wrap gap-2 mt-4">
                    <a 
                      href={`/auctions/${auction.id}`} 
                      class="inline-flex items-center justify-center px-3 py-1.5 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                    >
                      View Details
                    </a>
                    
                    {#if auction.status === 'ENDED' && auction.winning_bidder}
                      <a 
                        href={`/messages/${auction.winning_bidder}`} 
                        class="inline-flex items-center justify-center px-3 py-1.5 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                      >
                        Contact Buyer
                      </a>
                    {/if}
                    
                    {#if auction.status === 'DRAFT' || auction.status === 'ACTIVE'}
                      <a 
                        href={`/auctions/${auction.id}/edit`} 
                        class="inline-flex items-center justify-center px-3 py-1.5 border border-gray-300 text-sm font-medium rounded-md text-blue-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                      >
                        Edit Auction
                      </a>
                    {/if}
                  </div>
                </div>
              </div>
            </div>
          {/each}
        </div>
        
        <!-- Pagination -->
        {#if pagination.total_pages > 1}
          <div class="flex justify-center mt-8">
            <nav class="relative z-0 inline-flex rounded-md shadow-sm" aria-label="Pagination">
              <!-- Previous page -->
              <button
                type="button"
                class="relative inline-flex items-center px-3 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 transition-colors {!pagination.previous ? 'opacity-50 cursor-not-allowed' : ''}"
                on:click={() => pagination.previous && goToPage(pagination.previous)}
                disabled={!pagination.previous}
                aria-label="Previous page"
              >
                <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                  <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
              </button>
              
              <!-- Page numbers -->
              <span class="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700">
                Page {pagination.page} of {pagination.total_pages}
              </span>
              
              <!-- Next page -->
              <button
                type="button"
                class="relative inline-flex items-center px-3 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 transition-colors {!pagination.next ? 'opacity-50 cursor-not-allowed' : ''}"
                on:click={() => pagination.next && goToPage(pagination.next)}
                disabled={!pagination.next}
                aria-label="Next page"
              >
                <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                  <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
                </svg>
              </button>
            </nav>
          </div>
        {/if}
      {/if}
    </div>
  </div>