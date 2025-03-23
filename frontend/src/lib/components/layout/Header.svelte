<!-- src/lib/components/layout/Header.svelte -->
<script>
	import { createEventDispatcher } from 'svelte';
	import { t, language, changeLanguage, languageNames } from '$lib/i18n';
	import { page } from '$app/stores';
	import { fly, slide, fade } from 'svelte/transition';
	import { browser } from '$app/environment';
	import { quintOut } from 'svelte/easing';
  
	// Auth store and notification system
	import { isAuthenticated, currentUser, authStore } from '$lib/stores/auth';
	import { unreadCount } from '$lib/stores/notification';
  
	// Event dispatcher to communicate with parent components
	const dispatch = createEventDispatcher();
  
	// Props
	export let menuOpen = false;
  
	// Local state
	let scrollY = 0;
	let headerTransparent = true;
	let userMenuOpen = false;
	let previousScrollY = 0;
	let scrollingDown = false;
	let headerHidden = false;
  
	// Update header transparency and visibility on scroll
	function handleScroll() {
	  scrollingDown = scrollY > previousScrollY;
	  previousScrollY = scrollY;
	  
	  if (scrollY > 20) {
		headerTransparent = false;
		
		// Hide header on scroll down (only on mobile)
		if (scrollingDown && scrollY > 150 && window.innerWidth < 768) {
		  headerHidden = true;
		} else {
		  headerHidden = false;
		}
	  } else {
		headerTransparent = true;
		headerHidden = false;
	  }
	}
  
	// Toggle mobile menu
	function toggleMenu() {
	  menuOpen = !menuOpen;
	  
	  if (menuOpen) {
		// Close user menu if open
		userMenuOpen = false;
		
		// Prevent body scroll when menu is open
		if (browser) {
		  document.body.style.overflow = 'hidden';
		}
	  } else {
		// Re-enable body scroll when menu is closed
		if (browser) {
		  document.body.style.overflow = '';
		}
	  }
	  
	  dispatch('toggleMenu', { menuOpen });
	}
  
	// Toggle user menu
	function toggleUserMenu() {
	  userMenuOpen = !userMenuOpen;
	}
  
	// Handle logout
	function handleLogout() {
	  userMenuOpen = false;
	  menuOpen = false;
	  
	  if (browser) {
		document.body.style.overflow = '';
	  }
	  
	  authStore.logout();
	}
  
	// Toggle language
	function toggleLanguage() {
	  changeLanguage($language === 'ar' ? 'en' : 'ar');
	}
  
	// Check if a nav link is active (current page)
	function isActive(path) {
	  if (!browser || !$page || !$page.url) return false;
	  return $page.url.pathname.startsWith(path);
	}
  
	// Close user menu when clicking outside
	function handleClickOutside(event) {
	  if (
		userMenuOpen &&
		!event.target.closest('#user-menu-button') &&
		!event.target.closest('#user-menu')
	  ) {
		userMenuOpen = false;
	  }
	}
	
	// Close mobile menu on route change
	$: if (browser && $page && menuOpen) {
	  menuOpen = false;
	  document.body.style.overflow = '';
	}
	
	// Clean up on component unmount
	function cleanup() {
	  if (browser) {
		document.body.style.overflow = '';
	  }
	}
  </script>
  
  <svelte:window bind:scrollY on:scroll={handleScroll} on:click={handleClickOutside} on:beforeunload={cleanup} />
  
  <header
	class="fixed top-0 right-0 left-0 transition-all duration-300 z-50
	  {headerTransparent ? 'bg-transparent' : 'bg-surface-light dark:bg-surface-dark shadow-glass'}
	  {headerHidden ? '-translate-y-full' : 'translate-y-0'}"
  >
	<div class="container mx-auto px-4 sm:px-6">
	  <div class="flex h-16 md:h-20 items-center justify-between">
		<!-- Logo -->
		<div class="flex-shrink-0">
		  <a href="/" class="flex items-center">
			<div class="flex items-center space-x-2">
			  <div class="h-8 w-8 rounded-lg bg-primary/10 flex items-center justify-center text-primary">
				<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-5 h-5">
				  <path d="M11.47 3.84a.75.75 0 011.06 0l8.69 8.69a.75.75 0 101.06-1.06l-8.689-8.69a2.25 2.25 0 00-3.182 0l-8.69 8.69a.75.75 0 001.061 1.06l8.69-8.69z" />
				  <path d="M12 5.432l8.159 8.159c.03.03.06.058.091.086v6.198c0 1.035-.84 1.875-1.875 1.875H15a.75.75 0 01-.75-.75v-4.5a.75.75 0 00-.75-.75h-3a.75.75 0 00-.75.75V21a.75.75 0 01-.75.75H5.625a1.875 1.875 0 01-1.875-1.875v-6.198a2.29 2.29 0 00.091-.086L12 5.43z" />
				</svg>
			  </div>
			  <span class="text-neutral-800 dark:text-white font-medium text-lg hidden xs:block">
				{$t('general.app_name')}
			  </span>
			</div>
		  </a>
		</div>
  
		<!-- Desktop navigation -->
		<nav
		  class="hidden md:flex md:items-center space-x-2 md:space-x-3 lg:space-x-5 {$language === 'ar' ? 'space-x-reverse' : ''}"
		>
		  <a
			href="/"
			class="px-3 py-2.5 rounded-xl text-sm font-medium transition-all
			  {isActive('/') && !isActive('/dashboard')
				? 'text-primary bg-primary-50 dark:bg-primary-900/30 dark:text-primary-300'
				: 'text-neutral-700 hover:text-primary dark:text-neutral-300 dark:hover:text-primary-300 hover:bg-neutral-100/80 dark:hover:bg-neutral-800/50'}"
		  >
			{$t('navigation.home')}
		  </a>
		  
		  <a
			href="/auctions"
			class="px-3 py-2.5 rounded-xl text-sm font-medium transition-all
			  {isActive('/auctions')
				? 'text-primary bg-primary-50 dark:bg-primary-900/30 dark:text-primary-300'
				: 'text-neutral-700 hover:text-primary dark:text-neutral-300 dark:hover:text-primary-300 hover:bg-neutral-100/80 dark:hover:bg-neutral-800/50'}"
		  >
			{$t('navigation.auctions')}
		  </a>
		  
		  <a
			href="/properties"
			class="px-3 py-2.5 rounded-xl text-sm font-medium transition-all
			  {isActive('/properties')
				? 'text-primary bg-primary-50 dark:bg-primary-900/30 dark:text-primary-300'
				: 'text-neutral-700 hover:text-primary dark:text-neutral-300 dark:hover:text-primary-300 hover:bg-neutral-100/80 dark:hover:bg-neutral-800/50'}"
		  >
			{$t('navigation.properties')}
		  </a>
  
		  <!-- Language toggle button with two-letter code -->
		  <button
			class="px-3 py-2 rounded-xl text-sm font-medium transition-all flex items-center text-neutral-700 hover:text-primary dark:text-neutral-300 dark:hover:text-primary-300 hover:bg-neutral-100/80 dark:hover:bg-neutral-800/50"
			on:click={toggleLanguage}
		  >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10"/>
              <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
              <path d="M2 12h20"/>
            </svg>
			{$language === 'ar' ? 'EN' : 'AR'}
		  </button>
  
		  <!-- Authenticated menu items -->
		  {#if $isAuthenticated}
			<a
			  href="/dashboard"
			  class="px-3 py-2.5 rounded-xl text-sm font-medium transition-all
				{isActive('/dashboard')
				  ? 'text-primary bg-primary-50 dark:bg-primary-900/30 dark:text-primary-300'
				  : 'text-neutral-700 hover:text-primary dark:text-neutral-300 dark:hover:text-primary-300 hover:bg-neutral-100/80 dark:hover:bg-neutral-800/50'}"
			>
			  {$t('navigation.dashboard')}
			</a>

            <!-- Profile link -->
            <a
              href="/dashboard/profile"
              class="px-3 py-2.5 rounded-xl text-sm font-medium transition-all flex items-center
                {isActive('/dashboard/profile')
                  ? 'text-primary bg-primary-50 dark:bg-primary-900/30 dark:text-primary-300'
                  : 'text-neutral-700 hover:text-primary dark:text-neutral-300 dark:hover:text-primary-300 hover:bg-neutral-100/80 dark:hover:bg-neutral-800/50'}"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/>
                <circle cx="12" cy="7" r="4"/>
              </svg>
              {$t('navigation.profile')}
            </a>
  
			<!-- Notification indicator -->
			<a
			  href="/dashboard/notifications"
			  class="relative p-2 rounded-full text-neutral-700 hover:text-primary dark:text-neutral-300 dark:hover:text-primary-300 hover:bg-neutral-100/80 dark:hover:bg-neutral-800/50 transition-all"
			  aria-label={$t('navigation.notifications')}
			>
			  <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
				<path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9" />
				<path d="M10.3 21a1.94 1.94 0 0 0 3.4 0" />
			  </svg>
  
			  {#if $unreadCount > 0}
				<span
				  class="absolute top-0 right-0 flex h-5 w-5 items-center justify-center rounded-full bg-error text-xs text-white font-medium"
				  transition:scale={{duration: 300, start: 0.5}}
				>
				  {$unreadCount > 9 ? '9+' : $unreadCount}
				</span>
			  {/if}
			</a>

            <!-- Logout button -->
            <button
              on:click={handleLogout}
              class="px-3 py-2.5 rounded-xl text-sm font-medium transition-all flex items-center text-error hover:text-error/80 dark:text-error-300"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
                <polyline points="16 17 21 12 16 7" />
                <line x1="21" y1="12" x2="9" y2="12" />
              </svg>
              {$t('navigation.logout')}
            </button>
  
			<!-- User menu -->
			<div class="relative {$language === 'ar' ? 'mr-1' : 'ml-1'}">
			  <button
				type="button"
				id="user-menu-button"
				class="flex items-center rounded-full focus:outline-none"
				aria-expanded={userMenuOpen}
				aria-haspopup="true"
				on:click={toggleUserMenu}
			  >
				<span class="sr-only">{$t('navigation.profile')}</span>
				<div class="h-9 w-9 overflow-hidden rounded-full ring-2 ring-white dark:ring-neutral-800 transition-all hover:ring-primary/20 dark:hover:ring-primary/30">
				  {#if $currentUser && $currentUser.avatar}
					<img
					  class="h-full w-full object-cover"
					  src={$currentUser.avatar}
					  alt={$currentUser.firstName}
					/>
				  {:else}
					<div
					  class="bg-primary text-white flex h-full w-full items-center justify-center text-base font-semibold"
					>
					  {#if $currentUser && $currentUser.firstName}
						{$currentUser.firstName[0].toUpperCase()}
					  {:else}
						U
					  {/if}
					</div>
				  {/if}
				</div>
			  </button>
  
			  <!-- Dropdown menu - User options -->
			  {#if userMenuOpen}
				<div
				  id="user-menu"
				  in:fly={{ y: 10, duration: 200, easing: quintOut }}
				  out:fade={{ duration: 100 }}
				  class="absolute {$language === 'ar' ? 'left-0' : 'right-0'} mt-2 w-52 origin-top-right rounded-xl bg-white dark:bg-neutral-800 shadow-lg ring-1 ring-black/5 dark:ring-white/10 focus:outline-none overflow-hidden z-50"
				  role="menu"
				  aria-orientation="vertical"
				  aria-labelledby="user-menu-button"
				  tabindex="-1"
				>
				  <!-- User info section -->
				  <div class="px-4 py-3 border-b border-neutral-100 dark:border-neutral-700">
					<p class="text-sm font-medium text-neutral-800 dark:text-white truncate">
					  {#if $currentUser && $currentUser.firstName}
						{$currentUser.firstName} {$currentUser.lastName || ''}
					  {:else}
						{$t('auth.profile')}
					  {/if}
					</p>
					<p class="text-xs text-neutral-500 dark:text-neutral-400 truncate mt-0.5">
					  {#if $currentUser && $currentUser.email}
						{$currentUser.email}
					  {/if}
					</p>
				  </div>
				  
				  <div class="py-1" role="none">
					<a
					  href="/dashboard/profile"
					  class="flex items-center px-4 py-2.5 text-sm text-neutral-700 dark:text-neutral-200 hover:bg-neutral-50 dark:hover:bg-neutral-700/50"
					  role="menuitem"
					>
					  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2 text-neutral-500 dark:text-neutral-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2" />
						<circle cx="12" cy="7" r="4" />
					  </svg>
					  {$t('navigation.profile')}
					</a>
					
					<a
					  href="/dashboard/settings"
					  class="flex items-center px-4 py-2.5 text-sm text-neutral-700 dark:text-neutral-200 hover:bg-neutral-50 dark:hover:bg-neutral-700/50"
					  role="menuitem"
					>
					  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2 text-neutral-500 dark:text-neutral-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z" />
						<circle cx="12" cy="12" r="3" />
					  </svg>
					  {$t('navigation.settings')}
					</a>
					
					<button
					  on:click={handleLogout}
					  class="flex items-center w-full px-4 py-2.5 text-sm text-error hover:bg-neutral-50 dark:hover:bg-neutral-700/50"
					  role="menuitem"
					>
					  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
						<polyline points="16 17 21 12 16 7" />
						<line x1="21" y1="12" x2="9" y2="12" />
					  </svg>
					  {$t('navigation.logout')}
					</button>
				  </div>
				</div>
			  {/if}
			</div>
		  {:else}
			<!-- Unauthenticated actions - White bg with black text -->
			<a
			  href="/auth/login"
			  class="inline-flex items-center px-4 py-2 text-sm font-medium text-neutral-800 bg-white hover:bg-neutral-100 transition-colors duration-200 rounded-xl border border-neutral-200"
			>
			  {$t('navigation.login')}
			</a>
  
			<a
			  href="/auth/register"
			  class="inline-flex items-center px-4 py-2 text-sm font-medium text-neutral-800 bg-white hover:bg-neutral-100 transition-colors duration-200 rounded-xl border border-neutral-200 ml-2"
			>
			  {$t('navigation.register')}
			</a>
		  {/if}
		</nav>
  
		<!-- Mobile Actions -->
		<div class="flex items-center md:hidden space-x-3">
		  {#if $isAuthenticated}
			<!-- Notification indicator (mobile) -->
			<a
			  href="/dashboard/notifications"
			  class="relative p-2 rounded-full text-neutral-700 hover:text-primary dark:text-neutral-300 dark:hover:text-primary-300"
			  aria-label={$t('navigation.notifications')}
			>
			  <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
				<path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9" />
				<path d="M10.3 21a1.94 1.94 0 0 0 3.4 0" />
			  </svg>
  
			  {#if $unreadCount > 0}
				<span
				  class="absolute top-0 right-0 flex h-5 w-5 items-center justify-center rounded-full bg-error text-xs text-white font-medium"
				>
				  {$unreadCount > 9 ? '9+' : $unreadCount}
				</span>
			  {/if}
			</a>
			
			<!-- User avatar (mobile) -->
			<a 
			  href="/dashboard/profile"
			  class="relative flex"
			>
			  <div class="h-9 w-9 overflow-hidden rounded-full ring-2 ring-white dark:ring-neutral-800">
				{#if $currentUser && $currentUser.avatar}
				  <img
					class="h-full w-full object-cover"
					src={$currentUser.avatar}
					alt={$currentUser.firstName}
				  />
				{:else}
				  <div
					class="bg-primary text-white flex h-full w-full items-center justify-center text-base font-semibold"
				  >
					{#if $currentUser && $currentUser.firstName}
					  {$currentUser.firstName[0].toUpperCase()}
					{:else}
					  U
					{/if}
				  </div>
				{/if}
			  </div>
			</a>
		  {/if}
		  
          <!-- Language toggle for mobile -->
          <button
            on:click={toggleLanguage}
            class="p-2 rounded-lg text-neutral-700 hover:text-primary dark:text-neutral-300 dark:hover:text-primary-300 flex items-center justify-center"
            aria-label="Toggle language"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10"/>
              <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
              <path d="M2 12h20"/>
            </svg>
          </button>
          
		  <!-- Mobile menu button -->
		  <button
			type="button"
			aria-controls="mobile-menu"
			aria-expanded={menuOpen}
			on:click={toggleMenu}
			class="inline-flex items-center justify-center p-2 rounded-lg text-neutral-700 hover:text-primary dark:text-neutral-300 dark:hover:text-primary-300 hover:bg-neutral-100 dark:hover:bg-neutral-800 transition-colors"
            aria-label="Toggle mobile navigation"
		  >
			<span class="sr-only">{menuOpen ? 'Close menu' : 'Open menu'}</span>
			<div class="relative w-6 h-6">
			  <span class="absolute block h-0.5 w-6 bg-current transform transition duration-300 ease-in-out rounded-full
				{menuOpen ? 'rotate-45 top-3' : 'top-2'}"></span>
			  <span class="absolute block h-0.5 w-6 bg-current transform transition duration-300 ease-in-out rounded-full
				{menuOpen ? 'opacity-0' : 'opacity-100'} top-3"></span>
			  <span class="absolute block h-0.5 w-6 bg-current transform transition duration-300 ease-in-out rounded-full
				{menuOpen ? '-rotate-45 top-3' : 'top-4'}"></span>
			</div>
		  </button>
		</div>
	  </div>
	</div>
  </header>
  
  <!-- Mobile menu overlay -->
  {#if menuOpen}
	<div 
	  class="fixed inset-0 bg-black/30 backdrop-blur-sm z-40 md:hidden"
	  transition:fade={{ duration: 200 }}
	  on:click={toggleMenu}
	></div>
	
	<!-- Mobile menu panel -->
	<div 
	  id="mobile-menu" 
	  class="fixed top-16 bottom-0 right-0 w-full max-w-sm bg-white dark:bg-neutral-900 z-40 md:hidden overflow-y-auto"
	  class:left-0={$language === 'ar'}
	  class:right-0={$language !== 'ar'}
	  transition:fly={{ x: $language === 'ar' ? -300 : 300, duration: 300, easing: quintOut }}
	>
	  <div class="flex flex-col h-full">
		<div class="flex-1 px-4 py-6 space-y-3">
		  <a
			href="/"
			class="flex items-center px-4 py-3 rounded-xl {isActive('/') && !isActive('/dashboard')
			  ? 'bg-primary-50 dark:bg-primary-900/30 text-primary dark:text-primary-300'
			  : 'text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-800/70'}"
			on:click={toggleMenu}
		  >
			<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
			  <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
			  <polyline points="9 22 9 12 15 12 15 22"/>
			</svg>
			<span class="font-medium">{$t('navigation.home')}</span>
		  </a>
		  
		  <a
			href="/auctions"
			class="flex items-center px-4 py-3 rounded-xl {isActive('/auctions')
			  ? 'bg-primary-50 dark:bg-primary-900/30 text-primary dark:text-primary-300'
			  : 'text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-800/70'}"
			on:click={toggleMenu}
		  >
			<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
			  <path d="m9 9 6 6"/>
			  <path d="m9 15 6-6"/>
			  <circle cx="12" cy="12" r="10"/>
			</svg>
			<span class="font-medium">{$t('navigation.auctions')}</span>
		  </a>
		  
		  <a
			href="/properties"
			class="flex items-center px-4 py-3 rounded-xl {isActive('/properties')
			  ? 'bg-primary-50 dark:bg-primary-900/30 text-primary dark:text-primary-300'
			  : 'text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-800/70'}"
			on:click={toggleMenu}
		  >
			<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
			  <path d="M3 9a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V9z"/>
			  <path d="M3 9v2m18-2v2"/>
			  <path d="M9 16h6"/>
			  <path d="M17 3v4"/>
			  <path d="M7 3v4"/>
			</svg>
			<span class="font-medium">{$t('navigation.properties')}</span>
		  </a>
		  
		  {#if $isAuthenticated}
			<a
			  href="/dashboard"
			  class="flex items-center px-4 py-3 rounded-xl {isActive('/dashboard')
				? 'bg-primary-50 dark:bg-primary-900/30 text-primary dark:text-primary-300'
				: 'text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-800/70'}"
			  on:click={toggleMenu}
			>
			  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
				<rect width="7" height="9" x="3" y="3" rx="1"/>
				<rect width="7" height="5" x="14" y="3" rx="1"/>
				<rect width="7" height="9" x="14" y="12" rx="1"/>
				<rect width="7" height="5" x="3" y="16" rx="1"/>
			  </svg>
			  <span class="font-medium">{$t('navigation.dashboard')}</span>
			</a>
			
			<a
			  href="/dashboard/profile"
			  class="flex items-center px-4 py-3 rounded-xl {isActive('/dashboard/profile')
				? 'bg-primary-50 dark:bg-primary-900/30 text-primary dark:text-primary-300'
				: 'text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-800/70'}"
			  on:click={toggleMenu}
			>
			  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
				<path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/>
				<circle cx="12" cy="7" r="4"/>
			  </svg>
			  <span class="font-medium">{$t('navigation.profile')}</span>
			</a>
			
			<a
			  href="/dashboard/notifications"
			  class="flex items-center justify-between px-4 py-3 rounded-xl {isActive('/dashboard/notifications')
				? 'bg-primary-50 dark:bg-primary-900/30 text-primary dark:text-primary-300'
				: 'text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-800/70'}"
			  on:click={toggleMenu}
			>
			  <div class="flex items-center">
				<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
				  <path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/>
				  <path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/>
				</svg>
				<span class="font-medium">{$t('navigation.notifications')}</span>
			  </div>
			  {#if $unreadCount > 0}
				<span class="flex h-5 w-5 items-center justify-center rounded-full bg-error text-xs text-white font-medium">
				  {$unreadCount > 9 ? '9+' : $unreadCount}
				</span>
			  {/if}
			</a>
		  {/if}
		  
		  <!-- Language switcher mobile - changed to two-letter code -->
		  <button
			on:click={() => { toggleLanguage(); toggleMenu(); }}
			class="flex items-center w-full px-4 py-3 rounded-xl text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-800/70"
		  >
			<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
			  <circle cx="12" cy="12" r="10"/>
              <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
              <path d="M2 12h20"/>
			</svg>
			<span class="font-medium">
			  {$language === 'ar' ? 'EN' : 'AR'}
			</span>
		  </button>
		</div>
		
		<!-- Bottom auth actions -->
		<div class="p-4 border-t border-neutral-200 dark:border-neutral-800">
		  {#if $isAuthenticated}
			<button
			  on:click={handleLogout}
			  class="flex items-center justify-center w-full px-4 py-3 text-white font-medium rounded-xl bg-error hover:bg-error/90 transition-colors"
			>
			  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
				<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
				<polyline points="16 17 21 12 16 7"/>
				<line x1="21" y1="12" x2="9" y2="12"/>
			  </svg>
			  {$t('navigation.logout')}
			</button>
		  {:else}
			<div class="flex flex-col space-y-3">
			  <a
				href="/auth/login"
				class="flex items-center justify-center w-full px-4 py-3 text-neutral-800 font-medium rounded-xl bg-white hover:bg-neutral-100 transition-colors border border-neutral-200"
				on:click={toggleMenu}
			  >
				{$t('navigation.login')}
			  </a>
			  
			  <a
				href="/auth/register"
				class="flex items-center justify-center w-full px-4 py-3 text-neutral-800 font-medium rounded-xl bg-white hover:bg-neutral-100 transition-colors border border-neutral-200"
				on:click={toggleMenu}
			  >
				{$t('navigation.register')}
			  </a>
			</div>
		  {/if}
		</div>
	  </div>
	</div>
  {/if}