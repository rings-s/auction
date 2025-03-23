<!-- src/routes/auctions/create/+page.svelte -->
<script>
    import { onMount } from 'svelte';
    import { t } from '$lib/i18n';
    import { goto } from '$app/navigation';
    import { authStore } from '$lib/stores/auth';
    import AuctionForm from '$lib/components/auctions/AuctionForm.svelte';
    import { Alert } from '$lib/components/ui';
    
    // Component state
    let isAuthorized = false;
    let alertType = 'error';
    let alertMessage = '';
    let showAlert = false;
    
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
      // Navigate back to auctions list
      goto('/auctions');
    }
    
    // Initialize component
    onMount(() => {
      // Check if user is authenticated and has required role
      if ($authStore.isAuthenticated) {
        const roles = $authStore.user?.roles || [];
        isAuthorized = $authStore.user.is_admin || $authStore.user.is_staff || roles.includes('agent');
        
        if (!isAuthorized) {
          alertType = 'error';
          alertMessage = t('auth.insufficient_permissions');
          showAlert = true;
        }
      } else {
        // Redirect to login
        const returnUrl = encodeURIComponent(window.location.pathname);
        goto(`/auth/login?return_url=${returnUrl}`);
      }
    });
  </script>
  
  <svelte:head>
    <title>{t('auctions.create')} | {t('site.name')}</title>
    <meta name="description" content={t('auctions.create_meta_description')} />
  </svelte:head>
  
  <div class="auction-create-page">
    <div class="mb-6">
      <h1 class="text-2xl md:text-3xl font-bold">{t('auctions.create')}</h1>
      <p class="text-gray-600 mt-1">
        {t('auctions.create_description')}
      </p>
    </div>
    
    {#if showAlert}
      <Alert 
        type={alertType} 
        message={alertMessage} 
        class="mb-6"
      />
    {/if}
    
    {#if isAuthorized}
      <div class="bg-white rounded-lg border shadow-sm p-6">
        <AuctionForm 
          mode="create"
          submitText={t('auctions.create')}
          on:success={handleSuccess}
          on:cancel={handleCancel}
        />
      </div>
    {/if}
  </div>