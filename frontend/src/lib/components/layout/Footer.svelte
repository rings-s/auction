<!-- src/lib/components/layout/Footer.svelte -->
<script>
  import { onMount } from 'svelte';
  import { browser } from '$app/environment';
  
  // Safe import on client
  let isAuthenticated = false;
  
  // Get current year for copyright
  const currentYear = new Date().getFullYear();
  
  // Footer sections for organization
  const quickLinks = [
    { href: '/', label: 'Home' },
    { href: '/auctions', label: 'Auctions' },
    { href: '/categories', label: 'Categories' },
    { href: '/about', label: 'About Us' },
    { href: '/contact', label: 'Contact' }
  ];
  
  const legalLinks = [
    { href: '/terms', label: 'Terms of Service' },
    { href: '/privacy', label: 'Privacy Policy' },
    { href: '/cookies', label: 'Cookie Policy' },
    { href: '/faq', label: 'FAQ' }
  ];
  
  const userLinks = [
    { href: '/dashboard', label: 'Dashboard', authRequired: true },
    { href: '/profile', label: 'My Profile', authRequired: true },
    { href: '/auctions/my-bids', label: 'My Bids', authRequired: true },
    { href: '/register', label: 'Create Account', authRequired: false },
    { href: '/login', label: 'Sign In', authRequired: false }
  ];
  
  // Social media links with proper hrefs
  const socialLinks = [
    { href: "https://facebook.com/gudic", label: "Facebook" },
    { href: "https://instagram.com/gudic", label: "Instagram" },
    { href: "https://twitter.com/gudic", label: "Twitter" }
  ];
  
  onMount(async () => {
    if (browser) {
      // Import auth store on client-side only
      const authModule = await import('$lib/stores/authStore');
      
      // Subscribe to auth state
      const unsubAuth = authModule.isAuthenticated.subscribe(value => {
        isAuthenticated = value;
      });
      
      return () => {
        unsubAuth();
      };
    }
  });
</script>

<footer class="glass-effect border-t border-white/20 mt-20">
<!-- Newsletter section - top part of footer -->
<div class="bg-gradient">
  <div class="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:py-16 lg:px-8 flex flex-col md:flex-row justify-between items-center">
    <div class="max-w-xl mb-8 md:mb-0">
      <h2 class="text-2xl font-bold text-white tracking-tight">
        Stay updated with latest auctions
      </h2>
      <p class="mt-3 text-white text-base opacity-80">
        Subscribe to our newsletter and never miss new auctions, promotions and auction tips.
      </p>
    </div>
    <div class="w-full md:w-96">
      <form class="sm:flex" action="/newsletter/subscribe" method="POST">
        <label for="email-address" class="sr-only">Email address</label>
        <input
          id="email-address"
          name="email-address"
          type="email"
          autocomplete="email"
          required
          class="w-full px-5 py-3 placeholder-text-light focus:ring-primary-blue focus:border-primary-blue border-white rounded-xl"
          placeholder="Enter your email"
        />
        <div class="mt-3 sm:mt-0 sm:ml-3">
          <button
            type="submit"
            class="w-full flex items-center justify-center px-5 py-3 border border-transparent text-base font-medium rounded-xl shadow-sm text-secondary-blue bg-white hover:bg-neutral-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-white"
          >
            Subscribe
          </button>
        </div>
      </form>
      <p class="mt-3 text-sm text-white opacity-80 text-center md:text-left">
        We care about your data. Read our <a href="/privacy" class="text-white underline">Privacy Policy</a>.
      </p>
    </div>
  </div>
</div>

