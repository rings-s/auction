<!-- src/lib/components/auction/AuctionCard.svelte -->
<script>
	import { t } from '$lib/i18n';
	import { onMount, onDestroy } from 'svelte';
	import { getAuctionStatus } from '$lib/api/auction';

	let { auction } = $props();

	let timeRemaining = $state({ days: 0, hours: 0, minutes: 0, seconds: 0 });
	let interval;
	let statusInfo = null;
	let loading = false;
	let recentBidAnimation = $state(false);

	// Enhanced auction state using $derived
	let isLive = $derived(auction?.status === 'live');
	let isScheduled = $derived(auction?.status === 'scheduled');
	let isEnded = $derived(auction?.status === 'ended' || auction?.status === 'completed');
	let isActive = $derived(isLive || isScheduled);
	let hasActiveBidding = $derived(isLive && auction.bid_count > 0);

	// Calculate bid activity level
	let bidActivityLevel = $derived(getBidActivityLevel());

	function getBidActivityLevel() {
		if (!auction?.bid_count) return 'low';
		if (auction.bid_count > 20) return 'hot';
		if (auction.bid_count > 10) return 'active';
		return 'moderate';
	}

	function updateTimeRemaining() {
		if (!auction?.end_date) {
			timeRemaining = { days: 0, hours: 0, minutes: 0, seconds: 0 };
			return;
		}

		const endDate = new Date(auction.end_date);
		const startDate = new Date(auction.start_date);
		const now = new Date();

		const targetDate = isScheduled ? startDate : endDate;
		const diff = targetDate - now;

		if (diff <= 0) {
			timeRemaining = { days: 0, hours: 0, minutes: 0, seconds: 0 };
			if (isScheduled && now >= startDate) {
				refreshAuctionStatus();
			}
			clearInterval(interval);
			return;
		}

		const days = Math.floor(diff / (1000 * 60 * 60 * 24));
		const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
		const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
		const seconds = Math.floor((diff % (1000 * 60)) / 1000);

		timeRemaining = { days, hours, minutes, seconds };
	}

	async function refreshAuctionStatus() {
		if (!auction?.id || loading) return;

		try {
			loading = true;
			const newStatusInfo = await getAuctionStatus(auction.id);

			// Check if bid count increased
			if (newStatusInfo.bid_count > auction.bid_count) {
				recentBidAnimation = true;
				setTimeout(() => (recentBidAnimation = false), 3000);
			}

			auction = {
				...auction,
				status: newStatusInfo.status,
				current_bid: newStatusInfo.current_bid,
				bid_count: newStatusInfo.bid_count || auction.bid_count,
				is_biddable: newStatusInfo.is_biddable,
				is_active: newStatusInfo.is_active,
				time_remaining: newStatusInfo.time_remaining
			};

			statusInfo = newStatusInfo;
			updateTimeRemaining();
		} catch (error) {
			console.error('Failed to refresh auction status:', error);
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		updateTimeRemaining();
		interval = setInterval(() => {
			updateTimeRemaining();

			// Check if we need to refresh status (e.g., scheduled -> live)
			const now = new Date();
			const startDate = new Date(auction.start_date);
			const endDate = new Date(auction.end_date);

			if (isScheduled && now >= startDate) {
				refreshAuctionStatus();
			} else if (isLive && now >= endDate) {
				refreshAuctionStatus();
			}
		}, 1000);

		// Status check interval
		let statusInterval;
		if (isActive) {
			statusInterval = setInterval(refreshAuctionStatus, 15000); // Check every 15 seconds
		}

		return () => {
			clearInterval(interval);
			if (statusInterval) clearInterval(statusInterval);
		};
	});

	onDestroy(() => {
		if (interval) clearInterval(interval);
	});

	function getPropertyImageUrl(property) {
		if (!property) return '/images/auction-placeholder.jpg';

		if (property.main_image) {
			if (typeof property.main_image === 'string') {
				return property.main_image;
			}
			if (property.main_image.url) {
				return property.main_image.url;
			}
			if (property.main_image.file) {
				return property.main_image.file;
			}
		}

		if (property.media && property.media.length > 0) {
			const firstImage = property.media.find(
				(m) => m.media_type === 'image' || (m.url && typeof m.url === 'string')
			);

			if (firstImage) {
				return firstImage.url || firstImage.file || '/images/auction-placeholder.jpg';
			}
		}

		return '/images/auction-placeholder.jpg';
	}

	function getAuctionImage() {
		if (auction.media && auction.media.length > 0) {
			const auctionImage = auction.media.find(
				(m) => m.media_type === 'image' || (m.url && typeof m.url === 'string')
			);

			if (auctionImage) {
				return auctionImage.url || auctionImage.file;
			}
		}

		if (auction.related_property) {
			return getPropertyImageUrl(auction.related_property);
		}

		return '/images/auction-placeholder.jpg';
	}

	// Enhanced gradient status badge system
	function getStatusBadgeClass(status) {
		const baseClasses =
			'inline-flex items-center px-3 py-1.5 rounded-xl text-xs font-bold uppercase tracking-wider backdrop-blur-sm transform transition-all duration-300 hover:scale-105 shadow-lg';

		switch (status) {
			case 'live':
				return `${baseClasses} bg-gradient-to-r from-green-500 via-emerald-500 to-teal-600 text-white shadow-green-500/30 animate-pulse-soft`;
			case 'scheduled':
				return `${baseClasses} bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-600 text-white shadow-blue-500/30`;
			case 'ended':
				return `${baseClasses} bg-gradient-to-r from-red-500 via-pink-500 to-rose-600 text-white shadow-red-500/30`;
			case 'completed':
				return `${baseClasses} bg-gradient-to-r from-purple-500 via-violet-500 to-indigo-600 text-white shadow-purple-500/30`;
			case 'cancelled':
				return `${baseClasses} bg-gradient-to-r from-gray-500 via-slate-500 to-gray-600 text-white shadow-gray-500/30`;
			default:
				return `${baseClasses} bg-gradient-to-r from-gray-400 via-slate-400 to-gray-500 text-white shadow-gray-500/30`;
		}
	}

	// Get bid activity gradient class
	function getBidActivityClass() {
		switch (bidActivityLevel) {
			case 'hot':
				return 'bg-gradient-to-r from-red-500 via-orange-500 to-yellow-500 animate-pulse-fast';
			case 'active':
				return 'bg-gradient-to-r from-orange-500 via-amber-500 to-yellow-500 animate-pulse-soft';
			case 'moderate':
				return 'bg-gradient-to-r from-yellow-500 via-amber-500 to-orange-500';
			default:
				return 'bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-500';
		}
	}

	function getStatusText(status) {
		switch (status) {
			case 'live':
				return $t('auction.statusLive');
			case 'scheduled':
				return $t('auction.statusScheduled');
			case 'ended':
				return $t('auction.statusEnded');
			case 'completed':
				return $t('auction.statusCompleted');
			case 'cancelled':
				return $t('auction.statusCancelled');
			default:
				return $t('auction.statusDraft');
		}
	}

	function formatCurrency(amount) {
		if (!amount) return '$0';
		return new Intl.NumberFormat('en-US', {
			style: 'currency',
			currency: 'USD',
			minimumFractionDigits: 0,
			maximumFractionDigits: 0
		}).format(amount);
	}

	function getTimeRemainingDisplay() {
		if (timeRemaining.days > 0) {
			return `${timeRemaining.days}d ${timeRemaining.hours}h`;
		} else if (timeRemaining.hours > 0) {
			return `${timeRemaining.hours}h ${timeRemaining.minutes}m`;
		} else if (timeRemaining.minutes > 0) {
			return `${timeRemaining.minutes}m ${timeRemaining.seconds}s`;
		} else {
			return `${timeRemaining.seconds}s`;
		}
	}
