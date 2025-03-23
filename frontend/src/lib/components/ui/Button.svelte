<!-- src/lib/components/ui/Button.svelte -->
<script>
  // Button props
  export let type = 'button';
  export let variant = 'primary';
  export let size = 'md';
  export let fullWidth = false;
  export let disabled = false;
  export let loading = false;
  export let outline = false;
  export let href = '';
  export let target = '';
  export let rel = '';
  export let onClick = null;
  export let role = null;
  
  // For auth pages specifically
  export let highContrast = false;
  
  // Generate class based on variant
  $: variantClass = getVariantClass(variant, outline, highContrast);
  
  // Generate size class
  $: sizeClass = getSizeClass(size);
  
  // Generate width class
  $: widthClass = fullWidth ? 'w-full' : 'w-auto';
  
  // Generate variant class
  function getVariantClass(variant, outline, highContrast) {
    const variants = {
      primary: outline 
        ? 'border-primary text-primary hover:bg-primary hover:text-white hover:bg-opacity-90'
        : highContrast
          ? 'bg-primary-dark hover:bg-primary border border-primary-light text-white hover:shadow-lg' 
          : 'bg-primary hover:bg-primary-dark text-white',
      secondary: outline
        ? 'border-cosmos-text-muted text-cosmos-text-muted hover:bg-cosmos-text-muted hover:text-cosmos-bg hover:bg-opacity-90'
        : highContrast
          ? 'bg-cosmos-text-default hover:bg-cosmos-text-muted text-cosmos-bg-dark border border-cosmos-text'
          : 'bg-cosmos-bg-light hover:bg-cosmos-text-dim text-cosmos-text hover:text-cosmos-bg',
      success: outline
        ? 'border-status-success text-status-success hover:bg-status-success hover:text-white hover:bg-opacity-90'
        : highContrast
          ? 'bg-status-success hover:bg-green-700 text-white border border-green-600'
          : 'bg-status-success hover:bg-green-600 text-white',
      error: outline
        ? 'border-status-error text-status-error hover:bg-status-error hover:text-white hover:bg-opacity-90'
        : highContrast
          ? 'bg-status-error hover:bg-red-700 text-white border border-red-600'
          : 'bg-status-error hover:bg-red-600 text-white',
      warning: outline
        ? 'border-status-warning text-status-warning hover:bg-status-warning hover:text-white hover:bg-opacity-90'
        : highContrast
          ? 'bg-status-warning hover:bg-yellow-600 text-white border border-yellow-500'
          : 'bg-status-warning hover:bg-yellow-500 text-white',
      info: outline
        ? 'border-status-info text-status-info hover:bg-status-info hover:text-white hover:bg-opacity-90'
        : highContrast
          ? 'bg-status-info hover:bg-blue-700 text-white border border-blue-600'
          : 'bg-status-info hover:bg-blue-600 text-white',
      transparent: 'bg-transparent hover:bg-cosmos-bg-light text-cosmos-text-muted hover:text-cosmos-text'
    };
    
    return variants[variant] || variants.primary;
  }
  
  // Generate size class
  function getSizeClass(size) {
    const sizes = {
      sm: 'px-2 py-1 text-xs',
      md: 'px-4 py-2 text-sm',
      lg: 'px-6 py-3 text-base'
    };
    
    return sizes[size] || sizes.md;
  }
</script>

{#if href}
  <a
    {href}
    {target}
    {rel}
    class="{variantClass} {sizeClass} {widthClass} inline-flex items-center justify-center rounded-md border font-medium transition-colors focus:outline-none {disabled ? 'cursor-not-allowed opacity-50' : 'cursor-pointer'}"
    class:opacity-70={disabled}
    class:cursor-not-allowed={disabled}
    role={role || 'link'}
    on:click={onClick}
    {...$$restProps}
  >
    {#if loading}
      <svg class="mr-2 h-4 w-4 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
    {/if}
    <slot />
  </a>
{:else}
  <button
    {type}
    {disabled}
    class="{variantClass} {sizeClass} {widthClass} inline-flex items-center justify-center rounded-md border font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 {disabled ? 'cursor-not-allowed opacity-50' : 'cursor-pointer'}"
    class:ring-primary={variant === 'primary'}
    class:ring-status-success={variant === 'success'}
    class:ring-status-error={variant === 'error'}
    class:ring-status-warning={variant === 'warning'}
    class:ring-status-info={variant === 'info'}
    role={role || 'button'}
    on:click={onClick}
    {...$$restProps}
  >
    {#if loading}
      <svg class="mr-2 h-4 w-4 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
    {/if}
    <slot />
  </button>
{/if}