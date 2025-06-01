<!-- src/routes/+layout.svelte -->
<script>
	import '../app.css';
	import { onMount } from 'svelte';
	import { theme } from '$lib/stores/theme';
	import { fade } from 'svelte/transition';
	import { page } from '$app/stores';

	import { locale } from '$lib/i18n';
	import { user } from '$lib/stores/user';
	import { fetchUserProfile } from '$lib/api/auth';
	import { installSilentFetch } from '$lib/utils/silentFetch';
	
	import Navbar from '$lib/components/layout/Navbar.svelte';
	import Footer from '$lib/components/layout/Footer.svelte';
	import ToastContainer from '$lib/components/ToastContainer.svelte';
	
	let loading = true;
	let mounted = false;
	
	// Check if current page is home page
	$: isHomePage = $page.route?.id === '/';
	
	onMount(async () => {
	  // Install silent fetch to prevent browser console logs in all environments
	  installSilentFetch();
	  
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
		//   console.error('Failed to fetch user profile:', error);
		}
	  }
	  
	  loading = false;
	  mounted = true;
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
</svelte:head>

<!-- Main App Container with conditional styling -->
<div class="min-h-screen flex flex-col relative overflow-x-hidden transition-all duration-700 ease-out"
     class:home-layout={isHomePage}
     class:default-layout={!isHomePage}>
	
	<!-- Home Page Background (only for home page) -->
	{#if isHomePage}
		<div class="home-background fixed inset-0 pointer-events-none overflow-hidden z-0">
			<!-- Large Floating Orbs -->
			<div class="absolute -top-24 -left-24 w-96 h-96 bg-gradient-to-br from-violet-200 to-blue-200 dark:from-violet-500 dark:to-blue-500 rounded-full blur-3xl opacity-20 dark:opacity-10 animate-pulse"></div>
			<div class="absolute top-1/3 -right-32 w-80 h-80 bg-gradient-to-br from-blue-200 to-cyan-200 dark:from-blue-500 dark:to-cyan-500 rounded-full blur-3xl opacity-15 dark:opacity-8 animate-pulse delay-1000"></div>
			<div class="absolute -bottom-24 left-1/4 w-72 h-72 bg-gradient-to-br from-cyan-200 to-violet-200 dark:from-cyan-500 dark:to-violet-500 rounded-full blur-3xl opacity-20 dark:opacity-10 animate-pulse delay-2000"></div>
			
			<!-- Medium Floating Elements -->
			<div class="absolute top-1/2 right-1/4 w-48 h-48 bg-gradient-to-br from-indigo-200 to-purple-200 dark:from-indigo-500 dark:to-purple-500 rounded-full blur-2xl opacity-15 dark:opacity-8 animate-bounce delay-500"></div>
			<div class="absolute bottom-1/4 left-1/3 w-56 h-56 bg-gradient-to-br from-purple-200 to-pink-200 dark:from-purple-500 dark:to-pink-500 rounded-full blur-2xl opacity-20 dark:opacity-10 animate-bounce delay-1500"></div>
			
			<!-- Small Floating Dots -->
			<div class="absolute top-1/4 left-1/4 w-2 h-2 bg-violet-400 dark:bg-violet-300 rounded-full opacity-60 dark:opacity-40 animate-bounce delay-300"></div>
			<div class="absolute top-2/3 right-1/3 w-1.5 h-1.5 bg-blue-400 dark:bg-blue-300 rounded-full opacity-50 dark:opacity-35 animate-bounce delay-700"></div>
			<div class="absolute top-1/2 left-2/3 w-1 h-1 bg-cyan-400 dark:bg-cyan-300 rounded-full opacity-40 dark:opacity-30 animate-bounce delay-100"></div>
			<div class="absolute bottom-1/3 left-1/2 w-1.5 h-1.5 bg-violet-400 dark:bg-violet-300 rounded-full opacity-45 dark:opacity-35 animate-bounce delay-900"></div>
			<div class="absolute top-3/4 right-1/4 w-1 h-1 bg-indigo-400 dark:bg-indigo-300 rounded-full opacity-35 dark:opacity-25 animate-bounce delay-400"></div>
			<div class="absolute bottom-1/2 left-3/4 w-2 h-2 bg-purple-400 dark:bg-purple-300 rounded-full opacity-40 dark:opacity-30 animate-bounce delay-800"></div>
		</div>
	{/if}

	{#if !loading && mounted}
		<!-- Navbar with conditional glass effect -->
		<div class="navbar-container relative z-50 border-b border-violet-200 dark:border-violet-700 transition-all duration-300"
		     class:navbar-glass={isHomePage}
		     class:navbar-solid={!isHomePage}>
			<Navbar />
		</div>
		
		<!-- Main Content Area -->
		<main 
			class="flex-grow relative z-10 transition-all duration-500 ease-out"
			in:fade={{ duration: 600, delay: 100 }}
		>
			<slot />
		</main>
		
		<!-- Footer with conditional glass effect -->
		<div class="footer-container relative z-50 border-t border-violet-200 dark:border-violet-700 transition-all duration-300"
		     class:footer-glass={isHomePage}
		     class:footer-solid={!isHomePage}>
			<Footer />
		</div>
		
	{:else}
		<!-- Elegant Loading State -->
		<div class="flex items-center justify-center min-h-screen relative z-10">
			<div class="loading-card flex flex-col items-center space-y-4 p-8 rounded-2xl border border-violet-200 dark:border-violet-700 shadow-lg transition-all duration-300">
				<!-- Animated Loading Spinner -->
				<div class="relative">
					<div class="w-12 h-12 border-2 border-violet-200 dark:border-violet-700 rounded-full"></div>
					<div class="absolute top-0 left-0 w-12 h-12 border-2 border-violet-500 dark:border-violet-400 border-t-transparent rounded-full animate-spin"></div>
				</div>
				<!-- Loading Text -->
				<p class="text-sm font-medium text-slate-600 dark:text-slate-300 animate-pulse">Loading...</p>
			</div>
		</div>
	{/if}
	
	<!-- Toast Container -->
	<ToastContainer />
</div>

<style>
	/* Home Layout Styles */
	.home-layout {
		background: linear-gradient(180deg, 
			#ffffff 0%,
			#f8f5ff 20%,
			#f3f0ff 40%,
			#ede9fe 60%,
			#e8e3ff 80%,
			#ddd6fe 100%
		);
	}

	:global(.dark) .home-layout {
		background: linear-gradient(180deg, 
			#0f172a 0%,
			#1e293b 20%,
			#312e81 40%,
			#3730a3 60%,
			#4338ca 80%,
			#5b21b6 100%
		);
	}

	/* Default Layout Styles (for other pages) */
	.default-layout {
		background: #ffffff;
	}

	:global(.dark) .default-layout {
		background: #0f172a;
	}

	/* Glass Effect Components (only for home page) */
	.navbar-glass {
		background: rgba(255, 255, 255, 0.8);
		backdrop-filter: blur(12px);
		-webkit-backdrop-filter: blur(12px);
	}

	:global(.dark) .navbar-glass {
		background: rgba(15, 23, 42, 0.8);
	}

	.footer-glass {
		background: rgba(255, 255, 255, 0.85);
		backdrop-filter: blur(12px);
		-webkit-backdrop-filter: blur(12px);
	}

	:global(.dark) .footer-glass {
		background: rgba(15, 23, 42, 0.85);
	}

	/* Solid Components (for other pages) */
	.navbar-solid {
		background: #ffffff;
		border-bottom: 1px solid #e5e7eb;
	}

	:global(.dark) .navbar-solid {
		background: #0f172a;
		border-bottom-color: #374151;
	}

	.footer-solid {
		background: #f9fafb;
		border-top: 1px solid #e5e7eb;
	}

	:global(.dark) .footer-solid {
		background: #111827;
		border-top-color: #374151;
	}

	.loading-card {
		background: rgba(255, 255, 255, 0.9);
		backdrop-filter: blur(12px);
		-webkit-backdrop-filter: blur(12px);
	}

	:global(.dark) .loading-card {
		background: rgba(30, 41, 59, 0.9);
	}

	/* Global Glass Effect Classes (scoped to home page only) */
	.home-layout :global(.glass-card) {
		background: rgba(255, 255, 255, 0.8);
		backdrop-filter: blur(8px);
		-webkit-backdrop-filter: blur(8px);
		border: 1px solid rgba(139, 92, 246, 0.2);
		border-radius: 0.75rem;
		box-shadow: 0 10px 25px rgba(139, 92, 246, 0.1);
		transition: all 0.3s ease;
	}

	.home-layout :global(.dark .glass-card) {
		background: rgba(30, 41, 59, 0.8);
		border: 1px solid rgba(167, 139, 250, 0.3);
		box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
	}

	.home-layout :global(.glass-card:hover) {
		background: rgba(255, 255, 255, 0.9);
		border-color: rgba(139, 92, 246, 0.3);
		box-shadow: 0 20px 40px rgba(139, 92, 246, 0.15);
		transform: translateY(-2px);
	}

	.home-layout :global(.dark .glass-card:hover) {
		background: rgba(30, 41, 59, 0.9);
		border-color: rgba(167, 139, 250, 0.4);
		box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
	}

	/* Default Card Styles (for other pages) */
	.default-layout :global(.glass-card) {
		background: #ffffff;
		border: 1px solid #e5e7eb;
		border-radius: 0.75rem;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
		transition: all 0.3s ease;
	}

	.default-layout :global(.dark .glass-card) {
		background: #1f2937;
		border: 1px solid #374151;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
	}

	.default-layout :global(.glass-card:hover) {
		box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
		transform: translateY(-2px);
	}

	/* Enhanced Button Styles */
	:global(.btn-primary) {
		background: linear-gradient(135deg, #8b5cf6, #3b82f6);
		color: white;
		padding: 0.625rem 1.5rem;
		border-radius: 0.5rem;
		font-weight: 500;
		transition: all 0.2s ease;
		border: none;
		cursor: pointer;
		display: inline-flex;
		align-items: center;
		gap: 0.5rem;
	}

	:global(.btn-primary:hover) {
		background: linear-gradient(135deg, #7c3aed, #2563eb);
		transform: translateY(-1px) scale(1.02);
		box-shadow: 0 10px 25px rgba(139, 92, 246, 0.3);
	}

	:global(.btn-primary:focus) {
		outline: none;
		box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.3);
	}

	:global(.btn-secondary) {
		background: rgba(255, 255, 255, 0.8);
		color: #374151;
		padding: 0.625rem 1.5rem;
		border-radius: 0.5rem;
		font-weight: 500;
		border: 1px solid rgba(139, 92, 246, 0.3);
		transition: all 0.2s ease;
		cursor: pointer;
		display: inline-flex;
		align-items: center;
		gap: 0.5rem;
	}

	:global(.dark .btn-secondary) {
		background: rgba(71, 85, 105, 0.8);
		color: #e2e8f0;
		border-color: rgba(167, 139, 250, 0.4);
	}

	:global(.btn-secondary:hover) {
		background: rgba(255, 255, 255, 0.9);
		transform: translateY(-1px) scale(1.02);
		box-shadow: 0 4px 15px rgba(139, 92, 246, 0.2);
	}

	:global(.dark .btn-secondary:hover) {
		background: rgba(71, 85, 105, 0.9);
	}

	:global(.btn-secondary:focus) {
		outline: none;
		box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.3);
	}

	/* Enhanced Input Styles */
	:global(.input-glass) {
		background: rgba(255, 255, 255, 0.8);
		border: 1px solid rgba(139, 92, 246, 0.3);
		border-radius: 0.5rem;
		padding: 0.625rem 1rem;
		color: #1f2937;
		transition: all 0.2s ease;
	}

	:global(.dark .input-glass) {
		background: rgba(30, 41, 59, 0.8);
		color: white;
		border-color: rgba(167, 139, 250, 0.4);
	}

	:global(.input-glass::placeholder) {
		color: #6b7280;
	}

	:global(.dark .input-glass::placeholder) {
		color: #9ca3af;
	}

	:global(.input-glass:focus) {
		outline: none;
		border-color: #8b5cf6;
		box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.2);
		background: rgba(255, 255, 255, 0.9);
	}

	:global(.dark .input-glass:focus) {
		background: rgba(30, 41, 59, 0.9);
		border-color: #a78bfa;
	}

	/* Micro Interactions */
	:global(a) {
		transition: all 0.2s ease;
	}

	:global(a:hover) {
		transform: translateX(2px);
	}

	/* Interactive Elements */
	:global(.interactive) {
		transition: all 0.2s ease;
		cursor: pointer;
	}

	:global(.interactive:hover) {
		transform: translateY(-2px);
		box-shadow: 0 4px 15px rgba(139, 92, 246, 0.15);
	}

	/* Custom Scrollbar */
	:global(::-webkit-scrollbar) {
		width: 6px;
	}

	:global(::-webkit-scrollbar-track) {
		background: #f3f0ff;
	}

	:global(.dark ::-webkit-scrollbar-track) {
		background: #1e293b;
	}

	:global(::-webkit-scrollbar-thumb) {
		background: #a78bfa;
		border-radius: 3px;
	}

	:global(::-webkit-scrollbar-thumb:hover) {
		background: #8b5cf6;
	}

	/* Enhanced Focus States */
	:global(*:focus-visible) {
		outline: none;
		box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.3);
	}

	/* Text Selection */
	:global(::selection) {
		background: rgba(139, 92, 246, 0.2);
		color: #581c87;
	}

	:global(.dark ::selection) {
		background: rgba(167, 139, 250, 0.3);
		color: #e9d5ff;
	}

	/* Page Transition Effects */
	:global(.fade-in) {
		animation: fadeIn 0.6s ease-out forwards;
	}

	@keyframes fadeIn {
		from {
			opacity: 0;
			transform: translateY(20px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	/* Stagger Animation for Lists */
	:global(.stagger-item) {
		opacity: 0;
		animation: slideUp 0.6s ease-out forwards;
	}

	:global(.stagger-item:nth-child(1)) { animation-delay: 0.1s; }
	:global(.stagger-item:nth-child(2)) { animation-delay: 0.2s; }
	:global(.stagger-item:nth-child(3)) { animation-delay: 0.3s; }
	:global(.stagger-item:nth-child(4)) { animation-delay: 0.4s; }
	:global(.stagger-item:nth-child(5)) { animation-delay: 0.5s; }

	@keyframes slideUp {
		from {
			opacity: 0;
			transform: translateY(30px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	/* Smooth Scrolling */
	:global(html) {
		scroll-behavior: smooth;
	}

	/* Reduced Motion Support */
	@media (prefers-reduced-motion: reduce) {
		:global(*) {
			animation-duration: 0.01ms !important;
			animation-iteration-count: 1 !important;
			transition-duration: 0.01ms !important;
		}
		
		.animate-pulse,
		.animate-bounce,
		.animate-spin {
			animation: none !important;
		}
	}

	/* Performance Optimizations */
	.navbar-container,
	.footer-container,
	.loading-card {
		will-change: transform, opacity;
		transform: translateZ(0);
	}
</style>