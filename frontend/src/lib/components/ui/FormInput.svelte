<!-- src/lib/components/ui/FormInput.svelte -->
<script>
    import { language } from '$lib/i18n';
    
    export let type = 'text';
    export let name = '';
    export let value = '';
    export let placeholder = '';
    export let label = '';
    export let error = null;
    export let required = false;
    export let disabled = false;
    export let dirOverride = null; // Override direction
    export let className = '';
    export let autocomplete = '';
    export let id = name;
    export let forceRTL = false;
    export let forceLTR = false;
  
    // Handle text direction
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
  </script>
  
  <div class="mb-4">
    {#if label}
      <label 
        for={id} 
        class="block mb-1.5 text-sm font-medium text-neutral-800 dark:text-white"
      >
        {label} {#if required}<span class="text-error ml-0.5">*</span>{/if}
      </label>
    {/if}
    
    <input
      {id}
      {type}
      {name}
      bind:value
      {autocomplete}
      {placeholder}
      {disabled}
      required={required}
      dir={dir}
      class="w-full px-4 py-2.5 rounded-xl text-neutral-900 dark:text-white 
        bg-white dark:bg-neutral-800 
        border border-neutral-200 dark:border-neutral-700
        focus:ring-2 focus:ring-primary-300 dark:focus:ring-primary-800 focus:border-primary
        disabled:opacity-60 placeholder:text-neutral-400 dark:placeholder:text-neutral-500
        transition duration-200 ease-in-out
        {error ? 'border-error focus:ring-error/25 focus:border-error' : ''}
        {className}"
    />
    
    {#if error}
      <p class="mt-1 text-sm text-error">{error}</p>
    {/if}
  </div>