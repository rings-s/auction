<script>
  import { t, locale } from '$lib/i18n';
  import ContactForm from '$lib/components/messages/ContactForm.svelte';
  import { fade, fly, draw } from 'svelte/transition';
  import { onMount } from 'svelte';
  import { tweened } from 'svelte/motion';
  import { cubicOut } from 'svelte/easing';
  
  let mounted = false;
  let parallaxElements = [];
  let svgVisible = false;
  
  // Parallax effect on scroll
  function handleScroll() {
    if (!mounted) return;
    const scrollY = window.scrollY;
    
    parallaxElements.forEach(element => {
      const speed = element.dataset.speed || 0.1;
      const yPos = -(scrollY * speed);
      element.style.transform = `translateY(${yPos}px)`;
    });
  }
  
  // Animate SVG elements on hover
  function handleHover(event, enter) {
    const elements = event.currentTarget.querySelectorAll('.animate-on-hover');
    elements.forEach(el => {
      if (enter) {
        el.style.transform = 'translateY(-5px)';
      } else {
        el.style.transform = 'translateY(0)';
      }
    });
  }
  
  // Add subtle animation to SVG elements
  const houseOpacity = tweened(0, {
    duration: 1200,
    easing: cubicOut
  });
  
  // Initialize on mount
  onMount(() => {
    mounted = true;
    parallaxElements = document.querySelectorAll('[data-parallax]');
    window.addEventListener('scroll', handleScroll);
    svgVisible = true;
    houseOpacity.set(1);
    
    return () => {
      window.removeEventListener('scroll', handleScroll);
    };
  });
  
  // Computed values
  $: isRTL = $locale === 'ar';
</script>

<svelte:head>
  <title>{$t('common.contactUs')} | {$t('common.siteName')}</title>
  <meta name="description" content={$t('meta.contactUsDescription')} />
</svelte:head>

