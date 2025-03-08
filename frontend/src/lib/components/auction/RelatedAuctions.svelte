<!-- src/lib/components/auction/RelatedAuctions.svelte -->
<script>
  import { onMount } from 'svelte';
  import { api } from '$lib/api';
  import AuctionCard from './AuctionCard.svelte';
  import Spinner from '$lib/components/ui/Spinner.svelte';
  
  // Props
  export let currentAuctionId = '';
  export let categoryId = '';
  export let subcategoryId = '';
  export let limit = 4;
  export let title = "Related Auctions";
  export let viewAllLink = "/auctions";
  export let viewAllLabel = "Browse All Auctions";
  export let showViewAllButton = true;
  export let containerClass = ""; // Additional class for the container
  
  // State
  let auctions = [];
  let loading = true;
  let error = null;
  
  // Load related auctions
  async function loadRelatedAuctions() {
    try {
      loading = true;
      error = null;
      
      // Prepare query parameters
      const params = {
        category: categoryId,
        status: 'ACTIVE',
        sort_by: 'created_at',
        direction: 'desc',
        page_size: limit + 1 // Fetch one extra to account for filtering out current
      };
      
      // Add subcategory if available
      if (subcategoryId) {
        params.subcategory = subcategoryId;
      }
      
      const response = await api.auction.list({
        params
      });
      
      // Filter out the current auction
      auctions = (response.results || [])
        .filter(auction => auction.id !== currentAuctionId)
        .slice(0, limit);
      
      loading = false;
    } catch (err) {
      console.error('Error loading related auctions:', err);
      error = 'Failed to load related auctions.';
      loading = false;
    }
  }
  
  // If no related auctions found, try with category only
  async function tryFallbackQuery() {
    if (!auctions.length && subcategoryId) {
      try {
        const params = {
          category: categoryId,
          status: 'ACTIVE',
          sort_by: 'created_at',
          direction: 'desc',
          page_size: limit + 1
        };
        
        const response = await api.auction.list({
          params
        });
        
        // Filter out the current auction
        auctions = (response.results || [])
          .filter(auction => auction.id !== currentAuctionId)
          .slice(0, limit);
      } catch (err) {
        console.error('Error loading fallback auctions:', err);
      }
    }
  }
  
  onMount(() => {
    if (categoryId) {
      loadRelatedAuctions().then(() => {
        // If no auctions found, try fallback query
        tryFallbackQuery();
      });
    }
  });
</script>

{#if auctions.length > 0}
<div class={containerClass}>
  <h2 class="text-xl font-semibold text-text-dark mb-6">{title}</h2>
  
  {#if loading}
    <div class="flex justify-center py-8">
      <Spinner size="lg" />
    </div>
  {:else if error}
    <div class="bg-red-50 p-4 rounded-md text-red-600 mb-4">
      <p class="text-center">{error}</p>
    </div>
  {:else}
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
      {#each auctions as auction (auction.id)}
        <AuctionCard {auction} compact={true} />
      {/each}
    </div>
    
    {#if showViewAllButton}
      <div class="mt-6 text-center">
        <a href={viewAllLink} class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-blue">
          {viewAllLabel}
        </a>
      </div>
    {/if}
  {/if}
</div>
{/if}