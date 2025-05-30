<!-- src/routes/dashboard/+page.svelte -->
<script>
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { goto } from '$app/navigation';
    import { t } from '$lib/i18n';
    import { user } from '$lib/stores/user';
    import { 
      dashboardStats, 
      dashboardActivity, 
      dashboardLoading, 
      dashboardError,
      userPriority,
      canAccessSystemDashboard
    } from '$lib/stores/dashboard';
    import { 
      getUserDashboardStats, 
      getRecentActivity,
      refreshDashboardData 
    } from '$lib/api/dashboard';
    import { toast } from '$lib/stores/toastStore';
  
    // Components
    import StatCard from '$lib/components/dashboard/StatCard.svelte';
    import ActivityFeed from '$lib/components/dashboard/ActivityFeed.svelte';
    import QuickActions from '$lib/components/dashboard/QuickActions.svelte';
    import LoadingSkeleton from '$lib/components/ui/LoadingSkeleton.svelte';
    import Alert from '$lib/components/ui/Alert.svelte';
    import Button from '$lib/components/ui/Button.svelte';
    import Breadcrumb from '$lib/components/ui/Breadcrumb.svelte';
  
    let refreshing = false;
    let mounted = false;
  
    // Breadcrumb items
    $: breadcrumbItems = [
      { label: $t('nav.home'), href: '/' },
      { label: $t('dashboard.title'), href: '/dashboard', active: true }
    ];
  

    const propertyIcon = `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
        <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z"/>
    </svg>`;

    const auctionIcon = `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
        <path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z"/>
    </svg>`;

    const bidIcon = `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
    <path d="M8.433 7.418c.155-.103.346-.196.567-.267v1.698a2.305 2.305 0 01-.567-.267C8.07 8.34 8 8.114 8 8c0-.114.07-.34.433-.582zM11 12.849v-1.698c.22.071.412.164.567.267.364.243.433.468.433.582 0 .114-.07.34-.433.582a2.305 2.305 0 01-.567.267z"/>
        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-13a1 1 0 10-2 0v.092a4.535 4.535 0 00-1.676.662C6.602 6.234 6 7.009 6 8c0 .99.602 1.765 1.324 2.246.48.32 1.054.545 1.676.662v1.941c-.391-.127-.68-.317-.843-.504a1 1 0 10-1.51 1.31c.562.649 1.413 1.076 2.353 1.253V15a1 1 0 102 0v-.092a4.535 4.535 0 001.676-.662C13.398 13.766 14 12.991 14 12c0-.99-.602-1.765-1.324-2.246A4.535 4.535 0 0011 9.092V7.151c.391.127.68.317.843.504a1 1 0 101.511-1.31c-.563-.649-1.413-1.076-2.354-1.253V5z" clip-rule="evenodd"/>
    </svg>`;

    const messageIcon = `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
    <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z"/>
        <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z"/>
    </svg>`;

    // Load dashboard data
    async function loadDashboardData() {
    if (!$user) {
        goto('/login');
        return;
    }

    dashboardLoading.set(true);
    dashboardError.set(null);

    try {
        const [stats, activity] = await Promise.all([
            getUserDashboardStats(),
            getRecentActivity(10)
        ]);

        dashboardStats.set(stats);
        dashboardActivity.set(activity);
    } catch (error) {
        console.error('Failed to load dashboard data:', error);
        dashboardError.set(error.message);
        toast.error($t('dashboard.loadError'));
    } finally {
        dashboardLoading.set(false);
    }
    }

    // Refresh dashboard data
    async function handleRefresh() {
        if (refreshing) return;
   
        refreshing = true;
        try {
            await loadDashboardData();
            toast.success($t('dashboard.refreshed'));
        } catch (error) {
            toast.error($t('dashboard.refreshError'));
        } finally {
            refreshing = false;
        }
    }

    // Auto-refresh every 5 minutes
    let refreshInterval;
    onMount(() => {
        mounted = true;
        loadDashboardData();
   
        refreshInterval = setInterval(() => {
            if (document.visibilityState === 'visible') {
                loadDashboardData();
            }
        }, 5 * 60 * 1000); // 5 minutes

        return () => {
            if (refreshInterval) {
                clearInterval(refreshInterval);
            }
        };
    });

 // Computed values
    $: stats = $dashboardStats;
    $: activities = $dashboardActivity;
    $: isLoading = $dashboardLoading;
    $: error = $dashboardError;
</script>

<svelte:head>
    <title>{$t('dashboard.title')} - {$t('app.name')}</title>
    <meta name="description" content={$t('dashboard.description')} />
</svelte:head>

