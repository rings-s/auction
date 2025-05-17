<!-- src/lib/components/AuctionForm.svelte -->
<script>
    import { onMount } from 'svelte';
    import { t } from '$lib/i18n/i18n';
    import { fetchProperties } from '$lib/api/property';
    import { user } from '$lib/stores/user';
  
    export let auction = {
      title: '',
      slug: '',
      auction_type: 'reserve',
      status: 'draft',
      description: '',
      start_date: '',
      end_date: '',
      registration_deadline: '',
      related_property: null,
      starting_bid: '',
      minimum_increment: 100,
      is_published: false,
      is_featured: false,
      terms_conditions: ''
    };
  
    export let activeTab = 'basic';
    export let loading = false;
    export let error = '';
  
    let properties = [];
    let loadingProperties = true;
    let propertiesError = '';
  
    onMount(async () => {
      await loadUserProperties();
      
      // Initialize dates
      const now = new Date();
      const tomorrow = new Date(now);
      tomorrow.setDate(tomorrow.getDate() + 1);
      
      const nextWeek = new Date(now);
      nextWeek.setDate(nextWeek.getDate() + 7);
      
      if (!auction.start_date) {
        auction.start_date = tomorrow.toISOString().slice(0, 16);
      }
      
      if (!auction.end_date) {
        auction.end_date = nextWeek.toISOString().slice(0, 16);
      }
    });
  
    async function loadUserProperties() {
      try {
        loadingProperties = true;
        propertiesError = '';
        
        // Fetch properties owned by current user
        const response = await fetchProperties({ owner: 'current' });
        properties = response.results || [];
        
      } catch (err) {
        console.error('Error loading properties:', err);
        propertiesError = err.message || $t('error.fetchFailed');
      } finally {
        loadingProperties = false;
      }
    }
  
    function formatDateTime(date) {
      return date ? new Date(date).toISOString().slice(0, 16) : '';
    }
  
    function setTab(tab) {
      activeTab = tab;
    }
  
    // Ensure dates are properly formatted before submission
    export function prepareDataForSubmission() {
      const preparedData = { ...auction };
      
      // Ensure dates are in proper ISO format
      if (preparedData.start_date) {
        preparedData.start_date = new Date(preparedData.start_date).toISOString();
      }
      
      if (preparedData.end_date) {
        preparedData.end_date = new Date(preparedData.end_date).toISOString();
      }
      
      if (preparedData.registration_deadline) {
        preparedData.registration_deadline = new Date(preparedData.registration_deadline).toISOString();
      }
      
      return preparedData;
    }
  </script>
  
  <div class="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-lg">
    <!-- Tabs -->
    <div class="border-b border-gray-200 dark:border-gray-700">
      <nav class="-mb-px flex space-x-8 overflow-x-auto" aria-label="Tabs">
        <button
          on:click={() => setTab('basic')}
          class={`${
            activeTab === 'basic'
              ? 'border-primary-500 text-primary-600 dark:text-primary-400'
              : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
          } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
        >
          {$t('auction.basicInfo')}
        </button>
        <button
          on:click={() => setTab('scheduling')}
          class={`${
            activeTab === 'scheduling'
              ? 'border-primary-500 text-primary-600 dark:text-primary-400'
              : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
          } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
        >
          {$t('auction.scheduling')}
        </button>
        <button
          on:click={() => setTab('financial')}
          class={`${
            activeTab === 'financial'
              ? 'border-primary-500 text-primary-600 dark:text-primary-400'
              : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
          } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
        >
          {$t('auction.financial')}
        </button>
        <button
          on:click={() => setTab('property')}
          class={`${
            activeTab === 'property'
              ? 'border-primary-500 text-primary-600 dark:text-primary-400'
              : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
          } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
        >
          {$t('auction.selectProperty')}
        </button>
        <button
          on:click={() => setTab('terms')}
          class={`${
            activeTab === 'terms'
              ? 'border-primary-500 text-primary-600 dark:text-primary-400'
              : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
          } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
        >
          {$t('auction.termsConditions')}
        </button>
      </nav>
    </div>
  
    <div class="px-4 py-5 sm:p-6">
      {#if error}
        <div class="mb-4 rounded-md bg-red-50 dark:bg-red-900/30 p-4">
          <div class="flex">
            <div class="flex-shrink-0">
              <svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
              </svg>
            </div>
            <div class="ml-3">
              <h3 class="text-sm font-medium text-red-800 dark:text-red-200">
                {error}
              </h3>
            </div>
          </div>
        </div>
      {/if}
  
      <!-- Basic Information -->
      {#if activeTab === 'basic'}
        <div class="space-y-6">
          <div>
            <h3 class="text-lg font-medium leading-6 text-gray-900 dark:text-white">{$t('auction.basicInfo')}</h3>
            <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">{$t('auction.basicInfoDesc')}</p>
          </div>
  
          <div class="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
            <!-- Auction Title -->
            <div class="sm:col-span-4">
              <label for="title" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                {$t('auction.title')}
              </label>
              <div class="mt-1">
                <input
                  type="text"
                  id="title"
                  bind:value={auction.title}
                  required
                  class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                />
              </div>
            </div>
  
            <!-- Auction Type -->
            <div class="sm:col-span-3">
              <label for="auction_type" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                {$t('auction.auctionType')}
              </label>
              <div class="mt-1">
                <select
                  id="auction_type"
                  bind:value={auction.auction_type}
                  class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                >
                  <option value="sealed">{$t('auction.typeSealed')}</option>
                  <option value="reserve">{$t('auction.typeReserve')}</option>
                  <option value="no_reserve">{$t('auction.typeNoReserve')}</option>
                </select>
                <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
                  {#if auction.auction_type === 'sealed'}
                    {$t('auction.typeSealedDesc')}
                  {:else if auction.auction_type === 'reserve'}
                    {$t('auction.typeReserveDesc')}
                  {:else}
                    {$t('auction.typeNoReserveDesc')}
                  {/if}
                </p>
              </div>
            </div>
  
            <!-- Status -->
            <div class="sm:col-span-3">
              <label for="status" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                {$t('auction.status')}
              </label>
              <div class="mt-1">
                <select
                  id="status"
                  bind:value={auction.status}
                  class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                >
                  <option value="draft">{$t('auction.statusDraft')}</option>
                  <option value="scheduled">{$t('auction.statusScheduled')}</option>
                  <option value="live">{$t('auction.statusLive')}</option>
                </select>
              </div>
            </div>
  
            <!-- Description -->
            <div class="sm:col-span-6">
              <label for="description" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                {$t('auction.description')}
              </label>
              <div class="mt-1">
                <textarea
                  id="description"
                  bind:value={auction.description}
                  rows="5"
                  class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                ></textarea>
              </div>
            </div>
  
            <!-- Publishing Options -->
            <div class="sm:col-span-6">
              <fieldset>
                <legend class="text-sm font-medium text-gray-700 dark:text-gray-300">{$t('auction.publishingOptions')}</legend>
                <div class="mt-2 space-y-4">
                  <div class="relative flex items-start">
                    <div class="flex items-center h-5">
                      <input
                        id="is_published"
                        type="checkbox"
                        bind:checked={auction.is_published}
                        class="focus:ring-primary-500 h-4 w-4 text-primary-600 border-gray-300 dark:border-gray-700 rounded dark:bg-gray-800"
                      />
                    </div>
                    <div class="ml-3 text-sm">
                      <label for="is_published" class="font-medium text-gray-700 dark:text-gray-300">{$t('auction.published')}</label>
                      <p class="text-gray-500 dark:text-gray-400">{$t('auction.publishedHelp')}</p>
                    </div>
                  </div>
                  <div class="relative flex items-start">
                    <div class="flex items-center h-5">
                      <input
                        id="is_featured"
                        type="checkbox"
                        bind:checked={auction.is_featured}
                        class="focus:ring-primary-500 h-4 w-4 text-primary-600 border-gray-300 dark:border-gray-700 rounded dark:bg-gray-800"
                      />
                    </div>
                    <div class="ml-3 text-sm">
                      <label for="is_featured" class="font-medium text-gray-700 dark:text-gray-300">{$t('auction.featured')}</label>
                      <p class="text-gray-500 dark:text-gray-400">{$t('auction.featuredHelp')}</p>
                    </div>
                  </div>
                </div>
              </fieldset>
            </div>
          </div>
        </div>
      {/if}
  
      <!-- Scheduling -->
      {#if activeTab === 'scheduling'}
        <div class="space-y-6">
          <div>
            <h3 class="text-lg font-medium leading-6 text-gray-900 dark:text-white">{$t('auction.scheduling')}</h3>
            <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">{$t('auction.schedulingDesc')}</p>
          </div>
  
          <div class="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
            <!-- Start Date -->
            <div class="sm:col-span-3">
              <label for="start_date" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                {$t('auction.startDate')}
              </label>
              <div class="mt-1">
                <input
                  type="datetime-local"
                  id="start_date"
                  bind:value={auction.start_date}
                  required
                  class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                />
              </div>
            </div>
  
            <!-- End Date -->
            <div class="sm:col-span-3">
              <label for="end_date" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                {$t('auction.endDate')}
              </label>
              <div class="mt-1">
                <input
                  type="datetime-local"
                  id="end_date"
                  bind:value={auction.end_date}
                  required
                  class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                />
              </div>
            </div>
  
            <!-- Registration Deadline -->
            <div class="sm:col-span-3">
              <label for="registration_deadline" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                {$t('auction.registrationDeadline')}
              </label>
              <div class="mt-1">
                <input
                  type="datetime-local"
                  id="registration_deadline"
                  bind:value={auction.registration_deadline}
                  class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                />
                <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">{$t('auction.registrationDeadlineHelp')}</p>
              </div>
            </div>
          </div>
        </div>
      {/if}
  
      <!-- Financial Information -->
      {#if activeTab === 'financial'}
        <div class="space-y-6">
          <div>
            <h3 class="text-lg font-medium leading-6 text-gray-900 dark:text-white">{$t('auction.financial')}</h3>
            <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">{$t('auction.financialDesc')}</p>
          </div>
  
          <div class="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
            <!-- Starting Bid -->
            <div class="sm:col-span-3">
              <label for="starting_bid" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                {$t('auction.startingBid')} ($)
              </label>
              <div class="mt-1 relative rounded-md shadow-sm">
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <span class="text-gray-500 dark:text-gray-400 sm:text-sm">$</span>
                </div>
                <input
                  type="number"
                  id="starting_bid"
                  bind:value={auction.starting_bid}
                  min="0"
                  step="0.01"
                  required
                  class="focus:ring-primary-500 focus:border-primary-500 block w-full pl-7 pr-12 sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                  placeholder="0.00"
                />
                <div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                  <span class="text-gray-500 dark:text-gray-400 sm:text-sm">USD</span>
                </div>
              </div>
            </div>
  
            <!-- Minimum Increment -->
            <div class="sm:col-span-3">
              <label for="minimum_increment" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                {$t('auction.minimumIncrement')} ($)
              </label>
              <div class="mt-1 relative rounded-md shadow-sm">
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <span class="text-gray-500 dark:text-gray-400 sm:text-sm">$</span>
                </div>
                <input
                  type="number"
                  id="minimum_increment"
                  bind:value={auction.minimum_increment}
                  min="0"
                  step="0.01"
                  required
                  class="focus:ring-primary-500 focus:border-primary-500 block w-full pl-7 pr-12 sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                  placeholder="0.00"
                />
                <div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                  <span class="text-gray-500 dark:text-gray-400 sm:text-sm">USD</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      {/if}
  
      <!-- Property Selection -->
      {#if activeTab === 'property'}
        <div class="space-y-6">
          <div>
            <h3 class="text-lg font-medium leading-6 text-gray-900 dark:text-white">{$t('auction.selectProperty')}</h3>
            <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">{$t('auction.selectPropertyDesc')}</p>
          </div>
  
          {#if loadingProperties}
            <div class="flex justify-center py-12">
              <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
            </div>
          {:else if propertiesError}
            <div class="text-center py-12 bg-red-50 dark:bg-red-900/30 rounded-lg">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-red-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <h3 class="text-lg font-medium text-red-800 dark:text-red-200 mb-1">{propertiesError}</h3>
              <button
                type="button"
                on:click={loadUserProperties}
                class="mt-3 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                {$t('auction.tryAgain')}
              </button>
            </div>
          {:else if properties.length === 0}
            <div class="text-center py-12 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-gray-400 dark:text-gray-500 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
              <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-1">{$t('auction.noProperties')}</h3>
              <p class="text-gray-500 dark:text-gray-400 mb-4">{$t('auction.noPropertiesDesc')}</p>
              <a 
                href="/properties/create" 
                class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                {$t('property.createProperty')}
              </a>
            </div>
          {:else}
            <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {#each properties as property}
                <div 
                  class={`border rounded-lg overflow-hidden hover:shadow-md transition-shadow cursor-pointer ${auction.related_property === property.id ? 'border-primary-500 ring-2 ring-primary-500' : 'border-gray-200 dark:border-gray-700'}`}
                  on:click={() => auction.related_property = property.id}
                  on:keypress={() => auction.related_property = property.id}
                  role="button"
                  tabindex="0"
                >
                  <div class="h-40 bg-gray-200 dark:bg-gray-700">
                    {#if property.main_image}
                      <img src={property.main_image} alt={property.title} class="w-full h-full object-cover" />
                    {:else}
                      <div class="flex items-center justify-center h-full text-gray-400 dark:text-gray-500">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
                        </svg>
                      </div>
                    {/if}
                  </div>
                  <div class="p-4">
                    <h3 class="font-medium text-gray-900 dark:text-white">{property.title}</h3>
                    <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">{property.address}, {property.city}</p>
                    <div class="flex justify-between items-baseline mt-2">
                      <span class="inline-block bg-gray-100 dark:bg-gray-700 rounded-full px-3 py-1 text-xs font-semibold text-gray-700 dark:text-gray-300">
                        {property.property_type_display}
                      </span>
                      <span class="text-lg font-bold text-gray-900 dark:text-white">${property.market_value.toLocaleString()}</span>
                    </div>
                  </div>
                </div>
              {/each}
            </div>
          {/if}
        </div>
      {/if}
  
      <!-- Terms & Conditions -->
      {#if activeTab === 'terms'}
        <div class="space-y-6">
          <div>
            <h3 class="text-lg font-medium leading-6 text-gray-900 dark:text-white">{$t('auction.termsConditions')}</h3>
            <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">{$t('auction.termsConditionsDesc')}</p>
          </div>
  
          <div>
            <label for="terms_conditions" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
              {$t('auction.termsConditionsText')}
            </label>
            <div class="mt-1">
              <textarea
                id="terms_conditions"
                bind:value={auction.terms_conditions}
                rows="10"
                class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
              ></textarea>
            </div>
            <p class="mt-2 text-xs text-gray-500 dark:text-gray-400">{$t('auction.termsConditionsHelp')}</p>
          </div>
        </div>
      {/if}
    </div>
  </div>