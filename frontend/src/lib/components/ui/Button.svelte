<!-- src/lib/components/ui/Button.svelte -->
<script>
  /**
   * Button Component
   * A versatile button component with various styles, sizes, and states.
   */
  
  // Button props
  export let type = 'button'; // button, submit, reset
  export let variant = 'primary'; // primary, secondary, success, error, warning, info, outline, ghost, link
  export let size = 'md'; // sm, md, lg
  export let fullWidth = false;
  export let disabled = false;
  export let loading = false;
  export let href = ''; // If provided, renders as <a> instead of <button>
  export let target = ''; // For <a> tags: _blank, _self, etc.
  export let rel = ''; // For <a> tags
  export let ariaLabel = undefined; // Accessibility label
  export let highContrast = false; // Higher contrast version for better visibility
  
  // Get the base style classes that are shared between <button> and <a>
  $: baseClasses = [
    // Core classes
    "inline-flex items-center justify-center rounded-md border font-medium transition-colors focus:outline-none",
    
    // Size classes
    size === 'sm' ? 'px-2 py-1 text-xs' : 
    size === 'lg' ? 'px-6 py-3 text-base' : 
    'px-4 py-2 text-sm', // Default md
    
    // Width
    fullWidth ? 'w-full' : 'w-auto',
    
    // State classes
    disabled ? 'cursor-not-allowed opacity-50' : 'cursor-pointer',
    
    // Variant classes
    variant === 'primary' && !outline 
      ? highContrast 
        ? 'bg-primary-dark hover:bg-primary border border-primary-light text-white hover:shadow-lg' 
        : 'bg-primary hover:bg-primary-dark text-white'
      : '',
    
    variant === 'secondary' && !outline 
      ? highContrast 
        ? 'bg-cosmos-text-default hover:bg-cosmos-text-muted text-cosmos-bg-dark border border-cosmos-text'
        : 'bg-cosmos-bg-light hover:bg-cosmos-text-dim text-cosmos-text hover:text-cosmos-bg'
      : '',
    
    variant === 'success' && !outline 
      ? highContrast 
        ? 'bg-status-success hover:bg-green-700 text-white border border-green-600'
        : 'bg-status-success hover:bg-green-600 text-white'
      : '',
    
    variant === 'error' && !outline 
      ? highContrast 
        ? 'bg-status-error hover:bg-red-700 text-white border border-red-600'
        : 'bg-status-error hover:bg-red-600 text-white'
      : '',
    
    variant === 'warning' && !outline 
      ? highContrast 
        ? 'bg-status-warning hover:bg-yellow-600 text-white border border-yellow-500'
        : 'bg-status-warning hover:bg-yellow-500 text-white'
      : '',
    
    variant === 'info' && !outline 
      ? highContrast 
        ? 'bg-status-info hover:bg-blue-700 text-white border border-blue-600'
        : 'bg-status-info hover:bg-blue-600 text-white'
      : '',
    
    variant === 'transparent' ? 'bg-transparent hover:bg-cosmos-bg-light text-cosmos-text-muted hover:text-cosmos-text' : '',
    
    // Outline variants
    variant === 'primary' && outline ? 'border-primary text-primary hover:bg-primary hover:text-white hover:bg-opacity-90' : '',
    variant === 'secondary' && outline ? 'border-cosmos-text-muted text-cosmos-text-muted hover:bg-cosmos-text-muted hover:text-cosmos-bg hover:bg-opacity-90' : '',
    variant === 'success' && outline ? 'border-status-success text-status-success hover:bg-status-success hover:text-white hover:bg-opacity-90' : '',
    variant === 'error' && outline ? 'border-status-error text-status-error hover:bg-status-error hover:text-white hover:bg-opacity-90' : '',
    variant === 'warning' && outline ? 'border-status-warning text-status-warning hover:bg-status-warning hover:text-white hover:bg-opacity-90' : '',
    variant === 'info' && outline ? 'border-status-info text-status-info hover:bg-status-info hover:text-white hover:bg-opacity-90' : '',
    
    variant === 'link' ? 'border-transparent bg-transparent text-primary hover:underline px-0 py-0' : '',
    variant === 'ghost' ? 'border-transparent bg-transparent hover:bg-cosmos-bg-light text-cosmos-text' : '',
  ].filter(Boolean).join(' ');
  
  // Generate focus ring classes for button
  $: focusRingClasses = [
    'focus:ring-2 focus:ring-offset-2',
    variant === 'primary' ? 'focus:ring-primary focus:ring-opacity-50' : '',
    variant === 'success' ? 'focus:ring-status-success focus:ring-opacity-50' : '',
    variant === 'error' ? 'focus:ring-status-error focus:ring-opacity-50' : '',
    variant === 'warning' ? 'focus:ring-status-warning focus:ring-opacity-50' : '',
    variant === 'info' ? 'focus:ring-status-info focus:ring-opacity-50' : '',
  ].filter(Boolean).join(' ');
</script>

{#if href}
  <!-- Render as anchor when href is provided -->
  <a
    {href}
    {target}
    {rel}
    role="button"
    class={baseClasses}
    class:pointer-events-none={disabled}
    aria-disabled={disabled}
    aria-label={ariaLabel}
    on:click
    on:focus
    on:blur
    on:mouseenter
    on:mouseleave
    {...$$restProps}
  >
    {#if loading}
      <svg class="mr-2 h-4 w-4 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" aria-hidden="true">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
    {/if}
    <slot></slot>
  </a>
{:else}
  <!-- Render as button by default -->
  <button
    {type}
    class="{baseClasses} {focusRingClasses}"
    disabled={disabled || loading}
    aria-disabled={disabled || loading}
    aria-label={ariaLabel}
    on:click
    on:focus
    on:blur
    on:mouseenter
    on:mouseleave
    {...$$restProps}
  >
    {#if loading}
      <svg class="mr-2 h-4 w-4 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" aria-hidden="true">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
    {/if}
    <slot></slot>
  </button>
{/if}