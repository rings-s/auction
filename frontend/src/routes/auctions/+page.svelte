<!-- src/routes/auctions/+page.svelte -->
<script>
  import { onMount } from 'svelte';
  import { auctionStore } from '$lib/stores/auctionStore';
  import AuctionCard from '$lib/components/auction/AuctionCard.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Spinner from '$lib/components/ui/Spinner.svelte';
  import { isAuthenticated, primaryRole } from '$lib/stores/authStore';
  import { browser } from '$app/environment';
  import { api } from '$lib/api';
  import RelatedAuctions from '$lib/components/auction/RelatedAuctions.svelte';
  
  // State variables
  let auctions = [];
  let categories = [];
  let loading = true;
  let error = null;
  let filters = {
    status: 'ACTIVE',
    sort_by: 'created_at',
    direction: 'desc',
    min_price: '',
    max_price: '',
    category: ''
  };
  let pagination = {
    page: 1,
    total_pages: 1,
    count: 0,
    next: null,
    previous: null
  };
  
  // Status options
  const statusOptions = [
    { value: 'ACTIVE', label: 'Active' },
    { value: 'ENDED', label: 'Ended' },
    { value: 'DRAFT', label: 'Draft' },
    { value: 'CANCELLED', label: 'Cancelled' }
  ];
  
  // Sort options
  const sortOptions = [
    { value: 'created_at', label: 'Date Created' },
    { value: 'end_time', label: 'End Time' },
    { value: 'current_price', label: 'Price' }
  ];
  
  // Direction options
  const directionOptions = [
    { value: 'desc', label: 'Descending' },
    { value: 'asc', label: 'Ascending' }
  ];
  
  // Load auctions and categories
  async function loadCategories() {
    try {
      const response = await api.category.list({
        params: { is_active: true }
      });
      
      if (response && Array.isArray(response.results)) {
        categories = response.results || [];
      } else {
        categories = [];
        console.warn('Unexpected categories response format:', response);
      }
    } catch (err) {
      console.error('Error loading categories:', err);
      categories = [];
    }
  }
  
  async function loadAuctions(page = 1) {
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
      console.error('Error loading auctions:', err);
      error = 'Failed to load auctions. Please try again.';
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
  
  // Clear all filters
  function clearFilters() {
    filters = {
      status: 'ACTIVE',
      sort_by: 'created_at',
      direction: 'desc',
      min_price: '',
      max_price: '',
      category: ''
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
  
  // Initialize on mount
  onMount(async () => {
    // Load categories first
    await loadCategories();
    // Then load auctions with default filters
    await loadAuctions();
  });
</script>

<svelte:head>
  <title>Browse Auctions | GUDIC</title>
  <meta name="description" content="Browse all active auctions on the GUDIC platform." />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
  <!-- Header Section -->
  <div class="flex flex-col md:flex-row justify-between items-start md:items-center mb-6">
    <div>
      <h1 class="text-2xl font-bold text-gray-900 tracking-tight">Browse Auctions</h1>
      <p class="mt-1 text-gray-600">Find and bid on auctions that match your interests</p>
    </div>
    
    <!-- Create Auction button for sellers and admins -->
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
      <!-- Category filter -->
      <div class="space-y-1">
        <label for="category" class="block text-sm font-medium text-gray-700">
          Category
        </label>
        <select
          id="category"
          name="category"
          value={filters.category || ''}
          on:change={handleFilterChange}
          class="block w-full rounded-lg border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
        >
          <option value="">All Categories</option>
          {#each categories as category}
            <option value={category.slug}>{category.name}</option>
          {/each}
        </select>
      </div>
      
      <!-- Status filter -->
      <div class="space-y-1">
        <label for="status" class="block text-sm font-medium text-gray-700">
          Status
        </label>
        <select
          id="status"
          name="status"
          value={filters.status || ''}
          on:change={handleFilterChange}
          class="block w-full rounded-lg border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
        >
          <option value="">All Statuses</option>
          {#each statusOptions as option}
            <option value={option.value}>{option.label}</option>
          {/each}
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
            on:change={handleFilterChange}
            placeholder="Search auctions..."
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
          value={filters.sort_by || 'created_at'}
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
          <p class="text-sm text-red-500 mb-4">There was a problem loading the auctions.</p>
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
        <h3 class="text-xl font-medium text-gray-900 mb-2">No auctions found</h3>
        <p class="text-gray-500 max-w-md mx-auto mb-5">Try changing your filters or check back later for new auctions.</p>
        <button 
          type="button"
          class="inline-flex items-center justify-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          on:click={clearFilters}
        >
          Clear Filters
        </button>
      </div>
    {:else}
      <!-- Results Summary -->
      <div class="text-sm text-gray-500 mb-4">
        Showing <span class="font-medium text-gray-700">{auctions.length}</span> of <span class="font-medium text-gray-700">{pagination.count}</span> auctions
      </div>
      
      <!-- Auction grid -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
        {#each auctions as auction (auction.id)}
          <AuctionCard {auction} />
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