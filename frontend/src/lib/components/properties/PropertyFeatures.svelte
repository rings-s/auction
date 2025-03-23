<!-- src/lib/components/properties/PropertyFeatures.svelte -->
<script>
  /**
   * Property Features Component
   * Displays property features, amenities, and specifications in an organized layout
   */
  import { t, language } from '$lib/i18n';
  import Card from '$lib/components/ui/Card.svelte';
  import Badge from '$lib/components/ui/Badge.svelte';
  
  // Props - Property features and amenities
  export let features = []; // Array of features
  export let amenities = []; // Array of amenities
  export let outdoorSpaces = {}; // Object for outdoor spaces
  export let parking = {}; // Object for parking details
  export let buildingServices = {}; // Object for building services
  export let infrastructure = {}; // Object for infrastructure details
  
  // Helper function to get suitable icon for feature type
  function getFeatureIcon(feature) {
    // Predefined mapping for common features
    const iconMap = {
      // Indoor features
      'air_conditioning': 'M9.5 21V15m0 0L3 12m6.5 3l6.5-3m-13 0l6.5-3m0 0l6.5 3M3 9l6.5 3M16 21V15',
      'central_heating': 'M15 14.5l-3-3-3 3m5.5 0V18a2 2 0 01-2 2h-1a2 2 0 01-2-2v-3.5M13 8c-2.5 0-2.5 3.5 0 3.5 2.5 0 2.5-3.5 0-3.5z',
      'fireplace': 'M20.25 14.15v4.25c0 1.094-.787 2.036-1.872 2.18-2.087.277-4.216.42-6.378.42s-4.291-.143-6.378-.42c-1.085-.144-1.872-1.086-1.872-2.18v-4.25m16.5 0a2.18 2.18 0 00.75-1.661V8.706c0-1.081-.768-2.015-1.837-2.175a48.114 48.114 0 00-3.413-.387m4.5 8.006c-.194.165-.42.295-.673.38A23.978 23.978 0 0112 15.75c-2.648 0-5.195-.429-7.577-1.22a2.016 2.016 0 01-.673-.38m0 0A2.18 2.18 0 013 12.489V8.706c0-1.081.768-2.015 1.837-2.175a48.111 48.111 0 013.413-.387m7.5 0V5.25A2.25 2.25 0 0013.5 3h-3a2.25 2.25 0 00-2.25 2.25v.894m7.5 0a48.667 48.667 0 00-7.5 0M12 12.75h.008v.008H12v-.008z',
      'security_system': 'M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z',
      'elevator': 'M3 8.688c0-.864.933-1.405 1.683-.977l7.108 4.062a1.125 1.125 0 010 1.953l-7.108 4.062A1.125 1.125 0 013 16.81V8.688zM12.75 8.688c0-.864.933-1.405 1.683-.977l7.108 4.062a1.125 1.125 0 010 1.953l-7.108 4.062a1.125 1.125 0 01-1.683-.977V8.688z',
      'smart_home': 'M8.25 21v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21m0 0h4.5V3.545M12.75 21h7.5V10.75M2.25 21h1.5m18 0h-18M2.25 9l4.5-1.636M18.75 3l-1.5.545m0 6.205l3 1m1.5.5l-1.5-.5M6.75 7.364V3h-3v18m3-13.636l10.5-3.819',
      
      // Outdoor features
      'pool': 'M13.5 21v-7.5a.75.75 0 01.75-.75h3a.75.75 0 01.75.75V21m-4.5 0H2.36m11.14 0H18m0 0h3.64m-1.39 0V9.349m-16.5 11.65V9.35m0 0a3.001 3.001 0 003.75-.615A2.993 2.993 0 009.75 9.75c.896 0 1.7-.393 2.25-1.016a2.993 2.993 0 002.25 1.016c.896 0 1.7-.393 2.25-1.016a3.001 3.001 0 003.75.614m-16.5 0a3.004 3.004 0 01-.621-4.72L4.318 3.44A1.5 1.5 0 015.378 3h13.243a1.5 1.5 0 011.06.44l1.19 1.189a3 3 0 01-.621 4.72m-13.5 8.65h3.75a.75.75 0 00.75-.75V13.5a.75.75 0 00-.75-.75H6.75a.75.75 0 00-.75.75v3.75c0 .415.336.75.75.75z',
      'garden': 'M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 001.5-1.5V6a1.5 1.5 0 00-1.5-1.5H3.75A1.5 1.5 0 002.25 6v12a1.5 1.5 0 001.5 1.5zm10.5-11.25h.008v.008h-.008V8.25zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z',
      'balcony': 'M3.75 21h16.5M4.5 3h15M5.25 3v18m13.5-18v18M9 6.75h1.5m-1.5 3h1.5m-1.5 3h1.5m3-6H15m-1.5 3H15m-1.5 3H15M9 21v-3.375c0-.621.504-1.125 1.125-1.125h3.75c.621 0 1.125.504 1.125 1.125V21',
      'terrace': 'M13.5 21v-7.5a.75.75 0 01.75-.75h3a.75.75 0 01.75.75V21m-4.5 0H2.36m11.14 0H18m0 0h3.64m-1.39 0V9.349m-16.5 11.65V9.35m0 0a3.001 3.001 0 003.75-.615A2.993 2.993 0 009.75 9.75c.896 0 1.7-.393 2.25-1.016a2.993 2.993 0 002.25 1.016c.896 0 1.7-.393 2.25-1.016a3.001 3.001 0 003.75.614m-16.5 0a3.004 3.004 0 01-.621-4.72L4.318 3.44A1.5 1.5 0 015.378 3h13.243a1.5 1.5 0 011.06.44l1.19 1.189a3 3 0 01-.621 4.72m-13.5 8.65h3.75a.75.75 0 00.75-.75V13.5a.75.75 0 00-.75-.75H6.75a.75.75 0 00-.75.75v3.75c0 .415.336.75.75.75z',
      
      // Parking
      'garage': 'M8.25 18.75a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m3 0h6m-9 0H3.375a1.125 1.125 0 01-1.125-1.125V14.25m17.25 4.5a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m3 0h1.125c.621 0 1.129-.504 1.09-1.124a17.902 17.902 0 00-3.213-9.193 2.056 2.056 0 00-1.58-.86H14.25M16.5 18.75h-2.25m0-11.177v-.958c0-.568-.422-1.048-.987-1.106a48.554 48.554 0 00-10.026 0 1.106 1.106 0 00-.987 1.106v7.635m12-6.677v6.677m0 4.5v-4.5m0 0h-12',
      'parking': 'M8.25 18.75a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m3 0h6m-9 0H3.375a1.125 1.125 0 01-1.125-1.125V14.25m17.25 4.5a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m3 0h1.125c.621 0 1.129-.504 1.09-1.124a17.902 17.902 0 00-3.213-9.193 2.056 2.056 0 00-1.58-.86H14.25M16.5 18.75h-2.25m0-11.177v-.958c0-.568-.422-1.048-.987-1.106a48.554 48.554 0 00-10.026 0 1.106 1.106 0 00-.987 1.106v7.635m12-6.677v6.677m0 4.5v-4.5m0 0h-12',
      
      // Infrastructure
      'fiber_optic': 'M14.25 9.75L16.5 12l-2.25 2.25m-4.5 0L7.5 12l2.25-2.25M6 20.25h12A2.25 2.25 0 0020.25 18V6A2.25 2.25 0 0018 3.75H6A2.25 2.25 0 003.75 6v12A2.25 2.25 0 006 20.25z',
      'solar_panels': 'M12 3v2.25m6.364.386l-1.591 1.591M21 12h-2.25m-.386 6.364l-1.591-1.591M12 18.75V21m-4.773-4.227l-1.591 1.591M5.25 12H3m4.227-4.773L5.636 5.636',
      'water_supply': 'M12 3v2.25m6.364.386l-1.591 1.591M21 12h-2.25m-.386 6.364l-1.591-1.591M12 18.75V21m-4.773-4.227l-1.591 1.591M5.25 12H3m4.227-4.773L5.636 5.636M15 12a3 3 0 11-6 0 3 3 0 016 0z',
      
      // Default
      'default': 'M11.48 3.499a.562.562 0 011.04 0l2.125 5.111a.563.563 0 00.475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 00-.182.557l1.285 5.385a.562.562 0 01-.84.61l-4.725-2.885a.563.563 0 00-.586 0L6.982 20.54a.562.562 0 01-.84-.61l1.285-5.386a.562.562 0 00-.182-.557l-4.204-3.602a.563.563 0 01.321-.988l5.518-.442a.563.563 0 00.475-.345L11.48 3.5z'
    };
    
    // Convert feature to lowercase and normalize
    const normalizedFeature = String(feature).toLowerCase().replace(/\s+/g, '_');
    
    // Return path data if found, otherwise return default
    return iconMap[normalizedFeature] || iconMap.default;
  }
  
  // Check if object has values
  function hasValues(obj) {
    return obj && typeof obj === 'object' && Object.keys(obj).length > 0;
  }
  
  // Format feature name
  function formatFeatureName(name) {
    if (!name) return '';
    
    // Try to find translation
    const translationKey = `properties.features.${name.toLowerCase().replace(/\s+/g, '_')}`;
    const translated = $t(translationKey);
    
    // If translation exists (doesn't return the key itself), use it
    if (translated !== translationKey) {
      return translated;
    }
    
    // Otherwise, format the name by converting snake_case or camelCase to Title Case
    return name
      .replace(/([A-Z])/g, ' $1') // Insert space before capital letters
      .replace(/_/g, ' ') // Replace underscores with spaces
      .replace(/^\w/, c => c.toUpperCase()) // Capitalize first letter
      .trim();
  }
