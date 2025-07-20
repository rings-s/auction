<script>
	import { t } from '$lib/i18n';
	import AuctionStatus from '$lib/components/auction/AuctionStatus.svelte';
	import ShareButtons from '$lib/components/shared/ShareButtons.svelte';
	import Button from '$lib/components/ui/Button.svelte';

	export let auction;
	export let isOwner;
	export let viewCount;
	export let bidCount;
</script>

<!-- Page Header -->
<header class="mb-8">
	<div class="flex flex-col justify-between gap-4 lg:flex-row lg:items-start">
		<div class="min-w-0 flex-1">
			<!-- Status Badges -->
			<div class="mb-3 flex flex-wrap items-center gap-2">
				<AuctionStatus status={auction.status} />
				<span
					class="inline-flex items-center rounded-md bg-gray-100 px-2 py-1 text-xs font-medium text-gray-800 dark:bg-gray-700 dark:text-gray-200"
				>
					{auction.auction_type === 'sealed'
						? $t('auction.typeSealed')
						: auction.auction_type === 'private'
							? $t('auction.typeReserve')
							: $t('auction.typeNoReserve')}
				</span>
				{#if auction.is_featured}
					<span
						class="bg-warning-100 text-warning-800 dark:bg-warning-900 dark:text-warning-200 inline-flex items-center rounded-md px-2 py-1 text-xs font-medium"
					>
						⭐ {$t('auction.featured')}
					</span>
				{/if}
			</div>

			<!-- Title -->
			<h1 class="mb-2 text-2xl leading-tight font-bold text-gray-900 lg:text-3xl dark:text-white">
				{auction.title}
			</h1>

			<!-- Metadata -->
			<div class="flex flex-wrap items-center gap-3 text-sm text-gray-500 dark:text-gray-400">
				<span>Auction #{auction.id}</span>
				<span>•</span>
				<span>{viewCount} views</span>
				<span>•</span>
				<span>{bidCount} bids</span>
			</div>
		</div>

		<!-- Action Buttons -->
		<div class="flex flex-wrap items-center gap-2">
			<ShareButtons
				url={`/auctions/${auction.slug}`}
				title={auction.title}
				description={auction.description}
			/>
			{#if isOwner}
				<Button
					variant="outline"
					size="small"
					href={`/auctions/${auction.id}/edit`}
					class="inline-flex items-center"
				>
					<svg class="mr-1.5 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
						/>
					</svg>
					{$t('auction.edit')}
				</Button>
			{/if}
		</div>
	</div>
</header>
