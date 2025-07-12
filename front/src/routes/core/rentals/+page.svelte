<!-- src/routes/core/rentals/+page.svelte -->
<script>
  import { onMount } from 'svelte';
  import { fade, slide, fly } from 'svelte/transition';
  import { t, locale } from '$lib/i18n';
  import { user } from '$lib/stores/user';
  
  // Core store integration
  import {
    rentalProperties,
    leases,
    rentalLoading,
    rentalError,
    rentalFilters,
    rentalStats,
    filteredRentalProperties,
    rentalActions
  } from '$lib/stores/core.js';
  
  // Components
  import LoadingSkeleton from '$lib/components/ui/LoadingSkeleton.svelte';
  import EmptyState from '$lib/components/ui/EmptyState.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Modal from '$lib/components/ui/Modal.svelte';
  import CoreStatsCard from '$lib/components/core/CoreStatsCard.svelte';

  // State using Svelte 5 runes
  let activeTab = $state('properties');
  let searchQuery = $state('');
  let currentPage = $state(1);
  let totalPages = $state(1);
  let showMobileFilters = $state(false);
  let showCreateModal = $state(false);
  let isRTL = $derived($locale === 'ar');

  // Derived values from core store
  let currentRentalProperties = $derived($rentalProperties || []);
  let currentLeases = $derived($leases || []);
  let loading = $derived($rentalLoading);
  let error = $derived($rentalError);
  let stats = $derived($rentalStats);
  let filters = $derived($rentalFilters);

  // Form data
  let formData = $state({
    property_id: '',
    rental_type: 'long_term',
    monthly_rent: '',
    security_deposit: '',
    bedrooms: 0,
    bathrooms: 1.0,
    furnished: false,
    pets_allowed: false,
    available_date: '',
    property_manager_id: ''
  });

  // Computed values using core store filtering
  let displayedProperties = $derived.by(() => {
    const baseProperties = $filteredRentalProperties || [];
    return baseProperties.filter(property => {
      return !searchQuery || 
        property.property_info?.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        property.property_info?.address?.toLowerCase().includes(searchQuery.toLowerCase());
    });
  });

  let displayedLeases = $derived.by(() => {
    return currentLeases.filter(lease => {
      return !searchQuery || 
        lease.rental_property_info?.property_title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        lease.tenant_info?.full_name?.toLowerCase().includes(searchQuery.toLowerCase());
    });
  });

  onMount(async () => {
    await rentalActions.loadAll();
  });

  // Update filters in the core store
  function updateFilters(newFilters) {
    rentalFilters.update(current => ({ ...current, ...newFilters }));
  }

  async function handleCreateRentalProperty(event) {
    event.preventDefault();
    try {
      // For now, just log the form data since we don't have backend integration yet
      console.log('Would create rental property:', formData);
      
      showCreateModal = false;
      
      // Reset form
      formData = {
        property_id: '',
        rental_type: 'long_term',
        monthly_rent: '',
        security_deposit: '',
        bedrooms: 0,
        bathrooms: 1.0,
        furnished: false,
        pets_allowed: false,
        available_date: '',
        property_manager_id: ''
      };
    } catch (err) {
      console.error('Failed to create rental property:', err);
    }
  }

  function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount || 0);
  }

  function formatDate(date) {
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    }).format(new Date(date));
  }

  function getLeaseStatusColor(status) {
    const colors = {
      active: 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400',
      expired: 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400',
      terminated: 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400'
    };
    return colors[status] || 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400';
  }

  function getOccupancyRate() {
    if (stats.totalProperties === 0) return 0;
    return ((stats.occupiedProperties / stats.totalProperties) * 100).toFixed(1);
  }
</script>

<svelte:head>
  <title>{$t('core.rentals.title')} | {$t('app.name')}</title>
</svelte:head>

