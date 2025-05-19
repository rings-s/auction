<!-- src/lib/components/Modal.svelte -->
<script>
    import { onMount, onDestroy, createEventDispatcher } from 'svelte';
    import { fade, fly } from 'svelte/transition';
    
    export let show = false;
    export let title = '';
    export let maxWidth = 'md'; // 'sm', 'md', 'lg', 'xl', 'full'
    export let closeOnEscape = true;
    export let closeOnClickOutside = true;
    
    const dispatch = createEventDispatcher();
    let modal;
    
    const widthClasses = {
      sm: 'max-w-sm',
      md: 'max-w-md',
      lg: 'max-w-lg',
      xl: 'max-w-xl',
      '2xl': 'max-w-2xl',
      '3xl': 'max-w-3xl',
      '4xl': 'max-w-4xl',
      '5xl': 'max-w-5xl',
      '6xl': 'max-w-6xl',
      '7xl': 'max-w-7xl',
      full: 'max-w-full'
    };
    
    $: modalClass = `w-full ${widthClasses[maxWidth] || widthClasses.md} mx-auto`;
    
    function close() {
      show = false;
      dispatch('close');
    }
    
    function handleKeydown(e) {
      if (closeOnEscape && e.key === 'Escape' && show) {
        close();
      }
    }
    
    function handleClickOutside(e) {
      if (closeOnClickOutside && modal && !modal.contains(e.target) && show) {
        close();
      }
    }
    
    onMount(() => {
      document.addEventListener('keydown', handleKeydown);
      return () => {
        document.removeEventListener('keydown', handleKeydown);
      };
    });
  </script>
  
  <!-- Trap focus inside the modal when it's open -->
  <svelte:window on:keydown={handleKeydown} />
  
  {#if show}
    <div 
      class="fixed inset-0 z-50 overflow-y-auto"
      aria-labelledby={title ? 'modal-title' : undefined}
      role="dialog"
      aria-modal="true"
      transition:fade={{ duration: 200 }}
    >
      <!-- Background overlay -->
      <div 
        class="fixed inset-0 bg-gray-500 bg-opacity-75 dark:bg-gray-900 dark:bg-opacity-75 transition-opacity"
        on:click={handleClickOutside}
      ></div>
      
      <!-- Modal container -->
      <div class="flex items-center justify-center min-h-screen p-4 text-center sm:p-0">
        <!-- Modal panel -->
        <div
          bind:this={modal}
          class={modalClass}
          transition:fly={{ y: 30, duration: 300 }}
        >
          <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl overflow-hidden transform transition-all">
            {#if title}
              <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                <h3 class="text-lg font-medium text-gray-900 dark:text-white" id="modal-title">
                  {title}
                </h3>
              </div>
            {/if}
            
            <!-- Modal content -->
            <slot></slot>
            
            <!-- Close button in top right corner -->
            <button
              type="button"
              class="absolute top-3 right-3 text-gray-400 hover:text-gray-500 dark:hover:text-gray-300"
              on:click={close}
              aria-label="Close"
            >
              <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  {/if}