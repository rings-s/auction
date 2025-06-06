<!-- src/lib/components/layout/Navbar.svelte -->
<script>
  import { page } from '$app/stores';
  import { user } from '$lib/stores/user';
	import { t, locale } from '$lib/i18n';
  import { theme } from '$lib/stores/theme';
  import { AUTH_ENDPOINTS } from '$lib/constants';
  import ThemeToggle from '$lib/components/ui/ThemeToggle.svelte';
  import LanguageSelector from '../shared/LanguageSelector.svelte';
  import { onMount, afterUpdate } from 'svelte';
  import { fade, fly, slide, scale } from 'svelte/transition';
  import { spring } from 'svelte/motion';
  import { cubicInOut, elasticOut } from 'svelte/easing';
  
  let isOpen = false;
  let scrollY;
  let navbarSolid = false;
  let prevScrollY = 0;
  let isNavbarVisible = true;
  
  // Toggle mobile menu with enhanced animation
  function toggleMenu() {
    isOpen = !isOpen;
  }
  
  // Close mobile menu when navigating
  afterUpdate(() => {
    if (typeof document !== 'undefined') {
      const navLinks = document.querySelectorAll('nav a');
      navLinks.forEach(link => {
        link.addEventListener('click', () => {
          isOpen = false;
        });
      });
    }
  });
  
  // Improved logout function
  async function logout() {
    try {
      const refreshToken = localStorage.getItem('refreshToken');
      
      if (refreshToken) {
        const response = await fetch(AUTH_ENDPOINTS.LOGOUT, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ refresh: refreshToken }),
        });
        
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        user.set(null);
        window.location.href = '/';
      }
    } catch (error) {
      console.error('Logout failed:', error);
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      user.set(null);
    }
  }
  
  // Enhanced scroll handling for modern sticky behavior
  function handleScroll() {
    navbarSolid = scrollY > 10;
    
    if (scrollY > 100) {
      isNavbarVisible = scrollY < prevScrollY || scrollY < 50;
    } else {
      isNavbarVisible = true;
    }
    
    prevScrollY = scrollY;
  }
  
  onMount(() => {
    window.addEventListener('scroll', handleScroll);
    handleScroll();
    
    return () => {
      window.removeEventListener('scroll', handleScroll);
    };
  });
  
  // Determine active section for adaptive color theming
  $: activeSection = 
    $page.url.pathname === '/' ? 'home' :
    $page.url.pathname.startsWith('/properties') ? 'properties' :
    $page.url.pathname.startsWith('/auctions') ? 'auctions' :
    $page.url.pathname.startsWith('/dashboard') ? 'dashboard' :
    $page.url.pathname.startsWith('/messages') ? 'messages' : 'default';
    
  // Fixed color classes - using static classes instead of dynamic ones
  $: sectionStyles = {
    home: {
      logoAccent: 'from-blue-500 to-blue-600',
      navActive: 'border-blue-500 text-blue-600 dark:text-blue-400',
      loginBtn: 'border-blue-200 dark:border-blue-800 hover:bg-blue-50 dark:hover:bg-blue-900/30 text-blue-600 dark:text-blue-400 focus:ring-blue-400',
      signupBtn: 'bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 focus:ring-blue-400'
    },
    properties: {
      logoAccent: 'from-emerald-500 to-emerald-600',
      navActive: 'border-emerald-500 text-emerald-600 dark:text-emerald-400',
      loginBtn: 'border-emerald-200 dark:border-emerald-800 hover:bg-emerald-50 dark:hover:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400 focus:ring-emerald-400',
      signupBtn: 'bg-emerald-600 hover:bg-emerald-700 dark:bg-emerald-500 dark:hover:bg-emerald-600 focus:ring-emerald-400'
    },
    auctions: {
      logoAccent: 'from-orange-500 to-orange-600',
      navActive: 'border-orange-500 text-orange-600 dark:text-orange-400',
      loginBtn: 'border-orange-200 dark:border-orange-800 hover:bg-orange-50 dark:hover:bg-orange-900/30 text-orange-600 dark:text-orange-400 focus:ring-orange-400',
      signupBtn: 'bg-orange-600 hover:bg-orange-700 dark:bg-orange-500 dark:hover:bg-orange-600 focus:ring-orange-400'
    },
    dashboard: {
      logoAccent: 'from-purple-500 to-purple-600',
      navActive: 'border-purple-500 text-purple-600 dark:text-purple-400',
      loginBtn: 'border-purple-200 dark:border-purple-800 hover:bg-purple-50 dark:hover:bg-purple-900/30 text-purple-600 dark:text-purple-400 focus:ring-purple-400',
      signupBtn: 'bg-purple-600 hover:bg-purple-700 dark:bg-purple-500 dark:hover:bg-purple-600 focus:ring-purple-400'
    },
    messages: {
      logoAccent: 'from-indigo-500 to-indigo-600',
      navActive: 'border-indigo-500 text-indigo-600 dark:text-indigo-400',
      loginBtn: 'border-indigo-200 dark:border-indigo-800 hover:bg-indigo-50 dark:hover:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 focus:ring-indigo-400',
      signupBtn: 'bg-indigo-600 hover:bg-indigo-700 dark:bg-indigo-500 dark:hover:bg-indigo-600 focus:ring-indigo-400'
    },
    default: {
      logoAccent: 'from-blue-500 to-blue-600',
      navActive: 'border-blue-500 text-blue-600 dark:text-blue-400',
      loginBtn: 'border-blue-200 dark:border-blue-800 hover:bg-blue-50 dark:hover:bg-blue-900/30 text-blue-600 dark:text-blue-400 focus:ring-blue-400',
      signupBtn: 'bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 focus:ring-blue-400'
    }
  };

  $: currentStyles = sectionStyles[activeSection] || sectionStyles.default;

  // Check if user can access dashboard
  $: canAccessDashboard = $user && $user.is_verified;
