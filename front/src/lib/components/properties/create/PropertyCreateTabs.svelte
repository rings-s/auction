<!-- src/lib/components/properties/create/PropertyCreateTabs.svelte -->
<script>
    import { t, locale } from '$lib/i18n';
    import { fade } from 'svelte/transition';
    import LocationPicker from '$lib/components/properties/LocationPicker.svelte';
    import MediaUploader from '$lib/components/shared/MediaUploader.svelte';
    import RoomManager from '$lib/components/properties/RoomManager.svelte';
    import TagSelector from '$lib/components/ui/TagSelector.svelte';
    
    export let currentStep;
    export let propertyData;
    export let rooms;
    export let mediaFiles;
    export let validationErrors;
    export let availableFeatures;
    export let availableAmenities;
    export let availableRoomFeatures;
    export let propertyTypeOptions;
    export let buildingTypeOptions;
    export let onLocationChange;
    export let onFeaturesChange;
    export let onAmenitiesChange;
    export let onRoomsChange;
    export let onMediaChange;
    
    // Constants
    const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
  </script>
  
  <!-- Tab Content Container -->
  <div class="bg-white dark:bg-gray-800 rounded-b-xl shadow-md overflow-hidden">
    <!-- Step 1: Basic Information -->
    <div 
      id="tab-basic-info"
      class="p-8"
      style="display: {currentStep === 1 ? 'block' : 'none'}"
      transition:fade={{ duration: 200 }}
    >
      <div class="space-y-8">
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
    </div>
    
    <!-- Step 2: Location Information -->
    <div 
      id="tab-location"
      class="p-8"
      style="display: {currentStep === 2 ? 'block' : 'none'}"
      transition:fade={{ duration: 200 }}
    >
      <div class="space-y-8">
        <LocationPicker
          bind:address={propertyData.address}
          bind:city={propertyData.city}
          bind:state={propertyData.state}
          bind:postalCode={propertyData.postal_code}
          bind:country={propertyData.country}
          bind:latitude={propertyData.latitude}
          bind:longitude={propertyData.longitude}
          on:locationChange={onLocationChange}
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
    </div>
    
    <!-- Step 3: Property Details -->
    <div 
      id="tab-details"
      class="p-8"
      style="display: {currentStep === 3 ? 'block' : 'none'}"
      transition:fade={{ duration: 200 }}
    >
      <div class="space-y-8">
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
          
          <!-- Features -->
          <div class="sm:col-span-6 mt-2">
            <TagSelector
              title={$t('property.features')}
              tags={availableFeatures}
              selectedTags={propertyData.features}
              on:change={onFeaturesChange}
              variant="pill"
            />
          </div>
          
          <!-- Amenities -->
          <div class="sm:col-span-6 mt-2">
            <TagSelector
              title={$t('property.amenities')}
              tags={availableAmenities}
              selectedTags={propertyData.amenities}
              on:change={onAmenitiesChange}
              variant="pill"
            />
          </div>
          
          <!-- Rooms -->
          <div class="sm:col-span-6 mt-4">
            <div class="bg-gray-50 dark:bg-gray-700 p-6 rounded-lg shadow-inner">
              <RoomManager
                bind:rooms
                availableFeatures={availableRoomFeatures}
                on:change={onRoomsChange}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Step 4: Financial Information & Media Upload -->
    <div 
      id="tab-financial"
      class="p-8"
      style="display: {currentStep === 4 ? 'block' : 'none'}"
      transition:fade={{ duration: 200 }}
    >
      <div class="space-y-8">
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
          
          <!-- Publishing Options -->
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
                <svg class="w-5 h-5 mr-2 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
                  on:change={onMediaChange}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>