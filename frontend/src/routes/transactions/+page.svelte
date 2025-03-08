<!-- src/routes/transactions/+page.svelte -->
<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { fade, fly, slide } from 'svelte/transition';
  import { quintOut, cubicOut } from 'svelte/easing';
  import { isAuthenticated, user } from '$lib/stores/authStore';
  import { notificationStore } from '$lib/stores/notificationStore';
  import { api } from '$lib/api';
  import { searchOpen } from '$lib/stores/uiStore';
  
  // UI Components
  import Button from '$lib/components/ui/Button.svelte';
  import Spinner from '$lib/components/ui/Spinner.svelte';
  import Alert from '$lib/components/ui/Alert.svelte';
  import Badge from '$lib/components/ui/Badge.svelte';
  import Dropdown from '$lib/components/ui/Dropdown.svelte';
  import Modal from '$lib/components/ui/Modal.svelte';
  import DateRangePicker from '$lib/components/ui/DateRangePicker.svelte';
  import SearchOverlay from '$lib/components/search/SearchOverlay.svelte';
  
  // Data states
  let transactions = [];
  let filteredTransactions = [];
  let loading = true;
  let error = null;
  let exportLoading = false;
  
  // UI states
  let selectedTransaction = null;
  let isDetailModalOpen = false;
  let isFilterMenuOpen = false;
  let searchQuery = '';
  let dateRange = { from: null, to: null };
  let skeletonCount = 5;
  
  // Pagination
  let pagination = {
    page: 1,
    limit: 10,
    total: 0,
    totalPages: 0
  };
  
  // Filter states
  let activeTab = 'all';
  let filterType = 'all';
  let filterStatus = 'all';
  let sortBy = 'date';
  let sortDirection = 'desc';
  
  // Filter options
  const tabs = [
    { id: 'all', label: 'All' },
    { id: 'purchases', label: 'Purchases' },
    { id: 'sales', label: 'Sales' },
    { id: 'payouts', label: 'Payouts' },
    { id: 'refunds', label: 'Refunds' }
  ];
  
  const transactionTypes = [
    { id: 'all', label: 'All Types' },
    { id: 'purchase', label: 'Purchase' },
    { id: 'sale', label: 'Sale' },
    { id: 'payout', label: 'Payout' },
    { id: 'refund', label: 'Refund' },
    { id: 'fee', label: 'Platform Fee' }
  ];
  
  const statusOptions = [
    { id: 'all', label: 'All Statuses' },
    { id: 'pending', label: 'Pending' },
    { id: 'processing', label: 'Processing' },
    { id: 'completed', label: 'Completed' },
    { id: 'failed', label: 'Failed' },
    { id: 'refunded', label: 'Refunded' },
    { id: 'disputed', label: 'Disputed' }
  ];
  
  const sortOptions = [
    { id: 'date', label: 'Date' },
    { id: 'amount', label: 'Amount' },
    { id: 'status', label: 'Status' }
  ];
  
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
  function formatDate(dateString, includeTime = true) {
    if (!dateString) return '';
    
    try {
      const date = new Date(dateString);
      if (isNaN(date.getTime())) {
        console.warn('Invalid date for formatting:', dateString);
        return '';
      }
      
      if (includeTime) {
        return new Intl.DateTimeFormat('en-US', {
          year: 'numeric',
          month: 'short',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        }).format(date);
      } else {
        return new Intl.DateTimeFormat('en-US', {
          year: 'numeric',
          month: 'short',
          day: 'numeric'
        }).format(date);
      }
    } catch (err) {
      console.error('Error formatting date:', err);
      return '';
    }
  }
  
  // Format transaction type display
  function formatTransactionType(type) {
    if (!type) return 'Unknown';
    
    return type.charAt(0).toUpperCase() + type.slice(1).toLowerCase();
  }
  
  // Get status badge configuration
  function getStatusBadge(status) {
    if (!status) return { color: 'default', icon: 'help-circle', label: 'Unknown' };
    
    const normalizedStatus = typeof status === 'string' ? status.toLowerCase() : '';
    
    switch(normalizedStatus) {
      case 'pending':
        return { color: 'warning', icon: 'clock', label: 'Pending' };
      case 'processing':
        return { color: 'info', icon: 'refresh-cw', label: 'Processing' };
      case 'completed':
        return { color: 'success', icon: 'check-circle', label: 'Completed' };
      case 'failed':
        return { color: 'error', icon: 'x-circle', label: 'Failed' };
      case 'refunded':
        return { color: 'info', icon: 'rotate-ccw', label: 'Refunded' };
      case 'disputed':
        return { color: 'error', icon: 'alert-triangle', label: 'Disputed' };
      default:
        return { color: 'default', icon: 'help-circle', label: status || 'Unknown' };
    }
  }
  
  // Get transaction type icon
  function getTransactionTypeIcon(type) {
    if (!type) return 'dollar-sign';
    
    const normalizedType = typeof type === 'string' ? type.toLowerCase() : '';
    
    switch(normalizedType) {
      case 'purchase':
        return 'shopping-cart';
      case 'sale':
        return 'tag';
      case 'payout':
        return 'credit-card';
      case 'refund':
        return 'rotate-ccw';
      case 'fee':
        return 'percent';
      default:
        return 'dollar-sign';
    }
  }
  
  // Load transactions data
  async function loadTransactions(resetPage = false) {
    if (!$isAuthenticated) {
      goto('/login?redirect=/transactions');
      return;
    }
    
    if (resetPage) {
      pagination.page = 1;
    }
    
    try {
      loading = true;
      error = null;
      
      // Prepare API query parameters
      const params = {
        page: pagination.page,
        limit: pagination.limit,
        sort_by: sortBy,
        direction: sortDirection
      };
      
      // Add filters
      if (activeTab !== 'all') {
        params.category = activeTab;
      }
      
      if (filterType !== 'all') {
        params.type = filterType;
      }
      
      if (filterStatus !== 'all') {
        params.status = filterStatus;
      }
      
      if (searchQuery.trim()) {
        params.search = searchQuery.trim();
      }
      
      if (dateRange.from) {
        params.date_from = dateRange.from.toISOString().split('T')[0];
      }
      
      if (dateRange.to) {
        params.date_to = dateRange.to.toISOString().split('T')[0];
      }
      
      // Use standard API pattern
      const response = await api.transaction.list({ params });
      
      // Process response
      if (response && Array.isArray(response.results)) {
        transactions = response.results.map(tx => ({
          ...tx,
          statusBadge: getStatusBadge(tx.status)
        }));
        
        // Update pagination if count exists
        pagination = {
          ...pagination,
          total: response.count || 0,
          totalPages: response.total_pages || Math.ceil((response.count || 0) / pagination.limit)
        };
      } else {
        // Handle empty or invalid response
        transactions = [];
        pagination = {
          ...pagination,
          total: 0,
          totalPages: 0
        };
      }
      
      applyFilters();
    } catch (err) {
      console.error('Error loading transactions:', err);
      const errorMessage = err.message || err.error || 'Unknown error';
      error = `Failed to load transactions: ${errorMessage}`;
      notificationStore.error(error);
      transactions = [];
    } finally {
      loading = false;
    }
  }
  
  // Apply client-side filters and sorting
  function applyFilters() {
    filteredTransactions = [...transactions];
  }
  
  // Change page
  function changePage(newPage) {
    if (newPage < 1 || newPage > pagination.totalPages) return;
    
    pagination.page = newPage;
    loadTransactions(false);
  }
  
  // Set active tab and reload data
  function setActiveTab(tabId) {
    activeTab = tabId;
    loadTransactions(true);
  }
  
  // Reset all filters
  function resetFilters() {
    activeTab = 'all';
    filterType = 'all';
    filterStatus = 'all';
    searchQuery = '';
    dateRange = { from: null, to: null };
    
    loadTransactions(true);
  }
  
  // Show transaction details
  function showTransactionDetails(transaction) {
    selectedTransaction = transaction;
    isDetailModalOpen = true;
  }
  
  // Open global search overlay
  function openGlobalSearch() {
    searchOpen.set(true);
  }
  
  // Handle search result selection from SearchOverlay
  function handleSearchResult(result) {
    if (result.type === 'auctions') {
      goto(`/auctions/${result.item.id}`);
    } else if (result.type === 'transactions') {
      // If it's a transaction result, show its details
      showTransactionDetails(result.item);
    } else if (result.type === 'categories') {
      // If it's a category, filter by that category
      filterType = result.item.id;
      loadTransactions(true);
    }
  }
  
  // Export transactions as CSV
  async function exportTransactions() {
    try {
      exportLoading = true;
      
      // Prepare export parameters (same as current filters)
      const params = {
        format: 'csv',
        sort_by: sortBy,
        direction: sortDirection
      };
      
      if (activeTab !== 'all') {
        params.category = activeTab;
      }
      
      if (filterType !== 'all') {
        params.type = filterType;
      }
      
      if (filterStatus !== 'all') {
        params.status = filterStatus;
      }
      
      if (searchQuery.trim()) {
        params.search = searchQuery.trim();
      }
      
      if (dateRange.from) {
        params.date_from = dateRange.from.toISOString().split('T')[0];
      }
      
      if (dateRange.to) {
        params.date_to = dateRange.to.toISOString().split('T')[0];
      }
      
      // Use standard API pattern
      const response = await api.transaction.export({ params });
      
      if (response && response.data) {
        // Create download link
        const blob = new Blob([response.data], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = `transactions_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        
        // Clean up
        setTimeout(() => {
          document.body.removeChild(a);
          window.URL.revokeObjectURL(url);
        }, 100);
        
        notificationStore.success('Transactions exported successfully');
      } else {
        throw new Error('Export response is empty or invalid');
      }
    } catch (err) {
      console.error('Error preparing export:', err);
      notificationStore.error('Failed to export transactions: ' + (err.message || 'Unknown error'));
    } finally {
      exportLoading = false;
    }
  }
  
  // Initialize data loading with improved authentication handling
  onMount(() => {
    const unsubscribe = isAuthenticated.subscribe(value => {
      if (value === true) {
        // Only load data when we're certain authentication is complete and successful
        loadTransactions();
      } else if (value === false) {
        // Redirect if definitely not authenticated
        goto('/login?redirect=/transactions');
      }
      // If undefined, still initializing - do nothing yet
    });
    
    // Cleanup subscription on component unmount
    return () => {
      unsubscribe();
    };
  });
</script>

<svelte:head>
  <title>Transaction History | GUDIC</title>
  <meta name="description" content="View your transaction history including purchases, sales, payouts and refunds." />
</svelte:head>

{#if $searchOpen}
  <SearchOverlay on:select={event => handleSearchResult(event.detail)} />
{/if}

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
  <!-- Page header with animated welcome -->
  <div class="mb-6" in:fly={{ y: -20, duration: 500 }}>
    <h1 class="text-3xl font-bold text-gray-900 flex items-center">
      <span class="text-transparent bg-clip-text bg-gradient-to-r from-primary-blue to-secondary-blue">
        Transaction History
      </span>
      {#if !loading && pagination.total > 0}
        <span class="ml-3 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-blue/10 text-secondary-blue">
          {pagination.total} {pagination.total === 1 ? 'transaction' : 'transactions'}
        </span>
      {/if}
    </h1>
    <p class="mt-2 text-gray-600 max-w-3xl">
      View and manage your complete financial history including purchases, sales, payouts, and refunds.
    </p>
  </div>
  
  <!-- Tab navigation -->
  <div class="mb-5" in:fade={{ delay: 100, duration: 300 }}>
    <div class="border-b border-gray-200">
      <nav class="-mb-px flex space-x-8 overflow-x-auto hide-scrollbar">
        {#each tabs as tab}
          <button
            class="whitespace-nowrap py-3 px-1 border-b-2 font-medium text-sm
              {activeTab === tab.id 
                ? 'border-primary-blue text-primary-blue' 
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
            on:click={() => setActiveTab(tab.id)}
          >
            {tab.label}
            {#if tab.id !== 'all' && transactions.length > 0}
              <span class="ml-1 text-xs rounded-full bg-gray-100 px-2 py-0.5">
                {transactions.filter(t => t.category === tab.id).length}
              </span>
            {/if}
          </button>
        {/each}
      </nav>
    </div>
  </div>
  
  <!-- Filter section -->
  <div class="mb-5 bg-white rounded-xl shadow-sm border border-gray-200 p-4" in:fade={{ delay: 200, duration: 300 }}>
    <div class="flex flex-col md:flex-row space-y-4 md:space-y-0 md:justify-between md:items-end">
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 w-full md:w-auto">
        <!-- Transaction type filter -->
        <div>
          <label for="filter-type" class="block text-sm font-medium text-gray-700 mb-1">
            Transaction Type
          </label>
          <select
            id="filter-type"
            bind:value={filterType}
            on:change={() => loadTransactions(true)}
            class="bg-white block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-blue focus:border-primary-blue sm:text-sm rounded-md"
          >
            {#each transactionTypes as type}
              <option value={type.id}>{type.label}</option>
            {/each}
          </select>
        </div>
        
        <!-- Status filter -->
        <div>
          <label for="filter-status" class="block text-sm font-medium text-gray-700 mb-1">
            Status
          </label>
          <select
            id="filter-status"
            bind:value={filterStatus}
            on:change={() => loadTransactions(true)}
            class="bg-white block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-blue focus:border-primary-blue sm:text-sm rounded-md"
          >
            {#each statusOptions as status}
              <option value={status.id}>{status.label}</option>
            {/each}
          </select>
        </div>
        
        <!-- Date range filter -->
        <div>
          <label for="filter-date" class="block text-sm font-medium text-gray-700 mb-1">
            Date Range
          </label>
          <DateRangePicker
            startDate={dateRange.from}
            endDate={dateRange.to}
            on:change={({detail}) => {
              if (detail) {
                dateRange = { from: detail.startDate, to: detail.endDate };
                loadTransactions(true);
              }
            }}
            placeholder="Select dates"
            class="w-full"
          />
        </div>
      </div>
      
      <div class="flex flex-row space-x-2">
        <!-- Search with ability to open global search -->
        <div class="relative w-full md:w-64">
          <div class="flex">
            <input
              type="text"
              placeholder="Search transactions..."
              bind:value={searchQuery}
              on:keyup={(e) => e.key === 'Enter' && loadTransactions(true)}
              class="pl-9 pr-3 py-2 w-full bg-white border border-gray-300 rounded-l-md text-sm focus:ring-2 focus:ring-primary-blue/30 focus:border-primary-blue"
            />
            <button
              class="bg-gray-100 hover:bg-gray-200 px-3 border border-l-0 border-gray-300 rounded-r-md flex items-center"
              on:click={openGlobalSearch}
              title="Open advanced search"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h7" />
              </svg>
            </button>
          </div>
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </div>
        
        <!-- Reset filters -->
        <Button
          variant="outline"
          size="sm"
          on:click={resetFilters}
          title="Reset all filters"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </Button>
        
        <!-- Export transactions -->
        <Button
          variant="outline"
          size="sm"
          on:click={exportTransactions}
          loading={exportLoading}
          disabled={loading || transactions.length === 0}
          title="Export transactions as CSV"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Export
        </Button>
      </div>
    </div>
  </div>
  
  <!-- Content section -->
  <div>
    <!-- Loading state with skeletons -->
    {#if loading}
      <div class="space-y-3" in:fade={{ duration: 300 }}>
        {#each Array(skeletonCount) as _, i}
          <div class="bg-white shadow-sm rounded-lg border border-gray-200 overflow-hidden animate-pulse p-4">
            <div class="flex justify-between">
              <div class="flex space-x-4">
                <!-- Transaction icon skeleton -->
                <div class="h-12 w-12 rounded-full bg-gray-200"></div>
                
                <!-- Transaction details skeleton -->
                <div class="space-y-2">
                  <div class="h-4 bg-gray-200 rounded w-32"></div>
                  <div class="h-4 bg-gray-200 rounded w-48"></div>
                </div>
              </div>
              
              <!-- Amount & Status skeleton -->
              <div class="text-right space-y-2">
                <div class="h-4 bg-gray-200 rounded w-24 ml-auto"></div>
                <div class="h-6 bg-gray-200 rounded-full w-20 ml-auto"></div>
              </div>
            </div>
          </div>
        {/each}
      </div>
    
    <!-- Error state -->
    {:else if error}
      <Alert variant="error" class="my-6">
        <div class="flex flex-col items-center p-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-red-500 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <p class="font-medium mb-2">{error}</p>
          <Button 
            variant="primary" 
            size="sm" 
            on:click={() => loadTransactions(true)}
          >
            Try Again
          </Button>
        </div>
      </Alert>
    
    <!-- Empty state -->
    {:else if transactions.length === 0}
      <div class="bg-white shadow-sm rounded-lg border border-gray-200 p-10 text-center" in:fade={{ duration: 300 }}>
        <div class="max-w-md mx-auto">
          <div class="w-20 h-20 mx-auto bg-primary-blue/10 rounded-full flex items-center justify-center mb-6">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-primary-blue" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
            </svg>
          </div>
          <h3 class="text-lg font-semibold text-gray-900 mb-2">No transactions found</h3>
          <p class="text-gray-600 mb-6">
            {#if filterType !== 'all' || filterStatus !== 'all' || searchQuery || dateRange.from || dateRange.to}
              No transactions match your current filters. Try adjusting your search criteria.
            {:else}
              You don't have any transactions yet. Transactions will appear here once you make a purchase or sell an item.
            {/if}
          </p>
          
          {#if filterType !== 'all' || filterStatus !== 'all' || searchQuery || dateRange.from || dateRange.to}
            <Button 
              variant="outline" 
              size="md"
              on:click={resetFilters}
            >
              Clear Filters
            </Button>
          {:else}
            <Button 
              href="/auctions" 
              variant="primary" 
              size="md"
            >
              Browse Auctions
            </Button>
          {/if}
        </div>
      </div>
    
    <!-- Transactions list -->
    {:else}
      <div class="space-y-3">
        {#each transactions as transaction, i (transaction.id)}
          <div 
            class="bg-white shadow-sm rounded-lg border border-gray-200 overflow-hidden hover:shadow-md hover:-translate-y-0.5 transition-all duration-300 cursor-pointer"
            on:click={() => showTransactionDetails(transaction)}
            in:fly={{ y: 20, delay: i * 50, duration: 300, easing: quintOut }}
          >
            <div class="p-4">
              <div class="flex justify-between">
                <!-- Transaction icon and basic info -->
                <div class="flex space-x-4">
                  <div class="h-12 w-12 rounded-full bg-primary-blue/10 flex items-center justify-center text-primary-blue">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                    </svg>
                  </div>
                  
                  <div>
                    <p class="font-medium text-gray-900">
                      {formatTransactionType(transaction.type)} 
                      {transaction.reference_number ? `#${transaction.reference_number}` : ''}
                    </p>
                    <p class="text-sm text-gray-600">
                      {transaction.description || 
                        `${formatTransactionType(transaction.type)} for ${transaction.auction_details?.title || 'Unknown item'}`}
                    </p>
                    <p class="text-sm text-gray-500 mt-1">
                      {formatDate(transaction.created_at)}
                    </p>
                  </div>
                </div>
                
                <!-- Amount and status -->
                <div class="text-right">
                  <p class={`text-lg font-semibold ${transaction.direction === 'outgoing' ? 'text-red-600' : 'text-green-600'}`}>
                    {transaction.direction === 'outgoing' ? '-' : '+'}{formatCurrency(transaction.amount, transaction.currency)}
                  </p>
                  
                  <div class="mt-1">
                    {#if transaction.statusBadge}
                      <span 
                        class={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                          ${transaction.statusBadge.color === 'success' ? 'bg-green-100 text-green-800' : 
                            transaction.statusBadge.color === 'warning' ? 'bg-yellow-100 text-yellow-800' : 
                            transaction.statusBadge.color === 'error' ? 'bg-red-100 text-red-800' : 
                            transaction.statusBadge.color === 'info' ? 'bg-blue-100 text-blue-800' : 
                            'bg-gray-100 text-gray-800'}`}
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        {transaction.statusBadge.label}
                      </span>
                    {/if}
                  </div>
                </div>
              </div>
            </div>
          </div>
        {/each}
      </div>
      
      <!-- Pagination -->
      {#if pagination.totalPages > 1}
        <div class="mt-6 flex justify-center">
          <nav class="relative z-0 inline-flex rounded-md shadow-sm" aria-label="Pagination">
            <!-- Previous button -->
            <button
              class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              on:click={() => changePage(pagination.page - 1)}
              disabled={pagination.page === 1}
            >
              <span class="sr-only">Previous</span>
              <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" />
              </svg>
            </button>
            
            <!-- Fixed simplified pagination approach -->
            {#if pagination.totalPages <= 5}
              <!-- Show all pages if 5 or fewer -->
              {#each Array(pagination.totalPages) as _, i}
                <button
                  class={`relative inline-flex items-center px-4 py-2 border text-sm font-medium
                    ${pagination.page === i + 1 
                      ? 'z-10 bg-primary-blue text-white border-primary-blue'
                      : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'}`}
                  on:click={() => changePage(i + 1)}
                >
                  {i + 1}
                </button>
              {/each}
            {:else}
              <!-- First page -->
              <button
                class={`relative inline-flex items-center px-4 py-2 border text-sm font-medium
                  ${pagination.page === 1 
                    ? 'z-10 bg-primary-blue text-white border-primary-blue'
                    : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'}`}
                on:click={() => changePage(1)}
              >
                1
              </button>
              
              <!-- Ellipsis if not showing second page -->
              {#if pagination.page > 3}
                <span class="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700">
                  ...
                </span>
              {/if}
              
              <!-- Pages around current page -->
              {#each Array(Math.min(3, pagination.totalPages - 2)) as _, i}
                {@const pageNum = pagination.page <= 3 
                  ? i + 2 
                  : pagination.page >= pagination.totalPages - 2 
                    ? pagination.totalPages - 4 + i 
                    : pagination.page - 1 + i}
                
                {#if pageNum > 1 && pageNum < pagination.totalPages}
                  <button
                    class={`relative inline-flex items-center px-4 py-2 border text-sm font-medium
                      ${pagination.page === pageNum 
                        ? 'z-10 bg-primary-blue text-white border-primary-blue'
                        : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'}`}
                    on:click={() => changePage(pageNum)}
                  >
                    {pageNum}
                  </button>
                {/if}
              {/each}
              
              <!-- Ellipsis if not showing second-to-last page -->
              {#if pagination.page < pagination.totalPages - 2}
                <span class="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700">
                  ...
                </span>
              {/if}
              
              <!-- Last page -->
              <button
                class={`relative inline-flex items-center px-4 py-2 border text-sm font-medium
                  ${pagination.page === pagination.totalPages 
                    ? 'z-10 bg-primary-blue text-white border-primary-blue'
                    : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'}`}
                on:click={() => changePage(pagination.totalPages)}
              >
                {pagination.totalPages}
              </button>
            {/if}
            
            <!-- Next button -->
            <button
              class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              on:click={() => changePage(pagination.page + 1)}
              disabled={pagination.page === pagination.totalPages}
            >
              <span class="sr-only">Next</span>
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

<!-- Transaction Detail Modal -->
{#if isDetailModalOpen && selectedTransaction}
  <Modal
    open={isDetailModalOpen}
    title="Transaction Details"
    on:close={() => isDetailModalOpen = false}
    size="md"
    marginY={20}
  >
    <div class="p-4">
      <!-- Main transaction info -->
      <div class="flex justify-between items-start mb-4">
        <div>
          <h2 class="text-xl font-bold text-gray-900">{formatTransactionType(selectedTransaction.type)}</h2>
          <p class="text-gray-600">{formatDate(selectedTransaction.created_at)}</p>
        </div>
        
        <div class="text-right">
          <p class={`text-xl font-bold ${selectedTransaction.direction === 'outgoing' ? 'text-red-600' : 'text-green-600'}`}>
            {selectedTransaction.direction === 'outgoing' ? '-' : '+'}{formatCurrency(selectedTransaction.amount, selectedTransaction.currency)}
          </p>
          
          {#if selectedTransaction.statusBadge}
            <span 
              class={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                ${selectedTransaction.statusBadge.color === 'success' ? 'bg-green-100 text-green-800' : 
                selectedTransaction.statusBadge.color === 'warning' ? 'bg-yellow-100 text-yellow-800' : 
                selectedTransaction.statusBadge.color === 'error' ? 'bg-red-100 text-red-800' : 
                selectedTransaction.statusBadge.color === 'info' ? 'bg-blue-100 text-blue-800' : 
                'bg-gray-100 text-gray-800'}`}
            >
              {selectedTransaction.statusBadge.label}
            </span>
          {/if}
        </div>
      </div>
      
      <!-- Transaction details -->
      <div class="bg-gray-50 rounded-lg p-4 mb-4">
        <h3 class="font-medium text-gray-900 mb-2">Transaction Details</h3>
        
        <div class="grid grid-cols-2 gap-y-2 text-sm">
          <div class="text-gray-600">Transaction ID</div>
          <div class="text-gray-900 font-medium">{selectedTransaction.id}</div>
          
          {#if selectedTransaction.reference_number}
            <div class="text-gray-600">Reference Number</div>
            <div class="text-gray-900 font-medium">{selectedTransaction.reference_number}</div>
          {/if}
          
          <div class="text-gray-600">Type</div>
          <div class="text-gray-900 font-medium">{formatTransactionType(selectedTransaction.type)}</div>
          
          <div class="text-gray-600">Status</div>
          <div class="text-gray-900 font-medium">{selectedTransaction.status}</div>
          
          <div class="text-gray-600">Date</div>
          <div class="text-gray-900 font-medium">{formatDate(selectedTransaction.created_at)}</div>
          
          {#if selectedTransaction.payment_method}
            <div class="text-gray-600">Payment Method</div>
            <div class="text-gray-900 font-medium">{selectedTransaction.payment_method}</div>
          {/if}
        </div>
      </div>
      
      <!-- Related item (if applicable) -->
      {#if selectedTransaction.auction_details}
        <div class="border border-gray-200 rounded-lg p-4 mb-4">
          <h3 class="font-medium text-gray-900 mb-2">Related Item</h3>
          
          <div class="flex items-center">
            {#if selectedTransaction.auction_details.image_url}
              <div class="flex-shrink-0 h-16 w-16 rounded-md overflow-hidden bg-gray-100 mr-4">
                <img 
                  src={selectedTransaction.auction_details.image_url} 
                  alt={selectedTransaction.auction_details.title}
                  class="h-full w-full object-cover"
                />
              </div>
            {/if}
            
            <div>
              <a 
                href={`/auctions/${selectedTransaction.auction_details.id}`}
                class="font-medium text-primary-blue hover:underline"
              >
                {selectedTransaction.auction_details.title}
              </a>
              
              <p class="text-sm text-gray-600 mt-1">
                {selectedTransaction.type === 'purchase' ? 'Purchased from' : 'Sold to'} 
                {selectedTransaction.auction_details.seller_name || selectedTransaction.auction_details.buyer_name || 'Unknown user'}
              </p>
            </div>
          </div>
        </div>
      {/if}
      
      <!-- Payment breakdown -->
      <div class="border-t border-gray-200 pt-4 mb-4">
        <h3 class="font-medium text-gray-900 mb-2">Payment Breakdown</h3>
        
        <div class="space-y-2">
          {#if selectedTransaction.item_price !== undefined}
            <div class="flex justify-between text-sm">
              <span class="text-gray-600">Item Price</span>
              <span class="text-gray-900">{formatCurrency(selectedTransaction.item_price, selectedTransaction.currency)}</span>
            </div>
          {/if}
          
          {#if selectedTransaction.service_fee !== undefined}
            <div class="flex justify-between text-sm">
              <span class="text-gray-600">Service Fee</span>
              <span class="text-gray-900">{formatCurrency(selectedTransaction.service_fee, selectedTransaction.currency)}</span>
            </div>
          {/if}
          
          {#if selectedTransaction.shipping_fee !== undefined}
            <div class="flex justify-between text-sm">
              <span class="text-gray-600">Shipping</span>
              <span class="text-gray-900">{formatCurrency(selectedTransaction.shipping_fee, selectedTransaction.currency)}</span>
            </div>
          {/if}
          
          {#if selectedTransaction.tax !== undefined}
            <div class="flex justify-between text-sm">
              <span class="text-gray-600">Tax</span>
              <span class="text-gray-900">{formatCurrency(selectedTransaction.tax, selectedTransaction.currency)}</span>
            </div>
          {/if}
          
          {#if selectedTransaction.discount !== undefined}
            <div class="flex justify-between text-sm">
              <span class="text-gray-600">Discount</span>
              <span class="text-green-600">-{formatCurrency(selectedTransaction.discount, selectedTransaction.currency)}</span>
            </div>
          {/if}
          
          <div class="flex justify-between text-sm pt-2 border-t border-gray-200 font-semibold">
            <span>Total</span>
            <span>{formatCurrency(selectedTransaction.amount, selectedTransaction.currency)}</span>
          </div>
        </div>
      </div>
      
      <!-- Action buttons -->
      <div class="flex space-x-3">
        {#if selectedTransaction.receipt_url}
          <Button
            variant="outline"
            fullWidth={true}
            href={selectedTransaction.receipt_url}
            target="_blank"
            rel="noopener noreferrer"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            View Receipt
          </Button>
        {/if}
        
        {#if selectedTransaction.type === 'purchase' && selectedTransaction.status === 'completed' && selectedTransaction.auction_details?.id}
          <Button
            variant="primary"
            fullWidth={true}
            href={`/feedback/${selectedTransaction.auction_details.id}/create`}
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            Leave Feedback
          </Button>
        {/if}
        
        {#if selectedTransaction.can_dispute}
          <Button
            variant="outline"
            fullWidth={true}
            class="text-red-600 border-red-600 hover:bg-red-50"
            href={`/support/dispute/${selectedTransaction.id}`}
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            Report Issue
          </Button>
        {/if}
      </div>
    </div>
  </Modal>
{/if}

<style>
  /* Hide scrollbar but allow scrolling */
  .hide-scrollbar {
    -ms-overflow-style: none;  /* IE and Edge */
    scrollbar-width: none;  /* Firefox */
  }
  .hide-scrollbar::-webkit-scrollbar {
    display: none;  /* Chrome, Safari and Opera */
  }
  
  /* Animation for skeleton loading */
  @keyframes pulse {
    0%, 100% {
      opacity: 1;
    }
    50% {
      opacity: .5;
    }
  }
  
  .animate-pulse {
    animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
  }
</style>