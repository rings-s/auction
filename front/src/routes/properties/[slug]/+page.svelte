<script>
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { t, locale } from '$lib/i18n';
  import { translateFeatures, translateAmenities } from '$lib/i18n';
  
  import Tabs from '$lib/components/ui/Tabs.svelte';
  import Gallery from '$lib/components/ui/Gallery.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Modal from '$lib/components/ui/Modal.svelte';
  import ContactForm from '$lib/components/messages/ContactForm.svelte';
  import ShareButtons from '$lib/components/shared/ShareButtons.svelte';
  import LoadingSkeleton from '$lib/components/ui/LoadingSkeleton.svelte';
  import PropertyOverview from './PropertyOverview.svelte';
  import PropertyRoomsFeatures from './PropertyRoomsFeatures.svelte';
  import PropertyLocation from './PropertyLocation.svelte';
  import PropertyGallery from './PropertyGallery.svelte';

  export let data;
  
  let property = data.property;
  let activeTab = 'overview';
  let showContactModal = false;
  let mounted = false;

  // Tab configuration with compact design
  const tabs = [
    { 
      id: 'overview', 
      label: $t('property.tab.overview'),
      icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2V7z" /></svg>'
    },
    { 
      id: 'rooms', 
      label: $t('property.tab.rooms'),
      icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" /></svg>'
    },
    { 
      id: 'location', 
      label: $t('property.tab.location'),
      icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" /></svg>'
    },
    { 
      id: 'gallery', 
      label: $t('property.tab.gallery'),
      icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>'
    },
    { 
      id: 'contact', 
      label: $t('messages.title'),
      icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>'
    }
  ];

  // Reactive computed values
  $: isRTL = $locale === 'ar';
  $: pageTitle = property?.title || $t('property.title');
  $: pageDescription = property?.description || '';
  $: currentUrl = $page.url.toString();

  onMount(() => {
    mounted = true;
    if (property?.title) {
      document.title = `${property.title} - ${$t('app.name')}`;
    }
  });

  function handleTabChange(event) {
    activeTab = event.detail.id;
  }

  function handleContactSuccess() {
    showContactModal = false;
  }
</script>

<svelte:head>
  <title>{pageTitle} - {$t('app.name')}</title>
  <meta name="description" content={pageDescription} />
  <meta property="og:title" content={pageTitle} />
  <meta property="og:description" content={pageDescription} />
  <meta property="og:url" content={currentUrl} />
  {#if property?.main_image?.url}
    <meta property="og:image" content={property.main_image.url} />
  {/if}
</svelte:head>

<div class="min-h-screen bg-gray-50 dark:bg-gray-900">
  <div class="max-w-7xl mx-auto">
    {#if !mounted}
      <div class="px-4 sm:px-6 lg:px-8 py-4">
        <LoadingSkeleton type="propertyCard" />
      </div>
    {:else}
      <!-- Property Header - Compact Design -->
      <div class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 sticky top-0 z-40">
        <div class="px-4 sm:px-6 lg:px-8 py-3">
          <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <div class="flex-1 min-w-0">
              <!-- Breadcrumb - Compact -->
              <div class="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400 mb-2">
                <a href="/properties" class="hover:text-primary-600 dark:hover:text-primary-400 transition-colors">
                  {$t('properties.title')}
                </a>
                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
                <span class="truncate">{property.title}</span>
              </div>
              
              <!-- Title - Fluid Typography -->
              <h1 class="font-bold text-gray-900 dark:text-white mb-2" 
                  style="font-size: clamp(1rem, 2vw, 1.5rem); line-height: 1.3;">
                {property.title}
              </h1>
              
              <!-- Property Meta - Compact Icons -->
              <div class="flex flex-wrap items-center gap-3 text-gray-600 dark:text-gray-400" 
                   style="font-size: clamp(0.75rem, 1.5vw, 1rem);">
                {#if property.location}
                  <div class="flex items-center gap-1">
                    <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                    </svg>
                    <span>{property.location.city}, {property.location.state}</span>
                  </div>
                {/if}
                
                {#if property.market_value}
                  <div class="flex items-center gap-1">
                    <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span class="font-semibold text-primary-600 dark:text-primary-400">
                      ${property.market_value.toLocaleString()}
                    </span>
                  </div>
                {/if}
                
                {#if property.size_sqm}
                  <div class="flex items-center gap-1">
                    <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
                    </svg>
                    <span>{property.size_sqm} {$t('property.sqm')}</span>
                  </div>
                {/if}
              </div>
            </div>
            
            <!-- Action Buttons - Compact -->
            <div class="flex items-center gap-2 flex-shrink-0">
              <ShareButtons
                url={currentUrl}
                title={property.title}
                description={property.description}
                variant="compact"
              />
              
              <Button
                variant="primary"
                size="sm"
                on:click={() => showContactModal = true}
                class="h-8 px-3 text-xs font-medium shadow-md"
              >
                <svg class="w-3 h-3 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
                {$t('property.contactOwner')}
              </Button>
            </div>
          </div>
        </div>
      </div>

      <!-- Main Content -->
      <div class="px-4 sm:px-6 lg:px-8 py-4">
        <!-- Tabs Navigation - Compact Design -->
        <div class="mb-4">
          <Tabs
            {tabs}
            bind:activeTab
            variant="pills"
            size="sm"
            fullWidth={false}
            centered={false}
            iconPosition="left"
            on:change={handleTabChange}
            class="h-8"
          />
        </div>

        <!-- Tab Content -->
        <div class="tab-content">
          {#if activeTab === 'overview'}
            <PropertyOverview {property} />
          {:else if activeTab === 'rooms'}
            <PropertyRoomsFeatures {property} />
          {:else if activeTab === 'location'}
            <PropertyLocation {property} />
          {:else if activeTab === 'gallery'}
            <PropertyGallery {property} />
          {:else if activeTab === 'contact'}
            <div class="max-w-3xl mx-auto">
              <ContactForm
                {property}
                on:success={handleContactSuccess}
              />
            </div>
          {/if}
        </div>
      </div>
    {/if}
  </div>
</div>

<!-- Contact Modal -->
<Modal
  bind:show={showContactModal}
  title={$t('property.contactOwner')}
  maxWidth="lg"
>
  <ContactForm
    {property}
    compact={true}
    on:success={handleContactSuccess}
  />
</Modal>

<style>
  .tab-content {
    min-height: 300px;
    animation: fadeIn 0.2s ease-in-out;
  }
  
  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(8px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  
  /* Responsive typography using CSS custom properties for clamp support */
  :global(.property-title) {
    font-size: clamp(1rem, 2vw, 1.5rem);
  }
  
  :global(.property-text) {
    font-size: clamp(0.75rem, 1.5vw, 1rem);
  }
</style>