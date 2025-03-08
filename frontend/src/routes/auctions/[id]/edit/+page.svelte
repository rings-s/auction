<!-- src/routes/auctions/[id]/edit/+page.svelte -->
<script>
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { goto } from '$app/navigation';
    import { isAuthenticated, primaryRole, user } from '$lib/stores/authStore';
    import { auctionStore } from '$lib/stores/auctionStore';
    import { notificationStore } from '$lib/stores/notificationStore';
    import Button from '$lib/components/ui/Button.svelte';
    import Spinner from '$lib/components/ui/Spinner.svelte';
    import Alert from '$lib/components/ui/Alert.svelte';
    import Tabs from '$lib/components/ui/Tabs.svelte';
    import ImageUploader from '$lib/components/ui/ImageUploader.svelte';
    import { formatDate, formatCurrency } from '$lib/utils/formatters';
    
    // Get auction ID from URL
    $: auctionId = $page.params.id;
    
    // Reactive state
    $: auction = $auctionStore.currentAuction;
    $: loading = $auctionStore.loading.details;
    $: error = $auctionStore.error;
    $: currentUser = $user;
    $: showErrors = false;
    
    // Form state
    let formData = {
      basic: {
        title: '',
        description: '',
        category: '',
        subcategory: '',
        starting_price: 0,
        reserve_price: 0,
        minimum_bid_increment: 0,
        currency: 'USD'
      },
      scheduling: {
        start_time: '',
        end_time: '',
        auto_extend: true,
        extension_threshold: 300, // 5 minutes in seconds
        extension_duration: 300  // 5 minutes in seconds
      },
      images: {
        main_image: null,
        image_1: null,
        image_2: null,
        image_3: null,
        image_4: null,
        image_5: null
      },
      specific: {}
    };
    
    // Auction type and options
    let auctionType = '';
    let categories = [];
    let subcategories = [];
    let saving = false;
    let successMessage = '';
    
    // Available auction types
    const auctionTypes = [
      { id: 'real_estate', label: 'Real Estate' },
      { id: 'vehicle', label: 'Vehicle' },
      { id: 'machinery', label: 'Machinery' },
      { id: 'factory', label: 'Factory' },
      { id: 'heavy_vehicle', label: 'Heavy Vehicle' }
    ];
    
    // Form validation state
    let validationErrors = {
      basic: {},
      scheduling: {},
      images: {},
      specific: {}
    };
    
    // Tabs
    const tabs = [
      { id: 'basic', label: 'Basic Information' },
      { id: 'scheduling', label: 'Scheduling' },
      { id: 'images', label: 'Images' },
      { id: 'specific', label: 'Specific Details' }
    ];
    let activeTab = 'basic';
    
    // Helper function to fetch all categories
    async function fetchCategories() {
      try {
        const response = await fetch('/api/base/categories');
        const data = await response.json();
        categories = data.results || [];
      } catch (err) {
        console.error('Error fetching categories:', err);
        notificationStore.error('Failed to load categories.');
      }
    }
    
    // Helper function to fetch subcategories for a specific category
    async function fetchSubcategories(categoryId) {
      if (!categoryId) {
        subcategories = [];
        return;
      }
      
      try {
        const response = await fetch(`/api/base/subcategories?category_id=${categoryId}`);
        const data = await response.json();
        subcategories = data.results || [];
      } catch (err) {
        console.error('Error fetching subcategories:', err);
        notificationStore.error('Failed to load subcategories.');
      }
    }
    
    // Helper function to format date for input fields
    function formatDateForInput(dateString) {
      if (!dateString) return '';
      
      const date = new Date(dateString);
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      const hours = String(date.getHours()).padStart(2, '0');
      const minutes = String(date.getMinutes()).padStart(2, '0');
      
      return `${year}-${month}-${day}T${hours}:${minutes}`;
    }
    
    // Initialize form with existing auction data
    function initializeForm() {
      if (!auction) return;
      
      // Basic information
      formData.basic = {
        title: auction.title || '',
        description: auction.description || '',
        category: auction.category || '',
        subcategory: auction.subcategory || '',
        starting_price: auction.starting_price || auction.current_price || 0,
        reserve_price: auction.reserve_price || 0,
        minimum_bid_increment: auction.minimum_bid_increment || 0,
        currency: auction.currency || 'USD'
      };
      
      // Scheduling
      formData.scheduling = {
        start_time: formatDateForInput(auction.start_time),
        end_time: formatDateForInput(auction.end_time),
        auto_extend: auction.timer_details?.auto_extend ?? true,
        extension_threshold: auction.timer_details?.extension_threshold || 300,
        extension_duration: auction.timer_details?.extension_duration || 300
      };
      
      // Images
      formData.images = {
        main_image: auction.main_image || null,
        image_1: auction.image_1 || null,
        image_2: auction.image_2 || null,
        image_3: auction.image_3 || null,
        image_4: auction.image_4 || null,
        image_5: auction.image_5 || null
      };
      
      // Determine auction type from specific_data
      if (auction.specific_data) {
        auctionType = auction.specific_data.auction_type || '';
        
        // Initialize specific data based on auction type
        if (auctionType) {
          formData.specific = { ...auction.specific_data.data };
        }
      }
    }
    
    // Handle category change
    function handleCategoryChange(event) {
      const categoryId = event.target.value;
      formData.basic.category = categoryId;
      formData.basic.subcategory = '';
      fetchSubcategories(categoryId);
    }
    
    // Handle auction type change
    function handleAuctionTypeChange(event) {
      auctionType = event.target.value;
      formData.specific = {}; // Reset specific details when changing type
    }
    
    // Validate form data
    function validateForm() {
      // Reset validation errors
      validationErrors = {
        basic: {},
        scheduling: {},
        images: {},
        specific: {}
      };
      
      let isValid = true;
      
      // Validate basic information
      if (!formData.basic.title) {
        validationErrors.basic.title = 'Title is required';
        isValid = false;
      }
      
      if (!formData.basic.description) {
        validationErrors.basic.description = 'Description is required';
        isValid = false;
      }
      
      if (!formData.basic.category) {
        validationErrors.basic.category = 'Category is required';
        isValid = false;
      }
      
      if (formData.basic.starting_price <= 0) {
        validationErrors.basic.starting_price = 'Starting price must be greater than zero';
        isValid = false;
      }
      
      if (formData.basic.reserve_price < 0) {
        validationErrors.basic.reserve_price = 'Reserve price cannot be negative';
        isValid = false;
      }
      
      if (formData.basic.minimum_bid_increment <= 0) {
        validationErrors.basic.minimum_bid_increment = 'Minimum bid increment must be greater than zero';
        isValid = false;
      }
      
      // Validate scheduling
      if (!formData.scheduling.start_time) {
        validationErrors.scheduling.start_time = 'Start time is required';
        isValid = false;
      }
      
      if (!formData.scheduling.end_time) {
        validationErrors.scheduling.end_time = 'End time is required';
        isValid = false;
      }
      
      if (formData.scheduling.start_time && formData.scheduling.end_time) {
        const start = new Date(formData.scheduling.start_time);
        const end = new Date(formData.scheduling.end_time);
        
        if (end <= start) {
          validationErrors.scheduling.end_time = 'End time must be after start time';
          isValid = false;
        }
      }
      
      // Image validation is optional
      
      // Validate specific details based on auction type
      if (auctionType) {
        // Add specific validations based on auction type
        switch (auctionType) {
          case 'real_estate':
            if (!formData.specific.property_type) {
              validationErrors.specific.property_type = 'Property type is required';
              isValid = false;
            }
            
            if (!formData.specific.location) {
              validationErrors.specific.location = 'Location is required';
              isValid = false;
            }
            break;
            
          case 'vehicle':
            if (!formData.specific.make) {
              validationErrors.specific.make = 'Make is required';
              isValid = false;
            }
            
            if (!formData.specific.model) {
              validationErrors.specific.model = 'Model is required';
              isValid = false;
            }
            
            if (!formData.specific.year) {
              validationErrors.specific.year = 'Year is required';
              isValid = false;
            }
            break;
            
          // Add other auction type validations as needed
        }
      }
      
      return isValid;
    }
    
    // Handle form submission
    async function handleSubmit() {
      showErrors = true;
      
      if (!validateForm()) {
        notificationStore.error('Please correct the errors in the form.');
        return;
      }
      
      try {
        saving = true;
        
        // Prepare data for API
        const auctionData = {
          auction: {
            title: formData.basic.title,
            description: formData.basic.description,
            category: formData.basic.category,
            subcategory: formData.basic.subcategory || null,
            starting_price: formData.basic.starting_price,
            reserve_price: formData.basic.reserve_price,
            minimum_bid_increment: formData.basic.minimum_bid_increment,
            currency: formData.basic.currency,
            start_time: formData.scheduling.start_time,
            end_time: formData.scheduling.end_time,
            ...formData.images
          },
          timer: {
            auto_extend: formData.scheduling.auto_extend,
            extension_threshold: formData.scheduling.extension_threshold,
            extension_duration: formData.scheduling.extension_duration
          }
        };
        
        // Add auction type and specific data if available
        if (auctionType) {
          auctionData.auction_type = auctionType;
          auctionData.specific_data = formData.specific;
        }
        
        // Update auction
        const response = await fetch(`/api/base/auctions/${auctionId}/update/`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(auctionData)
        });
        
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || 'Failed to update auction');
        }
        
        // Success
        notificationStore.success('Auction updated successfully!');
        successMessage = 'Auction updated successfully!';
        
        // Redirect to auction details page
        setTimeout(() => {
          goto(`/auctions/${auctionId}`);
        }, 1500);
      } catch (err) {
        console.error('Error updating auction:', err);
        notificationStore.error(err.message || 'Failed to update auction');
        error = err.message || 'Failed to update auction';
      } finally {
        saving = false;
      }
    }
    
    // Load auction data
    onMount(async () => {
      if (auctionId) {
        try {
          // Load auction details
          await auctionStore.loadAuctionDetails(auctionId);
          
          // Check if user has permission to edit
          if (auction && auction.seller !== $user?.id && $primaryRole?.code !== 'admin') {
            notificationStore.error('You do not have permission to edit this auction');
            goto(`/auctions/${auctionId}`);
            return;
          }
          
          // Initialize form with auction data
          initializeForm();
          
          // Load categories and subcategories
          await fetchCategories();
          if (formData.basic.category) {
            await fetchSubcategories(formData.basic.category);
          }
        } catch (err) {
          console.error('Error loading auction details:', err);
          notificationStore.error('Failed to load auction details');
        }
      }
    });
  </script>
  
  <svelte:head>
    <title>Edit {auction ? auction.title : 'Auction'} | GUDIC</title>
    <meta name="description" content="Edit auction details" />
  </svelte:head>
  
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Loading state -->
    {#if loading}
      <div class="flex justify-center items-center py-12">
        <Spinner size="lg" />
      </div>
    <!-- Error state -->
    {:else if error}
      <div class="bg-red-50 p-4 rounded-md text-red-600 mb-8">
        <p class="text-center">{error}</p>
        <div class="flex justify-center mt-4">
          <Button 
            variant="primary" 
            size="sm"
            on:click={() => {
              auctionStore.clearError();
              auctionStore.loadAuctionDetails(auctionId);
            }}
          >
            Try Again
          </Button>
        </div>
      </div>
    <!-- Content state -->
    {:else if auction}
      <!-- Header -->
      <div class="mb-6">
        <div class="flex justify-between items-center">
          <h1 class="text-3xl font-bold text-text-dark">Edit Auction</h1>
          
          <Button 
            href={`/auctions/${auctionId}`} 
            variant="outline"
            size="sm"
          >
            Cancel
          </Button>
        </div>
        <p class="text-text-medium mt-2">Update the details of your auction.</p>
        
        {#if successMessage}
          <div class="mt-4 bg-green-50 p-4 rounded-md text-green-600">
            <p class="text-center">{successMessage}</p>
          </div>
        {/if}
      </div>
      
      <!-- Main content area -->
      <div class="bg-white rounded-lg border border-primary-blue/20 overflow-hidden">
        <Tabs {tabs} bind:activeTab>
          
          <!-- Basic Information Tab -->
          {#if activeTab === 'basic'}
            <div class="p-6">
              <h2 class="text-xl font-semibold text-text-dark mb-4">Basic Information</h2>
              
              <div class="space-y-6">
                <!-- Title -->
                <div>
                  <label for="title" class="block text-sm font-medium text-text-dark mb-1">
                    Title <span class="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    id="title"
                    bind:value={formData.basic.title}
                    class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-blue focus:border-primary-blue"
                    class:border-red-500={showErrors && validationErrors.basic.title}
                  />
                  {#if showErrors && validationErrors.basic.title}
                    <p class="mt-1 text-sm text-red-500">{validationErrors.basic.title}</p>
                  {/if}
                </div>
                
                <!-- Description -->
                <div>
                  <label for="description" class="block text-sm font-medium text-text-dark mb-1">
                    Description <span class="text-red-500">*</span>
                  </label>
                  <textarea
                    id="description"
                    bind:value={formData.basic.description}
                    rows="5"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-blue focus:border-primary-blue"
                    class:border-red-500={showErrors && validationErrors.basic.description}
                  ></textarea>
                  {#if showErrors && validationErrors.basic.description}
                    <p class="mt-1 text-sm text-red-500">{validationErrors.basic.description}</p>
                  {/if}
                </div>
                
                <!-- Category and Subcategory -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label for="category" class="block text-sm font-medium text-text-dark mb-1">
                      Category <span class="text-red-500">*</span>
                    </label>
                    <select
                      id="category"
                      on:change={handleCategoryChange}
                      value={formData.basic.category}
                      class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-blue focus:border-primary-blue"
                      class:border-red-500={showErrors && validationErrors.basic.category}
                    >
                      <option value="">Select Category</option>
                      {#each categories as category}
                        <option value={category.id}>{category.name}</option>
                      {/each}
                    </select>
                    {#if showErrors && validationErrors.basic.category}
                      <p class="mt-1 text-sm text-red-500">{validationErrors.basic.category}</p>
                    {/if}
                  </div>
                  
                  <div>
                    <label for="subcategory" class="block text-sm font-medium text-text-dark mb-1">
                      Subcategory
                    </label>
                    <select
                      id="subcategory"
                      bind:value={formData.basic.subcategory}
                      class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-blue focus:border-primary-blue"
                      disabled={!formData.basic.category || subcategories.length === 0}
                    >
                      <option value="">Select Subcategory</option>
                      {#each subcategories as subcategory}
                        <option value={subcategory.id}>{subcategory.name}</option>
                      {/each}
                    </select>
                  </div>
                </div>
                
                <!-- Auction Type -->
                <div>
                  <label for="auction-type" class="block text-sm font-medium text-text-dark mb-1">
                    Auction Type <span class="text-red-500">*</span>
                  </label>
                  <select
                    id="auction-type"
                    on:change={handleAuctionTypeChange}
                    value={auctionType}
                    class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-blue focus:border-primary-blue"
                  >
                    <option value="">Select Auction Type</option>
                    {#each auctionTypes as type}
                      <option value={type.id}>{type.label}</option>
                    {/each}
                  </select>
                </div>
                
                <!-- Pricing -->
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div>
                    <label for="starting-price" class="block text-sm font-medium text-text-dark mb-1">
                      Starting Price <span class="text-red-500">*</span>
                    </label>
                    <div class="relative">
                      <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <span class="text-gray-500 sm:text-sm">$</span>
                      </div>
                      <input
                        type="number"
                        id="starting-price"
                        bind:value={formData.basic.starting_price}
                        min="0"
                        step="0.01"
                        class="w-full pl-7 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-blue focus:border-primary-blue"
                        class:border-red-500={showErrors && validationErrors.basic.starting_price}
                      />
                    </div>
                    {#if showErrors && validationErrors.basic.starting_price}
                      <p class="mt-1 text-sm text-red-500">{validationErrors.basic.starting_price}</p>
                    {/if}
                  </div>
                  
                  <div>
                    <label for="reserve-price" class="block text-sm font-medium text-text-dark mb-1">
                      Reserve Price
                    </label>
                    <div class="relative">
                      <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <span class="text-gray-500 sm:text-sm">$</span>
                      </div>
                      <input
                        type="number"
                        id="reserve-price"
                        bind:value={formData.basic.reserve_price}
                        min="0"
                        step="0.01"
                        class="w-full pl-7 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-blue focus:border-primary-blue"
                        class:border-red-500={showErrors && validationErrors.basic.reserve_price}
                      />
                    </div>
                    {#if showErrors && validationErrors.basic.reserve_price}
                      <p class="mt-1 text-sm text-red-500">{validationErrors.basic.reserve_price}</p>
                    {/if}
                  </div>
                  
                  <div>
                    <label for="minimum-bid-increment" class="block text-sm font-medium text-text-dark mb-1">
                      Minimum Bid Increment <span class="text-red-500">*</span>
                    </label>
                    <div class="relative">
                      <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <span class="text-gray-500 sm:text-sm">$</span>
                      </div>
                      <input
                        type="number"
                        id="minimum-bid-increment"
                        bind:value={formData.basic.minimum_bid_increment}
                        min="0.01"
                        step="0.01"
                        class="w-full pl-7 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-blue focus:border-primary-blue"
                        class:border-red-500={showErrors && validationErrors.basic.minimum_bid_increment}
                      />
                    </div>
                    {#if showErrors && validationErrors.basic.minimum_bid_increment}
                      <p class="mt-1 text-sm text-red-500">{validationErrors.basic.minimum_bid_increment}</p>
                    {/if}
                  </div>
                </div>
                
                <!-- Currency -->
                <div>
                  <label for="currency" class="block text-sm font-medium text-text-dark mb-1">
                    Currency
                  </label>
                  <select
                    id="currency"
                    bind:value={formData.basic.currency}
                    class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-blue focus:border-primary-blue"
                  >
                    <option value="USD">USD - US Dollar</option>
                    <option value="EUR">EUR - Euro</option>
                    <option value="GBP">GBP - British Pound</option>
                    <option value="CAD">CAD - Canadian Dollar</option>
                    <option value="AUD">AUD - Australian Dollar</option>
                    <option value="JPY">JPY - Japanese Yen</option>
                  </select>
                </div>
              </div>
            </div>
          
          <!-- Scheduling Tab -->
          {:else if activeTab === 'scheduling'}
            <div class="p-6">
              <h2 class="text-xl font-semibold text-text-dark mb-4">Scheduling</h2>
              
              <div class="space-y-6">
                <!-- Start Time -->
                <div>
                  <label for="start-time" class="block text-sm font-medium text-text-dark mb-1">
                    Start Time <span class="text-red-500">*</span>
                  </label>
                  <input
                    type="datetime-local"
                    id="start-time"
                    bind:value={formData.scheduling.start_time}
                    class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-blue focus:border-primary-blue"
                    class:border-red-500={showErrors && validationErrors.scheduling.start_time}
                  />
                  {#if showErrors && validationErrors.scheduling.start_time}
                    <p class="mt-1 text-sm text-red-500">{validationErrors.scheduling.start_time}</p>
                  {/if}
                </div>
                
                <!-- End Time -->
                <div>
                  <label for="end-time" class="block text-sm font-medium text-text-dark mb-1">
                    End Time <span class="text-red-500">*</span>
                  </label>
                  <input
                    type="datetime-local"
                    id="end-time"
                    bind:value={formData.scheduling.end_time}
                    class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-blue focus:border-primary-blue"
                    class:border-red-500={showErrors && validationErrors.scheduling.end_time}
                  />
                  {#if showErrors && validationErrors.scheduling.end_time}
                    <p class="mt-1 text-sm text-red-500">{validationErrors.scheduling.end_time}</p>
                  {/if}
                </div>
                
                <!-- Auto-extend Settings -->
                <div class="bg-primary-blue/5 p-4 rounded-lg">
                  <div class="flex items-center mb-4">
                    <input
                      id="auto-extend"
                      type="checkbox"
                      bind:checked={formData.scheduling.auto_extend}
                      class="h-4 w-4 text-primary-blue focus:ring-primary-blue border-gray-300 rounded"
                    />
                    <label for="auto-extend" class="ml-2 block text-sm font-medium text-text-dark">
                      Auto-extend auction when bids are placed near the end time
                    </label>
                  </div>
                  
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-4" class:opacity-50={!formData.scheduling.auto_extend}>
                    <div>
                      <label for="extension-threshold" class="block text-sm font-medium text-text-dark mb-1">
                        Extension Threshold (seconds)
                      </label>
                      <input
                        type="number"
                        id="extension-threshold"
                        bind:value={formData.scheduling.extension_threshold}
                        min="30"
                        step="30"
                        disabled={!formData.scheduling.auto_extend}
                        class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-blue focus:border-primary-blue"
                      />
                      <p class="mt-1 text-xs text-text-medium">
                        Auction will extend if a bid is placed within this many seconds of the end time.
                      </p>
                    </div>
                    
                    <div>
                      <label for="extension-duration" class="block text-sm font-medium text-text-dark mb-1">
                        Extension Duration (seconds)
                      </label>
                      <input
                        type="number"
                        id="extension-duration"
                        bind:value={formData.scheduling.extension_duration}
                        min="60"
                        step="60"
                        disabled={!formData.scheduling.auto_extend}
                        class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-blue focus:border-primary-blue"
                      />
                      <p class="mt-1 text-xs text-text-medium">
                        The auction end time will be extended by this many seconds.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          
          <!-- Images Tab -->
          {:else if activeTab === 'images'}
            <div class="p-6">
              <h2 class="text-xl font-semibold text-text-dark mb-4">Images</h2>
              
              <div class="space-y-6">
                <!-- Main Image -->
                <div>
                  <label class="block text-sm font-medium text-text-dark mb-1">
                    Main Image
                  </label>
                  <ImageUploader
                    currentImage={formData.images.main_image}
                    onImageSelected={(file) => formData.images.main_image = file}
                    onImageRemoved={() => formData.images.main_image = null}
                  />
                </div>
                
                <!-- Additional Images -->
                <div>
                  <label class="block text-sm font-medium text-text-dark mb-1">
                    Additional Images
                  </label>
                  
                  <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
                    <!-- Image 1 -->
                    <div>
                      <ImageUploader
                        currentImage={formData.images.image_1}
                        onImageSelected={(file) => formData.images.image_1 = file}
                        onImageRemoved={() => formData.images.image_1 = null}
                      />
                    </div>
                    
                    <!-- Image 2 -->
                    <div>
                      <ImageUploader
                        currentImage={formData.images.image_2}
                        onImageSelected={(file) => formData.images.image_2 = file}
                        onImageRemoved={() => formData.images.image_2 = null}
                      />
                    </div>
                    
                    <!-- Image 3 -->
                    <div>
                      <ImageUploader
                        currentImage={formData.images.image_3}
                        onImageSelected={(file) => formData.images.image_3 = file}
                        onImageRemoved={() => formData.images.image_3 = null}
                      />
                    </div>
                    
                    <!-- Image 4 -->
                    <div>
                      <ImageUploader
                        currentImage={formData.images.image_4}
                        onImageSelected={(file) => formData.images.image_4 = file}
                        onImageRemoved={() => formData.images.image_4 = null}
                      />
                    </div>
                    
                    <!-- Image 5 -->
                    <div>
                      <ImageUploader
                        currentImage={formData.images.image_5}
                        onImageSelected={(file) => formData.images.image_5 = file}
                        onImageRemoved={() => formData.images.image_5 = null}
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          
          <!-- Specific Details Tab -->
          {:else if activeTab === 'specific'}
            <div class="p-6">
              <h2 class="text-xl font-semibold text-text-dark mb-4">Specific Details</h2>
              
              {#if !auctionType}
                <div class="text-center py-8">
                  <p class="text-text-medium mb-4">Please select an auction type to add specific details.</p>
                  <Button 
                    variant="outline" 
                    size="sm"
                    on:click={() => activeTab = 'basic'}
                  >
                    Go to Basic Information
                  </Button>
                </div>
              {:else if auctionType === 'real_estate'}
                <!-- Real Estate Fields -->
                <div class="space-y-6">
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <!-- Property Type -->
                    <div>
                      <label for="property-type" class="block text-sm font-medium text-text-dark mb-1">
                        Property Type <span class="text-red-500">*</span>
                      </label>
                      <select
                        id="property-type"
                        bind:value={formData.specific.property_type}
                        class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-blue focus:border-primary-blue"
                        class:border-red-500={showErrors && validationErrors.specific.property_type}
                      >
                        <option value="">Select Property Type</option>
                        <option value="RESIDENTIAL">Residential</option>
                        <option value="COMMERCIAL">Commercial</option>
                        <option value="INDUSTRIAL">Industrial</option>
                        <option value="LAND">Land/Lot</option>
                        <option value="FARM">Farm/Ranch</option>
                        <option value="OTHER">Other</option>
                      </select>
                      {#if showErrors && validationErrors.specific.property_type}
                        <p class="mt-1 text-sm text-red-500">{validationErrors.specific.property_type}</p>
                      {/if}
                    </div>
                    
                    <!-- Size -->
                    <div>
                      <label for="size-sqm" class="block text-sm font-medium text-text-dark mb-1">
                        Size (sqm)
                      </label>
                      <input
                        type="number"
                        id="size-sqm"
                        bind:value={formData.specific.size_sqm}
                        min="0"
                        class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-blue focus:border-primary-blue"
                      />
                    </div>
                  </div>
                  
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <!-- Location -->
                    <div>
                      <label for="location" class="block text-sm font-medium text-text-dark mb-1">
                        Location <span class="text-red-500">*</span>
                      </label>
                      <input
                        type="text"
                        id="location"
                        bind:value={formData.specific.location}
                        class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-blue focus:border-primary-blue"
                        class:border-red-500={showErrors && validationErrors.specific.location}
                      />
                      {#if showErrors && validationErrors.specific.location}
                        <p class="mt-1 text-sm text-red-500">{validationErrors.specific.location}</p>
                      {/if}
                    </div>
                    
                    <!-- Address -->
                    <div>
                      <label for="address" class="block text-sm font-medium text-text-dark mb-1">
                        Address
                      </label>
                      <input
                        type="text"
                        id="address"
                        bind:value={formData.specific.address}
                        class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-blue focus:border-primary-blue"
                      />
                    </div>
                  </div>
                  
                  <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <!-- Bedrooms -->
                    <div>
                      <label for="bedrooms" class="block text-sm font-medium text-text-dark mb-1">
                        Bedrooms
                      </label>
                      <input
                        type="number"
                        id="bedrooms"
                        bind:value={formData.specific.bedrooms}
                        min="0"
                        class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-blue focus:border-primary-blue"
                      />
                    </div>
                    
                    <!-- Bathrooms -->
                    <div>
                      <label for="bathrooms" class="block text-sm font-medium text-text-dark mb-1">
                        Bathrooms
                      </label>
                      <input
                        type="number"
                        id="bathrooms"
                        bind:value={formData.specific.bathrooms}
                        min="0"
                        step="0.5"
                        class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-blue focus:border-primary-blue"
                      />
                    </div>
                    
                    <!-- Year Built -->
                    <div>
                      <label for="year-built" class="block text-sm font-medium text-text-dark mb-1">
                        Year Built
                      </label>
                      <input
                        type="number"
                        id="year-built"
                        bind:value={formData.specific.year_built}
                        min="1800"
                        max={new Date().getFullYear()}
                        class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-blue focus:border-primary-blue"
                      />
                    </div>
                  </div>
                  
                  <!-- Property Condition -->
                  <div>
                    <label for="property-condition" class="block text-sm font-medium text-text-dark mb-1">
                      Property Condition
                    </label>
                    <select
                      id="property-condition"
                      bind:value={formData.specific.property_condition}
                      class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-blue focus:border-primary-blue"
                    >
                      <option value="">Select Condition</option>
                      <option value="NEW">New</option>
                      <option value="EXCELLENT">Excellent</option>
                      <option value="GOOD">Good</option>
                      <option value="FAIR">Fair</option>
                      <option value="POOR">Poor</option>
                      <option value="FIXER_UPPER">Fixer Upper</option>
                    </select>
                  </div>
                  
                  <!-- Zoning Info -->
                  <div>
                    <label for="zoning-info" class="block text-sm font-medium text-text-dark mb-1">
                      Zoning Information
                    </label>
                    <textarea
                      id="zoning-info"
                      bind:value={formData.specific.zoning_info}
                      rows="3"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-blue focus:border-primary-blue"
                    ></textarea>
                  </div>
                </div>
              {:else if auctionType === 'vehicle'}
                <!-- Vehicle Fields -->
                <div class="space-y-6">
                  <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <!-- Make -->
                    <div>
                      <label for="make" class="block text-sm font-medium text-text-dark mb-1">
                        Make <span class="text-red-500">*</span>
                      </label>
                      <input
                        type="text"
                        id="make"
                        bind:value={formData.specific.make}
                        class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-blue focus:border-primary-blue"
                        class:border-red-500={showErrors && validationErrors.specific.make}
                      />
                      {#if showErrors && validationErrors.specific.make}
                        <p class="mt-1 text-sm text-red-500">{validationErrors.specific.make}</p>
                      {/if}
                    </div>
                    
                    <!-- Model -->
                    <div>
                      <label for="model" class="block text-sm font-medium text-text-dark mb-1">
                        Model <span class="text-red-500">*</span>
                      </label>
                      <input
                        type="text"
                        id="model"
                        bind:value={formData.specific.model}
                        class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-blue focus:border-primary-blue"
                        class:border-red-500={showErrors && validationErrors.specific.model}
                      />
                      {#if showErrors && validationErrors.specific.model}
                        <p class="mt-1 text-sm text-red-500">{validationErrors.specific.model}</p>
                      {/if}
                    </div>
                    
                    <!-- Year -->
                    <div>
                      <label for="year" class="block text-sm font-medium text-text-dark mb-1">
                        Year <span class="text-red-500">*</span>
                      </label>
                      <input
                        type="number"
                        id="year"
                        bind:value={formData.specific.year}
                        min="1900"
                        max={new Date().getFullYear() + 1}
                        class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-blue focus:border-primary-blue"
                        class:border-red-500={showErrors && validationErrors.specific.year}
                      />
                      {#if showErrors && validationErrors.specific.year}
                        <p class="mt-1 text-sm text-red-500">{validationErrors.specific.year}</p>
                      {/if}
                    </div>
                  </div>
                  
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <!-- Mileage -->
                    <div>
                      <label for="mileage" class="block text-sm font-medium text-text-dark mb-1">
                        Mileage
                      </label>
                      <input
                        type="number"
                        id="mileage"
                        bind:value={formData.specific.mileage}
                        min="0"
                        class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-blue focus:border-primary-blue"
                      />
                    </div>
                    
                    <!-- VIN -->
                    <div>
                      <label for="vin" class="block text-sm font-medium text-text-dark mb-1">
                        VIN
                      </label>
                      <input
                        type="text"
                        id="vin"
                        bind:value={formData.specific.vin}
                        class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-blue focus:border-primary-blue"
                      />
                    </div>
                  </div>
                  
                  <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <!-- Engine Type -->
                    <div>
                      <label for="engine-type" class="block text-sm font-medium text-text-dark mb-1">
                        Engine Type
                      </label>
                      <input
                        type="text"
                        id="engine-type"
                        bind:value={formData.specific.engine_type}
                        class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-blue focus:border-primary-blue"
                      />
                    </div>
                    
                    <!-- Transmission -->
                    <div>
                      <label for="transmission" class="block text-sm font-medium text-text-dark mb-1">
                        Transmission
                      </label>
                      <select
                        id="transmission"
                        bind:value={formData.specific.transmission}
                        class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-blue focus:border-primary-blue"
                      >
                        <option value="">Select Transmission</option>
                        <option value="AUTOMATIC">Automatic</option>
                        <option value="MANUAL">Manual</option>
                        <option value="SEMI_AUTO">Semi-Automatic</option>
                        <option value="CVT">CVT</option>
                        <option value="OTHER">Other</option>
                      </select>
                    </div>
                    
                    <!-- Fuel Type -->
                    <div>
                      <label for="fuel-type" class="block text-sm font-medium text-text-dark mb-1">
                        Fuel Type
                      </label>
                      <select
                        id="fuel-type"
                        bind:value={formData.specific.fuel_type}
                        class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-blue focus:border-primary-blue"
                      >
                        <option value="">Select Fuel Type</option>
                        <option value="GASOLINE">Gasoline</option>
                        <option value="DIESEL">Diesel</option>
                        <option value="ELECTRIC">Electric</option>
                        <option value="HYBRID">Hybrid</option>
                        <option value="PLUGIN_HYBRID">Plug-in Hybrid</option>
                        <option value="OTHER">Other</option>
                      </select>
                    </div>
                  </div>
                  
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <!-- Color -->
                    <div>
                      <label for="color" class="block text-sm font-medium text-text-dark mb-1">
                        Color
                      </label>
                      <input
                        type="text"
                        id="color"
                        bind:value={formData.specific.color}
                        class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-blue focus:border-primary-blue"
                      />
                    </div>
                    
                    <!-- Condition -->
                    <div>
                      <label for="condition" class="block text-sm font-medium text-text-dark mb-1">
                        Condition
                      </label>
                      <select
                        id="condition"
                        bind:value={formData.specific.condition}
                        class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-blue focus:border-primary-blue"
                      >
                        <option value="">Select Condition</option>
                        <option value="NEW">New</option>
                        <option value="LIKE_NEW">Like New</option>
                        <option value="EXCELLENT">Excellent</option>
                        <option value="GOOD">Good</option>
                        <option value="FAIR">Fair</option>
                        <option value="POOR">Poor</option>
                        <option value="SALVAGE">Salvage</option>
                      </select>
                    </div>
                  </div>
                  
                  <!-- Service History -->
                  <div>
                    <label for="service-history" class="block text-sm font-medium text-text-dark mb-1">
                      Service History
                    </label>
                    <textarea
                      id="service-history"
                      bind:value={formData.specific.service_history}
                      rows="3"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-blue focus:border-primary-blue"
                    ></textarea>
                  </div>
                </div>
              {:else}
                <!-- Other auction types would be implemented similarly -->
                <div class="text-center py-8">
                  <p class="text-text-medium">Specific fields for {auctionType} auctions will be shown here.</p>
                </div>
              {/if}
            </div>
          {/if}
        </Tabs>
      </div>
      
      <!-- Form Actions -->
      <div class="mt-6 flex justify-end">
        <div class="flex space-x-4">
          <Button 
            href={`/auctions/${auctionId}`} 
            variant="outline"
            size="md"
          >
            Cancel
          </Button>
          
          <Button 
            variant="primary" 
            size="md"
            on:click={handleSubmit}
            disabled={saving}
            loading={saving}
          >
            Update Auction
          </Button>
        </div>
      </div>
    {:else}
      <!-- Empty state -->
      <div class="text-center py-12">
        <p class="text-text-medium">Auction not found or has been removed.</p>
        <Button 
          href="/auctions" 
          variant="primary" 
          size="md"
          class="mt-4"
        >
          Browse Auctions
        </Button>
      </div>
    {/if}
  </div>