</script>

<svelte:window bind:scrollY on:scroll={handleScroll} />

<nav 
  class={`fixed w-full z-30 transition-all duration-500 ${
    navbarSolid 
      ? 'bg-white/80 dark:bg-gray-900/80 backdrop-blur-lg shadow-lg border-b border-gray-200/50 dark:border-gray-700/50' 
      : 'bg-transparent'
  } ${
    isNavbarVisible
      ? 'transform translate-y-0' 
      : 'transform -translate-y-full'
  }`}
>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="flex justify-between h-16">
      <!-- Logo area -->
      <div class="flex lg:gap-x-12">
        <div class="flex-shrink-0 flex items-center">
          <a 
            href="/" 
            class="flex items-center space-x-3 relative group"
          >
            <!-- Logo Image -->
            <div class="relative">
              <img 
                src="/logo.png" 
                alt="Real Estate Platform" 
                class="h-10 w-auto transition-all duration-300 group-hover:scale-105"
              />
              <!-- Gradient overlay on hover -->
              <div class={`absolute inset-0 bg-gradient-to-r ${currentStyles.logoAccent} opacity-0 group-hover:opacity-20 transition-opacity duration-300 rounded-lg`}></div>
            </div>
            

            
            <!-- Animated underline -->
            <span class={`absolute bottom-0 left-0 w-0 h-0.5 bg-gradient-to-r ${currentStyles.logoAccent} transition-all duration-500 group-hover:w-full rounded-full opacity-70`}></span>
          </a>
        </div>
        
        <!-- Desktop links with fixed spacing -->
        <div class="hidden lg:flex lg:space-x-8">
          <slot name="nav-links">
            <a 
              href="/" 
              class={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-all duration-300 ${
                $page.url.pathname === '/' 
                  ? currentStyles.navActive
                  : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
              }`}
            >{$t('nav.home')}</a>
            
            <a 
              href="/properties" 
              class={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-all duration-300 ${
                $page.url.pathname.startsWith('/properties') 
                  ? 'border-emerald-500 text-emerald-600 dark:text-emerald-400'
                  : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
              }`}
            >{$t('nav.properties')}</a>
            
            <a 
              href="/auctions" 
              class={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-all duration-300 ${
                $page.url.pathname.startsWith('/auctions') 
                  ? 'border-orange-500 text-orange-600 dark:text-orange-400'
                  : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
              }`}
            >{$t('nav.auctions')}</a>
            
            <a 
              href="/messages" 
              class={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-all duration-300 ${
                $page.url.pathname.startsWith('/messages') 
                  ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
                  : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
              }`}
            >{$t('nav.messages')}</a>
          </slot>
        </div>
      </div>
      
      <!-- Right side: Theme, Language, Auth -->
      <div class="hidden lg:ml-6 lg:flex lg:items-center lg:space-x-5">
        <div class="opacity-80 hover:opacity-100 transition-opacity duration-300">
          <ThemeToggle />
        </div>
        <div class="opacity-80 hover:opacity-100 transition-opacity duration-300">
          <LanguageSelector />
        </div>
        
        {#if $user}
          <!-- User is logged in -->
          <div class="relative group">
            <button 
              class="flex text-sm rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-300 hover:scale-105"
              aria-expanded="false"
              aria-haspopup="true"
            >
              <span class="sr-only">Open user menu</span>
              {#if $user.avatar_url}
                <img 
                  class="h-9 w-9 rounded-full ring-2 ring-blue-300/50 dark:ring-blue-700/50 shadow-md" 
                  src={$user.avatar_url} 
                  alt={$user.first_name} 
                />
              {:else}
                <div class={`h-9 w-9 rounded-full bg-gradient-to-br ${currentStyles.logoAccent} flex items-center justify-center text-white shadow-lg font-medium text-sm`}>
                  {$user.first_name?.[0] || ''}{$user.last_name?.[0] || ''}
                </div>
              {/if}
            </button>
            
            <!-- Dropdown menu -->
            <div class="absolute right-0 z-50 mt-2 w-48 origin-top-right rounded-xl bg-white dark:bg-gray-800 py-1 shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none transform opacity-0 scale-95 pointer-events-none group-hover:opacity-100 group-hover:scale-100 group-hover:pointer-events-auto transition-all duration-200 ease-in-out">
              <div class="px-4 py-3 border-b border-gray-200 dark:border-gray-700">
                <p class="text-sm text-gray-700 dark:text-gray-300 font-medium truncate">{$user.first_name} {$user.last_name}</p>
                <p class="text-xs text-gray-500 dark:text-gray-400 truncate">{$user.email}</p>
              </div>
              
              <a 
                href="/profile" 
                class="block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors duration-200"
              >
                {$t('nav.profile')}
              </a>
              
              {#if canAccessDashboard}
                <a 
                  href="/dashboard" 
                  class={`block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors duration-200 ${
                    $page.url.pathname.startsWith('/dashboard') 
                      ? 'bg-purple-50 dark:bg-purple-900/20 text-purple-700 dark:text-purple-300' 
                      : ''
                  }`}
                >
                  {$t('nav.dashboard')}
                </a>
              {/if}
              
              <div class="border-t border-gray-200 dark:border-gray-700"></div>
              
              <button 
                on:click={logout}
                class="block w-full text-left px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/30 transition-colors duration-200"
              >
                {$t('nav.logout')}
              </button>
            </div>
          </div>
        {:else}
          <!-- User is logged out -->
          <a 
            href="/login" 
            class={`relative overflow-hidden px-5 py-2 text-sm font-medium rounded-full transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2 border ${currentStyles.loginBtn}`}
            in:fade={{ duration: 400 }}
          >
            <span class="relative z-10">{$t('nav.login')}</span>
          </a>
          
          <a 
            href="/register" 
            class={`relative overflow-hidden px-5 py-2 text-sm font-medium rounded-full transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2 text-white shadow-sm hover:shadow-md transform hover:translate-y-[-1px] ${currentStyles.signupBtn}`}
            in:fade={{ duration: 400, delay: 100 }}
          >
            <span class="relative z-10">{$t('nav.register')}</span>
          </a>
        {/if}
      </div>
      
      <!-- Mobile menu toggle -->
      <div class="flex flex-row items-center gap-4 lg:hidden">
        <div class="opacity-80 hover:opacity-100 transition-opacity duration-300">
          <ThemeToggle />
        </div>
        <div class="opacity-80 hover:opacity-100 transition-opacity duration-300">
          <LanguageSelector />
        </div>
        
        <button 
          type="button" 
          class="inline-flex items-center justify-center p-2 rounded-full text-gray-500 hover:text-gray-600 dark:text-gray-400 dark:hover:text-gray-300 hover:bg-gray-100/50 dark:hover:bg-gray-800/50 backdrop-blur-sm focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500 transition-all duration-300"
          on:click={toggleMenu}
          aria-label="Toggle navigation menu"
        >
          <span class="sr-only">Open main menu</span>
          <div class="w-6 h-6 relative flex justify-center items-center">
            <span 
              class={`absolute block w-5 h-0.5 transition-all duration-300 ease-in-out bg-current rounded-full ${isOpen ? 'rotate-45' : '-translate-y-1.5'}`}>
            </span>
            <span 
              class={`absolute block w-5 h-0.5 transition-all duration-300 ease-in-out bg-current rounded-full ${isOpen ? 'opacity-0' : 'opacity-100'}`}>
            </span>
            <span 
              class={`absolute block w-5 h-0.5 transition-all duration-300 ease-in-out bg-current rounded-full ${isOpen ? '-rotate-45' : 'translate-y-1.5'}`}>
            </span>
          </div>
        </button>
      </div>
    </div>
  </div>

  <!-- Mobile menu -->
  {#if isOpen}
    <div 
      class="lg:hidden overflow-hidden"
      transition:slide={{ duration: 400, easing: cubicInOut }}
    >
      <div class="p-3 space-y-1 bg-gray-50/80 dark:bg-gray-800/80 backdrop-blur-lg rounded-xl mx-3 mt-2 mb-3 shadow-lg border border-gray-200/50 dark:border-gray-700/50">
        <slot name="mobile-nav-links">
          <a 
            href="/" 
            class={`flex items-center pl-3 pr-4 py-3 rounded-lg transition-all duration-300 ${
              $page.url.pathname === '/' 
                ? 'bg-blue-50/50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300'
                : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100/50 dark:hover:bg-gray-700/50'
            }`}
            on:click={() => isOpen = false}
            in:fly={{ x: -10, duration: 300, delay: 100 }}
          >
            <span class={`mr-3 text-lg ${$page.url.pathname === '/' ? 'text-blue-500' : 'text-gray-400'}`}>
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z" />
              </svg>
            </span>
            {$t('nav.home')}
          </a>
          
          <a 
            href="/properties" 
            class={`flex items-center pl-3 pr-4 py-3 rounded-lg transition-all duration-300 ${
              $page.url.pathname.startsWith('/properties') 
                ? 'bg-emerald-50/50 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-300'
                : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100/50 dark:hover:bg-gray-700/50'
            }`}
            on:click={() => isOpen = false}
            in:fly={{ x: -10, duration: 300, delay: 200 }}
          >
            <span class={`mr-3 text-lg ${$page.url.pathname.startsWith('/properties') ? 'text-emerald-500' : 'text-gray-400'}`}>
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z" />
              </svg>
            </span>
            {$t('nav.properties')}
          </a>
          
          <a 
            href="/auctions" 
            class={`flex items-center pl-3 pr-4 py-3 rounded-lg transition-all duration-300 ${
              $page.url.pathname.startsWith('/auctions') 
                ? 'bg-orange-50/50 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300'
                : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100/50 dark:hover:bg-gray-700/50'
            }`}
            on:click={() => isOpen = false}
            in:fly={{ x: -10, duration: 300, delay: 300 }}
          >
            <span class={`mr-3 text-lg ${$page.url.pathname.startsWith('/auctions') ? 'text-orange-500' : 'text-gray-400'}`}>
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M12 7a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0V8.414l-4.293 4.293a1 1 0 01-1.414 0L8 10.414l-4.293 4.293a1 1 0 01-1.414-1.414l5-5a1 1 0 011.414 0L11 10.586 14.586 7H12z" clip-rule="evenodd" />
              </svg>
            </span>
            {$t('nav.auctions')}
          </a>

          <!-- Dashboard Link - Mobile -->
          {#if canAccessDashboard}
            <a 
              href="/dashboard" 
              class={`flex items-center pl-3 pr-4 py-3 rounded-lg transition-all duration-300 ${
                $page.url.pathname.startsWith('/dashboard') 
                  ? 'bg-purple-50/50 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300'
                  : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100/50 dark:hover:bg-gray-700/50'
              }`}
              on:click={() => isOpen = false}
              in:fly={{ x: -10, duration: 300, delay: 350 }}
            >
              <span class={`mr-3 text-lg ${$page.url.pathname.startsWith('/dashboard') ? 'text-purple-500' : 'text-gray-400'}`}>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z" />
                </svg>
              </span>
              {$t('nav.dashboard')}
            </a>
          {/if}
          
          <a 
            href="/messages" 
            class={`flex items-center pl-3 pr-4 py-3 rounded-lg transition-all duration-300 ${
              $page.url.pathname.startsWith('/messages') 
                ? 'bg-indigo-50/50 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300'
                : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100/50 dark:hover:bg-gray-700/50'
            }`}
            on:click={() => isOpen = false}
            in:fly={{ x: -10, duration: 300, delay: 400 }}
          >
            <span class={`mr-3 text-lg ${$page.url.pathname.startsWith('/messages') ? 'text-indigo-500' : 'text-gray-400'}`}>
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path d="M2 5a2 2 0 012-2h7a2 2 0 012 2v4a2 2 0 01-2 2H9l-3 3v-3H4a2 2 0 01-2-2V5z" />
                <path d="M15 7v2a4 4 0 01-4 4H9.828l-1.766 1.767c.28.149.599.233.938.233h2l3 3v-3h2a2 2 0 002-2V9a2 2 0 00-2-2h-1z" />
              </svg>
            </span>
            {$t('nav.messages')}
          </a>
        </slot>
      </div>
      
      <div class="p-4 border-t border-gray-200/50 dark:border-gray-700/50 bg-gray-50/80 dark:bg-gray-800/80 backdrop-blur-lg rounded-xl mx-3 mb-3 shadow-lg">
        {#if $user}
          <!-- User is logged in (mobile) -->
          <div class="flex items-center mb-3">
            <div class="flex-shrink-0">
              {#if $user.avatar_url}
                <img class="h-10 w-10 rounded-full ring-2 ring-blue-300/50 dark:ring-blue-700/50 shadow-md" src={$user.avatar_url} alt={$user.first_name} />
              {:else}
                <div class={`h-10 w-10 rounded-full bg-gradient-to-br ${currentStyles.logoAccent} flex items-center justify-center text-white shadow-lg font-medium`}>
                  {$user.first_name?.[0] || ''}{$user.last_name?.[0] || ''}
                </div>
              {/if}
            </div>
            <div class="ml-3">
              <div class="text-base font-medium text-gray-800 dark:text-white">{$user.first_name} {$user.last_name}</div>
              <div class="text-sm font-medium text-gray-500 dark:text-gray-400">{$user.email}</div>
            </div>
          </div>
          
          <div class="flex flex-col space-y-2">
            <a 
              href="/profile" 
              class="flex items-center px-4 py-3 text-base font-medium rounded-lg transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-offset-2 text-blue-700 dark:text-blue-300 hover:bg-blue-50/50 dark:hover:bg-blue-900/30"
              on:click={() => isOpen = false}
              in:fly={{ x: -10, duration: 300, delay: 100 }}
            >
              <span class="mr-3 text-blue-500">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd" />
                </svg>
              </span>
              {$t('nav.profile')}
            </a>
            
            <button 
              on:click={() => {
                isOpen = false;
                logout();
              }}
              class="flex items-center px-4 py-3 text-base font-medium rounded-lg transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-red-400 focus:ring-offset-2 text-red-700 dark:text-red-300 hover:bg-red-50/50 dark:hover:bg-red-900/30"
              in:fly={{ x: -10, duration: 300, delay: 200 }}
            >
              <span class="mr-3 text-red-500">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M3 3a1 1 0 00-1 1v12a1 1 0 001 1h12a1 1 0 001-1V7.414l-5.707-5.707A1 1 0 009.586 1H3zm9 10.414l-3-3 1.414-1.414L12 8.586l1.586-1.586 1.414 1.414-3 3z" clip-rule="evenodd" />
                </svg>
              </span>
              {$t('nav.logout')}
            </button>
          </div>
        {:else}
          <!-- User is logged out (mobile) -->
          <div class="flex flex-col space-y-3">
            <a 
              href="/login" 
              class={`flex items-center justify-center py-3 text-base font-medium rounded-lg transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2 border bg-white dark:bg-gray-900 ${currentStyles.loginBtn}`}
              on:click={() => isOpen = false}
              in:fly={{ y: 20, duration: 300, delay: 100 }}
            >{$t('nav.login')}</a>
            
            <a 
              href="/register" 
              class={`flex items-center justify-center py-3 text-base font-medium rounded-lg transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2 text-white shadow-md ${currentStyles.signupBtn}`}
              on:click={() => isOpen = false}
              in:fly={{ y: 20, duration: 300, delay: 200 }}
            >{$t('nav.register')}</a>
          </div>
        {/if}
      </div>
    </div>
  {/if}
</nav>

<!-- Spacer for fixed navbar -->
<div class="h-16 transition-all duration-300"></div>