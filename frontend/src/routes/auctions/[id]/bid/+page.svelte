<script>
    import { onMount, onDestroy } from 'svelte';
    import { t } from '$lib/i18n';
    import { page } from '$app/stores';
    import { auctionActions, currentAuction, currentBids, loading, errors } from '$lib/stores/auction';
    import { formatCurrency, formatDate } from '$lib/utils/formatters';
    import { notifications } from '$lib/stores/notification';
    import { toast } from '$lib/stores/toast';
    import { goto } from '$app/navigation';
    import AuctionTimer from '$components/auctions/AuctionTimer.svelte';
    import BidForm from '$components/auctions/BidForm.svelte';
    import BidHistory from '$components/auctions/BidHistory.svelte';
    
    // Get auction ID from URL params
    let auctionId = '';
    let bidPlaced = false;
    let bidLoading = false;
    
    // Subscribe to page store to get auction ID from URL params
    $: if ($page && $page.params && $page.params.id) {
        auctionId = $page.params.id;
        loadAuctionData();
    }
    
    // Derived values
    $: isActive = $currentAuction?.status === 'active';
    $: isPending = $currentAuction?.status === 'pending';
    $: isEnded = ['closed', 'sold', 'cancelled'].includes($currentAuction?.status);
    $: canBid = isActive && !$loading.currentAuctionLoading;
    
    // Load auction data
    async function loadAuctionData() {
        if (!auctionId) return;
        
        try {
            // Load auction details with related data
            await auctionActions.loadAuctionDetail(auctionId, true, true);
            
            // Check if auction is not active
            if ($currentAuction && $currentAuction.status !== 'active') {
                // Show toast message for inactive auctions
                if ($currentAuction.status === 'pending') {
                    toast.warning($t('auctions.cannot_bid_pending'));
                } else if (isEnded) {
                    toast.error($t('auctions.cannot_bid_ended'));
                }
            }
        } catch (error) {
            console.error('Error loading auction:', error);
            toast.error($t('system_messages.error_loading_auction'));
        }
    }
    
    // Handle bid form submission
    async function handleBidSubmit(event) {
        if (!$currentAuction) return;
        
        bidLoading = true;
        const { bidAmount, isAutoBid, maxBidAmount } = event.detail;
        
        try {
            const result = await auctionActions.placeBid(
                auctionId,
                bidAmount,
                isAutoBid,
                maxBidAmount
            );
            
            if (result && result.success) {
                bidPlaced = true;
                toast.success($t('auctions.bid_placed_successfully'));
                
                // Reload auction and bids data
                await loadAuctionData();
                
                // Wait briefly and navigate back to auction details
                setTimeout(() => {
                    navigateToAuctionDetails(true);
                }, 2000);
            } else {
                throw new Error(result.error || $t('system_messages.error_occurred'));
            }
        } catch (error) {
            console.error('Error placing bid:', error);
            toast.error(error.message || $t('auctions.error_placing_bid'));
        } finally {
            bidLoading = false;
        }
    }
    
    // Handle auction timer end
    function handleAuctionEnd() {
        // Reload auction data to get updated status
        loadAuctionData();
        
        // Show toast notification
        toast.info($t('auctions.auction_has_ended'));
        
        // Navigate back to auction details
        setTimeout(() => {
            navigateToAuctionDetails();
        }, 1500);
    }
    
    // Navigate back to auction details
    function navigateToAuctionDetails(withNotification = false) {
        let url = `/auctions/${auctionId}`;
        if (withNotification) {
            url += '?notification=bid_success';
        }
        goto(url);
    }
    
    onMount(() => {
        // Initialize notifications
        const cleanup = notifications.init();
        
        return () => {
            if (cleanup) cleanup();
        };
    });
    
    onDestroy(() => {
        // Reset errors in store when leaving the page
        auctionActions.resetErrors();
    });
</script>

