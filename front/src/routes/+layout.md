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
	let mounted = false;
	
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
  
  <!-- Viewport meta for responsiveness -->
  <svelte:head>
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<title>Real Estate Auction Platform</title>
  </svelte:head>
  
  <div class="min-h-screen flex flex-col relative overflow-hidden">
	<!-- Sophisticated Animated Background -->
	<div class="fixed inset-0 -z-10 animated-background">
	  <!-- Primary Gradient Background -->
	  <div class="absolute inset-0 bg-gradient-to-br from-neutral-100 via-primary-50/30 to-secondary-50/20 dark:from-neutral-800 dark:via-primary-100/10 dark:to-secondary-100/5 transition-colors duration-500"></div>
	  
	  <!-- Floating Geometric Elements -->
	  {#if mounted}
		<div class="absolute inset-0 overflow-hidden opacity-60">
		  <!-- Large floating circles -->
		  <div class="floating-shape floating-circle-1 absolute w-96 h-96 rounded-full bg-gradient-to-r from-primary-200/20 to-secondary-200/20 dark:from-primary-800/10 dark:to-secondary-800/10"></div>
		  <div class="floating-shape floating-circle-2 absolute w-64 h-64 rounded-full bg-gradient-to-r from-secondary-200/25 to-warning-200/20 dark:from-secondary-800/15 dark:to-warning-800/10"></div>
		  <div class="floating-shape floating-circle-3 absolute w-48 h-48 rounded-full bg-gradient-to-r from-warning-200/20 to-primary-200/25 dark:from-warning-800/10 dark:to-primary-800/15"></div>
		  
		  <!-- Floating squares -->
		  <div class="floating-shape floating-square-1 absolute w-32 h-32 bg-gradient-to-r from-primary-300/15 to-secondary-300/15 dark:from-primary-700/8 dark:to-secondary-700/8 rotate-45"></div>
		  <div class="floating-shape floating-square-2 absolute w-24 h-24 bg-gradient-to-r from-secondary-300/20 to-warning-300/15 dark:from-secondary-700/10 dark:to-warning-700/8 rotate-12"></div>
		  
		  <!-- Floating lines -->
		  <div class="floating-shape floating-line-1 absolute w-px h-64 bg-gradient-to-b from-transparent via-primary-400/30 to-transparent dark:via-primary-600/20"></div>
		  <div class="floating-shape floating-line-2 absolute w-px h-48 bg-gradient-to-b from-transparent via-secondary-400/25 to-transparent dark:via-secondary-600/15"></div>
		  <div class="floating-shape floating-line-3 absolute w-px h-32 bg-gradient-to-b from-transparent via-warning-400/20 to-transparent dark:via-warning-600/10"></div>
		  
		  <!-- Horizontal floating lines -->
		  <div class="floating-shape floating-h-line-1 absolute h-px w-64 bg-gradient-to-r from-transparent via-primary-400/25 to-transparent dark:via-primary-600/15"></div>
		  <div class="floating-shape floating-h-line-2 absolute h-px w-48 bg-gradient-to-r from-transparent via-secondary-400/20 to-transparent dark:via-secondary-600/12"></div>
		</div>
		
		<!-- Subtle dot pattern overlay -->
		<div class="absolute inset-0 opacity-[0.015] dark:opacity-[0.008]">
		  <svg class="w-full h-full" xmlns="http://www.w3.org/2000/svg">
			<defs>
			  <pattern id="dots" patternUnits="userSpaceOnUse" width="40" height="40">
				<circle cx="20" cy="20" r="1.5" fill="currentColor" class="text-neutral-600"/>
			  </pattern>
			</defs>
			<rect width="100%" height="100%" fill="url(#dots)" />
		  </svg>
		</div>
	  {/if}
	</div>
  
	<!-- Main Content -->
	<div class="relative z-10 min-h-screen flex flex-col backdrop-blur-[0.5px]">
	  {#if !loading}
		<Navbar />
		
		<main class="flex-grow">
		  <slot />
		</main>
		
		<Footer />
	  {:else}
		<!-- Enhanced Loading Screen -->
		<div class="flex items-center justify-center min-h-screen">
		  <div class="relative">
			<!-- Outer spinning ring -->
			<div class="absolute inset-0 rounded-full border-4 border-primary-200 dark:border-primary-800"></div>
			<!-- Inner spinning element -->
			<div class="animate-spin rounded-full h-16 w-16 border-4 border-transparent border-t-primary-500 border-r-secondary-500"></div>
			<!-- Center dot -->
			<div class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-2 h-2 bg-primary-500 rounded-full animate-pulse"></div>
		  </div>
		</div>
	  {/if}
	  
	  <ToastContainer />
	</div>
  </div>
  
  <style>
	/* Sophisticated floating animations with varied timing */
	.floating-shape {
	  will-change: transform;
	}
	
	/* Circular floating elements */
	.floating-circle-1 {
	  top: -10%;
	  right: -5%;
	  animation: floatSlow 25s ease-in-out infinite, rotateSlow 40s linear infinite;
	}
	
	.floating-circle-2 {
	  bottom: -8%;
	  left: -3%;
	  animation: floatMedium 20s ease-in-out infinite reverse, rotateMedium 35s linear infinite reverse;
	}
	
	.floating-circle-3 {
	  top: 20%;
	  left: -6%;
	  animation: floatFast 15s ease-in-out infinite, rotateFast 30s linear infinite;
	}
	
	/* Square floating elements */
	.floating-square-1 {
	  top: 60%;
	  right: -2%;
	  animation: floatMedium 18s ease-in-out infinite, rotateMedium 25s linear infinite reverse;
	}
	
	.floating-square-2 {
	  top: 10%;
	  right: 15%;
	  animation: floatFast 12s ease-in-out infinite reverse, rotateSlow 20s linear infinite;
	}
	
	/* Vertical line elements */
	.floating-line-1 {
	  top: 15%;
	  right: 8%;
	  animation: floatVertical 22s ease-in-out infinite, fadeInOut 8s ease-in-out infinite;
	}
	
	.floating-line-2 {
	  bottom: 25%;
	  left: 12%;
	  animation: floatVertical 18s ease-in-out infinite reverse, fadeInOut 6s ease-in-out infinite 2s;
	}
	
	.floating-line-3 {
	  top: 45%;
	  right: 25%;
	  animation: floatVertical 16s ease-in-out infinite, fadeInOut 7s ease-in-out infinite 4s;
	}
	
	/* Horizontal line elements */
	.floating-h-line-1 {
	  top: 30%;
	  left: 20%;
	  animation: floatHorizontal 20s ease-in-out infinite, fadeInOut 9s ease-in-out infinite 1s;
	}
	
	.floating-h-line-2 {
	  bottom: 40%;
	  right: 20%;
	  animation: floatHorizontal 24s ease-in-out infinite reverse, fadeInOut 11s ease-in-out infinite 3s;
	}
	
	/* Keyframe Animations */
	@keyframes floatSlow {
	  0%, 100% { transform: translateY(0) translateX(0) scale(1); }
	  25% { transform: translateY(-20px) translateX(10px) scale(1.05); }
	  50% { transform: translateY(-10px) translateX(-15px) scale(0.95); }
	  75% { transform: translateY(-30px) translateX(5px) scale(1.02); }
	}
	
	@keyframes floatMedium {
	  0%, 100% { transform: translateY(0) translateX(0) scale(1); }
	  33% { transform: translateY(-15px) translateX(-10px) scale(1.03); }
	  66% { transform: translateY(-25px) translateX(12px) scale(0.97); }
	}
	
	@keyframes floatFast {
	  0%, 100% { transform: translateY(0) translateX(0) scale(1); }
	  50% { transform: translateY(-20px) translateX(-8px) scale(1.08); }
	}
	
	@keyframes floatVertical {
	  0%, 100% { transform: translateY(0) scaleY(1); }
	  50% { transform: translateY(-15px) scaleY(1.1); }
	}
	
	@keyframes floatHorizontal {
	  0%, 100% { transform: translateX(0) scaleX(1); }
	  50% { transform: translateX(-12px) scaleX(1.05); }
	}
	
	@keyframes rotateSlow {
	  from { transform: rotate(0deg); }
	  to { transform: rotate(360deg); }
	}
	
	@keyframes rotateMedium {
	  from { transform: rotate(0deg); }
	  to { transform: rotate(360deg); }
	}
	
	@keyframes rotateFast {
	  from { transform: rotate(0deg); }
	  to { transform: rotate(360deg); }
	}
	
	@keyframes fadeInOut {
	  0%, 100% { opacity: 0.6; }
	  50% { opacity: 0.2; }
	}
	
	/* Smooth backdrop blur effect */
	.backdrop-blur-\[0\.5px\] {
	  backdrop-filter: blur(0.5px);
	}
	
	/* Performance optimizations */
	.animated-background {
	  will-change: auto;
	  transform: translateZ(0);
	}
	
	/* Responsive adjustments */
	@media (max-width: 768px) {
	  .floating-circle-1 { width: 16rem; height: 16rem; }
	  .floating-circle-2 { width: 12rem; height: 12rem; }
	  .floating-circle-3 { width: 8rem; height: 8rem; }
	  .floating-square-1 { width: 6rem; height: 6rem; }
	  .floating-square-2 { width: 4rem; height: 4rem; }
	}
	
	/* Reduced motion support */
	@media (prefers-reduced-motion: reduce) {
	  .floating-shape {
		animation: none !important;
	  }
	  
	  .animated-background {
		animation: none !important;
	  }
	  
	  .animate-spin {
		animation: none !important;
	  }
	  
	  .animate-pulse {
		animation: none !important;
	  }
	}
	
	/* Dark mode specific adjustments */
	@media (prefers-color-scheme: dark) {
	  .floating-shape {
		opacity: 0.7;
	  }
	}
	
	/* High contrast mode support */
	@media (prefers-contrast: high) {
	  .floating-shape {
		opacity: 0.1;
	  }
	}
	
	/* Focus management for accessibility */
	.animated-background {
	  pointer-events: none;
	}
	
	/* Ensure text remains readable over animated background */
	main {
	  position: relative;
	  z-index: 1;
	}
  </style>