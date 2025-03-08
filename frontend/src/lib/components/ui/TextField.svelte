<!-- src/lib/components/ui/TextField.svelte -->
<script>
  /**
   * Enhanced TextField component with distinctive typography for the GUDIC platform
   */
  import { createEventDispatcher, onMount } from 'svelte';
  import Icon from './Icon.svelte';
  
  // Props
  export let type = 'text'; // text, password, email, number, search, tel, url, etc.
  export let id = '';
  export let name = '';
  export let label = '';
  export let placeholder = '';
  export let value = '';
  export let defaultValue = '';
  export let disabled = false;
  export let readonly = false;
  export let required = false;
  export let error = '';
  export let helperText = '';
  export let hideLabel = false;
  export let leftIcon = null; // Icon component or string name
  export let rightIcon = null; // Icon component or string name
  export let leftAddon = ''; // Text or HTML content for left addon
  export let rightAddon = ''; // Text or HTML content for right addon
  export let clearable = false; // Whether field can be cleared with a button
  export let variant = 'default'; // outlined, filled, underlined
  export let size = 'md'; // sm, md, lg
  export let fullWidth = false;
  export let rounded = 'md'; // none, sm, md, lg, full
  export let autocomplete = 'off';
  export let autofocus = false;
  export let maxLength = undefined;
  export let minLength = undefined;
  export let pattern = undefined;
  export let inputMode = undefined;
  export let debounce = 0; // Debounce delay in ms
  export let rows = undefined; // For textarea
  export let cols = undefined; // For textarea
  export let resize = true; // For textarea
  export let multiline = false; // Whether to render as textarea
  export let spellcheck = false;
  export let onEnterPressed = undefined; // Function to call when Enter is pressed
  export let rules = []; // Array of validation rules
  export let customClass = ''; // Additional CSS classes
  
  // Internal state
  let inputEl;
  let focused = false;
  let innerValue = value || defaultValue || '';
  let isHovered = false;
  let debounceTimer;
  let passwordVisible = false;
  let validationError = '';
  let touched = false;
  
  // Event dispatcher
  const dispatch = createEventDispatcher();
  
  // Initialize value from props
  $: {
    if (value !== innerValue) {
      innerValue = value;
    }
  }
  
  // Computed properties
  $: hasError = error || validationError;
  $: hasValue = innerValue !== '';
  $: showClearButton = clearable && hasValue && !disabled && !readonly;
  $: showPasswordToggle = type === 'password' && !disabled && !readonly;
  $: computedType = type === 'password' && passwordVisible ? 'text' : type;
  $: isTextarea = multiline === true;
  
  // Size classes mapping
  $: sizeClasses = {
    sm: 'text-xs py-1.5 px-3',
    md: 'text-sm py-2.5 px-4',
    lg: 'text-base py-3 px-5',
  }[size] || 'text-sm py-2.5 px-4';
  
  // Label size classes
  $: labelSizeClasses = {
    sm: 'text-xs',
    md: 'text-sm',
    lg: 'text-base',
  }[size] || 'text-sm';
  
  // Rounded corner classes
  $: roundedClasses = {
    'none': 'rounded-none',
    'sm': 'rounded-sm',
    'md': 'rounded-lg',
    'lg': 'rounded-xl',
    'full': 'rounded-full',
  }[rounded] || 'rounded-lg';
  
  // Variant styling classes with enhanced component contrast
  $: variantClasses = getVariantClasses(variant, focused, hasError, isHovered);
  
  // Helper function to determine variant classes with updated colors
  function getVariantClasses(variant, isFocused, hasError, isHovered) {
    const baseClasses = 'transition-all duration-300 border w-full component-text';
    
    if (hasError) {
      return `${baseClasses} border-error focus:border-error focus:ring-error/30 ${rounded !== 'none' ? roundedClasses : ''}`;
    }
    
    switch (variant) {
      case 'filled':
        return `${baseClasses} bg-neutral-50 border-neutral-200 focus:bg-white ${isFocused ? 'border-component-primary ring-2 ring-component-primary/20' : isHovered ? 'border-component-primary/60' : 'border-neutral-200'} ${rounded !== 'none' ? roundedClasses : ''}`;
      case 'underlined':
        return `${baseClasses} bg-transparent border-x-0 border-t-0 border-b-2 rounded-none ${isFocused ? 'border-component-primary' : isHovered ? 'border-component-primary/60' : 'border-neutral-200'}`;
      case 'outlined':
      default:
        return `${baseClasses} bg-white border-neutral-200 ${isFocused ? 'border-component-primary ring-2 ring-component-primary/20' : isHovered ? 'border-component-primary/60' : 'border-neutral-200'} ${rounded !== 'none' ? roundedClasses : ''}`;
    }
  }
  
  // Additional modifier classes
  $: modifierClasses = [
    disabled ? 'opacity-60 cursor-not-allowed bg-neutral-50' : '',
    fullWidth ? 'w-full' : '',
    customClass
  ].filter(Boolean).join(' ');
  
  // Layout classes for left/right icons and addons
  $: leftIconClasses = leftIcon || leftAddon ? 'pl-10' : '';
  $: rightIconClasses = (rightIcon || rightAddon || showClearButton || showPasswordToggle) ? 'pr-10' : '';
  
  // Label classes for positioning and animation with component typography contrast
  $: labelClasses = `
    absolute left-3 transition-all duration-200 pointer-events-none component-text
    ${hideLabel ? 'sr-only' : ''}
    ${labelSizeClasses} 
    ${(focused || hasValue) ? 'transform -translate-y-[140%] scale-80 text-xs text-component-primary z-10 whitespace-nowrap' : `text-component-text-light ${sizeClasses.split(' ')[1]}`}
  `;
  
  // Textarea resize class
  $: resizeClass = isTextarea && resize ? 'resize-y' : isTextarea && !resize ? 'resize-none' : '';
  
  // Combined input classes with component typography
  $: inputClasses = `
    block outline-none component-text
    ${sizeClasses}
    ${variantClasses}
    ${leftIconClasses}
    ${rightIconClasses}
    ${modifierClasses}
    ${resizeClass}
    ${isTextarea ? 'min-h-[80px]' : ''}
    ${isTextarea && variant === 'underlined' ? 'pt-6' : ''}
    placeholder-transparent
    focus:outline-none
    text-component-text-dark
  `;
  
  // Mount event
  onMount(() => {
    if (autofocus && inputEl) {
      inputEl.focus();
    }
    
    // Set initial value
    if (defaultValue && !value) {
      innerValue = defaultValue;
      handleChange();
    }
  });
  
  // Handle focus event
  function handleFocus() {
    focused = true;
    dispatch('focus');
  }
  
  // Handle blur event with validation
  function handleBlur() {
    focused = false;
    touched = true;
    
    if (rules.length > 0) {
      validateField();
    }
    
    dispatch('blur');
  }
  
  // Handle change with debounce
  function handleChange() {
    // Clear any previous timer
    if (debounceTimer) clearTimeout(debounceTimer);
    
    if (debounce > 0) {
      // Set a new timer
      debounceTimer = setTimeout(() => {
        updateValue();
      }, debounce);
    } else {
      // No debounce, update immediately
      updateValue();
    }
  }
  
  // Update the value and dispatch event
  function updateValue() {
    // Validate if touched and rules exist
    if (touched && rules.length > 0) {
      validateField();
    }
    
    // Update value and dispatch event
    value = innerValue;
    dispatch('change', { value: innerValue });
    dispatch('input', { value: innerValue });
  }
  
  // Key down handler for Enter key
  function handleKeyDown(event) {
    if (event.key === 'Enter' && onEnterPressed) {
      event.preventDefault();
      onEnterPressed(innerValue);
    }
    
    dispatch('keydown', event);
  }
  
  // Clear input value
  function clearValue() {
    innerValue = '';
    value = '';
    dispatch('clear');
    dispatch('change', { value: '' });
    dispatch('input', { value: '' });
    
    // Focus the input after clearing
    if (inputEl) {
      inputEl.focus();
    }
  }
  
  // Toggle password visibility
  function togglePasswordVisibility() {
    passwordVisible = !passwordVisible;
  }
  
  // Validate field against rules
  function validateField() {
    validationError = '';
    
    if (!rules.length) return true;
    
    for (const rule of rules) {
      if (typeof rule === 'function') {
        const result = rule(innerValue);
        if (result !== true) {
          validationError = result;
          return false;
        }
      }
    }
    
    return true;
  }
