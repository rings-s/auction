<!-- src/lib/components/auction/RecentAuctions.svelte -->
<script>
  import { onMount } from 'svelte';
  import { api } from '$lib/api';
  import AuctionCard from './AuctionCard.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Spinner from '$lib/components/ui/Spinner.svelte';
  
  // Props
  export let title = "Recent Auctions";
  export let viewAllLink = "/auctions";
  export let viewAllLabel = "View All";
  export let limit = 4;
  export let showHeader = true;
  export let params = {
    status: 'ACTIVE',
    sort_by: 'created_at',
    direction: 'desc'
  };
  export let emptyStateMessage = "No auctions available";
  export let showCompact = false;
  export let featured = false;
  
  // State variables
  let auctions = [];
  let loading = true;
  let error = null;
  
  // Load auctions based on params
  async function loadAuctions() {
    try {
      loading = true;
      
      const apiParams = {
        ...params,
        page_size: limit
      };
      
      const response = await api.auction.list({
        params: apiParams
      });
      
      auctions = response.results || [];
      loading = false;
    } catch (err) {
      console.error('Error loading auctions:', err);
      error = 'Failed to load auctions';
      loading = false;
    }
  }
  
  // Initialize on mount
  onMount(() => {
    loadAuctions();
  });
</script>

{#if showHeader}
  <div class="flex items-center justify-between mb-6">
    <h2 class="text-xl md:text-2xl font-semibold text-text-dark">{title}</h2>
    <Button 
      href={viewAllLink} 
      variant="outline" 
      size="sm"
    >
      {viewAllLabel}
    </Button>
  </div>
{/if}

{#if loading}
  <div class="flex justify-center py-12">
    <Spinner size="lg" />
  </div>
{:else if error}
  <div class="bg-red-50 p-4 rounded-md text-red-600 mb-4">
    <p class="text-center">{error}</p>
    <div class="flex justify-center mt-4">
      <Button 
        variant="outline" 
        size="sm"
        on:click={loadAuctions}
      >
        Try Again
      </Button>
    </div>
  </div>
{:else if auctions.length === 0}
  <div class="bg-white rounded-xl p-8 text-center shadow-sm border border-gray-200">
    <p class="text-text-medium">{emptyStateMessage}</p>
  </div>
{:else}
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
    {#each auctions as auction (auction.id)}
      <AuctionCard auction={auction} compact={showCompact} {featured} />
    {/each}
  </div>
{/if}