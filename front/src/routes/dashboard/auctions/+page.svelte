<!-- src/routes/dashboard/auctions/+page.svelte -->
<script>
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { t } from '$lib/i18n';
    import { user } from '$lib/stores/user';
    import { dashboardAuctions, dashboardLoading } from '$lib/stores/dashboard';
    import { getDashboardAuctions } from '$lib/api/dashboard';
    import { toast } from '$lib/stores/toastStore';
  
    // Components
    import Button from '$lib/components/ui/Button.svelte';
    import FormField from '$lib/components/ui/FormField.svelte';
    import LoadingSkeleton from '$lib/components/ui/LoadingSkeleton.svelte';
    import EmptyState from '$lib/components/ui/EmptyState.svelte';
    import Breadcrumb from '$lib/components/ui/Breadcrumb.svelte';
  
    let searchQuery = '';
    let statusFilter = '';
    let activeOnly = false;
    let currentPage = 1;
    let totalPages = 1;
    let totalAuctions = 0;
  
    // Breadcrumb items
    $: breadcrumbItems = [
      { label: $t('nav.home'), href: '/' },
      { label: $t('dashboard.title'), href: '/dashboard' },
      { label: $t('dashboard.auctions'), href: '/dashboard/auctions', active: true }
    ];
  
    // Status options
    const statusOptions = [
      { value: '', label: $t('common.all') },
      { value: 'draft', label: $t('auction.statusDraft') },
      { value: 'scheduled', label: $t('auction.statusScheduled') },
      { value: 'live', label: $t('auction.statusLive') },
      { value: 'ended', label: $t('auction.statusEnded') },
      { value: 'completed', label: $t('auction.statusCompleted') }
    ];
  
    // Load auctions
    async function loadAuctions() {
      dashboardLoading.set(true);
      
      try {
        const filters = {
          page: currentPage,
          search: searchQuery || undefined,
          status: statusFilter || undefined,
          active_only: activeOnly || undefined
        };
  
        const response = await getDashboardAuctions(filters);
        
        dashboardAuctions.set(response.results || []);
        totalPages = Math.ceil(response.count / 10);
        totalAuctions = response.count || 0;
        
      } catch (error) {
        console.error('Failed to load auctions:', error);
        toast.error($t('dashboard.loadAuctionsError'));
      } finally {
        dashboardLoading.set(false);
      }
    }
  
    // Handle search
    function handleSearch() {
      currentPage = 1;
      loadAuctions();
    }
  
    // Handle filter change
    function handleFilterChange() {
      currentPage = 1;
      loadAuctions();
    }
  
    // Handle pagination
    function handlePageChange(page) {
      currentPage = page;
      loadAuctions();
    }
  
    // Format time remaining
    function formatTimeRemaining(timeRemaining) {
      if (!timeRemaining || timeRemaining.total_seconds <= 0) {
        return $t('auction.auctionEnded');
      }
      
      const { days, hours, minutes } = timeRemaining;
      
      if (days > 0) {
        return `${days}${$t('auction.days')} ${hours}${$t('auction.hours')}`;
      } else if (hours > 0) {
        return `${hours}${$t('auction.hours')} ${minutes}${$t('auction.minutes')}`;
      } else {
        return `${minutes}${$t('auction.minutes')}`;
      }
    }
  
    onMount(() => {
      loadAuctions();
    });
  
    $: auctions = $dashboardAuctions;
    $: isLoading = $dashboardLoading;
  </script>
  
<svelte:head>
  <title>{$t('dashboard.auctions')} - {$t('dashboard.title')} - {$t('app.name')}</title>
</svelte:head>
  
