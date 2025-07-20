<script>
	import { t } from '$lib/i18n';
	import Tabs from '$lib/components/ui/Tabs.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Gallery from '$lib/components/ui/Gallery.svelte';
	import PropertyCard from '$lib/components/properties/PropertyCard.svelte';
	import AuctionStatus from '$lib/components/auction/AuctionStatus.svelte';

	export let auction;
	export let property;
	export let bids;
	export let bidsLoading;
	export let canBid;
	export let user;
	export let onLoadBids;
	export let onOpenBidModal;

	let activeTab = 'details';

	// Fix: Properly reactive tabs calculation
	$: tabs = [
		{ id: 'details', label: $t('auction.tabDetails') },
		{ id: 'property', label: $t('auction.tabProperty') },
		{ id: 'bids', label: `${$t('auction.tabBids')} (${Array.isArray(bids) ? bids.length : 0})` },
		{ id: 'terms', label: $t('auction.tabTerms') }
	];

	function getAllImages() {
		let images = [];

		if (auction?.media) {
			const auctionImages = auction.media
				.filter((m) => m.media_type === 'image')
				.map((m) => ({
					url: m.url || m.file,
					alt: m.name || auction.title,
					caption: m.name || 'Auction Image'
				}));
			images = [...images, ...auctionImages];
		}

		if (auction?.related_property?.media) {
			const propertyImages = auction.related_property.media
				.filter((m) => m.media_type === 'image')
				.map((m) => ({
					url: m.url || m.file,
					alt: m.name || auction.related_property.title,
					caption: m.name || 'Property Image'
				}));
			images = [...images, ...propertyImages];
		}

		return images;
	}

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
		const numericAmount = Number(amount);
		if (isNaN(numericAmount)) {
			return '--'; // Placeholder for invalid or non-numeric amounts
		}
		return new Intl.NumberFormat('en-US', {
			style: 'currency',
			currency: 'USD',
			minimumFractionDigits: 0,
			maximumFractionDigits: 0
		}).format(numericAmount);
	}

	function getTimeAgo(dateString) {
		const now = new Date();
		const past = new Date(dateString);
		const diffInSeconds = Math.floor((now - past) / 1000);

		if (diffInSeconds < 60) return $t('auction.justNow') || 'Just now';
		if (diffInSeconds < 3600)
			return `${Math.floor(diffInSeconds / 60)}${$t('auction.minutesAgo') || 'm ago'}`;
		if (diffInSeconds < 86400)
			return `${Math.floor(diffInSeconds / 3600)}${$t('auction.hoursAgo') || 'h ago'}`;
		return `${Math.floor(diffInSeconds / 86400)}${$t('auction.daysAgo') || 'd ago'}`;
	}

	// FIXED: Completely rewritten bidder name extraction function
	function getBidderName(bid) {
		// Return fallback immediately if bid is invalid
		if (!bid || typeof bid !== 'object') {
			return $t('auction.anonymousBidder') || 'Anonymous Bidder';
		}

		// Helper function to check if a value is a valid non-empty string
		function isValidString(value) {
			return (
				typeof value === 'string' &&
				value.trim().length > 0 &&
				value.trim() !== 'undefined' &&
				value.trim() !== 'null'
			);
		}

		// Helper function to safely convert and validate a value as string
		function safeString(value) {
			if (value === null || value === undefined) return null;
			const str = String(value).trim();
			if (
				str === '' ||
				str === 'undefined' ||
				str === 'null' ||
				str === 'NaN' ||
				str === '[object Object]'
			) {
				return null;
			}
			return str;
		}

		// Method 1: Try user_display_name first (most reliable)
		if (bid.user_display_name) {
			const displayName = safeString(bid.user_display_name);
			if (displayName) return displayName;
		}

		// Method 2: Try bidder_info object
		if (bid.bidder_info && typeof bid.bidder_info === 'object') {
			const info = bid.bidder_info;

			// Try display_name or name from bidder_info
			if (info.display_name) {
				const name = safeString(info.display_name);
				if (name) return name;
			}

			if (info.name) {
				const name = safeString(info.name);
				if (name) return name;
			}

			// Try username
			if (info.username) {
				const username = safeString(info.username);
				if (username) return username;
			}

			// Try first_name and last_name combination
			if (info.first_name) {
				const firstName = safeString(info.first_name);
				if (firstName) {
					const lastName = safeString(info.last_name);
					if (lastName) {
						return `${firstName} ${lastName}`;
					}
					return firstName;
				}
			}

			// Try email (extract username part before @)
			if (info.email && isValidString(info.email) && info.email.includes('@')) {
				const emailUsername = info.email.split('@')[0];
				const cleanUsername = safeString(emailUsername);
				if (cleanUsername) return cleanUsername;
			}

			// Try ID as last resort from bidder_info
			if (info.id) {
				const id = safeString(info.id);
				if (id) return `User ${id}`;
			}
		}

		// Method 3: Try direct bidder field
		if (bid.bidder) {
			const bidder = safeString(bid.bidder);
			if (bidder) return bidder;
		}

		// Method 4: Try user object
		if (bid.user && typeof bid.user === 'object') {
			if (bid.user.display_name) {
				const name = safeString(bid.user.display_name);
				if (name) return name;
			}

			if (bid.user.username) {
				const username = safeString(bid.user.username);
				if (username) return username;
			}

			if (bid.user.first_name) {
				const firstName = safeString(bid.user.first_name);
				if (firstName) {
					const lastName = safeString(bid.user.last_name);
					if (lastName) {
						return `${firstName} ${lastName}`;
					}
					return firstName;
				}
			}
		}

		// Method 5: Try any other name-like fields
		const nameFields = ['bidder_name', 'user_name', 'display_name', 'full_name'];
		for (const field of nameFields) {
			if (bid[field]) {
				const name = safeString(bid[field]);
				if (name) return name;
			}
		}

		// Final fallback
		return $t('auction.anonymousBidder') || 'Anonymous Bidder';
	}

	// Function to handle tab change and update parent
	function handleTabChange(event) {
		const tabId = event && event.id ? event.id : event;
		activeTab = tabId;

		if (tabId === 'bids' && (!Array.isArray(bids) || bids.length === 0) && !bidsLoading) {
			onLoadBids();
		}
	}
