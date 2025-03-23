<!-- src/lib/components/auction/AuctionTimer.svelte -->
<script>
    import { onMount, onDestroy, createEventDispatcher } from 'svelte';
    import { t } from '$lib/i18n';
    
    // Props
    export let endTime; // ISO date string or Date object
    export let status = 'active'; // active, pending, closed, etc.
    export let showLabels = true;
    export let size = 'default'; // default, small, large
    
    // State
    let days = 0;
    let hours = 0;
    let minutes = 0;
    let seconds = 0;
    let timeLeft = 0;
    let intervalId;
    let isActive = status === 'active';
    let isPending = status === 'pending';
    let isEnded = ['closed', 'sold', 'cancelled'].includes(status);
    
    // Event dispatcher
    const dispatch = createEventDispatcher();
    
    // Calculate time left in seconds
    function calculateTimeLeft() {
      const now = new Date();
      const end = new Date(endTime);
      const diff = Math.floor((end - now) / 1000);
      
      return diff > 0 ? diff : 0;
    }
    
    // Update timer display
    function updateTimer() {
      if (timeLeft <= 0) {
        clearInterval(intervalId);
        isEnded = true;
        isActive = false;
        isPending = false;
        
        // Dispatch event when timer ends
        dispatch('end');
        return;
      }
      
      // Calculate days, hours, minutes, seconds
      days = Math.floor(timeLeft / (60 * 60 * 24));
      hours = Math.floor((timeLeft % (60 * 60 * 24)) / (60 * 60));
      minutes = Math.floor((timeLeft % (60 * 60)) / 60);
      seconds = Math.floor(timeLeft % 60);
      
      timeLeft--;
    }
    
    // Start timer
    function startTimer() {
      timeLeft = calculateTimeLeft();
      updateTimer();
      intervalId = setInterval(updateTimer, 1000);
    }
    
    // Determine timer label based on status
    function getTimerLabel() {
      if (isEnded) {
        return $t('auctions.ended');
      }
      
      if (isPending) {
        return $t('auctions.starts_in');
      }
      
      return $t('auctions.ends_in');
    }
    
    // Get CSS classes based on size
    function getSizeClasses() {
      switch (size) {
        case 'small':
          return 'text-sm';
        case 'large':
          return 'text-2xl font-bold';
        default:
          return 'text-lg';
      }
    }
    
    // Format number with leading zero
    function pad(num) {
      return num.toString().padStart(2, '0');
    }
    
    // Initialize timer on mount
    onMount(() => {
      startTimer();
      
      return () => {
        clearInterval(intervalId);
      };
    });
    
    // Cleanup on destroy
    onDestroy(() => {
      clearInterval(intervalId);
    });
  </script>
  
  <div class="auction-timer">
    {#if showLabels}
      <div class="mb-1 text-sm text-cosmos-text-muted">
        {getTimerLabel()}
      </div>
    {/if}
    
    <div class={`flex items-center justify-center ${getSizeClasses()}`}>
      {#if isEnded}
        <span class="text-status-error">{$t('auctions.ended')}</span>
      {:else if days > 0}
        <!-- Show days when more than 1 day remains -->
        <div class="flex items-center justify-center space-x-1">
          <div class="flex flex-col items-center">
            <span class="font-mono font-bold {isActive ? 'text-status-success' : 'text-status-warning'}">{days}</span>
            {#if showLabels}
              <span class="text-xs text-cosmos-text-dim">{$t('auctions.days')}</span>
            {/if}
          </div>
          <span class="text-cosmos-text-muted">:</span>
          <div class="flex flex-col items-center">
            <span class="font-mono font-bold {isActive ? 'text-status-success' : 'text-status-warning'}">{pad(hours)}</span>
            {#if showLabels}
              <span class="text-xs text-cosmos-text-dim">{$t('auctions.hours')}</span>
            {/if}
          </div>
          <span class="text-cosmos-text-muted">:</span>
          <div class="flex flex-col items-center">
            <span class="font-mono font-bold {isActive ? 'text-status-success' : 'text-status-warning'}">{pad(minutes)}</span>
            {#if showLabels}
              <span class="text-xs text-cosmos-text-dim">{$t('auctions.minutes')}</span>
            {/if}
          </div>
          <span class="text-cosmos-text-muted">:</span>
          <div class="flex flex-col items-center">
            <span class="font-mono font-bold {isActive ? 'text-status-success' : 'text-status-warning'}">{pad(seconds)}</span>
            {#if showLabels}
              <span class="text-xs text-cosmos-text-dim">{$t('auctions.seconds')}</span>
            {/if}
          </div>
        </div>
      {:else}
        <!-- Compact timer when less than 1 day remains -->
        <div class="flex items-center justify-center space-x-1">
          <span class="font-mono font-bold {isActive ? 'text-status-success' : 'text-status-warning'}">{pad(hours)}</span>
          <span class="text-cosmos-text-muted">:</span>
          <span class="font-mono font-bold {isActive ? 'text-status-success' : 'text-status-warning'}">{pad(minutes)}</span>
          <span class="text-cosmos-text-muted">:</span>
          <span class="font-mono font-bold {isActive ? 'text-status-success' : 'text-status-warning'}">{pad(seconds)}</span>
        </div>
      {/if}
    </div>
  </div>