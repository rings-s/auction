<!-- src/routes/transactions/[id]/+page.svelte -->
<script>
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { fade, fly } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';
  import { isAuthenticated, user } from '$lib/stores/authStore';
  import { notificationStore } from '$lib/stores/notificationStore';
  import { api } from '$lib/api';
  
  // UI Components
  import Button from '$lib/components/ui/Button.svelte';
  import Spinner from '$lib/components/ui/Spinner.svelte';
  import Alert from '$lib/components/ui/Alert.svelte';
  import Modal from '$lib/components/ui/Modal.svelte';
  
  // Get the transaction ID from the URL
  const transactionId = $page.params.id;
  
  // State
  let transaction = null;
  let auction = null;
  let loading = true;
  let error = null;
  let showIssueModal = false;
  let issueDescription = '';
  let reportingIssue = false;
  let issueTypes = [
    { id: 'not_received', label: 'Item not received' },
    { id: 'damaged', label: 'Item received damaged' },
    { id: 'wrong_item', label: 'Wrong item received' },
    { id: 'not_as_described', label: 'Item not as described' },
    { id: 'other', label: 'Other issue' }
  ];
  let selectedIssueType = issueTypes[0].id;
  let trackingInfo = null;
  let trackingEvents = [];
  let sellerInfo = null;
  
  // Load transaction details
  async function loadTransactionDetails() {
    if (!$isAuthenticated) {
      goto('/login?redirect=/transactions/' + transactionId);
      return;
    }
    
    try {
      loading = true;
      error = null;
      
      // Use standard API pattern
      const transactionResponse = await api.transaction.getById(transactionId);
      
      if (!transactionResponse) {
        throw new Error('Failed to load transaction details - empty response');
      }
      
      transaction = transactionResponse;
      
      // Load related data in parallel for better performance
      await Promise.all([
        loadAuctionDetails(),
        loadTrackingInfo(),
        loadSellerInfo()
      ].filter(Boolean)); // Filter out any null promises
      
    } catch (err) {
      console.error('Error loading transaction details:', err);
      const errorMessage = err.error || err.message || 'Failed to load transaction details';
      error = errorMessage;
      notificationStore.error(error);
    } finally {
      loading = false;
    }
  }
  
  // Load auction details
  async function loadAuctionDetails() {
    if (!transaction || !transaction.auction_id) {
      return null; // Return null if no auction to load
    }
    
    try {
      const auctionResponse = await api.auction.getById(transaction.auction_id);
      auction = auctionResponse;
      return auction;
    } catch (auctionErr) {
      console.error('Error loading auction details:', auctionErr);
      return null; // Don't fail completely if just the auction details fail to load
    }
  }
  
  // Load tracking information
  async function loadTrackingInfo() {
    if (!transaction || !transaction.tracking_number || !transaction.shipping_carrier) {
      return null; // Return null if no tracking info to load
    }
    
    try {
      trackingInfo = await api.transaction.getTracking(
        transaction.tracking_number,
        transaction.shipping_carrier
      );
      
      // Process tracking events if available
      if (trackingInfo && Array.isArray(trackingInfo.events)) {
        trackingEvents = trackingInfo.events;
      } else if (trackingInfo && trackingInfo.tracking_events) {
        trackingEvents = trackingInfo.tracking_events;
      } else {
        trackingEvents = [];
      }
      
      // Sort events by timestamp if available
      if (trackingEvents.length > 0 && trackingEvents[0].timestamp) {
        trackingEvents.sort((a, b) => {
          const dateA = new Date(a.timestamp);
          const dateB = new Date(b.timestamp);
          return dateB - dateA; // Sort descending (newest first)
        });
      }
      
      return trackingInfo;
    } catch (err) {
      console.error('Error processing tracking information:', err);
      trackingInfo = null;
      trackingEvents = [];
      return null;
    }
  }
  
  // Load seller information
  async function loadSellerInfo() {
    if (!transaction || !transaction.seller_id) {
      return null; // Return null if no seller to load
    }
    
    try {
      sellerInfo = await api.profile.getPublicProfile(transaction.seller_id);
      return sellerInfo;
    } catch (err) {
      // Create a minimal seller info object on error
      sellerInfo = {
        name: 'Unknown Seller',
        id: transaction.seller_id
      };
      return sellerInfo;
    }
  }
  
  // Report an issue with the transaction
  async function reportIssue() {
    if (!issueDescription.trim()) {
      notificationStore.error('Please provide details about your issue');
      return;
    }
    
    if (!transaction || !transaction.id) {
      notificationStore.error('Transaction information is missing');
      return;
    }
    
    try {
      reportingIssue = true;
      
      // Call the API with the issue data
      const issueData = {
        issueType: selectedIssueType,
        description: issueDescription
      };
      
      await api.transaction.reportIssue(transaction.id, issueData);
      
      // Close modal and update transaction status
      showIssueModal = false;
      issueDescription = '';
      
      // Refresh transaction details to get updated status
      await loadTransactionDetails();
      
      notificationStore.success('Your issue has been reported. We will review it shortly.');
    } catch (err) {
      console.error('Error reporting issue:', err);
      const errorMessage = err.error || err.message || 'Failed to report issue. Please try again.';
      notificationStore.error(errorMessage);
    } finally {
      reportingIssue = false;
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
  
  // Get status color and label
  function getStatusInfo(status) {
    if (!status) return { color: 'bg-gray-100 text-gray-800', icon: 'help-circle', label: 'Unknown' };
    
    const normalizedStatus = typeof status === 'string' ? status.toLowerCase() : '';
    const statusMap = {
      'pending': {
        color: 'bg-yellow-100 text-yellow-800',
        icon: 'clock',
        label: 'Pending'
      },
      'processing': {
        color: 'bg-blue-100 text-blue-800',
        icon: 'refresh',
        label: 'Processing'
      },
      'shipped': {
        color: 'bg-purple-100 text-purple-800',
        icon: 'truck',
        label: 'Shipped'
      },
      'delivered': {
        color: 'bg-green-100 text-green-800',
        icon: 'check-circle',
        label: 'Delivered'
      },
      'cancelled': {
        color: 'bg-red-100 text-red-800',
        icon: 'x-circle',
        label: 'Cancelled'
      },
      'refunded': {
        color: 'bg-orange-100 text-orange-800',
        icon: 'refresh-ccw',
        label: 'Refunded'
      },
      'disputed': {
        color: 'bg-red-100 text-red-800',
        icon: 'alert-circle',
        label: 'Disputed'
      }
    };
    
    return statusMap[normalizedStatus] || {
      color: 'bg-gray-100 text-gray-800',
      icon: 'help-circle',
      label: status
    };
  }
  
  // Format tracking status
  function formatTrackingStatus(status) {
    if (!status) return 'Unknown';
    
    const statusMap = {
      'in_transit': 'In Transit',
      'delivered': 'Delivered',
      'exception': 'Exception',
      'out_for_delivery': 'Out for Delivery',
      'pending': 'Pending',
      'available_for_pickup': 'Available for Pickup',
      'return_to_sender': 'Return to Sender'
    };
    
    return statusMap[status] || status;
  }
  
  // Format address for display
  function formatAddress(address) {
    if (!address) return 'No address provided';
    
    let parts = [];
    if (address.full_name) parts.push(address.full_name);
    if (address.address_line_1) parts.push(address.address_line_1);
    if (address.address_line_2) parts.push(address.address_line_2);
    if (address.city && address.state) parts.push(`${address.city}, ${address.state} ${address.postal_code || ''}`);
    else if (address.city) parts.push(address.city);
    if (address.country) parts.push(address.country);
    if (address.phone_number) parts.push(address.phone_number);
    
    return parts.join('<br>');
  }
  
  // Display the right status color for timeline events
  function getEventStatusClass(status) {
    if (!status) return 'bg-gray-500';
    
    const statusClasses = {
      'ordered': 'bg-blue-500',
      'processing': 'bg-blue-500',
      'packed': 'bg-indigo-500',
      'shipped': 'bg-indigo-500',
      'in_transit': 'bg-purple-500',
      'out_for_delivery': 'bg-amber-500',
      'delivered': 'bg-green-500',
      'failed_delivery': 'bg-red-500',
      'exception': 'bg-red-500',
      'pending': 'bg-gray-500',
      'cancelled': 'bg-red-500',
      'refunded': 'bg-orange-500'
    };
    
    return statusClasses[status.toLowerCase()] || 'bg-gray-500';
  }
  
  // Calculate estimated delivery date
  function getEstimatedDelivery(transaction) {
    if (!transaction || !transaction.shipped_at) return 'Unknown';
    
    try {
      // Assuming 5-7 business days for delivery
      const shippedDate = new Date(transaction.shipped_at);
      if (isNaN(shippedDate.getTime())) return 'Unknown';
      
      const minDelivery = new Date(shippedDate);
      const maxDelivery = new Date(shippedDate);
      
      minDelivery.setDate(minDelivery.getDate() + 5);
      maxDelivery.setDate(maxDelivery.getDate() + 7);
      
      return `${formatDate(minDelivery, false)} - ${formatDate(maxDelivery, false)}`;
    } catch (error) {
      console.error('Error calculating estimated delivery:', error);
      return 'Unknown';
    }
  }
  
  // Handle download receipt
  function downloadReceipt() {
    if (!transaction) {
      notificationStore.error('Transaction information is missing');
      return;
    }
    
    // In a real implementation, this would likely trigger a PDF download
    notificationStore.info('Receipt download started...');
  }
  
  // Initialize on mount
  onMount(() => {
    const unsubscribe = isAuthenticated.subscribe(value => {
      if (value === true) {
        // Only load data when we're certain authentication is complete and successful
        loadTransactionDetails();
      } else if (value === false) {
        // Redirect if definitely not authenticated
        goto('/login?redirect=/transactions/' + transactionId);
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
  <title>Transaction Details | GUDIC</title>
  <meta name="description" content="View your transaction details and track your order" />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
  <!-- Loading state -->
  {#if loading}
    <div class="flex flex-col items-center justify-center py-8" in:fade={{ duration: 300 }}>
      <Spinner size="lg" />
      <p class="mt-4 text-text-medium">Loading transaction details...</p>
    </div>
  
  <!-- Error state -->
  {:else if error}
    <Alert variant="error" class="my-6">
      <div class="flex flex-col items-center p-3">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-red-500 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <p class="font-medium mb-2">{error}</p>
        <Button 
          variant="primary" 
          size="sm" 
          on:click={loadTransactionDetails}
        >
          Try Again
        </Button>
      </div>
    </Alert>
  
  <!-- Transaction details -->
  {:else if transaction}
    <div class="mb-4" in:fade={{ duration: 200 }}>
      <div class="flex items-center gap-2 mb-2">
        <a href="/transactions" class="text-text-medium hover:text-text-dark transition-colors flex items-center gap-1">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Back to Transactions
        </a>
      </div>
      
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-3">
        <div>
          <h1 class="text-2xl font-bold text-text-dark">Transaction Details</h1>
          <p class="text-text-medium">Order #{transaction.order_number || transaction.id}</p>
        </div>
        
        <div class="flex flex-wrap gap-2">
          <Button 
            variant="outline"
            size="sm"
            on:click={downloadReceipt}
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
            </svg>
            Receipt
          </Button>
          
          {#if transaction.seller_id}
            <a 
              href={`/messages/${transaction.seller_id}`}
              class="inline-flex items-center justify-center px-3 py-1.5 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
              Contact Seller
            </a>
          {:else}
            <button 
              class="inline-flex items-center justify-center px-3 py-1.5 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-400 bg-gray-100 cursor-not-allowed"
              disabled
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
              Contact Seller
            </button>
          {/if}
          
          {#if transaction.status !== 'disputed'}
            <Button 
              variant="primary"
              size="sm"
              on:click={() => showIssueModal = true}
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              Report Issue
            </Button>
          {/if}
        </div>
      </div>
    </div>
    
    <!-- Main content grid -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Left column: Order details and tracking -->
      <div class="lg:col-span-2 space-y-4">
        <!-- Order status card -->
        <div class="bg-white rounded-xl border border-primary-blue/20 overflow-hidden">
          <div class="px-4 py-3 border-b border-primary-blue/10 bg-gradient-to-r from-primary-blue/5 to-primary-peach/5">
            <h3 class="text-lg font-medium text-text-dark">Order Status</h3>
          </div>
          
          <div class="p-4">
            <div class="flex items-center mb-3">
              {@const statusInfo = getStatusInfo(transaction.status)}
              <div class={`px-3 py-1 rounded-full text-sm font-medium ${statusInfo.color} inline-flex items-center`}>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {statusInfo.label}
              </div>
            </div>
            
            <!-- Status timeline - with reduced spacing -->
            <div class="relative pl-5 border-l-2 border-slate-200 pb-1 space-y-4">
              <!-- Order placed -->
              <div class="relative">
                <div class="absolute -left-[15px] flex items-center justify-center w-7 h-7 rounded-full bg-primary-blue text-white">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
                  </svg>
                </div>
                <div class="ml-3">
                  <h4 class="text-sm font-medium text-text-dark">Order Placed</h4>
                  <p class="text-xs text-text-medium">{formatDate(transaction.created_at)}</p>
                  <p class="text-xs text-text-medium">Payment of {formatCurrency(transaction.amount, transaction.currency)} processed.</p>
                </div>
              </div>
              
              <!-- Processing -->
              {#if transaction.status !== 'cancelled' && transaction.status !== 'refunded'}
                <div class="relative">
                  <div class="absolute -left-[15px] flex items-center justify-center w-7 h-7 rounded-full {transaction.processed_at ? 'bg-primary-blue text-white' : 'bg-slate-200 text-slate-400'}">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                    </svg>
                  </div>
                  <div class="ml-3">
                    <h4 class="text-sm font-medium {transaction.processed_at ? 'text-text-dark' : 'text-text-light'}">Order Processing</h4>
                    {#if transaction.processed_at}
                      <p class="text-xs text-text-medium">{formatDate(transaction.processed_at)}</p>
                      <p class="text-xs text-text-medium">Your order is being prepared for shipping.</p>
                    {:else}
                      <p class="text-xs text-text-medium">Your order will be processed shortly.</p>
                    {/if}
                  </div>
                </div>
              {/if}
              
              <!-- Shipped -->
              {#if transaction.status !== 'cancelled' && transaction.status !== 'refunded' && transaction.status !== 'processing' && transaction.status !== 'pending'}
                <div class="relative">
                  <div class="absolute -left-[15px] flex items-center justify-center w-7 h-7 rounded-full {transaction.shipped_at ? 'bg-primary-blue text-white' : 'bg-slate-200 text-slate-400'}">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path d="M9 17a2 2 0 11-4 0 2 2 0 014 0zM19 17a2 2 0 11-4 0 2 2 0 014 0z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16V6a1 1 0 00-1-1H4a1 1 0 00-1 1v10a1 1 0 001 1h1m8-1a1 1 0 01-1 1H9m4-1V8a1 1 0 011-1h2.586a1 1 0 01.707.293l3.414 3.414a1 1 0 01.293.707V16a1 1 0 01-1 1h-1m-6-1a1 1 0 001 1h1M5 17a2 2 0 104 0m-4 0a2 2 0 114 0m6 0a2 2 0 104 0m-4 0a2 2 0 114 0" />
                    </svg>
                  </div>
                  <div class="ml-3">
                    <h4 class="text-sm font-medium {transaction.shipped_at ? 'text-text-dark' : 'text-text-light'}">Order Shipped</h4>
                    {#if transaction.shipped_at}
                      <p class="text-xs text-text-medium">{formatDate(transaction.shipped_at)}</p>
                      <p class="text-xs text-text-medium">
                        Shipped via {transaction.shipping_carrier || 'Standard Shipping'}.
                        {#if transaction.tracking_number}
                          <span class="font-medium">Tracking: {transaction.tracking_number}</span>
                        {/if}
                      </p>
                      <p class="text-xs text-text-medium">
                        Est. delivery: {getEstimatedDelivery(transaction)}
                      </p>
                    {:else}
                      <p class="text-xs text-text-medium">Your order will be shipped soon.</p>
                    {/if}
                  </div>
                </div>
              {/if}
              
              <!-- Delivered -->
              {#if transaction.status === 'delivered'}
                <div class="relative">
                  <div class="absolute -left-[15px] flex items-center justify-center w-7 h-7 rounded-full {transaction.delivered_at ? 'bg-green-500 text-white' : 'bg-slate-200 text-slate-400'}">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <div class="ml-3">
                    <h4 class="text-sm font-medium {transaction.delivered_at ? 'text-text-dark' : 'text-text-light'}">Order Delivered</h4>
                    {#if transaction.delivered_at}
                      <p class="text-xs text-text-medium">{formatDate(transaction.delivered_at)}</p>
                      <p class="text-xs text-text-medium">Your order has been delivered successfully.</p>
                    {:else}
                      <p class="text-xs text-text-medium">Your order will be delivered soon.</p>
                    {/if}
                  </div>
                </div>
              {/if}
              
              <!-- Cancelled or Refunded -->
              {#if transaction.status === 'cancelled' || transaction.status === 'refunded'}
                <div class="relative">
                  <div class="absolute -left-[15px] flex items-center justify-center w-7 h-7 rounded-full bg-red-500 text-white">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </div>
                  <div class="ml-3">
                    <h4 class="text-sm font-medium text-text-dark">
                      {transaction.status === 'cancelled' ? 'Order Cancelled' : 'Order Refunded'}
                    </h4>
                    <p class="text-xs text-text-medium">{formatDate(transaction.updated_at)}</p>
                    <p class="text-xs text-text-medium">
                      {transaction.status === 'cancelled' 
                        ? 'Your order has been cancelled.' 
                        : `Your payment of ${formatCurrency(transaction.amount, transaction.currency)} has been refunded.`
                      }
                      {#if transaction.cancellation_reason || transaction.refund_reason}
                        <br>Reason: {transaction.cancellation_reason || transaction.refund_reason}
                      {/if}
                    </p>
                  </div>
                </div>
              {/if}
              
              <!-- Disputed -->
              {#if transaction.status === 'disputed'}
                <div class="relative">
                  <div class="absolute -left-[15px] flex items-center justify-center w-7 h-7 rounded-full bg-red-500 text-white">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                  </div>
                  <div class="ml-3">
                    <h4 class="text-sm font-medium text-text-dark">Order Disputed</h4>
                    <p class="text-xs text-text-medium">{formatDate(transaction.dispute_date || transaction.updated_at)}</p>
                    <p class="text-xs text-text-medium">
                      Your dispute is being reviewed by our support team.
                      {#if transaction.dispute_reason}
                        <br>Reason: {transaction.dispute_reason}
                      {/if}
                    </p>
                  </div>
                </div>
              {/if}
            </div>
          </div>
        </div>
        
        <!-- Shipping tracking card -->
        {#if transaction.tracking_number && transaction.shipping_carrier}
          <div class="bg-white rounded-xl border border-primary-blue/20 overflow-hidden">
            <div class="px-4 py-3 border-b border-primary-blue/10 bg-gradient-to-r from-primary-blue/5 to-primary-peach/5">
              <h3 class="text-lg font-medium text-text-dark">Shipping Tracking</h3>
            </div>
            
            <div class="p-4">
              <div class="flex flex-wrap gap-3 mb-3">
                <div>
                  <div class="text-xs text-text-medium">Carrier</div>
                  <div class="text-sm font-medium">{transaction.shipping_carrier}</div>
                </div>
                <div>
                  <div class="text-xs text-text-medium">Tracking Number</div>
                  <div class="text-sm font-medium">{transaction.tracking_number}</div>
                </div>
                {#if trackingInfo && trackingInfo.status}
                  <div>
                    <div class="text-xs text-text-medium">Current Status</div>
                    <div class="text-sm font-medium">{formatTrackingStatus(trackingInfo.status)}</div>
                  </div>
                {/if}
              </div>
              
              {#if trackingEvents && trackingEvents.length > 0}
                <div class="relative pl-5 border-l-2 border-slate-200 pb-1 space-y-3 max-h-40 overflow-y-auto">
                  {#each trackingEvents as event, index}
                    <div class="relative">
                      <div class="absolute -left-[8px] flex items-center justify-center w-3.5 h-3.5 rounded-full {getEventStatusClass(event.status)}"></div>
                      <div class="ml-3">
                        <h4 class="text-sm font-medium text-text-dark">{formatTrackingStatus(event.status)}</h4>
                        <p class="text-xs text-text-medium">{formatDate(event.timestamp)}</p>
                        <p class="text-xs text-text-medium">{event.location || 'No location information'}</p>
                      </div>
                    </div>
                  {/each}
                </div>
              {:else}
                <div class="text-center py-3">
                  <p class="text-xs text-text-medium">Tracking information will be available once the package is in transit.</p>
                </div>
              {/if}
              
              {#if transaction.shipping_carrier && transaction.tracking_number}
                <div class="mt-3 text-center">
                  <Button 
                    variant="outline" 
                    size="sm"
                    href={`https://www.${transaction.shipping_carrier.toLowerCase()}.com/tracking?tracknum=${transaction.tracking_number}`}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    View on {transaction.shipping_carrier} Website
                  </Button>
                </div>
              {/if}
            </div>
          </div>
        {/if}
        
        <!-- Order items card -->
        <div class="bg-white rounded-xl border border-primary-blue/20 overflow-hidden">
          <div class="px-4 py-3 border-b border-primary-blue/10 bg-gradient-to-r from-primary-blue/5 to-primary-peach/5">
            <h3 class="text-lg font-medium text-text-dark">Order Items</h3>
          </div>
          
          <div class="p-4">
            <div class="border rounded-lg overflow-hidden">
              <div class="divide-y">
                <div class="p-3 flex items-center">
                  <div class="flex-shrink-0 w-14 h-14 bg-slate-100 rounded-md overflow-hidden">
                    {#if auction && auction.image_url}
                      <img 
                        src={auction.image_url} 
                        alt={auction.title} 
                        class="w-full h-full object-cover"
                      />
                    {:else}
                      <div class="flex items-center justify-center h-full bg-primary-blue/10 text-primary-blue">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                      </div>
                    {/if}
                  </div>
                  
                  <div class="ml-3 flex-1">
                    <h4 class="text-sm font-medium text-text-dark">
                      {#if auction}
                        <a href={`/auctions/${auction.id}`} class="hover:text-secondary-blue">
                          {auction.title}
                        </a>
                      {:else if transaction.item_title}
                        {transaction.item_title}
                      {:else if transaction.auction_details?.title}
                        {transaction.auction_details.title}
                      {:else}
                        Auction Item
                      {/if}
                    </h4>
                    <p class="text-xs text-text-medium">
                      Auction ID: {transaction.auction_id || 'N/A'}
                    </p>
                  </div>
                  
                  <div class="ml-3 text-right">
                    <div class="text-sm font-medium text-text-dark">
                      {formatCurrency(transaction.amount, transaction.currency)}
                    </div>
                    <div class="text-xs text-text-medium">
                      Qty: {transaction.quantity || 1}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Right column: Summary and seller info -->
      <div class="space-y-4">
        <!-- Order summary card -->
        <div class="bg-white rounded-xl border border-primary-blue/20 overflow-hidden">
          <div class="px-4 py-3 border-b border-primary-blue/10 bg-gradient-to-r from-primary-blue/5 to-primary-peach/5">
            <h3 class="text-lg font-medium text-text-dark">Order Summary</h3>
          </div>
          
          <div class="p-4">
            <div class="space-y-2">
              <div class="flex justify-between py-0.5">
                <span class="text-sm text-text-medium">Item subtotal</span>
                <span class="text-sm text-text-dark font-medium">
                  {formatCurrency(
                    transaction.amount - (transaction.shipping_cost || 0) - (transaction.tax || 0), 
                    transaction.currency
                  )}
                </span>
              </div>
              
              <div class="flex justify-between py-0.5">
                <span class="text-sm text-text-medium">Shipping</span>
                <span class="text-sm text-text-dark font-medium">
                  {formatCurrency(transaction.shipping_cost || 0, transaction.currency)}
                </span>
              </div>
              
              <div class="flex justify-between py-0.5">
                <span class="text-sm text-text-medium">Tax</span>
                <span class="text-sm text-text-dark font-medium">
                  {formatCurrency(transaction.tax || 0, transaction.currency)}
                </span>
              </div>
              
              <div class="border-t border-primary-blue/10 pt-2 mt-1">
                <div class="flex justify-between">
                  <span class="text-sm text-text-dark font-medium">Total</span>
                  <span class="text-secondary-blue font-bold">
                    {formatCurrency(transaction.amount, transaction.currency)}
                  </span>
                </div>
              </div>
              
              {#if transaction.status === 'refunded'}
                <div class="mt-2 p-2 bg-orange-50 border border-orange-200 rounded-md">
                  <div class="flex justify-between text-orange-700">
                    <span class="text-sm font-medium">Refunded</span>
                    <span class="font-bold">
                      {formatCurrency(transaction.refunded_amount || transaction.amount, transaction.currency)}
                    </span>
                  </div>
                  {#if transaction.refund_date}
                    <div class="text-xs text-orange-600 mt-1">
                      Refunded on {formatDate(transaction.refund_date)}
                    </div>
                  {/if}
                </div>
              {/if}
            </div>
            
            <div class="mt-3 text-sm">
              <div class="font-medium text-text-dark mb-1">Payment Method</div>
              <div class="flex items-center">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-slate-400 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                </svg>
                <span class="text-xs">{transaction.payment_method || 'Credit Card'}</span>
              </div>
              {#if transaction.payment_details}
                <div class="text-xs text-text-medium mt-1 ml-6">
                  {transaction.payment_details}
                </div>
              {/if}
            </div>
          </div>
        </div>
        
        <!-- Shipping info card -->
        <div class="bg-white rounded-xl border border-primary-blue/20 overflow-hidden">
          <div class="px-4 py-3 border-b border-primary-blue/10 bg-gradient-to-r from-primary-blue/5 to-primary-peach/5">
            <h3 class="text-lg font-medium text-text-dark">Shipping Information</h3>
          </div>
          
          <div class="p-4">
            <div class="grid grid-cols-1 gap-3">
              <!-- Shipping Address -->
              <div>
                <div class="text-sm font-medium text-text-dark mb-1">Shipping Address</div>
                <div class="text-xs text-text-medium">
                  {#if transaction.shipping_address}
                    {@html formatAddress(transaction.shipping_address)}
                  {:else}
                    No shipping address provided
                  {/if}
                </div>
              </div>
              
              <!-- Shipping Method -->
              <div>
                <div class="text-sm font-medium text-text-dark mb-1">Shipping Method</div>
                <div class="text-xs text-text-medium">
                  {transaction.shipping_method || 'Standard Shipping'}
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Seller information card -->
        {#if sellerInfo}
          <div class="bg-white rounded-xl border border-primary-blue/20 overflow-hidden">
            <div class="px-4 py-3 border-b border-primary-blue/10 bg-gradient-to-r from-primary-blue/5 to-primary-peach/5">
              <h3 class="text-lg font-medium text-text-dark">Seller Information</h3>
            </div>
            
            <div class="p-4">
              <div class="flex items-center">
                <div class="h-10 w-10 rounded-full bg-primary-blue/10 flex items-center justify-center mr-3">
                  {#if sellerInfo.avatar_url}
                    <img 
                      src={sellerInfo.avatar_url} 
                      alt={sellerInfo.name} 
                      class="h-10 w-10 rounded-full object-cover"
                    />
                  {:else}
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-secondary-blue" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                  {/if}
                </div>
                <div>
                  <div class="text-sm font-medium text-text-dark">{sellerInfo.name}</div>
                  <div class="text-xs text-text-medium">
                    {sellerInfo.location || 'No location provided'}
                  </div>
                </div>
              </div>
              
              <div class="mt-3">
                <a
                  href={`/messages/${sellerInfo.id}`}
                  class="w-full inline-flex items-center justify-center px-3 py-1.5 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                  </svg>
                  Contact Seller
                </a>
              </div>
            </div>
          </div>
        {/if}
        
        <!-- Need help card -->
        <div class="bg-white rounded-xl border border-primary-blue/20 overflow-hidden p-3">
          <h4 class="text-sm font-medium text-text-dark mb-1">Need help?</h4>
          <p class="text-xs text-text-medium mb-2">
            Questions about your order? Our support team is here to help.
          </p>
          <a
            href="/support"
            class="w-full inline-flex items-center justify-center px-3 py-1.5 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192l-3.536 3.536M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-5 0a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
            Contact Support
          </a>
        </div>
      </div>
    </div>
  {/if}
</div>

<!-- Report Issue Modal -->
<Modal
  bind:open={showIssueModal}
  title="Report an Issue"
  size="md"
  marginY={20}
>
  <div class="py-2">
    <p class="text-text-medium mb-3 text-sm">
      We're sorry to hear you're experiencing an issue with your order. Please provide details so we can help resolve it.
    </p>
    
    <div class="space-y-3">
      <!-- Issue type -->
      <div>
        <label for="issue-type" class="block text-sm font-medium text-text-dark mb-1">
          Issue Type <span class="text-secondary-blue">*</span>
        </label>
        <select
          id="issue-type"
          bind:value={selectedIssueType}
          class="block w-full px-3 py-2 border border-primary-blue/30 focus:ring-secondary-blue focus:border-secondary-blue rounded-md"
        >
          {#each issueTypes as issueType}
            <option value={issueType.id}>{issueType.label}</option>
          {/each}
        </select>
      </div>
      
      <!-- Issue description -->
      <div>
        <label for="issue-description" class="block text-sm font-medium text-text-dark mb-1">
          Issue Description <span class="text-secondary-blue">*</span>
        </label>
        <textarea
          id="issue-description"
          bind:value={issueDescription}
          rows="3"
          class="block w-full px-3 py-2 border border-primary-blue/30 focus:ring-secondary-blue focus:border-secondary-blue rounded-md"
          placeholder="Please provide details about the issue you're experiencing..."
        ></textarea>
      </div>
      
      <!-- Additional instructions -->
      <div class="text-xs text-text-medium border-t border-primary-blue/10 pt-2">
        <p class="mb-1">What happens after you report an issue:</p>
        <ol class="list-decimal list-inside space-y-0.5">
          <li>Our support team will review your report within 24-48 hours.</li>
          <li>The seller will be notified and given the opportunity to resolve the issue.</li>
          <li>If needed, our team will mediate the resolution process.</li>
        </ol>
      </div>
    </div>
  </div>
  
  <div slot="footer" class="flex justify-end space-x-3">
    <Button
      variant="outline"
      on:click={() => showIssueModal = false}
      disabled={reportingIssue}
    >
      Cancel
    </Button>
    <Button
      variant="primary"
      on:click={reportIssue}
      disabled={reportingIssue || !issueDescription.trim()}
    >
      {#if reportingIssue}
        <Spinner size="sm" class="mr-2" />
        Submitting...
      {:else}
        Submit Report
      {/if}
    </Button>
  </div>
</Modal>