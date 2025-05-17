<!-- src/lib/components/Navbar.svelte -->
<script>
  import { page } from '$app/stores';
  import { user } from '$lib/stores/user';
  import { t } from '$lib/i18n/i18n';
  import { theme } from '$lib/stores/theme';
  import ThemeToggle from './ThemeToggle.svelte';
  import LanguageSelector from './LanguageSelector.svelte';
  import { onMount, afterUpdate } from 'svelte';
  import { fade, fly, slide } from 'svelte/transition';
  import { quintOut } from 'svelte/easing';
  
  let isOpen = false;
  let scrollY;
  let navbarSolid = false;
  
  // Toggle mobile menu
  function toggleMenu() {
    isOpen = !isOpen;
  }
  
  // Close mobile menu when navigating
  afterUpdate(() => {
    // Add an event listener to all navigation links to close the menu
    if (typeof document !== 'undefined') {
      const navLinks = document.querySelectorAll('nav a');
      navLinks.forEach(link => {
        link.addEventListener('click', () => {
          isOpen = false;
        });
      });
    }
  });
  
  // Improved logout function with user store reset
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
        
        // Whether the API call succeeds or fails, we should clear local storage
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        
        // Reset the user store to null explicitly
        user.set(null);
        
        // Redirect to home
        window.location.href = '/';
      }
    } catch (error) {
      console.error('Logout failed:', error);
      
      // Even if there's an error, still clear credentials
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      user.set(null);
    }
  }
  
  // Enhanced scroll handling for navbar style
  function handleScroll() {
    navbarSolid = scrollY > 10;
  }
  
  onMount(() => {
    // Set up scroll listener
    window.addEventListener('scroll', handleScroll);
    
    // Initial check
    handleScroll();
    
    return () => {
      window.removeEventListener('scroll', handleScroll);
    };
  });
</script>

<svelte:window bind:scrollY on:scroll={handleScroll} />

