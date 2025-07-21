<script>
	import '../app.css';
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { theme } from '$lib/stores/theme';
	import { locale } from '$lib/i18n';
	import { user } from '$lib/stores/user';
	import { fetchUserProfile } from '$lib/api/auth';
	import { goto } from '$app/navigation';
	import { browser } from '$app/environment';

	import Navbar from '$lib/components/layout/Navbar.svelte';
	import Footer from '$lib/components/layout/Footer.svelte';
	import ToastContainer from '$lib/components/ToastContainer.svelte';

	// Reactive variables
	$: currentLocale = $locale;
	$: isArabic = currentLocale === 'ar';
	$: isDashboardPage = $page.url.pathname.startsWith('/dashboard');

	let loading = true;
	let error = null;

	onMount(async () => {
		try {
			// Apply saved theme
			const savedTheme = localStorage.getItem('theme');
			if (savedTheme) {
				theme.set(savedTheme);
			} else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
				theme.set('dark');
			}

			// Apply saved locale
			const savedLocale = localStorage.getItem('locale');
			if (savedLocale) {
				locale.set(savedLocale);
			}

			// Try to fetch user profile if tokens exist
			if (localStorage.getItem('accessToken')) {
				try {
					await fetchUserProfile();
				} catch (error) {
					console.error('Session refresh failed, redirecting to login:', error);
					// This error is thrown from auth.js when token refresh fails.
					// The user's state is already cleared, so we just need to navigate.
					goto('/login');
				}
			}

			loading = false;
		} catch (err) {
			console.error('Layout initialization error:', err);
			error = 'Failed to initialize application';
			loading = false;
		}
	});

	// Apply theme and direction classes to document
	$: if (browser) {
		document.documentElement.classList.remove('light', 'dark', 'rtl', 'ltr');
		document.documentElement.classList.add($locale === 'ar' ? 'rtl' : 'ltr');
		document.documentElement.classList.add($theme);
		document.documentElement.style.colorScheme = $theme;
		document.documentElement.lang = $locale;
		document.documentElement.dir = $locale === 'ar' ? 'rtl' : 'ltr';
		document.body.className = isArabic ? 'font-cairo' : 'font-inter';
	}

	function reloadPage() {
		if (browser) window.location.reload();
	}
</script>

<svelte:head>
	<title>Real Estate Auction Platform</title>
</svelte:head>

<div class="{isDashboardPage ? 'min-h-screen transition-colors duration-200 dark:bg-gray-800' : 'flex min-h-screen flex-col transition-colors duration-200 dark:bg-gray-800'}">
	{#if error}
		<div class="flex min-h-screen items-center justify-center bg-red-50 dark:bg-red-900/20">
			<div class="p-8 text-center">
				<h1 class="mb-4 text-2xl font-bold text-red-600 dark:text-red-400">Layout Error</h1>
				<p class="mb-4 text-gray-600 dark:text-gray-400">
					{error}
				</p>
				<button
					on:click={reloadPage}
					class="rounded bg-red-600 px-4 py-2 text-white transition-colors hover:bg-red-700"
				>
					Reload Page
				</button>
			</div>
		</div>
	{:else if loading}
		<div class="flex min-h-screen items-center justify-center">
			<div
				class="border-primary-500 h-12 w-12 animate-spin rounded-full border-t-2 border-b-2"
			></div>
		</div>
	{:else}
		{#if !isDashboardPage}
			<Navbar />
		{/if}

		<main class="flex-grow {isDashboardPage ? '' : ''}">
			<slot />
		</main>

		{#if !isDashboardPage}
			<Footer />
		{/if}

		<ToastContainer />
	{/if}
</div>
