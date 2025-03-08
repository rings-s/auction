<!-- src/lib/components/ui/FilterDropdown.svelte -->
<script>
    import { createEventDispatcher, onMount } from 'svelte';
    import { fade } from 'svelte/transition';
    
    // Props
    export let options = [];
    export let value = '';
    export let label = '';
    export let placeholder = 'Select an option';
    export let name = '';
    export let disabled = false;
    export let fullWidth = false;
    export let size = 'md'; // sm, md, lg
    export let variant = 'default'; // default, outlined, minimal
    
    // Internal state
    let isOpen = false;
    let buttonElement;
    let dropdownElement;
    
    // Event dispatcher
    const dispatch = createEventDispatcher();
    
    // Handle outside click to close dropdown
    function handleOutsideClick(event) {
      if (
        isOpen && 
        buttonElement && 
        !buttonElement.contains(event.target) && 
        dropdownElement && 
        !dropdownElement.contains(event.target)
      ) {
        isOpen = false;
      }
    }
    
    // Handle option selection
    function selectOption(option) {
      value = option.value;
      isOpen = false;
      dispatch('change', { name, value: option.value });
      dispatch('select', option);
    }
    
    // Toggle dropdown
    function toggleDropdown() {
      if (!disabled) {
        isOpen = !isOpen;
      }
    }
    
    // Get selected option label
    $: selectedOption = options.find(option => option.value === value);
    $: displayText = selectedOption ? selectedOption.label : placeholder;
    
    // Size classes
    $: sizeClasses = {
      sm: 'text-xs px-2 py-1',
      md: 'text-sm px-3 py-2',
      lg: 'text-base px-4 py-2'
    }[size];
    
    // Variant classes
    $: variantClasses = {
      default: 'bg-white border border-gray-300 shadow-sm hover:bg-gray-50',
      outlined: 'bg-transparent border border-primary-blue text-primary-blue hover:bg-primary-blue/5',
      minimal: 'bg-transparent hover:bg-gray-100'
    }[variant];
    
    // Add event listener on mount
    onMount(() => {
      document.addEventListener('click', handleOutsideClick);
      
      // Clean up on destroy
      return () => {
        document.removeEventListener('click', handleOutsideClick);
      };
    });
  </script>
  
  <div class="relative {fullWidth ? 'w-full' : ''}">
    {#if label}
      <label class="block text-sm font-medium text-gray-700 mb-1">
        {label}
      </label>
    {/if}
    
    <button
      type="button"
      bind:this={buttonElement}
      on:click={toggleDropdown}
      class="{sizeClasses} {variantClasses} rounded-md font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-blue transition-colors {fullWidth ? 'w-full' : ''} flex items-center justify-between {disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}"
      aria-haspopup="listbox"
      aria-expanded={isOpen}
      disabled={disabled}
    >
      <span class="truncate">{displayText}</span>
      <svg 
        xmlns="http://www.w3.org/2000/svg" 
        class="h-5 w-5 ml-2 transition-transform duration-200" 
        class:rotate-180={isOpen}
        fill="none" 
        viewBox="0 0 24 24" 
        stroke="currentColor"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </button>
    
    {#if isOpen}
      <div 
        bind:this={dropdownElement}
        class="absolute z-10 mt-1 w-full bg-white rounded-md shadow-lg max-h-60 overflow-auto border border-gray-200 focus:outline-none"
        transition:fade={{ duration: 150 }}
        role="listbox"
        tabindex="-1"
      >
        <ul class="py-1">
          {#each options as option (option.value)}
            <li 
              class="cursor-pointer text-gray-900 relative select-none py-2 pl-3 pr-9 hover:bg-gray-100 {value === option.value ? 'bg-primary-blue/10' : ''}"
              role="option"
              aria-selected={value === option.value}
              on:click={() => selectOption(option)}
            >
              <div class="flex items-center">
                {#if option.icon}
                  <div class="mr-3 flex-shrink-0 h-5 w-5 text-gray-400">
                    <svelte:component this={option.icon} />
                  </div>
                {/if}
                <span class="block truncate {value === option.value ? 'font-medium' : 'font-normal'}">
                  {option.label}
                </span>
              </div>
              
              {#if value === option.value}
                <span class="absolute inset-y-0 right-0 flex items-center pr-4 text-primary-blue">
                  <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                  </svg>
                </span>
              {/if}
            </li>
          {/each}
          
          {#if options.length === 0}
            <li class="text-gray-500 py-2 px-3 text-center italic">
              No options available
            </li>
          {/if}
        </ul>
      </div>
    {/if}
  </div>