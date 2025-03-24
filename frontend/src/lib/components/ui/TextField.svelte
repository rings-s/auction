<!-- src/lib/components/ui/TextField.svelte -->
<script>
    /**
     * TextField Component
     * A versatile input component with support for various states and features.
     */
    import { createEventDispatcher } from 'svelte';
    import { fade } from 'svelte/transition';
    
    const dispatch = createEventDispatcher();
    
    // Props
    export let type = 'text'; // Input type: text, email, password, number, tel, url, search, etc.
    export let value = ''; // Input value
    export let name = ''; // Input name
    export let id = name || `input-${Math.random().toString(36).substring(2, 9)}`; // Input ID
    export let label = ''; // Label text
    export let placeholder = ''; // Placeholder text
    export let helpText = ''; // Help text below input
    export let error = ''; // Error message
    export let disabled = false; // Disabled state
    export let readonly = false; // Read-only state
    export let required = false; // Required field
    export let autocomplete = 'off'; // Autocomplete behavior
    export let autocapitalize = 'off'; // Autocapitalize behavior
    export let spellcheck = false; // Spellcheck behavior
    export let minlength = undefined; // Minimum input length
    export let maxlength = undefined; // Maximum input length
    export let min = undefined; // Minimum value (for number inputs)
    export let max = undefined; // Maximum value (for number inputs)
    export let step = undefined; // Step value (for number inputs)
    export let pattern = undefined; // Input pattern for validation
    export let size = 'md'; // sm, md, lg
    export let variant = 'outline'; // outline, filled, flushed, unstyled
    export let rounded = 'md'; // none, sm, md, lg, full
    export let leadingIcon = undefined; // Icon component to show at the start
    export let trailingIcon = undefined; // Icon component to show at the end
    export let leadingAddon = undefined; // Text or element to add before input
    export let trailingAddon = undefined; // Text or element to add after input
    export let clearable = false; // Show clear button when there's input
    export let counter = false; // Show character counter
    export let autofocus = false; // Autofocus input
    export let iconClickable = false; // Make trailing icon clickable
    export let onIconClick = () => {}; // Function to call when trailing icon is clicked
    export let dir = 'auto'; // Text direction: ltr, rtl, auto
    
    // Local state
    let focused = false;
    let inputElement;
    let passwordVisible = false;
    
    // Size classes
    $: sizeClasses = {
      sm: 'h-8 text-sm py-1',
      md: 'h-10 text-base py-2',
      lg: 'h-12 text-lg py-2.5'
    }[size] || 'h-10 text-base py-2';
    
    // Padding classes based on addons and icons
    $: paddingLeft = leadingIcon 
      ? size === 'sm' ? 'pl-8' : size === 'lg' ? 'pl-12' : 'pl-10' 
      : leadingAddon 
        ? 'pl-0' 
        : size === 'sm' ? 'pl-3' : size === 'lg' ? 'pl-5' : 'pl-4';
    
    $: paddingRight = (trailingIcon || (type === 'password' && !passwordVisible) || (clearable && value)) 
      ? size === 'sm' ? 'pr-8' : size === 'lg' ? 'pr-12' : 'pr-10' 
      : trailingAddon 
        ? 'pr-0' 
        : size === 'sm' ? 'pr-3' : size === 'lg' ? 'pr-5' : 'pr-4';
    
    // Border radius classes
    $: roundedClasses = {
      none: 'rounded-none',
      sm: 'rounded-sm',
      md: 'rounded-md',
      lg: 'rounded-lg',
      full: 'rounded-full'
    }[rounded] || 'rounded-md';
    
    // Get classes for different variants
    $: variantClasses = {
      outline: `border border-neutral-300 dark:border-neutral-700 ${focused ? 'border-primary ring-2 ring-primary/20' : ''}`,
      filled: `border border-transparent bg-neutral-100 dark:bg-neutral-800 ${focused ? 'border-primary ring-2 ring-primary/20' : ''}`,
      flushed: `border-b border-neutral-300 dark:border-neutral-700 rounded-none ${focused ? 'border-primary' : ''}`,
      unstyled: 'border-none shadow-none'
    }[variant] || 'border border-neutral-300 dark:border-neutral-700';
    
    // Combined input classes
    $: inputClasses = [
      'block w-full focus:outline-none px-0',
      'bg-transparent dark:text-white',
      'disabled:opacity-60 disabled:cursor-not-allowed',
      'placeholder:text-neutral-500 dark:placeholder:text-neutral-400',
      error ? 'text-error' : 'text-neutral-900 dark:text-white',
      sizeClasses
    ].filter(Boolean).join(' ');
    
    // Combined wrapper classes
    $: wrapperClasses = [
      'relative flex w-full',
      variantClasses,
      roundedClasses,
      error ? 'border-error focus-within:ring-error/20 focus-within:border-error' : '',
      disabled ? 'opacity-60 cursor-not-allowed bg-neutral-50 dark:bg-neutral-900' : '',
      'transition-colors duration-200'
    ].filter(Boolean).join(' ');
    
    // Handle focus event
    function handleFocus() {
      focused = true;
      dispatch('focus');
    }
    
    // Handle blur event
    function handleBlur() {
      focused = false;
      dispatch('blur');
    }
    
    // Handle clear button click
    function clearInput() {
      value = '';
      dispatch('clear');
      if (inputElement) {
        inputElement.focus();
      }
    }
    
    // Toggle password visibility
    function togglePasswordVisibility() {
      passwordVisible = !passwordVisible;
    }
    
    // Handle trailing icon click
    function handleIconClick() {
      if (iconClickable) {
        onIconClick();
      }
    }
  </script>
  
  <div class="w-full mb-4">
    {#if label}
      <label 
        for={id} 
        class="block mb-1.5 text-sm font-medium text-neutral-700 dark:text-neutral-200"
      >
        {label} {#if required}<span class="text-error">*</span>{/if}
      </label>
    {/if}
    
    <div class={wrapperClasses}>
      <!-- Leading addon -->
      {#if leadingAddon}
        <div class="flex items-center bg-neutral-100 dark:bg-neutral-800 border-r border-neutral-300 dark:border-neutral-700 px-3 rounded-l-md">
          {#if typeof leadingAddon === 'string'}
            <span class="text-neutral-500 dark:text-neutral-400 text-sm">{leadingAddon}</span>
          {:else}
            <svelte:component this={leadingAddon} />
          {/if}
        </div>
      {/if}
      
      <!-- Leading icon -->
      {#if leadingIcon}
        <div class={`absolute left-0 inset-y-0 flex items-center justify-center 
          ${size === 'sm' ? 'w-8' : size === 'lg' ? 'w-12' : 'w-10'} 
          pointer-events-none text-neutral-500 dark:text-neutral-400`}>
          <svelte:component this={leadingIcon} size={size === 'sm' ? 16 : size === 'lg' ? 24 : 20} />
        </div>
      {/if}
      
      <!-- Input element -->
      <input
        {id}
        {name}
        type={type === 'password' && passwordVisible ? 'text' : type}
        bind:value
        bind:this={inputElement}
        {placeholder}
        {readonly}
        {disabled}
        {required}
        {autocomplete}
        {autocapitalize}
        {spellcheck}
        {minlength}
        {maxlength}
        {min}
        {max}
        {step}
        {pattern}
        {dir}
        on:focus={handleFocus}
        on:blur={handleBlur}
        on:input={(e) => dispatch('input', e)}
        on:change={(e) => dispatch('change', e)}
        class={`${inputClasses} ${paddingLeft} ${paddingRight}`}
        aria-invalid={error ? 'true' : 'false'}
        aria-describedby={error || helpText ? `${id}-description` : undefined}
        autofocus={autofocus}
        {...$$restProps}
      />
      
      <!-- Password toggle -->
      {#if type === 'password'}
        <button
          type="button"
          tabindex="-1"
          class={`absolute right-0 inset-y-0 flex items-center justify-center 
            ${size === 'sm' ? 'w-8' : size === 'lg' ? 'w-12' : 'w-10'} 
            text-neutral-500 dark:text-neutral-400 hover:text-neutral-700 dark:hover:text-neutral-300 focus:outline-none`}
          on:click={togglePasswordVisibility}
          aria-label={passwordVisible ? 'Hide password' : 'Show password'}
        >
          {#if passwordVisible}
            <svg xmlns="http://www.w3.org/2000/svg" class={size === 'sm' ? 'h-4 w-4' : size === 'lg' ? 'h-6 w-6' : 'h-5 w-5'} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
              <circle cx="12" cy="12" r="3"></circle>
              <line x1="1" y1="1" x2="23" y2="23"></line>
            </svg>
          {:else}
            <svg xmlns="http://www.w3.org/2000/svg" class={size === 'sm' ? 'h-4 w-4' : size === 'lg' ? 'h-6 w-6' : 'h-5 w-5'} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
              <circle cx="12" cy="12" r="3"></circle>
            </svg>
          {/if}
        </button>
      {/if}
      
      <!-- Clear button -->
      {#if clearable && value && !disabled && !readonly && !trailingIcon}
        <button
          type="button"
          tabindex="-1"
          class={`absolute right-0 inset-y-0 flex items-center justify-center 
            ${size === 'sm' ? 'w-8' : size === 'lg' ? 'w-12' : 'w-10'} 
            text-neutral-500 dark:text-neutral-400 hover:text-neutral-700 dark:hover:text-neutral-300 focus:outline-none`}
          on:click={clearInput}
          aria-label="Clear input"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class={size === 'sm' ? 'h-4 w-4' : size === 'lg' ? 'h-6 w-6' : 'h-5 w-5'} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      {/if}
      
      <!-- Trailing icon -->
      {#if trailingIcon}
        <div 
          class={`absolute right-0 inset-y-0 flex items-center justify-center 
            ${size === 'sm' ? 'w-8' : size === 'lg' ? 'w-12' : 'w-10'} 
            ${iconClickable ? 'cursor-pointer text-neutral-600 dark:text-neutral-300' : 'pointer-events-none text-neutral-500 dark:text-neutral-400'}`}
          on:click={handleIconClick}
          on:keydown={(e) => {
            if (iconClickable && (e.key === 'Enter' || e.key === ' ')) {
              e.preventDefault();
              handleIconClick();
            }
          }}
          tabindex={iconClickable ? 0 : -1}
          role={iconClickable ? 'button' : undefined}
        >
          <svelte:component this={trailingIcon} size={size === 'sm' ? 16 : size === 'lg' ? 24 : 20} />
        </div>
      {/if}
      
      <!-- Trailing addon -->
      {#if trailingAddon}
        <div class="flex items-center bg-neutral-100 dark:bg-neutral-800 border-l border-neutral-300 dark:border-neutral-700 px-3 rounded-r-md">
          {#if typeof trailingAddon === 'string'}
            <span class="text-neutral-500 dark:text-neutral-400 text-sm">{trailingAddon}</span>
          {:else}
            <svelte:component this={trailingAddon} />
          {/if}
        </div>
      {/if}
    </div>
    
    <!-- Help text, error message and counter -->
    <div class="mt-1.5 flex justify-between">
      <div>
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
        <div class="ml-auto text-xs text-neutral-500 dark:text-neutral-400">
          {value?.length || 0}/{maxlength}
        </div>
      {/if}
    </div>
  </div>