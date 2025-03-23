<!-- src/lib/components/ui/Loader.svelte -->
<script>
    /**
     * Loader Component
     * Displays a configurable loading spinner
     */
    
    // Props
    export let size = "md"; // Size: xs, sm, md, lg, xl
    export let color = "primary"; // Color: primary, white, gray, success, error, warning, info
    export let type = "spinner"; // Type: spinner, dots, pulse
    export let centered = false; // Whether to center the loader in its container
    export let text = ""; // Optional loading text
    export let textPosition = "bottom"; // Text position: left, right, top, bottom
    
    // Size mapping for spinner width/height
    const sizeMap = {
      xs: "w-4 h-4",
      sm: "w-5 h-5",
      md: "w-8 h-8",
      lg: "w-12 h-12",
      xl: "w-16 h-16"
    };
    
    // Size mapping for border width
    const borderMap = {
      xs: "border-2",
      sm: "border-2",
      md: "border-3",
      lg: "border-4",
      xl: "border-[5px]"
    };
    
    // Color mapping
    const colorMap = {
      primary: {
        main: "border-primary",
        transparent: "border-primary border-opacity-20"
      },
      white: {
        main: "border-white",
        transparent: "border-white border-opacity-20"
      },
      gray: {
        main: "border-cosmos-text-muted",
        transparent: "border-cosmos-text-muted border-opacity-20"
      },
      success: {
        main: "border-status-success",
        transparent: "border-status-success border-opacity-20"
      },
      error: {
        main: "border-status-error",
        transparent: "border-status-error border-opacity-20"
      },
      warning: {
        main: "border-status-warning",
        transparent: "border-status-warning border-opacity-20"
      },
      info: {
        main: "border-status-info",
        transparent: "border-status-info border-opacity-20"
      }
    };
    
    // Text size based on loader size
    const textSizeMap = {
      xs: "text-xs",
      sm: "text-xs",
      md: "text-sm",
      lg: "text-base",
      xl: "text-lg"
    };
    
    // Animation speed based on size
    const animationSpeedMap = {
      xs: "animate-spin-fast",
      sm: "animate-spin-fast",
      md: "animate-spin",
      lg: "animate-spin-slow",
      xl: "animate-spin-slow"
    };
    
    // Wrapper classes based on centering and text position
    $: wrapperClasses = centered ? 'flex flex-col items-center justify-center' : 'inline-flex';
    $: wrapperDirection = textPosition === 'left' || textPosition === 'right' ? 
        'flex-row items-center' : 
        'flex-col items-center';
    $: textOrder = textPosition === 'left' || textPosition === 'top' ? 'order-first' : 'order-last';
    $: textMargin = textPosition === 'left' ? 'mr-2' : 
                   textPosition === 'right' ? 'ml-2' : 
                   textPosition === 'top' ? 'mb-2' : 
                   textPosition === 'bottom' ? 'mt-2' : '';
    
    // Determine spinner classes based on props
    $: spinnerSizeClass = sizeMap[size] || sizeMap.md;
    $: spinnerBorderClass = borderMap[size] || borderMap.md;
    $: spinnerColorClass = `${colorMap[color]?.transparent || colorMap.primary.transparent} ${colorMap[color]?.main || colorMap.primary.main}-t`;
    $: spinnerAnimationClass = animationSpeedMap[size] || animationSpeedMap.md;
    $: spinnerClasses = `inline-block rounded-full ${spinnerSizeClass} ${spinnerBorderClass} ${spinnerColorClass} ${spinnerAnimationClass}`;
    
    // Text classes
    $: textClasses = `${textSizeMap[size] || textSizeMap.md} text-cosmos-text-muted ${textMargin}`;
  </script>
  
  <!-- Main loader wrapper -->
  <div class={`${wrapperClasses} ${wrapperDirection}`} {...$$restProps}>
    {#if type === 'spinner'}
      <!-- Spinner type loader -->
      <div class={spinnerClasses}></div>
    {:else if type === 'dots'}
      <!-- Dots type loader -->
      <div class="flex space-x-1">
        <div class={`animate-bounce delay-0 rounded-full ${sizeMap[size].split(' ')[0].replace('w-', 'w-2 h-2')} bg-${color}`}></div>
        <div class={`animate-bounce delay-75 rounded-full ${sizeMap[size].split(' ')[0].replace('w-', 'w-2 h-2')} bg-${color}`}></div>
        <div class={`animate-bounce delay-150 rounded-full ${sizeMap[size].split(' ')[0].replace('w-', 'w-2 h-2')} bg-${color}`}></div>
      </div>
    {:else if type === 'pulse'}
      <!-- Pulse type loader -->
      <div class={`animate-pulse bg-${color} rounded-full ${spinnerSizeClass}`}></div>
    {/if}
    
    <!-- Optional text -->
    {#if text}
      <span class={`${textClasses} ${textOrder}`}>
        <slot>{text}</slot>
      </span>
    {/if}
  </div>
  
  <style>
    /* Define animation speeds not provided by Tailwind */
    :global(.animate-spin-fast) {
      animation: spin 0.6s linear infinite;
    }
    
    :global(.animate-spin-slow) {
      animation: spin 1.5s linear infinite;
    }
    
    @keyframes spin {
      from {
        transform: rotate(0deg);
      }
      to {
        transform: rotate(360deg);
      }
    }
    
    /* Animation delays */
    :global(.delay-0) {
      animation-delay: 0ms;
    }
    
    :global(.delay-75) {
      animation-delay: 75ms;
    }
    
    :global(.delay-150) {
      animation-delay: 150ms;
    }
  </style>