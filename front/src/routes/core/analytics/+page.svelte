<!-- src/routes/core/analytics/+page.svelte -->
<script>
  import { onMount } from 'svelte';
  import { fade, slide, fly } from 'svelte/transition';
  import { t, locale } from '$lib/i18n';
  import { user } from '$lib/stores/user';
  import { 
    analyticsLoading,
    analyticsError,
    analyticsData,
    performanceMetrics,
    analyticsActions,
    dashboardSummary,
    maintenanceStats,
    financialStats,
    rentalStats
  } from '$lib/stores/core.js';
  
  // Components
  import LoadingSkeleton from '$lib/components/ui/LoadingSkeleton.svelte';
  import EmptyState from '$lib/components/ui/EmptyState.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import CoreStatsCard from '$lib/components/core/CoreStatsCard.svelte';

  // Local UI state only
  let activeTab = $state('overview');
  let dateRange = $state('7d');
  let isRTL = $derived($locale === 'ar');

  // Derived values from core store
  let loading = $derived($analyticsLoading);
  let error = $derived($analyticsError);
  let analytics = $derived($analyticsData);
  let metrics = $derived($performanceMetrics);
  let summary = $derived($dashboardSummary);
  let maintenance = $derived($maintenanceStats);
  let financial = $derived($financialStats);
  let rental = $derived($rentalStats);

  onMount(async () => {
    await analyticsActions.loadDashboard();
  });

  function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount || 0);
  }

  function formatPercentage(value) {
    const numValue = Number(value) || 0;
    return `${numValue.toFixed(1)}%`;
  }

  function formatNumber(value) {
    return new Intl.NumberFormat('en-US').format(value || 0);
  }

  async function handleDateRangeChange() {
    // Reload analytics data when date range changes
    await analyticsActions.loadDashboard();
  }
</script>

<svelte:head>
  <title>{$t('core.analytics.title')} | {$t('app.name')}</title>
</svelte:head>

