<script>
	import { t } from '$lib/i18n';
	import Button from '$lib/components/ui/Button.svelte';
	import CountdownTimer from '$lib/components/auction/CountdownTimer.svelte';
	import AuctionStatus from '$lib/components/auction/AuctionStatus.svelte';

	export let auction;
	export let property;
	export let bids;
	export let canBid;
	export let canRegister;
	export let isOwner;
	export let isLiveAuction;
	// Removed unused export: export let isScheduledAuction;
	export let isActiveAuction;
	export let isRegistered;
	export let placingBid;
	export let minimumBidAmount;
	export let user;
	export let onTimerEnd;
	export let onOpenBidModal;
	export let onShowRegisterModal;
	export let onShowExtendModal;

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

	function formatCurrency(amount) {
		return new Intl.NumberFormat('en-US', {
			style: 'currency',
			currency: 'USD',
			minimumFractionDigits: 0,
			maximumFractionDigits: 0
		}).format(amount);
	}

	function getTimeAgo(dateString) {
		const now = new Date();
		const past = new Date(dateString);
		const diffInSeconds = Math.floor((now - past) / 1000);

		if (diffInSeconds < 60) return 'Just now';
		if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
		if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
		return `${Math.floor(diffInSeconds / 86400)}d ago`;
	}
</script>

