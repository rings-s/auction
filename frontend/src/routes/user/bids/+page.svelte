<!-- src/routes/user/bids/+page.svelte -->
<script>
    import { onMount } from 'svelte';
    import { bidStore } from '$lib/stores/bidStore';
    import { notificationStore } from '$lib/stores/notificationStore';
    import Button from '$lib/components/ui/Button.svelte';
    import Spinner from '$lib/components/ui/Spinner.svelte';
    import Alert from '$lib/components/ui/Alert.svelte';
    import { formatDate, formatCurrency } from '$lib/utils/formatters';
    
    // State
    let loading = true;
    let error = null;
    let filters = {
        status: '',
        sort_by: 'created_at',
        direction: 'desc'
    };
    let pagination = {
        page: 1,
        total_pages: 1,
        count: 0,
        next: null,
        previous: null
    };
    
    // Fetch bids on component mount
    onMount(async () => {
        try {
            await loadBids();
        } catch (err) {
            console.error('Error loading bids:', err);
            error = 'Failed to load your bids';
            notificationStore.error(error);
        } finally {
            loading = false;
        }
    });
    
    // Load bids with current filters
    async function loadBids(page = 1) {
        loading = true;
        error = null;
        
        try {
            await bidStore.loadUserBids({
                ...filters,
                page: page
            });
            
            // Update pagination from store
            pagination = {
                page: page,
                ...($bidStore.pagination)
            };
            
        } catch (err) {
            error = err.error || 'Failed to load your bids';
            notificationStore.error(error);
        } finally {
            loading = false;
        }
    }
    
    // Handle filter changes
    function handleFilterChange() {
        loadBids(1); // Reset to first page when filters change
    }
    
    // Handle pagination
    function goToPage(page) {
        if (page < 1 || page > pagination.total_pages) return;
        loadBids(page);
        window.scrollTo(0, 0);
    }
    
    // Get bid status badge style
    function getBidStatusClass(bid) {
        if (!bid.auction_details) return 'bg-gray-100 text-gray-800';
        
        const isHighestBidder = bid.amount === bid.auction_details.current_price;
        const isActive = bid.auction_details.status === 'ACTIVE';
        const hasEnded = new Date(bid.auction_details.end_time) < new Date();
        
        if (isActive) {
            if (isHighestBidder) {
                return 'bg-green-100 text-green-800'; // Winning
            } else {
                return 'bg-yellow-100 text-yellow-800'; // Outbid
            }
        } else if (hasEnded) {
            if (isHighestBidder) {
                return 'bg-blue-100 text-blue-800'; // Won
            } else {
                return 'bg-red-100 text-red-800'; // Lost
            }
        }
        
        return 'bg-gray-100 text-gray-800';
    }
    
    // Get bid status text
    function getBidStatus(bid) {
        if (!bid.auction_details) return 'Unknown';
        
        const isHighestBidder = bid.amount === bid.auction_details.current_price;
        const isActive = bid.auction_details.status === 'ACTIVE';
        const hasEnded = new Date(bid.auction_details.end_time) < new Date();
        
        if (isActive) {
            if (isHighestBidder) {
                return 'Winning';
            } else {
                return 'Outbid';
            }
        } else if (hasEnded) {
            if (isHighestBidder) {
                return 'Won';
            } else {
                return 'Lost';
            }
        }
        
        return 'Unknown';
    }
</script>

