<!-- src/lib/components/ui/Modal.svelte -->
<script>
  import { createEventDispatcher, onMount, onDestroy } from 'svelte';
  import { fade, fly, scale } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';
  
  export let open = false;
  export let title = '';
  export let size = 'md'; // sm, md, lg, xl, full
  export let closeOnClickOutside = true;
  export let showCloseButton = true;
  export let closeOnEsc = true;
  export let marginY = 40; // Added margin-y parameter
  
  const dispatch = createEventDispatcher();
  let modalElement;
  let modalContentElement;
  let focusableElements = [];
  let firstFocusableElement;
  let lastFocusableElement;
  
  // Track whether initial mount has occurred
  let mounted = false;
  // Save the element that had focus before opening modal
  let previousActiveElement;
  
  onMount(() => {
    mounted = true;
    document.addEventListener('keydown', handleKeydown);
  });
  
  onDestroy(() => {
    document.removeEventListener('keydown', handleKeydown);
    // Make sure to clean up overflow when component is destroyed
    if (open) {
      document.body.classList.remove('overflow-hidden');
    }
  });
  
  // Watch for open state changes
  $: if (open && mounted) {
    document.body.classList.add('overflow-hidden');
    // Save the current active element to restore focus later
    previousActiveElement = document.activeElement;
    // Set up focus trap after the modal renders
    setTimeout(setupFocusTrap, 50);
  } else if (mounted) {
    document.body.classList.remove('overflow-hidden');
    // Restore focus when modal closes
    if (previousActiveElement) {
      previousActiveElement.focus();
    }
  }
  
  function setupFocusTrap() {
    if (!modalElement) return;
    
    // Get all focusable elements within the modal
    focusableElements = modalElement.querySelectorAll(
      'a[href]:not([disabled]), button:not([disabled]), textarea:not([disabled]), input[type="text"]:not([disabled]), input[type="email"]:not([disabled]), input[type="password"]:not([disabled]), input[type="number"]:not([disabled]), input[type="search"]:not([disabled]), input[type="tel"]:not([disabled]), input[type="url"]:not([disabled]), input[type="radio"]:not([disabled]), input[type="checkbox"]:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'
    );
    
    if (focusableElements.length) {
      firstFocusableElement = focusableElements[0];
      lastFocusableElement = focusableElements[focusableElements.length - 1];
      
      // Focus the first element
      firstFocusableElement.focus();
    }
  }
  
  function close() {
    dispatch('close');
  }
  
  function handleKeydown(e) {
    if (!open) return;
    
    // Close on Escape
    if (closeOnEsc && e.key === 'Escape') {
      e.preventDefault();
      close();
      return;
    }
    
    // Handle focus trap with Tab
    if (e.key === 'Tab' && focusableElements.length > 0) {
      // If shift key pressed and focus on first item, move to last item
      if (e.shiftKey && document.activeElement === firstFocusableElement) {
        e.preventDefault();
        lastFocusableElement.focus();
      } 
      // If focus on last item, cycle to first item
      else if (!e.shiftKey && document.activeElement === lastFocusableElement) {
        e.preventDefault();
        firstFocusableElement.focus();
      }
    }
  }
  
  function handleBackdropClick(e) {
    if (closeOnClickOutside && e.target === e.currentTarget) {
      close();
    }
  }
  
  // Set width based on size
  $: sizeClass = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl',
    full: 'max-w-full mx-5',
  }[size] || 'max-w-lg';
</script>

{#if open}
  <div 
    role="dialog"
    aria-modal="true"
    aria-labelledby={title ? 'modal-title' : undefined}
    class="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto"
    bind:this={modalElement}
    on:keydown={handleKeydown}
    tabindex="-1"
  >
    <!-- Backdrop overlay - using a button for a11y -->
    <button 
      class="fixed inset-0 w-full h-full bg-text-dark bg-opacity-75 backdrop-blur-sm transition-opacity cursor-default focus:outline-none"
      aria-label="Close modal"
      on:click={handleBackdropClick}
      in:fade={{ duration: 300, easing: cubicOut }}
      out:fade={{ duration: 150 }}
    ></button>
    
    <!-- Modal content with updated styling and margin-y -->
    <div 
      class="w-full {sizeClass} my-{marginY} z-10 overflow-hidden rounded-2xl bg-white shadow-xl transition-all relative"
      in:fly={{ y: 10, duration: 400, delay: 50, opacity: 0, easing: cubicOut }}
      out:scale={{ start: 1, end: 0.95, duration: 200, opacity: 0 }}
      bind:this={modalContentElement}
    >
      {#if title || showCloseButton}
        <div class="px-6 py-4 flex items-center justify-between border-b border-primary-blue/10 bg-gradient-to-r from-primary-blue/5 to-primary-peach/5">
          {#if title}
            <h3 id="modal-title" class="text-lg font-medium text-text-dark">
              {title}
            </h3>
          {:else}
            <div></div>
          {/if}
          
          {#if showCloseButton}
            <button
              type="button"
              class="text-text-light hover:text-text-dark focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-blue focus-visible:ring-offset-2 p-1 rounded-full transition-colors duration-200"
              on:click={close}
              aria-label="Close"
            >
              <svg 
                class="h-5 w-5" 
                xmlns="http://www.w3.org/2000/svg" 
                fill="none" 
                viewBox="0 0 24 24" 
                stroke="currentColor" 
                aria-hidden="true"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          {/if}
        </div>
      {/if}
      
      <div class="px-6 py-5">
        <slot />
      </div>
      
      <slot name="footer">
        {#if $$slots.footer}
          <div class="bg-neutral-50 px-6 py-4 border-t border-primary-blue/10">
            <slot name="footer" />
          </div>
        {/if}
      </slot>
    </div>
  </div>
{/if}

<style>
  /* Add subtle border glow for the modal */
  [aria-modal="true"] > div {
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1), 0 0 0 1px rgba(185, 220, 242, 0.1);
  }
  
  /* Ensure smooth transitions */
  [aria-modal="true"] > div,
  button {
    will-change: transform, opacity;
  }
</style>