<div class="min-h-screen ">
 <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
   
   <!-- Header -->
   <div class="mb-6">

     <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between">
       <div>
         <h1 class="text-xl font-semibold text-gray-900">
           {$t('dashboard.title')}
         </h1>
         <p class="mt-1 text-sm text-gray-600">
           {$t('dashboard.welcome', { name: $user?.first_name || $user?.email })}
         </p>
       </div>
       
       <div class="mt-4 sm:mt-0 flex items-center space-x-3">
         {#if $canAccessSystemDashboard}
           <Button
             variant="outline"
             size="compact"
             href="/dashboard/system"
           >
             {$t('dashboard.systemDashboard')}
           </Button>
         {/if}
         
         <Button
           variant="outline"
           size="compact"
           loading={refreshing}
           onClick={handleRefresh}
         >
           {$t('common.refresh')}
         </Button>
       </div>
     </div>
   </div>

   <!-- Error Alert -->
   {#if error}
     <Alert
       type="error"
       title={$t('error.title')}
       message={error}
       dismissible
       class="mb-6"
     />
   {/if}

   <!-- Main Dashboard Content -->
   <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
     
     <!-- Stats Overview -->
     <div class="lg:col-span-3 space-y-6">
       
       <!-- Key Metrics -->
       <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
         {#if isLoading}
           {#each Array(4) as _, i}
             <LoadingSkeleton type="rect" height="80px" />
           {/each}
         {:else if stats}
           <StatCard
             title={$t('dashboard.totalProperties')}
             value={stats.total_properties || 0}
             icon={propertyIcon}
             color="primary"
             href="/dashboard/properties"
           />
           
           <StatCard
             title={$t('dashboard.totalAuctions')}
             value={stats.total_auctions || 0}
             icon={auctionIcon}
             color="success"
             href="/dashboard/auctions"
           />
           
           <StatCard
             title={$t('dashboard.totalBids')}
             value={stats.total_bids || 0}
             icon={bidIcon}
             color="warning"
             href="/dashboard/bids"
           />
           
           <StatCard
             title={$t('dashboard.unreadMessages')}
             value={stats.messages_unread || 0}
             icon={messageIcon}
             color="info"
             href="/messages?filter=unread"
           />
         {/if}
       </div>

       <!-- Additional Stats for Advanced Users -->
       {#if stats && $userPriority >= 3}
         <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
           <StatCard
             title={$t('dashboard.publishedProperties')}
             value={stats.published_properties || 0}
             color="success"
             compact
           />
           
           <StatCard
             title={$t('dashboard.activeAuctions')}
             value={stats.active_auctions || 0}
             color="primary"
             compact
           />
           
           <StatCard
             title={$t('dashboard.winningBids')}
             value={stats.winning_bids || 0}
             color="warning"
             compact
           />
         </div>
       {/if}

       <!-- Performance Metrics (for appraisers/data entry) -->
       {#if stats && ($user?.role === 'appraiser' || $user?.role === 'data_entry')}
         <div class="bg-white rounded-lg border border-gray-200 p-4">
           <h3 class="text-sm font-medium text-gray-900 mb-4">
             {$t('dashboard.performanceMetrics')}
           </h3>
           
           <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
             <div class="text-center">
               <p class="text-lg font-semibold text-gray-900">
                 {stats.properties_this_month || 0}
               </p>
               <p class="text-xs text-gray-600">
                 {$t('dashboard.propertiesThisMonth')}
               </p>
             </div>
             
             <div class="text-center">
               <p class="text-lg font-semibold text-gray-900">
                 {stats.auctions_this_month || 0}
               </p>
               <p class="text-xs text-gray-600">
                 {$t('dashboard.auctionsThisMonth')}
               </p>
             </div>
             
             <div class="text-center">
               <p class="text-lg font-semibold text-gray-900">
                 {stats.avg_property_value ? `$${stats.avg_property_value.toLocaleString()}` : '$0'}
               </p>
               <p class="text-xs text-gray-600">
                 {$t('dashboard.avgPropertyValue')}
               </p>
             </div>
           </div>
         </div>
       {/if}

       <!-- Recent Activity -->
       <div class="lg:hidden">
         <ActivityFeed 
           activities={activities} 
           loading={isLoading}
           maxItems={5}
           compact
         />
       </div>
     </div>

     <!-- Sidebar -->
     <div class="lg:col-span-1 space-y-6">
       
       <!-- Quick Actions -->
       <QuickActions />

       <!-- Recent Activity (Desktop) -->
       <div class="hidden lg:block">
         <ActivityFeed 
           activities={activities} 
           loading={isLoading}
           maxItems={8}
         />
       </div>

       <!-- User Info Card -->
       <div class="bg-white rounded-lg border border-gray-200 p-4">
         <div class="flex items-center space-x-3">
           <div class="w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center">
             <span class="text-sm font-medium text-primary-600">
               {$user?.first_name?.[0] || $user?.email?.[0] || 'U'}
             </span>
           </div>
           
           <div class="flex-1 min-w-0">
             <p class="text-sm font-medium text-gray-900 truncate">
               {$user?.first_name} {$user?.last_name}
             </p>
             <p class="text-xs text-gray-600">
               {$t(`auth.role${$user?.role?.charAt(0)?.toUpperCase()}${$user?.role?.slice(1)}`)}
             </p>
           </div>
         </div>
         
         {#if $userPriority > 1}
           <div class="mt-3 pt-3 border-t border-gray-200">
             <div class="flex items-center justify-between">
               <span class="text-xs text-gray-600">
                 {$t('dashboard.userPriority')}
               </span>
               <div class="flex items-center space-x-1">
                 {#each Array(5) as _, i}
                   <div class="w-2 h-2 rounded-full {i < $userPriority ? 'bg-primary-500' : 'bg-gray-200'}"></div>
                 {/each}
               </div>
             </div>
           </div>
         {/if}
       </div>

     </div>
   </div>
 </div>
</div>