<svelte:head>
    <title>My Bids | GUDIC</title>
    <meta name="description" content="View all your auction bids" />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
    <!-- Header -->
    <div class="mb-8">
        <h1 class="text-3xl font-bold text-text-dark">My Bids</h1>
        <p class="text-text-medium mt-2">Track all your bidding activity</p>
    </div>
    
    <!-- Filters -->
    <div class="bg-white rounded-lg border border-primary-blue/20 p-5 mb-6">
        <div class="flex flex-wrap gap-4">
            <div>
                <label for="status" class="block text-sm font-medium text-text-medium mb-1">
                    Filter Status
                </label>
                <select
                    id="status"
                    bind:value={filters.status}
                    on:change={handleFilterChange}
                    class="w-full rounded-md border border-primary-blue/20 px-3 py-2 text-sm"
                >
                    <option value="">All Statuses</option>
                    <option value="winning">Winning</option>
                    <option value="outbid">Outbid</option>
                    <option value="won">Won</option>
                    <option value="lost">Lost</option>
                </select>
            </div>
            
            <div>
                <label for="sort_by" class="block text-sm font-medium text-text-medium mb-1">
                    Sort By
                </label>
                <select
                    id="sort_by"
                    bind:value={filters.sort_by}
                    on:change={handleFilterChange}
                    class="w-full rounded-md border border-primary-blue/20 px-3 py-2 text-sm"
                >
                    <option value="created_at">Date</option>
                    <option value="amount">Amount</option>
                </select>
            </div>
            
            <div>
                <label for="direction" class="block text-sm font-medium text-text-medium mb-1">
                    Order
                </label>
                <select
                    id="direction"
                    bind:value={filters.direction}
                    on:change={handleFilterChange}
                    class="w-full rounded-md border border-primary-blue/20 px-3 py-2 text-sm"
                >
                    <option value="desc">Descending</option>
                    <option value="asc">Ascending</option>
                </select>
            </div>
        </div>
    </div>
    
    <!-- Content -->
    {#if loading}
        <div class="flex justify-center py-12">
            <Spinner size="lg" />
        </div>
    {:else if error}
        <Alert variant="error" class="mb-6">
            {error}
            <div class="mt-2">
                <Button variant="outline" size="sm" on:click={() => loadBids()}>
                    Try Again
                </Button>
            </div>
        </Alert>
    {:else if $bidStore.userBids.length === 0}
        <div class="bg-white rounded-lg border border-primary-blue/20 p-8 text-center">
            <div class="text-secondary-blue/50 mb-4">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
            </div>
            <h3 class="text-lg font-medium text-text-dark mb-2">No Bids Found</h3>
            <p class="text-text-medium mb-6">You haven't placed any bids yet.</p>
            <a 
                href="/auctions" 
                class="inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-blue hover:bg-primary-blue/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-blue"
            >
                Browse Auctions
            </a>
        </div>
    {:else}
        <!-- Bids Table -->
        <div class="bg-white rounded-lg border border-primary-blue/20 overflow-hidden">
            <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-primary-blue/10">
                    <thead class="bg-primary-blue/5">
                        <tr>
                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-text-medium uppercase tracking-wider">
                                Auction
                            </th>
                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-text-medium uppercase tracking-wider">
                                Bid Amount
                            </th>
                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-text-medium uppercase tracking-wider">
                                Date
                            </th>
                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-text-medium uppercase tracking-wider">
                                Status
                            </th>
                            <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-text-medium uppercase tracking-wider">
                                Actions
                            </th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-primary-blue/10">
                        {#each $bidStore.userBids as bid}
                            <tr class="hover:bg-primary-blue/5">
                                <td class="px-6 py-4 whitespace-nowrap">
                                    <a 
                                        href="/auctions/{bid.auction}" 
                                        class="text-sm font-medium text-secondary-blue hover:underline"
                                    >
                                        {bid.auction_details?.title || `Auction #${bid.auction}`}
                                    </a>
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap">
                                    <span class="text-sm font-medium text-text-dark">
                                        {formatCurrency(bid.amount, bid.auction_details?.currency || 'USD')}
                                    </span>
                                    {#if bid.auto_bid_limit}
                                        <div class="text-xs text-text-medium">
                                            Auto up to {formatCurrency(bid.auto_bid_limit, bid.auction_details?.currency || 'USD')}
                                        </div>
                                    {/if}
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm text-text-medium">
                                    {formatDate(bid.created_at)}
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap">
                                    <span class="px-2 py-1 inline-flex text-xs leading-5 font-medium rounded-full {getBidStatusClass(bid)}">
                                        {getBidStatus(bid)}
                                    </span>
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                    <a 
                                        href="/auctions/{bid.auction}" 
                                        class="inline-flex items-center px-2.5 py-1.5 border border-gray-300 text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-blue"
                                    >
                                        View Auction
                                    </a>
                                    
                                    {#if getBidStatus(bid) === 'Outbid' && bid.auction_details?.status === 'ACTIVE'}
                                        <a 
                                            href={`/auctions/${bid.auction}/bid`} 
                                            class="ml-2 inline-flex items-center px-2.5 py-1.5 border border-transparent text-xs font-medium rounded shadow-sm text-white bg-primary-blue hover:bg-primary-blue/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-blue"
                                        >
                                            Bid Again
                                        </a>
                                    {/if}
                                </td>
                            </tr>
                        {/each}
                    </tbody>
                </table>
            </div>
        </div>
        
        <!-- Pagination -->
        {#if pagination.total_pages > 1}
            <div class="flex justify-center mt-8">
                <nav class="inline-flex rounded-md shadow">
                    <button
                        class="relative inline-flex items-center px-3 py-2 rounded-l-md border border-primary-blue/20 bg-white text-sm font-medium {pagination.previous ? 'text-text-dark hover:bg-primary-blue/5' : 'text-text-light cursor-not-allowed'}"
                        disabled={!pagination.previous}
                        on:click={() => goToPage(pagination.previous)}
                        aria-label="Previous page"
                    >
                        <span class="sr-only">Previous</span>
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" />
                        </svg>
                    </button>
                    
                    <span class="relative inline-flex items-center px-4 py-2 border-t border-b border-primary-blue/20 bg-white text-sm font-medium text-text-dark">
                        Page {pagination.page} of {pagination.total_pages}
                    </span>
                    
                    <button
                        class="relative inline-flex items-center px-3 py-2 rounded-r-md border border-primary-blue/20 bg-white text-sm font-medium {pagination.next ? 'text-text-dark hover:bg-primary-blue/5' : 'text-text-light cursor-not-allowed'}"
                        disabled={!pagination.next}
                        on:click={() => goToPage(pagination.next)}
                        aria-label="Next page"
                    >
                        <span class="sr-only">Next</span>
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
                        </svg>
                    </button>
                </nav>
            </div>
        {/if}
    {/if}
</div>