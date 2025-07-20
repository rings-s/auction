<!-- src/routes/dashboard/bids/+page.svelte -->
<script>
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { t } from '$lib/i18n';
	import { user } from '$lib/stores/user';
	import { dashboardBids, dashboardLoading } from '$lib/stores/dashboard';
	import { getDashboardBids } from '$lib/api/dashboard';
	import { toast } from '$lib/stores/toastStore.svelte.js';
	import { formatDistanceToNow } from 'date-fns';

	// Components
	import Button from '$lib/components/ui/Button.svelte';
	import FormField from '$lib/components/ui/FormField.svelte';
	import LoadingSkeleton from '$lib/components/ui/LoadingSkeleton.svelte';
	import EmptyState from '$lib/components/ui/EmptyState.svelte';
	import Breadcrumb from '$lib/components/ui/Breadcrumb.svelte';

	let searchQuery = '';
	let statusFilter = '';
	let winningOnly = false;
	let currentPage = 1;
	let totalPages = 1;
	let totalBids = 0;

	// Breadcrumb items
	$: breadcrumbItems = [
		{ label: $t('nav.home'), href: '/' },
		{ label: $t('dashboard.title'), href: '/dashboard' },
		{ label: $t('dashboard.bids'), href: '/dashboard/bids', active: true }
	];

	// Status options
	const statusOptions = [
		{ value: '', label: $t('common.all') },
		{ value: 'pending', label: $t('auction.pending') },
		{ value: 'accepted', label: $t('auction.accepted') },
		{ value: 'winning', label: $t('auction.winning') },
		{ value: 'outbid', label: $t('auction.outbid') },
		{ value: 'rejected', label: $t('auction.rejected') }
	];

	// Load bids
	async function loadBids() {
		dashboardLoading.set(true);

		try {
			const filters = {
				page: currentPage,
				search: searchQuery || undefined,
				status: statusFilter || undefined,
				winning_only: winningOnly || undefined
			};

			const response = await getDashboardBids(filters);

			dashboardBids.set(response.results || []);
			totalPages = Math.ceil(response.count / 10);
			totalBids = response.count || 0;
		} catch (error) {
			toast.error($t('dashboard.loadBidsError'));
		} finally {
			dashboardLoading.set(false);
		}
	}

	// Handle search
	function handleSearch() {
		currentPage = 1;
		loadBids();
	}

	// Handle filter change
	function handleFilterChange() {
		currentPage = 1;
		loadBids();
	}

	// Handle pagination
	function handlePageChange(page) {
		currentPage = page;
		loadBids();
	}

	// Format time ago
	function formatTimeAgo(timestamp) {
		try {
			return formatDistanceToNow(new Date(timestamp), { addSuffix: true });
		} catch (error) {
			return $t('common.unknown');
		}
	}

	// Get status color
	function getStatusColor(status) {
		const colors = {
			pending: 'bg-yellow-100 text-yellow-800',
			accepted: 'bg-blue-100 text-blue-800',
			winning: 'bg-green-100 text-green-800',
			outbid: 'bg-red-100 text-red-800',
			rejected: 'bg-gray-100 text-gray-800'
		};

		return colors[status] || colors.pending;
	}

	onMount(() => {
		loadBids();
	});

	$: bids = $dashboardBids;
	$: isLoading = $dashboardLoading;
</script>

<svelte:head>
	<title>{$t('dashboard.bids')} - {$t('dashboard.title')} - {$t('app.name')}</title>
</svelte:head>

