<script>
  /**
   * Modern Alert component with animations for the GUDIC platform
   */
  import { createEventDispatcher, onMount } from 'svelte';
  import { fly, fade } from 'svelte/transition';
  
  export let variant = 'info'; // info, success, warning, error
  export let title = '';
  export let dismissible = false;
  export let icon = true;
  export let autoClose = false;
  export let duration = 5000; // ms
  
  const dispatch = createEventDispatcher();
  
  // Auto-close timer
  let timer;
  
  onMount(() => {
    if (autoClose) {
      timer = setTimeout(() => {
        dismiss();
      }, duration);
    }
    
    return () => {
      if (timer) clearTimeout(timer);
    };
  });
  
  function dismiss() {
    if (timer) clearTimeout(timer);
    dispatch('dismiss');
  }
  
  // Variant styles with our custom color palette
  $: variantStyles = {
    info: {
      container: 'bg-primary-blue/10 border-l-4 border-secondary-blue',
      icon: 'text-secondary-blue',
      title: 'text-secondary-blue',
      content: 'text-text-dark',
    },
    success: {
      container: 'bg-success/10 border-l-4 border-success',
      icon: 'text-success',
      title: 'text-success',
      content: 'text-text-dark',
    },
    warning: {
      container: 'bg-warning/10 border-l-4 border-warning',
      icon: 'text-warning',
      title: 'text-warning',
      content: 'text-text-dark',
    },
    error: {
      container: 'bg-error/10 border-l-4 border-error',
      icon: 'text-error',
      title: 'text-error',
      content: 'text-text-dark',
    },
  };
  
  // Icons based on variant
  $: iconSvg = {
    info: `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
      <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
    </svg>`,
    success: `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
    </svg>`,
    warning: `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
      <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
    </svg>`,
    error: `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
    </svg>`,
  };
</script>

<div 
  class="relative rounded-xl shadow-sm overflow-hidden mb-4 backdrop-blur-sm {variantStyles[variant].container}"
  role="alert"
  in:fly={{ y: 20, duration: 300 }}
  out:fade={{ duration: 200 }}
>
  <div class="flex p-4">
    {#if icon}
      <div class="flex-shrink-0 {variantStyles[variant].icon}">
        {@html iconSvg[variant]}
      </div>
    {/if}
    
    <div class={icon ? 'ml-3 flex-1' : 'flex-1'}>
      {#if title}
        <h3 class="text-sm font-medium {variantStyles[variant].title}">
          {title}
        </h3>
      {/if}
      
      <div class="text-sm {variantStyles[variant].content} {title ? 'mt-1' : ''}">
        <slot />
      </div>
    </div>
    
    {#if dismissible}
      <div class="ml-auto pl-3 flex-shrink-0">
        <button
          type="button"
          class="inline-flex rounded-full p-1.5 focus:outline-none focus:ring-2 focus:ring-offset-2 
            bg-transparent transition-colors duration-200
            hover:bg-black hover:bg-opacity-5
            {variantStyles[variant].icon}
            focus:ring-offset-white
            focus:ring-{variant === 'info' ? 'secondary-blue' : variant === 'success' ? 'success' : variant === 'warning' ? 'warning' : 'error'}"
          aria-label="Dismiss"
          on:click={dismiss}
        >
          <span class="sr-only">Dismiss</span>
          <svg class="h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
          </svg>
        </button>
      </div>
    {/if}
  </div>
  
  <!-- Progress bar for auto-close alerts -->
  {#if autoClose}
    <div class="absolute bottom-0 left-0 right-0 h-0.5 bg-current opacity-20">
      <div 
        class="h-full bg-current opacity-50"
        style="width: 100%; animation: countdown {duration}ms linear forwards;"
      ></div>
    </div>
  {/if}
</div>

<style>
  @keyframes countdown {
    from { width: 100%; }
    to { width: 0%; }
  }
  
  /* Add subtle pulsing animation for error alerts */
  div[role="alert"].bg-error\/10 {
    animation: subtle-pulse 2s infinite;
  }
  
  @keyframes subtle-pulse {
    0% { background-color: rgba(var(--error), 0.08); }
    50% { background-color: rgba(var(--error), 0.12); }
    100% { background-color: rgba(var(--error), 0.08); }
  }
</style>