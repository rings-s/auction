<!-- src/lib/components/ui/Dropdown.svelte -->
<script>
    /**
     * Dropdown Component
     * A flexible dropdown menu with various positioning options.
     */
    import { createEventDispatcher, onMount, onDestroy } from 'svelte';
    import { fade, fly } from 'svelte/transition';
    import { clickOutside } from '$lib/actions/clickOutside';
    
    const dispatch = createEventDispatcher();
    
    // Props
    export let label = ''; // Button label
    export let items = []; // Array of items: { id, label, icon, disabled, separator, onClick }
    export let variant = 'default'; // default, primary, outline, ghost, link
    export let size = 'md'; // sm, md, lg
    export let position = 'bottom-start'; // top-start, top, top-end, right-start, right, right-end, bottom-start, bottom, bottom-end, left-start, left, left-end
    export let width = undefined; // Width of dropdown menu
    export let icon = undefined; // Icon component
    export let iconPosition = 'left'; // left, right
    export let disabled = false; // Disabled state
    export let fullWidth = false; // Full width dropdown
    export let closeOnClick = true; // Close dropdown when item clicked
    export let showArrow = true; // Show dropdown caret
    export let trigger = undefined; // Custom trigger slot
    
    // Local state
    let isOpen = false;
    let triggerEl;
    let dropdownEl;
    let firstFocusableEl;
    let lastFocusableEl;
    
    // Button variants
    const buttonVariants = {
      default: 'bg-white dark:bg-neutral-800 border border-neutral-300 dark:border-neutral-700 text-neutral-800 dark:text-neutral-200 hover:bg-neutral-50 dark:hover:bg-neutral-700',
      primary: 'bg-primary text-white hover:bg-primary-dark',
      outline: 'bg-transparent border border-primary text-primary hover:bg-primary hover:text-white',
      ghost: 'bg-transparent hover:bg-neutral-100 dark:hover:bg-neutral-800 text-neutral-700 dark:text-neutral-300',
      link: 'bg-transparent p-0 text-primary hover:underline',
    };
    
    // Size variants
    const sizeVariants = {
      sm: 'py-1.5 px-3 text-sm',
      md: 'py-2 px-4 text-base',
      lg: 'py-2.5 px-5 text-lg',
    };
    
    // Get positioning classes
    function getPositionClasses(pos) {
      const posMap = {
        'top-start': 'bottom-full left-0 mb-1',
        'top': 'bottom-full left-1/2 -translate-x-1/2 mb-1',
        'top-end': 'bottom-full right-0 mb-1',
        'right-start': 'left-full top-0 ml-1',
        'right': 'left-full top-1/2 -translate-y-1/2 ml-1',
        'right-end': 'left-full bottom-0 ml-1',
        'bottom-start': 'top-full left-0 mt-1',
        'bottom': 'top-full left-1/2 -translate-x-1/2 mt-1',
        'bottom-end': 'top-full right-0 mt-1',
        'left-start': 'right-full top-0 mr-1',
        'left': 'right-full top-1/2 -translate-y-1/2 mr-1',
        'left-end': 'right-full bottom-0 mr-1',
      };
      
      return posMap[pos] || posMap['bottom-start'];
    }
    
    // Toggle dropdown
    function toggle() {
      if (disabled) return;
      isOpen = !isOpen;
      
      if (isOpen) {
        dispatch('open');
        setTimeout(setFocusableElements, 100);
      } else {
        dispatch('close');
      }
    }
    
    // Close dropdown
    function close() {
      if (isOpen) {
        isOpen = false;
        dispatch('close');
      }
    }
    
    // Item click handler
    function handleItemClick(item) {
      if (item.disabled) return;
      
      if (item.onClick) {
        item.onClick();
      }
      
      dispatch('select', { item });
      
      if (closeOnClick) {
        close();
      }
    }
    
    // Set focusable elements for keyboard navigation
    function setFocusableElements() {
      if (!dropdownEl) return;
      
      const focusableElements = 'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])';
      const elements = dropdownEl.querySelectorAll(focusableElements);
      
      if (elements.length) {
        firstFocusableEl = elements[0];
        lastFocusableEl = elements[elements.length - 1];
        firstFocusableEl.focus();
      }
    }
    
    // Keyboard handling
    function handleKeydown(e) {
      if (!isOpen) return;
      
      switch (e.key) {
        case 'Escape':
          e.preventDefault();
          close();
          triggerEl.focus();
          break;
        case 'Tab':
          // Trap focus inside dropdown
          if (e.shiftKey && document.activeElement === firstFocusableEl) {
            e.preventDefault();
            lastFocusableEl.focus();
          } else if (!e.shiftKey && document.activeElement === lastFocusableEl) {
            e.preventDefault();
            firstFocusableEl.focus();
          }
          break;
        case 'ArrowDown':
          e.preventDefault();
          if (document.activeElement === lastFocusableEl) {
            firstFocusableEl.focus();
          } else {
            const nextSibling = document.activeElement.nextElementSibling;
            if (nextSibling) nextSibling.focus();
          }
          break;
        case 'ArrowUp':
          e.preventDefault();
          if (document.activeElement === firstFocusableEl) {
            lastFocusableEl.focus();
          } else {
            const prevSibling = document.activeElement.previousElementSibling;
            if (prevSibling) prevSibling.focus();
          }
          break;
      }
    }
    
    // Handle click outside
    function handleClickOutside() {
      close();
    }
    
    onMount(() => {
      // Add keyboard event listener
      window.addEventListener('keydown', handleKeydown);
    });
    
    onDestroy(() => {
      // Remove keyboard event listener
      window.removeEventListener('keydown', handleKeydown);
    });
  </script>
  
  <div 
    class={`relative inline-flex ${fullWidth ? 'w-full' : ''}`}
    use:clickOutside={handleClickOutside}
  >
    <!-- Dropdown trigger -->
    {#if trigger}
      <!-- Custom trigger -->
      <div bind:this={triggerEl} on:click={toggle}>
        <slot name="trigger"></slot>
      </div>
    {:else}
      <!-- Default button trigger -->
      <button
        type="button"
        bind:this={triggerEl}
        class={`inline-flex items-center justify-center rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:ring-opacity-50 
          ${buttonVariants[variant] || buttonVariants.default} 
          ${sizeVariants[size] || sizeVariants.md}
          ${fullWidth ? 'w-full' : ''}
          ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
        on:click={toggle}
        disabled={disabled}
        aria-haspopup="true"
        aria-expanded={isOpen}
      >
        {#if icon && iconPosition === 'left'}
          <svelte:component this={icon} class="mr-2 -ml-0.5 h-5 w-5" />
        {/if}
        
        {label}
        
        {#if icon && iconPosition === 'right'}
          <svelte:component this={icon} class="ml-2 -mr-0.5 h-5 w-5" />
        {/if}
        
        {#if showArrow}
          <svg class={`h-4 w-4 ${iconPosition === 'left' ? 'ml-2' : 'ml-2'} transition-transform ${isOpen ? 'rotate-180' : ''}`} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
          </svg>
        {/if}
      </button>
    {/if}
    
    <!-- Dropdown menu -->
    {#if isOpen}
      <div
        bind:this={dropdownEl}
        class={`absolute z-50 ${getPositionClasses(position)} min-w-[12rem] ${width ? `w-${width}` : (fullWidth ? 'w-full' : '')}`}
        transition:fly={{ duration: 200, y: 5 }}
        role="menu"
        aria-orientation="vertical"
        tabindex="-1"
      >
        <div class="overflow-hidden rounded-md bg-white dark:bg-neutral-800 shadow-lg ring-1 ring-black ring-opacity-5">
          <div class="py-1" role="none">
            {#each items as item}
              {#if item.separator}
                <div class="h-px bg-neutral-200 dark:bg-neutral-700 my-1" role="separator" aria-orientation="horizontal"></div>
              {:else}
                <button
                  type="button"
                  class={`flex w-full items-center px-4 py-2 text-sm ${item.disabled ? 'opacity-50 cursor-not-allowed text-neutral-400 dark:text-neutral-500' : 'text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-700 focus:bg-neutral-100 dark:focus:bg-neutral-700'}`}
                  role="menuitem"
                  disabled={item.disabled}
                  on:click={() => handleItemClick(item)}
                >
                  {#if item.icon}
                    <svelte:component this={item.icon} class="mr-3 h-5 w-5 text-neutral-500 dark:text-neutral-400" aria-hidden="true" />
                  {/if}
                  {item.label}
                </button>
              {/if}
            {/each}
          </div>
        </div>
      </div>
    {/if}
  </div>