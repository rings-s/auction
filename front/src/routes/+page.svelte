<script>
	import { onMount } from 'svelte';
	import { browser } from '$app/environment';
	import PWAInstallButton from '$lib/components/PWAInstallButton.svelte';

	// Real estate auction data
	let activeAuctions = [
		{ 
			id: 1, 
			title: "Luxury Downtown Penthouse", 
			location: "Manhattan, NY",
			currentBid: 2850000,
			timeLeft: "2h 45m",
			image: "🏢",
			type: "Luxury"
		},
		{ 
			id: 2, 
			title: "Modern Suburban Villa", 
			location: "Beverly Hills, CA",
			currentBid: 3200000,
			timeLeft: "5h 12m",
			image: "🏡",
			type: "Residential"
		},
		{ 
			id: 3, 
			title: "Commercial Office Building", 
			location: "Chicago, IL",
			currentBid: 4750000,
			timeLeft: "1d 3h",
			image: "🏬",
			type: "Commercial"
		}
	];

	let stats = [
		{ value: '$847M+', label: 'Properties Sold', icon: '📈' },
		{ value: '12,500+', label: 'Successful Auctions', icon: '🔨' },
		{ value: '98.7%', label: 'Client Satisfaction', icon: '⭐' },
		{ value: '45', label: 'Cities Worldwide', icon: '🌍' }
	];

	let currentAuctionIndex = 0;
	
	onMount(() => {
		if (browser) {
			// Rotate featured auctions
			const interval = setInterval(() => {
				currentAuctionIndex = (currentAuctionIndex + 1) % activeAuctions.length;
			}, 4000);
			
			return () => clearInterval(interval);
		}
	});

	function formatCurrency(amount) {
		return new Intl.NumberFormat('en-US', {
			style: 'currency',
			currency: 'USD',
			minimumFractionDigits: 0,
			maximumFractionDigits: 0
		}).format(amount);
	}
</script>

<svelte:head>
	<title>Premier Real Estate Auctions | Find Your Perfect Property</title>
	<meta name="description" content="Discover exclusive properties through transparent auctions. Join thousands of satisfied buyers in finding their dream properties.">
</svelte:head>

<PWAInstallButton />

