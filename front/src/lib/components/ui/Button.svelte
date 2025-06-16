<!-- src/lib/components/ui/Button.svelte -->
<script>
  import { createEventDispatcher } from 'svelte';
  
  const dispatch = createEventDispatcher();
  
  // Props
  /** @type {'primary' | 'secondary' | 'outline' | 'danger' | 'success' | 'ghost'} */
  export let variant = 'primary'; 
  /** @type {'sm' | 'default' | 'large'} */
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
  export let rounded = 'default'; // 'default' | 'full'
  
  // Export "class" prop as "class_" because "class" is a reserved word
  export { class_ as class };
  
  // Simplified variant classes matching auction/properties pages
  const variants = {
    primary: `
      bg-primary-600 hover:bg-primary-700 
      text-white 
      border border-transparent
      shadow-sm hover:shadow-md
      focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500
      dark:bg-primary-600 dark:hover:bg-primary-700
    `,
    secondary: `
      bg-white hover:bg-gray-50 
      text-gray-700 
      border border-gray-300
      shadow-sm hover:shadow-md
      focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500
      dark:bg-gray-800 dark:hover:bg-gray-700
      dark:text-gray-300 dark:border-gray-600
    `,
    outline: `
      bg-white hover:bg-gray-50 
      text-gray-700 
      border border-gray-300
      shadow-sm hover:shadow-md
      focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500
      dark:bg-gray-800 dark:hover:bg-gray-700
      dark:text-gray-300 dark:border-gray-600
    `,
    danger: `
      bg-red-600 hover:bg-red-700 
      text-white 
      border border-transparent
      shadow-sm hover:shadow-md
      focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500
      dark:bg-red-600 dark:hover:bg-red-700
    `,
    success: `
      bg-green-600 hover:bg-green-700 
      text-white 
      border border-transparent
      shadow-sm hover:shadow-md
      focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500
      dark:bg-green-600 dark:hover:bg-green-700
    `,
    ghost: `
      bg-transparent hover:bg-gray-100 
      text-gray-700 
      border border-transparent
      focus:outline-none focus:ring-2 focus:ring-gray-500 focus:border-gray-500
      dark:hover:bg-gray-800
      dark:text-gray-300
    `
  };
  
  // Simplified size classes
  const sizes = {
    sm: `
      px-3 py-1.5 
      text-sm font-medium
    `,
    default: `
      px-4 py-2.5 
      text-sm font-medium
    `,
    large: `
      px-6 py-3 
      text-base font-medium
    `
  };
  
  // Border radius options
  const roundedStyles = {
    default: 'rounded-lg',
    full: 'rounded-full'
  };
  
  // Base classes
  const baseClasses = `
    inline-flex items-center justify-center
    font-medium
    transition-all duration-200
    relative
  `;
  
  // State classes
  $: stateClasses = (() => {
    if (disabled || loading) {
      return 'opacity-50 cursor-not-allowed';
    }
    return 'transform hover:-translate-y-0.5';
  })();
  
  // Generate final class string
  $: buttonClass = [
    baseClasses,
    sizes[size] || sizes.default,
    variants[variant] || variants.primary,
    roundedStyles[rounded] || roundedStyles.default,
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
</script>

{#if href}
  <a
    {href}
    {target}
    {rel}
    class={buttonClass}
    aria-disabled={disabled || loading}
    tabindex={disabled || loading ? -1 : 0}
    on:click={handleClick}
    role="button"
  >
    {#if loading}
      <svg 
        class="animate-spin h-4 w-4 {$$slots.default ? 'mr-2' : ''}" 
        xmlns="http://www.w3.org/2000/svg" 
        fill="none" 
        viewBox="0 0 24 24"
      >
        <circle 
          class="opacity-25" 
          cx="12" 
          cy="12" 
          r="10" 
          stroke="currentColor" 
          stroke-width="4"
        ></circle>
        <path 
          class="opacity-75" 
          fill="currentColor" 
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        ></path>
      </svg>
    {/if}
    <slot></slot>
  </a>
{:else}
  <button
    {type}
    {disabled}
    class={buttonClass}
    aria-disabled={disabled || loading}
    on:click={handleClick}
  >
    {#if loading}
      <svg 
        class="animate-spin h-4 w-4 {$$slots.default ? 'mr-2' : ''}" 
        xmlns="http://www.w3.org/2000/svg" 
        fill="none" 
        viewBox="0 0 24 24"
      >
        <circle 
          class="opacity-25" 
          cx="12" 
          cy="12" 
          r="10" 
          stroke="currentColor" 
          stroke-width="4"
        ></circle>
        <path 
          class="opacity-75" 
          fill="currentColor" 
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        ></path>
      </svg>
    {/if}
    <slot></slot>
  </button>
{/if}

<style>
  /* RTL support for loading spinner */
  :global([dir="rtl"]) .mr-2 {
    margin-right: 0;
    margin-left: 0.5rem;
  }
  
  /* Reduced motion support */
  @media (prefers-reduced-motion: reduce) {
    :global(button),
    :global(a[role="button"]) {
      transition: none !important;
    }
    
    :global(button:hover),
    :global(a[role="button"]:hover) {
      transform: none !important;
    }
    
    :global(.animate-spin) {
      animation: none !important;
    }
  }
</style>