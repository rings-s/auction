<!-- src/routes/+layout.svelte -->
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
	
	// Track hydration and initialization state
	let hydrated = false;
	let mounted = false;
	let error = null;
	let componentsLoaded = {
		navbar: true,
		footer: true,
		toast: true
	};
	
	// Initialize stores with safe defaults
	let currentTheme = 'light';
	let currentLocale = 'en';
	
	// Store unsubscribe functions
	let unsubscribeTheme = () => {};
	let unsubscribeLocale = () => {};
	
	onMount(async () => {
		try {
			console.log('Layout mounting...');
			mounted = true;
			
			// Subscribe to stores safely AFTER mount
			try {
				unsubscribeTheme = theme.subscribe((value) => {
					if (value && typeof value === 'string') {
						currentTheme = value;
						if (hydrated && typeof document !== 'undefined') {
							applyDocumentClasses(currentTheme, currentLocale);
						}
					}
				});
			} catch (themeError) {
				console.warn('Theme subscription failed:', themeError);
				currentTheme = 'light';
			}
			
			try {
				unsubscribeLocale = locale.subscribe((value) => {
					if (value && typeof value === 'string') {
						currentLocale = value;
						if (hydrated && typeof document !== 'undefined') {
							applyDocumentClasses(currentTheme, currentLocale);
						}
					}
				});
			} catch (localeError) {
				console.warn('Locale subscription failed:', localeError);
				currentLocale = 'en';
			}
			
			// Safely handle localStorage operations
			if (browser && typeof localStorage !== 'undefined') {
				try {
					// Apply saved theme with validation
					const savedTheme = localStorage.getItem('theme');
					if (savedTheme && (savedTheme === 'light' || savedTheme === 'dark')) {
						theme.set(savedTheme);
						currentTheme = savedTheme;
					} else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
						theme.set('dark');
						currentTheme = 'dark';
					} else {
						theme.set('light');
						currentTheme = 'light';
					}
					
					// Apply saved locale with validation
					const savedLocale = localStorage.getItem('locale') || localStorage.getItem('app-locale');
					if (savedLocale && (savedLocale === 'en' || savedLocale === 'ar')) {
						locale.set(savedLocale);
						currentLocale = savedLocale;
					} else {
						locale.set('en');
						currentLocale = 'en';
					}
				} catch (storageError) {
					console.warn('LocalStorage access failed:', storageError);
					// Set defaults if localStorage fails
					try {
						theme.set('light');
						locale.set('en');
					} catch (setError) {
						console.warn('Store set failed:', setError);
					}
					currentTheme = 'light';
					currentLocale = 'en';
				}
				
				// Try to fetch user profile if tokens exist
				try {
					if (localStorage.getItem('accessToken')) {
						await fetchUserProfile();
					}
				} catch (profileError) {
					console.warn('Profile fetch failed:', profileError);
					// Don't let profile errors break the layout
				}
			}
			
			// Apply initial document classes safely
			if (typeof document !== 'undefined') {
				applyDocumentClasses(currentTheme, currentLocale);
			}
			
			hydrated = true;
			console.log('Layout hydrated successfully with theme:', currentTheme, 'locale:', currentLocale);
			
		} catch (mountError) {
			console.error('Mount error:', mountError);
			error = mountError.message;
			// Still mark as hydrated to show something
			hydrated = true;
		}
	});
	
	// Cleanup subscriptions
	onDestroy(() => {
		try {
			unsubscribeTheme();
			unsubscribeLocale();
		} catch (cleanupError) {
			console.warn('Cleanup error:', cleanupError);
		}
	});
	
	// Safe function to apply document classes
	function applyDocumentClasses(themeValue, localeValue) {
		if (typeof document === 'undefined' || !browser) return;
		
		try {
			const classList = document.documentElement.classList;
			const validTheme = themeValue || 'light';
			const validLocale = localeValue || 'en';
			
			// Remove existing classes
			classList.remove('light', 'dark', 'rtl', 'ltr');
			
			// Add direction class
			if (validLocale === 'ar') {
				classList.add('rtl');
			} else {
				classList.add('ltr');
			}
			
			// Add theme class
			classList.add(validTheme);
			
			// Set additional attributes
			document.documentElement.style.colorScheme = validTheme;
			document.documentElement.lang = validLocale;
			document.documentElement.dir = validLocale === 'ar' ? 'rtl' : 'ltr';
			
			console.log('Applied document classes:', validTheme, validLocale === 'ar' ? 'rtl' : 'ltr');
			
		} catch (classError) {
			console.warn('Failed to apply document classes:', classError);
		}
	}
	
	// Component error handlers
	function handleNavbarError(err) {
		console.error('Navbar error:', err);
		componentsLoaded.navbar = false;
	}
	
	function handleFooterError(err) {
		console.error('Footer error:', err);
		componentsLoaded.footer = false;
	}
	
	function handleToastError(err) {
		console.error('Toast error:', err);
		componentsLoaded.toast = false;
	}
</script>

<svelte:head>
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<title>Real Estate Auction Platform</title>
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