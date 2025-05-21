<!-- src/routes/account/bids/+page.svelte -->
<script>
  import { onMount } from 'svelte';
  import { t } from '$lib/i18n/i18n';
  import { user } from '$lib/stores/user';
  import { goto } from '$app/navigation';
  import { fetchUserBids } from '$lib/api/auction';
  import Button from '$lib/components/ui/Button.svelte';
  import AuctionStatus from '$lib/components/auction/AuctionStatus.svelte';
  import LoadingSkeleton from '$lib/components/ui/LoadingSkeleton.svelte';
  import Alert from '$lib/components/ui/Alert.svelte';
  
  let bids = [];
  let loading = true;
  let error = null;
  
  onMount(async () => {
    // Check if user is logged in
    if (!$user) {
      goto('/login?redirect=/account/bids');
      return;
    }
    
    await loadBids();
  });
  
  async function loadBids() {
    try {
      loading = true;
      error = null;
      
      const response = await fetchUserBids();
      bids = response.results || response;
      
      // Sort bids by bid time (newest first)
      bids.sort((a, b) => new Date(b.bid_time) - new Date(a.bid_time));
      
    } catch (err) {
      console.error('Error loading user bids:', err);
      error = err.message;
    } finally {
      loading = false;
    }
  }
  
  function formatDateTime(dateString) {
    try {
      const date = new Date(dateString);
      return new Intl.DateTimeFormat('default', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      }).format(date);
    } catch (e) {
      return dateString;
    }
  }
</script>

<svelte:head>
  <title>{$t('account.myBids')} | Real Estate Platform</title>
</svelte:head>

<div class="bg-gray-50 dark:bg-gray-900 min-h-screen py-8 px-4 sm:px-6 lg:px-8">
  <div class="max-w-7xl mx-auto">
    <div class="md:flex md:items-center md:justify-between mb-6">
      <div class="flex-1 min-w-0">
        <h1 class="text-2xl font-bold leading-7 text-gray-900 dark:text-white sm:text-3xl">
          {$t('account.myBids')}
        </h1>
        <p class="mt-1 text-gray-500 dark:text-gray-400">
          {$t('account.myBidsDesc')}
        </p>
      </div>
      <div class="mt-4 flex md:mt-0 md:ml-4">
        <Button
          variant="primary"
          href="/auctions"
          aria-label={$t('auction.viewAuctions')}
        >
          {$t('auction.viewAuctions')}
        </Button>
      </div>
    </div>
    
    {#if loading}
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <LoadingSkeleton type="text" class="mb-4" />
        <LoadingSkeleton type="text" class="mb-4" />
        <LoadingSkeleton type="text" class="mb-4" />
      </div>
    {:else if error}
      <Alert 
        type="error" 
        title={$t('error.title')} 
        message={error}
      />
    {:else if bids.length === 0}
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 text-center">
        <svg class="h-12 w-12 mx-auto text-gray-400 dark:text-gray-500 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
        <h2 class="text-lg font-medium text-gray-900 dark:text-white mb-1">
          {$t('account.noBids')}
        </h2>
        <p class="text-gray-500 dark:text-gray-400 mb-4">
          {$t('account.noBidsMessage')}
        </p>
        <Button
          variant="primary"
          href="/auctions"
          aria-label={$t('auction.startBidding')}
        >
          {$t('auction.startBidding')}
        </Button>
      </div>
    {:else}
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead class="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  {$t('auction.auction')}
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  {$t('auction.bidAmount')}
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  {$t('auction.bidTime')}
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  {$t('auction.status')}
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  {$t('common.actions')}
                </th>
              </tr>
            </thead>
            <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {#each bids as bid}
                <tr>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm font-medium text-gray-900 dark:text-white">
                      {bid.auction_info?.title || 'Unknown Auction'}
                    </div>
                    <div class="text-xs text-gray-500 dark:text-gray-400">
                      ID: {bid.auction_id}
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm font-medium text-gray-900 dark:text-white">
                      ${parseFloat(bid.amount).toLocaleString()}
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm text-gray-500 dark:text-gray-400">
                      {formatDateTime(bid.bid_time)}
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <AuctionStatus status={bid.status} isCompact={true} />
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm">
                    <Button
                      variant="outline"
                      size="small"
                      href={`/auctions/${bid.auction_info?.slug || bid.auction_id}`}
                      aria-label={$t('auction.viewAuction')}
                    >
                      {$t('auction.viewAuction')}
                    </Button>
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      </div>
    {/if}
  </div>
</div>