<!-- Auction Status Card -->
<div class="rounded-lg bg-white p-4 shadow-sm dark:bg-neutral-800">
	{#if isLiveAuction}
		<!-- Live Auction Timer -->
		<div class="mb-4">
			<h3 class="mb-3 flex items-center text-base font-semibold text-neutral-900 dark:text-white">
				<span class="bg-danger-500 mr-2 h-2 w-2 animate-pulse rounded-full"></span>
				{$t('auction.timeRemaining')}
			</h3>
			<CountdownTimer endDate={auction.end_date} onEnd={onTimerEnd} />
		</div>
	{:else if auction.status === 'scheduled'}
		<!-- Scheduled Auction Timer -->
		<div class="mb-4">
			<h3 class="mb-3 flex items-center text-base font-semibold text-neutral-900 dark:text-white">
				<span class="bg-warning-500 mr-2 h-2 w-2 animate-pulse rounded-full"></span>
				{$t('auction.startsIn')}
			</h3>
			<CountdownTimer endDate={auction.start_date} onEnd={onTimerEnd} variant="secondary" />
			<p class="mt-2 text-sm text-neutral-600 dark:text-neutral-400">
				{formatDateTime(auction.start_date)}
			</p>
		</div>
	{:else if auction.status === 'ended' || auction.status === 'completed'}
		<!-- Ended Auction -->
		<div class="mb-4">
			<h3 class="mb-2 text-base font-semibold text-neutral-900 dark:text-white">
				{$t('auction.auctionEnded')}
			</h3>
			<p class="text-sm text-neutral-600 dark:text-neutral-400">
				{formatDateTime(auction.end_date)}
			</p>
			{#if auction.status === 'completed' && bids.length > 0}
				<div
					class="bg-success-50 dark:bg-success-900/20 border-success-200 dark:border-success-800 mt-3 rounded-lg border p-3"
				>
					<h4
						class="text-success-800 dark:text-success-200 mb-1 flex items-center text-sm font-semibold"
					>
						🎉 Auction Winner
					</h4>
					<p class="text-success-700 dark:text-success-300 text-sm">
						{bids[0]?.bidder_info?.name || 'Anonymous'} won with {formatCurrency(
							bids[0]?.amount || 0
						)}
					</p>
				</div>
			{/if}
		</div>
	{/if}

	<!-- Current Bid Display -->
	<div class="mb-4 border-t border-neutral-200 pt-4 dark:border-neutral-700">
		<div class="text-center">
			<div class="mb-1 text-sm font-medium text-neutral-500 dark:text-neutral-400">
				{$t('auction.currentBid')}
			</div>
			<div class="text-primary-600 dark:text-primary-400 mb-1 text-2xl font-bold">
				{formatCurrency(auction.current_bid || auction.starting_bid)}
			</div>
			<div class="text-sm text-neutral-500 dark:text-neutral-400">
				{$t('auction.totalBids')}: {auction.bid_count || bids.length}
			</div>
		</div>
	</div>

	<!-- Main Action Button -->
	<div class="space-y-3">
		{#if canBid}
			<Button
				variant="primary"
				class="w-full font-semibold"
				on:click={onOpenBidModal}
				disabled={placingBid}
			>
				{#if placingBid}
					<svg
						class="mr-2 -ml-1 h-4 w-4 animate-spin text-white"
						xmlns="http://www.w3.org/2000/svg"
						fill="none"
						viewBox="0 0 24 24"
					>
						<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"
						></circle>
						<path
							class="opacity-75"
							fill="currentColor"
							d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
						></path>
					</svg>
				{:else}
					<svg class="mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M13 10V3L4 14h7v7l9-11h-7z"
						/>
					</svg>
				{/if}
				{$t('auction.placeBid')}
			</Button>
			<p class="text-center text-xs text-neutral-500 dark:text-neutral-400">
				{$t('auction.minimumBid')}: {formatCurrency(minimumBidAmount)}
			</p>
		{:else if canRegister}
			<Button variant="secondary" class="w-full font-semibold" on:click={onShowRegisterModal}>
				<svg class="mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"
					/>
				</svg>
				{$t('auction.registerForAuction')}
			</Button>
		{:else if auction.status === 'scheduled'}
			{#if isRegistered}
				<div
					class="bg-success-50 dark:bg-success-900/20 border-success-200 dark:border-success-800 rounded-lg border p-3"
				>
					<div class="flex items-center">
						<svg
							class="text-success-500 h-4 w-4 flex-shrink-0"
							fill="currentColor"
							viewBox="0 0 20 20"
						>
							<path
								fill-rule="evenodd"
								d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
								clip-rule="evenodd"
							/>
						</svg>
						<div class="ml-2">
							<p class="text-success-800 dark:text-success-200 text-sm font-semibold">
								✅ Registered
							</p>
							<p class="text-success-600 dark:text-success-400 text-xs">
								Ready to bid when auction starts
							</p>
						</div>
					</div>
				</div>
			{:else if user}
				<Button variant="secondary" class="w-full font-semibold" on:click={onShowRegisterModal}>
					<svg class="mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"
						/>
					</svg>
					{$t('auction.registerForAuction')}
				</Button>
			{:else}
				<Button
					variant="secondary"
					class="w-full font-semibold"
					href="/login?redirect=/auctions/{auction.slug}"
				>
					<svg class="mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1"
						/>
					</svg>
					{$t('auction.loginToRegister')}
				</Button>
			{/if}
		{:else if !user}
			<Button
				variant="primary"
				class="w-full font-semibold"
				href="/login?redirect=/auctions/{auction.slug}"
			>
				<svg class="mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1"
					/>
				</svg>
				{$t('auction.loginToPlaceBid')}
			</Button>
		{:else}
			<Button variant="outline" class="w-full font-semibold" href="/auctions">
				<svg class="mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M10 19l-7-7m0 0l7-7m-7 7h18"
					/>
				</svg>
				{$t('auctions.backToAuctions')}
			</Button>
		{/if}
	</div>

	<!-- Owner Controls -->
	{#if isOwner && isActiveAuction}
		<div class="mt-4 border-t border-neutral-200 pt-4 dark:border-neutral-700">
			<h3 class="mb-2 text-base font-semibold text-neutral-900 dark:text-white">Owner Controls</h3>
			<div class="space-y-2">
				<Button variant="outline" size="small" class="w-full" on:click={onShowExtendModal}>
					<svg class="mr-1.5 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
						/>
					</svg>
					Extend Auction
				</Button>
			</div>
		</div>
	{/if}
</div>

<!-- Property Quick Info Card -->
{#if property}
	<div class="overflow-hidden rounded-lg bg-white shadow-sm dark:bg-neutral-800">
		<div class="p-4">
			<div class="mb-3 flex items-center justify-between">
				<h3 class="text-base font-semibold text-neutral-900 dark:text-white">
					{$t('auction.propertyInfo')}
				</h3>
				<a
					href={`/properties/${property.slug}`}
					target="_blank"
					class="text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 text-sm font-medium transition-colors"
				>
					{$t('property.viewDetails')}
				</a>
			</div>

			<!-- Property Image -->
			<div class="mb-3 aspect-video overflow-hidden rounded-lg bg-neutral-200 dark:bg-neutral-700">
				{#if property.main_image?.url}
					<img
						src={property.main_image.url}
						alt={property.title}
						class="h-full w-full object-cover"
					/>
				{:else}
					<div class="flex h-full items-center justify-center">
						<svg
							class="h-8 w-8 text-neutral-400 dark:text-neutral-500"
							fill="none"
							viewBox="0 0 24 24"
							stroke="currentColor"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
							/>
						</svg>
					</div>
				{/if}
			</div>

			<h4 class="mb-3 text-sm font-semibold text-neutral-900 dark:text-white">
				{property.title}
			</h4>

			<!-- Property Details -->
			<dl class="space-y-2 text-sm">
				<div class="flex items-center justify-between">
					<dt class="font-medium text-neutral-500 dark:text-neutral-400">
						{$t('property.location')}
					</dt>
					<dd class="text-right font-semibold text-neutral-900 dark:text-white">
						{property.location?.city}, {property.location?.state}
					</dd>
				</div>
				<div class="flex items-center justify-between">
					<dt class="font-medium text-neutral-500 dark:text-neutral-400">
						{$t('property.propertyType')}
					</dt>
					<dd class="font-semibold text-neutral-900 dark:text-white">
						{property.property_type_display}
					</dd>
				</div>
				<div class="flex items-center justify-between">
					<dt class="font-medium text-neutral-500 dark:text-neutral-400">{$t('property.size')}</dt>
					<dd class="font-semibold text-neutral-900 dark:text-white">
						{property.size_sqm}
						{$t('property.sqm')}
					</dd>
				</div>
				<div class="flex items-center justify-between">
					<dt class="font-medium text-neutral-500 dark:text-neutral-400">
						{$t('property.marketValue')}
					</dt>
					<dd class="text-success-600 dark:text-success-400 font-semibold">
						{formatCurrency(property.market_value)}
					</dd>
				</div>
			</dl>
		</div>
	</div>
{/if}

<!-- Recent Activity Card -->
{#if bids.length > 0}
	<div class="rounded-lg bg-white p-4 shadow-sm dark:bg-neutral-800">
		<div class="mb-3 flex items-center justify-between">
			<h3 class="text-base font-semibold text-neutral-900 dark:text-white">
				{$t('auction.recentActivity')}
			</h3>
			<span class="text-sm text-neutral-500 dark:text-neutral-400"> Latest 3 </span>
		</div>

		<div class="space-y-2">
			{#each bids.slice(0, 3) as bid}
				<div
					class="flex items-center justify-between rounded-lg bg-neutral-50 p-2 dark:bg-neutral-700"
				>
					<div class="min-w-0 flex-1">
						<p class="text-sm font-semibold text-neutral-900 dark:text-white">
							{formatCurrency(bid.amount)}
						</p>
						<p class="truncate text-xs text-neutral-500 dark:text-neutral-400">
							{bid.bidder_info?.name || 'Anonymous'}
							{#if bid.bidder_info?.id === user?.id}
								<span class="text-primary-600 dark:text-primary-400 font-medium"
									>({$t('auction.you')})</span
								>
							{/if}
						</p>
					</div>
					<div class="ml-2 flex-shrink-0 text-right">
						<p class="text-xs text-neutral-500 dark:text-neutral-400">
							{getTimeAgo(bid.bid_time)}
						</p>
						<AuctionStatus status={bid.status} isCompact={true} />
					</div>
				</div>
			{/each}

			<Button
				variant="outline"
				size="small"
				on:click={() => (activeTab = 'bids')}
				class="mt-2 w-full"
			>
				{$t('auction.viewAllBids')} ({bids.length})
			</Button>
		</div>
	</div>
{/if}

<!-- Help Card -->
<div class="rounded-lg bg-white p-4 shadow-sm dark:bg-neutral-800">
	<h3 class="mb-2 text-base font-semibold text-neutral-900 dark:text-white">
		{$t('auction.needHelp')}
	</h3>
	<p class="mb-3 text-sm text-neutral-600 dark:text-neutral-400">
		Questions about this auction? Contact support.
	</p>
	<Button
		variant="outline"
		size="small"
		class="w-full"
		href="/contact?subject=Auction%20{auction.id}"
	>
		<svg class="mr-1.5 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
			<path
				stroke-linecap="round"
				stroke-linejoin="round"
				stroke-width="2"
				d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
			/>
		</svg>
		{$t('auction.contactSupport')}
	</Button>
</div>
