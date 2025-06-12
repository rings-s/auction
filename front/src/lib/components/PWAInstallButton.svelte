<script>
	import { onMount } from 'svelte';
	import { browser } from '$app/environment';

	let deferredPrompt = null;
	let showInstallButton = false;
	let isStandalone = false;
	let debugInfo = '';

	onMount(() => {
		if (browser) {
			console.log('PWAInstallButton mounted');
			
			// Check if app is already installed
			isStandalone = window.matchMedia('(display-mode: standalone)').matches || 
						   window.navigator.standalone === true;

			debugInfo = `Standalone: ${isStandalone}`;
			console.log('PWA Debug:', debugInfo);

			if (!isStandalone) {
				// Listen for install prompt
				window.addEventListener('beforeinstallprompt', (e) => {
					console.log('beforeinstallprompt fired');
					e.preventDefault();
					deferredPrompt = e;
					showInstallButton = true;
				});

				// Listen for app installed
				window.addEventListener('appinstalled', () => {
					console.log('PWA was installed');
					showInstallButton = false;
					deferredPrompt = null;
					isStandalone = true;
				});

				// Force show button for testing (remove in production)
				setTimeout(() => {
					if (!isStandalone) {
						showInstallButton = true;
						console.log('Forcing install button visibility for testing');
					}
				}, 1000);
			}
		}
	});

	async function handleInstall() {
		console.log('Install button clicked');
		
		if (!deferredPrompt) {
			// Manual install instructions
			alert('To install this app:\n\n1. Click the menu button (⋮) in your browser\n2. Select "Install app" or "Add to Home Screen"\n\nOr use Chrome\'s address bar install icon if available.');
			return;
		}

		try {
			deferredPrompt.prompt();
			const { outcome } = await deferredPrompt.userChoice;
			
			console.log('Install prompt outcome:', outcome);
			
			deferredPrompt = null;
			showInstallButton = false;
		} catch (error) {
			console.error('Install error:', error);
		}
	}
</script>

<!-- Always show for testing - remove the conditional in production -->
{#if showInstallButton || !isStandalone}
	<div class="fixed top-4 right-4 z-50">
		<button
			type="button"
			class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors shadow-lg"
			on:click={handleInstall}
			title="Install App"
		>
			<svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v12m0-12l-4 4m4-4l4 4m-8 6h8"></path>
			</svg>
			📱 Install App
		</button>
	</div>
{/if}

<!-- Debug info for testing -->
{#if browser && !isStandalone}
	<div class="fixed bottom-4 right-4 z-50 bg-black text-white text-xs p-2 rounded opacity-75">
		Debug: {debugInfo}
	</div>
{/if}