<script>
  import { t } from '$lib/i18n';
  import { createEventDispatcher } from 'svelte';

  export let title = '';
  export let value = 0;
  export let change = null;
  export let icon = '';
  export let color = 'primary';
  export let loading = false;
  export let href = null;
  export let clickable = false;
  export let compact = false;

  const dispatch = createEventDispatcher();

  const colorClasses = {
    primary: 'text-primary-600 bg-primary-50 border-primary-100 dark:text-primary-400 dark:bg-primary-900/20 dark:border-primary-800',
    success: 'text-success-600 bg-success-50 border-success-100 dark:text-success-400 dark:bg-success-900/20 dark:border-success-800',
    warning: 'text-warning-600 bg-warning-50 border-warning-100 dark:text-warning-400 dark:bg-warning-900/20 dark:border-warning-800',
    danger: 'text-danger-600 bg-danger-50 border-danger-100 dark:text-danger-400 dark:bg-danger-900/20 dark:border-danger-800',
    info: 'text-primary-600 bg-primary-50 border-primary-100 dark:text-primary-400 dark:bg-primary-900/20 dark:border-primary-800'
  };

  function handleClick() {
    if (clickable && !loading) {
      dispatch('click');
    }
  }

  function handleKeydown(event) {
    if (clickable && !loading && (event.key === 'Enter' || event.key === ' ')) {
      event.preventDefault();
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
    class="block bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 {compact ? 'p-3' : 'p-4'} hover:shadow-md transition-shadow duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
  >
    <div class="flex items-center">
      {#if icon}
        <div class="flex-shrink-0 {compact ? 'w-8 h-8' : 'w-10 h-10'} rounded-lg flex items-center justify-center {colorClasses[color]}">
          {@html icon}
        </div>
      {/if}
      
      <div class="flex-1 {icon ? (compact ? 'ml-3' : 'ml-4') : ''}">
        <p class="text-xs font-medium text-gray-600 dark:text-gray-400 truncate">{title}</p>
        
        {#if loading}
          <div class="mt-1 h-6 bg-gray-200 dark:bg-gray-700 rounded animate-pulse"></div>
        {:else}
          <div class="flex items-baseline">
            <p class="text-lg font-semibold text-gray-900 dark:text-white">
              {formatValue(value)}
            </p>
            
            {#if change}
              <span class="ml-2 text-xs font-medium {change.type === 'increase' ? 'text-success-600 dark:text-success-400' : 'text-danger-600 dark:text-danger-400'}">
                {change.type === 'increase' ? '+' : ''}{change.value}%
              </span>
            {/if}
          </div>
        {/if}
      </div>
    </div>
  </a>
{:else if clickable}
  <button
    type="button"
    class="w-full text-left bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 {compact ? 'p-3' : 'p-4'} hover:shadow-md transition-shadow duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
    on:click={handleClick}
    on:keydown={handleKeydown}
    disabled={loading}
    aria-label={title}
  >
    <div class="flex items-center">
      {#if icon}
        <div class="flex-shrink-0 {compact ? 'w-8 h-8' : 'w-10 h-10'} rounded-lg flex items-center justify-center {colorClasses[color]}">
          {@html icon}
        </div>
      {/if}
      
      <div class="flex-1 {icon ? (compact ? 'ml-3' : 'ml-4') : ''}">
        <p class="text-xs font-medium text-gray-600 dark:text-gray-400 truncate">{title}</p>
        
        {#if loading}
          <div class="mt-1 h-6 bg-gray-200 dark:bg-gray-700 rounded animate-pulse"></div>
        {:else}
          <div class="flex items-baseline">
            <p class="text-lg font-semibold text-gray-900 dark:text-white">
              {formatValue(value)}
            </p>
            
            {#if change}
              <span class="ml-2 text-xs font-medium {change.type === 'increase' ? 'text-success-600 dark:text-success-400' : 'text-danger-600 dark:text-danger-400'}">
                {change.type === 'increase' ? '+' : ''}{change.value}%
              </span>
            {/if}
          </div>
        {/if}
      </div>
    </div>
  </button>
{:else}
  <div 
    class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 {compact ? 'p-3' : 'p-4'} transition-shadow duration-200"
    role="presentation"
  >
    <div class="flex items-center">
      {#if icon}
        <div class="flex-shrink-0 {compact ? 'w-8 h-8' : 'w-10 h-10'} rounded-lg flex items-center justify-center {colorClasses[color]}">
          {@html icon}
        </div>
      {/if}
      
      <div class="flex-1 {icon ? (compact ? 'ml-3' : 'ml-4') : ''}">
        <p class="text-xs font-medium text-gray-600 dark:text-gray-400 truncate">{title}</p>
        
        {#if loading}
          <div class="mt-1 h-6 bg-gray-200 dark:bg-gray-700 rounded animate-pulse"></div>
        {:else}
          <div class="flex items-baseline">
            <p class="text-lg font-semibold text-gray-900 dark:text-white">
              {formatValue(value)}
            </p>
            
            {#if change}
              <span class="ml-2 text-xs font-medium {change.type === 'increase' ? 'text-success-600 dark:text-success-400' : 'text-danger-600 dark:text-danger-400'}">
                {change.type === 'increase' ? '+' : ''}{change.value}%
              </span>
            {/if}
          </div>
        {/if}
      </div>
    </div>
  </div>
{/if}