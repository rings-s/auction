<!-- src/routes/auctions/[id]/edit/+page.svelte -->
<script>
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { t } from '$lib/i18n';
    import { goto } from '$app/navigation';
    import { authStore } from '$lib/stores/auth';
    import { auctionActions, currentAuction, loading, errors } from '$lib/stores/auction';
    import AuctionForm from '../../components/auctions/AuctionForm.svelte';
    import { Alert, Loading } from '$lib/components/ui';
    
    // Get auction ID from page params
    $: auctionId = $page.params.id;
    
    // Component state
    let isAuthorized = false;
    let isLoading = true;
    let alertType = 'error';
    let alertMessage = '';
    let showAlert = false;
    
    // Load auction data
    async function loadAuctionData() {
      try {
        isLoading = true;
        const result = await auctionActions.loadAuctionDetail(auctionId, false, true, true);
        
        if (!result.success) {
          alertType = 'error';
          alertMessage = result.error || t('auctions.load_error');
          showAlert = true;
        } else {
          // Check if user has permission to edit this auction
          const isCreator = $authStore.user?.id === $currentAuction?.created_by?.id;
          const isAdmin = $authStore.user.is_admin || $authStore.user.is_staff;
          
          if (!isCreator && !isAdmin) {
            alertType = 'error';
            alertMessage = t('auctions.not_authorized_to_edit');
            showAlert = true;
            isAuthorized = false;
          } else {
            isAuthorized = true;
          }
        }
      } catch (error) {
        alertType = 'error';
        alertMessage = error.message || t('general.error_occurred');
        showAlert = true;
      } finally {
        isLoading = false;
      }
    }
    
    // Handle success
    function handleSuccess(event) {
      const auctionId = event.detail.auction?.id;
      
      if (auctionId) {
        // Navigate to auction detail page
        goto(`/auctions/${auctionId}`);
      }
    }
    
    // Handle cancellation
    function handleCancel() {
      // Navigate back to auction detail
      goto(`/auctions/${auctionId}`);
    }
    
    // Initialize component
    onMount(async () => {
      // Check if user is authenticated
      if ($authStore.isAuthenticated) {
        await loadAuctionData();
      } else {
        // Redirect to login
        const returnUrl = encodeURIComponent(window.location.pathname);
        goto(`/auth/login?return_url=${returnUrl}`);
      }
    });
  </script>
  
  <svelte:head>
    <title>{$currentAuction ? t('auctions.edit') + ': ' + $currentAuction.title : t('auctions.edit')} | {t('site.name')}</title>
    <meta name="description" content={t('auctions.edit_meta_description')} />
  </svelte:head>
  
  <div class="auction-edit-page">
    <div class="mb-6">
      <h1 class="text-2xl md:text-3xl font-bold">{t('auctions.edit')}</h1>
      <p class="text-gray-600 mt-1">
        {$currentAuction?.title || t('auctions.edit_description')}
      </p>
    </div>
    
    {#if showAlert}
      <Alert 
        type={alertType} 
        message={alertMessage} 
        class="mb-6"
      />
    {/if}
    
    {#if isLoading || $loading.currentAuctionLoading}
      <div class="flex flex-col items-center justify-center p-10">
        <Loading size="large" />
        <p class="mt-4 text-lg">{t('auctions.loading')}</p>
      </div>
    {:else if $errors.detailError}
      <Alert 
        type="error" 
        message={$errors.detailError || t('auctions.load_error')} 
        class="mb-6"
      />
    {:else if isAuthorized && $currentAuction}
      <div class="bg-white rounded-lg border shadow-sm p-6">
        <AuctionForm 
          mode="edit"
          auctionData={$currentAuction}
          submitText={t('auctions.update')}
          on:success={handleSuccess}
          on:cancel={handleCancel}
        />
      </div>
    {/if}
  </div>