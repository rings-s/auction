<!-- src/lib/components/properties/PropertyForm.svelte -->
<script>
    /**
     * Property Form Component
     * Comprehensive form for creating and editing property listings.
     */
    import { onMount } from 'svelte';
    import { t } from '$lib/i18n';
    import { fade } from 'svelte/transition';
    import { api } from '$lib/services/api';
    
    // UI Components
    import Input from '$lib/components/ui/Input.svelte';
    import Select from '$lib/components/ui/Select.svelte';
    import Button from '$lib/components/ui/Button.svelte';
    import Alert from '$lib/components/ui/Alert.svelte';
    import Card from '$lib/components/ui/Card.svelte';
    import Tabs from '$lib/components/ui/Tabs.svelte';
    import TabItem from '$lib/components/ui/TabItem.svelte';
    import Spinner from '$lib/components/ui/Spinner.svelte';
    import Badge from '$lib/components/ui/Badge.svelte';
    
    // Props
    export let propertyId = null; // If set, we're editing an existing property
    export let initialData = null; // Optionally pass initial data directly
    export let onSuccess = () => {}; // Callback after successful save
    export let onCancel = () => {}; // Callback for cancel action
    
    // State
    let loading = propertyId ? true : false; // Load data if editing
    let saving = false; // Track submission state
    let error = null; // General error message
    let success = false; // Success message state
    let activeTab = 'basics'; // Current active tab
    let uploadProgress = 0; // Image upload progress
    let uploadingImages = false; // Flag for image upload state
    
    // Form data with defaults
    let formData = {
      // Basic details
      title: '',
      description: '',
      property_type: 'apartment',
      status: 'draft',
      estimated_value: '',
      area: '',
      built_up_area: '',
      bedrooms: '',
      bathrooms: '',
      year_built: '',
      condition: 'good',
      floor_number: '',
      
      // Location
      address: '',
      district: '',
      city: '',
      country: '',
      postal_code: '',
      latitude: '',
      longitude: '',
      
      // Features & amenities
      features: [],
      amenities: [],
      
      // Outdoor spaces
      outdoor_spaces: {
        garden: false,
        balcony: false,
        terrace: false,
        pool: false
      },
      
      // Parking
      parking: {
        spaces: 0,
        type: '',
        underground: false,
        garage_size: '',
        electric_vehicle_charging: false
      },
      
      // Building services
      building_services: {
        elevator: false,
        security: false,
        concierge: false,
        maintenance: false
      },
      
      // Infrastructure
      infrastructure: {
        water_supply: true,
        electricity: true,
        gas: false,
        sewage: true,
        internet: false,
        fiber_optic: false
      },
      
      // Images
      images: [],
      main_image_index: 0,
      
      // Other
      is_featured: false,
      is_verified: false
    };
    
    // Form validation errors
    let errors = {};
    
    // Tabs configuration
    const tabs = [
      { id: 'basics', label: $t('properties.tab_basic_details') },
      { id: 'location', label: $t('properties.tab_location') },
      { id: 'features', label: $t('properties.tab_features') },
      { id: 'images', label: $t('properties.tab_images') },
      { id: 'advanced', label: $t('properties.tab_advanced') }
    ];
    
    // Option lists for selects
    const propertyTypeOptions = [
      { value: 'apartment', label: $t('properties.types.apartment') },
      { value: 'villa', label: $t('properties.types.villa') },
      { value: 'land', label: $t('properties.types.land') },
      { value: 'commercial', label: $t('properties.types.commercial') },
      { value: 'industrial', label: $t('properties.types.industrial') },
      { value: 'mixed_use', label: $t('properties.types.mixed_use') }
    ];
    
    const statusOptions = [
      { value: 'draft', label: $t('properties.status.draft') },
      { value: 'active', label: $t('properties.status.available') },
      { value: 'under_contract', label: $t('properties.status.under_contract') },
      { value: 'sold', label: $t('properties.status.sold') },
      { value: 'inactive', label: $t('properties.status.inactive') }
    ];
    
    const conditionOptions = [
      { value: 'excellent', label: $t('properties.condition.excellent') },
      { value: 'good', label: $t('properties.condition.good') },
      { value: 'fair', label: $t('properties.condition.fair') },
      { value: 'needs_renovation', label: $t('properties.condition.needs_renovation') },
      { value: 'new_construction', label: $t('properties.condition.new_construction') }
    ];
    
    const parkingTypeOptions = [
      { value: 'garage', label: $t('properties.parking_types.garage') },
      { value: 'carport', label: $t('properties.parking_types.carport') },
      { value: 'street', label: $t('properties.parking_types.street') },
      { value: 'assigned', label: $t('properties.parking_types.assigned') },
      { value: 'none', label: $t('properties.parking_types.none') }
    ];
    
    // Feature selection options
    const featureOptions = [
      'air_conditioning',
      'heating',
      'fireplace',
      'security_system',
      'storage_room',
      'furnished',
      'hardwood_floors',
      'double_glazing',
      'marble_floors',
      'walk_in_closet',
      'central_vacuum',
      'alarm_system',
      'sauna',
      'jacuzzi',
      'smart_home',
      'disability_access'
    ].map(feature => ({ 
      id: feature, 
      label: $t(`properties.features.${feature}`) 
    }));
    
    // Amenity selection options
    const amenityOptions = [
      'gym',
      'swimming_pool',
      'spa',
      'sauna',
      'garden',
      'playground',
      'bbq_area',
      'community_center',
      'tennis_court',
      'basketball_court',
      'pet_friendly',
      'laundry_room',
      'guest_parking',
      'bicycle_storage'
    ].map(amenity => ({ 
      id: amenity, 
      label: $t(`properties.amenities.${amenity}`) 
    }));
    
    // Load existing property data
    async function loadProperty() {
      if (!propertyId) return;
      
      loading = true;
      error = null;
      
      try {
        const response = await api.get(`properties/${propertyId}/edit/`);
        
        if (response?.data?.property) {
          // Merge the retrieved data with default structure
          formData = {
            ...formData,
            ...response.data.property
          };
        } else {
          throw new Error('Invalid response format');
        }
      } catch (err) {
        console.error('Error loading property data:', err);
        error = err.message || $t('system_messages.error_occurred');
      } finally {
        loading = false;
      }
    }
    
    // Handle form submission
    async function handleSubmit() {
      if (saving) return;
      
      saving = true;
      error = null;
      errors = {};
      
      // Validate form
      if (!validateForm()) {
        saving = false;
        return;
      }
      
      try {
        let response;
        
        if (propertyId) {
          // Update existing property
          response = await api.put(`properties/${propertyId}/`, formData);
        } else {
          // Create new property
          response = await api.post('properties/', formData);
        }
        
        if (response?.data?.success) {
          success = true;
          const newPropertyId = response.data.property_id || propertyId;
          
          // If we have images to upload, do that now
          if (formData.newImages && formData.newImages.length > 0) {
            await uploadImages(newPropertyId);
          }
          
          // Call success callback
          setTimeout(() => {
            onSuccess(newPropertyId);
          }, 1500);
        } else {
          throw new Error(response?.data?.message || 'Unknown error');
        }
      } catch (err) {
        console.error('Error saving property:', err);
        
        // Handle validation errors from server
        if (err.response?.data?.errors) {
          errors = err.response.data.errors;
          
          // Scroll to first tab with error
          for (const [field, message] of Object.entries(errors)) {
            const tab = getTabForField(field);
            if (tab && tab !== activeTab) {
              activeTab = tab;
              break;
            }
          }
        } else {
          error = err.message || $t('system_messages.error_occurred');
        }
      } finally {
        saving = false;
      }
    }
    
    // Helper to determine which tab contains a field
    function getTabForField(field) {
      const tabMapping = {
        // Basic details tab
        title: 'basics',
        description: 'basics',
        property_type: 'basics',
        status: 'basics',
        estimated_value: 'basics',
        area: 'basics',
        built_up_area: 'basics',
        bedrooms: 'basics',
        bathrooms: 'basics',
        year_built: 'basics',
        condition: 'basics',
        floor_number: 'basics',
        
        // Location tab
        address: 'location',
        district: 'location',
        city: 'location',
        country: 'location',
        postal_code: 'location',
        latitude: 'location',
        longitude: 'location',
        
        // Features tab
        features: 'features',
        amenities: 'features',
        outdoor_spaces: 'features',
        parking: 'features',
        building_services: 'features',
        infrastructure: 'features',
        
        // Images tab
        images: 'images',
        main_image_index: 'images',
        
        // Advanced tab
        is_featured: 'advanced',
        is_verified: 'advanced'
      };
      
      return tabMapping[field] || 'basics';
    }
    
    // Validate form fields
    function validateForm() {
      errors = {};
      
      // Required fields validation
      const requiredFields = {
        title: $t('properties.validation.title_required'),
        property_type: $t('properties.validation.property_type_required'),
        area: $t('properties.validation.area_required'),
        estimated_value: $t('properties.validation.price_required'),
        address: $t('properties.validation.address_required'),
        city: $t('properties.validation.city_required'),
        country: $t('properties.validation.country_required')
      };
      
      for (const [field, message] of Object.entries(requiredFields)) {
        if (!formData[field]) {
          errors[field] = message;
        }
      }
      
      // Numeric fields validation
      const numericFields = {
        area: $t('properties.validation.area_numeric'),
        built_up_area: $t('properties.validation.built_up_area_numeric'),
        estimated_value: $t('properties.validation.price_numeric'),
        bedrooms: $t('properties.validation.bedrooms_numeric'),
        bathrooms: $t('properties.validation.bathrooms_numeric'),
        year_built: $t('properties.validation.year_built_numeric'),
        latitude: $t('properties.validation.latitude_numeric'),
        longitude: $t('properties.validation.longitude_numeric')
      };
      
      for (const [field, message] of Object.entries(numericFields)) {
        if (formData[field] && isNaN(parseFloat(formData[field]))) {
          errors[field] = message;
        }
      }
      
      // Special validations
      if (formData.latitude && (parseFloat(formData.latitude) < -90 || parseFloat(formData.latitude) > 90)) {
        errors.latitude = $t('properties.validation.latitude_range');
      }
      
      if (formData.longitude && (parseFloat(formData.longitude) < -180 || parseFloat(formData.longitude) > 180)) {
        errors.longitude = $t('properties.validation.longitude_range');
      }
      
      if (formData.year_built && parseInt(formData.year_built) > new Date().getFullYear()) {
        errors.year_built = $t('properties.validation.year_built_future');
      }
      
      return Object.keys(errors).length === 0;
    }
    
    // Handle image uploads
    async function uploadImages(propId) {
      if (!formData.newImages || formData.newImages.length === 0) return;
      
      uploadingImages = true;
      uploadProgress = 0;
      
      try {
        const totalImages = formData.newImages.length;
        let uploaded = 0;
        
        for (const file of formData.newImages) {
          const formDataObj = new FormData();
          formDataObj.append('property_id', propId);
          formDataObj.append('image', file);
          formDataObj.append('is_primary', formData.main_image_index === uploaded ? 'true' : 'false');
          
          await api.post('properties/images/upload/', formDataObj, {
            headers: {
              'Content-Type': 'multipart/form-data'
            },
            onUploadProgress: (progressEvent) => {
              const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
              uploadProgress = (uploaded / totalImages) * 100 + (percentCompleted / totalImages);
            }
          });
          
          uploaded++;
          uploadProgress = (uploaded / totalImages) * 100;
        }
      } catch (err) {
        console.error('Error uploading images:', err);
        error = $t('properties.validation.image_upload_error');
      } finally {
        uploadingImages = false;
      }
    }
    
    // Handle file selection
    function handleFileSelect(event) {
      const files = Array.from(event.target.files);
      formData.newImages = [...(formData.newImages || []), ...files];
      
      // Preview the images
      for (const file of files) {
        const reader = new FileReader();
        reader.onload = (e) => {
          formData.imagesPreviews = [...(formData.imagesPreviews || []), e.target.result];
        };
        reader.readAsDataURL(file);
      }
    }
    
    // Set main image from new uploads
    function setMainImage(index) {
      formData.main_image_index = index;
    }
    
    // Remove image from queue
    function removeImage(index) {
      formData.newImages = formData.newImages.filter((_, i) => i !== index);
      formData.imagesPreviews = formData.imagesPreviews.filter((_, i) => i !== index);
      
      if (formData.main_image_index === index) {
        formData.main_image_index = 0;
      } else if (formData.main_image_index > index) {
        formData.main_image_index--;
      }
    }
    
    // Handle checkbox arrays (features, amenities)
    function handleCheckboxArray(array, value, checked) {
      if (checked) {
        if (!formData[array].includes(value)) {
          formData[array] = [...formData[array], value];
        }
      } else {
        formData[array] = formData[array].filter(item => item !== value);
      }
    }
    
    // Initialize component
    onMount(() => {
      // Use the initial data if provided, otherwise load from API
      if (initialData) {
        formData = { ...formData, ...initialData };
        loading = false;
      } else if (propertyId) {
        loadProperty();
      }
      
      // Initialize image previews array
      formData.imagesPreviews = [];
      formData.newImages = [];
    });
    
    // Handle tab change
    function handleTabChange(event) {
      activeTab = event.detail.tabId;
    }
  </script>
  
  <div class="property-form">
    {#if loading}
      <div class="my-16 flex justify-center">
        <Spinner size="lg" text={$t('general.loading')} />
      </div>
    {:else if success}
      <div class="my-8" in:fade={{ duration: 300 }}>
        <Alert type="success" title={$t('properties.form.success_title')}>
          <p>{propertyId ? $t('properties.form.updated_success') : $t('properties.form.created_success')}</p>
          {#if uploadingImages}
            <div class="mt-4">
              <p class="mb-2">{$t('properties.form.uploading_images')}: {Math.round(uploadProgress)}%</p>
              <div class="h-2 w-full overflow-hidden rounded-full bg-cosmos-bg-light">
                <div class="h-full bg-primary" style="width: {uploadProgress}%"></div>
              </div>
            </div>
          {/if}
        </Alert>
      </div>
    {:else}
      <form on:submit|preventDefault={handleSubmit} class="space-y-6">
        <!-- Header with title -->
        <div class="mb-6 border-b border-cosmos-bg-light pb-4">
          <h1 class="text-2xl font-bold text-cosmos-text">
            {propertyId ? $t('properties.form.edit_property') : $t('properties.form.add_property')}
          </h1>
          <p class="text-cosmos-text-muted">
            {$t('properties.form.subtitle')}
          </p>
        </div>
        
        {#if error}
          <Alert type="error" title={$t('general.error')} dismissible>
            <p>{error}</p>
          </Alert>
        {/if}
        
        <!-- Tabs Navigation -->
        <Tabs {tabs} {activeTab} on:change={handleTabChange} />
        
        <!-- Tab Content -->
        <div class="tab-content">
          <!-- Basic Details Tab -->
          <TabItem id="basics" active={activeTab === 'basics'}>
            <Card>
              <h2 class="mb-4 text-xl font-medium text-cosmos-text">
                {$t('properties.form.basic_details')}
              </h2>
              
              <div class="grid grid-cols-1 gap-6 md:grid-cols-2">
                <!-- Title -->
                <div class="md:col-span-2">
                  <Input
                    type="text"
                    name="title"
                    label={$t('properties.form.title')}
                    bind:value={formData.title}
                    error={errors.title}
                    required
                    placeholder={$t('properties.form.title_placeholder')}
                  />
                </div>
                
                <!-- Property Type & Status -->
                <Select
                  name="property_type"
                  label={$t('properties.property_type')}
                  options={propertyTypeOptions}
                  bind:value={formData.property_type}
                  error={errors.property_type}
                  required
                />
                
                <Select
                  name="status"
                  label={$t('properties.property_status')}
                  options={statusOptions}
                  bind:value={formData.status}
                  error={errors.status}
                />
                
                <!-- Price -->
                <Input
                  type="number"
                  name="estimated_value"
                  label={$t('properties.property_price')}
                  bind:value={formData.estimated_value}
                  error={errors.estimated_value}
                  required
                  placeholder={$t('properties.form.price_placeholder')}
                />
                
                <!-- Area -->
                <Input
                  type="number"
                  name="area"
                  label={$t('properties.property_area')} 
                  helpText={$t('properties.form.in_square_meters')}
                  bind:value={formData.area}
                  error={errors.area}
                  required
                  placeholder="0"
                />
                
                <!-- Built-up Area -->
                <Input
                  type="number"
                  name="built_up_area"
                  label={$t('properties.built_up_area')}
                  helpText={$t('properties.form.in_square_meters')}
                  bind:value={formData.built_up_area}
                  error={errors.built_up_area}
                  placeholder="0"
                />
                
                <!-- Bedrooms & Bathrooms -->
                <Input
                  type="number"
                  name="bedrooms"
                  label={$t('properties.bedrooms')}
                  bind:value={formData.bedrooms}
                  error={errors.bedrooms}
                  placeholder="0"
                />
                
                <Input
                  type="number"
                  name="bathrooms"
                  label={$t('properties.bathrooms')}
                  bind:value={formData.bathrooms}
                  error={errors.bathrooms}
                  placeholder="0"
                />
                
                <!-- Year Built & Condition -->
                <Input
                  type="number"
                  name="year_built"
                  label={$t('properties.build_year')}
                  bind:value={formData.year_built}
                  error={errors.year_built}
                  placeholder={$t('properties.form.year_placeholder')}
                />
                
                <Select
                  name="condition"
                  label={$t('properties.property_condition')}
                  options={conditionOptions}
                  bind:value={formData.condition}
                  error={errors.condition}
                />
                
                <!-- Floor Number -->
                <Input
                  type="number"
                  name="floor_number"
                  label={$t('properties.floor_number')}
                  bind:value={formData.floor_number}
                  error={errors.floor_number}
                  placeholder="0"
                />
              </div>
              
              <!-- Description -->
              <div class="mt-6">
                <label for="description" class="mb-1.5 block text-sm font-medium text-cosmos-text">
                  {$t('properties.property_description')}
                </label>
                <textarea
                  id="description"
                  name="description"
                  bind:value={formData.description}
                  rows="5"
                  class="w-full rounded-lg border border-cosmos-bg-light bg-cosmos-bg p-4 text-cosmos-text transition focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary focus:ring-opacity-25"
                  placeholder={$t('properties.form.description_placeholder')}
                ></textarea>
                {#if errors.description}
                  <p class="mt-1.5 text-sm text-red-500">{errors.description}</p>
                {/if}
              </div>
            </Card>
          </TabItem>
          
          <!-- Location Tab -->
          <TabItem id="location" active={activeTab === 'location'}>
            <Card>
              <h2 class="mb-4 text-xl font-medium text-cosmos-text">
                {$t('properties.form.location_details')}
              </h2>
              
              <div class="grid grid-cols-1 gap-6 md:grid-cols-2">
                <!-- Address -->
                <div class="md:col-span-2">
                  <Input
                    type="text"
                    name="address"
                    label={$t('properties.property_address')}
                    bind:value={formData.address}
                    error={errors.address}
                    required
                    placeholder={$t('properties.form.address_placeholder')}
                  />
                </div>
                
                <!-- District & City -->
                <Input
                  type="text"
                  name="district"
                  label={$t('properties.property_district')}
                  bind:value={formData.district}
                  error={errors.district}
                  placeholder={$t('properties.form.district_placeholder')}
                />
                
                <Input
                  type="text"
                  name="city"
                  label={$t('properties.property_city')}
                  bind:value={formData.city}
                  error={errors.city}
                  required
                  placeholder={$t('properties.form.city_placeholder')}
                />
                
                <!-- Country & Postal Code -->
                <Input
                  type="text"
                  name="country"
                  label={$t('properties.property_country')}
                  bind:value={formData.country}
                  error={errors.country}
                  required
                  placeholder={$t('properties.form.country_placeholder')}
                />
                
                <Input
                  type="text"
                  name="postal_code"
                  label={$t('properties.property_postal_code')}
                  bind:value={formData.postal_code}
                  error={errors.postal_code}
                  placeholder={$t('properties.form.postal_code_placeholder')}
                />
                
                <!-- Coordinates -->
                <Input
                  type="text"
                  name="latitude"
                  label={$t('properties.latitude')}
                  helpText={$t('properties.form.latitude_help')}
                  bind:value={formData.latitude}
                  error={errors.latitude}
                  placeholder="-90 to 90"
                />
                
                <Input
                  type="text"
                  name="longitude"
                  label={$t('properties.longitude')}
                  helpText={$t('properties.form.longitude_help')}
                  bind:value={formData.longitude}
                  error={errors.longitude}
                  placeholder="-180 to 180"
                />
              </div>
              
              <!-- Map placeholder -->
              <div class="mt-6 rounded-lg border border-cosmos-bg-light bg-cosmos-bg-light bg-opacity-20 p-4 text-center">
                <p class="mb-2 text-cosmos-text-muted">{$t('properties.form.map_coming_soon')}</p>
                <small class="text-cosmos-text-dim">{$t('properties.form.map_hint')}</small>
              </div>
            </Card>
          </TabItem>
          
          <!-- Features Tab -->
          <TabItem id="features" active={activeTab === 'features'}>
            <Card>
              <h2 class="mb-4 text-xl font-medium text-cosmos-text">
                {$t('properties.form.features_amenities')}
              </h2>
              
              <!-- Features -->
              <div class="mb-6">
                <h3 class="mb-3 font-medium text-cosmos-text">{$t('properties.property_features')}</h3>
                
                <div class="grid grid-cols-1 gap-y-3 sm:grid-cols-2 md:grid-cols-3">
                  {#each featureOptions as feature}
                    <label class="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={formData.features.includes(feature.id)}
                        on:change={(e) => handleCheckboxArray('features', feature.id, e.target.checked)}
                        class="h-4 w-4 rounded border-cosmos-bg-light bg-cosmos-bg text-primary focus:ring-primary"
                      />
                      <span class="text-sm text-cosmos-text">{feature.label}</span>
                    </label>
                  {/each}
                </div>
                
                {#if errors.features}
                  <p class="mt-1.5 text-sm text-red-500">{errors.features}</p>
                {/if}
              </div>
              
              <!-- Amenities -->
              <div class="mb-6">
                <h3 class="mb-3 font-medium text-cosmos-text">{$t('properties.amenities')}</h3>
                
                <div class="grid grid-cols-1 gap-y-3 sm:grid-cols-2 md:grid-cols-3">
                  {#each amenityOptions as amenity}
                    <label class="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={formData.amenities.includes(amenity.id)}
                        on:change={(e) => handleCheckboxArray('amenities', amenity.id, e.target.checked)}
                        class="h-4 w-4 rounded border-cosmos-bg-light bg-cosmos-bg text-primary focus:ring-primary"
                      />
                      <span class="text-sm text-cosmos-text">{amenity.label}</span>
                    </label>
                  {/each}
                </div>
                
                {#if errors.amenities}
                  <p class="mt-1.5 text-sm text-red-500">{errors.amenities}</p>
                {/if}
              </div>
              
              <!-- Outdoor Spaces -->
              <div class="mb-6">
                <h3 class="mb-3 font-medium text-cosmos-text">{$t('properties.outdoor_spaces')}</h3>
                
                <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
                  <!-- Garden -->
                  <div class="rounded-lg bg-cosmos-bg-light bg-opacity-20 p-4">
                    <label class="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        bind:checked={formData.outdoor_spaces.garden}
                        class="h-4 w-4 rounded border-cosmos-bg-light bg-cosmos-bg text-primary focus:ring-primary"
                      />
                      <span class="text-sm font-medium text-cosmos-text">{$t('properties.features.garden')}</span>
                    </label>
                    
                    {#if formData.outdoor_spaces.garden}
                      <div class="mt-2">
                        <Input
                          type="number"
                          name="garden_size"
                          label={$t('properties.form.area_size')}
                          bind:value={formData.outdoor_spaces.garden_size}
                          placeholder="0"
                          helpText={$t('properties.form.in_square_meters')}
                        />
                      </div>
                    {/if}
                  </div>
                  
                  <!-- Pool -->
                  <div class="rounded-lg bg-cosmos-bg-light bg-opacity-20 p-4">
                    <label class="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        bind:checked={formData.outdoor_spaces.pool}
                        class="h-4 w-4 rounded border-cosmos-bg-light bg-cosmos-bg text-primary focus:ring-primary"
                      />
                      <span class="text-sm font-medium text-cosmos-text">{$t('properties.features.pool')}</span>
                    </label>
                    
                    {#if formData.outdoor_spaces.pool}
                      <div class="mt-2 grid grid-cols-2 gap-2">
                        <div>
                          <label class="text-xs text-cosmos-text-muted">
                            {$t('properties.form.pool_type')}
                          </label>
                          <select
                            bind:value={formData.outdoor_spaces.pool_type}
                            class="mt-1 w-full rounded border border-cosmos-bg-light bg-cosmos-bg p-2 text-sm text-cosmos-text"
                          >
                            <option value="indoor">{$t('properties.form.indoor')}</option>
                            <option value="outdoor">{$t('properties.form.outdoor')}</option>
                            <option value="both">{$t('properties.form.both')}</option>
                          </select>
                        </div>
                        
                        <Input
                          type="number"
                          name="pool_size"
                          label={$t('properties.form.area_size')}
                          bind:value={formData.outdoor_spaces.pool_size}
                          placeholder="0"
                          size="sm"
                        />
                      </div>
                    {/if}
                  </div>
                  
                  <!-- Balcony -->
                  <div class="rounded-lg bg-cosmos-bg-light bg-opacity-20 p-4">
                    <label class="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        bind:checked={formData.outdoor_spaces.balcony}
                        class="h-4 w-4 rounded border-cosmos-bg-light bg-cosmos-bg text-primary focus:ring-primary"
                      />
                      <span class="text-sm font-medium text-cosmos-text">{$t('properties.features.balcony')}</span>
                    </label>
                    
                    {#if formData.outdoor_spaces.balcony}
                      <div class="mt-2">
                        <Input
                          type="number"
                          name="balcony_size"
                          label={$t('properties.form.area_size')}
                          bind:value={formData.outdoor_spaces.balcony_size}
                          placeholder="0"
                          helpText={$t('properties.form.in_square_meters')}
                        />
                      </div>
                    {/if}
                  </div>
                  
                  <!-- Terrace -->
                  <div class="rounded-lg bg-cosmos-bg-light bg-opacity-20 p-4">
                    <label class="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        bind:checked={formData.outdoor_spaces.terrace}
                        class="h-4 w-4 rounded border-cosmos-bg-light bg-cosmos-bg text-primary focus:ring-primary"
                      />
                      <span class="text-sm font-medium text-cosmos-text">{$t('properties.features.terrace')}</span>
                    </label>
                    
                    {#if formData.outdoor_spaces.terrace}
                      <div class="mt-2">
                        <Input
                          type="number"
                          name="terrace_size"
                          label={$t('properties.form.area_size')}
                          bind:value={formData.outdoor_spaces.terrace_size}
                          placeholder="0"
                          helpText={$t('properties.form.in_square_meters')}
                        />
                      </div>
                    {/if}
                  </div>
                </div>
              </div>
              
              <!-- Parking -->
              <div class="mb-6">
                <h3 class="mb-3 font-medium text-cosmos-text">{$t('properties.parking')}</h3>
                
                <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
                  <!-- Parking Type -->
                  <Select
                    name="parking_type"
                    label={$t('properties.parking_type')}
                    options={parkingTypeOptions}
                    bind:value={formData.parking.type}
                    error={errors['parking.type']}
                  />
                  
                  <!-- Parking Spaces -->
                  <Input
                    type="number"
                    name="parking_spaces"
                    label={$t('properties.parking_spaces')}
                    bind:value={formData.parking.spaces}
                    error={errors['parking.spaces']}
                    placeholder="0"
                  />
                  
                  <!-- Underground Parking -->
                  <div class="rounded-lg bg-cosmos-bg-light bg-opacity-20 p-4">
                    <label class="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        bind:checked={formData.parking.underground}
                        class="h-4 w-4 rounded border-cosmos-bg-light bg-cosmos-bg text-primary focus:ring-primary"
                      />
                      <span class="text-sm font-medium text-cosmos-text">{$t('properties.underground_parking')}</span>
                    </label>
                  </div>
                  
                  <!-- Garage Size -->
                  <Input
                    type="number"
                    name="garage_size"
                    label={$t('properties.garage_size')}
                    bind:value={formData.parking.garage_size}
                    error={errors['parking.garage_size']}
                    placeholder="0"
                    helpText={$t('properties.form.in_square_meters')}
                  />
                  
                  <!-- EV Charging -->
                  <div class="rounded-lg bg-cosmos-bg-light bg-opacity-20 p-4">
                    <label class="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        bind:checked={formData.parking.electric_vehicle_charging}
                        class="h-4 w-4 rounded border-cosmos-bg-light bg-cosmos-bg text-primary focus:ring-primary"
                      />
                      <span class="text-sm font-medium text-cosmos-text">{$t('properties.ev_charging')}</span>
                    </label>
                  </div>
                </div>
              </div>
              
              <!-- Building Services -->
              <div class="mb-6">
                <h3 class="mb-3 font-medium text-cosmos-text">{$t('properties.building_services')}</h3>
                
                <div class="grid grid-cols-1 gap-y-3 sm:grid-cols-2 md:grid-cols-4">
                  {#each Object.keys(formData.building_services) as service}
                    <label class="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        bind:checked={formData.building_services[service]}
                        class="h-4 w-4 rounded border-cosmos-bg-light bg-cosmos-bg text-primary focus:ring-primary"
                      />
                      <span class="text-sm text-cosmos-text">{$t(`properties.services.${service}`)}</span>
                    </label>
                  {/each}
                </div>
              </div>
              
              <!-- Infrastructure -->
              <div>
                <h3 class="mb-3 font-medium text-cosmos-text">{$t('properties.infrastructure')}</h3>
                
                <div class="grid grid-cols-1 gap-y-3 sm:grid-cols-2 md:grid-cols-4">
                  {#each Object.keys(formData.infrastructure) as item}
                    <label class="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        bind:checked={formData.infrastructure[item]}
                        class="h-4 w-4 rounded border-cosmos-bg-light bg-cosmos-bg text-primary focus:ring-primary"
                      />
                      <span class="text-sm text-cosmos-text">{$t(`properties.infrastructure.${item}`)}</span>
                    </label>
                  {/each}
                </div>
              </div>
            </Card>
          </TabItem>
          
          <!-- Images Tab -->
          <TabItem id="images" active={activeTab === 'images'}>
            <Card>
              <h2 class="mb-4 text-xl font-medium text-cosmos-text">
                {$t('properties.form.property_images')}
              </h2>
              
              <p class="mb-4 text-cosmos-text-muted">
                {$t('properties.form.images_description')}
              </p>
              
              <!-- Existing Images (if editing) -->
              {#if propertyId && formData.images && formData.images.length > 0}
                <div class="mb-6">
                  <h3 class="mb-3 font-medium text-cosmos-text">{$t('properties.form.existing_images')}</h3>
                  
                  <div class="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
                    {#each formData.images as image, index}
                      <div class="relative rounded-lg border border-cosmos-bg-light bg-cosmos-bg-light overflow-hidden group">
                        <img 
                          src={image.path} 
                          alt={image.caption || $t('properties.form.property_image')} 
                          class="aspect-[4/3] w-full object-cover"
                        />
                        
                        {#if image.is_primary}
                          <div class="absolute bottom-2 right-2">
                            <Badge variant="success" value={$t('properties.form.main_image')} size="sm" />
                          </div>
                        {/if}
                        
                        <div class="absolute inset-0 flex items-center justify-center bg-cosmos-bg-dark bg-opacity-40 opacity-0 transition group-hover:opacity-100">
                          <div class="flex space-x-2">
                            <button
                              type="button"
                              class="rounded-full bg-primary p-2 text-white transition hover:bg-primary-dark"
                              on:click={() => {
                                /* To be implemented - set as main image */
                              }}
                              aria-label={$t('properties.form.set_as_main')}
                            >
                              <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                              </svg>
                            </button>
                            
                            <button
                              type="button"
                              class="rounded-full bg-status-error p-2 text-white transition hover:bg-red-600"
                              on:click={() => {
                                /* To be implemented - remove image */
                              }}
                              aria-label={$t('properties.form.remove_image')}
                            >
                              <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                              </svg>
                            </button>
                          </div>
                        </div>
                      </div>
                    {/each}
                  </div>
                </div>
              {/if}
              
              <!-- New Image Upload -->
              <div>
                <h3 class="mb-3 font-medium text-cosmos-text">{$t('properties.form.upload_images')}</h3>
                
                <div class="mb-4">
                  <div class="flex w-full items-center justify-center">
                    <label
                      for="image-upload"
                      class="flex w-full cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed border-cosmos-bg-light bg-cosmos-bg-light bg-opacity-30 p-6 transition hover:bg-opacity-50"
                    >
                      <div class="flex flex-col items-center justify-center pb-6 pt-5">
                        <svg class="mb-3 h-10 w-10 text-cosmos-text-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                        </svg>
                        <p class="mb-2 text-sm text-cosmos-text"><span class="font-medium">{$t('properties.form.click_to_upload')}</span> {$t('properties.form.or_drag_drop')}</p>
                        <p class="text-xs text-cosmos-text-muted">{$t('properties.form.image_requirements')}</p>
                      </div>
                      <input
                        id="image-upload"
                        type="file"
                        accept="image/*"
                        multiple
                        class="hidden"
                        on:change={handleFileSelect}
                      />
                    </label>
                  </div>
                </div>
                
                <!-- Image previews -->
                {#if formData.imagesPreviews && formData.imagesPreviews.length > 0}
                  <div class="mb-6">
                    <h4 class="mb-2 text-sm font-medium text-cosmos-text">{$t('properties.form.selected_images')}</h4>
                    
                    <div class="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
                      {#each formData.imagesPreviews as preview, index}
                        <div class="relative rounded-lg border border-cosmos-bg-light bg-cosmos-bg-light overflow-hidden group">
                          <img 
                            src={preview} 
                            alt={$t('properties.form.uploaded_image')} 
                            class="aspect-[4/3] w-full object-cover"
                          />
                          
                          {#if formData.main_image_index === index}
                            <div class="absolute bottom-2 right-2">
                              <Badge variant="success" value={$t('properties.form.main_image')} size="sm" />
                            </div>
                          {/if}
                          
                          <div class="absolute inset-0 flex items-center justify-center bg-cosmos-bg-dark bg-opacity-40 opacity-0 transition group-hover:opacity-100">
                            <div class="flex space-x-2">
                              <button
                                type="button"
                                class="rounded-full bg-primary p-2 text-white transition hover:bg-primary-dark"
                                on:click={() => setMainImage(index)}
                                aria-label={$t('properties.form.set_as_main')}
                              >
                                <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                                </svg>
                              </button>
                              
                              <button
                                type="button"
                                class="rounded-full bg-status-error p-2 text-white transition hover:bg-red-600"
                                on:click={() => removeImage(index)}
                                aria-label={$t('properties.form.remove_image')}
                              >
                                <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                                </svg>
                              </button>
                            </div>
                          </div>
                        </div>
                      {/each}
                    </div>
                    
                    {#if errors.images}
                      <p class="mt-2 text-sm text-red-500">{errors.images}</p>
                    {/if}
                  </div>
                {/if}
              </div>
            </Card>
          </TabItem>
          
          <!-- Advanced Tab -->
          <TabItem id="advanced" active={activeTab === 'advanced'}>
            <Card>
              <h2 class="mb-4 text-xl font-medium text-cosmos-text">
                {$t('properties.form.advanced_settings')}
              </h2>
              
              <div class="space-y-4">
                <!-- Featured Property -->
                <div class="rounded-lg bg-cosmos-bg-light bg-opacity-20 p-4">
                  <div class="flex items-start">
                    <div class="flex h-5 items-center">
                      <input
                        id="is_featured"
                        name="is_featured"
                        type="checkbox"
                        bind:checked={formData.is_featured}
                        class="h-4 w-4 rounded border-cosmos-bg-light bg-cosmos-bg text-primary focus:ring-primary"
                      />
                    </div>
                    <div class="ml-3 text-sm">
                      <label for="is_featured" class="font-medium text-cosmos-text">{$t('properties.form.featured_property')}</label>
                      <p class="text-cosmos-text-muted">{$t('properties.form.featured_description')}</p>
                    </div>
                  </div>
                </div>
                
                <!-- Verified Property -->
                <div class="rounded-lg bg-cosmos-bg-light bg-opacity-20 p-4">
                  <div class="flex items-start">
                    <div class="flex h-5 items-center">
                      <input
                        id="is_verified"
                        name="is_verified"
                        type="checkbox"
                        bind:checked={formData.is_verified}
                        class="h-4 w-4 rounded border-cosmos-bg-light bg-cosmos-bg text-primary focus:ring-primary"
                      />
                    </div>
                    <div class="ml-3 text-sm">
                      <label for="is_verified" class="font-medium text-cosmos-text">{$t('properties.form.verified_property')}</label>
                      <p class="text-cosmos-text-muted">{$t('properties.form.verified_description')}</p>
                    </div>
                  </div>
                </div>
                
                <!-- Additional Fields Placeholder -->
                <div class="rounded-lg bg-cosmos-bg-light bg-opacity-10 border border-cosmos-bg-light p-4">
                  <h3 class="mb-2 text-sm font-medium text-cosmos-text-muted">{$t('properties.form.additional_fields')}</h3>
                  <p class="text-xs text-cosmos-text-dim">{$t('properties.form.coming_soon')}</p>
                </div>
              </div>
            </Card>
          </TabItem>
        </div>
        
        <!-- Form Actions -->
        <div class="mt-6 flex items-center justify-end space-x-4 border-t border-cosmos-bg-light pt-6">
          <Button 
            variant="secondary" 
            onClick={onCancel}
            disabled={saving}
          >
            {$t('general.cancel')}
          </Button>
          
          <Button 
            type="submit" 
            variant="primary"
            loading={saving}
            disabled={saving}
          >
            {propertyId ? $t('properties.form.update_property') : $t('properties.form.create_property')}
          </Button>
        </div>
      </form>
    {/if}
  </div>