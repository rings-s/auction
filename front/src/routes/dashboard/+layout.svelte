<!-- Enhanced Dashboard Root Layout -->
<script>
	import { page } from '$app/stores';
	import { user } from '$lib/stores/user';
	import { canAccessSystemDashboard, userPriority } from '$lib/stores/dashboard';
	import { t } from '$lib/i18n';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { fade, fly } from 'svelte/transition';

	let sidebarOpen = false;
	let mounted = false;

	// Enhanced navigation with icons and descriptions
	$: navigationItems = [
		{
			name: $t('dashboard.overview'),
			description: $t('dashboard.overviewDesc'),
			href: '/dashboard',
			icon: 'home',
			current: $page.url.pathname === '/dashboard',
			badge: null
		},
		{
			name: $t('dashboard.properties'),
			description: $t('dashboard.manageProperties'),
			href: '/dashboard/properties',
			icon: 'building',
			current: $page.url.pathname.startsWith('/dashboard/properties'),
			badge: null
		},
		{
			name: $t('dashboard.auctions'),
			description: $t('dashboard.manageAuctions'),
			href: '/dashboard/auctions',
			icon: 'gavel',
			current: $page.url.pathname.startsWith('/dashboard/auctions'),
			badge: null
		},
		{
			name: $t('dashboard.bids'),
			description: $t('dashboard.manageBids'),
			href: '/dashboard/bids',
			icon: 'currency',
			current: $page.url.pathname.startsWith('/dashboard/bids'),
			badge: null
		},
		{
			name: $t('dashboard.analytics'),
			description: $t('dashboard.analyticsDesc'),
			href: '/dashboard/analytics',
			icon: 'chart',
			current: $page.url.pathname.startsWith('/dashboard/analytics'),
			badge: null
		},
		{
			name: $t('dashboard.payments'),
			description: $t('dashboard.paymentsDesc'),
			href: '/dashboard/payments',
			icon: 'creditCard',
			current: $page.url.pathname.startsWith('/dashboard/payments'),
			badge: null
		},
		{
			name: $t('dashboard.workers'),
			description: $t('dashboard.workersDesc'),
			href: '/dashboard/workers',
			icon: 'users',
			current: $page.url.pathname.startsWith('/dashboard/workers'),
			badge: null
		},
		{
			name: $t('dashboard.bankAccounts'),
			description: $t('dashboard.bankAccountsDesc'),
			href: '/dashboard/bank-accounts',
			icon: 'bank',
			current: $page.url.pathname.startsWith('/dashboard/bank-accounts'),
			badge: null
		},
		...($canAccessSystemDashboard
			? [
					{
						name: $t('dashboard.systemDashboard'),
						description: $t('dashboard.systemOverview'),
						href: '/dashboard/system',
						icon: 'cog',
						current: $page.url.pathname.startsWith('/dashboard/system'),
						badge: 'Admin'
					}
				]
			: [])
	];

	// SVG Icons for navigation
	const icons = {
		home: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
			<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
		</svg>`,
		building: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
			<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
		</svg>`,
		gavel: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
			<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
		</svg>`,
		currency: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
			<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"/>
		</svg>`,
		chart: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
			<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
		</svg>`,
		creditCard: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
			<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"/>
		</svg>`,
		users: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
			<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"/>
		</svg>`,
		bank: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
			<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 14v3m4-3v3m4-3v3M3 21h18M3 10h18M10.5 3L12 2l1.5 1H21l-1 6H4l-1-6h7.5z"/>
		</svg>`,
		cog: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
			<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
			<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
		</svg>`
	};

	// Check authentication
	onMount(() => {
		mounted = true;
		if (!$user) {
			goto('/login');
			return;
		}
	});

	// Close sidebar when route changes
	$: if ($page.url.pathname && mounted) {
		sidebarOpen = false;
	}

	// Toggle sidebar
	function toggleSidebar() {
		sidebarOpen = !sidebarOpen;
	}

	// Close sidebar when clicking outside
	function handleClickOutside(event) {
		if (sidebarOpen && !event.target.closest('.sidebar-container')) {
			sidebarOpen = false;
		}
	}
</script>

<svelte:head>
	<title>{$t('dashboard.title')} - {$t('app.name')}</title>
	<meta name="description" content={$t('dashboard.description')} />
</svelte:head>

<svelte:window on:click={handleClickOutside} />

{#if mounted && $user}
	<div class="min-h-screen bg-gray-50 dark:bg-gray-900">
		<!-- Mobile menu overlay -->
		{#if sidebarOpen}
			<div 
				class="fixed inset-0 z-40 bg-gray-600 bg-opacity-75 lg:hidden" 
				transition:fade={{ duration: 200 }}
				on:click={toggleSidebar}
			></div>
		{/if}

		<!-- Sidebar -->
		<div class="sidebar-container fixed inset-y-0 left-0 z-50 w-72 transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0 {sidebarOpen ? 'translate-x-0' : '-translate-x-full'}">
			<div class="flex h-full flex-col bg-white dark:bg-gray-800 shadow-xl">
				<!-- Sidebar header -->
				<div class="flex h-16 shrink-0 items-center justify-between px-6 border-b border-gray-200 dark:border-gray-700">
					<div class="flex items-center space-x-3">
						<div class="h-8 w-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
							<svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
							</svg>
						</div>
						<h1 class="text-lg font-semibold text-gray-900 dark:text-white">
							{$t('dashboard.title')}
						</h1>
					</div>
					
					<!-- Close button for mobile -->
					<button 
						type="button" 
						class="lg:hidden p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
						on:click={toggleSidebar}
					>
						<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
						</svg>
					</button>
				</div>

				<!-- Navigation -->
				<nav class="flex-1 px-4 py-6 space-y-2 overflow-y-auto">
					{#each navigationItems as item}
						<a
							href={item.href}
							class="group flex items-center px-3 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 {item.current
								? 'bg-gradient-to-r from-indigo-500 to-purple-600 text-white shadow-lg transform scale-[1.02]'
								: 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-white'}"
						>
							<div class="flex items-center justify-center w-10 h-10 rounded-lg {item.current ? 'bg-white/20' : 'bg-gray-100 dark:bg-gray-700 group-hover:bg-gray-200 dark:group-hover:bg-gray-600'} mr-3 transition-colors duration-200">
								{@html icons[item.icon]}
							</div>
							<div class="flex-1 min-w-0">
								<div class="flex items-center justify-between">
									<span class="truncate">{item.name}</span>
									{#if item.badge}
										<span class="ml-2 px-2 py-1 text-xs font-medium bg-orange-100 text-orange-800 rounded-full">
											{item.badge}
										</span>
									{/if}
								</div>
								<p class="text-xs opacity-75 truncate mt-0.5">{item.description}</p>
							</div>
						</a>
					{/each}
				</nav>

				<!-- User section -->
				<div class="flex-shrink-0 border-t border-gray-200 dark:border-gray-700 p-4">
					<!-- User Priority Indicator -->
					{#if $userPriority > 1}
						<div class="mb-4 p-3 bg-gradient-to-r from-amber-50 to-orange-50 dark:from-amber-900/20 dark:to-orange-900/20 rounded-lg border border-amber-200 dark:border-amber-700">
							<div class="flex items-center justify-between mb-2">
								<span class="text-sm font-medium text-amber-800 dark:text-amber-300">
									{$t('dashboard.userPriority')}
								</span>
								<div class="flex items-center space-x-1">
									{#each Array(5) as _, i}
										<div
											class="h-2 w-2 rounded-full transition-colors duration-200 {i < $userPriority
												? 'bg-amber-500'
												: 'bg-gray-300 dark:bg-gray-600'}"
										></div>
									{/each}
								</div>
							</div>
							<p class="text-xs text-amber-700 dark:text-amber-400">
								{$t('dashboard.priorityLevel', { level: $userPriority })}
							</p>
						</div>
					{/if}

					<!-- User profile -->
					<div class="flex items-center space-x-3 p-3 rounded-lg bg-gray-50 dark:bg-gray-700/50">
						<div class="flex-shrink-0">
							{#if $user.avatar_url}
								<img
									class="h-10 w-10 rounded-full ring-2 ring-indigo-500"
									src={$user.avatar_url}
									alt={$user.first_name}
								/>
							{:else}
								<div class="h-10 w-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-medium">
									{$user.first_name?.[0] || ''}{$user.last_name?.[0] || ''}
								</div>
							{/if}
						</div>
						<div class="flex-1 min-w-0">
							<p class="text-sm font-medium text-gray-900 dark:text-white truncate">
								{$user.first_name} {$user.last_name}
							</p>
							<p class="text-xs text-gray-500 dark:text-gray-400 truncate">
								{$user.email}
							</p>
						</div>
						<a
							href="/profile"
							class="p-2 text-gray-400 hover:text-gray-500 dark:hover:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors duration-200"
						>
							<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
							</svg>
						</a>
					</div>
				</div>
			</div>
		</div>

		<!-- Main content -->
		<div class="lg:pl-72">
			<!-- Top navigation bar -->
			<div class="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-gray-200 dark:border-gray-700 bg-white/80 dark:bg-gray-800/80 backdrop-blur-md px-4 sm:px-6 lg:px-8">
				<!-- Mobile menu button -->
				<button
					type="button"
					class="lg:hidden p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
					on:click={toggleSidebar}
				>
					<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
					</svg>
				</button>

				<!-- Breadcrumb -->
				<div class="flex items-center space-x-2 text-sm">
					<a href="/dashboard" class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300">
						{$t('dashboard.title')}
					</a>
					{#if $page.url.pathname !== '/dashboard'}
						<svg class="w-4 h-4 text-gray-300 dark:text-gray-600" fill="currentColor" viewBox="0 0 20 20">
							<path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd"/>
						</svg>
						<span class="text-gray-900 dark:text-white font-medium">
							{navigationItems.find(item => item.current)?.name || $t('common.page')}
						</span>
					{/if}
				</div>

				<!-- Right side actions -->
				<div class="flex items-center space-x-3">
					<!-- Quick actions will be added here -->
				</div>
			</div>

			<!-- Page content -->
			<main class="flex-1">
				<slot />
			</main>
		</div>
	</div>
{/if}