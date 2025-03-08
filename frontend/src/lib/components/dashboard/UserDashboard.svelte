<!-- src/lib/components/dashboard/UserDashboard.svelte -->
<script>
  import { fade } from 'svelte/transition';
  import { goto } from '$app/navigation';
  import Button from '$lib/components/ui/Button.svelte';
  import Alert from '$lib/components/ui/Alert.svelte';
  import RecentAuctionsDashboard from './RecentAuctionsDashboard.svelte';
  import RecentBidsComponent from '$lib/components/bids/RecentBidsComponent.svelte';
  
  // Component props
  export let user = { first_name: 'User' };
  export let primaryRole = { code: 'buyer' };
  export let statistics = {
    selling_auctions: 0,
    bidding_auctions: 0, 
    won_auctions: 0,
    sold_auctions: 0
  };
  // Remove unused exports and replace with consts if needed for external reference
  export let recentTransactions = [];
  export let connectionStatus = null;
  
  // Callback functions
  export let onRefreshDashboard = () => {};
  export let onRefreshSection = (section) => {};
  export let onReconnect = () => {};
  
  // Format currency
  function formatCurrency(amount, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency
    }).format(amount);
  }
  
  // Format date
  function formatDate(dateStr) {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  }
  
  // Get status badge color
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
      case 'PENDING':
        return 'warning';
      case 'COMPLETED':
        return 'success';
      case 'DISPUTED':
        return 'error';
      default:
        return 'default';
    }
  }
