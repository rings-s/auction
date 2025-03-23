<!-- src/lib/components/ui/Input.svelte -->
<script>
    import { t } from '$lib/i18n';
    
    // Props
    export let type = 'text';
    export let name = '';
    export let value = '';
    export let placeholder = '';
    export let label = undefined;
    export let error = undefined;
    export let disabled = false;
    export let required = false;
    export let dir = 'auto'; // auto, rtl, ltr
    export let icon = undefined; // Icon to display
    export let iconPosition = 'left'; // left, right
  </script>
  
  <div class="w-full">
    {#if label}
      <label for={name} class="block text-sm font-medium text-cosmos-text mb-1">
        {label} {#if required}<span class="text-primary">*</span>{/if}
      </label>
    {/if}
    
    <div class="relative">
      {#if icon && iconPosition === 'left'}
        <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-cosmos-text-muted">
          <svelte:component this={icon} size={18} />
        </div>
      {/if}
      
      <input
        {type}
        {name}
        id={name}
        bind:value
        {placeholder}
        {disabled}
        {dir}
        {required}
        class="py-2 px-4 block w-full rounded-lg border transition-all
              bg-cosmos-bg text-cosmos-text
              border-cosmos-bg-light focus:border-primary
              focus:ring focus:ring-primary focus:ring-opacity-25
              placeholder-cosmos-text-muted
              disabled:opacity-60 disabled:cursor-not-allowed"
        class:pl-10={icon && iconPosition === 'left'}
        class:pr-10={icon && iconPosition === 'right'}
        class:border-red-500={error}
        class:focus:border-red-500={error}
        class:focus:ring-red-500={error}
        on:blur
        on:focus
        on:input
        on:change
        {...$$restProps}
      />
      
      {#if icon && iconPosition === 'right'}
        <div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none text-cosmos-text-muted">
          <svelte:component this={icon} size={18} />
        </div>
      {/if}
    </div>
    
    {#if error}
      <p class="mt-1 text-sm text-red-500">{error}</p>
    {/if}
  </div>