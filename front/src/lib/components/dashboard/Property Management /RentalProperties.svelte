<!-- src/lib/components/dashboard/RentalManagement.svelte -->
<script>
    import { onMount } from 'svelte';
    import { fade, slide, fly } from 'svelte/transition';
    import { rentalProperties, leases, rentalLoading, loadRentalData } from '$lib/stores/propertyDashboard.js';
    import LoadingSkeleton from '$lib/components/ui/LoadingSkeleton.svelte';
    import Button from '$lib/components/ui/Button.svelte';
    import Modal from '$lib/components/ui/Modal.svelte';
  
    // Svelte 5 runes
    let properties = $derived($rentalProperties);
    let leaseData = $derived($leases);
    let loading = $derived($rentalLoading);
    let activeView = $state('properties');
    let searchQuery = $state('');
    let statusFilter = $state('');
    let showCreateModal = $state(false);
  
    // Filters
    let filteredProperties = $derived(() => {
      if (!properties) return [];
      return properties.filter(property => {
        const matchesSearch = !searchQuery || 
          property.property_info?.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
          property.property_info?.address?.toLowerCase().includes(searchQuery.toLowerCase());
        
        const matchesStatus = !statusFilter || 
          (statusFilter === 'occupied' && property.is_currently_rented) ||
          (statusFilter === 'vacant' && !property.is_currently_rented);
        
        return matchesSearch && matchesStatus;
      });
    });
  
    let filteredLeases = $derived(() => {
      if (!leaseData) return [];
      return leaseData.filter(lease => {
        return !searchQuery || 
          lease.rental_property_info?.property_title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
          lease.tenant_info?.full_name?.toLowerCase().includes(searchQuery.toLowerCase());
      });
    });
  
    onMount(async () => {
      await loadRentalData();
    });
  
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
  
    function getStatusColor(isOccupied) {
      return isOccupied 
        ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400'
        : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400';
    }
  
    function getLeaseStatusColor(status) {
      const colors = {
        active: 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400',
        expired: 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400',
        terminated: 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400'
      };
      return colors[status] || 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400';
    }
  </script>
  
  <div class="space-y-6">
    <!-- Rental Management Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white">Rental Management</h2>
        <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Manage rental properties, leases, and tenant relationships
        </p>
      </div>
      
      <div class="mt-4 sm:mt-0 flex items-center space-x-3">
        <Button
          size="sm"
          variant="outline"
          onclick={() => showCreateModal = true}
        >
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          Add Rental Property
        </Button>
      </div>
    </div>
  
    <!-- View Toggle -->
    <div class="border-b border-gray-200 dark:border-gray-700">
      <nav class="-mb-px flex space-x-8" aria-label="Tabs">
        <button
          onclick={() => activeView = 'properties'}
          class={`${
            activeView === 'properties'
              ? 'border-primary-500 text-primary-600 dark:text-primary-400'
              : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
          } whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm`}
        >
          Rental Properties ({filteredProperties.length})
        </button>
        <button
          onclick={() => activeView = 'leases'}
          class={`${
            activeView === 'leases'
              ? 'border-primary-500 text-primary-600 dark:text-primary-400'
              : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
          } whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm`}
        >
          Lease Agreements ({filteredLeases.length})
        </button>
      </nav>
    </div>
  
    <!-- Filters -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-3 sm:space-y-0 sm:space-x-4">
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
            placeholder="Search properties or tenants..."
            class="block w-full pl-10 pr-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md leading-5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-1 focus:ring-primary-500 focus:border-primary-500 text-sm"
          />
        </div>
      </div>
      
      {#if activeView === 'properties'}
        <div class="flex items-center space-x-3">
          <select
            bind:value={statusFilter}
            class="block pl-3 pr-10 py-2 text-base border border-gray-300 dark:border-gray-600 focus:outline-none focus:ring-primary-500 focus:border-primary-500 text-sm rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            <option value="">All Properties</option>
            <option value="occupied">Occupied</option>
            <option value="vacant">Vacant</option>
          </select>
        </div>
      {/if}
    </div>
  
    {#if loading}
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {#each Array(6) as _}
          <LoadingSkeleton class="h-64" />
        {/each}
      </div>
    {:else if activeView === 'properties'}
      <!-- Rental Properties Grid -->
      {#if filteredProperties.length === 0}
        <div class="text-center py-12 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
          <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
          </svg>
          <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-white">No rental properties found</h3>
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Get started by adding your first rental property.
          </p>
          <div class="mt-6">
            <Button onclick={() => showCreateModal = true}>
              Add Rental Property
            </Button>
          </div>
        </div>
      {:else}
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" in:fade>
          {#each filteredProperties as property, index}
            <div
              class="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700 hover:shadow-lg transition-shadow duration-200"
              in:fly={{ y: 20, duration: 300, delay: index * 50 }}
            >
              <div class="flex items-start justify-between mb-4">
                <div class="flex-1">
                  <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-1">
                    {property.property_info?.title || 'Untitled Property'}
                  </h3>
                  <p class="text-sm text-gray-500 dark:text-gray-400">
                    {property.property_info?.address || 'No address'}
                  </p>
                </div>
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {getStatusColor(property.is_currently_rented)}">
                  {property.is_currently_rented ? 'Occupied' : 'Vacant'}
                </span>
              </div>
  
              <div class="space-y-3">
                <div class="flex justify-between items-center">
                  <span class="text-sm text-gray-500 dark:text-gray-400">Monthly Rent</span>
                  <span class="text-lg font-semibold text-gray-900 dark:text-white">
                    {formatCurrency(property.monthly_rent)}
                  </span>
                </div>
  
                <div class="flex justify-between items-center">
                  <span class="text-sm text-gray-500 dark:text-gray-400">Security Deposit</span>
                  <span class="text-sm font-medium text-gray-900 dark:text-white">
                    {formatCurrency(property.security_deposit)}
                  </span>
                </div>
  
                <div class="flex justify-between items-center">
                  <span class="text-sm text-gray-500 dark:text-gray-400">Beds/Baths</span>
                  <span class="text-sm text-gray-900 dark:text-white">
                    {property.bedrooms}bd / {property.bathrooms}ba
                  </span>
                </div>
  
                {#if property.current_lease}
                  <div class="border-t border-gray-200 dark:border-gray-600 pt-3 mt-3">
                    <div class="text-sm text-gray-500 dark:text-gray-400 mb-1">Current Tenant</div>
                    <div class="text-sm font-medium text-gray-900 dark:text-white">
                      {property.current_lease.tenant_name}
                    </div>
                    <div class="text-xs text-gray-500 dark:text-gray-400">
                      Lease expires in {property.current_lease.days_remaining} days
                    </div>
                  </div>
                {/if}
              </div>
  
              <div class="flex items-center justify-between mt-4 pt-4 border-t border-gray-200 dark:border-gray-600">
                <div class="flex space-x-2">
                  <Button size="sm" variant="outline">
                    Edit
                  </Button>
                  <Button size="sm" variant="outline">
                    View
                  </Button>
                </div>
              </div>
            </div>
          {/each}
        </div>
      {/if}
    {:else}
      <!-- Lease Agreements List -->
      {#if filteredLeases.length === 0}
        <div class="text-center py-12 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
          <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-white">No lease agreements found</h3>
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Create lease agreements for your rental properties.
          </p>
        </div>
      {:else}
        <div class="space-y-4" in:fade>
          {#each filteredLeases as lease, index}
            <div
              class="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700 hover:shadow-lg transition-shadow duration-200"
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
                        <span class="font-medium">Property:</span>
                        <span>{lease.rental_property_info?.property_title}</span>
                      </div>
                      <div class="flex items-center space-x-4">
                        <span class="font-medium">Tenant:</span>
                        <span>{lease.tenant_info?.full_name || lease.tenant_info?.email}</span>
                      </div>
                      <div class="flex items-center space-x-4">
                        <span>Term: {formatDate(lease.start_date)} - {formatDate(lease.end_date)}</span>
                        {#if lease.days_remaining > 0}
                          <span class="text-yellow-600 dark:text-yellow-400">
                            {lease.days_remaining} days remaining
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
                      per month
                    </div>
                  </div>
                  <div class="flex items-center space-x-2">
                    <Button size="sm" variant="outline">
                      Edit
                    </Button>
                    <Button size="sm" variant="outline">
                      View
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          {/each}
        </div>
      {/if}
    {/if}
  </div>
  
  <!-- Create Rental Property Modal -->
  <Modal bind:open={showCreateModal} title="Create Rental Property">
    <div class="p-6">
      <p class="text-gray-600 dark:text-gray-400 mb-4">
        Convert an existing property to a rental property or create a new one.
      </p>
      
      <div class="space-y-4">
        <Button class="w-full justify-start" variant="outline">
          <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3-3m0 0l-3 3m3-3v12" />
          </svg>
          Convert Existing Property
        </Button>
        
        <Button class="w-full justify-start" variant="outline">
          <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          Create New Property
        </Button>
      </div>
    </div>
  </Modal>