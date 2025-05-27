<!-- src/routes/about/+page.svelte -->
<script>
    import { onMount } from 'svelte';
    import { fade, fly, scale } from 'svelte/transition';
    import { cubicOut } from 'svelte/easing';
    import { locale } from '$lib/i18n';
    import Button from '$lib/components/ui/Button.svelte';
    
    let mounted = false;
    let scrollY = 0;
    let prefersReducedMotion = false;
    let intersectionObserver;
    
    // RTL computed value
    $: isRTL = $locale === 'ar';
    
    // Enhanced data structure
    const aboutData = {
      en: {
        topSection: {
          badge: "About Our Company",
          title: "Revolutionizing Real Estate",
          subtitle: "Through Innovation & Trust",
          description: "We're pioneering the future of property transactions with cutting-edge technology and unwavering commitment to transparency."
        },
        hero: {
          title: "Building Tomorrow's Real Estate Marketplace",
          subtitle: "Connecting investors, buyers, and sellers through our advanced auction platform powered by transparency and innovation.",
          stats: [
            { value: "2019", label: "Founded", icon: "calendar" },
            { value: "50K+", label: "Properties", icon: "building" },
            { value: "15", label: "Countries", icon: "globe" }
          ]
        },
        mission: {
          title: "Our Mission & Vision",
          content: "To democratize real estate investing by creating the world's most transparent, efficient, and accessible property auction platform.",
          vision: "A world where everyone has equal access to premium real estate opportunities.",
          values: [
            { 
              title: "Transparency", 
              desc: "Every transaction is open and verifiable with complete audit trails",
              icon: "eye"
            },
            { 
              title: "Innovation", 
              desc: "Leveraging cutting-edge technology to simplify complex processes",
              icon: "lightbulb"
            },
            { 
              title: "Trust", 
              desc: "Building lasting relationships through reliability and excellence",
              icon: "shield"
            }
          ]
        },
        cta: {
          title: "Ready to Transform Your Real Estate Journey?",
          subtitle: "Join thousands of successful investors who trust our platform for their property transactions.",
          primaryBtn: "Get Started Today",
          secondaryBtn: "Contact Our Team"
        }
      },
      ar: {
        topSection: {
          badge: "عن شركتنا",
          title: "ثورة في مجال العقارات",
          subtitle: "من خلال الابتكار والثقة",
          description: "نحن نقود مستقبل معاملات العقارات بالتكنولوجيا المتطورة والالتزام الثابت بالشفافية."
        },
        hero: {
          title: "بناء سوق العقارات للمستقبل",
          subtitle: "ربط المستثمرين والمشترين والبائعين من خلال منصة المزادات المتطورة المدعومة بالشفافية والابتكار.",
          stats: [
            { value: "2019", label: "التأسيس", icon: "calendar" },
            { value: "50+", label: "ألف عقار", icon: "building" },
            { value: "15", label: "دولة", icon: "globe" }
          ]
        },
        mission: {
          title: "مهمتنا ورؤيتنا",
          content: "إضفاء الطابع الديمقراطي على الاستثمار العقاري من خلال إنشاء منصة مزادات العقارات الأكثر شفافية وكفاءة وإمكانية وصول في العالم.",
          vision: "عالم يتمتع فيه الجميع بوصول متساوٍ إلى فرص العقارات المميزة.",
          values: [
            { 
              title: "الشفافية", 
              desc: "كل معاملة مفتوحة وقابلة للتحقق مع مسارات تدقيق كاملة",
              icon: "eye"
            },
            { 
              title: "الابتكار", 
              desc: "الاستفادة من التكنولوجيا المتطورة لتبسيط العمليات المعقدة",
              icon: "lightbulb"
            },
            { 
              title: "الثقة", 
              desc: "بناء علاقات دائمة من خلال الموثوقية والتميز",
              icon: "shield"
            }
          ]
        },
        cta: {
          title: "هل أنت مستعد لتغيير رحلة العقارات الخاصة بك؟",
          subtitle: "انضم لآلاف المستثمرين الناجحين الذين يثقون بمنصتنا لمعاملاتهم العقارية.",
          primaryBtn: "ابدأ اليوم",
          secondaryBtn: "تواصل مع فريقنا"
        }
      }
    };
    
    function getText(key) {
      const lang = $locale || 'en';
      const keys = key.split('.');
      let value = aboutData[lang] || aboutData.en;
      
      for (const k of keys) {
        if (value && value[k]) {
          value = value[k];
        } else {
          return key;
        }
      }
      return value;
    }
    
    // Icon mapping
    const iconMap = {
      calendar: "M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z",
      building: "M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4",
      globe: "M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9",
      eye: "M15 12a3 3 0 11-6 0 3 3 0 016 0z M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z",
      lightbulb: "M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z",
      shield: "M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
    };
    
    onMount(() => {
      mounted = true;
      
      if (typeof window !== 'undefined') {
        const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
        prefersReducedMotion = mediaQuery.matches;
        
        mediaQuery.addEventListener('change', (e) => {
          prefersReducedMotion = e.matches;
        });
        
        // Intersection Observer for scroll animations
        intersectionObserver = new IntersectionObserver(
          (entries) => {
            entries.forEach((entry) => {
              if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
              }
            });
          },
          { threshold: 0.1, rootMargin: '0px 0px -50px 0px' }
        );
        
        // Observe elements
        setTimeout(() => {
          document.querySelectorAll('.observe').forEach((el) => {
            intersectionObserver.observe(el);
          });
        }, 100);
      }
      
      return () => {
        if (intersectionObserver) {
          intersectionObserver.disconnect();
        }
      };
    });
    
    // Enhanced parallax effects
    $: scrollOffset = scrollY * 0.1;
    $: scrollOffsetSlow = scrollY * 0.05;
  </script>
  
  <svelte:head>
    <title>About Us | Premier Real Estate Auctions</title>
    <meta name="description" content="Learn about our mission to transform real estate through innovative auction technology.">
  </svelte:head>
  
  <svelte:window bind:scrollY />
  
  <!-- Main Container -->
  <div class={`bg-white dark:bg-slate-900 ${isRTL ? 'rtl' : 'ltr'}`} dir={isRTL ? 'rtl' : 'ltr'}>
    
    <!-- Simplified Advanced SVG Background -->
    <div class="fixed inset-0 overflow-hidden pointer-events-none" aria-hidden="true">
      <svg 
        class="absolute inset-0 w-full h-full opacity-20 dark:opacity-30" 
        viewBox="0 0 1440 900" 
        fill="none" 
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          <!-- Simplified Advanced Gradients -->
          <linearGradient id="modernGradient1" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#3b82f6;stop-opacity:0.6"/>
            <stop offset="50%" style="stop-color:#8b5cf6;stop-opacity:0.4"/>
            <stop offset="100%" style="stop-color:#06b6d4;stop-opacity:0.3"/>
          </linearGradient>
          
          <radialGradient id="modernGradient2" cx="50%" cy="50%" r="50%">
            <stop offset="0%" style="stop-color:#f59e0b;stop-opacity:0.5"/>
            <stop offset="100%" style="stop-color:#ef4444;stop-opacity:0.2"/>
          </radialGradient>
          
          <linearGradient id="modernGradient3" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" style="stop-color:#10b981;stop-opacity:0.4"/>
            <stop offset="100%" style="stop-color:#3b82f6;stop-opacity:0.2"/>
          </linearGradient>
        </defs>
        
        <!-- Simplified Modern Shapes -->
        <g transform="translate({scrollOffset}, 0)">
          <!-- Clean Geometric Shape 1 -->
          <rect x="200" y="100" width="300" height="200" rx="60" fill="url(#modernGradient1)" opacity="0.3">
            <animateTransform attributeName="transform" type="rotate" 
              values="0 350 200;5 350 200;0 350 200" dur="8s" repeatCount="indefinite"/>
          </rect>
          
          <!-- Modern Circle -->
          <circle cx="800" cy="300" r="100" fill="url(#modernGradient2)" opacity="0.4">
            <animate attributeName="r" values="80;120;80" dur="6s" repeatCount="indefinite"/>
          </circle>
          
          <!-- Flowing Wave Shape -->
          <path d="M0,400 Q360,300 720,400 T1440,400 L1440,500 Q1080,600 720,500 T0,500 Z" 
                fill="url(#modernGradient3)" opacity="0.2">
            <animate attributeName="d" 
              values="M0,400 Q360,300 720,400 T1440,400 L1440,500 Q1080,600 720,500 T0,500 Z;
                      M0,420 Q360,320 720,420 T1440,420 L1440,520 Q1080,620 720,520 T0,520 Z;
                      M0,400 Q360,300 720,400 T1440,400 L1440,500 Q1080,600 720,500 T0,500 Z"
              dur="10s" repeatCount="indefinite"/>
          </path>
        </g>
        
        <!-- Slow Moving Elements -->
        <g transform="translate({scrollOffsetSlow}, 0)">
          <!-- Minimalist Line Pattern -->
          <g opacity="0.3">
            <line x1="100" y1="600" x2="400" y2="650" stroke="url(#modernGradient1)" stroke-width="2"/>
            <line x1="600" y1="650" x2="900" y2="600" stroke="url(#modernGradient1)" stroke-width="2"/>
            <line x1="1000" y1="600" x2="1300" y2="650" stroke="url(#modernGradient1)" stroke-width="2"/>
          </g>
        </g>
      </svg>
    </div>
  
    {#if mounted}
      <!-- Top White Space Section with Advanced UI -->
      <section class="relative z-10 bg-gradient-to-b from-slate-50 via-white to-slate-50 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900 px-6 sm:px-8 lg:px-12">
        <div class="max-w-4xl mx-auto pt-24 pb-20">
          
          <!-- Top Badge -->
          <div 
            in:fade={{ duration: 800, delay: 100, easing: cubicOut }}
            class="flex justify-center mb-10"
          >
            <div class="inline-flex items-center gap-3 px-6 py-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-full text-sm font-semibold text-blue-700 dark:text-blue-300 shadow-sm">
              <div class="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
              {getText('topSection.badge')}
            </div>
          </div>
          
          <!-- Main Heading -->
          <div class="text-center space-y-8 mb-16">
            <div 
              in:fly={{ y: prefersReducedMotion ? 0 : 40, duration: 800, delay: 200, easing: cubicOut }}
            >
              <h1 class="text-5xl sm:text-6xl lg:text-7xl font-black text-slate-900 dark:text-white leading-[0.9] tracking-tight mb-6">
                {getText('topSection.title')}
              </h1>
              <div class="text-3xl sm:text-4xl lg:text-5xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-emerald-600 bg-clip-text text-transparent">
                {getText('topSection.subtitle')}
              </div>
            </div>
            
            <!-- Description with narrower width and better padding -->
            <div 
              in:fly={{ y: prefersReducedMotion ? 0 : 30, duration: 800, delay: 400, easing: cubicOut }}
              class="max-w-2xl mx-auto px-4"
            >
              <p class="text-lg text-slate-600 dark:text-slate-300 leading-relaxed font-medium">
                {getText('topSection.description')}
              </p>
            </div>
          </div>
          
          <!-- Advanced Visual Element with Better Padding -->
          <div 
            in:scale={{ duration: 1000, delay: 600, easing: cubicOut }}
            class="relative max-w-3xl mx-auto"
          >
            <!-- Main Card with Enhanced Padding -->
            <div class="bg-white/90 dark:bg-slate-800/90 backdrop-blur-xl border border-slate-200/60 dark:border-slate-700/60 rounded-3xl p-10 sm:p-12 shadow-2xl shadow-slate-900/10 dark:shadow-slate-900/30">
              
              <!-- Stats Grid with Better Spacing -->
              <div class="grid grid-cols-1 sm:grid-cols-3 gap-10 sm:gap-12">
                {#each getText('hero.stats') as stat, index}
                  <div 
                    class="text-center group"
                    in:fly={{ 
                      y: prefersReducedMotion ? 0 : 30, 
                      duration: 600, 
                      delay: 800 + (index * 150), 
                      easing: cubicOut 
                    }}
                  >
                    <!-- Icon with Better Spacing -->
                    <div class="w-18 h-18 mx-auto mb-6 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center shadow-lg shadow-blue-500/30 group-hover:scale-110 transition-transform duration-300">
                      <svg class="w-9 h-9 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={iconMap[stat.icon]}/>
                      </svg>
                    </div>
                    
                    <!-- Stat Value -->
                    <div class="text-4xl font-black text-slate-900 dark:text-white mb-3">
                      {stat.value}
                    </div>
                    
                    <!-- Stat Label -->
                    <div class="text-sm font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                      {stat.label}
                    </div>
                  </div>
                {/each}
              </div>
            </div>
            
            <!-- Decorative Elements -->
            <div class="absolute -top-6 -left-6 w-32 h-32 bg-gradient-to-br from-blue-400/20 to-purple-400/20 rounded-full blur-2xl"></div>
            <div class="absolute -bottom-6 -right-6 w-40 h-40 bg-gradient-to-br from-emerald-400/20 to-blue-400/20 rounded-full blur-2xl"></div>
          </div>
        </div>
      </section>
  
      <!-- Hero Section with FIXED Light Mode Colors -->
      <section class="relative z-10 bg-slate-900 dark:bg-slate-900 px-6 sm:px-8 lg:px-12 py-24 observe">
        <div class="max-w-6xl mx-auto">
          
          <!-- Content Grid with Better Padding -->
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-16 lg:gap-20 items-center">
            
            <!-- Text Content with Enhanced Padding -->
            <div class={`space-y-10 ${isRTL ? 'lg:order-2 text-right' : 'lg:order-1 text-left'} px-4 lg:px-0`}>
              <div class="space-y-8">
                <!-- FIXED: Always white text on dark background -->
                <h2 class="text-4xl sm:text-5xl lg:text-6xl font-bold text-white leading-tight">
                  {getText('hero.title')}
                </h2>
                
                <!-- Narrower paragraph width with better padding -->
                <div class="max-w-lg pr-4">
                  <p class="text-lg text-slate-300 leading-relaxed">
                    {getText('hero.subtitle')}
                  </p>
                </div>
              </div>
              
              <!-- CTA Buttons with Better Spacing -->
              <div class="flex flex-col sm:flex-row gap-5 pt-6">
                <Button variant="primary" size="large" href="/properties" class_="w-full sm:w-auto px-8 py-4">
                  {isRTL ? 'ابدأ الآن' : 'Get Started'}
                </Button>
                <Button variant="outline" size="large" href="/contact" class_="w-full sm:w-auto px-8 py-4">
                  {isRTL ? 'تعرف أكثر' : 'Learn More'}
                </Button>
              </div>
            </div>
            
            <!-- Advanced Visual Element with Enhanced Padding -->
            <div class={`${isRTL ? 'lg:order-1' : 'lg:order-2'} px-4 lg:px-0`}>
              <div class="relative">
                <!-- Main Feature Card with Better Internal Padding -->
                <div class="bg-slate-800/90 backdrop-blur-xl border border-slate-700/50 rounded-3xl p-10 shadow-2xl shadow-slate-900/50">
                  
                  <!-- Header with Better Spacing -->
                  <div class="flex items-center gap-5 mb-10">
                    <div class="w-14 h-14 bg-gradient-to-br from-emerald-400 to-blue-500 rounded-xl flex items-center justify-center">
                      <svg class="w-7 h-7 text-white" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M13 10V3L4 14h7v7l9-11h-7z"/>
                      </svg>
                    </div>
                    <div>
                      <h3 class="text-xl font-bold text-white">Platform Analytics</h3>
                      <p class="text-sm text-slate-400">Real-time insights</p>
                    </div>
                  </div>
                  
                  <!-- Mock Chart with Better Spacing -->
                  <div class="space-y-6">
                    <div class="flex items-center justify-between">
                      <span class="text-sm text-slate-400">Active Auctions</span>
                      <span class="text-2xl font-bold text-emerald-400">247</span>
                    </div>
                    
                    <div class="w-full bg-slate-700 rounded-full h-3">
                      <div class="bg-gradient-to-r from-emerald-400 to-blue-500 h-3 rounded-full w-3/4 animate-pulse"></div>
                    </div>
                    
                    <div class="grid grid-cols-2 gap-6 pt-6">
                      <div class="text-center p-4">
                        <div class="text-2xl font-bold text-blue-400">$2.5M</div>
                        <div class="text-xs text-slate-500 mt-1">This Month</div>
                      </div>
                      <div class="text-center p-4">
                        <div class="text-2xl font-bold text-purple-400">98%</div>
                        <div class="text-xs text-slate-500 mt-1">Success Rate</div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- Floating Elements -->
                <div class="absolute -top-4 -right-4 w-24 h-24 bg-gradient-to-br from-blue-500/30 to-purple-500/30 rounded-full blur-xl animate-pulse"></div>
                <div class="absolute -bottom-4 -left-4 w-32 h-32 bg-gradient-to-br from-emerald-500/20 to-blue-500/20 rounded-full blur-xl"></div>
              </div>
            </div>
          </div>
        </div>
      </section>
  
      <!-- Mission Section with Enhanced Layout and Padding -->
      <section class="relative z-10 bg-gradient-to-b from-slate-50 to-white dark:from-slate-800 dark:to-slate-900 px-6 sm:px-8 lg:px-12 py-24 observe">
        <div class="max-w-6xl mx-auto">
          
          <!-- Section Header with Better Padding -->
          <div class="text-center mb-20 px-4">
            <h2 class="text-4xl sm:text-5xl font-bold text-slate-900 dark:text-white mb-8">
              {getText('mission.title')}
            </h2>
            
            <!-- Narrower content width with enhanced padding -->
            <div class="max-w-3xl mx-auto space-y-8">
              <p class="text-xl text-slate-600 dark:text-slate-300 leading-relaxed px-4">
                {getText('mission.content')}
              </p>
              <div class="max-w-2xl mx-auto">
                <p class="text-lg text-slate-500 dark:text-slate-400 italic px-4">
                  {getText('mission.vision')}
                </p>
              </div>
            </div>
          </div>
          
          <!-- Values Grid with Enhanced Cards and Padding -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-10 px-4">
            {#each getText('mission.values') as value, index}
              <div 
                class="group relative"
                in:fly={{ 
                  y: prefersReducedMotion ? 0 : 40, 
                  duration: 800, 
                  delay: 200 + (index * 150), 
                  easing: cubicOut 
                }}
              >
                <!-- Card with Enhanced Internal Padding -->
                <div class="bg-white/90 dark:bg-slate-800/90 backdrop-blur-lg border border-slate-200/60 dark:border-slate-700/40 rounded-3xl p-10 h-full transition-all duration-500 hover:bg-white dark:hover:bg-slate-800 hover:border-slate-300 dark:hover:border-slate-600 hover:transform hover:-translate-y-4 hover:shadow-2xl hover:shadow-slate-900/20">
                  
                  <!-- Icon with Better Spacing -->
                  <div class="w-18 h-18 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center mb-8 group-hover:scale-110 group-hover:rotate-3 transition-all duration-300 shadow-lg shadow-blue-500/30">
                    <svg class="w-9 h-9 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={iconMap[value.icon]}/>
                    </svg>
                  </div>
                  
                  <!-- Content with Better Spacing -->
                  <h3 class="text-2xl font-bold text-slate-900 dark:text-white mb-6">
                    {value.title}
                  </h3>
                  
                  <!-- Narrower description with padding -->
                  <div class="max-w-sm">
                    <p class="text-slate-600 dark:text-slate-300 leading-relaxed">
                      {value.desc}
                    </p>
                  </div>
                </div>
                
                <!-- Decorative gradient behind card -->
                <div class="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-purple-500/5 rounded-3xl transform rotate-1 -z-10 group-hover:rotate-2 transition-transform duration-300"></div>
              </div>
            {/each}
          </div>
        </div>
      </section>
  
      <!-- CTA Section with FIXED Light Mode Colors and Enhanced Padding -->
      <section class="relative z-10 bg-slate-900 dark:bg-slate-900 px-6 sm:px-8 lg:px-12 py-24 observe">
        <div class="max-w-4xl mx-auto text-center px-4">
          
          <!-- Enhanced CTA Design with Better Padding -->
          <div class="relative">
            <!-- Main CTA Card with Enhanced Internal Padding -->
            <div class="bg-slate-800/90 backdrop-blur-xl border border-slate-700/50 rounded-3xl p-12 sm:p-16 shadow-2xl shadow-slate-900/50">
              <!-- FIXED: Always white text on dark background -->
              <h2 class="text-4xl sm:text-5xl font-bold text-white mb-8">
                {getText('cta.title')}
              </h2>
              
              <!-- Narrower CTA description with better padding -->
              <div class="max-w-2xl mx-auto mb-10 px-4">
                <p class="text-lg text-slate-300 leading-relaxed">
                  {getText('cta.subtitle')}
                </p>
              </div>
              
              <!-- CTA Buttons with Enhanced Spacing -->
              <div class="flex flex-col sm:flex-row gap-5 justify-center">
                <Button variant="primary" size="large" href="/register" class_="w-full sm:w-auto px-10 py-4">
                  {getText('cta.primaryBtn')}
                </Button>
                <Button variant="outline" size="large" href="/contact" class_="w-full sm:w-auto px-10 py-4">
                  {getText('cta.secondaryBtn')}
                </Button>
              </div>
            </div>
            
            <!-- Decorative Elements -->
            <div class="absolute -top-8 -left-8 w-40 h-40 bg-gradient-to-br from-blue-500/20 to-purple-500/20 rounded-full blur-2xl"></div>
            <div class="absolute -bottom-8 -right-8 w-48 h-48 bg-gradient-to-br from-emerald-500/20 to-blue-500/20 rounded-full blur-2xl"></div>
          </div>
        </div>
      </section>
    {/if}
  </div>
  
  <style>
    /* Enhanced animations */
    .observe {
      opacity: 0;
      transform: translateY(40px);
      transition: all 1s cubic-bezier(0.16, 1, 0.3, 1);
    }
    
    .observe.animate-in {
      opacity: 1;
      transform: translateY(0);
    }
    
    /* RTL-specific enhancements */
    .rtl {
      direction: rtl;
    }
    
    .rtl .text-left {
      text-align: right;
    }
    
    .rtl h1, .rtl h2, .rtl h3 {
      font-family: 'Cairo', 'Segoe UI', system-ui, sans-serif;
      line-height: 1.4;
    }
    
    .rtl p {
      font-family: 'Cairo', 'Segoe UI', system-ui, sans-serif;
      line-height: 1.8;
    }
    
    /* Enhanced hover effects */
    .group:hover .group-hover\:scale-110 {
      transform: scale(1.1);
    }
    
    .group:hover .group-hover\:rotate-3 {
      transform: rotate(3deg) scale(1.1);
    }
    
    /* Accessibility improvements */
    @media (prefers-reduced-motion: reduce) {
      *, *::before, *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
        scroll-behavior: auto !important;
      }
      
      .observe {
        opacity: 1 !important;
        transform: none !important;
      }
    }
    
    /* High contrast support */
    @media (prefers-contrast: high) {
      .bg-white\/90, .bg-slate-800\/90 {
        background-opacity: 1 !important;
      }
      
      .border-slate-200\/60, .border-slate-700\/40 {
        border-width: 2px !important;
        border-opacity: 1 !important;
      }
    }
    
    /* Enhanced typography */
    * {
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
      text-rendering: optimizeLegibility;
    }
    
    /* Focus management */
    :global(:focus-visible) {
      outline: 2px solid #3b82f6;
      outline-offset: 2px;
      border-radius: 4px;
    }
  </style>