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
  let currentTestimonial = 0;
  
  // Computed value for RTL mode
  $: isRTL = $locale === 'ar';

  // Local translations fallback
  const translations = {
    en: {
      badge: {
        live: 'Live Now',
        activeCount: '24 Active Auctions'
      },
      headline: {
        line1: 'Discover Premium',
        line2: 'Real Estate',
        line3: 'Through Smart Auctions'
      },
      subheadline: 'Join thousands of successful buyers and sellers in our transparent auction marketplace. Find your dream property with confidence.',
      cta: {
        explore: 'Browse Properties',
        learnMore: 'How It Works'
      },
      metrics: {
        properties: {
          value: '$2.5M+',
          label: 'Properties Sold'
        },
        success: {
          value: '98%',
          label: 'Success Rate'
        },
        users: {
          value: '15K+',
          label: 'Happy Clients'
        },
        satisfaction: {
          value: '4.9★',
          label: 'Client Rating'
        }
      },
      features: {
        verified: {
          title: 'Verified Properties',
          description: '100% authenticated listings'
        },
        transparent: {
          title: 'Transparent Bidding',
          description: 'Real-time auction updates'
        },
        secure: {
          title: 'Secure Transactions',
          description: 'Bank-level security'
        }
      },
      testimonials: [
        {
          name: 'Sarah Johnson',
          role: 'Property Investor',
          content: 'Found my perfect investment property through their auction platform. The process was transparent and efficient.',
          rating: 5
        },
        {
          name: 'Ahmed Al-Rashid',
          role: 'First-time Buyer',
          content: 'Amazing experience! The team guided me through every step of my first property purchase.',
          rating: 5
        },
        {
          name: 'Maria Rodriguez',
          role: 'Real Estate Agent',
          content: 'This platform has revolutionized how I help my clients find and bid on properties.',
          rating: 5
        }
      ]
    },
    ar: {
      badge: {
        live: 'مباشر الآن',
        activeCount: '24 مزاد نشط'
      },
      headline: {
        line1: 'اكتشف العقارات',
        line2: 'المميزة',
        line3: 'عبر المزادات الذكية'
      },
      subheadline: 'انضم لآلاف المشترين والبائعين الناجحين في منصة المزادات الشفافة. اعثر على عقار أحلامك بثقة.',
      cta: {
        explore: 'تصفح العقارات',
        learnMore: 'كيف يعمل'
      },
      metrics: {
        properties: {
          value: '+2.5 مليون$',
          label: 'عقار مباع'
        },
        success: {
          value: '98%',
          label: 'معدل النجاح'
        },
        users: {
          value: '+15 ألف',
          label: 'عميل سعيد'
        },
        satisfaction: {
          value: '★4.9',
          label: 'تقييم العملاء'
        }
      },
      features: {
        verified: {
          title: 'عقارات موثقة',
          description: '100% قوائم معتمدة'
        },
        transparent: {
          title: 'مزايدة شفافة',
          description: 'تحديثات المزاد الفورية'
        },
        secure: {
          title: 'معاملات آمنة',
          description: 'أمان بمستوى البنوك'
        }
      },
      testimonials: [
        {
          name: 'سارة أحمد',
          role: 'مستثمرة عقارية',
          content: 'وجدت عقار الاستثمار المثالي من خلال منصة المزادات. العملية كانت شفافة وفعالة.',
          rating: 5
        },
        {
          name: 'أحمد الراشد',
          role: 'مشتري لأول مرة',
          content: 'تجربة رائعة! الفريق أرشدني خلال كل خطوة في شراء أول عقار لي.',
          rating: 5
        },
        {
          name: 'مريم محمد',
          role: 'وكيلة عقارية',
          content: 'هذه المنصة ثورت طريقة مساعدة عملائي في إيجاد والمزايدة على العقارات.',
          rating: 5
        }
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

  // Testimonial rotation
  function rotateTestimonial() {
    const testimonials = getText('testimonials');
    currentTestimonial = (currentTestimonial + 1) % testimonials.length;
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

      // Auto-rotate testimonials
      const testimonialInterval = setInterval(rotateTestimonial, 4000);
      
      return () => {
        clearInterval(testimonialInterval);
      };
    }
  });
</script>

<svelte:head>
  <title>Premier Real Estate Auctions | Find Your Perfect Property</title>
  <meta name="description" content="Discover exclusive properties through transparent auctions. Join thousands of satisfied buyers in finding their dream properties.">
</svelte:head>

<svelte:window bind:scrollY />

<!-- Hero Section with Modern Layout -->
<section class="hero" aria-label="Hero section">
  <!-- Animated Background -->
  <div class="hero__background" aria-hidden="true">
    <div class="hero__gradient"></div>
    <div class="hero__pattern"></div>
    <div class="hero__orbs">
      <div class="hero__orb hero__orb--1"></div>
      <div class="hero__orb hero__orb--2"></div>
      <div class="hero__orb hero__orb--3"></div>
    </div>
  </div>

  <!-- Main Container -->
  <div class="hero__container">
    {#if mounted}
      <!-- Status Badge -->
      <div 
        in:fade={{ duration: 400, delay: 100, easing: cubicOut }}
        class="hero__badge"
        role="status"
        aria-live="polite"
      >
        <span class="hero__badge-indicator" aria-hidden="true"></span>
        <span class="hero__badge-text">{getText('badge.live')}</span>
        <span class="hero__badge-count">{getText('badge.activeCount')}</span>
      </div>

      <!-- Main Content Grid -->
      <div class="hero__content">
        <!-- Left Column: Text Content -->
        <div class="hero__text-column">
          <!-- Main Headline -->
          <h1 
            in:fly={{ y: prefersReducedMotion ? 0 : 32, duration: 600, delay: 200, easing: cubicOut }}
            class="hero__headline"
          >
            <span class="hero__headline-line">{getText('headline.line1')}</span>
            <span class="hero__headline-accent">{getText('headline.line2')}</span>
            <span class="hero__headline-line">{getText('headline.line3')}</span>
          </h1>
          
          <!-- Subheadline -->
          <p 
            in:fly={{ y: prefersReducedMotion ? 0 : 24, duration: 600, delay: 300, easing: cubicOut }}
            class="hero__subheadline"
          >
            {getText('subheadline')}
          </p>
          
          <!-- CTA Buttons -->
          <div 
            in:fly={{ y: prefersReducedMotion ? 0 : 24, duration: 600, delay: 400, easing: cubicOut }}
            class="hero__cta-group"
          >
            <Button 
              variant="primary" 
              size="large" 
              href="/properties" 
              class_="hero__cta-primary"
            >
              <span>{getText('cta.explore')}</span>
              <svg 
                class="hero__cta-icon" 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </Button>
            
            <Button 
              variant="outline" 
              size="large" 
              href="/how-it-works" 
              class_="hero__cta-secondary"
            >
              <span>{getText('cta.learnMore')}</span>
            </Button>
          </div>

          <!-- Trust Metrics -->
          <div 
            in:fade={{ duration: 600, delay: 500, easing: cubicOut }}
            class="hero__metrics"
            role="region"
            aria-label="Platform statistics"
          >
            {#each Object.entries(getText('metrics')) as [key, metric], index}
              <div class="hero__metric" in:scale={{ duration: 400, delay: 500 + (index * 100) }}>
                <span class="hero__metric-value">{metric.value}</span>
                <span class="hero__metric-label">{metric.label}</span>
              </div>
              {#if index < Object.keys(getText('metrics')).length - 1}
                <div class="hero__metric-divider" aria-hidden="true"></div>
              {/if}
            {/each}
          </div>
        </div>

        <!-- Right Column: Interactive Elements -->
        <div class="hero__visual-column">
          <!-- Feature Cards -->
          <div class="hero__feature-cards">
            {#each Object.entries(getText('features')) as [key, feature], index}
              <div 
                class="hero__feature-card"
                in:fly={{ y: prefersReducedMotion ? 0 : 32, duration: 600, delay: 600 + (index * 150), easing: cubicOut }}
              >
                <div class="hero__feature-icon">
                  {#if key === 'verified'}
                    <svg fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
                      <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                    </svg>
                  {:else if key === 'transparent'}
                    <svg fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
                      <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                      <path fill-rule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clip-rule="evenodd" />
                    </svg>
                  {:else}
                    <svg fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
                      <path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd" />
                    </svg>
                  {/if}
                </div>
                <div class="hero__feature-content">
                  <h3 class="hero__feature-title">{feature.title}</h3>
                  <p class="hero__feature-description">{feature.description}</p>
                </div>
              </div>
            {/each}
          </div>

          <!-- Floating Testimonial Card -->
          <div 
            class="hero__testimonial-card"
            in:fly={{ y: prefersReducedMotion ? 0 : 40, duration: 800, delay: 1000, easing: cubicOut }}
          >
            {#each getText('testimonials') as testimonial, index}
              {#if index === currentTestimonial}
                <div 
                  class="hero__testimonial-content"
                  in:fade={{ duration: 300 }}
                  out:fade={{ duration: 300 }}
                >
                  <div class="hero__testimonial-rating">
                    {#each Array(testimonial.rating) as _}
                      <svg class="hero__testimonial-star" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                      </svg>
                    {/each}
                  </div>
                  <blockquote class="hero__testimonial-quote">
                    "{testimonial.content}"
                  </blockquote>
                  <div class="hero__testimonial-author">
                    <div class="hero__testimonial-avatar">
                      {testimonial.name.charAt(0)}
                    </div>
                    <div>
                      <cite class="hero__testimonial-name">{testimonial.name}</cite>
                      <p class="hero__testimonial-role">{testimonial.role}</p>
                    </div>
                  </div>
                </div>
              {/if}
            {/each}
          </div>
        </div>
      </div>
    {/if}
  </div>
</section>

<style>
  /* Hero Section */
  .hero {
    position: relative;
    min-height: 100vh;
    display: flex;
    align-items: center;
    overflow: hidden;
    padding: 6rem 0;
  }

  /* Animated Background */
  .hero__background {
    position: absolute;
    inset: 0;
    z-index: -1;
  }

  .hero__gradient {
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, 
      rgba(59, 130, 246, 0.05) 0%, 
      rgba(139, 92, 246, 0.05) 50%, 
      rgba(16, 185, 129, 0.05) 100%
    );
    animation: gradientShift 8s ease-in-out infinite;
  }

  :global(.dark) .hero__gradient {
    background: linear-gradient(135deg, 
      rgba(59, 130, 246, 0.1) 0%, 
      rgba(139, 92, 246, 0.1) 50%, 
      rgba(16, 185, 129, 0.1) 100%
    );
  }

  .hero__pattern {
    position: absolute;
    inset: 0;
    opacity: 0.3;
    background-image: 
      radial-gradient(circle at 25% 25%, rgba(59, 130, 246, 0.1) 0%, transparent 50%),
      radial-gradient(circle at 75% 75%, rgba(139, 92, 246, 0.1) 0%, transparent 50%),
      radial-gradient(circle at 50% 10%, rgba(16, 185, 129, 0.08) 0%, transparent 40%);
  }

  .hero__orbs {
    position: absolute;
    inset: 0;
    pointer-events: none;
  }

  .hero__orb {
    position: absolute;
    border-radius: 50%;
    filter: blur(1px);
    animation: float 6s ease-in-out infinite;
  }

  .hero__orb--1 {
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(59, 130, 246, 0.15) 0%, transparent 70%);
    top: 10%;
    right: 10%;
    animation-delay: 0s;
  }

  .hero__orb--2 {
    width: 200px;
    height: 200px;
    background: radial-gradient(circle, rgba(139, 92, 246, 0.1) 0%, transparent 70%);
    bottom: 20%;
    left: 5%;
    animation-delay: 2s;
  }

  .hero__orb--3 {
    width: 150px;
    height: 150px;
    background: radial-gradient(circle, rgba(16, 185, 129, 0.12) 0%, transparent 70%);
    top: 60%;
    right: 30%;
    animation-delay: 4s;
  }

  /* Container System (matches auction page exactly) */
  .hero__container {
    width: 100%;
    max-width: 1280px;
    margin: 0 auto;
    padding: 0 2rem;
  }

  @media (min-width: 640px) {
    .hero__container {
      padding: 0 2.5rem;
    }
  }

  @media (min-width: 768px) {
    .hero__container {
      padding: 0 3rem;
    }
  }

  @media (min-width: 1024px) {
    .hero__container {
      padding: 0 3rem;
    }
  }

  @media (min-width: 1280px) {
    .hero__container {
      padding: 0 4rem;
    }
  }

  /* Content Layout */
  .hero__content {
    display: grid;
    grid-template-columns: 1fr;
    gap: 4rem;
    align-items: center;
  }

  @media (min-width: 1024px) {
    .hero__content {
      grid-template-columns: 5fr 4fr;
      gap: 6rem;
    }
  }

  /* Badge */
  .hero__badge {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1.25rem;
    background: rgba(59, 130, 246, 0.08);
    border: 1px solid rgba(59, 130, 246, 0.2);
    border-radius: 50px;
    font-size: 0.875rem;
    font-weight: 500;
    margin-bottom: 2rem;
    backdrop-filter: blur(12px);
    transition: all 0.3s ease;
  }

  .hero__badge:hover {
    background: rgba(59, 130, 246, 0.12);
    transform: translateY(-2px);
  }

  .hero__badge-indicator {
    width: 8px;
    height: 8px;
    background: #10b981;
    border-radius: 50%;
    animation: pulse 2s infinite;
  }

  .hero__badge-text {
    color: #3b82f6;
    font-weight: 600;
  }

  .hero__badge-count {
    color: #6b7280;
    font-size: 0.8125rem;
  }

  /* Typography */
  .hero__headline {
    font-size: clamp(2.5rem, 5vw, 4rem);
    font-weight: 800;
    line-height: 1.1;
    letter-spacing: -0.025em;
    margin-bottom: 1.5rem;
  }

  .hero__headline-line {
    display: block;
    color: #0f172a;
  }

  :global(.dark) .hero__headline-line {
    color: #f8fafc;
  }

  .hero__headline-accent {
    display: block;
    background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: textShimmer 3s ease-in-out infinite;
  }

  .hero__subheadline {
    font-size: 1.25rem;
    line-height: 1.6;
    color: #64748b;
    margin-bottom: 2.5rem;
    max-width: 540px;
  }

  :global(.dark) .hero__subheadline {
    color: #cbd5e1;
  }

  /* CTA Group */
  .hero__cta-group {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    margin-bottom: 3rem;
  }

  :global(.hero__cta-primary) {
    background: #3b82f6;
    color: white;
    padding: 1rem 2rem;
    border-radius: 12px;
    font-weight: 600;
    font-size: 1rem;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.25);
    border: 2px solid transparent;
  }

  :global(.hero__cta-primary:hover) {
    background: #2563eb;
    transform: translateY(-2px);
    box-shadow: 0 8px 25px -3px rgba(59, 130, 246, 0.35);
  }

  .hero__cta-icon {
    width: 1.25rem;
    height: 1.25rem;
    transition: transform 0.2s ease;
  }

  :global(.hero__cta-primary:hover) .hero__cta-icon {
    transform: translateX(2px);
  }

  :global(.hero__cta-secondary) {
    background: white;
    color: #374151;
    padding: 1rem 2rem;
    border: 2px solid #e5e7eb;
    border-radius: 12px;
    font-weight: 600;
    font-size: 1rem;
    transition: all 0.3s ease;
    backdrop-filter: blur(8px);
  }

  :global(.dark .hero__cta-secondary) {
    background: rgba(31, 41, 55, 0.8);
    color: #f3f4f6;
    border-color: #374151;
  }

  :global(.hero__cta-secondary:hover) {
    border-color: #3b82f6;
    color: #3b82f6;
    background: rgba(248, 250, 252, 0.9);
    transform: translateY(-1px);
  }

  /* Metrics */
  .hero__metrics {
    display: flex;
    align-items: center;
    gap: 2rem;
    flex-wrap: wrap;
  }

  .hero__metric {
    text-align: center;
    transition: transform 0.3s ease;
  }

  .hero__metric:hover {
    transform: translateY(-4px);
  }

  .hero__metric-value {
    display: block;
    font-size: 1.875rem;
    font-weight: 700;
    color: #0f172a;
    line-height: 1.2;
  }

  :global(.dark) .hero__metric-value {
    color: #f8fafc;
  }

  .hero__metric-label {
    display: block;
    font-size: 0.875rem;
    color: #6b7280;
    margin-top: 0.25rem;
  }

  :global(.dark) .hero__metric-label {
    color: #9ca3af;
  }

  .hero__metric-divider {
    width: 1px;
    height: 2.5rem;
    background: #e5e7eb;
  }

  :global(.dark) .hero__metric-divider {
    background: #374151;
  }

  /* Visual Column */
  .hero__visual-column {
    position: relative;
    display: flex;
    flex-direction: column;
    gap: 2rem;
  }

  /* Feature Cards */
  .hero__feature-cards {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .hero__feature-card {
    background: rgba(255, 255, 255, 0.95);
    border: 1px solid rgba(229, 231, 235, 0.8);
    border-radius: 16px;
    padding: 1.5rem;
    display: flex;
    align-items: start;
    gap: 1rem;
    backdrop-filter: blur(12px);
    transition: all 0.3s ease;
    cursor: pointer;
  }

  :global(.dark) .hero__feature-card {
    background: rgba(31, 41, 55, 0.95);
    border-color: rgba(55, 65, 81, 0.8);
  }

  .hero__feature-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 32px -4px rgba(0, 0, 0, 0.1);
    border-color: rgba(59, 130, 246, 0.3);
  }

  .hero__feature-icon {
    width: 2.5rem;
    height: 2.5rem;
    border-radius: 12px;
    background: linear-gradient(135deg, #3b82f6, #8b5cf6);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    flex-shrink: 0;
  }

  .hero__feature-icon svg {
    width: 1.25rem;
    height: 1.25rem;
  }

  .hero__feature-content {
    flex: 1;
  }

  .hero__feature-title {
    font-size: 1rem;
    font-weight: 600;
    color: #0f172a;
    margin-bottom: 0.25rem;
  }

  :global(.dark) .hero__feature-title {
    color: #f8fafc;
  }

  .hero__feature-description {
    font-size: 0.875rem;
    color: #6b7280;
    line-height: 1.4;
  }

  :global(.dark) .hero__feature-description {
    color: #9ca3af;
  }

  /* Testimonial Card */
  .hero__testimonial-card {
    background: rgba(255, 255, 255, 0.98);
    border: 1px solid rgba(229, 231, 235, 0.8);
    border-radius: 20px;
    padding: 2rem;
    backdrop-filter: blur(16px);
    box-shadow: 0 20px 50px -12px rgba(0, 0, 0, 0.15);
    animation: floatTestimonial 8s ease-in-out infinite;
    position: relative;
    overflow: hidden;
  }

  :global(.dark) .hero__testimonial-card {
    background: rgba(31, 41, 55, 0.98);
    border-color: rgba(55, 65, 81, 0.8);
  }

  .hero__testimonial-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, #3b82f6, #8b5cf6, #10b981);
    animation: shimmer 2s ease-in-out infinite;
  }

  .hero__testimonial-content {
    position: relative;
  }

  .hero__testimonial-rating {
    display: flex;
    gap: 0.25rem;
    margin-bottom: 1rem;
  }

  .hero__testimonial-star {
    width: 1rem;
    height: 1rem;
    color: #fbbf24;
  }

  .hero__testimonial-quote {
    font-size: 1rem;
    line-height: 1.6;
    color: #374151;
    margin-bottom: 1.5rem;
    font-style: italic;
  }

  :global(.dark) .hero__testimonial-quote {
    color: #d1d5db;
  }

  .hero__testimonial-author {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .hero__testimonial-avatar {
    width: 2.5rem;
    height: 2.5rem;
    border-radius: 50%;
    background: linear-gradient(135deg, #3b82f6, #8b5cf6);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: 600;
    font-size: 1rem;
  }

  .hero__testimonial-name {
    font-weight: 600;
    color: #0f172a;
    font-size: 0.875rem;
    display: block;
  }

  :global(.dark) .hero__testimonial-name {
    color: #f8fafc;
  }

  .hero__testimonial-role {
    color: #6b7280;
    font-size: 0.75rem;
    margin: 0;
  }

  :global(.dark) .hero__testimonial-role {
    color: #9ca3af;
  }

  /* Animations */
  @keyframes gradientShift {
    0%, 100% { 
      background: linear-gradient(135deg, 
        rgba(59, 130, 246, 0.05) 0%, 
        rgba(139, 92, 246, 0.05) 50%, 
        rgba(16, 185, 129, 0.05) 100%
      );
    }
    50% { 
      background: linear-gradient(135deg, 
        rgba(16, 185, 129, 0.05) 0%, 
        rgba(59, 130, 246, 0.05) 50%, 
        rgba(139, 92, 246, 0.05) 100%
      );
    }
  }

  @keyframes float {
    0%, 100% { transform: translateY(0) rotate(0deg) scale(1); }
    33% { transform: translateY(-20px) rotate(2deg) scale(1.05); }
    66% { transform: translateY(-10px) rotate(-1deg) scale(0.95); }
  }

  @keyframes floatTestimonial {
    0%, 100% { transform: translateY(0) rotate(0deg); }
    50% { transform: translateY(-8px) rotate(1deg); }
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }

  @keyframes textShimmer {
    0%, 100% { 
      background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
      -webkit-background-clip: text;
      background-clip: text;
    }
    50% { 
      background: linear-gradient(135deg, #8b5cf6 0%, #10b981 100%);
      -webkit-background-clip: text;
      background-clip: text;
    }
  }

  @keyframes shimmer {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
  }

  /* RTL Support */
  :global(.rtl) .hero__content {
    direction: rtl;
  }

  :global(.rtl) .hero__cta-icon {
    transform: scaleX(-1);
  }

  :global(.rtl .hero__cta-primary:hover) .hero__cta-icon {
    transform: scaleX(-1) translateX(-2px);
  }

  /* Mobile Responsive */
  @media (max-width: 1023px) {
    .hero {
      padding: 4rem 0;
    }

    .hero__container {
      padding: 0 1.5rem;
    }

    .hero__content {
      gap: 3rem;
    }

    .hero__visual-column {
      order: -1;
    }

    .hero__testimonial-card {
      padding: 1.5rem;
    }
  }

  @media (max-width: 767px) {
    .hero {
      min-height: auto;
      padding: 3rem 0;
    }

    .hero__container {
      padding: 0 1rem;
    }

    .hero__content {
      gap: 2.5rem;
    }

    .hero__headline {
      font-size: clamp(2rem, 8vw, 2.5rem);
      margin-bottom: 1rem;
    }

    .hero__subheadline {
      font-size: 1.125rem;
      margin-bottom: 2rem;
    }

    .hero__cta-group {
      flex-direction: column;
      gap: 0.75rem;
    }

    :global(.hero__cta-primary),
    :global(.hero__cta-secondary) {
      width: 100%;
      justify-content: center;
    }

    .hero__metrics {
      justify-content: space-between;
      width: 100%;
      gap: 1rem;
    }

    .hero__metric-value {
      font-size: 1.5rem;
    }

    .hero__feature-cards {
      gap: 0.75rem;
    }

    .hero__feature-card {
      padding: 1.25rem;
    }
  }

  /* Accessibility */
  @media (prefers-reduced-motion: reduce) {
    .hero__orb,
    .hero__testimonial-card,
    .hero__badge-indicator,
    .hero__gradient,
    .hero__headline-accent {
      animation: none;
    }

    .hero__feature-card:hover,
    .hero__metric:hover,
    :global(.hero__cta-primary:hover),
    :global(.hero__cta-secondary:hover) {
      transform: none;
    }
  }

  /* High Contrast */
  @media (prefers-contrast: high) {
    .hero__badge,
    .hero__feature-card,
    .hero__testimonial-card {
      border-width: 2px;
    }

    :global(.hero__cta-primary),
    :global(.hero__cta-secondary) {
      border-width: 3px;
    }
  }
</style>