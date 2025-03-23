<!-- src/lib/components/ui/Modal.svelte -->
<script>
    /**
     * Modal Component
     * A flexible modal dialog with customizable header, body, and footer sections.
     */
    import { fade, fly } from 'svelte/transition';
    import { createEventDispatcher } from 'svelte';
    import { language } from '$lib/i18n';
    
    const dispatch = createEventDispatcher();
    
    // Props
    export let isOpen = false;
    export let title = "";
    export let size = "md"; // xs, sm, md, lg, xl, full
    export let closeOnClickOutside = true;
    export let closeOnEscape = true;
    export let hideCloseButton = false;
    export let preventBodyScroll = true;
    export let backdropBlur = true;
    export let position = "center"; // center, top, bottom
    export let zIndex = "z-50";
    
    // Local state
    let isRTL = false;
    let previousOverflow = '';
    
    // Set RTL direction based on language
    $: isRTL = $language === 'ar';
    
    // Modal size classes
    $: sizeClasses = {
      xs: "max-w-xs",
      sm: "max-w-sm",
      md: "max-w-md",
      lg: "max-w-lg",
      xl: "max-w-xl",
      "2xl": "max-w-2xl",
      "3xl": "max-w-3xl",
      "4xl": "max-w-4xl",
      "5xl": "max-w-5xl",
      "6xl": "max-w-6xl",
      "7xl": "max-w-7xl",
      full: "max-w-full"
    }[size] || "max-w-md";
    
    // Position classes
    $: positionClasses = {
      center: "items-center justify-center",
      top: "items-start justify-center pt-10",
      bottom: "items-end justify-center pb-10"
    }[position] || "items-center justify-center";
    
    // Handle click outside
    function handleClickOutside() {
      if (closeOnClickOutside) {
        close();
      }
    }
    
    // Handle escape key press
    function handleKeydown(e) {
      if (closeOnEscape && e.key === 'Escape' && isOpen) {
        e.preventDefault();
        close();
      }
    }
    
    // Close the modal
    function close() {
      isOpen = false;
      dispatch('close');
    }
    
    // Update modal state based on isOpen
    $: if (isOpen && preventBodyScroll && typeof document !== 'undefined') {
      previousOverflow = document.body.style.overflow;
      document.body.style.overflow = 'hidden';
    } else if (!isOpen && preventBodyScroll && typeof document !== 'undefined') {
      document.body.style.overflow = previousOverflow;
    }
  </script>
  
  <svelte:window on:keydown={handleKeydown} />
  
  {#if isOpen}
    <div
      class="fixed inset-0 {zIndex} flex {positionClasses} p-4"
      class:backdrop-blur-sm={backdropBlur}
      class:bg-black/60={!backdropBlur}
      class:bg-black/40={backdropBlur}
      transition:fade={{ duration: 200 }}
      on:click|self={handleClickOutside}
      aria-modal="true"
      role="dialog"
      dir={isRTL ? 'rtl' : 'ltr'}
    >
      <div 
        class="w-full {sizeClasses} bg-white dark:bg-neutral-800 rounded-xl shadow-xl overflow-hidden"
        transition:fly={{ y: 20, duration: 300 }}
      >
        <!-- Header -->
        {#if title || $$slots.header}
          <div class="px-6 py-4 border-b border-neutral-200 dark:border-neutral-700 flex items-center justify-between">
            <div class="flex-1">
              {#if $$slots.header}
                <slot name="header" />
              {:else}
                <h3 class="text-lg font-semibold text-neutral-900 dark:text-white">
                  {title}
                </h3>
              {/if}
            </div>
            
            {#if !hideCloseButton}
              <button
                type="button"
                class="ml-auto -mx-1.5 -my-1.5 bg-white/10 hover:bg-neutral-100 dark:hover:bg-neutral-700 rounded-lg p-1.5 inline-flex items-center justify-center h-8 w-8 focus:outline-none focus:ring-2 focus:ring-neutral-300 dark:focus:ring-neutral-600"
                on:click={close}
                aria-label="Close"
              >
                <span class="sr-only">Close</span>
                <svg class="w-4 h-4 text-neutral-500 dark:text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            {/if}
          </div>
        {/if}
        
        <!-- Body -->
        <div class="p-6 max-h-[calc(100vh-10rem)] overflow-y-auto">
          <slot />
        </div>
        
        <!-- Footer -->
        {#if $$slots.footer}
          <div class="px-6 py-4 bg-neutral-50 dark:bg-neutral-800/50 border-t border-neutral-200 dark:border-neutral-700">
            <slot name="footer" />
          </div>
        {/if}
      </div>
    </div>
  {/if}