<!-- Main footer with links -->
<div class="max-w-7xl mx-auto py-12 px-4 overflow-hidden sm:px-6 lg:px-8">
  <nav class="flex flex-wrap justify-center -mx-5 -my-2">
    <div class="px-5 py-2 w-full md:w-1/3 lg:w-1/4 mb-8 md:mb-0">
      <div class="flex items-center mb-4">
        <div class="w-10 h-10 rounded-full bg-gradient-to-br from-primary-blue to-primary-peach flex items-center justify-center mr-2 shadow-md">
          <span class="text-white font-bold text-lg">G</span>
        </div>
        <span class="font-bold text-xl text-text-dark">GUDIC</span>
      </div>
      <p class="text-base text-text-medium mb-4 max-w-xs">
        The next-generation platform connecting professionals worldwide through our secure and transparent auction system.
      </p>
      <div class="flex space-x-4">
        {#each socialLinks as { href, label }}
          <a href={href} class="text-text-medium hover:text-secondary-blue transition-colors">
            <span class="sr-only">{label}</span>
            {#if label === 'Facebook'}
              <svg class="h-6 w-6" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path fill-rule="evenodd" d="M22 12c0-5.523-4.477-10-10-10S2 6.477 2 12c0 4.991 3.657 9.128 8.438 9.878v-6.987h-2.54V12h2.54V9.797c0-2.506 1.492-3.89 3.777-3.89 1.094 0 2.238.195 2.238.195v2.46h-1.26c-1.243 0-1.63.771-1.63 1.562V12h2.773l-.443 2.89h-2.33v6.988C18.343 21.128 22 16.991 22 12z" clip-rule="evenodd" />
              </svg>
            {:else if label === 'Instagram'}
              <svg class="h-6 w-6" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path fill-rule="evenodd" d="M12.315 2c2.43 0 2.784.013 3.808.06 1.064.049 1.791.218 2.427.465a4.902 4.902 0 011.772 1.153 4.902 4.902 0 011.153 1.772c.247.636.416 1.363.465 2.427.048 1.067.06 1.407.06 4.123v.08c0 2.643-.012 2.987-.06 4.043-.049 1.064-.218 1.791-.465 2.427a4.902 4.902 0 01-1.153 1.772 4.902 4.902 0 01-1.772 1.153c-.636.247-1.363.416-2.427.465-1.067.048-1.407.06-4.123.06h-.08c-2.643 0-2.987-.012-4.043-.06-1.064-.049-1.791-.218-2.427-.465a4.902 4.902 0 01-1.772-1.153 4.902 4.902 0 01-1.153-1.772c-.247-.636-.416-1.363-.465-2.427-.047-1.024-.06-1.379-.06-3.808v-.63c0-2.43.013-2.784.06-3.808.049-1.064.218-1.791.465-2.427a4.902 4.902 0 011.153-1.772A4.902 4.902 0 015.45 2.525c.636-.247 1.363-.416 2.427-.465C8.901 2.013 9.256 2 11.685 2h.63zm-.081 1.802h-.468c-2.456 0-2.784.011-3.807.058-.975.045-1.504.207-1.857.344-.467.182-.8.398-1.15.748-.35.35-.566.683-.748 1.15-.137.353-.3.882-.344 1.857-.047 1.023-.058 1.351-.058 3.807v.468c0 2.456.011 2.784.058 3.807.045.975.207 1.504.344 1.857.182.466.399.8.748 1.15.35.35.683.566 1.15.748.353.137.882.3 1.857.344 1.054.048 1.37.058 4.041.058h.08c2.597 0 2.917-.01 3.96-.058.976-.045 1.505-.207 1.858-.344.466-.182.8-.398 1.15-.748.35-.35.566-.683.748-1.15.137-.353.3-.882.344-1.857.048-1.055.058-1.37.058-4.041v-.08c0-2.597-.01-2.917-.058-3.96-.045-.976-.207-1.505-.344-1.858a3.097 3.097 0 00-.748-1.15 3.098 3.098 0 00-1.15-.748c-.353-.137-.882-.3-1.857-.344-1.023-.047-1.351-.058-3.807-.058zM12 6.865a5.135 5.135 0 110 10.27 5.135 5.135 0 010-10.27zm0 1.802a3.333 3.333 0 100 6.666 3.333 3.333 0 000-6.666zm5.338-3.205a1.2 1.2 0 110 2.4 1.2 1.2 0 010-2.4z" clip-rule="evenodd" />
              </svg>
            {:else if label === 'Twitter'}
              <svg class="h-6 w-6" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path d="M8.29 20.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0022 5.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.106 4.106 0 001.27 5.477A4.072 4.072 0 012.8 9.713v.052a4.105 4.105 0 003.292 4.022 4.095 4.095 0 01-1.853.07 4.108 4.108 0 003.834 2.85A8.233 8.233 0 012 18.407a11.616 11.616 0 006.29 1.84" />
              </svg>
            {/if}
          </a>
        {/each}
      </div>
    </div>
    
    <div class="px-5 py-2 w-1/2 md:w-1/6 lg:w-1/6">
      <h3 class="text-sm font-semibold text-text-light tracking-wider uppercase mb-4">
        Quick Links
      </h3>
      <ul class="space-y-2">
        {#each quickLinks as { href, label }}
          <li>
            <a href={href} class="text-base text-text-medium hover:text-secondary-blue transition-colors">
              {label}
            </a>
          </li>
        {/each}
      </ul>
    </div>
    
    <div class="px-5 py-2 w-1/2 md:w-1/6 lg:w-1/6">
      <h3 class="text-sm font-semibold text-text-light tracking-wider uppercase mb-4">
        Legal
      </h3>
      <ul class="space-y-2">
        {#each legalLinks as { href, label }}
          <li>
            <a href={href} class="text-base text-text-medium hover:text-secondary-blue transition-colors">
              {label}
            </a>
          </li>
        {/each}
      </ul>
    </div>
    
    <div class="px-5 py-2 w-1/2 md:w-1/6 lg:w-1/6 mt-6 md:mt-0">
      <h3 class="text-sm font-semibold text-text-light tracking-wider uppercase mb-4">
        Account
      </h3>
      <ul class="space-y-2">
        {#each userLinks as { href, label, authRequired }}
          {#if (authRequired && browser && isAuthenticated) || (!authRequired && browser && !isAuthenticated) || (!authRequired)}
            <li>
              <a href={href} class="text-base text-text-medium hover:text-secondary-blue transition-colors">
                {label}
              </a>
            </li>
          {/if}
        {/each}
      </ul>
    </div>
  </nav>
  
  <!-- Copyright section -->
  <div class="mt-12 pt-8 border-t border-primary-blue/10 flex flex-col md:flex-row justify-between items-center">
    <p class="text-base text-text-medium">
      &copy; {currentYear} GUDIC. All rights reserved.
    </p>
    <div class="mt-6 md:mt-0 flex items-center space-x-4">
      <a href="/support" class="text-sm text-text-medium hover:text-secondary-blue transition-colors">
        Support
      </a>
      <span class="h-4 w-px bg-primary-blue/20"></span>
      <a href="/sitemap" class="text-sm text-text-medium hover:text-secondary-blue transition-colors">
        Sitemap
      </a>
      <span class="h-4 w-px bg-primary-blue/20"></span>
      <a href="/accessibility" class="text-sm text-text-medium hover:text-secondary-blue transition-colors">
        Accessibility
      </a>
    </div>
  </div>
</div>
</footer>

<style>
  .bg-gradient {
    background: linear-gradient(135deg, var(--secondary-blue), var(--secondary-peach));
    border-radius: 1rem;
    margin: 2rem;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
  }
</style>