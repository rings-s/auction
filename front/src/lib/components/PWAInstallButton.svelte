<script>
    import { onMount } from 'svelte';
    import { browser } from '$app/environment';
  
    let deferredPrompt = null;
    let showInstallButton = false;
  
    onMount(() => {
      if (browser) {
        window.addEventListener('beforeinstallprompt', (e) => {
          e.preventDefault();
          deferredPrompt = e;
          showInstallButton = true;
        });
  
        window.addEventListener('appinstalled', () => {
          console.log('PWA was installed');
          showInstallButton = false;
          deferredPrompt = null;
        });
      }
    });
  
    async function handleInstall() {
      if (!deferredPrompt) return;
  
      deferredPrompt.prompt();
      const { outcome } = await deferredPrompt.userChoice;
      
      if (outcome === 'accepted') {
        console.log('User accepted the install prompt');
      } else {
        console.log('User dismissed the install prompt');
      }
      
      deferredPrompt = null;
      showInstallButton = false;
    }
  </script>
  
  {#if showInstallButton}
    <button
      type="button"
      class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
      on:click={handleInstall}
    >
      <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
      </svg>
      Install App
    </button>
  {/if}