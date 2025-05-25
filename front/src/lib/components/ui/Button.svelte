<!-- src/lib/components/ui/Button.svelte -->
<script>
  import { createEventDispatcher } from 'svelte';
  
  const dispatch = createEventDispatcher();
  
  // Props
  /** @type {'primary' | 'secondary' | 'outline' | 'danger' | 'success' | 'ghost'} */
  export let variant = 'primary'; 
  /** @type {'small' | 'default' | 'large' | 'xl'} */
  export let size = 'default'; 
  /** @type {'button' | 'submit' | 'reset'} */
  export let type = 'button'; 
  export let disabled = false;
  export let loading = false;
  export let fullWidth = false;
  export let href = null;
  export let target = null;
  export let rel = null;
  export let onClick = null;
  export let class_ = '';
  export let iconLeft = null;
  export let iconRight = null;
  export let rounded = 'default'; // 'none' | 'default' | 'full'
  
  // Export "class" prop as "class_" because "class" is a reserved word
  export { class_ as class };
  
  // Define variant classes with dark mode support
  const variants = {
    primary: `
      bg-primary-600 hover:bg-primary-700 active:bg-primary-800
      focus:ring-primary-500 focus:ring-opacity-50
      text-white border border-transparent
      shadow-sm hover:shadow-md active:shadow-sm
      dark:bg-primary-500 dark:hover:bg-primary-600 dark:active:bg-primary-700
    `,
    secondary: `
      bg-secondary-600 hover:bg-secondary-700 active:bg-secondary-800
      focus:ring-secondary-500 focus:ring-opacity-50
      text-white border border-transparent
      shadow-sm hover:shadow-md active:shadow-sm
      dark:bg-secondary-500 dark:hover:bg-secondary-600 dark:active:bg-secondary-700
    `,
    outline: `
      bg-white hover:bg-gray-50 active:bg-gray-100
      text-gray-700 border border-gray-300 hover:border-gray-400
      focus:ring-primary-500 focus:ring-opacity-50
      shadow-sm hover:shadow-md active:shadow-sm
      dark:bg-gray-800 dark:hover:bg-gray-700 dark:active:bg-gray-600
      dark:text-gray-200 dark:border-gray-600 dark:hover:border-gray-500
    `,
    danger: `
      bg-red-600 hover:bg-red-700 active:bg-red-800
      focus:ring-red-500 focus:ring-opacity-50
      text-white border border-transparent
      shadow-sm hover:shadow-md active:shadow-sm
      dark:bg-red-500 dark:hover:bg-red-600 dark:active:bg-red-700
    `,
    success: `
      bg-green-600 hover:bg-green-700 active:bg-green-800
      focus:ring-green-500 focus:ring-opacity-50
      text-white border border-transparent
      shadow-sm hover:shadow-md active:shadow-sm
      dark:bg-green-500 dark:hover:bg-green-600 dark:active:bg-green-700
    `,
    ghost: `
      bg-transparent hover:bg-gray-100 active:bg-gray-200
      text-gray-700 border border-transparent
      focus:ring-primary-500 focus:ring-opacity-50
      dark:hover:bg-gray-800 dark:active:bg-gray-700
      dark:text-gray-200
    `
  };
  
  // Define size classes
  const sizes = {
    small: 'px-3 py-1.5 text-xs gap-1.5',
    default: 'px-4 py-2 text-sm gap-2',
    large: 'px-6 py-3 text-base gap-2.5',
    xl: 'px-8 py-4 text-lg gap-3'
  };
  
  // Define rounded classes
  const roundedClasses = {
    none: 'rounded-none',
    default: 'rounded-lg',
    full: 'rounded-full'
  };
  
  // Base classes
  const baseClasses = `
    inline-flex items-center justify-center
    font-medium leading-tight
    focus:outline-none focus:ring-2 focus:ring-offset-2
    transition-all duration-200 ease-in-out
    select-none
  `;
  
  // State classes
  $: stateClasses = (() => {
    if (disabled || loading) {
      return 'opacity-50 cursor-not-allowed pointer-events-none';
    }
    return 'transform hover:-translate-y-0.5 active:translate-y-0 cursor-pointer';
  })();
  
  // Generate final class string
  $: buttonClass = [
    baseClasses,
    sizes[size] || sizes.default,
    variants[variant] || variants.primary,
    roundedClasses[rounded] || roundedClasses.default,
    fullWidth ? 'w-full' : '',
    stateClasses,
    class_
  ].filter(Boolean).join(' ').trim();
  
  // Handle click events
  function handleClick(event) {
    if (disabled || loading) {
      event.preventDefault();
      return;
    }
    
    if (onClick) {
      onClick(event);
    }
    
    dispatch('click', event);
  }
  
  // Loading spinner component
  function LoadingSpinner() {
    return `
      <svg class="animate-spin h-4 w-4 text-current" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
    `;
  }
</script>

{#if href}
  <a
    {href}
    {target}
    {rel}
    class={buttonClass}
    aria-disabled={disabled}
    tabindex={disabled ? -1 : 0}
    on:click={handleClick}
    role="button"
  >
    <!-- Left Icon or Loading Spinner -->
    {#if loading}
      <svg class="animate-spin h-4 w-4 text-current" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
    {:else if iconLeft}
      <span class="button-icon button-icon--left">
        {@html iconLeft}
      </span>
    {/if}
    
    <!-- Button Content -->
    <span class="button-content" class:sr-only={loading && !$$slots.default}>
      <slot></slot>
    </span>
    
    <!-- Right Icon -->
    {#if iconRight && !loading}
      <span class="button-icon button-icon--right">
        {@html iconRight}
      </span>
    {/if}
  </a>
{:else}
  <button
    {type}
    {disabled}
    class={buttonClass}
    aria-disabled={disabled}
    on:click={handleClick}
  >
    <!-- Left Icon or Loading Spinner -->
    {#if loading}
      <svg class="animate-spin h-4 w-4 text-current" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
    {:else if iconLeft}
      <span class="button-icon button-icon--left">
        {@html iconLeft}
      </span>
    {/if}
    
    <!-- Button Content -->
    <span class="button-content" class:sr-only={loading && !$$slots.default}>
      <slot></slot>
    </span>
    
    <!-- Right Icon -->
    {#if iconRight && !loading}
      <span class="button-icon button-icon--right">
        {@html iconRight}
      </span>
    {/if}
  </button>
{/if}

<style>
  /* Icon styling */
  :global(.button-icon) {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }
  
  :global(.button-icon svg) {
    width: 1em;
    height: 1em;
  }
  
  /* RTL support */
  :global(.rtl .button-icon--right) {
    order: -1;
  }
  
  :global(.rtl .button-icon--left) {
    order: 1;
  }
  
  /* Loading state content hiding */
  .sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
  }
  
  /* Focus styles for better accessibility */
  :global(button:focus-visible),
  :global(a[role="button"]:focus-visible) {
    outline: 2px solid transparent;
    outline-offset: 2px;
  }
  
  /* Improve contrast in high contrast mode */
  @media (prefers-contrast: high) {
    :global(button),
    :global(a[role="button"]) {
      border-width: 2px;
    }
  }
  
  /* Disable animations for users who prefer reduced motion */
  @media (prefers-reduced-motion: reduce) {
    :global(button),
    :global(a[role="button"]) {
      transition: none;
    }
    
    :global(button:hover),
    :global(a[role="button"]:hover) {
      transform: none;
    }
    
    :global(.animate-spin) {
      animation: none;
    }
  }
</style>