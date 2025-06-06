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
    buildings: false
  };
  
  // Enhanced translations
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
      }
    },
    ar: {
      badge: {
        live: 'مباشر الآن',
        count: '24 نشط'
      },
      headline: 'اكــــشن',
      subheadline: 'اكتشف العقارات الحصرية من خلال المزادات الشفافة. انضم لآلاف المشترين والبائعين الناجحين.',
      cta: {
        primary: 'ابدأ المزايدة',
        secondary: 'عرض العقارات'
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
      { element: 'buildings', delay: 500 }
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

<!-- Hero Section - Bold RTL/LTR Design -->
<section class="relative min-h-screen overflow-hidden" aria-label="Hero section" dir="{isRTL ? 'rtl' : 'ltr'}">
  
  <!-- Enhanced Professional Gradient Background -->
  <div class="absolute inset-0">
    <div class="absolute inset-0 bg-gradient-to-br from-slate-50/90 via-white to-purple-50/70"></div>
    <div class="absolute inset-0 bg-gradient-to-tr from-transparent via-indigo-50/30 to-blue-50/40"></div>
    <div class="absolute inset-0 bg-gradient-to-bl from-emerald-50/20 via-transparent to-cyan-50/30"></div>
  </div>
  
  <!-- Sophisticated Geometric Accent Elements -->
  <div class="absolute inset-0 overflow-hidden pointer-events-none" aria-hidden="true">
    <!-- Primary Accent - Positioned based on language direction -->
    <div class="absolute {isRTL ? 'top-0 left-0' : 'top-0 right-0'} w-2/5 h-3/5 bg-gradient-to-{isRTL ? 'br' : 'bl'} from-purple-100/40 via-indigo-50/25 to-transparent opacity-70"></div>
    
    <!-- Secondary Accent - Opposite positioning -->
    <div class="absolute {isRTL ? 'bottom-10 right-0' : 'bottom-10 left-0'} w-1/3 h-2/5 bg-gradient-to-{isRTL ? 'tl' : 'tr'} from-blue-100/35 via-cyan-50/20 to-transparent rounded-full filter blur-3xl opacity-80"></div>
    
    <!-- Tertiary Accent for depth -->
    <div class="absolute top-1/4 {isRTL ? 'right-1/3' : 'left-1/3'} w-48 h-48 bg-gradient-to-br from-emerald-100/50 via-teal-50/30 to-transparent rounded-full filter blur-2xl opacity-60"></div>
    
    <!-- Professional overlay mesh -->
    <div class="absolute inset-0 bg-gradient-to-tr from-transparent via-white/15 to-purple-50/25 opacity-40"></div>
  </div>

  <!-- Bold SVG Buildings - Outside Content Area -->
  {#if mounted && visibleElements.buildings}
    <div 
      class="absolute inset-0 w-full h-full pointer-events-none opacity-25 lg:opacity-35" 
      aria-hidden="true"
      in:fade={{ duration: 2500, delay: 0, easing: cubicOut }}
    >
      <!-- Mobile/Tablet: Column Layout - Large Bottom SVG -->
      <div class="lg:hidden absolute bottom-0 left-0 right-0 w-full h-2/3 flex items-end justify-center">
        <div class="w-full h-full max-w-5xl">
          <svg class="w-full h-full {isRTL ? 'scale-x-[-1]' : ''}" viewBox="0 0 1400 700" fill="none" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <linearGradient id="windowGlowMobile" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#8b5cf6" stop-opacity="0.9"/>
                <stop offset="25%" stop-color="#7c3aed" stop-opacity="0.75"/>
                <stop offset="50%" stop-color="#6366f1" stop-opacity="0.6"/>
                <stop offset="75%" stop-color="#3b82f6" stop-opacity="0.45"/>
                <stop offset="100%" stop-color="#06b6d4" stop-opacity="0.3"/>
              </linearGradient>
              <linearGradient id="buildingStrokeMobile" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stop-color="#e2e8f0" stop-opacity="1"/>
                <stop offset="50%" stop-color="#cbd5e1" stop-opacity="0.8"/>
                <stop offset="100%" stop-color="#94a3b8" stop-opacity="0.6"/>
              </linearGradient>
              <linearGradient id="roofGradMobile" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stop-color="#8b5cf6" stop-opacity="0.5"/>
                <stop offset="100%" stop-color="#6366f1" stop-opacity="0.2"/>
              </linearGradient>
            </defs>
            
            <!-- Building Complex 1 -->
            <g class="animate-pulse" style="animation-duration: 5s; animation-delay: 0.5s;">
              <rect x="80" y="280" width="140" height="420" rx="12" fill="none" stroke="url(#buildingStrokeMobile)" stroke-width="3"/>
              <polygon points="75,280 150,245 225,280" fill="url(#roofGradMobile)"/>
              <g opacity="0.85">
                {#each Array(6) as _, floor}
                  {#each Array(3) as _, window}
                    <rect 
                      x="{105 + window * 30}" 
                      y="{320 + floor * 55}" 
                      width="16" 
                      height="22" 
                      rx="4" 
                      fill="url(#windowGlowMobile)"
                      class="animate-pulse"
                      style="animation-delay: {(floor * 3 + window) * 0.4}s; animation-duration: 4s;"
                    />
                  {/each}
                {/each}
              </g>
            </g>
            
            <!-- Building Complex 2 -->
            <g class="animate-pulse" style="animation-duration: 6s; animation-delay: 1s;">
              <rect x="260" y="200" width="160" height="500" rx="15" fill="none" stroke="url(#buildingStrokeMobile)" stroke-width="3"/>
              <rect x="260" y="175" width="160" height="30" rx="15" fill="url(#roofGradMobile)"/>
              <g opacity="0.8">
                {#each Array(7) as _, floor}
                  {#each Array(4) as _, window}
                    <rect 
                      x="{285 + window * 28}" 
                      y="{235 + floor * 60}" 
                      width="18" 
                      height="26" 
                      rx="4" 
                      fill="url(#windowGlowMobile)"
                      class="animate-pulse"
                      style="animation-delay: {(floor * 4 + window) * 0.3}s; animation-duration: 5s;"
                    />
                  {/each}
                {/each}
              </g>
            </g>
            
            <!-- Building Complex 3 - Tallest -->
            <g class="animate-pulse" style="animation-duration: 7s; animation-delay: 1.5s;">
              <rect x="460" y="120" width="180" height="580" rx="18" fill="none" stroke="url(#buildingStrokeMobile)" stroke-width="3"/>
              <rect x="460" y="95" width="180" height="30" rx="15" fill="url(#roofGradMobile)"/>
              <g opacity="0.75">
                {#each Array(8) as _, floor}
                  {#each Array(5) as _, window}
                    <rect 
                      x="{485 + window * 26}" 
                      y="{155 + floor * 65}" 
                      width="20" 
                      height="28" 
                      rx="4" 
                      fill="url(#windowGlowMobile)"
                      class="animate-pulse"
                      style="animation-delay: {(floor * 5 + window) * 0.25}s; animation-duration: 6s;"
                    />
                  {/each}
                {/each}
              </g>
            </g>
            
            <!-- Building Complex 4 -->
            <g class="animate-pulse" style="animation-duration: 5.5s; animation-delay: 2s;">
              <rect x="680" y="240" width="140" height="460" rx="12" fill="none" stroke="url(#buildingStrokeMobile)" stroke-width="3"/>
              <polygon points="675,240 750,205 825,240" fill="url(#roofGradMobile)"/>
              <g opacity="0.85">
                {#each Array(6) as _, floor}
                  {#each Array(3) as _, window}
                    <rect 
                      x="{705 + window * 30}" 
                      y="{275 + floor * 70}" 
                      width="17" 
                      height="24" 
                      rx="4" 
                      fill="url(#windowGlowMobile)"
                      class="animate-pulse"
                      style="animation-delay: {(floor * 3 + window) * 0.4}s; animation-duration: 4.5s;"
                    />
                  {/each}
                {/each}
              </g>
            </g>
            
            <!-- Building Complex 5 -->
            <g class="animate-pulse" style="animation-duration: 4.5s; animation-delay: 2.5s;">
              <rect x="860" y="300" width="120" height="400" rx="10" fill="none" stroke="url(#buildingStrokeMobile)" stroke-width="3"/>
              <rect x="860" y="275" width="120" height="30" rx="15" fill="url(#roofGradMobile)"/>
              <g opacity="0.9">
                {#each Array(5) as _, floor}
                  {#each Array(3) as _, window}
                    <rect 
                      x="{880 + window * 25}" 
                      y="{335 + floor * 70}" 
                      width="15" 
                      height="20" 
                      rx="4" 
                      fill="url(#windowGlowMobile)"
                      class="animate-pulse"
                      style="animation-delay: {(floor * 3 + window) * 0.5}s; animation-duration: 3.5s;"
                    />
                  {/each}
                {/each}
              </g>
            </g>
            
            <!-- Building Complex 6 -->
            <g class="animate-pulse" style="animation-duration: 4s; animation-delay: 3s;">
              <rect x="1020" y="360" width="100" height="340" rx="8" fill="none" stroke="url(#buildingStrokeMobile)" stroke-width="3"/>
              <polygon points="1015,360 1070,330 1125,360" fill="url(#roofGradMobile)"/>
              <g opacity="0.85">
                {#each Array(4) as _, floor}
                  {#each Array(2) as _, window}
                    <rect 
                      x="{1040 + window * 30}" 
                      y="{395 + floor * 75}" 
                      width="14" 
                      height="18" 
                      rx="4" 
                      fill="url(#windowGlowMobile)"
                      class="animate-pulse"
                      style="animation-delay: {(floor * 2 + window) * 0.7}s; animation-duration: 3s;"
                    />
                  {/each}
                {/each}
              </g>
            </g>
            
            <!-- Building Complex 7 -->
            <g class="animate-pulse" style="animation-duration: 6s; animation-delay: 3.5s;">
              <rect x="1160" y="400" width="80" height="300" rx="8" fill="none" stroke="url(#buildingStrokeMobile)" stroke-width="3"/>
              <rect x="1160" y="375" width="80" height="30" rx="15" fill="url(#roofGradMobile)"/>
              <g opacity="0.8">
                {#each Array(3) as _, floor}
                  {#each Array(2) as _, window}
                    <rect 
                      x="{1175 + window * 25}" 
                      y="{430 + floor * 80}" 
                      width="12" 
                      height="16" 
                      rx="3" 
                      fill="url(#windowGlowMobile)"
                      class="animate-pulse"
                      style="animation-delay: {(floor * 2 + window) * 0.8}s; animation-duration: 3s;"
                    />
                  {/each}
                {/each}
              </g>
            </g>
          </svg>
        </div>
      </div>

      <!-- Desktop: Row Layout - Massive Side-positioned SVG -->
      <div class="hidden lg:block absolute inset-0 w-full h-full">
        <div class="w-full h-full flex items-center {isRTL ? 'justify-start' : 'justify-end'}">
          <div class="w-4/5 h-5/6 max-w-6xl {isRTL ? 'mr-0 ml-auto' : 'ml-0 mr-auto'} flex items-center {isRTL ? 'justify-start' : 'justify-end'}">
            <svg class="w-full h-full {isRTL ? 'scale-x-[-1]' : ''}" viewBox="0 0 1400 800" fill="none" xmlns="http://www.w3.org/2000/svg">
              <defs>
                <linearGradient id="windowGlowDesktop" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stop-color="#8b5cf6" stop-opacity="0.95"/>
                  <stop offset="20%" stop-color="#7c3aed" stop-opacity="0.8"/>
                  <stop offset="40%" stop-color="#6366f1" stop-opacity="0.65"/>
                  <stop offset="60%" stop-color="#3b82f6" stop-opacity="0.5"/>
                  <stop offset="80%" stop-color="#06b6d4" stop-opacity="0.35"/>
                  <stop offset="100%" stop-color="#10b981" stop-opacity="0.2"/>
                </linearGradient>
                
                <linearGradient id="buildingStrokeDesktop" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" stop-color="#f1f5f9" stop-opacity="1"/>
                  <stop offset="30%" stop-color="#e2e8f0" stop-opacity="0.9"/>
                  <stop offset="70%" stop-color="#cbd5e1" stop-opacity="0.7"/>
                  <stop offset="100%" stop-color="#94a3b8" stop-opacity="0.5"/>
                </linearGradient>
                
                <linearGradient id="roofGradDesktop" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" stop-color="#8b5cf6" stop-opacity="0.6"/>
                  <stop offset="50%" stop-color="#7c3aed" stop-opacity="0.4"/>
                  <stop offset="100%" stop-color="#6366f1" stop-opacity="0.15"/>
                </linearGradient>
                
                <radialGradient id="spotGlowDesktop" cx="50%" cy="50%" r="50%">
                  <stop offset="0%" stop-color="#8b5cf6" stop-opacity="0.4"/>
                  <stop offset="70%" stop-color="#6366f1" stop-opacity="0.2"/>
                  <stop offset="100%" stop-color="#6366f1" stop-opacity="0"/>
                </radialGradient>
              </defs>
              
              <!-- Massive Building Complex 1 -->
              <g class="animate-pulse" style="animation-duration: 5s; animation-delay: 0.5s;">
                <rect x="80" y="350" width="160" height="450" rx="15" fill="none" stroke="url(#buildingStrokeDesktop)" stroke-width="3.5"/>
                <polygon points="75,350 160,310 245,350" fill="url(#roofGradDesktop)"/>
                <g opacity="0.85">
                  {#each Array(7) as _, floor}
                    {#each Array(4) as _, window}
                      <rect 
                        x="{105 + window * 28}" 
                        y="{390 + floor * 55}" 
                        width="18" 
                        height="24" 
                        rx="4" 
                        fill="url(#windowGlowDesktop)"
                        class="animate-pulse"
                        style="animation-delay: {(floor * 4 + window) * 0.3}s; animation-duration: 4s;"
                      />
                    {/each}
                  {/each}
                </g>
              </g>
              
              <!-- Massive Building Complex 2 -->
              <g class="animate-pulse" style="animation-duration: 6s; animation-delay: 1s;">
                <rect x="280" y="250" width="180" height="550" rx="18" fill="none" stroke="url(#buildingStrokeDesktop)" stroke-width="3.5"/>
                <rect x="280" y="220" width="180" height="35" rx="17" fill="url(#roofGradDesktop)"/>
                <g opacity="0.8">
                  {#each Array(8) as _, floor}
                    {#each Array(4) as _, window}
                      <rect 
                        x="{305 + window * 32}" 
                        y="{285 + floor * 60}" 
                        width="20" 
                        height="28" 
                        rx="4" 
                        fill="url(#windowGlowDesktop)"
                        class="animate-pulse"
                        style="animation-delay: {(floor * 4 + window) * 0.25}s; animation-duration: 5s;"
                      />
                    {/each}
                  {/each}
                </g>
              </g>
              
              <!-- Massive Building Complex 3 - Tallest -->
              <g class="animate-pulse" style="animation-duration: 7s; animation-delay: 1.5s;">
                <rect x="500" y="150" width="200" height="650" rx="20" fill="none" stroke="url(#buildingStrokeDesktop)" stroke-width="3.5"/>
                <rect x="500" y="120" width="200" height="35" rx="17" fill="url(#roofGradDesktop)"/>
                <g opacity="0.75">
                  {#each Array(9) as _, floor}
                    {#each Array(5) as _, window}
                      <rect 
                        x="{525 + window * 30}" 
                        y="{185 + floor * 65}" 
                        width="22" 
                        height="30" 
                        rx="4" 
                        fill="url(#windowGlowDesktop)"
                        class="animate-pulse"
                        style="animation-delay: {(floor * 5 + window) * 0.2}s; animation-duration: 6s;"
                      />
                    {/each}
                  {/each}
                </g>
              </g>
              
              <!-- Massive Building Complex 4 -->
              <g class="animate-pulse" style="animation-duration: 5.5s; animation-delay: 2s;">
                <rect x="740" y="300" width="160" height="500" rx="15" fill="none" stroke="url(#buildingStrokeDesktop)" stroke-width="3.5"/>
                <polygon points="735,300 820,260 905,300" fill="url(#roofGradDesktop)"/>
                <g opacity="0.85">
                  {#each Array(7) as _, floor}
                    {#each Array(4) as _, window}
                      <rect 
                        x="{765 + window * 28}" 
                        y="{340 + floor * 65}" 
                        width="19" 
                        height="26" 
                        rx="4" 
                        fill="url(#windowGlowDesktop)"
                        class="animate-pulse"
                        style="animation-delay: {(floor * 4 + window) * 0.3}s; animation-duration: 4.5s;"
                      />
                    {/each}
                  {/each}
                </g>
              </g>
              
              <!-- Massive Building Complex 5 -->
              <g class="animate-pulse" style="animation-duration: 4.5s; animation-delay: 2.5s;">
                <rect x="940" y="380" width="130" height="420" rx="12" fill="none" stroke="url(#buildingStrokeDesktop)" stroke-width="3.5"/>
                <rect x="940" y="350" width="130" height="35" rx="17" fill="url(#roofGradDesktop)"/>
                <g opacity="0.9">
                  {#each Array(6) as _, floor}
                    {#each Array(3) as _, window}
                      <rect 
                        x="{965 + window * 30}" 
                        y="{415 + floor * 60}" 
                        width="16" 
                        height="22" 
                        rx="4" 
                        fill="url(#windowGlowDesktop)"
                        class="animate-pulse"
                        style="animation-delay: {(floor * 3 + window) * 0.4}s; animation-duration: 3.5s;"
                      />
                    {/each}
                  {/each}
                </g>
              </g>
              
              <!-- Massive Building Complex 6 -->
              <g class="animate-pulse" style="animation-duration: 4s; animation-delay: 3s;">
                <rect x="1110" y="420" width="110" height="380" rx="10" fill="none" stroke="url(#buildingStrokeDesktop)" stroke-width="3.5"/>
                <polygon points="1105,420 1165,385 1225,420" fill="url(#roofGradDesktop)"/>
                <g opacity="0.85">
                  {#each Array(5) as _, floor}
                    {#each Array(2) as _, window}
                      <rect 
                        x="{1135 + window * 35}" 
                        y="{460 + floor * 70}" 
                        width="15" 
                        height="20" 
                        rx="4" 
                        fill="url(#windowGlowDesktop)"
                        class="animate-pulse"
                        style="animation-delay: {(floor * 2 + window) * 0.6}s; animation-duration: 3s;"
                      />
                    {/each}
                  {/each}
                </g>
              </g>

              <!-- Enhanced Floating Elements -->
              <g class="animate-bounce" style="animation-duration: 6s; animation-delay: 3.5s;">
                <circle cx="300" cy="180" r="22" fill="url(#spotGlowDesktop)"/>
                <circle cx="300" cy="180" r="16" fill="none" stroke="#8b5cf6" stroke-width="2.5" opacity="0.8"/>
                <path d="M288 168 L300 156 L312 168 L312 192 L288 192 Z" fill="none" stroke="#8b5cf6" stroke-width="2" opacity="0.9"/>
              </g>
              
              <g class="animate-bounce" style="animation-duration: 7s; animation-delay: 4s;">
                <circle cx="800" cy="160" r="20" fill="url(#spotGlowDesktop)"/>
                <circle cx="800" cy="160" r="14" fill="none" stroke="#6366f1" stroke-width="2.5" opacity="0.8"/>
                <path d="M788 148 L800 136 L812 148 L812 172 L788 172 Z" fill="none" stroke="#6366f1" stroke-width="2" opacity="0.9"/>
              </g>

              <!-- Growth Indicators -->
              <g class="animate-ping" style="animation-duration: 3s; animation-delay: 4.5s;">
                <circle cx="450" cy="100" r="18" fill="#10b981" opacity="0.4"/>
                <circle cx="450" cy="100" r="12" fill="#10b981" opacity="0.7"/>
                <circle cx="450" cy="100" r="6" fill="#10b981" opacity="1"/>
              </g>
              
              <g class="animate-ping" style="animation-duration: 4s; animation-delay: 5s;">
                <circle cx="950" cy="120" r="16" fill="#06b6d4" opacity="0.4"/>
                <circle cx="950" cy="120" r="10" fill="#06b6d4" opacity="0.7"/>
                <circle cx="950" cy="120" r="5" fill="#06b6d4" opacity="1"/>
              </g>
            </svg>
          </div>
        </div>
      </div>
    </div>
  {/if}

  <!-- Content Container - RTL Responsive -->
  <div class="relative z-20 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 min-h-screen">
    {#if mounted}
      
      <!-- Column Layout: xs, sm, md screens -->
      <div class="flex flex-col min-h-screen justify-center items-center text-center lg:hidden py-16">
        <div class="w-full max-w-lg space-y-8">
          
          <!-- Status Badge -->
          <div class="flex justify-center">
            {#if visibleElements.badge}
              <div 
                in:fade={{ duration: 800, delay: 0, easing: cubicOut }}
                class="inline-flex items-center gap-3 px-6 py-4 rounded-2xl text-sm font-bold transition-all duration-500 hover:scale-105 hover:shadow-2xl group bg-white/95 backdrop-blur-xl border border-gray-200/70 shadow-xl relative overflow-hidden"
                role="status"
                aria-live="polite"
              >
                <span class="w-3 h-3 bg-emerald-400 rounded-full animate-pulse shadow-lg shadow-emerald-400/60" aria-hidden="true"></span>
                <span class="text-purple-600 font-bold tracking-wide">{getText('badge.live')}</span>
                <span class="w-px h-4 bg-gradient-to-b from-transparent via-slate-300 to-transparent"></span>
                <span class="text-slate-600 text-sm font-medium">{getText('badge.count')}</span>
                <div class="absolute inset-0 bg-gradient-to-r from-purple-500/8 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
              </div>
            {/if}
          </div>
          
          <!-- Hero Headline -->
          <div>
            {#if visibleElements.headline}
              <h1 
                in:fly={{ y: prefersReducedMotion ? 0 : 50, duration: 1000, delay: 0, easing: cubicOut }}
                class="text-5xl sm:text-6xl md:text-7xl 
                       font-black leading-[0.9] tracking-tight text-slate-900 text-center"
                style="{isRTL ? 'font-family: system-ui, -apple-system, sans-serif; line-height: 1.15 !important;' : ''}"
              >
                <span class="hover:text-transparent hover:bg-clip-text hover:bg-gradient-to-r hover:from-purple-600 hover:via-indigo-600 hover:to-blue-600 transition-all duration-700">
                  {getText('headline')}
                </span>
              </h1>
            {/if}
          </div>
          
          <!-- Subheadline -->
          <div>
            {#if visibleElements.subheadline}
              <p 
                in:fly={{ y: prefersReducedMotion ? 0 : 30, duration: 800, delay: 200, easing: cubicOut }}
                class="text-lg sm:text-xl md:text-2xl leading-relaxed text-slate-600 font-medium text-center max-w-[55ch] mx-auto"
              >
                {getText('subheadline')}
              </p>
            {/if}
          </div>
          
          <!-- CTA Section -->
          {#if visibleElements.cta}
            <div 
              in:fly={{ y: prefersReducedMotion ? 0 : 30, duration: 800, delay: 400, easing: cubicOut }}
              class="flex flex-col gap-4 pt-8 {isRTL ? 'items-center' : 'items-center'}"
            >
              <Button 
                variant="primary" 
                size="default" 
                href="/auctions"
                class="w-full max-w-xs group relative overflow-hidden bg-gradient-to-r from-purple-600 via-indigo-600 to-blue-600 hover:from-purple-700 hover:via-indigo-700 hover:to-blue-700 text-white border-0 shadow-2xl hover:shadow-purple-500/40 transform hover:scale-105 hover:-translate-y-1 transition-all duration-300 rounded-2xl font-bold px-8 py-5 text-lg"
              >
                <span class="relative z-10">{getText('cta.primary')}</span>
                <svg 
                  class="w-5 h-5 transition-all duration-300 group-hover:translate-x-1 relative z-10 {isRTL ? 'rotate-180' : ''}" 
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                  slot="iconRight"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
                <div class="absolute inset-0 bg-gradient-to-r from-white/25 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-2xl"></div>
              </Button>

              <Button 
                variant="outline" 
                size="default" 
                href="/properties"
                class="w-full max-w-xs group relative overflow-hidden bg-white/95 backdrop-blur-xl text-slate-700 border-slate-300/70 hover:bg-slate-50 hover:border-purple-300/80 shadow-xl hover:shadow-2xl transform hover:scale-105 hover:-translate-y-1 transition-all duration-300 font-bold rounded-2xl px-8 py-5 text-lg"
              >
                <span class="relative z-10">{getText('cta.secondary')}</span>
                <div class="absolute inset-0 bg-gradient-to-r from-purple-50/60 to-indigo-50/40 opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-2xl"></div>
              </Button>
            </div>
          {/if}
        </div>
      </div>

      <!-- Row Layout: lg+ screens -->
      <div class="hidden lg:flex min-h-screen {isRTL ? 'flex-row-reverse' : 'flex-row'}">
        <div class="flex-1 flex items-center {isRTL ? 'justify-end' : 'justify-start'} py-12">
          <div class="w-full max-w-3xl space-y-10 {isRTL ? 'text-right' : 'text-left'}">
            
            <!-- Desktop Status Badge -->
            <div class="flex {isRTL ? 'justify-end' : 'justify-start'}">
              {#if visibleElements.badge}
                <div 
                  in:fade={{ duration: 800, delay: 0, easing: cubicOut }}
                  class="inline-flex items-center gap-4 px-8 py-4 rounded-2xl text-sm font-bold transition-all duration-500 hover:scale-105 hover:shadow-2xl group bg-white/95 backdrop-blur-xl border border-gray-200/70 shadow-xl relative overflow-hidden"
                  role="status"
                  aria-live="polite"
                >
                  <span class="w-3 h-3 bg-emerald-400 rounded-full animate-pulse shadow-lg shadow-emerald-400/60" aria-hidden="true"></span>
                  <span class="text-purple-600 font-bold tracking-wide text-base">{getText('badge.live')}</span>
                  <span class="w-px h-5 bg-gradient-to-b from-transparent via-slate-300 to-transparent"></span>
                  <span class="text-slate-600 text-sm font-medium">{getText('badge.count')}</span>
                  <div class="absolute inset-0 bg-gradient-to-r from-purple-500/8 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                </div>
              {/if}
            </div>
            
            <!-- Desktop Headline -->
            <div>
              {#if visibleElements.headline}
                <h1 
                  in:fly={{ y: prefersReducedMotion ? 0 : 50, duration: 1000, delay: 0, easing: cubicOut }}
                  class="text-7xl lg:text-8xl xl:text-9xl 
                         font-black leading-[0.85] tracking-tight text-slate-900
                         {isRTL ? 'text-right' : 'text-left'}"
                  style="{isRTL ? 'font-family: system-ui, -apple-system, sans-serif; line-height: 1.15 !important;' : ''}"
                >
                  <span class="hover:text-transparent hover:bg-clip-text hover:bg-gradient-to-r hover:from-purple-600 hover:via-indigo-600 hover:to-blue-600 transition-all duration-700">
                    {getText('headline')}
                  </span>
                </h1>
              {/if}
            </div>
            
            <!-- Desktop Subheadline -->
            <div class="max-w-2xl {isRTL ? 'ml-auto' : 'mr-auto lg:mr-0'}">
              {#if visibleElements.subheadline}
                <p 
                  in:fly={{ y: prefersReducedMotion ? 0 : 30, duration: 800, delay: 200, easing: cubicOut }}
                  class="text-2xl lg:text-2xl leading-relaxed text-slate-600 font-medium {isRTL ? 'text-right' : 'text-left'} max-w-[55ch]"
                >
                  {getText('subheadline')}
                </p>
              {/if}
            </div>
            
            <!-- Desktop CTA -->
            {#if visibleElements.cta}
              <div 
                in:fly={{ y: prefersReducedMotion ? 0 : 30, duration: 800, delay: 400, easing: cubicOut }}
                class="flex flex-col sm:flex-row gap-6 pt-8 {isRTL ? 'sm:flex-row-reverse justify-end' : 'justify-start'}"
              >
                <Button 
                  variant="primary" 
                  size="default" 
                  href="/auctions"
                  class="group relative overflow-hidden bg-gradient-to-r from-purple-600 via-indigo-600 to-blue-600 hover:from-purple-700 hover:via-indigo-700 hover:to-blue-700 text-white border-0 shadow-2xl hover:shadow-purple-500/40 transform hover:scale-105 hover:-translate-y-1 transition-all duration-300 rounded-2xl font-bold px-10 py-5 text-lg"
                >
                  <span class="relative z-10">{getText('cta.primary')}</span>
                  <svg 
                    class="w-5 h-5 transition-all duration-300 group-hover:translate-x-1 relative z-10 {isRTL ? 'rotate-180' : ''}" 
                    fill="none" 
                    stroke="currentColor" 
                    viewBox="0 0 24 24"
                    aria-hidden="true"
                    slot="iconRight"
                  >
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                  <div class="absolute inset-0 bg-gradient-to-r from-white/25 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-2xl"></div>
                </Button>

                <Button 
                  variant="outline" 
                  size="default" 
                  href="/properties"
                  class="group relative overflow-hidden bg-white/95 backdrop-blur-xl text-slate-700 border-slate-300/70 hover:bg-slate-50 hover:border-purple-300/80 shadow-xl hover:shadow-2xl transform hover:scale-105 hover:-translate-y-1 transition-all duration-300 font-bold rounded-2xl px-10 py-5 text-lg"
                >
                  <span class="relative z-10">{getText('cta.secondary')}</span>
                  <div class="absolute inset-0 bg-gradient-to-r from-purple-50/60 to-indigo-50/40 opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-2xl"></div>
                </Button>
              </div>
            {/if}
          </div>
        </div>
      </div>
    {/if}
  </div>
</section>