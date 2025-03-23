<!-- src/routes/auctions/[id]/edit/+page.svelte -->
<script>
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { t, isRTL } from '$lib/i18n';
  import { goto } from '$app/navigation';
  import { authStore } from '$lib/stores/auth';
  import { auctionActions, currentAuction, loading, errors } from '$lib/stores/auction';
  import AuctionForm from '$lib/components/auctions/AuctionForm.svelte';
  import Breadcrumb from '$lib/components/ui/Breadcrumb.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Alert from '$lib/components/ui/Alert.svelte';
  import Spinner from '$lib/components/ui/Spinner.svelte';
  import DeleteAuctionModal from '$lib/components/auctions/DeleteAuctionModal.svelte';
  import { toast } from '$lib/stores/toast';
  
  // Get auction ID from page params
  $: auctionId = $page.params.id;
  
  // Component state
  let isAuthorized = false;
  let isAuthorizing = true;
  let permissionError = null;
  let showDeleteModal = false;
  
  // Load auction data
  async function loadAuctionData() {
      try {
          isAuthorizing = true;
          const result = await auctionActions.loadAuctionDetail(auctionId, false, true, true);
          
          if (!result.success) {
              permissionError = result.error || t('auctions.load_error');
              return;
          }
          
          // Check if user has permission to edit this auction
          await checkPermissions();
      } catch (error) {
          console.error('Error loading auction:', error);
          permissionError = error.message || t('general.error_occurred');
      } finally {
          isAuthorizing = false;
      }
  }
  
  // Check user permissions
  async function checkPermissions() {
      try {
          if (!$currentAuction) return;
          
          // Check if user is authenticated
          if (!$authStore.isAuthenticated) {
              // Store current path for redirect after login
              if (browser) {
                  localStorage.setItem('redirectAfterLogin', window.location.pathname);
              }
              
              // Redirect to login
              goto('/auth/login');
              return;
          }
          
          // Check if user is the creator/owner of this auction or has admin permissions
          const isCreator = $authStore.user?.id === $currentAuction?.created_by?.id;
          const isPropertyOwner = $authStore.user?.id === $currentAuction?.related_property?.owner?.id;
          const isAdmin = $authStore.user?.is_admin || $authStore.user?.is_staff;
          const hasPermission = isCreator || isPropertyOwner || isAdmin || 
                              $authStore.user?.roles?.includes('admin') || 
                              $authStore.user?.roles?.includes('staff');
          
          if (hasPermission) {
              isAuthorized = true;
          } else {
              permissionError = t('auctions.not_authorized_to_edit');
              isAuthorized = false;
          }
      } catch (error) {
          console.error('Error checking permissions:', error);
          permissionError = t('general.error_occurred');
          isAuthorized = false;
      }
  }
  
  // Handle success
  function handleSuccess(event) {
      const auction = event.detail?.auction;
      
      if (auction?.id) {
          // Show success toast
          toast.success(t('auctions.update_success'));
          
          // Navigate to auction detail page after a brief delay
          setTimeout(() => {
              goto(`/auctions/${auction.id}`);
          }, 800);
      }
  }
  
  // Handle cancellation
  function handleCancel() {
      // Navigate back to auction detail
      goto(`/auctions/${auctionId}`);
  }
  
  // Open delete modal
  function openDeleteModal() {
      showDeleteModal = true;
  }
  
  // Handle successful deletion
  function handleDeleteSuccess() {
      // Navigate to auctions list
      toast.success(t('auctions.delete_success'));
      setTimeout(() => {
          goto('/auctions');
      }, 800);
  }
  
  // Initialize component
  onMount(async () => {
      // Reset any previous errors
      auctionActions.resetErrors();
      
      // Load auction data
      await loadAuctionData();
  });
</script>

<svelte:head>
  <title>{$currentAuction ? t('auctions.edit') + ': ' + $currentAuction.title : t('auctions.edit')} | {t('general.app_name')}</title>
  <meta name="description" content={t('auctions.edit_meta_description')} />
</svelte:head>

<div class="container mx-auto px-4 py-8">
  <!-- Breadcrumb -->
  <div class="mb-6">
      <Breadcrumb
          items={[
              { label: t('navigation.home'), href: '/' },
              { label: t('auctions.title'), href: '/auctions' },
              $currentAuction ? 
                  { label: $currentAuction.title, href: `/auctions/${auctionId}` } :
                  { label: t('auctions.auction_details'), href: `/auctions/${auctionId}` },
              { label: t('auctions.edit'), href: `/auctions/${auctionId}/edit`, active: true }
          ]}
      />
  </div>

  <!-- Page header -->
  <div class="mb-8 flex flex-col md:flex-row md:items-end md:justify-between gap-4">
      <div>
          <h1 class="text-3xl font-bold text-neutral-900 dark:text-neutral-100">
              {t('auctions.edit')}
          </h1>
          <p class="mt-2 text-neutral-600 dark:text-neutral-400">
              {$currentAuction?.title || t('auctions.edit_description')}
          </p>
      </div>
      
      {#if isAuthorized && $currentAuction}
          <Button 
              variant="error" 
              size="md"
              on:click={openDeleteModal}
              class="flex items-center"
          >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 {isRTL() ? 'ml-1.5' : 'mr-1.5'}" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
              </svg>
              {t('auctions.delete_auction')}
          </Button>
      {/if}
  </div>
  
  <!-- Authorization check -->
  {#if isAuthorizing || $loading.currentAuctionLoading}
      <div class="flex justify-center py-12">
          <Spinner size="lg" />
      </div>
  {:else if permissionError || $errors.detailError}
      <Alert 
          type="error" 
          title={t('general.error')}
          message={permissionError || $errors.detailError}
          class="mb-6"
      />
  {:else if isAuthorized && $currentAuction}
      <!-- Form errors -->
      {#if $errors.updateError}
          <Alert 
              type="error" 
              message={$errors.updateError}
              class="mb-6"
              dismissible={true}
          />
      {/if}
      
      <!-- Auction Form -->
      <div class="bg-white dark:bg-neutral-800 rounded-xl border border-neutral-200 dark:border-neutral-700 shadow-sm">
          <AuctionForm 
              mode="edit"
              auctionData={$currentAuction}
              submitText={t('auctions.update')}
              on:success={handleSuccess}
              on:cancel={handleCancel}
          />
      </div>
  {/if}
  
  <!-- Delete Auction Modal -->
  <DeleteAuctionModal
      auction={$currentAuction}
      bind:isOpen={showDeleteModal}
      on:success={handleDeleteSuccess}
  />
</div>