<!-- src/routes/login/+page.svelte -->
<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { login } from '$lib/api/auth';
	import { t } from '$lib/i18n';
	import { user } from '$lib/stores/user.svelte.js';
	import { page } from '$app/stores';
	import LoginForm from '$lib/components/auth/LoginForm.svelte';

	let loading = false;
	let error = '';
	let initialEmail = '';
	let verifiedMessage = '';

	// Default redirect is home page
	let redirectTo = '/';

	onMount(() => {
		// Get parameters from URL
		const urlParams = new URLSearchParams($page.url.searchParams);

		// Handle redirect parameter
		const redirect = urlParams.get('redirect');
		if (redirect) {
			redirectTo = redirect;
		}

		// Handle email parameter (from verification or reset)
		const emailParam = urlParams.get('email');
		if (emailParam) {
			initialEmail = emailParam;
		}

		// Check if coming from successful verification
		const verified = urlParams.get('verified');
		if (verified === 'true') {
			verifiedMessage = $t('auth.emailVerified');
		}

		// Handle reset success parameter
		const resetSuccess = urlParams.get('resetSuccess');
		if (resetSuccess === 'true') {
			verifiedMessage = $t('auth.passwordResetSuccess');
		}

		// If user is already logged in, go to home page
		if ($user) {
			goto('/');
		}
	});

	async function handleLogin(event) {
		const { email, password, rememberMe } = event.detail;

		try {
			loading = true;
			error = '';
			// Removed console.log for production
			// console.log('Attempting login...');
			const response = await login(email, password);

			// Removed console.log for production
			// console.log('Login successful, checking tokens...');
			// Verify tokens were stored
			const accessToken = localStorage.getItem('accessToken');
			const refreshToken = localStorage.getItem('refreshToken');

			if (!accessToken || !refreshToken) {
				// Removed console.log for production
				// console.error('Tokens not stored after login!');
				throw new Error('Login succeeded but tokens were not stored');
			}

			// Removed console.log for production
			// console.log('Tokens stored successfully, redirecting...');
			if (response) {
				goto(redirectTo);
			}
		} catch (err) {
			// Removed console.log for production
			// console.error('Login error:', err);
			error = (err && err.message) || $t('error.invalidCredentials');
		} finally {
			loading = false;
		}
	}
</script>

<svelte:head>
	<title>{$t('auth.login')} | Real Estate Platform</title>
</svelte:head>

<div class="flex min-h-screen flex-col items-center justify-center px-4 py-12 sm:px-6 lg:px-8">
	<div
		class="w-full max-w-md transform space-y-8 rounded-xl bg-white p-8 shadow-lg transition-all dark:bg-gray-800"
	>
		<div>
			<h2 class="mt-2 text-center text-3xl font-bold tracking-tight text-gray-900 dark:text-white">
				{$t('auth.login')}
			</h2>
			<p class="mt-3 text-center text-sm text-gray-600 dark:text-gray-400">
				{$t('auth.noAccount')}
				<a
					href="/register"
					class="text-primary-600 hover:text-primary-500 dark:text-primary-400 decoration-primary-500/30 hover:decoration-primary-500 font-medium underline decoration-2 transition-colors duration-200"
				>
					{$t('auth.createAccount')}
				</a>
			</p>
		</div>

		{#if error}
			<div
				class="rounded-lg border-l-4 border-red-500 bg-red-50 p-4 dark:border-red-600 dark:bg-red-900/30"
			>
				<div class="flex items-start">
					<div class="flex-shrink-0">
						<svg
							class="h-5 w-5 text-red-500"
							xmlns="http://www.w3.org/2000/svg"
							viewBox="0 0 20 20"
							fill="currentColor"
							aria-hidden="true"
						>
							<path
								fill-rule="evenodd"
								d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
								clip-rule="evenodd"
							/>
						</svg>
					</div>
					<div class="ml-3">
						<h3 class="text-sm font-medium text-red-800 dark:text-red-200">
							{error}
						</h3>
					</div>
				</div>
			</div>
		{/if}

		{#if verifiedMessage}
			<div
				class="rounded-lg border-l-4 border-green-500 bg-green-50 p-4 dark:border-green-600 dark:bg-green-900/30"
			>
				<div class="flex items-start">
					<div class="flex-shrink-0">
						<svg
							class="h-5 w-5 text-green-500"
							xmlns="http://www.w3.org/2000/svg"
							viewBox="0 0 20 20"
							fill="currentColor"
						>
							<path
								fill-rule="evenodd"
								d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
								clip-rule="evenodd"
							/>
						</svg>
					</div>
					<div class="ml-3">
						<h3 class="text-sm font-medium text-green-800 dark:text-green-200">
							{verifiedMessage}
						</h3>
					</div>
				</div>
			</div>
		{/if}

		<LoginForm {loading} {redirectTo} on:submit={handleLogin} />
	</div>
</div>
