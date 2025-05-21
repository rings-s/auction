<!-- src/lib/components/AuctionForm.svelte -->
<script>
  import { onMount } from 'svelte';
  import { t } from '$lib/i18n/i18n';
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
  
  // Form validation state
  let touched = {
    title: false,
    related_property_id: false,
    start_date: false,
    end_date: false,
    starting_bid: false
  };
  
  // Define form tabs
  const tabs = [
    { id: 'basic', label: $t('auction.basicInfo') },
    { id: 'scheduling', label: $t('auction.scheduling') },
    { id: 'financial', label: $t('auction.financial') },
    { id: 'property', label: $t('auction.selectProperty') },
    { id: 'media', label: $t('auction.media') },
    { id: 'terms', label: $t('auction.termsConditions') }
  ];
  
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
      // For now, we'll just add them to our media array
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
    
    // Map related_property_id to related_property for API
    if (preparedData.related_property_id) {
      preparedData.related_property = preparedData.related_property_id;
    }
    
    // Remove client-side only fields
    delete preparedData.related_property_id;
    
    return preparedData;
  }
</script>

<!-- Tab Content -->
<div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
  <!-- Tabs Navigation -->
  <Tabs {tabs} bind:activeTab />
  
  <div class="mt-6">
    {#if activeTab === 'basic'}
      <div class="space-y-6">
        <div>
          <h2 class="text-lg font-medium leading-6 text-gray-900 dark:text-white">
            {$t('auction.basicInfo')}
          </h2>
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
            {$t('auction.basicInfoDesc')}
          </p>
        </div>
        
        <div class="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
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
          
          <!-- Auction Type -->
          <div class="sm:col-span-3">
            <FormField
              type="select"
              id="auction_type"
              label={$t('auction.auctionType')}
              bind:value={auction.auction_type}
              options={[
                { value: 'sealed', label: $t('auction.typeSealed') },
                { value: 'reserve', label: $t('auction.typeReserve') },
                { value: 'no_reserve', label: $t('auction.typeNoReserve') }
              ]}
              helpText={
                auction.auction_type === 'sealed' ? $t('auction.typeSealedDesc') :
                auction.auction_type === 'reserve' ? $t('auction.typeReserveDesc') :
                $t('auction.typeNoReserveDesc')
              }
            />
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
          
          <!-- Description -->
          <div class="sm:col-span-6">
            <FormField
              type="textarea"
              id="description"
              label={$t('auction.description')}
              bind:value={auction.description}
              rows={5}
            />
          </div>
          
          <!-- Publishing Options -->
          <div class="sm:col-span-6">
            <fieldset>
              <legend class="text-sm font-medium text-gray-700 dark:text-gray-300">
                {$t('auction.publishingOptions')}
              </legend>
              <div class="mt-4 space-y-4">
                <Switch
                  id="is_published"
                  label={$t('auction.published')}
                  description={$t('auction.publishedHelp')}
                  bind:checked={auction.is_published}
                />
                <Switch
                  id="is_featured"
                  label={$t('auction.featured')}
                  description={$t('auction.featuredHelp')}
                  bind:checked={auction.is_featured}
                />
              </div>
            </fieldset>
          </div>
        </div>
      </div>
      
    {:else if activeTab === 'scheduling'}
      <div class="space-y-6">
        <div>
          <h2 class="text-lg font-medium leading-6 text-gray-900 dark:text-white">
            {$t('auction.scheduling')}
          </h2>
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
            {$t('auction.schedulingDesc')}
          </p>
        </div>
        
        <div class="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
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
      </div>
      
    {:else if activeTab === 'financial'}
      <div class="space-y-6">
        <div>
          <h2 class="text-lg font-medium leading-6 text-gray-900 dark:text-white">
            {$t('auction.financial')}
          </h2>
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
            {$t('auction.financialDesc')}
          </p>
        </div>
        
        <div class="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
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
          <div class="sm:col-span-6">
            <Switch
              id="require_bid_verification"
              label={$t('auction.requireBidVerification')}
              description={$t('auction.requireBidVerificationHelp')}
              bind:checked={auction.require_bid_verification}
            />
          </div>
        </div>
      </div>
      
    {:else if activeTab === 'property'}
      <div class="space-y-6">
        <div>
          <h2 class="text-lg font-medium leading-6 text-gray-900 dark:text-white">
            {$t('auction.selectProperty')}
          </h2>
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
            {$t('auction.selectPropertyDesc')}
          </p>
        </div>
        
        <PropertySelector
          selectedPropertyId={auction.related_property_id}
          on:select={handlePropertySelect}
          error={touched.related_property_id && !auction.related_property_id ? $t('auction.propertyRequired') : ''}
        />
      </div>
      
    {:else if activeTab === 'media'}
      <div class="space-y-6">
        <div>
          <h2 class="text-lg font-medium leading-6 text-gray-900 dark:text-white">
            {$t('auction.media')}
          </h2>
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
            {$t('auction.mediaDesc')}
          </p>
        </div>
        
        {#if mediaError}
          <Alert type="error" message={mediaError} />
        {/if}
        
        <MediaUploader
          on:change={handleMediaUpload}
          {uploadingMedia}
          progress={50}
          maxFiles={10}
          allowedTypes={['image/jpeg', 'image/png', 'image/webp']}
        />
        
        {#if auction.media && auction.media.length > 0}
          <div>
            <h3 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
              {$t('auction.uploadedMedia')}
            </h3>
            
            <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
              {#each auction.media as media (media.id)}
                <div class="relative group">
                  <div class="aspect-w-3 aspect-h-2 rounded-lg overflow-hidden bg-gray-100 dark:bg-gray-800">
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
                  
                  <div class="absolute top-2 right-2 flex space-x-1">
                    <button
                      type="button"
                      class="p-1 rounded-full bg-white shadow-sm text-gray-500 opacity-0 group-hover:opacity-100 transition-opacity"
                      on:click={() => setPrimaryMedia(media.id)}
                      aria-label={$t('auction.setPrimary')}
                    >
                      <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
                      </svg>
                    </button>
                    <button
                      type="button"
                      class="p-1 rounded-full bg-red-100 text-red-600 opacity-0 group-hover:opacity-100 transition-opacity"
                      on:click={() => removeMedia(media.id)}
                      aria-label={$t('auction.removeMedia')}
                    >
                      <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                  
                  {#if media.is_primary}
                    <div class="absolute top-0 left-0 m-2">
                      <span class="inline-flex items-center px-1.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        {$t('auction.primary')}
                      </span>
                    </div>
                  {/if}
                  
                  <p class="mt-1 text-xs text-gray-500 dark:text-gray-400 truncate">
                    {media.name}
                  </p>
                </div>
              {/each}
            </div>
          </div>
        {/if}
      </div>
      
    {:else if activeTab === 'terms'}
      <div class="space-y-6">
        <div>
          <h2 class="text-lg font-medium leading-6 text-gray-900 dark:text-white">
            {$t('auction.termsConditions')}
          </h2>
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
            {$t('auction.termsConditionsDesc')}
          </p>
        </div>
        
        <div>
          <FormField
            type="textarea"
            id="terms_conditions"
            label={$t('auction.termsConditionsText')}
            bind:value={auction.terms_conditions}
            rows={10}
            helpText={$t('auction.termsConditionsHelp')}
          />
        </div>
      </div>
    {/if}
  </div>
</div>