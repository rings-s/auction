<!-- src/lib/components/ui/Alert.svelte -->
<script>
    import { fade, fly } from 'svelte/transition';
    import { createEventDispatcher } from 'svelte';
    
    const dispatch = createEventDispatcher();
    
    // Props
    export let type = 'info'; // info, success, warning, error
    export let title = undefined;
    export let dismissible = false;
    export let showIcon = true;
    export let autoClose = false;
    export let autoCloseDelay = 5000; // ms
    
    // State
    let visible = true;
    
    // Generate CSS classes based on props
    $: typeClasses = {
      info: 'bg-blue-900 bg-opacity-20 border-blue-800 text-blue-300',
      success: 'bg-green-900 bg-opacity-20 border-green-800 text-green-300',
      warning: 'bg-yellow-900 bg-opacity-20 border-yellow-800 text-yellow-300',
      error: 'bg-red-900 bg-opacity-20 border-red-800 text-red-300'
    }[type];
    
    // Auto close timer
    import { onMount, onDestroy } from 'svelte';
    
    let timer;
    
    onMount(() => {
      if (autoClose) {
        timer = setTimeout(() => {
          close();
        }, autoCloseDelay);
      }
    });
    
    onDestroy(() => {
      if (timer) clearTimeout(timer);
    });
    
    function close() {
      visible = false;
      dispatch('close');
    }
  </script>
  
  {#if visible}
    <div
      class="flex items-start p-4 rounded-lg border my-3 {typeClasses}"
      in:fly={{ y: -20, duration: 300 }}
      out:fade={{ duration: 200 }}
      role="alert"
    >
      {#if showIcon}
        <div class="flex-shrink-0 mr-3">
          {#if type === 'info'}
            <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          {:else if type === 'success'}
            <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          {:else if type === 'warning'}
            <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          {:else if type === 'error'}
            <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          {/if}
        </div>
      {/if}
      
      <div class="flex-1">
        {#if title}
          <h3 class="text-sm font-medium mb-1">{title}</h3>
        {/if}
        <div class="text-sm">
          <slot />
        </div>
      </div>
      
      {#if dismissible}
        <button
          class="ml-auto -mx-1.5 -my-1.5 bg-transparent hover:bg-cosmos-bg-light rounded-lg p-1.5 inline-flex items-center justify-center h-8 w-8 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
          on:click={close}
          aria-label="Close"
        >
          <span class="sr-only">Close</span>
          <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      {/if}
    </div>
  {/if}