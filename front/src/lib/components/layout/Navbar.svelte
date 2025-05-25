<!-- src/lib/components/Navbar.svelte -->
<script>
  import { page } from '$app/stores';
  import { user } from '$lib/stores/user';
  import { t } from '$lib/i18n/i18n';
  import { theme } from '$lib/stores/theme';
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
        const response = await fetch('http://localhost:8000/api/accounts/logout/', {
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
    // Apply glassmorphism effect based on scroll
    navbarSolid = scrollY > 10;
    
    // Smart hide/show navbar on scroll
    if (scrollY > 100) { // Only apply after scrolling past hero section
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
    $page.url.pathname.startsWith('/auctions') ? 'auctions' : 'default';
    
  // Define accent colors based on active section
  $: accentColor = {
    home: 'primary',
    properties: 'secondary',
    auctions: 'success',
    default: 'primary'
  }[activeSection];
</script>

<svelte:window bind:scrollY on:scroll={handleScroll} />

<nav 
  class={`fixed w-full z-30 transition-all duration-500 ${
    navbarSolid 
      ? 'bg-white/80 dark:bg-gray-900/80 backdrop-blur-lg border-b border-gray-200/30 dark:border-gray-700/30' 
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
      <div class="flex">
        <div class="flex-shrink-0 flex items-center">
          <a 
            href="/" 
            class="text-2xl font-bold relative group"
          >
            <span class={`relative z-10 transition-colors duration-500 text-${accentColor}-600 dark:text-${accentColor}-400`}>
              RealEstate
            </span>
            <span class={`absolute bottom-0 left-0 w-0 h-0.5 bg-${accentColor}-500 dark:bg-${accentColor}-400 transition-all duration-500 group-hover:w-full rounded-full opacity-70`}></span>
          </a>
        </div>
        
        <!-- Desktop links -->
        <div class="hidden lg:ml-8 lg:flex" class:lg:space-x-8={document.documentElement.dir !== 'rtl'} class:lg:space-x-reverse={document.documentElement.dir === 'rtl'} class:lg:mr-8={document.documentElement.dir === 'rtl'}>
          <slot name="nav-links">
            <a 
              href="/" 
              class={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-all duration-300 ${
                $page.url.pathname === '/' 
                  ? `border-primary-500 text-primary-600 dark:text-primary-400` 
                  : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
              }`}
            >{$t('nav.home')}</a>
            
            <a 
              href="/properties" 
              class={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-all duration-300 ${
                $page.url.pathname.startsWith('/properties') 
                  ? `border-secondary-500 text-secondary-600 dark:text-secondary-400` 
                  : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
              }`}
            >{$t('nav.properties')}</a>
            
            <a 
              href="/auctions" 
              class={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-all duration-300 ${
                $page.url.pathname.startsWith('/auctions') 
                  ? `border-success-500 text-success-600 dark:text-success-400` 
                  : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
              }`}
            >{$t('nav.auctions')}</a>
            
            <a 
              href="/messages" 
              class={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-all duration-300 ${
                $page.url.pathname.startsWith('/messages') 
                  ? `border-primary-500 text-primary-600 dark:text-primary-400` 
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
            <a 
              href="/profile" 
              class="flex text-sm rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-all duration-300 hover:scale-105"
            >
              <span class="sr-only">Open user profile</span>
              {#if $user.avatar_url}
                <img 
                  class="h-9 w-9 rounded-full ring-2 ring-primary-300/50 dark:ring-primary-700/50 shadow-md" 
                  src={$user.avatar_url} 
                  alt={$user.first_name} 
                />
              {:else}
                <div class="h-9 w-9 rounded-full bg-gradient-to-br from-primary-400 to-secondary-500 flex items-center justify-center text-white shadow-lg">
                  {$user.first_name[0]}{$user.last_name[0]}
                </div>
              {/if}
              
              <!-- Tooltip on hover -->
              <div class="absolute -bottom-10 left-1/2 transform -translate-x-1/2 px-2 py-1 bg-gray-900 dark:bg-gray-800 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none whitespace-nowrap">
                {$user.first_name} {$user.last_name}
              </div>
            </a>
          </div>
          
          <button 
            on:click={logout}
            class="relative overflow-hidden px-4 py-2 text-sm font-medium rounded-full transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-danger-400 focus:ring-offset-2 bg-white dark:bg-gray-800 text-danger-600 dark:text-danger-400 border border-danger-200 dark:border-danger-700 hover:bg-danger-50 dark:hover:bg-danger-900/30 shadow-sm"
          >
            <span class="relative z-10">{$t('nav.logout')}</span>
          </button>
        {:else}
          <!-- User is logged out -->
          <a 
            href="/login" 
            class={`relative overflow-hidden px-5 py-2 text-sm font-medium rounded-full transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-${accentColor}-400 focus:ring-offset-2 border border-${accentColor}-200 dark:border-${accentColor}-800 hover:bg-${accentColor}-50 dark:hover:bg-${accentColor}-900/30 text-${accentColor}-600 dark:text-${accentColor}-400`}
            in:fade={{ duration: 400 }}
          >
            <span class="relative z-10">{$t('nav.login')}</span>
          </a>
          
          <a 
            href="/register" 
            class={`relative overflow-hidden px-5 py-2 text-sm font-medium rounded-full transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-${accentColor}-400 focus:ring-offset-2 bg-${accentColor}-600 hover:bg-${accentColor}-700 dark:bg-${accentColor}-500 dark:hover:bg-${accentColor}-600 text-white shadow-sm hover:shadow-md transform hover:translate-y-[-1px]`}
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
          class="inline-flex items-center justify-center p-2 rounded-full text-gray-500 hover:text-gray-600 dark:text-gray-400 dark:hover:text-gray-300 hover:bg-gray-100/50 dark:hover:bg-gray-800/50 backdrop-blur-sm focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary-500 transition-all duration-300"
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
                ? `bg-primary-50/50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300` 
                : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100/50 dark:hover:bg-gray-700/50'
            }`}
            on:click={() => isOpen = false}
            in:fly={{ x: -10, duration: 300, delay: 100 }}
          >
            <span class={`mr-3 text-lg ${$page.url.pathname === '/' ? 'text-primary-500' : 'text-gray-400'}`}>
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
                ? `bg-secondary-50/50 dark:bg-secondary-900/30 text-secondary-700 dark:text-secondary-300` 
                : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100/50 dark:hover:bg-gray-700/50'
            }`}
            on:click={() => isOpen = false}
            in:fly={{ x: -10, duration: 300, delay: 200 }}
          >
            <span class={`mr-3 text-lg ${$page.url.pathname.startsWith('/properties') ? 'text-secondary-500' : 'text-gray-400'}`}>
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path d="M4 4a2 2 0 012-2h8a2 2 0 012 2v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
              </svg>
            </span>
            {$t('nav.properties')}
          </a>
          
          <a 
            href="/auctions" 
            class={`flex items-center pl-3 pr-4 py-3 rounded-lg transition-all duration-300 ${
              $page.url.pathname.startsWith('/auctions') 
                ? `bg-success-50/50 dark:bg-success-900/30 text-success-700 dark:text-success-300` 
                : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100/50 dark:hover:bg-gray-700/50'
            }`}
            on:click={() => isOpen = false}
            in:fly={{ x: -10, duration: 300, delay: 300 }}
          >
            <span class={`mr-3 text-lg ${$page.url.pathname.startsWith('/auctions') ? 'text-success-500' : 'text-gray-400'}`}>
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M12 7a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0V8.414l-4.293 4.293a1 1 0 01-1.414 0L8 10.414l-4.293 4.293a1 1 0 01-1.414-1.414l5-5a1 1 0 011.414 0L11 10.586 14.586 7H12z" clip-rule="evenodd" />
              </svg>
            </span>
            {$t('nav.auctions')}
          </a>
          
          <a 
            href="/messages" 
            class={`flex items-center pl-3 pr-4 py-3 rounded-lg transition-all duration-300 ${
              $page.url.pathname.startsWith('/messages') 
                ? `bg-primary-50/50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300` 
                : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100/50 dark:hover:bg-gray-700/50'
            }`}
            on:click={() => isOpen = false}
            in:fly={{ x: -10, duration: 300, delay: 350 }}
          >
            <span class={`mr-3 text-lg ${$page.url.pathname.startsWith('/messages') ? 'text-primary-500' : 'text-gray-400'}`}>
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
                <img class="h-10 w-10 rounded-full ring-2 ring-primary-300/50 dark:ring-primary-700/50 shadow-md" src={$user.avatar_url} alt={$user.first_name} />
              {:else}
                <div class="h-10 w-10 rounded-full bg-gradient-to-br from-primary-400 to-secondary-500 flex items-center justify-center text-white shadow-lg">
                  {$user.first_name[0]}{$user.last_name[0]}
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
              class="flex items-center px-4 py-3 text-base font-medium rounded-lg transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-primary-400 focus:ring-offset-2 text-primary-700 dark:text-primary-300 hover:bg-primary-50/50 dark:hover:bg-primary-900/30"
              on:click={() => isOpen = false}
              in:fly={{ x: -10, duration: 300, delay: 100 }}
            >
              <span class="mr-3 text-primary-500">
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
              class="flex items-center px-4 py-3 text-base font-medium rounded-lg transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-danger-400 focus:ring-offset-2 text-danger-700 dark:text-danger-300 hover:bg-danger-50/50 dark:hover:bg-danger-900/30"
              in:fly={{ x: -10, duration: 300, delay: 200 }}
            >
              <span class="mr-3 text-danger-500">
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
              class={`flex items-center justify-center py-3 text-base font-medium rounded-lg transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-primary-400 focus:ring-offset-2 border border-${accentColor}-200 dark:border-${accentColor}-800 bg-white dark:bg-gray-900 text-${accentColor}-600 dark:text-${accentColor}-400`}
              on:click={() => isOpen = false}
              in:fly={{ y: 20, duration: 300, delay: 100 }}
            >{$t('nav.login')}</a>
            
            <a 
              href="/register" 
              class={`flex items-center justify-center py-3 text-base font-medium rounded-lg transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-secondary-400 focus:ring-offset-2 bg-${accentColor}-600 hover:bg-${accentColor}-700 dark:bg-${accentColor}-500 dark:hover:bg-${accentColor}-600 text-white shadow-md`}
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