</script>

<div class="relative {fullWidth ? 'w-full' : 'inline-block'} {customClass}">
<!-- Input element -->
{#if isTextarea}
  <textarea
    {id}
    {name}
    class={inputClasses}
    placeholder={placeholder}
    {disabled}
    {readonly}
    {required}
    {rows}
    {cols}
    {spellcheck}
    {maxLength}
    {minLength}
    {autocomplete}
    aria-invalid={!!hasError}
    aria-describedby={hasError ? `${id}-error` : helperText ? `${id}-helper` : undefined}
    bind:value={innerValue}
    bind:this={inputEl}
    on:focus={handleFocus}
    on:blur={handleBlur}
    on:input={handleChange}
    on:keydown={handleKeyDown}
    on:mouseenter={() => isHovered = true}
    on:mouseleave={() => isHovered = false}
    {...$$restProps}
  ></textarea>
{:else}
  <input
    type={computedType}
    {id}
    {name}
    class={inputClasses}
    placeholder={placeholder}
    {disabled}
    {readonly}
    {required}
    {pattern}
    {inputMode}
    {maxLength}
    {minLength}
    {autocomplete}
    {spellcheck}
    aria-invalid={!!hasError}
    aria-describedby={hasError ? `${id}-error` : helperText ? `${id}-helper` : undefined}
    bind:value={innerValue}
    bind:this={inputEl}
    on:focus={handleFocus}
    on:blur={handleBlur}
    on:input={handleChange}
    on:keydown={handleKeyDown}
    on:mouseenter={() => isHovered = true}
    on:mouseleave={() => isHovered = false}
    {...$$restProps}
  />
{/if}

<!-- Animated label -->
{#if label}
  <label for={id} class={labelClasses}>
    {label}{#if required}<span class="text-error ml-1">*</span>{/if}
  </label>
{/if}

<!-- Left icon or addon -->
{#if leftIcon || leftAddon}
  <div class="absolute left-0 inset-y-0 flex items-center pl-3 pointer-events-none">
    {#if leftIcon}
      {#if typeof leftIcon === 'string'}
        <Icon name={leftIcon} size={size === 'lg' ? 'md' : size === 'sm' ? 'xs' : 'sm'} class={focused ? 'text-component-primary' : 'text-component-text-light'} />
      {:else}
        <svelte:component this={leftIcon} class={`h-5 w-5 ${focused ? 'text-component-primary' : 'text-component-text-light'}`} />
      {/if}
    {:else if leftAddon}
      <span class="component-text text-component-text-light text-sm">{leftAddon}</span>
    {/if}
  </div>
{/if}

<!-- Right icon/addon area -->
{#if rightIcon || rightAddon || showClearButton || showPasswordToggle}
  <div class="absolute right-0 inset-y-0 flex items-center gap-1 pr-3">
    {#if showClearButton}
      <button
        type="button"
        class="p-1 rounded-full text-component-text-light hover:text-component-text-dark hover:bg-neutral-100 focus:outline-none focus:ring-1 focus:ring-component-primary"
        on:click={clearValue}
        aria-label="Clear input"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
        </svg>
      </button>
    {/if}
    
    {#if showPasswordToggle}
      <button
        type="button"
        class="p-1 rounded-full text-component-text-light hover:text-component-text-dark hover:bg-neutral-100 focus:outline-none focus:ring-1 focus:ring-component-primary"
        on:click={togglePasswordVisibility}
        aria-label={passwordVisible ? "Hide password" : "Show password"}
      >
        {#if passwordVisible}
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
            <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
            <path fill-rule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clip-rule="evenodd" />
          </svg>
        {:else}
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M3.707 2.293a1 1 0 00-1.414 1.414l14 14a1 1 0 001.414-1.414l-1.473-1.473A10.014 10.014 0 0019.542 10C18.268 5.943 14.478 3 10 3a9.958 9.958 0 00-4.512 1.074l-1.78-1.781zm4.261 4.26l1.514 1.515a2.003 2.003 0 012.45 2.45l1.514 1.514a4 4 0 00-5.478-5.478z" clip-rule="evenodd" />
            <path d="M12.454 16.697L9.75 13.992a4 4 0 01-3.742-3.741L2.335 6.578A9.98 9.98 0 00.458 10c1.274 4.057 5.065 7 9.542 7 .847 0 1.669-.105 2.454-.303z" />
          </svg>
        {/if}
      </button>
    {/if}
    
    {#if rightIcon}
      {#if typeof rightIcon === 'string'}
        <Icon name={rightIcon} size={size === 'lg' ? 'md' : size === 'sm' ? 'xs' : 'sm'} class={focused ? 'text-component-primary' : 'text-component-text-light'} />
      {:else}
        <svelte:component this={rightIcon} class={`h-5 w-5 ${focused ? 'text-component-primary' : 'text-component-text-light'}`} />
      {/if}
    {:else if rightAddon}
      <span class="component-text text-component-text-light text-sm">{rightAddon}</span>
    {/if}
  </div>
{/if}

<!-- Error message -->
{#if hasError}
  <p id="{id}-error" class="mt-1 text-xs text-error component-text" role="alert">
    {error || validationError}
  </p>
<!-- Helper text -->
{:else if helperText}
  <p id="{id}-helper" class="mt-1 text-xs text-component-text-light component-text">
    {helperText}
  </p>
{/if}

<!-- Character counter when maxLength is specified -->
{#if maxLength}
  <div class="absolute right-3 -bottom-5 text-xs text-component-text-light component-text">
    {innerValue.length}/{maxLength}
  </div>
{/if}
</div>

<style>
/* Add subtle animation for focus/hover states */
input, textarea {
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
  transition: all 0.3s ease;
  font-family: 'Outfit', sans-serif;
  letter-spacing: 0.01em;
}

input:focus, textarea:focus {
  box-shadow: 0 3px 10px rgba(0, 98, 204, 0.15);
  transform: translateY(-1px);
}

/* Custom autofill style */
input:-webkit-autofill,
input:-webkit-autofill:hover,
input:-webkit-autofill:focus,
textarea:-webkit-autofill,
textarea:-webkit-autofill:hover,
textarea:-webkit-autofill:focus {
  -webkit-text-fill-color: var(--component-text-dark);
  transition: background-color 5000s ease-in-out 0s;
  box-shadow: 0 0 0px 1000px white inset;
}

/* Smooth placeholder transition */
input::placeholder,
textarea::placeholder {
  color: transparent;
  transition: color 0.2s ease;
}

input:focus::placeholder,
textarea:focus::placeholder {
  color: var(--component-text-light);
}

/* Focus ring animation */
input:focus, textarea:focus {
  animation: ring-pulse 1.5s infinite;
}

@keyframes ring-pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(0, 98, 204, 0.2);
  }
  70% {
    box-shadow: 0 0 0 4px rgba(0, 98, 204, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(0, 98, 204, 0);
  }
}
</style>