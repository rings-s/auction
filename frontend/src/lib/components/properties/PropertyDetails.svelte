<!-- components/properties/PropertyDetails.svelte -->
<script>
    import { onMount } from 'svelte';
    import { createEventDispatcher } from 'svelte';
    import { fade, fly } from 'svelte/transition';
    import { t, language } from '$lib/i18n';
    import { formatCurrency, formatDate } from '$lib/utils/formatters';
    import { isAuthenticated, currentUser } from '$lib/stores/auth';
    
    // UI Components
    import Gallery from '$lib/components/ui/Gallery.svelte';
    import Button from '$lib/components/ui/Button.svelte';
    import Card from '$lib/components/ui/Card.svelte';
    import Badge from '$lib/components/ui/Badge.svelte';
    import PropertyMap from '$lib/components/properties/PropertyMap.svelte';
    import PropertyFeatures from '$lib/components/properties/PropertyFeatures.svelte';
    import DocumentsList from '$lib/components/documents/DocumentsList.svelte';
    
    // Props
    export let property;
    
    // Local state
    let activeTab = 'description';
    let showShareModal = false;
    let favoriteStatus = false;
    let loadingFavorite = false;
    let carouselOptions = {};
    
    // Event dispatcher
    const dispatch = createEventDispatcher();
    
    // Determine if current user is the owner
    $: isOwner = $isAuthenticated && $currentUser && property?.owner?.id === $currentUser.id;
    
    // Computed properties for RTL support
    $: isRTL = $language === 'ar';
    
    // Update carousel options based on RTL status
    $: carouselOptions = {
      ...carouselOptions,
      rtl: isRTL
    };
    
    // Format property values
    $: formattedPrice = property?.estimated_value 
      ? formatCurrency(property.estimated_value) 
      : null;
    
    $: formattedArea = property?.area 
      ? `${property.area} ${$t('properties.property_area_unit')}` 
      : null;
    
    // Property type translation
    $: propertyType = property?.property_type 
      ? $t(`properties.types.${property.property_type.toLowerCase()}`) 
      : null;
    
    // Property status translation
    $: propertyStatus = property?.status 
      ? $t(`properties.status.${property.status.toLowerCase()}`) 
      : null;
    
    // Tabs configuration
    const tabs = [
      { id: 'description', label: $t('properties.property_description') },
      { id: 'features', label: $t('properties.property_features') },
      { id: 'location', label: $t('properties.property_location') },
      { id: 'documents', label: $t('properties.property_documents') }
    ];
    
    // Toggle favorite status
    async function toggleFavorite() {
      if (!$isAuthenticated) {
        // Redirect to login if not authenticated
        window.location.href = `/auth/login?redirect=/properties/${property.id}`;
        return;
      }
      
      loadingFavorite = true;
      
      try {
        // API call would go here
        favoriteStatus = !favoriteStatus;
      } catch (err) {
        console.error('Error toggling favorite:', err);
      } finally {
        loadingFavorite = false;
      }
    }
    
    // Contact property owner
    function contactOwner() {
      dispatch('contactOwner');
    }
    
    // Toggle share modal
    function toggleShareModal() {
      showShareModal = !showShareModal;
    }
    
    // Copy link to clipboard
    function copyLink() {
      const url = window.location.href;
      navigator.clipboard.writeText(url);
      // Show success toast
    }
    
    // Share on social media
    function shareOnSocial(platform) {
      const url = encodeURIComponent(window.location.href);
      const title = encodeURIComponent(property.title);
      
      let shareUrl = '';
      
      switch (platform) {
        case 'facebook':
          shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${url}`;
          break;
        case 'twitter':
          shareUrl = `https://twitter.com/intent/tweet?url=${url}&text=${title}`;
          break;
        case 'whatsapp':
          shareUrl = `https://wa.me/?text=${title}%20${url}`;
          break;
        case 'telegram':
          shareUrl = `https://t.me/share/url?url=${url}&text=${title}`;
          break;
      }
      
      if (shareUrl) {
        window.open(shareUrl, '_blank');
      }
    }
    
    onMount(() => {
      // Check if property is in favorites on mount
      if ($isAuthenticated) {
        // API call to check favorite status would go here
      }
    });
  </script>
  
  <div class="property-details-container" class:rtl={isRTL}>
    <!-- Hero Section with Property Images -->
    <section class="relative bg-neutral-100 dark:bg-neutral-900">
      {#if property?.main_image_url || property?.images?.length > 0}
        <Gallery 
          images={property.images || [property.main_image_url]} 
          options={carouselOptions}
        />
      {:else}
        <div class="h-80 bg-neutral-200 dark:bg-neutral-800 flex items-center justify-center">
          <span class="text-neutral-500 dark:text-neutral-400">
            {$t('properties.no_images')}
          </span>
        </div>
      {/if}
      
      <!-- Property Basic Info Overlay -->
      <div class="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent p-4 md:p-6">
        <div class="container mx-auto">
          <div class="flex flex-col md:flex-row items-start md:items-end justify-between">
            <div>
              <h1 class="text-2xl md:text-3xl lg:text-4xl font-bold text-white mb-2">
                {property?.title}
              </h1>
              <p class="text-white/90 flex items-center space-x-2 text-sm md:text-base">
                <span>{property?.address}</span>
                {#if property?.city}
                  <span class="mx-1">•</span>
                  <span>{property?.city}</span>
                {/if}
                {#if property?.district}
                  <span class="mx-1">•</span>
                  <span>{property?.district}</span>
                {/if}
              </p>
            </div>
            
            <div class="mt-4 md:mt-0">
              {#if formattedPrice}
                <div class="text-xl md:text-2xl font-bold text-white">
                  {formattedPrice}
                </div>
              {/if}
              
              {#if propertyStatus}
                <Badge 
                  type={property?.status === 'available' ? 'success' : 
                       property?.status === 'pending' ? 'warning' :
                       property?.status === 'sold' ? 'error' : 'info'}
                  size="lg"
                  class="mt-2"
                >
                  {propertyStatus}
                </Badge>
              {/if}
            </div>
          </div>
        </div>
      </div>
    </section>
    
    <!-- Main Content -->
    <section class="container mx-auto px-4 py-8">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Left Column: Property Details -->
        <div class="lg:col-span-2">
          <!-- Property Key Features -->
          <Card class="mb-6" padding={true}>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
              {#if propertyType}
                <div class="text-center property-feature-item">
                  <div class="feature-icon flex justify-center mb-2">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-primary" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
                      <polyline points="9 22 9 12 15 12 15 22"></polyline>
                    </svg>
                  </div>
                  <div class="property-info-label text-sm text-neutral-500 dark:text-neutral-400">
                    {$t('properties.property_type')}
                  </div>
                  <div class="property-info-value font-medium mt-1">
                    {propertyType}
                  </div>
                </div>
              {/if}
              
              {#if property?.bedrooms}
                <div class="text-center property-feature-item">
                  <div class="feature-icon flex justify-center mb-2">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-primary" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M20 9v4a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V9a2 2 0 0 1 2-2h10"></path>
                      <path d="M2 16v1a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-1"></path>
                      <path d="M22 5V7a2 2 0 0 1-2 2h-7.2"></path>
                    </svg>
                  </div>
                  <div class="property-info-label text-sm text-neutral-500 dark:text-neutral-400">
                    {$t('properties.bedrooms')}
                  </div>
                  <div class="property-info-value font-medium mt-1">
                    {property.bedrooms}
                  </div>
                </div>
              {/if}
              
              {#if property?.bathrooms}
                <div class="text-center property-feature-item">
                  <div class="feature-icon flex justify-center mb-2">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-primary" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M9 6 6.5 3.5a1.5 1.5 0 0 0-1-.5C4.683 3 4 3.683 4 4.5V17a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-5"></path>
                      <line x1="10" y1="12" x2="16" y2="12"></line>
                    </svg>
                  </div>
                  <div class="property-info-label text-sm text-neutral-500 dark:text-neutral-400">
                    {$t('properties.bathrooms')}
                  </div>
                  <div class="property-info-value font-medium mt-1">
                    {property.bathrooms}
                  </div>
                </div>
              {/if}
              
              {#if formattedArea}
                <div class="text-center property-feature-item">
                  <div class="feature-icon flex justify-center mb-2">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-primary" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                      <line x1="9" y1="3" x2="9" y2="21"></line>
                      <line x1="15" y1="3" x2="15" y2="21"></line>
                      <line x1="3" y1="9" x2="21" y2="9"></line>
                      <line x1="3" y1="15" x2="21" y2="15"></line>
                    </svg>
                  </div>
                  <div class="property-info-label text-sm text-neutral-500 dark:text-neutral-400">
                    {$t('properties.property_area')}
                  </div>
                  <div class="property-info-value font-medium mt-1">
                    {formattedArea}
                  </div>
                </div>
              {/if}
            </div>
          </Card>
          
          <!-- Property Tabs -->
          <Card class="mb-6" padding={false}>
            <!-- Tab Headers -->
            <div class="tab-header flex overflow-x-auto border-b border-neutral-200 dark:border-neutral-700">
              {#each tabs as tab}
                <button
                  class="px-4 py-3 text-sm font-medium transition whitespace-nowrap
                        {activeTab === tab.id 
                          ? 'text-primary border-b-2 border-primary'
                          : 'text-neutral-600 dark:text-neutral-300 hover:text-primary'}"
                  on:click={() => activeTab = tab.id}
                >
                  {tab.label}
                </button>
              {/each}
            </div>
            
            <!-- Tab Content -->
            <div class="p-4">
              {#if activeTab === 'description'}
                <div in:fade={{duration: 200}}>
                  {#if property?.description}
                    <div class="prose dark:prose-invert max-w-none">
                      {@html property.description}
                    </div>
                  {:else}
                    <p class="text-neutral-500 dark:text-neutral-400">
                      {$t('properties.no_description')}
                    </p>
                  {/if}
                </div>
              {/if}
              
              {#if activeTab === 'features'}
                <div in:fade={{duration: 200}}>
                  <PropertyFeatures property={property} />
                </div>
              {/if}
              
              {#if activeTab === 'location'}
                <div in:fade={{duration: 200}}>
                  {#if property?.location}
                    <PropertyMap location={property.location} title={property.title} />
                  {:else}
                    <div class="flex flex-col items-center justify-center bg-neutral-100 dark:bg-neutral-800 p-8 rounded-lg">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-neutral-400 mb-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M12 22s-8-4.5-8-11.8a8 8 0 0 1 16 0c0 7.3-8 11.8-8 11.8z" />
                        <circle cx="12" cy="10" r="3" />
                      </svg>
                      <p class="text-neutral-500 text-center">
                        {$t('properties.no_location')}
                      </p>
                    </div>
                  {/if}
                  
                  {#if property?.address || property?.city || property?.district || property?.country}
                    <div class="mt-4 space-y-2">
                      {#if property?.address}
                        <div class="flex items-start">
                          <span class="text-neutral-500 dark:text-neutral-400 min-w-32">
                            {$t('properties.property_address')}:
                          </span>
                          <span class="font-medium">
                            {property.address}
                          </span>
                        </div>
                      {/if}
                      
                      {#if property?.city}
                        <div class="flex items-start">
                          <span class="text-neutral-500 dark:text-neutral-400 min-w-32">
                            {$t('properties.property_city')}:
                          </span>
                          <span class="font-medium">
                            {property.city}
                          </span>
                        </div>
                      {/if}
                      
                      {#if property?.district}
                        <div class="flex items-start">
                          <span class="text-neutral-500 dark:text-neutral-400 min-w-32">
                            {$t('properties.property_district')}:
                          </span>
                          <span class="font-medium">
                            {property.district}
                          </span>
                        </div>
                      {/if}
                      
                      {#if property?.country}
                        <div class="flex items-start">
                          <span class="text-neutral-500 dark:text-neutral-400 min-w-32">
                            {$t('properties.property_country')}:
                          </span>
                          <span class="font-medium">
                            {property.country}
                          </span>
                        </div>
                      {/if}
                    </div>
                  {/if}
                </div>
              {/if}
              
              {#if activeTab === 'documents'}
                <div in:fade={{duration: 200}}>
                  {#if property?.documents && property.documents.length > 0}
                    <DocumentsList documents={property.documents} />
                  {:else}
                    <p class="text-neutral-500 dark:text-neutral-400">
                      {$t('properties.no_documents')}
                    </p>
                  {/if}
                </div>
              {/if}
            </div>
          </Card>
        </div>
        
        <!-- Right Column: Actions & Owner Info -->
        <div>
          <!-- Owner Information Card -->
          <Card padding={true} class="mb-6">
            <h3 class="text-lg font-semibold mb-4">{$t('properties.property_owner')}</h3>
            
            {#if property?.owner}
              <div class="flex items-center">
                {#if property.owner.avatar_url}
                  <img 
                    src={property.owner.avatar_url} 
                    alt={property.owner.full_name} 
                    class="h-12 w-12 rounded-full object-cover mr-3"
                  />
                {:else}
                  <div class="h-12 w-12 rounded-full bg-primary text-white flex items-center justify-center text-xl font-medium mr-3">
                    {property.owner.full_name ? property.owner.full_name[0].toUpperCase() : 'U'}
                  </div>
                {/if}
                
                <div>
                  <div class="font-medium">{property.owner.full_name}</div>
                  <div class="text-sm text-neutral-500 dark:text-neutral-400">
                    {property.owner.email}
                  </div>
                </div>
              </div>
              
              <div class="mt-4 flex flex-col space-y-3">
                <Button 
                  variant="primary" 
                  size="lg"
                  class="w-full"
                  on:click={contactOwner}
                  disabled={isOwner}
                >
                  {#if isOwner}
                    {$t('properties.own_property')}
                  {:else}
                    {$t('properties.contact_owner')}
                  {/if}
                </Button>
              </div>
            {:else}
              <p class="text-neutral-500 dark:text-neutral-400">
                {$t('properties.owner_info_unavailable')}
              </p>
            {/if}
          </Card>
          
          <!-- Property Actions Card -->
          <Card padding={true} class="mb-6">
            <h3 class="text-lg font-semibold mb-4">{$t('properties.actions')}</h3>
            
            <div class="flex flex-col space-y-3">
              <Button 
                variant="secondary"
                size="lg"
                class="w-full"
                on:click={toggleFavorite}
                loading={loadingFavorite}
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 24 24" fill={favoriteStatus ? "currentColor" : "none"} stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z" />
                </svg>
                {favoriteStatus 
                  ? $t('properties.remove_from_favorites') 
                  : $t('properties.add_to_favorites')}
              </Button>
              
              <Button 
                variant="outline"
                size="lg"
                class="w-full"
                on:click={toggleShareModal}
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8" />
                  <polyline points="16 6 12 2 8 6" />
                  <line x1="12" y1="2" x2="12" y2="15" />
                </svg>
                {$t('properties.share_property')}
              </Button>
            </div>
          </Card>
          
          <!-- Property Details Card -->
          <Card padding={true}>
            <h3 class="text-lg font-semibold mb-4">{$t('properties.additional_details')}</h3>
            
            <div class="space-y-3">
              {#if property?.property_number}
                <div class="flex items-start justify-between">
                  <span class="text-neutral-500 dark:text-neutral-400">
                    {$t('properties.property_number')}:
                  </span>
                  <span class="font-medium text-right">
                    {property.property_number}
                  </span>
                </div>
              {/if}
              
              {#if property?.build_year}
                <div class="flex items-start justify-between">
                  <span class="text-neutral-500 dark:text-neutral-400">
                    {$t('properties.build_year')}:
                  </span>
                  <span class="font-medium text-right">
                    {property.build_year}
                  </span>
                </div>
              {/if}
              
              {#if property?.floor_number}
                <div class="flex items-start justify-between">
                  <span class="text-neutral-500 dark:text-neutral-400">
                    {$t('properties.floor_number')}:
                  </span>
                  <span class="font-medium text-right">
                    {property.floor_number}
                  </span>
                </div>
              {/if}
              
              {#if property?.facing_direction}
                <div class="flex items-start justify-between">
                  <span class="text-neutral-500 dark:text-neutral-400">
                    {$t('properties.facing_direction')}:
                  </span>
                  <span class="font-medium text-right">
                    {property.facing_direction}
                  </span>
                </div>
              {/if}
              
              {#if property?.is_verified}
                <div class="flex items-start justify-between">
                  <span class="text-neutral-500 dark:text-neutral-400">
                    {$t('properties.verified')}:
                  </span>
                  <span class="font-medium text-right text-green-600 dark:text-green-400 flex items-center">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                      <polyline points="22 4 12 14.01 9 11.01" />
                    </svg>
                    {$t('properties.verified_property')}
                  </span>
                </div>
              {/if}
              
              {#if property?.created_at}
                <div class="flex items-start justify-between">
                  <span class="text-neutral-500 dark:text-neutral-400">
                    {$t('properties.listed_on')}:
                  </span>
                  <span class="font-medium text-right">
                    {formatDate(property.created_at)}
                  </span>
                </div>
              {/if}
            </div>
          </Card>
        </div>
      </div>
    </section>
    
    <!-- Share Modal -->
    {#if showShareModal}
      <div 
        class="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
        transition:fade={{duration: 200}}
        on:click|self={toggleShareModal}
      >
        <Card 
          class="w-full max-w-md"
          padding={true}
          in:fly={{y: 20, duration: 300}}
        >
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-xl font-bold">{$t('properties.share_property')}</h3>
            <button 
              class="h-8 w-8 rounded-full flex items-center justify-center text-neutral-500 hover:bg-neutral-100 dark:hover:bg-neutral-800"
              on:click={toggleShareModal}
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            </button>
          </div>
          
          <p class="mb-4">{$t('properties.share_via')}:</p>
          
          <div class="grid grid-cols-4 gap-3 mb-6">
            <!-- Social Media Buttons -->
            <button 
              class="flex flex-col items-center p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/30 transition"
              on:click={() => shareOnSocial('facebook')}
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-blue-600 dark:text-blue-400" viewBox="0 0 24 24" fill="currentColor">
                <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
              </svg>
              <span class="text-xs mt-1 text-blue-600 dark:text-blue-400">Facebook</span>
            </button>
            
            <button 
              class="flex flex-col items-center p-3 bg-sky-50 dark:bg-sky-900/20 rounded-lg hover:bg-sky-100 dark:hover:bg-sky-900/30 transition"
              on:click={() => shareOnSocial('twitter')}
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-sky-500 dark:text-sky-400" viewBox="0 0 24 24" fill="currentColor">
                <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z" />
              </svg>
              <span class="text-xs mt-1 text-sky-500 dark:text-sky-400">Twitter</span>
            </button>
            
            <button 
              class="flex flex-col items-center p-3 bg-green-50 dark:bg-green-900/20 rounded-lg hover:bg-green-100 dark:hover:bg-green-900/30 transition"
              on:click={() => shareOnSocial('whatsapp')}
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-green-600 dark:text-green-400" viewBox="0 0 24 24" fill="currentColor">
                <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z" />
              </svg>
              <span class="text-xs mt-1 text-green-600 dark:text-green-400">WhatsApp</span>
            </button>
            
            <button 
              class="flex flex-col items-center p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/30 transition"
              on:click={() => shareOnSocial('telegram')}
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-blue-500 dark:text-blue-400" viewBox="0 0 24 24" fill="currentColor">
                <path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z" />
              </svg>
              <span class="text-xs mt-1 text-blue-500 dark:text-blue-400">Telegram</span>
            </button>
          </div>
          
          <div class="mb-2">
            <label class="block text-sm font-medium mb-2">{$t('properties.copy_link')}:</label>
            <div class="flex">
              <input 
                type="text" 
                value={browser ? window.location.href : ''}
                readonly
                class="flex-1 rounded-l-lg border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-800 px-3 py-2 text-sm"
              />
              <button 
                class="bg-primary hover:bg-primary-dark text-white rounded-r-lg px-4 flex items-center justify-center"
                on:click={copyLink}
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                  <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                </svg>
              </button>
            </div>
          </div>
          
          <div class="pt-4 border-t border-neutral-200 dark:border-neutral-700 flex justify-end">
            <Button
              variant="primary"
              on:click={toggleShareModal}
            >
              {$t('general.close')}
            </Button>
          </div>
        </Card>
      </div>
    {/if}
  </div>
  
  <style>
    /* Base RTL styling */
    .rtl {
      direction: rtl;
      text-align: right;
    }
    
    /* RTL-specific styling for property features */
    .rtl .feature-icon {
      margin-right: 0;
      margin-left: 0.5rem;
    }
    
    /* RTL-specific styling for property details */
    .rtl .tab-header {
      flex-direction: row-reverse;
    }
    
    /* RTL-specific styling for property actions */
    .rtl svg.mr-2 {
      margin-right: 0;
      margin-left: 0.5rem;
    }
    
    /* RTL-specific styling for property info */
    .rtl .property-feature-item {
      text-align: center;
    }
    
    /* RTL-specific styling for carousel */
    .rtl :global(.carousel-arrow-prev) {
      left: auto;
      right: 1rem;
    }
    
    .rtl :global(.carousel-arrow-next) {
      right: auto;
      left: 1rem;
    }
    
    /* RTL-specific styling for text fields */
    .rtl input[type="text"] {
      text-align: right;
    }
    
    /* Fix spacing in RTL mode */
    .rtl .mr-3 {
      margin-right: 0;
      margin-left: 0.75rem;
    }
    
    /* Fix icon direction for RTL */
    .rtl .icon-flip-rtl {
      transform: scaleX(-1);
    }
    
    /* Fix form elements for RTL */
    @media (min-width: 768px) {
      .rtl .text-md-right {
        text-align: left;
      }
      
      .rtl .text-md-left {
        text-align: right;
      }
    }
  </style>