<svelte:head>
    {#if $currentAuction}
        <title>{$t('auctions.place_bid')} - {$currentAuction.title} | {$t('general.site_name')}</title>
        <meta name="description" content={$t('auctions.place_bid_description')} />
    {:else}
        <title>{$t('auctions.place_bid')} | {$t('general.site_name')}</title>
        <meta name="description" content={$t('auctions.loading_auction_details')} />
    {/if}
</svelte:head>

<div class="min-h-screen bg-cosmos-bg">
    <div class="container mx-auto px-4 py-8">
        <!-- Back button and page title -->
        <div class="mb-6 flex items-center space-x-4">
            <button 
                on:click={() => navigateToAuctionDetails()}
                class="flex items-center text-cosmos-text-muted hover:text-cosmos-text"
            >
                <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                </svg>
                <span class="ml-2">{$t('general.back')}</span>
            </button>
            
            <h1 class="text-2xl font-bold text-cosmos-text">{$t('auctions.place_bid')}</h1>
        </div>
        
        {#if $loading.currentAuctionLoading}
            <!-- Loading state -->
            <div class="flex justify-center p-12">
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
            <!-- Bidding interface when auction data is loaded -->
            <div class="grid grid-cols-1 gap-8 lg:grid-cols-3">
                <!-- Left column - Auction details -->
                <div class="lg:col-span-2">
                    <!-- Auction info card -->
                    <div class="mb-6 rounded-xl bg-cosmos-bg-light bg-opacity-30 p-6 backdrop-blur-sm">
                        <div class="mb-4 flex items-center justify-between">
                            <div>
                                <h2 class="text-xl font-bold text-cosmos-text">{$currentAuction.title}</h2>
                                {#if $currentAuction.related_property}
                                    <p class="text-cosmos-text-muted">{$currentAuction.related_property.title}</p>
                                {/if}
                            </div>
                            
                            <!-- Auction status badge -->
                            <div>
                                {#if isActive}
                                    <span class="rounded-full bg-status-success px-3 py-1 text-xs text-white">
                                        {$t('auctions.status.active')}
                                    </span>
                                {:else if isPending}
                                    <span class="rounded-full bg-status-warning px-3 py-1 text-xs text-white">
                                        {$t('auctions.status.pending')}
                                    </span>
                                {:else}
                                    <span class="rounded-full bg-cosmos-text-dim px-3 py-1 text-xs text-white">
                                        {$currentAuction.status_display || $t(`auctions.status.${$currentAuction.status}`)}
                                    </span>
                                {/if}
                            </div>
                        </div>
                        
                        <!-- Auction timer -->
                        <div class="mb-6 rounded-lg bg-cosmos-bg p-4">
                            <AuctionTimer 
                                endTime={$currentAuction.end_date}
                                status={$currentAuction.status}
                                showLabels={true}
                                size="large"
                                on:end={handleAuctionEnd}
                            />
                        </div>
                        
                        <!-- Auction info -->
                        <div class="grid grid-cols-2 gap-4 sm:grid-cols-3">
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
                            
                            <div>
                                <p class="text-sm text-cosmos-text-muted">{$t('auctions.bid_count')}</p>
                                <p class="font-medium text-cosmos-text">{$currentAuction.bid_count}</p>
                            </div>
                            
                            <div>
                                <p class="text-sm text-cosmos-text-muted">{$t('auctions.start_date')}</p>
                                <p class="font-medium text-cosmos-text">{formatDate($currentAuction.start_date)}</p>
                            </div>
                            
                            <div>
                                <p class="text-sm text-cosmos-text-muted">{$t('auctions.end_date')}</p>
                                <p class="font-medium text-cosmos-text">{formatDate($currentAuction.end_date)}</p>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Bid history -->
                    <div class="rounded-xl bg-cosmos-bg-light bg-opacity-30 p-6 backdrop-blur-sm">
                        <BidHistory 
                            {auctionId} 
                            bids={$currentBids} 
                            isLoading={$loading.bidsLoading}
                            winningBid={$currentBids && $currentBids.length > 0 ? $currentBids[0] : null}
                            onRefresh={() => auctionActions.loadAuctionBids(auctionId)}
                            pageCount={$currentAuction?.bid_pages || 1}
                            currentPage={1}
                            onPageChange={(page) => {
                                auctionActions.loadAuctionBids(auctionId, { page });
                            }}
                        />
                    </div>
                </div>
                
                <!-- Right column - Bid form -->
                <div>
                    <div class="sticky top-20 rounded-xl bg-cosmos-bg-light bg-opacity-30 p-6 backdrop-blur-sm">
                        <h3 class="mb-4 text-xl font-bold text-cosmos-text">{$t('auctions.place_bid')}</h3>
                        
                        {#if bidPlaced}
                            <!-- Success message after bid is placed -->
                            <div class="rounded-lg bg-status-success bg-opacity-10 p-4 text-center">
                                <p class="text-status-success">{$t('auctions.bid_placed_successfully')}</p>
                                <p class="mt-2 text-sm text-cosmos-text-muted">{$t('auctions.redirecting')}</p>
                            </div>
                        {:else if !canBid}
                            <!-- Message when bidding is not possible -->
                            <div class="rounded-lg bg-cosmos-text-dim bg-opacity-10 p-4 text-center">
                                {#if isPending}
                                    <p class="text-cosmos-text-muted">{$t('auctions.cannot_bid_pending')}</p>
                                {:else if isEnded}
                                    <p class="text-cosmos-text-muted">{$t('auctions.cannot_bid_ended')}</p>
                                {:else}
                                    <p class="text-cosmos-text-muted">{$t('auctions.cannot_bid_generic')}</p>
                                {/if}
                                
                                <button 
                                    class="mt-4 rounded-lg bg-primary px-4 py-2 text-white hover:bg-primary-dark"
                                    on:click={() => navigateToAuctionDetails()}
                                >
                                    {$t('general.back_to_auction')}
                                </button>
                            </div>
                        {:else}
                            <!-- Bid form -->
                            <BidForm 
                                auction={$currentAuction}
                                on:bid-placed={handleBidSubmit}
                            />
                            
                            <!-- Bidding rules -->
                            <div class="mt-6 rounded-lg bg-cosmos-bg p-4">
                                <h4 class="mb-2 font-medium text-cosmos-text">{$t('auctions.bidding_rules')}</h4>
                                <ul class="list-inside list-disc space-y-2 text-sm text-cosmos-text-muted">
                                    <li>{$t('auctions.bidding_rule_1')}</li>
                                    <li>{$t('auctions.bidding_rule_2')}</li>
                                    <li>{$t('auctions.bidding_rule_3')}</li>
                                    <li>{$t('auctions.bidding_rule_4')}</li>
                                </ul>
                            </div>
                        {/if}
                    </div>
                </div>
            </div>
        {:else}
            <!-- No auction data found -->
            <div class="rounded-xl bg-cosmos-bg-light bg-opacity-30 p-6 text-center">
                <p class="text-cosmos-text-muted">{$t('auctions.auction_not_found')}</p>
                <a 
                    href="/auctions"
                    class="mt-4 inline-block rounded-lg bg-primary px-4 py-2 text-white hover:bg-primary-dark"
                >
                    {$t('auctions.browse_auctions')}
                </a>
            </div>
        {/if}
    </div>
</div>