<!-- routes/properties/+page.svelte -->
<script>
    /**
     * Properties List Page
     * Displays a filterable grid of property listings with search capabilities
     */
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { t } from '$lib/i18n';
    import { fade } from 'svelte/transition';
    import { browser } from '$app/environment';
    
    // UI Components
    import PropertyGrid from '$lib/components/properties/PropertyGrid.svelte';
    import Alert from '$lib/components/ui/Alert.svelte';
    import Spinner from '$lib/components/ui/Spinner.svelte';
    import Card from '$lib/components/ui/Card.svelte';
    import Breadcrumb from '$lib/components/ui/Breadcrumb.svelte';
    import { toast } from '$lib/stores/toast';
    
    // Metadata for SEO
    const metaDescription = $t('properties.meta_description');
    
    // State
    let loading = true;
    let initialFilters = {};
    let title = $t('properties.all_properties');
    let error = null;
    
    // Breadcrumb configuration
    $: breadcrumbItems = [
      { label: $t('navigation.home'), href: '/' },
      { label: title, active: true }
    ];
    
    // Feature section items
    const features = [
      {
        icon: 'search',
        title: $t('properties.feature.search_title'),
        description: $t('properties.feature.search_description')
      },
      {
        icon: 'compare',
        title: $t('properties.feature.compare_title'),
        description: $t('properties.feature.compare_description')
      },
      {
        icon: 'auction',
        title: $t('properties.feature.auction_title'),
        description: $t('properties.feature.auction_description')
      }
    ];
    
    // Handle URL parameters to initialize filters
    function initializeFilters() {
      if (browser && $page.url.searchParams) {
        try {
          // Extract filter parameters from URL
          const params = $page.url.searchParams;
          
          initialFilters = {
            property_type: params.get('property_type') || '',
            status: params.get('status') || '',
            city: params.get('city') || '',
            district: params.get('district') || '',
            bedrooms: params.get('bedrooms') || '',
            bathrooms: params.get('bathrooms') || '',
            min_price: params.get('min_price') || '',
            max_price: params.get('max_price') || '',
            min_area: params.get('min_area') || '',
            max_area: params.get('max_area') || '',
            sort_by: params.get('sort_by') || 'created_at',
            order: params.get('order') || 'desc'
          };
          
          // Set title based on filters
          if (initialFilters.property_type) {
            // Translate property type from key to display name
            const propertyTypes = {
              'land': $t('properties.types.land'),
              'apartment': $t('properties.types.apartment'), 
              'villa': $t('properties.types.villa'),
              'commercial': $t('properties.types.commercial'),
              'building': $t('properties.types.building'),
              'farm': $t('properties.types.farm'),
              'industrial': $t('properties.types.industrial'),
              'office': $t('properties.types.office'),
              'retail': $t('properties.types.retail'),
              'mixed_use': $t('properties.types.mixed_use')
            };
            
            title = propertyTypes[initialFilters.property_type] || $t('properties.all_properties');
            
            if (initialFilters.city) {
              title += ` ${$t('properties.in')} ${initialFilters.city}`;
            }
          } else if (initialFilters.city) {
            title = `${$t('properties.properties_in')} ${initialFilters.city}`;
          }
        } catch (err) {
          console.error('Error parsing URL parameters:', err);
          error = $t('system_messages.error_occurred');
          toast.error($t('system_messages.error_occurred'));
        }
      }
      
      loading = false;
    }
    
    // Initialize the page
    onMount(() => {
      initializeFilters();
    });
    
    // Get icon SVG path based on feature type
    function getFeatureIcon(type) {
      switch(type) {
        case 'search':
          return 'M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z';
        case 'compare':
          return 'M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3';
        case 'auction':
          return 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01';
        default:
          return 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z';
      }
    }
  </script>
  
  <svelte:head>
    <title>{title} | {$t('general.app_name')}</title>
    <meta name="description" content={metaDescription} />
    <meta property="og:title" content={`${title} | ${$t('general.app_name')}`} />
    <meta property="og:description" content={metaDescription} />
    <meta property="og:type" content="website" />
  </svelte:head>
  
  <div class="min-h-screen bg-cosmos-bg pb-12">
    <!-- Hero Section -->
    <section aria-labelledby="properties-heading" class="bg-gradient-to-b from-cosmos-bg-dark to-cosmos-bg py-12">
      <div class="container mx-auto px-4">
        <div class="mx-auto max-w-4xl text-center md:text-left">
          <!-- Breadcrumb -->
          <div class="mb-4">
            <Breadcrumb items={breadcrumbItems} />
          </div>
          
          <h1 id="properties-heading" class="text-3xl font-bold text-cosmos-text md:text-4xl">{title}</h1>
          <p class="mt-3 text-lg text-cosmos-text-muted">
            {$t('properties.browse_description')}
          </p>
        </div>
      </div>
    </section>
    
    <!-- Main Content -->
    <section class="container mx-auto px-4 py-8">
      {#if error}
        <Alert type="error" dismissible={true} title={$t('general.error')}>
          {error}
        </Alert>
      {:else if loading}
        <div class="flex justify-center py-12">
          <Spinner size="lg" text={$t('general.loading')} />
        </div>
      {:else}
        <div in:fade={{ duration: 300 }}>
          <PropertyGrid 
            initialFilters={initialFilters}
            showFilters={true}
            title=""
          />
        </div>
      {/if}
    </section>
    
    <!-- Feature Callout Section -->
    <section aria-labelledby="features-heading" class="container mx-auto mt-8 px-4">
      <Card bordered={true} glass={true} padding={true} hover={false}>
        <h2 id="features-heading" class="mb-8 text-center text-2xl font-bold text-cosmos-text">
          {$t('properties.features_heading')}
        </h2>
        
        <div class="grid grid-cols-1 gap-8 md:grid-cols-3">
          {#each features as feature}
            <div class="text-center">
              <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-primary bg-opacity-10">
                <svg class="h-8 w-8 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={getFeatureIcon(feature.icon)} />
                </svg>
              </div>
              <h3 class="mt-4 text-lg font-medium text-cosmos-text">{feature.title}</h3>
              <p class="mt-2 text-cosmos-text-muted">{feature.description}</p>
            </div>
          {/each}
        </div>
      </Card>
    </section>
    
    <!-- Advanced Search Features (Collapsed by default) -->
    <section class="container mx-auto mt-12 px-4">
      <div class="rounded-xl bg-cosmos-bg-light bg-opacity-10 px-6 py-8 backdrop-blur-sm">
        <h2 class="mb-4 text-xl font-bold text-cosmos-text">{$t('properties.search_tips_heading')}</h2>
        
        <div class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          <div>
            <h3 class="text-lg font-medium text-cosmos-text">{$t('properties.search_by_area')}</h3>
            <p class="mt-2 text-sm text-cosmos-text-muted">{$t('properties.search_by_area_description')}</p>
          </div>
          
          <div>
            <h3 class="text-lg font-medium text-cosmos-text">{$t('properties.save_searches')}</h3>
            <p class="mt-2 text-sm text-cosmos-text-muted">{$t('properties.save_searches_description')}</p>
          </div>
          
          <div>
            <h3 class="text-lg font-medium text-cosmos-text">{$t('properties.notifications')}</h3>
            <p class="mt-2 text-sm text-cosmos-text-muted">{$t('properties.notifications_description')}</p>
          </div>
        </div>
      </div>
    </section>
  </div>