<div class="min-h-screen bg-gray-50">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
    
    <!-- Header -->
    <div class="mb-6">
      <Breadcrumb items={breadcrumbItems} class="mb-4" />
      
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 class="text-xl font-semibold text-gray-900">
            {$t('dashboard.auctions')}
          </h1>
          <p class="mt-1 text-sm text-gray-600">
            {$t('dashboard.manageAuctions')}
          </p>
        </div>
        
        <div class="mt-4 sm:mt-0">
          <Button
            variant="primary"
            size="compact"
            href="/auctions/create"
          >
            {$t('dashboard.createAuction')}
          </Button>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-lg border border-gray-200 p-4 mb-6">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <FormField
          type="text"
          placeholder={$t('common.search')}
          bind:value={searchQuery}
          on:input={handleSearch}
        />
        
        <FormField
          type="select"
          options={statusOptions}
          bind:value={statusFilter}
          on:change={handleFilterChange}
        />
        
        <div class="flex items-center">
          <input
            type="checkbox"
            id="activeOnly"
            bind:checked={activeOnly}
            on:change={handleFilterChange}
            class="h-4 w-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
          />
          <label for="activeOnly" class="ml-2 text-sm text-gray-700">
            {$t('auction.activeOnly')}
          </label>
        </div>
        
        <Button
          variant="outline"
          size="default"
          onClick={() => {
            searchQuery = '';
            statusFilter = '';
            activeOnly = false;
            handleFilterChange();
          }}
        >
          {$t('search.clear')}
        </Button>
      </div>
    </div>

    <!-- Auctions List -->
    {#if isLoading}
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {#each Array(6) as _}
          <LoadingSkeleton type="auctionCard" />
        {/each}
      </div>
    {:else if auctions.length === 0}
      <EmptyState
        icon="auction"
        title={$t('dashboard.noAuctions')}
        description={$t('dashboard.noAuctionsDesc')}
        actionLabel={$t('dashboard.createAuction')}
        actionUrl="/auctions/create"
      />
    {:else}
      <div class="space-y-4">
        <!-- Auctions Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {#each auctions as auction (auction.id)}
            <div class="bg-white rounded-lg border border-gray-200 overflow-hidden hover:shadow-md transition-shadow">
              
              <!-- Auction Image -->
              <div class="aspect-w-16 aspect-h-9 bg-gray-200 relative">
                {#if auction.property_title}
                  <div class="absolute top-2 left-2 z-10">
                    <span class="inline-flex items-center px-2 py-1 rounded text-xs font-medium {
                      auction.status === 'live' ? 'bg-green-100 text-green-800' :
                      auction.status === 'scheduled' ? 'bg-blue-100 text-blue-800' :
                      auction.status === 'ended' ? 'bg-gray-100 text-gray-800' :
                      'bg-yellow-100 text-yellow-800'
                    }">
                      {auction.status_display}
                    </span>
                  </div>
                {/if}
                
                <div class="flex items-center justify-center">
                  <svg class="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
              </div>

              <!-- Auction Info -->
              <div class="p-4">
                <div class="flex items-start justify-between mb-2">
                  <h3 class="text-sm font-medium text-gray-900 truncate flex-1">
                    {auction.title}
                  </h3>
                  
                  <div class="flex items-center space-x-1 ml-2">
                    {#if auction.is_featured}
                      <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-yellow-100 text-yellow-800">
                        {$t('auction.featured')}
                      </span>
                    {/if}
                  </div>
                </div>

                <p class="text-xs text-gray-600 mb-2">
                  {auction.property_title || $t('auction.noProperty')}
                </p>

                <div class="space-y-2 mb-3">
                  <div class="flex items-center justify-between text-xs">
                    <span class="text-gray-500">{$t('auction.currentBid')}</span>
                    <span class="font-medium text-gray-900">
                      ${(auction.current_bid || auction.starting_bid)?.toLocaleString() || 0}
                    </span>
                  </div>
                  
                  <div class="flex items-center justify-between text-xs">
                    <span class="text-gray-500">{$t('auction.totalBids')}</span>
                    <span class="font-medium text-gray-900">
                      {auction.bid_count || 0}
                    </span>
                  </div>
                  
                  {#if auction.is_active}
                    <div class="flex items-center justify-between text-xs">
                      <span class="text-gray-500">{$t('auction.timeRemaining')}</span>
                      <span class="font-medium text-primary-600">
                        {formatTimeRemaining(auction.time_remaining)}
                      </span>
                    </div>
                  {/if}
                </div>

                <div class="flex items-center justify-between">
                  <div class="text-xs text-gray-500">
                    {auction.days_until_start > 0 ? 
                      `${$t('auction.startsIn')} ${auction.days_until_start} ${$t('auction.days')}` :
                      formatTimeRemaining(auction.time_remaining)
                    }
                  </div>
                  
                  <div class="flex items-center space-x-2">
                    <Button
                      variant="outline"
                      size="compact"
                      href="/auctions/{auction.slug}"
                    >
                      {$t('common.view')}
                    </Button>
                    
                    <Button
                      variant="ghost"
                      size="compact"
                      href="/auctions/{auction.id}/edit"
                    >
                      {$t('common.edit')}
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          {/each}
        </div>

        <!-- Pagination -->
        {#if totalPages > 1}
          <div class="flex items-center justify-between bg-white px-4 py-3 border border-gray-200 rounded-lg">
            <div class="flex items-center">
              <p class="text-sm text-gray-700">
                {$t('dashboard.showing')} 
                <span class="font-medium">{(currentPage - 1) * 10 + 1}</span>
                {$t('common.to')}
                <span class="font-medium">{Math.min(currentPage * 10, totalAuctions)}</span>
                {$t('common.of')}
                <span class="font-medium">{totalAuctions}</span>
                {$t('dashboard.auctions')}
              </p>
            </div>
            
            <div class="flex items-center space-x-2">
              <Button
                variant="outline"
                size="compact"
                disabled={currentPage === 1}
                onClick={() => handlePageChange(currentPage - 1)}
              >
                {$t('common.previous')}
              </Button>
              
              <span class="text-sm text-gray-700">
                {currentPage} / {totalPages}
              </span>
              
              <Button
                variant="outline"
                size="compact"
                disabled={currentPage === totalPages}
                onClick={() => handlePageChange(currentPage + 1)}
              >
                {$t('common.next')}
              </Button>
            </div>
          </div>
        {/if}
      </div>
    {/if}
  </div>
</div>