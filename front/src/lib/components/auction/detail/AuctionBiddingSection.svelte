<script>
	import { t } from '$lib/i18n';
	import Button from '$lib/components/ui/Button.svelte';

	export let auction;
	export let bids;
	export let canBid;
	export let canRegister;
	export let isLiveAuction;
	export let isScheduledAuction;
	export let placingBid;
	export let userHighestBid;
	export let minimumBidAmount;
	export let user;
	export let onOpenBidModal;
	export let onShowRegisterModal;

	function formatCurrency(amount) {
		return new Intl.NumberFormat('en-US', {
			style: 'currency',
			currency: 'USD',
			minimumFractionDigits: 0,
			maximumFractionDigits: 0
		}).format(amount);
	}
</script>

<!-- ENHANCED BIDDING SECTION with Improved Design -->
<section class="mb-8">
	<div
		class="relative overflow-hidden rounded-xl border border-gray-200 bg-white shadow-lg dark:border-gray-700 dark:bg-gray-800"
	>
		<!-- Clean gradient background -->
		<div
			class="absolute inset-0 bg-gradient-to-br from-blue-50/50 via-transparent to-indigo-50/50 dark:from-gray-900/50 dark:via-transparent dark:to-gray-800/50"
		></div>

		<!-- Content -->
		<div class="relative">
			<!-- Header Section -->
			<div class="border-b border-gray-200 px-4 py-6 sm:px-6 dark:border-gray-700">
				<div class="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
					<div>
						<h2
							class="flex items-center gap-3 text-xl font-bold text-gray-900 sm:text-2xl dark:text-white"
						>
							{#if isLiveAuction}
								<span class="flex items-center gap-2">
									<span class="h-3 w-3 animate-pulse rounded-full bg-red-500"></span>
									<span class="text-lg text-red-600 dark:text-red-400">🔴</span>
									{$t('auction.liveAuction')}
								</span>
							{:else if isScheduledAuction}
								<span class="flex items-center gap-2">
									<span class="h-3 w-3 animate-pulse rounded-full bg-amber-500"></span>
									<span class="text-lg text-amber-600 dark:text-amber-400">⏰</span>
									{$t('auction.startsSoon')}
								</span>
							{/if}
						</h2>
						<div
							class="mt-2 flex flex-wrap items-center gap-4 text-sm text-gray-600 dark:text-gray-300"
						>
							<span
								>{$t('auction.currentBid')}:
								<span class="font-semibold text-gray-900 dark:text-white"
									>{formatCurrency(auction.current_bid || auction.starting_bid)}</span
								></span
							>
							<span>•</span>
							<span
								>{$t('auction.nextBid')}:
								<span class="font-semibold text-blue-600 dark:text-blue-400"
									>{formatCurrency(minimumBidAmount)}</span
								></span
							>
						</div>
					</div>

					<!-- Bid Count Display -->
					<div class="text-center sm:text-right">
						<div class="text-3xl leading-none font-bold text-gray-900 sm:text-4xl dark:text-white">
							{auction.bid_count || bids.length}
						</div>
						<div class="text-sm font-medium text-gray-500 dark:text-gray-400">
							{$t('auction.totalBids')}
						</div>
					</div>
				</div>
			</div>

			<!-- Bidding Interface -->
			<div class="p-4 sm:p-6">
				{#if canBid}
					<div class="space-y-6">
						<!-- Main Action -->
						<div class="flex flex-col items-center gap-4 sm:flex-row">
							<div class="flex-1">
								<Button
									variant="primary"
									size="large"
									class="w-full border-0 bg-blue-600 py-4 text-lg font-semibold shadow-lg hover:bg-blue-700"
									on:click={onOpenBidModal}
									disabled={placingBid}
								>
									{#if placingBid}
										<svg
											class="mr-3 -ml-1 h-5 w-5 animate-spin text-white"
											xmlns="http://www.w3.org/2000/svg"
											fill="none"
											viewBox="0 0 24 24"
										>
											<circle
												class="opacity-25"
												cx="12"
												cy="12"
												r="10"
												stroke="currentColor"
												stroke-width="4"
											></circle>
											<path
												class="opacity-75"
												fill="currentColor"
												d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
											></path>
										</svg>
									{:else}
										<svg class="mr-3 h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
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
								<p class="mt-2 text-center text-sm text-gray-500 dark:text-gray-400">
									{$t('auction.minimumBid')}: {formatCurrency(minimumBidAmount)}
								</p>
							</div>

							{#if userHighestBid}
								<div
									class="flex-1 rounded-lg border border-gray-200 bg-gray-50 p-4 text-center dark:border-gray-600 dark:bg-gray-700"
								>
									<div class="mb-1 text-xs text-gray-500 dark:text-gray-400">
										{$t('auction.yourHighestBid')}
									</div>
									<div class="mb-1 text-xl font-bold text-gray-900 dark:text-white">
										{formatCurrency(userHighestBid.amount)}
									</div>
									<div class="text-sm font-medium">
										{#if userHighestBid.status === 'winning'}
											<span class="text-green-600 dark:text-green-400"
												>🎉 {$t('auction.winning')}</span
											>
										{:else}
											<span class="text-amber-600 dark:text-amber-400"
												>⚠️ {$t('auction.outbid')}</span
											>
										{/if}
									</div>
								</div>
							{/if}
						</div>

						<!-- Scheduled Auction Notice -->
						{#if isScheduledAuction}
							<div
								class="rounded-lg border border-amber-200 bg-amber-50 p-4 dark:border-amber-800 dark:bg-amber-900/20"
							>
								<div class="flex items-start gap-3">
									<svg
										class="mt-0.5 h-5 w-5 flex-shrink-0 text-amber-600 dark:text-amber-400"
										fill="currentColor"
										viewBox="0 0 24 24"
									>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
										/>
									</svg>
									<div>
										<h4 class="mb-1 text-sm font-medium text-amber-800 dark:text-amber-200">
											{$t('auction.preBiddingAvailable')}
										</h4>
										<p class="text-sm text-amber-700 dark:text-amber-300">
											{$t('auction.preBiddingDescription')}
										</p>
									</div>
								</div>
							</div>
						{/if}
					</div>
				{:else if canRegister}
					<!-- Registration CTA -->
					<div class="py-8 text-center">
						<div
							class="mx-auto max-w-sm rounded-lg border border-gray-200 bg-gray-50 p-6 dark:border-gray-600 dark:bg-gray-700"
						>
							<div
								class="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-blue-100 dark:bg-blue-900"
							>
								<svg
									class="h-8 w-8 text-blue-600 dark:text-blue-400"
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
							<h3 class="mb-2 text-lg font-bold text-gray-900 dark:text-white">
								{$t('auction.joinThisAuction')}
							</h3>
							<p class="mb-4 text-sm text-gray-600 dark:text-gray-400">
								{$t('auction.registerToParticipate')}
							</p>
							<Button
								variant="primary"
								size="default"
								class="bg-blue-600 font-semibold hover:bg-blue-700"
								on:click={onShowRegisterModal}
							>
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
						</div>
					</div>
				{:else if !user}
					<!-- Sign In CTA -->
					<div class="py-8 text-center">
						<div
							class="mx-auto max-w-sm rounded-lg border border-gray-200 bg-gray-50 p-6 dark:border-gray-600 dark:bg-gray-700"
						>
							<div
								class="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-blue-100 dark:bg-blue-900"
							>
								<svg
									class="h-8 w-8 text-blue-600 dark:text-blue-400"
									fill="none"
									viewBox="0 0 24 24"
									stroke="currentColor"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
									/>
								</svg>
							</div>
							<h3 class="mb-2 text-lg font-bold text-gray-900 dark:text-white">
								{$t('auction.signInToBid')}
							</h3>
							<p class="mb-4 text-sm text-gray-600 dark:text-gray-400">
								{$t('auction.createAccountToParticipate')}
							</p>
							<Button
								variant="primary"
								size="default"
								class="bg-blue-600 font-semibold hover:bg-blue-700"
								href={`/login?redirect=/auctions/${auction.slug}`}
							>
								<svg class="mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1"
									/>
								</svg>
								{$t('auction.signInToBid')}
							</Button>
						</div>
					</div>
				{/if}
			</div>
		</div>
	</div>
</section>
