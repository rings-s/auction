<!-- routes/dashboard/properties/[id]/delete/+page.svelte -->
<script>
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import { page } from '$app/stores';
    import { t, language } from '$lib/i18n';
    import { fade, fly } from 'svelte/transition';
    
    import { api } from '$lib/services/api';
    import { toast } from '$lib/stores/toast';
    import { authStore } from '$lib/stores/auth';
    
    // UI Components
    import Button from '$lib/components/ui/Button.svelte';
    import Card from '$lib/components/ui/Card.svelte';
    import Alert from '$lib/components/ui/Alert.svelte';
    import Spinner from '$lib/components/ui/Spinner.svelte';
    import Checkbox from '$lib/components/ui/Checkbox.svelte';
    import Badge from '$lib/components/ui/Badge.svelte';
    
    // State
    let property = null;
    let loading = true;
    let deleting = false;
    let error = null;
    let confirmDelete = false;
    let confirmText = '';
    let constraints = [];
    let canDelete = false;
    
    // Extract property ID from URL
    $: propertyId = $page.params.id;
    
    // Auth state
    $: isAuthenticated = $authStore.isAuthenticated;
    $: currentUser = $authStore.user;
    
    // Check for RTL layout
    $: isRTL = $language === 'ar';
    
    // Fetch property data
    async function loadProperty() {
      if (!isAuthenticated) {
        goto('/auth/login');
        return;
      }
      
      loading = true;
      error = null;
      
      try {
        const response = await api.get(`/properties/${propertyId}/`);
        
        if (response?.data?.property) {
          property = response.data.property;
          
          // Check if user has permission to delete
          if (property.owner?.id !== currentUser?.id && !currentUser?.isAdmin) {
            error = $t('properties.delete.unauthorized');
            canDelete = false;
            return;
          }
          
          // Check for deletion constraints
          constraints = [];
          
          // Check property status
          if (!['draft', 'inactive'].includes(property.status)) {
            constraints.push({
              type: 'error',
              message: $t('properties.delete.constraint_status', { status: property.status_display })
            });
          }
          
          // Check for active auctions
          if (property.has_auction) {
            constraints.push({
              type: 'error',
              message: $t('properties.delete.constraint_auction')
            });
          }
          
          // Determine if property can be deleted
          canDelete = constraints.filter(c => c.type === 'error').length === 0;
          
          // Add warning for soft delete
          constraints.push({
            type: 'warning',
            message: $t('properties.delete.soft_delete_warning')
          });
        } else {
          throw new Error('Invalid response format');
        }
      } catch (err) {
        console.error('Error fetching property details:', err);
        error = err.response?.data?.error || $t('system_messages.error_occurred');
      } finally {
        loading = false;
      }
    }
    
    // Delete property
    async function handleDelete() {
      if (!confirmDelete || confirmText !== property.property_number) {
        toast.error($t('properties.delete.confirm_error'));
        return;
      }
      
      deleting = true;
      error = null;
      
      try {
        const response = await api.delete(`/properties/${propertyId}/`);
        
        // Success message
        toast.success($t('properties.delete.success'));
        
        // Redirect to properties list after short delay
        setTimeout(() => {
          goto('/dashboard/properties');
        }, 1500);
      } catch (err) {
        console.error('Error deleting property:', err);
        error = err.response?.data?.error || $t('system_messages.error_occurred');
        toast.error($t('properties.delete.error'));
      } finally {
        deleting = false;
      }
    }
    
    // Cancel and return to property details
    function cancelDelete() {
      goto(`/dashboard/properties/${propertyId}`);
    }
    
    // Initialize
    onMount(() => {
      if (propertyId) {
        loadProperty();
      }
    });
  </script>
  
  <svelte:head>
    <title>{$t('properties.delete.title')} | {$t('general.app_name')}</title>
  </svelte:head>
  
  <div class="container mx-auto px-4 py-8" class:rtl={isRTL}>
    <div class="mb-6">
      <Button 
        variant="ghost" 
        on:click={cancelDelete}
        class="inline-flex items-center text-neutral-600 hover:text-neutral-900 dark:text-neutral-400 dark:hover:text-white"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M19 12H5M5 12l7 7M5 12l7-7"/>
        </svg>
        {$t('general.back')}
      </Button>
    </div>
    
    <Card padding={true} class="max-w-2xl mx-auto">
      <div class="text-center mb-6">
        <div class="bg-error/10 dark:bg-error/5 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-error" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2M10 11v6M14 11v6"/>
          </svg>
        </div>
        <h1 class="text-2xl font-bold text-error mb-2">{$t('properties.delete.title')}</h1>
        <p class="text-neutral-500 dark:text-neutral-400">{$t('properties.delete.subtitle')}</p>
      </div>
      
      {#if loading}
        <div class="py-8 text-center">
          <Spinner size="lg" text={$t('general.loading')} />
        </div>
      {:else if error && !property}
        <Alert type="error" title={$t('general.error')} class="mb-4">
          <p>{error}</p>
          <div class="mt-4">
            <Button 
              variant="primary"
              on:click={loadProperty}
            >
              {$t('general.retry')}
            </Button>
          </div>
        </Alert>
      {:else if property}
        <div in:fade={{ duration: 300 }}>
          {#if !canDelete}
            <Alert type="error" title={$t('properties.delete.cannot_delete')} class="mb-6">
              <ul class="list-disc list-inside mt-2 space-y-1">
                {#each constraints.filter(c => c.type === 'error') as constraint}
                  <li>{constraint.message}</li>
                {/each}
              </ul>
            </Alert>
          {/if}
          
          <div class="mb-6">
            <h2 class="text-lg font-semibold mb-3">{$t('properties.delete.property_details')}</h2>
            
            <div class="bg-neutral-50 dark:bg-neutral-800/50 rounded-lg p-4 mb-4">
              <div class="flex flex-col md:flex-row md:items-center mb-3">
                <div class="text-neutral-500 dark:text-neutral-400 w-40 mb-1 md:mb-0">
                  {$t('properties.property_number')}:
                </div>
                <div class="font-medium">
                  {property.property_number}
                </div>
              </div>
              
              <div class="flex flex-col md:flex-row md:items-center mb-3">
                <div class="text-neutral-500 dark:text-neutral-400 w-40 mb-1 md:mb-0">
                  {$t('properties.title')}:
                </div>
                <div class="font-medium">
                  {property.title}
                </div>
              </div>
              
              <div class="flex flex-col md:flex-row md:items-center mb-3">
                <div class="text-neutral-500 dark:text-neutral-400 w-40 mb-1 md:mb-0">
                  {$t('properties.property_type')}:
                </div>
                <div>
                  {property.property_type_display}
                </div>
              </div>
              
              <div class="flex flex-col md:flex-row md:items-center mb-3">
                <div class="text-neutral-500 dark:text-neutral-400 w-40 mb-1 md:mb-0">
                  {$t('properties.property_status')}:
                </div>
                <div>
                  <Badge type={
                    property.status === 'active' ? 'success' :
                    property.status === 'pending_approval' ? 'warning' :
                    property.status === 'sold' ? 'info' :
                    'default'
                  }>
                    {property.status_display}
                  </Badge>
                </div>
              </div>
              
              <div class="flex flex-col md:flex-row md:items-center">
                <div class="text-neutral-500 dark:text-neutral-400 w-40 mb-1 md:mb-0">
                  {$t('properties.property_location')}:
                </div>
                <div>
                  {property.city}
                  {#if property.district}, {property.district}{/if}
                </div>
              </div>
            </div>
          </div>
          
          <div class="mb-6">
            <h2 class="text-lg font-semibold mb-3">{$t('properties.delete.warning')}</h2>
            
            <Alert type="warning" class="mb-4">
              <p class="font-medium">{$t('properties.delete.warning_message')}</p>
              <ul class="list-disc list-inside mt-2 space-y-1">
                <li>{$t('properties.delete.warning_data')}</li>
                <li>{$t('properties.delete.warning_documents')}</li>
                <li>{$t('properties.delete.warning_restore')}</li>
                {#each constraints.filter(c => c.type === 'warning') as constraint}
                  <li>{constraint.message}</li>
                {/each}
              </ul>
            </Alert>
          </div>
          
          {#if canDelete}
            <div class="border-t border-neutral-200 dark:border-neutral-700 pt-6">
              <h2 class="text-lg font-semibold mb-3">{$t('properties.delete.confirmation')}</h2>
              
              <p class="mb-4">
                {$t('properties.delete.confirm_message', { property_number: property.property_number })}
              </p>
              
              <div class="mb-4">
                <input
                  type="text"
                  class="w-full rounded-md border border-neutral-300 bg-white px-3 py-2 text-neutral-900 placeholder-neutral-400 focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary dark:border-neutral-700 dark:bg-neutral-800 dark:text-white dark:placeholder-neutral-500"
                  placeholder={property.property_number}
                  bind:value={confirmText}
                />
              </div>
              
              <div class="mb-6">
                <Checkbox 
                  bind:checked={confirmDelete}
                  label={$t('properties.delete.checkbox')}
                />
              </div>
              
              <div class="flex justify-between">
                <Button 
                  variant="outline"
                  on:click={cancelDelete}
                  disabled={deleting}
                >
                  {$t('general.cancel')}
                </Button>
                
                <Button 
                  variant="error"
                  on:click={handleDelete}
                  loading={deleting}
                  disabled={deleting || !confirmDelete || confirmText !== property.property_number}
                >
                  {#if deleting}
                    {$t('properties.delete.deleting')}
                  {:else}
                    {$t('properties.delete.confirm_button')}
                  {/if}
                </Button>
              </div>
            </div>
          {:else}
            <div class="border-t border-neutral-200 dark:border-neutral-700 pt-6">
              <div class="flex justify-between">
                <Button 
                  variant="outline"
                  on:click={cancelDelete}
                >
                  {$t('general.back')}
                </Button>
                
                <Button 
                  variant="primary"
                  on:click={() => goto(`/dashboard/properties/${propertyId}`)}
                >
                  {$t('properties.view_details')}
                </Button>
              </div>
            </div>
          {/if}
        </div>
      {/if}
    </Card>
  </div>
  
  <style>
    /* RTL Support */
    .rtl {
      direction: rtl;
      text-align: right;
    }
    
    .rtl .mr-1\.5 {
      margin-right: 0;
      margin-left: 0.375rem;
    }
    
    /* List styles for RTL */
    .rtl .list-inside {
      padding-left: 0;
      padding-right: 1.25rem;
    }
  </style>