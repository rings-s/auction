<!-- src/lib/components/auctions/BidForm.svelte -->
<script>
	import { createEventDispatcher } from 'svelte';
	import { t, formatCurrency } from '$lib/i18n';
	import { auctionActions, errors } from '$lib/stores/auction';
	
	// Components 
	import TextField from '$lib/components/ui/TextField.svelte';
	import Checkbox from '$lib/components/ui/Checkbox.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Alert from '$lib/components/ui/Alert.svelte';
	
	// Props
	export let auction;
	export let disabled = false;
	
	// State
	let bidAmount = auction.current_bid + auction.min_bid_increment;
	let isAutoBid = false;
	let maxBidAmount = bidAmount * 1.5; // Default max bid is 1.5x the initial bid
	let loading = false;
	let error = null;
	let success = null;
	let formErrors = {};
	
	// Calculate minimum bid amount based on current bid and increment
	$: minBidAmount = auction.current_bid + auction.min_bid_increment;
	
	// Event dispatcher to notify parent component
	const dispatch = createEventDispatcher();
	
	// Validate form
	function validateForm() {
	  const errors = {};
	  
	  if (!bidAmount || bidAmount <= 0) {
		errors.bidAmount = t('auctions.bid_amount_required');
	  }
	  
	  if (bidAmount < minBidAmount) {
		errors.bidAmount = t('auctions.bid_minimum_increment', {
		  amount: formatCurrency(minBidAmount)
		});
	  }
	  
	  if (isAutoBid) {
		if (!maxBidAmount || maxBidAmount <= 0) {
		  errors.maxBidAmount = t('auctions.max_bid_amount_required');
		}
		
		if (maxBidAmount <= bidAmount) {
		  errors.maxBidAmount = t('auctions.max_bid_higher_than_bid');
		}
	  }
	  
	  formErrors = errors;
	  return Object.keys(errors).length === 0;
	}
	
	// Handle bid form submission
	async function handleSubmit() {
	  // Reset messages
	  error = null;
	  success = null;
	  
	  // Validate form
	  if (!validateForm()) {
		return;
	  }
	  
	  loading = true;
	  
	  try {
		const result = await auctionActions.placeBid(
		  auction.id, 
		  bidAmount, 
		  isAutoBid, 
		  isAutoBid ? maxBidAmount : null
		);
		
		if (result.success) {
		  // Show success message
		  success = t('system_messages.bid_placed_success');
		  
		  // Notify parent component
		  dispatch('bid-placed', {
			bid: result.data.bid,
			amount: bidAmount
		  });
		  
		  // Reset form
		  bidAmount = result.data.bid.bid_amount + auction.min_bid_increment;
		  isAutoBid = false;
		  maxBidAmount = bidAmount * 1.5;
		} else {
		  error = result.error || t('system_messages.bid_placed_failure');
		}
	  } catch (err) {
		console.error('Error placing bid:', err);
		error = err.message || t('system_messages.bid_placed_failure');
	  } finally {
		loading = false;
	  }
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
  
  <div class="bid-form bg-white dark:bg-neutral-800 rounded-xl border border-neutral-200 dark:border-neutral-700 shadow-sm p-4">
	<h3 class="text-lg font-semibold text-neutral-800 dark:text-neutral-200 mb-4">
	  {t('auctions.place_bid')}
	</h3>
	
	<!-- Current Bid / Starting Price -->
	<div class="mb-4 flex justify-between items-center">
	  <span class="text-sm text-neutral-600 dark:text-neutral-400">
		{auction.bid_count > 0 ? t('auctions.current_bid') : t('auctions.starting_price')}
	  </span>
	  <span class="font-semibold text-neutral-800 dark:text-neutral-200">
		{formatCurrency(auction.current_bid || auction.starting_price)}
	  </span>
	</div>
	
	<!-- Min Increment Info -->
	<div class="mb-4 flex justify-between items-center">
	  <span class="text-sm text-neutral-600 dark:text-neutral-400">
		{t('auctions.min_increment')}
	  </span>
	  <span class="font-semibold text-neutral-800 dark:text-neutral-200">
		{formatCurrency(auction.min_bid_increment)}
	  </span>
	</div>
	
	<div class="border-t border-neutral-200 dark:border-neutral-700 my-4"></div>
	
	<!-- Error/Success Messages -->
	{#if error || $errors.bidError}
	  <Alert 
		type="error" 
		message={error || $errors.bidError} 
		class="mb-4" 
		dismissible={true}
		on:dismiss={() => error = null}
	  />
	{/if}
	
	{#if success}
	  <Alert 
		type="success" 
		message={success} 
		class="mb-4"
		dismissible={true}
		on:dismiss={() => success = null}
	  />
	{/if}
	
	<form on:submit|preventDefault={handleSubmit} class="space-y-4">
	  <!-- Bid Amount Input -->
	  <div>
		<TextField
		  label={t('auctions.your_bid')}
		  type="number"
		  min={minBidAmount}
		  step={auction.min_bid_increment}
		  bind:value={bidAmount}
		  error={formErrors.bidAmount}
		  prefix="SAR"
		  required={true}
		  disabled={loading || disabled}
		/>
		
		<p class="mt-1 text-xs text-neutral-500 dark:text-neutral-400">
		  {t('auctions.min_bid_info').replace('{0}', formatCurrency(minBidAmount))}
		</p>
	  </div>
	  
	  <!-- Auto-Bid Toggle -->
	  <div>
		<Checkbox
		  label={t('auctions.enable_auto_bid')}
		  bind:checked={isAutoBid}
		  on:change={toggleAutoBid}
		  disabled={loading || disabled}
		/>
		
		<p class="mt-1 text-xs text-neutral-500 dark:text-neutral-400">
		  {t('auctions.auto_bidding_info')}
		</p>
	  </div>
	  
	  <!-- Max Bid Amount (for Auto-Bid) -->
	  {#if isAutoBid}
		<div class="p-4 bg-neutral-50 dark:bg-neutral-700/30 rounded-lg border border-neutral-200 dark:border-neutral-700">
		  <TextField
			label={t('auctions.max_bid_amount')}
			type="number"
			min={bidAmount + auction.min_bid_increment}
			step={auction.min_bid_increment}
			bind:value={maxBidAmount}
			error={formErrors.maxBidAmount}
			prefix="SAR"
			required={isAutoBid}
			disabled={loading || disabled}
		  />
		  
		  <p class="mt-1 text-xs text-neutral-500 dark:text-neutral-400">
			{t('auctions.max_bid_info')}
		  </p>
		</div>
	  {/if}
	  
	  <!-- Bid confirmation message -->
	  <div class="bg-warning-50 dark:bg-warning-900/20 border border-warning-200 dark:border-warning-800/30 rounded-lg p-3">
		<p class="text-sm text-warning-700 dark:text-warning-400">
		  {t('auctions.bid_confirmation')}
		</p>
	  </div>
	  
	  <!-- Submit Button -->
	  <div>
		<Button
		  type="submit"
		  variant="primary"
		  fullWidth={true}
		  loading={loading}
		  disabled={loading || disabled || bidAmount < minBidAmount || (isAutoBid && maxBidAmount <= bidAmount)}
		>
		  {t('auctions.place_bid')}
		</Button>
	  </div>
	  
	  <!-- Bid Terms -->
	  <p class="text-xs text-neutral-500 dark:text-neutral-400 text-center">
		{t('auctions.bid_terms')}
	  </p>
	</form>
  </div>