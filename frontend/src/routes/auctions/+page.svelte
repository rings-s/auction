<!-- src/routes/auctions/+page.svelte -->
<script>
  import { onMount, onDestroy } from 'svelte';
  import { t, isRTL } from '$lib/i18n';
  import { page } from '$app/stores';
  import { auctionActions, loading, auctionsList, auctionsMetadata } from '$lib/stores/auction';
  
  // Components
  import AuctionGrid from '$lib/components/auctions/AuctionGrid.svelte';
  import Breadcrumb from '$lib/components/ui/Breadcrumb.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Select from '$lib/components/ui/Select.svelte';
  import { goto } from '$app/navigation';
  
  // Get query params from URL
  let queryParams = {};
  let auctionType = '';
  
  // URL parameter subscription
  const unsubscribe = page.subscribe(($page) => {
    // Extract query params from URL
    const params = new URLSearchParams($page.url.search);
    
    // Build query params object
    queryParams = {};
    
    for (const [key, value] of params.entries()) {
      queryParams[key] = value;
    }
    
    // Check if auction type is specified in URL
    auctionType = params.get('auction_type') || '';
  });
  
  // Auction type options for filter tabs
  const auctionTypeOptions = [
    { id: '', label: $t('general.all') },
    { id: 'active', label: $t('auctions.active_auctions') },
    { id: 'upcoming', label: $t('auctions.upcoming_auctions') },
    { id: 'closed', label: $t('auctions.closed_auctions') }
  ];
  
  // Handle auction type change
  function setAuctionType(type) {
    // Update URL
    const url = new URL(window.location);
    
    if (type) {
      url.searchParams.set('auction_type', type);
    } else {
      url.searchParams.delete('auction_type');
    }
    
    goto(url.toString());
  }
  
  // Handle creating a new auction
  function createAuction() {
    goto('/auctions/create');
  }
  
  // Cleanup on component destroy
  onDestroy(() => {
    unsubscribe();
  });
</script>

<svelte:head>
  <title>{$t('auctions.title')} | {$t('general.app_name')}</title>
  <meta name="description" content={$t('auctions.title')} />
</svelte:head>

<div class="auctions-page container mx-auto px-4 py-8">
  <!-- Breadcrumb -->
  <div class="mb-6">
    <Breadcrumb
      items={[
        { label: $t('navigation.home'), href: '/' },
        { label: $t('auctions.title'), href: '/auctions', active: true }
      ]}
    />
  </div>
  
  <!-- Page Header with Title and Actions -->
  <div class="mb-8 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
    <div>
      <h1 class="text-3xl font-bold text-neutral-900 dark:text-neutral-100">
        {$t('auctions.title')}
      </h1>
      <p class="mt-2 text-neutral-600 dark:text-neutral-400">
        {$t('auctions.explore_properties')}
      </p>
    </div>
    
    <div class="flex flex-wrap items-center gap-3">
      <!-- View Options (Grid/List) -->
      <div class="hidden md:flex bg-white dark:bg-neutral-800 rounded-lg border border-neutral-200 dark:border-neutral-700 p-1">
        <button 
          class="p-2 rounded-md text-neutral-800 dark:text-neutral-200 hover:bg-neutral-100 dark:hover:bg-neutral-700 transition-colors"
          aria-label="Grid view"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
          </svg>
        </button>
        <button 
          class="p-2 rounded-md text-neutral-500 dark:text-neutral-400 hover:bg-neutral-100 dark:hover:bg-neutral-700 transition-colors"
          aria-label="List view"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
          </svg>
        </button>
      </div>
      
      <!-- Create Auction Button (for authorized users) -->
      <Button 
        variant="primary" 
        on:click={createAuction}
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 {isRTL() ? 'ml-1.5' : 'mr-1.5'}" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" />
        </svg>
        {$t('auctions.create_auction')}
      </Button>
    </div>
  </div>
  
  <!-- Auction Type Filter Tabs -->
  <div class="mb-6 border-b border-neutral-200 dark:border-neutral-700">
    <div class="flex flex-wrap -mb-px">
      {#each auctionTypeOptions as option}
        <button 
          class={`inline-block py-4 px-4 text-sm font-medium border-b-2 ${
            auctionType === option.id 
              ? 'border-primary-600 text-primary-600 dark:border-primary-400 dark:text-primary-400' 
              : 'border-transparent text-neutral-500 hover:text-neutral-700 hover:border-neutral-300 dark:text-neutral-400 dark:hover:text-neutral-300 dark:hover:border-neutral-600'
          }`}
          on:click={() => setAuctionType(option.id)}
        >
          {option.label}
        </button>
      {/each}
    </div>
  </div>
  
  <!-- Auction Grid Component -->
  <AuctionGrid
    initialFilters={queryParams}
    autoPaginate={true}
    pageSize={12}
    showFilters={true}
    filtersExpanded={false}
  />
</div>