<!-- src/routes/auctions/[id]/edit/+page.svelte -->
<script>
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { goto } from '$app/navigation';
    import { t } from '$lib/i18n/i18n';
    import { user } from '$lib/stores/user';
    import { fetchAuctionById, updateAuction, deleteAuction } from '$lib/api/auction';
    import Breadcrumb from '$lib/components/ui/Breadcrumb.svelte';
    import Button from '$lib/components/ui/Button.svelte';
    import Alert from '$lib/components/ui/Alert.svelte';
    import Modal from '$lib/components/ui/Modal.svelte';
    import LoadingSkeleton from '$lib/components/ui/LoadingSkeleton.svelte';
    
    // Import shared auction form component
    import AuctionForm from '$lib/components/auction/AuctionForm.svelte';
    
    let auction = null;
    let loading = true;
    let saving = false;
    let error = '';
    let success = '';
    let auctionForm;
    let showDeleteModal = false;
    let deleteLoading = false;
    
    $: auctionId = $page.params.id;
    $: breadcrumbItems = [
      { label: $t('nav.home'), href: '/' },
      { label: $t('nav.auctions'), href: '/auctions' },
      { label: auction?.title || '', href: `/auctions/${auction?.slug}` },
      { label: $t('auction.edit'), href: `/auctions/${auctionId}/edit`, active: true }
    ];
    
    onMount(async () => {
      // Check if user is logged in
      if (!$user) {
        goto('/login?redirect=/auctions/' + auctionId + '/edit');
        return;
      }
      
      await loadAuction();
    });
    
    async function loadAuction() {
      loading = true;
      error = '';
      
      try {
        // Fetch auction details
        const auctionData = await fetchAuctionById(auctionId);
        auction = auctionData;
      } catch (err) {
        console.error('Error loading auction:', err);
        error = err.message || $t('error.fetchFailed');
      } finally {
        loading = false;
      }
    }
    
    async function handleUpdate() {
      if (!auctionForm) {
        error = $t('error.formNotReady');
        return;
      }
      
      try {
        saving = true;
        error = '';
        success = '';
        
        // Get form data from the auction form component
        const auctionData = auctionForm.prepareDataForSubmission();
        
        // Update auction
        const updatedAuction = await updateAuction(auctionId, auctionData);
        
        if (updatedAuction) {
          success = $t('auction.updateSuccess');
          auction = updatedAuction;
          
          // Redirect after a short delay
          setTimeout(() => {
            goto(`/auctions/${updatedAuction.slug}`);
          }, 2000);
        }
      } catch (err) {
        console.error('Error updating auction:', err);
        error = err.message || $t('auction.updateFailed');
      } finally {
        saving = false;
      }
    }
    
    async function handleDelete() {
      try {
        deleteLoading = true;
        
        // Delete auction
        await deleteAuction(auctionId);
        
        // Close modal
        showDeleteModal = false;
        
        // Redirect to auctions list
        goto('/auctions?deleted=true');
      } catch (err) {
        console.error('Error deleting auction:', err);
        error = err.message || $t('auction.deleteFailed');
        showDeleteModal = false;
      } finally {
        deleteLoading = false;
      }
    }
  </script>
  
  <svelte:head>
    <title>{$t('auction.edit')} {auction?.title || ''} | Real Estate Platform</title>
    <meta name="description" content={$t('auction.editDesc')} />
  </svelte:head>
  
  <div class="bg-gray-50 dark:bg-gray-900 min-h-screen py-8 px-4 sm:px-6 lg:px-8">
    <div class="max-w-7xl mx-auto">
      <!-- Breadcrumbs -->
      <Breadcrumb items={breadcrumbItems} class="mb-6" />
      
      <div class="md:flex md:items-center md:justify-between mb-8">
        <div class="flex-1 min-w-0">
          <h1 class="text-2xl font-bold leading-7 text-gray-900 dark:text-white sm:text-3xl sm:truncate">
            {$t('auction.edit')} {auction?.title || ''}
          </h1>
          <p class="mt-1 text-gray-500 dark:text-gray-400">
            {$t('auction.editDesc')}
          </p>
        </div>
        
        <!-- Delete Button -->
        {#if auction && ($user?.id === auction.created_by?.id || $user?.is_admin)}
          <div class="mt-4 md:mt-0 md:ml-4">
            <Button
              variant="danger"
              type="button"
              onClick={() => showDeleteModal = true}
              aria-label={$t('auction.delete')}
            >
              <svg class="h-5 w-5 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
              {$t('auction.delete')}
            </Button>
          </div>
        {/if}
      </div>
  
      {#if success}
        <Alert type="success" title={success} class="mb-8" />
      {/if}
      
      {#if error}
        <Alert type="error" title={error} class="mb-8" />
      {/if}
  
      {#if loading}
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          <LoadingSkeleton type="auctionForm" />
        </div>
      {:else if auction}
        <form on:submit|preventDefault={handleUpdate} class="space-y-8">
          <AuctionForm
            bind:this={auctionForm}
            initialAuction={auction}
            isEditing={true}
          />
          
          <!-- Submit Buttons -->
          <div class="flex justify-between">
            <Button
              variant="outline"
              type="button"
              onClick={() => goto(`/auctions/${auction.slug}`)}
              aria-label={$t('common.cancel')}
            >
              {$t('common.cancel')}
            </Button>
            
            <Button
              variant="primary"
              type="submit"
              loading={saving}
              disabled={saving}
              aria-label={$t('auction.save')}
            >
              {#if saving}
                <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              {/if}
              {$t('auction.save')}
            </Button>
          </div>
        </form>
      {:else}
        <Alert 
          type="error"
          title={$t('auction.notFound')}
          message={$t('auction.notFoundDesc')}
          action={{
            label: $t('auctions.backToAuctions'),
            href: '/auctions'
          }}
        />
      {/if}
      <!-- Delete Confirmation Modal -->
        <Modal
        bind:show={showDeleteModal}
        title={$t('auction.deleteConfirm')}
        maxWidth="md"
        >
        <div class="p-6">
        <div class="flex items-start">
            <div class="flex-shrink-0 text-red-600">
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            </div>
            <div class="ml-3">
            <h3 class="text-lg font-medium text-gray-900 dark:text-white">
                {$t('auction.deleteConfirmTitle')}
            </h3>
            <div class="mt-2">
                <p class="text-sm text-gray-500 dark:text-gray-400">
                {$t('auction.deleteConfirmMessage')}
                </p>
                <p class="mt-2 text-sm font-medium text-gray-900 dark:text-white">
                {auction.title}
                </p>
            </div>
            </div>
        </div>
        
        <div class="mt-6 flex justify-end space-x-3">
            <Button
            variant="outline"
            onClick={() => showDeleteModal = false}
            disabled={deleteLoading}
            aria-label={$t('common.cancel')}
            >
            {$t('common.cancel')}
            </Button>
            <Button
            variant="danger"
            onClick={handleDelete}
            loading={deleteLoading}
            disabled={deleteLoading}
            aria-label={$t('auction.confirmDelete')}
            >
            {$t('auction.confirmDelete')}
            </Button>
        </div>
        </div>
        </Modal>