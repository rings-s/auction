<!-- src/routes/+layout.svelte -->
<script>
  import { onMount } from 'svelte';
  import { browser } from '$app/environment';
  import { navigating } from '$app/stores';
  import { fade, fly } from 'svelte/transition';
  import { quintOut } from 'svelte/easing';
  import Header from '$lib/components/layout/Header.svelte';
  import Footer from '$lib/components/layout/Footer.svelte';
  import SearchOverlay from '$lib/components/search/SearchOverlay.svelte';
  import '../app.css';
  
  // Safely handle browser-only imports
  let authStore;
  let isAuthenticated;
  let isVerified;
  let notificationStore;
  let NotificationType;
  let searchOpen;
  
  // Notification handling
  let notifications = [];
  let showSearch = false;
  
  // Auth state verification
  let authCheckComplete = false;
  
  // Enhanced token management and authentication verification
  async function verifyAuthState() {
    if (!browser) return;
    
    const accessToken = localStorage.getItem('accessToken');
    const refreshToken = localStorage.getItem('refreshToken');
    const lastActivity = localStorage.getItem('lastActivity');
    const now = Date.now();
    
    // Check for token expiration based on inactivity
    if (lastActivity && now - parseInt(lastActivity) > 24 * 60 * 60 * 1000) {
      console.log('Token expired due to inactivity, logging out');
      authStore.logout();
      notificationStore.warning('Your session has expired. Please log in again.');
      return;
    }
    
    // Update last activity
    if (browser) {
      localStorage.setItem('lastActivity', now.toString());
    }
    
    // Verify token with backend if we have one
    if (accessToken && refreshToken) {
      try {
        await authStore.verifyAuth();
        console.log('Token verification successful');
      } catch (error) {
        console.error('Token verification failed:', error);
        // The auth store will handle logout if token is invalid
      }
    }
    
    authCheckComplete = true;
  }
  
  onMount(async () => {
    if (browser) {
      // Dynamically import browser-only modules
      const authModule = await import('$lib/stores/authStore');
      const notifModule = await import('$lib/stores/notificationStore');
      const uiModule = await import('$lib/stores/uiStore');
      
      authStore = authModule.authStore;
      isAuthenticated = authModule.isAuthenticated;
      isVerified = authModule.isVerified;
      notificationStore = notifModule.notificationStore;
      NotificationType = notifModule.NotificationType;
      searchOpen = uiModule.searchOpen;
      
      // Subscribe to notifications
      const unsubNotifications = notificationStore.subscribe(value => {
        notifications = value;
      });
      
      // Subscribe to search state
      const unsubSearch = searchOpen.subscribe(value => {
        showSearch = value;
      });
      
      // Verify authentication state
      verifyAuthState();
      
      return () => {
        unsubNotifications();
        unsubSearch();
      };
    }
  });
  
  // Update last activity on navigation when in browser
  $: if (browser && $navigating) {
    localStorage.setItem('lastActivity', Date.now().toString());
  }
  
  function removeNotification(id) {
    if (browser && notificationStore) {
      notificationStore.remove(id);
    }
  }
  
  // Get notification icon based on type
  function getNotificationIcon(type) {
    if (!browser || !NotificationType) return '';
    
    switch (type) {
      case NotificationType.SUCCESS:
        return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
        </svg>`;
      case NotificationType.ERROR:
        return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
        </svg>`;
      case NotificationType.WARNING:
        return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
        </svg>`;
      default:
        return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
        </svg>`;
    }
  }
  
  // Get notification styles based on type
  function getNotificationStyle(type) {
    if (!browser || !NotificationType) return '';
    
    switch (type) {
      case NotificationType.SUCCESS:
        return 'bg-white border-l-4 border-success text-success';
      case NotificationType.ERROR:
        return 'bg-white border-l-4 border-error text-error';
      case NotificationType.WARNING:
        return 'bg-white border-l-4 border-warning text-warning';
      default:
        return 'bg-white border-l-4 border-secondary-blue text-secondary-blue';
    }
  }
</script>

<svelte:head>
  <!-- Add Font - Inter -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@100..900&display=swap" rel="stylesheet">
</svelte:head>

<!-- Main layout with modern design and gradient background -->
<div class="min-h-screen flex flex-col font-[Inter]">
  <!-- Global search overlay -->
  {#if browser && showSearch}
    <div transition:fade={{ duration: 150 }}>
      <SearchOverlay />
    </div>
  {/if}

  <!-- Header Component -->
  <Header />
  
  <!-- Main content area with proper spacing -->
  <main class="flex-grow pt-20">
    <!-- Decorative gradient elements - client-side only -->
    {#if browser}
      <div class="fixed inset-0 -z-10 overflow-hidden">
        <!-- Top-right blob -->
        <div class="absolute top-0 right-0 w-96 h-96 bg-primary-blue opacity-30 rounded-full filter blur-3xl transform translate-x-1/3 -translate-y-1/3 animate-blob"></div>
        
        <!-- Left blob -->
        <div class="absolute top-1/3 left-0 w-96 h-96 bg-primary-peach opacity-30 rounded-full filter blur-3xl transform -translate-x-1/2 animate-blob animation-delay-2000"></div>
        
        <!-- Bottom-right blob -->
        <div class="absolute bottom-0 right-1/4 w-96 h-96 bg-primary-blue opacity-20 rounded-full filter blur-3xl transform translate-y-1/3 animate-blob animation-delay-4000"></div>
      </div>
    {/if}
    
    <!-- Content container with glass effect for important content -->
    <div class="relative z-10">
      <slot />
    </div>
  </main>
  
  <!-- Footer Component -->
  <Footer />
</div>

<!-- Toast notifications with animations - client-side only -->
{#if browser && notifications.length > 0}
  <div class="fixed bottom-0 right-0 z-50 m-6 flex flex-col space-y-4 max-w-md">
    {#each notifications as notification (notification.id)}
      <div
        class="transform transition-all duration-300 ease-in-out w-full"
        in:fly={{ y: 20, duration: 300, easing: quintOut }}
        out:fly={{ y: 20, duration: 200, easing: quintOut }}
      >
        <div class="rounded-lg shadow-lg p-4 flex items-start {getNotificationStyle(notification.type)}">
          <div class="flex-shrink-0">
            {@html getNotificationIcon(notification.type)}
          </div>
          <div class="ml-3 flex-1">
            <p class="text-sm font-medium">
              {notification.message}
            </p>
          </div>
          <div class="ml-auto pl-3">
            <div class="-mx-1.5 -my-1.5">
              <button
                type="button"
                class="inline-flex rounded-md p-1.5 focus:outline-none focus:ring-2 focus:ring-offset-2"
                on:click={() => removeNotification(notification.id)}
              >
                <span class="sr-only">Dismiss</span>
                <svg class="h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                  <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    {/each}
  </div>
{/if}

<style>
  :global(body) {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
      Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    color: var(--text-dark);
  }
  
  :global(h1, h2, h3, h4, h5, h6) {
    font-weight: 700;
    line-height: 1.2;
    color: var(--text-dark);
  }
  
  :global(button, a, input, select, textarea) {
    transition: all 0.2s ease;
  }
</style>