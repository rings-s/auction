<!-- routes/properties/[id]/+page.svelte -->
<script>
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { t } from '$lib/i18n';
    import { formatCurrency } from '$lib/utils/formatters';

    import { authStore } from '$lib/stores/auth';
    import { toast } from '$lib/stores/toast';
    import { api } from '$lib/services/api';
    
    // UI Components
    import PropertyDetails from '$lib/components/properties/PropertyDetails.svelte';
    import PropertyCard from '$lib/components/properties/PropertyCard.svelte';
    import AuctionCard from '$lib/components/auctions/AuctionCard.svelte';
    import LoadingIndicator from '$lib/components/ui/LoadingIndicator.svelte';
    import Alert from '$lib/components/ui/Alert.svelte';
    import Button from '$lib/components/ui/Button.svelte';
    import GlassCard from '$lib/components/ui/GlassCard.svelte';
    
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
    
    // Share property
    function shareProperty() {
        try {
            if (navigator && navigator.share) {
                navigator.share({
                    title: property ? property.title : '',
                    text: property ? `${property.title} - ${property.address || ''}, ${property.city || ''}` : '',
                    url: window.location.href
                }).catch(err => {
                    console.error('Error sharing:', err);
                });
            } else if (navigator && navigator.clipboard) {
                // Fallback: copy to clipboard
                navigator.clipboard.writeText(window.location.href)
                    .then(() => {
                        toast.success($t('general.link_copied'));
                    })
                    .catch(err => {
                        console.error('Error copying link:', err);
                    });
            } else {
                // Ultra fallback: show URL to copy manually
                prompt($t('general.copy_url'), window.location.href);
            }
        } catch (err) {
            console.error('Share error:', err);
        }
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
            <LoadingIndicator size="xl" text={$t('general.loading')} />
        </div>
    {:else if error}
        <div class="container mx-auto my-16 max-w-3xl px-4">
            <Alert type="error" title={$t('general.error')}>
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
        <div>
            <!-- Hero Section with Property Header -->
            <div class="relative bg-gradient-to-b from-cosmos-bg-dark to-cosmos-bg pb-8 pt-8">
                <div class="container mx-auto px-4 lg:px-8">
                    <!-- Breadcrumb -->
                    <div class="mb-6 flex text-sm text-cosmos-text-muted">
                        <a href="/" class="hover:text-primary">{$t('navigation.home')}</a>
                        <span class="mx-2">/</span>
                        <a href="/properties" class="hover:text-primary">{$t('navigation.properties')}</a>
                        <span class="mx-2">/</span>
                        <span class="truncate text-cosmos-text">{property.title}</span>
                    </div>
                    
                    <!-- Property Header -->
                    <div class="mb-8 flex flex-col justify-between gap-6 lg:flex-row lg:items-start">
                        <!-- Title and Location -->
                        <div class="flex-1">
                            <div class="flex flex-wrap items-center gap-3">
                                <h1 class="text-2xl font-bold text-cosmos-text sm:text-3xl md:text-4xl">
                                    {property.title}
                                </h1>
                                
                                {#if property.is_verified}
                                    <span class="flex items-center rounded-full bg-status-success bg-opacity-20 px-3 py-1 text-xs font-medium text-status-success">
                                        <svg class="mr-1 h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                                        </svg>
                                        {$t('properties.verified')}
                                    </span>
                                {/if}
                                
                                {#if property.has_auction}
                                    <span class="flex items-center rounded-full bg-primary bg-opacity-20 px-3 py-1 text-xs font-medium text-primary">
                                        <svg class="mr-1 h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                                        </svg>
                                        {$t('properties.has_auction')}
                                    </span>
                                {/if}
                            </div>
                            
                            <div class="mt-2 flex items-center text-cosmos-text-muted">
                                <svg class="mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                                </svg>
                                <p>{property.address}, {property.district}, {property.city}</p>
                            </div>
                            
                            <!-- Status Tags -->
                            <div class="mt-4 flex flex-wrap gap-2">
                                <span class="rounded-full bg-property-{property.property_type} bg-opacity-80 px-3 py-1 text-sm text-white">
                                    {property.property_type_display || $t(`properties.types.${property.property_type}`)}
                                </span>
                                
                                <span class="rounded-full bg-cosmos-text-muted px-3 py-1 text-sm text-white">
                                    {property.status_display || $t(`properties.status.${property.status}`)}
                                </span>
                                
                                {#if property.is_featured}
                                    <span class="rounded-full bg-[#FFD700] px-3 py-1 text-sm font-medium text-cosmos-bg-dark">
                                        {$t('general.featured')}
                                    </span>
                                {/if}
                            </div>
                        </div>
                        
                        <!-- Price and Actions -->
                        <div class="flex flex-col items-start gap-4 sm:flex-row sm:items-center lg:flex-col lg:items-end">
                            <!-- Price Box -->
                            <div class="rounded-xl bg-cosmos-bg-light bg-opacity-30 p-4 backdrop-blur-sm">
                                <p class="text-sm text-cosmos-text-muted">{$t('properties.property_price')}</p>
                                <p class="text-2xl font-bold text-primary md:text-3xl">
                                    {property.estimated_value ? formatCurrency(property.estimated_value) : '-'}
                                </p>
                                
                                {#if property.price_per_sqm}
                                    <p class="mt-1 text-sm text-cosmos-text-muted">
                                        {formatCurrency(property.price_per_sqm)} / m²
                                    </p>
                                {/if}
                            </div>
                            
                            <!-- Action Buttons -->
                            <div class="flex flex-wrap gap-2">
                                {#if property.has_auction}
                                    <a 
                                        href={`/auctions?property_id=${property.id}`}
                                        class="flex items-center rounded-lg bg-primary px-4 py-2 text-sm font-medium text-white transition hover:bg-primary-dark"
                                    >
                                        <svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
                                        </svg>
                                        {$t('properties.view_auctions')}
                                    </a>
                                {/if}
                                
                                <button 
                                    class="flex items-center rounded-lg bg-cosmos-bg-light bg-opacity-30 px-4 py-2 text-sm font-medium text-cosmos-text transition hover:bg-cosmos-bg-light"
                                    on:click={toggleContactModal}
                                >
                                    <svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                                    </svg>
                                    {$t('properties.contact_owner')}
                                </button>
                                
                                <button 
                                    class="flex items-center rounded-lg bg-cosmos-bg-light bg-opacity-30 px-4 py-2 text-sm font-medium text-cosmos-text transition hover:bg-cosmos-bg-light"
                                    on:click={shareProperty}
                                >
                                    <svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
                                    </svg>
                                    {$t('properties.share_property')}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Main Content -->
            <div class="container mx-auto px-4 py-8">
                <PropertyDetails property={property} /> 
                
                <!-- Related Auctions Section -->
                {#if relatedAuctions && relatedAuctions.length > 0}
                    <section class="mt-16">
                        <h2 class="mb-6 text-2xl font-bold text-cosmos-text">{$t('properties.related_auctions')}</h2>
                        
                        <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                            {#each relatedAuctions as auction}
                                <AuctionCard {auction} />
                            {/each}
                        </div>
                        
                        {#if relatedAuctions.length === 1}
                            <div class="mt-6 text-center">
                                <a 
                                    href={`/auctions/${relatedAuctions[0].id}`}
                                    class="inline-block rounded-lg bg-primary px-6 py-3 text-white transition hover:bg-primary-dark"
                                >
                                    {$t('properties.view_auction')}
                                </a>
                            </div>
                        {/if}
                    </section>
                {/if}
                
                <!-- Recommended Properties -->
                {#if recommendedProperties && recommendedProperties.length > 0}
                    <section class="mt-16">
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
        </div>
        
        <!-- Contact Modal -->
        {#if showContactModal}
            <div class="fixed inset-0 z-50 flex items-center justify-center bg-cosmos-bg-dark bg-opacity-80 p-4">
                <GlassCard class="w-full max-w-md">
                    <div class="flex items-center justify-between">
                        <h3 class="text-xl font-bold text-cosmos-text">{$t('properties.contact_owner')}</h3>
                        
                        <button 
                            class="rounded-full p-1 text-cosmos-text-muted transition hover:bg-cosmos-bg-light hover:text-cosmos-text"
                            on:click={toggleContactModal}
                        >
                            <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>
                    
                    {#if contactFormSuccess}
                        <div class="mt-6 rounded-lg bg-status-success bg-opacity-10 p-6 text-center">
                            <svg class="mx-auto h-12 w-12 text-status-success" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                            </svg>
                            <h4 class="mt-4 text-lg font-medium text-cosmos-text">{$t('properties.message_sent')}</h4>
                            <p class="mt-2 text-cosmos-text-muted">{$t('properties.owner_will_respond')}</p>
                        </div>
                    {:else if !isAuthenticated}
                        <div class="mt-6 rounded-lg bg-primary bg-opacity-10 p-6 text-center">
                            <p class="text-cosmos-text">{$t('properties.login_to_contact')}</p>
                            <a 
                                href={`/auth/login?redirect=/properties/${propertyId}`}
                                class="mt-4 inline-block rounded-lg bg-primary px-6 py-2 text-white hover:bg-primary-dark"
                            >
                                {$t('auth.login')}
                            </a>
                        </div>
                    {:else if isOwner}
                        <div class="mt-6 rounded-lg bg-cosmos-bg-light bg-opacity-30 p-6 text-center">
                            <p class="text-cosmos-text">{$t('properties.own_property')}</p>
                            <a 
                                href="/dashboard/properties"
                                class="mt-4 inline-block rounded-lg bg-primary px-6 py-2 text-white hover:bg-primary-dark"
                            >
                                {$t('dashboard.manage_properties')}
                            </a>
                        </div>
                    {:else}
                        <form class="mt-6 space-y-4" on:submit={sendMessage}>
                            {#if contactFormError}
                                <Alert type="error" dismissible>{contactFormError}</Alert>
                            {/if}
                            
                            <div>
                                <label for="subject" class="mb-1 block text-sm font-medium text-cosmos-text-muted">
                                    {$t('properties.message_subject')}*
                                </label>
                                <input 
                                    type="text" 
                                    id="subject" 
                                    class="w-full rounded-lg border border-cosmos-bg-light bg-cosmos-bg-light bg-opacity-30 p-3 text-cosmos-text outline-none focus:border-primary"
                                    placeholder={$t('properties.subject_placeholder')}
                                    bind:value={contactFormData.subject}
                                    required
                                />
                            </div>
                            
                            <div>
                                <label for="message" class="mb-1 block text-sm font-medium text-cosmos-text-muted">
                                    {$t('properties.your_message')}*
                                </label>
                                <textarea 
                                    id="message" 
                                    rows="5" 
                                    class="w-full rounded-lg border border-cosmos-bg-light bg-cosmos-bg-light bg-opacity-30 p-3 text-cosmos-text outline-none focus:border-primary"
                                    placeholder={$t('properties.message_placeholder')}
                                    bind:value={contactFormData.message}
                                    required
                                ></textarea>
                            </div>
                            
                            <div>
                                <label for="phone" class="mb-1 block text-sm font-medium text-cosmos-text-muted">
                                    {$t('properties.your_phone')}
                                </label>
                                <input 
                                    type="tel" 
                                    id="phone" 
                                    class="w-full rounded-lg border border-cosmos-bg-light bg-cosmos-bg-light bg-opacity-30 p-3 text-cosmos-text outline-none focus:border-primary"
                                    placeholder={$t('properties.phone_placeholder')}
                                    bind:value={contactFormData.phone}
                                />
                            </div>
                            
                            <div class="flex space-x-3">
                                <button 
                                    type="button" 
                                    class="flex-1 rounded-lg border border-cosmos-bg-light py-3 text-cosmos-text-muted transition hover:text-cosmos-text"
                                    on:click={toggleContactModal}
                                    disabled={contactFormLoading}
                                >
                                    {$t('general.cancel')}
                                </button>
                                
                                <button 
                                    type="submit" 
                                    class="flex-1 rounded-lg bg-primary py-3 font-medium text-white transition hover:bg-primary-dark disabled:opacity-70"
                                    disabled={contactFormLoading}
                                >
                                    {#if contactFormLoading}
                                        <span class="flex items-center justify-center">
                                            <svg class="mr-2 h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
                                                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                                                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                            </svg>
                                            {$t('general.sending')}
                                        </span>
                                    {:else}
                                        {$t('properties.send_message')}
                                    {/if}
                                </button>
                            </div>
                        </form>
                    {/if}
                </GlassCard>
            </div>
        {/if}
    {/if}
</div>