</script>

<div class="property-features space-y-8">
  <!-- Main Features -->
  {#if features && features.length > 0}
    <Card title={$t('properties.property_features')}>
      <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {#each features as feature}
          <div class="flex items-center space-x-2" role="listitem">
            <div class="flex h-8 w-8 items-center justify-center rounded-full bg-primary bg-opacity-10 flex-shrink-0">
              <svg class="h-5 w-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={getFeatureIcon(feature)} />
              </svg>
            </div>
            <span class="text-sm text-cosmos-text">{formatFeatureName(feature)}</span>
          </div>
        {/each}
      </div>
    </Card>
  {/if}
  
  <!-- Amenities -->
  {#if amenities && amenities.length > 0}
    <Card title={$t('properties.amenities')}>
      <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {#each amenities as amenity}
          <div class="flex items-center space-x-2" role="listitem">
            <div class="flex h-6 w-6 items-center justify-center rounded-full bg-cosmos-bg-light flex-shrink-0">
              <svg class="h-3 w-3 text-cosmos-text" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
              </svg>
            </div>
            <span class="text-sm text-cosmos-text">{formatFeatureName(amenity)}</span>
          </div>
        {/each}
      </div>
    </Card>
  {/if}
  
  <!-- Outdoor Spaces -->
  {#if hasValues(outdoorSpaces)}
    <Card title={$t('properties.outdoor_spaces')}>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {#each Object.entries(outdoorSpaces) as [key, value]}
          <div class="rounded-lg bg-cosmos-bg-light bg-opacity-20 p-4">
            <div class="flex items-center">
              <div class="mr-3 flex h-10 w-10 items-center justify-center rounded-full bg-primary bg-opacity-10 flex-shrink-0">
                <svg class="h-5 w-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={getFeatureIcon(key)} />
                </svg>
              </div>
              <div>
                <p class="text-sm font-medium text-cosmos-text">{formatFeatureName(key)}</p>
                {#if typeof value === 'object'}
                  <p class="text-xs text-cosmos-text-muted">
                    {#if value.size}
                      {value.size} m²
                    {/if}
                    {#if value.description}
                      {#if value.size} • {/if}
                      {value.description}
                    {/if}
                  </p>
                {:else if typeof value === 'string'}
                  <p class="text-xs text-cosmos-text-muted">{value}</p>
                {:else if typeof value === 'number'}
                  <p class="text-xs text-cosmos-text-muted">{value} m²</p>
                {:else if typeof value === 'boolean' && value}
                  <p class="text-xs text-cosmos-text-muted">{$t('general.available')}</p>
                {/if}
              </div>
            </div>
          </div>
        {/each}
      </div>
    </Card>
  {/if}
  
  <!-- Parking -->
  {#if hasValues(parking)}
    <Card title={$t('properties.parking')}>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {#if parking.spaces}
          <div class="rounded-lg bg-cosmos-bg-light bg-opacity-20 p-4">
            <p class="text-sm text-cosmos-text-muted">{$t('properties.parking_spaces')}</p>
            <p class="font-medium text-cosmos-text">{parking.spaces}</p>
          </div>
        {/if}
        
        {#if parking.type}
          <div class="rounded-lg bg-cosmos-bg-light bg-opacity-20 p-4">
            <p class="text-sm text-cosmos-text-muted">{$t('properties.parking_type')}</p>
            <p class="font-medium text-cosmos-text">{formatFeatureName(parking.type)}</p>
          </div>
        {/if}
        
        {#if parking.garage_size}
          <div class="rounded-lg bg-cosmos-bg-light bg-opacity-20 p-4">
            <p class="text-sm text-cosmos-text-muted">{$t('properties.garage_size')}</p>
            <p class="font-medium text-cosmos-text">{parking.garage_size} m²</p>
          </div>
        {/if}
        
        {#if parking.underground !== undefined}
          <div class="rounded-lg bg-cosmos-bg-light bg-opacity-20 p-4">
            <p class="text-sm text-cosmos-text-muted">{$t('properties.underground_parking')}</p>
            <p class="font-medium text-cosmos-text">
              {parking.underground ? $t('general.yes') : $t('general.no')}
            </p>
          </div>
        {/if}
        
        {#if parking.electric_vehicle_charging !== undefined}
          <div class="rounded-lg bg-cosmos-bg-light bg-opacity-20 p-4">
            <p class="text-sm text-cosmos-text-muted">{$t('properties.ev_charging')}</p>
            <p class="font-medium text-cosmos-text">
              {parking.electric_vehicle_charging ? $t('general.yes') : $t('general.no')}
            </p>
          </div>
        {/if}
      </div>
    </Card>
  {/if}
  
  <!-- Building Services -->
  {#if hasValues(buildingServices)}
    <Card title={$t('properties.building_services')}>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {#each Object.entries(buildingServices) as [key, value]}
          <div class="rounded-lg bg-cosmos-bg-light bg-opacity-20 p-4">
            <p class="text-sm text-cosmos-text-muted">{formatFeatureName(key)}</p>
            {#if typeof value === 'boolean'}
              <p class="font-medium text-cosmos-text">
                {value ? $t('general.yes') : $t('general.no')}
              </p>
            {:else if value}
              <p class="font-medium text-cosmos-text">{value}</p>
            {/if}
          </div>
        {/each}
      </div>
    </Card>
  {/if}
  
  <!-- Infrastructure -->
  {#if hasValues(infrastructure)}
    <Card title={$t('properties.infrastructure')}>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {#each Object.entries(infrastructure) as [key, value]}
          <div class="rounded-lg bg-cosmos-bg-light bg-opacity-20 p-4">
            <div class="flex items-center">
              <div class="mr-3 flex h-10 w-10 items-center justify-center rounded-full bg-primary bg-opacity-10 flex-shrink-0">
                <svg class="h-5 w-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={getFeatureIcon(key)} />
                </svg>
              </div>
              <div>
                <p class="text-sm font-medium text-cosmos-text">{formatFeatureName(key)}</p>
                {#if typeof value === 'string'}
                  <p class="text-xs text-cosmos-text-muted">{value}</p>
                {:else if typeof value === 'boolean'}
                  <p class="text-xs text-cosmos-text-muted">
                    {value ? $t('general.available') : $t('general.not_available')}
                  </p>
                {:else if typeof value === 'object' && value.available !== undefined}
                  <p class="text-xs text-cosmos-text-muted">
                    {value.available ? $t('general.available') : $t('general.not_available')}
                    {#if value.details}
                      • {value.details}
                    {/if}
                  </p>
                {/if}
              </div>
            </div>
          </div>
        {/each}
      </div>
    </Card>
  {/if}
  
  <!-- No Features Message -->
  {#if !features.length && !amenities.length && !hasValues(outdoorSpaces) && !hasValues(parking) && !hasValues(buildingServices) && !hasValues(infrastructure)}
    <div class="rounded-lg bg-cosmos-bg-light bg-opacity-50 p-6 text-center">
      <p class="text-cosmos-text-muted">{$t('properties.no_features_available')}</p>
    </div>
  {/if}
</div>