<!-- src/lib/components/layout/Header.svelte -->
<script>
  import { onMount, afterUpdate } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { fade, fly } from 'svelte/transition';
  import { slide } from 'svelte/transition';
  import Button from '$lib/components/ui/Button.svelte';
  import { browser } from '$app/environment';

  // Initialize state variables with defaults
  let authStore = null;
  let isAuthenticated = null; // Will be set to a store later
  let primaryRole = null;     // Will be set to a store later
  let searchOpen = null;      // Will be set to a store later
  let user = { first_name: 'User' }; // Default user object
  let scrolled = false;
  let profileMenuOpen = false;
  let mobileMenuOpen = false;
  let categoryMenuOpen = false;
  let sellerActionsOpen = false;
  let lastScrollY = 0;
  let headerVisible = true;
  let profileRef;
  let mobileMenuRef;
  let sellerActionsRef;

  // Computed property to check if user is a seller or admin
  $: isSeller = browser && isAuthenticated && $isAuthenticated && primaryRole && 
                ($primaryRole?.code === 'seller' || $primaryRole?.code === 'admin');

  // Main navigation links
  const navLinks = [
    { href: '/', label: 'Home' },
    { href: '/auctions', label: 'Auctions' },
    { href: '/transactions', label: 'Transactions' },
    { href: '/howitworks', label: 'How it works' },
    { href: '/categories', label: 'Categories' }
  ];

  // Seller action links
  const sellerActions = [
    { href: '/auctions/create', label: 'Create Auction' },
    { href: '/auctions/selling', label: 'My Listings' },
    { href: '/auctions/sold', label: 'Sold Auctions' }
  ];

  // Categories data - static for now
  const categories = [
    { slug: 'real-estate', name: 'Real Estate', icon: 'home' },
    { slug: 'vehicles', name: 'Vehicles', icon: 'car' },
    { slug: 'machinery', name: 'Machinery', icon: 'cog' },
    { slug: 'factories', name: 'Factories', icon: 'building' },
    { slug: 'heavy-vehicles', name: 'Heavy Vehicles', icon: 'truck' }
  ];

  // Toggle functions
  function toggleProfileMenu(event) {
    event.stopPropagation();
    profileMenuOpen = !profileMenuOpen;
    if (profileMenuOpen) {
      mobileMenuOpen = false;
      categoryMenuOpen = false;
      sellerActionsOpen = false;
    }
  }

  function toggleMobileMenu() {
    mobileMenuOpen = !mobileMenuOpen;
    if (mobileMenuOpen) {
      profileMenuOpen = false;
      categoryMenuOpen = false;
      sellerActionsOpen = false;
    }
  }

  function toggleCategoryMenu() {
    categoryMenuOpen = !categoryMenuOpen;
    if (categoryMenuOpen) {
      profileMenuOpen = false;
      sellerActionsOpen = false;
    }
  }

  function toggleSellerActions(event) {
    event.stopPropagation();
    sellerActionsOpen = !sellerActionsOpen;
    if (sellerActionsOpen) {
      profileMenuOpen = false;
      categoryMenuOpen = false;
    }
  }

  function handleLogout() {
    if (browser && authStore) {
      authStore.logout();
      profileMenuOpen = false;
      goto('/login'); // Redirect after logout
    }
  }

  function toggleSearch() {
    if (browser && searchOpen) {
      searchOpen.set(true); // Assumes searchOpen is a writable store
      closeAllMenus();
    }
  }

  function closeAllMenus() {
    profileMenuOpen = false;
    mobileMenuOpen = false;
    categoryMenuOpen = false;
    sellerActionsOpen = false;
  }

  // Handle scroll for auto-hiding header
  function handleScroll() {
    if (!browser) return;
    const currentScrollY = window.scrollY;
    scrolled = currentScrollY > 10;
    if (currentScrollY > lastScrollY + 5) {
      headerVisible = false;
    } else if (currentScrollY < lastScrollY - 5) {
      headerVisible = true;
    }
    lastScrollY = currentScrollY;
  }

  // Handle click outside
  function handleClickOutside(event) {
    if (profileMenuOpen && profileRef && !profileRef.contains(event.target)) {
      profileMenuOpen = false;
    }
    if (
      mobileMenuOpen && 
      mobileMenuRef && 
      !mobileMenuRef.contains(event.target) && 
      !event.target.closest('button[aria-controls="mobile-menu"]')
    ) {
      mobileMenuOpen = false;
    }
    if (sellerActionsOpen && sellerActionsRef && !sellerActionsRef.contains(event.target)) {
      sellerActionsOpen = false;
    }
  }

  onMount(async () => {
    if (!browser) return;

    try {
      const authModule = await import('$lib/stores/authStore');
      const uiModule = await import('$lib/stores/uiStore');

      authStore = authModule.authStore;
      isAuthenticated = authModule.isAuthenticated;
      primaryRole = authModule.primaryRole;
      searchOpen = uiModule.searchOpen;

      // Subscribe to auth store
      const unsubAuth = authStore.subscribe(value => {
        user = value.user || { first_name: 'User' };
      });

      window.addEventListener('scroll', handleScroll);
      document.addEventListener('click', handleClickOutside);

      return () => {
        window.removeEventListener('scroll', handleScroll);
        document.removeEventListener('click', handleClickOutside);
        unsubAuth();
      };
    } catch (error) {
      console.error('Failed to load stores:', error);
    }
  });

  afterUpdate(() => {
    headerVisible = true;
  });

  $: isActive = (href) => $page.url.pathname === href;
