<!-- src/lib/components/dashboard/StatCard.svelte -->
<script>
    import { t } from '$lib/i18n';
    import { createEventDispatcher } from 'svelte';
  
    export let title = '';
    export let value = 0;
    export let change = null; // { value: number, type: 'increase' | 'decrease' }
    export let icon = '';
    export let color = 'primary'; // 'primary', 'success', 'warning', 'danger', 'info'
    export let loading = false;
    export let href = null;
    export let clickable = false;
    export let compact = false;
  
    const dispatch = createEventDispatcher();
  
    const colorClasses = {
      primary: 'text-primary-600 bg-primary-50 border-primary-100',
      success: 'text-success-600 bg-success-50 border-success-100',
      warning: 'text-warning-600 bg-warning-50 border-warning-100',
      danger: 'text-danger-600 bg-danger-50 border-danger-100',
      info: 'text-info-600 bg-info-50 border-info-100'
    };
  
    function handleClick() {
      if (clickable && !loading) {
        dispatch('click');
      }
    }
  
    function formatValue(val) {
      if (typeof val === 'number') {
        return val.toLocaleString();
      }
      return val;
    }
  </script>
  
  {#if href}
    <a 
      {href}
      class="block bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow duration-200 {compact ? 'p-3' : 'p-4'}"
    >
      <div class="flex items-center">
        {#if icon}
          <div class="flex-shrink-0 {compact ? 'w-8 h-8' : 'w-10 h-10'} rounded-lg flex items-center justify-center {colorClasses[color]}">
            {@html icon}
          </div>
        {/if}
        
        <div class="flex-1 {icon ? (compact ? 'ml-3' : 'ml-4') : ''}">
          <p class="text-xs font-medium text-gray-600 truncate">{title}</p>
          
          {#if loading}
            <div class="mt-1 h-6 bg-gray-200 rounded animate-pulse"></div>
          {:else}
            <div class="flex items-baseline">
              <p class="text-lg font-semibold text-gray-900">
                {formatValue(value)}
              </p>
              
              {#if change}
                <span class="ml-2 text-xs font-medium {change.type === 'increase' ? 'text-success-600' : 'text-danger-600'}">
                  {change.type === 'increase' ? '+' : ''}{change.value}%
                </span>
              {/if}
            </div>
          {/if}
        </div>
      </div>
    </a>
  {:else}
    <div 
      class="bg-white rounded-lg border border-gray-200 {compact ? 'p-3' : 'p-4'} {clickable ? 'cursor-pointer hover:shadow-md' : ''} transition-shadow duration-200"
      on:click={handleClick}
      role={clickable ? 'button' : 'presentation'}
      tabindex={clickable ? 0 : -1}
    >
      <div class="flex items-center">
        {#if icon}
          <div class="flex-shrink-0 {compact ? 'w-8 h-8' : 'w-10 h-10'} rounded-lg flex items-center justify-center {colorClasses[color]}">
            {@html icon}
          </div>
        {/if}
        
        <div class="flex-1 {icon ? (compact ? 'ml-3' : 'ml-4') : ''}">
          <p class="text-xs font-medium text-gray-600 truncate">{title}</p>
          
          {#if loading}
            <div class="mt-1 h-6 bg-gray-200 rounded animate-pulse"></div>
          {:else}
            <div class="flex items-baseline">
              <p class="text-lg font-semibold text-gray-900">
                {formatValue(value)}
              </p>
              
              {#if change}
                <span class="ml-2 text-xs font-medium {change.type === 'increase' ? 'text-success-600' : 'text-danger-600'}">
                  {change.type === 'increase' ? '+' : ''}{change.value}%
                </span>
              {/if}
            </div>
          {/if}
        </div>
      </div>
    </div>
  {/if}