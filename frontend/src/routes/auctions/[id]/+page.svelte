<script>
    import { onMount, onDestroy } from 'svelte';
    import { t } from '$lib/i18n';
    import { page } from '$app/stores';
    import { auctionActions, currentAuction, currentBids, loading, errors } from '$lib/stores/auction';
    import { formatCurrency, formatDate } from '$lib/utils/formatters';
    import { notifications } from '$lib/stores/notification';
    import { toast } from '$lib/stores/toast';
    import { animateSequence } from '$lib/utils/animations';
    import { goto } from '$app/navigation';
    import AuctionTimer from '$components/auctions/AuctionTimer.svelte';
    import BidHistory from '$components/auctions/BidHistory.svelte';
    
    // Helper function to get status color
    function getStatusColor(status) {
      const colors = {
        'active': 'status-success',
        'pending': 'status-warning',
        'extended': 'status-info',
        'closed': 'cosmos-text-dim',
        'sold': 'status-error',
        'cancelled': 'status-error'
      };
      
      return colors[status] || 'cosmos-text-dim';
    }
    
    // Get auction ID from URL params
    let auctionId = '';
    let animElements;
    let unsubscribe;
    
    // Subscribe to page store to get auction ID from URL params
    $: if ($page && $page.params && $page.params.id) {
        auctionId = $page.params.id;
        loadAuctionData();
    }
    
    // Load auction data from store
    async function loadAuctionData() {
        if (!auctionId) return;
        
        try {
            // Load auction details with related data
            await auctionActions.loadAuctionDetail(
                auctionId, 
                true,  // include bids
                true   // include property
            );
            
            // Check if we need to load bids separately
            if (!$currentAuction?.recent_bids?.length && $currentAuction) {
                await auctionActions.loadAuctionBids(auctionId);
            }
            
            // Animate elements when data is loaded
            if (animElements && $currentAuction) {
                setTimeout(() => {
                    animateSequence(animElements, {
                        animation: 'fadeInUp',
                        delay: 100,
                        stagger: 100
                    });
                }, 200);
            }
            
        } catch (error) {
            console.error('Error loading auction:', error);
            toast.error($t('system_messages.error_loading_auction'));
        }
    }
    
    // Handle auction timer end
    function handleAuctionEnd() {
        // Reload auction data to get updated status
        loadAuctionData();
        
        // Show toast notification
        toast.info($t('auctions.auction_has_ended'));
    }
    
    // Navigate to bid page
    function navigateToBidPage() {
        goto(`/auctions/${auctionId}/bid`);
    }
    
    onMount(() => {
        // Initialize notification store
        const notifyCleanup = notifications.init();
        
        // Reload auction data if already pre-loaded but might be stale
        if ($currentAuction && $currentAuction.id === auctionId) {
            loadAuctionData();
        }
        
        return () => {
            if (notifyCleanup) notifyCleanup();
        };
    });
    
    onDestroy(() => {
        // Reset current auction in store when leaving the page
        auctionActions.resetCurrentAuction();
    });
</script>

