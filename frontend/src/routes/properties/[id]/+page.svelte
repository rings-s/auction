<!-- routes/properties/[id]/+page.svelte -->
<script>
    /**
     * Property Detail Page
     * Displays a single property with all its details, images, and actions
     */
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { t } from '$lib/i18n';
    import { formatCurrency } from '$lib/utils/formatters';
    import { fade } from 'svelte/transition';
  
    import { authStore } from '$lib/stores/auth';
    import { toast } from '$lib/stores/toast';
    import { api } from '$lib/services/api';
    
    // UI Components
    import PropertyDetails from '$lib/components/properties/PropertyDetails.svelte';
    import PropertyCard from '$lib/components/properties/PropertyCard.svelte';
    import AuctionCard from '$lib/components/auctions/AuctionCard.svelte';
    import Spinner from '$lib/components/ui/Spinner.svelte';
    import Alert from '$lib/components/ui/Alert.svelte';
    import Button from '$lib/components/ui/Button.svelte';
    import Card from '$lib/components/ui/Card.svelte';
    import Input from '$lib/components/ui/Input.svelte';
    
    // State
    let property = null;
    let relatedAuctions = [];
    let recommendedProperties = [];
    let loading = true;
    let error = null;
    let showContactModal = false;
    let contactFormData = { subject: '', message: '', phone: '' };
    let contactFormLoading = false;
    let contactFormSuccess = false;
    let contactFormError = null;
    
    // Get property ID from URL
    $: propertyId = $page.params.id;
    
    // Auth state
    $: isAuthenticated = $authStore.isAuthenticated;
    $: currentUser = $authStore.user;
    $: isOwner = currentUser && property?.owner?.id === currentUser.id;
    
    // Load property data
    async function loadProperty() {
      loading = true;
      error = null;
      
      try {
        // Fetch property details
        const response = await api.get(`properties/${propertyId}/`, {
          include_auctions: true,
          include_documents: true
        });
        
        if (response?.data?.property) {
          property = response.data.property;
          
          // Extract related auctions if any
          if (property.auctions && property.auctions.length > 0) {
            relatedAuctions = property.auctions;
          }
          
          // Pre-fill contact form subject
          contactFormData.subject = `${$t('properties.inquiry_about')} ${property.title}`;
          
          // Load recommended properties
          await loadRecommendedProperties();
        } else {
          throw new Error('Invalid response format');
        }
      } catch (err) {
        console.error('Error fetching property details:', err);
        error = err.message || $t('system_messages.error_occurred');
      } finally {
        loading = false;
      }
    }
    
    // Load recommended properties
    async function loadRecommendedProperties() {
      if (!property) return;
      
      try {
        const response = await api.get('properties/', {
          property_type: property.property_type,
          city: property.city,
          limit: 4,
          exclude: propertyId
        });
        
        if (response?.data?.results) {
          recommendedProperties = response.data.results.slice(0, 4);
        }
      } catch (err) {
        console.error('Error fetching recommended properties:', err);
        // Non-critical, don't show error
      }
    }
    
    // Toggle contact modal
    function toggleContactModal() {
      showContactModal = !showContactModal;
      
      if (!showContactModal) {
        // Reset form state when closing
        contactFormSuccess = false;
        contactFormError = null;
      }
    }
    
    // Send message to property owner
    async function sendMessage(event) {
      event.preventDefault();
      contactFormLoading = true;
      contactFormError = null;
      
      // Validate form
      if (!contactFormData.subject || !contactFormData.message) {
        contactFormError = $t('system_messages.required_fields');
        contactFormLoading = false;
        return;
      }
      
      try {
        // Send message via API
        const response = await api.post(`properties/${propertyId}/contact/`, contactFormData);
        
        if (response?.data?.success) {
          contactFormSuccess = true;
          toast.success($t('system_messages.message_sent'));
          
          // Reset form
          contactFormData.message = '';
          contactFormData.phone = '';
          
          // Close modal after delay
          setTimeout(() => {
            if (contactFormSuccess) {
              toggleContactModal();
            }
          }, 2000);
        } else {
          throw new Error(response?.data?.error || $t('system_messages.error_occurred'));
        }
      } catch (err) {
        console.error('Error sending message:', err);
        contactFormError = err.message || $t('system_messages.error_occurred');
      } finally {
        contactFormLoading = false;
      }
    }
    
    // Handle contact owner button click in PropertyDetails
    function handleContactOwner() {
      toggleContactModal();
    }
    
    // Initialize
    onMount(() => {
      if (propertyId) {
        loadProperty();
      }
    });
  </script>
  
  <svelte:head>
    <title>{property?.title || $t('properties.property_details')} | {$t('site.name')}</title>
    <meta name="description" content={property?.description || $t('properties.meta_description')} />
  </svelte:head>
  
  <div class="min-h-screen bg-cosmos-bg pb-12">
    {#if loading}
      <div class="flex justify-center p-20">
        <Spinner size="xl" text={$t('general.loading')} />
      </div>
    {:else if error}
      <div class="container mx-auto my-16 max-w-3xl px-4">
        <Alert type="error" title={$t('general.error')} dismissible={false}>
          <p>{error}</p>
          <div class="mt-4">
            <Button 
              variant="primary"
              onClick={loadProperty}
            >
              {$t('general.retry')}
            </Button>
          </div>
        </Alert>
      </div>
    {:else if property}
      <div in:fade={{ duration: 300 }}>
        <!-- Main Property Details Component -->
        <PropertyDetails 
          {property} 
          on:contactOwner={handleContactOwner} 
        />
        
        <!-- Related Auctions Section -->
        {#if relatedAuctions && relatedAuctions.length > 0}
          <section class="container mx-auto mt-16 px-4">
            <h2 class="mb-6 text-2xl font-bold text-cosmos-text">{$t('properties.related_auctions')}</h2>
            
            <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {#each relatedAuctions as auction}
                <AuctionCard {auction} />
              {/each}
            </div>
            
            {#if relatedAuctions.length === 1}
              <div class="mt-6 text-center">
                <Button 
                  variant="primary"
                  href={`/auctions/${relatedAuctions[0].id}`}
                >
                  {$t('properties.view_auction')}
                </Button>
              </div>
            {/if}
          </section>
        {/if}
        
        <!-- Recommended Properties -->
        {#if recommendedProperties && recommendedProperties.length > 0}
          <section class="container mx-auto mt-16 px-4">
            <h2 class="mb-6 text-2xl font-bold text-cosmos-text">{$t('properties.similar_properties')}</h2>
            
            <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {#each recommendedProperties as recProperty}
                {#if recProperty}
                  <PropertyCard property={recProperty} />
                {/if}
              {/each}
            </div>
          </section>
        {/if}
      </div>
      
      <!-- Contact Modal -->
      {#if showContactModal}
        <div 
          class="fixed inset-0 z-50 flex items-center justify-center bg-cosmos-bg-dark bg-opacity-80 p-4"
          transition:fade={{ duration: 200 }}
        >
          <Card class="w-full max-w-md" padding={true}>
            <div class="flex items-center justify-between">
              <h3 class="text-xl font-bold text-cosmos-text">{$t('properties.contact_owner')}</h3>
              
              <Button 
                variant="ghost"
                size="sm"
                onClick={toggleContactModal}
                ariaLabel={$t('general.close')}
              >
                <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </Button>
            </div>
            
            {#if contactFormSuccess}
              <div class="mt-6 rounded-lg bg-status-success bg-opacity-10 p-6 text-center">
                <svg class="mx-auto h-12 w-12 text-status-success" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                <h4 class="mt-4 text-lg font-medium text-cosmos-text">{$t('properties.message_sent')}</h4>
                <p class="mt-2 text-cosmos-text-muted">{$t('properties.owner_will_respond')}</p>
              </div>
            {:else if !isAuthenticated}
              <div class="mt-6 rounded-lg bg-primary bg-opacity-10 p-6 text-center">
                <p class="text-cosmos-text">{$t('properties.login_to_contact')}</p>
                <Button 
                  variant="primary"
                  href={`/auth/login?redirect=/properties/${propertyId}`}
                  class="mt-4"
                >
                  {$t('auth.login')}
                </Button>
              </div>
            {:else if isOwner}
              <div class="mt-6 rounded-lg bg-cosmos-bg-light bg-opacity-30 p-6 text-center">
                <p class="text-cosmos-text">{$t('properties.own_property')}</p>
                <Button 
                  variant="primary"
                  href="/dashboard/properties"
                  class="mt-4"
                >
                  {$t('dashboard.manage_properties')}
                </Button>
              </div>
            {:else}
              <form class="mt-6 space-y-4" on:submit={sendMessage}>
                {#if contactFormError}
                  <Alert type="error" dismissible>{contactFormError}</Alert>
                {/if}
                
                <Input
                  type="text"
                  label={$t('properties.message_subject')}
                  placeholder={$t('properties.subject_placeholder')}
                  bind:value={contactFormData.subject}
                  required={true}
                />
                
                <div>
                  <label for="message" class="mb-1.5 block text-sm font-medium text-cosmos-text">
                    {$t('properties.your_message')}*
                  </label>
                  <textarea 
                    id="message" 
                    rows="5" 
                    class="w-full rounded-lg border border-cosmos-bg-light bg-cosmos-bg bg-opacity-30 p-3 text-cosmos-text outline-none focus:border-primary focus:ring-2 focus:ring-primary focus:ring-opacity-25"
                    placeholder={$t('properties.message_placeholder')}
                    bind:value={contactFormData.message}
                    required
                  ></textarea>
                </div>
                
                <Input
                  type="tel"
                  label={$t('properties.your_phone')}
                  placeholder={$t('properties.phone_placeholder')}
                  bind:value={contactFormData.phone}
                />
                
                <div class="flex space-x-3">
                  <Button 
                    type="button" 
                    variant="secondary"
                    onClick={toggleContactModal}
                    disabled={contactFormLoading}
                    class="flex-1"
                  >
                    {$t('general.cancel')}
                  </Button>
                  
                  <Button 
                    type="submit" 
                    variant="primary"
                    loading={contactFormLoading}
                    disabled={contactFormLoading}
                    class="flex-1"
                  >
                    {$t('properties.send_message')}
                  </Button>
                </div>
              </form>
            {/if}
          </Card>
        </div>
      {/if}
    {/if}
  </div>