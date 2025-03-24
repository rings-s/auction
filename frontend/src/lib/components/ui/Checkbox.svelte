<!-- src/lib/components/ui/Checkbox.svelte -->
<script>
    /**
     * Checkbox Component
     * A customizable checkbox input with various styles and states.
     */
    import { createEventDispatcher } from 'svelte';
    
    const dispatch = createEventDispatcher();
    
    // Props
    export let checked = false; // Checked state
    export let indeterminate = false; // Indeterminate state
    export let value = ""; // Value attribute
    export let name = ""; // Input name
    export let id = name || `checkbox-${Math.random().toString(36).substring(2, 9)}`; // Input ID
    export let label = ""; // Checkbox label
    export let labelPosition = "right"; // Label position: right, left
    export let disabled = false; // Disabled state
    export let readonly = false; // Read-only state
    export let required = false; // Required state
    export let error = ""; // Error message
    export let helpText = ""; // Help text
    export let size = "md"; // sm, md, lg
    export let variant = "default"; // default, filled, outline
    export let color = "primary"; // primary, success, warning, error, info, custom
    export let customColor = undefined; // Custom checkbox color
    export let borderRadius = "md"; // none, sm, md, lg, full
    export let animation = true; // Enable animation
    
    // Size classes for checkbox
    $: sizeClasses = {
      sm: 'h-4 w-4',
      md: 'h-5 w-5',
      lg: 'h-6 w-6'
    }[size] || 'h-5 w-5';
    
    // Size classes for label text
    $: textSizeClasses = {
      sm: 'text-sm',
      md: 'text-base',
      lg: 'text-lg'
    }[size] || 'text-base';
    
    // Border radius classes
    $: borderRadiusClasses = {
      none: 'rounded-none',
      sm: 'rounded-sm',
      md: 'rounded',
      lg: 'rounded-md',
      full: 'rounded-full'
    }[borderRadius] || 'rounded';
    
    // Color classes for filled and checked state
    $: colorClasses = {
      primary: 'bg-primary border-primary',
      success: 'bg-green-500 border-green-500',
      warning: 'bg-amber-500 border-amber-500',
      error: 'bg-red-500 border-red-500',
      info: 'bg-blue-500 border-blue-500',
      custom: customColor ? `bg-[${customColor}] border-[${customColor}]` : 'bg-primary border-primary'
    }[color] || 'bg-primary border-primary';
    
    // Focus ring color classes
    $: focusRingClasses = {
      primary: 'focus:ring-primary/30',
      success: 'focus:ring-green-500/30',
      warning: 'focus:ring-amber-500/30',
      error: 'focus:ring-red-500/30',
      info: 'focus:ring-blue-500/30',
      custom: customColor ? `focus:ring-[${customColor}]/30` : 'focus:ring-primary/30'
    }[color] || 'focus:ring-primary/30';
    
    // Border color classes for unchecked state
    $: borderClasses = {
      primary: 'border-neutral-300 dark:border-neutral-600',
      success: 'border-neutral-300 dark:border-neutral-600',
      warning: 'border-neutral-300 dark:border-neutral-600',
      error: 'border-neutral-300 dark:border-neutral-600',
      info: 'border-neutral-300 dark:border-neutral-600',
      custom: 'border-neutral-300 dark:border-neutral-600'
    }[color] || 'border-neutral-300 dark:border-neutral-600';
    
    // Combined checkbox input classes
    $: checkboxClasses = [
      'appearance-none border',
      sizeClasses,
      borderRadiusClasses,
      checked || indeterminate ? colorClasses : borderClasses,
      'transition-colors',
      animation ? 'duration-200' : '',
      disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer',
      error ? 'border-red-500 dark:border-red-500' : '',
      'focus:outline-none focus:ring-2 focus:ring-offset-2',
      focusRingClasses
    ].filter(Boolean).join(' ');
    
    // Label classes
    $: labelClasses = [
      textSizeClasses,
      disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer',
      error ? 'text-red-500' : 'text-neutral-700 dark:text-neutral-300'
    ].filter(Boolean).join(' ');
    
    // Wrapper classes for spacing between checkbox and label
    $: wrapperClasses = [
      'flex items-center',
      labelPosition === 'left' ? 'flex-row-reverse' : 'flex-row',
      labelPosition === 'left' ? 'justify-end' : '',
      labelPosition === 'left' ? 'space-x-reverse' : '',
      'space-x-2'
    ].filter(Boolean).join(' ');
    
    // Handle changes and dispatch events
    function handleChange(event) {
      if (!disabled && !readonly) {
        checked = event.target.checked;
        indeterminate = false;
        dispatch('change', { checked, value });
      }
    }
    
    // Handle indeterminate state which can't be set via HTML attribute
    let checkboxElement;
    $: if (checkboxElement) {
      checkboxElement.indeterminate = indeterminate;
    }
  </script>
  
  <div class="mb-2">
    <div class={wrapperClasses}>
      <input
        bind:this={checkboxElement}
        {id}
        {name}
        {value}
        {disabled}
        {required}
        {readonly}
        type="checkbox"
        bind:checked
        on:change={handleChange}
        class={checkboxClasses}
        aria-checked={indeterminate ? 'mixed' : checked}
        aria-invalid={error ? 'true' : 'false'}
        aria-describedby={error || helpText ? `${id}-description` : undefined}
        {...$$restProps}
      />
      
      {#if checked || indeterminate}
        <div class="pointer-events-none absolute flex items-center justify-center" style={`width: ${size === 'sm' ? '1rem' : size === 'lg' ? '1.5rem' : '1.25rem'}`}>
          {#if checked}
            <svg class={`fill-white ${size === 'sm' ? 'h-3 w-3' : size === 'lg' ? 'h-4 w-4' : 'h-3.5 w-3.5'}`} viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
            </svg>
          {:else if indeterminate}
            <svg class={`fill-white ${size === 'sm' ? 'h-3 w-3' : size === 'lg' ? 'h-4 w-4' : 'h-3.5 w-3.5'}`} viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
              <path fill-rule="evenodd" d="M3 10a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clip-rule="evenodd" />
            </svg>
          {/if}
        </div>
      {/if}
      
      {#if label}
        <label for={id} class={labelClasses}>
          {label}
        </label>
      {/if}
    </div>
    
    {#if error}
      <p id={`${id}-description`} class="mt-1 text-sm text-red-500">
        {error}
      </p>
    {:else if helpText}
      <p id={`${id}-description`} class="mt-1 text-sm text-neutral-500 dark:text-neutral-400">
        {helpText}
      </p>
    {/if}
  </div>