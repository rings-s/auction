<!-- src/lib/components/PropertyCard.svelte -->
<script>
  import { t, locale } from '$lib/i18n'; // Fixed import path
  
  export let property = {};

  // Computed value for RTL mode
  $: isRTL = $locale === 'ar';

  // Format currency based on locale
  const formatCurrency = (value) => {
    if (!value) return '';
    
    if ($locale === 'ar') {
      return new Intl.NumberFormat('ar-SA', {
        style: 'currency',
        currency: 'SAR',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
      }).format(value);
    }
    
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  };

  // Format date based on locale
  const formatDate = (dateString) => {
    if (!dateString) return '';
    
    const date = new Date(dateString);
    return date.toLocaleDateString($locale === 'ar' ? 'ar-SA' : 'en-US');
  };

  // Get status class
  const getStatusClass = (status) => {
    const classes = {
      available: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
      under_contract: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
      sold: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
      auction: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
    };
    return classes[status] || classes.available;
  };
  
  // Helper function to get image URL from any property data format
  function getImageUrl(property) {
    if (!property) return '/images/property-placeholder.jpg';
    
    // Check main_image property
    if (property.main_image) {
      // Could be direct URL or nested object
      if (typeof property.main_image === 'string') {
        return property.main_image;
      }
      
      // Check for url property first
      if (property.main_image.url) {
        return property.main_image.url;
      }
      
      // Then check for file property
      if (property.main_image.file) {
        return property.main_image.file;
      }
    }
    
    // Try media array (first item that's an image)
    if (property.media && property.media.length > 0) {
      const firstImage = property.media.find(m => 
        m.media_type === 'image' || 
        (m.url && typeof m.url === 'string')
      );
      
      if (firstImage) {
        return firstImage.url || firstImage.file || '/images/property-placeholder.jpg';
      }
    }
    
    // Default placeholder
    return '/images/property-placeholder.jpg';
  }

  // Get translated status text
  function getStatusText(status) {
    if (!status) return $t('property.statusTypes.available');
    
    const statusKey = `property.statusTypes.${status}`;
    const translated = $t(statusKey);
    
    // If translation not found, return the original status or default
    return translated !== statusKey ? translated : $t('property.statusTypes.available');
  }

  // Get translated property type
  function getPropertyTypeText(propertyType) {
    if (!propertyType) return '';
    
    // If it's an object with name property
    if (typeof propertyType === 'object' && propertyType.name) {
      return propertyType.name;
    }
    
    // If it's a string, try to translate it
    const typeKey = `nav.propertyTypes.${propertyType}`;
    const translated = $t(typeKey);
    
    return translated !== typeKey ? translated : propertyType;
  }
</script>

<a 
  href={`/properties/${property.slug || property.id}`} 
  class="block h-full group transform transition-all duration-300 hover:scale-[1.02] hover:shadow-xl"
>
  <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden transition-all duration-300 hover:shadow-2xl h-full flex flex-col border border-neutral-200 dark:border-neutral-700" dir={isRTL ? 'rtl' : 'ltr'}>
    <!-- Image Section -->
    <div class="relative h-56">
      <img 
        src={getImageUrl(property)} 
        alt={property.title || $t('property.title')}
        class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
        loading="lazy"
      />
      
      <!-- Status Badge -->
      <div class="absolute top-0 {isRTL ? 'left-0' : 'right-0'} m-2">
        <span class={`inline-flex items-center px-2.5 py-0.5 rounded-md text-sm font-medium ${getStatusClass(property.status)}`}>
          {getStatusText(property.status)}
        </span>
      </div>
      
      <!-- Featured Badge -->
      {#if property.is_featured}
        <div class="absolute top-0 {isRTL ? 'right-0' : 'left-0'} m-2">
          <span class="inline-flex items-center px-2.5 py-0.5 rounded-md text-sm font-medium bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200">
            {$t('property.featured')}
          </span>
        </div>
      {/if}
      
      <!-- Title Overlay -->
      <div class="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent p-4">
        <h3 class="text-lg font-semibold text-white truncate" title={property.title}>
          {property.title || $t('property.title')}
        </h3>
        <p class="text-sm text-gray-200">
          {#if property.location?.city || property.city}
            {property.location?.city || property.city}{#if property.location?.state || property.state}, {property.location?.state || property.state}{/if}
          {:else}
            {$t('property.noLocationData')}
          {/if}
        </p>
      </div>
    </div>
    
    <!-- Details Section -->
    <div class="p-4 flex-grow">
      <!-- Price and Type -->
      <div class="mb-3 flex justify-between items-center">
        <span class="inline-block bg-gray-100 dark:bg-gray-700 rounded-full px-3 py-1 text-sm font-semibold text-gray-700 dark:text-gray-300 truncate">
          {getPropertyTypeText(property.property_type || property.property_type_display)}
        </span>
        <span class="text-xl font-bold text-gray-900 dark:text-white">
          {formatCurrency(property.market_value)}
        </span>
      </div>
      
      <!-- Description -->
      {#if property.description}
        <p class="text-gray-600 dark:text-gray-300 line-clamp-2 text-sm mb-3">
          {property.description}
        </p>
      {/if}
      
      <!-- Property Stats -->
      <div class="grid grid-cols-2 gap-2 text-sm text-gray-500 dark:text-gray-400">
        <div class="flex items-center">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 {isRTL ? 'ml-1' : 'mr-1'}" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5v-4m0 4h-4m4 0l-5-5" />
          </svg>
          {property.size_sqm || 0} {$t('property.sqm')}
        </div>
        <div class="flex items-center">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 {isRTL ? 'ml-1' : 'mr-1'}" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
          </svg>
          {property.rooms?.length || 0} {$t('property.rooms')}
        </div>
      </div>
    </div>
    
    <!-- Footer Section -->
    <div class="border-t border-gray-200 dark:border-gray-700 p-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center text-sm text-gray-500 dark:text-gray-400">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 {isRTL ? 'ml-1' : 'mr-1'}" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          {formatDate(property.created_at)}
        </div>
        <span class="inline-flex items-center text-sm text-primary-600 dark:text-primary-400 font-medium">
          {$t('property.viewDetails')}
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 {isRTL ? 'mr-1' : 'ml-1'}" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={isRTL ? "M15 19l-7-7 7-7" : "M9 5l7 7-7 7"} />
          </svg>
        </span>
      </div>
    </div>
  </div>
</a>

<style>
  .line-clamp-2 {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
</style>