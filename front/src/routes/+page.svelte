<script>
  import { onMount } from 'svelte';
  import { locale, t } from '$lib/i18n';
  $: isRTL = $locale === 'ar';
  import { fade, fly, scale } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';
  import Button from '$lib/components/ui/Button.svelte';
  import { theme } from '$lib/stores/theme';
  
  let mounted = false;
  let prefersReducedMotion = false;
  let scrollY = 0;
  
  // Enhanced animations with stagger effect
  let visibleElements = {
    badge: false,
    headline: false,
    subheadline: false,
    cta: false,
    metrics: false,
    marketCard: false
  };
  
  // Enhanced translations with Marketing Growth Card
  const translations = {
    en: {
      badge: {
        live: 'Live Now',
        count: '24 Active'
      },
      headline: 'Auctions',
      subheadline: 'Discover exclusive properties through transparent auctions. Join thousands of successful buyers and sellers.',
      cta: {
        primary: 'Start Bidding',
        secondary: 'View Properties'
      },
      metrics: [
        { value: '$2.5M+', label: 'Sold' },
        { value: '98%', label: 'Success' },
        { value: '15K+', label: 'Users' },
        { value: '4.9★', label: 'Rating' }
      ],
      marketGrowth: {
        title: 'Market Growth',
        period: '12 months',
        stats: {
          growthRate: { value: '+24.5%', label: 'Growth Rate' },
          volume: { value: '$3.2M', label: 'Volume' }
        },
        metrics: [
          { label: 'Properties Sold', value: '+18.2%' },
          { label: 'Average Price', value: '+12.8%' },
          { label: 'Market Activity', value: '+31.5%' }
        ]
      }
    },
    ar: {
      badge: {
        live: 'مباشر الآن',
        count: '24 نشط'
      },
      headline: 'مزادات',
      subheadline: 'اكتشف العقارات الحصرية من خلال المزادات الشفافة. انضم لآلاف المشترين والبائعين الناجحين.',
      cta: {
        primary: 'ابدأ المزايدة',
        secondary: 'عرض العقارات'
      },
      metrics: [
        { value: '+2.5م$', label: 'مباع' },
        { value: '98%', label: 'نجاح' },
        { value: '+15ألف', label: 'مستخدم' },
        { value: '★4.9', label: 'تقييم' }
      ],
      marketGrowth: {
        title: 'نمو السوق',
        period: '12 شهر',
        stats: {
          growthRate: { value: '+24.5%', label: 'معدل النمو' },
          volume: { value: '3.2م$', label: 'الحجم' }
        },
        metrics: [
          { label: 'العقارات المباعة', value: '+18.2%' },
          { label: 'متوسط السعر', value: '+12.8%' },
          { label: 'نشاط السوق', value: '+31.5%' }
        ]
      }
    }
  };
  
  // Get text with fallback
  function getText(key) {
    const lang = $locale || 'en';
    const keys = key.split('.');
    let value = translations[lang] || translations.en;
    
    for (const k of keys) {
      if (value && value[k]) {
        value = value[k];
      } else {
        return key;
      }
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

    // Staggered animation reveal
    const animationSequence = [
      { element: 'badge', delay: 100 },
      { element: 'headline', delay: 200 },
      { element: 'subheadline', delay: 300 },
      { element: 'cta', delay: 400 },
      { element: 'metrics', delay: 500 },
      { element: 'marketCard', delay: 600 }
    ];

    animationSequence.forEach(({ element, delay }) => {
      setTimeout(() => {
        visibleElements[element] = true;
      }, delay);
    });
  });
</script>

<svelte:head>
  <title>Premier Real Estate Auctions | Find Your Perfect Property</title>
  <meta name="description" content="Discover exclusive properties through transparent auctions. Join thousands of satisfied buyers in finding their dream properties.">
</svelte:head>

<svelte:window bind:scrollY />