<nav 
class={`fixed w-full z-30 transition-all duration-500 ${
  navbarSolid 
    ? 'bg-white/95 dark:bg-gray-900/95 shadow-lg backdrop-blur-sm transform translate-y-0' 
    : 'bg-transparent shadow-none transform'
}`}
>
<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
  <div class="flex justify-between h-16">
    <div class="flex">
      <div class="flex-shrink-0 flex items-center">
        <a 
          href="/" 
          class="text-2xl font-bold text-primary-700 dark:text-primary-300 relative group overflow-hidden"
        >
          <span class="relative z-10 group-hover:text-primary-500 dark:group-hover:text-primary-400 transition-colors duration-300">RealEstate</span>
          <span class="absolute bottom-0 left-0 w-0 h-1 bg-primary-500 dark:bg-primary-400 transition-all duration-300 group-hover:w-full"></span>
        </a>
      </div>
      <!-- Desktop links, hidden on md and below -->
      <div class="hidden lg:ml-6 lg:flex lg:space-x-8">
        <slot name="nav-links">
          <a 
            href="/" 
            class={`inline-flex items-center px-1 pt-1 border-b-2 transition-all duration-300 ${
              $page.url.pathname === '/' 
                ? 'border-primary-500 text-primary-700 dark:text-primary-300' 
                : 'border-transparent text-gray-600 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 hover:border-primary-300'
            }`}
          >{$t('nav.home')}</a>
          
          <a 
            href="/properties" 
            class={`inline-flex items-center px-1 pt-1 border-b-2 transition-all duration-300 ${
              $page.url.pathname.startsWith('/properties') 
                ? 'border-secondary-500 text-secondary-700 dark:text-secondary-300' 
                : 'border-transparent text-gray-600 dark:text-gray-300 hover:text-secondary-600 dark:hover:text-secondary-400 hover:border-secondary-300'
            }`}
          >{$t('nav.properties')}</a>
          
          <a 
            href="/auctions" 
            class={`inline-flex items-center px-1 pt-1 border-b-2 transition-all duration-300 ${
              $page.url.pathname.startsWith('/auctions') 
                ? 'border-success-500 text-success-700 dark:text-success-300' 
                : 'border-transparent text-gray-600 dark:text-gray-300 hover:text-success-600 dark:hover:text-success-400 hover:border-success-300'
            }`}
          >{$t('nav.auctions')}</a>
        </slot>
      </div>
    </div>
    
    <!-- Right side: Theme, Language, Auth -->
    <div class="hidden lg:ml-6 lg:flex lg:items-center lg:space-x-4">
      <ThemeToggle />
      <LanguageSelector />
      
      {#if $user}
        <!-- User is logged in -->
        <div class="relative">
          <a 
            href="/profile" 
            class="flex text-sm rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-transform duration-300 hover:scale-110"
          >
            <span class="sr-only">Open user profile</span>
            {#if $user.avatar_url}
              <img class="h-8 w-8 rounded-full ring-2 ring-primary-300 dark:ring-primary-700" src={$user.avatar_url} alt={$user.first_name} />
            {:else}
              <div class="h-8 w-8 rounded-full bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center text-white shadow-md">
                {$user.first_name[0]}{$user.last_name[0]}
              </div>
            {/if}
          </a>
        </div>
        
        <button 
          on:click={logout}
          class="relative overflow-hidden px-4 py-2 text-base font-semibold rounded-md transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-danger-400 focus:ring-offset-2 bg-danger-600 hover:bg-danger-700 dark:bg-danger-500 dark:hover:bg-danger-600 text-white dark:text-gray-900 shadow-md hover:shadow-lg transform hover:-translate-y-1"
        >
          <span class="relative z-10">{$t('nav.logout')}</span>
          <span class="absolute inset-0 bg-danger-700 dark:bg-danger-600 transform scale-x-0 origin-left transition-transform duration-300 group-hover:scale-x-100"></span>
        </button>
      {:else}
        <!-- User is logged out - these login/register buttons will always show when $user is null -->
        <a 
          href="/login" 
          class="relative overflow-hidden px-4 py-2 text-sm font-semibold rounded-md transition-all duration-300 shadow-md hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-primary-400 focus:ring-offset-2 bg-primary-600 hover:bg-primary-700 dark:bg-primary-400 dark:hover:bg-primary-500 text-white dark:text-gray-900 transform hover:-translate-y-1"
          in:fade={{ duration: 400 }}
        >
          <span class="relative z-10">{$t('nav.login')}</span>
        </a>
        
        <a 
          href="/register" 
          class="relative overflow-hidden px-4 py-2 text-sm font-semibold rounded-md transition-all duration-300 shadow-md hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-secondary-400 focus:ring-offset-2 bg-secondary-600 hover:bg-secondary-700 dark:bg-secondary-400 dark:hover:bg-secondary-500 text-white dark:text-gray-900 transform hover:-translate-y-1"
          in:fade={{ duration: 400, delay: 100 }}
        >
          <span class="relative z-10">{$t('nav.register')}</span>
        </a>
      {/if}
    </div>
    
    <!-- Mobile menu toggle, visible on xs, sm, md -->
    <div class="flex flex-row items-center gap-4 lg:hidden">
      <ThemeToggle />
      <LanguageSelector />
      
      <button 
        type="button" 
        class="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary-500 transition-all duration-300 hover:rotate-180"
        on:click={toggleMenu}
        aria-label="Toggle navigation menu"
      >
        <span class="sr-only">Open main menu</span>
        {#if isOpen}
          <svg 
            in:fade={{ duration: 200 }}
            class="block w-6 h-6" 
            xmlns="http://www.w3.org/2000/svg" 
            fill="none" 
            viewBox="0 0 24 24" 
            stroke="currentColor" 
            aria-hidden="true"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        {:else}
          <svg 
            in:fade={{ duration: 200 }}
            class="block w-6 h-6" 
            xmlns="http://www.w3.org/2000/svg" 
            fill="none" 
            viewBox="0 0 24 24" 
            stroke="currentColor" 
            aria-hidden="true"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        {/if}
      </button>
    </div>
  </div>
</div>

<!-- Mobile menu, visible on xs, sm, md only -->
{#if isOpen}
  <div 
    class="lg:hidden"
    transition:slide={{ duration: 300, easing: quintOut }}
  >
    <div class="pt-2 pb-3 space-y-1">
      <slot name="mobile-nav-links">
        <a 
          href="/" 
          class={`block pl-3 pr-4 py-2 border-l-4 transition-all duration-300 ${
            $page.url.pathname === '/' 
              ? 'border-primary-500 text-primary-700 dark:text-primary-300 bg-primary-50 dark:bg-gray-900/70' 
              : 'border-transparent text-gray-700 dark:text-gray-300 hover:bg-primary-50 dark:hover:bg-gray-800 hover:border-primary-300'
          }`}
          on:click={() => isOpen = false}
        >{$t('nav.home')}</a>
        
        <a 
          href="/properties" 
          class={`block pl-3 pr-4 py-2 border-l-4 transition-all duration-300 ${
            $page.url.pathname.startsWith('/properties') 
              ? 'border-secondary-500 text-secondary-700 dark:text-secondary-300 bg-secondary-50 dark:bg-gray-900/70' 
              : 'border-transparent text-gray-700 dark:text-gray-300 hover:bg-secondary-50 dark:hover:bg-gray-800 hover:border-secondary-300'
          }`}
          on:click={() => isOpen = false}
        >{$t('nav.properties')}</a>
        
        <a 
          href="/auctions" 
          class={`block pl-3 pr-4 py-2 border-l-4 transition-all duration-300 ${
            $page.url.pathname.startsWith('/auctions') 
              ? 'border-success-500 text-success-700 dark:text-success-300 bg-success-50 dark:bg-gray-900/70' 
              : 'border-transparent text-gray-700 dark:text-gray-300 hover:bg-success-50 dark:hover:bg-gray-800 hover:border-success-300'
          }`}
          on:click={() => isOpen = false}
        >{$t('nav.auctions')}</a>
      </slot>
    </div>
    
    <div class="pt-4 pb-3 border-t border-gray-200 dark:border-gray-700">
      {#if $user}
        <!-- User is logged in (mobile) -->
        <div class="flex items-center px-4">
          <div class="flex-shrink-0">
            {#if $user.avatar_url}
              <img class="h-10 w-10 rounded-full ring-2 ring-primary-300 dark:ring-primary-700" src={$user.avatar_url} alt={$user.first_name} />
            {:else}
              <div class="h-10 w-10 rounded-full bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center text-white shadow-md">
                {$user.first_name[0]}{$user.last_name[0]}
              </div>
            {/if}
          </div>
          <div class="ml-3">
            <div class="text-base font-medium text-gray-800 dark:text-white">{$user.first_name} {$user.last_name}</div>
            <div class="text-sm font-medium text-gray-500 dark:text-gray-400">{$user.email}</div>
          </div>
        </div>
        
        <div class="mt-3 space-y-1 px-4">
          <a 
            href="/profile" 
            class="block px-4 py-2 text-base font-semibold rounded-md transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-primary-400 focus:ring-offset-2 text-primary-700 dark:text-primary-200 hover:bg-primary-50 dark:hover:bg-primary-800/30 transform hover:translate-x-1"
            on:click={() => isOpen = false}
          >{$t('nav.profile')}</a>
          
          <button 
            on:click={() => {
              isOpen = false;
              logout();
            }}
            class="block w-full text-left px-4 py-2 text-base font-semibold rounded-md transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-danger-400 focus:ring-offset-2 bg-danger-600 hover:bg-danger-700 dark:bg-danger-500 dark:hover:bg-danger-600 text-white dark:text-gray-900 shadow-md hover:shadow-lg transform hover:translate-x-1"
          >
            {$t('nav.logout')}
          </button>
        </div>
      {:else}
        <!-- User is logged out (mobile) -->
        <div class="flex flex-col space-y-2 px-4">
          <a 
            href="/login" 
            class="block text-center py-2 text-base font-semibold rounded-md transition-all duration-300 shadow-md hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-primary-400 focus:ring-offset-2 bg-primary-600 hover:bg-primary-700 dark:bg-primary-400 dark:hover:bg-primary-500 text-white dark:text-gray-900 transform hover:translate-y-[-2px]"
            on:click={() => isOpen = false}
            in:fly={{ y: 20, duration: 300, delay: 100 }}
          >{$t('nav.login')}</a>
          
          <a 
            href="/register" 
            class="block text-center py-2 text-base font-semibold rounded-md transition-all duration-300 shadow-md hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-secondary-400 focus:ring-offset-2 bg-secondary-600 hover:bg-secondary-700 dark:bg-secondary-400 dark:hover:bg-secondary-500 text-white dark:text-gray-900 transform hover:translate-y-[-2px]"
            on:click={() => isOpen = false}
            in:fly={{ y: 20, duration: 300, delay: 200 }}
          >{$t('nav.register')}</a>
        </div>
      {/if}
    </div>
  </div>
{/if}
</nav>

<!-- Add padding for fixed navbar with smooth transition -->
<div class="h-16 transition-all duration-300"></div>