<!-- Hero Section -->
<section class="relative min-h-screen bg-gradient-to-br from-neutral-50 via-white to-neutral-100 dark:from-neutral-950 dark:via-neutral-900 dark:to-neutral-800 overflow-hidden">
	<!-- Background Pattern -->
	<div class="absolute inset-0 opacity-5">
		<div class="absolute top-20 left-20 w-96 h-96 bg-primary-400 rounded-full mix-blend-multiply filter blur-xl animate-float-gentle"></div>
		<div class="absolute top-40 right-20 w-96 h-96 bg-secondary-400 rounded-full mix-blend-multiply filter blur-xl animate-float-gentle" style="animation-delay: 2s;"></div>
		<div class="absolute bottom-20 left-1/2 w-96 h-96 bg-accent-400 rounded-full mix-blend-multiply filter blur-xl animate-float-gentle" style="animation-delay: 4s;"></div>
	</div>

	<div class="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
		<div class="flex flex-col lg:flex-row items-center min-h-screen py-12 gap-12">
			
			<!-- Left Content -->
			<div class="flex-1 text-center lg:text-left z-10">
				<!-- Trust Badge -->
				<div class="inline-flex items-center gap-2 px-4 py-2 bg-success-50 dark:bg-success-900/20 border border-success-200 dark:border-success-800 rounded-full text-success-700 dark:text-success-300 text-sm font-medium mb-6">
					<div class="w-2 h-2 bg-success-500 rounded-full animate-pulse"></div>
					<span>Trusted by 50,000+ Property Investors</span>
				</div>

				<!-- Main Headline -->
				<h1 class="text-4xl sm:text-5xl lg:text-6xl xl:text-7xl font-bold leading-tight mb-6">
					<span class="text-neutral-900 dark:text-white">Discover</span>
					<span class="block gradient-text-primary">Premium Properties</span>
					<span class="text-neutral-600 dark:text-neutral-300 text-3xl sm:text-4xl lg:text-5xl xl:text-6xl">Through Live Auctions</span>
				</h1>

				<!-- Subheadline -->
				<p class="text-lg sm:text-xl text-neutral-600 dark:text-neutral-300 mb-8 max-w-2xl leading-relaxed">
					Join the world's most transparent real estate marketplace. Bid on verified properties, 
					connect with serious buyers, and secure your investment with confidence.
				</p>

				<!-- CTA Buttons -->
				<div class="flex flex-col sm:flex-row gap-4 mb-12">
					<button class="btn-modern-primary group">
						<span>Browse Live Auctions</span>
						<svg class="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"></path>
						</svg>
					</button>
					
					<button class="btn-modern-secondary group">
						<svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1.5a2.5 2.5 0 100-5H9v5z"></path>
						</svg>
						<span>How It Works</span>
					</button>
				</div>

				<!-- Stats Grid -->
				<div class="grid grid-cols-2 lg:grid-cols-4 gap-6">
					{#each stats as stat}
						<div class="text-center lg:text-left group">
							<div class="text-2xl mb-1">{stat.icon}</div>
							<div class="text-2xl sm:text-3xl font-bold text-neutral-900 dark:text-white mb-1 group-hover:gradient-text-primary transition-all">
								{stat.value}
							</div>
							<div class="text-sm text-neutral-600 dark:text-neutral-400">
								{stat.label}
							</div>
						</div>
					{/each}
				</div>
			</div>

			<!-- Right Content - Live Auction Card -->
			<div class="flex-1 relative z-10">
				<div class="relative max-w-lg mx-auto">
					<!-- Main Auction Card -->
					<div class="glass-modern rounded-3xl p-8 border border-white/20 dark:border-neutral-700/50 shadow-2xl">
						<!-- Live Indicator -->
						<div class="flex items-center justify-between mb-6">
							<div class="flex items-center gap-2">
								<div class="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
								<span class="text-sm font-semibold text-red-500 uppercase tracking-wide">Live Auction</span>
							</div>
							<span class="px-3 py-1 bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 text-xs font-medium rounded-full">
								{activeAuctions[currentAuctionIndex].type}
							</span>
						</div>

						<!-- Property Image Placeholder -->
						<div class="relative mb-6 group">
							<div class="w-full h-48 bg-gradient-to-br from-neutral-100 to-neutral-200 dark:from-neutral-800 dark:to-neutral-700 rounded-2xl flex items-center justify-center text-6xl group-hover:scale-105 transition-transform duration-300">
								{activeAuctions[currentAuctionIndex].image}
							</div>
							<div class="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent rounded-2xl"></div>
						</div>

						<!-- Property Info -->
						<div class="space-y-4">
							<div>
								<h3 class="text-xl font-bold text-neutral-900 dark:text-white mb-2">
									{activeAuctions[currentAuctionIndex].title}
								</h3>
								<p class="text-neutral-600 dark:text-neutral-300 flex items-center gap-1">
									<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
									</svg>
									{activeAuctions[currentAuctionIndex].location}
								</p>
							</div>

							<!-- Current Bid -->
							<div class="flex items-center justify-between p-4 bg-neutral-50 dark:bg-neutral-800/50 rounded-xl">
								<div>
									<p class="text-sm text-neutral-600 dark:text-neutral-400">Current Bid</p>
									<p class="text-2xl font-bold gradient-text-primary">
										{formatCurrency(activeAuctions[currentAuctionIndex].currentBid)}
									</p>
								</div>
								<div class="text-right">
									<p class="text-sm text-neutral-600 dark:text-neutral-400">Time Left</p>
									<p class="text-lg font-semibold text-orange-500">
										{activeAuctions[currentAuctionIndex].timeLeft}
									</p>
								</div>
							</div>

							<!-- Bid Button -->
							<button class="w-full bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 text-white py-4 rounded-xl font-semibold transition-all transform hover:scale-105 shadow-lg">
								Place Bid Now
							</button>
						</div>
					</div>

					<!-- Floating Elements -->
					<div class="absolute -top-4 -right-4 bg-accent-500 text-white px-4 py-2 rounded-full text-sm font-bold animate-pulse shadow-lg">
						🔥 Hot Bid
					</div>
					
					<div class="absolute -bottom-4 -left-4 bg-success-500 text-white px-4 py-2 rounded-full text-sm font-bold shadow-lg">
						✓ Verified
					</div>
				</div>

				<!-- Auction Indicators -->
				<div class="flex justify-center mt-6 gap-2">
					{#each activeAuctions as _, index}
						<button 
							class="w-3 h-3 rounded-full transition-all {index === currentAuctionIndex ? 'bg-primary-500' : 'bg-neutral-300 dark:bg-neutral-600'}"
							on:click={() => currentAuctionIndex = index}
						></button>
					{/each}
				</div>
			</div>
		</div>
	</div>

	<!-- Scroll Indicator -->
	<div class="absolute bottom-8 left-1/2 transform -translate-x-1/2 animate-bounce">
		<svg class="w-6 h-6 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
			<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3"></path>
		</svg>
	</div>
</section>