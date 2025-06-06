<!-- front/src/routes/auctions/create/+page.svelte -->
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
  let validationErrors = {};
  
  // Safe translation helper
  function safeTranslate(key, fallback = '') {
    try {
      return $t ? $t(key) : fallback;
    } catch (e) {
      console.warn(`Translation error for key: ${key}`, e);
      return fallback;
    }
  }
  
  // Define breadcrumb items with safe translations
  $: breadcrumbItems = [
    { label: safeTranslate('nav.home', 'Home'), href: '/' },
    { label: safeTranslate('nav.auctions', 'Auctions'), href: '/auctions' },
    { label: safeTranslate('auction.createAuction', 'Create Auction'), href: '/auctions/create', active: true }
  ];
  
  onMount(async () => {
    try {
      // Check if user is logged in
      if (!$user) {
        goto('/login?redirect=/auctions/create');
        return;
      }
      
      // Check if user has permissions
      const hasPermission = $user.is_staff || 
                           $user.is_superuser || 
                           $user.role === 'owner' || 
                           $user.role === 'appraiser' ||
                           $user.role === 'admin';
      
      if (!hasPermission) {
        error = safeTranslate('auction.unauthorizedMessage', 'You do not have permission to create auctions.');
      }
    } catch (e) {
      console.error('Error in onMount:', e);
      error = 'An error occurred while loading the page.';
    } finally {
      loading = false;
    }
  });
  
  async function handleSubmit() {
    try {
      submitting = true;
      error = '';
      success = '';
      validationErrors = {};
      
      // Validate the form
      if (!auctionForm) {
        throw new Error('Form not initialized');
      }
      
      const validation = auctionForm.validateForm();
      if (!validation.valid) {
        error = validation.error || 'Please check the form for errors';
        validationErrors = validation.errors || {};
        return;
      }
      
      // Get prepared data from the form component
      const preparedAuction = auctionForm.prepareDataForSubmission();
      
      if (!preparedAuction) {
        throw new Error('Failed to get form data');
      }
      
      // Validate required fields
      if (!preparedAuction.title || !preparedAuction.description) {
        throw new Error('Title and description are required');
      }
      
      // Create auction first
      const response = await createAuction(preparedAuction);
      
      if (response && response.id) {
        // Upload any temporary media after auction creation
        try {
          await auctionForm.uploadTempMedia(response.id);
        } catch (mediaError) {
          console.warn('Media upload failed:', mediaError);
          // Don't fail the entire process if media upload fails
        }
        
        success = safeTranslate('auction.createSuccess', 'Auction created successfully!');
        
        // Show success message and redirect after a delay
        setTimeout(() => {
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
      error = err.message || safeTranslate('auction.createFailed', 'Failed to create auction. Please try again.');
    } finally {
      submitting = false;
    }
  }

  
  function togglePreview() {
    try {
      if (!auctionForm) {
        error = 'Form not initialized';
        return;
      }
      
      if (!isPreview) {
        // Validate form before showing preview
        const validation = auctionForm.validateForm();
        if (!validation.valid) {
          error = validation.error || 'Please fix the errors before previewing';
          validationErrors = validation.errors || {};
          return;
        }
        
        // Get data for preview
        previewData = auctionForm.prepareDataForSubmission();
        if (!previewData) {
          error = 'Failed to get form data for preview';
          return;
        }
      }
      
      error = '';
      isPreview = !isPreview;
    } catch (e) {
      console.error('Error toggling preview:', e);
      error = 'An error occurred while toggling preview mode.';
    }
  }
  
  function backToForm() {
    isPreview = false;
    error = '';
  }
</script>

<svelte:head>
  <title>{safeTranslate('auction.createAuction', 'Create Auction')} | Real Estate Platform</title>
  <meta name="description" content={safeTranslate('auction.createAuctionDesc', 'Create a new auction for your property')} />
</svelte:head>

<div class="min-h-screen bg-gray-50 dark:bg-gray-900 py-6 px-4 sm:px-6 lg:px-8">
  <div class="max-w-6xl mx-auto space-y-6">
    <!-- Breadcrumb Navigation -->
    <Breadcrumb items={breadcrumbItems} />
    
    <!-- Page Header -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
      <div class="md:flex md:items-center md:justify-between">
        <div class="flex-1 min-w-0">
          <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
            {isPreview ? safeTranslate('auction.preview', 'Preview') : safeTranslate('auction.createAuction', 'Create Auction')}
          </h1>
          <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
            {isPreview ? 
              safeTranslate('auction.previewDesc', 'Review your auction before publishing') : 
              safeTranslate('auction.createAuctionDesc', 'Create a new auction for your property')
            }
          </p>
        </div>
        
        <!-- Preview Toggle Button -->
        {#if !loading && !error}
          <div class="mt-4 lg:mt-0 lg:ml-4">
            <Button
              variant={isPreview ? 'secondary' : 'outline'}
              size="sm"
              on:click={togglePreview}
              disabled={submitting}
              iconLeft={isPreview ? 
                '<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>' :
                '<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>'
              }
            >
              {isPreview ? safeTranslate('common.edit', 'Edit') : safeTranslate('auction.preview', 'Preview')}
            </Button>
          </div>
        {/if}
      </div>
    </div>
    
    <!-- Error Messages -->
    {#if error}
      <Alert 
        type="error" 
        title={safeTranslate('error.title', 'Error')}
        message={error}
        dismissible={true}
        on:dismiss={() => { error = ''; }}
      />
    {/if}
    
    <!-- Success Messages -->
    {#if success}
      <Alert 
        type="success" 
        title={safeTranslate('success.title', 'Success')}
        message={success}
      />
    {/if}
    
    <!-- Loading State -->
    {#if loading}
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
        <LoadingSkeleton type="auctionForm" />
      </div>
    
    <!-- Preview Mode -->
    {:else if isPreview && previewData}
      <div class="border border-blue-200 dark:border-blue-800 rounded-lg overflow-hidden bg-white dark:bg-gray-800 shadow-sm">
        <div class="bg-blue-50 dark:bg-blue-900/20 px-6 py-3 border-b border-blue-200 dark:border-blue-800">
          <div class="flex items-center text-blue-700 dark:text-blue-300">
            <svg class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
            <span class="font-medium text-sm">{safeTranslate('common.preview', 'Preview')}</span>
          </div>
        </div>
        
        <AuctionPreview auction={previewData} />
      </div>
      
      <!-- Preview Action Buttons -->
      <div class="flex justify-end space-x-3">
        <Button
          variant="outline"
          size="sm"
          on:click={backToForm}
          iconLeft='<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 17l-5-5m0 0l5-5m-5 5h12" /></svg>'
        >
          {safeTranslate('common.edit', 'Edit')}
        </Button>
        
        <Button
          variant="primary"
          size="sm"
          on:click={handleSubmit}
          loading={submitting}
          disabled={submitting}
          iconLeft='<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>'
        >
          {submitting ? safeTranslate('common.creating', 'Creating...') : safeTranslate('auction.create', 'Create')}
        </Button>
      </div>
    
    <!-- Form Mode -->
    {:else}
      <div class="space-y-6">
        <AuctionForm 
          bind:this={auctionForm} 
          {validationErrors}
          on:validationChange={(e) => validationErrors = e.detail}
        />
        
        <!-- Submit Buttons -->
        <div class="flex justify-end space-x-3">
          <Button
            variant="outline"
            size="sm"
            on:click={() => goto('/auctions')}
            disabled={submitting}
            iconLeft='<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>'
          >
            {safeTranslate('common.cancel', 'Cancel')}
          </Button>
          
          <Button
            variant="secondary"
            size="sm"
            on:click={togglePreview}
            disabled={submitting}
            iconLeft='<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>'
          >
            {safeTranslate('auction.preview', 'Preview')}
          </Button>
          
          <Button
            variant="primary"
            size="sm"
            on:click={handleSubmit}
            loading={submitting}
            disabled={submitting}
            iconLeft='<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>'
          >
            {submitting ? safeTranslate('common.creating', 'Creating...') : safeTranslate('auction.create', 'Create')}
          </Button>
        </div>
      </div>
    {/if}
  </div>
</div>