<!-- src/lib/components/auction/AuctionForm.svelte -->
<script>
  import { onMount } from 'svelte';
  import { t } from '$lib/i18n';
  import { getProperties } from '$lib/api/property';
  import { uploadMultipleMedia, deleteMedia, updateMedia } from '$lib/api/media';
  import { user } from '$lib/stores/user';
  import Tabs from '$lib/components/ui/Tabs.svelte';
  import FormField from '$lib/components/ui/FormField.svelte';
  import Switch from '$lib/components/ui/Switch.svelte';
  import PropertySelector from '$lib/components/properties/PropertySelector.svelte';
  import MediaUploader from '$lib/components/shared/MediaUploader.svelte';
  import Alert from '$lib/components/ui/Alert.svelte';
  
  // Take initial auction data as a prop
  export let initialAuction = null;
  export let isEditing = false;
  
  // The auction object that will be bound to form controls
  let auction = {
    title: '',
    slug: '',
    auction_type: 'reserve',
    status: 'draft',
    description: '',
    start_date: '',
    end_date: '',
    registration_deadline: '',
    related_property: null,
    related_property_id: null,
    starting_bid: '',
    minimum_increment: 100,
    auto_extend_minutes: 0,
    minimum_participants: 1,
    require_bid_verification: false,
    is_published: false,
    is_featured: false,
    terms_conditions: '',
    media: []
  };
  
  let activeTab = 'basic';
  let uploadingMedia = false;
  let mediaError = '';
  let currentStep = 1;
  const totalSteps = 6;
  
  // Form validation state
  let touched = {
    title: false,
    related_property_id: false,
    start_date: false,
    end_date: false,
    starting_bid: false
  };
  
  // Safe translation helper
  function safeTranslate(key, fallback = '', params = {}) {
    try {
      return $t ? $t(key, params) : fallback;
    } catch (e) {
      console.warn(`Translation error for key: ${key}`, e);
      return fallback;
    }
  }
  
  // Update current step when tab changes
  $: {
    if (activeTab === 'basic') currentStep = 1;
    else if (activeTab === 'scheduling') currentStep = 2;
    else if (activeTab === 'financial') currentStep = 3;
    else if (activeTab === 'property') currentStep = 4;
    else if (activeTab === 'media') currentStep = 5;
    else if (activeTab === 'terms') currentStep = 6;
  }
  
  // Define the tab icons
  const basicIcon = '<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>';
  const schedulingIcon = '<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>';
  const financialIcon = '<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>';
  const propertyIcon = '<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" /></svg>';
  const mediaIcon = '<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>';
  const termsIcon = '<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>';
  
  // Define form tabs with icons for better visual recognition
  const tabs = [
    { 
      id: 'basic', 
      label: safeTranslate('auction.basicInfo', 'Basic Info'),
      icon: basicIcon
    },
    { 
      id: 'scheduling', 
      label: safeTranslate('auction.scheduling', 'Scheduling'),
      icon: schedulingIcon
    },
    { 
      id: 'financial', 
      label: safeTranslate('auction.financial', 'Financial'),
      icon: financialIcon
    },
    { 
      id: 'property', 
      label: safeTranslate('auction.selectProperty', 'Property'),
      icon: propertyIcon
    },
    { 
      id: 'media', 
      label: safeTranslate('auction.media', 'Media'),
      icon: mediaIcon
    },
    { 
      id: 'terms', 
      label: safeTranslate('auction.termsConditions', 'Terms'),
      icon: termsIcon
    }
  ];
  
  // Initialize component
  onMount(() => {
    if (initialAuction) {
      // If we're editing an existing auction, initialize with its data
      auction = {
        ...auction,
        ...initialAuction,
        // Ensure related_property_id is set for PropertySelector
        related_property_id: initialAuction.related_property?.id || null,
        // Ensure media is properly initialized
        media: initialAuction.media || []
      };
      
      // Format dates for datetime-local inputs
      if (auction.start_date) {
        auction.start_date = formatDateForInput(new Date(auction.start_date));
      }
      if (auction.end_date) {
        auction.end_date = formatDateForInput(new Date(auction.end_date));
      }
      if (auction.registration_deadline) {
        auction.registration_deadline = formatDateForInput(new Date(auction.registration_deadline));
      }
    } else {
      // If creating a new auction, set default dates
      const now = new Date();
      
      // Default start date is tomorrow at noon
      const tomorrow = new Date(now);
      tomorrow.setDate(tomorrow.getDate() + 1);
      tomorrow.setHours(12, 0, 0, 0);
      
      // Default end date is 7 days from now at noon
      const nextWeek = new Date(now);
      nextWeek.setDate(nextWeek.getDate() + 7);
      nextWeek.setHours(12, 0, 0, 0);
      
      // Default registration deadline is today at 6 PM
      const today = new Date(now);
      today.setHours(18, 0, 0, 0);
      
      auction.start_date = formatDateForInput(tomorrow);
      auction.end_date = formatDateForInput(nextWeek);
      auction.registration_deadline = formatDateForInput(today);
    }
  });
  
  // Helper function to format dates for input fields
  function formatDateForInput(date) {
    if (!date) return '';
    return date.toISOString().slice(0, 16);
  }
  
  // Create a slug from the title
  function generateSlug(title) {
    return title
      .toLowerCase()
      .replace(/[^\w\s-]/g, '')
      .replace(/\s+/g, '-')
      .replace(/-+/g, '-')
      .trim();
  }
  
  // Handle property selection
  function handlePropertySelect(e) {
    auction.related_property_id = e.detail.id;
    auction.related_property = e.detail;
  }

  // Handle auction type selection with keyboard support
  function handleAuctionTypeSelect(type, event) {
    if (event.type === 'click' || (event.type === 'keydown' && (event.key === 'Enter' || event.key === ' '))) {
      event.preventDefault();
      auction.auction_type = type;
    }
  }
  
  // Handle media uploads - FIXED: Actually upload to server
  async function handleMediaUpload(e) {
    uploadingMedia = true;
    mediaError = '';
    
    try {
      const files = e.detail.files;
      
      if (!files || files.length === 0) {
        throw new Error('No files selected');
      }

      // For new auctions, we need to create a temporary auction first or wait until after auction creation
      // For now, we'll store the files and upload them after auction creation
      if (!isEditing) {
        // Store files temporarily for upload after auction creation
        const tempMedia = Array.from(files).map((file, index) => ({
          id: `temp-${Date.now()}-${index}`,
          file: file, // Store the actual file object
          url: URL.createObjectURL(file), // For preview
          name: file.name,
          media_type: file.type.startsWith('image/') ? 'image' : 'document',
          is_primary: auction.media.length === 0 && index === 0,
          isTemp: true // Mark as temporary
        }));
        
        auction.media = [...auction.media, ...tempMedia];
      } else {
        // For editing, upload immediately since we have an auction ID
        const uploadedMedia = await uploadMultipleMedia(
          files, 
          'auction', 
          auction.id, 
          { makeFirstPrimary: auction.media.length === 0 }
        );
        
        // Add uploaded media to auction media array
        const formattedMedia = uploadedMedia.map(media => ({
          id: media.id,
          url: media.url,
          name: media.name,
          media_type: media.media_type,
          is_primary: media.is_primary,
          isTemp: false
        }));
        
        auction.media = [...auction.media, ...formattedMedia];
      }
    } catch (err) {
      console.error('Media upload error:', err);
      mediaError = err.message || safeTranslate('error.uploadFailed', 'Upload failed');
    } finally {
      uploadingMedia = false;
    }
  }
  
  // Remove media item
  async function removeMedia(mediaId) {
    try {
      const mediaItem = auction.media.find(m => m.id === mediaId);
      
      if (!mediaItem) return;
      
      // If it's a temporary media (not yet uploaded), just remove from array
      if (mediaItem.isTemp) {
        auction.media = auction.media.filter(item => item.id !== mediaId);
        // Revoke the object URL to free memory
        if (mediaItem.url && mediaItem.url.startsWith('blob:')) {
          URL.revokeObjectURL(mediaItem.url);
        }
      } else {
        // If it's uploaded media, delete from server
        await deleteMedia(mediaId);
        auction.media = auction.media.filter(item => item.id !== mediaId);
      }
    } catch (err) {
      console.error('Error removing media:', err);
      mediaError = err.message || safeTranslate('error.deleteFailed', 'Failed to delete media');
    }
  }
  
  // Set primary media
  async function setPrimaryMedia(mediaId) {
    try {
      const mediaItem = auction.media.find(m => m.id === mediaId);
      
      if (!mediaItem) return;
      
      // Update local state
      auction.media = auction.media.map(item => ({
        ...item,
        is_primary: item.id === mediaId
      }));
      
      // If not temporary media, update on server
      if (!mediaItem.isTemp) {
        await updateMedia(mediaId, { is_primary: true });
      }
    } catch (err) {
      console.error('Error setting primary media:', err);
      mediaError = err.message || safeTranslate('error.updateFailed', 'Failed to update media');
    }
  }
  
  // Upload temporary media after auction creation
  export async function uploadTempMedia(auctionId) {
    const tempMedia = auction.media.filter(media => media.isTemp);
    
    if (tempMedia.length === 0) return [];
    
    try {
      const files = tempMedia.map(media => media.file);
      const uploadedMedia = await uploadMultipleMedia(
        files, 
        'auction', 
        auctionId, 
        { makeFirstPrimary: tempMedia.some(m => m.is_primary) }
      );
      
      // Update auction media with server response
      auction.media = auction.media.filter(media => !media.isTemp); // Remove temp media
      
      const formattedMedia = uploadedMedia.map(media => ({
        id: media.id,
        url: media.url,
        name: media.name,
        media_type: media.media_type,
        is_primary: media.is_primary,
        isTemp: false
      }));
      
      auction.media = [...auction.media, ...formattedMedia];
      
      // Clean up temporary URLs
      tempMedia.forEach(media => {
        if (media.url && media.url.startsWith('blob:')) {
          URL.revokeObjectURL(media.url);
        }
      });
      
      return uploadedMedia;
    } catch (err) {
      console.error('Error uploading temporary media:', err);
      throw err;
    }
  }
  
  // Go to next tab
  function goToNextTab() {
    const currentIndex = tabs.findIndex(tab => tab.id === activeTab);
    if (currentIndex < tabs.length - 1) {
      activeTab = tabs[currentIndex + 1].id;
    }
  }
  
  // Go to previous tab
  function goToPreviousTab() {
    const currentIndex = tabs.findIndex(tab => tab.id === activeTab);
    if (currentIndex > 0) {
      activeTab = tabs[currentIndex - 1].id;
    }
  }
  
  // Validate the auction form - can be called by parent
  export function validateForm() {
    touched = {
      title: true,
      related_property_id: true,
      start_date: true,
      end_date: true,
      starting_bid: true
    };
    
    // Check required fields
    if (!auction.title) {
      return { valid: false, error: safeTranslate('auction.titleRequired', 'Title is required'), tab: 'basic' };
    }
    
    if (!auction.related_property_id) {
      return { valid: false, error: safeTranslate('auction.propertyRequired', 'Property is required'), tab: 'property' };
    }
    
    if (!auction.start_date || !auction.end_date) {
      return { valid: false, error: safeTranslate('auction.datesRequired', 'Start and end dates are required'), tab: 'scheduling' };
    }
    
    // Validate date order
    const startDate = new Date(auction.start_date);
    const endDate = new Date(auction.end_date);
    
    if (endDate <= startDate) {
      return { valid: false, error: safeTranslate('auction.endDateAfterStart', 'End date must be after start date'), tab: 'scheduling' };
    }
    
    // Check registration deadline if provided
    if (auction.registration_deadline) {
      const regDeadline = new Date(auction.registration_deadline);
      if (regDeadline >= startDate) {
        return { valid: false, error: safeTranslate('auction.regDeadlineBeforeStart', 'Registration deadline must be before start date'), tab: 'scheduling' };
      }
    }
    
    if (!auction.starting_bid || parseFloat(auction.starting_bid) <= 0) {
      return { valid: false, error: safeTranslate('auction.startingBidRequired', 'Starting bid is required'), tab: 'financial' };
    }
    
    return { valid: true };
  }
  
  // Prepare data for submission - can be called by parent
  export function prepareDataForSubmission() {
    const preparedData = { ...auction };
    
    // Generate slug if not provided
    if (!preparedData.slug && preparedData.title) {
      preparedData.slug = generateSlug(preparedData.title);
    }
    
    // Format dates
    if (preparedData.start_date) {
      preparedData.start_date = new Date(preparedData.start_date).toISOString();
    }
    
    if (preparedData.end_date) {
      preparedData.end_date = new Date(preparedData.end_date).toISOString();
    }
    
    if (preparedData.registration_deadline) {
      preparedData.registration_deadline = new Date(preparedData.registration_deadline).toISOString();
    }
    
    // Handle related_property_id mapping
    if (preparedData.related_property_id) {
      preparedData.related_property_id = parseInt(preparedData.related_property_id, 10);
    }
    
    // Convert numeric values to proper numbers
    if (preparedData.starting_bid) {
      preparedData.starting_bid = parseFloat(preparedData.starting_bid);
    }
    
    if (preparedData.minimum_increment) {
      preparedData.minimum_increment = parseFloat(preparedData.minimum_increment);
    }
    
    if (preparedData.auto_extend_minutes) {
      preparedData.auto_extend_minutes = parseInt(preparedData.auto_extend_minutes, 10);
    }
    
    if (preparedData.minimum_participants) {
      preparedData.minimum_participants = parseInt(preparedData.minimum_participants, 10);
    }
    
    // Don't include media in the auction creation request
    // Media will be uploaded separately
    delete preparedData.media;
    
    return preparedData;
  }
