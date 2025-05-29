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
  
  // Simplified translations with fewer text elements
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
      ]
    },
    ar: {
      badge: {
        live: 'مباشر الآن',
        count: '24 نشط'
      },
      headline: ' اكشن',
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
      ]
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
  });
</script>

<svelte:head>
  <title>Premier Real Estate Auctions | Find Your Perfect Property</title>
  <meta name="description" content="Discover exclusive properties through transparent auctions. Join thousands of satisfied buyers in finding their dream properties.">
</svelte:head>

<svelte:window bind:scrollY />

<!-- F-Layout Hero Section with Tailwind -->
<section class="hero-section relative min-h-screen flex items-center overflow-hidden py-32 pb-16 bg-transparent z-10" aria-label="Hero section">
  
  <!-- Enhanced Dynamic SVG Background - Center Right -->
  <div class="absolute top-1/2 w-[70%] h-[90%] z-0 overflow-visible opacity-40 {isRTL ? 'left-0' : 'right-0'} -translate-y-1/2" aria-hidden="true">
    <svg class="w-full h-full animate-pulse rtl:scale-x-[-1]" viewBox="0 0 1200 800" fill="none" xmlns="http://www.w3.org/2000/svg">

      <!-- Enhanced animated building outlines -->
      <g class="animate-bounce" style="animation-duration: 12s;">
        <!-- Building 1 - Modern Skyscraper -->
        <path class="building-element animate-pulse" style="animation-delay: 0s; animation-duration: 8s;" d="M500 700 L500 150 L580 130 L580 700 Z" stroke="url(#gradient1)" stroke-width="3" fill="url(#buildingFill1)"/>
        <path d="M500 150 L540 120 L580 130 Z" stroke="url(#gradient1)" stroke-width="2" fill="url(#accent1)"/>
        <!-- Windows -->
        <rect x="520" y="180" width="12" height="16" fill="url(#windowGlow)" rx="2"/>
        <rect x="540" y="200" width="12" height="16" fill="url(#windowGlow)" rx="2"/>
        <rect x="520" y="240" width="12" height="16" fill="url(#windowGlow)" rx="2"/>
        <rect x="540" y="260" width="12" height="16" fill="url(#windowGlow)" rx="2"/>
        
        <!-- Building 2 - Corporate Tower -->
        <path class="building-element animate-pulse" style="animation-delay: 1.5s; animation-duration: 8s;" d="M620 700 L620 100 L720 80 L720 700 Z" stroke="url(#gradient2)" stroke-width="3" fill="url(#buildingFill2)"/>
        <path d="M620 100 L670 60 L720 80 Z" stroke="url(#gradient2)" stroke-width="2" fill="url(#accent2)"/>
        <!-- Glass facade -->
        <rect x="640" y="120" width="60" height="200" fill="url(#glassFacade)" opacity="0.6" rx="4"/>
        
        <!-- Building 3 - Residential Complex -->
        <path class="building-element animate-pulse" style="animation-delay: 3s; animation-duration: 8s;" d="M750 700 L750 200 L880 180 L880 700 Z" stroke="url(#gradient3)" stroke-width="3" fill="url(#buildingFill3)"/>
        <path d="M750 200 L815 160 L880 180 Z" stroke="url(#gradient3)" stroke-width="2" fill="url(#accent3)"/>
        
        <!-- Building 4 - Mixed Use -->
        <path class="building-element animate-pulse" style="animation-delay: 4.5s; animation-duration: 8s;" d="M900 700 L900 250 L1020 230 L1020 700 Z" stroke="url(#gradient4)" stroke-width="3" fill="url(#buildingFill4)"/>
        
        <!-- Building 5 - Luxury Towers -->
        <path class="building-element animate-pulse" style="animation-delay: 6s; animation-duration: 8s;" d="M1050 700 L1050 120 L1150 100 L1150 700 Z" stroke="url(#gradient1)" stroke-width="3" fill="url(#buildingFill1)"/>
        <path d="M1050 120 L1100 80 L1150 100 Z" stroke="url(#gradient1)" stroke-width="2" fill="url(#accent1)"/>
      </g>
      
      <!-- Enhanced fluid growth curves -->
      <g class="animate-pulse" style="animation-duration: 15s;">
        <path class="growth-curve animate-pulse" style="animation-delay: 0s; animation-duration: 10s;" d="M375 600 Q575 450 775 380 Q975 310 1175 250" stroke="url(#growthGradient)" stroke-width="4" fill="none"/>
        <path class="growth-curve animate-pulse" style="animation-delay: 2s; animation-duration: 10s;" d="M425 650 Q625 500 825 430 Q1025 360 1225 300" stroke="url(#growthGradient2)" stroke-width="3" fill="none"/>
        <path class="growth-curve animate-pulse" style="animation-delay: 4s; animation-duration: 10s;" d="M475 680 Q675 530 875 460 Q1075 390 1275 330" stroke="url(#growthGradient3)" stroke-width="2" fill="none"/>
      </g>
      
      <!-- Enhanced floating data points -->
      <g class="animate-bounce" style="animation-duration: 6s;">
        <circle class="data-point animate-ping" style="animation-delay: 0s; animation-duration: 4s;" cx="675" cy="400" r="6" fill="url(#accent1)"/>
        <circle class="data-point animate-ping" style="animation-delay: 1s; animation-duration: 4s;" cx="875" cy="350" r="5" fill="url(#accent2)"/>
        <circle class="data-point animate-ping" style="animation-delay: 2s; animation-duration: 4s;" cx="1075" cy="300" r="7" fill="url(#accent3)"/>
        <circle class="data-point animate-ping" style="animation-delay: 0.5s; animation-duration: 4s;" cx="775" cy="380" r="4" fill="url(#accent4)"/>
        <circle class="data-point animate-ping" style="animation-delay: 1.5s; animation-duration: 4s;" cx="975" cy="320" r="5" fill="url(#accent1)"/>
      </g>
      
      <!-- Enhanced gradient definitions -->
      <defs>
        <linearGradient id="gradient1" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" class="stop-primary-light"/>
          <stop offset="100%" class="stop-primary-dark"/>
        </linearGradient>
        <linearGradient id="gradient2" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" class="stop-secondary-light"/>
          <stop offset="100%" class="stop-secondary-dark"/>
        </linearGradient>
        <linearGradient id="gradient3" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" class="stop-accent-light"/>
          <stop offset="100%" class="stop-accent-dark"/>
        </linearGradient>
        <linearGradient id="gradient4" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" class="stop-tertiary-light"/>
          <stop offset="100%" class="stop-tertiary-dark"/>
        </linearGradient>
        <linearGradient id="growthGradient" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" class="stop-growth-start"/>
          <stop offset="50%" class="stop-growth-mid"/>
          <stop offset="100%" class="stop-growth-end"/>
        </linearGradient>
        <linearGradient id="growthGradient2" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" class="stop-growth2-start"/>
          <stop offset="100%" class="stop-growth2-end"/>
        </linearGradient>
        <linearGradient id="growthGradient3" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" class="stop-growth3-start"/>
          <stop offset="100%" class="stop-growth3-end"/>
        </linearGradient>
        <radialGradient id="buildingFill1" cx="50%" cy="50%" r="70%">
          <stop offset="0%" class="stop-building-fill-light"/>
          <stop offset="100%" class="stop-building-fill-dark"/>
        </radialGradient>
        <radialGradient id="buildingFill2" cx="50%" cy="50%" r="70%">
          <stop offset="0%" class="stop-building2-fill-light"/>
          <stop offset="100%" class="stop-building2-fill-dark"/>
        </radialGradient>
        <radialGradient id="buildingFill3" cx="50%" cy="50%" r="70%">
          <stop offset="0%" class="stop-building3-fill-light"/>
          <stop offset="100%" class="stop-building3-fill-dark"/>
        </radialGradient>
        <radialGradient id="buildingFill4" cx="50%" cy="50%" r="70%">
          <stop offset="0%" class="stop-building4-fill-light"/>
          <stop offset="100%" class="stop-building4-fill-dark"/>
        </radialGradient>
        <radialGradient id="accent1" cx="50%" cy="50%" r="60%">
          <stop offset="0%" class="stop-accent1-light"/>
          <stop offset="100%" class="stop-accent1-dark"/>
        </radialGradient>
        <radialGradient id="accent2" cx="50%" cy="50%" r="60%">
          <stop offset="0%" class="stop-accent2-light"/>
          <stop offset="100%" class="stop-accent2-dark"/>
        </radialGradient>
        <radialGradient id="accent3" cx="50%" cy="50%" r="60%">
          <stop offset="0%" class="stop-accent3-light"/>
          <stop offset="100%" class="stop-accent3-dark"/>
        </radialGradient>
        <radialGradient id="accent4" cx="50%" cy="50%" r="60%">
          <stop offset="0%" class="stop-accent4-light"/>
          <stop offset="100%" class="stop-accent4-dark"/>
        </radialGradient>
        <linearGradient id="windowGlow" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" class="stop-window-light"/>
          <stop offset="100%" class="stop-window-dark"/>
        </linearGradient>
        <linearGradient id="glassFacade" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" class="stop-glass-light"/>
          <stop offset="100%" class="stop-glass-dark"/>
        </linearGradient>
      </defs>
    </svg>
  </div>

  <!-- F-Layout Container -->
  <div class="relative z-10 w-full max-w-7xl mx-auto px-4 sm:px-6 md:px-8 lg:px-12 xl:px-16">
    {#if mounted}
      <!-- F-Layout: Top horizontal bar - Status badge -->
      <div class="flex justify-start mb-12">
        <div 
          in:fade={{ duration: 400, delay: 100, easing: cubicOut }}
          class="status-badge inline-flex items-center gap-3 px-6 py-3.5 rounded-full text-sm font-semibold backdrop-blur-sm transition-all duration-300 hover:-translate-y-0.5 hover:shadow-lg"
          role="status"
          aria-live="polite"
        >
          <span class="w-2.5 h-2.5 bg-emerald-500 rounded-full animate-pulse" aria-hidden="true"></span>
          <span class="text-blue-600 font-bold">{getText('badge.live')}</span>
          <span class="text-slate-600 text-xs font-medium">{getText('badge.count')}</span>
        </div>
      </div>

      <!-- F-Layout: Main content grid -->
      <div class="grid grid-cols-1 lg:grid-cols-5 gap-16 lg:gap-24 items-start">
        
        <!-- Left column: Primary F-pattern content (wider - 3/5 of space) -->
        <div class="lg:col-span-3 space-y-8">
          
          <!-- Main headline - Enhanced for Arabic -->
          <div class="max-w-4xl">
            <h1 
              in:fly={{ y: prefersReducedMotion ? 0 : 32, duration: 600, delay: 200, easing: cubicOut }}
              class="headline text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-black leading-[0.9] tracking-tight {isRTL ? 'text-right font-arabic' : 'text-left'}"
            >
              <span class="headline-gradient block bg-gradient-to-r from-blue-600 via-purple-600 to-emerald-600 bg-clip-text text-transparent animate-pulse {isRTL ? 'text-6xl sm:text-8xl md:text-9xl lg:text-10xl w-full pb-4 mb-2' : ''}">
                {getText('headline')}
              </span>
            </h1>
          </div>
          
          <!-- Subheadline - Enhanced for Arabic -->
          <div class="{isRTL ? 'max-w-2xl' : 'max-w-3xl'}">
            <p 
              in:fly={{ y: prefersReducedMotion ? 0 : 24, duration: 600, delay: 300, easing: cubicOut }}
              class="subheadline text-xl sm:text-2xl leading-relaxed font-medium {isRTL ? 'text-right font-arabic' : 'text-left'}"
            >
              {getText('subheadline')}
            </p>
          </div>
          
          <!-- CTA buttons - positioned along F-pattern -->
          <div 
            in:fly={{ y: prefersReducedMotion ? 0 : 24, duration: 600, delay: 400, easing: cubicOut }}
            class="flex flex-col sm:flex-row gap-4 pt-4 {isRTL ? 'sm:flex-row-reverse justify-end' : ''}"
          >
            <Button 
              variant="primary" 
              size="small" 
              href="/auctions"
            >
              <span>{getText('cta.primary')}</span>
              <svg 
                class="w-4 h-4 transition-transform duration-200 group-hover:translate-x-0.5 {isRTL ? 'rotate-180' : ''}" 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
                aria-hidden="true"
                slot="iconRight"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </Button>

            <Button 
              variant="outline" 
              size="small" 
              href="/properties"
            >
              <span>{getText('cta.secondary')}</span>
            </Button>
          </div>

          <!-- Trust metrics - bottom of F-pattern -->
          <div 
            in:fade={{ duration: 600, delay: 500, easing: cubicOut }}
            class="grid grid-cols-2 sm:grid-cols-4 gap-6 pt-8"
            role="region"
            aria-label="Platform statistics"
          >
            {#each getText('metrics') as metric, index}
              <div 
                class="metric-card text-center p-6 rounded-2xl backdrop-blur-sm transition-all duration-300 hover:-translate-y-2 hover:shadow-lg" 
                in:scale={{ duration: 400, delay: 600 + (index * 100), easing: cubicOut }}
              >
                <span class="metric-value block text-2xl sm:text-3xl font-black leading-none">
                  {metric.value}
                </span>
                <span class="metric-label block text-sm font-medium mt-2">
                  {metric.label}
                </span>
              </div>
            {/each}
          </div>
        </div>

        <!-- Right column: Enhanced Market Growth Visualization -->
        <div class="lg:col-span-2 space-y-8">
          <!-- Advanced Market trend visualization -->
          <div 
            class="market-growth-card rounded-3xl p-8 backdrop-blur-2xl shadow-xl transition-all duration-300 hover:-translate-y-2 hover:shadow-2xl"
            in:fly={{ y: prefersReducedMotion ? 0 : 40, duration: 800, delay: 600, easing: cubicOut }}
          >
            <div class="flex justify-between items-center mb-8">
              <h3 class="market-growth-title text-xl font-bold">Market Growth</h3>
              <div class="flex items-center gap-2">
                <span class="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></span>
                <span class="market-growth-period text-sm font-medium">12 months</span>
              </div>
            </div>
            
            <!-- Enhanced Chart -->
            <div class="mb-8">
              <svg class="w-full h-32" viewBox="0 0 300 120" fill="none">
                <!-- Grid lines -->
                <defs>
                  <pattern id="grid" width="30" height="12" patternUnits="userSpaceOnUse">
                    <path d="m 30 0 l 0 12 m -30 0 l 30 0" stroke="url(#gridGradient)" stroke-width="0.5" opacity="0.3"/>
                  </pattern>
                  <linearGradient id="gridGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" class="stop-grid-light"/>
                    <stop offset="100%" class="stop-grid-dark"/>
                  </linearGradient>
                  <linearGradient id="mainChartGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" class="stop-chart-start"/>
                    <stop offset="30%" class="stop-chart-mid1"/>
                    <stop offset="70%" class="stop-chart-mid2"/>
                    <stop offset="100%" class="stop-chart-end"/>
                  </linearGradient>
                  <linearGradient id="areaGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" class="stop-area-top"/>
                    <stop offset="100%" class="stop-area-bottom"/>
                  </linearGradient>
                </defs>
                
                <!-- Grid -->
                <rect width="100%" height="100%" fill="url(#grid)"/>
                
                <!-- Area under curve -->
                <path class="animate-pulse chart-area" style="animation-duration: 4s;" d="M15 100 Q50 80 100 60 Q150 45 200 35 Q250 25 285 20 L285 100 Z" fill="url(#areaGradient)" opacity="0.3"/>
                
                <!-- Main trend line -->
                <path class="animate-pulse chart-line" style="animation-duration: 4s;" d="M15 100 Q50 80 100 60 Q150 45 200 35 Q250 25 285 20" stroke="url(#mainChartGradient)" stroke-width="3" fill="none"/>
                
                <!-- Data points -->
                <circle class="animate-bounce chart-point" style="animation-duration: 3s; animation-delay: 0s;" cx="50" cy="80" r="4" fill="url(#accent1)"/>
                <circle class="animate-bounce chart-point" style="animation-duration: 3s; animation-delay: 0.5s;" cx="100" cy="60" r="4" fill="url(#accent2)"/>
                <circle class="animate-bounce chart-point" style="animation-duration: 3s; animation-delay: 1s;" cx="150" cy="45" r="4" fill="url(#accent3)"/>
                <circle class="animate-bounce chart-point" style="animation-duration: 3s; animation-delay: 1.5s;" cx="200" cy="35" r="5" fill="url(#accent1)"/>
                <circle class="animate-bounce chart-point" style="animation-duration: 3s; animation-delay: 2s;" cx="250" cy="25" r="5" fill="url(#accent4)"/>
                
                <!-- Trend indicators -->
                <path d="M270 30 L280 20 L275 20 L275 15 M280 20 L275 25" stroke="url(#accent4)" stroke-width="2" fill="none"/>
              </svg>
            </div>
            
            <!-- Stats Grid -->
            <div class="grid grid-cols-2 gap-4 mb-6">
              <div class="growth-stat-item text-center p-4 rounded-xl backdrop-blur-sm">
                <span class="growth-stat-value block text-2xl font-black text-emerald-600">+24.5%</span>
                <span class="growth-stat-label block text-xs font-medium">Growth Rate</span>
              </div>
              <div class="growth-stat-item text-center p-4 rounded-xl backdrop-blur-sm">
                <span class="growth-stat-value block text-2xl font-black text-blue-600">$3.2M</span>
                <span class="growth-stat-label block text-xs font-medium">Volume</span>
              </div>
            </div>
            
            <!-- Additional metrics -->
            <div class="space-y-3">
              <div class="flex justify-between items-center">
                <span class="growth-metric-label text-sm font-medium">Properties Sold</span>
                <span class="growth-metric-value text-sm font-bold text-emerald-600">+18.2%</span>
              </div>
              <div class="flex justify-between items-center">
                <span class="growth-metric-label text-sm font-medium">Average Price</span>
                <span class="growth-metric-value text-sm font-bold text-blue-600">+12.8%</span>
              </div>
              <div class="flex justify-between items-center">
                <span class="growth-metric-label text-sm font-medium">Market Activity</span>
                <span class="growth-metric-value text-sm font-bold text-purple-600">+31.5%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    {/if}
  </div>
</section>

<style>
  /* Hero Section - transparent background */
  .hero-section {
    background: transparent;
  }

  /* Status Badge */
  .status-badge {
    background: rgba(59, 130, 246, 0.08);
    border: 1px solid rgba(59, 130, 246, 0.2);
  }

  .status-badge:hover {
    background: rgba(59, 130, 246, 0.12);
    box-shadow: 0 10px 25px -5px rgba(59, 130, 246, 0.1);
  }

  :global(.dark) .status-badge {
    background: rgba(59, 130, 246, 0.15);
    border-color: rgba(59, 130, 246, 0.3);
  }

  /* Typography */
  .headline {
    color: #0f172a;
  }

  :global(.dark) .headline {
    color: #f8fafc;
  }

  .subheadline {
    color: #475569;
  }

  :global(.dark) .subheadline {
    color: #cbd5e1;
  }

  /* Enhanced Arabic Font Support */
  .font-arabic {
    font-family: 'Cairo', 'Amiri', 'Noto Sans Arabic', system-ui, sans-serif;
    font-weight: 900;
    letter-spacing: -0.02em;
  }

  /* Metric Cards */
  .metric-card {
    background: rgba(255, 255, 255, 0.7);
    border: 1px solid rgba(226, 232, 240, 0.5);
  }

  .metric-card:hover {
    border-color: rgba(59, 130, 246, 0.3);
    box-shadow: 0 10px 25px -5px rgba(226, 232, 240, 0.5);
  }

  :global(.dark) .metric-card {
    background: rgba(30, 41, 59, 0.7);
    border-color: rgba(71, 85, 105, 0.5);
  }

  :global(.dark) .metric-card:hover {
    box-shadow: 0 10px 25px -5px rgba(30, 41, 59, 0.5);
  }

  .metric-value {
    color: #0f172a;
  }

  :global(.dark) .metric-value {
    color: #f8fafc;
  }

  .metric-label {
    color: #475569;
  }

  :global(.dark) .metric-label {
    color: #94a3b8;
  }

  /* Market Growth Card */
  .market-growth-card {
    background: rgba(255, 255, 255, 0.95);
    border: 1px solid rgba(226, 232, 240, 0.8);
    box-shadow: 0 25px 50px -12px rgba(226, 232, 240, 0.2);
  }

  :global(.dark) .market-growth-card {
    background: rgba(30, 41, 59, 0.95);
    border-color: rgba(71, 85, 105, 0.8);
    box-shadow: 0 25px 50px -12px rgba(15, 23, 42, 0.2);
  }

  .market-growth-title {
    color: #0f172a;
  }

  :global(.dark) .market-growth-title {
    color: #f8fafc;
  }

  .market-growth-period {
    color: #475569;
  }

  :global(.dark) .market-growth-period {
    color: #94a3b8;
  }

  /* Growth Stats */
  .growth-stat-item {
    background: rgba(248, 250, 252, 0.8);
    border: 1px solid rgba(226, 232, 240, 0.3);
  }

  :global(.dark) .growth-stat-item {
    background: rgba(15, 23, 42, 0.8);
    border-color: rgba(71, 85, 105, 0.3);
  }

  .growth-stat-label {
    color: #64748b;
  }

  :global(.dark) .growth-stat-label {
    color: #94a3b8;
  }

  .growth-metric-label {
    color: #475569;
  }

  :global(.dark) .growth-metric-label {
   color: #cbd5e1;
 }

 /* SVG Elements - Light Mode */
 .stop-primary-light {
   stop-color: #3b82f6;
   stop-opacity: 1;
 }

 .stop-primary-dark {
   stop-color: #1d4ed8;
   stop-opacity: 1;
 }

 .stop-secondary-light {
   stop-color: #8b5cf6;
   stop-opacity: 1;
 }

 .stop-secondary-dark {
   stop-color: #7c3aed;
   stop-opacity: 1;
 }

 .stop-accent-light {
   stop-color: #10b981;
   stop-opacity: 1;
 }

 .stop-accent-dark {
   stop-color: #059669;
   stop-opacity: 1;
 }

 .stop-tertiary-light {
   stop-color: #f59e0b;
   stop-opacity: 1;
 }

 .stop-tertiary-dark {
   stop-color: #d97706;
   stop-opacity: 1;
 }

 .stop-growth-start {
   stop-color: #3b82f6;
   stop-opacity: 0.8;
 }

 .stop-growth-mid {
   stop-color: #8b5cf6;
   stop-opacity: 0.6;
 }

 .stop-growth-end {
   stop-color: #10b981;
   stop-opacity: 0.4;
 }

 .stop-growth2-start {
   stop-color: #f59e0b;
   stop-opacity: 0.6;
 }

 .stop-growth2-end {
   stop-color: #ef4444;
   stop-opacity: 0.4;
 }

 .stop-growth3-start {
   stop-color: #06b6d4;
   stop-opacity: 0.4;
 }

 .stop-growth3-end {
   stop-color: #8b5cf6;
   stop-opacity: 0.2;
 }

 .stop-building-fill-light {
   stop-color: #3b82f6;
   stop-opacity: 0.15;
 }

 .stop-building-fill-dark {
   stop-color: #1d4ed8;
   stop-opacity: 0.08;
 }

 .stop-building2-fill-light {
   stop-color: #8b5cf6;
   stop-opacity: 0.15;
 }

 .stop-building2-fill-dark {
   stop-color: #7c3aed;
   stop-opacity: 0.08;
 }

 .stop-building3-fill-light {
   stop-color: #10b981;
   stop-opacity: 0.15;
 }

 .stop-building3-fill-dark {
   stop-color: #059669;
   stop-opacity: 0.08;
 }

 .stop-building4-fill-light {
   stop-color: #f59e0b;
   stop-opacity: 0.15;
 }

 .stop-building4-fill-dark {
   stop-color: #d97706;
   stop-opacity: 0.08;
 }

 .stop-accent1-light {
   stop-color: #3b82f6;
   stop-opacity: 1;
 }

 .stop-accent1-dark {
   stop-color: #1d4ed8;
   stop-opacity: 0.8;
 }

 .stop-accent2-light {
   stop-color: #f59e0b;
   stop-opacity: 1;
 }

 .stop-accent2-dark {
   stop-color: #d97706;
   stop-opacity: 0.8;
 }

 .stop-accent3-light {
   stop-color: #10b981;
   stop-opacity: 1;
 }

 .stop-accent3-dark {
   stop-color: #059669;
   stop-opacity: 0.8;
 }

 .stop-accent4-light {
   stop-color: #8b5cf6;
   stop-opacity: 1;
 }

 .stop-accent4-dark {
   stop-color: #7c3aed;
   stop-opacity: 0.8;
 }

 .stop-window-light {
   stop-color: #fbbf24;
   stop-opacity: 0.9;
 }

 .stop-window-dark {
   stop-color: #f59e0b;
   stop-opacity: 0.7;
 }

 .stop-glass-light {
   stop-color: #60a5fa;
   stop-opacity: 0.3;
 }

 .stop-glass-dark {
   stop-color: #3b82f6;
   stop-opacity: 0.2;
 }

 .stop-grid-light {
   stop-color: #e2e8f0;
   stop-opacity: 0.5;
 }

 .stop-grid-dark {
   stop-color: #cbd5e1;
   stop-opacity: 0.3;
 }

 .stop-chart-start {
   stop-color: #3b82f6;
   stop-opacity: 1;
 }

 .stop-chart-mid1 {
   stop-color: #8b5cf6;
   stop-opacity: 0.9;
 }

 .stop-chart-mid2 {
   stop-color: #06b6d4;
   stop-opacity: 0.8;
 }

 .stop-chart-end {
   stop-color: #10b981;
   stop-opacity: 1;
 }

 .stop-area-top {
   stop-color: #10b981;
   stop-opacity: 0.2;
 }

 .stop-area-bottom {
   stop-color: #10b981;
   stop-opacity: 0.05;
 }

 /* SVG Elements - Dark Mode */
 :global(.dark) .stop-primary-light {
   stop-color: #60a5fa;
   stop-opacity: 1;
 }

 :global(.dark) .stop-primary-dark {
   stop-color: #3b82f6;
   stop-opacity: 1;
 }

 :global(.dark) .stop-secondary-light {
   stop-color: #a78bfa;
   stop-opacity: 1;
 }

 :global(.dark) .stop-secondary-dark {
   stop-color: #8b5cf6;
   stop-opacity: 1;
 }

 :global(.dark) .stop-accent-light {
   stop-color: #34d399;
   stop-opacity: 1;
 }

 :global(.dark) .stop-accent-dark {
   stop-color: #10b981;
   stop-opacity: 1;
 }

 :global(.dark) .stop-tertiary-light {
   stop-color: #fbbf24;
   stop-opacity: 1;
 }

 :global(.dark) .stop-tertiary-dark {
   stop-color: #f59e0b;
   stop-opacity: 1;
 }

 :global(.dark) .stop-growth-start {
   stop-color: #60a5fa;
   stop-opacity: 0.9;
 }

 :global(.dark) .stop-growth-mid {
   stop-color: #a78bfa;
   stop-opacity: 0.7;
 }

 :global(.dark) .stop-growth-end {
   stop-color: #34d399;
   stop-opacity: 0.5;
 }

 :global(.dark) .stop-growth2-start {
   stop-color: #fbbf24;
   stop-opacity: 0.7;
 }

 :global(.dark) .stop-growth2-end {
   stop-color: #f87171;
   stop-opacity: 0.5;
 }

 :global(.dark) .stop-growth3-start {
   stop-color: #22d3ee;
   stop-opacity: 0.5;
 }

 :global(.dark) .stop-growth3-end {
   stop-color: #a78bfa;
   stop-opacity: 0.3;
 }

 :global(.dark) .stop-building-fill-light {
   stop-color: #60a5fa;
   stop-opacity: 0.2;
 }

 :global(.dark) .stop-building-fill-dark {
   stop-color: #3b82f6;
   stop-opacity: 0.1;
 }

 :global(.dark) .stop-building2-fill-light {
   stop-color: #a78bfa;
   stop-opacity: 0.2;
 }

 :global(.dark) .stop-building2-fill-dark {
   stop-color: #8b5cf6;
   stop-opacity: 0.1;
 }

 :global(.dark) .stop-building3-fill-light {
   stop-color: #34d399;
   stop-opacity: 0.2;
 }

 :global(.dark) .stop-building3-fill-dark {
   stop-color: #10b981;
   stop-opacity: 0.1;
 }

 :global(.dark) .stop-building4-fill-light {
   stop-color: #fbbf24;
   stop-opacity: 0.2;
 }

 :global(.dark) .stop-building4-fill-dark {
   stop-color: #f59e0b;
   stop-opacity: 0.1;
 }

 :global(.dark) .stop-accent1-light {
   stop-color: #60a5fa;
   stop-opacity: 1;
 }

 :global(.dark) .stop-accent1-dark {
   stop-color: #3b82f6;
   stop-opacity: 0.8;
 }

 :global(.dark) .stop-accent2-light {
   stop-color: #fbbf24;
   stop-opacity: 1;
 }

 :global(.dark) .stop-accent2-dark {
   stop-color: #f59e0b;
   stop-opacity: 0.8;
 }

 :global(.dark) .stop-accent3-light {
   stop-color: #34d399;
   stop-opacity: 1;
 }

 :global(.dark) .stop-accent3-dark {
   stop-color: #10b981;
   stop-opacity: 0.8;
 }

 :global(.dark) .stop-accent4-light {
   stop-color: #a78bfa;
   stop-opacity: 1;
 }

 :global(.dark) .stop-accent4-dark {
   stop-color: #8b5cf6;
   stop-opacity: 0.8;
 }

 :global(.dark) .stop-window-light {
   stop-color: #fcd34d;
   stop-opacity: 1;
 }

 :global(.dark) .stop-window-dark {
   stop-color: #fbbf24;
   stop-opacity: 0.8;
 }

 :global(.dark) .stop-glass-light {
   stop-color: #7dd3fc;
   stop-opacity: 0.4;
 }

 :global(.dark) .stop-glass-dark {
   stop-color: #60a5fa;
   stop-opacity: 0.3;
 }

 :global(.dark) .stop-grid-light {
   stop-color: #475569;
   stop-opacity: 0.3;
 }

 :global(.dark) .stop-grid-dark {
   stop-color: #334155;
   stop-opacity: 0.2;
 }

 :global(.dark) .stop-chart-start {
   stop-color: #60a5fa;
   stop-opacity: 1;
 }

 :global(.dark) .stop-chart-mid1 {
   stop-color: #a78bfa;
   stop-opacity: 0.9;
 }

 :global(.dark) .stop-chart-mid2 {
   stop-color: #22d3ee;
   stop-opacity: 0.8;
 }

 :global(.dark) .stop-chart-end {
   stop-color: #34d399;
   stop-opacity: 1;
 }

 :global(.dark) .stop-area-top {
   stop-color: #34d399;
   stop-opacity: 0.3;
 }

 :global(.dark) .stop-area-bottom {
   stop-color: #34d399;
   stop-opacity: 0.08;
 }

 /* Building and Chart Elements */
 .building-element {
   transition: all 0.3s ease;
 }

 .growth-curve {
   filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
 }

 :global(.dark) .growth-curve {
   filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
 }

 .data-point {
   filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
 }

 :global(.dark) .data-point {
   filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.4));
 }

 .chart-line {
   filter: drop-shadow(0 2px 8px rgba(16, 185, 129, 0.3));
 }

 :global(.dark) .chart-line {
   filter: drop-shadow(0 2px 8px rgba(52, 211, 153, 0.4));
 }

 .chart-point {
   filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
 }

 :global(.dark) .chart-point {
   filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.4));
 }

 .chart-area {
   filter: drop-shadow(0 4px 12px rgba(16, 185, 129, 0.1));
 }

 :global(.dark) .chart-area {
   filter: drop-shadow(0 4px 12px rgba(52, 211, 153, 0.2));
 }

 /* Reduced Motion Support */
 @media (prefers-reduced-motion: reduce) {
   .building-element,
   .growth-curve,
   .data-point,
   .chart-line,
   .chart-point,
   .chart-area {
     animation: none !important;
   }

   .animate-pulse,
   .animate-bounce,
   .animate-ping {
     animation: none !important;
   }
 }

 /* RTL Support for Arabic */
 :global([dir="rtl"]) .headline {
   text-align: right;
 }

 :global([dir="rtl"]) .subheadline {
   text-align: right;
 }

 :global([dir="rtl"]) .font-arabic {
   font-family: 'Amiri', 'Cairo', 'Noto Sans Arabic', 'Tajawal', system-ui, sans-serif;
   font-weight: 900;
   letter-spacing: 0;
   line-height: 1.1;
 }

 /* Enhanced Arabic Typography */
 @media screen and (min-width: 640px) {
   :global([dir="rtl"]) .font-arabic {
     font-size: 1.2em;
     line-height: 0.95;
   }
 }

 @media screen and (min-width: 768px) {
   :global([dir="rtl"]) .font-arabic {
     font-size: 1.15em;
   }
 }

 @media screen and (min-width: 1024px) {
   :global([dir="rtl"]) .font-arabic {
     font-size: 1.1em;
   }
 }

 /* High Contrast Mode Support */
 @media (prefers-contrast: high) {
   .hero-section {
     background: #ffffff;
   }

   :global(.dark) .hero-section {
     background: #000000;
   }

   .headline {
     color: #000000 !important;
   }

   :global(.dark) .headline {
     color: #ffffff !important;
   }

   .subheadline {
     color: #333333 !important;
   }

   :global(.dark) .subheadline {
     color: #cccccc !important;
   }
 }

 /* Performance Optimizations */
 .hero-section,
 .building-element,
 .growth-curve,
 .data-point,
 .chart-line,
 .chart-point,
 .chart-area {
   will-change: transform, opacity;
   transform: translateZ(0);
 }

 /* Smooth font rendering */
 .headline,
 .subheadline,
 .font-arabic {
   -webkit-font-smoothing: antialiased;
   -moz-osx-font-smoothing: grayscale;
   text-rendering: optimizeLegibility;
 }
</style>