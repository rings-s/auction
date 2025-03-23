<!-- routes/dashboard/properties/[id]/edit/+page.svelte -->
<script>
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import { page } from '$app/stores';
    import { t, language } from '$lib/i18n';
    import { fade } from 'svelte/transition';
    import { browser } from '$app/environment';
    
    import { api } from '$lib/services/api';
    import { toast } from '$lib/stores/toast';
    import { authStore } from '$lib/stores/auth';
    import { formatCurrency } from '$lib/utils/formatters';
    
    // UI Components
    import Button from '$lib/components/ui/Button.svelte';
    import Card from '$lib/components/ui/Card.svelte';
    import Alert from '$lib/components/ui/Alert.svelte';
    import Spinner from '$lib/components/ui/Spinner.svelte';
    import Input from '$lib/components/ui/Input.svelte';
    import Select from '$lib/components/ui/Select.svelte';
    import Textarea from '$lib/components/ui/Textarea.svelte';
    import Toggle from '$lib/components/ui/Toggle.svelte';
    import ImageUpload from '$lib/components/ui/ImageUpload.svelte';
    import LocationPicker from '$lib/components/maps/LocationPicker.svelte';
    import Breadcrumb from '$lib/components/ui/Breadcrumb.svelte';
    
    // State
    let originalProperty = null;
    let formData = {
      title: '',
      description: '',
      property_type: '',
      status: '',
      estimated_value: '',
      area: '',
      bedrooms: '',
      bathrooms: '',
      year_built: '',
      address: '',
      city: '',
      district: '',
      country: '',
      postal_code: '',
      latitude: null,
      longitude: null,
      features: [],
      is_featured: false,
      is_published: false,
      images: []
    };
    
    let newImages = [];
    let imagesToDelete = [];
    let activeTab = 'basic';
    let loading = true;
    let saving = false;
    let error = null;
    let validationErrors = {};
    let formTouched = false;
    let mapLoaded = false;
    
    // Extract property ID from URL
    $: propertyId = $page.params.id;
    
    // Auth state
    $: isAuthenticated = $authStore.isAuthenticated;
    $: currentUser = $authStore.user;
    
    // Check for RTL layout
    $: isRTL = $language === 'ar';
    
    // Define property types
    const propertyTypes = [
      { value: 'apartment', label: $t('properties.types.apartment') },
      { value: 'villa', label: $t('properties.types.villa') },
      { value: 'land', label: $t('properties.types.land') },
      { value: 'commercial', label: $t('properties.types.commercial') },
      { value: 'industrial', label: $t('properties.types.industrial') },
      { value: 'mixed_use', label: $t('properties.types.mixed_use') },
      { value: 'building', label: $t('properties.types.building') },
      { value: 'farm', label: $t('properties.types.farm') },
      { value: 'office', label: $t('properties.types.office') },
      { value: 'retail', label: $t('properties.types.retail') }
    ];
    
    // Define property statuses
    const propertyStatuses = [
      { value: 'draft', label: $t('properties.status.draft') },
      { value: 'pending_approval', label: $t('properties.status.pending_approval') },
      { value: 'active', label: $t('properties.status.active') },
      { value: 'inactive', label: $t('properties.status.inactive') }
    ];
    
    // Define common property features
    const commonFeatures = [
      { value: 'pool', label: $t('properties.features.pool') },
      { value: 'garden', label: $t('properties.features.garden') },
      { value: 'garage', label: $t('properties.features.garage') },
      { value: 'air_conditioning', label: $t('properties.features.air_conditioning') },
      { value: 'heating', label: $t('properties.features.heating') },
      { value: 'elevator', label: $t('properties.features.elevator') },
      { value: 'security_system', label: $t('properties.features.security_system') },
      { value: 'balcony', label: $t('properties.features.balcony') },
      { value: 'gym', label: $t('properties.features.gym') },
      { value: 'furnished', label: $t('properties.features.furnished') },
      { value: 'pets_allowed', label: $t('properties.features.pets_allowed') },
      { value: 'parking', label: $t('properties.features.parking') }
    ];
    
    // Form tabs
    const tabs = [
      { id: 'basic', label: $t('properties.edit.tabs.basic') },
      { id: 'details', label: $t('properties.edit.tabs.details') },
      { id: 'location', label: $t('properties.edit.tabs.location') },
      { id: 'features', label: $t('properties.edit.tabs.features') },
      { id: 'images', label: $t('properties.edit.tabs.images') }
    ];
    
    // Breadcrumb items
    $: breadcrumbItems = [
      { label: $t('navigation.dashboard'), href: '/dashboard' },
      { label: $t('navigation.my_properties'), href: '/dashboard/properties' },
      { label: formData.title || $t('properties.edit.title'), active: true }
    ];
    
    // Fetch property data
    async function loadProperty() {
      if (!isAuthenticated) {
        goto('/auth/login');
        return;
      }
      
      loading = true;
      error = null;
      
      try {
        const response = await api.get(`/properties/${propertyId}/`);
        
        if (response?.data?.property) {
          originalProperty = response.data.property;
          
          // Check if user has permission to edit
          if (originalProperty.owner?.id !== currentUser?.id && !currentUser?.isAdmin) {
            error = $t('properties.edit.unauthorized');
            return;
          }
          
          // Fill form with property data
          for (const key in formData) {
            if (key in originalProperty) {
              formData[key] = originalProperty[key];
            }
          }
          
          // Convert features array if needed
          if (typeof originalProperty.features === 'string') {
            try {
              formData.features = JSON.parse(originalProperty.features);
            } catch (e) {
              formData.features = [];
            }
          } else if (Array.isArray(originalProperty.features)) {
            formData.features = [...originalProperty.features];
          }
          
          // Handle images
          if (originalProperty.images && Array.isArray(originalProperty.images)) {
            formData.images = [...originalProperty.images];
          } else if (originalProperty.main_image_url) {
            formData.images = [originalProperty.main_image_url];
          }
        } else {
          throw new Error('Invalid response format');
        }
      } catch (err) {
        console.error('Error fetching property details:', err);
        error = err.response?.data?.error || $t('system_messages.error_occurred');
      } finally {
        loading = false;
      }
    }
    
    // Handle tab switching
    function setActiveTab(tabId) {
      activeTab = tabId;
    }
    
    // Handle image upload
    function handleImageUpload(event) {
      const files = event.detail.files;
      if (files && files.length > 0) {
        newImages = [...newImages, ...files];
      }
    }
    
    // Remove existing image
    function removeExistingImage(index) {
      const imageUrl = formData.images[index];
      imagesToDelete.push(imageUrl);
      formData.images = formData.images.filter((_, i) => i !== index);
      formTouched = true;
    }
    
    // Remove new image
    function removeNewImage(index) {
      newImages = newImages.filter((_, i) => i !== index);
      formTouched = true;
    }
    
    // Toggle feature selection
    function toggleFeature(feature) {
      if (formData.features.includes(feature)) {
        formData.features = formData.features.filter(f => f !== feature);
      } else {
        formData.features = [...formData.features, feature];
      }
      formTouched = true;
    }
    
    // Handle location change
    function handleLocationChange(event) {
      const { lat, lng } = event.detail;
      formData.latitude = lat;
      formData.longitude = lng;
      formTouched = true;
    }
    
    // Validate form before submission
    function validateForm() {
      validationErrors = {};
      let isValid = true;
      
      // Required fields
      if (!formData.title) {
        validationErrors.title = $t('properties.edit.errors.title_required');
        isValid = false;
      }
      
      if (!formData.property_type) {
        validationErrors.property_type = $t('properties.edit.errors.property_type_required');
        isValid = false;
      }
      
      // Numeric validation
      if (formData.estimated_value && isNaN(parseFloat(formData.estimated_value))) {
        validationErrors.estimated_value = $t('properties.edit.errors.numeric_value');
        isValid = false;
      }
      
      if (formData.area && isNaN(parseFloat(formData.area))) {
        validationErrors.area = $t('properties.edit.errors.numeric_value');
        isValid = false;
      }
      
      if (formData.bedrooms && isNaN(parseInt(formData.bedrooms))) {
        validationErrors.bedrooms = $t('properties.edit.errors.integer_value');
        isValid = false;
      }
      
      if (formData.bathrooms && isNaN(parseInt(formData.bathrooms))) {
        validationErrors.bathrooms = $t('properties.edit.errors.integer_value');
        isValid = false;
      }
      
      if (formData.year_built && (isNaN(parseInt(formData.year_built)) || parseInt(formData.year_built) < 1800 || parseInt(formData.year_built) > new Date().getFullYear())) {
        validationErrors.year_built = $t('properties.edit.errors.invalid_year');
        isValid = false;
      }
      
      return isValid;
    }
    
    // Save property
    async function handleSubmit() {
      if (!validateForm()) {
        // Find the first tab with errors and switch to it
        for (const field in validationErrors) {
          if (field === 'title' || field === 'property_type' || field === 'status') {
            setActiveTab('basic');
            break;
          } else if (field === 'estimated_value' || field === 'area' || field === 'bedrooms' || field === 'bathrooms' || field === 'year_built') {
            setActiveTab('details');
            break;
          } else if (field === 'address' || field === 'city' || field === 'district' || field === 'country' || field === 'postal_code' || field === 'latitude' || field === 'longitude') {
            setActiveTab('location');
            break;
          }
        }
        
        toast.error($t('properties.edit.errors.fix_errors'));
        return;
      }
      
      saving = true;
      error = null;
      
      try {
        // Prepare form data for submission
        const propertyData = new FormData();
        
        // Add text fields
        for (const key in formData) {
          if (key !== 'images' && key !== 'features' && formData[key] !== null && formData[key] !== undefined) {
            propertyData.append(key, formData[key]);
          }
        }
        
        // Add features as JSON
        if (formData.features && formData.features.length > 0) {
          propertyData.append('features', JSON.stringify(formData.features));
        }
        
        // Add new images
        newImages.forEach((file, index) => {
          propertyData.append(`image_${index}`, file);
        });
        
        // Add list of images to delete
        if (imagesToDelete.length > 0) {
          propertyData.append('images_to_delete', JSON.stringify(imagesToDelete));
        }
        
        // Send update request
        const response = await api.patch(`/properties/${propertyId}/`, propertyData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
        
        if (response?.data?.property) {
          toast.success($t('properties.edit.success'));
          
          // Redirect to property details after short delay
          setTimeout(() => {
            goto(`/dashboard/properties/${propertyId}`);
          }, 1500);
        } else {
          throw new Error('Invalid response format');
        }
      } catch (err) {
        console.error('Error updating property:', err);
        error = err.response?.data?.error || $t('system_messages.error_occurred');
        
        // Handle validation errors from API
        if (err.response?.data?.errors) {
          validationErrors = { ...validationErrors, ...err.response.data.errors };
        }
        
        toast.error($t('properties.edit.error'));
      } finally {
        saving = false;
      }
    }
    
    // Cancel and return to property details
    function cancelEdit() {
      if (formTouched) {
        // Show confirmation dialog before navigating away
        if (confirm($t('properties.edit.unsaved_changes'))) {
          goto(`/dashboard/properties/${propertyId}`);
        }
      } else {
        goto(`/dashboard/properties/${propertyId}`);
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
    <title>{$t('properties.edit.title')} | {$t('general.app_name')}</title>
  </svelte:head>
  
  <div class="container mx-auto px-4 py-8" class:rtl={isRTL}>
    <!-- Breadcrumb -->
    <div class="mb-6">
      <Breadcrumb items={breadcrumbItems} />
    </div>
    
    <!-- Page header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-neutral-900 dark:text-white mb-2">
        {$t('properties.edit.title')}
      </h1>
      <p class="text-neutral-500 dark:text-neutral-400">
        {$t('properties.edit.subtitle')}
      </p>
    </div>
    
    {#if loading}
      <div class="py-12 text-center">
        <Spinner size="lg" text={$t('general.loading')} />
      </div>
    {:else if error && !originalProperty}
      <Alert type="error" title={$t('general.error')} class="mb-6">
        <p>{error}</p>
        <div class="mt-4">
          <Button 
            variant="primary"
            on:click={loadProperty}
          >
            {$t('general.retry')}
          </Button>
        </div>
      </Alert>
    {:else if originalProperty}
      <div in:fade={{ duration: 300 }} class="grid grid-cols-1 md:grid-cols-12 gap-8">
        <!-- Form tabs for navigation (mobile) -->
        <div class="md:hidden col-span-full overflow-x-auto mb-2">
          <div class="flex space-x-2 border-b border-neutral-200 dark:border-neutral-700">
            {#each tabs as tab}
              <button
                type="button"
                class="px-4 py-2 text-sm font-medium whitespace-nowrap {activeTab === tab.id 
                  ? 'text-primary border-b-2 border-primary'
                  : 'text-neutral-600 hover:text-neutral-900 dark:text-neutral-400 dark:hover:text-white'}"
                on:click={() => setActiveTab(tab.id)}
              >
                {tab.label}
              </button>
            {/each}
          </div>
        </div>
        
        <!-- Sidebar navigation (desktop) -->
        <div class="hidden md:block md:col-span-3 lg:col-span-2">
          <Card padding={false} class="sticky top-20">
            <div class="py-4">
              {#each tabs as tab, index}
                <button
                  type="button"
                  class="w-full text-left px-4 py-3 {activeTab === tab.id 
                    ? 'bg-primary-50 text-primary dark:bg-primary-900/20 dark:text-primary-300'
                    : 'text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900 dark:text-neutral-400 dark:hover:bg-neutral-800 dark:hover:text-white'}"
                  on:click={() => setActiveTab(tab.id)}
                >
                  <div class="flex items-center">
                    <span class="flex h-6 w-6 items-center justify-center rounded-full bg-neutral-200 text-xs font-medium text-neutral-800 dark:bg-neutral-700 dark:text-neutral-300 mr-3">
                      {index + 1}
                    </span>
                    {tab.label}
                  </div>
                </button>
              {/each}
            </div>
            
            <div class="border-t border-neutral-200 dark:border-neutral-700 p-4">
              <Button 
                variant="outline"
                class="w-full mb-2"
                on:click={cancelEdit}
                disabled={saving}
              >
                {$t('general.cancel')}
              </Button>
              
              <Button 
                variant="primary"
                class="w-full"
                on:click={handleSubmit}
                loading={saving}
                disabled={saving}
              >
                {saving ? $t('properties.edit.saving') : $t('properties.edit.save')}
              </Button>
            </div>
          </Card>
        </div>
        
        <!-- Main form content -->
        <div class="md:col-span-9 lg:col-span-10">
          <Card padding={true}>
            {#if error}
              <Alert type="error" title={$t('general.error')} class="mb-6">
                <p>{error}</p>
              </Alert>
            {/if}
            
            <form on:submit|preventDefault={handleSubmit}>
              <!-- Basic information tab -->
              <div class="tab-content" class:hidden={activeTab !== 'basic'}>
                <h2 class="text-xl font-semibold mb-6">{$t('properties.edit.tabs.basic')}</h2>
                
                <div class="grid grid-cols-1 gap-6">
                  <Input
                    type="text"
                    label={$t('properties.title')}
                    placeholder={$t('properties.edit.placeholders.title')}
                    bind:value={formData.title}
                    error={validationErrors.title}
                    required
                    on:input={() => formTouched = true}
                  />
                  
                  <Select
                    label={$t('properties.property_type')}
                    options={propertyTypes}
                    bind:value={formData.property_type}
                    error={validationErrors.property_type}
                    required
                    on:change={() => formTouched = true}
                  />
                  
                  <Select
                    label={$t('properties.property_status')}
                    options={propertyStatuses}
                    bind:value={formData.status}
                    error={validationErrors.status}
                    on:change={() => formTouched = true}
                  />
                  
                  <Textarea
                    label={$t('properties.property_description')}
                    placeholder={$t('properties.edit.placeholders.description')}
                    bind:value={formData.description}
                    error={validationErrors.description}
                    rows={5}
                    on:input={() => formTouched = true}
                  />
                  
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <Toggle
                      label={$t('properties.is_featured')}
                      description={$t('properties.edit.featured_description')}
                      bind:checked={formData.is_featured}
                      on:change={() => formTouched = true}
                    />
                    
                    <Toggle
                      label={$t('properties.is_published')}
                      description={$t('properties.edit.published_description')}
                      bind:checked={formData.is_published}
                      on:change={() => formTouched = true}
                    />
                  </div>
                </div>
              </div>
              
              <!-- Detailed specifications tab -->
              <div class="tab-content" class:hidden={activeTab !== 'details'}>
                <h2 class="text-xl font-semibold mb-6">{$t('properties.edit.tabs.details')}</h2>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <Input
                    type="number"
                    label={$t('properties.estimated_value')}
                    placeholder={$t('properties.edit.placeholders.estimated_value')}
                    prefix={$t('properties.currency')}
                    bind:value={formData.estimated_value}
                    error={validationErrors.estimated_value}
                    on:input={() => formTouched = true}
                  />
                  
                  <Input
                    type="number"
                    label={$t('properties.property_area')}
                    placeholder={$t('properties.edit.placeholders.area')}
                    suffix={$t('properties.area_unit')}
                    bind:value={formData.area}
                    error={validationErrors.area}
                    on:input={() => formTouched = true}
                  />
                  
                  <Input
                    type="number"
                    label={$t('properties.bedrooms')}
                    placeholder={$t('properties.edit.placeholders.bedrooms')}
                    bind:value={formData.bedrooms}
                    error={validationErrors.bedrooms}
                    on:input={() => formTouched = true}
                  />
                  
                  <Input
                    type="number"
                    label={$t('properties.bathrooms')}
                    placeholder={$t('properties.edit.placeholders.bathrooms')}
                    bind:value={formData.bathrooms}
                    error={validationErrors.bathrooms}
                    on:input={() => formTouched = true}
                  />
                  
                  <Input
                    type="number"
                    label={$t('properties.year_built')}
                    placeholder={$t('properties.edit.placeholders.year_built')}
                    bind:value={formData.year_built}
                    error={validationErrors.year_built}
                    min="1800"
                    max={new Date().getFullYear().toString()}
                    on:input={() => formTouched = true}
                  />
                </div>
              </div>
              
              <!-- Location tab -->
              <div class="tab-content" class:hidden={activeTab !== 'location'}>
                <h2 class="text-xl font-semibold mb-6">{$t('properties.edit.tabs.location')}</h2>
                
                <div class="grid grid-cols-1 gap-6">
                  <Input
                    type="text"
                    label={$t('properties.property_address')}
                    placeholder={$t('properties.edit.placeholders.address')}
                    bind:value={formData.address}
                    error={validationErrors.address}
                    on:input={() => formTouched = true}
                  />
                  
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <Input
                      type="text"
                      label={$t('properties.property_city')}
                      placeholder={$t('properties.edit.placeholders.city')}
                      bind:value={formData.city}
                      error={validationErrors.city}
                      on:input={() => formTouched = true}
                    />
                    
                    <Input
                      type="text"
                      label={$t('properties.property_district')}
                      placeholder={$t('properties.edit.placeholders.district')}
                      bind:value={formData.district}
                      error={validationErrors.district}
                      on:input={() => formTouched = true}
                    />
                  </div>
                  
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <Input
                      type="text"
                      label={$t('properties.property_country')}
                      placeholder={$t('properties.edit.placeholders.country')}
                      bind:value={formData.country}
                      error={validationErrors.country}
                      on:input={() => formTouched = true}
                    />
                    
                    <Input
                      type="text"
                      label={$t('properties.property_postal_code')}
                      placeholder={$t('properties.edit.placeholders.postal_code')}
                      bind:value={formData.postal_code}
                      error={validationErrors.postal_code}
                      on:input={() => formTouched = true}
                    />
                  </div>
                  
                  <div class="mt-4">
                    <label class="mb-2 block text-sm font-medium text-neutral-900 dark:text-white">
                      {$t('properties.edit.map_location')}
                    </label>
                    
                    <div class="h-80 rounded-lg overflow-hidden">
                      <LocationPicker
                        latitude={formData.latitude}
                        longitude={formData.longitude}
                        on:change={handleLocationChange}
                        on:load={() => mapLoaded = true}
                      />
                    </div>
                    
                    {#if !mapLoaded}
                      <p class="mt-2 text-sm text-neutral-500 dark:text-neutral-400">
                        {$t('properties.edit.map_loading')}
                      </p>
                    {/if}
                    
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                      <Input
                        type="number"
                        label={$t('properties.latitude')}
                        step="0.000001"
                        bind:value={formData.latitude}
                        error={validationErrors.latitude}
                        on:input={() => formTouched = true}
                      />
                      
                      <Input
                        type="number"
                        label={$t('properties.longitude')}
                        step="0.000001"
                        bind:value={formData.longitude}
                        error={validationErrors.longitude}
                        on:input={() => formTouched = true}
                      />
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Features tab -->
              <div class="tab-content" class:hidden={activeTab !== 'features'}>
                <h2 class="text-xl font-semibold mb-6">{$t('properties.edit.tabs.features')}</h2>
                
                <p class="mb-4 text-neutral-500 dark:text-neutral-400">
                  {$t('properties.edit.features_description')}
                </p>
                
                <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  {#each commonFeatures as feature}
                    <div class="flex items-center">
                      <input
                        type="checkbox"
                        id={`feature-${feature.value}`}
                        class="h-5 w-5 rounded border-neutral-300 text-primary focus:ring-primary dark:border-neutral-700 dark:bg-neutral-800"
                        checked={formData.features.includes(feature.value)}
                        on:change={() => toggleFeature(feature.value)}
                      />
                      <label
                        for={`feature-${feature.value}`}
                        class="ml-2 text-sm text-neutral-900 dark:text-neutral-100"
                      >
                        {feature.label}
                      </label>
                    </div>
                  {/each}
                </div>
                
                <div class="mt-6">
                  <label class="mb-2 block text-sm font-medium text-neutral-900 dark:text-white">
                    {$t('properties.edit.additional_features')}
                  </label>
                  
                  <Textarea
                    placeholder={$t('properties.edit.placeholders.additional_features')}
                    rows={3}
                    on:input={() => formTouched = true}
                  />
                  
                  <p class="mt-2 text-sm text-neutral-500 dark:text-neutral-400">
                    {$t('properties.edit.features_hint')}
                  </p>
                </div>
              </div>
              
              <!-- Images tab -->
              <div class="tab-content" class:hidden={activeTab !== 'images'}>
                <h2 class="text-xl font-semibold mb-6">{$t('properties.edit.tabs.images')}</h2>
                
                <!-- Existing images -->
                {#if formData.images && formData.images.length > 0}
                  <div class="mb-6">
                    <h3 class="text-sm font-medium text-neutral-900 dark:text-white mb-3">
                      {$t('properties.edit.current_images')}
                    </h3>
                    
                    <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                      {#each formData.images as image, index}
                        <div class="relative group rounded-lg overflow-hidden border border-neutral-200 dark:border-neutral-700">
                          <img 
                            src={image} 
                            alt={`Property image ${index + 1}`}
                            class="w-full h-48 object-cover"
                          />
                          
                          <!-- Remove image button -->
                          <button
                            type="button"
                            class="absolute top-2 right-2 bg-black/60 text-white rounded-full p-1.5 opacity-0 group-hover:opacity-100 focus:opacity-100 transition-opacity"
                            on:click={() => removeExistingImage(index)}
                            title={$t('properties.edit.remove_image')}
                          >
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                              <path d="M6 18L18 6M6 6l12 12" />
                            </svg>
                          </button>
                          
                          <!-- Main image indicator -->
                          {#if index === 0}
                            <div class="absolute bottom-0 left-0 right-0 bg-primary text-white text-xs py-1 text-center">
                              {$t('properties.edit.main_image')}
                            </div>
                          {/if}
                        </div>
                      {/each}
                    </div>
                  </div>
                {/if}
                
                <!-- New images -->
                {#if newImages.length > 0}
                  <div class="mb-6">
                    <h3 class="text-sm font-medium text-neutral-900 dark:text-white mb-3">
                      {$t('properties.edit.new_images')}
                    </h3>
                    
                    <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                      {#each newImages as image, index}
                        <div class="relative group rounded-lg overflow-hidden border border-neutral-200 dark:border-neutral-700">
                          <img 
                            src={URL.createObjectURL(image)} 
                            alt={`New property image ${index + 1}`}
                            class="w-full h-48 object-cover"
                          />
                          
                          <!-- Remove image button -->
                          <button
                            type="button"
                            class="absolute top-2 right-2 bg-black/60 text-white rounded-full p-1.5 opacity-0 group-hover:opacity-100 focus:opacity-100 transition-opacity"
                            on:click={() => removeNewImage(index)}
                            title={$t('properties.edit.remove_image')}
                          >
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                              <path d="M6 18L18 6M6 6l12 12" />
                            </svg>
                          </button>
                        </div>
                      {/each}
                    </div>
                  </div>
                {/if}
                
                <!-- Image upload -->
                <div class="mt-4">
                  <ImageUpload
                    label={$t('properties.edit.upload_images')}
                    description={$t('properties.edit.upload_description')}
                    accept="image/jpeg,image/png,image/jpg"
                    multiple={true}
                    maxSize={5}
                    on:upload={handleImageUpload}
                    error={validationErrors.images}
                  />
                </div>
              </div>
            </form>
          </Card>
          
          <!-- Mobile action buttons -->
          <div class="md:hidden mt-6 flex flex-col-reverse sm:flex-row sm:justify-between sm:space-x-2">
            <Button 
              variant="outline"
              class="mt-4 sm:mt-0 w-full sm:w-auto"
              on:click={cancelEdit}
              disabled={saving}
            >
              {$t('general.cancel')}
            </Button>
            
            <Button 
              variant="primary"
              class="w-full sm:w-auto"
              on:click={handleSubmit}
              loading={saving}
              disabled={saving}
            >
              {saving ? $t('properties.edit.saving') : $t('properties.edit.save')}
            </Button>
          </div>
        </div>
      </div>
    {/if}
  </div>
  
  <style>
    /* RTL Support */
    .rtl {
      direction: rtl;
      text-align: right;
    }
    
    .rtl .mr-3 {
      margin-right: 0;
      margin-left: 0.75rem;
    }
    
    .rtl .ml-2 {
      margin-left: 0;
      margin-right: 0.5rem;
    }
    
    .rtl .space-x-2 > * + * {
      margin-left: 0;
      margin-right: 0.5rem;
    }
    
    /* Fix tab button spacing in RTL */
    .rtl .space-x-2 {
      margin-right: 0;
    }
    
    /* Ensure icons are properly aligned in RTL */
    .rtl .svg-icon {
      transform: scaleX(-1);
    }
  </style>