<!-- src/lib/components/ui/Spinner.svelte -->
<script>
    /**
     * Spinner Component
     * Displays a loading indicator with various styles and sizes.
     */
      
    // Props
    export let size = "md"; // Size: xs, sm, md, lg, xl
    export let color = "primary"; // Color: primary, white, gray, success, error, warning, info
    export let variant = "border"; // Type: border, dots, grow
    export let text = ""; // Optional loading text
    export let textPosition = "bottom"; // Text position: left, right, top, bottom
    export let centered = false; // Center in parent container
    export let ariaLabel = "Loading"; // Accessibility label
    
    // Size mapping for spinner width/height
    const sizeMap = {
      xs: "w-4 h-4",
      sm: "w-5 h-5",
      md: "w-8 h-8",
      lg: "w-12 h-12",
      xl: "w-16 h-16"
    };
    
    // Size mapping for border width
    const borderSizeMap = {
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
        transparent: "border-primary/20",
        bg: "bg-primary"
      },
      white: {
        main: "border-white",
        transparent: "border-white/20",
        bg: "bg-white"
      },
      gray: {
        main: "border-cosmos-text-muted",
        transparent: "border-cosmos-text-muted/20",
        bg: "bg-cosmos-text-muted"
      },
      success: {
        main: "border-status-success",
        transparent: "border-status-success/20",
        bg: "bg-status-success"
      },
      error: {
        main: "border-status-error",
        transparent: "border-status-error/20",
        bg: "bg-status-error"
      },
      warning: {
        main: "border-status-warning",
        transparent: "border-status-warning/20",
        bg: "bg-status-warning"
      },
      info: {
        main: "border-status-info",
        transparent: "border-status-info/20",
        bg: "bg-status-info"
      }
    };
    
    // Text size based on spinner size
    const textSizeMap = {
      xs: "text-xs",
      sm: "text-xs",
      md: "text-sm",
      lg: "text-base",
      xl: "text-lg"
    };
    
    // Animation speed based on size
    const animationSpeedMap = {
      xs: "animate-spin-fast", // Custom animation class
      sm: "animate-spin-fast",
      md: "animate-spin",
      lg: "animate-spin-slow",
      xl: "animate-spin-slow"
    };
    
    // Wrapper classes based on centering and text position
    $: wrapperClasses = [
      centered ? 'flex flex-col items-center justify-center' : 'inline-flex',
      textPosition === 'left' || textPosition === 'right' ? 'flex-row items-center' : 'flex-col items-center',
    ].filter(Boolean).join(' ');
    
    // Text order and margin classes
    $: textClasses = [
      textSizeMap[size] || textSizeMap.md,
      "text-cosmos-text-muted",
      textPosition === 'left' ? 'mr-2 order-first' : 
      textPosition === 'right' ? 'ml-2 order-last' : 
      textPosition === 'top' ? 'mb-2 order-first' : 
      textPosition === 'bottom' ? 'mt-2 order-last' : '',
    ].filter(Boolean).join(' ');
    
    // Border spinner classes
    $: borderSpinnerClasses = [
      "inline-block rounded-full",
      sizeMap[size] || sizeMap.md,
      borderSizeMap[size] || borderSizeMap.md,
      `${colorMap[color]?.transparent || colorMap.primary.transparent} ${colorMap[color]?.main || colorMap.primary.main}-t`,
      animationSpeedMap[size] || animationSpeedMap.md
    ].filter(Boolean).join(' ');
    
    // Dots spinner (individual dot classes)
    $: dotClasses = [
      "rounded-full",
      colorMap[color]?.bg || colorMap.primary.bg,
      // Calculate size based on parent spinner size (smaller)
      size === 'xs' ? 'w-1 h-1' :
      size === 'sm' ? 'w-1.5 h-1.5' :
      size === 'md' ? 'w-2 h-2' :
      size === 'lg' ? 'w-3 h-3' :
      'w-4 h-4'
    ].filter(Boolean).join(' ');
    
    // Grow spinner classes
    $: growSpinnerClasses = [
      "animate-pulse rounded-full",
      colorMap[color]?.bg || colorMap.primary.bg,
      sizeMap[size] || sizeMap.md
    ].filter(Boolean).join(' ');
  </script>
  
  <div 
    class={wrapperClasses} 
    role="status" 
    aria-label={ariaLabel}
    {...$$restProps}
  >
    {#if variant === 'border'}
      <!-- Border spinner (most common) -->
      <div class={borderSpinnerClasses}>
        <span class="sr-only">{ariaLabel}</span>
      </div>
    {:else if variant === 'dots'}
      <!-- Dots spinner -->
      <div class="flex space-x-1">
        <div class="{dotClasses} animate-bounce"></div>
        <div class="{dotClasses} animate-bounce delay-75"></div>
        <div class="{dotClasses} animate-bounce delay-150"></div>
        <span class="sr-only">{ariaLabel}</span>
      </div>
    {:else if variant === 'grow'}
      <!-- Grow/pulse spinner -->
      <div class={growSpinnerClasses}>
        <span class="sr-only">{ariaLabel}</span>
      </div>
    {/if}
    
    <!-- Optional text -->
    {#if text}
      <span class={textClasses}>
        <slot>{text}</slot>
      </span>
    {/if}
  </div>
  
  <style>
    /* Custom animation speeds not provided by Tailwind */
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
    :global(.delay-75) {
      animation-delay: 75ms;
    }
    
    :global(.delay-150) {
      animation-delay: 150ms;
    }
  </style>