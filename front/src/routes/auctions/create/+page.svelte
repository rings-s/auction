<!-- src/routes/auctions/create/+page.svelte -->
<script>
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import { t } from '$lib/i18n/i18n';
    import { user } from '$lib/stores/user';
    import { createAuction } from '$lib/api/auction';
    import AuctionForm from '$lib/components/AuctionForm.svelte';
  
    let auction;
    let activeTab = 'basic';
    let loading = false;
    let error = '';
    let success = '';
  
    onMount(() => {
      // Check if user is logged in
      if (!$user) {
        goto('/login?redirect=/auctions/create');
      }
    });
  
    async function handleSubmit() {
      try {
        loading = true;
        error = '';
        success = '';
  
        // Basic validation
        if (!auction.title) {
          error = $t('auction.titleRequired');
          return;
        }
  
        if (!auction.related_property) {
          error = $t('auction.propertyRequired');
          return;
        }
  
        if (!auction.start_date || !auction.end_date) {
          error = $t('auction.datesRequired');
          return;
        }
  
        if (!auction.starting_bid) {
          error = $t('auction.startingBidRequired');
          return;
        }
  
        // Get prepared data from the form component
        const preparedAuction = auction.prepareDataForSubmission();
  
        // Create auction
        const response = await createAuction(preparedAuction);
        
        if (response && response.id) {
          success = $t('auction.createSuccess');
          
          // Redirect after a short delay
          setTimeout(() => {
            goto(`/auctions/${response.slug}`);
          }, 2000);
        }
      } catch (err) {
        console.error('Error creating auction:', err);
        error = err.message || $t('auction.createFailed');
      } finally {
        loading = false;
      }
    }
  </script>

<svelte:head>
<title>{$t('auction.createAuction')} | Real Estate Platform</title>
</svelte:head>

<div class="bg-gray-50 dark:bg-gray-900 py-8">
<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
<div class="md:flex md:items-center md:justify-between mb-8">
<div class="flex-1 min-w-0">
  <h1 class="text-2xl font-bold leading-7 text-gray-900 dark:text-white sm:text-3xl sm:truncate">
    {$t('auction.createAuction')}
  </h1>
  <p class="mt-1 text-gray-500 dark:text-gray-400">
    {$t('auction.createAuctionDesc')}
  </p>
</div>
</div>

{#if success}
<div class="mb-8 rounded-md bg-green-50 dark:bg-green-900/30 p-4">
  <div class="flex">
    <div class="flex-shrink-0">
      <svg class="h-5 w-5 text-green-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
      </svg>
    </div>
    <div class="ml-3">
      <h3 class="text-sm font-medium text-green-800 dark:text-green-200">
        {success}
      </h3>
    </div>
  </div>
</div>
{/if}

<form on:submit|preventDefault={handleSubmit}>
<div class="space-y-8">
  <!-- Auction Information Form -->
  <AuctionForm bind:this={auction} {activeTab} {error} {loading} />

  <!-- Submit Buttons -->
  <div class="flex justify-end">
    <button
      type="button"
      on:click={() => goto('/auctions')}
      class="bg-white dark:bg-gray-800 py-2 px-4 border border-gray-300 dark:border-gray-700 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
    >
      {$t('auction.cancel')}
    </button>
    <button
      type="submit"
      disabled={loading}
      class="ml-3 inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
    >
      {#if loading}
        <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      {/if}
      {$t('auction.create')}
    </button>
  </div>
</div>
</form>
</div>
</div>