<svelte:head>
    {#if $currentAuction}
        <title>{$currentAuction.title} | {$t('general.site_name')}</title>
        <meta name="description" content={$currentAuction.description || $t('auctions.auction_details')} />
    {:else}
        <title>{$t('auctions.auction_details')} | {$t('general.site_name')}</title>
        <meta name="description" content={$t('auctions.loading_auction_details')} />
    {/if}
</svelte:head>

<!-- Main content -->
<div class="container mx-auto px-4 py-8">
    {#if $loading.currentAuctionLoading}
        <!-- Loading state -->
        <div class="flex justify-center p-20">
            <div class="animate-pulse-slow flex flex-col items-center">
                <div class="h-16 w-16 rounded-full bg-primary bg-opacity-20"></div>
                <p class="mt-4 text-cosmos-text-muted">{$t('general.loading')}</p>
            </div>
        </div>
    {:else if $errors.detailError}
        <!-- Error state -->
        <div class="rounded-xl bg-status-error bg-opacity-10 p-6 text-center">
            <p class="text-status-error">{$errors.detailError}</p>
            <button 
                class="mt-4 rounded-lg bg-primary px-4 py-2 text-white hover:bg-primary-dark"
                on:click={loadAuctionData}
            >
                {$t('general.retry')}
            </button>
        </div>
    {:else if $currentAuction}
        <!-- Auction Header -->
        <div class="mb-8 flex flex-col lg:flex-row lg:items-center lg:justify-between">
            <div>
                <h1 class="text-3xl font-bold text-cosmos-text">{$currentAuction.title}</h1>
                <p class="mt-2 text-cosmos-text-muted">
                    {$currentAuction.related_property?.title || ''}
                </p>
                
                <div class="mt-4 flex flex-wrap gap-3">
                    <span class={`rounded-full px-3 py-1 text-sm text-white bg-${getStatusColor($currentAuction.status)}`}>
                        {$currentAuction.status_display || $t(`auctions.status.${$currentAuction.status}`)}
                    </span>
                    
                    {#if $currentAuction.related_property}
                        <span class="rounded-full bg-property-{$currentAuction.related_property.property_type} bg-opacity-80 px-3 py-1 text-sm text-white">
                            {$currentAuction.related_property.property_type_display || $t(`properties.types.${$currentAuction.related_property.property_type}`)}
                        </span>
                    {/if}
                    
                    {#if $currentAuction.is_featured}
                        <span class="rounded-full bg-[#FFD700] px-3 py-1 text-sm text-cosmos-bg-dark">
                            {$t('general.featured')}
                        </span>
                    {/if}
                </div>
            </div>
            
            <div class="mt-6 lg:mt-0">
                {#if isActive}
                    <div class="rounded-xl bg-primary bg-opacity-5 p-4">
                        <AuctionTimer 
                            endTime={$currentAuction.end_date}
                            status={$currentAuction.status}
                            on:end={handleAuctionEnd}
                        />
                    </div>
                {:else if isPending}
                    <div class="rounded-xl bg-status-warning bg-opacity-5 p-4">
                        <AuctionTimer 
                            endTime={$currentAuction.start_date}
                            status={$currentAuction.status}
                            on:end={handleAuctionEnd}
                        />
                    </div>
                {:else}
                    <div class="rounded-xl bg-cosmos-bg-light p-4 text-center">
                        <p class="text-cosmos-text-muted">
                            {$t('auctions.ended')}
                        </p>
                    </div>
                {/if}
            </div>
        </div>
        
        <!-- Main Content -->
        <div class="grid grid-cols-1 gap-8 lg:grid-cols-3">
            <!-- Left Column - Images and Description -->
            <div class="lg:col-span-2">
                <!-- Main Image -->
                <div class="mb-6 overflow-hidden rounded-xl">
                    <img 
                        src={$currentAuction.featured_image_url || '/images/placeholders/auction-placeholder.jpg'} 
                        alt={$currentAuction.title}
                        class="w-full object-cover"
                    />
                </div>
                
                <!-- Image Gallery -->
                {#if $currentAuction.related_property && $currentAuction.related_property.images && $currentAuction.related_property.images.length > 1}
                    <div class="mb-8 grid grid-cols-4 gap-2">
                        {#each $currentAuction.related_property.images.slice(0, 4) as image, i}
                            <div class="overflow-hidden rounded-lg">
                                <img 
                                    src={image.path} 
                                    alt={`${$currentAuction.related_property.title} - ${i + 1}`}
                                    class="h-24 w-full cursor-pointer object-cover hover:opacity-90"
                                />
                            </div>
                        {/each}
                    </div>
                {/if}
                
                <!-- Auction Description -->
                <div class="mb-8 rounded-xl bg-cosmos-bg-light bg-opacity-20 p-6 backdrop-blur-sm">
                    <h2 class="mb-4 text-xl font-bold text-cosmos-text">{$t('auctions.auction_details')}</h2>
                    <p class="mb-4 text-cosmos-text">{$currentAuction.description}</p>
                    
                    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                        <div>
                            <p class="text-sm text-cosmos-text-muted">{$t('auctions.auction_type')}</p>
                            <p class="font-medium text-cosmos-text">{$currentAuction.auction_type_display}</p>
                        </div>
                        
                        <div>
                            <p class="text-sm text-cosmos-text-muted">{$t('auctions.start_date')}</p>
                            <p class="font-medium text-cosmos-text">{formatDate($currentAuction.start_date)}</p>
                        </div>
                        
                        <div>
                            <p class="text-sm text-cosmos-text-muted">{$t('auctions.end_date')}</p>
                            <p class="font-medium text-cosmos-text">{formatDate($currentAuction.end_date)}</p>
                        </div>
                        
                        <div>
                            <p class="text-sm text-cosmos-text-muted">{$t('auctions.starting_price')}</p>
                            <p class="font-medium text-cosmos-text">{formatCurrency($currentAuction.starting_price)}</p>
                        </div>
                        
                        <div>
                            <p class="text-sm text-cosmos-text-muted">{$t('auctions.current_bid')}</p>
                            <p class="font-bold text-primary">{formatCurrency($currentAuction.current_bid)}</p>
                        </div>
                        
                        <div>
                            <p class="text-sm text-cosmos-text-muted">{$t('auctions.min_increment')}</p>
                            <p class="font-medium text-cosmos-text">{formatCurrency($currentAuction.min_bid_increment)}</p>
                        </div>
                    </div>
                </div>
                
                <!-- Bid History Section -->
                <div class="mb-8">
                    <BidHistory 
                        {auctionId} 
                        bids={$currentBids || []}
                        isLoading={$loading.bidsLoading}
                        winningBid={$currentBids && $currentBids.length > 0 ? $currentBids[0] : null}
                        onRefresh={() => auctionActions.loadAuctionBids(auctionId)}
                    />
                </div>
            </div>
            
            <!-- Right Column - Bid Form and Summary -->
            <div>
                <!-- Bid Form Card -->
                <div class="mb-6 rounded-xl bg-cosmos-bg-light bg-opacity-30 p-6 backdrop-blur-sm">
                    <h3 class="mb-4 text-xl font-bold text-cosmos-text">{$t('auctions.place_bid')}</h3>
                    
                    <div class="mb-4 space-y-4">
                        <div>
                            <p class="text-sm text-cosmos-text-muted">{$t('auctions.current_bid')}</p>
                            <p class="text-2xl font-bold text-primary">{formatCurrency($currentAuction.current_bid)}</p>
                        </div>
                        
                        <div class="flex items-center justify-between">
                            <div>
                                <p class="text-sm text-cosmos-text-muted">{$t('auctions.bid_count')}</p>
                                <p class="text-lg font-medium text-cosmos-text">{$currentAuction.bid_count}</p>
                            </div>
                            
                            <div>
                                <p class="text-sm text-cosmos-text-muted">{$t('auctions.min_increment')}</p>
                                <p class="text-lg font-medium text-cosmos-text">{formatCurrency($currentAuction.min_bid_increment)}</p>
                            </div>
                        </div>
                    </div>
                    
                    <div class="mt-6">
                        {#if canBid}
                            <a 
                                href={`/auctions/${auctionId}/bid`}
                                class="block w-full rounded-lg bg-primary py-3 text-center font-medium text-white transition hover:bg-primary-dark"
                            >
                                {$t('auctions.place_bid')}
                            </a>
                        {:else if isPending}
                            <div class="rounded-lg bg-status-warning bg-opacity-10 p-4 text-center">
                                <p class="text-status-warning">
                                    {$t('auctions.starts_in')}
                                </p>
                            </div>
                        {:else if isEnded}
                            <div class="rounded-lg bg-cosmos-text-dim bg-opacity-10 p-4 text-center">
                                <p class="text-cosmos-text-dim">
                                    {$t('auctions.ended')}
                                </p>
                            </div>
                        {/if}
                    </div>
                </div>
                
                <!-- Property Summary Card -->
                {#if $currentAuction.related_property}
                    <div class="rounded-xl bg-cosmos-bg-light bg-opacity-30 p-6 backdrop-blur-sm">
                        <h3 class="mb-4 text-lg font-bold text-cosmos-text">{$t('properties.property_details')}</h3>
                        
                        <div class="space-y-4">
                            <div class="flex items-center">
                                <div class="mr-3 h-10 w-10 flex-shrink-0 rounded-full bg-property-{$currentAuction.related_property.property_type} bg-opacity-20 p-2">
                                    <!-- Icon based on property type -->
                                    <svg class="h-full w-full text-property-{$currentAuction.related_property.property_type}" fill="currentColor" viewBox="0 0 20 20">
                                        <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z" />
                                    </svg>
                                </div>
                                
                                <div class="flex-grow">
                                    <p class="text-sm text-cosmos-text-muted">{$t('properties.property_type')}</p>
                                    <p class="font-medium text-cosmos-text">{$currentAuction.related_property.property_type_display}</p>
                                </div>
                            </div>
                            
                            <div class="flex items-center">
                                <div class="mr-3 h-10 w-10 flex-shrink-0 rounded-full bg-primary bg-opacity-20 p-2">
                                    <!-- Location icon -->
                                    <svg class="h-full w-full text-primary" fill="currentColor" viewBox="0 0 20 20">
                                        <path fill-rule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clip-rule="evenodd" />
                                    </svg>
                                </div>
                                
                                <div class="flex-grow">
                                    <p class="text-sm text-cosmos-text-muted">{$t('properties.property_location')}</p>
                                    <p class="font-medium text-cosmos-text">{$currentAuction.related_property.city}, {$currentAuction.related_property.district}</p>
                                </div>
                            </div>
                            
                            <div class="flex items-center">
                                <div class="mr-3 h-10 w-10 flex-shrink-0 rounded-full bg-primary bg-opacity-20 p-2">
                                    <!-- Area icon -->
                                    <svg class="h-full w-full text-primary" fill="currentColor" viewBox="0 0 20 20">
                                        <path fill-rule="evenodd" d="M4 4a2 2 0 012-2h8a2 2 0 012 2v12a1 1 0 01-1 1h-2a1 1 0 01-1-1v-2a1 1 0 00-1-1H9a1 1 0 00-1 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V4zm3 1h2v2H7V5zm2 4H7v2h2V9zm2-4h2v2h-2V5zm2 4h-2v2h2V9z" clip-rule="evenodd" />
                                    </svg>
                                </div>
                                
                                <div class="flex-grow">
                                    <p class="text-sm text-cosmos-text-muted">{$t('properties.property_area')}</p>
                                    <p class="font-medium text-cosmos-text">{$currentAuction.related_property.area} m²</p>
                                </div>
                            </div>
                        </div>
                        
                        <div class="mt-6">
                            <a 
                                href={`/properties/${$currentAuction.related_property.id}`}
                                class="block w-full rounded-lg bg-primary bg-opacity-10 py-3 text-center text-sm font-medium text-primary transition hover:bg-primary hover:text-white"
                            >
                                {$t('properties.view_property')}
                            </a>
                        </div>
                    </div>
                {/if}
            </div>
        </div>
    {:else}
        <!-- No auction data found -->
        <div class="flex h-32 items-center justify-center">
            <p class="text-cosmos-text-muted">{$t('general.not_found')}</p>
        </div>
    {/if}
</div>

<!-- Floating Bid Button - Only show for active auctions -->
{#if $currentAuction && $currentAuction.status === 'active'}
    <div class="fixed bottom-6 right-6 z-header sm:bottom-8 sm:right-8">
        <button
            on:click={navigateToBidPage}
            class="flex items-center gap-2 rounded-full bg-primary px-6 py-3 text-white shadow-glow transition hover:bg-primary-dark"
        >
            <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            <span class="font-medium">{$t('auctions.place_bid')}</span>
        </button>
    </div>
{/if}

<!-- Error toast displayed when there's an error loading auction -->
{#if $errors.detailError}
    <div class="toast-error">{$errors.detailError}</div>
{/if}