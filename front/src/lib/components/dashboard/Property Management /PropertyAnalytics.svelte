<!-- src/lib/components/dashboard/PropertyAnalytics.svelte -->
<script>
  import { onMount } from 'svelte';
  import { fade, fly } from 'svelte/transition';
  import { analyticsData, analyticsLoading, loadAnalytics } from '$lib/stores/propertyDashboard.js';
  import LoadingSkeleton from '$lib/components/ui/LoadingSkeleton.svelte';
  import Button from '$lib/components/ui/Button.svelte';

  // Svelte 5 runes
  let analytics = $derived($analyticsData);
  let loading = $derived($analyticsLoading);
  let selectedPeriod = $state('30d');
  let selectedMetric = $state('revenue');

  const periods = [
    { value: '7d', label: 'Last 7 days' },
    { value: '30d', label: 'Last 30 days' },
    { value: '90d', label: 'Last 90 days' },
    { value: '1y', label: 'Last year' }
  ];

  const metrics = [
    { value: 'revenue', label: 'Revenue', color: 'green' },
    { value: 'expenses', label: 'Expenses', color: 'red' },
    { value: 'occupancy', label: 'Occupancy', color: 'blue' },
    { value: 'maintenance', label: 'Maintenance', color: 'orange' }
  ];

  onMount(async () => {
    await loadAnalytics(selectedPeriod);
  });

  // Effect to reload data when period changes
  $effect(() => {
    if (selectedPeriod) {
      loadAnalytics(selectedPeriod);
    }
  });

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

<div class="space-y-6">
  <!-- Analytics Header -->
  <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between">
    <div>
      <h2 class="text-xl font-semibold text-gray-900 dark:text-white">Property Analytics</h2>
      <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
        Comprehensive performance insights for your property portfolio
      </p>
    </div>
    
    <div class="mt-4 sm:mt-0 flex items-center space-x-3">
      <select
        bind:value={selectedPeriod}
        class="block pl-3 pr-10 py-2 text-base border border-gray-300 dark:border-gray-600 focus:outline-none focus:ring-primary-500 focus:border-primary-500 text-sm rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
      >
        {#each periods as period}
          <option value={period.value}>{period.label}</option>
        {/each}
      </select>
      
      <Button size="sm" variant="outline">
        Export Report
      </Button>
    </div>
  </div>

  {#if loading}
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {#each Array(4) as _}
        <LoadingSkeleton class="h-64" />
      {/each}
    </div>
  {:else if analytics}
    <!-- Key Performance Indicators -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6" in:fade>
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
        <div class="flex items-center">
          <div class="p-2 bg-green-100 dark:bg-green-900/20 rounded-lg">
            <svg class="w-6 h-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
            </svg>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-green-600 dark:text-green-400">Total Revenue</p>
            <p class="text-2xl font-bold text-green-900 dark:text-green-100">
              {formatCurrency(analytics.totalRevenue)}
            </p>
          </div>
        </div>
      </div>
      
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
        <div class="flex items-center">
          <div class="p-2 bg-red-100 dark:bg-red-900/20 rounded-lg">
            <svg class="w-6 h-6 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
            </svg>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-red-600 dark:text-red-400">Total Expenses</p>
            <p class="text-2xl font-bold text-red-900 dark:text-red-100">
              {formatCurrency(analytics.totalExpenses)}
            </p>
          </div>
        </div>
      </div>
      
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
        <div class="flex items-center">
          <div class="p-2 bg-blue-100 dark:bg-blue-900/20 rounded-lg">
            <svg class="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-blue-600 dark:text-blue-400">Net Income</p>
            <p class="text-2xl font-bold text-blue-900 dark:text-blue-100">
              {formatCurrency(analytics.netIncome)}
            </p>
          </div>
        </div>
      </div>
      
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
        <div class="flex items-center">
          <div class="p-2 bg-purple-100 dark:bg-purple-900/20 rounded-lg">
            <svg class="w-6 h-6 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-purple-600 dark:text-purple-400">Occupancy Rate</p>
            <p class="text-2xl font-bold text-purple-900 dark:text-purple-100">
              {formatPercentage(analytics.occupancyRate)}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts Section -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Revenue Trend Chart -->
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700" in:fly={{ y: 20, delay: 100 }}>
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Revenue Trend</h3>
        <div class="h-64 flex items-center justify-center bg-gray-50 dark:bg-gray-700 rounded-lg">
          <div class="text-center">
            <svg class="w-12 h-12 text-gray-400 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <p class="text-gray-500 dark:text-gray-400">Revenue trend chart</p>
            <p class="text-xs text-gray-400">Chart implementation needed</p>
          </div>
        </div>
      </div>

      <!-- Property Performance -->
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700" in:fly={{ y: 20, delay: 200 }}>
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Property Performance</h3>
        <div class="space-y-4">
          {#if analytics.topPerformingProperties}
            {#each analytics.topPerformingProperties as property, index}
              <div class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div class="flex items-center space-x-3">
                  <div class="w-8 h-8 bg-primary-100 dark:bg-primary-900/20 rounded-full flex items-center justify-center">
                    <span class="text-sm font-medium text-primary-600 dark:text-primary-400">
                      {index + 1}
                    </span>
                  </div>
                  <div>
                    <p class="text-sm font-medium text-gray-900 dark:text-white">
                      {property.title}
                    </p>
                    <p class="text-xs text-gray-500 dark:text-gray-400">
                      {property.address}
                    </p>
                  </div>
                </div>
                <div class="text-right">
                  <p class="text-sm font-medium text-gray-900 dark:text-white">
                    {formatCurrency(property.monthlyRevenue)}
                  </p>
                  <p class="text-xs text-gray-500 dark:text-gray-400">
                    {formatPercentage(property.yield)} yield
                  </p>
                </div>
              </div>
            {/each}
          {:else}
            <div class="text-center py-8">
              <p class="text-gray-500 dark:text-gray-400">No performance data available</p>
            </div>
          {/if}
        </div>
      </div>
    </div>

    <!-- Expense Breakdown -->
    <div class="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700" in:fly={{ y: 20, delay: 300 }}>
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Expense Breakdown</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {#each analytics.expenseBreakdown || [] as expense}
          <div class="text-center">
            <div class="text-2xl font-bold text-gray-900 dark:text-white">
              {formatCurrency(expense.amount)}
            </div>
            <div class="text-sm text-gray-500 dark:text-gray-400 capitalize">
              {expense.category}
            </div>
            <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 mt-2">
              <div 
                class="bg-primary-500 h-2 rounded-full" 
                style="width: {expense.percentage}%"
              ></div>
            </div>
          </div>
        {/each}
      </div>
    </div>
  {:else}
    <div class="text-center py-12">
      <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>
      <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-white">No Analytics Data</h3>
      <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
        Analytics data will appear here once you have properties and transactions.
      </p>
    </div>
  {/if}
</div>