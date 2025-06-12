<!-- src/routes/properties/create/+page.svelte -->
<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { t, locale } from '$lib/i18n';
  import { user } from '$lib/stores/user';
  import { createProperty, uploadPropertyMediaBatch, addPropertyRoom } from '$lib/api/property';
  
  // Import new components
  import PropertyCreateHeader from '$lib/components/properties/create/PropertyCreateHeader.svelte';
  import PropertyCreateTabs from '$lib/components/properties/create/PropertyCreateTabs.svelte';
  import PropertyCreateFooter from '$lib/components/properties/create/PropertyCreateFooter.svelte';
  
  // Constants
  const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
  
  // Property form data structure - aligned with backend model
  let propertyData = {
    title: '',
    property_type: '',
    building_type: '',
    deed_number: '',
    description: '',
    size_sqm: '',
    floors: '',
    year_built: '',
    address: '',
    city: '',
    state: '',
    postal_code: '',
    country: 'المملكة العربية السعودية',
    latitude: null,
    longitude: null,
    market_value: '',
    minimum_bid: '',
    features: [],
    amenities: [],
    is_published: false,
    is_featured: false
  };
  
  // Feature/amenity lists with bilingual support
  let featuresList = [
    { code: 'swimming-pool', enName: 'Swimming Pool', arName: 'حمام سباحة' },
    { code: 'garden', enName: 'Garden', arName: 'حديقة' },
    { code: 'garage', enName: 'Garage', arName: 'مرآب' },
    { code: 'balcony', enName: 'Balcony', arName: 'شرفة' },
    { code: 'air-conditioning', enName: 'Air Conditioning', arName: 'تكييف' },
    { code: 'heating', enName: 'Heating', arName: 'تدفئة' },
    { code: 'elevator', enName: 'Elevator', arName: 'مصعد' },
    { code: 'security-system', enName: 'Security System', arName: 'نظام أمني' },
    { code: 'parking', enName: 'Parking', arName: 'موقف سيارات' },
    { code: 'gym', enName: 'Gym', arName: 'صالة رياضية' },
    { code: 'furnished', enName: 'Furnished', arName: 'مفروش' },
    { code: 'fireplace', enName: 'Fireplace', arName: 'موقد' },
    { code: 'storage', enName: 'Storage', arName: 'مخزن' },
    { code: 'laundry-room', enName: 'Laundry Room', arName: 'غرفة غسيل' }
  ];
  
  let amenitiesList = [
    { code: 'schools', enName: 'Schools', arName: 'مدارس' },
    { code: 'hospitals', enName: 'Hospitals', arName: 'مستشفيات' },
    { code: 'shopping-centers', enName: 'Shopping Centers', arName: 'مراكز تسوق' },
    { code: 'parks', enName: 'Parks', arName: 'حدائق عامة' },
    { code: 'public-transportation', enName: 'Public Transportation', arName: 'مواصلات عامة' },
    { code: 'restaurants', enName: 'Restaurants', arName: 'مطاعم' },
    { code: 'beach-access', enName: 'Beach Access', arName: 'وصول للشاطئ' },
    { code: 'sports-facilities', enName: 'Sports Facilities', arName: 'مرافق رياضية' },
    { code: 'university', enName: 'University', arName: 'جامعة' },
    { code: 'mosque', enName: 'Mosque', arName: 'مسجد' }
  ];
  
  let roomFeaturesList = [
    { code: 'window', enName: 'Window', arName: 'نافذة' },
    { code: 'air-conditioning', enName: 'Air Conditioning', arName: 'تكييف' },
    { code: 'heating', enName: 'Heating', arName: 'تدفئة' },
    { code: 'bathroom', enName: 'Bathroom', arName: 'حمام' },
    { code: 'walk-in-closet', enName: 'Walk-in Closet', arName: 'خزانة كبيرة' },
    { code: 'built-in-wardrobe', enName: 'Built-in Wardrobe', arName: 'خزانة مدمجة' },
    { code: 'ceiling-fan', enName: 'Ceiling Fan', arName: 'مروحة سقف' }
  ];
  
  // Localize feature/amenity names based on selected language
  $: availableFeatures = featuresList.map(item => $locale === 'ar' ? item.arName : item.enName);
  $: availableAmenities = amenitiesList.map(item => $locale === 'ar' ? item.arName : item.enName);
  $: availableRoomFeatures = roomFeaturesList.map(item => $locale === 'ar' ? item.arName : item.enName);
  
  // State management
  let loading = false;
  let error = null;
  let success = null;
  let mediaFiles = [];
  let showSuccessModal = false;
  let createdPropertyId = null;
  let uploadProgress = 0;
  let uploadingMedia = false;
  let rooms = [];
  let validationErrors = {};
  
  // Property types options
  $: propertyTypeOptions = [
    { value: 'residential', label: $locale === 'ar' ? 'سكني' : 'Residential' },
    { value: 'commercial', label: $locale === 'ar' ? 'تجاري' : 'Commercial' },
    { value: 'industrial', label: $locale === 'ar' ? 'صناعي' : 'Industrial' },
    { value: 'land', label: $locale === 'ar' ? 'أرض' : 'Land' },
    { value: 'agricultural', label: $locale === 'ar' ? 'زراعي' : 'Agricultural' },
    { value: 'mixed_use', label: $locale === 'ar' ? 'متعدد الاستخدامات' : 'Mixed Use' }
  ];
  
  // Building types options
  $: buildingTypeOptions = [
    { value: 'apartment', label: $locale === 'ar' ? 'شقة' : 'Apartment' },
    { value: 'villa', label: $locale === 'ar' ? 'فيلا' : 'Villa' },
    { value: 'house', label: $locale === 'ar' ? 'منزل' : 'House' },
    { value: 'office', label: $locale === 'ar' ? 'مكتب' : 'Office' },
    { value: 'retail', label: $locale === 'ar' ? 'محل تجاري' : 'Retail' },
    { value: 'warehouse', label: $locale === 'ar' ? 'مستودع' : 'Warehouse' },
    { value: 'other', label: $locale === 'ar' ? 'أخرى' : 'Other' }
  ];
  
  // Multi-step form management
  let currentStep = 1;
  const totalSteps = 4;
  
  // Event handlers
  function handleLocationChange(event) {
    const locationData = event.detail;
    propertyData = { ...propertyData, ...locationData };
  }
  
  function handleFeaturesChange(event) {
    propertyData.features = event.detail;
  }
  
  function handleAmenitiesChange(event) {
    propertyData.amenities = event.detail;
  }
  
  function handleRoomsChange(event) {
    rooms = event.detail;
  }
  
  function handleMediaChange(event) {
    mediaFiles = event.detail.files;
  }
  
  // Form validation by step
  function validateStep(step) {
    validationErrors = {};
    
    if (step === 1) {
      // Basic info validation
      if (!propertyData.title) {
        validationErrors.title = $t('validation.titleRequired');
      } else if (propertyData.title.length > 255) {
        validationErrors.title = $t('validation.titleTooLong');
      }
      
      if (!propertyData.property_type) {
        validationErrors.property_type = $t('validation.propertyTypeRequired');
      }
      
      if (!propertyData.deed_number) {
        validationErrors.deed_number = $t('validation.deedNumberRequired');
      }
      
      if (!propertyData.description) {
        validationErrors.description = $t('validation.descriptionRequired');
      }
    }
    
    else if (step === 2) {
      // Location validation
      if (!propertyData.address) {
        validationErrors.address = $t('validation.addressRequired');
      } else if (propertyData.address.length > 255) {
        validationErrors.address = $t('validation.addressTooLong');
      }
      
      if (!propertyData.city) {
        validationErrors.city = $t('validation.cityRequired');
      } else if (propertyData.city.length > 100) {
        validationErrors.city = $t('validation.cityTooLong');
      }
      
      if (!propertyData.state) {
        validationErrors.state = $t('validation.stateRequired');
      } else if (propertyData.state.length > 100) {
        validationErrors.state = $t('validation.stateTooLong');
      }
      
      if (propertyData.postal_code && propertyData.postal_code.length > 20) {
        validationErrors.postal_code = $t('validation.postalCodeTooLong');
      }
    }
    
    else if (step === 3) {
      // Property details validation
      if (!propertyData.size_sqm) {
        validationErrors.size_sqm = $t('validation.sizeRequired');
      } else {
        const size = parseFloat(propertyData.size_sqm);
        if (isNaN(size) || size <= 0) {
          validationErrors.size_sqm = $t('validation.invalidSizeFormat');
        }
      }
      
      if (propertyData.floors) {
        const floors = parseInt(propertyData.floors);
        if (isNaN(floors) || floors < 0) {
          validationErrors.floors = $t('validation.invalidFloorsFormat');
        }
      }
      
      if (propertyData.year_built) {
        const year = parseInt(propertyData.year_built);
        if (isNaN(year) || year < 1800 || year > new Date().getFullYear() + 1) {
          validationErrors.year_built = $t('validation.invalidYearFormat');
        }
      }
    }
    
    else if (step === 4) {
      // Financial validation
      if (!propertyData.market_value) {
        validationErrors.market_value = $t('validation.marketValueRequired');
      } else {
        const value = parseFloat(propertyData.market_value);
        if (isNaN(value) || value <= 0) {
          validationErrors.market_value = $t('validation.invalidMarketValueFormat');
        }
      }
      
      if (propertyData.minimum_bid) {
        const minBid = parseFloat(propertyData.minimum_bid);
        if (isNaN(minBid) || minBid <= 0) {
          validationErrors.minimum_bid = $t('validation.invalidMinimumBidFormat');
        } else if (propertyData.market_value && minBid >= parseFloat(propertyData.market_value)) {
          validationErrors.minimum_bid = $t('validation.invalidMinimumBidRange');
        }
      }
    }
    
    return Object.keys(validationErrors).length === 0;
  }
  
  // Navigation functions
  function goToNextStep() {
    if (validateStep(currentStep)) {
      if (currentStep < totalSteps) {
        currentStep++;
        window.scrollTo(0, 0);
      }
    }
  }
  
  function goToPrevStep() {
    if (currentStep > 1) {
      currentStep--;
      window.scrollTo(0, 0);
    }
  }
  
  // Form submission handler
  async function handleSubmit() {
    if (!validateStep(currentStep)) {
      return;
    }
    
    loading = true;
    error = null;
    
    try {
      // Step 1: Create the property without rooms first
      const propertySubmissionData = {
        ...propertyData
      };
      
      // Submit property data
      const result = await createProperty(propertySubmissionData);
      
      // Extract property ID from response
      createdPropertyId = result.id || (result.data && result.data.id);
      
      // Step 2: If we have rooms and a property ID, create rooms separately
      if (rooms.length > 0 && createdPropertyId) {
        try {
          // Create each room for the property
          const roomPromises = rooms.map(async (room) => {
            try {
              // Clean up room data before submission
              const roomData = { ...room };
              // Remove temporary IDs
              if (roomData.id && roomData.id.toString().startsWith('temp-')) {
                delete roomData.id;
              }
              // Ensure property ID is set
              roomData.property = createdPropertyId;
              
              // Call API to create room
              const result = await addPropertyRoom(createdPropertyId, roomData);
              return result;
            } catch (roomError) {
              throw roomError;
            }
          });

          await Promise.all(roomPromises);
        } catch (roomError) {
          // Still consider it a success, but with warning
          success = $t('property.createSuccessRoomsFailed');
        }
      }
      
      // Handle media files upload
      if (mediaFiles.length > 0 && createdPropertyId) {
        uploadingMedia = true;
        
        try {
          await uploadPropertyMediaBatch(
            createdPropertyId, 
            mediaFiles,
            (completed, total) => {
              uploadProgress = Math.round((completed / total) * 100);
            }
          );
          
          success = $t('property.createSuccess');
        } catch (mediaError) {
          success = $t('property.createSuccessMediaFailed');
        } finally {
          uploadingMedia = false;
        }
      } else {
        success = $t('property.createSuccess');
      }
      
      showSuccessModal = true;
    } catch (err) {
      error = err.message || $t('property.createFailed');
    } finally {
      loading = false;
    }
  }
  
  function viewCreatedProperty() {
    goto(`/properties/${createdPropertyId}`);
  }
  
  // Check if user has permission to create properties
  $: isAuthorized = $user && ($user.role === 'owner' || $user.role === 'appraiser' || $user.is_staff);
