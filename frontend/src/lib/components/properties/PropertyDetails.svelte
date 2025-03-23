<!-- src/lib/components/properties/PropertyDetails.svelte -->
<script>
    /**
     * Property Details Component
     * Comprehensive component that displays all property information
     */
    import { onMount } from 'svelte';
    import { fade } from 'svelte/transition';
    import { t, isRTL, language } from '$lib/i18n';
    import { formatCurrency, formatDate} from '$lib/utils/formatters';
    import { api } from '$lib/services/api';
    
    import PropertyImages from './PropertyImages.svelte';
    import PropertyFeatures from './PropertyFeatures.svelte';
    import PropertyMap from './PropertyMap.svelte';
    import Card from '$lib/components/ui/Card.svelte';
    import Button from '$lib/components/ui/Button.svelte';
    import Badge from '$lib/components/ui/Badge.svelte';
    import Spinner from '$lib/components/ui/Spinner.svelte';
    import Alert from '$lib/components/ui/Alert.svelte';
    import Tabs from '$lib/components/ui/Tabs.svelte';
    import TabItem from '$lib/components/ui/TabItem.svelte';
    import Breadcrumb from '$lib/components/ui/Breadcrumb.svelte';
    
    // Props - Property ID to load
    export let propertyId = undefined;
    export let property = null; // Direct property object can be passed instead of loading via ID
    
    // State
    let loading = !property; // Only load if property is not directly provided
    let error = null;
    let relatedAuctions = [];
    let recommendedProperties = [];
    let activeTab = 'details'; // details, features, location, documents, auctions
    
    // Tabs configuration
    $: tabs = [
      { id: 'details', label: $t('properties.property_details') },
      { id: 'features', label: $t('properties.property_features') },
      { id: 'location', label: $t('properties.property_location') },
      ...(property?.documents?.length > 0 ? [{ id: 'documents', label: $t('properties.property_documents') }] : []),
      ...(relatedAuctions?.length > 0 ? [{ id: 'auctions', label: $t('properties.property_auctions') }] : [])
    ];
    
    // Breadcrumb configuration
    $: breadcrumbItems = [
      { label: $t('navigation.home'), href: '/' },
      { label: $t('navigation.properties'), href: '/properties' },
      { label: property?.title || $t('properties.property_details'), active: true }
    ];
    
    // Load property data
    async function loadProperty() {
      if (!propertyId || property) return;
      
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
          exclude: property.id
        });
        
        if (response?.data?.results) {
          recommendedProperties = response.data.results.slice(0, 4);
        }
      } catch (err) {
        console.error('Error fetching recommended properties:', err);
        // Non-critical, don't show error
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
              alert($t('general.copied'));
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
      if (!property && propertyId) {
        loadProperty();
      } else if (property && property.auctions) {
        // Extract related auctions from provided property data
        relatedAuctions = property.auctions;
      }
    });
    
    // Dispatch event when tab changes
    function handleTabChange(event) {
      activeTab = event.detail.tabId;
    }
  </script>
  
  <div class="property-details">
    <!-- Loading State -->
    {#if loading}
      <div class="my-16 flex justify-center">
        <Spinner size="lg" text={$t('general.loading')} />
      </div>
    
    <!-- Error State -->
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
    
    <!-- Property Content -->
    {:else if property}
      <div class="property-content" in:fade={{ duration: 300 }}>
        <!-- Breadcrumb -->
        <div class="mb-6">
          <Breadcrumb items={breadcrumbItems} />
        </div>
        
        <!-- Property Images -->
        <div class="mb-8">
          <PropertyImages 
            images={property.images || []} 
            mainImageUrl={property.main_image_url} 
            title={property.title}
          />
        </div>
        
        <!-- Main Content -->
        <div class="grid grid-cols-1 gap-8 lg:grid-cols-3">
          <!-- Main Content Area (Left) -->
          <div class="lg:col-span-2">
            <!-- Tab Navigation -->
            <div class="mb-6">
              <Tabs {tabs} activeTab={activeTab} on:change={handleTabChange} />
            </div>
            
            <!-- Tab Content -->
            <Card padding={true} bordered={true}>
              <TabItem id="details" active={activeTab === 'details'}>
                <!-- Property Description -->
                <div class="space-y-6">
                  <div>
                    <h2 class="mb-4 text-xl font-bold text-cosmos-text">{$t('properties.property_description')}</h2>
                    <div class="prose prose-invert max-w-none text-cosmos-text">
                      <p>{property.description || $t('properties.no_description')}</p>
                    </div>
                  </div>
                  
                  <!-- Key Details -->
                  <div>
                    <h3 class="mb-4 text-lg font-medium text-cosmos-text">{$t('properties.property_details')}</h3>
                    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                      <!-- Property Type -->
                      <div class="rounded-lg bg-cosmos-bg-light bg-opacity-20 p-4">
                        <div class="flex items-center">
                          <div class="mr-3 flex h-10 w-10 items-center justify-center rounded-full bg-primary bg-opacity-20">
                            <svg class="h-5 w-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                            </svg>
                          </div>
                          <div>
                            <p class="text-sm text-cosmos-text-muted">{$t('properties.property_type')}</p>
                            <p class="font-medium text-cosmos-text">{property.property_type_display || $t(`properties.types.${property.property_type}`)}</p>
                          </div>
                        </div>
                      </div>
                      
                      <!-- Property Area -->
                      <div class="rounded-lg bg-cosmos-bg-light bg-opacity-20 p-4">
                        <div class="flex items-center">
                          <div class="mr-3 flex h-10 w-10 items-center justify-center rounded-full bg-primary bg-opacity-20">
                            <svg class="h-5 w-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
                            </svg>
                          </div>
                          <div>
                            <p class="text-sm text-cosmos-text-muted">{$t('properties.property_area')}</p>
                            <p class="font-medium text-cosmos-text">{property.area} m²</p>
                          </div>
                        </div>
                      </div>
                      
                      {#if property.built_up_area}
                        <!-- Built Up Area -->
                        <div class="rounded-lg bg-cosmos-bg-light bg-opacity-20 p-4">
                          <div class="flex items-center">
                            <div class="mr-3 flex h-10 w-10 items-center justify-center rounded-full bg-primary bg-opacity-20">
                              <svg class="h-5 w-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 21h7a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                              </svg>
                            </div>
                            <div>
                              <p class="text-sm text-cosmos-text-muted">{$t('properties.built_up_area')}</p>
                              <p class="font-medium text-cosmos-text">{property.built_up_area} m²</p>
                            </div>
                          </div>
                        </div>
                      {/if}
                      
                      {#if property.bedrooms > 0}
                        <!-- Bedrooms -->
                        <div class="rounded-lg bg-cosmos-bg-light bg-opacity-20 p-4">
                          <div class="flex items-center">
                            <div class="mr-3 flex h-10 w-10 items-center justify-center rounded-full bg-primary bg-opacity-20">
                              <svg class="h-5 w-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                              </svg>
                            </div>
                            <div>
                              <p class="text-sm text-cosmos-text-muted">{$t('properties.bedrooms')}</p>
                              <p class="font-medium text-cosmos-text">{property.bedrooms}</p>
                            </div>
                          </div>
                        </div>
                      {/if}
                      
                      {#if property.bathrooms > 0}
                        <!-- Bathrooms -->
                        <div class="rounded-lg bg-cosmos-bg-light bg-opacity-20 p-4">
                          <div class="flex items-center">
                            <div class="mr-3 flex h-10 w-10 items-center justify-center rounded-full bg-primary bg-opacity-20">
                              <svg class="h-5 w-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                              </svg>
                            </div>
                            <div>
                              <p class="text-sm text-cosmos-text-muted">{$t('properties.bathrooms')}</p>
                              <p class="font-medium text-cosmos-text">{property.bathrooms}</p>
                            </div>
                          </div>
                        </div>
                      {/if}
                      
                      {#if property.year_built}
                        <!-- Year Built -->
                        <div class="rounded-lg bg-cosmos-bg-light bg-opacity-20 p-4">
                          <div class="flex items-center">
                            <div class="mr-3 flex h-10 w-10 items-center justify-center rounded-full bg-primary bg-opacity-20">
                              <svg class="h-5 w-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                              </svg>
                            </div>
                            <div>
                              <p class="text-sm text-cosmos-text-muted">{$t('properties.build_year')}</p>
                              <p class="font-medium text-cosmos-text">{property.year_built}</p>
                            </div>
                          </div>
                        </div>
                      {/if}
                      
                      {#if property.condition}
                        <!-- Condition -->
                        <div class="rounded-lg bg-cosmos-bg-light bg-opacity-20 p-4">
                          <div class="flex items-center">
                            <div class="mr-3 flex h-10 w-10 items-center justify-center rounded-full bg-primary bg-opacity-20">
                              <svg class="h-5 w-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                              </svg>
                            </div>
                            <div>
                              <p class="text-sm text-cosmos-text-muted">{$t('properties.property_condition')}</p>
                              <p class="font-medium text-cosmos-text">
                                {property.condition_display || $t(`properties.condition.${property.condition}`)}
                              </p>
                            </div>
                          </div>
                        </div>
                      {/if}
                      
                      {#if property.floor_number !== null && property.floor_number !== undefined}
                        <!-- Floor Number -->
                        <div class="rounded-lg bg-cosmos-bg-light bg-opacity-20 p-4">
                          <div class="flex items-center">
                            <div class="mr-3 flex h-10 w-10 items-center justify-center rounded-full bg-primary bg-opacity-20">
                              <svg class="h-5 w-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                              </svg>
                            </div>
                            <div>
                              <p class="text-sm text-cosmos-text-muted">{$t('properties.floor_number')}</p>
                              <p class="font-medium text-cosmos-text">{property.floor_number}</p>
                            </div>
                          </div>
                        </div>
                      {/if}
                    </div>
                  </div>
                </div>
              </TabItem>
              
              <TabItem id="features" active={activeTab === 'features'}>
                <!-- Property Features Tab -->
                <PropertyFeatures 
                  features={property.features || []} 
                  amenities={property.amenities || []}
                  outdoorSpaces={property.outdoor_spaces || {}}
                  parking={property.parking || {}}
                  buildingServices={property.building_services || {}}
                  infrastructure={property.infrastructure || {}}
                />
              </TabItem>
              
              <TabItem id="location" active={activeTab === 'location'}>
                <!-- Property Location Tab -->
                <div class="space-y-6">
                  <h2 class="text-xl font-bold text-cosmos-text">{$t('properties.property_location')}</h2>
                  
                  <!-- Address Information -->
                  <div class="grid grid-cols-1 gap-4 rounded-lg bg-cosmos-bg-light bg-opacity-20 p-5 sm:grid-cols-2">
                    <div>
                      <p class="text-sm text-cosmos-text-muted">{$t('properties.property_address')}</p>
                      <p class="font-medium text-cosmos-text">{property.address}</p>
                    </div>
                    
                    <div>
                      <p class="text-sm text-cosmos-text-muted">{$t('properties.property_district')}</p>
                      <p class="font-medium text-cosmos-text">{property.district}</p>
                    </div>
                    
                    <div>
                      <p class="text-sm text-cosmos-text-muted">{$t('properties.property_city')}</p>
                      <p class="font-medium text-cosmos-text">{property.city}</p>
                    </div>
                    
                    <div>
                      <p class="text-sm text-cosmos-text-muted">{$t('properties.property_country')}</p>
                      <p class="font-medium text-cosmos-text">{property.country}</p>
                    </div>
                    
                    {#if property.postal_code}
                      <div>
                        <p class="text-sm text-cosmos-text-muted">{$t('properties.property_postal_code')}</p>
                        <p class="font-medium text-cosmos-text">{property.postal_code}</p>
                      </div>
                    {/if}
                  </div>
                  
                  <!-- Map -->
                  <div class="overflow-hidden rounded-lg">
                    <div class="h-80 w-full">
                      {#if property.latitude && property.longitude}
                        <PropertyMap 
                          latitude={property.latitude} 
                          longitude={property.longitude}
                          address={property.address}
                          title={property.title}
                        />
                      {:else}
                        <div class="flex h-full w-full items-center justify-center bg-cosmos-bg-light">
                          <div class="text-center">
                            <svg class="mx-auto mb-2 h-10 w-10 text-cosmos-text-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 01.707-5.878M9.172 16.172a4 4 0 001.414-7.586l-1.414 1.414M9.172 16.172l-6.293 6.293M12 10l-3.293 3.293M13.828 13.828a4 4 0 01-5.656 0M9.172 17.172a4 4 0 01-5.656-5.656" />
                            </svg>
                            <p class="text-cosmos-text-muted">{$t('properties.no_location_data')}</p>
                          </div>
                        </div>
                      {/if}
                    </div>
                  </div>
                  
                  <!-- Surrounding Information -->
                  {#if property.surroundings && Object.keys(property.surroundings).length > 0}
                    <div class="mt-6">
                      <h3 class="mb-4 text-lg font-medium text-cosmos-text">{$t('properties.surroundings')}</h3>
                      <div class="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
                        {#each Object.entries(property.surroundings) as [key, value]}
                          <div class="rounded-lg bg-cosmos-bg-light bg-opacity-20 p-3">
                            <p class="text-sm text-cosmos-text-muted">{key}</p>
                            <p class="font-medium text-cosmos-text">{value}</p>
                          </div>
                        {/each}
                      </div>
                    </div>
                  {/if}
                </div>
              </TabItem>
              
              <TabItem id="documents" active={activeTab === 'documents'}>
                <!-- Property Documents Tab -->
                <div class="space-y-6">
                  <h2 class="text-xl font-bold text-cosmos-text">{$t('properties.property_documents')}</h2>
                  
                  <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
                    {#each property.documents || [] as document}
                      <div class="overflow-hidden rounded-lg border border-cosmos-bg-light bg-cosmos-bg-light bg-opacity-20 transition hover:bg-cosmos-bg-light hover:bg-opacity-30">
                        <div class="flex items-center p-4">
                          <div class="mr-4 flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-lg bg-primary bg-opacity-10">
                            <svg class="h-6 w-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                            </svg>
                          </div>
                          
                          <div class="flex-grow">
                            <h4 class="font-medium text-cosmos-text">{document.title}</h4>
                            <p class="text-sm text-cosmos-text-muted">{document.document_type_display}</p>
                          </div>
                          
                          {#if document.main_file_url}
                            <a 
                              href={document.main_file_url} 
                              target="_blank" 
                              rel="noopener noreferrer"
                              class="flex h-8 w-8 items-center justify-center rounded-md bg-primary bg-opacity-20 text-primary transition hover:bg-primary hover:text-white"
                              aria-label={$t('properties.download_document')}
                            >
                              <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                              </svg>
                            </a>
                          {/if}
                        </div>
                      </div>
                    {/each}
                  </div>
                  
                  {#if !property.documents || property.documents.length === 0}
                    <div class="rounded-lg bg-cosmos-bg-light bg-opacity-20 p-6 text-center">
                      <svg class="mx-auto mb-2 h-10 w-10 text-cosmos-text-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                      <p class="text-cosmos-text-muted">{$t('general.no_data_available')}</p>
                    </div>
                  {/if}
                </div>
              </TabItem>
              
              <TabItem id="auctions" active={activeTab === 'auctions'}>
                <!-- Property Auctions Tab -->
                <div class="space-y-6">
                  <h2 class="text-xl font-bold text-cosmos-text">{$t('properties.property_auctions')}</h2>
                  
                  <div class="space-y-4">
                    {#each relatedAuctions as auction}
                      <div class="overflow-hidden rounded-lg bg-cosmos-bg-light bg-opacity-20 transition hover:bg-cosmos-bg-light hover:bg-opacity-30">
                        <a href={`/auctions/${auction.id}`} class="block p-4">
                          <div class="flex flex-col justify-between space-y-4 sm:flex-row sm:items-center sm:space-y-0">
                            <div>
                              <h3 class="font-medium text-cosmos-text">{auction.title}</h3>
                              <div class="mt-1 flex flex-wrap items-center gap-2">
                                <Badge 
                                  value={auction.status_display || $t(`auctions.status.${auction.status}`)}
                                  variant={auction.status === 'active' ? 'success' : 
                                          auction.status === 'pending' ? 'warning' : 
                                          auction.status === 'extended' ? 'info' : 'error'}
                                  size="sm"
                                />
                                <span class="text-xs text-cosmos-text-muted">
                                  {$t('auctions.start_date')}: {formatDate(auction.start_date, {day: 'numeric', month: 'short', year: 'numeric'})}
                                </span>
                              </div>
                            </div>
                            
                            <div class="text-right">
                              <div class="text-xs text-cosmos-text-muted">{$t('auctions.current_bid')}</div>
                              <div class="text-lg font-bold text-primary">{formatCurrency(auction.current_bid)}</div>
                              
                              {#if auction.bid_count > 0}
                                <div class="mt-1 text-xs text-cosmos-text-muted">
                                  {auction.bid_count} {auction.bid_count === 1 ? $t('auctions.bid') : $t('auctions.bids')}
                                </div>
                              {/if}
                            </div>
                          </div>
                          
                          {#if auction.time_remaining > 0}
                            <div class="mt-4 flex items-center rounded-md bg-cosmos-bg-light bg-opacity-30 p-2">
                              <svg class="mr-2 h-4 w-4 text-cosmos-text-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                              </svg>
                              <span class="text-sm text-cosmos-text-muted">
                                {$t('auctions.ends_in')}: 
                                {Math.floor(auction.time_remaining / 86400)} {$t('auctions.days')}, 
                                {Math.floor((auction.time_remaining % 86400) / 3600)} {$t('auctions.hours')}
                              </span>
                            </div>
                          {/if}
                        </a>
                      </div>
                    {/each}
                  </div>
                  
                  {#if relatedAuctions.length === 0}
                    <div class="rounded-lg bg-cosmos-bg-light bg-opacity-20 p-6 text-center">
                      <svg class="mx-auto mb-2 h-10 w-10 text-cosmos-text-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <p class="text-cosmos-text-muted">{$t('properties.no_auctions')}</p>
                    </div>
                  {/if}
                </div>
              </TabItem>
            </Card>
          </div>
          
          <!-- Sidebar (Right Column) -->
          <div>
            <!-- Owner Information -->
            <Card class="mb-6" title={$t('properties.property_owner')}>
              {#if property && property.owner}
                <div class="flex items-center">
                  <div class="mr-4 h-14 w-14 overflow-hidden rounded-full bg-primary bg-opacity-20">
                    {#if property.owner.avatar_url}
                      <img 
                        src={property.owner.avatar_url} 
                        alt={property.owner.full_name || property.owner.email || $t('general.user')}
                        class="h-full w-full object-cover"
                      />
                    {:else}
                      <div class="flex h-full w-full items-center justify-center text-lg font-medium text-primary">
                        {property.owner.full_name 
                          ? property.owner.full_name.charAt(0).toUpperCase() 
                          : (property.owner.email 
                            ? property.owner.email.charAt(0).toUpperCase() 
                            : 'U')}
                      </div>
                    {/if}
                  </div>
                  
                  <div>
                    <p class="font-medium text-cosmos-text">
                      {property.owner.full_name || property.owner.email || $t('general.user')}
                    </p>
                    {#if property.owner.role}
                      <p class="text-sm text-cosmos-text-muted">
                        {$t(`auth.roles.${property.owner.role}`)}
                      </p>
                    {/if}
                  </div>
                </div>
                
                <div class="mt-4">
                  <Button
                    variant="primary"
                    fullWidth={true}
                    onClick={() => dispatch('contactOwner')}
                  >
                    <svg class="mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                    </svg>
                    {$t('properties.contact_owner')}
                  </Button>
                </div>
              {:else}
                <div class="rounded-lg bg-cosmos-bg-light bg-opacity-40 p-4 text-center">
                  <p class="text-cosmos-text-muted">{$t('general.no_data_available')}</p>
                </div>
              {/if}
            </Card>
            
            <!-- Property Key Stats -->
            <Card class="mb-6" title={$t('general.statistics')}>
              <div class="grid grid-cols-2 gap-4">
                {#if property && property.views_count !== undefined}
                  <div class="rounded-lg bg-cosmos-bg-light bg-opacity-30 p-3 text-center">
                    <div class="text-2xl font-bold text-primary">{property.views_count}</div>
                    <div class="text-sm text-cosmos-text-muted">{$t('general.views')}</div>
                  </div>
                {/if}
                
                {#if property && property.created_at}
                  <div class="rounded-lg bg-cosmos-bg-light bg-opacity-30 p-3 text-center">
                    <div class="text-sm font-bold text-primary">
                      {formatDate(property.created_at, {month: 'short', day: 'numeric', year: 'numeric'})}
                    </div>
                    <div class="text-sm text-cosmos-text-muted">{$t('general.created_at')}</div>
                  </div>
                {/if}
                
                {#if property && property.price_per_sqm}
                  <div class="rounded-lg bg-cosmos-bg-light bg-opacity-30 p-3 text-center">
                    <div class="text-lg font-bold text-primary">{formatCurrency(property.price_per_sqm)}</div>
                    <div class="text-sm text-cosmos-text-muted">{$t('general.per_sqm')}</div>
                  </div>
                {/if}
                
                {#if relatedAuctions && relatedAuctions.length > 0}
                  <div class="rounded-lg bg-cosmos-bg-light bg-opacity-30 p-3 text-center">
                    <div class="text-2xl font-bold text-primary">{relatedAuctions.length}</div>
                    <div class="text-sm text-cosmos-text-muted">{$t('auctions.title')}</div>
                  </div>
                {/if}
              </div>
            </Card>
            
            <!-- Share and Similar Properties -->
            <Card class="mb-6">
              <div class="space-y-3">
                <Button 
                  variant="outline"
                  fullWidth={true}
                  onClick={shareProperty}
                >
                  <svg class="mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
                  </svg>
                  {$t('properties.share_property')}
                </Button>
                
                <a 
                  href={`/search?property_type=${property.property_type}&city=${property.city}`} 
                  class="flex w-full items-center justify-center rounded-lg border border-cosmos-text-muted py-3 font-medium text-cosmos-text-muted transition hover:border-cosmos-text hover:text-cosmos-text"
                >
                  <svg class="mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                  {$t('properties.similar_properties')}
                </a>
              </div>
            </Card>
            
            <!-- Mini Map Preview -->
            {#if property.latitude && property.longitude}
              <div class="mb-6 overflow-hidden rounded-xl">
                <div class="h-40 w-full">
                  <PropertyMap 
                    latitude={property.latitude} 
                    longitude={property.longitude}
                    address={property.address}
                    title={property.title}
                    zoom={13}
                    interactive={false}
                  />
                </div>
              </div>
            {/if}
          </div>
        </div>
      </div>
    {/if}
  </div>
  
  <style>
    /* RTL adjustments */
    :global([dir="rtl"]) .property-details svg:not(.no-flip) {
      transform: scaleX(-1);
    }
    
    :global([dir="rtl"]) .property-details .mr-2,
    :global([dir="rtl"]) .property-details .mr-3,
    :global([dir="rtl"]) .property-details .mr-4 {
      margin-right: 0;
      margin-left: 0.5rem;
    }
  </style>