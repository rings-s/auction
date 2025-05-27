<script>
  import { onMount } from 'svelte';
  import { locale, t } from '$lib/i18n';
  import { fade, fly, scale } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';
  import Button from '$lib/components/ui/Button.svelte';
  import { theme } from '$lib/stores/theme';
  
  let mounted = false;
  let prefersReducedMotion = false;
  let scrollY = 0;
  
  // Computed value for RTL mode
  $: isRTL = $locale === 'ar';

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
      headline: 'أكشن',
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
<section class="relative min-h-screen flex items-center overflow-hidden py-32 pb-16 bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800" aria-label="Hero section">
  
  <!-- Dynamic SVG Background -->
  <div class="absolute inset-0 z-0 overflow-hidden" aria-hidden="true">
    <svg class="absolute top-0 -right-[10%] w-[70%] h-full opacity-60 dark:opacity-80 animate-pulse" viewBox="0 0 1200 800" fill="none" xmlns="http://www.w3.org/2000/svg">
      <!-- Animated building outlines -->
      <g class="animate-bounce" style="animation-duration: 8s;">
        <!-- Building 1 - Skyscraper -->
        <path class="animate-pulse" style="animation-delay: 0s; animation-duration: 6s;" d="M100 700 L100 200 L160 180 L160 700 Z" stroke="url(#gradient1)" stroke-width="2" fill="url(#buildingFill1)" opacity="0.8"/>
        <rect class="opacity-60" x="110" y="220" width="8" height="12" fill="url(#gradient1)"/>
        <rect class="opacity-60" x="130" y="240" width="8" height="12" fill="url(#gradient1)"/>
        <rect class="opacity-60" x="140" y="260" width="8" height="12" fill="url(#gradient1)"/>
        
        <!-- Building 2 - Modern tower -->
        <path class="animate-pulse" style="animation-delay: 1s; animation-duration: 6s;" d="M200 700 L200 150 L280 140 L280 700 Z" stroke="url(#gradient2)" stroke-width="2" fill="url(#buildingFill2)" opacity="0.7"/>
        <path class="opacity-80" d="M200 150 L240 130 L280 140 Z" stroke="url(#gradient2)" stroke-width="2" fill="url(#accent1)"/>
        
        <!-- Building 3 - Residential -->
        <path class="animate-pulse" style="animation-delay: 2s; animation-duration: 6s;" d="M320 700 L320 300 L420 280 L420 700 Z" stroke="url(#gradient3)" stroke-width="2" fill="url(#buildingFill3)" opacity="0.6"/>
        <path class="opacity-70" d="M320 300 L370 250 L420 280 Z" stroke="url(#gradient3)" stroke-width="2" fill="url(#accent2)"/>
        
        <!-- Building 4 - Commercial -->
        <path class="animate-pulse" style="animation-delay: 3s; animation-duration: 6s;" d="M450 700 L450 350 L550 330 L550 700 Z" stroke="url(#gradient1)" stroke-width="2" fill="url(#buildingFill1)" opacity="0.5"/>
      </g>
      
      <!-- Fluid growth curves -->
      <g class="animate-pulse" style="animation-duration: 12s;">
        <path class="opacity-80 animate-pulse" style="animation-delay: 0s; animation-duration: 8s;" d="M50 600 Q200 500 400 450 T800 380" stroke="url(#growthGradient)" stroke-width="3" fill="none"/>
        <path class="opacity-60 animate-pulse" style="animation-delay: 2s; animation-duration: 8s;" d="M100 650 Q300 550 500 500 T900 430" stroke="url(#growthGradient2)" stroke-width="2" fill="none"/>
        <path class="opacity-40 animate-pulse" style="animation-delay: 4s; animation-duration: 8s;" d="M150 680 Q350 580 600 530 T1000 460" stroke="url(#growthGradient3)" stroke-width="2" fill="none"/>
      </g>
      
      <!-- Floating data points -->
      <g class="animate-bounce" style="animation-duration: 4s;">
        <circle class="animate-ping opacity-80" style="animation-delay: 0s; animation-duration: 3s;" cx="300" cy="450" r="4" fill="url(#accent1)"/>
        <circle class="animate-ping opacity-70" style="animation-delay: 0.5s; animation-duration: 3s;" cx="500" cy="400" r="3" fill="url(#accent2)"/>
        <circle class="animate-ping opacity-90" style="animation-delay: 1s; animation-duration: 3s;" cx="700" cy="380" r="5" fill="url(#accent3)"/>
        <circle class="animate-ping opacity-60" style="animation-delay: 1.5s; animation-duration: 3s;" cx="450" cy="420" r="3" fill="url(#accent1)"/>
      </g>
      
      <!-- Gradient definitions -->
      <defs>
        <linearGradient id="gradient1" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style="stop-color:#3B82F6;stop-opacity:1" />
          <stop offset="100%" style="stop-color:#1D4ED8;stop-opacity:1" />
        </linearGradient>
        <linearGradient id="gradient2" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style="stop-color:#8B5CF6;stop-opacity:1" />
          <stop offset="100%" style="stop-color:#7C3AED;stop-opacity:1" />
        </linearGradient>
        <linearGradient id="gradient3" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style="stop-color:#10B981;stop-opacity:1" />
          <stop offset="100%" style="stop-color:#059669;stop-opacity:1" />
        </linearGradient>
        <linearGradient id="growthGradient" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" style="stop-color:#3B82F6;stop-opacity:0.8" />
          <stop offset="50%" style="stop-color:#8B5CF6;stop-opacity:0.6" />
          <stop offset="100%" style="stop-color:#10B981;stop-opacity:0.4" />
        </linearGradient>
        <linearGradient id="growthGradient2" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" style="stop-color:#F59E0B;stop-opacity:0.6" />
          <stop offset="100%" style="stop-color:#EF4444;stop-opacity:0.4" />
        </linearGradient>
        <linearGradient id="growthGradient3" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" style="stop-color:#06B6D4;stop-opacity:0.4" />
          <stop offset="100%" style="stop-color:#8B5CF6;stop-opacity:0.2" />
        </linearGradient>
        <radialGradient id="buildingFill1" cx="50%" cy="50%" r="50%">
          <stop offset="0%" style="stop-color:#3B82F6;stop-opacity:0.1" />
          <stop offset="100%" style="stop-color:#1D4ED8;stop-opacity:0.05" />
        </radialGradient>
        <radialGradient id="buildingFill2" cx="50%" cy="50%" r="50%">
          <stop offset="0%" style="stop-color:#8B5CF6;stop-opacity:0.1" />
          <stop offset="100%" style="stop-color:#7C3AED;stop-opacity:0.05" />
        </radialGradient>
        <radialGradient id="buildingFill3" cx="50%" cy="50%" r="50%">
          <stop offset="0%" style="stop-color:#10B981;stop-opacity:0.1" />
          <stop offset="100%" style="stop-color:#059669;stop-opacity:0.05" />
        </radialGradient>
        <radialGradient id="accent1" cx="50%" cy="50%" r="50%">
          <stop offset="0%" style="stop-color:#3B82F6;stop-opacity:1" />
          <stop offset="100%" style="stop-color:#1D4ED8;stop-opacity:0.8" />
        </radialGradient>
        <radialGradient id="accent2" cx="50%" cy="50%" r="50%">
          <stop offset="0%" style="stop-color:#F59E0B;stop-opacity:1" />
          <stop offset="100%" style="stop-color:#D97706;stop-opacity:0.8" />
        </radialGradient>
        <radialGradient id="accent3" cx="50%" cy="50%" r="50%">
          <stop offset="0%" style="stop-color:#10B981;stop-opacity:1" />
          <stop offset="100%" style="stop-color:#059669;stop-opacity:0.8" />
        </radialGradient>
      </defs>
    </svg>
    
    <!-- Gradient overlay -->
    <div class="absolute inset-0 bg-gradient-to-br from-blue-500/3 via-purple-500/2 to-emerald-500/3"></div>
  </div>

  <!-- F-Layout Container -->
  <div class="relative z-10 w-full max-w-7xl mx-auto px-4 sm:px-6 md:px-8 lg:px-12 xl:px-16">
    {#if mounted}
      <!-- F-Layout: Top horizontal bar - Status badge -->
      <div class="flex justify-start mb-12">
        <div 
          in:fade={{ duration: 400, delay: 100, easing: cubicOut }}
          class="inline-flex items-center gap-3 px-6 py-3.5 bg-blue-500/8 border border-blue-500/20 rounded-full text-sm font-semibold backdrop-blur-sm transition-all duration-300 hover:bg-blue-500/12 hover:-translate-y-0.5 hover:shadow-lg hover:shadow-blue-500/10"
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
          
          <!-- Main headline - top horizontal scan (wider typography) -->
          <div class="max-w-4xl">
            <h1 
              in:fly={{ y: prefersReducedMotion ? 0 : 32, duration: 600, delay: 200, easing: cubicOut }}
              class="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-black leading-[0.9] tracking-tight text-slate-900 dark:text-slate-50"
            >
              <span class="block bg-gradient-to-r from-blue-600 via-purple-600 to-emerald-600 bg-clip-text text-transparent animate-pulse">
                {getText('headline')}
              </span>
            </h1>
          </div>
          
          <!-- Subheadline - second horizontal scan (wider) -->
          <div class="max-w-3xl">
            <p 
              in:fly={{ y: prefersReducedMotion ? 0 : 24, duration: 600, delay: 300, easing: cubicOut }}
              class="text-xl sm:text-2xl leading-relaxed text-slate-600 dark:text-slate-300 font-medium"
            >
              {getText('subheadline')}
            </p>
          </div>
          
          <!-- CTA buttons - positioned along F-pattern -->
          <!-- Updated CTA section in your +page.svelte -->
          <div 
          in:fly={{ y: prefersReducedMotion ? 0 : 24, duration: 600, delay: 400, easing: cubicOut }}
          class="flex flex-col sm:flex-row gap-4 pt-4"
          >
            <Button 
              variant="primary" 
              size="small" 
              href="/auctions"
            >
              <span>{getText('cta.primary')}</span>
              <svg 
                class="w-4 h-4 transition-transform duration-200 group-hover:translate-x-0.5" 
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
                class="text-center p-6 bg-white/70 dark:bg-slate-800/70 border border-slate-200/50 dark:border-slate-700/50 rounded-2xl backdrop-blur-sm transition-all duration-300 hover:-translate-y-2 hover:shadow-lg hover:shadow-slate-200/50 dark:hover:shadow-slate-800/50 hover:border-blue-500/30" 
                in:scale={{ duration: 400, delay: 600 + (index * 100), easing: cubicOut }}
              >
                <span class="block text-2xl sm:text-3xl font-black text-slate-900 dark:text-slate-50 leading-none">
                  {metric.value}
                </span>
                <span class="block text-sm text-slate-600 dark:text-slate-400 font-medium mt-2">
                  {metric.label}
                </span>
              </div>
            {/each}
          </div>
        </div>

        <!-- Right column: Visual elements (2/5 of space) -->
        <div class="lg:col-span-2 space-y-8">
          <!-- Market trend visualization -->
          <div 
            class="bg-white/95 dark:bg-slate-800/95 border border-slate-200/80 dark:border-slate-700/80 rounded-3xl p-8 backdrop-blur-2xl shadow-xl shadow-slate-200/20 dark:shadow-slate-900/20 transition-all duration-300 hover:-translate-y-2 hover:shadow-2xl"
            in:fly={{ y: prefersReducedMotion ? 0 : 40, duration: 800, delay: 600, easing: cubicOut }}
          >
            <div class="flex justify-between items-center mb-6">
              <h3 class="text-xl font-bold text-slate-900 dark:text-slate-50">Market Growth</h3>
              <span class="text-sm text-slate-600 dark:text-slate-400 font-medium">12 months</span>
            </div>
            
            <div class="mb-6">
              <svg class="w-full h-16" viewBox="0 0 200 60" fill="none">
                <path class="animate-pulse" style="animation-duration: 3s;" d="M10 50 Q50 30 100 25 T190 15" stroke="url(#chartGradient)" stroke-width="2" fill="none"/>
                <circle class="animate-bounce" style="animation-duration: 2s;" cx="190" cy="15" r="3" fill="#10B981"/>
                <defs>
                  <linearGradient id="chartGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" style="stop-color:#3B82F6;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#10B981;stop-opacity:1" />
                  </linearGradient>
                </defs>
              </svg>
            </div>
            
            <div class="space-y-1">
              <span class="block text-3xl font-black text-emerald-600">+24.5%</span>
              <span class="block text-sm text-slate-600 dark:text-slate-400">Average growth</span>
            </div>
          </div>
        </div>
      </div>
    {/if}
  </div>
</section>