</script>

<div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
  <!-- Progress Indicator -->
  <div class="bg-gray-50 dark:bg-gray-900 px-6 py-4">
    <div class="flex items-center justify-between">
      <h2 class="text-lg font-medium text-gray-900 dark:text-white">
        {isEditing ? safeTranslate('auction.editAuction', 'Edit Auction') : safeTranslate('auction.createAuction', 'Create Auction')}
      </h2>
      <div class="text-sm text-gray-500 dark:text-gray-400">
        {safeTranslate('common.step', 'Step')} {currentStep} {safeTranslate('common.of', 'of')} {totalSteps}
      </div>
    </div>
    <div class="w-full bg-gray-200 dark:bg-gray-700 h-2 mt-2 rounded-full overflow-hidden">
      <div 
        class="bg-primary-600 dark:bg-primary-500 h-full rounded-full transition-all duration-300"
        style="width: {(currentStep / totalSteps) * 100}%"
      ></div>
    </div>
  </div>

  <!-- Tabs Navigation -->
  <div class="px-6 pt-6 pb-3 border-b border-gray-200 dark:border-gray-700">
    <Tabs 
      {tabs} 
      bind:activeTab={activeTab} 
      iconPosition="left" 
      variant="underline"
      size="default"
    />
  </div>
  
  <!-- Tab Content -->
  <div class="p-6">
    {#if activeTab === 'basic'}
      <!-- Basic Info Tab Content -->
      <div class="space-y-6">
        <div class="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
          <!-- Auction Title -->
          <div class="sm:col-span-4">
            <FormField
              type="text"
              id="title"
              label={safeTranslate('auction.title', 'Title')}
              bind:value={auction.title}
              required={true}
              error={touched.title && !auction.title ? safeTranslate('auction.titleRequired', 'Title is required') : ''}
              onBlur={() => touched.title = true}
            />
          </div>
          
          <!-- Auction Type -->
          <div class="sm:col-span-6">
            <fieldset class="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
              <legend class="text-base font-medium text-gray-900 dark:text-white px-2">
                {safeTranslate('auction.auctionType', 'Auction Type')}
              </legend>
              
              <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-2" role="radiogroup" aria-labelledby="auction-type-legend">
                {#each [
                  { value: 'sealed', label: safeTranslate('auction.typeSealed', 'Sealed Bid'), desc: safeTranslate('auction.typeSealedDesc', 'Sealed bid auction') },
                  { value: 'reserve', label: safeTranslate('auction.typeReserve', 'Reserve'), desc: safeTranslate('auction.typeReserveDesc', 'Auction with reserve price') },
                  { value: 'no_reserve', label: safeTranslate('auction.typeNoReserve', 'No Reserve'), desc: safeTranslate('auction.typeNoReserveDesc', 'Auction without reserve') }
                ] as type}
                  <button
                    type="button"
                    role="radio"
                    aria-checked={auction.auction_type === type.value}
                    class="relative border rounded-lg p-4 text-left transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
                    class:border-primary-500={auction.auction_type === type.value}
                    class:bg-primary-50={auction.auction_type === type.value}
                    class:dark:border-primary-400={auction.auction_type === type.value}
                    class:dark:bg-primary-900={auction.auction_type === type.value}
                    class:dark:bg-opacity-20={auction.auction_type === type.value}
                    class:border-gray-300={auction.auction_type !== type.value}
                    class:dark:border-gray-600={auction.auction_type !== type.value}
                    class:hover:border-gray-400={auction.auction_type !== type.value}
                    class:dark:hover:border-gray-500={auction.auction_type !== type.value}
                    on:click={(e) => handleAuctionTypeSelect(type.value, e)}
                    on:keydown={(e) => handleAuctionTypeSelect(type.value, e)}
                  >
                    {#if auction.auction_type === type.value}
                      <div class="absolute top-2 right-2 text-primary-500 dark:text-primary-400">
                        <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                        </svg>
                      </div>
                    {/if}
                    <h3 class="text-sm font-medium text-gray-900 dark:text-white mb-1">{type.label}</h3>
                    <p class="text-xs text-gray-500 dark:text-gray-400">{type.desc}</p>
                  </button>
                {/each}
              </div>
            </fieldset>
          </div>
          
          <!-- Description -->
          <div class="sm:col-span-6">
            <FormField
              type="textarea"
              id="description"
              label={safeTranslate('auction.description', 'Description')}
              bind:value={auction.description}
              rows={4}
            />
          </div>
          
          <!-- Publishing Options -->
          <div class="sm:col-span-6">
            <div class="bg-gray-50 dark:bg-gray-900 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
              <h3 class="text-base font-medium text-gray-900 dark:text-white mb-4">
                {safeTranslate('auction.publishingOptions', 'Publishing Options')}
              </h3>
              <div class="space-y-4">
                <Switch
                  id="is_published"
                  label={safeTranslate('auction.published', 'Published')}
                  description={safeTranslate('auction.publishedHelp', 'Make this auction visible to the public')}
                  bind:checked={auction.is_published}
                  size="default"
                  variant="primary"
                />
                <Switch
                  id="is_featured"
                  label={safeTranslate('auction.featured', 'Featured')}
                  description={safeTranslate('auction.featuredHelp', 'Highlight this auction')}
                  bind:checked={auction.is_featured}
                  size="default"
                  variant="success"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
      
    {:else if activeTab === 'scheduling'}
      <!-- Scheduling Tab Content -->
      <div class="space-y-6">
        <div class="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-2">
          <!-- Start Date -->
          <div>
            <FormField
              type="datetime-local"
              id="start_date"
              label={safeTranslate('auction.startDate', 'Start Date')}
              bind:value={auction.start_date}
              required={true}
              error={touched.start_date && !auction.start_date ? safeTranslate('auction.startDateRequired', 'Start date is required') : ''}
              onBlur={() => touched.start_date = true}
            />
          </div>
          
          <!-- End Date -->
          <div>
            <FormField
              type="datetime-local"
              id="end_date"
              label={safeTranslate('auction.endDate', 'End Date')}
              bind:value={auction.end_date}
              required={true}
              error={touched.end_date && !auction.end_date ? safeTranslate('auction.endDateRequired', 'End date is required') : ''}
              onBlur={() => touched.end_date = true}
            />
          </div>
          
          <!-- Registration Deadline -->
          <div>
            <FormField
              type="datetime-local"
              id="registration_deadline"
              label={safeTranslate('auction.registrationDeadline', 'Registration Deadline')}
              bind:value={auction.registration_deadline}
              helpText={safeTranslate('auction.registrationDeadlineHelp', 'Optional deadline for registration')}
            />
          </div>
          
          <!-- Auto-extend Feature -->
          <div>
            <FormField
              type="number"
              id="auto_extend_minutes"
              label={safeTranslate('auction.autoExtend', 'Auto-extend (minutes)')}
              bind:value={auction.auto_extend_minutes}
              min="0"
              step="1"
              helpText={safeTranslate('auction.autoExtendHelp', 'Extend auction if bid placed near end')}
            />
          </div>
        </div>
      </div>
      
    {:else if activeTab === 'financial'}
      <!-- Financial Tab Content -->
      <div class="space-y-6">
        <div class="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-2">
          <!-- Starting Bid -->
          <div>
            <FormField
              type="currency"
              id="starting_bid"
              label={safeTranslate('auction.startingBid', 'Starting Bid')}
              bind:value={auction.starting_bid}
              required={true}
              error={touched.starting_bid && !auction.starting_bid ? safeTranslate('auction.startingBidRequired', 'Starting bid is required') : ''}
              onBlur={() => touched.starting_bid = true}
              currencySymbol="$"
            />
          </div>
          
          <!-- Minimum Increment -->
          <div>
            <FormField
              type="currency"
              id="minimum_increment"
              label={safeTranslate('auction.minimumIncrement', 'Minimum Increment')}
              bind:value={auction.minimum_increment}
              required={true}
              currencySymbol="$"
            />
          </div>
          
          <!-- Minimum Participants -->
          <div class="sm:col-span-2">
            <FormField
              type="number"
              id="minimum_participants"
              label={safeTranslate('auction.minimumParticipants', 'Minimum Participants')}
              bind:value={auction.minimum_participants}
              min="1"
              step="1"
              helpText={safeTranslate('auction.minimumParticipantsHelp', 'Minimum number of participants required')}
            />
          </div>
        </div>
      </div>
      
    {:else if activeTab === 'property'}
      <!-- Property Selection Tab Content -->
      <div class="space-y-6">
        <PropertySelector
          selectedPropertyId={auction.related_property_id}
          on:select={handlePropertySelect}
          error={touched.related_property_id && !auction.related_property_id ? safeTranslate('auction.propertyRequired', 'Property is required') : ''}
        />
      </div>
      
    {:else if activeTab === 'media'}
      <!-- Media Tab Content -->
      <div class="space-y-6">
        {#if mediaError}
          <Alert type="error" message={mediaError} />
        {/if}
        
        <!-- Media uploader -->
        <div class="border border-gray-200 dark:border-gray-700 rounded-lg p-6">
          <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">
            {safeTranslate('auction.uploadMedia', 'Upload Media')}
          </h3>
          <MediaUploader
            on:change={handleMediaUpload}
            uploadingMedia={uploadingMedia}
            maxFiles={10}
            allowedTypes={['image/jpeg', 'image/png', 'image/webp']}
          />
        </div>
        
        {#if auction.media && auction.media.length > 0}
          <div class="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
            <div class="bg-gray-50 dark:bg-gray-900 px-6 py-4 border-b border-gray-200 dark:border-gray-700">
              <div class="flex justify-between items-center">
                <h3 class="text-lg font-medium text-gray-900 dark:text-white">
                  {safeTranslate('auction.uploadedMedia', 'Uploaded Media')}
                </h3>
                <span class="text-sm text-gray-500 dark:text-gray-400">
                  {auction.media.length} {safeTranslate('auction.items', 'items')}
                </span>
              </div>
            </div>
            <div class="p-6">
              <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
                {#each auction.media as media (media.id)}
                  <div class="relative group border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
                    <div class="aspect-w-3 aspect-h-2 bg-gray-100 dark:bg-gray-800">
                      {#if media.media_type === 'image'}
                        <img
                          src={media.url || media.file}
                          alt={media.name}
                          class="object-cover w-full h-full"
                        />
                      {:else}
                        <div class="flex items-center justify-center h-full">
                          <svg class="h-8 w-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                          </svg>
                        </div>
                      {/if}
                    </div>
                    
                    <div class="p-2 bg-white dark:bg-gray-800">
                      <p class="text-xs text-gray-500 dark:text-gray-400 truncate">
                        {media.name}
                      </p>
                      {#if media.isTemp}
                        <p class="text-xs text-warning-500">
                          {safeTranslate('media.pendingUpload', 'Pending upload')}
                        </p>
                      {/if}
                    </div>
                    
                    <!-- Controls -->
                    <div class="absolute inset-0 bg-gray-900 bg-opacity-50 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                      <div class="flex flex-col space-y-2">
                        <button
                          type="button"
                          class="px-3 py-1 bg-white text-gray-700 rounded text-xs font-medium hover:bg-gray-50 transition-colors"
                          on:click={() => setPrimaryMedia(media.id)}
                          aria-label={safeTranslate('auction.setPrimaryMedia', 'Set as primary media for {name}', { name: media.name })}
                        >
                          {safeTranslate('auction.setPrimary', 'Set Primary')}
                        </button>
                        <button
                          type="button"
                          class="px-3 py-1 bg-danger-500 text-white rounded text-xs font-medium hover:bg-danger-600 transition-colors"
                          on:click={() => removeMedia(media.id)}
                          aria-label={safeTranslate('auction.removeMedia', 'Remove media {name}', { name: media.name })}
                        >
                          {safeTranslate('auction.remove', 'Remove')}
                        </button>
                      </div>
                    </div>
                    
                    {#if media.is_primary}
                      <div class="absolute top-0 left-0 m-2">
                        <span class="inline-flex items-center px-1.5 py-0.5 rounded-full text-xs font-medium bg-success-100 text-success-800 dark:bg-success-900 dark:text-success-200">
                          {safeTranslate('auction.primary', 'Primary')}
                        </span>
                      </div>
                    {/if}
                  </div>
                {/each}
              </div>
            </div>
          </div>
        {/if}
      </div>
      
    {:else if activeTab === 'terms'}
      <!-- Terms Tab Content -->
      <div class="space-y-6">
        <div class="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
          <div class="bg-gray-50 dark:bg-gray-900 px-6 py-4 border-b border-gray-200 dark:border-gray-700">
            <h3 class="text-lg font-medium text-gray-900 dark:text-white">
              {safeTranslate('auction.termsConditionsText', 'Terms and Conditions')}
            </h3>
            <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
              {safeTranslate('auction.termsConditionsHelp', 'Define the terms and conditions for this auction')}
            </p>
          </div>
          <div class="p-6">
            <FormField
              type="textarea"
              id="terms_conditions"
              bind:value={auction.terms_conditions}
              rows={12}
            />
          </div>
        </div>
      </div>
    {/if}
  </div>
  
  <!-- Action Buttons -->
  <div class="bg-gray-50 dark:bg-gray-900 px-6 py-4 flex justify-between items-center border-t border-gray-200 dark:border-gray-700">
    <button
      type="button"
      class="inline-flex items-center px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      on:click={goToPreviousTab}
      disabled={currentStep === 1}
    >
      <svg class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
      </svg>
      {safeTranslate('common.previous', 'Previous')}
    </button>
    
    {#if currentStep < totalSteps}
      <button
        type="button"
        class="inline-flex items-center px-3 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 transition-colors"
        on:click={goToNextTab}
      >
        {safeTranslate('common.next', 'Next')}
        <svg class="h-4 w-4 ml-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
        </svg>
      </button>
    {/if}
  </div>
</div>