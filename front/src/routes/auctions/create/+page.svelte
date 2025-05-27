<!-- src/routes/auctions/create/+page.svelte -->
<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { t } from '$lib/i18n';
  import { user } from '$lib/stores/user';
  import { createAuction } from '$lib/api/auction';
  import AuctionForm from '$lib/components/auction/AuctionForm.svelte';
  import AuctionPreview from '$lib/components/auction/AuctionPreview.svelte';
  import Breadcrumb from '$lib/components/ui/Breadcrumb.svelte';
  import Alert from '$lib/components/ui/Alert.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import LoadingSkeleton from '$lib/components/ui/LoadingSkeleton.svelte';
  
  let auctionForm;
  let isPreview = false;
  let loading = true;
  let submitting = false;
  let error = '';
  let success = '';
  let previewData = null;
  
  // Define breadcrumb items
  const breadcrumbItems = [
    { label: $t('nav.home'), href: '/' },
    { label: $t('nav.auctions'), href: '/auctions' },
    { label: $t('auction.createAuction'), href: '/auctions/create', active: true }
  ];
  
  onMount(async () => {
    // Check if user is logged in
    if (!$user) {
      goto('/login?redirect=/auctions/create');
      return;
    }
    
    // Check if user has permissions (property owner, appraiser, or admin)
    if (!($user.is_staff || $user.is_superuser || $user.role === 'owner' || $user.role === 'appraiser')) {
      error = $t('property.unauthorizedMessage');
    }
    
    loading = false;
  });
  
  async function handleSubmit() {
    try {
      submitting = true;
      error = '';
      success = '';
      
      // Validate the form
      const validation = auctionForm.validateForm();
      if (!validation.valid) {
        error = validation.error;
        // Switch to the tab with the error if tab is specified
        if (validation.tab && auctionForm) {
          auctionForm.activeTab = validation.tab;
        }
        return;
      }
      
      // Get prepared data from the form component
      const preparedAuction = auctionForm.prepareDataForSubmission();
      
      // Create auction
      const response = await createAuction(preparedAuction);
      
      if (response) {
        success = $t('auction.createSuccess');
        
        // Show success message and redirect after a delay
        setTimeout(() => {
          // Use slug if available, otherwise use ID
          const redirectPath = response.slug ? 
            `/auctions/${response.slug}` : 
            `/auctions/${response.id}`;
          goto(redirectPath);
        }, 1500);
      } else {
        throw new Error('Invalid response from server');
      }
    } catch (err) {
      console.error('Error creating auction:', err);
      error = err.message || $t('auction.createFailed');
    } finally {
      submitting = false;
    }
  }
  
  function togglePreview() {
    if (!isPreview) {
      // Get form data for preview
      const validation = auctionForm.validateForm();
      if (!validation.valid) {
        error = validation.error;
        return;
      }
      
      // Prepare data for preview
      previewData = auctionForm.prepareDataForSubmission();
    }
    
    isPreview = !isPreview;
  }
</script>

<svelte:head>
  <title>{$t('auction.createAuction')} | Real Estate Platform</title>
  <meta name="description" content={$t('auction.createAuctionDesc')} />
</svelte:head>

<div class="min-h-screen bg-gray-50 dark:bg-gray-900 py-8 px-4 sm:px-6 lg:px-8">
  <div class="max-w-7xl mx-auto space-y-8">
    <!-- Breadcrumb Navigation -->
    <Breadcrumb items={breadcrumbItems} />
    
    <!-- Page Header -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
      <div class="md:flex md:items-center md:justify-between">
        <div class="flex-1 min-w-0">
          <h1 class="text-2xl font-bold leading-7 text-gray-900 dark:text-white sm:text-3xl">
            {$t('auction.createAuction')}
          </h1>
          <p class="mt-2 text-base text-gray-500 dark:text-gray-400 max-w-3xl">
            {$t('auction.createAuctionDesc')}
          </p>
        </div>
        
        <!-- Preview Toggle Button -->
        {#if !loading}
          <div class="mt-5 flex lg:mt-0 lg:ml-4">
            <Button
              variant={isPreview ? 'primary' : 'outline'}
              onClick={togglePreview}
              disabled={submitting}
              class="flex items-center"
            >
              <svg class="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                {#if isPreview}
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                {:else}
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                {/if}
              </svg>
              {isPreview ? $t('common.edit') : $t('auction.preview')}
            </Button>
          </div>
        {/if}
      </div>
    </div>
    
    {#if error}
      <Alert 
        type="error" 
        title={$t('error.title')}
        message={error}
        dismissible={true}
      />
    {/if}
    
    {#if success}
      <Alert 
        type="success" 
        title={$t('auction.createSuccess')}
        message={$t('common.loading') + '...'}
      />
    {/if}
    
    {#if loading}
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
        <LoadingSkeleton type="auctionForm" />
      </div>
    {:else if isPreview && previewData}
      <div class="border border-primary-200 dark:border-primary-800 rounded-lg overflow-hidden bg-white dark:bg-gray-800 shadow-lg">
        <div class="bg-primary-50 dark:bg-primary-900/20 px-6 py-4 border-b border-primary-200 dark:border-primary-800">
          <div class="flex items-center text-primary-700 dark:text-primary-300">
            <svg class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
            <span class="font-medium">{$t('common.preview')}</span>
          </div>
        </div>
        
        <AuctionPreview auction={previewData} />
      </div>
      
      <div class="flex justify-end space-x-4">
        <Button
          variant="outline"
          onClick={togglePreview}
          aria-label={$t('common.edit')}
        >
          <svg class="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 17l-5-5m0 0l5-5m-5 5h12" />
          </svg>
          {$t('common.edit')}
        </Button>
        
        <Button
          variant="primary"
          onClick={handleSubmit}
          loading={submitting}
          disabled={submitting}
          aria-label={$t('auction.create')}
        >
          <svg class="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
          {$t('auction.create')}
        </Button>
      </div>
    {:else}
      <div class="space-y-8">
        <AuctionForm bind:this={auctionForm} />
        
        <!-- Submit Buttons -->
        <div class="flex justify-end space-x-4">
          <Button
            variant="outline"
            onClick={() => goto('/auctions')}
            disabled={submitting}
            aria-label={$t('common.cancel')}
          >
            <svg class="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
            {$t('common.cancel')}
          </Button>
          
          <Button
            variant="secondary"
            onClick={togglePreview}
            disabled={submitting}
            aria-label={$t('auction.preview')}
            class="min-w-[150px]"
          >
            <svg class="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
            {$t('auction.preview')}
          </Button>
          
          <Button
            variant="primary"
            onClick={handleSubmit}
            loading={submitting}
            disabled={submitting}
            aria-label={$t('auction.create')}
            class="min-w-[180px]"
          >
            <svg class="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            {$t('auction.create')}
          </Button>
        </div>
      </div>
    {/if}
  </div>
</div>

<style>
  /* Enhanced animations for better UX */
  button {
    transition: all 0.2s ease-in-out;
  }
  
  button:hover {
    transform: translateY(-1px);
  }
  
  button:active {
    transform: translateY(1px);
  }
</style>