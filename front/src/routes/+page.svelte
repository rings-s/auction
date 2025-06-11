<script>
  import { onMount } from 'svelte';
  import { locale, t } from '$lib/i18n';
  import { fade, fly, scale } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';
  import Button from '$lib/components/ui/Button.svelte';
  import { theme } from '$lib/stores/theme';
  
  // Initialize with safe defaults
  $: isRTL = $locale === 'ar';
  
  let mounted = false;
  let scrollY = 0;
  let mouseX = 0;
  let mouseY = 0;
  let prefersReducedMotion = false;
  
  // Animation states
  let visibleElements = {
    badge: false,
    headline: false,
    subheadline: false,
    cta: false,
    metrics: false,
    features: false,
    illustration: false
  };
  
  // Static data to avoid undefined errors
  const metrics = {
    en: [
      { value: '$2.5M+', label: 'Total Sales' },
      { value: '98%', label: 'Success Rate' },
      { value: '15K+', label: 'Active Users' },
      { value: '4.9★', label: 'Rating' }
    ],
    ar: [
      { value: '+2.5م$', label: 'إجمالي المبيعات' },
      { value: '98%', label: 'معدل النجاح' },
      { value: '+15ألف', label: 'مستخدم نشط' },
      { value: '★4.9', label: 'التقييم' }
    ]
  };

  const features = {
    en: [
      { title: 'Secure Bidding', desc: 'Bank-level encryption', icon: 'shield' },
      { title: 'Real-time Updates', desc: 'Live auction tracking', icon: 'bolt' },
      { title: 'Expert Support', desc: '24/7 assistance', icon: 'headset' }
    ],
    ar: [
      { title: 'مزايدة آمنة', desc: 'تشفير على مستوى البنوك', icon: 'shield' },
      { title: 'تحديثات فورية', desc: 'تتبع المزاد المباشر', icon: 'bolt' },
      { title: 'دعم الخبراء', desc: 'مساعدة على مدار الساعة', icon: 'headset' }
    ]
  };

  // Safe getter functions
  function getCurrentLocale() {
    return $locale || 'en';
  }

  function getMetrics() {
    const lang = getCurrentLocale();
    return metrics[lang] || metrics.en;
  }

  function getFeatures() {
    const lang = getCurrentLocale();
    return features[lang] || features.en;
  }

  // Mouse parallax effect
  function handleMouseMove(event) {
    if (!mounted) return;
    const rect = event.currentTarget.getBoundingClientRect();
    mouseX = ((event.clientX - rect.left) / rect.width - 0.5) * 20;
    mouseY = ((event.clientY - rect.top) / rect.height - 0.5) * 20;
  }

  onMount(() => {
    mounted = true;
    
    // Check for reduced motion preference
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
      { element: 'illustration', delay: 600 },
      { element: 'features', delay: 700 }
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

<!-- Hero Section with Consistent Design -->
<section 
  class="relative min-h-screen flex items-center py-20 sm:py-24 lg:py-32 overflow-hidden bg-gradient-to-b from-white via-purple-50/20 to-white dark:from-gray-900 dark:via-purple-950/20 dark:to-gray-900" 
  aria-label="Hero section"
  on:mousemove={handleMouseMove}
  role="presentation"
>
  
  <!-- Background Decoration -->
  <div class="absolute inset-0 pointer-events-none overflow-hidden">
    <div class="absolute top-20 left-0 w-96 h-96 bg-purple-200/30 dark:bg-purple-800/20 rounded-full blur-3xl"></div>
    <div class="absolute bottom-20 right-0 w-96 h-96 bg-blue-200/30 dark:bg-blue-800/20 rounded-full blur-3xl"></div>
    
    <!-- Floating elements -->
    {#if mounted}
      <div 
        class="absolute top-1/4 right-1/4 w-64 h-64 bg-purple-300/20 dark:bg-purple-700/10 rounded-full blur-2xl"
        style="transform: translate({mouseX * 0.5}px, {mouseY * 0.5}px)"
      ></div>
      <div 
        class="absolute bottom-1/3 left-1/3 w-48 h-48 bg-blue-300/20 dark:bg-blue-700/10 rounded-full blur-2xl"
        style="transform: translate({mouseX * -0.3}px, {mouseY * -0.3}px)"
      ></div>
    {/if}
  </div>

  <!-- Main Content Container -->
  <div class="relative z-10 w-full max-w-7xl mx-auto px-6 sm:px-8 lg:px-12">
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16 items-center">
      
      <!-- Left Content -->
      <div class="lg:col-span-6 space-y-8">
        
        <!-- Status Badge -->
        {#if visibleElements.badge && mounted}
          <div 
            in:fade={{ duration: 600, easing: cubicOut }}
            class="inline-flex items-center gap-3"
          >
            <div class="inline-flex items-center gap-3 px-6 py-3 rounded-full bg-white/80 dark:bg-gray-800/80 backdrop-blur-md border border-purple-200/50 dark:border-purple-700/50 shadow-lg">
              <div class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span class="text-sm font-bold tracking-wide bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                {$t('hero.badge.live', { default: 'LIVE NOW' })}
              </span>
            </div>
            <span class="text-sm font-medium text-gray-600 dark:text-gray-400">
              {$t('hero.badge.count', { default: '24 Active Auctions' })}
            </span>
          </div>
        {/if}
        
        <!-- Main Headline with Gradient -->
        {#if visibleElements.headline && mounted}
          <h1 
            in:fly={{ y: prefersReducedMotion ? 0 : 30, duration: 800, delay: 200 }}
            class="text-5xl sm:text-6xl lg:text-7xl font-black leading-[0.95] tracking-tight bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent {isRTL ? 'text-right' : 'text-left'}"
          >
            {$t('hero.headline', { default: 'Premium Real Estate Auctions' })}
          </h1>
        {/if}
        
        <!-- Subheadline -->
        {#if visibleElements.subheadline && mounted}
          <p 
            in:fly={{ y: prefersReducedMotion ? 0 : 20, duration: 800, delay: 300 }}
            class="text-lg leading-relaxed text-gray-600 dark:text-gray-300 max-w-lg {isRTL ? 'text-right' : 'text-left'}"
          >
            {$t('hero.subheadline', { default: 'Discover exclusive properties through transparent bidding. Join thousands of successful buyers and sellers.' })}
          </p>
        {/if}

        <!-- CTA Buttons -->
        {#if visibleElements.cta && mounted}
          <div 
            in:fly={{ y: prefersReducedMotion ? 0 : 20, duration: 800, delay: 400 }}
            class="flex flex-col sm:flex-row gap-4 pt-4"
          >
            <Button 
              href="/auctions"
              variant="primary"
              size="large"
              class="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white border-0 shadow-xl hover:shadow-2xl transform hover:-translate-y-1 transition-all duration-300 font-bold px-8 py-4 rounded-xl"
            >
              {$t('hero.cta.primary', { default: 'Start Bidding' })}
              <svg 
                class="w-5 h-5 ml-2 rtl:ml-0 rtl:mr-2" 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
                slot="iconRight"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </Button>

            <Button 
              href="/properties"
              variant="outline"
              size="large"
              class="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border-2 border-purple-300 dark:border-purple-700 text-purple-700 dark:text-purple-300 hover:bg-purple-50 dark:hover:bg-purple-900/30 font-bold px-8 py-4 rounded-xl shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-300"
            >
              {$t('hero.cta.secondary', { default: 'View Properties' })}
            </Button>
          </div>
        {/if}

        <!-- Metrics Row -->
        {#if visibleElements.metrics && mounted}
          <div 
            in:fade={{ duration: 700, easing: cubicOut }}
            class="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-8"
          >
            {#each getMetrics() as metric, index}
              <div 
                class="text-center p-4 rounded-2xl bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border border-purple-200/50 dark:border-purple-700/50 shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-1"
                in:scale={{ duration: 500, delay: index * 100, easing: cubicOut }}
              >
                <span class="block text-2xl font-black bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                  {metric.value}
                </span>
                <span class="block text-xs font-medium text-gray-600 dark:text-gray-400 mt-1">
                  {metric.label}
                </span>
              </div>
            {/each}
          </div>
        {/if}
      </div>

      <!-- Right Content - Illustration -->
      <div class="lg:col-span-6 space-y-8">
        {#if visibleElements.illustration && mounted}
          <!-- Real Estate Auction Illustration -->
          <div 
            in:scale={{ duration: 1000, delay: 500, easing: cubicOut }}
            class="relative w-full aspect-square max-w-md mx-auto"
          >
            <svg viewBox="0 0 400 400" class="w-full h-full">
              <defs>
                <linearGradient id="heroGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" class="text-purple-400" stop-color="currentColor" stop-opacity="0.8" />
                  <stop offset="100%" class="text-blue-500" stop-color="currentColor" stop-opacity="0.6" />
                </linearGradient>
                <linearGradient id="heroAccent" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" class="text-purple-600" stop-color="currentColor" />
                  <stop offset="100%" class="text-blue-600" stop-color="currentColor" />
                </linearGradient>
              </defs>
              
              <g stroke="url(#heroGrad)" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round">
                <!-- Modern Building Complex -->
                <path d="M100 350 L100 150 Q150 120 200 150 L200 350" />
                <path d="M200 350 L200 180 L280 160 L280 350" />
                
                <!-- Windows -->
                {#each Array(6) as _, i}
                  <rect 
                    x={120 + (i % 3) * 25} 
                    y={180 + Math.floor(i / 3) * 40} 
                    width="15" 
                    height="20" 
                    rx="2"
                  />
                {/each}
                
                <!-- Auction Gavel -->
                <g stroke="url(#heroAccent)" stroke-width="3">
                  <line x1="320" y1="100" x2="360" y2="60" />
                  <rect x="310" y="95" width="20" height="10" rx="2" />
                  <circle cx="315" cy="110" r="3" fill="url(#heroAccent)" />
                </g>
                
                <!-- Floating bid amounts -->
                <g fill="url(#heroAccent)" fill-opacity="0.2" stroke="url(#heroAccent)">
                  <rect x="50" y="80" width="60" height="30" rx="15" />
                  <text x="80" y="100" text-anchor="middle" font-size="14" font-weight="bold" fill="url(#heroAccent)">$450K</text>
                </g>
                
                <g fill="url(#heroAccent)" fill-opacity="0.2" stroke="url(#heroAccent)">
                  <rect x="290" y="200" width="60" height="30" rx="15" />
                  <text x="320" y="220" text-anchor="middle" font-size="14" font-weight="bold" fill="url(#heroAccent)">$380K</text>
                </g>
              </g>
            </svg>
          </div>
        {/if}

        <!-- Feature Cards -->
        {#if visibleElements.features && mounted}
          <div class="grid grid-cols-3 gap-4">
            {#each getFeatures() as feature, index}
              <div 
                in:scale={{ duration: 500, delay: 700 + index * 100, easing: cubicOut }}
                class="text-center p-4 rounded-2xl bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm hover:bg-white/80 dark:hover:bg-gray-800/80 transition-all duration-300"
              >
                <div class="w-12 h-12 mx-auto mb-2 rounded-xl bg-gradient-to-br from-purple-500/20 to-blue-500/20 flex items-center justify-center">
                  {#if feature.icon === 'shield'}
                    <svg class="w-6 h-6 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                    </svg>
                  {:else if feature.icon === 'bolt'}
                    <svg class="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  {:else}
                    <svg class="w-6 h-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192l-3.536 3.536M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-5 0a4 4 0 11-8 0 4 4 0 018 0z" />
                    </svg>
                  {/if}
                </div>
                <h4 class="text-sm font-bold text-gray-900 dark:text-white mb-1">{feature.title}</h4>
                <p class="text-xs text-gray-600 dark:text-gray-400">{feature.desc}</p>
              </div>
            {/each}
          </div>
        {/if}
      </div>
    </div>
  </div>
</section>

<style>
  /* Respect reduced motion */
  @media (prefers-reduced-motion: reduce) {
    * {
      animation-duration: 0.01ms !important;
      animation-iteration-count: 1 !important;
      transition-duration: 0.01ms !important;
    }
  }
</style>