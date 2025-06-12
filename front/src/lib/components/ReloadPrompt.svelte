<script>
    import { onMount } from 'svelte';
    import { browser } from '$app/environment';
  
    let ReloadPromptComponent = null;
    let needRefresh = false;
    let updateServiceWorker = null;
  
    onMount(async () => {
      if (browser) {
        try {
          const { registerSW } = await import('virtual:pwa-register');
          
          updateServiceWorker = registerSW({
            onNeedRefresh() {
              needRefresh = true;
            },
            onOfflineReady() {
              console.log('App ready to work offline');
              showOfflineReady();
            },
            onRegistered(r) {
              console.log('SW Registered: ' + r);
            },
            onRegisterError(error) {
              console.log('SW registration error', error);
            }
          });
        } catch (error) {
          console.log('PWA registration error:', error);
        }
      }
    });
  
    function showOfflineReady() {
      // You can show a toast notification here
      console.log('App is ready to work offline!');
    }
  
    function closePrompt() {
      needRefresh = false;
    }
  
    function handleUpdate() {
      if (updateServiceWorker) {
        updateServiceWorker(true);
      }
    }
  </script>
  
  {#if needRefresh}
    <div class="fixed bottom-4 right-4 left-4 sm:left-auto sm:w-96 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-xl p-4 z-50">
      <div class="flex items-start space-x-3">
        <div class="flex-shrink-0">
          <svg class="w-6 h-6 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"></path>
          </svg>
        </div>
        <div class="flex-1 min-w-0">
          <h3 class="text-sm font-medium text-gray-900 dark:text-white">
            New version available!
          </h3>
          <p class="text-sm text-gray-500 dark:text-gray-400">
            Click reload to update to the latest version.
          </p>
        </div>
      </div>
      <div class="mt-4 flex space-x-2">
        <button
          type="button"
          class="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          on:click={handleUpdate}
        >
          Reload
        </button>
        <button
          type="button"
          class="inline-flex items-center px-3 py-2 border border-gray-300 dark:border-gray-600 text-sm leading-4 font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          on:click={closePrompt}
        >
          Later
        </button>
      </div>
    </div>
  {/if}