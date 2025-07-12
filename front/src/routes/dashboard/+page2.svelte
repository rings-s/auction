<!-- src/routes/dashboard/+page.svelte -->
<script>
    import { onMount } from 'svelte';
    import { fade, slide } from 'svelte/transition';
    import { t, locale } from '$lib/i18n';
    import { user } from '$lib/stores/user';
    
    // Property Management Components
    import PropertyAnalytics from '$lib/components/dashboard/PropertyAnalytics.svelte';
    import RentalManagement from '$lib/components/dashboard/RentalManagement.svelte';
    import FinancialDashboard from '$lib/components/dashboard/FinancialDashboard.svelte';
    import MaintenancePanel from '$lib/components/dashboard/MaintenancePanel.svelte';
    import ContractManagement from '$lib/components/dashboard/ContractManagement.svelte';
    
    // UI Components
    import LoadingSkeleton from '$lib/components/ui/LoadingSkeleton.svelte';
    import Button from '$lib/components/ui/Button.svelte';
    import StatCard from '$lib/components/dashboard/StatCard.svelte';
  
    // Property Management Store
    import { 
      dashboardSummary, 
      propertyLoading, 
      propertyError,
      loadDashboardData,
      refreshAllData 
    } from '$lib/stores/propertyDashboard.js';
  
    // Svelte 5 runes for state management
    let activeTab = $state('overview');
    let isRTL = $derived($locale === 'ar');
    let loading = $derived($propertyLoading);
    let error = $derived($propertyError);
    let summary = $derived($dashboardSummary);
    
    // User permissions
    let canAccessPropertyManagement = $derived(
      $user?.role === 'landlord' || 
      $user?.role === 'property_manager' || 
      $user?.role === 'owner' || 
      $user?.is_staff
    );
  
    // Property management tabs
    const tabs = [
      { 
        id: 'overview', 
        label: 'Overview', 
        icon: 'chart-bar',
        description: 'Portfolio summary'
      },
      { 
        id: 'analytics', 
        label: 'Analytics', 
        icon: 'chart-pie',
        description: 'Performance insights'
      },
      { 
        id: 'rentals', 
        label: 'Rentals', 
        icon: 'home',
        description: 'Properties & leases'
      },
      { 
        id: 'financial', 
        label: 'Financial', 
        icon: 'currency-dollar',
        description: 'Income & expenses'
      },
      { 
        id: 'maintenance', 
        label: 'Maintenance', 
        icon: 'wrench-screwdriver',
        description: 'Requests & vendors'
      },
      { 
        id: 'contracts', 
        label: 'Contracts', 
        icon: 'document-text',
        description: 'Legal agreements'
      }
    ];
  
    // Filter tabs based on user permissions
    let availableTabs = $derived(() => {
      if (!canAccessPropertyManagement) {
        return tabs.filter(tab => tab.id === 'overview');
      }
      return tabs;
    });
  
    onMount(async () => {
      if (canAccessPropertyManagement) {
        await loadDashboardData();
      }
    });
  
    async function handleRefresh() {
      if (canAccessPropertyManagement) {
        await refreshAllData();
      }
    }
  
    function getIcon(iconName) {
      const icons = {
        'chart-bar': `<path stroke-linecap="round" stroke-linejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 0 1 3 19.875v-6.75ZM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V8.625ZM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V4.125Z" />`,
        'chart-pie': `<path stroke-linecap="round" stroke-linejoin="round" d="M10.5 6a7.5 7.5 0 1 0 7.5 7.5h-7.5V6Z M13.5 10.5H21A7.5 7.5 0 0 0 13.5 3v7.5Z" />`,
        'home': `<path stroke-linecap="round" stroke-linejoin="round" d="m2.25 12 8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25" />`,
        'currency-dollar': `<path stroke-linecap="round" stroke-linejoin="round" d="M12 6v12m-3-2.818.879.659c1.171.879 3.07.879 4.242 0 1.172-.879 1.172-2.303 0-3.182C13.536 12.219 12.768 12 12 12c-.725 0-1.467-.22-2.121-.659-1.172-.879-1.172-2.303 0-3.182s3.07-.879 4.242 0L15 9m-3 0V6m0 12v-3" />`,
        'wrench-screwdriver': `<path stroke-linecap="round" stroke-linejoin="round" d="M11.42 15.17 17.25 21A2.652 2.652 0 0 0 21 17.25l-5.877-5.877M11.42 15.17l2.496-3.03c.317-.384.74-.626 1.208-.766M11.42 15.17l-4.655 5.653a2.548 2.548 0 1 1-3.586-3.586l6.837-5.63m5.108-.233c.55-.164 1.163-.188 1.743-.14a4.5 4.5 0 0 0 4.486-6.336l-3.276 3.277a3.004 3.004 0 0 1-2.25-2.25l3.276-3.276a4.5 4.5 0 0 0-6.336 4.486c.091 1.076-.071 2.264-.904 2.95l-.102.085m-1.745 1.437L5.909 7.5H4.5L2.25 3.75l1.5-1.5L7.5 4.5v1.409l4.26 4.26m-1.745 1.437 1.745-1.437m6.615 8.206L15.75 15.75M4.867 19.125h.008v.008h-.008v-.008Z" />`,
        'document-text': `<path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />`
      };
      return icons[iconName] || '';
    }
  
    function formatCurrency(amount) {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
      }).format(amount || 0);
    }
  </script>
  
  <svelte:head>
    <title>Property Management Dashboard | Real Estate Platform</title>
  </svelte:head>
  
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
  
      <!-- Header Section -->
      <div class="bg-white dark:bg-gray-800 shadow rounded-lg mb-6" in:fade={{ duration: 300 }}>
        <div class="px-4 py-5 sm:p-6">
          <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between">
            <div class="flex-1 min-w-0">
              <h1 class="text-2xl font-bold leading-7 text-gray-900 dark:text-white sm:text-3xl sm:truncate">
                Property Management Dashboard
              </h1>
              <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Welcome back, {$user?.first_name || 'User'}! Manage your properties, track performance, and handle operations.
              </p>
            </div>
            
            <div class="mt-4 flex items-center space-x-3 sm:mt-0 sm:ml-4">
              <Button
                variant="outline"
                size="sm"
                onclick={handleRefresh}
                disabled={loading}
              >
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                Refresh
              </Button>
              
              {#if canAccessPropertyManagement}
                <Button size="sm" href="/properties/create">
                  <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                  Add Property
                </Button>
              {/if}
            </div>
          </div>
        </div>
      </div>
  
      {#if !canAccessPropertyManagement}
        <!-- Basic User Dashboard -->
        <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6" in:fade>
          <div class="text-center">
            <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
            <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-white">Welcome to the Platform</h3>
            <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Contact an administrator to access property management features.
            </p>
            <div class="mt-6">
              <Button href="/properties">
                Browse Properties
              </Button>
            </div>
          </div>
        </div>
      {:else}
        <!-- Property Management Dashboard -->
        
        <!-- Quick Stats Overview -->
        {#if summary && activeTab === 'overview'}
          <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-6" in:slide={{ duration: 400 }}>
            <StatCard
              title="Total Properties"
              value={summary.totalProperties || 0}
              change="+2.5%"
              trend="up"
              color="blue"
              icon="home"
            />
            
            <StatCard
              title="Monthly Income"
              value={formatCurrency(summary.monthlyIncome || 0)}
              change="+8.2%"
              trend="up"
              color="green"
              icon="currency-dollar"
            />
            
            <StatCard
              title="Occupancy Rate"
              value={`${(summary.occupancyRate || 0).toFixed(1)}%`}
              change="-1.3%"
              trend="down"
              color="purple"
              icon="chart-bar"
            />
            
            <StatCard
              title="Pending Maintenance"
              value={summary.pendingMaintenance || 0}
              change="+12"
              trend="neutral"
              color="orange"
              icon="wrench-screwdriver"
            />
          </div>
        {/if}
  
        <!-- Navigation Tabs -->
        <div class="bg-white dark:bg-gray-800 shadow rounded-lg" in:fade={{ delay: 200 }}>
          <div class="border-b border-gray-200 dark:border-gray-700">
            <nav class="-mb-px flex space-x-8 px-6 overflow-x-auto" aria-label="Tabs">
              {#each availableTabs as tab}
                <button
                  onclick={() => activeTab = tab.id}
                  class={`${
                    activeTab === tab.id
                      ? 'border-primary-500 text-primary-600 dark:text-primary-400'
                      : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
                  } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center transition-colors duration-200`}
                >
                  <svg class="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                    {@html getIcon(tab.icon)}
                  </svg>
                  <div class="text-left">
                    <div class="font-medium">{tab.label}</div>
                    <div class="text-xs text-gray-500 dark:text-gray-400 hidden sm:block">{tab.description}</div>
                  </div>
                </button>
              {/each}
            </nav>
          </div>
  
          <!-- Tab Content -->
          <div class="p-6">
            {#if loading}
              <div class="space-y-4">
                {#each Array(3) as _}
                  <LoadingSkeleton class="h-64" />
                {/each}
              </div>
            {:else if error}
              <div class="text-center py-12">
                <svg class="mx-auto h-12 w-12 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5l-6.928-12c-.77-.833-2.186-.833-2.956 0L.165 16.5C-.605 17.333.357 19 1.896 19z" />
                </svg>
                <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-white">Error Loading Data</h3>
                <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">{error}</p>
                <div class="mt-6">
                  <Button onclick={handleRefresh}>
                    Try Again
                  </Button>
                </div>
              </div>
            {:else}
              <div in:fade={{ duration: 300 }}>
                {#if activeTab === 'overview'}
                  <!-- Overview Content -->
                  <div class="space-y-6">
                    <!-- Quick Actions -->
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                      <Button href="/properties/create" class="h-24 flex flex-col items-center justify-center">
                        <svg class="w-6 h-6 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                        </svg>
                        Add Property
                      </Button>
                      
                      <Button variant="outline" class="h-24 flex flex-col items-center justify-center">
                        <svg class="w-6 h-6 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                        </svg>
                        New Lease
                      </Button>
                      
                      <Button variant="outline" class="h-24 flex flex-col items-center justify-center">
                        <svg class="w-6 h-6 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                        </svg>
                        Record Payment
                      </Button>
                      
                      <Button variant="outline" class="h-24 flex flex-col items-center justify-center">
                        <svg class="w-6 h-6 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                        </svg>
                        Maintenance Request
                      </Button>
                    </div>
  
                    <!-- Recent Activity Summary -->
                    <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-6">
                      <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Recent Activity</h3>
                      <p class="text-sm text-gray-500 dark:text-gray-400">
                        Select a tab above to view detailed property management information.
                      </p>
                    </div>
                  </div>
                {:else if activeTab === 'analytics'}
                  <PropertyAnalytics />
                {:else if activeTab === 'rentals'}
                  <RentalManagement />
                {:else if activeTab === 'financial'}
                  <FinancialDashboard />
                {:else if activeTab === 'maintenance'}
                  <MaintenancePanel />
                {:else if activeTab === 'contracts'}
                  <ContractManagement />
                {/if}
              </div>
            {/if}
          </div>
        </div>
      {/if}
    </div>
  </div>