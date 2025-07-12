<!-- src/routes/core/+layout.svelte -->
<script>
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { fade, slide } from 'svelte/transition';
  import { t, locale } from '$lib/i18n';
  import { user } from '$lib/stores/user';

  // State
  let showMobileNav = false;
  let showDesktopSidebar = true;
  let isRTL = $derived($locale === 'ar');

  // Navigation items with role-based visibility - make reactive
  let navItems = $derived([
    {
      href: '/core',
      icon: 'chart-bar',
      label: $t('core.nav.dashboard'),
      description: $t('core.nav.dashboardDesc'),
      roles: ['landlord', 'property_manager', 'appraiser', 'data_entry', 'tenant']
    },
    {
      href: '/core/financial',
      icon: 'currency-dollar',
      label: $t('core.nav.financial'),
      description: $t('core.nav.financialDesc'),
      roles: ['landlord', 'property_manager', 'tenant', 'appraiser']
    },
    {
      href: '/core/rentals',
      icon: 'home',
      label: $t('core.nav.rentals'),
      description: $t('core.nav.rentalsDesc'),
      roles: ['landlord', 'property_manager', 'tenant']
    },
    {
      href: '/core/maintenance',
      icon: 'wrench-screwdriver',
      label: $t('core.nav.maintenance'),
      description: $t('core.nav.maintenanceDesc'),
      roles: ['landlord', 'property_manager', 'tenant', 'maintenance_staff', 'vendor']
    },
    {
      href: '/core/contracts',
      icon: 'document-text',
      label: $t('core.nav.contracts'),
      description: $t('core.nav.contractsDesc'),
      roles: ['landlord', 'property_manager', 'tenant']
    },
    {
      href: '/core/analytics',
      icon: 'chart-pie',
      label: $t('core.nav.analytics'),
      description: $t('core.nav.analyticsDesc'),
      roles: ['landlord', 'property_manager', 'appraiser']
    }
  ]);

  // Check permissions
  onMount(() => {
    if (!$user) {
      goto('/login');
      return;
    }

    // Check if user has access to any core features
    // Backend allows tenants to access certain features (maintenance requests, leases, etc.)
    const allowedRoles = ['landlord', 'property_manager', 'appraiser', 'data_entry', 'tenant', 'maintenance_staff', 'vendor'];
    if (!$user.is_superuser && !allowedRoles.includes($user.role)) {
      goto('/dashboard');
    }
  });

  // Check if user can access a specific nav item
  function canAccessNavItem(navItem) {
    if (!$user) return false;
    if ($user.is_superuser) return true;
    return navItem.roles.includes($user.role);
  }

  // Get visible nav items for current user
  let visibleNavItems = $derived(navItems.filter(item => canAccessNavItem(item)));

  function isActive(href) {
    if (href === '/core') {
      return $page.url.pathname === '/core';
    }
    return $page.url.pathname.startsWith(href);
  }

  function getIcon(iconName) {
    const icons = {
      'chart-bar': `<path stroke-linecap="round" stroke-linejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 0 1 3 19.875v-6.75ZM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V8.625ZM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V4.125Z" />`,
      'currency-dollar': `<path stroke-linecap="round" stroke-linejoin="round" d="M12 6v12m-3-2.818.879.659c1.171.879 3.07.879 4.242 0 1.172-.879 1.172-2.303 0-3.182C13.536 12.219 12.768 12 12 12c-.725 0-1.467-.22-2.121-.659-1.172-.879-1.172-2.303 0-3.182s3.07-.879 4.242 0L15 9m-3 0V6m0 12v-3" />`,
      'home': `<path stroke-linecap="round" stroke-linejoin="round" d="m2.25 12 8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25" />`,
      'wrench-screwdriver': `<path stroke-linecap="round" stroke-linejoin="round" d="M11.42 15.17 17.25 21A2.652 2.652 0 0 0 21 17.25l-5.877-5.877M11.42 15.17l2.496-3.03c.317-.384.74-.626 1.208-.766M11.42 15.17l-4.655 5.653a2.548 2.548 0 1 1-3.586-3.586l6.837-5.63m5.108-.233c.55-.164 1.163-.188 1.743-.14a4.5 4.5 0 0 0 4.486-6.336l-3.276 3.277a3.004 3.004 0 0 1-2.25-2.25l3.276-3.276a4.5 4.5 0 0 0-6.336 4.486c.091 1.076-.071 2.264-.904 2.95l-.102.085m-1.745 1.437L5.909 7.5H4.5L2.25 3.75l1.5-1.5L7.5 4.5v1.409l4.26 4.26m-1.745 1.437 1.745-1.437m6.615 8.206L15.75 15.75M4.867 19.125h.008v.008h-.008v-.008Z" />`,
      'document-text': `<path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />`,
      'chart-pie': `<path stroke-linecap="round" stroke-linejoin="round" d="M10.5 6a7.5 7.5 0 1 0 7.5 7.5h-7.5V6Z M13.5 10.5H21A7.5 7.5 0 0 0 13.5 3v7.5Z" />`
    };
    return icons[iconName] || '';
  }

  function closeSidebar() {
    showDesktopSidebar = false;
  }

  function openSidebar() {
    showDesktopSidebar = true;
  }
</script>

