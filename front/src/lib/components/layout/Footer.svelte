<!-- src/lib/components/layout/Footer.svelte -->
<script>
  import { t, locale } from '$lib/i18n';
  import { onMount } from 'svelte';
  
  let currentYear = new Date().getFullYear();
  let mounted = false;
  
  onMount(() => {
    mounted = true;
  });
  
  // Quick links organized by category
  const quickLinks = [
    { name: $t('nav.home'), href: '/' },
    { name: $t('nav.properties'), href: '/properties' },
    { name: $t('nav.auctions'), href: '/auctions' },
    { name: $t('nav.about'), href: '/about' }
  ];
  
  const supportLinks = [
    { name: $t('footer.help'), href: '/help' },
    { name: $t('nav.contact'), href: '/contact' },
    { name: $t('footer.faq'), href: '/faq' },
    { name: $t('footer.support'), href: '/support' }
  ];
  
  const legalLinks = [
    { name: $t('footer.privacy'), href: '/privacy' },
    { name: $t('footer.terms'), href: '/terms' },
    { name: $t('footer.cookies'), href: '/cookies' }
  ];
</script>

<footer class="relative bg-gradient-to-br from-gray-50 via-white to-gray-100 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 border-t border-gray-200/50 dark:border-gray-700/50">
  <!-- Decorative background elements -->
  <div class="absolute inset-0 overflow-hidden pointer-events-none">
    <div class="absolute -top-40 -right-40 w-80 h-80 bg-gradient-to-br from-primary-100/30 to-secondary-100/30 dark:from-primary-900/20 dark:to-secondary-900/20 rounded-full blur-3xl"></div>
    <div class="absolute -bottom-40 -left-40 w-80 h-80 bg-gradient-to-tr from-success-100/30 to-primary-100/30 dark:from-success-900/20 dark:to-primary-900/20 rounded-full blur-3xl"></div>
  </div>
  
  <div class="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <!-- Main footer content -->
    <div class="py-16 lg:py-20">
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-8">
        
        <!-- Brand section -->
        <div class="lg:col-span-4 space-y-6">
          <div class="space-y-4">
            <a href="/" class="inline-block group">
              <h2 class="text-3xl font-bold bg-gradient-to-r from-primary-600 via-secondary-600 to-success-600 bg-clip-text text-transparent group-hover:scale-105 transition-transform duration-300">
                RealEstate
              </h2>
            </a>
            <p class="text-gray-600 dark:text-gray-300 text-lg leading-relaxed max-w-md">
              {$t('footer.aboutText')}
            </p>
          </div>
          
          <!-- Contact info with enhanced styling -->
          <div class="space-y-4">
            <div class="flex items-start space-x-3 group">
              <div class="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-lg flex items-center justify-center group-hover:scale-105 transition-transform duration-300">
                <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
              <div>
                <p class="text-sm text-gray-500 dark:text-gray-400 font-medium">Email</p>
                <a href="mailto:info@realestate.com" class="text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 transition-colors duration-300">
                  info@realestate.com
                </a>
              </div>
            </div>
            
            <div class="flex items-start space-x-3 group">
              <div class="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-secondary-500 to-success-500 rounded-lg flex items-center justify-center group-hover:scale-105 transition-transform duration-300">
                <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                </svg>
              </div>
              <div>
                <p class="text-sm text-gray-500 dark:text-gray-400 font-medium">Phone</p>
                <a href="tel:+15551234567" class="text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 transition-colors duration-300">
                  +1 (555) 123-4567
                </a>
              </div>
            </div>
            
            <div class="flex items-start space-x-3 group">
              <div class="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-success-500 to-primary-500 rounded-lg flex items-center justify-center group-hover:scale-105 transition-transform duration-300">
                <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </div>
              <div>
                <p class="text-sm text-gray-500 dark:text-gray-400 font-medium">Address</p>
                <address class="text-gray-700 dark:text-gray-300 not-italic">
                  123 Main Street<br>
                  New York, NY 10001<br>
                  United States
                </address>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Links sections -->
        <div class="lg:col-span-8">
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-8 lg:gap-12">
            
            <!-- Quick Links -->
            <div class="space-y-6">
              <h3 class="text-lg font-bold text-gray-900 dark:text-white relative">
                {$t('footer.quickLinks')}
                <span class="absolute -bottom-2 left-0 w-12 h-0.5 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-full"></span>
              </h3>
              <ul class="space-y-3">
                {#each quickLinks as link}
                  <li>
                    <a 
                      href={link.href} 
                      class="text-gray-600 dark:text-gray-400 hover:text-primary-600 dark:hover:text-primary-400 transition-all duration-300 flex items-center group"
                    >
                      <span class="w-0 group-hover:w-2 h-0.5 bg-primary-500 rounded-full transition-all duration-300 mr-0 group-hover:mr-2"></span>
                      {link.name}
                    </a>
                  </li>
                {/each}
              </ul>
            </div>
            
            <!-- Support -->
            <div class="space-y-6">
              <h3 class="text-lg font-bold text-gray-900 dark:text-white relative">
                {$t('footer.support')}
                <span class="absolute -bottom-2 left-0 w-12 h-0.5 bg-gradient-to-r from-secondary-500 to-success-500 rounded-full"></span>
              </h3>
              <ul class="space-y-3">
                {#each supportLinks as link}
                  <li>
                    <a 
                      href={link.href} 
                      class="text-gray-600 dark:text-gray-400 hover:text-secondary-600 dark:hover:text-secondary-400 transition-all duration-300 flex items-center group"
                    >
                      <span class="w-0 group-hover:w-2 h-0.5 bg-secondary-500 rounded-full transition-all duration-300 mr-0 group-hover:mr-2"></span>
                      {link.name}
                    </a>
                  </li>
                {/each}
              </ul>
            </div>
            
            <!-- Legal -->
            <div class="space-y-6">
              <h3 class="text-lg font-bold text-gray-900 dark:text-white relative">
                {$t('footer.legal')}
                <span class="absolute -bottom-2 left-0 w-12 h-0.5 bg-gradient-to-r from-success-500 to-primary-500 rounded-full"></span>
              </h3>
              <ul class="space-y-3">
                {#each legalLinks as link}
                  <li>
                    <a 
                      href={link.href} 
                      class="text-gray-600 dark:text-gray-400 hover:text-success-600 dark:hover:text-success-400 transition-all duration-300 flex items-center group"
                    >
                      <span class="w-0 group-hover:w-2 h-0.5 bg-success-500 rounded-full transition-all duration-300 mr-0 group-hover:mr-2"></span>
                      {link.name}
                    </a>
                  </li>
                {/each}
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Newsletter section -->
    <div class="py-8 border-t border-gray-200/50 dark:border-gray-700/50">
      <div class="max-w-4xl mx-auto text-center space-y-6">
        <div class="space-y-2">
          <h3 class="text-2xl font-bold text-gray-900 dark:text-white">
            {$t('footer.newsletter.title')}
          </h3>
          <p class="text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
            {$t('footer.newsletter.description')}
          </p>
        </div>
        
        <form class="flex flex-col sm:flex-row gap-3 max-w-md mx-auto">
          <input 
            type="email" 
            placeholder={$t('footer.newsletter.placeholder')}
            class="flex-1 px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-300"
            required
          />
          <button 
            type="submit"
            class="px-6 py-3 bg-gradient-to-r from-primary-600 to-secondary-600 hover:from-primary-700 hover:to-secondary-700 text-white font-medium rounded-lg transition-all duration-300 hover:shadow-lg hover:scale-105 focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
          >
            {$t('footer.newsletter.subscribe')}
          </button>
        </form>
      </div>
    </div>
    
    <!-- Bottom section -->
    <div class="py-8 border-t border-gray-200/50 dark:border-gray-700/50">
      <div class="flex flex-col lg:flex-row justify-between items-center space-y-6 lg:space-y-0">
        
        <!-- Copyright -->
        <div class="flex flex-col sm:flex-row items-center space-y-2 sm:space-y-0 sm:space-x-6">
          <p class="text-gray-500 dark:text-gray-400 text-sm">
            &copy; {currentYear} RealEstate. {$t('footer.rights')}
          </p>
          <p class="text-gray-500 dark:text-gray-400 text-sm">
            {$t('footer.madeBy')} <span class="font-medium text-gray-700 dark:text-gray-300">Ahmed Bashir Ali</span>
          </p>
        </div>
        
        <!-- Social links -->
        <div class="flex items-center space-x-4">
          <p class="text-sm text-gray-500 dark:text-gray-400 mr-2">
            {$t('footer.followUs')}
          </p>
          
          <!-- Facebook -->
          <a href="/" class="group p-2 rounded-lg bg-gray-100 dark:bg-gray-800 hover:bg-blue-50 dark:hover:bg-blue-900/30 transition-all duration-300" aria-label="Facebook">
            <svg class="w-5 h-5 text-gray-600 dark:text-gray-400 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors duration-300" fill="currentColor" viewBox="0 0 24 24">
              <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
            </svg>
          </a>
          
          <!-- Twitter -->
          <a href="/" class="group p-2 rounded-lg bg-gray-100 dark:bg-gray-800 hover:bg-blue-50 dark:hover:bg-blue-900/30 transition-all duration-300" aria-label="Twitter">
            <svg class="w-5 h-5 text-gray-600 dark:text-gray-400 group-hover:text-blue-500 dark:group-hover:text-blue-400 transition-colors duration-300" fill="currentColor" viewBox="0 0 24 24">
              <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/>
            </svg>
          </a>
          
          <!-- Instagram -->
          <a href="/" class="group p-2 rounded-lg bg-gray-100 dark:bg-gray-800 hover:bg-pink-50 dark:hover:bg-pink-900/30 transition-all duration-300" aria-label="Instagram">
            <svg class="w-5 h-5 text-gray-600 dark:text-gray-400 group-hover:text-pink-600 dark:group-hover:text-pink-400 transition-colors duration-300" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12.017 0C5.396 0 .029 5.367.029 11.987c0 6.62 5.367 11.987 11.988 11.987 6.62 0 11.987-5.367 11.987-11.987C24.014 5.367 18.637.001 12.017.001zM8.449 16.988c-1.297 0-2.448-.49-3.323-1.297C4.198 14.895 3.708 13.744 3.708 12.447s.49-2.448 1.418-3.323C6.001 8.198 7.152 7.708 8.449 7.708s2.448.49 3.323 1.416c.875.926 1.365 2.077 1.365 3.374s-.49 2.448-1.365 3.323c-.875.807-2.026 1.167-3.323 1.167zm7.718 0c-1.297 0-2.448-.49-3.323-1.297-.875-.926-1.365-2.077-1.365-3.374s.49-2.448 1.365-3.323c.875-.926 2.026-1.416 3.323-1.416s2.448.49 3.323 1.416c.875.875 1.365 2.026 1.365 3.323s-.49 2.448-1.365 3.374c-.875.807-2.026 1.297-3.323 1.297z"/>
            </svg>
          </a>
          
          <!-- LinkedIn -->
          <a href="/" class="group p-2 rounded-lg bg-gray-100 dark:bg-gray-800 hover:bg-blue-50 dark:hover:bg-blue-900/30 transition-all duration-300" aria-label="LinkedIn">
            <svg class="w-5 h-5 text-gray-600 dark:text-gray-400 group-hover:text-blue-700 dark:group-hover:text-blue-400 transition-colors duration-300" fill="currentColor" viewBox="0 0 24 24">
              <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
            </svg>
          </a>
          
          <!-- YouTube -->
          <a href="/" class="group p-2 rounded-lg bg-gray-100 dark:bg-gray-800 hover:bg-red-50 dark:hover:bg-red-900/30 transition-all duration-300" aria-label="YouTube">
            <svg class="w-5 h-5 text-gray-600 dark:text-gray-400 group-hover:text-red-600 dark:group-hover:text-red-400 transition-colors duration-300" fill="currentColor" viewBox="0 0 24 24">
              <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
            </svg>
          </a>
        </div>
      </div>
    </div>
  </div>
</footer>