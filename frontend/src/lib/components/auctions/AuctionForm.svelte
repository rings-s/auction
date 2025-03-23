<!-- src/routes/auctions/components/AuctionForm.svelte -->
<script>
    import { onMount, createEventDispatcher } from 'svelte';
    import { t } from '$lib/i18n';
    import { DateTimePicker } from '$lib/components/form';
    import { Dropdown, NumericInput, TextInput, TextArea, Switch } from '$lib/components/form';
    import { Button, Loading, Alert } from '$lib/components/ui';
    import { auctionActions, loading, errors } from '$lib/stores/auction';
    import propertyStore from '$lib/stores/property';
    
    // Props
    export let auctionData = null;
    export let mode = 'create'; // 'create' or 'edit'
    export let submitText = t('general.create'); // Button text
    export let cancelable = true;
    export let redirectAfterSubmit = true;
    
    // Component state
    let formData = initFormData();
    let formErrors = {};
    let isSubmitting = false;
    let alertMessage = '';
    let alertType = 'info';
    let showAlert = false;
    let propertiesLoading = false;
    let propertyOptions = [];
    
    const dispatch = createEventDispatcher();
    
    // Initialize form data
    function initFormData() {
      if (mode === 'edit' && auctionData) {
        // For edit mode, use existing data
        return {
          property_id: auctionData.related_property?.id,
          title: auctionData.title || '',
          description: auctionData.description || '',
          auction_type: auctionData.auction_type || 'online',
          start_date: auctionData.start_date ? new Date(auctionData.start_date) : null,
          end_date: auctionData.end_date ? new Date(auctionData.end_date) : null,
          starting_price: auctionData.starting_price || 0,
          reserve_price: auctionData.reserve_price || 0,
          min_bid_increment: auctionData.min_bid_increment || 100,
          deposit_required: auctionData.deposit_required || false,
          deposit_amount: auctionData.deposit_amount || 0,
          buyer_premium_percent: auctionData.buyer_premium_percent || 5,
          seller_commission_percent: auctionData.seller_commission_percent || 2.5,
          auto_extend: auctionData.auto_extend || true,
          extension_minutes: auctionData.extension_minutes || 10,
          is_private: auctionData.is_private || false,
          is_featured: auctionData.is_featured || false,
          is_published: auctionData.is_published || false,
          terms_conditions: auctionData.terms_conditions || ''
        };
      } else {
        // For create mode, use defaults
        return {
          property_id: '',
          title: '',
          description: '',
          auction_type: 'online',
          start_date: new Date(new Date().getTime() + 24 * 60 * 60 * 1000), // Default to tomorrow
          end_date: new Date(new Date().getTime() + 7 * 24 * 60 * 60 * 1000), // Default to a week from now
          starting_price: 0,
          reserve_price: 0,
          min_bid_increment: 100,
          deposit_required: false,
          deposit_amount: 0,
          buyer_premium_percent: 5,
          seller_commission_percent: 2.5,
          auto_extend: true,
          extension_minutes: 10,
          is_private: false,
          is_featured: false,
          is_published: false,
          terms_conditions: ''
        };
      }
    }
    
    // Load available properties
    async function loadProperties() {
      propertiesLoading = true;
      
      try {
        // Load user's properties
        const result = await propertyStore.loadProperties({
          status: 'active',
          owner_id: 'current', // Assuming API supports this to get current user's properties
          has_auction: false, // Only properties without active auctions
          page_size: 100
        });
        
        if (result.success) {
          propertyOptions = result.data.results.map(prop => ({
            value: prop.id,
            label: `${prop.title} - ${prop.property_type_display || prop.property_type}`
          }));
          
          // If in edit mode, include the current property
          if (mode === 'edit' && auctionData?.related_property) {
            const currentPropertyExists = propertyOptions.some(p => p.value === auctionData.related_property.id);
            
            if (!currentPropertyExists) {
              propertyOptions.unshift({
                value: auctionData.related_property.id,
                label: `${auctionData.related_property.title} - ${auctionData.related_property.property_type_display || auctionData.related_property.property_type}`
              });
            }
          }
        } else {
          showErrorAlert(result.error || t('properties.load_error'));
        }
      } catch (error) {
        showErrorAlert(error?.message || t('general.error_occurred'));
      } finally {
        propertiesLoading = false;
      }
    }
    
    // Auction type options
    const auctionTypeOptions = [
      { value: 'public', label: t('auctions.types.public') },
      { value: 'private', label: t('auctions.types.private') },
      { value: 'online', label: t('auctions.types.online') },
      { value: 'onsite', label: t('auctions.types.onsite') },
      { value: 'hybrid', label: t('auctions.types.hybrid') }
    ];
    
    // Form validation
    function validateForm() {
      const errors = {};
      
      // Required fields
      if (!formData.property_id) errors.property_id = t('auctions.property_required');
      if (!formData.title) errors.title = t('auctions.title_required');
      if (!formData.start_date) errors.start_date = t('auctions.start_date_required');
      if (!formData.end_date) errors.end_date = t('auctions.end_date_required');
      if (formData.starting_price <= 0) errors.starting_price = t('auctions.starting_price_required');
      if (formData.reserve_price <= 0) errors.reserve_price = t('auctions.reserve_price_required');
      
      // Business logic validation
      if (formData.start_date && formData.end_date && formData.start_date >= formData.end_date) {
        errors.end_date = t('auctions.end_date_after_start');
      }
      
      if (formData.reserve_price < formData.starting_price) {
        errors.reserve_price = t('auctions.reserve_price_gte_starting');
      }
      
      if (formData.deposit_required && formData.deposit_amount <= 0) {
        errors.deposit_amount = t('auctions.deposit_amount_required');
      }
      
      if (formData.min_bid_increment <= 0) {
        errors.min_bid_increment = t('auctions.min_bid_increment_required');
      }
      
      formErrors = errors;
      return Object.keys(errors).length === 0;
    }
    
    // Show error alert
    function showErrorAlert(message) {
      alertMessage = message;
      alertType = 'error';
      showAlert = true;
    }
    
    // Show success alert
    function showSuccessAlert(message) {
      alertMessage = message;
      alertType = 'success';
      showAlert = true;
    }
    
    // Form submission
    async function handleSubmit() {
      // Validate form
      if (!validateForm()) {
        return;
      }
      
      isSubmitting = true;
      
      try {
        let result;
        
        if (mode === 'edit') {
          // Update existing auction
          result = await auctionActions.updateAuction(auctionData.id, formData);
        } else {
          // Create new auction
          result = await auctionActions.createAuction(formData);
        }
        
        if (result.success) {
          // Show success message
          showSuccessAlert(
            mode === 'edit' 
              ? t('auctions.update_success') 
              : t('auctions.create_success')
          );
          
          // Emit success event
          dispatch('success', { auction: result.data.auction });
          
          // Handle redirection
          if (redirectAfterSubmit) {
            const auctionId = result.data.auction.id;
            // Redirect to auction detail page after a brief delay
            setTimeout(() => {
              window.location.href = `/auctions/${auctionId}`;
            }, 1500);
          }
        } else {
          // Show error message
          showErrorAlert(result.error || t('general.error_occurred'));
        }
      } catch (error) {
        showErrorAlert(error?.message || t('general.error_occurred'));
      } finally {
        isSubmitting = false;
      }
    }
    
    // Handle cancel
    function handleCancel() {
      dispatch('cancel');
    }
    
    // Initialize component
    onMount(() => {
      // Load available properties
      loadProperties();
      
      // Initialize form data
      formData = initFormData();
    });
  </script>
  
  <!-- Form container -->
  <div class="auction-form">
    <!-- Alert for messages -->
    {#if showAlert}
      <Alert 
        type={alertType} 
        message={alertMessage} 
        dismissible={true}
        on:dismiss={() => showAlert = false}
        class="mb-4"
      />
    {/if}
    
    <!-- Form -->
    <form on:submit|preventDefault={handleSubmit}>
      <!-- Basic Information -->
      <div class="section mb-6">
        <h3 class="text-lg font-semibold mb-4">{t('auctions.basic_information')}</h3>
        
        <!-- Property selection -->
        <div class="mb-4">
          <Dropdown
            label={t('auctions.property')}
            options={propertyOptions}
            bind:value={formData.property_id}
            error={formErrors.property_id}
            placeholder={t('auctions.select_property')}
            disabled={mode === 'edit' || propertiesLoading}
            required
          />
          {#if propertiesLoading}
            <div class="mt-1 text-sm text-gray-500">
              <Loading size="small" /> {t('auctions.loading_properties')}
            </div>
          {/if}
        </div>
        
        <!-- Title -->
        <div class="mb-4">
          <TextInput
            label={t('auctions.title')}
            bind:value={formData.title}
            error={formErrors.title}
            placeholder={t('auctions.title_placeholder')}
            required
          />
        </div>
        
        <!-- Description -->
        <div class="mb-4">
          <TextArea
            label={t('auctions.description')}
            bind:value={formData.description}
            error={formErrors.description}
            placeholder={t('auctions.description_placeholder')}
            rows={4}
          />
        </div>
        
        <!-- Auction Type -->
        <div class="mb-4">
          <Dropdown
            label={t('auctions.auction_type')}
            options={auctionTypeOptions}
            bind:value={formData.auction_type}
            error={formErrors.auction_type}
            required
          />
        </div>
      </div>
      
      <!-- Pricing Information -->
      <div class="section mb-6">
        <h3 class="text-lg font-semibold mb-4">{t('auctions.pricing_information')}</h3>
        
        <!-- Starting Price -->
        <div class="mb-4">
          <NumericInput
            label={t('auctions.starting_price')}
            bind:value={formData.starting_price}
            error={formErrors.starting_price}
            min={0}
            step={100}
            currency={true}
            required
          />
        </div>
        
        <!-- Reserve Price -->
        <div class="mb-4">
          <NumericInput
            label={t('auctions.reserve_price')}
            bind:value={formData.reserve_price}
            error={formErrors.reserve_price}
            min={0}
            step={100}
            currency={true}
            required
          />
        </div>
        
        <!-- Minimum Bid Increment -->
        <div class="mb-4">
          <NumericInput
            label={t('auctions.min_bid_increment')}
            bind:value={formData.min_bid_increment}
            error={formErrors.min_bid_increment}
            min={1}
            step={10}
            currency={true}
            required
          />
        </div>
        
        <!-- Commission Rates -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <NumericInput
            label={t('auctions.buyer_premium_percent')}
            bind:value={formData.buyer_premium_percent}
            error={formErrors.buyer_premium_percent}
            min={0}
            max={100}
            step={0.5}
            percent={true}
          />
          
          <NumericInput
            label={t('auctions.seller_commission_percent')}
            bind:value={formData.seller_commission_percent}
            error={formErrors.seller_commission_percent}
            min={0}
            max={100}
            step={0.5}
            percent={true}
          />
        </div>
        
        <!-- Deposit Requirements -->
        <div class="mb-4">
          <Switch
            label={t('auctions.deposit_required')}
            bind:checked={formData.deposit_required}
          />
        </div>
        
        {#if formData.deposit_required}
          <div class="mb-4">
            <NumericInput
              label={t('auctions.deposit_amount')}
              bind:value={formData.deposit_amount}
              error={formErrors.deposit_amount}
              min={0}
              step={100}
              currency={true}
              required={formData.deposit_required}
            />
          </div>
        {/if}
      </div>
      
      <!-- Dates and Duration -->
      <div class="section mb-6">
        <h3 class="text-lg font-semibold mb-4">{t('auctions.dates_and_duration')}</h3>
        
        <!-- Start Date -->
        <div class="mb-4">
          <DateTimePicker
            label={t('auctions.start_date')}
            bind:value={formData.start_date}
            error={formErrors.start_date}
            min={new Date()}
            required
          />
        </div>
        
        <!-- End Date -->
        <div class="mb-4">
          <DateTimePicker
            label={t('auctions.end_date')}
            bind:value={formData.end_date}
            error={formErrors.end_date}
            min={formData.start_date || new Date()}
            required
          />
        </div>
        
        <!-- Auto-extension Settings -->
        <div class="mb-4">
          <Switch
            label={t('auctions.auto_extend')}
            bind:checked={formData.auto_extend}
          />
          
          {#if formData.auto_extend}
            <div class="mt-2">
              <NumericInput
                label={t('auctions.extension_minutes')}
                bind:value={formData.extension_minutes}
                error={formErrors.extension_minutes}
                min={1}
                max={60}
                step={1}
                required={formData.auto_extend}
              />
            </div>
          {/if}
        </div>
      </div>
      
      <!-- Publication Settings -->
      <div class="section mb-6">
        <h3 class="text-lg font-semibold mb-4">{t('auctions.publication_settings')}</h3>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <!-- Is Private -->
          <div class="mb-4">
            <Switch
              label={t('auctions.is_private')}
              bind:checked={formData.is_private}
            />
            <p class="mt-1 text-sm text-gray-500">{t('auctions.private_description')}</p>
          </div>
          
          <!-- Is Featured -->
          <div class="mb-4">
            <Switch
              label={t('auctions.is_featured')}
              bind:checked={formData.is_featured}
            />
            <p class="mt-1 text-sm text-gray-500">{t('auctions.featured_description')}</p>
          </div>
          
          <!-- Is Published -->
          <div class="mb-4">
            <Switch
              label={t('auctions.is_published')}
              bind:checked={formData.is_published}
            />
            <p class="mt-1 text-sm text-gray-500">{t('auctions.published_description')}</p>
          </div>
        </div>
      </div>
      
      <!-- Terms and Conditions -->
      <div class="section mb-6">
        <h3 class="text-lg font-semibold mb-4">{t('auctions.terms_and_conditions')}</h3>
        
        <div class="mb-4">
          <TextArea
            label={t('auctions.terms_conditions')}
            bind:value={formData.terms_conditions}
            error={formErrors.terms_conditions}
            placeholder={t('auctions.terms_conditions_placeholder')}
            rows={6}
          />
        </div>
      </div>
      
      <!-- Form Actions -->
      <div class="flex justify-end space-x-4">
        {#if cancelable}
          <Button 
            type="button" 
            variant="outline" 
            on:click={handleCancel}
            disabled={isSubmitting}
          >
            {t('general.cancel')}
          </Button>
        {/if}
        
        <Button 
          type="submit" 
          variant="primary" 
          disabled={isSubmitting}
        >
          {#if isSubmitting}
            <Loading size="small" />
          {/if}
          {submitText}
        </Button>
      </div>
    </form>
  </div>
  
  <style>
    .section {
      background-color: var(--color-bg-card, #fff);
      border-radius: 0.5rem;
      padding: 1.5rem;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
  </style>