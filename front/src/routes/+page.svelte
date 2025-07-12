<script>
  import { onMount } from 'svelte';
  import { fade, fly, scale } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';
  import { locale } from '$lib/i18n/config.js';
  import { user } from '$lib/stores/user';
  
  let mounted = false;
  let scrollY = 0;
  let prefersReducedMotion = false;
  
  // RTL support
  $: isRTL = $locale === 'ar';
  
  // Content structure with translations
  const content = {
    en: {
      hero: {
        badge: "Trusted by 50K+ Users",
        title: {
          line1: "Find Your Dream",
          line2: "Property"
        },
        subtitle: "Explore premium real estate opportunities through transparent auctions and direct listings. Your perfect property is just a click away.",
        cta: {
          primary: "Browse Properties",
          secondary: "View Auctions"
        },
        stats: [
          { value: "2.5K+", label: "Properties" },
          { value: "847M", label: "Total Value" },
          { value: "98%", label: "Success Rate" },
          { value: "45+", label: "Cities" }
        ],
        features: {
          verified: "Verified",
          secure: "Secure",
          instant: "Instant"
        }
      }
    },
    ar: {
      hero: {
        badge: "موثوق من 50ألف+ مستخدم",
        title: {
          line1: "اعثر على",
          line2: "عقار أحلامك"
        },
        subtitle: "استكشف فرص العقارات المميزة من خلال المزادات الشفافة والقوائم المباشرة. عقارك المثالي على بعد نقرة واحدة.",
        cta: {
          primary: "تصفح العقارات",
          secondary: "عرض المزادات"
        },
        stats: [
          { value: "2.5ألف+", label: "عقار" },
          { value: "847م", label: "القيمة الكلية" },
          { value: "98%", label: "معدل النجاح" },
          { value: "45+", label: "مدينة" }
        ],
        features: {
          verified: "موثق",
          secure: "آمن",
          instant: "فوري"
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
  <title>{isRTL ? 'منصة العقارات المتميزة' : 'Premium Real Estate Platform'}</title>
  <meta name="description" content="{getText('hero.subtitle')}">
</svelte:head>

<svelte:window bind:scrollY />

<div class="min-h-screen bg-gray-50 dark:bg-gray-950 overflow-hidden" dir={isRTL ? 'rtl' : 'ltr'}>
  {#if mounted}
    <!-- Hero Section -->
    <section class="relative min-h-screen flex items-center">
      <!-- Enhanced Background with Better Dark Mode -->
      <div class="absolute inset-0">
        <div 
          class="absolute inset-0 background-div"
          style="background: linear-gradient(135deg, 
                 var(--color-neutral-50) 0%, 
                 var(--color-primary-50) 25%, 
                 var(--color-secondary-50) 50%, 
                 var(--color-neutral-50) 100%);"
        ></div>
        <div class="absolute inset-0 overflow-hidden">
          <!-- Enhanced Floating Shapes -->
          <div 
            class="absolute -top-1/3 -left-1/3 w-[80%] h-[80%] rounded-full shape-1"
            style="background: radial-gradient(circle at center, 
                   var(--color-primary-300) 0%, 
                   var(--color-primary-500) 50%, 
                   transparent 70%);
                   transform: rotate({scrollY * 0.02}deg) scale(1.2);
                   filter: blur(120px);"
          ></div>
          <div 
            class="absolute -bottom-1/3 -right-1/3 w-[70%] h-[70%] rounded-full shape-3"
            style="background: radial-gradient(circle at center, 
                   var(--color-secondary-300) 0%, 
                   var(--color-secondary-500) 50%, 
                   transparent 70%);
                   transform: rotate({-scrollY * 0.02}deg) scale(1.1);
                   filter: blur(100px);"
          ></div>
          <!-- Additional shape for depth -->
          <div 
            class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[60%] h-[60%] rounded-full shape-2"
            style="background: radial-gradient(circle at center, 
                   var(--color-accent-200) 0%, 
                   var(--color-accent-400) 50%, 
                   transparent 70%);
                   transform: rotate({scrollY * 0.01}deg);
                   filter: blur(150px);"
          ></div>
        </div>
      </div>
      
      <!-- Content Container -->
      <div class="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12 items-center">
          
          <!-- Left Content - 40% -->
          <div class="lg:col-span-5 space-y-6 lg:space-y-8">
            <!-- Enhanced Trust Badge -->
            <div
              in:fly={{ y: prefersReducedMotion ? 0 : 20, duration: 600, delay: 200 }}
              class="inline-flex items-center gap-2 px-4 py-2.5 bg-gradient-to-r from-secondary-100 to-secondary-50 dark:from-secondary-900/30 dark:to-secondary-800/20 backdrop-blur-sm rounded-full border border-secondary-300 dark:border-secondary-700 shadow-sm"
            >
              <div class="w-2 h-2 bg-secondary-500 rounded-full animate-pulse"></div>
              <span class="text-xs font-semibold text-secondary-700 dark:text-secondary-300">
                {getText('hero.badge')}
              </span>
            </div>
            
            <!-- Title with Brown Accent -->
            <div class="space-y-2">
              <h1
                in:fly={{ y: prefersReducedMotion ? 0 : 30, duration: 800, delay: 300 }}
                class="text-5xl sm:text-6xl lg:text-7xl xl:text-8xl font-black leading-[0.9] tracking-tight"
              >
                <span class="block text-gray-900 dark:text-white">
                  {getText('hero.title.line1')}
                </span>
                <span class="block text-secondary-600 dark:text-secondary-400 mt-2">
                  {getText('hero.title.line2')}
                </span>
              </h1>
            </div>
            
            <!-- Subtitle -->
            <p
              in:fly={{ y: prefersReducedMotion ? 0 : 20, duration: 800, delay: 400 }}
              class="text-base lg:text-lg leading-relaxed text-gray-600 dark:text-gray-300 max-w-xl"
            >
              {getText('hero.subtitle')}
            </p>
            
            <!-- CTA Buttons -->
            <div
              in:fly={{ y: prefersReducedMotion ? 0 : 20, duration: 800, delay: 500 }}
              class="flex flex-col sm:flex-row gap-3"
            >
              <a 
                href="/properties"
                class="inline-flex items-center justify-center px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-xl shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all duration-200"
              >
                {getText('hero.cta.primary')}
                <svg class="w-4 h-4 {isRTL ? 'mr-2' : 'ml-2'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="{isRTL ? 'M11 19l-7-7 7-7m8 14l-7-7 7-7' : 'M13 5l7 7-7 7M5 12h14'}" />
                </svg>
              </a>
              
              <a 
                href="/auctions"
                class="inline-flex items-center justify-center px-6 py-3 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 font-medium rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm hover:shadow-md transform hover:-translate-y-0.5 transition-all duration-200"
              >
                {getText('hero.cta.secondary')}
              </a>
            </div>
            
            <!-- Stats Grid with Brown Accents -->
            <div
              in:fly={{ y: prefersReducedMotion ? 0 : 20, duration: 800, delay: 600 }}
              class="grid grid-cols-4 gap-4 pt-6"
            >
              {#each getText('hero.stats') as stat, i}
                <div class="text-center">
                  <div class="text-xl sm:text-2xl font-bold text-secondary-600 dark:text-secondary-400">
                    {stat.value}
                  </div>
                  <div class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                    {stat.label}
                  </div>
                </div>
              {/each}
            </div>
          </div>
          
          <!-- Right SVG Animation - 60% -->
          <div class="lg:col-span-7 relative">
            <div
              in:scale={{ duration: 1000, delay: 300, easing: cubicOut }}
              class="relative w-full"
            >
              <svg viewBox="0 0 900 800" class="w-full h-full max-w-[1000px] mx-auto">
                <defs>
                  <!-- Enhanced Gradients -->
                  <linearGradient id="primaryGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:var(--color-primary-400);stop-opacity:1" />
                    <stop offset="100%" style="stop-color:var(--color-primary-600);stop-opacity:1" />
                  </linearGradient>
                  
                  <linearGradient id="secondaryGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:var(--color-secondary-400);stop-opacity:1" />
                    <stop offset="100%" style="stop-color:var(--color-secondary-600);stop-opacity:1" />
                  </linearGradient>
                  
                  <linearGradient id="successGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:var(--color-success-400);stop-opacity:1" />
                    <stop offset="100%" style="stop-color:var(--color-success-600);stop-opacity:1" />
                  </linearGradient>

                  <linearGradient id="windowGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" style="stop-color:#ffffff;stop-opacity:0.9" />
                    <stop offset="100%" style="stop-color:#ffffff;stop-opacity:0.4" />
                  </linearGradient>
                  
                  <!-- Enhanced Filters -->
                  <filter id="softShadow">
                    <feDropShadow dx="0" dy="6" stdDeviation="8" flood-color="rgba(0,0,0,0.15)"/>
                  </filter>
                  
                  <filter id="glow">
                    <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
                    <feMerge>
                      <feMergeNode in="coloredBlur"/>
                      <feMergeNode in="SourceGraphic"/>
                    </feMerge>
                  </filter>
                </defs>
                
                <!-- City Skyline Group -->
                <g transform="translate(450, 400)">
                  
                  <!-- Background Buildings -->
                  <g opacity="0.15">
                    <rect x="-380" y="-100" width="60" height="200" fill="var(--color-neutral-400)" />
                    <rect x="-300" y="-140" width="80" height="240" fill="var(--color-neutral-400)" />
                    <rect x="280" y="-120" width="70" height="220" fill="var(--color-neutral-400)" />
                  </g>
                  
                  <!-- Left Office Building -->
                  <g filter="url(#softShadow)" transform="translate(-200, 0)">
                    <rect x="-70" y="-160" width="140" height="310" rx="4" fill="url(#secondaryGradient)">
                      <animateTransform
                        attributeName="transform"
                        type="translate"
                        values="0,0; 0,-8; 0,0"
                        dur="8s"
                        repeatCount="indefinite" />
                    </rect>
                    <!-- Windows Grid -->
                    <g opacity="0.8">
                      {#each Array(15) as _, i}
                        <rect 
                          x={-60 + (i % 3) * 45} 
                          y={-150 + Math.floor(i / 3) * 55} 
                          width="35" 
                          height="45" 
                          fill="url(#windowGradient)"
                          rx="2">
                          <animate 
                            attributeName="opacity" 
                            values="0.4;0.9;0.6;0.9;0.4" 
                            dur="6s" 
                            begin="{i * 0.3}s"
                            repeatCount="indefinite" />
                        </rect>
                      {/each}
                    </g>
                  </g>
                  
                  <!-- Central Tower -->
                  <g filter="url(#softShadow)">
                    <rect x="-80" y="-200" width="160" height="350" rx="4" fill="url(#primaryGradient)">
                      <animateTransform
                        attributeName="transform"
                        type="translate"
                        values="0,0; 0,-10; 0,0"
                        dur="7s"
                        repeatCount="indefinite" />
                    </rect>
                    <!-- Window Pattern -->
                    <g opacity="0.8">
                      {#each Array(18) as _, i}
                        <rect 
                          x={-70 + (i % 3) * 50} 
                          y={-190 + Math.floor(i / 3) * 55} 
                          width="40" 
                          height="45" 
                          fill="url(#windowGradient)"
                          rx="2">
                          <animate 
                            attributeName="opacity" 
                            values="0.5;1;0.7;1;0.5" 
                            dur="5s" 
                            begin="{i * 0.2}s"
                            repeatCount="indefinite" />
                        </rect>
                      {/each}
                    </g>
                    <!-- Rooftop -->
                    <rect x="-40" y="-210" width="80" height="10" rx="5" fill="var(--color-primary-700)" />
                    <circle cx="0" cy="-215" r="3" fill="var(--color-danger-500)">
                      <animate attributeName="opacity" values="1;0.2;1" dur="2s" repeatCount="indefinite" />
                    </circle>
                  </g>
                  
                  <!-- Right Residential Building -->
                  <g filter="url(#softShadow)" transform="translate(200, 20)">
                    <rect x="-60" y="-140" width="120" height="290" rx="4" fill="url(#successGradient)">
                      <animateTransform
                        attributeName="transform"
                        type="translate"
                        values="0,0; 0,-6; 0,0"
                        dur="7.5s"
                        repeatCount="indefinite" />
                    </rect>
                    <!-- Balconies and Windows -->
                    {#each Array(5) as _, i}
                      <g transform="translate(0, {-120 + i * 50})">
                        <rect x="-50" y="0" width="100" height="3" fill="var(--color-success-700)" rx="1" />
                        <rect x="-45" y="5" width="40" height="35" fill="url(#windowGradient)" rx="2" opacity="0.8" />
                        <rect x="5" y="5" width="40" height="35" fill="url(#windowGradient)" rx="2" opacity="0.8" />
                      </g>
                    {/each}
                  </g>
                  
                  <!-- Enhanced Modern Villa (Left Foreground) -->
                  <g filter="url(#softShadow)" transform="translate(-320, 100)">
                    <!-- Main Structure -->
                    <rect x="-55" y="-35" width="110" height="75" fill="var(--color-neutral-100)" rx="4" />
                    <!-- Large Glass Windows -->
                    <rect x="-50" y="-30" width="45" height="55" fill="url(#windowGradient)" rx="2" opacity="0.8" />
                    <rect x="5" y="-30" width="45" height="55" fill="url(#windowGradient)" rx="2" opacity="0.8" />
                    <!-- Modern Flat Roof -->
                    <rect x="-55" y="-40" width="110" height="5" fill="var(--color-neutral-700)" />
                    <!-- Roof Garden -->
                    <rect x="-30" y="-38" width="20" height="3" fill="var(--color-success-500)" rx="1" />
                    <rect x="10" y="-38" width="20" height="3" fill="var(--color-success-500)" rx="1" />
                    <!-- Entry Door -->
                    <rect x="-12" y="10" width="24" height="30" fill="var(--color-secondary-700)" rx="2" />
                    <!-- Door Handle -->
                    <circle cx="5" cy="25" r="1.5" fill="var(--color-secondary-400)" />
                    <!-- Driveway -->
                    <rect x="-40" y="40" width="80" height="5" fill="var(--color-neutral-400)" opacity="0.5" />
                    <!-- Garden -->
                    <ellipse cx="-35" cy="45" rx="15" ry="8" fill="var(--color-success-300)" opacity="0.4" />
                    <ellipse cx="35" cy="45" rx="15" ry="8" fill="var(--color-success-300)" opacity="0.4" />
                    <!-- Small Trees -->
                    <circle cx="-35" cy="40" r="5" fill="var(--color-success-500)" opacity="0.6" />
                    <circle cx="35" cy="40" r="5" fill="var(--color-success-500)" opacity="0.6" />
                  </g>
                  
                  <!-- Enhanced Modern House (Right Foreground) -->
                  <g filter="url(#softShadow)" transform="translate(320, 90)">
                    <!-- House Base with Pitched Roof -->
                    <path d="M -60 40 L -60 -20 L 0 -50 L 60 -20 L 60 40 Z" fill="url(#secondaryGradient)" />
                    <!-- Roof Ridge -->
                    <line x1="-60" y1="-20" x2="0" y2="-50" stroke="var(--color-secondary-700)" stroke-width="2" />
                    <line x1="0" y1="-50" x2="60" y2="-20" stroke="var(--color-secondary-700)" stroke-width="2" />
                    <!-- Chimney -->
                    <rect x="25" y="-40" width="15" height="25" fill="var(--color-secondary-600)" rx="1" />
                    <!-- Large Windows -->
                    <rect x="-45" y="-10" width="35" height="40" fill="url(#windowGradient)" rx="2" opacity="0.8" />
                    <rect x="10" y="-10" width="35" height="40" fill="url(#windowGradient)" rx="2" opacity="0.8" />
                    <!-- Window Frames -->
                    <line x1="-45" y1="10" x2="-10" y2="10" stroke="var(--color-secondary-700)" stroke-width="1" />
                    <line x1="10" y1="10" x2="45" y2="10" stroke="var(--color-secondary-700)" stroke-width="1" />
                    <line x1="-27.5" y1="-10" x2="-27.5" y2="30" stroke="var(--color-secondary-700)" stroke-width="1" />
                    <line x1="27.5" y1="-10" x2="27.5" y2="30" stroke="var(--color-secondary-700)" stroke-width="1" />
                    <!-- Entry Door -->
                    <rect x="-12" y="5" width="24" height="35" fill="var(--color-secondary-800)" rx="2" />
                    <!-- Door Details -->
                    <rect x="-10" y="10" width="20" height="15" fill="var(--color-secondary-700)" rx="1" opacity="0.5" />
                    <circle cx="6" cy="22" r="1" fill="var(--color-secondary-400)" />
                    <!-- Porch -->
                    <rect x="-20" y="40" width="40" height="3" fill="var(--color-secondary-600)" />
                    <!-- Front Garden -->
                    <ellipse cx="0" cy="48" rx="50" ry="10" fill="var(--color-success-300)" opacity="0.3" />
                    <!-- Bushes -->
                    <ellipse cx="-30" cy="42" rx="8" ry="4" fill="var(--color-success-500)" opacity="0.5" />
                    <ellipse cx="30" cy="42" rx="8" ry="4" fill="var(--color-success-500)" opacity="0.5" />
                  </g>
                </g>
                
                <!-- Enhanced Property Info Cards -->
                {#each [
                  { x: 280, y: 220, price: "$450K", type: "Villa", delay: "0s" },
                  { x: 620, y: 200, price: "$2.8M", type: "Luxury", delay: "1s" },
                  { x: 400, y: 520, price: "$320K", type: "Condo", delay: "2s" },
                  { x: 520, y: 420, price: "$1.2M", type: "Office", delay: "3s" }
                ] as tag}
                  <g transform="translate({tag.x}, {tag.y})">
                    <rect 
                      x="-52" 
                      y="-18" 
                      width="104" 
                      height="36" 
                      rx="18" 
                      fill="white"
                      stroke="var(--color-gray-200)"
                      stroke-width="1"
                      filter="url(#softShadow)">
                      <animate
                        attributeName="y"
                        values="-18;-24;-18"
                        dur="4s"
                        begin={tag.delay}
                        repeatCount="indefinite" />
                    </rect>
                    <text 
                      x="-35" 
                      y="6" 
                      text-anchor="start" 
                      fill="var(--color-secondary-700)" 
                      font-size="15" 
                      font-weight="700"
                      font-family="Inter, sans-serif">
                      {tag.price}
                    </text>
                    <text 
                      x="35" 
                      y="6" 
                      text-anchor="end" 
                      fill="var(--color-gray-600)" 
                      font-size="13" 
                      font-weight="500"
                      font-family="Inter, sans-serif">
                      {tag.type}
                    </text>
                  </g>
                {/each}
                
                <!-- Enhanced Feature Badges -->
                <g transform="translate(450, 700)">
                  {#each [
                    { x: -150, feature: 'verified', icon: '✓', color: 'success' },
                    { x: 0, feature: 'secure', icon: '🔒', color: 'primary' },
                    { x: 150, feature: 'instant', icon: '⚡', color: 'warning' }
                  ] as item, i}
                    <g transform="translate({item.x}, 0)">
                      <rect 
                        x="-50" 
                        y="-16" 
                        width="100" 
                        height="32" 
                        rx="16" 
                        fill="white"
                        stroke="var(--color-{item.color}-300)"
                        stroke-width="1.5"
                        filter="url(#softShadow)">
                        <animate 
                          attributeName="opacity" 
                          values="0.9;1;0.9" 
                          dur="3s" 
                          begin="{i * 0.5}s" 
                          repeatCount="indefinite" />
                      </rect>
                      <!-- Badge Background -->
                      <circle cx="-30" cy="0" r="10" fill="var(--color-{item.color}-100)" />
                      <text 
                        x="-30" 
                        y="6" 
                        text-anchor="middle" 
                        font-size="16" 
                        fill="var(--color-{item.color}-600)">
                        {item.icon}
                      </text>
                      <text 
                        x="5" 
                        y="6" 
                        text-anchor="middle" 
                        font-size="13" 
                        fill="var(--color-{item.color}-700)" 
                        font-weight="600"
                        font-family="Inter, sans-serif">
                        {getText(`hero.features.${item.feature}`)}
                      </text>
                    </g>
                  {/each}
                </g>
                
                <!-- Subtle Animated Particles -->
                <g opacity="0.3">
                  {#each Array(20) as _, i}
                    <circle 
                      cx="{150 + Math.random() * 600}" 
                      cy="{100 + Math.random() * 500}" 
                      r="{0.5 + Math.random() * 0.5}"
                      fill="var(--color-primary-400)">
                      <animate
                        attributeName="opacity"
                        values="0;0.8;0"
                        dur="{4 + Math.random() * 3}s"
                        begin="{Math.random() * 3}s"
                        repeatCount="indefinite" />
                      <animateTransform
                        attributeName="transform"
                        type="translate"
                        values="0,0; {Math.random() * 20 - 10},{-Math.random() * 30}; 0,0"
                        dur="{4 + Math.random() * 3}s"
                        begin="{Math.random() * 3}s"
                        repeatCount="indefinite" />
                    </circle>
                  {/each}
                </g>
              </svg>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Quick Actions Section for Property Management Users -->
    {#if $user && ($user.role === 'landlord' || $user.role === 'property_manager' || $user.role === 'appraiser' || $user.is_staff)}
      <section class="py-16 bg-gray-50 dark:bg-gray-800">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div class="text-center mb-12">
            <h2 class="text-3xl font-bold text-gray-900 dark:text-white">
              Property Management Hub
            </h2>
            <p class="mt-4 text-lg text-gray-600 dark:text-gray-400">
              Quick access to your property management tools and insights
            </p>
          </div>
          
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <!-- Financial Management -->
            <div class="bg-white dark:bg-gray-900 rounded-xl shadow-lg p-6 hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1">
              <div class="flex items-center mb-4">
                <div class="w-12 h-12 bg-green-100 dark:bg-green-900/20 rounded-lg flex items-center justify-center">
                  <svg class="w-6 h-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                  </svg>
                </div>
                <h3 class="ml-4 text-lg font-semibold text-gray-900 dark:text-white">Financial Tracking</h3>
              </div>
              <p class="text-gray-600 dark:text-gray-400 mb-4">
                Monitor income, expenses, and track your property portfolio performance.
              </p>
              <div class="flex space-x-3">
                <a href="/core/financial" class="flex-1 bg-green-600 hover:bg-green-700 text-white text-center py-2 px-4 rounded-lg transition-colors duration-200 text-sm font-medium">
                  View Financial Dashboard
                </a>
              </div>
            </div>

            <!-- Maintenance Management -->
            <div class="bg-white dark:bg-gray-900 rounded-xl shadow-lg p-6 hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1">
              <div class="flex items-center mb-4">
                <div class="w-12 h-12 bg-orange-100 dark:bg-orange-900/20 rounded-lg flex items-center justify-center">
                  <svg class="w-6 h-6 text-orange-600 dark:text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  </svg>
                </div>
                <h3 class="ml-4 text-lg font-semibold text-gray-900 dark:text-white">Maintenance Requests</h3>
              </div>
              <p class="text-gray-600 dark:text-gray-400 mb-4">
                Manage property maintenance, coordinate with vendors, and track repair status.
              </p>
              <div class="flex space-x-3">
                <a href="/core/maintenance" class="flex-1 bg-orange-600 hover:bg-orange-700 text-white text-center py-2 px-4 rounded-lg transition-colors duration-200 text-sm font-medium">
                  Manage Maintenance
                </a>
              </div>
            </div>

            <!-- Contract Management -->
            <div class="bg-white dark:bg-gray-900 rounded-xl shadow-lg p-6 hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1">
              <div class="flex items-center mb-4">
                <div class="w-12 h-12 bg-blue-100 dark:bg-blue-900/20 rounded-lg flex items-center justify-center">
                  <svg class="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <h3 class="ml-4 text-lg font-semibold text-gray-900 dark:text-white">Contracts & Leases</h3>
              </div>
              <p class="text-gray-600 dark:text-gray-400 mb-4">
                Create, manage, and track lease agreements and vendor contracts.
              </p>
              <div class="flex space-x-3">
                <a href="/core/contracts" class="flex-1 bg-blue-600 hover:bg-blue-700 text-white text-center py-2 px-4 rounded-lg transition-colors duration-200 text-sm font-medium">
                  View Contracts
                </a>
              </div>
            </div>

            <!-- Rental Management -->
            <div class="bg-white dark:bg-gray-900 rounded-xl shadow-lg p-6 hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1">
              <div class="flex items-center mb-4">
                <div class="w-12 h-12 bg-purple-100 dark:bg-purple-900/20 rounded-lg flex items-center justify-center">
                  <svg class="w-6 h-6 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z" />
                  </svg>
                </div>
                <h3 class="ml-4 text-lg font-semibold text-gray-900 dark:text-white">Rental Properties</h3>
              </div>
              <p class="text-gray-600 dark:text-gray-400 mb-4">
                Manage your rental properties, tenants, and lease agreements.
              </p>
              <div class="flex space-x-3">
                <a href="/core/rentals" class="flex-1 bg-purple-600 hover:bg-purple-700 text-white text-center py-2 px-4 rounded-lg transition-colors duration-200 text-sm font-medium">
                  Manage Rentals
                </a>
              </div>
            </div>

            <!-- Analytics & Reports -->
            <div class="bg-white dark:bg-gray-900 rounded-xl shadow-lg p-6 hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1">
              <div class="flex items-center mb-4">
                <div class="w-12 h-12 bg-indigo-100 dark:bg-indigo-900/20 rounded-lg flex items-center justify-center">
                  <svg class="w-6 h-6 text-indigo-600 dark:text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
                <h3 class="ml-4 text-lg font-semibold text-gray-900 dark:text-white">Analytics & Reports</h3>
              </div>
              <p class="text-gray-600 dark:text-gray-400 mb-4">
                Get insights into your property performance with detailed analytics.
              </p>
              <div class="flex space-x-3">
                <a href="/core/analytics" class="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white text-center py-2 px-4 rounded-lg transition-colors duration-200 text-sm font-medium">
                  View Analytics
                </a>
              </div>
            </div>

            <!-- Quick Access Dashboard -->
            <div class="bg-white dark:bg-gray-900 rounded-xl shadow-lg p-6 hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1">
              <div class="flex items-center mb-4">
                <div class="w-12 h-12 bg-teal-100 dark:bg-teal-900/20 rounded-lg flex items-center justify-center">
                  <svg class="w-6 h-6 text-teal-600 dark:text-teal-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
                  </svg>
                </div>
                <h3 class="ml-4 text-lg font-semibold text-gray-900 dark:text-white">Management Dashboard</h3>
              </div>
              <p class="text-gray-600 dark:text-gray-400 mb-4">
                Access your comprehensive property management dashboard overview.
              </p>
              <div class="flex space-x-3">
                <a href="/core" class="flex-1 bg-teal-600 hover:bg-teal-700 text-white text-center py-2 px-4 rounded-lg transition-colors duration-200 text-sm font-medium">
                  Go to Dashboard
                </a>
              </div>
            </div>
          </div>
        </div>
      </section>
    {/if}
  {/if}
</div>

<style>
  .background-div {
    opacity: 0.3;
  }
  :global(.dark) .background-div {
    opacity: 0.05;
  }

  .shape-1 {
    opacity: 0.2;
  }
  :global(.dark) .shape-1 {
    opacity: 0.1;
  }

  .shape-2 {
    opacity: 0.1;
  }
  :global(.dark) .shape-2 {
    opacity: 0.05;
  }

  .shape-3 {
    opacity: 0.2;
  }
  :global(.dark) .shape-3 {
    opacity: 0.1;
  }
  
  /* Ensure badge text stays within containers */
  text {
    dominant-baseline: middle;
  }
  
  /* Transform origin for rotation animations */
  .origin-center {
    transform-origin: center;
  }
  
  /* Gradient text for secondary color */
  .text-secondary-600 {
    background: linear-gradient(135deg, var(--color-secondary-500) 0%, var(--color-secondary-700) 100%);
    background-clip: text;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  
  /* Respect reduced motion */
  @media (prefers-reduced-motion: reduce) {
    .animate-pulse {
      animation: none;
    }
  }
  
  /* Ensure proper height on mobile */
  @media (max-width: 1024px) {
    section {
      min-height: auto;
      padding-top: 4rem;
      padding-bottom: 4rem;
    }
  }
</style>