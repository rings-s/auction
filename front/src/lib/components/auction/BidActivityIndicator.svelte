<!-- src/lib/components/auction/BidActivityIndicator.svelte -->
<script>
	import { onMount, onDestroy } from 'svelte';
	import { getAuctionStatus } from '$lib/api/auction';

	export let auctionId;
	export let initialBidCount = 0;
	export let size = 'default'; // 'small', 'default', 'large'

	let bidCount = initialBidCount;
	let previousCount = initialBidCount;
	let newBidAnimation = false;
	let interval;

	async function checkForNewBids() {
		try {
			const status = await getAuctionStatus(auctionId);

			if (status.bid_count > bidCount) {
				previousCount = bidCount;
				bidCount = status.bid_count;
				newBidAnimation = true;

				setTimeout(() => {
					newBidAnimation = false;
				}, 3000);
			}
		} catch (error) {
			console.error('Failed to check bid status:', error);
		}
	}

	onMount(() => {
		interval = setInterval(checkForNewBids, 10000); // Check every 10 seconds
	});

	onDestroy(() => {
		if (interval) clearInterval(interval);
	});

	$: sizeClasses = {
		small: 'text-xs px-2 py-0.5',
		default: 'text-sm px-3 py-1',
		large: 'text-base px-4 py-2'
	}[size];
</script>

<div
	class="inline-flex items-center {sizeClasses} rounded-full {newBidAnimation
		? 'animate-pulse bg-green-500 text-white'
		: 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300'}"
>
	<svg class="mr-1.5 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
		<path
			stroke-linecap="round"
			stroke-linejoin="round"
			stroke-width="2"
			d="M17 8h2a2 2 0 012 2v6a2 2 0 01-2 2h-2v4l-4-4H9a1.994 1.994 0 01-1.414-.586m0 0L11 14h4a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2v4l.586-.586z"
		/>
	</svg>
	<span class="font-medium">
		{bidCount}
		{bidCount === 1 ? 'bid' : 'bids'}
	</span>
	{#if newBidAnimation}
		<span class="ml-1.5 text-xs">+{bidCount - previousCount}</span>
	{/if}
</div>
