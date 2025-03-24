<!-- src/lib/components/ui/Textarea.svelte -->
<script>
  import { createEventDispatcher } from 'svelte';
  import { fade } from 'svelte/transition';
  
  const dispatch = createEventDispatcher();
  
  // Base props
  export let value = '';
  export let name = '';
  export let id = name || `textarea-${Math.random().toString(36).substring(2, 9)}`;
  export let label = '';
  export let placeholder = '';
  export let helpText = '';
  export let error = '';
  
  // Styling and behavior props
  export let variant = 'default'; // default, outline, filled, glass
  export let rows = 3;
  export let maxlength = null;
  export let minlength = null;
  export let required = false;
  export let disabled = false;
  export let readonly = false;
  export let autofocus = false;
  export let resize = 'vertical'; // 'none', 'vertical', 'horizontal', 'both'
  export let rounded = 'md'; // none, sm, md, lg, xl, 2xl, 3xl, full
  export let counter = false; // Show character counter
  export let wrapperClass = ''; // Additional classes for wrapper
  export let labelClass = ''; // Additional classes for label
  export let size = 'default'; // sm, default, lg
  
  // Active state
  let focused = false;
  
  // Resize classes
  $: resizeClass = {
    'none': 'resize-none',
    'vertical': 'resize-y',
    'horizontal': 'resize-x',
    'both': 'resize'
  }[resize] || 'resize-y';
  
  // Size classes
  $: sizeClasses = {
    'sm': 'text-sm py-1.5 px-2.5',
    'default': 'text-base py-2 px-3',
    'lg': 'text-lg py-3 px-4'
  }[size] || 'text-base py-2 px-3';
  
  // Rounded classes
  $: roundedClasses = {
    'none': 'rounded-none',
    'sm': 'rounded-sm',
    'md': 'rounded-md',
    'lg': 'rounded-lg',
    'xl': 'rounded-xl',
    '2xl': 'rounded-2xl',
    '3xl': 'rounded-3xl',
    'full': 'rounded-full'
  }[rounded] || 'rounded-md';
  
  // Variant styles
  $: variantClasses = {
    'default': 'border border-neutral-300 bg-white dark:border-neutral-700 dark:bg-neutral-800',
    'outline': 'border border-neutral-300 bg-transparent dark:border-neutral-700',
    'filled': 'border border-transparent bg-neutral-100 dark:bg-neutral-800',
    'glass': 'border border-neutral-200/30 dark:border-neutral-700/30 bg-surface-glass dark:bg-neutral-800/30 backdrop-blur-sm shadow-glass-sm'
  }[variant] || 'border border-neutral-300 bg-white dark:border-neutral-700 dark:bg-neutral-800';
  
  // State classes
  $: stateClasses = [
    error ? 'border-error focus:border-error focus:ring-error/20 dark:border-error dark:focus:ring-error/20' : 
    focused ? 'border-primary focus:border-primary focus:ring-primary/20 dark:border-primary dark:focus:ring-primary/20' : '',
    disabled ? 'opacity-60 cursor-not-allowed bg-neutral-50 dark:bg-neutral-900' : '',
  ].filter(Boolean).join(' ');
  
  // Text and placeholder colors
  $: textColorClass = error ? 'text-error dark:text-error' : 'text-neutral-900 dark:text-white';
  $: placeholderClass = 'placeholder-neutral-500 dark:placeholder-neutral-400';
  
  // Handle focus events
  function handleFocus() {
    focused = true;
    dispatch('focus');
  }
  
  function handleBlur() {
    focused = false;
    dispatch('blur');
  }
  
  // Calculate remaining characters
  $: remainingChars = maxlength ? maxlength - value.length : null;
  $: isNearLimit = maxlength && remainingChars <= Math.max(maxlength * 0.1, 10);
</script>

<div class="w-full mb-4 {wrapperClass}">
  {#if label}
    <label 
      for={id} 
      class="block mb-1.5 text-sm font-medium text-neutral-700 dark:text-neutral-200 {labelClass}"
    >
      {label} {#if required}<span class="text-error">*</span>{/if}
    </label>
  {/if}
  
  <div class="relative">
    <textarea
      {id}
      {name}
      bind:value
      class="{sizeClasses} {roundedClasses} {variantClasses} {stateClasses} {resizeClass} w-full
      {textColorClass} {placeholderClass} 
      transition-all duration-200 ease-in-out
      focus:outline-none focus:ring-2 focus:ring-opacity-50
      disabled:opacity-60 disabled:cursor-not-allowed"
      {placeholder}
      {rows}
      {maxlength}
      {minlength}
      {disabled}
      {readonly}
      {required}
      aria-invalid={error ? 'true' : 'false'}
      aria-describedby={error || helpText ? `${id}-description` : undefined}
      on:focus={handleFocus}
      on:blur={handleBlur}
      on:input={(e) => dispatch('input', e)}
      on:change={(e) => dispatch('change', e)}
      {autofocus}
      {...$$restProps}
    ></textarea>
    
    {#if variant === 'glass' && !error && !disabled}
      <div class="absolute inset-0 pointer-events-none rounded-md bg-white/5 dark:bg-black/5 backdrop-blur-[1px]"></div>
    {/if}
  </div>
  
  <!-- Help text, error message and counter -->
  <div class="mt-1.5 flex justify-between">
    <div class="flex-1">
      {#if error}
        <p 
          id={`${id}-description`} 
          class="text-sm text-error" 
          in:fade={{ duration: 150 }}
        >
          {error}
        </p>
      {:else if helpText}
        <p 
          id={`${id}-description`} 
          class="text-sm text-neutral-500 dark:text-neutral-400"
        >
          {helpText}
        </p>
      {/if}
    </div>
    
    {#if counter && maxlength}
      <div class="flex-shrink-0 text-xs {isNearLimit ? 'text-warning' : 'text-neutral-500 dark:text-neutral-400'}">
        {value.length}/{maxlength}
      </div>
    {/if}
  </div>
</div>