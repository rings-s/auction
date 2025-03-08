<!-- src/lib/components/auction/AuctionTimer.svelte -->
<script>
  import { onMount, onDestroy } from 'svelte';
  import { api } from '$lib/api';
  import { formatTimeRemaining } from '$lib/utils/formatters';
  
  // Props
  export let auction = null; // Complete auction object or auction ID
  export let accent = false; // For featured auctions with special styling
  export let size = 'normal'; // 'small', 'normal', 'large'
  export let onTimeUpdate = null; // Optional callback when time updates
  export let onExpired = null; // Optional callback when timer expires
  
  // Reactive state
  $: auctionId = typeof auction === 'object' ? auction?.id : auction;
  $: endTime = typeof auction === 'object' ? auction?.end_time : null;
  $: timerDetails = typeof auction === 'object' ? auction?.timer_details : null;
  
  // Component state
  let remaining = { days: 0, hours: 0, minutes: 0, seconds: 0, total_seconds: 0 };
  let timerInterval = null;
  let isExpired = false;
  let isExtended = false;
  
  // Reactive timer urgency based on remaining time
  $: urgency = getUrgencyLevel(remaining.total_seconds);
  
  // Format time with leading zeros
  function pad(num) {
    return num.toString().padStart(2, '0');
  }
  
  // Determine urgency level based on remaining time
  function getUrgencyLevel(totalSeconds) {
    if (totalSeconds <= 300) return 'high'; // Less than 5 minutes
    if (totalSeconds <= 3600) return 'medium'; // Less than 1 hour
    return 'low'; // More than 1 hour
  }
  
  // Get timer text color based on urgency with consistent color scheme
  function getTextColor(urgency) {
    if (urgency === 'high') return 'text-error';
    if (urgency === 'medium') return 'text-warning';
    return accent ? 'text-secondary-blue' : 'text-text-dark';
  }
  
  // Calculate remaining time
  function calculateRemainingTime() {
    if (!endTime) return;
    
    const now = new Date();
    const end = new Date(endTime);
    
    // If auction has ended
    if (now >= end) {
      remaining = {
        days: 0,
        hours: 0,
        minutes: 0,
        seconds: 0,
        total_seconds: 0
      };
      
      if (!isExpired) {
        isExpired = true;
        if (onExpired) onExpired();
      }
      
      return;
    }
    
    const totalSeconds = Math.floor((end - now) / 1000);
    const days = Math.floor(totalSeconds / 86400);
    const hours = Math.floor((totalSeconds % 86400) / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = totalSeconds % 60;
    
    remaining = {
      days,
      hours,
      minutes,
      seconds,
      total_seconds: totalSeconds
    };
    
    // Check for extension threshold
    if (timerDetails?.auto_extend && totalSeconds <= timerDetails.extension_threshold) {
      // Apply pulsing animation for urgency
      isExtended = true;
    }
    
    // Call the update callback if provided
    if (onTimeUpdate) onTimeUpdate(remaining);
  }
  
  // Fetch auction details if only ID is provided
  async function fetchAuctionDetails() {
    if (!auctionId || typeof auction === 'object') return;
    
    try {
      const auctionData = await api.auction.getById(auctionId);
      endTime = auctionData.end_time;
      timerDetails = auctionData.timer_details;
      calculateRemainingTime();
    } catch (err) {
      console.error('Error fetching auction details for timer:', err);
    }
  }
  
  // Update the auction's timer data when it changes
  $: if (auction && typeof auction === 'object') {
    endTime = auction.end_time;
    timerDetails = auction.timer_details;
    // Reset expired flag if auction end time changes
    if (isExpired && new Date(endTime) > new Date()) {
      isExpired = false;
    }
  }
  
  onMount(() => {
    // If only ID is provided, fetch auction details
    if (auctionId && !endTime) {
      fetchAuctionDetails();
    }
    
    // Initial calculation
    calculateRemainingTime();
    
    // Start interval
    timerInterval = setInterval(calculateRemainingTime, 1000);
    
    return () => {
      if (timerInterval) clearInterval(timerInterval);
    };
  });
  
  onDestroy(() => {
    if (timerInterval) clearInterval(timerInterval);
  });
</script>

<div class="w-full {size === 'small' ? 'text-sm' : size === 'large' ? 'text-lg' : 'text-base'}">
  {#if remaining.total_seconds > 0}
    <div class="flex items-center justify-between">
      <div class="text-xs text-text-medium font-medium">Time Remaining</div>
      <div class={`font-medium ${getTextColor(urgency)}`}>
        {#if remaining.total_seconds > 86400}
          <!-- More than a day left -->
          <span class="timer-digits">{remaining.days}d {pad(remaining.hours)}h {pad(remaining.minutes)}m</span>
        {:else if remaining.total_seconds > 3600}
          <!-- Less than a day but more than an hour -->
          <span class="timer-digits">{pad(remaining.hours)}h {pad(remaining.minutes)}m {pad(remaining.seconds)}s</span>
        {:else}
          <!-- Less than an hour -->
          <span class={`timer-digits ${urgency === 'high' ? 'animate-pulse' : ''}`}>
            {pad(remaining.minutes)}:{pad(remaining.seconds)}
          </span>
        {/if}
      </div>
    </div>
    
    {#if timerDetails?.auto_extend && remaining.total_seconds <= timerDetails.extension_threshold}
      <div class="mt-1 text-xs text-warning flex items-center">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 mr-1" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
        </svg>
        Bid now and extend the auction!
      </div>
    {/if}
    
    <!-- Progress bar with gradient for medium and low urgency -->
    <div class="mt-2 w-full bg-neutral-100 rounded-full h-1.5 overflow-hidden">
      <div 
        class={`h-full rounded-full ${
          urgency === 'high' 
            ? 'bg-error' 
            : urgency === 'medium' 
              ? 'bg-warning' 
              : accent ? 'bg-gradient-to-r from-primary-blue to-primary-peach' : 'bg-text-medium'
        }`}
        style={`width: ${Math.min(100, Math.max(5, remaining.total_seconds > 86400 ? 100 : remaining.total_seconds > 3600 ? 65 : remaining.total_seconds > 300 ? 35 : 10))}%`}
      ></div>
    </div>
  {:else}
    <div class="text-center font-medium text-text-medium">
      Auction Ended
    </div>
  {/if}
</div>

<style>
  /* Subtle highlight for timer digits */
  .timer-digits {
    border-radius: 0.25rem;
    padding: 0.125rem 0.25rem;
    background-color: rgba(185, 220, 242, 0.1);
    transition: all 0.3s ease;
  }
  
  /* Add pulsing effect for high urgency */
  @keyframes pulse-high-urgency {
    0%, 100% { 
      background-color: rgba(229, 123, 123, 0.1); 
    }
    50% { 
      background-color: rgba(229, 123, 123, 0.2); 
    }
  }
  
  .animate-pulse {
    animation: pulse-high-urgency 1s cubic-bezier(0.4, 0, 0.6, 1) infinite;
  }
</style>