<!-- src/routes/auctions/create/+page.svelte -->
<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { api } from '$lib/api';
  import { notificationStore } from '$lib/stores/notificationStore';
  import Button from '$lib/components/ui/Button.svelte';
  import Spinner from '$lib/components/ui/Spinner.svelte';
  import Alert from '$lib/components/ui/Alert.svelte';
  import { isAuthenticated, primaryRole } from '$lib/stores/authStore';
  
  // Form data
  let formData = {
    auction: {
      title: '',
      description: '',
      category: '',
      subcategory: null,
      start_time: '',
      end_time: '',
      starting_price: '',
      reserve_price: '',
      minimum_bid_increment: '',
      currency: 'USD',
      status: 'DRAFT'
    },
    timer: {
      duration: '7D',
      auto_extend: true,
      extension_threshold: 5, // 5 minutes (will be converted to seconds for API)
      extension_duration: 5 // 5 minutes (will be converted to seconds for API)
    },
    auction_type: '',
    specific_data: {}
  };
  
  // State variables
  let categories = [];
  let subcategories = [];
  let loading = {
    categories: true,
    subcategories: false,
    submit: false
  };
  let error = '';
  let imageFile = null;
  let imagePreview = null;
  let additionalImages = [];
  let additionalImagePreviews = [];
  
  // Available auction types
  const auctionTypes = [
    { value: 'real_estate', label: 'Real Estate' },
    { value: 'vehicle', label: 'Vehicle' },
    { value: 'machinery', label: 'Machinery' },
    { value: 'factory', label: 'Factory' },
    { value: 'heavy_vehicle', label: 'Heavy Vehicle' }
  ];
  
  // Load categories
  async function loadCategories() {
    try {
      loading.categories = true;
      const response = await api.category.list({
        params: { is_active: true }
      });
      categories = response.results || [];
      loading.categories = false;
    } catch (err) {
      console.error('Error loading categories:', err);
      loading.categories = false;
    }
  }
  
  // Load subcategories when category changes
  async function loadSubcategories() {
    if (!formData.auction.category) {
      subcategories = [];
      formData.auction.subcategory = null;
      return;
    }
    
    try {
      loading.subcategories = true;
      const response = await api.category.listSubcategories(formData.auction.category);
      subcategories = response.results || [];
      loading.subcategories = false;
    } catch (err) {
      console.error('Error loading subcategories:', err);
      loading.subcategories = false;
    }
  }
  
  // Watch for category change
  $: if (formData.auction.category) {
    loadSubcategories();
  }
  
  // Handle image upload
  function handleImageChange(event) {
    const file = event.target.files[0];
    if (file) {
      imageFile = file;
      const reader = new FileReader();
      reader.onload = e => {
        imagePreview = e.target.result;
      };
      reader.readAsDataURL(file);
    }
  }
  
  // Handle additional images upload
  function handleAdditionalImagesChange(event) {
    const files = Array.from(event.target.files);
    additionalImages = [...additionalImages, ...files].slice(0, 5); // Limit to 5 images
    
    // Reset previews and generate new ones
    additionalImagePreviews = [];
    
    additionalImages.forEach(file => {
      const reader = new FileReader();
      reader.onload = e => {
        additionalImagePreviews = [...additionalImagePreviews, e.target.result];
      };
      reader.readAsDataURL(file);
    });
  }
  
  // Remove additional image
  function removeAdditionalImage(index) {
    additionalImages = additionalImages.filter((_, i) => i !== index);
    additionalImagePreviews = additionalImagePreviews.filter((_, i) => i !== index);
  }
  
  // Handle auction type change
  function handleAuctionTypeChange(event) {
    formData.auction_type = event.target.value;
    
    // Reset specific data
    formData.specific_data = {};
    
    // Initialize specific data based on auction type
    if (formData.auction_type === 'real_estate') {
      formData.specific_data = {
        property_type: 'RESIDENTIAL',
        size_sqm: '',
        location: '',
        address: '',
        bedrooms: '',
        bathrooms: '',
        year_built: '',
        zoning_info: '',
        legal_description: '',
        property_condition: '',
        historical_value: {}
      };
    } else if (formData.auction_type === 'vehicle') {
      formData.specific_data = {
        make: '',
        model: '',
        year: '',
        mileage: '',
        condition: '',
        vin: '',
        engine_type: '',
        transmission: '',
        fuel_type: '',
        color: '',
        registration_number: '',
        service_history: {}
      };
    } else if (formData.auction_type === 'machinery') {
      formData.specific_data = {
        machine_type: '',
        manufacturer: '',
        model_number: '',
        year_manufactured: '',
        operating_hours: '',
        power_requirements: '',
        dimensions: '',
        weight: '',
        capacity: '',
        maintenance_history: {},
        safety_certificates: {},
        technical_specifications: {}
      };
    } else if (formData.auction_type === 'factory') {
      formData.specific_data = {
        total_area_sqm: '',
        built_up_area_sqm: '',
        location: '',
        address: '',
        production_capacity: '',
        power_capacity: '',
        water_supply: '',
        waste_management: '',
        environmental_certificates: {},
        infrastructure_details: {},
        utility_connections: {}
      };
    } else if (formData.auction_type === 'heavy_vehicle') {
      formData.specific_data = {
        vehicle_type: '',
        make: '',
        model: '',
        year: '',
        load_capacity: '',
        operating_hours: '',
        engine_power: '',
        registration_number: '',
        compliance_certificates: {},
        maintenance_history: {}
      };
    }
  }
  
  // Dynamic fields based on auction type
  function getAuctionTypeFields() {
    if (formData.auction_type === 'real_estate') {
      return [
        { name: 'property_type', label: 'Property Type', type: 'select', options: [
          { value: 'RESIDENTIAL', label: 'Residential' },
          { value: 'COMMERCIAL', label: 'Commercial' },
          { value: 'INDUSTRIAL', label: 'Industrial' },
          { value: 'LAND', label: 'Land' }
        ]},
        { name: 'size_sqm', label: 'Size (sqm)', type: 'number' },
        { name: 'location', label: 'Location', type: 'text' },
        { name: 'address', label: 'Address', type: 'textarea' },
        { name: 'bedrooms', label: 'Bedrooms', type: 'number' },
        { name: 'bathrooms', label: 'Bathrooms', type: 'number' },
        { name: 'year_built', label: 'Year Built', type: 'number' },
        { name: 'zoning_info', label: 'Zoning Information', type: 'textarea' },
        { name: 'legal_description', label: 'Legal Description', type: 'textarea' },
        { name: 'property_condition', label: 'Property Condition', type: 'textarea' }
      ];
    } else if (formData.auction_type === 'vehicle') {
      return [
        { name: 'make', label: 'Make', type: 'text' },
        { name: 'model', label: 'Model', type: 'text' },
        { name: 'year', label: 'Year', type: 'number' },
        { name: 'mileage', label: 'Mileage', type: 'number' },
        { name: 'condition', label: 'Condition', type: 'select', options: [
          { value: 'New', label: 'New' },
          { value: 'Like New', label: 'Like New' },
          { value: 'Excellent', label: 'Excellent' },
          { value: 'Good', label: 'Good' },
          { value: 'Fair', label: 'Fair' },
          { value: 'Poor', label: 'Poor' }
        ]},
        { name: 'vin', label: 'VIN', type: 'text' },
        { name: 'engine_type', label: 'Engine Type', type: 'text' },
        { name: 'transmission', label: 'Transmission', type: 'select', options: [
          { value: 'Automatic', label: 'Automatic' },
          { value: 'Manual', label: 'Manual' },
          { value: 'Semi-Automatic', label: 'Semi-Automatic' },
          { value: 'CVT', label: 'CVT' }
        ]},
        { name: 'fuel_type', label: 'Fuel Type', type: 'select', options: [
          { value: 'Gasoline', label: 'Gasoline' },
          { value: 'Diesel', label: 'Diesel' },
          { value: 'Electric', label: 'Electric' },
          { value: 'Hybrid', label: 'Hybrid' },
          { value: 'Plug-in Hybrid', label: 'Plug-in Hybrid' },
          { value: 'Other', label: 'Other' }
        ]},
        { name: 'color', label: 'Color', type: 'text' },
        { name: 'registration_number', label: 'Registration Number', type: 'text' }
      ];
    } else if (formData.auction_type === 'machinery') {
      return [
        { name: 'machine_type', label: 'Machine Type', type: 'text' },
        { name: 'manufacturer', label: 'Manufacturer', type: 'text' },
        { name: 'model_number', label: 'Model Number', type: 'text' },
        { name: 'year_manufactured', label: 'Year Manufactured', type: 'number' },
        { name: 'operating_hours', label: 'Operating Hours', type: 'number' },
        { name: 'power_requirements', label: 'Power Requirements', type: 'text' },
        { name: 'dimensions', label: 'Dimensions', type: 'text' },
        { name: 'weight', label: 'Weight (kg)', type: 'number' },
        { name: 'capacity', label: 'Capacity', type: 'text' }
      ];
    } else if (formData.auction_type === 'factory') {
      return [
        { name: 'total_area_sqm', label: 'Total Area (sqm)', type: 'number' },
        { name: 'built_up_area_sqm', label: 'Built-up Area (sqm)', type: 'number' },
        { name: 'location', label: 'Location', type: 'text' },
        { name: 'address', label: 'Address', type: 'textarea' },
        { name: 'production_capacity', label: 'Production Capacity', type: 'textarea' },
        { name: 'power_capacity', label: 'Power Capacity', type: 'text' },
        { name: 'water_supply', label: 'Water Supply', type: 'text' },
        { name: 'waste_management', label: 'Waste Management', type: 'textarea' }
      ];
    } else if (formData.auction_type === 'heavy_vehicle') {
      return [
        { name: 'vehicle_type', label: 'Vehicle Type', type: 'text' },
        { name: 'make', label: 'Make', type: 'text' },
        { name: 'model', label: 'Model', type: 'text' },
        { name: 'year', label: 'Year', type: 'number' },
        { name: 'load_capacity', label: 'Load Capacity (tons)', type: 'number' },
        { name: 'operating_hours', label: 'Operating Hours', type: 'number' },
        { name: 'engine_power', label: 'Engine Power', type: 'text' },
        { name: 'registration_number', label: 'Registration Number', type: 'text' }
      ];
    }
    
    return [];
  }
  
  // Handle JSON fields that need to be serialized
  function prepareFormDataForSubmission() {
    const preparedData = JSON.parse(JSON.stringify(formData));
    
    // Convert timer values from minutes to seconds
    preparedData.timer.extension_threshold = preparedData.timer.extension_threshold * 60;
    preparedData.timer.extension_duration = preparedData.timer.extension_duration * 60;
    
    // Handle JSON fields based on auction type
    if (formData.auction_type === 'real_estate') {
      preparedData.specific_data.historical_value = JSON.stringify({});
    } else if (formData.auction_type === 'vehicle') {
      preparedData.specific_data.service_history = JSON.stringify({});
    } else if (formData.auction_type === 'machinery') {
      preparedData.specific_data.maintenance_history = JSON.stringify({});
      preparedData.specific_data.safety_certificates = JSON.stringify({});
      preparedData.specific_data.technical_specifications = JSON.stringify({});
    } else if (formData.auction_type === 'factory') {
      preparedData.specific_data.environmental_certificates = JSON.stringify({});
      preparedData.specific_data.infrastructure_details = JSON.stringify({});
      preparedData.specific_data.utility_connections = JSON.stringify({});
    } else if (formData.auction_type === 'heavy_vehicle') {
      preparedData.specific_data.compliance_certificates = JSON.stringify({});
      preparedData.specific_data.maintenance_history = JSON.stringify({});
    }
    
    return preparedData;
  }
  
  // Handle form submission
  async function handleSubmit() {
    try {
      // Validate required fields
      if (!formData.auction.title) {
        error = 'Title is required';
        return;
      }
      
      if (!formData.auction.category) {
        error = 'Category is required';
        return;
      }
      
      if (!formData.auction.starting_price) {
        error = 'Starting price is required';
        return;
      }
      
      // Start submission
      loading.submit = true;
      error = '';
      
      // Process date times
      const now = new Date();
      const twoWeeksLater = new Date(now.getTime() + 14 * 24 * 60 * 60 * 1000);
      
      if (!formData.auction.start_time) {
        formData.auction.start_time = now.toISOString();
      }
      
      if (!formData.auction.end_time) {
        formData.auction.end_time = twoWeeksLater.toISOString();
      }
      
      // Set current price to starting price initially
      formData.auction.current_price = formData.auction.starting_price;
      
      // Ensure minimum_bid_increment has a value
      if (!formData.auction.minimum_bid_increment || formData.auction.minimum_bid_increment <= 0) {
        formData.auction.minimum_bid_increment = Math.max(1, formData.auction.starting_price * 0.01);
      }
      
      // Prepare data
      const preparedData = prepareFormDataForSubmission();
      
      // Submit auction data
      const response = await api.auction.create(preparedData);
      
      // Upload main image if selected
      if (imageFile && response.id) {
        const formDataImg = new FormData();
        formDataImg.append('main_image', imageFile);
        
        await api.auction.uploadImage(response.id, formDataImg);
      }
      
      // Upload additional images if selected
      if (additionalImages.length > 0 && response.id) {
        const formDataImages = new FormData();
        additionalImages.forEach((img, index) => {
          formDataImages.append(`image_${index + 1}`, img);
        });
        
        await api.auction.uploadAdditionalImages(response.id, formDataImages);
      }
      
      // Show success notification
      notificationStore.success('Auction created successfully');
      
      // Redirect to auction page
      goto(`/auctions/${response.id}`);
    } catch (err) {
      console.error('Error creating auction:', err);
      error = err.error || 'Failed to create auction. Please try again.';
      notificationStore.error(error);
    } finally {
      loading.submit = false;
    }
  }
  
  // Format currency
  function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: formData.auction.currency
    }).format(value || 0);
  }
  
  // Initialize on mount
  onMount(async () => {
    loadCategories();
  });
