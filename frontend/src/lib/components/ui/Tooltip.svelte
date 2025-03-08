<!-- src/lib/components/ui/Tooltip.svelte -->
<script>
  /**
   * Modern Tooltip component with animations for the GUDIC platform
   * Can be used as a directive or wrapper component
   */
  import { createEventDispatcher, onMount, onDestroy } from 'svelte';
  import { fade, fly } from 'svelte/transition';
  import { scale } from 'svelte/transition';
  
  // Props
  export let text = ''; // Tooltip text content
  export let position = 'top'; // top, bottom, left, right
  export let trigger = 'hover'; // hover, click, focus, manual
  export let delay = 200; // Delay before showing in ms
  export let offset = 8; // Distance from trigger element in pixels
  export let arrow = true; // Whether to show the arrow
  export let maxWidth = 250; // Maximum width in pixels
  export let disabled = false; // Whether the tooltip is disabled
  export let visible = false; // For manual control
  export let theme = 'dark'; // dark, light, or custom
  export let openDelay = delay; // Delay before showing
  export let closeDelay = 0; // Delay before hiding
  export let interactive = false; // Whether tooltip is interactive
  export let customClass = ''; // Additional CSS classes
  export let zIndex = 50; // Z-index for the tooltip
  export let escapeHTML = true; // Whether to escape HTML in text
  export let rounded = 'md'; // none, sm, md, lg, xl
  export let animation = 'fade-fly'; // fade, fly, fade-fly, scale
  
  // Internal state
  let tooltipElement;
  let triggerElement;
  let isVisible = visible;
  let timeout;
  let closeTimeout;
  
  // Event dispatcher
  const dispatch = createEventDispatcher();
  
  // Theme classes lookup object - simplifying the reactive declaration
  const themeClassesMap = {
    dark: 'bg-text-dark text-white',
    light: 'bg-white text-text-dark border border-slate-200 shadow-sm',
    primary: 'bg-primary-blue text-white',
    secondary: 'bg-secondary-blue text-white',
    success: 'bg-success text-white',
    warning: 'bg-warning text-white',
    error: 'bg-error text-white',
  };
  
  // Rounded corner classes lookup object
  const roundedClassesMap = {
    'none': 'rounded-none',
    'sm': 'rounded-sm',
    'md': 'rounded-md',
    'lg': 'rounded-lg',
    'xl': 'rounded-xl',
    'full': 'rounded-full',
  };
  
  // Get theme classes based on current theme
  $: themeClasses = themeClassesMap[theme] || themeClassesMap.dark;
  
  // Get rounded classes based on current rounded value
  $: roundedClasses = roundedClassesMap[rounded] || roundedClassesMap.md;
  
  // Position calculation
  $: positionStyles = getPositionStyles(position, offset);
  
  // Arrow position calculation
  $: arrowStyles = getArrowStyles(position);
  
  // Get animation props based on position and animation type
  $: animationProps = getAnimationProps(position, animation);
  
  // Get position-specific styles
  function getPositionStyles(pos, gap) {
    const positions = {
      top: `bottom: 100%; left: 50%; transform: translateX(-50%) translateY(-${gap}px);`,
      bottom: `top: 100%; left: 50%; transform: translateX(-50%) translateY(${gap}px);`,
      left: `right: 100%; top: 50%; transform: translateY(-50%) translateX(-${gap}px);`,
      right: `left: 100%; top: 50%; transform: translateY(-50%) translateX(${gap}px);`
    };
    
    return positions[pos] || positions.top;
  }
  
  // Get arrow position styles
  function getArrowStyles(pos) {
    const arrowPositions = {
      top: `bottom: -5px; left: 50%; transform: translateX(-50%) rotate(45deg);`,
      bottom: `top: -5px; left: 50%; transform: translateX(-50%) rotate(45deg);`,
      left: `right: -5px; top: 50%; transform: translateY(-50%) rotate(45deg);`,
      right: `left: -5px; top: 50%; transform: translateY(-50%) rotate(45deg);`
    };
    
    return arrowPositions[pos] || arrowPositions.top;
  }
  
  // Get animation properties
  function getAnimationProps(pos, animType) {
    // Fade animation
    if (animType === 'fade') {
      return { transition: fade, props: { duration: 150 } };
    }
    // Scale animation
    else if (animType === 'scale') {
      return { transition: scale, props: { duration: 150, start: 0.85 } };
    }
    // Default fade-fly animation
    else {
      const flyDirections = { 
        top: { y: -5 },
        bottom: { y: 5 },
        left: { x: -5 },
        right: { x: 5 }
      };
      
      const direction = flyDirections[pos] || flyDirections.top;
      
      return { 
        transition: fly, 
        props: { 
          ...direction,
          duration: 150,
          opacity: 0
        } 
      };
    }
  }
  
  // Show tooltip
  function showTooltip() {
    if (disabled) return;
    
    clearTimeout(timeout);
    clearTimeout(closeTimeout);
    
    timeout = setTimeout(() => {
      isVisible = true;
      dispatch('show');
      
      // Position tooltip correctly after it's rendered
      // Using setTimeout ensures the DOM has updated
      setTimeout(() => {
        if (tooltipElement && triggerElement) {
          positionTooltip();
        }
      }, 0);
    }, openDelay);
  }
  
  // Hide tooltip
  function hideTooltip() {
    clearTimeout(timeout);
    
    closeTimeout = setTimeout(() => {
      isVisible = false;
      dispatch('hide');
    }, closeDelay);
  }
  
  // Position tooltip based on trigger element
  function positionTooltip() {
    if (!tooltipElement || !triggerElement) return;
    
    const triggerRect = triggerElement.getBoundingClientRect();
    const tooltipRect = tooltipElement.getBoundingClientRect();
    
    // Adjust position if tooltip exceeds viewport
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;
    
    // Reset any previous adjustments
    tooltipElement.style.left = '';
    tooltipElement.style.right = '';
    tooltipElement.style.top = '';
    tooltipElement.style.bottom = '';
    tooltipElement.style.transform = '';
    
    // Apply default positioning based on position prop
    if (position === 'top' || position === 'bottom') {
      tooltipElement.style.left = '50%';
      tooltipElement.style.transform = `translateX(-50%) translateY(${position === 'top' ? -offset : offset}px)`;
      
      if (position === 'top') {
        tooltipElement.style.bottom = '100%';
      } else {
        tooltipElement.style.top = '100%';
      }
    } else {
      tooltipElement.style.top = '50%';
      tooltipElement.style.transform = `translateY(-50%) translateX(${position === 'left' ? -offset : offset}px)`;
      
      if (position === 'left') {
        tooltipElement.style.right = '100%';
      } else {
        tooltipElement.style.left = '100%';
      }
    }
    
    // After applying default positioning, make adjustments for viewport boundaries
    
    // Horizontal overflow adjustment
    if (position === 'top' || position === 'bottom') {
      const tooltipLeft = triggerRect.left + (triggerRect.width / 2) - (tooltipRect.width / 2);
      const tooltipRight = tooltipLeft + tooltipRect.width;
      
      if (tooltipRight > viewportWidth) {
        // Too far right
        const overflow = tooltipRight - viewportWidth;
        tooltipElement.style.left = `calc(50% - ${overflow + 5}px)`;
      } else if (tooltipLeft < 0) {
        // Too far left
        tooltipElement.style.left = `calc(50% - ${tooltipLeft - 5}px)`;
      }
    }
    
    // Vertical overflow adjustment
    if (position === 'left' || position === 'right') {
      const tooltipTop = triggerRect.top + (triggerRect.height / 2) - (tooltipRect.height / 2);
      const tooltipBottom = tooltipTop + tooltipRect.height;
      
      if (tooltipBottom > viewportHeight) {
        // Too far down
        const overflow = tooltipBottom - viewportHeight;
        tooltipElement.style.top = `calc(50% - ${overflow + 5}px)`;
      } else if (tooltipTop < 0) {
        // Too far up
        tooltipElement.style.top = `calc(50% - ${tooltipTop - 5}px)`;
      }
    }
  }
  
  // Handle click outside for interactive tooltips
  function handleClickOutside(event) {
    if (interactive && isVisible && tooltipElement && !tooltipElement.contains(event.target) && 
        triggerElement && !triggerElement.contains(event.target)) {
      hideTooltip();
    }
  }
  
  // Toggle tooltip for click trigger
  function toggleTooltip() {
    if (isVisible) {
      hideTooltip();
    } else {
      showTooltip();
    }
  }
  
  // Setup event listeners based on trigger
  function setupEventListeners() {
    if (!triggerElement) return;
    
    if (trigger === 'hover' || trigger === 'hover-focus') {
      triggerElement.addEventListener('mouseenter', showTooltip);
      triggerElement.addEventListener('mouseleave', hideTooltip);
    }
    
    if (trigger === 'focus' || trigger === 'hover-focus') {
      triggerElement.addEventListener('focus', showTooltip);
      triggerElement.addEventListener('blur', hideTooltip);
    }
    
    if (trigger === 'click') {
      triggerElement.addEventListener('click', toggleTooltip);
      document.addEventListener('click', handleClickOutside);
    }
  }
  
  // Remove event listeners
  function cleanupEventListeners() {
    if (!triggerElement) return;
    
    triggerElement.removeEventListener('mouseenter', showTooltip);
    triggerElement.removeEventListener('mouseleave', hideTooltip);
    triggerElement.removeEventListener('focus', showTooltip);
    triggerElement.removeEventListener('blur', hideTooltip);
    triggerElement.removeEventListener('click', toggleTooltip);
    
    document.removeEventListener('click', handleClickOutside);
  }
  
  // Handle escape key
  function handleKeyDown(event) {
    if (event.key === 'Escape' && isVisible) {
      hideTooltip();
    }
  }
  
  // Watch for changes in the visible prop for manual control
  $: if (trigger === 'manual' && visible !== isVisible) {
    if (visible) {
      showTooltip();
    } else {
      hideTooltip();
    }
  }
  
  // Set up interactive tooltip behavior
  $: if (interactive && tooltipElement) {
    tooltipElement.addEventListener('mouseenter', showTooltip);
    tooltipElement.addEventListener('mouseleave', hideTooltip);
  }
  
  // Lifecycle hooks
  onMount(() => {
    // The parent element of the tooltip is the trigger element
    triggerElement = tooltipElement?.parentElement;
    
    if (triggerElement) {
      setupEventListeners();
    }
    
    // Initial visibility state
    if (visible && trigger === 'manual') {
      showTooltip();
    }
    
    // Add keyboard support
    document.addEventListener('keydown', handleKeyDown);
  });
  
  onDestroy(() => {
    cleanupEventListeners();
    document.removeEventListener('keydown', handleKeyDown);
    
    // Clear any pending timeouts
    clearTimeout(timeout);
    clearTimeout(closeTimeout);
  });
