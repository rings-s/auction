<!-- src/lib/components/ui/FormAlert.svelte -->
<script>
    export let type = 'info'; // info, success, warning, error
    export let dismissible = false;
    export let className = '';
    
    let visible = true;
    
    // Types with colors
    const types = {
      info: {
        bg: 'bg-primary-50 dark:bg-primary-900/20',
        border: 'border-primary-200 dark:border-primary-900/30',
        text: 'text-primary-800 dark:text-primary-200',
        icon: 'text-primary-500 dark:text-primary-400'
      },
      success: {
        bg: 'bg-green-50 dark:bg-green-900/20',
        border: 'border-green-200 dark:border-green-900/30',
        text: 'text-green-800 dark:text-green-200',
        icon: 'text-green-500 dark:text-green-400'
      },
      warning: {
        bg: 'bg-amber-50 dark:bg-amber-900/20',
        border: 'border-amber-200 dark:border-amber-900/30',
        text: 'text-amber-800 dark:text-amber-200',
        icon: 'text-amber-500 dark:text-amber-400'
      },
      error: {
        bg: 'bg-red-50 dark:bg-red-900/20',
        border: 'border-red-200 dark:border-red-900/30',
        text: 'text-red-800 dark:text-red-200',
        icon: 'text-red-500 dark:text-red-400'
      }
    };
    
    // Icons for each type
    const icons = {
      info: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-5 h-5">
        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a.75.75 0 000 1.5h.253a.25.25 0 01.244.304l-.459 2.066A1.75 1.75 0 0010.747 15H11a.75.75 0 000-1.5h-.253a.25.25 0 01-.244-.304l.459-2.066A1.75 1.75 0 009.253 9H9z" clip-rule="evenodd" />
      </svg>`,
      success: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-5 h-5">
        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z" clip-rule="evenodd" />
      </svg>`,
      warning: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-5 h-5">
        <path fill-rule="evenodd" d="M8.485 2.495c.673-1.167 2.357-1.167 3.03 0l6.28 10.875c.673 1.167-.17 2.625-1.516 2.625H3.72c-1.347 0-2.189-1.458-1.515-2.625L8.485 2.495zM10 5a.75.75 0 01.75.75v3.5a.75.75 0 01-1.5 0v-3.5A.75.75 0 0110 5zm0 9a1 1 0 100-2 1 1 0 000 2z" clip-rule="evenodd" />
      </svg>`,
      error: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-5 h-5">
        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.28 7.22a.75.75 0 00-1.06 1.06L8.94 10l-1.72 1.72a.75.75 0 101.06 1.06L10 11.06l1.72 1.72a.75.75 0 101.06-1.06L11.06 10l1.72-1.72a.75.75 0 00-1.06-1.06L10 8.94 8.28 7.22z" clip-rule="evenodd" />
      </svg>`
    };
    
    function dismiss() {
      visible = false;
    }
  </script>
  
  {#if visible}
    <div class="rounded-xl p-4 mb-4 border {types[type].bg} {types[type].border} {className}" role="alert">
      <div class="flex">
        <div class="flex-shrink-0 {types[type].icon}">
          {@html icons[type]}
        </div>
        
        <div class="ml-3 flex-1 {types[type].text}">
          <slot />
        </div>
        
        {#if dismissible}
          <button
            type="button"
            class="ml-auto -mx-1.5 -my-1.5 rounded-lg p-1.5 inline-flex h-8 w-8 {types[type].text} hover:bg-opacity-10 hover:bg-black"
            aria-label="Dismiss"
            on:click={dismiss}
          >
            <span class="sr-only">Dismiss</span>
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
              <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
            </svg>
          </button>
        {/if}
      </div>
    </div>
  {/if}