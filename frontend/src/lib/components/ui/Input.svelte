<script>
  /**
   * Modern Input component with animation for the GUDIC platform
   */
  export let type = 'text';
  export let id = '';
  export let name = '';
  export let label = '';
  export let placeholder = '';
  export let value = '';
  export let disabled = false;
  export let readonly = false;
  export let required = false;
  export let error = '';
  export let helper = '';
  export let hideLabel = false;
  export let leftIcon = null;
  export let rightIcon = null;
  export let autocomplete = 'on';
  
  // Track focus state
  let focused = false;
  const handleFocus = () => { focused = true; };
  const handleBlur = () => { focused = false; };
  
  // Determine if the input has content
  $: hasContent = value !== '';
  
  // Container classes
  $: containerClass = 'relative group transition-all duration-300 mb-5';
  
  // Label classes with new color scheme
  $: labelClass = `
    absolute left-3 transition-all duration-200 
    ${hideLabel ? 'sr-only' : ''}
    ${(focused || hasContent) ? 'transform -translate-y-6 scale-75 text-xs text-secondary-blue z-10 bg-white px-2 -ml-2' : 'text-sm text-text-light top-3'}
  `;
  
  // Input classes with new color scheme
  $: inputClass = `
    block w-full px-3 py-3
    bg-white border-2
    rounded-xl
    text-text-dark text-base
    placeholder-transparent
    transition-all duration-200
    focus:outline-none
    ${error 
      ? 'border-error focus:border-error focus:ring-error/30' 
      : focused 
        ? 'border-secondary-blue ring-2 ring-primary-blue/20' 
        : 'border-primary-blue/30 hover:border-primary-blue/60'
    }
    ${disabled ? 'bg-neutral-50 cursor-not-allowed opacity-75' : ''}
    ${leftIcon ? 'pl-10' : ''}
    ${rightIcon ? 'pr-10' : ''}
  `;
  
  // Helper text classes
  $: helperClass = `mt-1 text-xs text-text-light transition-all duration-200`;
  
  // Error text classes
  $: errorClass = `mt-1 text-xs text-error transition-all duration-200`;
  
  // Icon classes
  $: iconClass = `
    absolute top-0 flex items-center h-full px-3
    ${disabled ? 'opacity-50' : ''}
    ${focused ? 'text-secondary-blue' : 'text-text-light'}
    transition-all duration-200
  `;
</script>

<div class={containerClass}>
  <input
    {type}
    {id}
    {name}
    {placeholder}
    class={inputClass}
    bind:value
    {disabled}
    {readonly}
    {required}
    {autocomplete}
    on:focus={handleFocus}
    on:blur={handleBlur}
    aria-invalid={!!error}
    aria-describedby={error ? `${id}-error` : helper ? `${id}-helper` : undefined}
    {...$$restProps}
  />
  
  {#if label}
    <label for={id} class={labelClass}>
      {label}{#if required}<span class="text-error ml-1">*</span>{/if}
    </label>
  {/if}
  
  {#if leftIcon}
    <div class="{iconClass} left-0">
      <svelte:component this={leftIcon} class="h-5 w-5" />
    </div>
  {/if}
  
  {#if rightIcon}
    <div class="{iconClass} right-0">
      <svelte:component this={rightIcon} class="h-5 w-5" />
    </div>
  {/if}
  
  {#if error}
    <p id="{id}-error" class={errorClass} role="alert">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 inline-block mr-1" viewBox="0 0 20 20" fill="currentColor">
        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
      </svg>
      {error}
    </p>
  {:else if helper}
    <p id="{id}-helper" class={helperClass}>{helper}</p>
  {/if}
</div>

<style>
  /* Add subtle animation for focus/hover states */
  input {
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
    transition: all 0.3s ease;
  }
  
  input:focus {
    box-shadow: 0 4px 10px rgba(185, 220, 242, 0.15);
    transform: translateY(-1px);
  }
  
  /* Custom autofill style */
  input:-webkit-autofill,
  input:-webkit-autofill:hover,
  input:-webkit-autofill:focus {
    -webkit-text-fill-color: var(--text-dark);
    transition: background-color 5000s ease-in-out 0s;
    box-shadow: 0 0 0px 1000px white inset;
  }
</style>