<script>
	import { onMount } from 'svelte';
	import { browser } from '$app/environment';
	import { locale, t } from '$lib/i18n';
	import { fly, fade, scale } from 'svelte/transition';
	import { quintOut, elasticOut } from 'svelte/easing';
  
	// Reactive translations
	$: badge = t('hero.badge');
	$: titleLine1 = t('hero.title.line1');
	$: titleLine2 = t('hero.title.line2');
	$: titleLine3 = t('hero.title.line3');
	$: subtitle = t('hero.subtitle');
	$: ctaPrimary = t('hero.cta.primary');
	$: ctaSecondary = t('hero.cta.secondary');
	$: stats = t('hero.stats');
	$: liveAuctionBadge = t('hero.liveAuction.badge');
	$: currentBidLabel = t('hero.liveAuction.currentBid');
	$: timeLeftLabel = t('hero.liveAuction.timeLeft');
	$: placeBidLabel = t('hero.liveAuction.placeBid');
	$: verifiedLabel = t('hero.liveAuction.verified');
	$: hotBidLabel = t('hero.liveAuction.hotBid');
	$: biddersLabel = t('hero.liveAuction.bidders');
	$: watchingLabel = t('hero.liveAuction.watching');
  
	$: isRTL = $locale === 'ar';
  
	// Enhanced auction data
	let activeAuctions = [
	  { 
		id: 1, 
		title: "Luxury Downtown Penthouse", 
		titleAr: "بنتهاوس فاخر في وسط المدينة",
		location: "Manhattan, NY",
		locationAr: "مانهاتن، نيويورك",
		currentBid: 2850000,
		timeLeft: "2h 45m",
		timeLeftAr: "2س 45د",
		image: "/images/luxury-penthouse.jpg",
		type: "Luxury",
		typeAr: "فاخر",
		bidders: 12,
		watchers: 45,
		increment: 50000,
		featured: true
	  },
	  { 
		id: 2, 
		title: "Modern Suburban Villa", 
		titleAr: "فيلا حديثة في الضواحي",
		location: "Beverly Hills, CA",
		locationAr: "بيفرلي هيلز، كاليفورنيا",
		currentBid: 3200000,
		timeLeft: "5h 12m",
		timeLeftAr: "5س 12د",
		image: "/images/modern-villa.jpg",
		type: "Residential",
		typeAr: "سكني",
		bidders: 18,
		watchers: 67,
		increment: 75000,
		featured: false
	  },
	  { 
		id: 3, 
		title: "Commercial Office Building", 
		titleAr: "مبنى مكاتب تجاري",
		location: "Chicago, IL",
		locationAr: "شيكاغو، إلينوي",
		currentBid: 4750000,
		timeLeft: "1d 3h",
		timeLeftAr: "1ي 3س",
		image: "/images/office-building.jpg",
		type: "Commercial",
		typeAr: "تجاري",
		bidders: 8,
		watchers: 34,
		increment: 100000,
		featured: false
	  }
	];
  
	let currentAuctionIndex = 0;
	let mounted = false;
	let mouseX = 0;
	let mouseY = 0;
	
	onMount(() => {
	  mounted = true;
	  
	  // Auto-rotate auctions
	  const interval = setInterval(() => {
		currentAuctionIndex = (currentAuctionIndex + 1) % activeAuctions.length;
	  }, 6000);
	  
	  // Mouse tracking for parallax
	  const handleMouseMove = (e) => {
		if (browser && window.innerWidth > 1024) {
		  mouseX = (e.clientX - window.innerWidth / 2) / 50;
		  mouseY = (e.clientY - window.innerHeight / 2) / 50;
		}
	  };
	  
	  window.addEventListener('mousemove', handleMouseMove);
	  
	  return () => {
		clearInterval(interval);
		window.removeEventListener('mousemove', handleMouseMove);
	  };
	});
  
	function formatCurrency(amount) {
	  return new Intl.NumberFormat(isRTL ? 'ar-SA' : 'en-US', {
		style: 'currency',
		currency: 'USD',
		minimumFractionDigits: 0,
		maximumFractionDigits: 0
	  }).format(amount);
	}
  
	function handleBidClick() {
	  // Navigate to auction detail or open bid modal
	  console.log('Bid clicked for:', activeAuctions[currentAuctionIndex]);
	}
  </script>
  
  <svelte:head>
	<title>{isRTL ? 'مزادات العقارات المميزة | اعثر على عقارك المثالي' : 'Premier Real Estate Auctions | Find Your Perfect Property'}</title>
	<meta name="description" content="{isRTL ? 'اكتشف العقارات الحصرية من خلال المزادات الشفافة.' : 'Discover exclusive properties through transparent auctions.'}">
  </svelte:head>
  
  <!-- Hero Section -->
  <section class="relative min-h-screen overflow-hidden bg-gradient-to-br from-neutral-50 via-white to-purple-50/30 dark:from-neutral-900 dark:via-neutral-900 dark:to-purple-950/20">
	
	{#if mounted}
	  <!-- Dynamic Background -->
	  <div class="absolute inset-0">
		<!-- Animated Gradient Orbs -->
		<div 
		  class="absolute top-[20%] {isRTL ? 'right-[10%]' : 'left-[10%]'} w-[500px] h-[500px] rounded-full opacity-20"
		  style="background: radial-gradient(circle, rgba(167, 139, 250, 0.4) 0%, transparent 70%); transform: translate({mouseX}px, {mouseY}px); filter: blur(40px);"
		></div>
		<div 
		  class="absolute bottom-[20%] {isRTL ? 'left-[10%]' : 'right-[10%]'} w-[400px] h-[400px] rounded-full opacity-20"
		  style="background: radial-gradient(circle, rgba(59, 130, 246, 0.4) 0%, transparent 70%); transform: translate({-mouseX}px, {-mouseY}px); filter: blur(40px);"
		></div>
		
		<!-- Geometric Pattern -->
		<div class="absolute inset-0 opacity-[0.02]">
		  <svg class="w-full h-full" xmlns="http://www.w3.org/2000/svg">
			<defs>
			  <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
				<circle cx="20" cy="20" r="1" fill="currentColor" class="text-neutral-900 dark:text-neutral-100" />
			  </pattern>
			</defs>
			<rect width="100%" height="100%" fill="url(#grid)" />
		  </svg>
		</div>
	  </div>
  
	  <div class="relative z-10 max-w-[1400px] mx-auto px-4 sm:px-6 lg:px-8">
		<div class="flex flex-col lg:flex-row items-center justify-between min-h-screen py-20 gap-12 lg:gap-16">
		  
		  <!-- Left Content -->
		  <div class="flex-1 max-w-2xl text-center lg:text-{isRTL ? 'right' : 'left'}">
			<!-- Trust Badge -->
			<div 
			  in:fly={{ y: 20, duration: 600, delay: 100 }}
			  class="inline-flex items-center gap-2 px-4 py-2 mb-8 bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-800 rounded-full"
			>
			  <div class="relative flex items-center justify-center">
				<div class="w-2 h-2 bg-emerald-500 rounded-full"></div>
				<div class="absolute w-2 h-2 bg-emerald-500 rounded-full animate-ping"></div>
			  </div>
			  <span class="text-sm font-semibold text-emerald-700 dark:text-emerald-300">
				{$badge}
			  </span>
			</div>
  
			<!-- Title with Advanced Typography -->
			<div class="space-y-2 mb-8">
			  <h1 
				in:fly={{ y: 30, duration: 700, delay: 200, easing: quintOut }}
				class="text-5xl sm:text-6xl lg:text-7xl font-black text-neutral-900 dark:text-white"
			  >
				{$titleLine1}
			  </h1>
			  <h1 
				in:fly={{ y: 30, duration: 700, delay: 350, easing: quintOut }}
				class="text-5xl sm:text-6xl lg:text-7xl font-black"
			  >
				<span class="bg-gradient-to-r from-purple-600 via-blue-600 to-purple-600 bg-clip-text text-transparent bg-[length:200%_auto] animate-gradient-shift">
				  {$titleLine2}
				</span>
			  </h1>
			  <h2 
				in:fly={{ y: 30, duration: 700, delay: 500, easing: quintOut }}
				class="text-3xl sm:text-4xl lg:text-5xl font-bold text-neutral-700 dark:text-neutral-300"
			  >
				{$titleLine3}
			  </h2>
			</div>
  
			<!-- Subtitle -->
			<p 
			  in:fly={{ y: 20, duration: 700, delay: 650 }}
			  class="text-lg sm:text-xl text-neutral-600 dark:text-neutral-400 mb-10 leading-relaxed max-w-xl mx-auto lg:mx-0"
			>
			  {$subtitle}
			</p>
  
			<!-- CTA Buttons -->
			<div 
			  in:fly={{ y: 20, duration: 700, delay: 800 }}
			  class="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start mb-16"
			>
			  <button class="group relative px-8 py-4 overflow-hidden rounded-2xl bg-gradient-to-r from-purple-600 to-blue-600 text-white font-semibold shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300">
				<span class="relative z-10 flex items-center justify-center gap-2">
				  {$ctaPrimary}
				  <svg class="w-5 h-5 transform group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
				  </svg>
				</span>
				<div class="absolute inset-0 bg-gradient-to-r from-purple-700 to-blue-700 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
			  </button>
			  
			  <button class="group px-8 py-4 rounded-2xl bg-white dark:bg-neutral-800 text-neutral-900 dark:text-white font-semibold border-2 border-neutral-200 dark:border-neutral-700 shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300">
				<span class="flex items-center justify-center gap-2">
				  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
				  </svg>
				  {$ctaSecondary}
				</span>
			  </button>
			</div>
  
			<!-- Stats Grid -->
			<div 
			  in:fly={{ y: 20, duration: 700, delay: 950 }}
			  class="grid grid-cols-2 lg:grid-cols-4 gap-4"
			>
			  {#each $stats as stat, i}
				<div 
				  in:scale={{ duration: 500, delay: 1000 + i * 100, easing: elasticOut }}
				  class="group p-4 lg:p-6 rounded-2xl bg-white/70 dark:bg-neutral-800/70 backdrop-blur-sm border border-neutral-200/50 dark:border-neutral-700/50 hover:border-purple-300 dark:hover:border-purple-700 transition-all duration-300 cursor-pointer"
				>
				  <div class="text-2xl mb-2">{stat.icon}</div>
				  <div class="text-2xl lg:text-3xl font-black text-neutral-900 dark:text-white group-hover:text-purple-600 dark:group-hover:text-purple-400 transition-colors">
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
		  <div class="flex-1 max-w-lg relative">
			<div 
			  in:scale={{ duration: 800, delay: 300, easing: quintOut }}
			  class="relative"
			  style="transform: perspective(1000px) rotateY({-mouseX/2}deg) rotateX({mouseY/2}deg)"
			>
			  <!-- Floating Elements -->
			  <div class="absolute -top-4 -right-4 z-20">
				<div class="px-4 py-2 bg-gradient-to-r from-orange-500 to-red-500 text-white rounded-full text-sm font-bold shadow-lg animate-pulse">
				  🔥 {$hotBidLabel}
				</div>
			  </div>
			  
			  <div class="absolute -bottom-4 -left-4 z-20">
				<div class="px-4 py-2 bg-emerald-500 text-white rounded-full text-sm font-bold shadow-lg flex items-center gap-2">
				  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
				  </svg>
				  {$verifiedLabel}
				</div>
			  </div>
  
			  <!-- Main Card -->
			  <div class="relative bg-white/95 dark:bg-neutral-800/95 backdrop-blur-xl rounded-3xl shadow-2xl overflow-hidden border border-neutral-200/50 dark:border-neutral-700/50">
				<!-- Live Indicator -->
				<div class="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-red-500 via-orange-500 to-red-500 animate-gradient-shift"></div>
				
				<!-- Card Content -->
				<div class="p-6 lg:p-8">
				  <!-- Header -->
				  <div class="flex items-center justify-between mb-6">
					<div class="flex items-center gap-2">
					  <div class="relative">
						<div class="w-3 h-3 bg-red-500 rounded-full"></div>
						<div class="absolute inset-0 w-3 h-3 bg-red-500 rounded-full animate-ping"></div>
					  </div>
					  <span class="text-sm font-bold text-red-500 uppercase tracking-wider">
						{$liveAuctionBadge}
					  </span>
					</div>
					<span class="px-3 py-1 bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 text-xs font-semibold rounded-full">
					  {isRTL ? activeAuctions[currentAuctionIndex].typeAr : activeAuctions[currentAuctionIndex].type}
					</span>
				  </div>
  
				  <!-- Property Image -->
				  <div class="relative mb-6 rounded-2xl overflow-hidden bg-neutral-100 dark:bg-neutral-700 h-64">
					<div class="absolute inset-0 flex items-center justify-center text-6xl">
					  {currentAuctionIndex === 0 ? '🏢' : currentAuctionIndex === 1 ? '🏡' : '🏬'}
					</div>
					<div class="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent"></div>
					
					<!-- Stats Overlay -->
					<div class="absolute bottom-4 left-4 right-4 flex items-center justify-between text-white">
					  <div class="flex items-center gap-4">
						<div class="flex items-center gap-1">
						  <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
							<path d="M9 6a3 3 0 11-6 0 3 3 0 016 0zM17 6a3 3 0 11-6 0 3 3 0 016 0zM12.93 17c.046-.327.07-.66.07-1a6.97 6.97 0 00-1.5-4.33A5 5 0 0119 16v1h-6.07zM6 11a5 5 0 015 5v1H1v-1a5 5 0 015-5z" />
						  </svg>
						  <span class="text-sm font-medium">{activeAuctions[currentAuctionIndex].bidders} {$biddersLabel}</span>
						</div>
						<div class="flex items-center gap-1">
						  <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
							<path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
							<path fill-rule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clip-rule="evenodd" />
						  </svg>
						  <span class="text-sm font-medium">{activeAuctions[currentAuctionIndex].watchers} {$watchingLabel}</span>
						</div>
					  </div>
					</div>
				  </div>
  
				  <!-- Property Details -->
				  <div class="space-y-4">
					<div>
					  <h3 class="text-xl font-bold text-neutral-900 dark:text-white mb-2">
						{isRTL ? activeAuctions[currentAuctionIndex].titleAr : activeAuctions[currentAuctionIndex].title}
					  </h3>
					  <p class="text-neutral-600 dark:text-neutral-400 flex items-center gap-1">
						<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
						  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
						</svg>
						{isRTL ? activeAuctions[currentAuctionIndex].locationAr : activeAuctions[currentAuctionIndex].location}
					  </p>
					</div>
  
					<!-- Bid Info -->
					<div class="p-4 bg-neutral-50 dark:bg-neutral-900/50 rounded-2xl">
					  <div class="flex items-center justify-between mb-3">
						<div>
						  <p class="text-sm text-neutral-600 dark:text-neutral-400 mb-1">{$currentBidLabel}</p>
						  <p class="text-2xl font-black text-purple-600 dark:text-purple-400">
							{formatCurrency(activeAuctions[currentAuctionIndex].currentBid)}
						  </p>
						</div>
						<div class="text-right">
						  <p class="text-sm text-neutral-600 dark:text-neutral-400 mb-1">{$timeLeftLabel}</p>
						  <p class="text-xl font-bold text-orange-500">
							{isRTL ? activeAuctions[currentAuctionIndex].timeLeftAr : activeAuctions[currentAuctionIndex].timeLeft}
						  </p>
						</div>
					  </div>
					  
					  <!-- Progress Bar -->
					  <div class="w-full h-2 bg-neutral-200 dark:bg-neutral-700 rounded-full overflow-hidden">
						<div class="h-full bg-gradient-to-r from-purple-500 to-blue-500 rounded-full animate-pulse" style="width: 65%"></div>
					  </div>
					</div>
  
					<!-- Place Bid Button -->
					<button 
					  on:click={handleBidClick}
					  class="w-full py-4 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white rounded-2xl font-bold text-lg shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300"
					>
					  {$placeBidLabel}
					</button>
				  </div>
				</div>
			  </div>
  
			  <!-- Pagination Dots -->
			  <!-- Pagination Dots -->
			  <div class="flex justify-center mt-6 gap-2">
				{#each activeAuctions as _, index}
				  <button 
					class="w-2 h-2 rounded-full transition-all duration-300 {index === currentAuctionIndex ? 'w-8 bg-purple-600 dark:bg-purple-400' : 'bg-neutral-300 dark:bg-neutral-600 hover:bg-neutral-400 dark:hover:bg-neutral-500'}"
					on:click={() => currentAuctionIndex = index}
					aria-label="Go to auction {index + 1}"
				  ></button>
				{/each}
			  </div>
			</div>
		  </div>
		</div>
	  </div>
   
	  <!-- Scroll Indicator -->
	  <div class="absolute bottom-8 left-1/2 transform -translate-x-1/2 animate-bounce">
		<svg class="w-6 h-6 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
		  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3" />
		</svg>
	  </div>
	{/if}
   </section>
   
   <style>
	/* Gradient animation */
	@keyframes gradient-shift {
	  0%, 100% { background-position: 0% 50%; }
	  50% { background-position: 100% 50%; }
	}
	
	.animate-gradient-shift {
	  animation: gradient-shift 4s ease infinite;
	}
	
	/* Float animation */
	@keyframes float-gentle {
	  0%, 100% { transform: translateY(0px) rotate(0deg); }
	  33% { transform: translateY(-10px) rotate(1deg); }
	  66% { transform: translateY(-5px) rotate(-1deg); }
	}
	
	.animate-float-gentle {
	  animation: float-gentle 6s ease-in-out infinite;
	}
	
	/* Respect reduced motion */
	@media (prefers-reduced-motion: reduce) {
	  .animate-gradient-shift,
	  .animate-float-gentle,
	  .animate-bounce,
	  .animate-pulse,
	  .animate-ping {
		animation: none;
	  }
	}
   </style>