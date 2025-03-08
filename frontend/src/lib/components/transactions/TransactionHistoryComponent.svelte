<!-- src/lib/components/transactions/TransactionHistoryComponent.svelte -->
<script>
  import { onMount } from 'svelte';
  import { api } from '$lib/api';
  import Button from '$lib/components/ui/Button.svelte';
  import Spinner from '$lib/components/ui/Spinner.svelte';
  import Alert from '$lib/components/ui/Alert.svelte';
  
  // Props
  export let title = "Transaction History";
  export let viewAllLink = "/account/transactions";
  export let viewAllLabel = "View All Transactions";
  export let limit = 5;
  export let showHeader = true;
  export let userId = null; // Optional: specific user's transactions
  export let auctionId = null; // Optional: specific auction's transactions
  export let status = null; // Optional: filter by status
  export let compact = false; // Compact display mode

  // State
  let transactions = [];
  let loading = true;
  let error = null;
  let statusFilter = status || 'all';
  
  // Status filter options
  const statusOptions = [
    { value: 'all', label: 'All Statuses' },
    { value: 'PENDING', label: 'Pending' },
    { value: 'PROCESSING', label: 'Processing' },
    { value: 'COMPLETED', label: 'Completed' },
    { value: 'FAILED', label: 'Failed' },
    { value: 'REFUNDED', label: 'Refunded' },
    { value: 'DISPUTED', label: 'Disputed' }
  ];
  
  // Load transactions
  async function loadTransactions() {
    try {
      loading = true;
      error = null;
      
      let params = {
        sort_by: 'created_at',
        direction: 'desc',
        limit
      };
      
      // Add filters if provided
      if (userId) params.winner = userId;
      if (auctionId) params.auction = auctionId;
      if (statusFilter && statusFilter !== 'all') params.status = statusFilter;
      
      const response = await api.transaction.list({
        params
      });
      
      if (response && response.results) {
        transactions = response.results;
      } else {
        transactions = [];
      }
      
      loading = false;
    } catch (err) {
      console.error('Error loading transactions:', err);
      error = 'Failed to load transaction history';
      loading = false;
    }
  }
  
  // Handle status filter change
  function handleStatusChange(event) {
    statusFilter = event.target.value;
    loadTransactions();
  }
  
  // Get status badge class
  function getStatusBadgeClass(status) {
    if (!status) return 'bg-gray-100 text-gray-800';
    
    switch (status) {
      case 'PENDING':
        return 'bg-yellow-100 text-yellow-800';
      case 'PROCESSING':
        return 'bg-blue-100 text-blue-800';
      case 'COMPLETED':
        return 'bg-green-100 text-green-800';
      case 'FAILED':
        return 'bg-red-100 text-red-800';
      case 'REFUNDED':
        return 'bg-purple-100 text-purple-800';
      case 'DISPUTED':
        return 'bg-orange-100 text-orange-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  }
  
  // Get payment method icon
  function getPaymentMethodIcon(method) {
    if (!method) return `<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>`;
    
    switch (method) {
      case 'CREDIT_CARD':
        return `<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
        </svg>`;
      case 'BANK_TRANSFER':
        return `<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 14v3m4-3v3m4-3v3M3 21h18M3 10h18M3 7l9-4 9 4M4 10h16v11H4V10z" />
        </svg>`;
      case 'PAYPAL':
        return `<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2z" />
        </svg>`;
      case 'ESCROW':
        return `<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
        </svg>`;
      default:
        return `<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>`;
    }
  }
  
  // Format currency with better error handling
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

  // Format date with better error handling
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
  
  // Safe format for address
  function safeFormatAddress(address) {
    if (!address) return 'No address provided';
    
    let parts = [];
    if (address.full_name) parts.push(address.full_name);
    if (address.address_line_1) parts.push(address.address_line_1);
    if (address.address_line_2) parts.push(address.address_line_2);
    if (address.city && address.state) parts.push(`${address.city}, ${address.state} ${address.postal_code || ''}`);
    else if (address.city) parts.push(address.city);
    if (address.country) parts.push(address.country);
    if (address.phone_number) parts.push(address.phone_number);
    
    // Return text with line breaks that works in Svelte templates
    return parts.join('\n');
  }
  
  onMount(() => {
    loadTransactions();
  });
</script>

{#if showHeader}
  <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-4 gap-2">
    <h3 class="text-lg font-medium text-text-dark">{title}</h3>
    
    {#if !status}
      <div class="flex space-x-2">
        <select
          bind:value={statusFilter}
          on:change={handleStatusChange}
          class="text-sm border border-gray-300 rounded-md shadow-sm focus:ring-primary-blue focus:border-primary-blue"
        >
          {#each statusOptions as option}
            <option value={option.value}>{option.label}</option>
          {/each}
        </select>
        
        <Button href={viewAllLink} variant="outline" size="sm">
          {viewAllLabel}
        </Button>
      </div>
    {:else}
      <Button href={viewAllLink} variant="outline" size="sm">
        {viewAllLabel}
      </Button>
    {/if}
  </div>
{/if}

{#if loading}
  <div class="flex justify-center items-center py-4">
    <Spinner size="md" />
  </div>
{:else if error}
  <Alert variant="error" class="mb-4">
    {error}
    <div class="mt-2">
      <button 
        type="button" 
        class="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        on:click={loadTransactions}
      >
        Try Again
      </button>
    </div>
  </Alert>
{:else if transactions.length === 0}
  <div class="text-center py-3 text-text-medium bg-neutral-50 rounded-md">
    <p>No transactions found</p>
  </div>
{:else if compact}
  <!-- Compact View -->
  <div class="space-y-2">
    {#each transactions as transaction}
      <div class="flex justify-between items-center p-3 bg-white border border-primary-blue/10 rounded-lg hover:bg-primary-blue/5 transition-colors">
        <div>
          <div class="font-medium text-text-dark">
            {transaction.auction_details?.title || `Auction #${transaction.auction || transaction.auction_id || ''}`}
          </div>
          <div class="text-sm text-text-medium flex items-center">
            <span class="mr-1">
              {@html getPaymentMethodIcon(transaction.payment_method)}
            </span>
            {formatDate(transaction.created_at)}
          </div>
        </div>
        <div class="text-right">
          <div class="font-medium text-secondary-blue">
            {formatCurrency(transaction.amount, transaction.currency || 'USD')}
          </div>
          <div class="mt-1">
            <span class="px-2 py-0.5 rounded-full text-xs font-medium {getStatusBadgeClass(transaction.status)}">
              {transaction.status}
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
          <th scope="col" class="px-4 py-2 text-left text-xs font-medium text-text-medium tracking-wider">
            Auction
          </th>
          <th scope="col" class="px-4 py-2 text-left text-xs font-medium text-text-medium tracking-wider">
            Amount
          </th>
          <th scope="col" class="px-4 py-2 text-left text-xs font-medium text-text-medium tracking-wider">
            Payment Method
          </th>
          <th scope="col" class="px-4 py-2 text-left text-xs font-medium text-text-medium tracking-wider">
            Date
          </th>
          <th scope="col" class="px-4 py-2 text-left text-xs font-medium text-text-medium tracking-wider">
            Status
          </th>
          <th scope="col" class="px-4 py-2 text-right text-xs font-medium text-text-medium tracking-wider">
            Actions
          </th>
        </tr>
      </thead>
      <tbody class="bg-white divide-y divide-primary-blue/10">
        {#each transactions as transaction}
          <tr class="hover:bg-neutral-50">
            <td class="px-4 py-2 whitespace-nowrap">
              <a 
                href="/auctions/{transaction.auction || transaction.auction_id}" 
                class="text-sm font-medium text-text-dark hover:text-secondary-blue"
              >
                {transaction.auction_details?.title || `Auction #${transaction.auction || transaction.auction_id || ''}`}
              </a>
            </td>
            <td class="px-4 py-2 whitespace-nowrap">
              <span class="text-sm font-medium text-secondary-blue">
                {formatCurrency(transaction.amount, transaction.currency || 'USD')}
              </span>
            </td>
            <td class="px-4 py-2 whitespace-nowrap">
              <div class="flex items-center text-sm text-text-medium">
                <span class="mr-1">
                  {@html getPaymentMethodIcon(transaction.payment_method)}
                </span>
                {transaction.payment_method || 'Standard'}
              </div>
            </td>
            <td class="px-4 py-2 whitespace-nowrap text-sm text-text-medium">
              {formatDate(transaction.created_at)}
            </td>
            <td class="px-4 py-2 whitespace-nowrap">
              <span class="px-2 inline-flex text-xs leading-5 font-medium rounded-full {getStatusBadgeClass(transaction.status)}">
                {transaction.status}
              </span>
            </td>
            <td class="px-4 py-2 whitespace-nowrap text-right text-sm font-medium">
              <a href={`/transactions/${transaction.id}`} class="inline-flex items-center px-2 py-1 border border-gray-300 text-xs font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                Details
              </a>
              
              {#if transaction.status === 'COMPLETED'}
                <a 
                  href={`/transactions/${transaction.id}/receipt`}
                  class="ml-2 inline-flex items-center px-2 py-1 border border-gray-300 text-xs font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  Receipt
                </a>
              {/if}
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
{/if}