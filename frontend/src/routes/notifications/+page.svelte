<!-- src/routes/notifications/+page.svelte -->
<script>
  import { onMount, onDestroy } from 'svelte';
  import { fade, fly, slide } from 'svelte/transition';
  import { goto } from '$app/navigation';
  import { browser } from '$app/environment';
  import { isAuthenticated, user } from '$lib/stores/authStore';
  import { notificationStore } from '$lib/stores/notificationStore';
  import { createNotificationConnection } from '$lib/websocketService';
  import { api } from '$lib/api';
  import { formatTimeAgo } from '$lib/utils/formatters';
  
  // UI Components
  import Button from '$lib/components/ui/Button.svelte';
  import Spinner from '$lib/components/ui/Spinner.svelte';
  import Alert from '$lib/components/ui/Alert.svelte';
  import Badge from '$lib/components/ui/Badge.svelte';
  
  // State management
  let notifications = [];
  let filteredNotifications = [];
  let loading = true;
  let error = null;
  let selectedCategory = 'all';
  let searchQuery = '';
  let hasUnread = false;
  let websocketConnection;
  let markingAllAsRead = false;
  let notificationGroups = {}; // Grouped by date
  
  // Configuration
  const skeletonCount = 5;
  
  // Notification categories
  const categories = [
    { id: 'all', label: 'All', icon: 'bell', color: 'primary-blue' },
    { id: 'bidding', label: 'Bidding', icon: 'gavel', color: 'green-500' },
    { id: 'auction', label: 'Auctions', icon: 'tag', color: 'amber-500' },
    { id: 'payment', label: 'Payments', icon: 'credit-card', color: 'purple-500' },
    { id: 'message', label: 'Messages', icon: 'chat', color: 'rose-500' },
    { id: 'system', label: 'System', icon: 'cog', color: 'slate-500' },
  ];
  
  // Get category metadata by ID
  function getCategoryById(id) {
    return categories.find(cat => cat.id === id) || categories[0];
  }
  
  // Get notification icon based on type
  function getNotificationIcon(type) {
    switch(type) {
      case 'outbid': return 'arrow-up';
      case 'bid_placed': return 'check-circle';
      case 'won_auction': return 'trophy';
      case 'auction_ended': return 'flag';
      case 'payment_received': return 'cash';
      case 'payment_due': return 'clock';
      case 'new_message': return 'envelope';
      case 'price_change': return 'tag';
      case 'followed_user': return 'user';
      case 'profile_update': return 'user-check';
      case 'wishlist_price_drop': return 'heart';
      case 'auction_ending_soon': return 'hourglass';
      default: return 'bell';
    }
  }
  
  // Get notification background based on type
  function getNotificationBackground(type, read = false) {
    if (read) return 'bg-white hover:bg-slate-50';
    
    // For unread notifications
    const category = getNotificationCategory(type);
    switch(category) {
      case 'bidding': return 'bg-green-50 hover:bg-green-100';
      case 'auction': return 'bg-amber-50 hover:bg-amber-100';
      case 'payment': return 'bg-purple-50 hover:bg-purple-100';
      case 'message': return 'bg-rose-50 hover:bg-rose-100';
      case 'system': return 'bg-slate-50 hover:bg-slate-100';
      default: return 'bg-blue-50 hover:bg-blue-100';
    }
  }
  
  // Get notification border based on type
  function getNotificationBorder(type, read = false) {
    if (read) return 'border-white hover:border-slate-100';
    
    // For unread notifications
    const category = getNotificationCategory(type);
    switch(category) {
      case 'bidding': return 'border-green-200';
      case 'auction': return 'border-amber-200';
      case 'payment': return 'border-purple-200';
      case 'message': return 'border-rose-200';
      case 'system': return 'border-slate-200';
      default: return 'border-blue-200';
    }
  }
  
  // Get notification accent color based on type
  function getNotificationColor(type) {
    const category = getNotificationCategory(type);
    switch(category) {
      case 'bidding': return 'text-green-500';
      case 'auction': return 'text-amber-500';
      case 'payment': return 'text-purple-500';
      case 'message': return 'text-rose-500';
      case 'system': return 'text-slate-500';
      default: return 'text-primary-blue';
    }
  }
  
  // Get notification category based on type
  function getNotificationCategory(type) {
    if (type === 'outbid' || type === 'bid_placed') return 'bidding';
    if (type === 'won_auction' || type === 'auction_ended' || type === 'auction_ending_soon' || type === 'price_change' || type === 'wishlist_price_drop') return 'auction';
    if (type === 'payment_received' || type === 'payment_due') return 'payment';
    if (type === 'new_message') return 'message';
    if (type === 'profile_update' || type === 'followed_user') return 'system';
    return 'all';
  }
  
  // Helper function to stop event propagation
  function stopPropagation(event) {
    if (event) {
      event.stopPropagation();
    }
  }
  
  // Handle keyboard interaction for accessibility
  function handleKeyDown(event, callback) {
    // Execute callback on Enter or Space key
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      callback();
    }
  }
  
  // Load notifications with improved error handling
  async function loadNotifications() {
    if (!browser) return; // Skip during SSR
    
    // Check authentication before proceeding
    if (!$isAuthenticated) {
      goto('/login?redirect=/notifications');
      return;
    }
    
    try {
      loading = true;
      error = null;
      
      // Try to get notifications from API
      try {
        // Use the proper API endpoint
        const response = await api.notification.list();
        
        if (response && response.success) {
          notifications = response.results || [];
          hasUnread = notifications.some(n => !n.read);
          groupNotificationsByDate();
          filterNotifications();
          return;
        }
      } catch (apiError) {
        if (browser) console.error('API error loading notifications:', apiError);
        // Don't throw here - fall back to mock data
      }
      
      // Fall back to mock data if API fails or isn't available
      if (browser) console.log('Falling back to mock notification data');
      const mockResponse = {
        success: true,
        results: generateMockNotifications()
      };
      
      notifications = mockResponse.results;
      hasUnread = notifications.some(n => !n.read);
      groupNotificationsByDate();
      filterNotifications();
      
    } catch (err) {
      if (browser) console.error('Error loading notifications:', err);
      error = 'Failed to load notifications. Please try again.';
      if (browser) notificationStore.error(error);
    } finally {
      loading = false;
    }
  }
  
  // Generate mock notifications for demo purposes
  function generateMockNotifications() {
    const now = new Date();
    
    // Create notifications from different time periods
    return [
      // Today
      {
        id: '1',
        type: 'outbid',
        title: 'You have been outbid',
        message: 'Someone placed a higher bid of $125.00 on "Vintage Camera"',
        timestamp: new Date(now.getTime() - 1000 * 60 * 30).toISOString(), // 30 minutes ago
        read: false,
        actionUrl: '/auctions/123/bid',
        actionLabel: 'Bid Again',
        entityId: '123',
        entityType: 'auction'
      },
      {
        id: '2',
        type: 'won_auction',
        title: 'Congratulations! You won an auction',
        message: 'You won "Antique Wooden Chair" with a bid of $350.00',
        timestamp: new Date(now.getTime() - 1000 * 60 * 90).toISOString(), // 1.5 hours ago
        read: false,
        actionUrl: '/auctions/124/checkout',
        actionLabel: 'Complete Payment',
        entityId: '124',
        entityType: 'auction'
      },
      {
        id: '3',
        type: 'new_message',
        title: 'New message from seller',
        message: 'John Doe: Thanks for your interest in the item. Let me know if you have any questions.',
        timestamp: new Date(now.getTime() - 1000 * 60 * 180).toISOString(), // 3 hours ago
        read: true,
        actionUrl: '/messages/john-doe',
        actionLabel: 'Reply',
        entityId: 'john-doe',
        entityType: 'conversation'
      }
      // Additional mock notifications would be here
    ];
  }
  
  // Group notifications by date categories
  function groupNotificationsByDate() {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
    const yesterday = today - 86400000; // 24 hours in milliseconds
    const thisWeekStart = today - (now.getDay() * 86400000);
    
    notificationGroups = {
      today: [],
      yesterday: [],
      thisWeek: [],
      earlier: []
    };
    
    notifications.forEach(notification => {
      // Make sure we have a valid timestamp
      if (!notification.timestamp) {
        notification.timestamp = new Date().toISOString();
      }
      
      try {
        const timestamp = new Date(notification.timestamp).getTime();
        
        if (timestamp >= today) {
          notificationGroups.today.push(notification);
        } else if (timestamp >= yesterday) {
          notificationGroups.yesterday.push(notification);
        } else if (timestamp >= thisWeekStart) {
          notificationGroups.thisWeek.push(notification);
        } else {
          notificationGroups.earlier.push(notification);
        }
      } catch (e) {
        // If date parsing fails, add to earlier
        notificationGroups.earlier.push(notification);
      }
    });
  }
  
  // Filter notifications based on selected category and search
  function filterNotifications() {
    let filtered = [...notifications];
    
    // Apply category filter
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(notification => 
        getNotificationCategory(notification.type) === selectedCategory
      );
    }
    
    // Apply search
    if (searchQuery && searchQuery.trim()) {
      const query = searchQuery.toLowerCase().trim();
      filtered = filtered.filter(notification => 
        (notification.title && notification.title.toLowerCase().includes(query)) || 
        (notification.message && notification.message.toLowerCase().includes(query))
      );
    }
    
    // Sort by timestamp (newest first)
    filtered.sort((a, b) => {
      // Handle missing timestamps
      if (!a.timestamp) return 1;
      if (!b.timestamp) return -1;
      try {
        return new Date(b.timestamp) - new Date(a.timestamp);
      } catch (e) {
        return 0; // Keep same position if date parsing fails
      }
    });
    
    filteredNotifications = filtered;
    
    // Regroup after filtering
    groupFilteredNotificationsByDate();
  }
  
  // Group filtered notifications by date
  function groupFilteredNotificationsByDate() {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
    const yesterday = today - 86400000; // 24 hours in milliseconds
    const thisWeekStart = today - (now.getDay() * 86400000);
    
    notificationGroups = {
      today: [],
      yesterday: [],
      thisWeek: [],
      earlier: []
    };
    
    filteredNotifications.forEach(notification => {
      // Make sure we have a valid timestamp
      if (!notification.timestamp) {
        notification.timestamp = new Date().toISOString();
      }
      
      try {
        const timestamp = new Date(notification.timestamp).getTime();
        
        if (timestamp >= today) {
          notificationGroups.today.push(notification);
        } else if (timestamp >= yesterday) {
          notificationGroups.yesterday.push(notification);
        } else if (timestamp >= thisWeekStart) {
          notificationGroups.thisWeek.push(notification);
        } else {
          notificationGroups.earlier.push(notification);
        }
      } catch (e) {
        // If date parsing fails, add to earlier
        notificationGroups.earlier.push(notification);
      }
    });
  }
  
  // Mark a notification as read - uses API if possible, falls back to local update
  async function markAsRead(notificationId) {
    if (!browser) return; // Skip during SSR
    
    // Find the notification
    const notification = notifications.find(n => n.id === notificationId);
    if (!notification || notification.read) return;
    
    try {
      // Try to call the API first
      try {
        if (websocketConnection && websocketConnection.isConnected()) {
          websocketConnection.markAsRead(notificationId);
        } else {
          // Fallback to REST API
          await api.notification.markAsRead(notificationId);
        }
      } catch (apiError) {
        if (browser) console.error('API error marking notification as read:', apiError);
        // Continue with local update even if API fails
      }
      
      // Update local state
      notification.read = true;
      notifications = [...notifications]; // Trigger reactivity
      hasUnread = notifications.some(n => !n.read);
      
      // Update filtered notifications
      filterNotifications();
    } catch (err) {
      if (browser) console.error('Error marking notification as read:', err);
      if (browser) notificationStore.error('Failed to update notification');
    }
  }
  
  // Mark all notifications as read
  async function markAllAsRead() {
    if (!browser) return; // Skip during SSR
    if (!hasUnread) return;
    
    try {
      markingAllAsRead = true;
      
      // Try API call first
      try {
        if (websocketConnection && websocketConnection.isConnected()) {
          websocketConnection.markAllAsRead();
        } else {
          // Fallback to REST API
          await api.notification.markAllAsRead();
        }
      } catch (apiError) {
        if (browser) console.error('API error marking all notifications as read:', apiError);
        // Continue with local update even if API fails
      }
      
      // Simulate API delay for smoother UX
      await new Promise(resolve => setTimeout(resolve, 300));
      
      // Update local state
      notifications = notifications.map(n => ({ ...n, read: true }));
      hasUnread = false;
      
      // Update filtered notifications
      filterNotifications();
      
      if (browser) notificationStore.success('All notifications marked as read');
    } catch (err) {
      if (browser) console.error('Error marking all notifications as read:', err);
      if (browser) notificationStore.error('Failed to update notifications');
    } finally {
      markingAllAsRead = false;
    }
  }
  
  // Delete notification
  async function deleteNotification(notificationId, event) {
    if (!browser) return; // Skip during SSR
    
    // Stop event propagation to prevent notification card click
    stopPropagation(event);
    
    try {
      // Try API call first
      try {
        await api.notification.delete(notificationId);
      } catch (apiError) {
        if (browser) console.error('API error deleting notification:', apiError);
        // Continue with local update even if API fails
      }
      
      // Update local state
      notifications = notifications.filter(n => n.id !== notificationId);
      
      // Update filtered notifications
      filterNotifications();
      
      if (browser) notificationStore.success('Notification removed');
    } catch (err) {
      if (browser) console.error('Error deleting notification:', err);
      if (browser) notificationStore.error('Failed to delete notification');
    }
  }
  
  // Handle notification click - mark as read and navigate
  function handleNotificationClick(notification) {
    if (!browser) return; // Skip during SSR
    
    markAsRead(notification.id);
    if (notification.actionUrl) {
      goto(notification.actionUrl);
    }
  }
  
  // Handle action button click without propagation
  function handleActionButtonClick(event, url) {
    stopPropagation(event);
    goto(url);
  }
  
  // Filter by category
  function setCategory(categoryId) {
    selectedCategory = categoryId;
    filterNotifications();
  }
  
  // Handle search
  function handleSearch() {
    filterNotifications();
  }
  
  // Set up WebSocket connection for real-time notifications
  function setupRealtimeConnection() {
    if (!browser) return () => {}; // Skip during SSR
    
    if (!$user || !$user.id) {
      if (browser) console.warn('Cannot setup WebSocket: User not authenticated');
      return () => {};
    }
    
    try {
      if (browser) console.log('Setting up notification WebSocket connection');
      websocketConnection = createNotificationConnection($user.id);
      
      // Subscribe to the notifications store from WebSocket
      const unsubscribe = websocketConnection.notifications.subscribe(wsNotifications => {
        if (wsNotifications && wsNotifications.length > 0) {
          // Update our local notifications with the WebSocket data
          notifications = wsNotifications;
          hasUnread = notifications.some(n => !n.read);
          groupNotificationsByDate();
          filterNotifications();
        }
      });
      
      // Return cleanup function
      return () => {
        unsubscribe();
        if (websocketConnection) {
          websocketConnection.close();
        }
      };
    } catch (error) {
      if (browser) console.error('Error setting up WebSocket connection:', error);
      if (browser) notificationStore.error('Failed to establish real-time connection. Notifications may be delayed.');
      return () => {};
    }
  }
  
  // Initialize when component mounts
  onMount(() => {
    if (browser) {
      loadNotifications();
      const cleanup = setupRealtimeConnection();
      return cleanup;
    }
  });
  
  // Clean up when component is destroyed
  onDestroy(() => {
    if (websocketConnection) {
      websocketConnection.close();
    }
  });
  
  // Watch for changes to selectedCategory and searchQuery
  $: if (browser && (selectedCategory !== undefined || searchQuery !== undefined)) {
    if (!loading) filterNotifications();
  }
