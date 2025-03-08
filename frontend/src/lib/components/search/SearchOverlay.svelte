<!-- src/lib/components/search/SearchOverlay.svelte -->
<script>
  import { createEventDispatcher, onMount, onDestroy } from 'svelte';
  import { fade, fly } from 'svelte/transition';
  import { searchOpen } from '$lib/stores/uiStore';
  import { goto } from '$app/navigation';
  import { api } from '$lib/api';
  import Spinner from '$lib/components/ui/Spinner.svelte';
  import { notificationStore } from '$lib/stores/notificationStore';
  
  const dispatch = createEventDispatcher();
  
  // Search state
  let searchQuery = '';
  let results = {
    auctions: [],
    categories: [],
    users: []
  };
  let selectedIndex = -1;
  let selectedSection = 'auctions';
  let searching = false;
  let searchInputEl;
  let searchTimeout;
  let error = null;
  
  // Filter options
  let filters = [
    { id: 'all', label: 'All', active: true },
    { id: 'auctions', label: 'Auctions', active: false },
    { id: 'categories', label: 'Categories', active: false }
  ];
  
  // Reference arrays for keyboard navigation
  let allResults = [];
  let visibleSections = [];
  
  // Computed visible sections
  $: {
    const activeFilter = filters.find(f => f.active)?.id || 'all';
    
    visibleSections = [];
    
    if (activeFilter === 'all' || activeFilter === 'auctions') {
      if (results.auctions?.length) visibleSections.push('auctions');
    }
    
    if (activeFilter === 'all' || activeFilter === 'categories') {
      if (results.categories?.length) visibleSections.push('categories');
    }
    
    if (activeFilter === 'all') {
      if (results.users?.length) visibleSections.push('users');
    }
  }
  
  // Calculate combined results for keyboard navigation
  $: {
    allResults = [];
    
    if (visibleSections.includes('auctions')) {
      results.auctions.forEach(r => allResults.push({ type: 'auctions', item: r }));
    }
    
    if (visibleSections.includes('categories')) {
      results.categories.forEach(r => allResults.push({ type: 'categories', item: r }));
    }
    
    if (visibleSections.includes('users')) {
      results.users.forEach(r => allResults.push({ type: 'users', item: r }));
    }
    
    // Reset selection index if no results or it's out of bounds
    if (allResults.length === 0) {
      selectedIndex = -1;
    } else if (selectedIndex >= allResults.length) {
      selectedIndex = 0; // Select first item if previous selection is out of bounds
    }
  }
  
  // Handle close
  function close() {
    searchOpen.set(false);
    searchQuery = '';
    selectedIndex = -1;
    results = {
      auctions: [],
      categories: [],
      users: []
    };
    error = null;
  }
  
  // Focus input on mount
  onMount(() => {
    // Focus the search input with a delay to ensure it's rendered
    setTimeout(() => {
      if (searchInputEl) {
        searchInputEl.focus();
        searchInputEl.select(); // Select any existing text for easy replacement
      }
    }, 50);
    
    // Add escape key handler
    const handleKeyDown = (event) => {
      if (event.key === 'Escape') {
        close();
      } else if (allResults.length > 0) {
        // Only handle navigation keys when we have results
        if (event.key === 'ArrowDown') {
          event.preventDefault();
          selectedIndex = (selectedIndex + 1) % allResults.length;
        } else if (event.key === 'ArrowUp') {
          event.preventDefault();
          selectedIndex = selectedIndex <= 0 ? allResults.length - 1 : selectedIndex - 1;
        } else if (event.key === 'Enter' && selectedIndex >= 0) {
          event.preventDefault();
          handleResultClick(allResults[selectedIndex]);
        }
      }
    };
    
    document.addEventListener('keydown', handleKeyDown);
    
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  });
  
  // Cleanup on component destruction
  onDestroy(() => {
    if (searchTimeout) {
      clearTimeout(searchTimeout);
    }
  });
  
  // Handle search input with debouncing
  function handleSearchInput() {
    // Clear any existing timeout
    if (searchTimeout) {
      clearTimeout(searchTimeout);
    }
    
    if (searchQuery.trim().length < 2) {
      results = {
        auctions: [],
        categories: [],
        users: []
      };
      return;
    }
    
    // Set a new timeout to delay the search
    searchTimeout = setTimeout(() => {
      executeSearch();
    }, 300); // 300ms debounce time
  }
  
  // Execute search
  async function executeSearch() {
    if (searchQuery.trim().length < 2) return;
    
    searching = true;
    error = null;
    
    try {
      // Get active filter to determine what to search
      const activeFilter = filters.find(f => f.active)?.id || 'all';
      let modelsToSearch = [];
      
      if (activeFilter === 'all') modelsToSearch = ['auctions', 'categories', 'users'];
      else if (activeFilter === 'auctions') modelsToSearch = ['auctions'];
      else if (activeFilter === 'categories') modelsToSearch = ['categories'];
      
      // Call search API with improved parameters
      const searchResponse = await api.search.search({
        params: {
          q: searchQuery,
          models: modelsToSearch.join(','),
          limit: 10 // Limit results per type
        }
      });
      
      // Process search results - make sure to handle the actual API response structure
      if (searchResponse) {
        results = {
          auctions: searchResponse.auctions || [],
          categories: searchResponse.categories || [],
          users: searchResponse.users || []
        };
      } else {
        results = { auctions: [], categories: [], users: [] };
      }
    } catch (err) {
      console.error('Search error:', err);
      error = 'Failed to perform search. Please try again.';
      results = { auctions: [], categories: [], users: [] };
    } finally {
      searching = false;
    }
  }
  
  // Handle filter click
  function setActiveFilter(filterId) {
    filters = filters.map(f => ({
      ...f,
      active: f.id === filterId
    }));
    
    // Re-run search if query exists
    if (searchQuery.trim().length >= 2) {
      executeSearch();
    }
  }
  
  // Handle result click
  function handleResultClick(result) {
    if (!result) return;
    
    const { type, item } = result;
    
    if (type === 'auctions') {
      goto(`/auctions/${item.id}`);
    } else if (type === 'categories') {
      goto(`/categories/${item.slug}`);
    } else if (type === 'users') {
      goto(`/users/${item.id}`);
    }
    
    close();
  }
  
  // Handle backdrop click with additional keyboard handler for a11y
  function handleBackdropClick(event) {
    // Only close if clicking the actual backdrop (not the modal content)
    if (event.target === event.currentTarget) {
      close();
    }
  }
  
  function handleBackdropKeydown(event) {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      close();
    }
  }
  
  // Render truncated description
  function truncateDescription(text, length = 120) {
    if (!text) return '';
    if (text.length > length) {
      return text.substring(0, length) + '...';
    }
    return text;
  }
  
  // Format price
  function formatPrice(price, currency = 'USD') {
    if (price === undefined || price === null) return '$0.00';
    
    try {
      const numericPrice = typeof price === 'string' ? parseFloat(price) : price;
      
      if (isNaN(numericPrice)) {
        return '$0.00';
      }
      
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency
      }).format(numericPrice);
    } catch (err) {
      console.error('Error formatting price:', err);
      return '$0.00';
    }
  }
  
  // Highlight matched text
  function highlightMatch(text, query) {
    if (!query || !text) return text;
    
    const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
    return text.replace(regex, '<mark class="bg-yellow-100 text-gray-900 px-0.5 rounded">$1</mark>');
  }