<div class="space-y-6">
  <!-- Header Section -->
  <div class="bg-white dark:bg-gray-800 shadow rounded-lg" in:fade={{ duration: 300 }}>
    <div class="px-4 py-5 sm:p-6">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div class="flex-1 min-w-0">
          <h1 class="text-2xl font-bold leading-7 text-gray-900 dark:text-white sm:text-3xl sm:truncate">
            {$t('core.analytics.title')}
          </h1>
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
            {$t('core.analytics.subtitle')}
          </p>
        </div>
        <div class="mt-4 flex items-center space-x-3 sm:mt-0 sm:ml-4">
          <select
            bind:value={dateRange}
            onchange={handleDateRangeChange}
            class="block w-32 pl-3 pr-10 py-2 text-base border border-gray-300 dark:border-gray-600 focus:outline-none focus:ring-primary-500 focus:border-primary-500 text-sm rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            <option value="7d">{$t('core.analytics.dateRanges.last7Days')}</option>
            <option value="30d">{$t('core.analytics.dateRanges.last30Days')}</option>
            <option value="90d">{$t('core.analytics.dateRanges.last90Days')}</option>
            <option value="1y">{$t('core.analytics.dateRanges.lastYear')}</option>
          </select>
          <Button size="sm" variant="outline">
            {$t('core.analytics.exportReport')}
          </Button>
        </div>
      </div>
    </div>
  </div>

  <!-- Overview Stats Grid -->
  {#if !$analyticsLoading}
    <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6" in:slide={{ duration: 400 }}>
      <CoreStatsCard
        title={$t('core.analytics.totalRevenue')}
        value={formatCurrency(metrics?.totalRevenue || 0)}
        icon="currency-dollar"
        color="green"
        trend="up"
        change="+12.3%"
      />
      
      <CoreStatsCard
        title={$t('core.analytics.totalExpenses')}
        value={formatCurrency(metrics?.totalExpenses || 0)}
        icon="credit-card"
        color="red"
        trend="down"
        change="-2.1%"
      />
      
      <CoreStatsCard
        title={$t('core.analytics.netIncome')}
        value={formatCurrency(metrics?.netIncome || 0)}
        icon="trending-up"
        color={(metrics?.netIncome || 0) >= 0 ? "green" : "red"}
        trend={(metrics?.netIncome || 0) >= 0 ? "up" : "down"}
        change={(metrics?.netIncome || 0) >= 0 ? "+8.5%" : "-3.2%"}
      />
      
      <CoreStatsCard
        title={$t('core.analytics.occupancyRate')}
        value={formatPercentage(metrics?.occupancyRate || 0)}
        icon="home"
        color="blue"
        trend="up"
        change="+2.4%"
      />
      
      <CoreStatsCard
        title={$t('core.analytics.maintenanceRequests')}
        value={(metrics?.maintenanceRequests || 0).toString()}
        icon="wrench-screwdriver"
        color="orange"
      />
      
      <CoreStatsCard
        title={$t('core.analytics.activeLeases')}
        value={(metrics?.activeLeases || 0).toString()}
        icon="document-text"
        color="purple"
      />
    </div>
  {:else}
    <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
      {#each Array(6) as _}
        <LoadingSkeleton class="h-24" />
      {/each}
    </div>
  {/if}

  <!-- Analytics Tabs -->
  <div class="bg-white dark:bg-gray-800 shadow rounded-lg" in:fade={{ delay: 100 }}>
    <div class="border-b border-gray-200 dark:border-gray-700">
      <nav class="-mb-px flex space-x-8 px-6" aria-label="Tabs">
        <button
          onclick={() => activeTab = 'overview'}
          class={`${
            activeTab === 'overview'
              ? 'border-primary-500 text-primary-600 dark:text-primary-400'
              : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
          } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center transition-colors duration-200`}
        >
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          {$t('core.analytics.tabs.overview')}
        </button>
        <button
          onclick={() => activeTab = 'financial'}
          class={`${
            activeTab === 'financial'
              ? 'border-primary-500 text-primary-600 dark:text-primary-400'
              : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
          } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center transition-colors duration-200`}
        >
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
          </svg>
          {$t('core.analytics.tabs.financial')}
        </button>
        <button
          onclick={() => activeTab = 'maintenance'}
          class={`${
            activeTab === 'maintenance'
              ? 'border-primary-500 text-primary-600 dark:text-primary-400'
              : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
          } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center transition-colors duration-200`}
        >
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
          </svg>
          {$t('core.analytics.tabs.maintenance')}
        </button>
        <button
          onclick={() => activeTab = 'occupancy'}
          class={`${
            activeTab === 'occupancy'
              ? 'border-primary-500 text-primary-600 dark:text-primary-400'
              : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
          } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center transition-colors duration-200`}
        >
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z" />
          </svg>
          {$t('core.analytics.tabs.occupancy')}
        </button>
      </nav>
    </div>

    <!-- Tab Content -->
    <div class="p-6">
      {#if $analyticsLoading}
        <div class="space-y-4">
          {#each Array(3) as _}
            <LoadingSkeleton class="h-64" />
          {/each}
        </div>
      {:else if $analyticsError}
        <EmptyState
          title="Failed to Load Analytics"
          description={$analyticsError}
          actionText="Try Again"
          onAction={() => analyticsActions.loadDashboard()}
        />
      {:else}
        <div class="space-y-6" in:slide={{ duration: 300 }}>
          {#if activeTab === 'overview'}
            <!-- Overview Content -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <!-- Revenue vs Expenses Chart Placeholder -->
              <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-6">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">{$t('core.analytics.revenueVsExpenses')}</h3>
                <div class="h-64 flex items-center justify-center bg-gray-100 dark:bg-gray-600 rounded-lg">
                  <div class="text-center">
                    <svg class="w-12 h-12 text-gray-400 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                    <p class="text-gray-500 dark:text-gray-400">{$t('core.analytics.chartsPlaceholder')}</p>
                  </div>
                </div>
              </div>

              <!-- Property Performance -->
              <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-6">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">{$t('core.analytics.propertyPerformance')}</h3>
                <div class="space-y-4">
                  <div class="flex justify-between items-center">
                    <span class="text-sm text-gray-600 dark:text-gray-400">{$t('core.analytics.occupancyRate')}</span>
                    <span class="text-sm font-medium text-gray-900 dark:text-white">{formatPercentage(metrics?.occupancyRate || 0)}</span>
                  </div>
                  <div class="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-2">
                    <div class="bg-green-500 h-2 rounded-full" style="width: {metrics?.occupancyRate || 0}%"></div>
                  </div>
                  
                  <div class="flex justify-between items-center">
                    <span class="text-sm text-gray-600 dark:text-gray-400">{$t('core.analytics.maintenanceResponse')}</span>
                    <span class="text-sm font-medium text-gray-900 dark:text-white">85%</span>
                  </div>
                  <div class="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-2">
                    <div class="bg-blue-500 h-2 rounded-full" style="width: 85%"></div>
                  </div>
                  
                  <div class="flex justify-between items-center">
                    <span class="text-sm text-gray-600 dark:text-gray-400">{$t('core.analytics.tenantSatisfaction')}</span>
                    <span class="text-sm font-medium text-gray-900 dark:text-white">92%</span>
                  </div>
                  <div class="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-2">
                    <div class="bg-purple-500 h-2 rounded-full" style="width: 92%"></div>
                  </div>
                </div>
              </div>
            </div>

          {:else if activeTab === 'financial'}
            <!-- Financial Analytics Content -->
            <div class="space-y-6">
              <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-6">
                  <div class="flex items-center">
                    <div class="p-2 bg-green-100 dark:bg-green-900/40 rounded-lg">
                      <svg class="w-6 h-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                      </svg>
                    </div>
                    <div class="ml-4">
                      <p class="text-sm font-medium text-green-600 dark:text-green-400">{$t('core.analytics.totalRevenue')}</p>
                      <p class="text-2xl font-bold text-green-900 dark:text-green-100">{formatCurrency(metrics?.totalRevenue || 0)}</p>
                    </div>
                  </div>
                </div>
                
                <div class="bg-red-50 dark:bg-red-900/20 rounded-lg p-6">
                  <div class="flex items-center">
                    <div class="p-2 bg-red-100 dark:bg-red-900/40 rounded-lg">
                      <svg class="w-6 h-6 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                      </svg>
                    </div>
                    <div class="ml-4">
                      <p class="text-sm font-medium text-red-600 dark:text-red-400">{$t('core.analytics.totalExpenses')}</p>
                      <p class="text-2xl font-bold text-red-900 dark:text-red-100">{formatCurrency(metrics?.totalExpenses || 0)}</p>
                    </div>
                  </div>
                </div>
                
                <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-6">
                  <div class="flex items-center">
                    <div class="p-2 bg-blue-100 dark:bg-blue-900/40 rounded-lg">
                      <svg class="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                      </svg>
                    </div>
                    <div class="ml-4">
                      <p class="text-sm font-medium text-blue-600 dark:text-blue-400">{$t('core.analytics.netIncome')}</p>
                      <p class="text-2xl font-bold text-blue-900 dark:text-blue-100">{formatCurrency(metrics?.netIncome || 0)}</p>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Financial Chart Placeholder -->
              <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-6">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">{$t('core.analytics.financialTrends')}</h3>
                <div class="h-64 flex items-center justify-center bg-gray-100 dark:bg-gray-600 rounded-lg">
                  <div class="text-center">
                    <svg class="w-12 h-12 text-gray-400 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                    <p class="text-gray-500 dark:text-gray-400">{$t('core.analytics.financialChartsPlaceholder')}</p>
                  </div>
                </div>
              </div>
            </div>

          {:else if activeTab === 'maintenance'}
            <!-- Maintenance Analytics Content -->
            <div class="space-y-6">
              <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div class="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4">
                  <div class="text-center">
                    <p class="text-sm font-medium text-yellow-600 dark:text-yellow-400">{$t('core.maintenance.pendingRequests')}</p>
                    <p class="text-2xl font-bold text-yellow-900 dark:text-yellow-100">{maintenance?.pendingRequests || 0}</p>
                  </div>
                </div>
                <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                  <div class="text-center">
                    <p class="text-sm font-medium text-blue-600 dark:text-blue-400">{$t('core.maintenance.inProgressRequests')}</p>
                    <p class="text-2xl font-bold text-blue-900 dark:text-blue-100">{maintenance?.inProgressRequests || 0}</p>
                  </div>
                </div>
                <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                  <div class="text-center">
                    <p class="text-sm font-medium text-green-600 dark:text-green-400">{$t('core.maintenance.completedRequests')}</p>
                    <p class="text-2xl font-bold text-green-900 dark:text-green-100">{maintenance?.completedRequests || 0}</p>
                  </div>
                </div>
                <div class="bg-red-50 dark:bg-red-900/20 rounded-lg p-4">
                  <div class="text-center">
                    <p class="text-sm font-medium text-red-600 dark:text-red-400">{$t('core.maintenance.emergencyRequests')}</p>
                    <p class="text-2xl font-bold text-red-900 dark:text-red-100">{maintenance?.emergencyRequests || 0}</p>
                  </div>
                </div>
              </div>

              <!-- Maintenance Chart Placeholder -->
              <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-6">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">{$t('core.analytics.maintenanceRequestTrends')}</h3>
                <div class="h-64 flex items-center justify-center bg-gray-100 dark:bg-gray-600 rounded-lg">
                  <div class="text-center">
                    <svg class="w-12 h-12 text-gray-400 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                    <p class="text-gray-500 dark:text-gray-400">{$t('core.analytics.maintenanceChartsPlaceholder')}</p>
                  </div>
                </div>
              </div>
            </div>

          {:else if activeTab === 'occupancy'}
            <!-- Occupancy Analytics Content -->
            <div class="space-y-6">
              <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-6">
                  <div class="text-center">
                    <p class="text-sm font-medium text-blue-600 dark:text-blue-400">{$t('core.analytics.currentOccupancy')}</p>
                    <p class="text-3xl font-bold text-blue-900 dark:text-blue-100">{formatPercentage(metrics?.occupancyRate || 0)}</p>
                  </div>
                </div>
                <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-6">
                  <div class="text-center">
                    <p class="text-sm font-medium text-green-600 dark:text-green-400">{$t('core.analytics.activeLeases')}</p>
                    <p class="text-3xl font-bold text-green-900 dark:text-green-100">{metrics?.activeLeases || 0}</p>
                  </div>
                </div>
                <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-6">
                  <div class="text-center">
                    <p class="text-sm font-medium text-purple-600 dark:text-purple-400">{$t('core.analytics.avgLeaseDuration')}</p>
                    <p class="text-3xl font-bold text-purple-900 dark:text-purple-100">{rental?.averageLeaseDuration || '12'} mo</p>
                  </div>
                </div>
              </div>

              <!-- Occupancy Chart Placeholder -->
              <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-6">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">{$t('core.analytics.occupancyTrends')}</h3>
                <div class="h-64 flex items-center justify-center bg-gray-100 dark:bg-gray-600 rounded-lg">
                  <div class="text-center">
                    <svg class="w-12 h-12 text-gray-400 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                    <p class="text-gray-500 dark:text-gray-400">{$t('core.analytics.chartsPlaceholder')}</p>
                  </div>
                </div>
              </div>
            </div>
          {/if}
        </div>
      {/if}
    </div>
  </div>
</div>