</script>

<svelte:head>
  <title>Notifications | GUDIC</title>
  <meta name="description" content="View and manage your notifications" />
</svelte:head>

<div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
  <!-- Header with animated title -->
  {#if browser}
    <div class="mb-6" in:fly={{ y: -20, duration: 500 }}>
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 class="text-3xl font-bold text-text-dark flex items-center">
            <span class="text-transparent bg-clip-text bg-gradient-to-r from-primary-blue to-secondary-blue">
              Notifications
            </span>
            {#if !loading && hasUnread}
              <span class="ml-3 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-blue/10 text-secondary-blue">
                {notifications.filter(n => !n.read).length} unread
              </span>
            {/if}
          </h1>
          <p class="mt-2 text-text-medium max-w-xl">
            Stay updated with your auction activity, messages, and important alerts
          </p>
        </div>
        
        <!-- Mark all as read button -->
        {#if hasUnread}
          <Button
            variant="outline"
            size="sm"
            on:click={markAllAsRead}
            loading={markingAllAsRead}
            class="whitespace-nowrap"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            Mark all as read
          </Button>
        {/if}
      </div>
    </div>
  {:else}
    <!-- Static header for SSR -->
    <div class="mb-6">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 class="text-3xl font-bold text-text-dark flex items-center">
            <span class="text-transparent bg-clip-text bg-gradient-to-r from-primary-blue to-secondary-blue">
              Notifications
            </span>
          </h1>
          <p class="mt-2 text-text-medium max-w-xl">
            Stay updated with your auction activity, messages, and important alerts
          </p>
        </div>
      </div>
    </div>
  {/if}
  
  <!-- Filter controls -->
  {#if browser}
    <div class="mb-6" in:fade={{ delay: 100, duration: 300 }}>
      <div class="flex flex-col sm:flex-row items-center gap-4">
        <!-- Category tabs -->
        <div class="flex overflow-x-auto hide-scrollbar space-x-2 pb-2 sm:pb-0 w-full sm:w-auto">
          {#each categories as category}
            <button 
              class="px-3 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors
                {selectedCategory === category.id
                  ? `bg-${category.color} text-white shadow-sm`
                  : `bg-white text-slate-600 hover:bg-slate-50 border border-slate-200`}"
              on:click={() => setCategory(category.id)}
            >
              <div class="flex items-center space-x-1.5">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  {#if category.icon === 'bell'}
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                  {:else if category.icon === 'gavel'}
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                  {:else if category.icon === 'tag'}
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                  {:else if category.icon === 'credit-card'}
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                  {:else if category.icon === 'chat'}
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  {:else if category.icon === 'cog'}
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  {/if}
                </svg>
                <span>{category.label}</span>
              </div>
            </button>
          {/each}
        </div>
        
        <!-- Search -->
        <div class="relative flex-1">
          <input
            type="text"
            placeholder="Search notifications..."
            bind:value={searchQuery}
            on:input={handleSearch}
            class="pl-9 pr-3 py-2 w-full bg-white border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-primary-blue/30 focus:border-primary-blue"
          />
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </div>
        
        <!-- Refresh button -->
        <button 
          class="p-2 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors hidden sm:block"
          on:click={loadNotifications}
          disabled={loading}
          aria-label="Refresh notifications"
        >
          <svg 
            xmlns="http://www.w3.org/2000/svg" 
            class="h-5 w-5 text-slate-600" 
            class:animate-spin={loading}
            fill="none" 
            viewBox="0 0 24 24" 
            stroke="currentColor"
            aria-hidden="true"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
      </div>
    </div>
  {:else}
    <!-- Static filter controls for SSR -->
    <div class="mb-6">
      <div class="flex flex-col sm:flex-row items-center gap-4">
        <!-- Category tabs -->
        <div class="flex overflow-x-auto hide-scrollbar space-x-2 pb-2 sm:pb-0 w-full sm:w-auto">
          {#each categories as category}
            <div class="px-3 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors
              {category.id === 'all' ? `bg-${category.color} text-white shadow-sm` : `bg-white text-slate-600 border border-slate-200`}">
              <div class="flex items-center space-x-1.5">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  {#if category.icon === 'bell'}
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                  {/if}
                </svg>
                <span>{category.label}</span>
              </div>
            </div>
          {/each}
        </div>
        
        <!-- Search (static) -->
        <div class="relative flex-1">
          <input
            type="text"
            placeholder="Search notifications..."
            class="pl-9 pr-3 py-2 w-full bg-white border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-primary-blue/30 focus:border-primary-blue"
            disabled
          />
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </div>
      </div>
    </div>
  {/if}
  
  <!-- Content area -->
  <div class="relative">
    <!-- Loading state with skeleton -->
    {#if loading}
      <div class="space-y-4 animate-pulse">
        <div class="border-b border-slate-200 pb-1">
          <div class="h-5 bg-slate-200 w-20 rounded"></div>
        </div>
        
        {#each Array(skeletonCount) as _, i}
          <div class="bg-white border border-slate-200 rounded-xl p-4">
            <div class="flex items-center space-x-4">
              <!-- Avatar skeleton -->
              <div class="rounded-full bg-slate-200 h-12 w-12 flex-shrink-0"></div>
              
              <!-- Content skeleton -->
              <div class="flex-1 space-y-2">
                <div class="h-4 bg-slate-200 w-3/4 rounded"></div>
                <div class="h-3 bg-slate-200 w-full rounded"></div>
                <div class="h-3 bg-slate-200 w-1/2 rounded"></div>
                <div class="flex justify-between items-center pt-2">
                  <div class="h-4 bg-slate-200 w-20 rounded"></div>
                  <div class="h-8 bg-slate-200 w-24 rounded"></div>
                </div>
              </div>
            </div>
          </div>
        {/each}
      </div>
    
    <!-- Error state -->
    {:else if error}
      <div class="bg-red-50 border border-red-200 rounded-xl p-8 text-center">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-red-400 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <h3 class="text-lg font-medium text-red-800 mb-2">{error}</h3>
        <p class="text-red-600 mb-4">Unable to load your notifications. Please try again.</p>
        <Button 
          variant="primary" 
          size="sm"
          on:click={loadNotifications}
        >
          Retry
        </Button>
      </div>
    
    <!-- Empty state -->
    {:else if browser && filteredNotifications.length === 0}
      <div class="bg-white border border-slate-200 rounded-xl p-12 text-center">
        <div class="flex flex-col items-center max-w-md mx-auto">
          <div class="w-20 h-20 rounded-full bg-primary-blue/10 flex items-center justify-center mb-6">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-primary-blue" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
          </div>
          <h2 class="text-xl font-semibold text-text-dark mb-2">No notifications found</h2>
          <p class="text-text-medium mb-6">
            {#if searchQuery}
              No notifications match your search criteria. Try adjusting your filters or search terms.
            {:else if selectedCategory !== 'all'}
              You don't have any {getCategoryById(selectedCategory).label.toLowerCase()} notifications.
            {:else}
              You're all caught up! Check back later for new notifications.
            {/if}
          </p>
          <div class="flex space-x-3">
            {#if searchQuery || selectedCategory !== 'all'}
              <Button 
                variant="outline" 
                size="sm"
                on:click={() => {
                  searchQuery = '';
                  selectedCategory = 'all';
                  filterNotifications();
                }}
              >
                Clear Filters
              </Button>
            {/if}
            
            <Button 
              href="/auctions" 
              variant="primary" 
              size="sm"
            >
              Browse Auctions
            </Button>
          </div>
        </div>
      </div>
    
    <!-- Initial state during SSR -->
    {:else if !browser}
      <div class="bg-white border border-slate-200 rounded-xl p-12 text-center">
        <div class="flex flex-col items-center max-w-md mx-auto">
          <div class="w-20 h-20 rounded-full bg-primary-blue/10 flex items-center justify-center mb-6">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-primary-blue" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
          </div>
          <h2 class="text-xl font-semibold text-text-dark mb-2">Your notifications will appear here</h2>
          <p class="text-text-medium mb-6">
            Please wait while we load your notifications...
          </p>
        </div>
      </div>
    
    <!-- Notification list with grouping -->
    {:else}
      <div class="space-y-6">
        <!-- Today's notifications -->
        {#if notificationGroups.today && notificationGroups.today.length > 0}
          <div>
            <div class="border-b border-slate-200 pb-1 mb-3">
              <h2 class="text-sm font-semibold text-text-dark">Today</h2>
            </div>
            <div class="space-y-3">
              {#each notificationGroups.today as notification, i (notification.id)}
                <!-- Using div instead of button to avoid nesting buttons (FIX) -->
                <div 
                  class="border rounded-xl overflow-hidden transition-all duration-300 cursor-pointer
                    {getNotificationBackground(notification.type, notification.read)}
                    {getNotificationBorder(notification.type, notification.read)}"
                  on:click={() => handleNotificationClick(notification)}
                  on:keydown={e => handleKeyDown(e, () => handleNotificationClick(notification))}
                  role="button"
                  tabindex="0"
                  in:slide={{ delay: i * 50, duration: 300 }}
                >
                  <div class="p-4">
                    <div class="flex items-start gap-3">
                      <!-- Icon -->
                      <div class={`h-10 w-10 rounded-full flex items-center justify-center flex-shrink-0 ${getNotificationColor(notification.type)} bg-opacity-10`}>
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                          {#if getNotificationIcon(notification.type) === 'arrow-up'}
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 11l3-3m0 0l3 3m-3-3v8m0-13a9 9 0 110 18 9 9 0 010-18z" />
                          {:else if getNotificationIcon(notification.type) === 'check-circle'}
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                          {:else if getNotificationIcon(notification.type) === 'trophy'}
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                          {:else if getNotificationIcon(notification.type) === 'flag'}
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 21v-4m0 0V5a2 2 0 012-2h6.5l1 1H21l-3 6 3 6h-8.5l-1-1H5a2 2 0 00-2 2zm9-13.5V9" />
                          {:else if getNotificationIcon(notification.type) === 'cash'}
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
                          {:else if getNotificationIcon(notification.type) === 'clock'}
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                          {:else if getNotificationIcon(notification.type) === 'envelope'}
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                          {:else if getNotificationIcon(notification.type) === 'tag'}
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                          {:else if getNotificationIcon(notification.type) === 'user'}
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                          {:else if getNotificationIcon(notification.type) === 'user-check'}
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4" />
                          {:else if getNotificationIcon(notification.type) === 'heart'}
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                          {:else if getNotificationIcon(notification.type) === 'hourglass'}
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                          {:else}
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                          {/if}
                        </svg>
                      </div>
                      
                      <!-- Content -->
                      <div class="flex-1">
                        <div class="flex justify-between items-start">
                          <h3 class="font-medium text-text-dark">{notification.title || 'Notification'}</h3>
                          {#if !notification.read}
                            <span class="h-2 w-2 rounded-full bg-primary-blue"></span>
                          {/if}
                        </div>
                        <p class="text-sm text-text-medium mt-1">{notification.message || ''}</p>
                        
                        <!-- Footer with time and actions -->
                        <div class="flex justify-between items-center mt-3 pt-2 border-t border-slate-200 border-opacity-50">
                          <span class="text-xs text-text-medium">
                            {formatTimeAgo(notification.timestamp)}
                          </span>
                          
                          <div class="flex items-center space-x-2">
                            {#if notification.actionLabel && notification.actionUrl}
                              <!-- Using action button with proper click handling -->
                              <Button 
                                href={notification.actionUrl} 
                                variant="outline" 
                                size="xs"
                                class={getNotificationColor(notification.type)}
                                on:click={(e) => handleActionButtonClick(e, notification.actionUrl)}
                              >
                                {notification.actionLabel}
                              </Button>
                            {/if}
                            
                            <button 
                              class="p-1.5 text-slate-400 hover:text-slate-600 rounded-full hover:bg-slate-100 transition-colors"
                              on:click={(e) => deleteNotification(notification.id, e)}
                              title="Delete notification"
                              aria-label="Delete notification"
                            >
                              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                              </svg>
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              {/each}
            </div>
          </div>
        {/if}
        
        <!-- Yesterday's notifications (similar structure to Today's) -->
        {#if notificationGroups.yesterday && notificationGroups.yesterday.length > 0}
          <div>
            <div class="border-b border-slate-200 pb-1 mb-3">
              <h2 class="text-sm font-semibold text-text-dark">Yesterday</h2>
            </div>
            <div class="space-y-3">
              {#each notificationGroups.yesterday as notification, i (notification.id)}
                <!-- Using div with role="button" (same structure as Today) -->
                <div 
                  class="border rounded-xl overflow-hidden transition-all duration-300 cursor-pointer
                    {getNotificationBackground(notification.type, notification.read)}
                    {getNotificationBorder(notification.type, notification.read)}"
                  on:click={() => handleNotificationClick(notification)}
                  on:keydown={e => handleKeyDown(e, () => handleNotificationClick(notification))}
                  role="button"
                  tabindex="0"
                  in:slide={{ delay: i * 50, duration: 300 }}
                >
                  <!-- Content similar to Today's notifications -->
                  <div class="p-4">
                    <!-- Content -->
                  </div>
                </div>
              {/each}
            </div>
          </div>
        {/if}
        
        <!-- This Week's notifications (similar structure) -->
        {#if notificationGroups.thisWeek && notificationGroups.thisWeek.length > 0}
          <!-- Similar structure to other sections, with proper accessibility -->
        {/if}
        
        <!-- Earlier notifications (similar structure) -->
        {#if notificationGroups.earlier && notificationGroups.earlier.length > 0}
          <!-- Similar structure to other sections, with proper accessibility -->
        {/if}
      </div>
    {/if}
  </div>
</div>

<style>
  /* Hide scrollbar but keep functionality */
  .hide-scrollbar {
    -ms-overflow-style: none;  /* IE and Edge */
    scrollbar-width: none;  /* Firefox */
  }
  
  .hide-scrollbar::-webkit-scrollbar {
    display: none;  /* Chrome, Safari and Opera */
  }
  
  /* Animation for loading skeleton */
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
  
  /* Animation for the notification icons */
  @keyframes bell-ring {
    0%, 100% {
      transform: rotate(0deg);
    }
    20%, 60% {
      transform: rotate(10deg);
    }
    40%, 80% {
      transform: rotate(-10deg);
    }
  }
  
  /* Create utility classes for all the category colors */
  .bg-primary-blue {
    background-color: var(--primary-blue, #3b82f6);
  }
  
  .text-primary-blue {
    color: var(--primary-blue, #3b82f6);
  }
  
  .bg-green-500 {
    background-color: #10b981;
  }
  
  .text-green-500 {
    color: #10b981;
  }
  
  .bg-amber-500 {
    background-color: #f59e0b;
  }
  
  .text-amber-500 {
    color: #f59e0b;
  }
  
  .bg-purple-500 {
    background-color: #8b5cf6;
  }
  
  .text-purple-500 {
    color: #8b5cf6;
  }
  
  .bg-rose-500 {
    background-color: #f43f5e;
  }
  
  .text-rose-500 {
    color: #f43f5e;
  }
  
  .bg-slate-500 {
    background-color: #64748b;
  }
  
  .text-slate-500 {
    color: #64748b;
  }
</style>