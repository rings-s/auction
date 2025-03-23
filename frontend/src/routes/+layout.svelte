<!-- src/routes/+layout.svelte -->
<script>
	import { onMount, onDestroy } from 'svelte';
	import { page } from '$app/stores';
	import { browser } from '$app/environment';
	import { isAuthenticated, currentUser, authStore } from '$lib/stores/auth';
	import { language, t } from '$lib/i18n';
	import { toast } from '$lib/stores/toast';
	import notifications from '$lib/stores/notification';

	// Import components
	import ToastContainer from '$lib/components/ui/ToastContainer.svelte';
	import Header from '$lib/components/layout/Header.svelte';
	import Footer from '$lib/components/layout/Footer.svelte';

	// Import styles
	import '../app.css';

	// States
	let menuOpen = false;
	let tokenRefreshTimer;
	let ready = false;

	// Expose props - fallback to default values if route layout doesn't specify them
	export let data = {};
	const { showHeader = true, showFooter = true, fullWidth = false, title = '' } = data;

	onMount(() => {
		// These operations should only run in the browser
		if (browser) {
			ready = true;

			// Set up token refresh timer
			setupTokenRefresh();

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
	<link rel="icon" href="/favicon.ico" />
</svelte:head>

<!-- Main app container with language direction -->
<div class="bg-gradient-to-br from-neutral-50 to-neutral-100 dark:from-neutral-900 dark:to-neutral-950 text-neutral-900 dark:text-white min-h-screen {directionClass}" class:ready>
	<!-- Minimalist animated background -->
	<div class="fixed top-0 left-0 right-0 bottom-0 overflow-hidden z-below">
		<!-- Large rotating circle -->
		<div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] opacity-[0.03] dark:opacity-[0.05] animate-slow-rotate">
			<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 800" class="w-full h-full text-primary">
				<circle cx="400" cy="400" r="380" fill="none" stroke="currentColor" stroke-width="1.5"></circle>
				<circle cx="400" cy="400" r="280" fill="none" stroke="currentColor" stroke-width="1"></circle>
			</svg>
		</div>
		
		<!-- Floating shapes -->
		<div class="absolute top-1/4 left-1/4 w-64 h-64 opacity-[0.04] dark:opacity-[0.06] animate-float-slow">
			<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" class="w-full h-full text-primary">
				<rect x="10" y="10" width="80" height="80" rx="8" fill="none" stroke="currentColor" stroke-width="0.5"></rect>
			</svg>
		</div>
		
		<div class="absolute bottom-1/4 right-1/4 w-48 h-48 opacity-[0.03] dark:opacity-[0.05] animate-float-slow animation-delay-1000">
			<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" class="w-full h-full text-primary">
				<polygon points="50,10 90,90 10,90" fill="none" stroke="currentColor" stroke-width="0.5"></polygon>
			</svg>
		</div>
		
		<!-- Subtle pulse circles -->
		<div class="absolute top-1/3 right-1/3 w-32 h-32 rounded-full bg-primary/[0.04] dark:bg-primary/[0.02] blur-xl animate-pulse-slow"></div>
		<div class="absolute bottom-1/3 left-1/5 w-48 h-48 rounded-full bg-primary/[0.02] dark:bg-primary/[0.01] blur-xl animate-pulse-slow animation-delay-700"></div>
		<div class="absolute top-2/3 right-1/5 w-40 h-40 rounded-full bg-secondary/[0.03] dark:bg-secondary/[0.02] blur-xl animate-pulse-slow animation-delay-1500"></div>
		
		<!-- Animated dots grid (minimal) -->
		<div class="dot-grid absolute inset-0 opacity-[0.02] dark:opacity-[0.03]"></div>
		
		<!-- Subtle overlay -->
		<div class="absolute inset-0 backdrop-blur-[1px]"></div>
	</div>

	<!-- Main layout structure -->
	<div class="relative flex min-h-screen flex-col z-base">
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

	/* Custom animations */
	@keyframes float-slow {
		0% { transform: translateY(0); }
		50% { transform: translateY(-15px); }
		100% { transform: translateY(0); }
	}
	
	@keyframes pulse-slow {
		0% { opacity: 0; }
		50% { opacity: 1; }
		100% { opacity: 0; }
	}
	
	@keyframes slow-rotate {
		0% { transform: translate(-50%, -50%) rotate(0deg); }
		100% { transform: translate(-50%, -50%) rotate(360deg); }
	}
	
	/* Animation classes */
	:global(.animate-float-slow) {
		animation: float-slow 20s ease-in-out infinite;
	}
	
	:global(.animate-pulse-slow) {
		animation: pulse-slow 15s ease-in-out infinite;
	}
	
	:global(.animate-slow-rotate) {
		animation: slow-rotate 180s linear infinite;
	}
	
	:global(.animation-delay-700) {
		animation-delay: 7s;
	}
	
	:global(.animation-delay-1000) {
		animation-delay: 10s;
	}
	
	:global(.animation-delay-1500) {
		animation-delay: 15s;
	}
	
	/* Dot grid pattern */
	:global(.dot-grid) {
		background-image: radial-gradient(currentColor 1px, transparent 1px);
		background-size: 30px 30px;
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
	
	/* Z-index layers for proper stacking */
	:global(.z-below) {
		z-index: -1;
	}
	:global(.z-base) {
		z-index: 0;
	}
	:global(.z-header) {
		z-index: 50;
	}
	:global(.z-footer) {
		z-index: 10;
	}
</style>