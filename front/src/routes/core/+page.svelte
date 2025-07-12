<!-- src/routes/core/+page.svelte -->
<script>
  import { onMount, onDestroy } from 'svelte';
  import { fade, slide, fly } from 'svelte/transition';
  import { t, locale } from '$lib/i18n';
  import { user } from '$lib/stores/user';
  
  // Core store integration
  import {
    coreLoading,
    coreError,
    dashboardSummary,
    maintenanceStats,
    financialStats,
    contractStats,
    rentalStats,
    refreshAllData,
    initializeCoreStore
  } from '$lib/stores/core.js';
  
  // Components
  import LoadingSkeleton from '$lib/components/ui/LoadingSkeleton.svelte';
  import EmptyState from '$lib/components/ui/EmptyState.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import StatCard from '$lib/components/dashboard/StatCard.svelte';

  // State using Svelte 5 runes
  let refreshInterval = $state(null);
  let isRTL = $derived($locale === 'ar');
  let loading = $derived($coreLoading);
  let error = $derived($coreError);
  let dashboardSummaryData = $derived($dashboardSummary);
  let maintenanceData = $derived($maintenanceStats);
  let financialData = $derived($financialStats);
  let contractData = $derived($contractStats);
  let rentalData = $derived($rentalStats);

  // Dashboard sections
  let activeSection = $state('overview');
  let showRefreshAnimation = $state(false);

  onMount(async () => {
    // Only initialize core store on core pages to prevent interference
    if (typeof window !== 'undefined' && window.location.pathname.startsWith('/core')) {
      await initializeCoreStore(['analytics', 'rental', 'maintenance', 'financial', 'contracts']);
      
      // Set up auto-refresh every 5 minutes - ONLY on core pages
      refreshInterval = setInterval(() => {
        // Double check we're still on a core page before refreshing
        if (typeof window !== 'undefined' && window.location.pathname.startsWith('/core')) {
          refreshAllData();
        }
      }, 300000);
    }
  });

  onDestroy(() => {
    if (refreshInterval) {
      clearInterval(refreshInterval);
    }
  });

  async function handleRefresh() {
    // Only refresh if we're on a core page
    if (typeof window !== 'undefined' && window.location.pathname.startsWith('/core')) {
      showRefreshAnimation = true;
      await refreshAllData();
      setTimeout(() => showRefreshAnimation = false, 1000);
    }
  }

  function getStatusColor(value, thresholds = { good: 80, warning: 60 }) {
    if (value >= thresholds.good) return 'text-green-600 dark:text-green-400';
    if (value >= thresholds.warning) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-red-600 dark:text-red-400';
  }

  function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount || 0);
  }

  function formatPercentage(value) {
    return `${(value || 0).toFixed(1)}%`;
  }
</script>

<svelte:head>
  <title>Property Management Dashboard | Real Estate Platform</title>
</svelte:head>