</script>

<!-- Image Gallery -->
<section class="overflow-hidden rounded-lg bg-white shadow-sm dark:bg-gray-800">
	<Gallery images={getAllImages()} alt={auction.title} showThumbnails={true} />
</section>

<!-- Navigation Tabs -->
<div class="overflow-hidden rounded-lg bg-white shadow-sm dark:bg-gray-800">
	<div class="border-b border-gray-200 dark:border-gray-700">
		<Tabs {tabs} bind:activeTab on:change={(e) => handleTabChange(e.detail)} />
	</div>

	<!-- Tab Content -->
	<div class="p-4 sm:p-6">
		{#if activeTab === 'details'}
			<div class="prose dark:prose-invert max-w-none">
				<h2 class="mb-4 text-xl font-bold text-gray-900 dark:text-white">
					{$t('auction.description')}
				</h2>

				{#if auction.description}
					<div class="mb-6 leading-relaxed text-gray-600 dark:text-gray-300">
						<p class="whitespace-pre-wrap">{auction.description}</p>
					</div>
				{:else}
					<div class="py-6 text-center text-gray-500 dark:text-gray-400">
						<svg
							class="mx-auto mb-2 h-10 w-10 opacity-40"
							fill="none"
							viewBox="0 0 24 24"
							stroke="currentColor"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
							/>
						</svg>
						<p class="text-sm">{$t('auction.noDescription')}</p>
					</div>
				{/if}

				<!-- Key Information Cards -->
				<div class="grid grid-cols-1 gap-4 md:grid-cols-2">
					<!-- Schedule Card -->
					<div class="rounded-lg bg-gray-50 p-4 dark:bg-gray-700">
						<h3
							class="mb-3 flex items-center text-base font-semibold text-gray-900 dark:text-white"
						>
							<svg
								class="mr-2 h-4 w-4 text-blue-500"
								fill="none"
								viewBox="0 0 24 24"
								stroke="currentColor"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
								/>
							</svg>
							{$t('auction.schedule')}
						</h3>
						<dl class="space-y-2">
							<div class="flex items-center justify-between">
								<dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
									{$t('auction.startDate')}
								</dt>
								<dd class="text-sm font-semibold text-gray-900 dark:text-white">
									{formatDateTime(auction.start_date)}
								</dd>
							</div>
							<div class="flex items-center justify-between">
								<dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
									{$t('auction.endDate')}
								</dt>
								<dd class="text-sm font-semibold text-gray-900 dark:text-white">
									{formatDateTime(auction.end_date)}
								</dd>
							</div>
							{#if auction.registration_deadline}
								<div class="flex items-center justify-between">
									<dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
										{$t('auction.registrationDeadline')}
									</dt>
									<dd class="text-sm font-semibold text-gray-900 dark:text-white">
										{formatDateTime(auction.registration_deadline)}
									</dd>
								</div>
							{/if}
						</dl>
					</div>

					<!-- Financial Details Card -->
					<div class="rounded-lg bg-gray-50 p-4 dark:bg-gray-700">
						<h3
							class="mb-3 flex items-center text-base font-semibold text-gray-900 dark:text-white"
						>
							<svg
								class="mr-2 h-4 w-4 text-green-500"
								fill="none"
								viewBox="0 0 24 24"
								stroke="currentColor"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"
								/>
							</svg>
							{$t('auction.keyDetails')}
						</h3>
						<dl class="space-y-2">
							<div class="flex items-center justify-between">
								<dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
									{$t('auction.startingBid')}
								</dt>
								<dd class="text-sm font-semibold text-gray-900 dark:text-white">
									{formatCurrency(auction.starting_bid)}
								</dd>
							</div>
							<div class="flex items-center justify-between">
								<dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
									{$t('auction.currentBid')}
								</dt>
								<dd class="text-sm font-semibold text-green-600 dark:text-green-400">
									{formatCurrency(auction.current_bid || auction.starting_bid)}
								</dd>
							</div>
							<div class="flex items-center justify-between">
								<dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
									{$t('auction.minimumIncrement')}
								</dt>
								<dd class="text-sm font-semibold text-gray-900 dark:text-white">
									{formatCurrency(auction.minimum_increment)}
								</dd>
							</div>
						</dl>
					</div>
				</div>
			</div>
		{:else if activeTab === 'property'}
			<div class="space-y-6">
				<div class="flex items-center justify-between">
					<h2 class="text-xl font-bold text-gray-900 dark:text-white">
						{$t('auction.auctionProperty')}
					</h2>
					{#if property && property.slug}
						<a
							href={`/properties/${property.slug}`}
							target="_blank"
							class="inline-flex items-center text-sm font-medium text-blue-600 transition-colors hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
						>
							{$t('property.viewDetails')}
							<svg class="ml-1 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
								/>
							</svg>
						</a>
					{/if}
				</div>

				<div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
					<!-- Property Card -->
					<div>
						{#if property}
							<PropertyCard {property} isCompact={true} />
						{:else}
							<div class="rounded-lg bg-gray-50 p-6 text-center dark:bg-gray-700">
								<p class="text-gray-500 dark:text-gray-400">
									{$t('property.noPropertyData') || 'Property data not available'}
								</p>
							</div>
						{/if}
					</div>

					<!-- Property Details -->
					<div class="space-y-4">
						{#if property}
							<!-- Key Details -->
							<div class="rounded-lg bg-gray-50 p-4 dark:bg-gray-700">
								<h4 class="mb-3 text-base font-semibold text-gray-900 dark:text-white">
									{$t('property.keyDetails')}
								</h4>
								<dl class="space-y-2">
									<div class="flex items-center justify-between">
										<dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
											{$t('property.propertyType')}
										</dt>
										<dd class="text-sm font-semibold text-gray-900 dark:text-white">
											{property.property_type_display || 'N/A'}
										</dd>
									</div>
									<div class="flex items-center justify-between">
										<dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
											{$t('property.size')}
										</dt>
										<dd class="text-sm font-semibold text-gray-900 dark:text-white">
											{property.size_sqm || 'N/A'}
											{property.size_sqm ? $t('property.sqm') : ''}
										</dd>
									</div>
									<div class="flex items-center justify-between">
										<dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
											{$t('property.location')}
										</dt>
										<dd class="text-sm font-semibold text-gray-900 dark:text-white">
											{property.location?.city
												? `${property.location.city}, ${property.location.state || ''}`
												: 'N/A'}
										</dd>
									</div>
									<div class="flex items-center justify-between">
										<dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
											{$t('property.marketValue')}
										</dt>
										<dd class="text-sm font-semibold text-green-600 dark:text-green-400">
											{property.market_value ? formatCurrency(property.market_value) : 'N/A'}
										</dd>
									</div>
								</dl>
							</div>
						{:else}
							<div class="rounded-lg bg-gray-50 p-4 text-center dark:bg-gray-700">
								<p class="text-gray-500 dark:text-gray-400">
									{$t('property.noPropertyDetails') || 'Property details not available'}
								</p>
							</div>
						{/if}

						<!-- Features -->
						{#if property && property.features && property.features.length > 0}
							<div class="rounded-lg bg-gray-50 p-4 dark:bg-gray-700">
								<h4 class="mb-3 text-base font-semibold text-gray-900 dark:text-white">
									{$t('property.features')}
								</h4>
								<div class="flex flex-wrap gap-1.5">
									{#each property.features as feature}
										<span
											class="inline-flex items-center rounded-md bg-blue-100 px-2 py-1 text-xs font-medium text-blue-800 dark:bg-blue-900 dark:text-blue-200"
										>
											{feature}
										</span>
									{/each}
								</div>
							</div>
						{/if}
					</div>
				</div>
			</div>
		{:else if activeTab === 'bids'}
			<div class="space-y-4">
				<!-- Bid History Header -->
				<div class="flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
					<div>
						<h2 class="text-xl font-bold text-gray-900 dark:text-white">
							{$t('auction.bidHistory')}
						</h2>
						<p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
							{Array.isArray(bids) ? bids.length : 0}
							{$t('auction.bidsPlaced')}
						</p>
					</div>
					<div class="flex items-center gap-2">
						{#if canBid}
							<Button variant="primary" size="small" on:click={onOpenBidModal}>
								<svg class="mr-1.5 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M12 6v6m0 0v6m0-6h6m-6 0H6"
									/>
								</svg>
								{$t('auction.placeBid')}
							</Button>
						{/if}
						<Button variant="outline" size="small" loading={bidsLoading} on:click={onLoadBids}>
							<svg class="mr-1.5 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
								/>
							</svg>
							{$t('auction.refresh')}
						</Button>
					</div>
				</div>

				{#if bidsLoading}
					<!-- Loading State -->
					<div class="flex items-center justify-center py-12">
						<div class="text-center">
							<div
								class="mb-3 inline-block h-6 w-6 animate-spin rounded-full border-b-2 border-blue-500"
							></div>
							<p class="text-sm text-gray-500 dark:text-gray-400">{$t('auction.loadingBids')}</p>
						</div>
					</div>
				{:else if !Array.isArray(bids) || bids.length === 0}
					<!-- Empty State -->
					<div class="py-12 text-center">
						<div
							class="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-gray-100 dark:bg-gray-700"
						>
							<svg
								class="h-6 w-6 text-gray-400 dark:text-gray-500"
								fill="none"
								viewBox="0 0 24 24"
								stroke="currentColor"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M13 10V3L4 14h7v7l9-11h-7z"
								/>
							</svg>
						</div>
						<h3 class="mb-2 text-base font-semibold text-gray-900 dark:text-gray-100">
							{$t('auction.noBids')}
						</h3>
						<p class="mb-4 text-sm text-gray-500 dark:text-gray-400">
							{$t('auction.beTheFirst')}
						</p>
						{#if canBid}
							<Button variant="primary" on:click={onOpenBidModal}>
								<svg class="mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M13 10V3L4 14h7v7l9-11h-7z"
									/>
								</svg>
								{$t('auction.placeFirstBid')}
							</Button>
						{:else if !user}
							<Button variant="primary" href={`/login?redirect=/auctions/${auction.slug}`}>
								{$t('auction.signInToPlaceFirstBid')}
							</Button>
						{/if}
					</div>
				{:else}
					<!-- Bid List -->
					<div class="space-y-3">
						{#each bids as bid, index (bid.id || `bid-${index}`)}
							<div
								class="group relative rounded-lg border border-gray-200 p-4 transition-all duration-200 hover:border-gray-300 dark:border-gray-700 dark:hover:border-gray-600 {index ===
								0
									? 'border-green-200 bg-gradient-to-r from-green-50 to-emerald-50 dark:border-green-800 dark:from-green-900/10 dark:to-emerald-900/10'
									: 'bg-white dark:bg-gray-800'} {bid.bidder_info?.id === user?.id
									? 'ring-1 ring-blue-200 dark:ring-blue-800'
									: ''}"
							>
								<div class="flex items-center justify-between">
									<div class="min-w-0 flex-1">
										<div class="mb-1 flex items-center gap-2">
											<p class="text-sm font-semibold text-gray-900 dark:text-white">
												{formatCurrency(bid.amount)}
											</p>
											{#if index === 0}
												<span
													class="inline-flex items-center rounded bg-green-100 px-2 py-0.5 text-xs font-medium text-green-800 dark:bg-green-900 dark:text-green-200"
												>
													{$t('auction.highestBid')}
												</span>
											{/if}
										</div>
										<div class="truncate text-xs text-gray-500 dark:text-gray-400">
											<!-- FIXED: Use the improved getBidderName function -->
											<span class="font-medium">
												{getBidderName(bid)}
											</span>
											{#if bid.bidder_info?.id === user?.id}
												<span class="ml-1 font-medium text-blue-600 dark:text-blue-400"
													>({$t('auction.you')})</span
												>
											{/if}
										</div>
									</div>
									<div class="ml-2 flex-shrink-0 text-right">
										<p class="mb-1 text-xs text-gray-500 dark:text-gray-400">
											{getTimeAgo(bid.bid_time)}
										</p>
										{#if bid.status}
											<AuctionStatus status={bid.status} isCompact={true} />
										{:else}
											<span
												class="inline-flex items-center rounded bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-800 dark:bg-blue-900 dark:text-blue-200"
											>
												{$t('auction.activeBid')}
											</span>
										{/if}
									</div>
								</div>

								<!-- Additional bid info if available -->
								{#if bid.auto_bid || bid.max_amount}
									<div class="mt-2 border-t border-gray-200 pt-2 dark:border-gray-600">
										<div class="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
											{#if bid.auto_bid}
												<span class="inline-flex items-center gap-1">
													<svg class="h-3 w-3" fill="currentColor" viewBox="0 0 20 20">
														<path
															fill-rule="evenodd"
															d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z"
															clip-rule="evenodd"
														/>
													</svg>
													{$t('auction.autoBid')}
												</span>
											{/if}
											{#if bid.max_amount}
												<span>{$t('auction.maxBid')}: {formatCurrency(bid.max_amount)}</span>
											{/if}
										</div>
									</div>
								{/if}
							</div>
						{/each}
					</div>

					<!-- Load More Button if there are many bids -->
					{#if bids.length >= 10}
						<div class="pt-4 text-center">
							<Button variant="outline" size="small" on:click={onLoadBids} loading={bidsLoading}>
								{$t('auction.loadMoreBids')}
							</Button>
						</div>
					{/if}
				{/if}
			</div>
		{:else if activeTab === 'terms'}
			<div class="space-y-4">
				<h2 class="text-xl font-bold text-gray-900 dark:text-white">
					{$t('auction.termsConditions')}
				</h2>

				{#if auction && auction.terms_conditions}
					<div
						class="prose dark:prose-invert max-w-none rounded-lg bg-gray-50 p-4 dark:bg-gray-700"
					>
						<div class="leading-relaxed whitespace-pre-wrap text-gray-600 dark:text-gray-300">
							{auction.terms_conditions}
						</div>
					</div>
				{:else}
					<div class="rounded-lg bg-gray-50 py-12 text-center dark:bg-gray-700">
						<div
							class="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-gray-200 dark:bg-gray-600"
						>
							<svg
								class="h-6 w-6 text-gray-400 dark:text-gray-500"
								fill="none"
								viewBox="0 0 24 24"
								stroke="currentColor"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
								/>
							</svg>
						</div>
						<h3 class="mb-1 text-base font-semibold text-gray-900 dark:text-gray-100">
							{$t('auction.noTerms')}
						</h3>
						<p class="text-sm text-gray-500 dark:text-gray-400">
							{$t('auction.contactForTerms')}
						</p>
					</div>
				{/if}

				<!-- Standard auction terms if no custom terms -->
				{#if auction && !auction.terms_conditions}
					<div
						class="rounded-lg border border-blue-200 bg-blue-50 p-4 dark:border-blue-800 dark:bg-blue-900/20"
					>
						<h4 class="mb-2 text-sm font-semibold text-blue-900 dark:text-blue-200">
							{$t('auction.standardTerms')}
						</h4>
						<ul class="space-y-1 text-sm text-blue-800 dark:text-blue-300">
							<li>• {$t('auction.term1')}</li>
							<li>• {$t('auction.term2')}</li>
							<li>• {$t('auction.term3')}</li>
							<li>• {$t('auction.term4')}</li>
						</ul>
					</div>
				{:else if !auction}
					<div class="rounded-lg bg-gray-50 p-6 text-center dark:bg-gray-700">
						<p class="text-gray-500 dark:text-gray-400">
							{$t('auction.noAuctionData') || 'Auction data not available'}
						</p>
					</div>
				{/if}
			</div>
		{/if}
	</div>
</div>
