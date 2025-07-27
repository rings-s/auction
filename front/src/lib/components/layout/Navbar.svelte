<!-- src/lib/components/layout/Navbar.svelte -->
<script>
	import { page } from '$app/stores';
	import { user } from '$lib/stores/user.svelte.js';
	import { t, locale } from '$lib/i18n';
	import { theme } from '$lib/stores/theme.svelte.js';
	import { AUTH_ENDPOINTS } from '$lib/constants';
	import ThemeToggle from '$lib/components/ui/ThemeToggle.svelte';
	import LanguageSelector from '$lib/components/shared/LanguageSelector.svelte';
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
			navLinks.forEach((link) => {
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
						'Content-Type': 'application/json'
					},
					body: JSON.stringify({ refresh: refreshToken })
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
		$page.url.pathname === '/'
			? 'home'
			: $page.url.pathname.startsWith('/properties')
				? 'properties'
				: $page.url.pathname.startsWith('/property-management')
					? 'rentals'
					: $page.url.pathname.startsWith('/auctions')
						? 'auctions'
						: $page.url.pathname.startsWith('/dashboard')
							? 'dashboard'
							: $page.url.pathname.startsWith('/messages')
								? 'messages'
								: 'default';

	// Enhanced gradient color system with vibrant gradients and animations
	$: sectionStyles = {
		home: {
			logoAccent: 'from-blue-500 via-cyan-500 to-blue-600',
			navbarGradient: 'bg-gradient-to-r from-blue-500/10 via-cyan-500/10 to-blue-600/10',
			navActive:
				'bg-gradient-to-r from-blue-500 to-cyan-600 bg-clip-text text-transparent border-b-2 border-gradient-to-r border-blue-500',
			navHover:
				'hover:bg-gradient-to-r hover:from-blue-50 hover:via-cyan-50 hover:to-blue-50 dark:hover:from-blue-900/20 dark:hover:via-cyan-900/20 dark:hover:to-blue-900/20',
			loginBtn:
				'border-2 border-gradient-to-r from-blue-400 to-cyan-500 hover:bg-gradient-to-r hover:from-blue-50 hover:to-cyan-50 text-gradient-to-r from-blue-600 to-cyan-700 focus:ring-4 focus:ring-blue-500/30 shadow-lg shadow-blue-500/20 hover:shadow-xl hover:shadow-blue-500/30 transition-all duration-300',
			signupBtn:
				'bg-gradient-to-r from-blue-600 via-cyan-600 to-blue-700 hover:from-blue-700 hover:via-cyan-700 hover:to-blue-800 text-white shadow-lg shadow-blue-500/30 hover:shadow-xl hover:shadow-blue-500/40 focus:ring-4 focus:ring-blue-500/30 transform hover:scale-[1.02] hover:-translate-y-0.5 transition-all duration-300'
		},
		properties: {
			logoAccent: 'from-emerald-500 via-green-500 to-teal-600',
			navbarGradient: 'bg-gradient-to-r from-emerald-500/10 via-green-500/10 to-teal-600/10',
			navActive:
				'bg-gradient-to-r from-emerald-500 to-teal-600 bg-clip-text text-transparent border-b-2 border-gradient-to-r border-emerald-500',
			navHover:
				'hover:bg-gradient-to-r hover:from-emerald-50 hover:via-green-50 hover:to-teal-50 dark:hover:from-emerald-900/20 dark:hover:via-green-900/20 dark:hover:to-teal-900/20',
			loginBtn:
				'border-2 border-gradient-to-r from-emerald-400 to-teal-500 hover:bg-gradient-to-r hover:from-emerald-50 hover:to-teal-50 text-gradient-to-r from-emerald-600 to-teal-700 focus:ring-4 focus:ring-emerald-500/30 shadow-lg shadow-emerald-500/20 hover:shadow-xl hover:shadow-emerald-500/30 transition-all duration-300',
			signupBtn:
				'bg-gradient-to-r from-emerald-600 via-green-600 to-teal-700 hover:from-emerald-700 hover:via-green-700 hover:to-teal-800 text-white shadow-lg shadow-emerald-500/30 hover:shadow-xl hover:shadow-emerald-500/40 focus:ring-4 focus:ring-emerald-500/30 transform hover:scale-[1.02] hover:-translate-y-0.5 transition-all duration-300'
		},
		rentals: {
			logoAccent: 'from-teal-500 via-cyan-500 to-blue-600',
			navbarGradient: 'bg-gradient-to-r from-teal-500/10 via-cyan-500/10 to-blue-600/10',
			navActive:
				'bg-gradient-to-r from-teal-500 to-blue-600 bg-clip-text text-transparent border-b-2 border-gradient-to-r border-teal-500',
			navHover:
				'hover:bg-gradient-to-r hover:from-teal-50 hover:via-cyan-50 hover:to-blue-50 dark:hover:from-teal-900/20 dark:hover:via-cyan-900/20 dark:hover:to-blue-900/20',
			loginBtn:
				'border-2 border-gradient-to-r from-teal-400 to-blue-500 hover:bg-gradient-to-r hover:from-teal-50 hover:to-blue-50 text-gradient-to-r from-teal-600 to-blue-700 focus:ring-4 focus:ring-teal-500/30 shadow-lg shadow-teal-500/20 hover:shadow-xl hover:shadow-teal-500/30 transition-all duration-300',
			signupBtn:
				'bg-gradient-to-r from-teal-600 via-cyan-600 to-blue-700 hover:from-teal-700 hover:via-cyan-700 hover:to-blue-800 text-white shadow-lg shadow-teal-500/30 hover:shadow-xl hover:shadow-teal-500/40 focus:ring-4 focus:ring-teal-500/30 transform hover:scale-[1.02] hover:-translate-y-0.5 transition-all duration-300'
		},
		auctions: {
			logoAccent: 'from-orange-500 via-red-500 to-pink-600',
			navbarGradient: 'bg-gradient-to-r from-orange-500/10 via-red-500/10 to-pink-600/10',
			navActive:
				'bg-gradient-to-r from-orange-500 to-pink-600 bg-clip-text text-transparent border-b-2 border-gradient-to-r border-orange-500',
			navHover:
				'hover:bg-gradient-to-r hover:from-orange-50 hover:via-red-50 hover:to-pink-50 dark:hover:from-orange-900/20 dark:hover:via-red-900/20 dark:hover:to-pink-900/20',
			loginBtn:
				'border-2 border-gradient-to-r from-orange-400 to-pink-500 hover:bg-gradient-to-r hover:from-orange-50 hover:to-pink-50 text-gradient-to-r from-orange-600 to-pink-700 focus:ring-4 focus:ring-orange-500/30 shadow-lg shadow-orange-500/20 hover:shadow-xl hover:shadow-orange-500/30 transition-all duration-300',
			signupBtn:
				'bg-gradient-to-r from-orange-600 via-red-600 to-pink-700 hover:from-orange-700 hover:via-red-700 hover:to-pink-800 text-white shadow-lg shadow-orange-500/30 hover:shadow-xl hover:shadow-orange-500/40 focus:ring-4 focus:ring-orange-500/30 transform hover:scale-[1.02] hover:-translate-y-0.5 transition-all duration-300'
		},
		dashboard: {
			logoAccent: 'from-purple-500 via-violet-500 to-indigo-600',
			navbarGradient: 'bg-gradient-to-r from-purple-500/10 via-violet-500/10 to-indigo-600/10',
			navActive:
				'bg-gradient-to-r from-purple-500 to-indigo-600 bg-clip-text text-transparent border-b-2 border-gradient-to-r border-purple-500',
			navHover:
				'hover:bg-gradient-to-r hover:from-purple-50 hover:via-violet-50 hover:to-indigo-50 dark:hover:from-purple-900/20 dark:hover:via-violet-900/20 dark:hover:to-indigo-900/20',
			loginBtn:
				'border-2 border-gradient-to-r from-purple-400 to-indigo-500 hover:bg-gradient-to-r hover:from-purple-50 hover:to-indigo-50 text-gradient-to-r from-purple-600 to-indigo-700 focus:ring-4 focus:ring-purple-500/30 shadow-lg shadow-purple-500/20 hover:shadow-xl hover:shadow-purple-500/30 transition-all duration-300',
			signupBtn:
				'bg-gradient-to-r from-purple-600 via-violet-600 to-indigo-700 hover:from-purple-700 hover:via-violet-700 hover:to-indigo-800 text-white shadow-lg shadow-purple-500/30 hover:shadow-xl hover:shadow-purple-500/40 focus:ring-4 focus:ring-purple-500/30 transform hover:scale-[1.02] hover:-translate-y-0.5 transition-all duration-300'
		},
		messages: {
			logoAccent: 'from-indigo-500 via-blue-500 to-purple-600',
			navbarGradient: 'bg-gradient-to-r from-indigo-500/10 via-blue-500/10 to-purple-600/10',
			navActive:
				'bg-gradient-to-r from-indigo-500 to-purple-600 bg-clip-text text-transparent border-b-2 border-gradient-to-r border-indigo-500',
			navHover:
				'hover:bg-gradient-to-r hover:from-indigo-50 hover:via-blue-50 hover:to-purple-50 dark:hover:from-indigo-900/20 dark:hover:via-blue-900/20 dark:hover:to-purple-900/20',
			loginBtn:
				'border-2 border-gradient-to-r from-indigo-400 to-purple-500 hover:bg-gradient-to-r hover:from-indigo-50 hover:to-purple-50 text-gradient-to-r from-indigo-600 to-purple-700 focus:ring-4 focus:ring-indigo-500/30 shadow-lg shadow-indigo-500/20 hover:shadow-xl hover:shadow-indigo-500/30 transition-all duration-300',
			signupBtn:
				'bg-gradient-to-r from-indigo-600 via-blue-600 to-purple-700 hover:from-indigo-700 hover:via-blue-700 hover:to-purple-800 text-white shadow-lg shadow-indigo-500/30 hover:shadow-xl hover:shadow-indigo-500/40 focus:ring-4 focus:ring-indigo-500/30 transform hover:scale-[1.02] hover:-translate-y-0.5 transition-all duration-300'
		},
		default: {
			logoAccent: 'from-blue-500 via-cyan-500 to-blue-600',
			navbarGradient: 'bg-gradient-to-r from-blue-500/10 via-cyan-500/10 to-blue-600/10',
			navActive:
				'bg-gradient-to-r from-blue-500 to-cyan-600 bg-clip-text text-transparent border-b-2 border-gradient-to-r border-blue-500',
			navHover:
				'hover:bg-gradient-to-r hover:from-blue-50 hover:via-cyan-50 hover:to-blue-50 dark:hover:from-blue-900/20 dark:hover:via-cyan-900/20 dark:hover:to-blue-900/20',
			loginBtn:
				'border-2 border-gradient-to-r from-blue-400 to-cyan-500 hover:bg-gradient-to-r hover:from-blue-50 hover:to-cyan-50 text-gradient-to-r from-blue-600 to-cyan-700 focus:ring-4 focus:ring-blue-500/30 shadow-lg shadow-blue-500/20 hover:shadow-xl hover:shadow-blue-500/30 transition-all duration-300',
			signupBtn:
				'bg-gradient-to-r from-blue-600 via-cyan-600 to-blue-700 hover:from-blue-700 hover:via-cyan-700 hover:to-blue-800 text-white shadow-lg shadow-blue-500/30 hover:shadow-xl hover:shadow-blue-500/40 focus:ring-4 focus:ring-blue-500/30 transform hover:scale-[1.02] hover:-translate-y-0.5 transition-all duration-300'
		}
	};

	$: currentStyles = sectionStyles[activeSection] || sectionStyles.default;

	// Check if user can access dashboard
	$: canAccessDashboard = $user && $user.is_verified;
</script>

<svelte:window bind:scrollY on:scroll={handleScroll} />

<nav
	class={`fixed z-30 w-full transition-all duration-500 ${
		navbarSolid
			? `border-b border-gray-200/30 bg-white/85 shadow-xl backdrop-blur-xl dark:border-gray-700/30 dark:bg-gray-900/85 ${currentStyles.navbarGradient}`
			: `bg-gradient-to-r from-transparent via-white/5 to-transparent dark:via-gray-900/5 ${currentStyles.navbarGradient}`
	} ${isNavbarVisible ? 'translate-y-0 transform' : '-translate-y-full transform'}`}
>
	<div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
		<div class="flex h-16 justify-between">
			<!-- Logo area -->
			<div class="flex lg:gap-x-12">
				<div class="flex flex-shrink-0 items-center">
					<a href="/" class="group relative flex items-center space-x-3">
						<!-- Logo Image -->
						<div class="relative">
							<img
								src="/logo.png"
								alt="Real Estate Platform"
								class="h-10 w-auto transition-all duration-300 group-hover:scale-105"
							/>
							<!-- Enhanced gradient overlay with shimmer effect -->
							<div
								class={`absolute inset-0 bg-gradient-to-r ${currentStyles.logoAccent} rounded-xl opacity-0 blur-sm transition-all duration-500 group-hover:opacity-25 group-hover:blur-none`}
							></div>
							<!-- Shimmer animation -->
							<div
								class="pointer-events-none absolute inset-0 -translate-x-full -skew-x-12 transform rounded-xl bg-gradient-to-r from-transparent via-white/20 to-transparent transition-transform duration-1000 group-hover:translate-x-full"
							></div>
						</div>

						<!-- Enhanced animated underline with glow effect -->
						<span
							class={`absolute bottom-0 left-0 h-1 w-0 bg-gradient-to-r ${currentStyles.logoAccent} rounded-full opacity-80 shadow-lg transition-all duration-500 group-hover:w-full group-hover:shadow-xl`}
						></span>
						<!-- Pulsing glow effect -->
						<span
							class={`absolute bottom-0 left-0 h-1 w-0 bg-gradient-to-r ${currentStyles.logoAccent} animate-pulse-soft rounded-full opacity-40 blur-sm transition-all duration-500 group-hover:w-full`}
						></span>
					</a>
				</div>

				<!-- Desktop links with fixed spacing -->
				<div class="hidden lg:flex lg:space-x-8">
					<slot name="nav-links">
						<a
							href="/"
							class={`group relative inline-flex items-center rounded-lg px-3 py-2 text-sm font-medium transition-all duration-300 focus:outline-none focus-visible:ring-3 focus-visible:ring-blue-500/70 focus-visible:ring-offset-2 focus-visible:text-gray-900 dark:focus-visible:text-white focus:ring-3 focus:ring-blue-500/70 focus:ring-offset-2 focus:text-gray-900 dark:focus:text-white ${
								$page.url.pathname === '/'
									? `${currentStyles.navActive} animate-pulse-soft scale-105 transform font-bold shadow-lg text-gray-900 dark:text-white`
									: `text-gray-700 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white ${currentStyles.navHover} transform hover:-translate-y-0.5 hover:scale-105 font-semibold`
							}`}
						>
							<!-- Gradient background for active state -->
							{#if $page.url.pathname === '/'}
								<div
									class={`absolute inset-0 bg-gradient-to-r ${currentStyles.logoAccent} rounded-lg opacity-10`}
								></div>
							{/if}
							<span class="relative z-10">{$t('nav.home')}</span>
						</a>

						<a
							href="/properties"
							class={`group relative inline-flex items-center rounded-lg px-3 py-2 text-sm font-medium transition-all duration-300 focus:outline-none focus-visible:ring-3 focus-visible:ring-emerald-500/70 focus-visible:ring-offset-2 focus-visible:text-gray-900 dark:focus-visible:text-white focus:ring-3 focus:ring-emerald-500/70 focus:ring-offset-2 focus:text-gray-900 dark:focus:text-white ${
								$page.url.pathname.startsWith('/properties') &&
								!$page.url.pathname.startsWith('/property-management')
									? 'animate-pulse-soft scale-105 transform bg-gradient-to-r from-emerald-500 to-teal-600 bg-clip-text font-bold text-transparent shadow-lg'
									: 'transform text-gray-700 hover:text-gray-900 hover:-translate-y-0.5 hover:scale-105 hover:bg-gradient-to-r hover:from-emerald-50 hover:via-green-50 hover:to-teal-50 dark:text-gray-300 dark:hover:text-white dark:hover:from-emerald-900/20 dark:hover:via-green-900/20 dark:hover:to-teal-900/20 font-semibold'
							}`}
						>
							<!-- Gradient background for active state -->
							{#if $page.url.pathname.startsWith('/properties') && !$page.url.pathname.startsWith('/property-management')}
								<div
									class="absolute inset-0 rounded-lg bg-gradient-to-r from-emerald-500/10 via-green-500/10 to-teal-600/10"
								></div>
							{/if}
							<span class="relative z-10">{$t('nav.properties')}</span>
						</a>

						<a
							href="/property-management"
							class={`group relative inline-flex items-center rounded-lg px-3 py-2 text-sm font-medium transition-all duration-300 focus:outline-none focus-visible:ring-3 focus-visible:ring-teal-500/70 focus-visible:ring-offset-2 focus-visible:text-gray-900 dark:focus-visible:text-white focus:ring-3 focus:ring-teal-500/70 focus:ring-offset-2 focus:text-gray-900 dark:focus:text-white ${
								$page.url.pathname.startsWith('/property-management')
									? 'animate-pulse-soft scale-105 transform bg-gradient-to-r from-teal-500 to-blue-600 bg-clip-text font-bold text-transparent shadow-lg'
									: 'transform text-gray-700 hover:text-gray-900 hover:-translate-y-0.5 hover:scale-105 hover:bg-gradient-to-r hover:from-teal-50 hover:via-cyan-50 hover:to-blue-50 dark:text-gray-300 dark:hover:text-white dark:hover:from-teal-900/20 dark:hover:via-cyan-900/20 dark:hover:to-blue-900/20 font-semibold'
							}`}
						>
							<!-- Gradient background for active state -->
							{#if $page.url.pathname.startsWith('/property-management')}
								<div
									class="absolute inset-0 rounded-lg bg-gradient-to-r from-teal-500/10 via-cyan-500/10 to-blue-600/10"
								></div>
							{/if}
							<span class="relative z-10">{$t('nav.rentals')}</span>
						</a>

						<a
							href="/auctions"
							class={`group relative inline-flex items-center rounded-lg px-3 py-2 text-sm font-medium transition-all duration-300 focus:outline-none focus-visible:ring-3 focus-visible:ring-orange-500/70 focus-visible:ring-offset-2 focus-visible:text-gray-900 dark:focus-visible:text-white focus:ring-3 focus:ring-orange-500/70 focus:ring-offset-2 focus:text-gray-900 dark:focus:text-white ${
								$page.url.pathname.startsWith('/auctions')
									? 'animate-pulse-soft scale-105 transform bg-gradient-to-r from-orange-500 to-pink-600 bg-clip-text font-bold text-transparent shadow-lg'
									: 'transform text-gray-700 hover:text-gray-900 hover:-translate-y-0.5 hover:scale-105 hover:bg-gradient-to-r hover:from-orange-50 hover:via-red-50 hover:to-pink-50 dark:text-gray-300 dark:hover:text-white dark:hover:from-orange-900/20 dark:hover:via-red-900/20 dark:hover:to-pink-900/20 font-semibold'
							}`}
						>
							<!-- Gradient background for active state -->
							{#if $page.url.pathname.startsWith('/auctions')}
								<div
									class="absolute inset-0 rounded-lg bg-gradient-to-r from-orange-500/10 via-red-500/10 to-pink-600/10"
								></div>
							{/if}
							<span class="relative z-10">{$t('nav.auctions')}</span>
						</a>

						<a
							href="/messages"
							class={`group relative inline-flex items-center rounded-lg px-3 py-2 text-sm font-medium transition-all duration-300 focus:outline-none focus-visible:ring-3 focus-visible:ring-indigo-500/70 focus-visible:ring-offset-2 focus-visible:text-gray-900 dark:focus-visible:text-white focus:ring-3 focus:ring-indigo-500/70 focus:ring-offset-2 focus:text-gray-900 dark:focus:text-white ${
								$page.url.pathname.startsWith('/messages')
									? 'animate-pulse-soft scale-105 transform bg-gradient-to-r from-indigo-500 to-purple-600 bg-clip-text font-bold text-transparent shadow-lg'
									: 'transform text-gray-700 hover:text-gray-900 hover:-translate-y-0.5 hover:scale-105 hover:bg-gradient-to-r hover:from-indigo-50 hover:via-blue-50 hover:to-purple-50 dark:text-gray-300 dark:hover:text-white dark:hover:from-indigo-900/20 dark:hover:via-blue-900/20 dark:hover:to-purple-900/20 font-semibold'
							}`}
						>
							<!-- Gradient background for active state -->
							{#if $page.url.pathname.startsWith('/messages')}
								<div
									class="absolute inset-0 rounded-lg bg-gradient-to-r from-indigo-500/10 via-blue-500/10 to-purple-600/10"
								></div>
							{/if}
							<span class="relative z-10">{$t('nav.messages')}</span>
						</a>
					</slot>
				</div>
			</div>

			<!-- Right side: Theme, Language, Auth -->
			<div class="hidden lg:ml-6 lg:flex lg:items-center lg:space-x-5">
				<div class="opacity-80 transition-opacity duration-300 hover:opacity-100">
					<ThemeToggle />
				</div>
				<div class="opacity-80 transition-opacity duration-300 hover:opacity-100">
					<LanguageSelector />
				</div>

				{#if $user}
					<!-- User is logged in -->
					<div class="group relative">
						<button
							class="flex rounded-full text-sm transition-all duration-300 hover:scale-105 focus:ring-3 focus:ring-blue-500/50 focus:ring-offset-2 focus:outline-none"
							aria-expanded="false"
							aria-haspopup="true"
						>
							<span class="sr-only">Open user menu</span>
							{#if $user.avatar_url}
								<img
									class="h-9 w-9 rounded-full shadow-md ring-2 ring-blue-300/50 dark:ring-blue-700/50"
									src={$user.avatar_url}
									alt={$user.first_name}
								/>
							{:else}
								<div
									class={`h-9 w-9 rounded-full bg-gradient-to-br ${currentStyles.logoAccent} flex items-center justify-center text-sm font-medium text-white shadow-lg`}
								>
									{$user.first_name?.[0] || ''}{$user.last_name?.[0] || ''}
								</div>
							{/if}
						</button>

						<!-- Dropdown menu -->
						<div
							class="ring-opacity-5 pointer-events-none absolute right-0 z-50 mt-2 w-48 origin-top-right scale-95 transform rounded-xl bg-white py-1 opacity-0 shadow-lg ring-1 ring-black transition-all duration-200 ease-in-out group-hover:pointer-events-auto group-hover:scale-100 group-hover:opacity-100 focus:outline-none dark:bg-gray-800"
						>
							<div class="border-b border-gray-200 px-4 py-3 dark:border-gray-700">
								<p class="truncate text-sm font-medium text-gray-700 dark:text-gray-300">
									{$user.first_name}
									{$user.last_name}
								</p>
								<p class="truncate text-xs text-gray-500 dark:text-gray-400">{$user.email}</p>
							</div>

							<a
								href="/profile"
								class="block px-4 py-2 text-sm font-semibold text-gray-800 transition-colors duration-200 hover:bg-gray-100 focus:bg-gray-100 focus:outline-none dark:text-gray-200 dark:hover:bg-gray-700 dark:focus:bg-gray-700"
							>
								{$t('nav.profile')}
							</a>

							{#if canAccessDashboard}
								<a
									href="/dashboard"
									class={`block px-4 py-2 text-sm font-semibold transition-colors duration-200 hover:bg-gray-100 focus:bg-gray-100 focus:outline-none dark:hover:bg-gray-700 dark:focus:bg-gray-700 ${
										$page.url.pathname.startsWith('/dashboard')
											? 'bg-purple-50 text-purple-800 dark:bg-purple-900/20 dark:text-purple-200'
											: 'text-gray-800 dark:text-gray-200'
									}`}
								>
									{$t('nav.dashboard')}
								</a>
							{/if}

							<div class="border-t border-gray-200 dark:border-gray-700"></div>

							<button
								on:click={logout}
								class="block w-full px-4 py-2 text-left text-sm font-semibold text-red-700 transition-colors duration-200 hover:bg-red-50 focus:bg-red-50 focus:outline-none dark:text-red-300 dark:hover:bg-red-900/30 dark:focus:bg-red-900/30"
							>
								{$t('nav.logout')}
							</button>
						</div>
					</div>
				{:else}
					<!-- Enhanced auth buttons with gradient effects -->
					<a
						href="/login"
						class={`group relative overflow-hidden rounded-xl px-6 py-2.5 text-sm font-semibold transition-all duration-300 focus:outline-none focus:ring-3 focus:ring-blue-500/50 focus:ring-offset-2 ${currentStyles.loginBtn}`}
						in:fade={{ duration: 400 }}
					>
						<!-- Shimmer effect -->
						<div
							class="absolute inset-0 -translate-x-full -skew-x-12 transform bg-gradient-to-r from-transparent via-white/10 to-transparent transition-transform duration-1000 group-hover:translate-x-full"
						></div>
						<span class="relative z-10 flex items-center">
							<svg class="mr-2 h-4 w-4 opacity-70" fill="currentColor" viewBox="0 0 20 20">
								<path
									fill-rule="evenodd"
									d="M3 3a1 1 0 011 1v12a1 1 0 11-2 0V4a1 1 0 011-1zm7.707 3.293a1 1 0 010 1.414L9.414 9H17a1 1 0 110 2H9.414l1.293 1.293a1 1 0 01-1.414 1.414l-3-3a1 1 0 010-1.414l3-3a1 1 0 011.414 0z"
									clip-rule="evenodd"
								/>
							</svg>
							{$t('nav.login')}
						</span>
					</a>

					<a
						href="/register"
						class={`group relative overflow-hidden rounded-xl px-6 py-2.5 text-sm font-semibold transition-all duration-300 focus:outline-none focus:ring-3 focus:ring-blue-500/50 focus:ring-offset-2 ${currentStyles.signupBtn}`}
						in:fade={{ duration: 400, delay: 100 }}
					>
						<!-- Shimmer effect -->
						<div
							class="absolute inset-0 -translate-x-full -skew-x-12 transform bg-gradient-to-r from-transparent via-white/10 to-transparent transition-transform duration-1000 group-hover:translate-x-full"
						></div>
						<span class="relative z-10 flex items-center">
							<svg class="mr-2 h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
								<path
									d="M8 9a3 3 0 100-6 3 3 0 000 6zM8 11a6 6 0 016 6H2a6 6 0 016-6zM16 7a1 1 0 10-2 0v1h-1a1 1 0 100 2h1v1a1 1 0 102 0v-1h1a1 1 0 100-2h-1V7z"
								/>
							</svg>
							{$t('nav.register')}
						</span>
					</a>
				{/if}
			</div>

			<!-- Mobile menu toggle -->
			<div class="flex flex-row items-center gap-4 lg:hidden">
				<div class="opacity-80 transition-opacity duration-300 hover:opacity-100">
					<ThemeToggle />
				</div>
				<div class="opacity-80 transition-opacity duration-300 hover:opacity-100">
					<LanguageSelector />
				</div>

				<button
					type="button"
					class="inline-flex items-center justify-center rounded-full p-2 text-gray-500 backdrop-blur-sm transition-all duration-300 hover:bg-gray-100/50 hover:text-gray-600 focus:ring-2 focus:ring-blue-500 focus:outline-none focus:ring-inset dark:text-gray-400 dark:hover:bg-gray-800/50 dark:hover:text-gray-300"
					on:click={toggleMenu}
					aria-label="Toggle navigation menu"
				>
					<span class="sr-only">Open main menu</span>
					<div class="relative flex h-6 w-6 items-center justify-center">
						<span
							class={`absolute block h-0.5 w-5 rounded-full bg-current transition-all duration-300 ease-in-out ${isOpen ? 'rotate-45' : '-translate-y-1.5'}`}
						>
						</span>
						<span
							class={`absolute block h-0.5 w-5 rounded-full bg-current transition-all duration-300 ease-in-out ${isOpen ? 'opacity-0' : 'opacity-100'}`}
						>
						</span>
						<span
							class={`absolute block h-0.5 w-5 rounded-full bg-current transition-all duration-300 ease-in-out ${isOpen ? '-rotate-45' : 'translate-y-1.5'}`}
						>
						</span>
					</div>
				</button>
			</div>
		</div>
	</div>

	<!-- Mobile menu -->
	{#if isOpen}
		<div class="overflow-hidden lg:hidden" transition:slide={{ duration: 400, easing: cubicInOut }}>
			<div
				class="mx-3 mt-2 mb-3 space-y-1 rounded-xl border border-gray-200/50 bg-gray-50/80 p-3 shadow-lg backdrop-blur-lg dark:border-gray-700/50 dark:bg-gray-800/80"
			>
				<slot name="mobile-nav-links">
					<a
						href="/"
						class={`flex items-center rounded-lg py-3 pr-4 pl-3 transition-all duration-300 focus:outline-none focus:ring-3 focus:ring-blue-500/50 focus:ring-offset-2 font-semibold ${
							$page.url.pathname === '/'
								? 'bg-blue-50/50 text-blue-800 dark:bg-blue-900/30 dark:text-blue-200'
								: 'text-gray-800 hover:text-gray-900 hover:bg-gray-100/50 dark:text-gray-200 dark:hover:text-white dark:hover:bg-gray-700/50'
						}`}
						on:click={() => (isOpen = false)}
						in:fly={{ x: -10, duration: 300, delay: 100 }}
					>
						<span
							class={`mr-3 text-lg ${$page.url.pathname === '/' ? 'text-blue-500' : 'text-gray-400'}`}
						>
							<svg
								xmlns="http://www.w3.org/2000/svg"
								class="h-5 w-5"
								viewBox="0 0 20 20"
								fill="currentColor"
							>
								<path
									d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z"
								/>
							</svg>
						</span>
						{$t('nav.home')}
					</a>

					<a
						href="/properties"
						class={`flex items-center rounded-lg py-3 pr-4 pl-3 transition-all duration-300 focus:outline-none focus:ring-3 focus:ring-emerald-500/50 focus:ring-offset-2 font-semibold ${
							$page.url.pathname.startsWith('/properties')
								? 'bg-emerald-50/50 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-200'
								: 'text-gray-800 hover:text-gray-900 hover:bg-gray-100/50 dark:text-gray-200 dark:hover:text-white dark:hover:bg-gray-700/50'
						}`}
						on:click={() => (isOpen = false)}
						in:fly={{ x: -10, duration: 300, delay: 200 }}
					>
						<span
							class={`mr-3 text-lg ${$page.url.pathname.startsWith('/properties') ? 'text-emerald-500' : 'text-gray-400'}`}
						>
							<svg
								xmlns="http://www.w3.org/2000/svg"
								class="h-5 w-5"
								viewBox="0 0 20 20"
								fill="currentColor"
							>
								<path
									d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z"
								/>
							</svg>
						</span>
						{$t('nav.properties')}
					</a>

					<a
						href="/auctions"
						class={`flex items-center rounded-lg py-3 pr-4 pl-3 transition-all duration-300 focus:outline-none focus:ring-3 focus:ring-orange-500/50 focus:ring-offset-2 font-semibold ${
							$page.url.pathname.startsWith('/auctions')
								? 'bg-orange-50/50 text-orange-800 dark:bg-orange-900/30 dark:text-orange-200'
								: 'text-gray-800 hover:text-gray-900 hover:bg-gray-100/50 dark:text-gray-200 dark:hover:text-white dark:hover:bg-gray-700/50'
						}`}
						on:click={() => (isOpen = false)}
						in:fly={{ x: -10, duration: 300, delay: 300 }}
					>
						<span
							class={`mr-3 text-lg ${$page.url.pathname.startsWith('/auctions') ? 'text-orange-500' : 'text-gray-400'}`}
						>
							<svg
								xmlns="http://www.w3.org/2000/svg"
								class="h-5 w-5"
								viewBox="0 0 20 20"
								fill="currentColor"
							>
								<path
									fill-rule="evenodd"
									d="M12 7a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0V8.414l-4.293 4.293a1 1 0 01-1.414 0L8 10.414l-4.293 4.293a1 1 0 01-1.414-1.414l5-5a1 1 0 011.414 0L11 10.586 14.586 7H12z"
									clip-rule="evenodd"
								/>
							</svg>
						</span>
						{$t('nav.auctions')}
					</a>

					<!-- Dashboard Link - Mobile -->
					{#if canAccessDashboard}
						<a
							href="/dashboard"
							class={`flex items-center rounded-lg py-3 pr-4 pl-3 transition-all duration-300 focus:outline-none focus:ring-3 focus:ring-purple-500/50 focus:ring-offset-2 font-semibold ${
								$page.url.pathname.startsWith('/dashboard')
									? 'bg-purple-50/50 text-purple-800 dark:bg-purple-900/30 dark:text-purple-200'
									: 'text-gray-800 hover:text-gray-900 hover:bg-gray-100/50 dark:text-gray-200 dark:hover:text-white dark:hover:bg-gray-700/50'
							}`}
							on:click={() => (isOpen = false)}
							in:fly={{ x: -10, duration: 300, delay: 350 }}
						>
							<span
								class={`mr-3 text-lg ${$page.url.pathname.startsWith('/dashboard') ? 'text-purple-500' : 'text-gray-400'}`}
							>
								<svg
									xmlns="http://www.w3.org/2000/svg"
									class="h-5 w-5"
									viewBox="0 0 20 20"
									fill="currentColor"
								>
									<path
										d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z"
									/>
								</svg>
							</span>
							{$t('nav.dashboard')}
						</a>
					{/if}

					<a
						href="/messages"
						class={`flex items-center rounded-lg py-3 pr-4 pl-3 transition-all duration-300 focus:outline-none focus:ring-3 focus:ring-indigo-500/50 focus:ring-offset-2 font-semibold ${
							$page.url.pathname.startsWith('/messages')
								? 'bg-indigo-50/50 text-indigo-800 dark:bg-indigo-900/30 dark:text-indigo-200'
								: 'text-gray-800 hover:text-gray-900 hover:bg-gray-100/50 dark:text-gray-200 dark:hover:text-white dark:hover:bg-gray-700/50'
						}`}
						on:click={() => (isOpen = false)}
						in:fly={{ x: -10, duration: 300, delay: 400 }}
					>
						<span
							class={`mr-3 text-lg ${$page.url.pathname.startsWith('/messages') ? 'text-indigo-500' : 'text-gray-400'}`}
						>
							<svg
								xmlns="http://www.w3.org/2000/svg"
								class="h-5 w-5"
								viewBox="0 0 20 20"
								fill="currentColor"
							>
								<path
									d="M2 5a2 2 0 012-2h7a2 2 0 012 2v4a2 2 0 01-2 2H9l-3 3v-3H4a2 2 0 01-2-2V5z"
								/>
								<path
									d="M15 7v2a4 4 0 01-4 4H9.828l-1.766 1.767c.28.149.599.233.938.233h2l3 3v-3h2a2 2 0 002-2V9a2 2 0 00-2-2h-1z"
								/>
							</svg>
						</span>
						{$t('nav.messages')}
					</a>
				</slot>
			</div>

			<div
				class="mx-3 mb-3 rounded-xl border-t border-gray-200/50 bg-gray-50/80 p-4 shadow-lg backdrop-blur-lg dark:border-gray-700/50 dark:bg-gray-800/80"
			>
				{#if $user}
					<!-- User is logged in (mobile) -->
					<div class="mb-3 flex items-center">
						<div class="flex-shrink-0">
							{#if $user.avatar_url}
								<img
									class="h-10 w-10 rounded-full shadow-md ring-2 ring-blue-300/50 dark:ring-blue-700/50"
									src={$user.avatar_url}
									alt={$user.first_name}
								/>
							{:else}
								<div
									class={`h-10 w-10 rounded-full bg-gradient-to-br ${currentStyles.logoAccent} flex items-center justify-center font-medium text-white shadow-lg`}
								>
									{$user.first_name?.[0] || ''}{$user.last_name?.[0] || ''}
								</div>
							{/if}
						</div>
						<div class="ml-3">
							<div class="text-base font-medium text-gray-800 dark:text-white">
								{$user.first_name}
								{$user.last_name}
							</div>
							<div class="text-sm font-medium text-gray-500 dark:text-gray-400">{$user.email}</div>
						</div>
					</div>

					<div class="flex flex-col space-y-2">
						<a
							href="/profile"
							class="flex items-center rounded-lg px-4 py-3 text-base font-medium text-blue-700 transition-all duration-300 hover:bg-blue-50/50 focus:ring-2 focus:ring-blue-400 focus:ring-offset-2 focus:outline-none dark:text-blue-300 dark:hover:bg-blue-900/30"
							on:click={() => (isOpen = false)}
							in:fly={{ x: -10, duration: 300, delay: 100 }}
						>
							<span class="mr-3 text-blue-500">
								<svg
									xmlns="http://www.w3.org/2000/svg"
									class="h-5 w-5"
									viewBox="0 0 20 20"
									fill="currentColor"
								>
									<path
										fill-rule="evenodd"
										d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z"
										clip-rule="evenodd"
									/>
								</svg>
							</span>
							{$t('nav.profile')}
						</a>

						<button
							on:click={() => {
								isOpen = false;
								logout();
							}}
							class="flex items-center rounded-lg px-4 py-3 text-base font-medium text-red-700 transition-all duration-300 hover:bg-red-50/50 focus:ring-2 focus:ring-red-400 focus:ring-offset-2 focus:outline-none dark:text-red-300 dark:hover:bg-red-900/30"
							in:fly={{ x: -10, duration: 300, delay: 200 }}
						>
							<span class="mr-3 text-red-500">
								<svg
									xmlns="http://www.w3.org/2000/svg"
									class="h-5 w-5"
									viewBox="0 0 20 20"
									fill="currentColor"
								>
									<path
										fill-rule="evenodd"
										d="M3 3a1 1 0 00-1 1v12a1 1 0 001 1h12a1 1 0 001-1V7.414l-5.707-5.707A1 1 0 009.586 1H3zm9 10.414l-3-3 1.414-1.414L12 8.586l1.586-1.586 1.414 1.414-3 3z"
										clip-rule="evenodd"
									/>
								</svg>
							</span>
							{$t('nav.logout')}
						</button>
					</div>
				{:else}
					<!-- Enhanced mobile auth buttons -->
					<div class="flex flex-col space-y-4">
						<a
							href="/login"
							class={`group relative flex transform items-center justify-center overflow-hidden rounded-xl py-3.5 text-base font-semibold transition-all duration-300 hover:scale-[1.02] focus:outline-none focus:ring-3 focus:ring-blue-500/50 focus:ring-offset-2 ${currentStyles.loginBtn}`}
							on:click={() => (isOpen = false)}
							in:fly={{ y: 20, duration: 300, delay: 100 }}
						>
							<!-- Shimmer effect -->
							<div
								class="absolute inset-0 -translate-x-full -skew-x-12 transform bg-gradient-to-r from-transparent via-white/10 to-transparent transition-transform duration-1000 group-hover:translate-x-full"
							></div>
							<span class="relative z-10 flex items-center">
								<svg class="mr-3 h-5 w-5 opacity-70" fill="currentColor" viewBox="0 0 20 20">
									<path
										fill-rule="evenodd"
										d="M3 3a1 1 0 011 1v12a1 1 0 11-2 0V4a1 1 0 011-1zm7.707 3.293a1 1 0 010 1.414L9.414 9H17a1 1 0 110 2H9.414l1.293 1.293a1 1 0 01-1.414 1.414l-3-3a1 1 0 010-1.414l3-3a1 1 0 011.414 0z"
										clip-rule="evenodd"
									/>
								</svg>
								{$t('nav.login')}
							</span>
						</a>

						<a
							href="/register"
							class={`group relative flex transform items-center justify-center overflow-hidden rounded-xl py-3.5 text-base font-semibold transition-all duration-300 hover:scale-[1.02] focus:outline-none focus:ring-3 focus:ring-emerald-500/50 focus:ring-offset-2 ${currentStyles.signupBtn}`}
							on:click={() => (isOpen = false)}
							in:fly={{ y: 20, duration: 300, delay: 200 }}
						>
							<!-- Shimmer effect -->
							<div
								class="absolute inset-0 -translate-x-full -skew-x-12 transform bg-gradient-to-r from-transparent via-white/10 to-transparent transition-transform duration-1000 group-hover:translate-x-full"
							></div>
							<span class="relative z-10 flex items-center">
								<svg class="mr-3 h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
									<path
										d="M8 9a3 3 0 100-6 3 3 0 000 6zM8 11a6 6 0 016 6H2a6 6 0 016-6zM16 7a1 1 0 10-2 0v1h-1a1 1 0 100 2h1v1a1 1 0 102 0v-1h1a1 1 0 100-2h-1V7z"
									/>
								</svg>
								{$t('nav.register')}
							</span>
						</a>
					</div>
				{/if}
			</div>
		</div>
	{/if}
</nav>

<!-- Spacer for fixed navbar -->
<div class="h-16 transition-all duration-300"></div>

<style>
	/* Enhanced gradient animations */
	@keyframes pulse-soft {
		0%,
		100% {
			opacity: 1;
			transform: scale(1);
		}
		50% {
			opacity: 0.8;
			transform: scale(1.02);
		}
	}

	.animate-pulse-soft {
		animation: pulse-soft 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
	}

	/* Enhanced gradient border animation */
	@keyframes gradient-shift {
		0%,
		100% {
			background-position: 0% 50%;
		}
		50% {
			background-position: 100% 50%;
		}
	}

	/* Shimmer effect */
	@keyframes shimmer {
		0% {
			transform: translateX(-100%) skewX(-12deg);
			opacity: 0;
		}
		50% {
			opacity: 1;
		}
		100% {
			transform: translateX(200%) skewX(-12deg);
			opacity: 0;
		}
	}

	/* Glow pulse animation */
	@keyframes glow-pulse {
		0%,
		100% {
			box-shadow: 0 0 5px currentColor;
			opacity: 0.7;
		}
		50% {
			box-shadow:
				0 0 20px currentColor,
				0 0 30px currentColor;
			opacity: 1;
		}
	}

	/* Enhance logo hover effects */
	.group:hover .logo-shimmer {
		animation: shimmer 1.5s ease-in-out;
	}

	/* Navigation link enhanced hover effects */
	.nav-link-gradient {
		background-size: 200% 200%;
		animation: gradient-shift 3s ease infinite;
	}

	/* Enhanced mobile menu animations */
	.mobile-menu-item {
		transform: translateX(-20px);
		opacity: 0;
	}

	.mobile-menu-item.animate-in {
		animation: slideInLeft 0.3s ease-out forwards;
	}

	@keyframes slideInLeft {
		to {
			transform: translateX(0);
			opacity: 1;
		}
	}

	/* Auth button enhanced effects */
	.auth-button::before {
		content: '';
		position: absolute;
		top: 0;
		left: -100%;
		width: 100%;
		height: 100%;
		background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
		transition: left 0.5s;
	}

	.auth-button:hover::before {
		left: 100%;
	}

	/* Section-based gradient animations */
	.section-home .nav-gradient {
		background: linear-gradient(45deg, #3b82f6, #06b6d4, #8b5cf6);
		background-size: 300% 300%;
		animation: gradient-shift 4s ease infinite;
	}

	.section-properties .nav-gradient {
		background: linear-gradient(45deg, #10b981, #059669, #0d9488);
		background-size: 300% 300%;
		animation: gradient-shift 4s ease infinite;
	}

	.section-auctions .nav-gradient {
		background: linear-gradient(45deg, #f97316, #ef4444, #ec4899);
		background-size: 300% 300%;
		animation: gradient-shift 4s ease infinite;
	}

	.section-dashboard .nav-gradient {
		background: linear-gradient(45deg, #8b5cf6, #7c3aed, #6366f1);
		background-size: 300% 300%;
		animation: gradient-shift 4s ease infinite;
	}

	.section-messages .nav-gradient {
		background: linear-gradient(45deg, #6366f1, #3b82f6, #8b5cf6);
		background-size: 300% 300%;
		animation: gradient-shift 4s ease infinite;
	}

	/* Responsive design enhancements */
	@media (max-width: 768px) {
		.mobile-gradient-bg {
			background: linear-gradient(135deg, rgba(59, 130, 246, 0.05), rgba(139, 92, 246, 0.05));
		}
	}

	/* Dark mode specific animations */
	@media (prefers-color-scheme: dark) {
		.glow-effect {
			filter: brightness(1.2);
		}
	}

	/* Reduced motion support */
	@media (prefers-reduced-motion: reduce) {
		.animate-pulse-soft,
		.nav-link-gradient,
		.logo-shimmer {
			animation: none !important;
		}

		* {
			transition-duration: 0.01ms !important;
		}
	}

	/* Custom gradient text support */
	.gradient-text {
		background: linear-gradient(45deg, var(--gradient-start), var(--gradient-end));
		-webkit-background-clip: text;
		background-clip: text;
		-webkit-text-fill-color: transparent;
		background-size: 200% 200%;
		animation: gradient-shift 3s ease infinite;
	}

	/* Enhanced focus states for accessibility */
	.focus-gradient:focus {
		outline: none;
		box-shadow:
			0 0 0 3px rgba(59, 130, 246, 0.5),
			0 0 0 6px rgba(59, 130, 246, 0.2);
		border-radius: 0.75rem;
	}
</style>