<div class="space-y-6">
  <!-- Header Section -->
  <div class="bg-white dark:bg-gray-800 shadow rounded-lg" in:fade={{ duration: 300 }}>
    <div class="px-4 py-5 sm:p-6">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div class="flex-1 min-w-0">
          <h1 class="text-2xl font-bold leading-7 text-gray-900 dark:text-white sm:text-3xl sm:truncate">
            Property Management Dashboard
          </h1>
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Comprehensive overview of your property portfolio and operations
          </p>
        </div>
        <div class="mt-4 flex items-center space-x-3 sm:mt-0 sm:ml-4">
          <Button
            variant="outline"
            size="sm"
            onclick={handleRefresh}
            disabled={loading}
            class={showRefreshAnimation ? 'animate-pulse' : ''}
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Refresh
          </Button>
          <Button href="/core/analytics" size="sm">
            View Reports
          </Button>
        </div>
      </div>
    </div>
  </div>

  {#if loading}
    <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
      {#each Array(8) as _}
        <LoadingSkeleton class="h-32" />
      {/each}
    </div>
  {:else if error}
    <div class="bg-white dark:bg-gray-800 shadow rounded-lg" in:fade>
      <EmptyState
        title="Failed to Load Dashboard"
        description={error}
        actionText="Try Again"
        actionHref="#"
        onAction={handleRefresh}
      />
    </div>
  {:else}
    <!-- Quick Stats Grid -->
    <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4" in:slide={{ duration: 400 }}>
      <!-- Total Properties -->
      <StatCard
        title="Total Properties"
        value={dashboardSummaryData?.totalProperties || 0}
        change="+2.5%"
        trend="up"
        color="blue"
        icon="home"
      />
      
      <!-- Monthly Income -->
      <StatCard
        title="Monthly Income"
        value={formatCurrency(dashboardSummaryData?.monthlyIncome || 0)}
        change="+8.2%"
        trend="up"
        color="green"
        icon="currency-dollar"
      />
      
      <!-- Occupancy Rate -->
      <StatCard
        title="Occupancy Rate"
        value={formatPercentage(dashboardSummaryData?.occupancyRate || 0)}
        change="-1.3%"
        trend="down"
        color="purple"
        icon="chart-bar"
      />
      
      <!-- Pending Maintenance -->
      <StatCard
        title="Pending Maintenance"
        value={dashboardSummaryData?.pendingMaintenance || 0}
        change="+12"
        trend="neutral"
        color="orange"
        icon="wrench-screwdriver"
      />
    </div>

    <!-- Section Navigation -->
    <div class="bg-white dark:bg-gray-800 shadow rounded-lg" in:fade={{ delay: 200 }}>
      <div class="border-b border-gray-200 dark:border-gray-700">
        <nav class="-mb-px flex space-x-8 px-6" aria-label="Tabs">
          {#each [
            { id: 'overview', label: 'Overview', icon: 'chart-bar' },
            { id: 'financial', label: 'Financial', icon: 'currency-dollar' },
            { id: 'maintenance', label: 'Maintenance', icon: 'wrench-screwdriver' },
            { id: 'leases', label: 'Leases', icon: 'document-text' },
            { id: 'contracts', label: 'Contracts', icon: 'clipboard-document-list' }
          ] as section}
            <button
              onclick={() => activeSection = section.id}
              class={`${
                activeSection === section.id
                  ? 'border-primary-500 text-primary-600 dark:text-primary-400'
                  : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
              } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center transition-colors duration-200`}
            >
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                {#if section.icon === 'chart-bar'}
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 0 1 3 19.875v-6.75ZM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V8.625ZM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V4.125Z" />
                {:else if section.icon === 'currency-dollar'}
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 6v12m-3-2.818.879.659c1.171.879 3.07.879 4.242 0 1.172-.879 1.172-2.303 0-3.182C13.536 12.219 12.768 12 12 12c-.725 0-1.467-.22-2.121-.659-1.172-.879-1.172-2.303 0-3.182s3.07-.879 4.242 0L15 9m-3 0V6m0 12v-3" />
                {:else if section.icon === 'wrench-screwdriver'}
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M11.42 15.17 17.25 21A2.652 2.652 0 0 0 21 17.25l-5.877-5.877M11.42 15.17l2.496-3.03c.317-.384.74-.626 1.208-.766M11.42 15.17l-4.655 5.653a2.548 2.548 0 1 1-3.586-3.586l6.837-5.63m5.108-.233c.55-.164 1.163-.188 1.743-.14a4.5 4.5 0 0 0 4.486-6.336l-3.276 3.277a3.004 3.004 0 0 1-2.25-2.25l3.276-3.276a4.5 4.5 0 0 0-6.336 4.486c.091 1.076-.071 2.264-.904 2.95l-.102.085m-1.745 1.437L5.909 7.5H4.5L2.25 3.75l1.5-1.5L7.5 4.5v1.409l4.26 4.26m-1.745 1.437 1.745-1.437m6.615 8.206L15.75 15.75M4.867 19.125h.008v.008h-.008v-.008Z" />
                {:else if section.icon === 'document-text'}
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
                {:else}
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 0 0 2.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 0 0-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 0 0 .75-.75 2.25 2.25 0 0 0-.1-.664m-5.8 0A2.251 2.251 0 0 1 13.5 2.25H15c1.012 0 1.867.668 2.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h4.125M8.25 8.25l13.5 13.5" />
                {/if}
              </svg>
              {section.label}
            </button>
          {/each}
        </nav>
      </div>

      <!-- Section Content -->
      <div class="p-6">
        {#if activeSection === 'overview'}
          <div in:fade={{ duration: 300 }}>
            <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Portfolio Overview</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <!-- Rental Properties Summary -->
              <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                <h4 class="text-sm font-medium text-gray-900 dark:text-white mb-3">Rental Properties</h4>
                <div class="space-y-2">
                  <div class="flex justify-between">
                    <span class="text-sm text-gray-600 dark:text-gray-400">Total Properties</span>
                    <span class="text-sm font-medium text-gray-900 dark:text-white">
                      {rentalData?.totalProperties || 0}
                    </span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-sm text-gray-600 dark:text-gray-400">Occupied</span>
                    <span class="text-sm font-medium text-gray-900 dark:text-white">
                      {rentalData?.occupiedProperties || 0}
                    </span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-sm text-gray-600 dark:text-gray-400">Vacant</span>
                    <span class="text-sm font-medium text-gray-900 dark:text-white">
                      {rentalData?.vacantProperties || 0}
                    </span>
                  </div>
                </div>
              </div>

              <!-- Financial Summary -->
              <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                <h4 class="text-sm font-medium text-gray-900 dark:text-white mb-3">Financial Performance</h4>
                <div class="space-y-2">
                  <div class="flex justify-between">
                    <span class="text-sm text-gray-600 dark:text-gray-400">YTD Income</span>
                    <span class="text-sm font-medium text-green-600 dark:text-green-400">
                      {formatCurrency(financialData?.ytdIncome || 0)}
                    </span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-sm text-gray-600 dark:text-gray-400">YTD Expenses</span>
                    <span class="text-sm font-medium text-red-600 dark:text-red-400">
                      {formatCurrency(financialData?.ytdExpenses || 0)}
                    </span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-sm text-gray-600 dark:text-gray-400">Net Profit</span>
                    <span class="text-sm font-medium text-gray-900 dark:text-white">
                      {formatCurrency(financialData?.netIncome || 0)}
                    </span>
                  </div>
                </div>
              </div>

              <!-- Quick Actions -->
              <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                <h4 class="text-sm font-medium text-gray-900 dark:text-white mb-3">Quick Actions</h4>
                <div class="space-y-3">
                  <Button href="/core/financial" size="sm" variant="outline" class="w-full justify-start">
                    <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                    </svg>
                    Add Transaction
                  </Button>
                  <Button href="/core/maintenance" size="sm" variant="outline" class="w-full justify-start">
                    <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                    </svg>
                    New Maintenance Request
                  </Button>
                  <Button href="/core/contracts" size="sm" variant="outline" class="w-full justify-start">
                    <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                    </svg>
                    Create Contract
                  </Button>
                </div>
              </div>
            </div>
          </div>
        {:else if activeSection === 'financial'}
          <div in:fade={{ duration: 300 }}>
            <div class="flex justify-between items-center mb-4">
              <h3 class="text-lg font-medium text-gray-900 dark:text-white">Financial Overview</h3>
              <Button href="/core/financial" size="sm">View Details</Button>
            </div>
            <!-- Financial summary content would go here -->
            <div class="text-center py-8 text-gray-500 dark:text-gray-400">
              Financial overview charts and summaries will be displayed here
            </div>
          </div>
        {:else if activeSection === 'maintenance'}
          <div in:fade={{ duration: 300 }}>
            <div class="flex justify-between items-center mb-4">
              <h3 class="text-lg font-medium text-gray-900 dark:text-white">Maintenance Overview</h3>
              <Button href="/core/maintenance" size="sm">View All Requests</Button>
            </div>
            <!-- Maintenance summary content would go here -->
            <div class="text-center py-8 text-gray-500 dark:text-gray-400">
              Maintenance requests summary and recent activity will be displayed here
            </div>
          </div>
        {:else if activeSection === 'leases'}
          <div in:fade={{ duration: 300 }}>
            <div class="flex justify-between items-center mb-4">
              <h3 class="text-lg font-medium text-gray-900 dark:text-white">Lease Overview</h3>
              <Button href="/core/rentals" size="sm">Manage Leases</Button>
            </div>
            <!-- Lease summary content would go here -->
            <div class="text-center py-8 text-gray-500 dark:text-gray-400">
              Lease status overview and expiring contracts will be displayed here
            </div>
          </div>
        {:else if activeSection === 'contracts'}
          <div in:fade={{ duration: 300 }}>
            <div class="flex justify-between items-center mb-4">
              <h3 class="text-lg font-medium text-gray-900 dark:text-white">Contract Overview</h3>
              <Button href="/core/contracts" size="sm">View Contracts</Button>
            </div>
            <!-- Contract summary content would go here -->
            <div class="text-center py-8 text-gray-500 dark:text-gray-400">
              Contract status overview and pending signatures will be displayed here
            </div>
          </div>
        {/if}
      </div>
    </div>
  {/if}
</div>