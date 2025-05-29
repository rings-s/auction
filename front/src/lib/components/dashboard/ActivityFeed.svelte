<!-- src/lib/components/dashboard/ActivityFeed.svelte -->
<script>
    import { t } from '$lib/i18n';
    import { onMount } from 'svelte';
    import { formatDistanceToNow } from 'date-fns';
  
    export let activities = [];
    export let loading = false;
    export let compact = false;
    export let maxItems = 10;
  
    $: displayActivities = activities.slice(0, maxItems);
  
    function getActivityIcon(type) {
      const icons = {
        property: `<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
        </svg>`,
        auction: `<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>`,
        bid: `<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
        </svg>`,
        message: `<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
        </svg>`
      };
      
      return icons[type] || icons.property;
    }
  
    function getPriorityColor(priority) {
      const colors = {
        urgent: 'text-danger-600 bg-danger-50',
        high: 'text-warning-600 bg-warning-50',
        medium: 'text-primary-600 bg-primary-50',
        low: 'text-gray-600 bg-gray-50'
      };
      
      return colors[priority] || colors.low;
    }
  
    function formatTimeAgo(timestamp) {
      try {
        return formatDistanceToNow(new Date(timestamp), { addSuffix: true });
      } catch (error) {
        return $t('common.unknown');
      }
    }
  </script>
  
<div class="bg-white rounded-lg border border-gray-200 {compact ? 'p-3' : 'p-4'}">
  <div class="flex items-center justify-between mb-3">
    <h3 class="text-sm font-medium text-gray-900">{$t('dashboard.recentActivity')}</h3>
    
    <button 
      class="text-xs text-primary-600 hover:text-primary-700 font-medium"
      on:click={() => window.location.href = '/dashboard/activity'}
    >
      {$t('common.viewAll')}
    </button>
  </div>

  {#if loading}
    <div class="space-y-3">
      {#each Array(5) as _}
        <div class="flex items-start space-x-3 animate-pulse">
          <div class="w-8 h-8 bg-gray-200 rounded-full flex-shrink-0"></div>
          <div class="flex-1 space-y-2">
            <div class="h-3 bg-gray-200 rounded w-3/4"></div>
            <div class="h-2 bg-gray-200 rounded w-1/2"></div>
          </div>
        </div>
      {/each}
    </div>
  {:else if displayActivities.length === 0}
    <div class="text-center py-6">
      <svg class="w-12 h-12 mx-auto text-gray-400 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <p class="text-sm text-gray-500">{$t('dashboard.noRecentActivity')}</p>
    </div>
  {:else}
    <div class="space-y-3">
      {#each displayActivities as activity (activity.id || `${activity.timestamp}-${activity.title}`)}
        <div class="flex items-start space-x-3">
          <div class="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center {getPriorityColor(activity.priority)}">
            {@html getActivityIcon(activity.activity_type)}
          </div>
          
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-gray-900 truncate">
              {activity.title}
            </p>
            
            {#if activity.description}
              <p class="text-xs text-gray-600 truncate">
                {activity.description}
              </p>
            {/if}
            
            <div class="flex items-center justify-between mt-1">
              <p class="text-xs text-gray-500">
                {formatTimeAgo(activity.timestamp)}
              </p>
              
              {#if activity.user_name}
                <p class="text-xs text-gray-500">
                  {activity.user_name}
                </p>
              {/if}
            </div>
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>