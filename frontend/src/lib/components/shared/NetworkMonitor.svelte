<!-- NetworkMonitor.svelte -->
<script>
    import { onMount, onDestroy } from 'svelte';
    import { notificationStore } from '$lib/stores/notificationStore';
    
    let isOnline = navigator.onLine;
    
    function handleStatusChange() {
      const newStatus = navigator.onLine;
      if (newStatus !== isOnline) {
        isOnline = newStatus;
        
        if (isOnline) {
          notificationStore.success('You are back online!');
        } else {
          notificationStore.error('You are offline. Some features may not work.');
        }
      }
    }
    
    onMount(() => {
      window.addEventListener('online', handleStatusChange);
      window.addEventListener('offline', handleStatusChange);
    });
    
    onDestroy(() => {
      window.removeEventListener('online', handleStatusChange);
      window.removeEventListener('offline', handleStatusChange);
    });
  </script>