</script>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
  <!-- Page Title -->
  <div class="mb-8 flex justify-between items-center">
    <div>
      <h1 class="text-3xl font-bold text-text-dark">Dashboard</h1>
      <p class="text-text-medium mt-2">Welcome back, {user?.first_name || 'User'}</p>
    </div>
    
    <!-- Refresh Button -->
    <Button variant="outline" on:click={onRefreshDashboard}>
      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
        <path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd" />
      </svg>
      Refresh
    </Button>
  </div>

  <!-- Connection Status Alert (shown only when there's an issue) -->
  {#if connectionStatus && ['error', 'failed'].includes(connectionStatus)}
    <Alert variant="warning" class="mb-6">
      <div class="flex items-center">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
        </svg>
        <span>Live updates unavailable. Some information may not be current.</span>
      </div>
      <div class="mt-2">
        <Button size="sm" variant="secondary" on:click={onReconnect}>
          Try Reconnect
        </Button>
      </div>
    </Alert>
  {/if}

  <!-- Statistics -->
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5 mb-8" in:fade={{ duration: 300, delay: 150 }}>
    <!-- Active Auctions -->
    <div class="card p-5 border border-primary-blue/20">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm font-medium text-text-medium">Active Auctions</p>
          <p class="text-2xl font-semibold text-text-dark mt-1">{statistics.selling_auctions}</p>
        </div>
        <div class="h-12 w-12 rounded-lg bg-primary-blue/10 flex items-center justify-center text-secondary-blue">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
          </svg>
        </div>
      </div>
      <div class="mt-2">
        <a href="/auctions/selling" class="text-secondary-blue hover:text-secondary-blue/80 text-sm font-medium">
          View All
        </a>
      </div>
    </div>
    
    <!-- Active Bids -->
    <div class="card p-5 border border-primary-peach/20">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm font-medium text-text-medium">Active Bids</p>
          <p class="text-2xl font-semibold text-text-dark mt-1">{statistics.bidding_auctions}</p>
        </div>
        <div class="h-12 w-12 rounded-lg bg-primary-peach/10 flex items-center justify-center text-secondary-peach">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
      </div>
      <div class="mt-2">
        <a href="/auctions/bidding" class="text-secondary-blue hover:text-secondary-blue/80 text-sm font-medium">
          View All
        </a>
      </div>
    </div>
    
    <!-- Won Auctions -->
    <div class="card p-5 border border-success/20">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm font-medium text-text-medium">Won Auctions</p>
          <p class="text-2xl font-semibold text-text-dark mt-1">{statistics.won_auctions}</p>
        </div>
        <div class="h-12 w-12 rounded-lg bg-success/10 flex items-center justify-center text-success">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
          </svg>
        </div>
      </div>
      <div class="mt-2">
        <a href="/auctions/won" class="text-secondary-blue hover:text-secondary-blue/80 text-sm font-medium">
          View All
        </a>
      </div>
    </div>
    
    <!-- Sold Auctions -->
    <div class="card p-5 border border-secondary-blue/20">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm font-medium text-text-medium">Sold Auctions</p>
          <p class="text-2xl font-semibold text-text-dark mt-1">{statistics.sold_auctions}</p>
        </div>
        <div class="h-12 w-12 rounded-lg bg-secondary-blue/10 flex items-center justify-center text-secondary-blue">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
        </div>
      </div>
      <div class="mt-2">
        <a href="/auctions/sold" class="text-secondary-blue hover:text-secondary-blue/80 text-sm font-medium">
          View All
        </a>
      </div>
    </div>
  </div>
  
  <!-- Recent Activity -->
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8" in:fade={{ duration: 300, delay: 300 }}>
    <!-- Recent Auctions - Replace with RecentAuctionsDashboard component -->
    <div class="card border border-primary-blue/20 overflow-hidden">
      <div class="px-5 py-4 border-b border-primary-blue/10 bg-gradient-to-r from-primary-blue/5 to-primary-peach/5">
        <div class="flex justify-between items-center">
          <h3 class="text-lg font-medium text-text-dark">Recent Auctions</h3>
          <!-- Section Refresh Button -->
          <button 
            class="text-secondary-blue hover:text-secondary-blue/80 p-1 rounded-full"
            on:click={() => onRefreshSection('recent_auctions')}
            title="Refresh auctions"
            aria-label="Refresh auctions"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd" />
            </svg>
          </button>
        </div>
      </div>
      
      <!-- Embed the RecentAuctionsDashboard component -->
      <div class="p-4">
        <RecentAuctionsDashboard
          title=""
          showHeader={false}
          limit={5}
          isSellerView={primaryRole?.code === 'seller'}
          viewAllLink="/auctions"
        />
      </div>
      
      <div class="px-5 py-4 border-t border-primary-blue/10 bg-neutral-50">
        <a href="/auctions" class="block text-center text-secondary-blue hover:text-secondary-blue/80 font-medium">
          View All Auctions
        </a>
      </div>
    </div>
    
    <!-- Recent Bids - using RecentBidsComponent -->
    <div class="card border border-primary-peach/20 overflow-hidden">
      <div class="px-5 py-4 border-b border-primary-peach/10 bg-gradient-to-r from-primary-peach/5 to-primary-blue/5">
        <div class="flex justify-between items-center">
          <h3 class="text-lg font-medium text-text-dark">Recent Bids</h3>
          <!-- Section Refresh Button -->
          <button 
            class="text-secondary-blue hover:text-secondary-blue/80 p-1 rounded-full"
            on:click={() => onRefreshSection('recent_bids')}
            title="Refresh bids"
            aria-label="Refresh bids"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd" />
            </svg>
          </button>
        </div>
      </div>
      
      <!-- Embed the RecentBidsComponent -->
      <div class="p-4">
        <RecentBidsComponent 
          title=""
          showHeader={false}
          limit={5}
          compact={true}
          viewAllLink="/auctions/my-bids"
        />
      </div>
      
      <div class="px-5 py-4 border-t border-primary-peach/10 bg-neutral-50">
        <a href="/auctions/my-bids" class="block text-center text-secondary-blue hover:text-secondary-blue/80 font-medium">
          View All Bids
        </a>
      </div>
    </div>
  </div>
  
  <!-- Recent Transactions -->
  <div class="card border border-primary-blue/20 overflow-hidden mb-8" in:fade={{ duration: 300, delay: 450 }}>
    <div class="px-5 py-4 border-b border-primary-blue/10 bg-gradient-to-r from-primary-blue/5 to-primary-peach/5 flex justify-between items-center">
      <h3 class="text-lg font-medium text-text-dark">Recent Transactions</h3>
      <!-- Section Refresh Button -->
      <button 
        class="text-secondary-blue hover:text-secondary-blue/80 p-1 rounded-full"
        on:click={() => onRefreshSection('recent_transactions')}
        title="Refresh transactions"
        aria-label="Refresh transactions"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd" />
        </svg>
      </button>
    </div>
    <div class="overflow-x-auto">
      {#if recentTransactions.length === 0}
        <div class="p-5 text-center text-text-medium">
          <p>No recent transactions</p>
        </div>
      {:else}
        <table class="min-w-full divide-y divide-primary-blue/10">
          <thead class="bg-neutral-50">
            <tr>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-text-light uppercase tracking-wider">
                Auction
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-text-light uppercase tracking-wider">
                Type
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-text-light uppercase tracking-wider">
                Date
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-text-light uppercase tracking-wider">
                Amount
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-text-light uppercase tracking-wider">
                Status
              </th>
              <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-text-light uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-primary-blue/10">
            {#each recentTransactions as transaction}
              <tr class="hover:bg-neutral-50">
                <td class="px-6 py-4 whitespace-nowrap">
                  <a href="/auctions/{transaction.auction}" class="text-secondary-blue hover:underline">
                    {transaction.auction_details?.title || `Auction #${transaction.auction}`}
                  </a>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-text-medium">
                  {transaction.payment_type}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-text-medium">
                  {formatDate(transaction.created_at)}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  {formatCurrency(transaction.amount, transaction.currency)}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="badge {getStatusBadge(transaction.status)}">
                    {transaction.status}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-right text-sm">
                  <a href="/transactions/{transaction.id}" class="text-secondary-blue hover:underline text-xs font-medium">
                    View Details
                  </a>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      {/if}
    </div>
    <div class="px-5 py-4 border-t border-primary-blue/10 bg-neutral-50">
      <a href="/transactions" class="block text-center text-secondary-blue hover:text-secondary-blue/80 font-medium">
        View All Transactions
      </a>
    </div>
  </div>
  
  <!-- Quick Actions -->
  <div class="card border border-primary-blue/20 p-5" in:fade={{ duration: 300, delay: 600 }}>
    <h3 class="text-lg font-medium text-text-dark mb-4">Quick Actions</h3>
    
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      {#if primaryRole?.code === 'seller' || primaryRole?.code === 'admin'}
        <a href="/auctions/create" class="btn-primary flex items-center justify-center py-2 px-4 rounded-md">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" />
          </svg>
          Create Auction
        </a>
      {/if}
      
      <a href="/auctions" class="btn-outline flex items-center justify-center py-2 px-4 rounded-md border border-gray-300 hover:bg-gray-50">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
          <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
          <path fill-rule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clip-rule="evenodd" />
        </svg>
        Browse Auctions
      </a>
      
      <a href="/profile" class="btn-outline flex items-center justify-center py-2 px-4 rounded-md border border-gray-300 hover:bg-gray-50">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-6-3a2 2 0 11-4 0 2 2 0 014 0zm-2 4a5 5 0 00-4.546 2.916A5.986 5.986 0 0010 16a5.986 5.986 0 004.546-2.084A5 5 0 0010 11z" clip-rule="evenodd" />
        </svg>
        Update Profile
      </a>
    </div>
  </div>
</div>

<style>
  /* Additional styling for dashboard elements */
  .card {
    border-radius: 1rem;
    box-shadow: 0 4px 6px rgba(0,0,0,0.03);
    transition: all 0.3s ease;
  }
  
  .card:hover {
    box-shadow: 0 8px 15px rgba(0,0,0,0.05);
    transform: translateY(-2px);
  }
  
  /* Style badges inside table */
  :global(td .badge) {
    font-size: 0.7rem !important;
    padding: 0.15rem 0.5rem !important;
  }
  
  /* Custom animation for dashboard sections */
  @keyframes fade-in-up {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  
  /* Custom button styles for <a> tags */
  .btn-primary {
    background-color: var(--color-primary-blue, #1E40AF);
    color: white;
    font-weight: 500;
    transition: background-color 0.2s;
  }
  
  .btn-primary:hover {
    background-color: var(--color-primary-blue-darker, #1E3A8A);
  }
  
  .btn-outline {
    color: var(--color-text-dark, #1F2937);
    background-color: transparent;
    font-weight: 500;
    transition: background-color 0.2s, border-color 0.2s;
  }
  
  .btn-outline:hover {
    border-color: var(--color-primary-blue, #1E40AF);
  }
  
  .badge {
    display: inline-block;
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