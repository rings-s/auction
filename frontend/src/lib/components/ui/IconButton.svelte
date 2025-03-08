<!-- src/lib/components/ui/IconButton.svelte -->
<script>
    /**
     * Modern IconButton component with animations for the GUDIC platform
     */
    import { createEventDispatcher } from 'svelte';
    import { fade } from 'svelte/transition';
    import Icon from './Icon.svelte';
    
    // Props
    export let icon = null; // Icon component or name string
    export let variant = 'default'; // primary, white, glass, gradient, outline, ghost
    export let size = 'md'; // xs, sm, md, lg, xl
    export let shape = 'circle'; // circle, square, rounded
    export let disabled = false;
    export let loading = false;
    export let href = undefined; // Optional URL for link buttons
    export let target = undefined; // Optional target for links
    export let rel = undefined; // Optional rel for links
    export let tooltipText = ''; // Optional tooltip text
    export let tooltipPosition = 'top'; // top, bottom, left, right
    export let fullWidth = false; // Whether to take full width
    export let ariaLabel = ''; // Accessibility label
    export let color = ''; // Custom color override
    export let badge = undefined; // Optional badge content
  
    // Internal state
    let showTooltip = false;
    let tooltipRef;
    let buttonRef;
    
    // Event dispatcher
    const dispatch = createEventDispatcher();
    
    // Variant styles based on new color palette
    $: variantClasses = {
      primary: 'bg-gradient-to-r from-secondary-blue to-secondary-peach text-white shadow-md hover:shadow-lg',
      white: 'bg-white text-secondary-blue hover:bg-neutral-50 shadow-md',
      glass: 'bg-white/20 backdrop-filter backdrop-blur-lg text-white border border-white/30 hover:bg-white/30',
      gradient: 'bg-gradient-to-r from-primary-blue to-primary-peach text-text-dark hover:shadow-md',
      outline: 'bg-transparent border-2 border-secondary-blue text-secondary-blue hover:bg-primary-blue/10',
      ghost: 'bg-transparent hover:bg-primary-blue/10 text-text-medium',
    }[variant] || 'bg-neutral-100 text-text-dark hover:bg-neutral-200';
    
    // Size classes
    $: sizeClasses = {
      xs: 'h-6 w-6 p-0.5',
      sm: 'h-8 w-8 p-1.5',
      md: 'h-10 w-10 p-2',
      lg: 'h-12 w-12 p-2.5',
      xl: 'h-14 w-14 p-3',
    }[size] || 'h-10 w-10 p-2';
    
    // Icon size classes
    $: iconSizeClasses = {
      xs: 'h-4 w-4',
      sm: 'h-5 w-5',
      md: 'h-5 w-5',
      lg: 'h-6 w-6',
      xl: 'h-7 w-7',
    }[size] || 'h-5 w-5';
    
    // Shape classes
    $: shapeClasses = {
      circle: 'rounded-full',
      square: 'rounded-none',
      rounded: 'rounded-lg',
    }[shape] || 'rounded-full';
    
    // Tooltip position classes
    $: tooltipPositionClasses = {
      top: 'bottom-full left-1/2 transform -translate-x-1/2 mb-2',
      bottom: 'top-full left-1/2 transform -translate-x-1/2 mt-2',
      left: 'right-full top-1/2 transform -translate-y-1/2 mr-2',
      right: 'left-full top-1/2 transform -translate-y-1/2 ml-2',
    }[tooltipPosition] || 'bottom-full left-1/2 transform -translate-x-1/2 mb-2';
    
    // Disabled state
    $: disabledClasses = disabled || loading 
      ? 'opacity-50 cursor-not-allowed pointer-events-none'
      : '';
      
    // Width class
    $: widthClass = fullWidth ? 'w-full' : '';
    
    // Combined classes
    $: btnClasses = `
      inline-flex items-center justify-center
      font-medium
      transition-all duration-300
      focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-secondary-blue
      ${variantClasses} 
      ${sizeClasses} 
      ${shapeClasses}
      ${disabledClasses}
      ${widthClass}
      relative
      transform hover:scale-[1.05] active:scale-[0.98]
    `;
    
    // Handle tooltip display
    function showTooltipHandler() {
      if (tooltipText && !disabled) {
        showTooltip = true;
      }
    }
    
    function hideTooltipHandler() {
      showTooltip = false;
    }
    
    // Handle click event
    function handleClick(event) {
      if (disabled || loading) {
        event.preventDefault();
        return;
      }
      
      dispatch('click', event);
    }
    
    // Determine component type based on href
    $: component = href ? 'a' : 'button';
    
    // Determine aria label
    $: accessibilityLabel = ariaLabel || tooltipText || 'Button';
  </script>
  
  <!-- If the button is a link -->
  {#if component === 'a'}
    <a
      {href}
      class={btnClasses}
      {target}
      {rel}
      aria-label={accessibilityLabel}
      on:click={handleClick}
      on:mouseenter={showTooltipHandler}
      on:mouseleave={hideTooltipHandler}
      on:focus={showTooltipHandler}
      on:blur={hideTooltipHandler}
      {disabled}
      bind:this={buttonRef}
      style={color ? `--button-color: ${color};` : ''}
      {...$$restProps}
    >
      <!-- Loading spinner -->
      {#if loading}
        <div class="animate-spin">
          <svg xmlns="http://www.w3.org/2000/svg" class={iconSizeClasses} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 12a9 9 0 1 1-6.219-8.56" />
          </svg>
        </div>
      <!-- Icon -->
      {:else}
        {#if typeof icon === 'string'}
          <Icon name={icon} size={size} />
        {:else}
          <svelte:component this={icon} class={iconSizeClasses} />
        {/if}
      {/if}
      
      <!-- Badge -->
      {#if badge !== undefined}
        <span class="absolute -top-1 -right-1 bg-red-500 text-white text-xs font-bold rounded-full h-5 min-w-[1.25rem] flex items-center justify-center px-1">
          {badge}
        </span>
      {/if}
      
      <!-- Tooltip -->
      {#if showTooltip && tooltipText}
        <div 
          class="absolute z-50 px-2 py-1 text-xs font-medium text-white bg-text-dark rounded shadow-lg whitespace-nowrap pointer-events-none {tooltipPositionClasses}"
          in:fade={{ duration: 150 }}
          bind:this={tooltipRef}
        >
          {tooltipText}
        </div>
      {/if}
    </a>
  <!-- If the button is a button -->
  {:else}
    <button
      type="button"
      class={btnClasses}
      {disabled}
      aria-label={accessibilityLabel}
      on:click={handleClick}
      on:mouseenter={showTooltipHandler}
      on:mouseleave={hideTooltipHandler}
      on:focus={showTooltipHandler}
      on:blur={hideTooltipHandler}
      bind:this={buttonRef}
      style={color ? `--button-color: ${color};` : ''}
      {...$$restProps}
    >
      <!-- Loading spinner -->
      {#if loading}
        <div class="animate-spin">
          <svg xmlns="http://www.w3.org/2000/svg" class={iconSizeClasses} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 12a9 9 0 1 1-6.219-8.56" />
          </svg>
        </div>
      <!-- Icon -->
      {:else}
        {#if typeof icon === 'string'}
          <Icon name={icon} size={size} />
        {:else}
          <svelte:component this={icon} class={iconSizeClasses} />
        {/if}
      {/if}
      
      <!-- Badge -->
      {#if badge !== undefined}
        <span class="absolute -top-1 -right-1 bg-red-500 text-white text-xs font-bold rounded-full h-5 min-w-[1.25rem] flex items-center justify-center px-1">
          {badge}
        </span>
      {/if}
      
      <!-- Tooltip -->
      {#if showTooltip && tooltipText}
        <div 
          class="absolute z-50 px-2 py-1 text-xs font-medium text-white bg-text-dark rounded shadow-lg whitespace-nowrap pointer-events-none {tooltipPositionClasses}"
          in:fade={{ duration: 150 }}
          bind:this={tooltipRef}
        >
          {tooltipText}
        </div>
      {/if}
    </button>
  {/if}
  
  <style>
    button, a {
      position: relative;
      overflow: hidden;
    }
    
    button::after, a::after {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: linear-gradient(rgba(255, 255, 255, 0), rgba(255, 255, 255, 0.2), rgba(255, 255, 255, 0));
      transform: translateX(-100%) rotate(45deg);
      transition: transform 0.6s;
    }
    
    button:hover::after, a:hover::after {
      transform: translateX(100%) rotate(45deg);
    }
    
    /* Animation for loading spinner */
    @keyframes spin {
      to {
        transform: rotate(360deg);
      }
    }
    
    .animate-spin {
      animation: spin 1s linear infinite;
    }
    
    /* Custom colors */
    button[style*="--button-color"], a[style*="--button-color"] {
      color: var(--button-color);
      border-color: var(--button-color);
    }
    
    button.bg-transparent[style*="--button-color"]:hover, 
    a.bg-transparent[style*="--button-color"]:hover {
      background-color: color-mix(in srgb, var(--button-color) 10%, transparent);
    }
  </style>