</script>

<div class="inline-block relative">
<slot></slot>

{#if isVisible && text}
  <div
    bind:this={tooltipElement}
    class="tooltip-content absolute {themeClasses} {roundedClasses} px-2 py-1 text-xs font-medium shadow-lg whitespace-normal {customClass}"
    style="position: absolute; z-index: {zIndex}; max-width: {maxWidth}px;"
    role="tooltip"
    in:{animationProps.transition}={animationProps.props}
    tabindex={interactive ? 0 : -1}
  >
    <!-- Tooltip content -->
    {#if escapeHTML}
      {text}
    {:else}
      {@html text}
    {/if}
    
    <!-- Arrow -->
    {#if arrow}
      <div 
        class="absolute h-2.5 w-2.5 {theme === 'light' ? 'bg-white border-t border-l border-slate-200' : themeClasses.split(' ')[0]}"
        style={arrowStyles}
        aria-hidden="true"
      ></div>
    {/if}
  </div>
{/if}
</div>

<style>
/* Prevent text selection within tooltip */
.tooltip-content {
  user-select: none;
  pointer-events: none;
  word-wrap: break-word;
}

/* Enable pointer events for interactive tooltips */
.tooltip-content[tabindex="0"] {
  pointer-events: auto;
}

/* Subtle border glow for better visibility */
.tooltip-content {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15), 0 0 0 1px rgba(0, 0, 0, 0.05);
}

/* Smooth transition for arrow */
.tooltip-content div {
  transition: all 0.15s ease-out;
}
</style>