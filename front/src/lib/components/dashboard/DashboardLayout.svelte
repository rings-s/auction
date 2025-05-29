<!-- src/lib/components/dashboard/DashboardLayout.svelte -->
<script>
    import { page } from '$app/stores';
    import { t } from '$lib/i18n';
    import { user } from '$lib/stores/user';
    import { canAccessSystemDashboard, userPriority } from '$lib/stores/dashboard';
    import Button from '$lib/components/ui/Button.svelte';
    
    // Navigation items based on user permissions
    $: navigationItems = [
      {
        name: $t('dashboard.overview'),
        href: '/dashboard',
        current: $page.url.pathname === '/dashboard'
      },
      {
        name: $t('dashboard.properties'),
        href: '/dashboard/properties', 
        current: $page.url.pathname.startsWith('/dashboard/properties')
      },
      {
        name: $t('dashboard.auctions'),
        href: '/dashboard/auctions',
        current: $page.url.pathname.startsWith('/dashboard/auctions')
      },
      {
        name: $t('dashboard.bids'),
        href: '/dashboard/bids',
        current: $page.url.pathname.startsWith('/dashboard/bids')
      },
      ...($canAccessSystemDashboard ? [{
        name: $t('dashboard.systemDashboard'),
        href: '/dashboard/system',
        current: $page.url.pathname.startsWith('/dashboard/system')
      }] : [])
    ];
  </script>
  
  <div class="flex h-screen bg-gray-50">
    
    <!-- Sidebar -->
    <div class="hidden md:flex md:flex-shrink-0">
      <div class="flex flex-col w-64">
        <div class="flex flex-col flex-grow pt-5 pb-4 overflow-y-auto bg-white border-r border-gray-200">
          
          <!-- Logo/Brand -->
          <div class="flex items-center flex-shrink-0 px-4">
            <h1 class="text-lg font-semibold text-primary-600">
              {$t('dashboard.title')}
            </h1>
          </div>
  
          <!-- Navigation -->
          <nav class="mt-8 flex-1 px-2 space-y-1">
            {#each navigationItems as item}
                <a
                href={item.href}
                class="group flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors {
                  item.current 
                    ? 'bg-primary-100 text-primary-900' 
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                }"
                >
                    {item.name}
                </a>
            {/each}
          </nav>
  
          <!-- User Priority Indicator -->
          {#if $userPriority > 1}
            <div class="flex-shrink-0 px-4 py-4 border-t border-gray-200">
              <div class="flex items-center justify-between">
                <span class="text-xs text-gray-500">
                  {$t('dashboard.userPriority')}
                </span>
                <div class="flex items-center space-x-1">
                  {#each Array(5) as _, i}
                    <div class="w-2 h-2 rounded-full {i < $userPriority ? 'bg-primary-500' : 'bg-gray-200'}"></div>
                  {/each}
                </div>
              </div>
            </div>
          {/if}
        </div>
      </div>
    </div>
  
    <!-- Main Content -->
    <div class="flex flex-col flex-1 overflow-hidden">
      <slot />
    </div>
  </div>
  
  <!-- Mobile Navigation -->
  <div class="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 px-4 py-2">
    <div class="flex justify-around">
      {#each navigationItems.slice(0, 4) as item}
        <a
          href={item.href}
          class="flex flex-col items-center py-2 px-3 text-xs {
            item.current ? 'text-primary-600' : 'text-gray-600'
          }"
        >
          <span class="truncate">{item.name}</span>
        </a>
      {/each}
    </div>
  </div>