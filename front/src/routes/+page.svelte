<script>
	import { onMount } from 'svelte';
	import { browser } from '$app/environment';
	import PWAInstallButton from '$lib/components/PWAInstallButton.svelte';

	// Sample data
	let stats = [
		{ value: '$2.5M+', label: 'Total Sales' },
		{ value: '98%', label: 'Success Rate' },
		{ value: '15K+', label: 'Active Users' },
		{ value: '4.9+', label: 'Rating' }
	];

	let pwaStatus = {
		serviceWorkerSupported: false,
		serviceWorkerRegistered: false,
		manifestFound: false,
		isStandalone: false,
		isHTTPS: false
	};

	// PWA Test function
	function testPWAStatus() {
		console.log('=== PWA Status Test ===');
		
		// Check service worker support
		pwaStatus.serviceWorkerSupported = 'serviceWorker' in navigator;
		console.log('Service Worker supported:', pwaStatus.serviceWorkerSupported);
		
		if (pwaStatus.serviceWorkerSupported) {
			// Check if SW is registered
			navigator.serviceWorker.getRegistrations().then(registrations => {
				pwaStatus.serviceWorkerRegistered = registrations.length > 0;
				console.log('SW Registrations:', registrations.length);
			});
		}

		// Check display mode
		pwaStatus.isStandalone = window.matchMedia('(display-mode: standalone)').matches;
		console.log('Display Mode Standalone:', pwaStatus.isStandalone);
		
		// Check manifest
		const manifestLink = document.querySelector('link[rel="manifest"]');
		pwaStatus.manifestFound = !!manifestLink;
		console.log('Manifest link found:', pwaStatus.manifestFound);
		if (manifestLink) {
			console.log('Manifest URL:', manifestLink.href);
		}

		// Check HTTPS
		pwaStatus.isHTTPS = location.protocol === 'https:' || location.hostname === 'localhost';
		console.log('HTTPS or localhost:', pwaStatus.isHTTPS);

		console.log('=== End PWA Test ===');
		
		// Force update to show status
		pwaStatus = { ...pwaStatus };
	}

	onMount(() => {
		if (browser) {
			// Auto-run test on mount
			setTimeout(testPWAStatus, 1000);
		}
	});
</script>

<svelte:head>
	<title>Premier Real Estate Auctions | Find Your Perfect Property</title>
	<meta name="description" content="Discover exclusive properties through transparent auctions. Join thousands of satisfied buyers in finding their dream properties.">
</svelte:head>

<!-- PWA Install Button Component -->
<PWAInstallButton />