</script>

<a
	href={`/auctions/${auction.slug}`}
	class="group block h-full transform transition-all duration-500 hover:-translate-y-2 hover:scale-[1.03] hover:shadow-2xl hover:shadow-blue-500/10"
>
	<div
		class="relative flex h-full flex-col overflow-hidden rounded-2xl border border-neutral-200/50 bg-white shadow-lg backdrop-blur-sm transition-all duration-500 hover:border-blue-300 hover:shadow-2xl dark:border-neutral-700/50 dark:bg-gray-800 dark:hover:border-blue-500 {hasActiveBidding
			? 'animate-pulse-soft ring-4 shadow-green-500/20 ring-green-500/50'
			: ''}"
	>
		<!-- Enhanced gradient overlay for visual appeal -->
		<div
			class="pointer-events-none absolute inset-0 rounded-2xl bg-gradient-to-br from-blue-50/30 via-transparent to-purple-50/30 opacity-0 transition-opacity duration-500 group-hover:opacity-100"
		></div>
		<!-- Image Section with Enhanced Overlays -->
		<div class="relative h-56 overflow-hidden">
			<img
				src={getAuctionImage()}
				alt={auction.title}
				class="h-full w-full object-cover transition-transform duration-500 group-hover:scale-110"
				loading="lazy"
			/>

			<!-- Gradient Overlay -->
			<div
				class="absolute inset-0 bg-gradient-to-t from-black/70 via-black/20 to-transparent"
			></div>

			<!-- Top Badges Row -->
			<div class="absolute top-3 right-3 left-3 flex items-start justify-between">
				<div class="flex flex-wrap gap-2">
					<!-- Status Badge -->
					<span class={getStatusBadgeClass(auction.status)}>
						{#if isLive}
							<span class="bg-success-500 mr-1.5 h-2 w-2 animate-pulse rounded-full"></span>
						{/if}
						{getStatusText(auction.status)}
					</span>

					<!-- Enhanced Featured Badge with sparkle animation -->
					{#if auction.is_featured}
						<span
							class="inline-flex transform animate-pulse items-center rounded-xl bg-gradient-to-r from-amber-400 to-yellow-500 px-3 py-1.5 text-xs font-bold text-white shadow-lg shadow-amber-500/30 backdrop-blur-sm transition-all duration-300 hover:scale-105"
						>
							<svg class="mr-1 h-3 w-3 animate-spin" fill="currentColor" viewBox="0 0 20 20">
								<path
									d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"
								/>
							</svg>
							⭐ {$t('auction.featured')}
						</span>
					{/if}
				</div>

				<!-- Enhanced Bid Activity Indicator -->
				{#if isLive && hasActiveBidding}
					<div class="flex items-center space-x-2">
						{#if bidActivityLevel === 'hot'}
							<span
								class="flex transform items-center rounded-xl px-3 py-1.5 text-xs font-bold text-white shadow-lg transition-all duration-300 hover:scale-105 {getBidActivityClass()}"
							>
								<svg class="mr-1 h-3 w-3 animate-spin" fill="currentColor" viewBox="0 0 20 20">
									<path
										d="M10 2L13.09 8.26L20 9L15 14L16.18 21L10 17.27L3.82 21L5 14L0 9L6.91 8.26L10 2Z"
									/>
								</svg>
								🔥 HOT AUCTION
							</span>
						{:else if recentBidAnimation}
							<span
								class="animate-bounce rounded-xl bg-gradient-to-r from-green-500 to-emerald-600 px-3 py-1.5 text-xs font-bold text-white shadow-lg shadow-green-500/30"
							>
								⚡ NEW BID!
							</span>
						{:else if bidActivityLevel === 'active'}
							<span
								class="animate-pulse-soft flex items-center rounded-xl bg-gradient-to-r from-orange-500 to-amber-600 px-3 py-1.5 text-xs font-bold text-white shadow-lg shadow-orange-500/30"
							>
								📈 ACTIVE
							</span>
						{/if}
					</div>
				{/if}
			</div>

			<!-- Title and Location Overlay -->
			<div class="absolute right-0 bottom-0 left-0 p-4">
				<h3
					class="group-hover:text-primary-300 mb-1 line-clamp-2 text-xl font-bold text-white transition-colors"
				>
					{auction.title}
				</h3>
				<p class="truncate text-sm text-gray-200">
					{#if auction.related_property?.location}
						📍 {auction.related_property.location.city || ''}{auction.related_property.location
							.state
							? `, ${auction.related_property.location.state}`
							: ''}
					{/if}
				</p>
			</div>
		</div>

		<!-- Content Section - Focused on Bidding Info -->
		<div class="flex flex-grow flex-col p-5">
			<!-- Auction Type and Quick Stats -->
			<div class="mb-4 flex items-center justify-between">
				<span
					class="inline-block rounded-full bg-neutral-100 px-3 py-1 text-sm font-medium text-neutral-700 dark:bg-neutral-700 dark:text-neutral-300"
				>
					{auction.auction_type === 'sealed'
						? '🔒 ' + $t('auction.typeSealed')
						: auction.auction_type === 'private'
							? '🏷️ ' + $t('auction.typeReserve')
							: '🎯 ' + $t('auction.typeNoReserve')}
				</span>

				<div class="flex items-center space-x-3 text-sm text-neutral-500 dark:text-neutral-400">
					<div class="flex items-center">
						<svg class="mr-1 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M17 8h2a2 2 0 012 2v6a2 2 0 01-2 2h-2v4l-4-4H9a1.994 1.994 0 01-1.414-.586m0 0L11 14h4a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2v4l.586-.586z"
							/>
						</svg>
						<span class="font-medium">{auction.bid_count || 0}</span>
					</div>
					<div class="flex items-center">
						<svg class="mr-1 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
							/>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
							/>
						</svg>
						<span>{auction.view_count || 0}</span>
					</div>
				</div>
			</div>

			<!-- Current Bid Section - Enhanced -->
			<div
				class="from-primary-50 to-secondary-50 dark:from-primary-900/20 dark:to-secondary-900/20 border-primary-200 dark:border-primary-800 mb-4 rounded-lg border bg-gradient-to-r p-4"
			>
				<div class="mb-2 flex items-baseline justify-between">
					<p class="text-sm font-medium text-neutral-600 dark:text-neutral-400">
						{auction.current_bid ? $t('auction.currentBid') : $t('auction.startingBid')}
					</p>
					{#if isLive}
						<span class="text-success-600 dark:text-success-400 animate-pulse text-xs font-medium">
							• {$t('auction.acceptingBids')}
						</span>
					{/if}
				</div>

				<div class="flex items-end justify-between">
					<div>
						<p
							class="group-hover:text-primary-600 dark:group-hover:text-primary-400 text-3xl font-bold text-gray-900 transition-colors dark:text-white"
						>
							{formatCurrency(auction.current_bid || auction.starting_bid)}
						</p>
						{#if auction.current_bid && auction.minimum_increment}
							<p class="mt-1 text-xs text-neutral-500 dark:text-neutral-400">
								Next min: {formatCurrency(
									(auction.current_bid || auction.starting_bid) + auction.minimum_increment
								)}
							</p>
						{/if}
					</div>

					{#if auction.bid_count > 0 && isLive}
						<div class="text-right">
							<p class="text-xs text-neutral-500 dark:text-neutral-400">
								{auction.bid_count}
								{auction.bid_count === 1 ? 'bid' : 'bids'}
							</p>
							{#if recentBidAnimation}
								<p class="text-success-600 dark:text-success-400 animate-pulse text-xs font-medium">
									↑ New bid!
								</p>
							{/if}
						</div>
					{/if}
				</div>
			</div>

			<!-- Time Display - Compact and Clear -->
			<!-- Update the timer section in AuctionCard.svelte to be more visible -->

			{#if isActive}
				<div
					class="from-primary-50 to-secondary-50 dark:from-primary-900/20 dark:to-secondary-900/20 border-primary-200 dark:border-primary-800 mb-4 rounded-lg border bg-gradient-to-r p-3"
				>
					<div class="mb-2 text-center">
						<span class="text-primary-700 dark:text-primary-300 text-xs font-medium">
							{isLive ? '🔴 ' + $t('auction.timeRemaining') : '📅 ' + $t('auction.startsIn')}
						</span>
					</div>

					<!-- Large Timer Display -->
					<div class="grid grid-cols-4 gap-1 text-center">
						<div class="rounded bg-white p-1 dark:bg-gray-800">
							<span class="text-primary-800 dark:text-primary-200 block text-lg font-bold">
								{timeRemaining.days}
							</span>
							<span class="text-primary-600 dark:text-primary-400 text-xs">
								{$t('auction.days')}
							</span>
						</div>
						<div class="rounded bg-white p-1 dark:bg-gray-800">
							<span class="text-primary-800 dark:text-primary-200 block text-lg font-bold">
								{String(timeRemaining.hours).padStart(2, '0')}
							</span>
							<span class="text-primary-600 dark:text-primary-400 text-xs">
								{$t('auction.hours')}
							</span>
						</div>
						<div class="rounded bg-white p-1 dark:bg-gray-800">
							<span class="text-primary-800 dark:text-primary-200 block text-lg font-bold">
								{String(timeRemaining.minutes).padStart(2, '0')}
							</span>
							<span class="text-primary-600 dark:text-primary-400 text-xs">
								{$t('auction.minutes')}
							</span>
						</div>
						<div class="rounded bg-white p-1 dark:bg-gray-800">
							<span class="text-primary-800 dark:text-primary-200 block text-lg font-bold">
								{String(timeRemaining.seconds).padStart(2, '0')}
							</span>
							<span class="text-primary-600 dark:text-primary-400 text-xs">
								{$t('auction.seconds')}
							</span>
						</div>
					</div>

					{#if isLive && timeRemaining.hours === 0 && timeRemaining.days === 0}
						<div class="mt-2 text-center">
							<span class="text-danger-600 dark:text-danger-400 animate-pulse text-xs font-bold">
								⚡ {$t('auction.endingSoon')} ⚡
							</span>
						</div>
					{/if}
				</div>
			{:else if isEnded}
				<div class="mb-4 rounded-lg bg-neutral-50 p-3 dark:bg-neutral-700">
					<p class="text-center text-sm font-medium text-neutral-600 dark:text-neutral-400">
						🏁 {$t('auction.auctionEnded')}
					</p>
					{#if auction.status === 'completed' && auction.bid_count > 0}
						<p class="text-success-600 dark:text-success-400 mt-1 text-center text-xs font-medium">
							🎉 {$t('auction.soldSuccessfully')}
						</p>
					{:else if auction.bid_count === 0}
						<p class="mt-1 text-center text-xs text-neutral-500 dark:text-neutral-400">
							{$t('auction.noBidsReceived')}
						</p>
					{/if}
				</div>
			{/if}

			<!-- Quick Property Info -->
			{#if auction.related_property}
				<div class="mt-auto border-t border-neutral-200 pt-3 dark:border-neutral-700">
					<div class="grid grid-cols-2 gap-2 text-xs">
						{#if auction.related_property.property_type_display}
							<div class="flex items-center text-neutral-600 dark:text-neutral-400">
								<svg class="mr-1 h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
									/>
								</svg>
								<span>{auction.related_property.property_type_display}</span>
							</div>
						{/if}
						{#if auction.related_property.size_sqm}
							<div class="flex items-center text-neutral-600 dark:text-neutral-400">
								<svg class="mr-1 h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"
									/>
								</svg>
								<span>{auction.related_property.size_sqm} sqm</span>
							</div>
						{/if}
					</div>
				</div>
			{/if}
		</div>

		<!-- Action Footer -->
		<div
			class="border-t border-neutral-200 bg-neutral-50 px-5 py-3 dark:border-neutral-700 dark:bg-neutral-900/50"
		>
			<div class="flex items-center justify-between">
				<div class="flex items-center text-sm font-medium">
					{#if isLive}
						<span class="text-primary-600 dark:text-primary-400 flex items-center font-bold">
							<svg class="mr-1.5 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M13 10V3L4 14h7v7l9-11h-7z"
								/>
							</svg>
							{$t('auction.bidNow')}
						</span>
					{:else if isScheduled}
						<span class="flex items-center text-neutral-600 dark:text-neutral-400">
							<svg class="mr-1.5 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
								/>
							</svg>
							{$t('auction.register')}
						</span>
					{:else}
						<span class="flex items-center text-neutral-600 dark:text-neutral-400">
							{$t('auction.viewDetails')}
						</span>
					{/if}
				</div>

				<svg
					class="h-5 w-5 transform text-neutral-400 transition-transform group-hover:translate-x-1 dark:text-neutral-500"
					fill="none"
					viewBox="0 0 24 24"
					stroke="currentColor"
				>
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
				</svg>
			</div>
		</div>
	</div>
</a>

<style>
	.line-clamp-2 {
		display: -webkit-box;
		-webkit-line-clamp: 2;
		-webkit-box-orient: vertical;
		overflow: hidden;
	}

	/* Enhanced gradient animations for auction cards */
	@keyframes pulse-soft {
		0%,
		100% {
			opacity: 1;
			transform: scale(1);
		}
		50% {
			opacity: 0.8;
			transform: scale(1.02);
		}
	}

	@keyframes pulse-fast {
		0%,
		100% {
			opacity: 1;
			transform: scale(1);
		}
		25% {
			opacity: 0.7;
			transform: scale(1.05);
		}
		75% {
			opacity: 0.9;
			transform: scale(0.98);
		}
	}

	@keyframes pulse-urgent {
		0%,
		100% {
			opacity: 1;
			transform: scale(1);
			box-shadow: 0 0 10px rgba(239, 68, 68, 0.5);
		}
		50% {
			opacity: 0.6;
			transform: scale(1.08);
			box-shadow: 0 0 25px rgba(239, 68, 68, 0.8);
		}
	}

	@keyframes pulse-border {
		0%,
		100% {
			border-color: rgba(34, 197, 94, 0.5);
			box-shadow: 0 0 10px rgba(34, 197, 94, 0.3);
		}
		50% {
			border-color: rgba(34, 197, 94, 0.8);
			box-shadow: 0 0 20px rgba(34, 197, 94, 0.6);
		}
	}

	@keyframes gradient-shift {
		0%,
		100% {
			background-position: 0% 50%;
		}
		50% {
			background-position: 100% 50%;
		}
	}

	@keyframes sparkle {
		0%,
		100% {
			transform: rotate(0deg) scale(1);
			filter: brightness(1);
		}
		25% {
			transform: rotate(90deg) scale(1.1);
			filter: brightness(1.3);
		}
		50% {
			transform: rotate(180deg) scale(1.2);
			filter: brightness(1.5);
		}
		75% {
			transform: rotate(270deg) scale(1.1);
			filter: brightness(1.3);
		}
	}

	.animate-pulse-soft {
		animation: pulse-soft 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
	}

	.animate-pulse-fast {
		animation: pulse-fast 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite;
	}

	.animate-pulse-urgent {
		animation: pulse-urgent 1s cubic-bezier(0.4, 0, 0.6, 1) infinite;
	}

	.animate-pulse-border {
		animation: pulse-border 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
	}

	/* Gradient background animations */
	.bg-gradient-animated {
		background-size: 200% 200%;
		animation: gradient-shift 3s ease infinite;
	}

	/* Enhanced hover effects */
	.group:hover .auction-card-content {
		transform: translateY(-2px);
	}

	.group:hover .auction-image {
		filter: brightness(1.1) contrast(1.05);
	}

	/* Live auction pulsing effect */
	.live-auction-glow {
		box-shadow:
			0 0 20px rgba(34, 197, 94, 0.3),
			inset 0 0 20px rgba(34, 197, 94, 0.1);
	}

	/* Bid activity intensity effects */
	.bid-hot {
		box-shadow:
			0 0 30px rgba(239, 68, 68, 0.4),
			inset 0 0 30px rgba(239, 68, 68, 0.1);
	}

	.bid-active {
		box-shadow:
			0 0 20px rgba(245, 158, 11, 0.4),
			inset 0 0 20px rgba(245, 158, 11, 0.1);
	}

	/* Timer urgency effects */
	.timer-urgent {
		animation: pulse-urgent 0.8s cubic-bezier(0.4, 0, 0.6, 1) infinite;
		border: 2px solid rgba(239, 68, 68, 0.6);
	}

	/* Enhanced focus states for accessibility */
	.auction-card:focus-within {
		outline: none;
		box-shadow:
			0 0 0 3px rgba(59, 130, 246, 0.5),
			0 0 0 6px rgba(59, 130, 246, 0.2);
		border-radius: 1rem;
	}

	/* Dark mode specific enhancements */
	@media (prefers-color-scheme: dark) {
		.live-auction-glow {
			box-shadow:
				0 0 25px rgba(34, 197, 94, 0.4),
				inset 0 0 25px rgba(34, 197, 94, 0.15);
		}

		.bid-hot {
			box-shadow:
				0 0 35px rgba(239, 68, 68, 0.5),
				inset 0 0 35px rgba(239, 68, 68, 0.15);
		}

		.bid-active {
			box-shadow:
				0 0 25px rgba(245, 158, 11, 0.5),
				inset 0 0 25px rgba(245, 158, 11, 0.15);
		}
	}

	/* Reduced motion support */
	@media (prefers-reduced-motion: reduce) {
		.animate-pulse-soft,
		.animate-pulse-fast,
		.animate-pulse-urgent,
		.animate-pulse-border,
		.bg-gradient-animated {
			animation: none !important;
		}

		* {
			transition-duration: 0.01ms !important;
		}
	}

	/* Mobile optimizations */
	@media (max-width: 768px) {
		.auction-card {
			transform: none !important;
		}

		.auction-card:hover {
			transform: translateY(-1px) !important;
			scale: 1.01 !important;
		}
	}
</style>
