<!-- src/lib/components/auction/edit/AuctionEditHeader.svelte -->
<script>
  import { t } from '$lib/i18n';
  import AuctionStatus from '$lib/components/auction/AuctionStatus.svelte';
  
  export let auction;
  // Removed unused export property 'saving'
</script>

<div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
  <div class="md:flex md:items-start md:justify-between">
    <div class="flex-1 min-w-0">
      <div class="flex items-center space-x-3 mb-2">
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
          {$t('auction.editAuction')}
        </h1>
        {#if auction}
          <AuctionStatus status={auction.status} />
        {/if}
      </div>
      
      {#if auction}
        <h2 class="text-lg text-primary-600 dark:text-primary-400 font-medium mb-2">
          {auction.title}
        </h2>
        <p class="text-sm text-neutral-600 dark:text-neutral-400">
          {$t('auction.editAuctionDesc')} • ID: #{auction.id}
        </p>
      {:else}
        <p class="text-sm text-neutral-600 dark:text-neutral-400">
          {$t('auction.editAuctionDesc')}
        </p>
      {/if}
    </div>
    
    <!-- Quick Info Panel -->
    {#if auction}
      <div class="mt-4 md:mt-0 md:ml-6">
        <div class="bg-neutral-50 dark:bg-neutral-800 rounded-lg p-4 min-w-0 md:min-w-[200px]">
          <h3 class="text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-3">
            {$t('auction.quickInfo')}
          </h3>
          <dl class="space-y-2">
            <div class="flex justify-between text-sm">
              <dt class="text-neutral-500 dark:text-neutral-400">{$t('auction.status')}:</dt>
              <dd class="font-medium text-gray-900 dark:text-white">
                {auction.status.charAt(0).toUpperCase() + auction.status.slice(1)}
              </dd>
            </div>
            <div class="flex justify-between text-sm">
              <dt class="text-neutral-500 dark:text-neutral-400">{$t('auction.currentBid')}:</dt>
              <dd class="font-medium text-success-600 dark:text-success-400">
                ${(auction.current_bid || auction.starting_bid || 0).toLocaleString()}
              </dd>
            </div>
            <div class="flex justify-between text-sm">
              <dt class="text-neutral-500 dark:text-neutral-400">{$t('auction.totalBids')}:</dt>
              <dd class="font-medium text-gray-900 dark:text-white">
                {auction.bid_count || 0}
              </dd>
            </div>
          </dl>
        </div>
      </div>
    {/if}
  </div>
</div>