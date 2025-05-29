<!-- src/routes/about/+page.svelte -->
<script>
  import { onMount } from 'svelte';
  import { fade, fly } from 'svelte/transition';
  import { locale } from '$lib/i18n';
  import Button from '$lib/components/ui/Button.svelte';
  
  let mounted = false;
  let scrollY = 0;
  let prefersReducedMotion = false;
  
  // RTL support
  $: isRTL = $locale === 'ar';
  
  // Content structure
  const content = {
    en: {
      hero: {
        title: "We're building the future of real estate",
        description: "Our platform transforms how people buy, sell, and invest in properties through transparent auctions and cutting-edge technology.",
        stats: [
          { number: "50K+", label: "Properties Listed" },
          { number: "98%", label: "Success Rate" },
          { number: "15", label: "Countries" }
        ]
      },
      story: {
        title: "Our Story",
        content: "Born from a vision to democratize real estate investing, we started with a simple belief: everyone should have access to transparent property transactions. What began as a small team in 2019 has grown into a global platform serving thousands of satisfied customers.",
        highlight: "We believe in transparency, innovation, and building trust through every interaction."
      },
      values: {
        title: "What drives us",
        items: [
          {
            title: "Transparency First",
            description: "Every bid, every transaction, every detail - open and verifiable."
          },
          {
            title: "Innovation Always", 
            description: "Pushing boundaries with technology to simplify complex processes."
          },
          {
            title: "Trust Through Action",
            description: "Building lasting relationships by delivering on our promises."
          }
        ]
      },
      team: {
        title: "Leadership",
        subtitle: "Guided by experience, driven by purpose",
        members: [
          { name: "Sarah Chen", role: "CEO & Co-founder", bio: "20+ years in proptech" },
          { name: "Marcus Johnson", role: "CTO & Co-founder", bio: "Former Google engineer" },
          { name: "Elena Rodriguez", role: "Head of Operations", bio: "Real estate veteran" }
        ]
      },
      cta: {
        title: "Ready to join our journey?",
        description: "Experience the future of real estate auctions today.",
        primaryBtn: "Get Started",
        secondaryBtn: "Talk to Sales"
      }
    },
    ar: {
      hero: {
        title: "نبني مستقبل العقارات",
        description: "منصتنا تحول كيفية شراء وبيع والاستثمار في العقارات من خلال المزادات الشفافة والتكنولوجيا المتطورة.",
        stats: [
          { number: "50+", label: "ألف عقار" },
          { number: "98%", label: "معدل النجاح" },
        ]
      },
      story: {
        title: "قصتنا",
        content: "وُلدت من رؤية لإضفاء الطابع الديمقراطي على الاستثمار العقاري، بدأنا بإيمان بسيط: يجب أن يتمتع الجميع بإمكانية الوصول إلى معاملات عقارية شفافة. ما بدأ كفريق صغير في 2019 نما إلى منصة عالمية تخدم آلاف العملاء الراضين.",
        highlight: "نؤمن بالشفافية والابتكار وبناء الثقة من خلال كل تفاعل."
      },
      values: {
        title: "ما يحركنا",
        items: [
          {
            title: "الشفافية أولاً",
            description: "كل عرض، كل معاملة، كل تفصيل - مفتوح وقابل للتحقق."
          },
          {
            title: "الابتكار دائماً",
            description: "دفع الحدود بالتكنولوجيا لتبسيط العمليات المعقدة."
          },
          {
            title: "الثقة من خلال العمل",
            description: "بناء علاقات دائمة من خلال الوفاء بوعودنا."
          }
        ]
      },
      team: {
        title: "القيادة",
        subtitle: "موجهون بالخبرة، مدفوعون بالهدف",
        members: [
          { name: "سارة تشين", role: "الرئيس التنفيذي والمؤسس المشارك", bio: "20+ سنة في تقنية العقارات" },
          { name: "ماركوس جونسون", role: "المدير التقني والمؤسس المشارك", bio: "مهندس سابق في جوجل" },
          { name: "إيلينا رودريغيز", role: "رئيس العمليات", bio: "خبيرة عقارات" }
        ]
      },
      cta: {
        title: "مستعد للانضمام إلى رحلتنا؟",
        description: "جرب مستقبل مزادات العقارات اليوم.",
        primaryBtn: "ابدأ الآن",
        secondaryBtn: "تحدث إلى المبيعات"
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
  <title>About Us | Transforming Real Estate Through Innovation</title>
  <meta name="description" content="Learn about our mission to democratize real estate through transparent auctions and innovative technology.">
</svelte:head>

<svelte:window bind:scrollY />

<div class="relative overflow-hidden" dir={isRTL ? 'rtl' : 'ltr'}>
  
  {#if mounted}
    <!-- Hero Section with Real Estate Theme -->
    <section class="relative min-h-screen flex items-center py-20 sm:py-24 lg:py-32">
      <div class="relative z-10 w-full max-w-7xl mx-auto px-6 sm:px-8 lg:px-12">
        <!-- Asymmetric Grid: 5/7 split -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16 items-center">
          
          <!-- Left Content - 5 columns -->
          <div class="lg:col-span-5 space-y-8">
            <h1
              in:fly={{ y: prefersReducedMotion ? 0 : 30, duration: 800, delay: 200 }}
              class="text-5xl sm:text-6xl lg:text-7xl font-bold leading-[0.95] tracking-tight text-slate-900 dark:text-white"
            >
              {getText('hero.title')}
            </h1>
            
            <p
              in:fly={{ y: prefersReducedMotion ? 0 : 20, duration: 800, delay: 300 }}
              class="text-lg leading-relaxed text-slate-600 dark:text-slate-300 max-w-md"
            >
              {getText('hero.description')}
            </p>
            
            <!-- Stats with animated underlines -->
            <div
              in:fly={{ y: prefersReducedMotion ? 0 : 20, duration: 800, delay: 400 }}
              class="flex flex-wrap gap-8 pt-4"
            >
              {#each getText('hero.stats') as stat, i}
                <div class="text-center relative">
                  <div class="text-3xl font-bold text-slate-900 dark:text-white">
                    {stat.number}
                  </div>
                  <div class="text-sm text-slate-500 dark:text-slate-400 mt-1">
                    {stat.label}
                  </div>
                  <!-- Animated underline -->
                  <div class="expand-line-stat w-full h-0.5 bg-gradient-to-r from-amber-500 to-orange-500 mt-2 motion-reduce:w-full" style="animation-delay: {(i + 1) * 200 + 600}ms;"></div>
                </div>
              {/each}
            </div>
          </div>
          
          <!-- Right Visual - 7 columns with Real Estate SVG -->
          <div class="lg:col-span-7 relative">
            <div
              in:fly={{ x: prefersReducedMotion ? 0 : 50, duration: 1000, delay: 500 }}
              class="relative"
            >
              <!-- Real Estate Auction Illustration -->
              <div class="relative w-full aspect-square max-w-lg mx-auto">
                <svg viewBox="0 0 400 400" class="w-full h-full">
                  <defs>
                    <linearGradient id="buildingGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                      <stop offset="0%" class="text-amber-500/80" stop-color="currentColor" />
                      <stop offset="100%" class="text-orange-500/60" stop-color="currentColor" />
                    </linearGradient>
                    <linearGradient id="accentGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                      <stop offset="0%" class="text-amber-600" stop-color="currentColor" />
                      <stop offset="100%" class="text-orange-600" stop-color="currentColor" />
                    </linearGradient>
                  </defs>
                  
                  <g stroke="url(#buildingGrad)" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round">
                    <!-- Main Building -->
                    <rect 
                      x="120" y="180" width="160" height="180" 
                      class="draw-line-hero motion-reduce:opacity-100"
                      style="animation-delay: 1s;"
                    />
                    
                    <!-- Building Roof -->
                    <polygon 
                      points="110,180 200,130 290,180" 
                      class="draw-line-hero motion-reduce:opacity-100"
                      style="animation-delay: 1.5s;"
                    />
                    
                    <!-- Windows Grid -->
                    <rect 
                      x="140" y="200" width="25" height="25" 
                      class="draw-line-hero motion-reduce:opacity-100"
                      style="animation-delay: 2s;"
                    />
                    <rect 
                      x="175" y="200" width="25" height="25" 
                      class="draw-line-hero motion-reduce:opacity-100"
                      style="animation-delay: 2.2s;"
                    />
                    <rect 
                      x="210" y="200" width="25" height="25" 
                      class="draw-line-hero motion-reduce:opacity-100"
                      style="animation-delay: 2.4s;"
                    />
                    <rect 
                      x="245" y="200" width="25" height="25" 
                      class="draw-line-hero motion-reduce:opacity-100"
                      style="animation-delay: 2.6s;"
                    />
                    
                    <!-- Second row of windows -->
                    <rect 
                      x="140" y="240" width="25" height="25" 
                      class="draw-line-hero motion-reduce:opacity-100"
                      style="animation-delay: 2.8s;"
                    />
                    <rect 
                      x="175" y="240" width="25" height="25" 
                      class="draw-line-hero motion-reduce:opacity-100"
                      style="animation-delay: 3s;"
                    />
                    <rect 
                      x="210" y="240" width="25" height="25" 
                      class="draw-line-hero motion-reduce:opacity-100"
                      style="animation-delay: 3.2s;"
                    />
                    <rect 
                      x="245" y="240" width="25" height="25" 
                      class="draw-line-hero motion-reduce:opacity-100"
                      style="animation-delay: 3.4s;"
                    />
                    
                    <!-- Door -->
                    <rect 
                      x="185" y="300" width="30" height="60" 
                      class="draw-line-hero motion-reduce:opacity-100"
                      style="animation-delay: 3.6s;"
                    />
                    
                    <!-- Auction Gavel -->
                    <g stroke="url(#accentGrad)" stroke-width="3">
                      <!-- Gavel Handle -->
                      <line 
                        x1="320" y1="120" x2="360" y2="80" 
                        class="draw-line-hero motion-reduce:opacity-100"
                        style="animation-delay: 4s;"
                      />
                      <!-- Gavel Head -->
                      <rect 
                        x="310" y="115" width="20" height="10" 
                        class="draw-line-hero motion-reduce:opacity-100"
                        style="animation-delay: 4.2s;"
                      />
                    </g>
                    
                    <!-- Dollar Signs (Auction Bids) -->
                    <g stroke="url(#accentGrad)" stroke-width="2" fill="url(#accentGrad)" fill-opacity="0.2">
                      <text 
                        x="80" y="100" 
                        font-family="serif" 
                        font-size="24" 
                        font-weight="bold"
                        class="draw-text motion-reduce:opacity-100"
                        style="animation-delay: 4.5s;"
                      >$</text>
                      <text 
                        x="340" y="200" 
                        font-family="serif" 
                        font-size="20" 
                        font-weight="bold"
                        class="draw-text motion-reduce:opacity-100"
                        style="animation-delay: 4.7s;"
                      >$</text>
                      <text 
                        x="60" y="280" 
                        font-family="serif" 
                        font-size="18" 
                        font-weight="bold"
                        class="draw-text motion-reduce:opacity-100"
                        style="animation-delay: 4.9s;"
                      >$</text>
                    </g>
                    
                    <!-- Property Lines/Boundaries -->
                    <g stroke="url(#buildingGrad)" stroke-width="1" stroke-dasharray="5,5">
                      <rect 
                        x="80" y="140" width="240" height="240" 
                        class="draw-line-hero motion-reduce:opacity-100"
                        style="animation-delay: 5s;"
                      />
                    </g>
                    
                    <!-- Location Pin -->
                    <g stroke="url(#accentGrad)" stroke-width="2" fill="url(#accentGrad)" fill-opacity="0.3">
                      <circle 
                        cx="200" cy="80" r="15" 
                        class="draw-line-hero motion-reduce:opacity-100"
                        style="animation-delay: 5.2s;"
                      />
                      <polygon 
                        points="200,95 190,110 210,110" 
                        class="draw-line-hero motion-reduce:opacity-100"
                        style="animation-delay: 5.4s;"
                      />
                    </g>
                  </g>
                </svg>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
    
    <!-- Enhanced Story Section with Timeline -->
    <section class="relative py-24 lg:py-32 overflow-hidden">
      <!-- Background decorative elements -->
      <div class="absolute inset-0 pointer-events-none overflow-hidden">
        <div class="absolute top-20 left-0 w-64 h-64 bg-amber-100 dark:bg-amber-900/20 rounded-full blur-3xl opacity-30 transform -translate-x-1/2"></div>
        <div class="absolute bottom-20 right-0 w-80 h-80 bg-orange-100 dark:bg-orange-900/20 rounded-full blur-3xl opacity-30 transform translate-x-1/2"></div>
        <svg class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-full h-full max-w-7xl" viewBox="0 0 1200 800" fill="none" xmlns="http://www.w3.org/2000/svg" style="opacity: 0.05">
          <path d="M600 100C600 100 300 300 300 400C300 500 600 700 600 700" stroke="currentColor" stroke-width="2" stroke-dasharray="8 8"/>
          <path d="M600 100C600 100 900 300 900 400C900 500 600 700 600 700" stroke="currentColor" stroke-width="2" stroke-dasharray="8 8"/>
        </svg>
      </div>
      
      <div class="relative max-w-7xl mx-auto px-6 sm:px-8 lg:px-12">
        <!-- Section Header -->
        <div class="text-center mb-16">
          <h2 
            in:fly={{ y: prefersReducedMotion ? 0 : -20, duration: 800, delay: 100 }}
            class="text-4xl md:text-5xl font-bold text-slate-900 dark:text-white mb-4 tracking-tight"
          >
            {getText('story.title')}
          </h2>
          <div class="expand-line-title w-32 h-1 bg-gradient-to-r from-amber-500 to-orange-500 mx-auto rounded-full motion-reduce:w-32 mb-6"></div>
        </div>
        
        <!-- Story Content with Timeline -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-x-12 gap-y-16 items-start">
          <!-- Left - Visual Timeline -->
          <div 
            in:fly={{ x: prefersReducedMotion ? 0 : -30, duration: 800, delay: 200 }}
            class="lg:col-span-5 relative"
          >
            <div class="sticky top-32 space-y-12">
              <!-- Timeline visual -->
              <div class="relative pl-8 border-l-2 border-amber-500 dark:border-amber-400 py-4">
                <div class="absolute left-0 top-0 w-4 h-4 rounded-full bg-amber-500 dark:bg-amber-400 transform -translate-x-1/2"></div>
                <div class="absolute left-0 bottom-0 w-4 h-4 rounded-full bg-orange-500 dark:bg-orange-400 transform -translate-x-1/2"></div>
                
                <!-- Timeline content -->
                <div class="space-y-8">
                  <div class="relative">
                    <div class="absolute left-0 top-3 w-3 h-3 rounded-full bg-amber-400 dark:bg-amber-300 transform -translate-x-[calc(0.5rem+1px)]"></div>
                    <h3 class="text-xl font-bold text-amber-600 dark:text-amber-300 mb-2">2019</h3>
                    <p class="text-slate-600 dark:text-slate-300">Founded with a vision to transform real estate transactions</p>
                  </div>
                  
                  <div class="relative">
                    <div class="absolute left-0 top-3 w-3 h-3 rounded-full bg-amber-400 dark:bg-amber-300 transform -translate-x-[calc(0.5rem+1px)]"></div>
                    <h3 class="text-xl font-bold text-amber-600 dark:text-amber-300 mb-2">2021</h3>
                    <p class="text-slate-600 dark:text-slate-300">Expanded to international markets with our innovative platform</p>
                  </div>
                  
                  <div class="relative">
                    <div class="absolute left-0 top-3 w-3 h-3 rounded-full bg-amber-400 dark:bg-amber-300 transform -translate-x-[calc(0.5rem+1px)]"></div>
                    <h3 class="text-xl font-bold text-amber-600 dark:text-amber-300 mb-2">Today</h3>
                    <p class="text-slate-600 dark:text-slate-300">Leading the industry with thousands of successful transactions</p>
                  </div>
                </div>
              </div>
              
              <!-- Stats cards -->
              <div class="grid grid-cols-2 gap-4">
                <div class="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-6 transform transition-all duration-300 hover:-translate-y-1 hover:shadow-xl border border-slate-100 dark:border-slate-700">
                  <div class="text-3xl font-bold text-amber-500 dark:text-amber-400 mb-1">50K+</div>
                  <div class="text-sm text-slate-600 dark:text-slate-300">{getText('hero.stats')[0].label}</div>
                </div>
                
                <div class="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-6 transform transition-all duration-300 hover:-translate-y-1 hover:shadow-xl border border-slate-100 dark:border-slate-700">
                  <div class="text-3xl font-bold text-orange-500 dark:text-orange-400 mb-1">98%</div>
                  <div class="text-sm text-slate-600 dark:text-slate-300">{getText('hero.stats')[1].label}</div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Right - Story Content -->
          <div 
            in:fly={{ x: prefersReducedMotion ? 0 : 30, duration: 800, delay: 300 }}
            class="lg:col-span-7 space-y-8"
          >
            <!-- Main story content -->
            <div class="bg-white dark:bg-slate-800/90 rounded-2xl shadow-xl p-8 lg:p-10 border border-slate-100 dark:border-slate-700">
              <p class="text-lg leading-relaxed text-slate-700 dark:text-slate-300 mb-8">
                {getText('story.content')}
              </p>
              
              <!-- Highlight quote -->
              <div class="relative">
                <svg class="absolute -top-6 -left-6 h-12 w-12 text-amber-200 dark:text-amber-700 opacity-50" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M14.017 21v-7.391c0-5.704 3.731-9.57 8.983-10.609l.995 2.151c-2.432.917-3.995 3.638-3.995 5.849h4v10h-9.983zm-14.017 0v-7.391c0-5.704 3.748-9.57 9-10.609l.996 2.151c-2.433.917-3.996 3.638-3.996 5.849h3.983v10h-9.983z" />
                </svg>
                <blockquote class="bg-gradient-to-r from-amber-50 to-orange-50 dark:from-amber-900/20 dark:to-orange-900/20 rounded-xl p-6 border-l-4 border-amber-500 dark:border-amber-400">
                  <p class="text-xl italic text-slate-800 dark:text-slate-200 leading-relaxed">
                    {getText('story.highlight')}
                  </p>
                </blockquote>
              </div>
            </div>
            
            <!-- Mission & Vision cards -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <!-- Mission card -->
              <div class="bg-white dark:bg-slate-800/90 rounded-xl shadow-lg p-6 border border-slate-100 dark:border-slate-700 transform transition-all duration-300 hover:-translate-y-1 hover:shadow-xl">
                <div class="flex items-center mb-4">
                  <div class="p-2 bg-amber-100 dark:bg-amber-900/30 rounded-lg mr-4">
                    <svg class="w-6 h-6 text-amber-600 dark:text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  </div>
                  <h3 class="text-xl font-bold text-slate-900 dark:text-white">Our Mission</h3>
                </div>
                <p class="text-slate-600 dark:text-slate-300">
                  To democratize real estate by creating the most transparent and accessible property marketplace in the world.
                </p>
              </div>
              
              <!-- Vision card -->
              <div class="bg-white dark:bg-slate-800/90 rounded-xl shadow-lg p-6 border border-slate-100 dark:border-slate-700 transform transition-all duration-300 hover:-translate-y-1 hover:shadow-xl">
                <div class="flex items-center mb-4">
                  <div class="p-2 bg-orange-100 dark:bg-orange-900/30 rounded-lg mr-4">
                    <svg class="w-6 h-6 text-orange-600 dark:text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  </div>
                  <h3 class="text-xl font-bold text-slate-900 dark:text-white">Our Vision</h3>
                </div>
                <p class="text-slate-600 dark:text-slate-300">
                  A world where everyone can participate in real estate opportunities with complete confidence and clarity.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
    

    
    <!-- Team Section -->
    <section class="relative py-24 lg:py-32">
      <div class="relative max-w-7xl mx-auto px-6 sm:px-8 lg:px-12">
        <div 
          in:fade={{ duration: 800, delay: 100 }}
          class="text-center mb-16"
        >
          <h2 class="text-4xl font-bold text-slate-900 dark:text-white mb-4">
            {getText('team.title')}
          </h2>
          <p class="text-lg text-slate-600 dark:text-slate-300 mb-4">
            {getText('team.subtitle')}
          </p>
          <div class="expand-line-team w-24 h-0.5 bg-amber-500 mx-auto motion-reduce:w-24"></div>
        </div>
        
        <!-- Team Grid -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8 lg:gap-12">
          {#each getText('team.members') as member, i}
            <div
              in:fly={{ y: prefersReducedMotion ? 0 : 30, duration: 800, delay: 200 + i * 100 }}
              class="group text-center"
            >
              <!-- Clean Geometric Avatar -->
              <div class="relative w-48 h-48 mx-auto mb-6">
                <div class="absolute inset-0 bg-gradient-to-br from-amber-100 to-orange-100 dark:from-amber-800/30 dark:to-orange-800/30 rounded-full flex items-center justify-center transform transition-transform duration-500 group-hover:scale-110 border-2 border-amber-200 dark:border-amber-700">
                  <!-- Simple geometric pattern -->
                  <div class="relative">
                    <span class="text-4xl font-bold text-slate-700 dark:text-slate-300">
                      {member.name.charAt(0)}
                    </span>
                    <!-- Decorative lines -->
                    <div class="absolute -top-4 -left-4 w-8 h-0.5 bg-amber-500 transform -rotate-45"></div>
                    <div class="absolute -bottom-4 -right-4 w-8 h-0.5 bg-orange-500 transform -rotate-45"></div>
                  </div>
                </div>
              </div>
              
              <h3 class="text-xl font-semibold text-slate-900 dark:text-white mb-1">
                {member.name}
              </h3>
              <p class="text-base text-amber-600 dark:text-amber-400 mb-2">
                {member.role}
              </p>
              <p class="text-sm text-slate-500 dark:text-slate-400 mb-3">
                {member.bio}
              </p>
              
              <!-- Simple underline -->
              <div class="expand-line-member w-16 h-0.5 bg-amber-400 mx-auto motion-reduce:w-16" style="animation-delay: {i * 300 + 800}ms;"></div>
            </div>
          {/each}
        </div>
      </div>
    </section>
    
    <!-- CTA Section -->
    <section class="relative py-24 lg:py-32 overflow-hidden">
      <div class="relative max-w-4xl mx-auto px-6 sm:px-8 lg:px-12 text-center">
        <h2 
          in:fade={{ duration: 800, delay: 100 }}
          class="text-4xl sm:text-5xl font-bold text-slate-900 dark:text-white mb-6"
        >
          {getText('cta.title')}
        </h2>
        
        <!-- Clean line under title -->
        <div class="expand-line-cta w-32 h-1 bg-gradient-to-r from-amber-500 to-orange-500 mx-auto mb-6 motion-reduce:w-32"></div>
        
        <p 
          in:fade={{ duration: 800, delay: 200 }}
          class="text-lg text-slate-600 dark:text-slate-300 mb-10 max-w-2xl mx-auto"
        >
          {getText('cta.description')}
        </p>
        
        <div 
          in:fly={{ y: prefersReducedMotion ? 0 : 20, duration: 800, delay: 300 }}
          class="flex flex-col sm:flex-row gap-4 justify-center"
        >
          <Button 
            variant="primary" 
            size="large" 
            href="/register" 
            class="bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 text-white border-0 px-8 py-4 relative overflow-hidden group transition-all duration-300"
          >
            <span class="relative z-10">{getText('cta.primaryBtn')}</span>
            <div class="absolute bottom-0 left-0 w-full h-0.5 bg-white/30 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300"></div>
          </Button>
          
          <Button 
            variant="outline" 
            size="large" 
            href="/contact" 
            class="border-2 border-amber-500 text-amber-600 hover:bg-amber-50 dark:border-amber-400 dark:text-amber-400 dark:hover:bg-amber-900/20 px-8 py-4 relative overflow-hidden group transition-all duration-300"
          >
            <span class="relative z-10">{getText('cta.secondaryBtn')}</span>
            <div class="absolute bottom-2 left-4 right-4 h-0.5 bg-amber-500 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300"></div>
          </Button>
        </div>
      </div>
    </section>
  {/if}
</div>

<style>
  /* Custom Keyframes for Line Animations */
  @keyframes drawLine {
    from {
      stroke-dasharray: 1000;
      stroke-dashoffset: 1000;
      opacity: 0;
    }
    to {
      stroke-dasharray: 1000;
      stroke-dashoffset: 0;
      opacity: 1;
    }
  }
  
  @keyframes expandWidth {
    from {
      width: 0;
    }
    to {
      width: 100%;
    }
  }
  
  @keyframes fadeInText {
    from {
      opacity: 0;
      transform: scale(0.8);
    }
    to {
      opacity: 1;
      transform: scale(1);
    }
  }
  
  /* Line drawing classes */
  .draw-line-hero {
    stroke-dasharray: 1000;
    stroke-dashoffset: 1000;
    opacity: 0;
    animation: drawLine 2s ease-out forwards;
  }
  
  .draw-text {
    opacity: 0;
    animation: fadeInText 1s ease-out forwards;
  }
  
  /* Width expansion classes */
  .expand-line-stat {
    width: 0;
    animation: expandWidth 0.8s ease-out forwards;
  }
  
  .expand-line-story {
    width: 0;
    animation: expandWidth 1s ease-out 0.2s forwards;
  }
  
  .expand-line-story-2 {
    width: 0;
    animation: expandWidth 0.8s ease-out 0.5s forwards;
  }
  
  .expand-line-story-3 {
    width: 0;
    animation: expandWidth 0.6s ease-out 0.8s forwards;
  }
  
  .expand-line-title {
    width: 0;
    animation: expandWidth 1s ease-out 0.3s forwards;
  }
  
  .expand-line-value {
    width: 0;
    animation: expandWidth 0.6s ease-out forwards;
  }
  
  .expand-line-team {
    width: 0;
    animation: expandWidth 0.8s ease-out 0.3s forwards;
  }
  
  .expand-line-member {
    width: 0;
    animation: expandWidth 0.5s ease-out forwards;
  }
  
  .expand-line-cta {
    width: 0;
    animation: expandWidth 0.8s ease-out 0.3s forwards;
  }
  
  /* Ensure animations respect reduced motion */
  @media (prefers-reduced-motion: reduce) {
    * {
      animation-duration: 0.01ms !important;
      animation-iteration-count: 1 !important;
      transition-duration: 0.01ms !important;
    }
    
    .draw-line-hero {
      stroke-dasharray: none;
      stroke-dashoffset: 0;
      opacity: 1;
    }
    
    .draw-text {
     opacity: 1;
     transform: scale(1);
   }
   
   .expand-line-stat,
   .expand-line-story,
   .expand-line-story-2,
   .expand-line-story-3,
   .expand-line-title,
   .expand-line-value,
   .expand-line-team,
   .expand-line-member,
   .expand-line-cta {
     width: 100% !important;
   }
 }
 
 /* RTL support */
 [dir="rtl"] .expand-line-stat,
 [dir="rtl"] .expand-line-story,
 [dir="rtl"] .expand-line-story-2,
 [dir="rtl"] .expand-line-story-3,
 [dir="rtl"] .expand-line-title,
 [dir="rtl"] .expand-line-value,
 [dir="rtl"] .expand-line-team,
 [dir="rtl"] .expand-line-member,
 [dir="rtl"] .expand-line-cta {
   transform-origin: right;
 }
 
 /* Enhanced focus states */
 :global(:focus-visible) {
   outline: 2px solid #f59e0b;
   outline-offset: 2px;
   border-radius: 0.25rem;
 }
 
 :global(.dark :focus-visible) {
   outline-color: #fbbf24;
 }
 
 /* Subtle hover effects for interactive elements */
 .group:hover .draw-line-hero {
   stroke-width: 2.5;
   transition: stroke-width 0.3s ease;
 }
 
 /* Clean card styling */
 .bg-white {
   background-color: rgba(255, 255, 255, 0.95);
 }
 
 .dark .bg-white {
   background-color: rgba(30, 41, 59, 0.95);
 }
</style>