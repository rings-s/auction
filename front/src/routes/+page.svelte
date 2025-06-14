<script>
  import { onMount } from 'svelte';
  import { fade, fly, scale } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';
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
        badge: "50K+ Investors",
        title: {
          line1: "Premium",
          line2: "Auctions"
        },
        subtitle: "Join the world's most transparent real estate marketplace. Bid on verified properties with confidence.",
        cta: {
          primary: "Start Bidding",
          secondary: "Learn More"
        },
        stats: [
          { value: "$847M", label: "Volume" },
          { value: "12.5K", label: "Deals" },
          { value: "98%", label: "Success" },
          { value: "45", label: "Cities" }
        ],
        features: {
          live: "Live",
          secure: "Secure",
          verified: "Verified"
        }
      }
    },
    ar: {
      hero: {
        badge: "50ألف+ مستثمر",
        title: {
          line1: "مزادات",
          line2: "مميزة"
        },
        subtitle: "انضم إلى أكثر أسواق العقارات شفافية في العالم. قدم عروضك على العقارات الموثقة بثقة.",
        cta: {
          primary: "ابدأ المزايدة",
          secondary: "اعرف المزيد"
        },
        stats: [
          { value: "847م$", label: "الحجم" },
          { value: "12.5ألف", label: "صفقة" },
          { value: "98%", label: "نجاح" },
          { value: "45", label: "مدينة" }
        ],
        features: {
          live: "مباشر",
          secure: "آمن",
          verified: "موثق"
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
  <title>{isRTL ? 'مزادات عقارية مميزة' : 'Premium Real Estate Auctions'}</title>
  <meta name="description" content="{isRTL ? 'اكتشف العقارات الحصرية من خلال المزادات الشفافة.' : 'Discover exclusive properties through transparent auctions.'}">
</svelte:head>

<svelte:window bind:scrollY />

<div class="relative overflow-hidden bg-gradient-to-br from-white via-primary-50/10 to-secondary-50/10 dark:from-gray-900 dark:via-primary-950/10 dark:to-secondary-950/10" dir={isRTL ? 'rtl' : 'ltr'}>
  
  {#if mounted}
    <!-- Hero Section with Enhanced Design -->
    <section class="relative min-h-screen flex items-center py-16 sm:py-20 lg:py-24">
      <!-- Subtle Animated Background -->
      <div class="absolute inset-0 pointer-events-none overflow-hidden">
        <div 
          class="absolute -top-1/4 -left-1/4 w-[100vw] h-[100vh] rounded-full opacity-[0.08]"
          style="background: radial-gradient(circle at center, var(--color-primary-400), transparent 60%);
                 transform: rotate({scrollY * 0.02}deg) scale({1 + scrollY * 0.0001});
                 filter: blur(100px);"
        ></div>
        <div 
          class="absolute -bottom-1/4 -right-1/4 w-[80vw] h-[80vh] rounded-full opacity-[0.06]"
          style="background: radial-gradient(circle at center, var(--color-secondary-400), transparent 60%);
                 transform: rotate({-scrollY * 0.02}deg) scale({1 + scrollY * 0.0001});
                 filter: blur(120px);"
        ></div>
      </div>
      
      <div class="relative z-10 w-full max-w-[1600px] mx-auto px-6 sm:px-8 lg:px-12">
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12 items-center">
          
          <!-- Left Content - Refined Typography -->
          <div class="lg:col-span-5 space-y-6 lg:space-y-8">
            <!-- Compact Trust Badge -->
            <div
              in:fly={{ y: prefersReducedMotion ? 0 : 20, duration: 600, delay: 200 }}
              class="inline-flex items-center gap-2 px-3 py-1.5 bg-success-50/80 dark:bg-success-900/20 border border-success-200/50 dark:border-success-700/50 rounded-full"
            >
              <div class="w-1.5 h-1.5 bg-success-500 rounded-full animate-pulse"></div>
              <span class="text-xs font-medium text-success-700 dark:text-success-300 tracking-wide uppercase">
                {getText('hero.badge')}
              </span>
            </div>
            
            <!-- Simplified Title -->
            <div class="space-y-1">
              <h1
                in:fly={{ y: prefersReducedMotion ? 0 : 30, duration: 800, delay: 300 }}
                class="text-6xl sm:text-7xl lg:text-8xl xl:text-9xl font-black leading-[0.85] tracking-tighter"
              >
                <span class="block text-gray-900 dark:text-white">
                  {getText('hero.title.line1')}
                </span>
                <span class="block gradient-text-primary mt-2">
                  {getText('hero.title.line2')}
                </span>
              </h1>
            </div>
            
            <!-- Concise Subtitle -->
            <p
              in:fly={{ y: prefersReducedMotion ? 0 : 20, duration: 800, delay: 400 }}
              class="text-base lg:text-lg leading-relaxed text-gray-600 dark:text-gray-400 max-w-md"
            >
              {getText('hero.subtitle')}
            </p>
            
            <!-- Refined CTA Buttons -->
            <div
              in:fly={{ y: prefersReducedMotion ? 0 : 20, duration: 800, delay: 500 }}
              class="flex flex-col sm:flex-row gap-3"
            >
              <button class="px-6 py-3 bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-700 hover:to-primary-800 text-white font-medium rounded-xl shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all duration-200">
                {getText('hero.cta.primary')}
              </button>
              
              <button class="px-6 py-3 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm text-gray-700 dark:text-gray-300 font-medium rounded-xl border border-gray-200/50 dark:border-gray-700/50 hover:bg-white dark:hover:bg-gray-800 shadow-sm hover:shadow-md transform hover:-translate-y-0.5 transition-all duration-200">
                {getText('hero.cta.secondary')}
              </button>
            </div>
            
            <!-- Minimal Stats -->
            <div
              in:fly={{ y: prefersReducedMotion ? 0 : 20, duration: 800, delay: 600 }}
              class="grid grid-cols-4 gap-4 pt-4"
            >
              {#each getText('hero.stats') as stat, i}
                <div class="text-center">
                  <div class="text-2xl font-bold text-gray-900 dark:text-white">
                    {stat.value}
                  </div>
                  <div class="text-xs text-gray-500 dark:text-gray-500 mt-0.5">
                    {stat.label}
                  </div>
                </div>
              {/each}
            </div>
          </div>
          
          <!-- Right SVG Animation - Larger and Enhanced -->
          <div class="lg:col-span-7 relative">
            <div
              in:scale={{ duration: 1000, delay: 300, easing: cubicOut }}
              class="relative w-full"
            >
              <svg viewBox="0 0 800 700" class="w-full h-full max-w-[800px] mx-auto">
                <defs>
                  <!-- Enhanced Gradients -->
                  <linearGradient id="primaryGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="var(--color-primary-400)" stop-opacity="0.9">
                      <animate attributeName="stop-color" values="var(--color-primary-400);var(--color-primary-500);var(--color-primary-400)" dur="4s" repeatCount="indefinite" />
                    </stop>
                    <stop offset="100%" stop-color="var(--color-primary-600)" stop-opacity="0.9">
                      <animate attributeName="stop-color" values="var(--color-primary-600);var(--color-primary-500);var(--color-primary-600)" dur="4s" repeatCount="indefinite" />
                    </stop>
                  </linearGradient>
                  
                  <linearGradient id="secondaryGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="var(--color-secondary-400)" stop-opacity="0.8" />
                    <stop offset="100%" stop-color="var(--color-secondary-600)" stop-opacity="0.8" />
                  </linearGradient>
                  
                  <linearGradient id="accentGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="var(--color-accent-400)" stop-opacity="0.9" />
                    <stop offset="100%" stop-color="var(--color-accent-600)" stop-opacity="0.9" />
                  </linearGradient>
                  
                  <!-- Refined Filters -->
                  <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
                    <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
                    <feMerge>
                      <feMergeNode in="coloredBlur"/>
                      <feMergeNode in="SourceGraphic"/>
                    </feMerge>
                  </filter>
                  
                  <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
                    <feDropShadow dx="0" dy="3" stdDeviation="4" flood-opacity="0.15"/>
                  </filter>
                </defs>
                
                <!-- Subtle Background Elements -->
                <circle cx="400" cy="350" r="320" fill="none" stroke="var(--color-primary-200)" stroke-width="0.5" opacity="0.2">
                  <animate attributeName="r" values="320;340;320" dur="8s" repeatCount="indefinite" />
                </circle>
                
                <!-- Main Building Group - Larger Scale -->
                <g transform="translate(400, 350) scale(1.4)">
                  <!-- Central Skyscraper -->
                  <g filter="url(#shadow)">
                    <path d="M -60 150 L -60 -100 Q 0 -130 60 -100 L 60 150 Z" 
                          fill="url(#primaryGrad)" 
                          stroke="var(--color-primary-700)" 
                          stroke-width="1.5"
                          filter="url(#glow)">
                      <animateTransform
                        attributeName="transform"
                        type="translate"
                        values="0,0; 0,-8; 0,0"
                        dur="5s"
                        repeatCount="indefinite" />
                    </path>
                    
                    <!-- Building Windows Grid -->
                    {#each Array(20) as _, i}
                      <rect 
                        x={-45 + (i % 4) * 25} 
                        y={-80 + Math.floor(i / 4) * 35} 
                        width="18" 
                        height="25" 
                        fill="var(--color-warning-300)"
                        opacity="0"
                        rx="2">
                        <animate 
                          attributeName="opacity" 
                          values="0;0.7;0.3;0.7;0" 
                          dur="4s" 
                          begin="{i * 0.15}s"
                          repeatCount="indefinite" />
                      </rect>
                    {/each}
                  </g>
                  
                  <!-- Left Building -->
                  <g filter="url(#shadow)">
                    <path d="M -140 150 L -140 -20 L -80 -50 L -80 150 Z" 
                          fill="url(#secondaryGrad)" 
                          stroke="var(--color-secondary-700)" 
                          stroke-width="1.5">
                      <animateTransform
                        attributeName="transform"
                        type="translate"
                        values="0,0; -3,-5; 0,0"
                        dur="6s"
                        repeatCount="indefinite" />
                    </path>
                  </g>
                  
                  <!-- Right Building -->
                  <g filter="url(#shadow)">
                    <path d="M 80 150 L 80 -20 L 140 -50 L 140 150 Z" 
                          fill="url(#secondaryGrad)" 
                          stroke="var(--color-secondary-700)" 
                          stroke-width="1.5">
                      <animateTransform
                        attributeName="transform"
                        type="translate"
                        values="0,0; 3,-5; 0,0"
                        dur="6s"
                        begin="1s"
                        repeatCount="indefinite" />
                    </path>
                  </g>
                </g>
                
                <!-- Auction Gavel - Positioned Higher -->
                <g transform="translate(400, 180)">
                  <g class="origin-center">
                    <animateTransform
                      attributeName="transform"
                      type="rotate"
                      values="0;-25;0"
                      dur="2.5s"
                      repeatCount="indefinite" />
                    
                    <!-- Gavel -->
                    <rect x="-80" y="-6" width="80" height="12" rx="6" fill="url(#accentGrad)" filter="url(#shadow)" />
                    <rect x="-100" y="-12" width="35" height="24" rx="4" fill="url(#accentGrad)" filter="url(#shadow)" />
                  </g>
                  
                  <!-- Impact Effect -->
                  <circle cx="0" cy="0" r="20" fill="none" stroke="var(--color-accent-400)" stroke-width="2" opacity="0">
                    <animate attributeName="r" values="20;60;20" dur="2.5s" repeatCount="indefinite" />
                    <animate attributeName="opacity" values="0;0.3;0" dur="2.5s" repeatCount="indefinite" />
                  </circle>
                </g>
                
                <!-- Floating Price Indicators - Minimal -->
                {#each [
                  { x: 250, y: 250, price: "$2.5M", delay: "0s" },
                  { x: 550, y: 230, price: "$3.8M", delay: "0.8s" },
                  { x: 350, y: 450, price: "$1.9M", delay: "1.6s" }
                ] as tag}
                  <g transform="translate({tag.x}, {tag.y})">
                    <rect 
                      x="-28" 
                      y="-12" 
                      width="56" 
                      height="24" 
                      rx="12" 
                      fill="var(--color-success-500)"
                      opacity="0.85"
                      filter="url(#shadow)">
                      <animate
                        attributeName="y"
                        values="-12;-20;-12"
                        dur="3s"
                        begin={tag.delay}
                        repeatCount="indefinite" />
                    </rect>
                    <text 
                      x="0" 
                      y="4" 
                      text-anchor="middle" 
                      fill="white" 
                      font-size="13" 
                      font-weight="600">
                      {tag.price}
                      <animate
                        attributeName="y"
                        values="4;-4;4"
                        dur="3s"
                        begin={tag.delay}
                        repeatCount="indefinite" />
                    </text>
                  </g>
                {/each}
                
                <!-- Minimal Feature Badges -->
                <g transform="translate(400, 600)">
                  {#each [
                    { x: -120, feature: 'live', color: 'danger' },
                    { x: 0, feature: 'secure', color: 'primary' },
                    { x: 120, feature: 'verified', color: 'success' }
                  ] as item, i}
                    <g transform="translate({item.x}, 0)">
                      <circle cx="0" cy="0" r="4" fill="var(--color-{item.color}-500)">
                        <animate attributeName="r" values="4;6;4" dur="2s" begin="{i * 0.3}s" repeatCount="indefinite" />
                      </circle>
                      <text x="0" y="20" text-anchor="middle" font-size="11" fill="var(--color-{item.color}-600)" font-weight="500" class="uppercase">
                        {getText(`hero.features.${item.feature}`)}
                      </text>
                    </g>
                  {/each}
                </g>
                
                <!-- Subtle Particles -->
                {#each Array(8) as _, i}
                  <circle 
                    cx="{200 + Math.random() * 400}" 
                    cy="{150 + Math.random() * 400}" 
                    r="1.5"
                    fill="var(--color-primary-400)"
                    opacity="0">
                    <animate
                      attributeName="opacity"
                      values="0;0.4;0"
                      dur="{4 + Math.random() * 2}s"
                      begin="{Math.random() * 3}s"
                      repeatCount="indefinite" />
                    <animateTransform
                      attributeName="transform"
                      type="translate"
                      values="0,0; {Math.random() * 10 - 5},{-Math.random() * 20}; 0,0"
                      dur="{4 + Math.random() * 2}s"
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
  
  /* Simplified uppercase text */
  .uppercase {
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  
  /* Respect reduced motion */
  @media (prefers-reduced-motion: reduce) {
    .animate-pulse {
      animation: none;
    }
  }
</style>