</script>

<header
  class="fixed w-full z-50 transition-all duration-300 {scrolled ? 'glass-effect shadow-md' : 'bg-transparent'} 
  {headerVisible ? 'translate-y-0' : '-translate-y-full'}"
>
  <div class="max-w-7xl mx-auto px-4">
    <div class="flex justify-between items-center h-20 relative">
      <!-- Mobile menu button - Left side -->
      <div class="md:hidden order-1 flex-1">
        <button
          type="button"
          class="flex items-center justify-center p-2 rounded-lg {scrolled ? 'text-text-dark hover:text-text-dark hover:bg-primary-blue/10' : 'text-white hover:bg-white/20'}"
          aria-expanded={mobileMenuOpen}
          on:click={toggleMobileMenu}
          aria-controls="mobile-menu"
        >
          <span class="sr-only">Open main menu</span>
          <div class="w-5 h-5 relative">
            <span 
              class="absolute h-0.5 w-5 bg-current transform transition-all duration-300"
              class:rotate-45={mobileMenuOpen}
              class:translate-y-0={mobileMenuOpen}
              class:-translate-y-1={!mobileMenuOpen}
            ></span>
            <span 
              class="absolute h-0.5 w-5 bg-current transform transition-all duration-300"
              class:opacity-0={mobileMenuOpen}
            ></span>
            <span 
              class="absolute h-0.5 w-5 bg-current transform transition-all duration-300"
              class:-rotate-45={mobileMenuOpen}
              class:translate-y-0={mobileMenuOpen}
              class:translate-y-1={!mobileMenuOpen}
            ></span>
          </div>
        </button>
      </div>

      <!-- Logo - Centered on mobile, left on desktop -->
      <div class="flex-1 md:flex-none flex justify-center md:justify-start items-center order-2 md:order-1">
        <a href="/" class="flex items-center gap-2">
          <div class="w-10 h-10 rounded-full bg-gradient-to-br from-secondary-blue to-primary-peach flex items-center justify-center shadow-md">
            <span class="text-white font-bold text-lg">G</span>
          </div>
          <span class="font-bold text-xl {scrolled ? 'text-text-dark' : 'text-white'}">GUDIC</span>
        </a>
      </div>

      <!-- Desktop Navigation - hidden on mobile -->
      <nav class="hidden md:flex items-center space-x-1 order-2">
        {#each navLinks as { href, label }}
          <a 
            {href} 
            class="relative px-3 py-2 rounded-lg text-sm font-medium transition-all
            {isActive(href) 
              ? (scrolled ? 'text-secondary-blue bg-white/80' : 'text-white bg-white/20') 
              : (scrolled ? 'text-text-dark hover:text-secondary-blue' : 'text-white/90 hover:text-white hover:bg-white/20')
            }"
            aria-current={isActive(href) ? 'page' : undefined}
          >
            {label}
          </a>
        {/each}
        
        <!-- Categories dropdown -->
        <div class="relative">
          <button 
            type="button"
            class="relative px-3 py-2 rounded-lg text-sm font-medium transition-all
            {categoryMenuOpen 
              ? (scrolled ? 'text-secondary-blue bg-white/80' : 'text-white bg-white/20') 
              : (scrolled ? 'text-text-dark hover:text-secondary-blue' : 'text-white/90 hover:text-white hover:bg-white/20')
            }"
            on:click={toggleCategoryMenu}
            aria-expanded={categoryMenuOpen}
          >
            Categories
            <span class="ml-1 inline-block transition-transform duration-200 {categoryMenuOpen ? 'rotate-180' : ''}">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 inline" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            </span>
          </button>
          
          {#if categoryMenuOpen}
            <div 
              class="absolute mt-2 w-56 rounded-lg shadow-lg glass-effect overflow-hidden z-20"
              transition:slide={{ duration: 200 }}
            >
              <div class="py-1">
                {#each categories as { slug, name, icon }}
                  <a 
                    href="/categories/{slug}" 
                    class="block px-4 py-2 text-sm text-text-dark hover:bg-primary-blue/10 transition-colors"
                    on:click={closeAllMenus}
                  >
                    <span class="flex items-center gap-3">
                      <span class="w-5 h-5 flex items-center justify-center text-secondary-blue">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                          <path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd" />
                        </svg>
                      </span>
                      {name}
                    </span>
                  </a>
                {/each}
                <a 
                  href="/categories" 
                  class="block px-4 py-2 text-sm text-secondary-blue font-medium hover:bg-primary-blue/10 transition-colors border-t border-slate-100/20 mt-1"
                  on:click={closeAllMenus}
                >
                  View All Categories
                </a>
              </div>
            </div>
          {/if}
        </div>
        
        <!-- Seller Actions Dropdown - Only visible for sellers/admins -->
        {#if isSeller}
        <div class="relative" bind:this={sellerActionsRef}>
          <button 
            type="button"
            class="relative px-3 py-2 rounded-lg text-sm font-medium transition-all
            {sellerActionsOpen 
              ? (scrolled ? 'text-secondary-blue bg-white/80' : 'text-white bg-white/20') 
              : (scrolled ? 'text-text-dark hover:text-secondary-blue' : 'text-white/90 hover:text-white hover:bg-white/20')
            }"
            on:click={toggleSellerActions}
            aria-expanded={sellerActionsOpen}
          >
            Seller Actions
            <span class="ml-1 inline-block transition-transform duration-200 {sellerActionsOpen ? 'rotate-180' : ''}">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 inline" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            </span>
          </button>
          
          {#if sellerActionsOpen}
            <div 
              class="absolute mt-2 w-56 rounded-lg shadow-lg glass-effect overflow-hidden z-20"
              transition:slide={{ duration: 200 }}
            >
              <div class="py-1">
                {#each sellerActions as { href, label }}
                  <a 
                    {href}
                    class="block px-4 py-2 text-sm text-text-dark hover:bg-primary-blue/10 transition-colors"
                    on:click={closeAllMenus}
                  >
                    <span class="flex items-center gap-3">
                      <span class="w-5 h-5 flex items-center justify-center text-secondary-blue">
                        {#if label === 'Create Auction'}
                          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" />
                          </svg>
                        {:else if label === 'My Listings'}
                          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                            <path d="M7 3a1 1 0 000 2h6a1 1 0 100-2H7zM4 7a1 1 0 011-1h10a1 1 0 110 2H5a1 1 0 01-1-1zM2 11a2 2 0 012-2h12a2 2 0 012 2v4a2 2 0 01-2 2H4a2 2 0 01-2-2v-4z" />
                          </svg>
                        {:else if label === 'Sold Auctions'}
                          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M10 2a4 4 0 00-4 4v1H5a1 1 0 00-.994.89l-1 9A1 1 0 004 18h12a1 1 0 00.994-1.11l-1-9A1 1 0 0015 7h-1V6a4 4 0 00-4-4zm2 5V6a2 2 0 10-4 0v1h4zm-6 3a1 1 0 112 0 1 1 0 01-2 0zm7-1a1 1 0 100 2 1 1 0 000-2z" clip-rule="evenodd" />
                          </svg>
                        {/if}
                      </span>
                      {label}
                    </span>
                  </a>
                {/each}
              </div>
            </div>
          {/if}
        </div>
        {/if}
        
        <!-- Search button -->
        <button 
          type="button" 
          class="relative p-2 rounded-lg text-sm font-medium transition-all
          {scrolled ? 'text-text-dark hover:text-secondary-blue' : 'text-white/90 hover:text-white hover:bg-white/20'}"
          on:click={toggleSearch}
          aria-label="Search"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" />
          </svg>
        </button>
      </nav>

      <!-- Right side - Auth actions or user profile -->
      <div class="flex items-center order-3 flex-1 justify-end">
        <!-- Mobile search button -->
        <button 
          type="button" 
          class="md:hidden relative p-2 rounded-lg text-sm font-medium transition-all
          {scrolled ? 'text-text-dark hover:text-secondary-blue' : 'text-white/90 hover:text-white hover:bg-white/20'}"
          on:click={toggleSearch}
          aria-label="Search"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" />
          </svg>
        </button>

        {#if browser && isAuthenticated !== null}
          {#if $isAuthenticated}
            <!-- User profile menu -->
            <div class="relative ml-3" bind:this={profileRef}>
              <button
                type="button"
                class="flex items-center gap-2 rounded-full focus:outline-none focus:ring-2 focus:ring-secondary-blue"
                id="user-menu-button"
                aria-expanded={profileMenuOpen}
                aria-haspopup="true"
                on:click={toggleProfileMenu}
              >
                <img
                  class="h-9 w-9 rounded-full object-cover border-2 {profileMenuOpen ? 'border-secondary-blue' : 'border-transparent'}"
                  src={user?.avatar || `https://ui-avatars.com/api/?name=${user?.first_name || ''}+${user?.last_name || ''}&background=b9dcf2&color=2a3646`}
                  alt="User profile"
                />
                <span class="hidden sm:block font-medium {scrolled ? 'text-text-dark' : 'text-white'} transition-colors">
                  {user?.first_name || 'User'}
                </span>
                <svg 
                  xmlns="http://www.w3.org/2000/svg" 
                  class="h-5 w-5 {scrolled ? 'text-text-light' : 'text-white/80'} transition-transform duration-200 {profileMenuOpen ? 'rotate-180' : ''}" 
                  viewBox="0 0 20 20" 
                  fill="currentColor"
                >
                  <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
              </button>

              {#if profileMenuOpen}
                <div
                  class="origin-top-right absolute right-0 mt-2 w-56 rounded-lg shadow-lg glass-effect divide-y divide-white/10"
                  role="menu"
                  aria-orientation="vertical"
                  aria-labelledby="user-menu-button"
                  tabindex="-1"
                  transition:slide={{ duration: 200 }}
                >
                  <div class="px-4 py-3 rounded-t-lg" style="background: linear-gradient(to right, rgba(185, 220, 242, 0.2), rgba(246, 207, 190, 0.2))">
                    <p class="text-sm font-medium text-text-dark">
                      {user?.first_name || ''} {user?.last_name || ''}
                    </p>
                    <p class="text-xs text-text-light truncate">
                      {user?.email || ''}
                    </p>
                  </div>
                  <div class="py-1">
                    <a
                      href="/dashboard"
                      class="block px-4 py-2 text-sm text-text-dark hover:bg-primary-blue/10"
                      role="menuitem"
                      on:click={closeAllMenus}
                    >
                      Dashboard
                    </a>
                    <a
                      href="/profile"
                      class="block px-4 py-2 text-sm text-text-dark hover:bg-primary-blue/10"
                      role="menuitem"
                      on:click={closeAllMenus}
                    >
                      Profile Settings
                    </a>
                  </div>
                  <div class="py-1">
                    <button
                      type="button"
                      class="block w-full text-left px-4 py-2 text-sm text-error hover:bg-error/10"
                      role="menuitem"
                      on:click={handleLogout}
                    >
                      Sign out
                    </button>
                  </div>
                </div>
              {/if}
            </div>
          {:else}
            <!-- Login/Register buttons -->
            <div class="flex items-center gap-3">
              <Button
                variant={scrolled ? 'outline' : 'glass'}
                size="sm"
                class="transition-all duration-300 hover:scale-105"
              >
                <a
                  href="/login"
                  class="btn btn-{scrolled ? 'outline' : 'glass'} px-3 py-1.5 text-sm transition-all duration-300 hover:scale-105"
                >
                  Sign in
                </a>
              </Button>
              <Button
                variant={scrolled ? 'primary' : 'white'}
                size="sm"
                class="hidden sm:inline-flex transition-all duration-300 hover:scale-105"
              >
                <a
                  href="/register"
                  class="btn btn-{scrolled ? 'primary' : 'white'} px-3 py-1.5 text-sm transition-all duration-300 hover:scale-105"
                >
                  Register
                </a>
              </Button>
            </div>
          {/if}
        {/if}
      </div>
    </div>
  </div>

  <!-- Mobile menu -->
  {#if mobileMenuOpen}
    <div class="md:hidden glass-effect overflow-hidden" bind:this={mobileMenuRef} transition:slide={{ duration: 250 }}>
      <div class="pt-2 pb-4 space-y-1 px-4">
        <!-- Search input for mobile -->
        <div class="py-3">
          <button 
            type="button"
            class="w-full flex items-center px-4 py-2.5 rounded-lg border border-white/30 shadow-sm text-left text-text-dark"
            on:click={toggleSearch}
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 text-text-light" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" />
            </svg>
            Search for auctions, categories, etc.
          </button>
        </div>
        
        {#each navLinks as { href, label }}
          <a 
            {href} 
            class="block px-4 py-2.5 rounded-lg text-base font-medium {isActive(href) ? 'bg-primary-blue/20 text-secondary-blue' : 'text-text-dark hover:bg-primary-blue/10'}"
            aria-current={isActive(href) ? 'page' : undefined}
            on:click={closeAllMenus}
          >
            {label}
          </a>
        {/each}
        
        <!-- Seller Actions Section (Mobile) - Only visible for sellers/admins -->
        {#if isSeller}
          <div class="py-2 border-t border-white/10">
            <h3 class="text-xs font-semibold text-text-light uppercase tracking-wider px-4 py-2">
              Seller Actions
            </h3>
            <div class="space-y-1">
              {#each sellerActions as { href, label }}
                <a 
                  {href} 
                  class="block px-4 py-2.5 rounded-lg text-base font-medium text-secondary-blue hover:bg-primary-blue/10"
                  on:click={closeAllMenus}
                >
                  {label}
                </a>
              {/each}
            </div>
          </div>
        {/if}
        
        <!-- Categories section -->
        <div class="py-2 border-t border-white/10">
          <h3 class="text-xs font-semibold text-text-light uppercase tracking-wider px-4 py-2">
            Browse Categories
          </h3>
          <div class="grid grid-cols-2 gap-2 pt-2">
            {#each categories as { slug, name }}
              <a 
                href="/categories/{slug}" 
                class="px-4 py-2 text-sm text-text-dark hover:bg-primary-blue/10 rounded-lg"
                on:click={closeAllMenus}
              >
                {name}
              </a>
            {/each}
            <a 
              href="/categories" 
              class="col-span-2 px-4 py-2 text-sm text-secondary-blue font-medium hover:bg-primary-blue/10 rounded-lg mt-2"
              on:click={closeAllMenus}
            >
              View All Categories →
            </a>
          </div>
        </div>
        
        {#if browser && isAuthenticated !== null && !$isAuthenticated}
          <div class="pt-4 border-t border-white/10 flex flex-col gap-2">
            <Button
              variant="primary"
              size="lg"
              class="w-full"
            >
              <a href="/login">
                Sign in
              </a>
            </Button>
            <Button
              variant="outline"
              size="lg"
              class="w-full"
            >
              <a href="/register">
                Register
              </a>
            </Button>
          </div>
        {/if}
      </div>
    </div>
  {/if}
</header>

<style>
  header {
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
  }

  .glass-effect {
    background-color: rgba(255, 255, 255, 0.7);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  }

  @media (max-width: 768px) {
    .glass-effect {
      background-color: rgba(255, 255, 255, 0.85);
    }
  }
</style>