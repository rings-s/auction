<!-- src/lib/components/ui/Switch.svelte -->
<script>
    import { createEventDispatcher } from 'svelte';
    import { tweened } from 'svelte/motion';
    import { cubicOut } from 'svelte/easing';
    
    const dispatch = createEventDispatcher();
    
    /**
     * Enhanced switch component with animations and customizable appearance
     */
    
    // Base props
    export let checked = false;
    export let name = '';
    export let id = name || `switch-${Math.random().toString(36).substring(2, 9)}`;
    export let label = '';
    export let labelPosition = 'right'; // right, left, top, bottom
    export let labelClass = '';
    
    // Styling props
    export let size = 'md'; // sm, md, lg
    export let color = 'primary'; // primary, secondary, accent, success, warning, error, info, any other custom color
    export let variant = 'default'; // default, outline, glass, minimal
    export let rounded = true; // true or false for pill shape
    export let wrapperClass = '';
    export let disabled = false;
    export let srOnly = false; // Screen reader only label
    export let showIcon = true; // Show icons for on/off
    
    // Accessibility props
    export let ariaLabel = label || 'Toggle';
    
    // Handle toggle
    function toggle() {
      if (disabled) return;
      
      checked = !checked;
      dispatch('change', { checked });
      dispatch('update:checked', checked);
    }
    
    // Handle keyboard interactions
    function handleKeyDown(event) {
      if (disabled) return;
      
      if (event.key === ' ' || event.key === 'Enter') {
        event.preventDefault();
        toggle();
      }
    }
    
    // Animation for the handle
    const handleX = tweened(checked ? 1 : 0, {
      duration: 150,
      easing: cubicOut
    });
    
    $: handleX.set(checked ? 1 : 0);
    
    // Color classes based on props
    $: colorClasses = {
      'primary': 'bg-primary-500',
      'secondary': 'bg-secondary-500',
      'accent': 'bg-accent-500',
      'success': 'bg-success',
      'warning': 'bg-warning',
      'error': 'bg-error',
      'info': 'bg-info'
    }[color] || 'bg-primary-500';
    
    // Size classes
    $: sizeTrackClasses = {
      'sm': 'w-8 h-4',
      'md': 'w-10 h-5',
      'lg': 'w-12 h-6'
    }[size] || 'w-10 h-5';
    
    $: sizeHandleClasses = {
      'sm': 'w-3 h-3',
      'md': 'w-4 h-4',
      'lg': 'w-5 h-5'
    }[size] || 'w-4 h-4';
    
    $: sizeIconClasses = {
      'sm': 'text-[8px]',
      'md': 'text-[10px]',
      'lg': 'text-[12px]'
    }[size] || 'text-[10px]';
    
    // Position classes for handle based on checked state and size
    $: handlePosition = {
      'sm': $handleX * 16 - 2, // px offset
      'md': $handleX * 20 - 2,
      'lg': $handleX * 24 - 2
    }[size] || $handleX * 20 - 2;
    
    // Variant classes
    $: variantClasses = {
      'default': checked ? colorClasses : 'bg-neutral-300 dark:bg-neutral-700',
      'outline': `${checked ? colorClasses : 'bg-neutral-200 dark:bg-neutral-800'} border ${checked ? 'border-'+color+'-600' : 'border-neutral-400 dark:border-neutral-600'}`,
      'glass': `${checked ? colorClasses : 'bg-neutral-200/40 dark:bg-neutral-800/40'} backdrop-blur-sm ${checked ? 'shadow-glass-sm' : ''}`,
      'minimal': checked ? colorClasses : 'bg-neutral-200 dark:bg-neutral-800'
    }[variant] || (checked ? colorClasses : 'bg-neutral-300 dark:bg-neutral-700');
    
    // Direction handling for label position
    $: isVertical = labelPosition === 'top' || labelPosition === 'bottom';
    $: flexDirection = {
      'top': 'flex-col-reverse',
      'right': 'flex-row',
      'bottom': 'flex-col',
      'left': 'flex-row-reverse'
    }[labelPosition] || 'flex-row';
    
    $: labelAlignment = {
      'top': 'items-center mb-1',
      'right': 'items-center ml-2',
      'bottom': 'items-center mt-1',
      'left': 'items-center mr-2'
    }[labelPosition] || 'items-center ml-2';
  </script>
  
  <div class="flex {isVertical ? 'flex-col' : 'items-center'} {flexDirection} {wrapperClass}">
    <div>
      <button
        type="button"
        role="switch"
        {id}
        aria-checked={checked}
        aria-label={ariaLabel}
        aria-labelledby={label && !srOnly ? `${id}-label` : undefined}
        class="relative inline-flex items-center justify-center focus:outline-none focus-visible:ring-2 
          focus-visible:ring-offset-2 focus-visible:ring-primary-500 dark:focus-visible:ring-offset-neutral-900
          {disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}"
        on:click={toggle}
        on:keydown={handleKeyDown}
        disabled={disabled}
        tabindex={disabled ? '-1' : '0'}
      >
        <!-- Track -->
        <div 
          class="relative {sizeTrackClasses} {variantClasses}
            {rounded ? 'rounded-full' : 'rounded-md'} 
            transition-colors duration-200 ease-in-out"
        >
          <!-- Icons inside track -->
          {#if showIcon && size !== 'sm'}
            <div class="absolute inset-0 flex items-center justify-between px-1 pointer-events-none">
              {#if checked}
                <span class="opacity-0">
                  <svg class="{sizeIconClasses} text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </span>
                <span class="opacity-100 text-white">
                  <svg class="{sizeIconClasses} text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
                  </svg>
                </span>
              {:else}
                <span class="opacity-100 text-neutral-600 dark:text-neutral-400">
                  <svg class="{sizeIconClasses}" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </span>
                <span class="opacity-0">
                  <svg class="{sizeIconClasses}" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
                  </svg>
                </span>
              {/if}
            </div>
          {/if}
          
          <!-- Handle/Thumb -->
          <span 
            class="absolute top-[2px] {sizeHandleClasses} transform transition-transform duration-200
              bg-white rounded-full shadow-md"
            style="left: {handlePosition}px"
            aria-hidden="true"
          ></span>
        </div>
      </button>
    </div>
    
    {#if label && !srOnly}
      <label
        id="{id}-label"
        for={id}
        class="text-sm font-medium text-neutral-700 dark:text-neutral-300 {labelAlignment} {labelClass}"
      >
        {label}
      </label>
    {:else if label && srOnly}
      <label id="{id}-label" for={id} class="sr-only">{label}</label>
    {/if}
  </div>