<div class="space-y-6">
  <!-- Header Section -->
  <div class="bg-white dark:bg-gray-800 shadow rounded-lg" in:fade={{ duration: 300 }}>
    <div class="px-4 py-5 sm:p-6">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div class="flex-1 min-w-0">
          <h1 class="text-2xl font-bold leading-7 text-gray-900 dark:text-white sm:text-3xl sm:truncate">
            {$t('core.rentals.title')}
          </h1>
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
            {$t('core.rentals.subtitle')}
          </p>
        </div>
        <div class="mt-4 flex items-center space-x-3 sm:mt-0 sm:ml-4">
          <Button
            href="/core/rentals/create"
            variant="outline"
            size="sm"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            {$t('core.rentals.addProperty')}
          </Button>
          <Button
            onclick={() => showCreateModal = true}
            size="sm"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            {$t('core.rentals.convertToRental')}
          </Button>
        </div>
      </div>
    </div>
  </div>

  <!-- Stats Grid -->
  {#if !loading}
    <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6" in:slide={{ duration: 400 }}>
      <CoreStatsCard
        title={$t('core.rentals.totalProperties')}
        value={stats.totalProperties.toString()}
        icon="home"
        color="blue"
        href="/core/rentals?tab=properties"
      />
      
      <CoreStatsCard
        title={$t('core.rentals.occupied')}
        value={stats.occupiedProperties.toString()}
        subtitle={$t('core.rentals.occupancyPercent', { rate: getOccupancyRate() })}
        icon="check-circle"
        color="green"
      />
      
      <CoreStatsCard
        title={$t('core.rentals.vacant')}
        value={stats.vacantProperties.toString()}
        icon="exclamation-triangle"
        color="yellow"
      />
      
      <CoreStatsCard
        title={$t('core.rentals.activeLeases')}
        value={stats.activeLeases.toString()}
        icon="document-text"
        color="purple"
        href="/core/rentals?tab=leases"
      />
      
      <CoreStatsCard
        title={$t('core.rentals.expiringSoon')}
        value={stats.expiringLeases.toString()}
        subtitle={$t('core.rentals.within30Days')}
        icon="clock"
        color="red"
      />
      
      <CoreStatsCard
        title={$t('core.rentals.monthlyIncome')}
        value={formatCurrency(stats.monthlyIncome)}
        icon="currency-dollar"
        color="green"
        trend="up"
        change="+5.2%"
      />
    </div>
  {:else}
    <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
      {#each Array(6) as _}
        <LoadingSkeleton class="h-24" />
      {/each}
    </div>
  {/if}

  <!-- Tabs -->
  <div class="bg-white dark:bg-gray-800 shadow rounded-lg" in:fade={{ delay: 100 }}>
    <div class="border-b border-gray-200 dark:border-gray-700">
      <nav class="-mb-px flex space-x-8 px-6" aria-label="Tabs">
        <button
          onclick={() => activeTab = 'properties'}
          class={`${
            activeTab === 'properties'
              ? 'border-primary-500 text-primary-600 dark:text-primary-400'
              : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
          } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center transition-colors duration-200`}
        >
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="m2.25 12 8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25" />
          </svg>
          {$t('core.rentals.rentalPropertiesCount', { count: stats.totalProperties })}
        </button>
        <button
          onclick={() => activeTab = 'leases'}
          class={`${
            activeTab === 'leases'
              ? 'border-primary-500 text-primary-600 dark:text-primary-400'
              : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
          } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center transition-colors duration-200`}
        >
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
          </svg>
          {$t('core.rentals.leaseAgreementsCount', { count: stats.activeLeases })}
        </button>
      </nav>
    </div>

    <!-- Filters and Search -->
    <div class="p-6 border-b border-gray-200 dark:border-gray-700">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-4 sm:space-y-0 sm:space-x-4">
        <div class="flex-1 max-w-lg">
          <div class="relative">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <input
              type="text"
              bind:value={searchQuery}
              placeholder={$t('core.common.searchPlaceholder', { type: activeTab === 'properties' ? $t('core.rentals.properties') : $t('core.rentals.leases') })}
              class="block w-full pl-10 pr-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md leading-5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-primary-500 focus:border-primary-500 text-sm"
            />
          </div>
        </div>
        
        <div class="flex items-center space-x-3">
          {#if activeTab === 'properties'}
            <!-- Rental Type Filter -->
            <div class="relative">
              <select
                value={filters.rental_type}
                onchange={(e) => updateFilters({ rental_type: e.target.value })}
                class="block w-40 pl-3 pr-10 py-2 text-base border border-gray-300 dark:border-gray-600 focus:outline-none focus:ring-primary-500 focus:border-primary-500 text-sm rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="">{$t('core.rentals.filters.allTypes')}</option>
                <option value="long_term">{$t('core.rentals.rentalTypes.longTerm')}</option>
                <option value="short_term">{$t('core.rentals.rentalTypes.shortTerm')}</option>
                <option value="vacation">{$t('core.rentals.rentalTypes.vacation')}</option>
                <option value="commercial">{$t('core.rentals.rentalTypes.commercial')}</option>
              </select>
            </div>

            <!-- Occupancy Filter -->
            <div class="relative">
              <select
                value={filters.is_currently_rented}
                onchange={(e) => updateFilters({ is_currently_rented: e.target.value })}
                class="block w-32 pl-3 pr-10 py-2 text-base border border-gray-300 dark:border-gray-600 focus:outline-none focus:ring-primary-500 focus:border-primary-500 text-sm rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="">{$t('core.rentals.filters.allStatus')}</option>
                <option value="true">{$t('core.rentals.occupied')}</option>
                <option value="false">{$t('core.rentals.vacant')}</option>
              </select>
            </div>
          {/if}

          <!-- Sort Filter -->
          <div class="relative">
            <select
              value={filters.sort}
              onchange={(e) => updateFilters({ sort: e.target.value })}
              class="block w-32 pl-3 pr-10 py-2 text-base border border-gray-300 dark:border-gray-600 focus:outline-none focus:ring-primary-500 focus:border-primary-500 text-sm rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="newest">{$t('core.rentals.sort.newest')}</option>
              <option value="oldest">{$t('core.rentals.sort.oldest')}</option>
              <option value="rent_high">{$t('core.rentals.sort.rentHigh')}</option>
              <option value="rent_low">{$t('core.rentals.sort.rentLow')}</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- Content -->
    <div class="p-6">
      {#if loading}
        <div class="space-y-4">
          {#each Array(5) as _}
            <LoadingSkeleton class="h-32" />
          {/each}
        </div>
      {:else if error}
        <EmptyState
          title={$t('core.common.failedToLoad')}
          description={error}
          actionText={$t('core.common.tryAgain')}
          onAction={() => rentalActions.loadAll()}
        />
      {:else if (activeTab === 'properties' ? displayedProperties : displayedLeases).length === 0}
        <EmptyState
          title={$t('core.rentals.noItemsFound', { type: activeTab === 'properties' ? $t('core.rentals.properties') : $t('core.rentals.leases') })}
          description={$t('core.rentals.createFirstItem', { type: activeTab === 'properties' ? $t('core.rentals.property') : $t('core.rentals.lease') })}
          actionText={$t('core.common.add') + ' ' + (activeTab === 'properties' ? $t('core.rentals.property') : $t('core.rentals.lease'))}
          onAction={() => showCreateModal = true}
        />
      {:else}
        <div class="space-y-6" in:slide={{ duration: 300 }}>
          {#if activeTab === 'properties'}
            <!-- Properties Grid -->
            <div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
              {#each displayedProperties as property, index}
                <div
                  class="bg-gray-50 dark:bg-gray-700 rounded-lg p-6 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors duration-200"
                  in:fly={{ y: 20, duration: 300, delay: index * 50 }}
                >
                  <div class="flex items-start justify-between mb-4">
                    <div class="flex-1">
                      <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-1">
                        {property.property_info?.title || $t('core.rentals.untitledProperty')}
                      </h3>
                      <p class="text-sm text-gray-500 dark:text-gray-400">
                        {property.property_info?.address || $t('core.rentals.noAddress')}
                      </p>
                    </div>
                    <span class={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      property.is_currently_rented 
                        ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400'
                        : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400'
                    }`}>
                      {property.is_currently_rented ? $t('core.rentals.occupied') : $t('core.rentals.vacant')}
                    </span>
                  </div>

                  <div class="space-y-3">
                    <div class="flex justify-between items-center">
                      <span class="text-sm text-gray-500 dark:text-gray-400">{$t('core.rentals.monthlyRent')}</span>
                      <span class="text-lg font-semibold text-gray-900 dark:text-white">
                        {formatCurrency(property.monthly_rent)}
                      </span>
                    </div>

                    <div class="flex justify-between items-center">
                      <span class="text-sm text-gray-500 dark:text-gray-400">{$t('core.rentals.securityDeposit')}</span>
                      <span class="text-sm font-medium text-gray-900 dark:text-white">
                        {formatCurrency(property.security_deposit)}
                      </span>
                    </div>

                    <div class="flex justify-between items-center">
                      <span class="text-sm text-gray-500 dark:text-gray-400">{$t('core.rentals.type')}</span>
                      <span class="text-sm text-gray-900 dark:text-white">
                        {property.rental_type_display || property.rental_type}
                      </span>
                    </div>

                    <div class="flex justify-between items-center">
                      <span class="text-sm text-gray-500 dark:text-gray-400">{$t('core.rentals.bedsBaths')}</span>
                      <span class="text-sm text-gray-900 dark:text-white">
                        {property.bedrooms}bd / {property.bathrooms}ba
                      </span>
                    </div>

                    {#if property.furnished || property.pets_allowed}
                      <div class="flex flex-wrap gap-1 mt-2">
                        {#if property.furnished}
                          <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400">
                            {$t('core.rentals.furnished')}
                          </span>
                        {/if}
                        {#if property.pets_allowed}
                          <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400">
                            {$t('core.rentals.petsOK')}
                          </span>
                        {/if}
                      </div>
                    {/if}

                    {#if property.current_lease}
                      <div class="border-t border-gray-200 dark:border-gray-600 pt-3 mt-3">
                        <div class="text-sm text-gray-500 dark:text-gray-400 mb-1">{$t('core.rentals.currentTenant')}</div>
                        <div class="text-sm font-medium text-gray-900 dark:text-white">
                          {property.current_lease.tenant_name}
                        </div>
                        <div class="text-xs text-gray-500 dark:text-gray-400">
                          {$t('core.rentals.leaseExpiresIn', { days: property.current_lease.days_remaining })}
                        </div>
                      </div>
                    {/if}
                  </div>

                  <div class="flex items-center justify-between mt-4 pt-4 border-t border-gray-200 dark:border-gray-600">
                    <div class="text-xs text-gray-500 dark:text-gray-400">
                      {property.monthly_yield ? $t('core.rentals.yieldPercent', { yield: property.monthly_yield.toFixed(2) }) : ''}
                    </div>
                    <div class="flex space-x-2">
                      <Button size="sm" variant="outline">
                        {$t('core.common.edit')}
                      </Button>
                      <Button size="sm" variant="outline">
                        {$t('core.common.view')}
                      </Button>
                    </div>
                  </div>
                </div>
              {/each}
            </div>
          {:else}
            <!-- Leases List -->
            <div class="space-y-4">
              {#each displayedLeases as lease, index}
                <div
                  class="bg-gray-50 dark:bg-gray-700 rounded-lg p-6 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors duration-200"
                  in:fly={{ y: 20, duration: 300, delay: index * 50 }}
                >
                  <div class="flex items-center justify-between">
                    <div class="flex items-start space-x-4">
                      <div class="flex-shrink-0">
                        <div class="w-12 h-12 bg-purple-100 dark:bg-purple-900/20 rounded-lg flex items-center justify-center">
                          <svg class="w-6 h-6 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                          </svg>
                        </div>
                      </div>
                      <div class="flex-1 min-w-0">
                        <div class="flex items-center space-x-2">
                          <h3 class="text-lg font-semibold text-gray-900 dark:text-white truncate">
                            {lease.lease_number}
                          </h3>
                          <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {getLeaseStatusColor(lease.status)}">
                            {lease.status_display || lease.status}
                          </span>
                        </div>
                        <div class="mt-1 text-sm text-gray-500 dark:text-gray-400 space-y-1">
                          <div class="flex items-center space-x-4">
                            <span class="font-medium">{$t('core.rentals.property')}:</span>
                            <span>{lease.rental_property_info?.property_title}</span>
                          </div>
                          <div class="flex items-center space-x-4">
                            <span class="font-medium">{$t('core.rentals.tenant')}:</span>
                            <span>{lease.tenant_info?.full_name || lease.tenant_info?.email}</span>
                          </div>
                          <div class="flex items-center space-x-4">
                            <span>{$t('core.rentals.term')}: {formatDate(lease.start_date)} - {formatDate(lease.end_date)}</span>
                            {#if lease.days_remaining > 0}
                              <span class="text-yellow-600 dark:text-yellow-400">
                                {$t('core.rentals.daysRemaining', { days: lease.days_remaining })}
                              </span>
                            {/if}
                          </div>
                        </div>
                      </div>
                    </div>
                    <div class="flex items-center space-x-6">
                      <div class="text-right">
                        <div class="text-xl font-bold text-gray-900 dark:text-white">
                          {formatCurrency(lease.monthly_rent)}
                        </div>
                        <div class="text-sm text-gray-500 dark:text-gray-400">
                          {$t('core.rentals.perMonth')}
                        </div>
                      </div>
                      <div class="flex items-center space-x-2">
                        <Button size="sm" variant="outline">
                          {$t('core.common.edit')}
                        </Button>
                        <Button size="sm" variant="outline">
                          {$t('core.common.view')}
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>
              {/each}
            </div>
          {/if}
        </div>
      {/if}
    </div>
  </div>
</div>

<!-- Create Rental Property Modal -->
<Modal bind:open={showCreateModal} title={$t('core.rentals.convertPropertyToRental')}>
  <form onsubmit={handleCreateRentalProperty} class="space-y-4">
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
      <div class="sm:col-span-2">
        <label for="property_id" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
          {$t('core.rentals.property')}
        </label>
        <select
          id="property_id"
          bind:value={formData.property_id}
          required
          class="mt-1 block w-full border border-gray-300 dark:border-gray-600 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
        >
          <option value="">{$t('core.rentals.selectProperty')}</option>
          <!-- Properties would be loaded dynamically -->
        </select>
      </div>
      
      <div>
        <label for="rental_type" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
          {$t('core.rentals.rentalType')}
        </label>
        <select
          id="rental_type"
          bind:value={formData.rental_type}
          required
          class="mt-1 block w-full border border-gray-300 dark:border-gray-600 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
        >
          <option value="long_term">{$t('core.rentals.rentalTypes.longTermRental')}</option>
          <option value="short_term">{$t('core.rentals.rentalTypes.shortTermRental')}</option>
          <option value="vacation">{$t('core.rentals.rentalTypes.vacationRental')}</option>
          <option value="commercial">{$t('core.rentals.rentalTypes.commercialRental')}</option>
        </select>
      </div>

      <div>
        <label for="monthly_rent" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
          {$t('core.rentals.monthlyRent')}
        </label>
        <input
          type="number"
          id="monthly_rent"
          bind:value={formData.monthly_rent}
          required
          step="0.01"
          min="0"
          class="mt-1 block w-full border border-gray-300 dark:border-gray-600 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
        />
      </div>

      <div>
        <label for="security_deposit" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
          {$t('core.rentals.securityDeposit')}
        </label>
        <input
          type="number"
          id="security_deposit"
          bind:value={formData.security_deposit}
          required
          step="0.01"
          min="0"
          class="mt-1 block w-full border border-gray-300 dark:border-gray-600 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
        />
      </div>

      <div>
        <label for="bedrooms" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
          {$t('core.rentals.bedrooms')}
        </label>
        <input
          type="number"
          id="bedrooms"
          bind:value={formData.bedrooms}
          min="0"
          class="mt-1 block w-full border border-gray-300 dark:border-gray-600 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
        />
      </div>

      <div>
        <label for="bathrooms" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
          {$t('core.rentals.bathrooms')}
        </label>
        <input
          type="number"
          id="bathrooms"
          bind:value={formData.bathrooms}
          step="0.5"
          min="0"
          class="mt-1 block w-full border border-gray-300 dark:border-gray-600 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
        />
      </div>

      <div>
        <label for="available_date" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
          {$t('core.rentals.availableDate')}
        </label>
        <input
          type="date"
          id="available_date"
          bind:value={formData.available_date}
          class="mt-1 block w-full border border-gray-300 dark:border-gray-600 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
        />
      </div>

      <div class="sm:col-span-2">
        <div class="flex items-center space-x-6">
          <div class="flex items-center">
            <input
              type="checkbox"
              id="furnished"
              bind:checked={formData.furnished}
              class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
            />
            <label for="furnished" class="ml-2 block text-sm text-gray-900 dark:text-white">
              {$t('core.rentals.furnished')}
            </label>
          </div>
          <div class="flex items-center">
            <input
              type="checkbox"
              id="pets_allowed"
              bind:checked={formData.pets_allowed}
              class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
            />
            <label for="pets_allowed" class="ml-2 block text-sm text-gray-900 dark:text-white">
              {$t('core.rentals.petsAllowed')}
            </label>
          </div>
        </div>
      </div>
    </div>

    <div class="flex justify-end space-x-3 pt-4">
      <Button
        type="button"
        variant="outline"
        onclick={() => showCreateModal = false}
      >
        {$t('core.common.cancel')}
      </Button>
      <Button type="submit">
        {$t('core.rentals.createRentalProperty')}
      </Button>
    </div>
  </form>
</Modal>