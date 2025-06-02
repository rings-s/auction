<script>
  import { onMount } from 'svelte';
  import { locale, t } from '$lib/i18n';
  $: isRTL = $locale === 'ar';
  import { fade, fly, scale } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';
  import Button from '$lib/components/ui/Button.svelte';
  
  let mounted = false;
  let prefersReducedMotion = false;
  
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
  
  <!-- Fancy Font Imports -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,500;0,600;0,700;0,800;0,900;1,400;1,500;1,600;1,700;1,800;1,900&family=Cairo:wght@200;300;400;500;600;700;800;900&display=swap" rel="stylesheet">
  
  <style>
    .font-playfair { font-family: 'Playfair Display', serif; }
    .font-cairo { font-family: 'Cairo', sans-serif; }
  </style>
</svelte:head>

<!-- Hero Section with Pure Tailwind -->
<section class="relative min-h-screen flex items-center overflow-hidden bg-gradient-to-br from-white via-purple-50 to-purple-100" aria-label="Hero section">
  
  <!-- Animated Background Elements -->
  <div class="absolute inset-0 z-0" aria-hidden="true">
    <!-- Floating circles -->
    <div class="absolute top-20 left-10 w-32 h-32 bg-gradient-to-r from-purple-200 to-indigo-200 rounded-full opacity-20 animate-pulse"></div>
    <div class="absolute top-40 right-20 w-24 h-24 bg-gradient-to-r from-blue-200 to-cyan-200 rounded-full opacity-30 animate-bounce" style="animation-delay: 1s;"></div>
    <div class="absolute bottom-40 left-20 w-40 h-40 bg-gradient-to-r from-indigo-200 to-purple-200 rounded-full opacity-25 animate-pulse" style="animation-delay: 2s;"></div>
    <div class="absolute top-60 right-40 w-16 h-16 bg-gradient-to-r from-cyan-200 to-blue-200 rounded-full opacity-40 animate-bounce" style="animation-delay: 0.5s;"></div>
    <div class="absolute bottom-60 right-10 w-28 h-28 bg-gradient-to-r from-purple-200 to-pink-200 rounded-full opacity-30 animate-pulse" style="animation-delay: 1.5s;"></div>
  </div>

  <!-- Architectural SVG Background -->
  <div class="absolute top-1/2 w-3/5 h-4/5 z-5 overflow-visible opacity-10 {isRTL ? 'left-0' : 'right-0'} -translate-y-1/2" aria-hidden="true">
    <svg class="w-full h-full {isRTL ? 'scale-x-[-1]' : ''}" viewBox="0 0 1200 800" fill="none" xmlns="http://www.w3.org/2000/svg">
      <!-- Building Silhouettes -->
      <g class="animate-pulse">
        <!-- Building 1 -->
        <path d="M500 700 L500 150 L580 130 L580 700 Z" stroke="url(#buildingGrad1)" stroke-width="2" fill="url(#buildingFill1)" class="animate-pulse" style="animation-delay: 0s;"/>
        <path d="M500 150 L540 120 L580 130 Z" stroke="url(#buildingGrad1)" stroke-width="1.5" fill="url(#accent1)"/>
        
        <!-- Building 2 -->
        <path d="M620 700 L620 100 L720 80 L720 700 Z" stroke="url(#buildingGrad2)" stroke-width="2" fill="url(#buildingFill2)" class="animate-pulse" style="animation-delay: 1s;"/>
        
        <!-- Building 3 -->
        <path d="M750 700 L750 200 L880 180 L880 700 Z" stroke="url(#buildingGrad3)" stroke-width="2" fill="url(#buildingFill3)" class="animate-pulse" style="animation-delay: 2s;"/>
        
        <!-- Building 4 -->
        <path d="M900 700 L900 250 L1020 230 L1020 700 Z" stroke="url(#buildingGrad1)" stroke-width="2" fill="url(#buildingFill1)" class="animate-pulse" style="animation-delay: 1.5s;"/>
        
        <!-- Growth Curves -->
        <path d="M375 600 Q575 450 775 380 Q975 310 1175 250" stroke="url(#growthGrad)" stroke-width="3" fill="none" class="animate-pulse"/>
        <path d="M425 650 Q625 500 825 430 Q1025 360 1225 300" stroke="url(#growthGrad2)" stroke-width="2" fill="none" class="animate-pulse" style="animation-delay: 0.5s;"/>
      </g>
      
      <!-- Gradient Definitions -->
      <defs>
        <linearGradient id="buildingGrad1" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#8b5cf6" stop-opacity="0.4"/>
          <stop offset="100%" stop-color="#6366f1" stop-opacity="0.3"/>
        </linearGradient>
        <linearGradient id="buildingGrad2" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#3b82f6" stop-opacity="0.4"/>
          <stop offset="100%" stop-color="#8b5cf6" stop-opacity="0.3"/>
        </linearGradient>
        <linearGradient id="buildingGrad3" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#06b6d4" stop-opacity="0.4"/>
          <stop offset="100%" stop-color="#3b82f6" stop-opacity="0.3"/>
        </linearGradient>
        <linearGradient id="growthGrad" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="#8b5cf6" stop-opacity="0.6"/>
          <stop offset="50%" stop-color="#3b82f6" stop-opacity="0.4"/>
          <stop offset="100%" stop-color="#06b6d4" stop-opacity="0.3"/>
        </linearGradient>
        <linearGradient id="growthGrad2" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="#6366f1" stop-opacity="0.5"/>
          <stop offset="100%" stop-color="#8b5cf6" stop-opacity="0.3"/>
        </linearGradient>
        <radialGradient id="buildingFill1" cx="50%" cy="50%" r="70%">
          <stop offset="0%" stop-color="#f8fafc" stop-opacity="0.8"/>
          <stop offset="100%" stop-color="#e2e8f0" stop-opacity="0.6"/>
        </radialGradient>
        <radialGradient id="buildingFill2" cx="50%" cy="50%" r="70%">
          <stop offset="0%" stop-color="#f1f5f9" stop-opacity="0.8"/>
          <stop offset="100%" stop-color="#e2e8f0" stop-opacity="0.6"/>
        </radialGradient>
        <radialGradient id="buildingFill3" cx="50%" cy="50%" r="70%">
          <stop offset="0%" stop-color="#f8fafc" stop-opacity="0.8"/>
          <stop offset="100%" stop-color="#cbd5e1" stop-opacity="0.6"/>
        </radialGradient>
        <radialGradient id="accent1" cx="50%" cy="50%" r="60%">
          <stop offset="0%" stop-color="#8b5cf6" stop-opacity="0.6"/>
          <stop offset="100%" stop-color="#6366f1" stop-opacity="0.4"/>
        </radialGradient>
      </defs>
    </svg>
  </div>

  <!-- Main Content Container -->
  <div class="relative z-10 w-full max-w-7xl mx-auto px-4 sm:px-6 md:px-8 lg:px-12 xl:px-16">
    {#if mounted}
      <!-- Status Badge -->
      <div class="flex justify-start mb-12">
        {#if visibleElements.badge}
          <div 
            in:fade={{ duration: 600, delay: 0, easing: cubicOut }}
            class="inline-flex items-center gap-3 px-6 py-4 rounded-2xl text-sm font-semibold transition-all duration-500 hover:-translate-y-1 hover:shadow-lg group bg-white/90 backdrop-blur-md border border-purple-200/50 shadow-lg"
            role="status"
            aria-live="polite"
          >
            <span class="w-3 h-3 bg-emerald-400 rounded-full animate-pulse shadow-lg shadow-emerald-400/50" aria-hidden="true"></span>
            <span class="text-purple-600 font-bold tracking-wide">{getText('badge.live')}</span>
            <span class="w-px h-4 bg-gradient-to-b from-transparent via-slate-300 to-transparent"></span>
            <span class="text-slate-600 text-xs font-medium">{getText('badge.count')}</span>
          </div>
        {/if}
      </div>

      <!-- F-Layout: Main content grid -->
      <div class="grid grid-cols-1 lg:grid-cols-5 gap-16 lg:gap-24 items-start">
        
        <!-- Left column: Primary content -->
        <div class="lg:col-span-3 space-y-10">
          
          <!-- HUGE Typography Headline with Fancy Fonts -->
          <div class="max-w-4xl">
            {#if visibleElements.headline}
              <h1 
                in:fly={{ y: prefersReducedMotion ? 0 : 40, duration: 800, delay: 0, easing: cubicOut }}
                class="text-8xl sm:text-9xl md:text-9xl lg:text-9xl xl:text-9xl 
                       {isRTL ? 'font-cairo text-right' : 'font-playfair text-left'} 
                       font-black leading-none tracking-tight text-slate-900 
                       drop-shadow-lg hover:text-purple-900 transition-colors duration-300"
              >
                {getText('headline')}
              </h1>
            {/if}
          </div>
          
          <!-- Enhanced Typography Paragraph -->
          <div class="{isRTL ? 'max-w-2xl ml-auto' : 'max-w-3xl'}">
            {#if visibleElements.subheadline}
              <p 
                in:fly={{ y: prefersReducedMotion ? 0 : 30, duration: 700, delay: 0, easing: cubicOut }}
                class="text-lg sm:text-xl leading-relaxed text-slate-600 max-w-[65ch] 
                       {isRTL ? 'text-right font-cairo' : 'text-left'} 
                       drop-shadow-sm"
              >
                {getText('subheadline')}
              </p>
            {/if}
          </div>
          
          <!-- CTA buttons with Tailwind styling -->
          {#if visibleElements.cta}
            <div 
              in:fly={{ y: prefersReducedMotion ? 0 : 30, duration: 700, delay: 0, easing: cubicOut }}
              class="flex flex-col sm:flex-row gap-4 pt-6 {isRTL ? 'sm:flex-row-reverse justify-end' : ''}"
            >
              <Button 
                variant="primary" 
                size="small" 
                href="/auctions"
                class="group relative overflow-hidden bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white border-0 shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-300"
              >
                <span class="relative z-10 font-semibold">{getText('cta.primary')}</span>
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

              <Button 
                variant="outline" 
                size="small" 
                href="/properties"
                class="bg-white/90 backdrop-blur-sm text-slate-700 border-slate-300 hover:bg-slate-50 hover:border-slate-400 shadow-md hover:shadow-lg transform hover:-translate-y-0.5 transition-all duration-300 font-semibold"
              >
                <span>{getText('cta.secondary')}</span>
              </Button>
            </div>
          {/if}

          <!-- Trust metrics with Tailwind styling -->
          {#if visibleElements.metrics}
            <div 
              in:fade={{ duration: 700, delay: 0, easing: cubicOut }}
              class="grid grid-cols-2 sm:grid-cols-4 gap-6 pt-10"
              role="region"
              aria-label="Platform statistics"
            >
              {#each getText('metrics') as metric, index}
                <div 
                  class="text-center p-6 rounded-2xl transition-all duration-500 hover:-translate-y-3 hover:shadow-xl group bg-white/80 backdrop-blur-sm border border-purple-100/50 shadow-md relative overflow-hidden" 
                  in:scale={{ duration: 500, delay: index * 100, easing: cubicOut }}
                >
                  <span class="block text-2xl sm:text-3xl font-black leading-none mb-2 text-slate-800 {isRTL ? 'font-cairo' : 'font-playfair'}">
                    {metric.value}
                  </span>
                  <span class="block text-sm font-medium text-slate-600 uppercase tracking-wide">
                    {metric.label}
                  </span>
                  <div class="absolute inset-0 rounded-2xl bg-gradient-to-br from-purple-500/5 to-indigo-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                </div>
              {/each}
            </div>
          {/if}
        </div>

        <!-- Right column: Market Growth Card -->
        <div class="lg:col-span-2 space-y-8 lg:mt-16">
          {#if visibleElements.marketCard}
            <div 
              class="rounded-3xl p-8 transition-all duration-700 hover:-translate-y-4 hover:shadow-2xl group bg-white/95 backdrop-blur-md border border-purple-200/50 shadow-xl relative overflow-hidden"
              in:fly={{ y: prefersReducedMotion ? 0 : 50, duration: 900, delay: 0, easing: cubicOut }}
            >
              <!-- Header -->
              <div class="flex justify-between items-center mb-8">
                <h3 class="text-xl font-bold text-slate-800 {isRTL ? 'text-right font-cairo' : 'text-left font-playfair'}">{getText('marketGrowth.title')}</h3>
                <div class="flex items-center gap-3 px-3 py-1.5 rounded-full bg-white/80 backdrop-blur-sm border border-purple-100">
                  <span class="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></span>
                  <span class="text-sm font-medium text-slate-600">{getText('marketGrowth.period')}</span>
                </div>
              </div>
              
              <!-- Chart Container -->
              <div class="mb-8 p-4 rounded-2xl bg-slate-50/80 backdrop-blur-sm border border-slate-200/50">
                <svg class="w-full h-32" viewBox="0 0 300 120" fill="none">
                  <defs>
                    <pattern id="grid" width="30" height="12" patternUnits="userSpaceOnUse">
                      <path d="m 30 0 l 0 12 m -30 0 l 30 0" stroke="#e2e8f0" stroke-width="0.5" opacity="0.5"/>
                    </pattern>
                    <linearGradient id="chartGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                      <stop offset="0%" stop-color="#8b5cf6" stop-opacity="0.8"/>
                      <stop offset="50%" stop-color="#3b82f6" stop-opacity="0.6"/>
                      <stop offset="100%" stop-color="#06b6d4" stop-opacity="0.4"/>
                    </linearGradient>
                    <linearGradient id="areaGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                      <stop offset="0%" stop-color="#8b5cf6" stop-opacity="0.3"/>
                      <stop offset="100%" stop-color="#8b5cf6" stop-opacity="0.05"/>
                    </linearGradient>
                  </defs>
                  
                  <rect width="100%" height="100%" fill="url(#grid)"/>
                  <path d="M15 100 Q50 80 100 60 Q150 45 200 35 Q250 25 285 20 L285 100 Z" fill="url(#areaGrad)" class="animate-pulse"/>
                  <path d="M15 100 Q50 80 100 60 Q150 45 200 35 Q250 25 285 20" stroke="url(#chartGrad)" stroke-width="3" fill="none" class="animate-pulse"/>
                  <circle cx="50" cy="80" r="4" fill="#8b5cf6" class="animate-pulse"/>
                  <circle cx="100" cy="60" r="4" fill="#3b82f6" class="animate-pulse" style="animation-delay: 0.5s;"/>
                  <circle cx="150" cy="45" r="4" fill="#06b6d4" class="animate-pulse" style="animation-delay: 1s;"/>
                  <circle cx="200" cy="35" r="5" fill="#8b5cf6" class="animate-pulse" style="animation-delay: 1.5s;"/>
                  <circle cx="250" cy="25" r="5" fill="#3b82f6" class="animate-pulse" style="animation-delay: 2s;"/>
                  <path d="M270 30 L280 20 L275 20 L275 15 M280 20 L275 25" stroke="#06b6d4" stroke-width="2" fill="none"/>
                </svg>
              </div>
              
              <!-- Stats Grid -->
              <div class="grid grid-cols-2 gap-4 mb-6">
                <div class="text-center p-4 rounded-xl transition-all duration-300 hover:scale-105 bg-emerald-50/80 backdrop-blur-sm border border-emerald-200/50">
                  <span class="block text-2xl font-black text-emerald-600 {isRTL ? 'font-cairo' : 'font-playfair'}">{getText('marketGrowth.stats.growthRate.value')}</span>
                  <span class="block text-xs font-medium text-slate-600 uppercase tracking-wide">{getText('marketGrowth.stats.growthRate.label')}</span>
                </div>
                <div class="text-center p-4 rounded-xl transition-all duration-300 hover:scale-105 bg-blue-50/80 backdrop-blur-sm border border-blue-200/50">
                  <span class="block text-2xl font-black text-blue-600 {isRTL ? 'font-cairo' : 'font-playfair'}">{getText('marketGrowth.stats.volume.value')}</span>
                  <span class="block text-xs font-medium text-slate-600 uppercase tracking-wide">{getText('marketGrowth.stats.volume.label')}</span>
               </div>
             </div>
             
             <!-- Additional metrics -->
             <div class="space-y-4">
               {#each getText('marketGrowth.metrics') as metric, index}
                 <div class="flex justify-between items-center p-2 rounded-lg transition-all duration-300 hover:bg-slate-50/80 backdrop-blur-sm {isRTL ? 'flex-row-reverse' : ''}">
                   <span class="text-sm font-medium text-slate-700 {isRTL ? 'text-right' : 'text-left'}">{metric.label}</span>
                   <span class="text-sm font-bold {index === 0 ? 'text-emerald-600' : index === 1 ? 'text-blue-600' : 'text-purple-600'}">{metric.value}</span>
                 </div>
               {/each}
             </div>

             <!-- Gradient overlay effect -->
             <div class="absolute inset-0 rounded-3xl bg-gradient-to-br from-white/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700 pointer-events-none"></div>
           </div>
         {/if}
       </div>
     </div>
   {/if}
 </div>
</section>