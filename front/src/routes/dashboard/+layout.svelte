<!-- Modern Dashboard Layout with Best Practices -->
<script>
	import { page } from '$app/stores';
	import { user } from '$lib/stores/user.svelte.js';
	import { getCanAccessSystemDashboard, getUserPriority } from '$lib/stores/dashboard.svelte.js';
	import { t } from '$lib/i18n';
	import { locale } from '$lib/i18n/config';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { fade, fly, slide } from 'svelte/transition';
	import { cubicOut } from 'svelte/easing';

	// Define children as snippet prop for Svelte 5
	let { children } = $props();

	// Svelte 5 Runes for reactive state
	let sidebarOpen = $state(false);
	let sidebarCollapsed = $state(false);
	let mounted = $state(false);
	let searchTerm = $state('');
	let notifications = $state([]);
	let isSearchFocused = $state(false);

	// Performance states
	let isNavigating = $state(false);
	let lastUpdate = $state(Date.now());

	// Permission-based reactive computations
	const canManageProperties = $derived(
		$user &&
			($user.is_superuser ||
				$user.role === 'administrator' ||
				$user.role === 'manager' ||
				$user.role === 'appraiser' ||
				$user.role === 'owner')
	);

	const canManageUsers = $derived(
		$user && ($user.is_superuser || $user.role === 'administrator' || $user.role === 'manager')
	);

	const canAccessFinancials = $derived(
		$user &&
			($user.is_superuser ||
				$user.role === 'administrator' ||
				$user.role === 'manager' ||
				$user.role === 'accountant' ||
				$user.role === 'legal_advisor')
	);

	const canManageMaintenance = $derived(
		$user &&
			($user.is_superuser ||
				$user.role === 'administrator' ||
				$user.role === 'manager' ||
				$user.role === 'maintenance_manager')
	);

	// Enhanced navigation with backend role-based permissions using Svelte 5 runes
	const navigationItems = $derived([
		// Always accessible items
		{
			name: $t('dashboard.overview'),
			description: $t('dashboard.overviewDesc'),
			href: '/dashboard',
			icon: 'home',
			current: $page.url.pathname === '/dashboard',
			badge: null,
			permission: true
		},
		// Property management - based on backend permissions
		...(canManageProperties
			? [
					{
						name: $t('dashboard.properties'),
						description: $t('dashboard.manageProperties'),
						href: '/dashboard/properties',
						icon: 'building',
						current: $page.url.pathname.startsWith('/dashboard/properties'),
						badge: null,
						permission: true
					}
				]
			: []),
		// Auction management - auctioneers and managers
		...($user &&
		($user.role === 'auctioneer' || $user.role === 'administrator' || $user.role === 'manager')
			? [
					{
						name: $t('dashboard.auctions'),
						description: $t('dashboard.manageAuctions'),
						href: '/dashboard/auctions',
						icon: 'gavel',
						current: $page.url.pathname.startsWith('/dashboard/auctions'),
						badge: null,
						permission: true
					}
				]
			: []),
		// Bidding - all authenticated users
		{
			name: $t('dashboard.bids'),
			description: $t('dashboard.manageBids'),
			href: '/dashboard/bids',
			icon: 'currency',
			current: $page.url.pathname.startsWith('/dashboard/bids'),
			badge: null,
			permission: true
		},
		// Analytics - property professionals and above
		...($user && ($user.is_property_professional || $user.is_admin_level || $user.role === 'owner')
			? [
					{
						name: $t('dashboard.analytics'),
						description: $t('dashboard.analyticsDesc'),
						href: '/dashboard/analytics',
						icon: 'chart',
						current: $page.url.pathname.startsWith('/dashboard/analytics'),
						badge: null,
						permission: true
					}
				]
			: []),
		// Financial management - accountants and legal advisors
		...(canAccessFinancials
			? [
					{
						name: $t('dashboard.payments'),
						description: $t('dashboard.paymentsDesc'),
						href: '/dashboard/payments',
						icon: 'creditCard',
						current: $page.url.pathname.startsWith('/dashboard/payments'),
						badge: null,
						permission: true
					},
					{
						name: $t('dashboard.bankAccounts'),
						description: $t('dashboard.bankAccountsDesc'),
						href: '/dashboard/bank-accounts',
						icon: 'bank',
						current: $page.url.pathname.startsWith('/dashboard/bank-accounts'),
						badge: null,
						permission: true
					}
				]
			: []),
		// Maintenance management
		...(canManageMaintenance
			? [
					{
						name: $t('dashboard.workers'),
						description: $t('dashboard.workersDesc'),
						href: '/dashboard/workers',
						icon: 'users',
						current: $page.url.pathname.startsWith('/dashboard/workers'),
						badge: null,
						permission: true
					}
				]
			: []),
		// User management - administrators and managers only
		...(canManageUsers
			? [
					{
						name: $t('dashboard.userManagement'),
						description: $t('dashboard.manageUsers'),
						href: '/dashboard/users',
						icon: 'userGroup',
						current: $page.url.pathname.startsWith('/dashboard/users'),
						badge: null,
						permission: true
					}
				]
			: []),
		// System dashboard - administrators only
		...(getCanAccessSystemDashboard()
			? [
					{
						name: $t('dashboard.systemDashboard'),
						description: $t('dashboard.systemOverview'),
						href: '/dashboard/system',
						icon: 'cog',
						current: $page.url.pathname.startsWith('/dashboard/system'),
						badge: 'Admin',
						permission: true
					}
				]
			: [])
	]);

	// Enhanced navigation item management with Svelte 5 runes
	const activeNavItem = $derived(
		navigationItems.find((item) => item.current) || navigationItems[0]
	);

	// Search functionality
	const filteredNavigationItems = $derived(() => {
		if (!searchTerm.trim()) return navigationItems;
		return navigationItems.filter(
			(item) =>
				item.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
				item.description.toLowerCase().includes(searchTerm.toLowerCase())
		);
	});

	// Language switching
	function switchLanguage(lang) {
		locale.set(lang);
	}

	// SVG Icons for navigation with enhanced icon set
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
		</svg>`,
		userGroup: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
			<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/>
		</svg>`,
		shield: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
			<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
		</svg>`,
		globe: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
			<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9"/>
		</svg>`,
		bell: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
			<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/>
		</svg>`
	};

	// Enhanced functions with Svelte 5 runes
	function toggleSidebar() {
		sidebarOpen = !sidebarOpen;
	}

	function toggleCollapse() {
		sidebarCollapsed = !sidebarCollapsed;
	}

	function handleSearchClear() {
		searchTerm = '';
	}

	function handleNavigation(href) {
		goto(href);
		if (window.innerWidth < 768) {
			sidebarOpen = false;
		}
	}

	function handleLogout() {
		// Implement logout logic
		user.set(null);
		goto('/login');
	}

	// Check authentication
	onMount(() => {
		mounted = true;
		if (!$user) {
			goto('/login');
			return;
		}

		// Handle responsive behavior
		const handleResize = () => {
			if (window.innerWidth >= 1024) {
				sidebarOpen = true;
			}
		};

		window.addEventListener('resize', handleResize);
		handleResize();

		return () => {
			window.removeEventListener('resize', handleResize);
		};
	});

	// Close sidebar when route changes
	$effect(() => {
		if ($page.url.pathname && mounted) {
			sidebarOpen = false;
		}
	});

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

<svelte:window onclick={handleClickOutside} />

{#if mounted && $user}
	<div class="min-h-screen bg-gray-50 dark:bg-gray-900">
		<!-- Mobile menu overlay -->
		{#if sidebarOpen}
			<div
				class="bg-opacity-75 fixed inset-0 z-40 bg-gray-600 lg:hidden"
				transition:fade={{ duration: 200 }}
				onclick={toggleSidebar}
			></div>
		{/if}

		<!-- Modern Sidebar -->
		<div
			class="sidebar-container fixed inset-y-0 left-0 z-50 transform transition-all duration-300 ease-in-out lg:static lg:inset-0 lg:translate-x-0 {sidebarCollapsed
				? 'w-16'
				: 'w-72'} {sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}"
		>
			<div
				class="flex h-full flex-col border-r border-gray-200/80 bg-white/95 shadow-2xl backdrop-blur-xl dark:border-gray-700/80 dark:bg-gray-800/95"
			>
				<!-- Enhanced Sidebar Header -->
				<div
					class="flex h-16 shrink-0 items-center justify-between border-b border-gray-200/50 px-6 dark:border-gray-700/50"
				>
					{#if !sidebarCollapsed}
						<div
							class="flex items-center space-x-3"
							transition:slide={{ duration: 200, easing: cubicOut }}
						>
							<div
								class="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 shadow-lg"
							>
								<svg
									class="h-6 w-6 text-white"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
									/>
								</svg>
							</div>
							<div class="flex flex-col">
								<h1 class="text-lg font-bold text-gray-900 dark:text-white">AuctionPro</h1>
								<p class="text-xs text-gray-500 dark:text-gray-400">Dashboard</p>
							</div>
						</div>
					{:else}
						<div class="flex w-full items-center justify-center">
							<div
								class="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 shadow-lg"
							>
								<svg
									class="h-5 w-5 text-white"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16"
									/>
								</svg>
							</div>
						</div>
					{/if}

					<!-- Mobile close / Desktop collapse toggle -->
					<div class="flex items-center space-x-2">
						{#if !sidebarCollapsed}
							<button
								type="button"
								class="hidden rounded-lg p-2 text-gray-400 transition-colors hover:bg-gray-100 hover:text-gray-600 focus:ring-2 focus:ring-indigo-500 focus:outline-none lg:flex dark:text-gray-500 dark:hover:bg-gray-700 dark:hover:text-gray-300"
								onclick={toggleCollapse}
								aria-label="Collapse sidebar"
							>
								<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M11 19l-7-7 7-7m8 14l-7-7 7-7"
									/>
								</svg>
							</button>
						{/if}

						<button
							type="button"
							class="rounded-lg p-2 text-gray-400 transition-colors hover:bg-gray-100 hover:text-gray-600 focus:ring-2 focus:ring-indigo-500 focus:outline-none lg:hidden dark:text-gray-500 dark:hover:bg-gray-700 dark:hover:text-gray-300"
							onclick={toggleSidebar}
							aria-label="Close sidebar"
						>
							<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M6 18L18 6M6 6l12 12"
								/>
							</svg>
						</button>
					</div>
				</div>

				<!-- Enhanced Search -->
				{#if !sidebarCollapsed}
					<div class="px-4 py-4" transition:slide={{ duration: 200, easing: cubicOut }}>
						<div class="group relative">
							<svg
								class="absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2 transform text-gray-400 transition-colors group-focus-within:text-indigo-500 dark:text-gray-500"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
								/>
							</svg>
							<input
								type="text"
								bind:value={searchTerm}
								onfocus={() => (isSearchFocused = true)}
								onblur={() => (isSearchFocused = false)}
								placeholder={$t('common.search')}
								class="w-full rounded-xl border border-gray-200/60 bg-gray-50/80 py-3 pr-10 pl-10 text-sm placeholder-gray-400 backdrop-blur-sm transition-all duration-300 focus:border-indigo-500/50 focus:bg-white focus:ring-2 focus:ring-indigo-500/80 dark:border-gray-700/60 dark:bg-gray-900/50 dark:placeholder-gray-500 dark:focus:bg-gray-800"
								aria-label="Search navigation items"
							/>
							{#if searchTerm}
								<button
									class="absolute top-1/2 right-3 -translate-y-1/2 transform rounded-md p-1 text-gray-400 transition-all duration-200 hover:bg-gray-200 hover:text-gray-600 dark:hover:bg-gray-700 dark:hover:text-gray-300"
									onclick={handleSearchClear}
									aria-label="Clear search"
								>
									<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M6 18L18 6M6 6l12 12"
										/>
									</svg>
								</button>
							{/if}

							<!-- Search focus indicator -->
							{#if isSearchFocused}
								<div
									class="pointer-events-none absolute inset-0 rounded-xl ring-2 ring-indigo-500/20 ring-offset-2 ring-offset-white dark:ring-offset-gray-800"
									transition:fade={{ duration: 200 }}
								></div>
							{/if}
						</div>
					</div>
				{/if}

				<!-- Enhanced Navigation with Modern Design -->
				<nav
					class="scrollbar-thin scrollbar-thumb-gray-300 dark:scrollbar-thumb-gray-600 scrollbar-track-transparent flex-1 space-y-2 overflow-y-auto px-3 py-4"
				>
					{#each filteredNavigationItems as item, index (item.href)}
						<a
							href={item.href}
							class="group relative flex transform items-center rounded-xl transition-all duration-300 ease-out hover:scale-[1.02] {item.current
								? 'bg-gradient-to-r from-indigo-500 via-purple-500 to-indigo-600 text-white shadow-lg ring-1 shadow-indigo-500/25 ring-white/20'
								: 'text-gray-700 hover:bg-gray-100/80 hover:text-gray-900 hover:shadow-md dark:text-gray-300 dark:hover:bg-gray-700/50 dark:hover:text-white'} {sidebarCollapsed
								? 'justify-center px-3 py-3'
								: 'px-4 py-3'}"
							onclick={(e) => {
								e.preventDefault();
								isNavigating = true;
								setTimeout(() => (isNavigating = false), 300);
								handleNavigation(item.href);
							}}
							role="button"
							tabindex="0"
							aria-label={sidebarCollapsed ? item.name : undefined}
							style="animation-delay: {index * 50}ms"
							in:slide={{ duration: 300, delay: index * 50, easing: cubicOut }}
						>
							<!-- Modern Icon Container -->
							<div
								class="relative flex items-center justify-center {sidebarCollapsed
									? 'h-8 w-8'
									: 'mr-4 h-10 w-10'} rounded-xl {item.current
									? 'bg-white/20 shadow-inner'
									: 'bg-gray-100/80 group-hover:bg-gray-200/80 group-hover:shadow-md dark:bg-gray-700/80 dark:group-hover:bg-gray-600/80'} transition-all duration-300"
							>
								<!-- Icon with enhanced styling -->
								<div class="text-current transition-transform duration-300 group-hover:scale-110">
									{@html icons[item.icon] || icons.home}
								</div>

								<!-- Active indicator -->
								{#if item.current}
									<div
										class="absolute inset-0 rounded-xl bg-gradient-to-br from-white/10 to-transparent"
									></div>
								{/if}
							</div>

							<!-- Navigation Content -->
							{#if !sidebarCollapsed}
								<div class="min-w-0 flex-1" transition:slide={{ duration: 200, easing: cubicOut }}>
									<div class="flex items-center justify-between">
										<span class="truncate text-sm font-semibold">
											{item.name}
										</span>
										{#if item.badge}
											<span
												class="ml-2 rounded-full px-2.5 py-1 text-xs font-bold {item.current
													? 'bg-white/25 text-white shadow-sm'
													: 'bg-indigo-100 text-indigo-700 dark:bg-indigo-900/50 dark:text-indigo-300'} transition-all duration-200"
											>
												{item.badge}
											</span>
										{/if}
									</div>
									<p class="mt-1 truncate text-xs font-medium opacity-70">
										{item.description}
									</p>
								</div>

								<!-- Navigation Arrow -->
								<div
									class="ml-2 flex-shrink-0 translate-x-0 transform opacity-0 transition-all duration-300 group-hover:translate-x-1 group-hover:opacity-100"
								>
									<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M9 5l7 7-7 7"
										/>
									</svg>
								</div>
							{/if}

							<!-- Collapsed State Badge -->
							{#if sidebarCollapsed && item.badge}
								<div
									class="absolute -top-1 -right-1 flex h-5 w-5 animate-pulse items-center justify-center rounded-full border-2 border-white bg-gradient-to-r from-red-500 to-pink-500 shadow-lg dark:border-gray-800"
								>
									<span class="text-xs font-bold text-white">
										{parseInt(item.badge) > 9 ? '9+' : item.badge}
									</span>
								</div>
							{/if}

							<!-- Enhanced Tooltip for Collapsed State -->
							{#if sidebarCollapsed}
								<div
									class="invisible absolute left-full z-50 ml-6 rounded-xl border border-gray-700/50 bg-gray-900/95 px-4 py-3 text-sm whitespace-nowrap text-white opacity-0 shadow-2xl backdrop-blur-sm transition-all duration-300 group-hover:visible group-hover:opacity-100 dark:bg-gray-800/95"
								>
									<div class="font-semibold">{item.name}</div>
									<div class="mt-1 text-xs opacity-75">{item.description}</div>
									{#if item.badge}
										<span
											class="mt-2 inline-block rounded-full bg-indigo-500/80 px-2 py-1 text-xs font-bold"
										>
											{item.badge}
										</span>
									{/if}
									<!-- Enhanced Tooltip Arrow -->
									<div class="absolute top-1/2 left-0 -translate-x-2 -translate-y-1/2 transform">
										<div
											class="h-4 w-4 rotate-45 border-t border-l border-gray-700/50 bg-gray-900/95 dark:bg-gray-800/95"
										></div>
									</div>
								</div>
							{/if}

							<!-- Loading state overlay -->
							{#if isNavigating && item.current}
								<div class="absolute inset-0 animate-pulse rounded-xl bg-white/10"></div>
							{/if}
						</a>
					{/each}
				</nav>

				<!-- User section -->
				<div class="flex-shrink-0 border-t border-gray-200 p-4 dark:border-gray-700">
					<!-- User Priority Indicator -->
					{#if getUserPriority() > 1}
						<div
							class="mb-4 rounded-lg border border-amber-200 bg-gradient-to-r from-amber-50 to-orange-50 p-3 dark:border-amber-700 dark:from-amber-900/20 dark:to-orange-900/20"
						>
							<div class="mb-2 flex items-center justify-between">
								<span class="text-sm font-medium text-amber-800 dark:text-amber-300">
									{$t('dashboard.userPriority')}
								</span>
								<div class="flex items-center space-x-1">
									{#each Array(5) as _, i}
										<div
											class="h-2 w-2 rounded-full transition-colors duration-200 {i <
											getUserPriority()
												? 'bg-amber-500'
												: 'bg-gray-300 dark:bg-gray-600'}"
										></div>
									{/each}
								</div>
							</div>
							<p class="text-xs text-amber-700 dark:text-amber-400">
								{$t('dashboard.priorityLevel', { level: getUserPriority() })}
							</p>
						</div>
					{/if}

					<!-- User profile -->
					<div class="flex items-center space-x-3 rounded-lg bg-gray-50 p-3 dark:bg-gray-700/50">
						<div class="flex-shrink-0">
							{#if $user.avatar_url}
								<img
									class="h-10 w-10 rounded-full ring-2 ring-indigo-500"
									src={$user.avatar_url}
									alt={$user.first_name}
								/>
							{:else}
								<div
									class="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 font-medium text-white"
								>
									{$user.first_name?.[0] || ''}{$user.last_name?.[0] || ''}
								</div>
							{/if}
						</div>
						<div class="min-w-0 flex-1">
							<p class="truncate text-sm font-medium text-gray-900 dark:text-white">
								{$user.first_name}
								{$user.last_name}
							</p>
							<p class="truncate text-xs text-gray-500 dark:text-gray-400">
								{$user.email}
							</p>
						</div>
						<a
							href="/profile"
							class="rounded-lg p-2 text-gray-400 transition-colors duration-200 hover:bg-gray-200 hover:text-gray-500 dark:hover:bg-gray-600 dark:hover:text-gray-300"
						>
							<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
								/>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
								/>
							</svg>
						</a>
					</div>
				</div>
			</div>
		</div>

		<!-- Enhanced Main Content Area -->
		<div
			class="flex-1 transition-all duration-300 ease-in-out {sidebarCollapsed
				? 'lg:ml-20'
				: 'lg:ml-80'} flex min-h-screen flex-col"
		>
			<!-- Enhanced Top Navigation Bar -->
			<header
				class="sticky top-0 z-40 border-b border-gray-200 bg-white/80 shadow-sm backdrop-blur-xl dark:border-gray-800 dark:bg-gray-900/80"
			>
				<div class="flex h-16 items-center justify-between px-4 sm:px-6 lg:px-8">
					<!-- Left section -->
					<div class="flex items-center space-x-4">
						<!-- Mobile menu button -->
						<button
							class="rounded-lg p-2 text-gray-500 transition-colors hover:bg-gray-100 hover:text-gray-700 focus:ring-2 focus:ring-indigo-500 focus:outline-none lg:hidden dark:text-gray-400 dark:hover:bg-gray-800 dark:hover:text-gray-200"
							onclick={toggleSidebar}
							aria-label="Open sidebar"
						>
							<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M4 6h16M4 12h16M4 18h16"
								/>
							</svg>
						</button>

						<!-- Enhanced Breadcrumb -->
						<nav class="hidden items-center space-x-2 text-sm sm:flex" aria-label="Breadcrumb">
							<a
								href="/dashboard"
								class="font-medium text-gray-500 transition-colors hover:text-indigo-600 dark:text-gray-400 dark:hover:text-indigo-400"
							>
								{$t('dashboard.title')}
							</a>
							{#if $page.url.pathname !== '/dashboard'}
								<svg
									class="h-4 w-4 text-gray-300 dark:text-gray-600"
									fill="currentColor"
									viewBox="0 0 20 20"
								>
									<path
										fill-rule="evenodd"
										d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
										clip-rule="evenodd"
									/>
								</svg>
								<span class="font-semibold text-gray-900 dark:text-white">
									{activeNavItem?.name || $t('common.page')}
								</span>
							{/if}
						</nav>

						<!-- Mobile active page title -->
						<h1 class="text-lg font-semibold text-gray-900 sm:hidden dark:text-white">
							{activeNavItem?.name || $t('dashboard.title')}
						</h1>
					</div>

					<!-- Right section -->
					<div class="flex items-center space-x-3">
						<!-- Language switcher -->
						<button
							class="hidden items-center rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-100 focus:ring-2 focus:ring-indigo-500 focus:outline-none sm:flex dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700"
							onclick={() => switchLanguage($locale === 'en' ? 'ar' : 'en')}
						>
							{@html icons.globe}
							<span class="ml-2">{$locale.toUpperCase()}</span>
						</button>

						<!-- Notifications -->
						<button
							class="relative rounded-lg p-2 text-gray-500 transition-colors hover:bg-gray-100 hover:text-gray-700 focus:ring-2 focus:ring-indigo-500 focus:outline-none dark:text-gray-400 dark:hover:bg-gray-800 dark:hover:text-gray-200"
							aria-label="View notifications"
						>
							{@html icons.bell}
							<!-- Notification badge -->
							<div
								class="absolute -top-1 -right-1 flex h-5 w-5 items-center justify-center rounded-full bg-red-500"
							>
								<span class="text-xs font-bold text-white">3</span>
							</div>
						</button>

						<!-- User menu -->
						<div class="relative">
							<button
								class="flex items-center space-x-2 rounded-lg p-2 transition-colors hover:bg-gray-100 focus:ring-2 focus:ring-indigo-500 focus:outline-none dark:hover:bg-gray-800"
								aria-label="User menu"
							>
								{#if $user.avatar}
									<img
										class="h-8 w-8 rounded-full ring-2 ring-indigo-500"
										src={$user.avatar}
										alt="User avatar"
									/>
								{:else}
									<div
										class="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 text-sm font-bold text-white"
									>
										{$user.first_name?.[0] || ''}{$user.last_name?.[0] || ''}
									</div>
								{/if}
								<span class="hidden text-sm font-medium text-gray-700 sm:block dark:text-gray-300">
									{$user.first_name}
								</span>
								<svg
									class="hidden h-4 w-4 text-gray-400 sm:block"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M19 9l-7 7-7-7"
									/>
								</svg>
							</button>
						</div>
					</div>
				</div>
			</header>

			<!-- Enhanced Page Content -->
			<main class="flex-1 overflow-auto bg-gray-50 dark:bg-gray-900">
				<div class="p-4 sm:p-6 lg:p-8">
					{@render children()}
				</div>
			</main>
		</div>
	</div>
{/if}
