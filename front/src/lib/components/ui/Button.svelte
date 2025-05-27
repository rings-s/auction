<!-- src/lib/components/ui/Button.svelte -->
<script>
  import { createEventDispatcher } from 'svelte';
  
  const dispatch = createEventDispatcher();
  
  // Props
  /** @type {'primary' | 'secondary' | 'outline' | 'danger' | 'success' | 'ghost'} */
  export let variant = 'primary'; 
  /** @type {'compact' | 'default' | 'large'} */
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
  
  // Export "class" prop as "class_" because "class" is a reserved word
  export { class_ as class };
  
  // Modern variant classes with subtle shadows and elevated look
  const variants = {
    primary: `
      bg-gradient-to-b from-blue-500 to-blue-600 
      hover:from-blue-600 hover:to-blue-700 
      active:from-blue-700 active:to-blue-800
      text-white border-0
      shadow-sm hover:shadow-md active:shadow-sm
      focus:ring-2 focus:ring-blue-500/40 focus:ring-offset-2
      dark:from-blue-600 dark:to-blue-700 
      dark:hover:from-blue-700 dark:hover:to-blue-800
    `,
    secondary: `
      bg-gradient-to-b from-slate-100 to-slate-200 
      hover:from-slate-200 hover:to-slate-300 
      active:from-slate-300 active:to-slate-400
      text-slate-700 border border-slate-300/50
      shadow-sm hover:shadow-md active:shadow-sm
      focus:ring-2 focus:ring-slate-500/40 focus:ring-offset-2
      dark:from-slate-700 dark:to-slate-800 
      dark:hover:from-slate-600 dark:hover:to-slate-700
      dark:text-slate-200 dark:border-slate-600/50
    `,
    outline: `
      bg-white/80 hover:bg-white 
      active:bg-slate-50
      text-slate-600 hover:text-slate-700
      border border-slate-300/60 hover:border-slate-400/80
      shadow-sm hover:shadow-md active:shadow-sm
      focus:ring-2 focus:ring-blue-500/40 focus:ring-offset-2
      backdrop-blur-sm
      dark:bg-slate-800/80 dark:hover:bg-slate-800
      dark:text-slate-300 dark:border-slate-600/60
    `,
    danger: `
      bg-gradient-to-b from-red-500 to-red-600 
      hover:from-red-600 hover:to-red-700 
      active:from-red-700 active:to-red-800
      text-white border-0
      shadow-sm hover:shadow-md active:shadow-sm
      focus:ring-2 focus:ring-red-500/40 focus:ring-offset-2
      dark:from-red-600 dark:to-red-700
    `,
    success: `
      bg-gradient-to-b from-emerald-500 to-emerald-600 
      hover:from-emerald-600 hover:to-emerald-700 
      active:from-emerald-700 active:to-emerald-800
      text-white border-0
      shadow-sm hover:shadow-md active:shadow-sm
      focus:ring-2 focus:ring-emerald-500/40 focus:ring-offset-2
      dark:from-emerald-600 dark:to-emerald-700
    `,
    ghost: `
      bg-transparent hover:bg-slate-100/80 
      active:bg-slate-200/80
      text-slate-600 hover:text-slate-700
      border-0
      focus:ring-2 focus:ring-slate-500/40 focus:ring-offset-2
      dark:hover:bg-slate-800/80 dark:active:bg-slate-700/80
      dark:text-slate-400 dark:hover:text-slate-300
    `
  };
  
  // Compact, touch-friendly size classes (min 40x40px touch targets)
  const sizes = {
    compact: `
      min-h-[40px] px-3 py-2 
      text-xs font-semibold 
      gap-1.5
    `,
    default: `
      min-h-[44px] px-4 py-2.5 
      text-sm font-semibold 
      gap-2
    `,
    large: `
      min-h-[48px] px-6 py-3 
      text-base font-semibold 
      gap-2.5
    `
  };
  
  // Modern border radius (8-12px range)
  const borderRadius = 'rounded-xl'; // 12px
  
  // Base classes with modern styling principles
  const baseClasses = `
    inline-flex items-center justify-center
    font-semibold leading-tight tracking-wide
    focus:outline-none 
    transition-all duration-200 ease-out
    select-none relative overflow-hidden
    ${borderRadius}
  `;
  
  // Enhanced state classes with smooth micro-interactions
  $: stateClasses = (() => {
    if (disabled || loading) {
      return 'opacity-60 cursor-not-allowed pointer-events-none';
    }
    return `
      cursor-pointer
      transform hover:scale-[1.02] hover:-translate-y-0.5 
      active:scale-[0.98] active:translate-y-0
    `;
  })();
  
  // Generate final class string
  $: buttonClass = [
    baseClasses,
    sizes[size] || sizes.default,
    variants[variant] || variants.primary,
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
    aria-disabled={disabled}
    tabindex={disabled ? -1 : 0}
    on:click={handleClick}
    role="button"
  >
    <!-- Subtle shine effect overlay for elevated look -->
    <div class="absolute inset-0 bg-gradient-to-b from-white/20 to-transparent opacity-0 hover:opacity-100 transition-opacity duration-200 {borderRadius}" aria-hidden="true"></div>
    
    <!-- Content container -->
    <div class="relative z-10 flex items-center justify-center gap-inherit">
      <!-- Left Icon or Loading Spinner -->
      {#if loading}
        <svg class="animate-spin w-4 h-4 text-current" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      {:else if iconLeft}
        <span class="flex items-center justify-center flex-shrink-0">
          {@html iconLeft}
        </span>
      {/if}
      
      <!-- Button Content -->
      <span class="flex items-center justify-center" class:sr-only={loading && !$$slots.default}>
        <slot></slot>
      </span>
      
      <!-- Right Icon -->
      {#if iconRight && !loading}
        <span class="flex items-center justify-center flex-shrink-0">
          {@html iconRight}
        </span>
      {/if}
    </div>
  </a>
{:else}
  <button
    {type}
    {disabled}
    class={buttonClass}
    aria-disabled={disabled}
    on:click={handleClick}
  >
    <!-- Subtle shine effect overlay for elevated look -->
    <div class="absolute inset-0 bg-gradient-to-b from-white/20 to-transparent opacity-0 hover:opacity-100 transition-opacity duration-200 {borderRadius}" aria-hidden="true"></div>
    
    <!-- Content container -->
    <div class="relative z-10 flex items-center justify-center gap-inherit">
      <!-- Left Icon or Loading Spinner -->
      {#if loading}
        <svg class="animate-spin w-4 h-4 text-current" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      {:else if iconLeft}
        <span class="flex items-center justify-center flex-shrink-0">
          {@html iconLeft}
        </span>
      {/if}
      
      <!-- Button Content -->
      <span class="flex items-center justify-center" class:sr-only={loading && !$$slots.default}>
        <slot></slot>
      </span>
      
      <!-- Right Icon -->
      {#if iconRight && !loading}
        <span class="flex items-center justify-center flex-shrink-0">
          {@html iconRight}
        </span>
      {/if}
    </div>
  </button>
{/if}

<style>
  /* Enhanced icon styling */
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
  
  /* Enhanced focus styles for better accessibility */
  :global(button:focus-visible),
  :global(a[role="button"]:focus-visible) {
    outline: 2px solid transparent;
    outline-offset: 2px;
  }
  
  /* High contrast mode support */
  @media (prefers-contrast: high) {
    :global(button),
    :global(a[role="button"]) {
      border-width: 2px !important;
      box-shadow: none !important;
    }
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
  
  /* Touch device optimizations */
  @media (pointer: coarse) {
    :global(button),
    :global(a[role="button"]) {
      min-height: 44px;
    }
  }
</style>