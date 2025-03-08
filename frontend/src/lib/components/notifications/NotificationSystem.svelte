<!-- src/lib/components/notification/NotificationSystem.svelte -->
<script>
  import { onMount, onDestroy } from 'svelte';
  import { fade, fly } from 'svelte/transition';
  import { notificationStore, NotificationType } from '$lib/stores/notificationStore';
  import { authStore } from '$lib/stores/authStore';
  import { createNotificationConnection } from '$lib/websocketService';
  import Spinner from '$lib/components/ui/Spinner.svelte';
  
  // Component state
  let notifications = [];
  let connection = null;
  let liveNotifications = [];
  let showNotificationsPanel = false;
  let unreadCount = 0;
  let connectionStatus = 'disconnected';
  
  // Initialize WebSocket connection for notifications
  function initConnection() {
    // If user is authenticated, connect to WebSocket for live notifications
    if ($authStore.isAuthenticated && $authStore.user?.id) {
      connection = createNotificationConnection($authStore.user.id);
      
      // Subscribe to remote notifications
      const unsubscribeRemote = connection.notifications.subscribe(remoteNotifications => {
        liveNotifications = remoteNotifications;
        
        // Update unread count
        unreadCount = remoteNotifications.filter(n => !n.read).length;
        
        // Process notifications - add new ones to the store
        if (remoteNotifications.length > 0) {
          const latestNotification = remoteNotifications[0];
          
          // If this is a new notification, add it to the local store too
          if (!latestNotification.read && !latestNotification.displayed) {
            notificationStore.add(
              latestNotification.message,
              mapTypeToLocalType(latestNotification.type),
              10000
            );
            
            // Mark it as displayed
            if (connection && connectionStatus === 'connected') {
              connection.send({
                action: 'mark_displayed',
                notification_id: latestNotification.id
              });
            }
          }
        }
      });
      
      // Subscribe to connection status
      const unsubscribeStatus = connection.status.subscribe(status => {
        connectionStatus = status;
      });
      
      return () => {
        unsubscribeRemote();
        unsubscribeStatus();
      };
    }
    
    return () => {};
  }
  
  // Initialize WebSocket connection for notifications
  onMount(() => {
    // Subscribe to local notification store first
    const unsubscribeStore = notificationStore.subscribe(value => {
      notifications = value;
    });
    
    const unsubscribeRemote = initConnection();
    
    return () => {
      unsubscribeStore();
      unsubscribeRemote();
    };
  });
  
  // Clean up WebSocket connection
  onDestroy(() => {
    if (connection) {
      connection.close();
    }
  });
  
  // Map server notification types to client types
  function mapTypeToLocalType(serverType) {
    const typeMap = {
      'INFO': NotificationType.INFO,
      'SUCCESS': NotificationType.SUCCESS,
      'WARNING': NotificationType.WARNING,
      'ERROR': NotificationType.ERROR,
    };
    
    return typeMap[serverType] || NotificationType.INFO;
  }
  
  // Toggle notifications panel
  function toggleNotificationsPanel() {
    showNotificationsPanel = !showNotificationsPanel;
    
    // Mark all as read when opening the panel
    if (showNotificationsPanel && connection && unreadCount > 0 && connectionStatus === 'connected') {
      connection.markAllAsRead();
      unreadCount = 0;
    }
  }
  
  // Mark a notification as read
  function markAsRead(notificationId) {
    if (connection && connectionStatus === 'connected') {
      connection.markAsRead(notificationId);
      
      // Update local unread count
      unreadCount = Math.max(0, unreadCount - 1);
    }
  }
  
  // Retry connection
  function retryConnection() {
    if (connection) {
      connection.reconnect();
    } else {
      initConnection();
    }
  }
  
  // Format notification timestamp
  function formatTime(timestamp) {
    if (!timestamp) return '';
    
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffSec = Math.floor(diffMs / 1000);
    const diffMin = Math.floor(diffSec / 60);
    const diffHour = Math.floor(diffMin / 60);
    const diffDay = Math.floor(diffHour / 24);
    
    if (diffDay > 0) {
      return `${diffDay}d ago`;
    } else if (diffHour > 0) {
      return `${diffHour}h ago`;
    } else if (diffMin > 0) {
      return `${diffMin}m ago`;
    } else {
      return 'Just now';
    }
  }
  
  // Get icon based on notification type
  function getNotificationIcon(type) {
    switch (type) {
      case 'SUCCESS':
      case NotificationType.SUCCESS:
        return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
        </svg>`;
      case 'WARNING':
      case NotificationType.WARNING:
        return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
        </svg>`;
      case 'ERROR':
      case NotificationType.ERROR:
        return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
        </svg>`;
      case 'INFO':
      case NotificationType.INFO:
      default:
        return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
        </svg>`;
    }
  }
  
  // Get background color class based on notification type
  function getBackgroundClass(type) {
    switch (type) {
      case 'SUCCESS':
      case NotificationType.SUCCESS:
        return 'bg-success text-white';
      case 'WARNING':
      case NotificationType.WARNING:
        return 'bg-warning text-white';
      case 'ERROR':
      case NotificationType.ERROR:
        return 'bg-error text-white';
      case 'INFO':
      case NotificationType.INFO:
      default:
        return 'bg-secondary-blue text-white';
    }
  }
