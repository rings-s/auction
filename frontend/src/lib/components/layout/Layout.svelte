<!-- src/lib/components/layout/Layout.svelte -->
<script>
	import { onMount, onDestroy } from 'svelte';
	import { browser } from '$app/environment';
	import { isAuthenticated, currentUser, authStore } from '$lib/stores/auth';
	import { language, t } from '$lib/i18n';
	import { toast } from '$lib/stores/toast';

	// Import components
	import ToastContainer from '$lib/components/ui/ToastContainer.svelte';
	import Header from '$lib/components/layout/Header.svelte';
	import Footer from '$lib/components/layout/Footer.svelte';

	// Import app.css with the correct path for SvelteKit aliases
	// The $app path aliases won't work for CSS, so don't use a relative path here
	// Instead, app.css should be imported in your root layout (+layout.svelte)

	// Props
	export let showHeader = true;
	export let showFooter = true;
	export let fullWidth = false;
	export let title = '';

	// States
	let menuOpen = false;
	let tokenRefreshTimer;
	let starsEl;
	let ready = false;

	onMount(() => {
		// These operations should only run in the browser
		if (browser) {
			ready = true;

			// Set up token refresh timer
			setupTokenRefresh();

			// Generate stars for cosmic background
			if (starsEl) {
				generateStars();
			}

			// Set language attributes on document
			updateDocumentLanguage($language);
		}
	});

	// Update document language attributes when language changes
	function updateDocumentLanguage(lang) {
		if (browser && lang) {
			document.documentElement.lang = lang;
			document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr';
		}
	}

	// Reactive statement to handle language changes
	$: if (browser && $language) {
		updateDocumentLanguage($language);
	}

	// Toggle mobile menu
	function toggleMenu() {
		menuOpen = !menuOpen;
	}

	// Set up token refresh timer - with browser safety check
	function setupTokenRefresh() {
		if (!browser) return;
		
		if (tokenRefreshTimer) {
			clearTimeout(tokenRefreshTimer);
		}

		if (!$isAuthenticated) {
			return;
		}

		// Refresh token 5 minutes before it expires
		const tokenExpiry = $currentUser?.tokenExpiry;
		if (tokenExpiry) {
			const now = Math.floor(Date.now() / 1000);
			const expiresIn = tokenExpiry - now;

			// If token expires in less than 6 minutes, refresh now
			if (expiresIn < 360) {
				authStore.refreshToken();
			}

			// Set timer to refresh 5 minutes before expiry
			const refreshTime = Math.max((expiresIn - 300) * 1000, 10000); // Min 10 seconds
			tokenRefreshTimer = setTimeout(() => {
				authStore.refreshToken();
			}, refreshTime);
		}
	}

	// Reactive statement to monitor authentication state changes
	$: if (browser && $isAuthenticated) {
		// Set up token refresh whenever authentication status changes
		setupTokenRefresh();
	}

	// Clean up on component destroy
	onDestroy(() => {
		if (browser && tokenRefreshTimer) {
			clearTimeout(tokenRefreshTimer);
		}
	});

	// Stars effect for the cosmic background
	function generateStars() {
		if (!browser || !starsEl) return;
		
		const starCount = 100;
		let starsHtml = '';

		for (let i = 0; i < starCount; i++) {
			const x = Math.random() * 100;
			const y = Math.random() * 100;
			const delay = Math.random() * 15;
			const duration = 3 + Math.random() * 4;
			const size = 1 + Math.random() * 1.5;
			const opacity = 0.2 + Math.random() * 0.5;

			starsHtml += `
          <div class="absolute rounded-full bg-white opacity-${Math.floor(opacity * 10)}"
               style="left: ${x}%; top: ${y}%; width: ${size}px; height: ${size}px;
                      animation: pulse-slow ${duration}s infinite ${delay}s;"
          ></div>
        `;
		}

		starsEl.innerHTML = starsHtml;
	}

	// Get HTML direction class based on language
	function getDirectionClass() {
		return $language === 'ar' ? 'dir-rtl' : 'dir-ltr';
	}

	// Get direction class based on language
	$: directionClass = getDirectionClass();
</script>

<svelte:head>
	{#if title}
		<title>{title} | {$t('general.app_name')}</title>
	{:else}
		<title>{$t('general.app_name')}</title>
	{/if}
</svelte:head>

<!-- Main app container with language direction -->
<div class="bg-cosmos-bg-dark text-cosmos-text min-h-screen {directionClass}" class:ready>
	<!-- Night sky effect with stars -->
	<div
		class="from-cosmos-bg-dark to-cosmos-bg fixed inset-0 overflow-hidden bg-gradient-to-b"
		style="z-index: -1;"
	>
		<div bind:this={starsEl} class="stars absolute inset-0 overflow-hidden"></div>
	</div>

	<!-- Main layout structure -->
	<div class="relative flex min-h-screen flex-col" style="z-index: 0;">
		{#if showHeader}
			<Header {menuOpen} on:toggleMenu={toggleMenu} />
		{/if}

		<main class="flex-grow">
			<div
				class={fullWidth
					? 'mx-auto w-full px-4 sm:px-6 lg:px-8'
					: 'container mx-auto px-4 sm:px-6 lg:px-8'}
			>
				<div class="mt-16 mb-12">
					<!-- Page content from route -->
					<slot />
				</div>
			</div>
		</main>

		{#if showFooter}
			<Footer />
		{/if}
	</div>

	<!-- Toast notifications -->
	<ToastContainer />
</div>

<style>
	/* Smooth transitions when content loads */
	.ready {
		transition: all 0.4s ease-in-out;
	}

	/* Pulsing star animation */
	@keyframes pulse-slow {
		0%,
		100% {
			opacity: var(--opacity, 0.5);
			transform: scale(1);
		}
		50% {
			opacity: var(--opacity, 0.2);
			transform: scale(0.8);
		}
	}

	/* Fade in effect */
	.ready :global(*) {
		animation: fadeIn 0.4s forwards;
	}

	@keyframes fadeIn {
		from {
			opacity: 0;
		}
		to {
			opacity: 1;
		}
	}
</style>