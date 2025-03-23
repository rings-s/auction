<!-- src/lib/components/auction/BidForm.svelte -->
<script>
	import { createEventDispatcher } from 'svelte';
	import { t, formatCurrency } from '$lib/i18n';
	import api from '$lib/services/api';

	// Props
	export let auction;

	// State
	let bidAmount = auction.current_bid + auction.min_bid_increment;
	let isAutoBid = false;
	let maxBidAmount = bidAmount * 1.5; // Default max bid is 1.5x the initial bid
	let loading = false;
	let error = null;
	let success = null;

	// Calculate minimum bid amount based on current bid and increment
	$: minBidAmount = auction.current_bid + auction.min_bid_increment;

	// Event dispatcher to notify parent component
	const dispatch = createEventDispatcher();

	// Handle bid form submission
	async function handleSubmit() {
		// Reset messages
		error = null;
		success = null;

		// Validate bid amount
		if (bidAmount < minBidAmount) {
			error = $t('auctions.bid_too_low').replace('{0}', formatCurrency(minBidAmount));
			return;
		}

		// Validate max bid amount for auto-bidding
		if (isAutoBid && maxBidAmount <= bidAmount) {
			error = $t('auctions.max_bid_too_low');
			return;
		}

		loading = true;

		try {
			// Prepare bid data
			const bidData = {
				auction: auction.id,
				bid_amount: bidAmount,
				is_auto_bid: isAutoBid,
				max_bid_amount: isAutoBid ? maxBidAmount : null
			};

			// Send bid request
			const response = await api.post('bids/place/', bidData);

			if (response && response.data) {
				// Show success message
				success = $t('system_messages.bid_placed_success');

				// Notify parent component
				dispatch('bid-placed', {
					bid: response.data.bid,
					amount: bidAmount
				});

				// Reset form
				bidAmount = response.data.bid.bid_amount + auction.min_bid_increment;
				isAutoBid = false;
				maxBidAmount = bidAmount * 1.5;
			} else {
				throw new Error('Invalid response format');
			}
		} catch (err) {
			console.error('Error placing bid:', err);

			// Set appropriate error message
			if (err.status === 400 && err.data && err.data.error) {
				error = err.data.error;
			} else {
				error = err.message || $t('system_messages.bid_placed_failure');
			}
		} finally {
			loading = false;
		}
	}

	// Handle bid amount input
	function handleBidInput(event) {
		const value = Number(event.target.value);
		bidAmount = value;

		// Update max bid amount if it's less than the bid amount
		if (isAutoBid && maxBidAmount <= value) {
			maxBidAmount = value * 1.5;
		}
	}

	// Format number for input value
	function formatNumber(value) {
		return value ? Number(value).toString() : '';
	}

	// Handle auto-bid toggle
	function toggleAutoBid() {
		isAutoBid = !isAutoBid;

		// If enabling auto-bid, set a default max bid amount
		if (isAutoBid) {
			maxBidAmount = Math.max(maxBidAmount, bidAmount * 1.5);
		}
	}
</script>

<form class="space-y-4" on:submit|preventDefault={handleSubmit}>
	<!-- Error/Success Messages -->
	{#if error}
		<div class="rounded-lg bg-status-error bg-opacity-10 p-3 text-sm text-status-error">
			{error}
		</div>
	{/if}

	{#if success}
		<div class="rounded-lg bg-status-success bg-opacity-10 p-3 text-sm text-status-success">
			{success}
		</div>
	{/if}

	<!-- Bid Amount Input -->
	<div>
		<label for="bidAmount" class="mb-2 block text-sm font-medium text-cosmos-text">
			{$t('auctions.your_bid')}
		</label>
		<div class="relative">
			<div class="pointer-events-none absolute inset-y-0 start-0 flex items-center pl-3">
				<span class="text-cosmos-text-muted"> ﷼ </span>
			</div>
			<input
				type="number"
				id="bidAmount"
				min={minBidAmount}
				step={auction.min_bid_increment}
				bind:value={bidAmount}
				on:input={handleBidInput}
				class="w-full rounded-lg border border-cosmos-bg-light bg-cosmos-bg p-3 pl-8 text-cosmos-text outline-none focus:border-primary"
				disabled={loading}
			/>
		</div>
		<p class="mt-1 text-xs text-cosmos-text-muted">
			{$t('auctions.min_bid_info').replace('{0}', formatCurrency(minBidAmount))}
		</p>
	</div>

	<!-- Auto-Bid Toggle -->
	<div class="flex items-center">
		<input
			type="checkbox"
			id="autoBid"
			bind:checked={isAutoBid}
			on:change={toggleAutoBid}
			class="h-4 w-4 rounded border-cosmos-bg-light bg-cosmos-bg text-primary focus:ring-primary"
			disabled={loading}
		/>
		<label for="autoBid" class="ml-2 text-sm text-cosmos-text">
			{$t('auctions.enable_auto_bid')}
		</label>
	</div>

	<!-- Max Bid Amount (for Auto-Bid) -->
	{#if isAutoBid}
		<div>
			<label for="maxBidAmount" class="mb-2 block text-sm font-medium text-cosmos-text">
				{$t('auctions.max_bid_amount')}
			</label>
			<div class="relative">
				<div class="pointer-events-none absolute inset-y-0 start-0 flex items-center pl-3">
					<span class="text-cosmos-text-muted"> ﷼ </span>
				</div>
				<input
					type="number"
					id="maxBidAmount"
					min={bidAmount + auction.min_bid_increment}
					step={auction.min_bid_increment}
					bind:value={maxBidAmount}
					class="w-full rounded-lg border border-cosmos-bg-light bg-cosmos-bg p-3 pl-8 text-cosmos-text outline-none focus:border-primary"
					disabled={loading}
				/>
			</div>
			<p class="mt-1 text-xs text-cosmos-text-muted">
				{$t('auctions.max_bid_info')}
			</p>
		</div>
	{/if}

	<!-- Submit Button -->
	<div>
		<button
			type="submit"
			class="w-full rounded-lg bg-primary py-3 text-white transition hover:bg-primary-dark disabled:cursor-not-allowed disabled:bg-primary disabled:opacity-50"
			disabled={loading || bidAmount < minBidAmount || (isAutoBid && maxBidAmount <= bidAmount)}
		>
			{#if loading}
				<span class="flex items-center justify-center space-x-2">
					<span class="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent"
					></span>
					<span>{$t('general.processing')}</span>
				</span>
			{:else}
				{$t('auctions.place_bid')}
			{/if}
		</button>
	</div>

	<!-- Bid Terms -->
	<p class="text-xs text-cosmos-text-dim">
		{$t('auctions.bid_terms')}
	</p>
</form>
