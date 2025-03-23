<!-- src/routes/auctions/create/+page.svelte -->
<script>
  import { onMount } from 'svelte';
  import { t } from '$lib/i18n';
  import { goto } from '$app/navigation';
  import { authStore } from '$lib/stores/auth';
  import { auctionActions, loading, errors } from '$lib/stores/auction';
  import AuctionForm from '$lib/components/auctions/AuctionForm.svelte';
  import Breadcrumb from '$lib/components/ui/Breadcrumb.svelte';
  import Alert from '$lib/components/ui/Alert.svelte';
  import Spinner from '$lib/components/ui/Spinner.svelte';
  import { toast } from '$lib/stores/toast';
  
  // Component state
  let isAuthorized = false;
  let isAuthorizing = true;
  let permissionError = null;
  
  // Handle form success
  function handleSuccess(event) {
      const auction = event.detail?.auction;
      
      if (auction?.id) {
          // Show success toast
          toast.success(t('auctions.create_success'));
          
          // Navigate to auction detail page after a brief delay
          setTimeout(() => {
              goto(`/auctions/${auction.id}`);
          }, 800);
      }
  }
  
  // Handle cancellation
  function handleCancel() {
      // Navigate back to auctions list
      goto('/auctions');
  }
  
  // Check user permissions
  async function checkPermissions() {
      isAuthorizing = true;
      
      try {
          // Wait for auth store to initialize
          if (!$authStore.initialized) {
              await new Promise(resolve => {
                  const unsubscribe = authStore.subscribe(state => {
                      if (state.initialized) {
                          unsubscribe();
                          resolve();
                      }
                  });
              });
          }
          
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
          
          // Check user roles/permissions
          const hasRequiredRole = $authStore.user?.roles?.some(role => 
              ['admin', 'staff', 'agent', 'seller'].includes(role)
          ) || $authStore.user?.is_admin || $authStore.user?.is_staff;
          
          if (hasRequiredRole) {
              isAuthorized = true;
          } else {
              permissionError = t('auth.insufficient_permissions');
              isAuthorized = false;
          }
      } catch (error) {
          console.error('Error checking permissions:', error);
          permissionError = t('general.error_occurred');
          isAuthorized = false;
      } finally {
          isAuthorizing = false;
      }
  }
  
  onMount(() => {
      // Check if user has permission to create auctions
      checkPermissions();
      
      // Reset any previous errors
      auctionActions.resetErrors();
  });
</script>

<svelte:head>
  <title>{t('auctions.create')} | {t('general.app_name')}</title>
  <meta name="description" content={t('auctions.create_description')} />
</svelte:head>

<div class="container mx-auto px-4 py-8">
  <!-- Breadcrumb -->
  <div class="mb-6">
      <Breadcrumb
          items={[
              { label: t('navigation.home'), href: '/' },
              { label: t('auctions.title'), href: '/auctions' },
              { label: t('auctions.create'), href: '/auctions/create', active: true }
          ]}
      />
  </div>

  <!-- Page header -->
  <div class="mb-8">
      <h1 class="text-3xl font-bold text-neutral-900 dark:text-neutral-100">
          {t('auctions.create')}
      </h1>
      <p class="mt-2 text-neutral-600 dark:text-neutral-400">
          {t('auctions.create_description')}
      </p>
  </div>
  
  <!-- Authorization check -->
  {#if isAuthorizing}
      <div class="flex justify-center py-12">
          <Spinner size="lg" />
      </div>
  {:else if permissionError}
      <Alert 
          type="error" 
          title={t('auth.access_denied')}
          message={permissionError}
          class="mb-6"
      />
  {:else if isAuthorized}
      <!-- Display any form errors -->
      {#if $errors.createError}
          <Alert 
              type="error" 
              message={$errors.createError}
              class="mb-6"
              dismissible={true}
          />
      {/if}
      
      <!-- Create Auction Form -->
      <div class="bg-white dark:bg-neutral-800 rounded-xl border border-neutral-200 dark:border-neutral-700 shadow-sm">
          <AuctionForm 
              mode="create"
              submitText={t('auctions.create')}
              on:success={handleSuccess}
              on:cancel={handleCancel}
          />
      </div>
  {/if}
</div>