</script>

<!-- Toast notifications container (fixed position) -->
<div aria-live="assertive" class="fixed inset-0 flex items-end px-4 py-6 pointer-events-none sm:p-6 sm:items-start z-50">
<div class="w-full flex flex-col items-center space-y-4 sm:items-end">
  {#each notifications as notification (notification.id)}
    <div 
      class="max-w-sm w-full bg-white shadow-lg rounded-lg pointer-events-auto ring-1 ring-black ring-opacity-5 overflow-hidden"
      transition:fly={{ y: 50, duration: 300 }}
      role="alert"
    >
      <div class="p-4">
        <div class="flex items-start">
          <div class="flex-shrink-0">
            <div class={`h-8 w-8 rounded-full flex items-center justify-center ${getBackgroundClass(notification.type)}`}>
              {@html getNotificationIcon(notification.type)}
            </div>
          </div>
          <div class="ml-3 w-0 flex-1 pt-0.5">
            <p class="text-sm font-medium text-text-dark">{notification.message}</p>
            <p class="mt-1 text-xs text-text-medium">{formatTime(notification.timestamp)}</p>
          </div>
          <div class="ml-4 flex-shrink-0 flex">
            <button
              type="button"
              class="bg-white rounded-md inline-flex text-text-medium hover:text-text-dark"
              on:click={() => notificationStore.remove(notification.id)}
            >
              <span class="sr-only">Close</span>
              <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  {/each}
</div>
</div>

<!-- Notification bell (only shown when authenticated) -->
{#if $authStore.isAuthenticated}
<div class="relative">
  <!-- Notification bell button -->
  <button
    type="button"
    class="relative p-2 rounded-full text-text-medium hover:text-text-dark focus:outline-none focus:ring-2 focus:ring-secondary-blue"
    on:click={toggleNotificationsPanel}
  >
    <span class="sr-only">View notifications</span>
    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
    </svg>
    
    {#if unreadCount > 0}
      <span class="absolute top-0 right-0 block h-5 w-5 rounded-full ring-2 ring-white bg-red-500 text-white text-xs font-medium flex items-center justify-center">
        {unreadCount > 9 ? '9+' : unreadCount}
      </span>
    {/if}
  </button>
  
  <!-- Connection status indicator (visible only in notification panel) -->
  {#if connectionStatus !== 'connected' && showNotificationsPanel}
    <div class="absolute top-0 right-0 mt-12 mr-1">
      {#if connectionStatus === 'connecting'}
        <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-yellow-100 text-yellow-800">
          <Spinner size="xs" class="mr-1" />
          Connecting...
        </span>
      {:else if connectionStatus === 'reconnecting'}
        <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-yellow-100 text-yellow-800">
          <Spinner size="xs" class="mr-1" />
          Reconnecting...
        </span>
      {:else if connectionStatus === 'failed'}
        <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800">
          <span class="h-2 w-2 mr-1 bg-red-400 rounded-full"></span>
          Connection Failed
          <button class="ml-1 underline text-red-700" on:click={retryConnection}>
            Retry
          </button>
        </span>
      {:else}
        <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800">
          <span class="h-2 w-2 mr-1 bg-red-400 rounded-full"></span>
          Disconnected
          <button class="ml-1 underline text-red-700" on:click={retryConnection}>
            Connect
          </button>
        </span>
      {/if}
    </div>
  {/if}
  
  <!-- Notifications panel -->
  {#if showNotificationsPanel}
    <div 
      class="origin-top-right absolute right-0 mt-2 w-80 rounded-md shadow-lg py-1 bg-white ring-1 ring-black ring-opacity-5 focus:outline-none z-50"
      transition:fade={{ duration: 150 }}
      role="menu"
      aria-orientation="vertical"
      aria-labelledby="notifications-menu"
    >
      <div class="px-4 py-2 border-b border-primary-blue/10">
        <h3 class="text-sm font-medium text-text-dark">Notifications</h3>
      </div>
      
      <!-- Connection error state -->
      {#if connectionStatus === 'failed'}
        <div class="px-4 py-3 text-center">
          <div class="mb-2 text-red-500">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <p class="text-sm text-text-medium mb-2">Failed to connect to notifications service</p>
          <Button 
            variant="outline" 
            size="sm"
            on:click={retryConnection}
          >
            Retry Connection
          </Button>
        </div>
      {:else}
        <div class="max-h-96 overflow-y-auto">
          {#if connectionStatus === 'connecting' || connectionStatus === 'reconnecting'}
            <div class="text-center py-6">
              <Spinner class="mx-auto mb-3" />
              <p class="text-sm text-text-medium">
                {connectionStatus === 'connecting' ? 'Connecting to notification service...' : 'Reconnecting...'}
              </p>
            </div>
          {:else if liveNotifications.length === 0}
            <div class="text-center py-6 text-text-medium">
              <p>No notifications</p>
            </div>
          {:else}
            <ul class="divide-y divide-primary-blue/10">
              {#each liveNotifications as notification (notification.id)}
                <li 
                  class="px-4 py-3 hover:bg-primary-blue/5 {notification.read ? '' : 'bg-primary-blue/5'}"
                  on:click={() => markAsRead(notification.id)}
                  on:keypress={(e) => e.key === 'Enter' && markAsRead(notification.id)}
                  role="menuitem"
                  tabindex="0"
                >
                  <div class="flex items-start">
                    <div class="flex-shrink-0">
                      <div class={`h-8 w-8 rounded-full flex items-center justify-center ${getBackgroundClass(notification.type)}`}>
                        {@html getNotificationIcon(notification.type)}
                      </div>
                    </div>
                    <div class="ml-3 flex-1">
                      <p class="text-sm font-medium text-text-dark">
                        {notification.message}
                      </p>
                      <p class="mt-1 text-xs text-text-medium">
                        {formatTime(notification.timestamp)}
                      </p>
                    </div>
                    {#if !notification.read}
                      <div class="ml-2 flex-shrink-0">
                        <div class="h-2 w-2 rounded-full bg-secondary-blue"></div>
                      </div>
                    {/if}
                  </div>
                </li>
              {/each}
            </ul>
          {/if}
        </div>
        
        {#if liveNotifications.length > 0 && connectionStatus === 'connected'}
          <div class="px-4 py-2 border-t border-primary-blue/10">
            <button
              type="button"
              class="text-xs text-secondary-blue hover:text-secondary-blue/80 font-medium disabled:opacity-50"
              on:click={() => connection?.markAllAsRead()}
              disabled={connectionStatus !== 'connected' || liveNotifications.every(n => n.read)}
            >
              Mark all as read
            </button>
          </div>
        {/if}
      {/if}
    </div>
    
    <!-- Close notifications panel when clicking outside -->
    <div
      class="fixed inset-0 z-40"
      on:click={() => (showNotificationsPanel = false)}
      on:keypress={(e) => e.key === 'Escape' && (showNotificationsPanel = false)}
    ></div>
  {/if}
</div>
{/if}

<style>
/* Custom scrollbar for notifications list */
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

/* Animation for status indicators */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.bg-red-400 {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>