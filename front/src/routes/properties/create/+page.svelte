<!-- src/routes/properties/create/+page.svelte -->
<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { t, locale } from '../../../../../i18n'; 
  import { user } from '$lib/stores/user';
  import { createProperty, uploadPropertyMediaBatch, addPropertyRoom } from '$lib/api/property';
  import LocationPicker from '$lib/components/properties/LocationPicker.svelte';
  import MediaUploader from '$lib/components/shared/MediaUploader.svelte';
  import RoomManager from '$lib/components/properties/RoomManager.svelte';
  import TagSelector from '$lib/components/ui/TagSelector.svelte';
  
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
  let propertyTypes = [];
  let buildingTypes = [];
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
        // Scroll to top for better UX
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
        // Don't include rooms here
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
              console.log('Room created successfully:', result);
              return result;
            } catch (roomError) {
              console.error('Error creating room:', roomData, roomError);
              throw roomError;
            }
          });

          await Promise.all(roomPromises);
          console.log('All rooms created successfully');
        } catch (roomError) {
          console.error('Error creating rooms:', roomError);
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
          console.error('Media upload error:', mediaError);
          success = $t('property.createSuccessMediaFailed');
        } finally {
          uploadingMedia = false;
        }
      } else {
        success = $t('property.createSuccess');
      }
      
      showSuccessModal = true;
    } catch (err) {
      console.error('Error creating property:', err);
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

<div class=" min-h-screen py-12">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <!-- Page Header with gradient text effect -->
    <div class="mb-12 text-center">
      <h1 class="text-3xl font-extrabold tracking-tight sm:text-4xl 
                 bg-clip-text text-transparent bg-gradient-to-r from-primary-600 to-secondary-600 
                 dark:from-primary-400 dark:to-secondary-400 inline-block">
        {$t('property.createProperty')}
      </h1>
      <p class="mt-4 max-w-2xl mx-auto text-lg text-gray-500 dark:text-gray-400">
        {$t('property.createPropertyDesc')}
      </p>
    </div>
    
    {#if !isAuthorized}
      <!-- Permission denied message with clear visual styling -->
      <div class="bg-yellow-50 border-l-4 border-yellow-400 p-4 dark:bg-yellow-900/20 dark:border-yellow-600 rounded-md shadow-md max-w-3xl mx-auto">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-yellow-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
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
      <!-- Enhanced Progress Indicator with visual cues -->
      <div class="mb-10 max-w-4xl mx-auto">
        <div class="flex justify-between items-center mb-2">
          <p class="text-sm font-medium text-gray-700 dark:text-gray-300">
            {$t('common.step')} {currentStep} {$t('common.of')} {totalSteps}
          </p>
          <p class="text-sm font-medium text-gray-700 dark:text-gray-300">
            {Math.round((currentStep / totalSteps) * 100)}%
          </p>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700 overflow-hidden">
          <div class="bg-gradient-to-r from-primary-500 to-secondary-500 h-2.5 rounded-full dark:from-primary-600 dark:to-secondary-400 transition-all duration-500 ease-out" 
               style="width: {(currentStep / totalSteps) * 100}%"></div>
        </div>
        
        <!-- Step indicators with visual connection lines -->
        <div class="flex justify-between mt-6 relative">
          <!-- Connection line -->
          <div class="absolute top-4 left-0 right-0 h-0.5 bg-gray-200 dark:bg-gray-700 -z-10"></div>
          
          {#each Array(totalSteps) as _, i}
            <div class="text-center z-10">
              <div class={`rounded-full h-8 w-8 flex items-center justify-center text-xs font-medium 
                          border-2 mx-auto cursor-pointer transition-all duration-300 
                          ${currentStep > i + 1 
                            ? 'bg-primary-500 border-primary-500 text-white dark:bg-primary-600' 
                            : currentStep === i + 1 
                              ? 'border-primary-500 text-primary-600 dark:text-primary-400 dark:border-primary-400'
                              : 'border-gray-300 text-gray-500 bg-white dark:bg-gray-800 dark:border-gray-600 dark:text-gray-400'}`}>
                {i + 1}
              </div>
              <div class="mt-2 text-xs font-medium text-gray-500 dark:text-gray-400 hidden sm:block">
                {#if i === 0}
                  {$t('property.basicInfo')}
                {:else if i === 1}
                  {$t('property.location')}
                {:else if i === 2}
                  {$t('property.details')}
                {:else if i === 3}
                  {$t('property.financial')}
                {/if}
              </div>
            </div>
          {/each}
        </div>
      </div>
      
      <!-- Form Container with refined styling -->
      <div class="bg-white dark:bg-gray-800 shadow-xl rounded-xl overflow-hidden max-w-4xl mx-auto transition-all duration-300">
        <!-- Card header with step title and icon -->
        <div class="bg-gradient-to-r from-gray-50 to-white dark:from-gray-800 dark:to-gray-750 p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 class="text-xl font-bold text-gray-900 dark:text-white flex items-center">
            {#if currentStep === 1}
              <svg class="w-6 h-6 mr-2 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
              </svg>
              {$t('property.basicInfo')}
            {:else if currentStep === 2}
              <svg class="w-6 h-6 mr-2 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
              </svg>
              {$t('property.location')}
            {:else if currentStep === 3}
              <svg class="w-6 h-6 mr-2 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
              </svg>
              {$t('property.details')}
            {:else if currentStep === 4}
              <svg class="w-6 h-6 mr-2 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              {$t('property.financial')}
            {/if}
          </h2>
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
            {#if currentStep === 1}
              {$t('property.basicInfoDesc')}
            {:else if currentStep === 2}
              {$t('property.locationDesc')}
            {:else if currentStep === 3}
              {$t('property.detailsDesc')}
            {:else if currentStep === 4}
              {$t('property.financialDesc')}
            {/if}
          </p>
        </div>
        
        <div class="p-6 sm:p-8">
          <!-- Step 1: Basic Information -->
          {#if currentStep === 1}
            <div class="space-y-8 animate-fadeIn">
              <div class="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
                <!-- Property Title -->
                <div class="sm:col-span-4">
                  <label for="title" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    {$t('property.title')} *
                  </label>
                  <div class="mt-1 relative rounded-md shadow-sm">
                    <input 
                      type="text" 
                      id="title" 
                      bind:value={propertyData.title} 
                      class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                      class:border-red-500={validationErrors.title}
                      placeholder={$t('property.titlePlaceholder')}
                    />
                    {#if validationErrors.title}
                      <div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                        <svg class="h-5 w-5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                          <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                        </svg>
                      </div>
                    {/if}
                  </div>
                  {#if validationErrors.title}
                    <p class="mt-1 text-sm text-red-600 dark:text-red-500">{validationErrors.title}</p>
                  {/if}
                </div>
                
                <!-- Property Type -->
                <div class="sm:col-span-3">
                  <label for="property_type" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    {$t('property.propertyType')} *
                  </label>
                  <div class="mt-1 relative rounded-md shadow-sm">
                    <select 
                      id="property_type" 
                      bind:value={propertyData.property_type}
                      class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                      class:border-red-500={validationErrors.property_type}
                    >
                      <option value="">{$t('common.select')}</option>
                      {#each propertyTypeOptions as option}
                        <option value={option.value}>{option.label}</option>
                      {/each}
                    </select>
                    {#if validationErrors.property_type}
                      <div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                        <svg class="h-5 w-5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                          <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                        </svg>
                      </div>
                    {/if}
                  </div>
                  {#if validationErrors.property_type}
                    <p class="mt-1 text-sm text-red-600 dark:text-red-500">{validationErrors.property_type}</p>
                  {/if}
                </div>
                
                <!-- Building Type -->
                <div class="sm:col-span-3">
                  <label for="building_type" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    {$t('property.buildingType')}
                  </label>
                  <div class="mt-1">
                    <select 
                      id="building_type" 
                      bind:value={propertyData.building_type}
                      class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                    >
                      <option value="">{$t('common.select')}</option>
                      {#each buildingTypeOptions as option}
                        <option value={option.value}>{option.label}</option>
                      {/each}
                    </select>
                  </div>
                </div>
                
                <!-- Deed Number -->
                <div class="sm:col-span-3">
                  <label for="deed_number" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    {$t('property.deedNumber')} *
                  </label>
                  <div class="mt-1 relative rounded-md shadow-sm">
                    <input 
                      type="text" 
                      id="deed_number" 
                      bind:value={propertyData.deed_number} 
                      class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                      class:border-red-500={validationErrors.deed_number}
                      placeholder={$t('property.deedNumberPlaceholder')}
                    />
                    {#if validationErrors.deed_number}
                      <div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                        <svg class="h-5 w-5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                          <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                        </svg>
                      </div>
                    {/if}
                  </div>
                  {#if validationErrors.deed_number}
                    <p class="mt-1 text-sm text-red-600 dark:text-red-500">{validationErrors.deed_number}</p>
                  {/if}
                  <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
                    {$t('property.deedNumberHelp')}
                  </p>
                </div>
                
                <!-- Description -->
                <div class="sm:col-span-6">
                  <label for="description" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    {$t('property.description')} *
                  </label>
                  <div class="mt-1">
                    <textarea 
                      id="description" 
                      bind:value={propertyData.description} 
                      rows="4" 
                      class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                      class:border-red-500={validationErrors.description}
                      placeholder={$t('property.descriptionPlaceholder')}
                    ></textarea>
                    {#if validationErrors.description}
                      <p class="mt-1 text-sm text-red-600 dark:text-red-500">{validationErrors.description}</p>
                    {/if}
                  </div>
                </div>
              </div>
            </div>
          {/if}
          
          <!-- Step 2: Location Information -->
          {#if currentStep === 2}
            <div class="space-y-8 animate-fadeIn">
              <LocationPicker
                bind:address={propertyData.address}
                bind:city={propertyData.city}
                bind:state={propertyData.state}
                bind:postalCode={propertyData.postal_code}
                bind:country={propertyData.country}
                bind:latitude={propertyData.latitude}
                bind:longitude={propertyData.longitude}
                on:locationChange={handleLocationChange}
              />
              
              <div class="space-y-3">
                {#if validationErrors.address}
                  <p class="text-sm text-red-600 dark:text-red-500">{validationErrors.address}</p>
                {/if}
                
                {#if validationErrors.city}
                  <p class="text-sm text-red-600 dark:text-red-500">{validationErrors.city}</p>
                {/if}
                
                {#if validationErrors.state}
                  <p class="text-sm text-red-600 dark:text-red-500">{validationErrors.state}</p>
                {/if}
              </div>
            </div>
          {/if}
          
          <!-- Step 3: Property Details -->
          {#if currentStep === 3}
            <div class="space-y-8 animate-fadeIn">
              <div class="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
                <!-- Size -->
                <div class="sm:col-span-2">
                  <label for="size_sqm" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    {$t('property.size')} ({$t('property.sqm')}) *
                  </label>
                  <div class="mt-1 relative rounded-md shadow-sm">
                    <input 
                      type="number" 
                      id="size_sqm" 
                      bind:value={propertyData.size_sqm} 
                      min="1" 
                      step="0.01" 
                      class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                      class:border-red-500={validationErrors.size_sqm}
                    />
                    {#if validationErrors.size_sqm}
                      <div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                        <svg class="h-5 w-5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                          <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                        </svg>
                      </div>
                    {/if}
                  </div>
                  {#if validationErrors.size_sqm}
                    <p class="mt-1 text-sm text-red-600 dark:text-red-500">{validationErrors.size_sqm}</p>
                  {/if}
                </div>
                
                <!-- Floors -->
                <div class="sm:col-span-2">
                  <label for="floors" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    {$t('property.floors')}
                  </label>
                  <div class="mt-1">
                    <input 
                      type="number" 
                      id="floors" 
                      bind:value={propertyData.floors} 
                      min="1" 
                      step="1" 
                      class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                      class:border-red-500={validationErrors.floors}
                    />
                    {#if validationErrors.floors}
                      <p class="mt-1 text-sm text-red-600 dark:text-red-500">{validationErrors.floors}</p>
                    {/if}
                  </div>
                </div>
                
                <!-- Year Built -->
                <div class="sm:col-span-2">
                  <label for="year_built" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    {$t('property.yearBuilt')}
                  </label>
                  <div class="mt-1">
                    <input 
                      type="number" 
                      id="year_built" 
                      bind:value={propertyData.year_built} 
                      min="1800" 
                      max="2025" 
                      step="1" 
                      class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                      class:border-red-500={validationErrors.year_built}
                    />
                    {#if validationErrors.year_built}
                      <p class="mt-1 text-sm text-red-600 dark:text-red-500">{validationErrors.year_built}</p>
                    {/if}
                  </div>
                </div>
                
                <!-- Features with properly translated values -->
                <div class="sm:col-span-6 mt-2">
                  <TagSelector
                    title={$t('property.features')}
                    tags={availableFeatures}
                    selectedTags={propertyData.features}
                    on:change={handleFeaturesChange}
                    variant="pill"
                  />
                </div>
                
                <!-- Amenities with properly translated values -->
                <div class="sm:col-span-6 mt-2">
                  <TagSelector
                    title={$t('property.amenities')}
                    tags={availableAmenities}
                    selectedTags={propertyData.amenities}
                    on:change={handleAmenitiesChange}
                    variant="pill"
                  />
                </div>
                
                <!-- Rooms with proper localization -->
                <div class="sm:col-span-6 mt-4">
                  <div class="bg-gray-50 dark:bg-gray-700 p-6 rounded-lg shadow-inner">
                    <RoomManager
                      bind:rooms
                      availableFeatures={availableRoomFeatures}
                      on:change={handleRoomsChange}
                    />
                  </div>
                </div>
              </div>
            </div>
          {/if}
          
          <!-- Step 4: Financial Information & Media Upload -->
          {#if currentStep === 4}
            <div class="space-y-8 animate-fadeIn">
              <div class="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
                <!-- Market Value -->
                <div class="sm:col-span-3">
                  <label for="market_value" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    {$t('property.marketValue')} *
                  </label>
                  <div class="mt-1 relative rounded-md shadow-sm">
                    <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <span class="text-gray-500 sm:text-sm">$</span>
                    </div>
                    <input 
                      type="number" 
                      id="market_value" 
                      bind:value={propertyData.market_value} 
                      min="1" 
                      step="0.01" 
                      class="pl-7 shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                      class:border-red-500={validationErrors.market_value}
                    />
                    {#if validationErrors.market_value}
                      <div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                        <svg class="h-5 w-5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                          <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                        </svg>
                      </div>
                    {/if}
                  </div>
                  {#if validationErrors.market_value}
                    <p class="mt-1 text-sm text-red-600 dark:text-red-500">{validationErrors.market_value}</p>
                  {/if}
                </div>
                
                <!-- Minimum Bid -->
                <div class="sm:col-span-3">
                  <label for="minimum_bid" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    {$t('property.minimumBid')}
                  </label>
                  <div class="mt-1 relative rounded-md shadow-sm">
                    <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <span class="text-gray-500 sm:text-sm">$</span>
                    </div>
                    <input 
                      type="number" 
                      id="minimum_bid" 
                      bind:value={propertyData.minimum_bid} 
                      min="1" 
                      step="0.01" 
                      class="pl-7 shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                      class:border-red-500={validationErrors.minimum_bid}
                    />
                  </div>
                  {#if validationErrors.minimum_bid}
                    <p class="mt-1 text-sm text-red-600 dark:text-red-500">{validationErrors.minimum_bid}</p>
                  {/if}
                </div>
                
                <!-- Publishing Options with elegantly styled cards -->
                <div class="sm:col-span-6">
                  <fieldset class="bg-gradient-to-br from-gray-50 to-white dark:from-gray-700 dark:to-gray-750 p-6 rounded-lg shadow-sm">
                    <legend class="text-base font-medium text-gray-700 dark:text-gray-300 px-3 py-1 bg-white dark:bg-gray-800 rounded-md shadow-sm border border-gray-200 dark:border-gray-600">
                      {$t('property.publishingOptions')}
                    </legend>
                    <div class="mt-4 space-y-4">
                      <div class="flex items-start">
                        <div class="flex items-center h-5">
                          <input 
                            id="is_published" 
                            type="checkbox" 
                            bind:checked={propertyData.is_published} 
                            class="focus:ring-primary-500 h-5 w-5 text-primary-600 border-gray-300 rounded dark:border-gray-600 dark:bg-gray-700"
                          />
                        </div>
                        <div class="ml-3 text-sm">
                          <label for="is_published" class="font-medium text-gray-700 dark:text-gray-300">
                            {$t('property.published')}
                          </label>
                          <p class="text-gray-500 dark:text-gray-400">
                            {$t('property.publishedHelp')}
                          </p>
                        </div>
                      </div>
                      
                      <div class="flex items-start">
                        <div class="flex items-center h-5">
                          <input 
                            id="is_featured" 
                            type="checkbox" 
                            bind:checked={propertyData.is_featured} 
                            class="focus:ring-primary-500 h-5 w-5 text-primary-600 border-gray-300 rounded dark:border-gray-600 dark:bg-gray-700"
                          />
                        </div>
                        <div class="ml-3 text-sm">
                          <label for="is_featured" class="font-medium text-gray-700 dark:text-gray-300">
                            {$t('property.featured')}
                          </label>
                          <p class="text-gray-500 dark:text-gray-400">
                            {$t('property.featuredHelp')}
                          </p>
                        </div>
                      </div>
                    </div>
                  </fieldset>
                </div>
                
                <!-- Media Upload -->
                <div class="sm:col-span-6 mt-2">
                  <div class="bg-gradient-to-br from-gray-50 to-white dark:from-gray-700 dark:to-gray-750 p-6 rounded-lg shadow-sm">
                    <h3 class="text-lg font-medium text-gray-900 dark:text-white flex items-center">
                      <svg class="w-5 h-5 mr-2 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                      </svg>
                      {$t('property.mediaUpload')}
                    </h3>
                    <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
                      {$t('property.mediaUploadDesc')}
                    </p>
                    
                    <div class="mt-4">
                      <MediaUploader
                        maxFiles={10}
                        maxSize={MAX_FILE_SIZE}
                        allowedTypes={['image/jpeg', 'image/png', 'image/gif', 'application/pdf']}
                        on:change={handleMediaChange}
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          {/if}
          
          <!-- Form Navigation with smooth transitions and clear visual feedback -->
          <div class="mt-10 pt-5 border-t border-gray-200 dark:border-gray-700">
            <div class="flex justify-between">
              <button
                type="button"
                on:click={goToPrevStep}
                disabled={currentStep === 1 || loading}
                class="py-2 px-4 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 border border-gray-300 dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600 dark:border-gray-600 disabled:opacity-50 transition-all duration-200 transform hover:-translate-x-1"
              >
                <span class="flex items-center">
                  <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
                  </svg>
                  {$t('common.previous')}
                </span>
              </button>
              
              {#if currentStep < totalSteps}
                <button
                  type="button"
                  on:click={goToNextStep}
                  class="ml-3 inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-all duration-200 transform hover:translate-x-1"
                >
                  <span class="flex items-center">
                    {$t('common.next')}
                    <svg class="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                    </svg>
                  </span>
                </button>
              {:else}
                <button
                  type="button"
                  on:click={handleSubmit}
                  disabled={loading}
                  class="ml-3 inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-gradient-to-r from-success-500 to-success-600 hover:from-success-600 hover:to-success-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-success-500 disabled:opacity-50 transition-all duration-200"
                >
                  {#if loading}
                    <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    {$t('common.processing')}
                  {:else}
                    <span class="flex items-center">
                      <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                      </svg>
                      {$t('property.create')}
                    </span>
                  {/if}
                </button>
              {/if}
            </div>
          </div>
        
        
          <!-- Error Message with clear visual styling -->
          {#if error}
            <div class="mt-6 bg-red-50 border-l-4 border-red-400 p-4 dark:bg-red-900/20 dark:border-red-600 rounded-md shadow-md">
              <div class="flex">
                <div class="flex-shrink-0">
                  <svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
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
      </div>
    {/if}
    
    <!-- Success Modal with polished design and animations -->
    {#if showSuccessModal}
      <div class="fixed inset-0 bg-gray-500 bg-opacity-75 z-50 flex items-center justify-center p-4 animate-fadeIn">
        <div class="bg-white dark:bg-gray-800 rounded-xl max-w-md w-full p-8 shadow-2xl transform transition-all sm:scale-100 scale-90 animate-slideIn">
          <div class="text-center">
            <div class="mx-auto flex items-center justify-center h-20 w-20 rounded-full bg-green-100 dark:bg-green-900 transform motion-safe:animate-bounce">
              <svg class="h-12 w-12 text-green-500 dark:text-green-300" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
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
                class="py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-all duration-200 hover:scale-105"
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

<style>
  .animate-fadeIn {
    animation: fadeIn 0.5s ease-in-out;
  }
  
  .animate-slideIn {
    animation: slideIn 0.5s ease-out;
  }
  
  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  
  @keyframes slideIn {
    from {
      opacity: 0;
      transform: translateY(-20px) scale(0.95);
    }
    to {
      opacity: 1;
      transform: translateY(0) scale(1);
    }
  }
</style>