<div class="min-h-screen">
	<div class="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
		<!-- Header -->
		<div class="mb-6">
			<Breadcrumb items={breadcrumbItems} class="mb-4" />

			<div class="flex flex-col sm:flex-row sm:items-center sm:justify-between">
				<div>
					<h1 class="text-xl font-semibold text-gray-900">
						{$t('dashboard.bids')}
					</h1>
					<p class="mt-1 text-sm text-gray-600">
						{$t('dashboard.manageBids')}
					</p>
				</div>

				<div class="mt-4 sm:mt-0">
					<Button variant="primary" size="compact" href="/auctions">
						{$t('dashboard.viewAuctions')}
					</Button>
				</div>
			</div>
		</div>

		<!-- Filters -->
		<div class="mb-6 rounded-lg border border-gray-200 bg-white p-4">
			<div class="grid grid-cols-1 gap-4 md:grid-cols-4">
				<FormField
					type="text"
					placeholder={$t('common.search')}
					bind:value={searchQuery}
					on:input={handleSearch}
				/>

				<FormField
					type="select"
					options={statusOptions}
					bind:value={statusFilter}
					on:change={handleFilterChange}
				/>

				<div class="flex items-center">
					<input
						type="checkbox"
						id="winningOnly"
						bind:checked={winningOnly}
						on:change={handleFilterChange}
						class="text-primary-600 focus:ring-primary-500 h-4 w-4 rounded border-gray-300"
					/>
					<label for="winningOnly" class="ml-2 text-sm text-gray-700">
						{$t('auction.winningOnly')}
					</label>
				</div>

				<Button
					variant="outline"
					size="default"
					onClick={() => {
						searchQuery = '';
						statusFilter = '';
						winningOnly = false;
						handleFilterChange();
					}}
				>
					{$t('search.clear')}
				</Button>
			</div>
		</div>

		<!-- Bids List -->
		{#if isLoading}
			<div class="space-y-4">
				{#each Array(8) as _}
					<LoadingSkeleton type="rect" height="120px" />
				{/each}
			</div>
		{:else if bids.length === 0}
			<EmptyState
				icon="auction"
				title={$t('dashboard.noBids')}
				description={$t('dashboard.noBidsDesc')}
				actionLabel={$t('dashboard.viewAuctions')}
				actionUrl="/auctions"
			/>
		{:else}
			<div class="space-y-4">
				<!-- Bids List -->
				<div class="space-y-4">
					{#each bids as bid (bid.id)}
						<div
							class="rounded-lg border border-gray-200 bg-white p-4 transition-shadow hover:shadow-md"
						>
							<div class="flex items-start justify-between">
								<!-- Bid Info -->
								<div class="flex-1">
									<div class="mb-2 flex items-center space-x-3">
										<h3 class="truncate text-sm font-medium text-gray-900">
											{bid.auction_title}
										</h3>

										<span
											class="inline-flex items-center rounded px-2 py-0.5 text-xs font-medium {getStatusColor(
												bid.status
											)}"
										>
											{bid.status_display}
										</span>

										{#if bid.is_winning}
											<span
												class="inline-flex items-center rounded bg-green-100 px-2 py-0.5 text-xs font-medium text-green-800"
											>
												{$t('auction.winning')}
											</span>
										{/if}
									</div>

									<p class="mb-2 text-xs text-gray-600">
										{bid.property_title || $t('common.unknown')}
									</p>

									<div class="grid grid-cols-2 gap-4 text-xs md:grid-cols-4">
										<div>
											<span class="text-gray-500">{$t('auction.bidAmount')}</span>
											<p class="font-medium text-gray-900">
												${bid.bid_amount?.toLocaleString() || 0}
											</p>
										</div>

										{#if bid.max_bid_amount}
											<div>
												<span class="text-gray-500">{$t('auction.maxBid')}</span>
												<p class="font-medium text-gray-900">
													${bid.max_bid_amount.toLocaleString()}
												</p>
											</div>
										{/if}

										<div>
											<span class="text-gray-500">{$t('auction.bidTime')}</span>
											<p class="font-medium text-gray-900">
												{formatTimeAgo(bid.bid_time)}
											</p>
										</div>

										<div>
											<span class="text-gray-500">{$t('dashboard.verified')}</span>
											<p
												class="font-medium {bid.is_verified ? 'text-green-600' : 'text-yellow-600'}"
											>
												{bid.is_verified ? $t('common.yes') : $t('common.no')}
											</p>
										</div>
									</div>
								</div>

								<!-- Actions -->
								<div class="ml-4 flex items-center space-x-2">
									<Button
										variant="outline"
										size="compact"
										href="/auctions/{bid.auction_slug || bid.auction_id}"
									>
										{$t('auction.viewAuction')}
									</Button>
								</div>
							</div>
						</div>
					{/each}
				</div>

				<!-- Pagination -->
				{#if totalPages > 1}
					<div
						class="flex items-center justify-between rounded-lg border border-gray-200 bg-white px-4 py-3"
					>
						<div class="flex items-center">
							<p class="text-sm text-gray-700">
								{$t('dashboard.showing')}
								<span class="font-medium">{(currentPage - 1) * 10 + 1}</span>
								{$t('common.to')}
								<span class="font-medium">{Math.min(currentPage * 10, totalBids)}</span>
								{$t('common.of')}
								<span class="font-medium">{totalBids}</span>
								{$t('dashboard.bids')}
							</p>
						</div>

						<div class="flex items-center space-x-2">
							<Button
								variant="outline"
								size="compact"
								disabled={currentPage === 1}
								onClick={() => handlePageChange(currentPage - 1)}
							>
								{$t('common.previous')}
							</Button>

							<span class="text-sm text-gray-700">
								{currentPage} / {totalPages}
							</span>

							<Button
								variant="outline"
								size="compact"
								disabled={currentPage === totalPages}
								onClick={() => handlePageChange(currentPage + 1)}
							>
								{$t('common.next')}
							</Button>
						</div>
					</div>
				{/if}
			</div>
		{/if}
	</div>
</div>