<div class="contact-page" class:rtl={isRTL}>
  <div class="contact-grid">
    <!-- Left Side: Villa Silhouette -->
    <div class="contact-illustration" 
         role="img"
         aria-label={$t('contact.findYourDreamHome')}
         on:mouseenter={(e) => handleHover(e, true)}
         on:mouseleave={(e) => handleHover(e, false)}>
      <div class="illustration-container" data-parallax data-speed="0.05">
        {#if svgVisible}
        <svg 
          viewBox="0 0 600 600" 
          xmlns="http://www.w3.org/2000/svg"
          class="villa-svg"
          style="opacity: ${$houseOpacity}">
          <!-- Base/Ground -->
          <path 
            in:draw={{duration: 1500, delay: 300}}
            class="svg-element ground"
            d="M50,450 C150,430 450,430 550,450" 
            fill="none" 
            stroke="var(--color-primary-300)" 
            stroke-width="2" />
          
          <!-- Villa Foundation -->
          <path 
            in:draw={{duration: 1800, delay: 600}}
            class="svg-element foundation animate-on-hover"
            d="M150,450 L150,350 L450,350 L450,450" 
            fill="none" 
            stroke="var(--color-primary-500)" 
            stroke-width="2" />
          
          <!-- Villa Main Structure -->
          <path 
            in:draw={{duration: 2000, delay: 900}}
            class="svg-element main-structure animate-on-hover"
            d="M200,350 L200,250 L400,250 L400,350" 
            fill="none" 
            stroke="var(--color-primary-600)" 
            stroke-width="2" />
          
          <!-- Villa Roof -->
          <path 
            in:draw={{duration: 1500, delay: 1200}}
            class="svg-element roof animate-on-hover"
            d="M150,250 L300,150 L450,250" 
            fill="none" 
            stroke="var(--color-primary-700)" 
            stroke-width="2" />
          
          <!-- Windows -->
          <rect 
            in:draw={{duration: 800, delay: 1500}}
            class="svg-element window animate-on-hover"
            x="220" y="280" 
            width="40" height="40" 
            fill="none" 
            stroke="var(--color-secondary-400)" 
            stroke-width="2" rx="2" />
          
          <rect 
            in:draw={{duration: 800, delay: 1700}}
            class="svg-element window animate-on-hover"
            x="340" y="280" 
            width="40" height="40" 
            fill="none" 
            stroke="var(--color-secondary-400)" 
            stroke-width="2" rx="2" />
          
          <!-- Door -->
          <path 
            in:draw={{duration: 1000, delay: 1900}}
            class="svg-element door animate-on-hover"
            d="M280,350 L280,290 L320,290 L320,350" 
            fill="none" 
            stroke="var(--color-secondary-600)" 
            stroke-width="2" />
          
          <!-- Decorative Elements -->
          <path 
            in:draw={{duration: 1200, delay: 2100}}
            class="svg-element decoration animate-on-hover"
            d="M170,390 L170,370 L210,370 L210,390" 
            fill="none" 
            stroke="var(--color-secondary-500)" 
            stroke-width="1.5" />
          
          <path 
            in:draw={{duration: 1200, delay: 2300}}
            class="svg-element decoration animate-on-hover"
            d="M390,390 L390,370 L430,370 L430,390" 
            fill="none" 
            stroke="var(--color-secondary-500)" 
            stroke-width="1.5" />
          
          <!-- Path to House -->
          <path 
            in:draw={{duration: 1500, delay: 2500}}
            class="svg-element path"
            d="M300,450 L300,350" 
            fill="none" 
            stroke="var(--color-secondary-300)" 
            stroke-width="1.5" 
            stroke-dasharray="5,5" />
        </svg>
        {/if}
        <div class="illustration-caption" in:fade={{delay: 2700, duration: 800}}>
          <h3>{$t('contact.findYourDreamHome')}</h3>
          <p>{$t('contact.weAreHereToHelp')}</p>
        </div>
      </div>
    </div>
    
    <!-- Right Side: Contact Form -->
    <div class="contact-form-container" in:fly={{x: isRTL ? -50 : 50, delay: 300, duration: 800}}>
      <div class="form-header">
        <h1>{$t('common.contactUs')}</h1>
        <p>{$t('contact.getInTouch')}</p>
      </div>
      
      <div class="contact-form-wrapper">
        <ContactForm compact={false} />
      </div>
      
      <div class="contact-info" in:fade={{delay: 600, duration: 800}}>
        <div class="info-item">
          <div class="info-icon">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
            </svg>
          </div>
          <div class="info-content">
            <h4>{$t('contact.phone')}</h4>
            <p>+1 (555) 123-4567</p>
          </div>
        </div>
        
        <div class="info-item">
          <div class="info-icon">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          </div>
          <div class="info-content">
            <h4>{$t('contact.email')}</h4>
            <p>info@luxuryestates.com</p>
          </div>
        </div>
        
        <div class="info-item">
          <div class="info-icon">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </div>
          <div class="info-content">
            <h4>{$t('contact.address')}</h4>
            <p>123 Luxury Avenue, Beverly Hills, CA 90210</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

<style>
  /* Main layout */
  .contact-page {
    width: 100%;
    max-width: 1440px;
    margin: 0 auto;
    padding: 2rem 1rem;
  }
  
  .contact-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 2rem;
    min-height: calc(100vh - 200px);
  }
  
  @media (min-width: 1024px) {
    .contact-grid {
      grid-template-columns: 1fr 1fr;
      gap: 4rem;
    }
  }
  
  /* Left side: Villa illustration */
  .contact-illustration {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 2rem;
  }
  
  .illustration-container {
    width: 100%;
    max-width: 500px;
    position: relative;
    transition: transform 0.3s ease;
  }
  
  .villa-svg {
    width: 100%;
    height: auto;
    transition: all 0.3s ease;
  }
  
  .villa-svg:hover {
    filter: drop-shadow(0 8px 16px rgba(var(--color-primary-rgb), 0.2));
  }
  
  .svg-element {
    transition: all 0.5s ease;
  }
  
  .animate-on-hover {
    transition: transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
  }
  
  .illustration-caption {
    text-align: center;
    margin-top: 2rem;
  }
  
  .illustration-caption h3 {
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--color-primary-700);
    margin-bottom: 0.5rem;
  }
  
  .illustration-caption p {
    font-size: 1rem;
    color: var(--color-gray-600);
  }
  
  /* Right side: Contact form */
  .contact-form-container {
    display: flex;
    flex-direction: column;
    padding: 2rem;
  }
  
  .form-header {
    margin-bottom: 2rem;
  }
  
  .form-header h1 {
    font-size: 2rem;
    font-weight: 700;
    color: var(--color-primary-700);
    margin-bottom: 0.5rem;
  }
  
  .form-header p {
    font-size: 1rem;
    color: var(--color-gray-600);
  }
  
  .contact-form-wrapper {
    /* Custom styling to match form requirements */
    --input-height: 36px; /* 32-40px height */
    --label-size: 14px; /* 14-16px label */
    --spacing-grid: 14px; /* 12-16px spacing */
  }
  
  /* Override styles for the embedded ContactForm component */
  :global(.contact-form-wrapper input:not([type="radio"]):not([type="checkbox"])) {
    height: var(--input-height);
    font-size: calc(var(--input-height) * 0.4);
    padding: 0 calc(var(--spacing-grid) * 0.85);
  }
  
  :global(.contact-form-wrapper label) {
    font-size: var(--label-size);
    margin-bottom: calc(var(--spacing-grid) * 0.5);
  }
  
  :global(.contact-form-wrapper .form-group) {
    margin-bottom: var(--spacing-grid);
  }
  
  /* Contact info section */
  .contact-info {
    margin-top: 3rem;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: calc(var(--spacing-grid) * 1.5);
  }
  
  .info-item {
    display: flex;
    align-items: flex-start;
    gap: calc(var(--spacing-grid) * 0.75);
  }
  
  .info-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    background-color: var(--color-primary-50);
    border-radius: 50%;
    color: var(--color-primary-600);
  }
  
  .info-icon svg {
    width: 20px;
    height: 20px;
  }
  
  .info-content h4 {
    font-size: 1rem;
    font-weight: 600;
    color: var(--color-gray-800);
    margin-bottom: 0.25rem;
  }
  
  .info-content p {
    font-size: 0.875rem;
    color: var(--color-gray-600);
  }
  
  /* RTL support */
  .rtl {
    direction: rtl;
  }
  
  .rtl .info-item {
    flex-direction: row-reverse;
  }
  
  /* Responsive adjustments */
  @media (max-width: 768px) {
    .contact-grid {
      gap: 1rem;
    }
    
    .contact-illustration,
    .contact-form-container {
      padding: 1rem;
    }
    
    .form-header h1 {
      font-size: 1.75rem;
    }
    
    .contact-info {
      grid-template-columns: 1fr;
    }
  }
  
  /* Accessibility enhancements */
  @media (prefers-reduced-motion: reduce) {
    .svg-element,
    .animate-on-hover,
    .villa-svg,
    .illustration-container {
      transition: none !important;
      animation: none !important;
    }
  }
  
  /* High contrast mode support */
  @media (prefers-contrast: more) {
    .svg-element {
      stroke-width: 3px;
    }
    
    .info-icon {
      background-color: var(--color-primary-200);
      color: var(--color-primary-900);
    }
  }
</style>