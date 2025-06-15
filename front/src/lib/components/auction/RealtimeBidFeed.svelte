<!-- src/lib/components/auction/RealtimeBidFeed.svelte -->
<script>
    import { onMount, onDestroy } from 'svelte';
    import { t } from '$lib/i18n';
    
    export let maxItems = 5;
    
    let recentBids = [];
    let ws;
    
    onMount(() => {
      // Connect to WebSocket for real-time updates
      connectWebSocket();
    });
    
    onDestroy(() => {
      if (ws) ws.close();
    });
    
    function connectWebSocket() {
      // This would connect to your WebSocket endpoint
      // For now, using mock data
      simulateRealtimeBids();
    }
    
    function simulateRealtimeBids() {
      // Simulate incoming bids for demo
      setInterval(() => {
        const mockBid = {
          id: Date.now(),
          auctionTitle: 'Sample Auction',
          amount: Math.floor(Math.random() * 10000) + 1000,
          bidderName: 'User***',
          timestamp: new Date()
        };
        
        recentBids = [mockBid, ...recentBids].slice(0, maxItems);
      }, 15000);
    }
    
    function getTimeAgo(date) {
      const seconds = Math.floor((new Date() - date) / 1000);
      if (seconds < 60) return 'just now';
      if (seconds < 3600) return Math.floor(seconds / 60) + 'm ago';
      return Math.floor(seconds / 3600) + 'h ago';
    }
</script>
  
<div class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4">
  <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-3 flex items-center">
    <span class="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></span>
    Live Bid Activity
  </h3>
  
  <div class="space-y-2">
    {#each recentBids as bid (bid.id)}
      <div class="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-700 rounded-lg animate-fadeIn">
        <div class="flex-1 min-w-0">
          <p class="text-sm font-medium text-gray-900 dark:text-white truncate">
            {bid.auctionTitle}
          </p>
          <p class="text-xs text-gray-500 dark:text-gray-400">
            {bid.bidderName} • {getTimeAgo(bid.timestamp)}
          </p>
        </div>
        <div class="text-right">
          <p class="text-sm font-bold text-green-600 dark:text-green-400">
            ${bid.amount.toLocaleString()}
          </p>
        </div>
      </div>
    {:else}
      <p class="text-sm text-gray-500 dark:text-gray-400 text-center py-4">
        Waiting for new bids...
      </p>
    {/each}
  </div>
</div>
  
<style>
  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(-10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  
  .animate-fadeIn {
    animation: fadeIn 0.3s ease-out;
  }
</style>