<script>
  /**
   * Enhanced Button component with distinct typography for the GUDIC platform
   */
  export let type = 'button';
  export let variant = 'primary'; // primary, white, glass, gradient, outline
  export let size = 'md'; // sm, md, lg, xl
  export let disabled = false;
  export let loading = false;
  export let fullWidth = false;
  export let icon = null;
  export let iconPosition = 'left';
  export let rounded = 'default'; // default, pill, square
  export let onClick = () => {};

  // Size classes with enhanced typographic contrast
  $: sizeClasses = {
    sm: 'text-xs py-1.5 px-3 h-8',
    md: 'text-sm py-2 px-4 h-10',
    lg: 'text-base py-2.5 px-5 h-12',
    xl: 'text-lg py-3 px-6 h-14',
  };
  
  // Rounded styles
  $: roundedClasses = {
    default: 'rounded-lg',
    pill: 'rounded-full',
    square: 'rounded-none'
  };
  
  // Disabled state
  $: disabledClasses = disabled || loading 
    ? 'opacity-60 cursor-not-allowed pointer-events-none'
    : '';
    
  // Width class
  $: widthClass = fullWidth ? 'w-full' : '';
  
  // Combined classes, using component-text class for typography contrast
  $: btnClasses = `
    component-text
    inline-flex items-center justify-center 
    font-semibold
    transition-all duration-300
    focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-component-primary
    ${sizeClasses[size]} 
    ${roundedClasses[rounded]}
    ${disabledClasses}
    ${widthClass}
    transform hover:scale-[1.02] active:scale-[0.98]
  `;
  
  // Apply specific variant styles
  $: variantStyles = getVariantStyles(variant);
  
  function getVariantStyles(variant) {
    switch(variant) {
      case 'primary':
        return 'bg-gradient-to-r from-component-primary to-component-secondary text-black shadow-md hover:shadow-lg';
      case 'white':
        return 'bg-white text-component-primary hover:bg-gray-50 shadow-md';
      case 'glass':
        return 'bg-white/20 backdrop-filter backdrop-blur-lg text-white border border-white/30 hover:bg-white/30';
      case 'gradient':
        return 'bg-gradient-to-r from-primary-blue to-primary-peach text-component-text-dark hover:shadow-md';
      case 'outline':
        return 'bg-transparent border-2 border-component-primary text-component-primary hover:bg-component-primary/5';
      default:
        return 'bg-gradient-to-r from-component-primary to-component-secondary text-white shadow-md hover:shadow-lg';
    }
  }
</script>

<button
  {type}
  class="{btnClasses} {variantStyles}"
  {disabled}
  on:click={onClick}
  {...$$restProps}
>
  {#if loading}
    <span class="mr-2 animate-spin">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M21 12a9 9 0 1 1-6.219-8.56" />
      </svg>
    </span>
    <span>Loading...</span>
  {:else}
    {#if icon && iconPosition === 'left'}
      <span class="mr-2">
        <svelte:component this={icon} class="h-5 w-5" />
      </span>
    {/if}
    
    <slot />
    
    {#if icon && iconPosition === 'right'}
      <span class="ml-2">
        <svelte:component this={icon} class="h-5 w-5" />
      </span>
    {/if}
  {/if}
</button>

<style>
  button {
    position: relative;
    overflow: hidden;
    /* Ensure typographic contrast with a font override */
    font-family: 'Outfit', sans-serif;
    letter-spacing: 0.02em;
  }
  
  button::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(rgba(255, 255, 255, 0), rgba(255, 255, 255, 0.3), rgba(255, 255, 255, 0));
    transform: translateX(-100%) rotate(45deg);
    transition: transform 0.6s;
  }
  
  button:hover::after {
    transform: translateX(100%) rotate(45deg);
  }
  
  /* Enhanced loading animation */
  .animate-spin {
    animation: spin 1s linear infinite;
  }
  
  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
</style>