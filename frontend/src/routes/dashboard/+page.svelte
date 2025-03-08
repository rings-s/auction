<!-- src/routes/dashboard/+page.svelte -->
<script>
  import { onMount, onDestroy } from 'svelte';
  import { browser } from '$app/environment';
  import UserDashboard from '$lib/components/dashboard/UserDashboard.svelte';
  import Spinner from '$lib/components/ui/Spinner.svelte';
  import Alert from '$lib/components/ui/Alert.svelte';
  
  // Stores - imported safely for SSR
  let profileStore;
  let authStore;
  let notificationStore;
  let api;
  let createDashboardConnection;
  
  // Dashboard WebSocket connection
  let dashboardConnection;
  let dashboardStatus;
  let dashboardDataStore;
  
  // Dashboard data
  let dashboardData = null;
  let recentAuctions = [];
  let recentBids = [];
  let recentTransactions = [];
  let statistics = {
    selling_auctions: 0,
    bidding_auctions: 0,
    won_auctions: 0,
    sold_auctions: 0
  };
  let primaryRole = { code: 'buyer' }; // Default value
  let user = { first_name: 'User' }; // Default value
  
  // WebSocket subscription
  let dashboardUnsubscribe = () => {};
  let statusUnsubscribe = () => {};
  
  // Loading state
  let loading = true;
  let error = null;
  
  // Safe import of browser-only modules
  onMount(async () => {
    if (browser) {
      try {
        // Dynamically import browser-only modules
        const storeModules = await import('$lib/stores/profileStore');
        const authModules = await import('$lib/stores/authStore');
        const notifModules = await import('$lib/stores/notificationStore');
        const apiModule = await import('$lib/api');
        const wsModule = await import('$lib/websocketService');
        
        profileStore = storeModules.profileStore;
        authStore = authModules.authStore;
        notificationStore = notifModules.notificationStore;
        api = apiModule.api;
        createDashboardConnection = wsModule.createDashboardConnection;
        
        // Subscribe to auth store to get user data
        const unsubscribe = authStore.subscribe(value => {
          user = value.user || { first_name: 'User' };
          primaryRole = value.primaryRole || { code: 'buyer' };
          
          // If user data is available and user is authenticated, set up dashboard WebSocket
          if (value.user && value.isAuthenticated && value.user.id) {
            setupDashboardWebSocket(value.user.id);
          }
        });
        
        // Load initial dashboard data from REST API
        const data = await api.base.user_dashboard();
        dashboardData = data;
        
        // Extract key sections from the dashboard data
        recentAuctions = data.recent_auctions || [];
        recentBids = data.recent_bids || [];
        recentTransactions = data.recent_transactions || [];
        
        // Set statistics based on role
        statistics = {
          selling_auctions: data.selling_auctions || 0,
          bidding_auctions: data.bidding_auctions || 0,
          won_auctions: data.won_auctions || 0,
          sold_auctions: data.sold_auctions || 0
        };
        
        loading = false;
        
        return () => {
          // Clean up subscriptions on component unmount
          unsubscribe();
          closeDashboardWebSocket();
        };
      } catch (err) {
        console.error('Error initializing dashboard:', err);
        error = err.message || 'Failed to load dashboard data';
        loading = false;
        
        if (notificationStore) {
          notificationStore.error('Failed to load dashboard data');
        }
      }
    }
  });
  
  onDestroy(() => {
    // Ensure WebSocket connections are properly closed on component unmount
    closeDashboardWebSocket();
  });
  
  // Set up dashboard WebSocket connection
  function setupDashboardWebSocket(userId) {
    // Close existing connection if any
    closeDashboardWebSocket();
    
    // Create new connection
    dashboardConnection = createDashboardConnection(userId);
    dashboardStatus = dashboardConnection.status;
    dashboardDataStore = dashboardConnection.dashboardData;
    
    // Subscribe to dashboard data updates
    dashboardUnsubscribe = dashboardDataStore.subscribe(data => {
      if (data && Object.keys(data).length > 0) {
        console.log('Received dashboard data update:', data);
        
        // Update statistics if available
        if (data.statistics) {
          statistics = data.statistics;
        }
        
        // Update recent auctions if available
        if (data.recent_auctions) {
          recentAuctions = data.recent_auctions;
        }
        
        // Update recent bids if available
        if (data.recent_bids) {
          recentBids = data.recent_bids;
        }
        
        // Update recent transactions if available
        if (data.recent_transactions) {
          recentTransactions = data.recent_transactions;
        }
      }
    });
    
    // Subscribe to connection status
    statusUnsubscribe = dashboardStatus.subscribe(newStatus => {
      console.log('Dashboard WebSocket status:', newStatus);
      
      // Handle reconnection attempts if connection fails
      if (newStatus === 'failed') {
        notificationStore.warning('Dashboard live updates unavailable. Some information may not be current.');
      } else if (newStatus === 'connected') {
        notificationStore.success('Dashboard live updates connected');
      }
    });
  }
  
  // Close dashboard WebSocket connection
  function closeDashboardWebSocket() {
    if (dashboardUnsubscribe) {
      dashboardUnsubscribe();
      dashboardUnsubscribe = () => {};
    }
    
    if (statusUnsubscribe) {
      statusUnsubscribe();
      statusUnsubscribe = () => {};
    }
    
    if (dashboardConnection) {
      dashboardConnection.close();
      dashboardConnection = null;
    }
  }
  
  // Refresh dashboard data - can be called when user wants fresh data
  function refreshDashboard() {
    if (dashboardConnection && dashboardConnection.isConnected()) {
      notificationStore.info('Refreshing dashboard data...');
      dashboardConnection.refreshDashboard();
    } else {
      // Fallback to REST API if WebSocket is not connected
      loading = true;
      api.base.user_dashboard()
        .then(data => {
          dashboardData = data;
          
          // Extract key sections
          recentAuctions = data.recent_auctions || [];
          recentBids = data.recent_bids || [];
          recentTransactions = data.recent_transactions || [];
          
          // Update statistics
          statistics = {
            selling_auctions: data.selling_auctions || 0,
            bidding_auctions: data.bidding_auctions || 0,
            won_auctions: data.won_auctions || 0,
            sold_auctions: data.sold_auctions || 0
          };
          
          notificationStore.success('Dashboard data refreshed');
          loading = false;
        })
        .catch(err => {
          console.error('Error refreshing dashboard:', err);
          error = err.message || 'Failed to refresh dashboard data';
          notificationStore.error('Failed to refresh dashboard data');
          loading = false;
        });
    }
  }
  
  // Refresh a specific section of the dashboard
  function refreshSection(section) {
    if (dashboardConnection && dashboardConnection.isConnected()) {
      notificationStore.info(`Refreshing ${section.replace('_', ' ')}...`);
      dashboardConnection.getSection(section);
    } else {
      // Fallback to REST API for full refresh if WebSocket is not connected
      refreshDashboard();
    }
  }
  
  // Reconnect WebSocket
  function reconnectWebSocket() {
    if (dashboardConnection) {
      dashboardConnection.reconnect();
      notificationStore.info('Attempting to reconnect to dashboard updates...');
    } else if (user && user.id) {
      setupDashboardWebSocket(user.id);
      notificationStore.info('Initializing dashboard connection...');
    } else {
      notificationStore.error('Cannot connect: User information not available');
    }
  }
</script>

<svelte:head>
  <title>Dashboard | GUDIC Auctions</title>
  <meta name="description" content="View your auction activity, bids, and transactions in real-time">
</svelte:head>

{#if loading}
  <div class="flex justify-center items-center py-12">
    <Spinner size="lg" />
  </div>
{:else if error}
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
    <Alert variant="error" class="mb-4">{error}</Alert>
    <button 
      class="px-4 py-2 bg-primary-blue text-white rounded-md hover:bg-primary-blue/90 transition"
      on:click={() => { error = null; loading = true; refreshDashboard(); }}
    >
      Retry Loading Dashboard
    </button>
  </div>
{:else if browser}
  <UserDashboard 
    {user}
    {primaryRole}
    {statistics}
    {recentAuctions}
    {recentBids}
    {recentTransactions}
    connectionStatus={$dashboardStatus}
    onRefreshDashboard={refreshDashboard}
    onRefreshSection={refreshSection}
    onReconnect={reconnectWebSocket}
  />
{/if}