<script>
  import { toasts, removeToast } from '$lib/stores/toastStore';
  import { fly } from 'svelte/transition';

  // Basic styling, can be customized extensively with Tailwind CSS
  const typeClasses = {
    info: 'bg-blue-500',
    success: 'bg-green-500',
    warning: 'bg-yellow-500',
    error: 'bg-red-500',
  };
</script>

{#if $toasts.length > 0}
  <div class="fixed bottom-0 right-0 p-4 space-y-2 z-50 max-w-sm w-full">
    {#each $toasts as toast (toast.id)}
      <div
        in:fly={{ y: 20, duration: 300 }}
        out:fly={{ y: 20, duration: 200 }}
        class="p-4 text-white rounded-md shadow-lg flex justify-between items-start {typeClasses[toast.type] || 'bg-gray-700'}"
        role="alert"
      >
        <p class="flex-grow pr-2">{toast.message}</p>
        <button
          on:click={() => removeToast(toast.id)}
          class="ml-2 p-1 -mr-1 -mt-1 rounded-full hover:bg-black hover:bg-opacity-20 focus:outline-none focus:ring-2 focus:ring-white"
          aria-label="Close"
        >
          &times;
        </button>
      </div>
    {/each}
  </div>
{/if}
