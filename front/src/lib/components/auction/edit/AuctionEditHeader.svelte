<!-- src/lib/components/auction/edit/AuctionEditHeader.svelte -->
<script>
	import { t } from '$lib/i18n';
	import AuctionStatus from '$lib/components/auction/AuctionStatus.svelte';

	const { auction, saving = false } = $props();
</script>

<div class="rounded-lg bg-white p-6 shadow-sm dark:bg-gray-800">
	<div class="md:flex md:items-start md:justify-between">
		<div class="min-w-0 flex-1">
			<div class="mb-2 flex items-center space-x-3">
				<h1 class="text-2xl font-bold text-gray-900 dark:text-white">
					{$t('auction.editAuction')}
				</h1>
				{#if auction}
					<AuctionStatus status={auction.status} />
				{/if}
			</div>

			{#if auction}
				<h2 class="text-primary-600 dark:text-primary-400 mb-2 text-lg font-medium">
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
				<div class="min-w-0 rounded-lg bg-neutral-50 p-4 md:min-w-[200px] dark:bg-neutral-800">
					<h3 class="mb-3 text-sm font-medium text-neutral-700 dark:text-neutral-300">
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
							<dd class="text-success-600 dark:text-success-400 font-medium">
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
