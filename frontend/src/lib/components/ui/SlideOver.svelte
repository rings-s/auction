<!-- src/lib/components/ui/SlideOver.svelte -->
<script>
    import { fade, fly } from 'svelte/transition';
    import { quintOut } from 'svelte/easing';
    
    // Props
    export let open = false;         // Controls whether the slide-over is visible
    export let title = '';           // Optional title for the header
    export let position = 'right';   // 'right' or 'left'
    export let maxWidth = 'md';      // 'sm', 'md', 'lg', 'xl', 'full'
    export let closeOnClickOutside = true;
    
    // Event handlers
    export let onClose = () => { open = false; };
    
    // Max width classes
    const maxWidthClasses = {
      sm: 'max-w-sm',
      md: 'max-w-md',
      lg: 'max-w-lg',
      xl: 'max-w-xl',
      '2xl': 'max-w-2xl',
      '3xl': 'max-w-3xl',
      full: 'max-w-full',
    };
    
    // Position classes
    const positionClasses = {
      right: 'right-0',
      left: 'left-0',
    };
    
    // Fly animation config
    const flyConfig = {
      x: position === 'right' ? 300 : -300,
      duration: 300,
      easing: quintOut
    };
    
    function handleOutsideClick() {
      if (closeOnClickOutside) {
        onClose();
      }
    }
  </script>
  
  {#if open}
    <div 
      class="fixed inset-0 bg-slate-900/50 z-50 backdrop-blur-sm transition-opacity duration-300"
      on:click={handleOutsideClick}
      on:keydown={(e) => { if (e.key === 'Enter' || e.key === ' ') handleOutsideClick() }}
      role="button"
      tabindex="0"
      in:fade={{ duration: 200 }}
      out:fade={{ duration: 150 }}
    >
      <div 
        class="fixed inset-y-0 {positionClasses[position]} w-full {maxWidthClasses[maxWidth]} bg-white shadow-xl overflow-y-auto"
        role="dialog"
        tabindex="-1"
        in:fly={flyConfig}
        out:fly={{ ...flyConfig, x: flyConfig.x, duration: 250 }}
      >
        <!-- Header -->
        {#if title || $$slots.header}
          <div class="sticky top-0 z-10 bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between">
            {#if $$slots.header}
              <slot name="header">
                <h3 class="text-lg font-semibold text-text-dark">{title}</h3>
              </slot>
            {:else}
              <h3 class="text-lg font-semibold text-text-dark">{title}</h3>
            {/if}
            
            <button 
              class="p-2 rounded-full hover:bg-slate-100 transition-colors"
              on:click={onClose}
              aria-label="Close panel"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        {/if}
        
        <!-- Content -->
        <div class={$$slots.header || title ? 'p-6' : 'p-0'}>
          <slot></slot>
        </div>
        
        <!-- Footer (if provided) -->
        {#if $$slots.footer}
          <div class="sticky bottom-0 z-10 bg-white border-t border-slate-200 px-6 py-4">
            <slot name="footer"></slot>
          </div>
        {/if}
      </div>
    </div>
  {/if}
  
  <style>
    /* Hide scrollbar in Firefox */
    .overflow-y-auto {
      scrollbar-width: thin;
      scrollbar-color: rgba(156, 163, 175, 0.5) rgba(243, 244, 246, 0.7);
    }
    
    /* Hide scrollbar in Chrome, Safari, Edge */
    .overflow-y-auto::-webkit-scrollbar {
      width: 4px;
    }
    
    .overflow-y-auto::-webkit-scrollbar-track {
      background: rgba(243, 244, 246, 0.7);
    }
    
    .overflow-y-auto::-webkit-scrollbar-thumb {
      background-color: rgba(156, 163, 175, 0.5);
      border-radius: 3px;
    }
  </style>