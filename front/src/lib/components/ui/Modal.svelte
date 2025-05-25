<!-- src/lib/components/Modal.svelte -->
<script lang="ts">
  import { onMount, onDestroy, createEventDispatcher } from 'svelte';
  import { fade, fly } from 'svelte/transition';
  
  export let show: boolean = false;
  export let title: string | null = null;

  type MaxWidthKey = 'sm' | 'md' | 'lg' | 'xl' | '2xl' | '3xl' | '4xl' | '5xl' | '6xl' | '7xl' | 'full';
  export let maxWidth: MaxWidthKey = 'md';

  export let closeOnEscape: boolean = true;
  export let closeOnClickOutside: boolean = true;

  let modal: HTMLDivElement | null = null;

  const dispatch = createEventDispatcher<{ close: void }>();

  function close() {
    show = false;
    dispatch('close');
  }

  // Tailwind classes for different max-widths
  const maxWidthClasses: Record<MaxWidthKey, string> = {
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

  $: modalClass = `w-full ${maxWidthClasses[maxWidth] || maxWidthClasses.md} mx-auto`;

  function handleKeydown(e: KeyboardEvent) {
    if (closeOnEscape && e.key === 'Escape' && show) {
      close();
    }
  }

  function handleClickOutside(e: MouseEvent) {
    if (closeOnClickOutside && modal && !modal.contains(e.target as Node) && show) {
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
      class="fixed inset-0 bg-gray-700 bg-opacity-75 dark:bg-gray-900 dark:bg-opacity-75 transition-opacity"
      on:click={handleClickOutside}
    ></div>
    
    <!-- Modal container -->
    <div class="flex items-center justify-center min-h-screen p-4 text-center sm:p-0 relative z-50">
      <!-- Modal panel -->
      <div
        bind:this={modal}
        class={modalClass}
        transition:fly={{ y: 30, duration: 300 }}
        style="position: relative; z-index: 60;"
      >
        <div class="bg-gray-50 dark:bg-gray-800 rounded-lg shadow-xl overflow-hidden transform transition-all relative z-50">
          {#if title}
            <div class="px-6 py-4 border-b border-gray-300 dark:border-gray-600">
              <h3 class="text-lg font-medium text-gray-700 dark:text-gray-100" id="modal-title">
                {title}
              </h3>
            </div>
          {/if}
          
          <!-- Modal content -->
          <slot></slot>
          
          <!-- Close button in top right corner -->
          <button
            type="button"
            class="absolute top-3 right-3 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
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