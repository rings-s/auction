<!-- src/routes/auctions/components/PlaceBidForm.svelte -->
<script>
    import { createEventDispatcher } from 'svelte';
    import { t } from '$lib/i18n';
    import { formatCurrency } from '$lib/i18n';
    import { NumericInput, Switch, Alert } from '$lib/components/ui';
    import { Button } from '$lib/components/ui';
    import { loading, errors } from '$lib/stores/auction';
    
    // Props
    export let auctionId;
    export let currentBid = 0;
    export let minBidIncrement = 100;
    
    // Component state
    let bidAmount = currentBid + minBidIncrement;
    let isAutoBid = false;
    let maxBidAmount = bidAmount + minBidIncrement * 5;
    let formErrors = {};
    
    // Event dispatcher
    const dispatch = createEventDispatcher();
    
    // Validation
    function validateForm() {
      const errors = {};
      
      if (!bidAmount || bidAmount <= 0) {
        errors.bidAmount = t('auctions.bid_amount_required');
      }
      
      if (bidAmount <= currentBid) {
        errors.bidAmount = t('auctions.bid_higher_than_current');
      }
      
      if (bidAmount < currentBid + minBidIncrement) {
        errors.bidAmount = t('auctions.bid_minimum_increment', {
          amount: formatCurrency(currentBid + minBidIncrement)
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
    
    // Handle form submission
    function handleSubmit() {
      if (!validateForm()) {
        return;
      }
      
      // Dispatch submit event with bid data
      dispatch('submit', {
        amount: bidAmount,
        isAutoBid,
        maxBidAmount: isAutoBid ? maxBidAmount : null
      });
    }
    
    // Handle form cancellation
    function handleCancel() {
      dispatch('cancel');
    }
  </script>
  
  <div class="place-bid-form">
    <!-- Display errors from auction store if any -->
    {#if $errors.bidError}
      <Alert type="error" message={$errors.bidError} class="mb-4" />
    {/if}
    
    <form on:submit|preventDefault={handleSubmit}>
      <!-- Bid amount -->
      <div class="mb-4">
        <NumericInput
          label={t('auctions.bid_amount')}
          bind:value={bidAmount}
          error={formErrors.bidAmount}
          min={currentBid + minBidIncrement}
          step={minBidIncrement}
          currency={true}
          required
        />
        <p class="mt-1 text-sm text-gray-500">
          {t('auctions.current_bid')}: {formatCurrency(currentBid)}
        </p>
        <p class="text-sm text-gray-500">
          {t('auctions.min_increment')}: {formatCurrency(minBidIncrement)}
        </p>
      </div>
      
      <!-- Auto bid option -->
      <div class="mb-4">
        <Switch
          label={t('auctions.enable_auto_bidding')}
          bind:checked={isAutoBid}
        />
        
        <p class="mt-1 text-sm text-gray-500">
          {t('auctions.auto_bidding_info')}
        </p>
      </div>
      
      <!-- Max bid amount (for auto bidding) -->
      {#if isAutoBid}
        <div class="mb-4 ml-6 bg-gray-50 p-4 rounded-lg border border-gray-200">
          <NumericInput
            label={t('auctions.max_bid_amount')}
            bind:value={maxBidAmount}
            error={formErrors.maxBidAmount}
            min={bidAmount + minBidIncrement}
            step={minBidIncrement}
            currency={true}
            required={isAutoBid}
          />
          <p class="mt-1 text-sm text-gray-500">
            {t('auctions.max_bid_info')}
          </p>
        </div>
      {/if}
      
      <!-- Bid confirmation message -->
      <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
        <p class="text-sm text-yellow-800">
          {t('auctions.bid_confirmation')}
        </p>
      </div>
      
      <!-- Form actions -->
      <div class="flex justify-end space-x-4">
        <Button 
          type="button" 
          variant="outline" 
          on:click={handleCancel}
          disabled={$loading.placingBid}
        >
          {t('general.cancel')}
        </Button>
        
        <Button 
          type="submit" 
          variant="primary" 
          disabled={$loading.placingBid}
          loading={$loading.placingBid}
        >
          {t('auctions.place_bid')}
        </Button>
      </div>
    </form>
  </div>