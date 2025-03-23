<!-- src/lib/components/ui/Toast.svelte -->
<script>
    /**
     * Toast Component
     * Displays temporary notifications with various styles.
     */
    import { fade, fly } from 'svelte/transition';
    import { createEventDispatcher } from 'svelte';
    
    const dispatch = createEventDispatcher();
    
    // Props
    export let id = crypto.randomUUID(); // Unique ID for toast
    export let type = 'info'; // info, success, error, warning
    export let message = ''; // Toast message
    export let title = undefined; // Optional toast title
    export let dismissible = true; // Can be dismissed manually
    export let duration = 5000; // Auto-dismiss after duration (ms), 0 for no auto-dismiss
    export let position = 'bottom-right'; // Position: top-right, top-left, bottom-right, bottom-left, top-center, bottom-center
    export let showIcon = true; // Show status icon
    
    // Determine icon based on type
    function getIcon(type) {
      switch (type) {
        case 'success':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>`;
        case 'error':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>`;
        case 'warning':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>`;
        case 'info':
        default:
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>`;
      }
    }
    
    // Get accent color based on type
    $: accentColor = type === 'success' ? 'bg-status-success' :
                    type === 'error' ? 'bg-status-error' :
                    type === 'warning' ? 'bg-status-warning' :
                    'bg-status-info';
    
    // Auto-dismiss timer
    import { onMount, onDestroy } from 'svelte';
    
    let timer;
    
    onMount(() => {
      if (duration > 0) {
        timer = setTimeout(() => {
          dismiss();
        }, duration);
      }
    });
    
    onDestroy(() => {
      if (timer) clearTimeout(timer);
    });
    
    function dismiss() {
      dispatch('dismiss', { id });
    }
  </script>
  
  <div
    id={`toast-${id}`}
    in:fly={{ y: 50, duration: 300 }}
    out:fade={{ duration: 200 }}
    class="bg-cosmos-bg-dark w-full max-w-xs flex items-center overflow-hidden rounded-lg shadow-lg"
    role="alert"
    aria-live="polite"
  >
    <div class={`${accentColor} w-1.5 self-stretch`}></div>
    
    {#if showIcon}
      <div class="p-3 text-cosmos-text-muted flex-shrink-0">
        {@html getIcon(type)}
      </div>
    {/if}
    
    <div class="p-3 flex-grow text-cosmos-text">
      {#if title}
        <h4 class="font-medium text-sm">{title}</h4>
      {/if}
      <p class={title ? 'mt-1 text-sm' : 'text-sm'}>
        {message}
        <slot></slot>
      </p>
    </div>
    
    {#if dismissible}
      <button
        class="p-2 text-cosmos-text-muted hover:text-cosmos-text flex-shrink-0"
        on:click={dismiss}
        aria-label="Dismiss"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-5 w-5"
          viewBox="0 0 20 20"
          fill="currentColor"
        >
          <path
            fill-rule="evenodd"
            d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
            clip-rule="evenodd"
          />
        </svg>
      </button>
    {/if}
  </div>