<!-- Hero Section -->
<section class="relative bg-gradient-to-br from-blue-50 to-purple-50 dark:from-gray-900 dark:to-gray-800 min-h-screen flex items-center">
	<div class="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
		<div class="grid lg:grid-cols-2 gap-12 items-center">
			<!-- Hero Content -->
			<div class="text-center lg:text-left">
				<!-- PWA Test Buttons Section - Very Visible -->
				<div class="mb-8 p-4 bg-yellow-100 border-2 border-yellow-400 rounded-lg">
					<h3 class="text-lg font-bold text-yellow-800 mb-4">🔧 PWA Testing Panel</h3>
					
					<div class="space-y-3">
						<button 
							class="w-full bg-red-500 hover:bg-red-600 text-white px-4 py-3 rounded-lg font-medium transition-colors"
							on:click={testPWAStatus}
						>
							🔍 Test PWA Status (Check Console)
						</button>
						
						<button 
							class="w-full bg-green-500 hover:bg-green-600 text-white px-4 py-3 rounded-lg font-medium transition-colors"
							on:click={() => {
								// Manual trigger install
								if ('serviceWorker' in navigator) {
									alert('Manual Install:\n\n1. Look for install icon in address bar\n2. Or use Chrome menu > Install app\n3. Or use the floating install button');
								}
							}}
						>
							📱 Manual Install Instructions
						</button>
					</div>

					<!-- PWA Status Display -->
					<div class="mt-4 text-sm text-yellow-800 space-y-1">
						<div>🔧 Service Worker: {pwaStatus.serviceWorkerSupported ? '✅' : '❌'}</div>
						<div>📄 Manifest: {pwaStatus.manifestFound ? '✅' : '❌'}</div>
						<div>🔒 HTTPS/Localhost: {pwaStatus.isHTTPS ? '✅' : '❌'}</div>
						<div>📱 Standalone: {pwaStatus.isStandalone ? '✅' : '❌'}</div>
					</div>
				</div>

				<!-- Live badge -->
				<div class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400 mb-6">
					<span class="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></span>
					hero.badge.live
				</div>

				<!-- Main headline -->
				<h1 class="text-4xl md:text-6xl font-bold text-gray-900 dark:text-white mb-6">
					<span class="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
						hero.headline
					</span>
				</h1>

				<!-- Subheadline -->
				<p class="text-xl text-gray-600 dark:text-gray-300 mb-8 max-w-2xl">
					hero.subheadline
				</p>

				<!-- CTA Buttons -->
				<div class="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
					<button class="bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 rounded-xl font-semibold transition-colors">
						hero.cta.primary
					</button>
					<button class="bg-white hover:bg-gray-50 text-blue-600 border-2 border-blue-600 px-8 py-4 rounded-xl font-semibold transition-colors">
						hero.cta.secondary
					</button>
				</div>

				<!-- Stats -->
				<div class="grid grid-cols-2 lg:grid-cols-4 gap-6 mt-12">
					{#each stats as stat}
						<div class="text-center lg:text-left">
							<div class="text-2xl md:text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-1">
								{stat.value}
							</div>
							<div class="text-sm text-gray-600 dark:text-gray-400">
								{stat.label}
							</div>
						</div>
					{/each}
				</div>
			</div>

			<!-- Hero Illustration -->
			<div class="relative">
				<div class="bg-white/10 backdrop-blur-sm rounded-3xl p-8 border border-white/20">
					<!-- Building illustration placeholder -->
					<div class="w-full h-96 bg-gradient-to-br from-blue-100 to-purple-100 dark:from-blue-900/50 dark:to-purple-900/50 rounded-2xl flex items-center justify-center">
						<div class="text-center">
							<!-- Building SVG -->
							<svg class="w-32 h-32 mx-auto mb-4 text-blue-400" fill="currentColor" viewBox="0 0 100 100">
								<rect x="20" y="30" width="60" height="60" rx="4"/>
								<rect x="30" y="40" width="8" height="8" fill="white" opacity="0.7"/>
								<rect x="42" y="40" width="8" height="8" fill="white" opacity="0.7"/>
								<rect x="54" y="40" width="8" height="8" fill="white" opacity="0.7"/>
								<rect x="30" y="52" width="8" height="8" fill="white" opacity="0.7"/>
								<rect x="42" y="52" width="8" height="8" fill="white" opacity="0.7"/>
								<rect x="54" y="52" width="8" height="8" fill="white" opacity="0.7"/>
								<rect x="30" y="64" width="8" height="8" fill="white" opacity="0.7"/>
								<rect x="42" y="64" width="8" height="8" fill="white" opacity="0.7"/>
								<rect x="54" y="64" width="8" height="8" fill="white" opacity="0.7"/>
							</svg>
							<div class="space-y-2">
								<div class="bg-blue-500 text-white px-3 py-1 rounded-full text-sm font-medium">
									$400K
								</div>
								<div class="bg-purple-500 text-white px-3 py-1 rounded-full text-sm font-medium">
									$500K
								</div>
							</div>
						</div>
					</div>
				</div>

				<!-- Floating badges -->
				<div class="absolute -top-4 -right-4 bg-purple-500 text-white px-3 py-1 rounded-full text-sm font-medium animate-pulse">
					$400K
				</div>
				<div class="absolute top-1/2 -left-4 bg-blue-500 text-white px-3 py-1 rounded-full text-sm font-medium">
					$500K
				</div>
			</div>
		</div>
	</div>
</section>

<!-- PWA Install Section -->
<section class="py-16 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-gray-800 dark:to-gray-900">
	<div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
		<h2 class="text-3xl font-bold text-gray-900 dark:text-white mb-4">
			Install Our App for Better Experience
		</h2>
		<p class="text-lg text-gray-600 dark:text-gray-300 mb-8">
			Get instant notifications, offline access, and a native app experience
		</p>
		
		<!-- Another install button here -->
		<div class="flex justify-center mb-8">
			<button 
				class="bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 rounded-xl font-semibold transition-colors flex items-center"
				on:click={() => {
					alert('Install Options:\n\n1. Look for install icon in Chrome address bar\n2. Use Chrome menu > Install app\n3. Use floating install button (top-right)\n4. Add to Home Screen on mobile');
				}}
			>
				<svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v12m0-12l-4 4m4-4l4 4m-8 6h8"></path>
				</svg>
				📱 Install App Now
			</button>
		</div>

		<!-- PWA Features -->
		<div class="grid sm:grid-cols-3 gap-6">
			<div class="flex flex-col items-center">
				<div class="w-12 h-12 bg-blue-100 dark:bg-blue-900/50 rounded-lg flex items-center justify-center mb-3">
					<svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z"></path>
					</svg>
				</div>
				<h3 class="font-semibold text-gray-900 dark:text-white">Mobile Optimized</h3>
				<p class="text-sm text-gray-600 dark:text-gray-400">Perfect mobile experience</p>
			</div>

			<div class="flex flex-col items-center">
				<div class="w-12 h-12 bg-blue-100 dark:bg-blue-900/50 rounded-lg flex items-center justify-center mb-3">
					<svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"></path>
					</svg>
				</div>
				<h3 class="font-semibold text-gray-900 dark:text-white">Works Offline</h3>
				<p class="text-sm text-gray-600 dark:text-gray-400">Access even without internet</p>
			</div>

			<div class="flex flex-col items-center">
				<div class="w-12 h-12 bg-blue-100 dark:bg-blue-900/50 rounded-lg flex items-center justify-center mb-3">
					<svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-5 5-5-5h5V8h5v9z"></path>
					</svg>
				</div>
				<h3 class="font-semibold text-gray-900 dark:text-white">Push Notifications</h3>
				<p class="text-sm text-gray-600 dark:text-gray-400">Never miss an auction</p>
			</div>
		</div>
	</div>
</section>