</script>

<!-- Search overlay - full screen with dark backdrop -->
<div 
  class="fixed inset-0 z-50 overflow-hidden"
  transition:fade={{ duration: 200 }}
  aria-modal="true"
  role="dialog"
  aria-labelledby="search-modal-title"
>
  <!-- Backdrop with click to close - with proper ARIA role -->
  <div
    role="button"
    tabindex="0"
    aria-label="Close search"
    class="absolute inset-0 bg-gray-900 bg-opacity-50 backdrop-blur-sm"
    on:click={handleBackdropClick}
    on:keydown={handleBackdropKeydown}
  ></div>

  <!-- Search panel -->
  <div class="relative w-full max-w-4xl mx-auto mt-20 bg-white rounded-xl shadow-2xl">
    <!-- Search header -->
    <div class="flex items-center p-4 border-b border-gray-200">
      <!-- Search icon -->
      <div class="text-gray-400 mr-3">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" />
        </svg>
      </div>
      
      <!-- Search input -->
      <input
        type="text"
        bind:this={searchInputEl}
        bind:value={searchQuery}
        on:input={handleSearchInput}
        placeholder="Search auctions, categories, etc."
        class="w-full py-2 px-0 text-lg text-gray-900 placeholder-gray-400 border-0 focus:ring-0 focus:border-0 focus:outline-none"
        id="search-input"
        aria-label="Search"
      />
      
      <!-- Loading indicator -->
      {#if searching}
        <div class="mr-4">
          <Spinner size="sm" />
        </div>
      {/if}
      
      <!-- Close button -->
      <button
        type="button"
        class="ml-2 flex items-center justify-center h-8 w-8 rounded-full text-gray-500 hover:text-gray-600 hover:bg-gray-100"
        on:click={close}
        aria-label="Close search"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
        </svg>
      </button>
    </div>
    
    <!-- Filters -->
    <div class="flex border-b border-gray-200 px-4">
      {#each filters as filter}
        <button
          type="button"
          class="relative py-3 px-4 text-sm font-medium transition-colors {filter.active ? 'text-indigo-600' : 'text-gray-500 hover:text-gray-700'}"
          on:click={() => setActiveFilter(filter.id)}
          aria-pressed={filter.active}
        >
          {filter.label}
          {#if filter.active}
            <span class="absolute bottom-0 left-0 right-0 h-0.5 bg-indigo-600"></span>
          {/if}
        </button>
      {/each}
    </div>
    
    <!-- Results area -->
    <div class="max-h-[60vh] overflow-y-auto p-2" role="region" aria-live="polite">
      {#if searchQuery.length < 2}
        <div class="p-8 text-center text-gray-500">
          <p>Type at least 2 characters to search</p>
        </div>
      {:else if error}
        <div class="p-8 text-center">
          <p class="text-red-500">{error}</p>
          <button 
            class="mt-2 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
            on:click={executeSearch}
          >
            Try Again
          </button>
        </div>
      {:else if searching && allResults.length === 0}
        <div class="p-8 text-center text-gray-500">
          <Spinner />
          <p class="mt-4">Searching...</p>
        </div>
      {:else if allResults.length === 0}
        <div class="p-8 text-center text-gray-500">
          <p>No results found for "{searchQuery}"</p>
        </div>
      {:else}
        <!-- Results by section -->
        {#if visibleSections.includes('auctions')}
          <div class="mb-4">
            <h3 id="search-section-auctions" class="text-xs font-semibold text-gray-500 uppercase tracking-wider px-4 py-2">
              Auctions
            </h3>
            <ul class="divide-y divide-gray-100" aria-labelledby="search-section-auctions">
              {#each results.auctions as auction (auction.id)}
                {@const index = allResults.findIndex(r => r.type === 'auctions' && r.item.id === auction.id)}
                <li>
                  <button
                    type="button"
                    class="w-full block hover:bg-gray-50 {selectedIndex === index ? 'bg-indigo-50' : ''} 
                      transition-colors duration-100 rounded-lg p-3 text-left"
                    on:click={() => handleResultClick({ type: 'auctions', item: auction })}
                    aria-selected={selectedIndex === index}
                  >
                    <div class="flex items-start">
                      <!-- Auction image -->
                      <div class="flex-shrink-0 h-12 w-12 rounded-md bg-gray-200 overflow-hidden">
                        {#if auction.image_url || auction.main_image}
                          <img 
                            src={auction.image_url || auction.main_image} 
                            alt={auction.title} 
                            class="h-full w-full object-cover"
                            on:error={(e) => e.target.src = 'https://via.placeholder.com/400?text=No+Image'}
                          />
                        {:else}
                          <div class="h-full w-full bg-indigo-100 flex items-center justify-center text-indigo-500">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
                            </svg>
                          </div>
                        {/if}
                      </div>
                      
                      <!-- Auction details -->
                      <div class="ml-4 flex-1">
                        <div class="flex justify-between">
                          <p class="text-sm font-medium text-gray-900">
                            {@html highlightMatch(auction.title, searchQuery)}
                          </p>
                          <p class="text-sm font-semibold text-indigo-600 whitespace-nowrap ml-4">
                            {formatPrice(auction.current_price, auction.currency)}
                          </p>
                        </div>
                        <p class="mt-1 text-xs text-gray-500">
                          {truncateDescription(auction.description)}
                        </p>
                        <div class="mt-2 flex items-center text-xs text-gray-500">
                          <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                            {auction.status}
                          </span>
                          <span class="mx-2">•</span>
                          <span>Ends {new Date(auction.end_time).toLocaleDateString()}</span>
                        </div>
                      </div>
                    </div>
                  </button>
                </li>
              {/each}
            </ul>
          </div>
        {/if}
        
        {#if visibleSections.includes('categories')}
          <div class="mb-4">
            <h3 id="search-section-categories" class="text-xs font-semibold text-gray-500 uppercase tracking-wider px-4 py-2">
              Categories
            </h3>
            <ul class="divide-y divide-gray-100" aria-labelledby="search-section-categories">
              {#each results.categories as category (category.id)}
                {@const index = allResults.findIndex(r => r.type === 'categories' && r.item.id === category.id)}
                <li>
                  <button
                    type="button"
                    class="w-full block hover:bg-gray-50 {selectedIndex === index ? 'bg-indigo-50' : ''} 
                      transition-colors duration-100 rounded-lg p-3 text-left"
                    on:click={() => handleResultClick({ type: 'categories', item: category })}
                    aria-selected={selectedIndex === index}
                  >
                    <div class="flex items-center">
                      <!-- Category icon -->
                      <div class="flex-shrink-0 h-10 w-10 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-600">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                          <path d="M7 3a1 1 0 000 2h6a1 1 0 100-2H7zM4 7a1 1 0 011-1h10a1 1 0 110 2H5a1 1 0 01-1-1zM2 11a2 2 0 012-2h12a2 2 0 012 2v4a2 2 0 01-2 2H4a2 2 0 01-2-2v-4z" />
                        </svg>
                      </div>
                      
                      <!-- Category details -->
                      <div class="ml-4">
                        <p class="text-sm font-medium text-gray-900">
                          {@html highlightMatch(category.name, searchQuery)}
                        </p>
                        <p class="text-xs text-gray-500">
                          {category.auction_count || 0} auctions
                        </p>
                      </div>
                    </div>
                  </button>
                </li>
              {/each}
            </ul>
          </div>
        {/if}
        
        {#if visibleSections.includes('users')}
          <div class="mb-4">
            <h3 id="search-section-users" class="text-xs font-semibold text-gray-500 uppercase tracking-wider px-4 py-2">
              Users
            </h3>
            <ul class="divide-y divide-gray-100" aria-labelledby="search-section-users">
              {#each results.users as user (user.id)}
                {@const index = allResults.findIndex(r => r.type === 'users' && r.item.id === user.id)}
                <li>
                  <button
                    type="button"
                    class="w-full block hover:bg-gray-50 {selectedIndex === index ? 'bg-indigo-50' : ''} 
                      transition-colors duration-100 rounded-lg p-3 text-left"
                    on:click={() => handleResultClick({ type: 'users', item: user })}
                    aria-selected={selectedIndex === index}
                  >
                    <div class="flex items-center">
                      <!-- User avatar -->
                      <div class="flex-shrink-0 h-10 w-10 rounded-full bg-gray-200 overflow-hidden">
                        <img 
                          src={user.avatar || `https://ui-avatars.com/api/?name=${user.first_name}+${user.last_name}&background=6366F1&color=fff`}
                          alt={`${user.first_name} ${user.last_name}`}
                          class="h-full w-full object-cover"
                          on:error={(e) => e.target.src = `https://ui-avatars.com/api/?name=${user.first_name}+${user.last_name}&background=6366F1&color=fff`}
                        />
                      </div>
                      
                      <!-- User details -->
                      <div class="ml-4">
                        <p class="text-sm font-medium text-gray-900">
                          {@html highlightMatch(`${user.first_name} ${user.last_name}`, searchQuery)}
                        </p>
                        <p class="text-xs text-gray-500">
                          {user.email ? user.email : 'User'}
                        </p>
                      </div>
                    </div>
                  </button>
                </li>
              {/each}
            </ul>
          </div>
        {/if}
      {/if}
    </div>
    
    <!-- Footer with keyboard shortcuts -->
    <div class="px-4 py-3 bg-gray-50 text-xs text-gray-500 rounded-b-xl flex items-center justify-between">
      <div>
        <span class="mr-3">Press <kbd class="px-1 py-0.5 rounded bg-white border border-gray-300 shadow-sm">↑</kbd> <kbd class="px-1 py-0.5 rounded bg-white border border-gray-300 shadow-sm">↓</kbd> to navigate</span>
        <span class="mr-3">Press <kbd class="px-1 py-0.5 rounded bg-white border border-gray-300 shadow-sm">Enter</kbd> to select</span>
        <span>Press <kbd class="px-1 py-0.5 rounded bg-white border border-gray-300 shadow-sm">Esc</kbd> to close</span>
      </div>
      <div>
        {#if allResults.length > 0}
          <span>{allResults.length} results</span>
        {/if}
      </div>
    </div>
  </div>
</div>

<style>
/* Style for keyboard keys */
kbd {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  font-size: 0.75rem;
  line-height: 1rem;
}

/* Custom scrollbar for results */
.overflow-y-auto {
  scrollbar-width: thin;
  scrollbar-color: #9ca3af #f3f4f6;
}

.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f3f4f6;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background-color: #9ca3af;
  border-radius: 3px;
}

/* Highlighted text in search results */
:global(mark) {
  background-color: #FEF3C7; /* Tailwind's yellow-100 */
  color: #1F2937; /* Tailwind's gray-800 */
  border-radius: 0.125rem;
  padding: 0 0.125rem;
}
</style>