</script>

<svelte:head>
  <title>{$t('property.createProperty')}</title>
</svelte:head>

<div class="min-h-screen py-12">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <!-- Back Button -->
    <div class="mb-6">
      <a 
        href="/properties" 
        class="inline-flex items-center text-sm font-medium text-primary-600 dark:text-primary-400 hover:text-primary-500 dark:hover:text-primary-300 transition-colors"
      >
        <svg class="mr-2 w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
        </svg>
        {$t('properties.backToProperties')}
      </a>
    </div>

    {#if !isAuthorized}
      <!-- Permission denied message -->
      <div class="bg-yellow-50 border-l-4 border-yellow-400 p-4 dark:bg-yellow-900/20 dark:border-yellow-600 rounded-md shadow-md max-w-3xl mx-auto">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-3">
            <p class="text-sm text-yellow-700 dark:text-yellow-200">
              {$t('property.unauthorizedMessage')}
            </p>
          </div>
        </div>
      </div>
    {:else}
      <!-- Property Create Form -->
      <div class="max-w-4xl mx-auto">
        <!-- Header Component -->
        <PropertyCreateHeader 
          {currentStep}
          {totalSteps}
          {loading}
        />
        
        <!-- Content Tabs Component -->
        <PropertyCreateTabs
          {currentStep}
          {propertyData}
          {rooms}
          {mediaFiles}
          {validationErrors}
          {availableFeatures}
          {availableAmenities}
          {availableRoomFeatures}
          {propertyTypeOptions}
          {buildingTypeOptions}
          onLocationChange={handleLocationChange}
          onFeaturesChange={handleFeaturesChange}
          onAmenitiesChange={handleAmenitiesChange}
          onRoomsChange={handleRoomsChange}
          onMediaChange={handleMediaChange}
        />
        
        <!-- Footer Component -->
        <PropertyCreateFooter
          {currentStep}
          {totalSteps}
          {loading}
          {uploadingMedia}
          {uploadProgress}
          onNext={goToNextStep}
          onPrev={goToPrevStep}
          onSubmit={handleSubmit}
        />
        
        <!-- Error Message -->
        {#if error}
          <div class="mt-6 bg-red-50 border-l-4 border-red-400 p-4 dark:bg-red-900/20 dark:border-red-600 rounded-md shadow-md">
            <div class="flex">
              <div class="flex-shrink-0">
                <svg class="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                </svg>
              </div>
              <div class="ml-3">
                <p class="text-sm text-red-700 dark:text-red-200">
                  {error}
                </p>
              </div>
            </div>
          </div>
        {/if}
      </div>
    {/if}
    
    <!-- Success Modal -->
    {#if showSuccessModal}
      <div class="fixed inset-0 bg-gray-500 bg-opacity-75 z-50 flex items-center justify-center p-4">
        <div class="bg-white dark:bg-gray-800 rounded-xl max-w-md w-full p-8 shadow-2xl">
          <div class="text-center">
            <div class="mx-auto flex items-center justify-center h-20 w-20 rounded-full bg-green-100 dark:bg-green-900">
              <svg class="h-12 w-12 text-green-500 dark:text-green-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
            </div>
            
            <h3 class="text-xl font-bold text-gray-900 dark:text-white mt-6">
              {$t('property.createSuccess')}
            </h3>
            
            <p class="text-base text-gray-500 dark:text-gray-400 mt-4">
              {$t('property.propertyCreatedMessage')}
            </p>
            
            {#if uploadingMedia}
              <div class="mt-8">
                <div class="w-full bg-gray-200 rounded-full h-3 dark:bg-gray-700 overflow-hidden">
                  <div class="bg-green-600 h-3 rounded-full transition-all duration-300" style="width: {uploadProgress}%"></div>
                </div>
                <p class="text-sm text-gray-500 dark:text-gray-400 mt-2">
                  {$t('mediaUploader.uploading')} ({uploadProgress}%)
                </p>
              </div>
            {/if}
            
            <div class="mt-10 flex flex-col sm:flex-row justify-center sm:space-x-4 space-y-4 sm:space-y-0">
              <button
                type="button"
                on:click={() => goto('/properties')}
                class="py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600 dark:border-gray-600 transition-all duration-200"
              >
                {$t('properties.backToProperties')}
              </button>
              
              <button
                type="button"
                on:click={viewCreatedProperty}
                class="btn-modern-primary py-2 px-4 rounded-md shadow-sm text-sm font-medium transition-all duration-200"
              >
                {$t('property.viewDetails')}
              </button>
            </div>
          </div>
        </div>
      </div>
    {/if}
  </div>
</div>