</script>

<svelte:head>
  <title>Create New Auction | GUDIC</title>
  <meta name="description" content="Create a new auction listing on GUDIC." />
</svelte:head>

<div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
  <!-- Header Section -->
  <div class="mb-10">
    <h1 class="text-3xl font-extrabold text-gray-900 tracking-tight">Create New Auction</h1>
    <p class="mt-2 text-gray-600">Fill out the details below to list your item for auction</p>
  </div>
  
  <!-- Error message -->
  {#if error}
    <Alert variant="error" class="mb-6">{error}</Alert>
  {/if}
  
  <!-- Form -->
  <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
    <div class="px-6 py-4 bg-gradient-to-r from-primary-blue/5 to-primary-peach/5 border-b border-gray-200">
      <h2 class="text-lg font-medium text-gray-900">Basic Information</h2>
    </div>
    
    <div class="p-6 space-y-6">
      <!-- Title and Category -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label for="title" class="block text-sm font-medium text-gray-700 mb-1">Title</label>
          <input
            type="text"
            id="title"
            bind:value={formData.auction.title}
            class="block w-full rounded-md border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            placeholder="Enter a descriptive title"
            required
          />
        </div>
        
        <div>
          <label for="category" class="block text-sm font-medium text-gray-700 mb-1">Category</label>
          <select
            id="category"
            bind:value={formData.auction.category}
            class="block w-full rounded-md border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            required
            disabled={loading.categories}
          >
            <option value="">Select a category</option>
            {#each categories as category}
              <option value={category.id}>{category.name}</option>
            {/each}
          </select>
          {#if loading.categories}
            <div class="mt-1 text-xs text-gray-500 flex items-center">
              <Spinner size="xs" class="mr-1" />
              Loading categories...
            </div>
          {/if}
        </div>
      </div>
      
      <!-- Subcategory -->
      {#if subcategories.length > 0}
        <div>
          <label for="subcategory" class="block text-sm font-medium text-gray-700 mb-1">Subcategory (Optional)</label>
          <select
            id="subcategory"
            bind:value={formData.auction.subcategory}
            class="block w-full rounded-md border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            disabled={loading.subcategories}
          >
            <option value="">Select a subcategory</option>
            {#each subcategories as subcategory}
              <option value={subcategory.id}>{subcategory.name}</option>
            {/each}
          </select>
          {#if loading.subcategories}
            <div class="mt-1 text-xs text-gray-500 flex items-center">
              <Spinner size="xs" class="mr-1" />
              Loading subcategories...
            </div>
          {/if}
        </div>
      {/if}
      
      <!-- Description -->
      <div>
        <label for="description" class="block text-sm font-medium text-gray-700 mb-1">Description</label>
        <textarea
          id="description"
          bind:value={formData.auction.description}
          rows="5"
          class="block w-full rounded-md border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          placeholder="Provide a detailed description of your item"
        ></textarea>
      </div>
      
      <!-- Auction Type -->
      <div>
        <label for="auction_type" class="block text-sm font-medium text-gray-700 mb-1">Auction Type</label>
        <select
          id="auction_type"
          bind:value={formData.auction_type}
          on:change={handleAuctionTypeChange}
          class="block w-full rounded-md border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
        >
          <option value="">Select auction type</option>
          {#each auctionTypes as type}
            <option value={type.value}>{type.label}</option>
          {/each}
        </select>
      </div>
      
      <!-- Type-specific fields -->
      {#if formData.auction_type}
        <div class="px-5 py-4 bg-gray-50 rounded-lg">
          <h3 class="text-md font-medium text-gray-900 mb-4">Additional Information for {auctionTypes.find(t => t.value === formData.auction_type).label}</h3>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            {#each getAuctionTypeFields() as field}
              <div>
                <label for={field.name} class="block text-sm font-medium text-gray-700 mb-1">{field.label}</label>
                
                {#if field.type === 'text'}
                  <input
                    type="text"
                    id={field.name}
                    bind:value={formData.specific_data[field.name]}
                    class="block w-full rounded-md border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  />
                {:else if field.type === 'number'}
                  <input
                    type="number"
                    id={field.name}
                    bind:value={formData.specific_data[field.name]}
                    class="block w-full rounded-md border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  />
                {:else if field.type === 'textarea'}
                  <textarea
                    id={field.name}
                    bind:value={formData.specific_data[field.name]}
                    rows="3"
                    class="block w-full rounded-md border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  ></textarea>
                {:else if field.type === 'select'}
                  <select
                    id={field.name}
                    bind:value={formData.specific_data[field.name]}
                    class="block w-full rounded-md border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  >
                    <option value="">Select {field.label}</option>
                    {#each field.options as option}
                      <option value={option.value}>{option.label}</option>
                    {/each}
                  </select>
                {/if}
              </div>
            {/each}
          </div>
        </div>
      {/if}
    </div>
  </div>
  
  <!-- Pricing Section -->
  <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden mt-6">
    <div class="px-6 py-4 bg-gradient-to-r from-primary-blue/5 to-primary-peach/5 border-b border-gray-200">
      <h2 class="text-lg font-medium text-gray-900">Pricing & Duration</h2>
    </div>
    
    <div class="p-6 space-y-6">
      <!-- Pricing fields -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div>
          <label for="starting_price" class="block text-sm font-medium text-gray-700 mb-1">Starting Price</label>
          <div class="mt-1 relative rounded-md shadow-sm">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <span class="text-gray-500 sm:text-sm">$</span>
            </div>
            <input
              type="number"
              id="starting_price"
              bind:value={formData.auction.starting_price}
              min="0"
              step="0.01"
              class="block w-full pl-7 pr-12 rounded-md border-gray-300 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              placeholder="0.00"
              required
            />
            <div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
              <span class="text-gray-500 sm:text-sm">{formData.auction.currency}</span>
            </div>
          </div>
        </div>
        
        <div>
          <label for="reserve_price" class="block text-sm font-medium text-gray-700 mb-1">Reserve Price (Optional)</label>
          <div class="mt-1 relative rounded-md shadow-sm">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <span class="text-gray-500 sm:text-sm">$</span>
            </div>
            <input
              type="number"
              id="reserve_price"
              bind:value={formData.auction.reserve_price}
              min="0"
              step="0.01"
              class="block w-full pl-7 pr-12 rounded-md border-gray-300 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              placeholder="0.00"
            />
            <div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
              <span class="text-gray-500 sm:text-sm">{formData.auction.currency}</span>
            </div>
          </div>
          <p class="mt-1 text-xs text-gray-500">Minimum price you're willing to accept</p>
        </div>
        
        <div>
          <label for="minimum_bid_increment" class="block text-sm font-medium text-gray-700 mb-1">Minimum Bid Increment</label>
          <div class="mt-1 relative rounded-md shadow-sm">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <span class="text-gray-500 sm:text-sm">$</span>
            </div>
            <input
              type="number"
              id="minimum_bid_increment"
              bind:value={formData.auction.minimum_bid_increment}
              min="0.01"
              step="0.01"
              class="block w-full pl-7 pr-12 rounded-md border-gray-300 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              placeholder="0.00"
            />
            <div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
              <span class="text-gray-500 sm:text-sm">{formData.auction.currency}</span>
            </div>
          </div>
          <p class="mt-1 text-xs text-gray-500">Minimum amount that must be added to the current price for a valid bid</p>
        </div>
      </div>
      
      <!-- Currency -->
      <div>
        <label for="currency" class="block text-sm font-medium text-gray-700 mb-1">Currency</label>
        <select
          id="currency"
          bind:value={formData.auction.currency}
          class="block w-full rounded-md border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
        >
        <option value="SAR">SAR - KSA Riyal</option>

          <option value="USD">USD - US Dollar</option>
          <option value="EUR">EUR - Euro</option>
          <option value="GBP">GBP - British Pound</option>
          <option value="CAD">CAD - Canadian Dollar</option>
          
        </select>
      </div>
      
      <!-- Duration fields -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label for="duration" class="block text-sm font-medium text-gray-700 mb-1">Auction Duration</label>
          <select
            id="duration"
            bind:value={formData.timer.duration}
            class="block w-full rounded-md border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          >
            <option value="1D">1 Day</option>
            <option value="3D">3 Days</option>
            <option value="5D">5 Days</option>
            <option value="7D">7 Days</option>
            <option value="14D">14 Days</option>
            <option value="30D">30 Days</option>
            <option value="CUSTOM">Custom Duration</option>
          </select>
        </div>
        
        <div>
          <label for="auto_extend" class="flex items-center">
            <input
              type="checkbox"
              id="auto_extend"
              bind:checked={formData.timer.auto_extend}
              class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <span class="ml-2 text-sm text-gray-700">Auto-extend auction when bids are placed near the end</span>
          </label>
          <p class="mt-1 text-xs text-gray-500">Helps prevent last-second sniping and ensures fair bidding</p>
        </div>
      </div>
      
      <!-- Extension settings (if auto-extend is enabled) -->
      {#if formData.timer.auto_extend}
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label for="extension_threshold" class="block text-sm font-medium text-gray-700 mb-1">
              Extension Threshold (minutes)
            </label>
            <input
              type="number"
              id="extension_threshold"
              bind:value={formData.timer.extension_threshold}
              min="1"
              max="60"
              class="block w-full rounded-md border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            />
            <p class="mt-1 text-xs text-gray-500">
              If a bid is placed with less than this many minutes remaining, the auction will be extended
            </p>
          </div>
          
          <div>
            <label for="extension_duration" class="block text-sm font-medium text-gray-700 mb-1">
              Extension Duration (minutes)
            </label>
            <input
              type="number"
              id="extension_duration"
              bind:value={formData.timer.extension_duration}
              min="1"
              max="60"
              class="block w-full rounded-md border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            />
            <p class="mt-1 text-xs text-gray-500">
              How many minutes to add when an auction is extended
            </p>
          </div>
        </div>
      {/if}
    </div>
  </div>
  
  <!-- Images Section -->
  <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden mt-6">
    <div class="px-6 py-4 bg-gradient-to-r from-primary-blue/5 to-primary-peach/5 border-b border-gray-200">
      <h2 class="text-lg font-medium text-gray-900">Images</h2>
    </div>
    
    <div class="p-6 space-y-6">
      <!-- Main image -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Main Image</label>
        <div class="flex items-center space-x-6">
          <div class="flex-shrink-0 h-32 w-32 bg-gray-100 rounded-lg overflow-hidden border-2 border-gray-200 border-dashed">
            {#if imagePreview}
              <img src={imagePreview} alt="Preview" class="h-full w-full object-cover" />
            {:else}
              <div class="flex flex-col items-center justify-center h-full">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                <p class="mt-1 text-xs text-gray-500">No image selected</p>
              </div>
            {/if}
          </div>
          
          <div>
            <label for="main-image" class="relative cursor-pointer bg-white rounded-md font-medium text-blue-600 hover:text-blue-500 focus-within:outline-none">
              <span>Upload a file</span>
              <input id="main-image" name="main-image" type="file" accept="image/*" class="sr-only" on:change={handleImageChange}>
            </label>
            <p class="text-xs text-gray-500">PNG, JPG, GIF up to 5MB</p>
          </div>
        </div>
      </div>
      
      <!-- Additional images -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Additional Images (up to 5)</label>
        
        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-4 mb-4">
          {#each additionalImagePreviews as preview, i}
            <div class="relative h-32 w-full bg-gray-100 rounded-lg overflow-hidden border border-gray-200">
              <img src={preview} alt={`Additional ${i+1}`} class="h-full w-full object-cover" />
              <button 
                type="button" 
                class="absolute top-1 right-1 bg-red-500 text-white rounded-full p-1 shadow-sm hover:bg-red-600"
                on:click={() => removeAdditionalImage(i)}
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          {/each}
          
          {#if additionalImagePreviews.length < 5}
            <div class="h-32 w-full bg-gray-100 rounded-lg overflow-hidden border-2 border-gray-200 border-dashed flex flex-col items-center justify-center">
              <label for="additional-images" class="cursor-pointer flex flex-col items-center justify-center w-full h-full">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                </svg>
                <p class="mt-1 text-xs text-gray-500">Add more</p>
                <input id="additional-images" name="additional-images" type="file" accept="image/*" multiple class="sr-only" on:change={handleAdditionalImagesChange}>
              </label>
            </div>
          {/if}
        </div>
        <p class="text-xs text-gray-500">Add up to 5 additional images to showcase your item</p>
      </div>
    </div>
  </div>
  
  <!-- Submit section -->
  <div class="mt-8 flex justify-end">
    <div class="flex space-x-4">
      <Button 
        href="/auctions" 
        variant="outline" 
        size="lg"
      >
        Cancel
      </Button>
      
      <Button 
        type="button" 
        variant="primary" 
        size="lg"
        on:click={handleSubmit}
        disabled={loading.submit}
        loading={loading.submit}
      >
        {formData.auction.status === 'DRAFT' ? 'Save as Draft' : 'Create Auction'}
      </Button>
    </div>
  </div>
</div>