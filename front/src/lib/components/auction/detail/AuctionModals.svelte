<script>
    import { t } from '$lib/i18n';
    import Modal from '$lib/components/ui/Modal.svelte';
    import Button from '$lib/components/ui/Button.svelte';
    import Alert from '$lib/components/ui/Alert.svelte';
    import FormField from '$lib/components/ui/FormField.svelte';
    
    export let auction;
    export let bidAmount;
    export let maxBidAmount;
    export let bidNotes;
    export let enableAutoBidding;
    export let placingBid;
    export let bidError;
    export let minimumBidAmount;
    export let extensionHours;
    export let extensionReason;
    
    export let showBidModal;
    export let showLoginModal;
    export let showRegisterModal;
    export let showExtendModal;
    
    export let onBidSubmission;
    export let onAuctionRegistration;
    export let onExtendAuction;
    
    function formatCurrency(amount) {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
      }).format(amount);
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
  </script>
  
  <!-- Enhanced Bid Modal with Fixed Styling -->
  <Modal
    bind:show={showBidModal}
    title={$t('auction.placeBid')}
    maxWidth="lg"
  >
    <form on:submit|preventDefault={onBidSubmission} class="space-y-4 p-4">
      {#if bidError}
        <Alert type="error" message={bidError} />
      {/if}
      
      <!-- Current Auction Status -->
      <div class="bg-gradient-to-r from-primary-50 to-blue-50 dark:from-primary-900/20 dark:to-blue-900/20 p-4 rounded-lg border border-primary-200 dark:border-primary-800">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-3 text-center">
          <div>
            <div class="text-sm font-medium text-primary-700 dark:text-primary-300 mb-1">Current Bid</div>
            <div class="text-xl font-bold text-primary-600 dark:text-primary-400">
              {formatCurrency(auction?.current_bid || auction?.starting_bid)}
            </div>
          </div>
          <div>
            <div class="text-sm font-medium text-primary-700 dark:text-primary-300 mb-1">Minimum Bid</div>
            <div class="text-lg font-bold text-primary-800 dark:text-primary-200">
              {formatCurrency(minimumBidAmount)}
            </div>
          </div>
          <div>
            <div class="text-sm font-medium text-primary-700 dark:text-primary-300 mb-1">Total Bids</div>
            <div class="text-lg font-bold text-primary-800 dark:text-primary-200">
              {auction?.bid_count || 0}
            </div>
          </div>
        </div>
      </div>
      
      <!-- Bid Amount Input -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <FormField
          type="number"
          id="bid_amount"
          label={$t('auction.bidAmount')}
          bind:value={bidAmount}
          min={minimumBidAmount}
          step="1"
          required={true}
          class="text-lg font-semibold"
        />
        
        <FormField
          type="number"
          id="max_bid_amount"
          label="Maximum Auto-Bid (Optional)"
          bind:value={maxBidAmount}
          step="1"
          helpText="Set a maximum amount for automatic bidding"
        />
      </div>
      
      <!-- Advanced Options -->
      <div class="border-t border-gray-200 dark:border-gray-700 pt-4">
        <h4 class="text-base font-semibold text-gray-900 dark:text-white mb-3">
          Advanced Options
        </h4>
        
        <div class="space-y-3">
          <label class="flex items-center">
            <input
              type="checkbox"
              bind:checked={enableAutoBidding}
              class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            />
            <span class="ml-2 text-sm font-medium text-gray-700 dark:text-gray-300">
              Enable Auto-Bidding
            </span>
          </label>
          <p class="text-xs text-gray-500 dark:text-gray-400 ml-6">
            Automatically place bids when you're outbid, up to your maximum amount
          </p>
          
          <FormField
            type="textarea"
            id="bid_notes"
            label="Notes (Optional)"
            bind:value={bidNotes}
            rows={2}
            helpText="Add any notes with your bid"
          />
        </div>
      </div>
      
      <!-- Bid Disclaimer -->
      <div class="bg-warning-50 dark:bg-warning-900/20 p-3 rounded-lg border border-warning-200 dark:border-warning-800">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-4 w-4 text-warning-500" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-2">
            <h3 class="text-sm font-semibold text-warning-800 dark:text-warning-200">
              Bid Agreement
            </h3>
            <div class="mt-1 text-sm text-warning-700 dark:text-warning-300">
              <p>{$t('auction.bidDisclaimer')}</p>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Action Buttons -->
      <div class="flex justify-end space-x-2 pt-4 border-t border-gray-200 dark:border-gray-700">
        <Button
          variant="outline"
          type="button"
          on:click={() => showBidModal = false}
          disabled={placingBid}
        >
          {$t('common.cancel')}
        </Button>
        
        <Button
          variant="primary"
          type="submit"
          loading={placingBid}
          disabled={placingBid || !bidAmount || parseFloat(bidAmount) < minimumBidAmount}
          class="px-6"
        >
          {#if placingBid}
            <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          {:else}
            <svg class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          {/if}
          {enableAutoBidding ? 'Place Auto-Bid' : $t('auction.confirmBid')}
        </Button>
      </div>
    </form>
  </Modal>
  
  <!-- Login Modal -->
  <Modal
    bind:show={showLoginModal}
    title={$t('auction.loginRequired')}
    maxWidth="sm"
  >
    <div class="text-center py-4 p-4">
      <div class="w-12 h-12 bg-warning-100 dark:bg-warning-900 rounded-full flex items-center justify-center mx-auto mb-3">
        <svg class="w-6 h-6 text-warning-600 dark:text-warning-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zM3 20a6 6 0 0112 0v1H3v-1z" />
        </svg>
      </div>
      
      <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-2">
        Sign In Required
      </h3>
      <p class="mb-4 text-gray-600 dark:text-gray-400 text-sm">
        {$t('auction.loginRequiredMessage')}
      </p>
      
      <div class="flex flex-col sm:flex-row justify-center gap-2">
        <Button
          variant="outline"
          on:click={() => showLoginModal = false}
        >
          {$t('common.cancel')}
        </Button>
        
        <Button
          variant="primary"
          href={`/login?redirect=/auctions/${auction?.slug}`}
        >
          {$t('nav.login')}
        </Button>
      </div>
    </div>
  </Modal>
  
  <!-- Registration Modal -->
  <Modal
    bind:show={showRegisterModal}
    title="Register for Auction"
    maxWidth="md"
  >
    <div class="p-4">
      <div class="bg-primary-50 dark:bg-primary-900/20 p-3 rounded-lg mb-4">
        <h4 class="text-base font-bold text-primary-900 dark:text-primary-100 mb-1">
          Auction Registration Required
        </h4>
        <p class="text-sm text-primary-700 dark:text-primary-300">
          You must register for this auction before you can place bids.
        </p>
      </div>
      
      <div class="space-y-4">
        <div class="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
          <h5 class="font-semibold text-gray-900 dark:text-white mb-3">Registration Requirements:</h5>
          <ul class="space-y-2">
            <li class="flex items-center text-sm text-gray-600 dark:text-gray-400">
              <svg class="h-4 w-4 text-success-500 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
              </svg>
              <span>Verified email address</span>
            </li>
            <li class="flex items-center text-sm text-gray-600 dark:text-gray-400">
              <svg class="h-4 w-4 text-success-500 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
              </svg>
              <span>Account in good standing</span>
            </li>
            <li class="flex items-center text-sm text-gray-600 dark:text-gray-400">
                <svg class="h-4 w-4 text-success-500 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                  </svg>
                  <span>Agreement to terms and conditions</span>
                </li>
              </ul>
            </div>
            
            <div class="bg-warning-50 dark:bg-warning-900/20 p-3 rounded-lg border border-warning-200 dark:border-warning-800">
              <div class="flex">
                <div class="flex-shrink-0">
                  <svg class="h-4 w-4 text-warning-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                  </svg>
                </div>
                <div class="ml-2">
                  <p class="text-sm text-warning-800 dark:text-warning-200">
                    <strong>Note:</strong> Registration is free and takes only a moment. Once registered, you'll be able to place bids throughout the auction period.
                  </p>
                </div>
              </div>
            </div>
          </div>
          
          <div class="flex justify-end space-x-2 mt-6">
            <Button
              variant="outline"
              on:click={() => showRegisterModal = false}
            >
              Cancel
            </Button>
            
            <Button
              variant="primary"
              on:click={onAuctionRegistration}
              class="px-6"
            >
              <svg class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Register for Auction
            </Button>
          </div>
        </div>
      </Modal>
      
      <!-- Extend Auction Modal -->
      <Modal
        bind:show={showExtendModal}
        title="Extend Auction"
        maxWidth="md"
      >
        <form on:submit|preventDefault={onExtendAuction} class="space-y-4 p-4">
          <div class="bg-primary-50 dark:bg-primary-900/20 p-4 rounded-lg">
            <h4 class="text-base font-bold text-primary-900 dark:text-primary-100 mb-1">
              Extend Auction Time
            </h4>
            <p class="text-sm text-primary-700 dark:text-primary-300">
              Current end time: <span class="font-semibold">{formatDateTime(auction?.end_date)}</span>
            </p>
          </div>
          
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <FormField
              type="number"
              id="extension_hours"
              label="Extension Hours"
              bind:value={extensionHours}
              min={1}
              max={168}
              step={1}
              required={true}
              helpText="Number of hours to extend (max 7 days)"
            />
            
            <div class="flex items-center justify-center bg-gray-50 dark:bg-gray-700 rounded-lg p-3">
              <div class="text-center">
                <div class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">New End Time</div>
                <div class="text-base font-bold text-gray-900 dark:text-white">
                  {#if extensionHours && auction?.end_date}
                    {formatDateTime(new Date(new Date(auction.end_date).getTime() + (extensionHours * 60 * 60 * 1000)).toISOString())}
                  {:else}
                    --
                  {/if}
                </div>
              </div>
            </div>
          </div>
          
          <FormField
            type="textarea"
            id="extension_reason"
            label="Reason for Extension (Optional)"
            bind:value={extensionReason}
            rows={3}
            helpText="Optional reason for extending the auction"
          />
          
          <div class="bg-warning-50 dark:bg-warning-900/20 p-3 rounded-lg border border-warning-200 dark:border-warning-800">
            <div class="flex">
              <div class="flex-shrink-0">
                <svg class="h-4 w-4 text-warning-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                </svg>
              </div>
              <div class="ml-2">
                <h3 class="text-sm font-semibold text-warning-800 dark:text-warning-200">
                  Extension Notice
                </h3>
                <div class="mt-1 text-sm text-warning-700 dark:text-warning-300">
                  <p>All registered bidders will be notified of the auction extension. This action cannot be undone.</p>
                </div>
              </div>
            </div>
          </div>
          
          <div class="flex justify-end space-x-2 pt-4 border-t border-gray-200 dark:border-gray-700">
            <Button
              variant="outline"
              type="button"
              on:click={() => showExtendModal = false}
            >
              Cancel
            </Button>
            
            <Button
              variant="primary"
              type="submit"
              class="px-6"
            >
              <svg class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Extend Auction
            </Button>
          </div>
        </form>
      </Modal>