<!-- Clean White Hero Section with Bottom Gradient -->
<section class="hero-section-white relative min-h-screen flex items-center overflow-hidden" aria-label="Hero section">
  
  <!-- White to Purple Gradient Background (matches reference image) -->
  <div class="gradient-bg-white absolute inset-0 z-0" aria-hidden="true">
    <!-- Main gradient from white top to purple bottom -->
    <div class="main-gradient"></div>
    
    <!-- Floating geometric elements (like in reference) -->
    <div class="floating-elements">
      <div class="element element-1"></div>
      <div class="element element-2"></div>
      <div class="element element-3"></div>
      <div class="element element-4"></div>
      <div class="element element-5"></div>
      <div class="element element-6"></div>
      <div class="element element-7"></div>
      <div class="element element-8"></div>
    </div>
  </div>

  <!-- Enhanced Dynamic SVG Background - Center Right -->
  <div class="absolute top-1/2 w-[70%] h-[90%] z-5 overflow-visible opacity-20 {isRTL ? 'left-0' : 'right-0'} -translate-y-1/2" aria-hidden="true">
    <svg class="w-full h-full svg-enhanced rtl:scale-x-[-1]" viewBox="0 0 1200 800" fill="none" xmlns="http://www.w3.org/2000/svg">

      <!-- Enhanced animated building outlines -->
      <g class="buildings-group" style="animation-duration: 12s;">
        <!-- Building 1 - Modern Skyscraper -->
        <path class="building-element" style="animation-delay: 0s; animation-duration: 8s;" d="M500 700 L500 150 L580 130 L580 700 Z" stroke="url(#gradientWhite1)" stroke-width="2" fill="url(#buildingFillWhite1)"/>
        <path d="M500 150 L540 120 L580 130 Z" stroke="url(#gradientWhite1)" stroke-width="1.5" fill="url(#accentWhite1)"/>
        <!-- Enhanced Windows with subtle glow -->
        <rect x="520" y="180" width="12" height="16" fill="url(#windowGlowWhite)" rx="2" class="window-glow-white"/>
        <rect x="540" y="200" width="12" height="16" fill="url(#windowGlowWhite)" rx="2" class="window-glow-white"/>
        <rect x="520" y="240" width="12" height="16" fill="url(#windowGlowWhite)" rx="2" class="window-glow-white"/>
        <rect x="540" y="260" width="12" height="16" fill="url(#windowGlowWhite)" rx="2" class="window-glow-white"/>
        
        <!-- Building 2 - Corporate Tower -->
        <path class="building-element" style="animation-delay: 1.5s; animation-duration: 8s;" d="M620 700 L620 100 L720 80 L720 700 Z" stroke="url(#gradientWhite2)" stroke-width="2" fill="url(#buildingFillWhite2)"/>
        <path d="M620 100 L670 60 L720 80 Z" stroke="url(#gradientWhite2)" stroke-width="1.5" fill="url(#accentWhite2)"/>
        <!-- Enhanced Glass facade -->
        <rect x="640" y="120" width="60" height="200" fill="url(#glassFacadeWhite)" opacity="0.3" rx="4" class="glass-panel-white"/>
        
        <!-- Building 3 - Residential Complex -->
        <path class="building-element" style="animation-delay: 3s; animation-duration: 8s;" d="M750 700 L750 200 L880 180 L880 700 Z" stroke="url(#gradientWhite3)" stroke-width="2" fill="url(#buildingFillWhite3)"/>
        <path d="M750 200 L815 160 L880 180 Z" stroke="url(#gradientWhite3)" stroke-width="1.5" fill="url(#accentWhite3)"/>
        
        <!-- Building 4 - Mixed Use -->
        <path class="building-element" style="animation-delay: 4.5s; animation-duration: 8s;" d="M900 700 L900 250 L1020 230 L1020 700 Z" stroke="url(#gradientWhite4)" stroke-width="2" fill="url(#buildingFillWhite4)"/>
        
        <!-- Building 5 - Luxury Towers -->
        <path class="building-element" style="animation-delay: 6s; animation-duration: 8s;" d="M1050 700 L1050 120 L1150 100 L1150 700 Z" stroke="url(#gradientWhite1)" stroke-width="2" fill="url(#buildingFillWhite1)"/>
        <path d="M1050 120 L1100 80 L1150 100 Z" stroke="url(#gradientWhite1)" stroke-width="1.5" fill="url(#accentWhite1)"/>
      </g>
      
      <!-- Enhanced fluid growth curves -->
      <g class="growth-curves" style="animation-duration: 15s;">
        <path class="growth-curve" style="animation-delay: 0s; animation-duration: 10s;" d="M375 600 Q575 450 775 380 Q975 310 1175 250" stroke="url(#growthGradientWhite)" stroke-width="3" fill="none"/>
        <path class="growth-curve" style="animation-delay: 2s; animation-duration: 10s;" d="M425 650 Q625 500 825 430 Q1025 360 1225 300" stroke="url(#growthGradientWhite2)" stroke-width="2" fill="none"/>
        <path class="growth-curve" style="animation-delay: 4s; animation-duration: 10s;" d="M475 680 Q675 530 875 460 Q1075 390 1275 330" stroke="url(#growthGradientWhite3)" stroke-width="2" fill="none"/>
      </g>
      
      <!-- Enhanced floating data points -->
      <g class="data-points" style="animation-duration: 6s;">
        <circle class="data-point" style="animation-delay: 0s; animation-duration: 4s;" cx="675" cy="400" r="4" fill="url(#accentWhite1)"/>
        <circle class="data-point" style="animation-delay: 1s; animation-duration: 4s;" cx="875" cy="350" r="4" fill="url(#accentWhite2)"/>
        <circle class="data-point" style="animation-delay: 2s; animation-duration: 4s;" cx="1075" cy="300" r="5" fill="url(#accentWhite3)"/>
        <circle class="data-point" style="animation-delay: 0.5s; animation-duration: 4s;" cx="775" cy="380" r="3" fill="url(#accentWhite4)"/>
        <circle class="data-point" style="animation-delay: 1.5s; animation-duration: 4s;" cx="975" cy="320" r="4" fill="url(#accentWhite1)"/>
      </g>
      
      <!-- White theme gradient definitions -->
      <defs>
        <linearGradient id="gradientWhite1" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#8b5cf6" stop-opacity="0.4"/>
          <stop offset="100%" stop-color="#6366f1" stop-opacity="0.3"/>
        </linearGradient>
        <linearGradient id="gradientWhite2" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#3b82f6" stop-opacity="0.4"/>
          <stop offset="100%" stop-color="#8b5cf6" stop-opacity="0.3"/>
        </linearGradient>
        <linearGradient id="gradientWhite3" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#06b6d4" stop-opacity="0.4"/>
          <stop offset="100%" stop-color="#3b82f6" stop-opacity="0.3"/>
        </linearGradient>
        <linearGradient id="gradientWhite4" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#8b5cf6" stop-opacity="0.4"/>
          <stop offset="100%" stop-color="#06b6d4" stop-opacity="0.3"/>
        </linearGradient>
        <linearGradient id="growthGradientWhite" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="#8b5cf6" stop-opacity="0.6"/>
          <stop offset="50%" stop-color="#3b82f6" stop-opacity="0.4"/>
          <stop offset="100%" stop-color="#06b6d4" stop-opacity="0.3"/>
        </linearGradient>
        <linearGradient id="growthGradientWhite2" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="#6366f1" stop-opacity="0.5"/>
          <stop offset="100%" stop-color="#8b5cf6" stop-opacity="0.3"/>
        </linearGradient>
        <linearGradient id="growthGradientWhite3" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="#3b82f6" stop-opacity="0.4"/>
          <stop offset="100%" stop-color="#06b6d4" stop-opacity="0.2"/>
        </linearGradient>
        <radialGradient id="buildingFillWhite1" cx="50%" cy="50%" r="70%">
          <stop offset="0%" stop-color="#f8fafc" stop-opacity="0.8"/>
          <stop offset="100%" stop-color="#e2e8f0" stop-opacity="0.6"/>
        </radialGradient>
        <radialGradient id="buildingFillWhite2" cx="50%" cy="50%" r="70%">
          <stop offset="0%" stop-color="#f1f5f9" stop-opacity="0.8"/>
          <stop offset="100%" stop-color="#e2e8f0" stop-opacity="0.6"/>
        </radialGradient>
        <radialGradient id="buildingFillWhite3" cx="50%" cy="50%" r="70%">
          <stop offset="0%" stop-color="#f8fafc" stop-opacity="0.8"/>
          <stop offset="100%" stop-color="#cbd5e1" stop-opacity="0.6"/>
        </radialGradient>
        <radialGradient id="buildingFillWhite4" cx="50%" cy="50%" r="70%">
          <stop offset="0%" stop-color="#f1f5f9" stop-opacity="0.8"/>
          <stop offset="100%" stop-color="#e2e8f0" stop-opacity="0.6"/>
        </radialGradient>
        <radialGradient id="accentWhite1" cx="50%" cy="50%" r="60%">
          <stop offset="0%" stop-color="#8b5cf6" stop-opacity="0.6"/>
          <stop offset="100%" stop-color="#6366f1" stop-opacity="0.4"/>
        </radialGradient>
        <radialGradient id="accentWhite2" cx="50%" cy="50%" r="60%">
          <stop offset="0%" stop-color="#3b82f6" stop-opacity="0.6"/>
          <stop offset="100%" stop-color="#8b5cf6" stop-opacity="0.4"/>
        </radialGradient>
        <radialGradient id="accentWhite3" cx="50%" cy="50%" r="60%">
          <stop offset="0%" stop-color="#06b6d4" stop-opacity="0.6"/>
          <stop offset="100%" stop-color="#3b82f6" stop-opacity="0.4"/>
        </radialGradient>
        <radialGradient id="accentWhite4" cx="50%" cy="50%" r="60%">
          <stop offset="0%" stop-color="#8b5cf6" stop-opacity="0.6"/>
          <stop offset="100%" stop-color="#06b6d4" stop-opacity="0.4"/>
        </radialGradient>
        <linearGradient id="windowGlowWhite" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#fbbf24" stop-opacity="0.8"/>
          <stop offset="100%" stop-color="#f59e0b" stop-opacity="0.6"/>
        </linearGradient>
        <linearGradient id="glassFacadeWhite" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#e0e7ff" stop-opacity="0.4"/>
          <stop offset="100%" stop-color="#c7d2fe" stop-opacity="0.2"/>
        </linearGradient>
      </defs>
    </svg>
  </div>

  <!-- Clean White Glass Container -->
  <div class="relative z-10 w-full max-w-7xl mx-auto px-4 sm:px-6 md:px-8 lg:px-12 xl:px-16">
    {#if mounted}
      <!-- Clean Status Badge -->
      <div class="flex justify-start mb-12">
        {#if visibleElements.badge}
          <div 
            in:fade={{ duration: 600, delay: 0, easing: cubicOut }}
            class="white-badge status-badge inline-flex items-center gap-3 px-6 py-4 rounded-2xl text-sm font-semibold transition-all duration-500 hover:-translate-y-1 hover:shadow-white-lg group"
            role="status"
            aria-live="polite"
          >
            <span class="w-3 h-3 bg-emerald-400 rounded-full pulse-glow-white" aria-hidden="true"></span>
            <span class="text-purple-600 font-bold tracking-wide">{getText('badge.live')}</span>
            <span class="white-divider w-px h-4 bg-gradient-to-b from-transparent via-slate-300 to-transparent"></span>
            <span class="text-slate-600 text-xs font-medium">{getText('badge.count')}</span>
          </div>
        {/if}
      </div>

      <!-- F-Layout: Main content grid -->
      <div class="grid grid-cols-1 lg:grid-cols-5 gap-16 lg:gap-24 items-start">
        
        <!-- Left column: Enhanced Primary F-pattern content -->
        <div class="lg:col-span-3 space-y-10">
          
          <!-- Custom Typography Headline -->
          <div class="max-w-4xl">
            {#if visibleElements.headline}
              <h1 
                in:fly={{ y: prefersReducedMotion ? 0 : 40, duration: 800, delay: 0, easing: cubicOut }}
                class="hero-title {isRTL ? 'text-right' : 'text-left'}"
                class:hero-title-ar={isRTL}
                class:hero-title-en={!isRTL}
              >
                {getText('headline')}
              </h1>
            {/if}
          </div>
          
          <!-- Custom Typography Paragraph -->
          <div class="{isRTL ? 'max-w-2xl' : 'max-w-3xl'}">
            {#if visibleElements.subheadline}
              <p 
                in:fly={{ y: prefersReducedMotion ? 0 : 30, duration: 700, delay: 0, easing: cubicOut }}
                class="hero-paragraph {isRTL ? 'text-right' : 'text-left'}"
              >
                {getText('subheadline')}
              </p>
            {/if}
          </div>
          
          <!-- Clean CTA buttons -->
          {#if visibleElements.cta}
            <div 
              in:fly={{ y: prefersReducedMotion ? 0 : 30, duration: 700, delay: 0, easing: cubicOut }}
              class="flex flex-col sm:flex-row gap-4 pt-6 {isRTL ? 'sm:flex-row-reverse justify-end' : ''}"
            >
              <div class="white-button-wrapper">
                <Button 
                  variant="primary" 
                  size="small" 
                  href="/auctions"
                  class="white-button-primary group relative overflow-hidden bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white border-0 shadow-lg hover:shadow-xl"
                >
                  <span class="relative z-10">{getText('cta.primary')}</span>
                  <svg 
                    class="w-4 h-4 transition-all duration-300 group-hover:translate-x-1 relative z-10 {isRTL ? 'rotate-180' : ''}" 
                    fill="none" 
                    stroke="currentColor" 
                    viewBox="0 0 24 24"
                    aria-hidden="true"
                    slot="iconRight"
                  >
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </Button>
              </div>

              <div class="white-button-wrapper">
                <Button 
                  variant="outline" 
                  size="small" 
                  href="/properties"
                  class="white-button-secondary bg-white text-slate-700 border-slate-300 hover:bg-slate-50 hover:border-slate-400 shadow-sm hover:shadow-md"
                >
                  <span>{getText('cta.secondary')}</span>
                </Button>
              </div>
            </div>
          {/if}

          <!-- Clean Trust metrics -->
          {#if visibleElements.metrics}
            <div 
              in:fade={{ duration: 700, delay: 0, easing: cubicOut }}
              class="grid grid-cols-2 sm:grid-cols-4 gap-6 pt-10"
              role="region"
              aria-label="Platform statistics"
            >
              {#each getText('metrics') as metric, index}
                <div 
                  class="white-metric-card metric-card text-center p-6 rounded-2xl transition-all duration-500 hover:-translate-y-3 hover:shadow-white-xl group" 
                  in:scale={{ duration: 500, delay: index * 100, easing: cubicOut }}
                >
                  <span class="metric-value-white block text-2xl sm:text-3xl font-black leading-none mb-2 text-slate-800">
                    {metric.value}
                  </span>
                  <span class="metric-label-white block text-sm font-medium text-slate-600">
                    {metric.label}
                  </span>
                  <div class="metric-glow-white absolute inset-0 rounded-2xl bg-gradient-to-br from-purple-500/5 to-indigo-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                </div>
              {/each}
            </div>
          {/if}
        </div>

        <!-- Enhanced Right column with proper spacing -->
        <div class="lg:col-span-2 space-y-8 lg:mt-16">
          {#if visibleElements.marketCard}
            <div 
              class="white-market-card market-growth-card rounded-3xl p-8 transition-all duration-700 hover:-translate-y-4 hover:shadow-white-2xl group"
              in:fly={{ y: prefersReducedMotion ? 0 : 50, duration: 900, delay: 0, easing: cubicOut }}
            >
              <!-- Enhanced Header with Arabic support -->
              <div class="flex justify-between items-center mb-8">
                <h3 class="market-growth-title-white text-xl font-bold text-slate-800 {isRTL ? 'text-right' : 'text-left'}">{getText('marketGrowth.title')}</h3>
                <div class="flex items-center gap-3 white-status-pill px-3 py-1.5 rounded-full">
                  <span class="w-2 h-2 bg-emerald-400 rounded-full pulse-glow-white"></span>
                  <span class="market-growth-period-white text-sm font-medium text-slate-600">{getText('marketGrowth.period')}</span>
                </div>
              </div>
              
              <!-- Clean Chart -->
              <div class="mb-8 white-chart-container p-4 rounded-2xl">
                <svg class="w-full h-32" viewBox="0 0 300 120" fill="none">
                  <defs>
                    <pattern id="gridWhite" width="30" height="12" patternUnits="userSpaceOnUse">
                      <path d="m 30 0 l 0 12 m -30 0 l 30 0" stroke="#e2e8f0" stroke-width="0.5" opacity="0.5"/>
                    </pattern>
                    <linearGradient id="mainChartGradientWhite" x1="0%" y1="0%" x2="100%" y2="0%">
                      <stop offset="0%" stop-color="#8b5cf6" stop-opacity="0.8"/>
                      <stop offset="50%" stop-color="#3b82f6" stop-opacity="0.6"/>
                      <stop offset="100%" stop-color="#06b6d4" stop-opacity="0.4"/>
                    </linearGradient>
                    <linearGradient id="areaGradientWhite" x1="0%" y1="0%" x2="0%" y2="100%">
                      <stop offset="0%" stop-color="#8b5cf6" stop-opacity="0.3"/>
                      <stop offset="100%" stop-color="#8b5cf6" stop-opacity="0.05"/>
                    </linearGradient>
                  </defs>
                  
                  <rect width="100%" height="100%" fill="url(#gridWhite)"/>
                  <path class="chart-area-white" d="M15 100 Q50 80 100 60 Q150 45 200 35 Q250 25 285 20 L285 100 Z" fill="url(#areaGradientWhite)"/>
                  <path class="chart-line-white" d="M15 100 Q50 80 100 60 Q150 45 200 35 Q250 25 285 20" stroke="url(#mainChartGradientWhite)" stroke-width="3" fill="none"/>
                  <circle class="chart-point-white" cx="50" cy="80" r="4" fill="#8b5cf6"/>
                  <circle class="chart-point-white" cx="100" cy="60" r="4" fill="#3b82f6"/>
                  <circle class="chart-point-white" cx="150" cy="45" r="4" fill="#06b6d4"/>
                  <circle class="chart-point-white" cx="200" cy="35" r="5" fill="#8b5cf6"/>
                  <circle class="chart-point-white" cx="250" cy="25" r="5" fill="#3b82f6"/>
                  <path d="M270 30 L280 20 L275 20 L275 15 M280 20 L275 25" stroke="#06b6d4" stroke-width="2" fill="none"/>
                </svg>
              </div>
              
              <!-- Enhanced Stats Grid with Arabic support -->
              <div class="grid grid-cols-2 gap-4 mb-6">
                <div class="white-stat-item growth-stat-item text-center p-4 rounded-xl transition-all duration-300 hover:scale-105">
                  <span class="growth-stat-value-white block text-2xl font-black text-emerald-600">{getText('marketGrowth.stats.growthRate.value')}</span>
                  <span class="growth-stat-label-white block text-xs font-medium text-slate-600">{getText('marketGrowth.stats.growthRate.label')}</span>
                </div>
                <div class="white-stat-item growth-stat-item text-center p-4 rounded-xl transition-all duration-300 hover:scale-105">
                  <span class="growth-stat-value-white block text-2xl font-black text-blue-600">{getText('marketGrowth.stats.volume.value')}</span>
                  <span class="growth-stat-label-white block text-xs font-medium text-slate-600">{getText('marketGrowth.stats.volume.label')}</span>
               </div>
             </div>
             
             <!-- Enhanced Additional metrics with Arabic support -->
             <div class="space-y-4">
               {#each getText('marketGrowth.metrics') as metric, index}
                 <div class="white-metric-row flex justify-between items-center p-2 rounded-lg transition-all duration-300 hover:bg-slate-50 {isRTL ? 'flex-row-reverse' : ''}">
                   <span class="growth-metric-label-white text-sm font-medium text-slate-700 {isRTL ? 'text-right' : 'text-left'}">{metric.label}</span>
                   <span class="growth-metric-value-white text-sm font-bold {index === 0 ? 'text-emerald-600' : index === 1 ? 'text-blue-600' : 'text-purple-600'}">{metric.value}</span>
                 </div>
               {/each}
             </div>

             <!-- Clean overlay effect -->
             <div class="white-overlay absolute inset-0 rounded-3xl bg-gradient-to-br from-white/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700 pointer-events-none"></div>
           </div>
         {/if}
       </div>
     </div>
   {/if}
 </div>
</section>

<style>
 /* Clean White Hero Section Background */
 .hero-section-white {
   background: #ffffff;
   position: relative;
 }

 /* Main Gradient Background - White to Purple (matching reference image) */
 .gradient-bg-white {
   background: transparent;
 }

 .main-gradient {
   position: absolute;
   inset: 0;
   background: linear-gradient(180deg, 
     #ffffff 0%,
     #ffffff 20%, 
     #faf8ff 40%,
     #f3f0ff 60%,
     #e8e3ff 80%,
     #d8cfff 90%,
     #c7b9ff 100%
   );
   opacity: 1;
 }

 /* Floating Geometric Elements (like in reference image) */
 .floating-elements {
   position: absolute;
   inset: 0;
   pointer-events: none;
   opacity: 0.6;
 }

 .element {
   position: absolute;
   border-radius: 50%;
   background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(59, 130, 246, 0.05) 100%);
   animation: float-element 20s ease-in-out infinite;
 }

 .element-1 {
   width: 120px;
   height: 120px;
   top: 15%;
   left: 10%;
   background: linear-gradient(135deg, rgba(139, 92, 246, 0.08) 0%, transparent 70%);
   animation-delay: 0s;
 }

 .element-2 {
   width: 80px;
   height: 80px;
   top: 25%;
   right: 15%;
   background: linear-gradient(135deg, rgba(59, 130, 246, 0.06) 0%, transparent 70%);
   animation-delay: -3s;
 }

 .element-3 {
   width: 150px;
   height: 150px;
   top: 45%;
   left: 5%;
   background: linear-gradient(135deg, rgba(6, 182, 212, 0.05) 0%, transparent 70%);
   animation-delay: -6s;
 }

 .element-4 {
   width: 100px;
   height: 100px;
   top: 65%;
   right: 25%;
   background: linear-gradient(135deg, rgba(139, 92, 246, 0.07) 0%, transparent 70%);
   animation-delay: -9s;
 }

 .element-5 {
   width: 60px;
   height: 60px;
   top: 35%;
   left: 35%;
   background: linear-gradient(135deg, rgba(99, 102, 241, 0.06) 0%, transparent 70%);
   animation-delay: -12s;
 }

 .element-6 {
   width: 200px;
   height: 200px;
   bottom: 20%;
   right: 10%;
   background: linear-gradient(135deg, rgba(59, 130, 246, 0.04) 0%, transparent 70%);
   animation-delay: -15s;
 }

 .element-7 {
   width: 90px;
   height: 90px;
   bottom: 35%;
   left: 25%;
   background: linear-gradient(135deg, rgba(6, 182, 212, 0.06) 0%, transparent 70%);
   animation-delay: -18s;
 }

 .element-8 {
   width: 110px;
   height: 110px;
   top: 55%;
   right: 45%;
   background: linear-gradient(135deg, rgba(139, 92, 246, 0.05) 0%, transparent 70%);
   animation-delay: -21s;
 }

 @keyframes float-element {
   0%, 100% { 
     transform: translate(0, 0) rotate(0deg) scale(1); 
     opacity: 0.6;
   }
   25% { 
     transform: translate(20px, -15px) rotate(90deg) scale(1.1); 
     opacity: 0.4;
   }
   50% { 
     transform: translate(-10px, -25px) rotate(180deg) scale(0.9); 
     opacity: 0.8;
   }
   75% { 
     transform: translate(-25px, 10px) rotate(270deg) scale(1.05); 
     opacity: 0.5;
   }
 }

 /* Custom Typography System */
 
 /* Title Styles - English */
 .hero-title-en {
   font-family: 'JosefinSans-BoldItalic', 'Josefin Sans', serif;
   font-weight: 800;
   font-style: italic;
   letter-spacing: -0.025em;
   line-height: 1.1;
   color: #0f172a;
   text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
 }

 /* Title Styles - Arabic */
 .hero-title-ar {
   font-family: 'VLAX', 'Cairo', 'Amiri', 'Noto Sans Arabic', serif;
   font-weight: 900;
   letter-spacing: 0;
   line-height: 1.1;
   color: #0f172a;
   text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
 }

 /* Responsive Title Sizes */
 .hero-title {
   font-size: 2.25rem; /* 4xl - xs */
 }

 @media (min-width: 640px) {
   .hero-title {
     font-size: 3rem; /* 5xl - sm */
   }
 }

 @media (min-width: 768px) {
   .hero-title {
     font-size: 3.75rem; /* 6xl - md */
   }
 }

 @media (min-width: 1024px) {
   .hero-title {
     font-size: 4.5rem; /* 7xl - lg */
   }
 }

 @media (min-width: 1280px) {
   .hero-title {
     font-size: 6rem; /* 8xl - xl */
   }
 }

 /* Paragraph Styles */
 .hero-paragraph {
   font-size: 1rem; /* base - xs */
   line-height: 1.625; /* relaxed */
   max-width: 65ch;
   color: #64748b;
   text-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
 }

 @media (min-width: 640px) {
   .hero-paragraph {
     font-size: 1.125rem; /* lg - sm and up */
   }
 }

 @media (min-width: 768px) {
   .hero-paragraph {
     font-size: 1.125rem; /* lg - md */
   }
 }

 @media (min-width: 1024px) {
   .hero-paragraph {
     font-size: 1.125rem; /* lg - lg */
   }
 }

 @media (min-width: 1280px) {
   .hero-paragraph {
     font-size: 1.125rem; /* lg - xl */
   }
 }

 /* Dark Mode Typography */
 :global(.dark) .hero-title-en,
 :global(.dark) .hero-title-ar {
   color: #f8fafc;
   text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
 }

 :global(.dark) .hero-paragraph {
   color: #cbd5e1;
   text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
 }

 /* Clean White Status Badge */
 .white-badge {
   background: rgba(255, 255, 255, 0.9);
   backdrop-filter: blur(12px);
   -webkit-backdrop-filter: blur(12px);
   border: 1px solid rgba(139, 92, 246, 0.2);
   box-shadow: 0 4px 20px rgba(139, 92, 246, 0.1),
               inset 0 1px 0 rgba(255, 255, 255, 0.8);
 }

 .white-badge:hover {
   background: rgba(255, 255, 255, 0.95);
   border-color: rgba(139, 92, 246, 0.3);
   box-shadow: 0 8px 30px rgba(139, 92, 246, 0.15),
               inset 0 1px 0 rgba(255, 255, 255, 0.9);
 }

 :global(.dark) .white-badge {
   background: rgba(15, 23, 42, 0.9);
   border-color: rgba(167, 139, 250, 0.3);
   box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2),
               inset 0 1px 0 rgba(255, 255, 255, 0.1);
 }

 :global(.dark) .white-badge:hover {
   background: rgba(15, 23, 42, 0.95);
   border-color: rgba(167, 139, 250, 0.4);
 }

 .pulse-glow-white {
   animation: pulse-glow-white 2s ease-in-out infinite;
   box-shadow: 0 0 8px rgba(52, 211, 153, 0.4);
 }

 @keyframes pulse-glow-white {
   0%, 100% { 
     opacity: 1; 
     box-shadow: 0 0 8px rgba(52, 211, 153, 0.4);
   }
   50% { 
     opacity: 0.8; 
     box-shadow: 0 0 15px rgba(52, 211, 153, 0.6);
   }
 }

 .white-divider {
   background: linear-gradient(to bottom, transparent, rgba(148, 163, 184, 0.3), transparent);
 }

 :global(.dark) .white-divider {
   background: linear-gradient(to bottom, transparent, rgba(71, 85, 105, 0.5), transparent);
 }

 /* Clean White Buttons */
 .white-button-wrapper {
   position: relative;
 }

 .white-button-primary {
   background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%) !important;
   border: none !important;
   box-shadow: 0 4px 20px rgba(139, 92, 246, 0.25) !important;
   color: white !important;
   font-weight: 600 !important;
 }

 .white-button-primary:hover {
   background: linear-gradient(135deg, #7c3aed 0%, #5b21b6 100%) !important;
   box-shadow: 0 8px 30px rgba(139, 92, 246, 0.35) !important;
   transform: translateY(-2px) !important;
 }

 .white-button-secondary {
   background: white !important;
   border: 1px solid #e2e8f0 !important;
   box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05) !important;
   color: #475569 !important;
   font-weight: 600 !important;
 }

 .white-button-secondary:hover {
   background: #f8fafc !important;
   border-color: #cbd5e1 !important;
   box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1) !important;
   transform: translateY(-1px) !important;
 }

 /* Clean White Metric Cards */
 .white-metric-card {
   background: rgba(255, 255, 255, 0.9);
   backdrop-filter: blur(8px);
   -webkit-backdrop-filter: blur(8px);
   border: 1px solid rgba(139, 92, 246, 0.1);
   box-shadow: 0 4px 20px rgba(139, 92, 246, 0.05),
               inset 0 1px 0 rgba(255, 255, 255, 0.8);
   position: relative;
   overflow: hidden;
 }

 .white-metric-card:hover {
   background: rgba(255, 255, 255, 0.95);
   border-color: rgba(139, 92, 246, 0.2);
   box-shadow: 0 8px 30px rgba(139, 92, 246, 0.1),
               inset 0 1px 0 rgba(255, 255, 255, 0.9);
 }

 :global(.dark) .white-metric-card {
   background: rgba(30, 41, 59, 0.9);
   border-color: rgba(167, 139, 250, 0.2);
   box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2),
               inset 0 1px 0 rgba(255, 255, 255, 0.05);
 }

 :global(.dark) .white-metric-card:hover {
   background: rgba(30, 41, 59, 0.95);
   border-color: rgba(167, 139, 250, 0.3);
 }

 .metric-value-white {
   color: #1e293b;
   filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.05));
 }

 .metric-label-white {
   color: #64748b;
   text-transform: uppercase;
   letter-spacing: 0.05em;
 }

 :global(.dark) .metric-value-white {
   color: #f8fafc;
 }

 :global(.dark) .metric-label-white {
   color: #94a3b8;
 }

 .metric-glow-white {
   pointer-events: none;
 }

 /* Enhanced White Market Growth Card with spacing */
 .white-market-card {
   background: rgba(255, 255, 255, 0.95);
   backdrop-filter: blur(12px);
   -webkit-backdrop-filter: blur(12px);
   border: 1px solid rgba(139, 92, 246, 0.15);
   box-shadow: 0 8px 30px rgba(139, 92, 246, 0.08),
               inset 0 1px 0 rgba(255, 255, 255, 0.9);
   position: relative;
   overflow: hidden;
 }

 .white-market-card:hover {
   box-shadow: 0 12px 40px rgba(139, 92, 246, 0.12),
               inset 0 1px 0 rgba(255, 255, 255, 0.95);
 }

 :global(.dark) .white-market-card {
   background: rgba(15, 23, 42, 0.95);
   border-color: rgba(167, 139, 250, 0.2);
   box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3),
               inset 0 1px 0 rgba(255, 255, 255, 0.1);
 }

 .market-growth-title-white {
   color: #1e293b;
   filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.05));
 }

 :global(.dark) .market-growth-title-white {
   color: #f8fafc;
 }

 .white-status-pill {
   background: rgba(255, 255, 255, 0.8);
   backdrop-filter: blur(6px);
   border: 1px solid rgba(139, 92, 246, 0.1);
 }

 :global(.dark) .white-status-pill {
   background: rgba(0, 0, 0, 0.2);
   border-color: rgba(255, 255, 255, 0.05);
 }

 .market-growth-period-white {
   color: #64748b;
 }

 :global(.dark) .market-growth-period-white {
   color: #94a3b8;
 }

 .white-chart-container {
   background: rgba(248, 250, 252, 0.8);
   backdrop-filter: blur(4px);
   border: 1px solid rgba(226, 232, 240, 0.5);
 }

 :global(.dark) .white-chart-container {
   background: rgba(0, 0, 0, 0.2);
   border-color: rgba(255, 255, 255, 0.05);
 }

 .white-stat-item {
   background: rgba(255, 255, 255, 0.8);
   backdrop-filter: blur(6px);
   border: 1px solid rgba(139, 92, 246, 0.1);
 }

 .white-stat-item:hover {
   background: rgba(255, 255, 255, 0.9);
   border-color: rgba(139, 92, 246, 0.2);
 }

 :global(.dark) .white-stat-item {
   background: rgba(0, 0, 0, 0.2);
   border-color: rgba(255, 255, 255, 0.05);
 }

 :global(.dark) .white-stat-item:hover {
   background: rgba(0, 0, 0, 0.3);
   border-color: rgba(255, 255, 255, 0.1);
 }

 .growth-stat-value-white {
   filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.05));
 }

 .growth-stat-label-white {
   color: #64748b;
   text-transform: uppercase;
   letter-spacing: 0.05em;
 }

 :global(.dark) .growth-stat-label-white {
   color: #94a3b8;
 }

 .white-metric-row {
   transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
 }

 .white-metric-row:hover {
   background: rgba(248, 250, 252, 0.8) !important;
 }

 :global(.dark) .white-metric-row:hover {
   background: rgba(255, 255, 255, 0.05) !important;
 }

 .growth-metric-label-white {
   color: #475569;
 }

 :global(.dark) .growth-metric-label-white {
   color: #cbd5e1;
 }

 .growth-metric-value-white {
   filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.05));
 }

 .white-overlay {
   background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, transparent 50%, rgba(139, 92, 246, 0.02) 100%);
 }

 /* Enhanced SVG Elements for White Theme */
 .svg-enhanced {
   filter: drop-shadow(0 2px 8px rgba(139, 92, 246, 0.05));
 }

 .buildings-group {
   animation: buildings-float-white 12s ease-in-out infinite;
 }

 @keyframes buildings-float-white {
   0%, 100% { transform: translateY(0px); }
   50% { transform: translateY(-3px); }
 }

 .building-element {
   transition: all 0.3s ease;
   filter: drop-shadow(0 1px 4px rgba(139, 92, 246, 0.08));
 }

 .window-glow-white {
   animation: window-glow-white 4s ease-in-out infinite alternate;
 }

 @keyframes window-glow-white {
   0% { opacity: 0.8; }
   100% { opacity: 1; filter: drop-shadow(0 0 3px rgba(251, 191, 36, 0.6)); }
 }

 .glass-panel-white {
   animation: glass-shimmer-white 5s ease-in-out infinite;
 }

 @keyframes glass-shimmer-white {
   0%, 100% { opacity: 0.3; }
   50% { opacity: 0.5; }
 }

 .growth-curves {
   animation: curves-flow-white 15s ease-in-out infinite;
 }

 @keyframes curves-flow-white {
   0%, 100% { transform: translateX(0px); }
   50% { transform: translateX(3px); }
 }

 .growth-curve {
   filter: drop-shadow(0 1px 4px rgba(139, 92, 246, 0.15));
   animation: curve-glow-white 8s ease-in-out infinite;
 }

 @keyframes curve-glow-white {
   0%, 100% { opacity: 1; }
   50% { opacity: 0.8; filter: drop-shadow(0 1px 6px rgba(139, 92, 246, 0.2)); }
 }

 .data-points {
   animation: points-bounce-white 6s ease-in-out infinite;
 }

 .data-point {
   filter: drop-shadow(0 1px 3px rgba(139, 92, 246, 0.15));
   animation: point-pulse-white 4s ease-in-out infinite;
 }

 @keyframes point-pulse-white {
   0%, 100% { transform: scale(1); opacity: 1; }
   50% { transform: scale(1.1); opacity: 0.8; }
 }

 /* Enhanced Chart Elements for White Theme */
 .chart-area-white {
   filter: drop-shadow(0 2px 6px rgba(139, 92, 246, 0.1));
   animation: area-pulse-white 6s ease-in-out infinite;
 }

 @keyframes area-pulse-white {
   0%, 100% { opacity: 0.3; }
   50% { opacity: 0.5; }
 }

 .chart-line-white {
   filter: drop-shadow(0 1px 4px rgba(139, 92, 246, 0.2));
   animation: line-draw-white 8s ease-in-out infinite;
   stroke-dasharray: 1000;
   stroke-dashoffset: 1000;
 }

 @keyframes line-draw-white {
   0% { stroke-dashoffset: 1000; }
   50%, 100% { stroke-dashoffset: 0; }
 }

 .chart-point-white {
   filter: drop-shadow(0 1px 3px rgba(139, 92, 246, 0.15));
   animation: chart-point-bounce-white 3s ease-in-out infinite;
 }

 @keyframes chart-point-bounce-white {
   0%, 100% { transform: scale(1) translateY(0); }
   50% { transform: scale(1.05) translateY(-1px); }
 }

 /* White Shadow Utilities */
 .shadow-white-lg {
   box-shadow: 0 8px 25px rgba(139, 92, 246, 0.1),
               inset 0 1px 0 rgba(255, 255, 255, 0.8);
 }

 .shadow-white-xl {
   box-shadow: 0 12px 35px rgba(139, 92, 246, 0.12),
               inset 0 1px 0 rgba(255, 255, 255, 0.9);
 }

 .shadow-white-2xl {
   box-shadow: 0 20px 50px rgba(139, 92, 246, 0.15),
               inset 0 2px 0 rgba(255, 255, 255, 0.95);
 }

 /* RTL Support for Arabic */
 :global([dir="rtl"]) .hero-title {
   text-align: right;
 }

 :global([dir="rtl"]) .hero-paragraph {
   text-align: right;
 }

 :global([dir="rtl"]) .hero-title-ar {
   font-family: 'VLAX', 'Cairo', 'Amiri', 'Noto Sans Arabic', 'Tajawal', system-ui, sans-serif;
   font-weight: 900;
   letter-spacing: 0;
   line-height: 1.1;
 }

 /* Enhanced Arabic Typography */
 @media screen and (min-width: 640px) {
   :global([dir="rtl"]) .hero-title-ar {
     font-size: 1.1em;
     line-height: 1.05;
   }
 }

 @media screen and (min-width: 768px) {
   :global([dir="rtl"]) .hero-title-ar {
     font-size: 1.05em;
   }
 }

 @media screen and (min-width: 1024px) {
   :global([dir="rtl"]) .hero-title-ar {
     font-size: 1.02em;
   }
 }

 /* Reduced Motion Support */
 @media (prefers-reduced-motion: reduce) {
   .building-element,
   .growth-curve,
   .data-point,
   .chart-line-white,
   .chart-point-white,
   .chart-area-white,
   .window-glow-white,
   .glass-panel-white,
   .buildings-group,
   .growth-curves,
   .data-points,
   .pulse-glow-white,
   .floating-elements .element {
     animation: none !important;
   }
 }

 /* Performance Optimizations */
 .hero-section-white,
 .white-badge,
 .white-metric-card,
 .white-market-card,
 .building-element,
 .growth-curve,
 .data-point,
 .chart-line-white,
 .chart-point-white,
 .chart-area-white {
   will-change: transform, opacity;
   transform: translateZ(0);
   contain: layout style paint;
 }

 /* Smooth font rendering */
 .hero-title-en,
 .hero-title-ar,
 .hero-paragraph {
   -webkit-font-smoothing: antialiased;
   -moz-osx-font-smoothing: grayscale;
   text-rendering: optimizeLegibility;
 }

 /* Ensure seamless integration with navbar */
 .hero-section-white {
   margin-top: 0;
   padding-top: 80px; /* Adjust based on your navbar height */
 }

 /* Remove any potential gaps */
 .hero-section-white::before {
   display: none;
 }

 /* Ensure consistent white background continues to navbar area */
 body {
   background-color: #ffffff;
 }

 /* High Contrast Mode Support */
 @media (prefers-contrast: high) {
   .hero-section-white {
     background: #ffffff;
   }

   :global(.dark) .hero-section-white {
     background: #000000;
   }

   .hero-title-en,
   .hero-title-ar {
     color: #000000 !important;
   }

   :global(.dark) .hero-title-en,
   :global(.dark) .hero-title-ar {
     color: #ffffff !important;
   }

   .hero-paragraph {
     color: #333333 !important;
   }

   :global(.dark) .hero-paragraph {
     color: #cccccc !important;
   }
 }
</style>