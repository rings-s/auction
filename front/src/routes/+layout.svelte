<script>
	import '../app.css';
	import { onMount, onDestroy } from 'svelte';
	import { theme } from '$lib/stores/theme';
	import { locale } from '$lib/i18n/config.js';
	import { user } from '$lib/stores/user';
	import { fetchUserProfile } from '$lib/api/auth';
	import { browser } from '$app/environment';

	import Navbar from '$lib/components/layout/Navbar.svelte';
	import Footer from '$lib/components/layout/Footer.svelte';
	import ToastContainer from '$lib/components/ToastContainer.svelte';
	import PWAInstallButton from '$lib/components/PWAInstallButton.svelte'; // Add this import

	// ... rest of your existing script code ...
</script>

<svelte:head>
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<title>Real Estate Auction Platform</title>
	
	<!-- PWA Manifest -->
	<link rel="manifest" href="/manifest.json">
	
	<!-- PWA Meta Tags -->
	<meta name="theme-color" content="#a78bfa">
	<meta name="apple-mobile-web-app-capable" content="yes">
	<meta name="apple-mobile-web-app-status-bar-style" content="default">
	<meta name="apple-mobile-web-app-title" content="Auction">
	<meta name="mobile-web-app-capable" content="yes">
	<meta name="msapplication-TileColor" content="#a78bfa">
	<meta name="msapplication-tap-highlight" content="no">
	
	<!-- Apple Touch Icons -->
	<link rel="apple-touch-icon" sizes="152x152" href="/icons/icon-152x152.png">
	<link rel="apple-touch-icon" sizes="180x180" href="/icons/icon-192x192.png">
	
	<!-- Load fonts with display=swap for better performance -->
	<link 
		href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Cairo:wght@400;600;700;800;900&display=swap" 
		rel="stylesheet"
	>
</svelte:head>

<!-- Always render consistent structure to prevent hydration mismatch -->
<div 
	class="min-h-screen flex flex-col bg-white dark:bg-gray-800 transition-colors duration-200"
	class:font-cairo={currentLocale === 'ar'}
	class:font-inter={currentLocale !== 'ar'}
>
	{#if error}
		<!-- Error state -->
		<div class="flex items-center justify-center min-h-screen bg-red-50 dark:bg-red-900/20">
			<div class="text-center p-8">
				<h1 class="text-2xl font-bold text-red-600 dark:text-red-400 mb-4">
					Layout Error
				</h1>
				<p class="text-gray-600 dark:text-gray-400 mb-4">
					{error}
				</p>
				<button 
					onclick={() => window.location.reload()} 
					class="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
				>
					Reload Page
				</button>
			</div>
		</div>
	{:else}
		<!-- PWA Install Button - Add this -->
		<div class="fixed top-4 right-4 z-50">
			<PWAInstallButton />
		</div>
		
		<!-- Navigation with fallback -->
		{#if componentsLoaded.navbar}
			<Navbar on:error={handleNavbarError} />
		{:else}
			<div class="h-16 bg-gray-100 dark:bg-gray-800 flex items-center justify-center border-b border-gray-200 dark:border-gray-700">
				<span class="text-gray-500 dark:text-gray-400">Navigation loading...</span>
			</div>
		{/if}
		
		<!-- Main content area -->
		<main class="flex-grow">
			<slot />
		</main>
		
		<!-- Footer with fallback -->
		{#if componentsLoaded.footer}
			<Footer on:error={handleFooterError} />
		{:else}
			<div class="h-24 bg-gray-100 dark:bg-gray-800 flex items-center justify-center border-t border-gray-200 dark:border-gray-700">
				<span class="text-gray-500 dark:text-gray-400">Footer loading...</span>
			</div>
		{/if}
		
		<!-- Toast notifications -->
		{#if componentsLoaded.toast}
			<ToastContainer on:error={handleToastError} />
		{/if}
	{/if}
</div>


<style>
	/* Global font classes with fallbacks */
	:global(.font-cairo) {
		font-family: 'Cairo', 'Inter', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
	}
	
	:global(.font-inter) {
		font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
	}
	
	/* Apply fonts globally based on direction with fallbacks */
	:global([dir="rtl"]) {
		font-family: 'Cairo', 'Inter', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
	}
	
	:global([dir="ltr"]) {
		font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
	}
	
	/* Ensure smooth transitions */
	:global(html) {
		transition: color-scheme 0.2s ease;
	}
	
	:global(body) {
		transition: background-color 0.2s ease, color 0.2s ease;
	}
	
	/* Prevent layout shift during font loading */
	:global(*) {
		font-display: swap;
	}
	
	/* Loading states */
	:global(.component-loading) {
		opacity: 0.7;
		transition: opacity 0.2s ease;
	}
	
	:global(.component-error) {
		border: 2px dashed #ef4444;
		background-color: #fef2f2;
		color: #dc2626;
	}
</style>