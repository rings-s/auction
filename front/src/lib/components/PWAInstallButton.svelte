<script>
	import { onMount } from 'svelte';
	import { browser } from '$app/environment';

	let deferredPrompt = null;

	onMount(() => {
		if (browser) {
			// Check if the app is already installed. Do not show the button if it is.
			const isStandalone =
				window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone;
			if (isStandalone) {
				return;
			}

			window.addEventListener('beforeinstallprompt', (e) => {
				// Prevent the default browser prompt
				e.preventDefault();
				// Stash the event so it can be triggered later
				deferredPrompt = e;
			});

			window.addEventListener('appinstalled', () => {
				// Clear the prompt when the app is installed
				deferredPrompt = null;
			});
		}
	});

	async function handleInstall() {
		if (!deferredPrompt) {
			// Fallback for browsers that don't support the prompt
			alert('To install, please use the "Add to Home Screen" option in your browser menu.');
			return;
		}
		try {
			// Show the browser's install prompt
			deferredPrompt.prompt();
			// Wait for the user to respond to the prompt
			await deferredPrompt.userChoice;
			// Clear the prompt once used
			deferredPrompt = null;
		} catch (error) {
			// The user chose not to install the app
		}
	}
</script>

{#if deferredPrompt}
	<div class="fixed top-4 right-4 z-50">
		<button
			type="button"
			class="inline-flex items-center rounded-lg border border-transparent bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-lg transition-colors hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:outline-none"
			on:click={handleInstall}
			title="Install App"
		>
			<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M12 4v12m0-12l-4 4m4-4l4 4m-8 6h8"
				></path>
			</svg>
			📱 Install App
		</button>
	</div>
{/if}
