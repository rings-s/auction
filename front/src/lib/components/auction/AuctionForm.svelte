<!-- src/lib/components/auction/AuctionForm.svelte -->
<script>
  import { onMount } from 'svelte';
  import { t } from '../../../../../i18n';
  import { getProperties } from '$lib/api/property';
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
  const basicIcon = '<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>';
  const schedulingIcon = '<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>';
  const financialIcon = '<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>';
  const propertyIcon = '<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" /></svg>';
  const mediaIcon = '<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>';
  const termsIcon = '<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>';
  
  // Define form tabs with icons for better visual recognition
  const tabs = [
    { 
      id: 'basic', 
      label: $t('auction.basicInfo'),
      icon: basicIcon
    },
    { 
      id: 'scheduling', 
      label: $t('auction.scheduling'),
      icon: schedulingIcon
    },
    { 
      id: 'financial', 
      label: $t('auction.financial'),
      icon: financialIcon
    },
    { 
      id: 'property', 
      label: $t('auction.selectProperty'),
      icon: propertyIcon
    },
    { 
      id: 'media', 
      label: $t('auction.media'),
      icon: mediaIcon
    },
    { 
      id: 'terms', 
      label: $t('auction.termsConditions'),
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
        related_property_id: initialAuction.related_property?.id || null
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
  
  // Handle media uploads
  async function handleMediaUpload(e) {
    uploadingMedia = true;
    mediaError = '';
    
    try {
      // This would typically upload files to your server and get URLs back
      const files = e.detail.files;
      
      // Simulating upload
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Add uploaded media to auction media array
      auction.media = [
        ...auction.media,
        ...Array.from(files).map((file, index) => ({
          id: `temp-${Date.now()}-${index}`,
          file: URL.createObjectURL(file),
          name: file.name,
          media_type: file.type.startsWith('image/') ? 'image' : 'document',
          is_primary: auction.media.length === 0 && index === 0 // First upload is primary
        }))
      ];
    } catch (err) {
      console.error('Error uploading media:', err);
      mediaError = err.message || $t('error.uploadFailed');
    } finally {
      uploadingMedia = false;
    }
  }
  
  // Remove media item
  function removeMedia(id) {
    auction.media = auction.media.filter(item => item.id !== id);
  }
  
  // Set primary media
  function setPrimaryMedia(id) {
    auction.media = auction.media.map(item => ({
      ...item,
      is_primary: item.id === id
    }));
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
      return { valid: false, error: $t('auction.titleRequired'), tab: 'basic' };
    }
    
    if (!auction.related_property_id) {
      return { valid: false, error: $t('auction.propertyRequired'), tab: 'property' };
    }
    
    if (!auction.start_date || !auction.end_date) {
      return { valid: false, error: $t('auction.datesRequired'), tab: 'scheduling' };
    }
    
    // Validate date order
    const startDate = new Date(auction.start_date);
    const endDate = new Date(auction.end_date);
    
    if (endDate <= startDate) {
      return { valid: false, error: $t('auction.endDateAfterStart'), tab: 'scheduling' };
    }
    
    // Check registration deadline if provided
    if (auction.registration_deadline) {
      const regDeadline = new Date(auction.registration_deadline);
      if (regDeadline >= startDate) {
        return { valid: false, error: $t('auction.regDeadlineBeforeStart'), tab: 'scheduling' };
      }
    }
    
    if (!auction.starting_bid || parseFloat(auction.starting_bid) <= 0) {
      return { valid: false, error: $t('auction.startingBidRequired'), tab: 'financial' };
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
    
    // FIX: Correctly handle related_property_id mapping to related_property
    if (preparedData.related_property_id) {
      preparedData.related_property_id = parseInt(preparedData.related_property_id, 10);
      preparedData.related_property = preparedData.related_property_id;
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
    
    return preparedData;
  }
</script>

<div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
  <!-- Progress Indicator -->
  <div class="bg-gray-50 dark:bg-gray-900 px-6 py-4">
    <div class="flex items-center justify-between">
      <h2 class="text-lg font-medium text-gray-900 dark:text-white">
        {isEditing ? $t('auction.editAuction') : $t('auction.createAuction')}
      </h2>
      <div class="text-sm text-gray-500 dark:text-gray-400">
        {$t('common.step')} {currentStep} {$t('common.of')} {totalSteps}
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
      <div class="space-y-8">
        <div class="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
          <div class="flex">
            <div class="flex-shrink-0">
              <svg class="h-5 w-5 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div class="ml-3">
              <h3 class="text-sm font-medium text-blue-800 dark:text-blue-200">
                {$t('auction.basicInfo')}
              </h3>
              <div class="mt-2 text-sm text-blue-700 dark:text-blue-300">
                <p>{$t('auction.basicInfoDesc')}</p>
              </div>
            </div>
          </div>
        </div>
        
        <div class="grid grid-cols-1 gap-y-8 gap-x-6 sm:grid-cols-6">
          <!-- Auction Title -->
          <div class="sm:col-span-4">
            <FormField
              type="text"
              id="title"
              label={$t('auction.title')}
              bind:value={auction.title}
              required={true}
              error={touched.title && !auction.title ? $t('auction.titleRequired') : ''}
              onBlur={() => touched.title = true}
            />
          </div>
          
          <!-- Auction Slug (for editing) -->
          {#if isEditing}
            <div class="sm:col-span-4">
              <FormField
                type="text"
                id="slug"
                label={$t('auction.slug')}
                bind:value={auction.slug}
                helpText={$t('auction.slugHelp')}
              />
            </div>
          {/if}
          
          <!-- Auction Type with better visual grouping -->
          <div class="sm:col-span-6">
            <fieldset class="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
              <legend class="text-base font-medium text-gray-900 dark:text-white px-2">
                {$t('auction.auctionType')}
              </legend>
              
              <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-2">
                {#each [
                  { value: 'sealed', label: $t('auction.typeSealed'), desc: $t('auction.typeSealedDesc') },
                  { value: 'reserve', label: $t('auction.typeReserve'), desc: $t('auction.typeReserveDesc') },
                  { value: 'no_reserve', label: $t('auction.typeNoReserve'), desc: $t('auction.typeNoReserveDesc') }
                ] as type}
                  <div 
                    class="relative border rounded-lg p-4 cursor-pointer transition-all duration-200"
                    class:border-primary-500={auction.auction_type === type.value}
                    class:bg-primary-50={auction.auction_type === type.value}
                    class:dark:border-primary-400={auction.auction_type === type.value}
                    class:dark:bg-primary-900={auction.auction_type === type.value}
                    class:dark:bg-opacity-20={auction.auction_type === type.value}
                    class:border-gray-300={auction.auction_type !== type.value}
                    class:dark:border-gray-600={auction.auction_type !== type.value}
                    class:hover:border-gray-400={auction.auction_type !== type.value}
                    class:dark:hover:border-gray-500={auction.auction_type !== type.value}
                    on:click={() => auction.auction_type = type.value}
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
                  </div>
                {/each}
              </div>
            </fieldset>
          </div>
          
          <!-- Status -->
          <div class="sm:col-span-3">
            <FormField
              type="select"
              id="status"
              label={$t('auction.status')}
              bind:value={auction.status}
              options={[
                { value: 'draft', label: $t('auction.statusDraft') },
                { value: 'scheduled', label: $t('auction.statusScheduled') },
                ...(isEditing ? [
                  { value: 'live', label: $t('auction.statusLive') },
                  { value: 'ended', label: $t('auction.statusEnded') },
                  { value: 'completed', label: $t('auction.statusCompleted') }
                ] : [])
              ]}
            />
          </div>
          
          <!-- Description with enhanced presentation -->
          <div class="sm:col-span-6">
            <FormField
              type="textarea"
              id="description"
              label={$t('auction.description')}
              bind:value={auction.description}
              rows={5}
            />
          </div>
          
          <!-- Publishing Options in a card for better visual hierarchy -->
          <div class="sm:col-span-6">
            <div class="bg-gray-50 dark:bg-gray-900 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
              <h3 class="text-base font-medium text-gray-900 dark:text-white mb-4">
                {$t('auction.publishingOptions')}
              </h3>
              <div class="space-y-4">
                <Switch
                  id="is_published"
                  label={$t('auction.published')}
                  description={$t('auction.publishedHelp')}
                  bind:checked={auction.is_published}
                  size="large"
                  variant="primary"
                />
                <Switch
                  id="is_featured"
                  label={$t('auction.featured')}
                  description={$t('auction.featuredHelp')}
                  bind:checked={auction.is_featured}
                  size="large"
                  variant="success"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
      
    {:else if activeTab === 'scheduling'}
      <div class="space-y-8">
        <div class="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
          <div class="flex">
            <div class="flex-shrink-0">
              <svg class="h-5 w-5 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <div class="ml-3">
              <h3 class="text-sm font-medium text-blue-800 dark:text-blue-200">
                {$t('auction.scheduling')}
              </h3>
              <div class="mt-2 text-sm text-blue-700 dark:text-blue-300">
                <p>{$t('auction.schedulingDesc')}</p>
              </div>
            </div>
          </div>
        </div>
        
        <div class="grid grid-cols-1 gap-y-8 gap-x-6 sm:grid-cols-6">
          <!-- Start Date -->
          <div class="sm:col-span-3">
            <FormField
              type="datetime-local"
              id="start_date"
              label={$t('auction.startDate')}
              bind:value={auction.start_date}
              required={true}
              error={touched.start_date && !auction.start_date ? $t('auction.startDateRequired') : ''}
              onBlur={() => touched.start_date = true}
            />
          </div>
          
          <!-- End Date -->
          <div class="sm:col-span-3">
            <FormField
              type="datetime-local"
              id="end_date"
              label={$t('auction.endDate')}
              bind:value={auction.end_date}
              required={true}
              error={touched.end_date && !auction.end_date ? $t('auction.endDateRequired') : ''}
              onBlur={() => touched.end_date = true}
            />
          </div>
          
          <!-- Registration Deadline -->
          <div class="sm:col-span-3">
            <FormField
              type="datetime-local"
              id="registration_deadline"
              label={$t('auction.registrationDeadline')}
              bind:value={auction.registration_deadline}
              helpText={$t('auction.registrationDeadlineHelp')}
            />
          </div>
          
          <!-- Auto-extend Feature -->
          <div class="sm:col-span-3">
            <FormField
              type="number"
              id="auto_extend_minutes"
              label={$t('auction.autoExtend')}
              bind:value={auction.auto_extend_minutes}
              min="0"
              step="1"
              helpText={$t('auction.autoExtendHelp')}
            />
          </div>
        </div>
        
        <!-- Timeline visualization -->
        <div class="border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
          <h3 class="text-base font-medium text-gray-900 dark:text-white mb-4">
            {$t('auction.timeline')}
          </h3>
          
          <div class="relative">
            <div class="absolute top-4 left-5 h-full w-0.5 bg-gray-300 dark:bg-gray-600"></div>
            
            <div class="space-y-6 relative">
              {#if auction.registration_deadline}
                <div class="flex space-x-4 items-start">
                  <div class="flex-shrink-0 w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center z-10">
                    <svg class="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
                    </svg>
                  </div>
                  <div class="pt-1.5">
                    <h4 class="text-sm font-medium text-gray-900 dark:text-white">
                      {$t('auction.registrationDeadline')}
                    </h4>
                    <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
                      {auction.registration_deadline ? new Date(auction.registration_deadline).toLocaleString() : ''}
                    </p>
                  </div>
                </div>
              {/if}
              
              <div class="flex space-x-4 items-start">
                <div class="flex-shrink-0 w-10 h-10 rounded-full bg-green-100 dark:bg-green-900 flex items-center justify-center z-10">
                  <svg class="w-5 h-5 text-green-600 dark:text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                  </svg>
                </div>
                <div class="pt-1.5">
                  <h4 class="text-sm font-medium text-gray-900 dark:text-white">
                    {$t('auction.startDate')}
                  </h4>
                  <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
                    {auction.start_date ? new Date(auction.start_date).toLocaleString() : ''}
                  </p>
                </div>
              </div>
              
              <div class="flex space-x-4 items-start">
                <div class="flex-shrink-0 w-10 h-10 rounded-full bg-red-100 dark:bg-red-900 flex items-center justify-center z-10">
                  <svg class="w-5 h-5 text-red-600 dark:text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
                  </svg>
                </div>
                <div class="pt-1.5">
                  <h4 class="text-sm font-medium text-gray-900 dark:text-white">
                    {$t('auction.endDate')}
                  </h4>
                  <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
                    {auction.end_date ? new Date(auction.end_date).toLocaleString() : ''}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
    {:else if activeTab === 'financial'}
      <div class="space-y-8">
        <div class="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
          <div class="flex">
            <div class="flex-shrink-0">
              <svg class="h-5 w-5 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div class="ml-3">
              <h3 class="text-sm font-medium text-blue-800 dark:text-blue-200">
                {$t('auction.financial')}
              </h3>
              <div class="mt-2 text-sm text-blue-700 dark:text-blue-300">
                <p>{$t('auction.financialDesc')}</p>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Bid structure -->
        <div class="rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
          <div class="px-4 py-5 bg-gray-50 dark:bg-gray-900 sm:px-6 border-b border-gray-200 dark:border-gray-700">
            <h3 class="text-lg font-medium leading-6 text-gray-900 dark:text-white">
              {$t('auction.bidding')}
            </h3>
          </div>
          <div class="px-4 py-5 sm:p-6">
            <div class="grid grid-cols-1 gap-y-8 gap-x-6 sm:grid-cols-6">
              <!-- Starting Bid -->
              <div class="sm:col-span-3">
                <FormField
                  type="currency"
                  id="starting_bid"
                  label={$t('auction.startingBid')}
                  bind:value={auction.starting_bid}
                  required={true}
                  error={touched.starting_bid && !auction.starting_bid ? $t('auction.startingBidRequired') : ''}
                  onBlur={() => touched.starting_bid = true}
                  currencySymbol="$"
                />
              </div>
              
              <!-- Minimum Increment -->
              <div class="sm:col-span-3">
                <FormField
                  type="currency"
                  id="minimum_increment"
                  label={$t('auction.minimumIncrement')}
                  bind:value={auction.minimum_increment}
                  required={true}
                  currencySymbol="$"
                />
              </div>
              
              <!-- Minimum Participants -->
              <div class="sm:col-span-3">
                <FormField
                  type="number"
                  id="minimum_participants"
                  label={$t('auction.minimumParticipants')}
                  bind:value={auction.minimum_participants}
                  min="1"
                  step="1"
                  helpText={$t('auction.minimumParticipantsHelp')}
                />
              </div>
              
              <!-- Bid Verification -->
              <div class="sm:col-span-6 mt-4">
                <div class="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
                  <Switch
                    id="require_bid_verification"
                    label={$t('auction.requireBidVerification')}
                    description={$t('auction.requireBidVerificationHelp')}
                    bind:checked={auction.require_bid_verification}
                    size="large"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
    {:else if activeTab === 'property'}
      <div class="space-y-8">
        <div class="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
          <div class="flex">
            <div class="flex-shrink-0">
              <svg class="h-5 w-5 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
            </div>
            <div class="ml-3">
              <h3 class="text-sm font-medium text-blue-800 dark:text-blue-200">
                {$t('auction.selectProperty')}
              </h3>
              <div class="mt-2 text-sm text-blue-700 dark:text-blue-300">
                <p>{$t('auction.selectPropertyDesc')}</p>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Property selection -->
        <div class="rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
          <div class="px-4 py-5 bg-gray-50 dark:bg-gray-900 sm:px-6">
            <div class="flex justify-between items-center">
              <h3 class="text-lg font-medium leading-6 text-gray-900 dark:text-white">
                {auction.related_property_id ? $t('auction.selectedProperty') : $t('auction.selectProperty')}
              </h3>
              {#if auction.related_property_id}
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                  {$t('auction.propertySelected')}
                </span>
              {/if}
            </div>
          </div>
          <div class="px-4 py-5 sm:p-6">
            <PropertySelector
              selectedPropertyId={auction.related_property_id}
              on:select={handlePropertySelect}
              error={touched.related_property_id && !auction.related_property_id ? $t('auction.propertyRequired') : ''}
            />
          </div>
        </div>
      </div>
      
    {:else if activeTab === 'media'}
      <div class="space-y-8">
        <div class="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
          <div class="flex">
            <div class="flex-shrink-0">
              <svg class="h-5 w-5 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <div class="ml-3">
              <h3 class="text-sm font-medium text-blue-800 dark:text-blue-200">
                {$t('auction.media')}
              </h3>
              <div class="mt-2 text-sm text-blue-700 dark:text-blue-300">
                <p>{$t('auction.mediaDesc')}</p>
              </div>
            </div>
          </div>
        </div>
        
        {#if mediaError}
          <Alert type="error" message={mediaError} />
        {/if}
        
        <!-- Media uploader -->
        <div class="rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
          <div class="px-4 py-5 bg-gray-50 dark:bg-gray-900 sm:px-6 border-b border-gray-200 dark:border-gray-700">
            <h3 class="text-lg font-medium leading-6 text-gray-900 dark:text-white">
              {$t('auction.uploadMedia')}
            </h3>
          </div>
          <div class="px-4 py-5 sm:p-6">
            <MediaUploader
              on:change={handleMediaUpload}
              {uploadingMedia}
              progress={50}
              maxFiles={10}
              allowedTypes={['image/jpeg', 'image/png', 'image/webp']}
            />
          </div>
        </div>
        
        {#if auction.media && auction.media.length > 0}
          <div class="rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
            <div class="px-4 py-5 bg-gray-50 dark:bg-gray-900 sm:px-6 border-b border-gray-200 dark:border-gray-700">
              <div class="flex justify-between items-center">
                <h3 class="text-lg font-medium leading-6 text-gray-900 dark:text-white">
                  {$t('auction.uploadedMedia')}
                </h3>
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                  {auction.media.length} {$t('auction.items')}
                </span>
              </div>
            </div>
            <div class="px-4 py-5 sm:p-6">
              <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
                {#each auction.media as media (media.id)}
                  <div class="relative group border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
                    <div class="aspect-w-3 aspect-h-2 bg-gray-100 dark:bg-gray-800">
                      {#if media.media_type === 'image'}
                        <img
                          src={media.file}
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
                    </div>
                    
                    <!-- Controls -->
                    <div class="absolute inset-0 bg-gray-900 bg-opacity-50 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                      <div class="flex flex-col space-y-2">
                        <button
                          type="button"
                          class="flex items-center justify-center px-3 py-1.5 bg-white text-gray-700 rounded-md text-sm font-medium hover:bg-gray-50 transition-colors"
                          on:click={() => setPrimaryMedia(media.id)}
                        >
                          <svg class="h-4 w-4 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
                          </svg>
                          {$t('auction.setPrimary')}
                        </button>
                        <button
                          type="button"
                          class="flex items-center justify-center px-3 py-1.5 bg-red-500 text-white rounded-md text-sm font-medium hover:bg-red-600 transition-colors"
                          on:click={() => removeMedia(media.id)}
                        >
                          <svg class="h-4 w-4 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                          {$t('auction.remove')}
                        </button>
                      </div>
                    </div>
                    
                    {#if media.is_primary}
                      <div class="absolute top-0 left-0 m-2">
                        <span class="inline-flex items-center px-1.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                          {$t('auction.primary')}
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
      <div class="space-y-8">
        <div class="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
          <div class="flex">
            <div class="flex-shrink-0">
              <svg class="h-5 w-5 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div class="ml-3">
              <h3 class="text-sm font-medium text-blue-800 dark:text-blue-200">
                {$t('auction.termsConditions')}
              </h3>
              <div class="mt-2 text-sm text-blue-700 dark:text-blue-300">
                <p>{$t('auction.termsConditionsDesc')}</p>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Terms and conditions editor -->
        <div class="rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
          <div class="px-4 py-5 bg-gray-50 dark:bg-gray-900 sm:px-6 border-b border-gray-200 dark:border-gray-700">
            <h3 class="text-lg font-medium leading-6 text-gray-900 dark:text-white">
              {$t('auction.termsConditionsText')}
            </h3>
            <p class="mt-1 max-w-2xl text-sm text-gray-500 dark:text-gray-400">
              {$t('auction.termsConditionsHelp')}
            </p>
          </div>
          <div class="px-4 py-5 sm:p-6">
            <FormField
              type="textarea"
              id="terms_conditions"
              bind:value={auction.terms_conditions}
              rows={15}
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
      class="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors"
      on:click={goToPreviousTab}
      disabled={currentStep === 1}
    >
      <svg class="h-5 w-5 mr-2 -ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
      </svg>
      {$t('common.previous')}
    </button>
    
    {#if currentStep < totalSteps}
      <button
        type="button"
        class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors"
        on:click={goToNextTab}
      >
        {$t('common.next')}
        <svg class="h-5 w-5 ml-2 -mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
        </svg>
      </button>
    {/if}
  </div>
</div>