<svelte:head>
  <title>{$t('core.layout.title')} | {$t('app.name')}</title>
</svelte:head>

<div class="min-h-screen bg-gray-50 dark:bg-gray-900">
  <!-- Mobile navigation toggle - Fixed to be truly mobile-only -->
  <div class="lg:hidden fixed top-0 left-0 right-0 z-30">
    <div class="flex items-center justify-between bg-white dark:bg-gray-800 px-4 py-3 border-b border-gray-200 dark:border-gray-700">
      <h1 class="text-lg font-semibold text-gray-900 dark:text-white">
        {$t('core.layout.title')}
      </h1>
      <button
        type="button"
        class="inline-flex items-center justify-center p-2 rounded-md text-gray-500 hover:text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-gray-300 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-primary-500"
        onclick={() => showMobileNav = !showMobileNav}
      >
        <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
        </svg>
      </button>
    </div>
  </div>

  <div class="flex">
    <!-- Desktop Sidebar -->
    {#if showDesktopSidebar}
      <div class="hidden lg:flex lg:w-64 lg:flex-col lg:fixed lg:inset-y-0 z-20">
        <div class="flex flex-col flex-grow pt-5 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 overflow-y-auto">
          <div class="flex items-center justify-between flex-shrink-0 px-4">
            <h1 class="text-xl font-semibold text-gray-900 dark:text-white">
              {$t('core.layout.title')}
            </h1>
            <button
              type="button"
              class="p-1.5 rounded-md text-gray-500 hover:text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-gray-300 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-primary-500"
              onclick={closeSidebar}
              title="Hide sidebar"
            >
              <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <div class="mt-5 flex-1 flex flex-col">
            <nav class="flex-1 px-2 pb-4 space-y-1">
              {#each visibleNavItems as item}
                <a
                  href={item.href}
                  class={`${
                    isActive(item.href)
                      ? 'bg-primary-50 dark:bg-primary-900/20 border-primary-500 text-primary-700 dark:text-primary-300'
                      : 'border-transparent text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white hover:bg-gray-50 dark:hover:bg-gray-700'
                  } group flex items-center px-3 py-2 text-sm font-medium border-l-4 transition-colors duration-200`}
                >
                  <svg class="mr-3 flex-shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                    {@html getIcon(item.icon)}
                  </svg>
                  <div>
                    <div class="font-medium">{item.label}</div>
                    <div class="text-xs text-gray-500 dark:text-gray-400">{item.description}</div>
                  </div>
                </a>
              {/each}
            </nav>
          </div>
        </div>
      </div>
    {/if}

    <!-- Mobile Sidebar -->
    {#if showMobileNav}
      <div class="lg:hidden fixed inset-0 z-40" transition:fade={{ duration: 200 }}>
        <div class="fixed inset-0 bg-gray-600 bg-opacity-75" onclick={() => showMobileNav = false}></div>
        <div class="relative flex-1 flex flex-col max-w-xs w-full bg-white dark:bg-gray-800" transition:slide={{ duration: 300 }}>
          <div class="absolute top-0 right-0 -mr-12 pt-2">
            <button
              type="button"
              class="ml-1 flex items-center justify-center h-10 w-10 rounded-full focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white"
              onclick={() => showMobileNav = false}
            >
              <svg class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <div class="flex-1 h-0 pt-5 pb-4 overflow-y-auto">
            <div class="flex-shrink-0 flex items-center px-4">
              <h1 class="text-xl font-semibold text-gray-900 dark:text-white">
                {$t('core.layout.title')}
              </h1>
            </div>
            <nav class="mt-5 px-2 space-y-1">
              {#each visibleNavItems as item}
                <a
                  href={item.href}
                  onclick={() => showMobileNav = false}
                  class={`${
                    isActive(item.href)
                      ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300'
                      : 'text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white hover:bg-gray-50 dark:hover:bg-gray-700'
                  } group flex items-center px-2 py-2 text-base font-medium rounded-md transition-colors duration-200`}
                >
                  <svg class="mr-4 flex-shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                    {@html getIcon(item.icon)}
                  </svg>
                  <div>
                    <div class="font-medium">{item.label}</div>
                    <div class="text-xs text-gray-500 dark:text-gray-400">{item.description}</div>
                  </div>
                </a>
              {/each}
            </nav>
          </div>
        </div>
      </div>
    {/if}

    <!-- Main Content -->
    <div class={`${showDesktopSidebar ? 'lg:pl-64' : 'lg:pl-0'} flex flex-col flex-1 transition-all duration-300`}>
      <main class="flex-1">
        <!-- Desktop sidebar toggle when collapsed -->
        {#if !showDesktopSidebar}
          <div class="hidden lg:block fixed top-4 left-4 z-30">
            <button
              type="button"
              class="p-2 rounded-md bg-white dark:bg-gray-800 shadow-lg text-gray-500 hover:text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-gray-300 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-primary-500 border border-gray-200 dark:border-gray-700"
              onclick={openSidebar}
              title="Show sidebar"
            >
              <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
              </svg>
            </button>
          </div>
        {/if}
        
        <!-- Add top padding on mobile to account for fixed header -->
        <div class="py-6 px-4 sm:px-6 lg:px-8 pt-20 lg:pt-6">
          <slot />
        </div>
      </main>
    </div>
  </div>
</div>