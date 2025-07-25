<!-- src/lib/components/AuctionPreview.svelte -->
<script>
	import { t } from '$lib/i18n';
	import AuctionStatus from '$lib/components/auction/AuctionStatus.svelte';
	import CountdownTimer from '$lib/components/auction/CountdownTimer.svelte';

	export let auction = {};

	function formatDateTime(dateString) {
		try {
			const date = new Date(dateString);
			return new Intl.DateTimeFormat('default', {
				year: 'numeric',
				month: 'long',
				day: 'numeric',
				hour: '2-digit',
				minute: '2-digit'
			}).format(date);
		} catch (e) {
			return dateString;
		}
	}
</script>

<div class="rounded-lg bg-gray-50 p-6 dark:bg-gray-900">
	<div class="mb-8">
		<div class="flex flex-wrap items-start justify-between">
			<div class="mb-4 md:mb-0">
				<div class="mb-2 flex flex-wrap items-center space-x-2">
					<AuctionStatus status={auction.status} />
					<span
						class="inline-flex items-center rounded-md bg-gray-100 px-2.5 py-0.5 text-sm font-medium text-gray-800 dark:bg-gray-700 dark:text-gray-200"
					>
						{auction.auction_type === 'sealed'
							? $t('auction.typeSealed')
							: auction.auction_type === 'reserve'
								? $t('auction.typeReserve')
								: $t('auction.typeNoReserve')}
					</span>
					{#if auction.is_featured}
						<span
							class="inline-flex items-center rounded-md bg-amber-100 px-2.5 py-0.5 text-sm font-medium text-amber-800 dark:bg-amber-900 dark:text-amber-200"
						>
							{$t('auction.featured')}
						</span>
					{/if}
				</div>
				<h1 class="mb-2 text-3xl font-bold text-gray-900 dark:text-white">
					{auction.title}
				</h1>
			</div>
		</div>
	</div>

	<div class="grid grid-cols-1 gap-8 lg:grid-cols-3">
		<!-- Main content -->
		<div class="space-y-6 lg:col-span-2">
			<div class="rounded-lg bg-white p-6 shadow-md dark:bg-gray-800">
				<h2 class="mb-4 text-xl font-semibold text-gray-900 dark:text-white">
					{$t('auction.description')}
				</h2>
				<div class="prose dark:prose-invert max-w-none text-gray-600 dark:text-gray-300">
					<p>{auction.description || $t('auction.noDescription')}</p>
				</div>

				<div class="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2">
					<div>
						<h3 class="mb-2 text-lg font-medium text-gray-900 dark:text-white">
							{$t('auction.startEndDates')}
						</h3>
						<dl class="grid grid-cols-2 gap-x-4 gap-y-2">
							<dt class="text-sm text-gray-500 dark:text-gray-400">
								{$t('auction.startDate')}
							</dt>
							<dd class="text-sm font-medium text-gray-900 dark:text-white">
								{formatDateTime(auction.start_date)}
							</dd>
							<dt class="text-sm text-gray-500 dark:text-gray-400">
								{$t('auction.endDate')}
							</dt>
							<dd class="text-sm font-medium text-gray-900 dark:text-white">
								{formatDateTime(auction.end_date)}
							</dd>
							{#if auction.registration_deadline}
								<dt class="text-sm text-gray-500 dark:text-gray-400">
									{$t('auction.registrationDeadline')}
								</dt>
								<dd class="text-sm font-medium text-gray-900 dark:text-white">
									{formatDateTime(auction.registration_deadline)}
								</dd>
							{/if}
						</dl>
					</div>

					<div>
						<h3 class="mb-2 text-lg font-medium text-gray-900 dark:text-white">
							{$t('auction.bidding')}
						</h3>
						<dl class="grid grid-cols-2 gap-x-4 gap-y-2">
							<dt class="text-sm text-gray-500 dark:text-gray-400">
								{$t('auction.startingBid')}
							</dt>
							<dd class="text-sm font-medium text-gray-900 dark:text-white">
								${auction.starting_bid?.toLocaleString() || '0'}
							</dd>
							<dt class="text-sm text-gray-500 dark:text-gray-400">
								{$t('auction.minimumIncrement')}
							</dt>
							<dd class="text-sm font-medium text-gray-900 dark:text-white">
								${auction.minimum_increment?.toLocaleString() || '0'}
							</dd>
						</dl>
					</div>
				</div>
			</div>

			<!-- Property Preview (if available) -->
			{#if auction.related_property}
				<div class="rounded-lg bg-white p-6 shadow-md dark:bg-gray-800">
					<h2 class="mb-4 text-xl font-semibold text-gray-900 dark:text-white">
						{$t('auction.auctionProperty')}
					</h2>
					<div class="flex items-center">
						<div
							class="h-16 w-16 flex-shrink-0 overflow-hidden rounded-md bg-gray-200 dark:bg-gray-700"
						>
							<img
								src={auction.related_property.main_image?.url || '/images/property-placeholder.jpg'}
								alt={auction.related_property.title}
								class="h-full w-full object-cover"
							/>
						</div>
						<div class="ml-4">
							<h3 class="text-lg font-medium text-gray-900 dark:text-white">
								{auction.related_property.title}
							</h3>
							<p class="text-sm text-gray-500 dark:text-gray-400">
								{auction.related_property.address}, {auction.related_property.location?.city}
							</p>
						</div>
					</div>
				</div>
			{/if}

			<!-- Terms Preview (if available) -->
			{#if auction.terms_conditions}
				<div class="rounded-lg bg-white p-6 shadow-md dark:bg-gray-800">
					<h2 class="mb-4 text-xl font-semibold text-gray-900 dark:text-white">
						{$t('auction.termsConditions')}
					</h2>
					<div class="prose dark:prose-invert max-w-none text-gray-600 dark:text-gray-300">
						<p>{auction.terms_conditions}</p>
					</div>
				</div>
			{/if}
		</div>

		<!-- Sidebar Preview -->
		<div class="space-y-6">
			<div class="rounded-lg bg-white p-6 shadow-md dark:bg-gray-800">
				<h3 class="mb-4 text-lg font-medium text-gray-900 dark:text-white">
					{$t('auction.auctionStatus')}
				</h3>

				{#if auction.status === 'live'}
					<div class="mb-4">
						<h4 class="mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">
							{$t('auction.timeRemaining')}
						</h4>
						<CountdownTimer endDate={auction.end_date} />
					</div>
				{:else if auction.status === 'scheduled'}
					<div class="mb-4">
						<h4 class="mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">
							{$t('auction.startsIn')}
						</h4>
						<CountdownTimer endDate={auction.start_date} variant="secondary" />
					</div>
				{/if}

				<div class="mb-4 border-t border-gray-200 pt-4 dark:border-gray-700">
					<div class="mb-1 flex items-baseline justify-between">
						<h4 class="text-sm font-medium text-gray-700 dark:text-gray-300">
							{$t('auction.startingBid')}
						</h4>
						<span class="text-primary-600 dark:text-primary-400 text-lg font-bold">
							${auction.starting_bid?.toLocaleString() || '0'}
						</span>
					</div>
				</div>
			</div>

			<!-- Media Preview -->
			{#if auction.media && auction.media.length > 0}
				<div class="rounded-lg bg-white p-6 shadow-md dark:bg-gray-800">
					<h3 class="mb-4 text-lg font-medium text-gray-900 dark:text-white">
						{$t('auction.media')}
					</h3>

					<div class="grid grid-cols-2 gap-2">
						{#each auction.media.slice(0, 4) as media}
							<div
								class="aspect-w-1 aspect-h-1 overflow-hidden rounded-md bg-gray-200 dark:bg-gray-700"
							>
								{#if media.media_type === 'image'}
									<img src={media.file} alt={media.name} class="h-full w-full object-cover" />
								{:else}
									<div class="flex h-full items-center justify-center">
										<svg
											class="h-8 w-8 text-gray-400"
											fill="none"
											viewBox="0 0 24 24"
											stroke="currentColor"
										>
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												stroke-width="2"
												d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"
											/>
										</svg>
									</div>
								{/if}
							</div>
						{/each}
					</div>

					{#if auction.media.length > 4}
						<div class="mt-2 text-center">
							<span class="text-sm text-gray-500 dark:text-gray-400">
								+{auction.media.length - 4}
								{$t('auction.moreImages')}
							</span>
						</div>
					{/if}
				</div>
			{/if}
		</div>
	</div>
</div>
