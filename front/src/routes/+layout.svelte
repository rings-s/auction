<!-- src/routes/+layout.svelte -->
<script>
	import '../app.css';
	import { onMount } from 'svelte';
	import { theme } from '$lib/stores/theme';

	import { locale } from '$lib/i18n/i18n';
	import { user } from '$lib/stores/user';
	import { fetchUserProfile } from '$lib/api/auth';
	
	import Navbar from '$lib/components/Navbar.svelte';
	import Footer from '$lib/components/Footer.svelte';
	
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
		  console.error('Failed to fetch user profile:', error);
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
	  document.documentElement.classList.add($theme); // always add theme last
	}
	
	// Apply lang and dir attributes
	$: if (typeof document !== 'undefined') {
	  document.documentElement.lang = $locale;
	  document.documentElement.dir = $locale === 'ar' ? 'rtl' : 'ltr';
	}
  </script>
  
  <!-- Viewport meta for responsiveness -->
  <svelte:head>
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<title>Real Estate Auction Platform</title>
  </svelte:head>
  
  <div class="min-h-screen flex flex-col bg-gray-50 dark:bg-gray-900 transition-colors duration-200">
	{#if !loading}
	  <Navbar />
	  
	  <main class="flex-grow">
		<slot />
	  </main>
	  
	  <Footer />
	{:else}
	  <div class="flex items-center justify-center min-h-screen">
		<div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
	  </div>
	{/if}
  </div>