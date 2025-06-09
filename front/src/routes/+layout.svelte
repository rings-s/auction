<!-- src/routes/+layout.svelte -->
<script>
	import '../app.css';
	import { onMount } from 'svelte';
	import { theme } from '$lib/stores/theme';
	import { locale } from '$lib/i18n';
	import { user } from '$lib/stores/user';
	import { fetchUserProfile } from '$lib/api/auth';
	
	import Navbar from '$lib/components/layout/Navbar.svelte';
	import Footer from '$lib/components/layout/Footer.svelte';
	import ToastContainer from '$lib/components/ToastContainer.svelte';
	
	let loading = true;
	
	onMount(async () => {
	  // Apply saved theme
	  const savedTheme = localStorage.getItem('theme');
	  if (savedTheme) {
		theme.set(savedTheme);
	  } else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
		theme.set('dark');
	  }
	  
	  // Apply saved locale
	  const savedLocale = localStorage.getItem('locale');
	  if (savedLocale) {
		locale.set(savedLocale);
	  }
	  
	  // Try to fetch user profile if tokens exist
	  if (localStorage.getItem('accessToken')) {
		try {
		  await fetchUserProfile();
		} catch (error) {
		  // Silently handle profile fetch errors
		}
	  }
	  
	  loading = false;
	});
	
	// Apply theme and direction classes to document when theme or locale changes
	$: if (typeof document !== 'undefined') {
	  document.documentElement.classList.remove('light', 'dark', 'rtl', 'ltr');
	  if ($locale === 'ar') {
		document.documentElement.classList.add('rtl');
	  } else {
		document.documentElement.classList.add('ltr');
	  }
	  document.documentElement.classList.add($theme);
	  document.documentElement.style.colorScheme = $theme;
	}
	
	// Apply lang and dir attributes
	$: if (typeof document !== 'undefined') {
	  document.documentElement.lang = $locale;
	  document.documentElement.dir = $locale === 'ar' ? 'rtl' : 'ltr';
	}
  </script>
  
  <svelte:head>
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<title>Real Estate Auction Platform</title>
	<!-- Global Font Loading -->
	<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Cairo:wght@400;600;700;800;900&display=swap" rel="preload" as="style">
	<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Cairo:wght@400;600;700;800;900&display=swap" rel="stylesheet">
  </svelte:head>
  
  <div class="min-h-screen flex flex-col bg-white dark:bg-gray-800 transition-colors duration-200 
			  {$locale === 'ar' ? 'font-cairo' : 'font-inter'}">
	{#if !loading}
	  <Navbar />
	  
	  <main class="flex-grow">
		<slot />
	  </main>
	  
	  <Footer />
	{:else}
	  <div class="flex items-center justify-center min-h-screen">
		<div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
	  </div>
	{/if}
	<ToastContainer />
  </div>
  
  <style>
	/* Global Font Classes */
	:global(.font-cairo) {
	  font-family: 'Cairo', 'Inter', system-ui, -apple-system, sans-serif;
	}
	
	:global(.font-inter) {
	  font-family: 'Inter', system-ui, -apple-system, sans-serif;
	}
	
	/* Apply fonts globally based on direction */
	:global([dir="rtl"]) {
	  font-family: 'Cairo', 'Inter', system-ui, -apple-system, sans-serif;
	}
	
	:global([dir="ltr"]) {
	  font-family: 'Inter', system-ui, -apple-system, sans-serif;
	}
  </style>