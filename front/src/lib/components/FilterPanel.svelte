<!-- src/lib/components/FilterPanel.svelte -->
<script>
    import { createEventDispatcher } from 'svelte';
    
    export let title = '';
    export let options = [];
    export let value = '';
    export let onChange = null;
    
    const dispatch = createEventDispatcher();
    
    function handleChange(newValue) {
      if (onChange) {
        onChange(newValue);
      } else {
        dispatch('change', newValue);
      }
    }
  </script>
  
  <div class="bg-white dark:bg-gray-800 rounded-md p-4">
    <h3 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">{title}</h3>
    
    <div class="space-y-2">
      {#each options as option}
        <button
          type="button"
          class="w-full flex items-center justify-between px-4 py-2 text-sm rounded-md transition-colors
            {value === option.value 
              ? 'bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300 font-medium' 
              : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'}"
          on:click={() => handleChange(option.value)}
        >
          <span>{option.label}</span>
          
          {#if value === option.value}
            <svg class="h-4 w-4 text-primary-600 dark:text-primary-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
            </svg>
          {/if}
        </button>
      {/each}
    </div>
  </div>