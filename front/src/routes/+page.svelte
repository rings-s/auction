<script>
	import { onMount } from 'svelte';
	import { fade, fly, scale } from 'svelte/transition';
	import { locale } from '$lib/i18n/config.js';
	
	let mounted = false;
	let scrollY = 0;
	let prefersReducedMotion = false;
	
	// RTL support
	$: isRTL = $locale === 'ar';
	
	// Content structure - same pattern as about page
	const content = {
	  en: {
		hero: {
		  badge: "Trusted by 50,000+ Property Investors",
		  title: {
			line1: "Discover",
			line2: "Premium Properties",
			line3: "Through Live Auctions"
		  },
		  subtitle: "Join the world's most transparent real estate marketplace. Bid on verified properties, connect with serious buyers, and secure your investment with confidence.",
		  cta: {
			primary: "Browse Live Auctions",
			secondary: "How It Works"
		  },
		  stats: [
			{ value: "$847M+", label: "Properties Sold" },
			{ value: "12,500+", label: "Successful Auctions" },
			{ value: "98.7%", label: "Client Satisfaction" },
			{ value: "45", label: "Cities Worldwide" }
		  ],
		  features: {
			live: "Live Bidding",
			secure: "Secure Transactions",
			verified: "Verified Properties"
		  }
		}
	  },
	  ar: {
		hero: {
		  badge: "موثوق من أكثر من 50,000 مستثمر عقاري",
		  title: {
			line1: "اكتشف",
			line2: "العقارات المميزة",
			line3: "من خلال المزادات المباشرة"
		  },
		  subtitle: "انضم إلى أكثر أسواق العقارات شفافة في العالم. قدم عروضك على العقارات المعتمدة، وتواصل مع المشترين الجادين، واحصل على استثمارك بثقة.",
		  cta: {
			primary: "تصفح المزادات المباشرة",
			secondary: "كيف يعمل"
		  },
		  stats: [
			{ value: "+847 مليون$", label: "عقارات مباعة" },
			{ value: "+12,500", label: "مزادات ناجحة" },
			{ value: "98.7%", label: "رضا العملاء" },
			{ value: "45", label: "مدينة حول العالم" }
		  ],
		  features: {
			live: "مزايدة مباشرة",
			secure: "معاملات آمنة",
			verified: "عقارات موثقة"
		  }
		}
	  }
	};
	
	function getText(path) {
	  const lang = $locale || 'en';
	  const keys = path.split('.');
	  let value = content[lang] || content.en;
	  
	  for (const key of keys) {
		value = value?.[key];
		if (!value) return path;
	  }
	  return value;
	}
	
	onMount(() => {
	  mounted = true;
	  
	  if (typeof window !== 'undefined') {
		const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
		prefersReducedMotion = mediaQuery.matches;
		
		mediaQuery.addEventListener('change', (e) => {
		  prefersReducedMotion = e.matches;
		});
	  }
	});
  </script>
  
  <svelte:head>
	<title>{isRTL ? 'مزادات العقارات المميزة | اعثر على عقارك المثالي' : 'Premier Real Estate Auctions | Find Your Perfect Property'}</title>
	<meta name="description" content="{isRTL ? 'اكتشف العقارات الحصرية من خلال المزادات الشفافة.' : 'Discover exclusive properties through transparent auctions.'}">
  </svelte:head>
  
  <svelte:window bind:scrollY />
  
  <div class="relative overflow-hidden bg-gradient-to-b from-white via-primary-50/20 to-white dark:from-gray-900 dark:via-primary-950/20 dark:to-gray-900" dir={isRTL ? 'rtl' : 'ltr'}>
	
	{#if mounted}
	  <!-- Hero Section with Advanced SVG Animation -->
	  <section class="relative min-h-screen flex items-center py-20 sm:py-24 lg:py-32">
		<!-- Animated Background Gradient -->
		<div class="absolute inset-0 pointer-events-none overflow-hidden">
		  <div 
			class="absolute top-0 left-0 w-[800px] h-[800px] rounded-full opacity-20"
			style="background: radial-gradient(circle at center, var(--color-primary-400), transparent 70%);
				   transform: translate(-30%, -30%) scale({1 + scrollY * 0.0003});
				   filter: blur(60px);"
		  ></div>
		  <div 
			class="absolute bottom-0 right-0 w-[600px] h-[600px] rounded-full opacity-20"
			style="background: radial-gradient(circle at center, var(--color-secondary-400), transparent 70%);
				   transform: translate(30%, 30%) scale({1 + scrollY * 0.0003});
				   filter: blur(60px);"
		  ></div>
		  <div 
			class="absolute top-1/2 left-1/2 w-[700px] h-[700px] rounded-full opacity-15"
			style="background: radial-gradient(circle at center, var(--color-accent-400), transparent 70%);
				   transform: translate(-50%, -50%) rotate({scrollY * 0.05}deg);
				   filter: blur(80px);"
		  ></div>
		</div>
		
		<div class="relative z-10 w-full max-w-7xl mx-auto px-6 sm:px-8 lg:px-12">
		  <div class="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16 items-center">
			
			<!-- Left Content -->
			<div class="lg:col-span-6 space-y-8">
			  <!-- Trust Badge -->
			  <div
				in:fly={{ y: prefersReducedMotion ? 0 : 20, duration: 600, delay: 200 }}
				class="inline-flex items-center gap-3 px-5 py-3 bg-gradient-to-r from-success-50 to-success-100 dark:from-success-900/20 dark:to-success-800/20 border border-success-200 dark:border-success-700 rounded-full shadow-sm"
			  >
				<div class="relative">
				  <div class="w-2 h-2 bg-success-500 rounded-full"></div>
				  <div class="absolute inset-0 w-2 h-2 bg-success-500 rounded-full animate-ping"></div>
				</div>
				<span class="text-sm font-semibold text-success-700 dark:text-success-300">
				  {getText('hero.badge')}
				</span>
			  </div>
			  
			  <!-- Main Title -->
			  <div class="space-y-2">
				<h1
				  in:fly={{ y: prefersReducedMotion ? 0 : 30, duration: 800, delay: 300 }}
				  class="text-5xl sm:text-6xl lg:text-7xl font-black leading-[0.95] tracking-tight"
				>
				  <span class="text-gray-900 dark:text-white">
					{getText('hero.title.line1')}
				  </span>
				</h1>
				<h1
				  in:fly={{ y: prefersReducedMotion ? 0 : 30, duration: 800, delay: 400 }}
				  class="text-5xl sm:text-6xl lg:text-7xl font-black leading-[0.95] tracking-tight"
				>
				  <span class="gradient-text-primary">
					{getText('hero.title.line2')}
				  </span>
				</h1>
				<h1
				  in:fly={{ y: prefersReducedMotion ? 0 : 30, duration: 800, delay: 500 }}
				  class="text-3xl sm:text-4xl lg:text-5xl font-bold leading-tight text-gray-700 dark:text-gray-300"
				>
				  {getText('hero.title.line3')}
				</h1>
			  </div>
			  
			  <!-- Subtitle -->
			  <p
				in:fly={{ y: prefersReducedMotion ? 0 : 20, duration: 800, delay: 600 }}
				class="text-lg leading-relaxed text-gray-600 dark:text-gray-300 max-w-xl"
			  >
				{getText('hero.subtitle')}
			  </p>
			  
			  <!-- CTA Buttons -->
			  <div
				in:fly={{ y: prefersReducedMotion ? 0 : 20, duration: 800, delay: 700 }}
				class="flex flex-col sm:flex-row gap-4"
			  >
				<button class="btn-modern-primary group">
				  <span class="flex items-center justify-center gap-2">
					{getText('hero.cta.primary')}
					<svg class="w-5 h-5 transform group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"></path>
					</svg>
				  </span>
				</button>
				
				<button class="btn-modern-secondary group">
				  <span class="flex items-center justify-center gap-2">
					<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
					</svg>
					{getText('hero.cta.secondary')}
				  </span>
				</button>
			  </div>
			  
			  <!-- Stats Grid -->
			  <div
				in:fly={{ y: prefersReducedMotion ? 0 : 20, duration: 800, delay: 800 }}
				class="grid grid-cols-2 gap-6"
			  >
				{#each getText('hero.stats') as stat, i}
				  <div class="group cursor-pointer">
					<div class="p-6 rounded-2xl glass-modern hover:scale-105 transition-all duration-300">
					  <div class="text-3xl font-black gradient-text-primary mb-2">
						{stat.value}
					  </div>
					  <div class="text-sm font-medium text-gray-600 dark:text-gray-400">
						{stat.label}
					  </div>
					</div>
				  </div>
				{/each}
			  </div>
			</div>
			
			<!-- Right SVG Animation -->
			<div class="lg:col-span-6 relative">
			  <div
				in:scale={{ duration: 1000, delay: 500, easing: 'cubicOut' }}
				class="relative w-full max-w-lg mx-auto"
			  >
				<svg viewBox="0 0 600 600" class="w-full h-full">
				  <defs>
					<!-- Gradient Definitions using CSS variables -->
					<linearGradient id="primaryGrad" x1="0%" y1="0%" x2="100%" y2="100%">
					  <stop offset="0%" stop-color="var(--color-primary-400)" stop-opacity="0.8">
						<animate attributeName="stop-color" values="var(--color-primary-400);var(--color-primary-600);var(--color-primary-400)" dur="4s" repeatCount="indefinite" />
					  </stop>
					  <stop offset="100%" stop-color="var(--color-primary-600)" stop-opacity="0.8">
						<animate attributeName="stop-color" values="var(--color-primary-600);var(--color-primary-400);var(--color-primary-600)" dur="4s" repeatCount="indefinite" />
					  </stop>
					</linearGradient>
					
					<linearGradient id="secondaryGrad" x1="0%" y1="0%" x2="100%" y2="100%">
					  <stop offset="0%" stop-color="var(--color-secondary-400)" stop-opacity="0.7" />
					  <stop offset="100%" stop-color="var(--color-secondary-600)" stop-opacity="0.7" />
					</linearGradient>
					
					<linearGradient id="accentGrad" x1="0%" y1="0%" x2="100%" y2="100%">
					  <stop offset="0%" stop-color="var(--color-accent-400)" stop-opacity="0.8" />
					  <stop offset="100%" stop-color="var(--color-accent-600)" stop-opacity="0.8" />
					</linearGradient>
					
					<!-- Glow Filter -->
					<filter id="glow">
					  <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
					  <feMerge>
						<feMergeNode in="coloredBlur"/>
						<feMergeNode in="SourceGraphic"/>
					  </feMerge>
					</filter>
					
					<!-- Shadow Filter -->
					<filter id="shadow" x="-50%" y="-50%" width="200%" height="200%">
					  <feGaussianBlur in="SourceAlpha" stdDeviation="3"/>
					  <feOffset dx="0" dy="4" result="offsetblur"/>
					  <feFlood flood-color="#000000" flood-opacity="0.1"/>
					  <feComposite in2="offsetblur" operator="in"/>
					  <feMerge>
						<feMergeNode/>
						<feMergeNode in="SourceGraphic"/>
					  </feMerge>
					</filter>
				  </defs>
				  
				  <!-- Background Circles -->
				  <circle cx="300" cy="300" r="280" fill="none" stroke="var(--color-primary-200)" stroke-width="1" opacity="0.3">
					<animate attributeName="r" values="280;290;280" dur="6s" repeatCount="indefinite" />
				  </circle>
				  <circle cx="300" cy="300" r="250" fill="none" stroke="var(--color-secondary-200)" stroke-width="1" opacity="0.3">
					<animate attributeName="r" values="250;240;250" dur="5s" repeatCount="indefinite" />
				  </circle>
				  
				  <!-- Central Building Complex -->
				  <g filter="url(#shadow)">
					<!-- Main Building -->
					<path d="M250 450 L250 200 Q300 170 350 200 L350 450 Z" 
						  fill="url(#primaryGrad)" 
						  stroke="var(--color-primary-600)" 
						  stroke-width="2"
						  filter="url(#glow)">
					  <animateTransform
						attributeName="transform"
						type="translate"
						values="0,0; 0,-10; 0,0"
						dur="4s"
						repeatCount="indefinite" />
					</path>
					
					<!-- Windows Animation -->
					{#each Array(12) as _, i}
					  <rect 
						x={270 + (i % 3) * 25} 
						y={230 + Math.floor(i / 3) * 50} 
						width="15" 
						height="25" 
						fill="var(--color-warning-400)"
						opacity="0"
						rx="2">
						<animate 
						  attributeName="opacity" 
						  values="0;0.8;0" 
						  dur="3s" 
						  begin="{i * 0.2}s"
						  repeatCount="indefinite" />
					  </rect>
					{/each}
					
					<!-- Side Buildings -->
					<path d="M180 450 L180 280 L230 250 L230 450 Z" 
						  fill="url(#secondaryGrad)" 
						  stroke="var(--color-secondary-600)" 
						  stroke-width="2">
					  <animateTransform
						attributeName="transform"
						type="translate"
						values="0,0; -5,-5; 0,0"
						dur="5s"
						repeatCount="indefinite" />
					</path>
					
					<path d="M370 450 L370 280 L420 250 L420 450 Z" 
						  fill="url(#secondaryGrad)" 
						  stroke="var(--color-secondary-600)" 
						  stroke-width="2">
					  <animateTransform
						attributeName="transform"
						type="translate"
						values="0,0; 5,-5; 0,0"
						dur="5s"
						begin="0.5s"
						repeatCount="indefinite" />
					</path>
				  </g>
				  
				  <!-- Auction Gavel Animation -->
				  <g transform="translate(300, 150)">
					<g class="origin-center">
					  <animateTransform
						attributeName="transform"
						type="rotate"
						values="0;-30;0"
						dur="2s"
						repeatCount="indefinite" />
					  
					  <!-- Gavel Handle -->
					  <rect x="-60" y="-5" width="60" height="10" rx="5" fill="url(#accentGrad)" filter="url(#glow)" />
					  
					  <!-- Gavel Head -->
					  <rect x="-80" y="-10" width="30" height="20" rx="3" fill="url(#accentGrad)" filter="url(#shadow)" />
					</g>
					
					<!-- Impact Lines -->
					{#each Array(3) as _, i}
					  <line 
						x1="0" 
						y1="0" 
						x2="{30 + i * 10}" 
						y2="{-20 + i * 5}" 
						stroke="var(--color-accent-500)" 
						stroke-width="2"
						opacity="0"
						stroke-linecap="round">
						<animate 
						  attributeName="opacity" 
						  values="0;1;0" 
						  dur="2s" 
						  begin="{1.5 + i * 0.1}s"
						  repeatCount="indefinite" />
					  </line>
					{/each}
				  </g>
				  
				  <!-- Floating Elements -->
				  <!-- Price Tags -->
				  {#each [
					{ x: 150, y: 200, price: "$2.5M", delay: "0s" },
					{ x: 400, y: 180, price: "$3.8M", delay: "1s" },
					{ x: 200, y: 350, price: "$1.9M", delay: "2s" }
				  ] as tag}
					<g transform="translate({tag.x}, {tag.y})">
					  <rect 
						x="-30" 
						y="-15" 
						width="60" 
						height="30" 
						rx="15" 
						fill="var(--color-success-500)"
						opacity="0.9"
						filter="url(#shadow)">
						<animate
						  attributeName="y"
						  values="-15;-25;-15"
						  dur="3s"
						  begin={tag.delay}
						  repeatCount="indefinite" />
					  </rect>
					  <text 
						x="0" 
						y="5" 
						text-anchor="middle" 
						fill="white" 
						font-size="14" 
						font-weight="bold">
						{tag.price}
						<animate
						  attributeName="y"
						  values="5;-5;5"
						  dur="3s"
						  begin={tag.delay}
						  repeatCount="indefinite" />
					  </text>
					</g>
				  {/each}
				  
				  <!-- Feature Icons -->
				  <g transform="translate(300, 500)">
					<!-- Live Badge -->
					<g transform="translate(-100, 0)">
					  <circle cx="0" cy="0" r="30" fill="var(--color-danger-100)" opacity="0.2">
						<animate attributeName="r" values="30;35;30" dur="2s" repeatCount="indefinite" />
					  </circle>
					  <circle cx="0" cy="0" r="8" fill="var(--color-danger-500)">
						<animate attributeName="opacity" values="1;0.5;1" dur="1s" repeatCount="indefinite" />
					  </circle>
					  <text x="0" y="25" text-anchor="middle" font-size="12" fill="var(--color-danger-600)" font-weight="600">
						{getText('hero.features.live')}
					  </text>
					</g>
					
					<!-- Secure Badge -->
					<g transform="translate(0, 0)">
					  <circle cx="0" cy="0" r="30" fill="var(--color-primary-100)" opacity="0.2" />
					  <path d="M -10 -10 L 10 -10 L 10 5 L 0 15 L -10 5 Z" 
							fill="var(--color-primary-500)" 
							stroke="none">
						<animateTransform
						  attributeName="transform"
						  type="scale"
						  values="1;1.1;1"
						  dur="3s"
						  repeatCount="indefinite" />
					  </path>
					  <text x="0" y="25" text-anchor="middle" font-size="12" fill="var(--color-primary-600)" font-weight="600">
						{getText('hero.features.secure')}
					  </text>
					</g>
					
					<!-- Verified Badge -->
					<g transform="translate(100, 0)">
					  <circle cx="0" cy="0" r="30" fill="var(--color-success-100)" opacity="0.2" />
					  <path d="M -12 0 L -4 8 L 12 -8" 
							fill="none" 
							stroke="var(--color-success-500)" 
							stroke-width="4"
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-dasharray="30"
							stroke-dashoffset="30">
						<animate 
						  attributeName="stroke-dashoffset" 
						  values="30;0" 
						  dur="2s" 
						  repeatCount="indefinite" />
					  </path>
					  <text x="0" y="25" text-anchor="middle" font-size="12" fill="var(--color-success-600)" font-weight="600">
						{getText('hero.features.verified')}
					  </text>
					</g>
				  </g>
				  
				  <!-- Particle Effects -->
				  {#each Array(15) as _, i}
					<circle 
					  cx="{150 + Math.random() * 300}" 
					  cy="{100 + Math.random() * 400}" 
					  r="2"
					  fill="var(--color-primary-400)"
					  opacity="0">
					  <animate
						attributeName="opacity"
						values="0;0.6;0"
						dur="{3 + Math.random() * 2}s"
						begin="{Math.random() * 3}s"
						repeatCount="indefinite" />
					  <animateTransform
						attributeName="transform"
						type="translate"
						values="0,0; {Math.random() * 20 - 10},{-Math.random() * 30}; 0,0"
						dur="{3 + Math.random() * 2}s"
						begin="{Math.random() * 3}s"
						repeatCount="indefinite" />
					</circle>
				  {/each}
				</svg>
			  </div>
			</div>
		  </div>
		</div>
	  </section>
	{/if}
  </div>
  
  <style>
	/* Transform origin for rotation animations */
	.origin-center {
	  transform-origin: center;
	}
	
	/* Respect reduced motion */
	@media (prefers-reduced-motion: reduce) {
	  .animate-pulse,
	  .animate-ping {
		animation: none;
	  }
	}
  </style>