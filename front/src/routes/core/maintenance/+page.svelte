<!-- src/routes/core/maintenance/+page.svelte -->
<script>
  import { onMount } from 'svelte';
  import { fade, slide, fly } from 'svelte/transition';
  import { t, locale } from '$lib/i18n';
  import { user } from '$lib/stores/user';
  import { 
    maintenanceRequests,
    vendors,
    maintenanceStats,
    maintenanceFilters,
    maintenanceLoading,
    maintenanceError,
    filteredMaintenanceRequests,
    maintenanceActions
  } from '$lib/stores/core.js';
  
  // Components
  import LoadingSkeleton from '$lib/components/ui/LoadingSkeleton.svelte';
  import EmptyState from '$lib/components/ui/EmptyState.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Modal from '$lib/components/ui/Modal.svelte';
  import CoreStatsCard from '$lib/components/core/CoreStatsCard.svelte';

  // Local UI state only
  let activeTab = $state('requests');
  let showCreateModal = $state(false);
  let isRTL = $derived($locale === 'ar');

  // Form data for new maintenance request
  let formData = $state({
    property_id: '',
    title: '',
    description: '',
    category: '',
    priority: 'medium',
    estimated_cost: '',
    assigned_to_id: '',
    scheduled_date: ''
  });

  // Update store filters when search changes
  function updateSearch(value) {
    maintenanceFilters.update(f => ({ ...f, search: value }));
  }

  onMount(async () => {
    await maintenanceActions.loadAll();
  });

  async function handleCreateRequest(event) {
    event.preventDefault();
    try {
      await maintenanceActions.createRequest(formData);
      showCreateModal = false;
      
      // Reset form
      formData = {
        property_id: '',
        title: '',
        description: '',
        category: '',
        priority: 'medium',
        estimated_cost: '',
        assigned_to_id: '',
        scheduled_date: ''
      };
    } catch (err) {
      error = err.message || 'Failed to create maintenance request';
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

  function getStatusColor(status) {
    const colors = {
      submitted: 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400',
      in_progress: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400',
      completed: 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400',
      cancelled: 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400'
    };
    return colors[status] || 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400';
  }

  function getPriorityColor(priority) {
    const colors = {
      low: 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400',
      medium: 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400',
      high: 'bg-orange-100 text-orange-800 dark:bg-orange-900/20 dark:text-orange-400',
      emergency: 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400'
    };
    return colors[priority] || 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400';
  }
</script>

<svelte:head>
  <title>Maintenance Management | Property Management</title>
</svelte:head>

<div class="space-y-6">
  <!-- Header Section -->
  <div class="bg-white dark:bg-gray-800 shadow rounded-lg" in:fade={{ duration: 300 }}>
    <div class="px-4 py-5 sm:p-6">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div class="flex-1 min-w-0">
          <h1 class="text-2xl font-bold leading-7 text-gray-900 dark:text-white sm:text-3xl sm:truncate">
            Maintenance Management
          </h1>
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Manage maintenance requests, vendors, and work orders
          </p>
        </div>
        <div class="mt-4 flex items-center space-x-3 sm:mt-0 sm:ml-4">
          <Button
            href="/core/maintenance/vendors"
            variant="outline"
            size="sm"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
            Manage Vendors
          </Button>
          <Button
            onclick={() => showCreateModal = true}
            size="sm"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            New Request
          </Button>
        </div>
      </div>
    </div>
  </div>

  <!-- Stats Grid -->
  {#if !$maintenanceLoading}
    <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6" in:slide={{ duration: 400 }}>
      <CoreStatsCard
        title="Total Requests"
        value={$maintenanceStats.totalRequests.toString()}
        icon="wrench-screwdriver"
        color="blue"
      />
      
      <CoreStatsCard
        title="Pending"
        value={$maintenanceStats.pendingRequests.toString()}
        icon="clock"
        color="yellow"
      />
      
      <CoreStatsCard
        title="In Progress"
        value={$maintenanceStats.inProgressRequests.toString()}
        icon="cog"
        color="blue"
      />
      
      <CoreStatsCard
        title="Completed"
        value={$maintenanceStats.completedRequests.toString()}
        icon="check-circle"
        color="green"
        trend="up"
        change="+12%"
      />
      
      <CoreStatsCard
        title="Emergency"
        value={$maintenanceStats.emergencyRequests.toString()}
        icon="exclamation-triangle"
        color="red"
      />
      
      <CoreStatsCard
        title="YTD Cost"
        value={formatCurrency($maintenanceStats.totalCostYTD)}
        icon="currency-dollar"
        color="purple"
        trend="up"
        change="+8.3%"
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
          onclick={() => activeTab = 'requests'}
          class={`${
            activeTab === 'requests'
              ? 'border-primary-500 text-primary-600 dark:text-primary-400'
              : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
          } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center transition-colors duration-200`}
        >
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M11.42 15.17 17.25 21A2.652 2.652 0 0 0 21 17.25l-5.877-5.877M11.42 15.17l2.496-3.03c.317-.384.74-.626 1.208-.766M11.42 15.17l-4.655 5.653a2.548 2.548 0 1 1-3.586-3.586l6.837-5.63m5.108-.233c.55-.164 1.163-.188 1.743-.14a4.5 4.5 0 0 0 4.486-6.336l-3.276 3.277a3.004 3.004 0 0 1-2.25-2.25l3.276-3.276a4.5 4.5 0 0 0-6.336 4.486c.091 1.076-.071 2.264-.904 2.95l-.102.085m-1.745 1.437L5.909 7.5H4.5L2.25 3.75l1.5-1.5L7.5 4.5v1.409l4.26 4.26m-1.745 1.437 1.745-1.437m6.615 8.206L15.75 15.75M4.867 19.125h.008v.008h-.008v-.008Z" />
          </svg>
          Maintenance Requests ({$maintenanceStats.totalRequests})
        </button>
        <button
          onclick={() => activeTab = 'vendors'}
          class={`${
            activeTab === 'vendors'
              ? 'border-primary-500 text-primary-600 dark:text-primary-400'
              : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
          } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center transition-colors duration-200`}
        >
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 19.128a9.38 9.38 0 0 0 2.625.372 9.337 9.337 0 0 0 4.121-.952 4.125 4.125 0 0 0-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 0 1 8.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0 1 11.964-3.07M12 6.375a3.375 3.375 0 1 1-6.75 0 3.375 3.375 0 0 1 6.75 0Zm8.25 2.25a2.625 2.625 0 1 1-5.25 0 2.625 2.625 0 0 1 5.25 0Z" />
          </svg>
          Vendors ({$vendors.length})
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
              bind:value={$maintenanceFilters.search}
              placeholder={`Search ${activeTab}...`}
              oninput={() => maintenanceActions.loadAll()}
              class="block w-full pl-10 pr-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md leading-5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-primary-500 focus:border-primary-500 text-sm"
            />
          </div>
        </div>
        
        {#if activeTab === 'requests'}
          <div class="flex items-center space-x-3">
            <!-- Status Filter -->
            <div class="relative">
              <select
                bind:value={$maintenanceFilters.status}
                onchange={() => maintenanceActions.loadAll()}
                class="block w-32 pl-3 pr-10 py-2 text-base border border-gray-300 dark:border-gray-600 focus:outline-none focus:ring-primary-500 focus:border-primary-500 text-sm rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="">All Status</option>
                <option value="submitted">Submitted</option>
                <option value="in_progress">In Progress</option>
                <option value="completed">Completed</option>
                <option value="cancelled">Cancelled</option>
              </select>
            </div>

            <!-- Priority Filter -->
            <div class="relative">
              <select
                bind:value={$maintenanceFilters.priority}
                onchange={() => maintenanceActions.loadAll()}
                class="block w-32 pl-3 pr-10 py-2 text-base border border-gray-300 dark:border-gray-600 focus:outline-none focus:ring-primary-500 focus:border-primary-500 text-sm rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="">All Priority</option>
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="emergency">Emergency</option>
              </select>
            </div>

            <!-- Category Filter -->
            <div class="relative">
              <select
                bind:value={$maintenanceFilters.category}
                onchange={() => maintenanceActions.loadAll()}
                class="block w-32 pl-3 pr-10 py-2 text-base border border-gray-300 dark:border-gray-600 focus:outline-none focus:ring-primary-500 focus:border-primary-500 text-sm rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="">All Categories</option>
                <option value="plumbing">Plumbing</option>
                <option value="electrical">Electrical</option>
                <option value="hvac">HVAC</option>
                <option value="appliances">Appliances</option>
                <option value="structural">Structural</option>
                <option value="other">Other</option>
              </select>
            </div>
          </div>
        {/if}
      </div>
    </div>

    <!-- Content -->
    <div class="p-6">
      {#if $maintenanceLoading}
        <div class="space-y-4">
          {#each Array(5) as _}
            <LoadingSkeleton class="h-32" />
          {/each}
        </div>
      {:else if $maintenanceError}
        <EmptyState
          title="Failed to Load Data"
          description={$maintenanceError}
          actionText="Try Again"
          onAction={maintenanceActions.loadAll}
        />
      {:else if (activeTab === 'requests' ? $filteredMaintenanceRequests : $vendors).length === 0}
        <EmptyState
          title={`No ${activeTab} found`}
          description={`Start by creating your first ${activeTab.slice(0, -1)}`}
          actionText={`Add ${activeTab === 'requests' ? 'Request' : 'Vendor'}`}
          onAction={() => showCreateModal = true}
        />
      {:else}
        <div class="space-y-4" in:slide={{ duration: 300 }}>
          {#if activeTab === 'requests'}
            <!-- Maintenance Requests List -->
            {#each $filteredMaintenanceRequests as request, index}
              <div
                class="bg-gray-50 dark:bg-gray-700 rounded-lg p-6 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors duration-200"
                in:fly={{ y: 20, duration: 300, delay: index * 50 }}
              >
                <div class="flex items-start justify-between">
                  <div class="flex items-start space-x-4">
                    <div class="flex-shrink-0">
                      <div class="w-12 h-12 bg-orange-100 dark:bg-orange-900/20 rounded-lg flex items-center justify-center">
                        <svg class="w-6 h-6 text-orange-600 dark:text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                        </svg>
                      </div>
                    </div>
                    <div class="flex-1 min-w-0">
                      <div class="flex items-center space-x-2 mb-2">
                        <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
                          {request.title}
                        </h3>
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {getStatusColor(request.status)}">
                          {request.status_display || request.status}
                        </span>
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {getPriorityColor(request.priority)}">
                          {request.priority_display || request.priority}
                        </span>
                      </div>
                      <div class="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                        <p>{request.description}</p>
                        <div class="flex items-center space-x-4">
                          <span class="font-medium">Property:</span>
                          <span>{request.property_info?.title || 'Unknown Property'}</span>
                        </div>
                        <div class="flex items-center space-x-4">
                          <span class="font-medium">Category:</span>
                          <span>{request.category_display || request.category}</span>
                          {#if request.assigned_to_info}
                            <span class="font-medium">Assigned to:</span>
                            <span>{request.assigned_to_info.full_name}</span>
                          {/if}
                        </div>
                        <div class="flex items-center space-x-4">
                          <span>Created: {formatDate(request.requested_date)}</span>
                          {#if request.scheduled_date}
                            <span>Scheduled: {formatDate(request.scheduled_date)}</span>
                          {/if}
                          {#if request.completed_date}
                            <span>Completed: {formatDate(request.completed_date)}</span>
                          {/if}
                        </div>
                      </div>
                    </div>
                  </div>
                  <div class="flex items-center space-x-6">
                    <div class="text-right">
                      {#if request.actual_cost}
                        <div class="text-lg font-semibold text-gray-900 dark:text-white">
                          {formatCurrency(request.actual_cost)}
                        </div>
                        <div class="text-sm text-gray-500 dark:text-gray-400">Actual Cost</div>
                      {:else if request.estimated_cost}
                        <div class="text-lg font-semibold text-gray-900 dark:text-white">
                          {formatCurrency(request.estimated_cost)}
                        </div>
                        <div class="text-sm text-gray-500 dark:text-gray-400">Estimated</div>
                      {/if}
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
          {:else}
            <!-- Vendors Grid -->
            <div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
              {#each $vendors as vendor, index}
                <div
                  class="bg-gray-50 dark:bg-gray-700 rounded-lg p-6 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors duration-200"
                  in:fly={{ y: 20, duration: 300, delay: index * 50 }}
                >
                  <div class="flex items-start justify-between mb-4">
                    <div class="flex-1">
                      <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-1">
                        {vendor.company_name}
                      </h3>
                      <p class="text-sm text-gray-500 dark:text-gray-400">
                        {vendor.vendor_type_display || vendor.vendor_type}
                      </p>
                    </div>
                    <span class={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      vendor.is_active 
                        ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400'
                        : 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400'
                    }`}>
                      {vendor.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </div>

                  <div class="space-y-2">
                    <div class="flex justify-between items-center">
                      <span class="text-sm text-gray-500 dark:text-gray-400">Contact</span>
                      <span class="text-sm text-gray-900 dark:text-white">
                        {vendor.contact_person || 'Not specified'}
                      </span>
                    </div>

                    <div class="flex justify-between items-center">
                      <span class="text-sm text-gray-500 dark:text-gray-400">Phone</span>
                      <span class="text-sm text-gray-900 dark:text-white">
                        {vendor.phone}
                      </span>
                    </div>

                    {#if vendor.email}
                      <div class="flex justify-between items-center">
                        <span class="text-sm text-gray-500 dark:text-gray-400">Email</span>
                        <span class="text-sm text-gray-900 dark:text-white">
                          {vendor.email}
                        </span>
                      </div>
                    {/if}

                    {#if vendor.hourly_rate}
                      <div class="flex justify-between items-center">
                        <span class="text-sm text-gray-500 dark:text-gray-400">Rate</span>
                        <span class="text-sm font-medium text-gray-900 dark:text-white">
                          {formatCurrency(vendor.hourly_rate)}/hr
                        </span>
                      </div>
                    {/if}

                    {#if vendor.rating}
                      <div class="flex justify-between items-center">
                        <span class="text-sm text-gray-500 dark:text-gray-400">Rating</span>
                        <span class="text-sm font-medium text-gray-900 dark:text-white">
                          {vendor.rating}/5.0 ⭐
                        </span>
                      </div>
                    {/if}

                    {#if vendor.is_preferred}
                      <div class="mt-2">
                        <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400">
                          Preferred Vendor
                        </span>
                      </div>
                    {/if}
                  </div>

                  <div class="flex items-center justify-between mt-4 pt-4 border-t border-gray-200 dark:border-gray-600">
                    <div class="text-xs text-gray-500 dark:text-gray-400">
                      {vendor.license_number ? `License: ${vendor.license_number}` : ''}
                    </div>
                    <div class="flex space-x-2">
                      <Button size="sm" variant="outline">
                        Edit
                      </Button>
                      <Button size="sm" variant="outline">
                        Contact
                      </Button>
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

<!-- Create Maintenance Request Modal -->
<Modal bind:open={showCreateModal} title="New Maintenance Request">
  <form onsubmit={handleCreateRequest} class="space-y-4">
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
      <div class="sm:col-span-2">
        <label for="property_id" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
          Property
        </label>
        <select
          id="property_id"
          bind:value={formData.property_id}
          required
          class="mt-1 block w-full border border-gray-300 dark:border-gray-600 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
        >
          <option value="">Select Property</option>
          <!-- Properties would be loaded dynamically -->
        </select>
      </div>
      
      <div class="sm:col-span-2">
        <label for="title" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
          Title
        </label>
        <input
          type="text"
          id="title"
          bind:value={formData.title}
          required
          class="mt-1 block w-full border border-gray-300 dark:border-gray-600 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
        />
      </div>

      <div>
        <label for="category" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
          Category
        </label>
        <select
          id="category"
          bind:value={formData.category}
          required
          class="mt-1 block w-full border border-gray-300 dark:border-gray-600 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
        >
          <option value="">Select Category</option>
          <option value="plumbing">Plumbing</option>
          <option value="electrical">Electrical</option>
          <option value="hvac">HVAC</option>
          <option value="appliances">Appliances</option>
          <option value="structural">Structural</option>
          <option value="other">Other</option>
        </select>
      </div>

      <div>
        <label for="priority" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
          Priority
        </label>
        <select
          id="priority"
          bind:value={formData.priority}
          required
          class="mt-1 block w-full border border-gray-300 dark:border-gray-600 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
        >
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
          <option value="emergency">Emergency</option>
        </select>
      </div>

      <div>
        <label for="estimated_cost" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
          Estimated Cost
        </label>
        <input
          type="number"
          id="estimated_cost"
          bind:value={formData.estimated_cost}
          step="0.01"
          min="0"
          class="mt-1 block w-full border border-gray-300 dark:border-gray-600 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
        />
      </div>

      <div>
        <label for="scheduled_date" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
          Scheduled Date
        </label>
        <input
          type="date"
          id="scheduled_date"
          bind:value={formData.scheduled_date}
          class="mt-1 block w-full border border-gray-300 dark:border-gray-600 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
        />
      </div>
    </div>
    
    <div>
      <label for="description" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
        Description
      </label>
      <textarea
        id="description"
        bind:value={formData.description}
        required
        rows="3"
        class="mt-1 block w-full border border-gray-300 dark:border-gray-600 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
      ></textarea>
    </div>

    <div class="flex justify-end space-x-3 pt-4">
      <Button
        type="button"
        variant="outline"
        onclick={() => showCreateModal = false}
      >
        Cancel
      </Button>
      <Button type="submit">
        Create Request
      </Button>
    </div>
  </form>
</Modal>