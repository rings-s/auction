<!-- src/lib/components/ui/Input.svelte -->
<script>
  /**
   * Input Component
   * A form input component with support for validation, icons, and RTL text.
   */
  import { language } from '$lib/i18n';
  
  // Props
  export let type = 'text'; // Input type: text, email, password, number, etc.
  export let name = ''; // Input name
  export let id = name || undefined; // Input ID, defaults to name
  export let value = ''; // Input value
  export let placeholder = ''; // Placeholder text
  export let label = undefined; // Input label
  export let error = undefined; // Error message
  export let disabled = false; // Disabled state
  export let required = false; // Required field
  export let dirOverride = null; // Override direction manually
  export let forceRTL = false; // Force RTL mode
  export let forceLTR = false; // Force LTR mode
  export let icon = undefined; // Icon to display
  export let iconPosition = 'left'; // Icon position: left, right
  export let autocomplete = ''; // Autocomplete attribute
  export let helpText = undefined; // Help text below input
  export let maxLength = undefined; // Max length
  export let minLength = undefined; // Min length
  export let readonly = false; // Readonly mode
  export let size = 'default'; // Input size: sm, default, lg
  
  // Handle text direction based on input type and language
  $: dir = dirOverride 
    ? dirOverride 
    : forceLTR 
      ? 'ltr' 
      : forceRTL 
        ? 'rtl' 
        : (type === 'email' || type === 'tel' || type === 'url' || type === 'number') 
          ? 'ltr' 
          : $language === 'ar' 
            ? 'rtl' 
            : 'ltr';
  
  // Size classes
  $: sizeClasses = {
    sm: 'py-1.5 px-3 text-sm',
    default: 'py-2 px-4 text-base',
    lg: 'py-3 px-5 text-lg'
  }[size] || sizeClasses.default;
  
  // Generate the input classes
  $: inputClasses = [
    "block w-full rounded-lg border transition-all duration-200",
    "bg-cosmos-bg text-cosmos-text",
    "border-cosmos-bg-light",
    "focus:outline-none focus:ring-2 focus:ring-primary focus:ring-opacity-25 focus:border-primary",
    "disabled:opacity-60 disabled:cursor-not-allowed",
    "placeholder:text-cosmos-text-muted",
    error ? "border-red-500 focus:border-red-500 focus:ring-red-500 focus:ring-opacity-25" : "",
    sizeClasses,
    icon && iconPosition === 'left' ? 'pl-10' : '',
    icon && iconPosition === 'right' ? 'pr-10' : '',
  ].filter(Boolean).join(' ');
  
  // Generate unique IDs for associated elements
  $: errorId = id ? `${id}-error` : undefined;
  $: helpTextId = id ? `${id}-description` : undefined;
  $: labelId = id ? `${id}-label` : undefined;
  
  // Calculate the aria-describedby attribute
  $: describedBy = [
    error && errorId ? errorId : null,
    helpText && helpTextId ? helpTextId : null,
  ].filter(Boolean).join(' ') || undefined;
</script>

<div class="w-full mb-4">
  {#if label}
    <label 
      for={id} 
      id={labelId}
      class="block mb-1.5 text-sm font-medium text-cosmos-text"
    >
      {label} {#if required}<span class="text-error ml-0.5">*</span>{/if}
    </label>
  {/if}
  
  <div class="relative">
    {#if icon && iconPosition === 'left'}
      <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-cosmos-text-muted">
        <svelte:component this={icon} size={18} />
      </div>
    {/if}
    
    <input
      {id}
      {type}
      {name}
      bind:value
      {placeholder}
      {disabled}
      {required}
      {readonly}
      {maxLength}
      {minLength}
      {autocomplete}
      {dir}
      class={inputClasses}
      aria-invalid={error ? 'true' : 'false'}
      aria-describedby={describedBy}
      {...$$restProps}
    />
    
    {#if icon && iconPosition === 'right'}
      <div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none text-cosmos-text-muted">
        <svelte:component this={icon} size={18} />
      </div>
    {/if}
  </div>
  
  {#if error}
    <p id={errorId} class="mt-1.5 text-sm text-red-500">{error}</p>
  {:else if helpText}
    <p id={helpTextId} class="mt-1.5 text-sm text-cosmos-text-muted">{helpText}</p>
  {/if}
</div>