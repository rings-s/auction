<!-- src/lib/components/FormField.svelte -->
<script>
    import { createEventDispatcher } from 'svelte';
    
    export let type = 'text';
    export let id = '';
    export let label = '';
    export let value = '';
    export let placeholder = '';
    export let helpText = '';
    export let error = '';
    export let required = false;
    export let disabled = false;
    export let min = null;
    export let max = null;
    export let step = null;
    export let rows = 3;
    export let options = [];
    export let multiple = false;
    export let currencySymbol = '';
    
    const dispatch = createEventDispatcher();
    
    function handleChange(e) {
      dispatch('change', e.target.value);
    }
    
    function handleBlur(e) {
      dispatch('blur', e.target.value);
    }
    
    function handleInput(e) {
      dispatch('input', e.target.value);
    }
    
    function handleFocus(e) {
      dispatch('focus', e.target.value);
    }
  </script>
  
  <div>
    {#if label}
      <label for={id} class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
        {label}{required ? ' *' : ''}
      </label>
    {/if}
    
    {#if type === 'textarea'}
      <div class="relative">
        <textarea
          {id}
          {placeholder}
          {required}
          {disabled}
          {rows}
          bind:value
          class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white {error ? 'border-red-500' : ''}"
          on:change={handleChange}
          on:blur={handleBlur}
          on:input={handleInput}
          on:focus={handleFocus}
        ></textarea>
        
        {#if error}
          <div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
            <svg class="h-5 w-5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
            </svg>
          </div>
        {/if}
      </div>
      
    {:else if type === 'select'}
      <div class="relative">
        <select
          {id}
          {required}
          {disabled}
          {multiple}
          bind:value
          class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white {error ? 'border-red-500' : ''}"
          on:change={handleChange}
          on:blur={handleBlur}
          on:focus={handleFocus}
        >
          {#each options as option}
            <option value={option.value}>{option.label}</option>
          {/each}
        </select>
        
        {#if error}
          <div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
            <svg class="h-5 w-5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
            </svg>
          </div>
        {/if}
      </div>
      
    {:else if type === 'currency'}
      <div class="relative">
        <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <span class="text-gray-500 dark:text-gray-400 sm:text-sm">{currencySymbol}</span>
        </div>
        <input
          {id}
          type="number"
          {placeholder}
          {required}
          {disabled}
          {min}
          {max}
          {step}
          bind:value
          class="pl-7 shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white {error ? 'border-red-500' : ''}"
          on:change={handleChange}
          on:blur={handleBlur}
          on:input={handleInput}
          on:focus={handleFocus}
        />
        
        {#if error}
          <div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
            <svg class="h-5 w-5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
            </svg>
          </div>
        {/if}
      </div>
      
    {:else}
      <div class="relative">
        <input
          {id}
          {type}
          {placeholder}
          {required}
          {disabled}
          {min}
          {max}
          {step}
          bind:value
          class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white {error ? 'border-red-500' : ''}"
          on:change={handleChange}
          on:blur={handleBlur}
          on:input={handleInput}
          on:focus={handleFocus}
        />
        
        {#if error}
          <div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
            <svg class="h-5 w-5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
            </svg>
          </div>
        {/if}
      </div>
    {/if}
    
    {#if error}
      <p class="mt-1 text-sm text-red-600 dark:text-red-500">{error}</p>
    {:else if helpText}
      <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">{helpText}</p>
    {/if}
  </div>