<!-- src/routes/verify-email/+page.svelte -->
<script>
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { verifyEmail } from '$lib/api/auth';
	import { API_BASE_URL } from '$lib/constants';
	import { t } from '$lib/i18n';
	import { user } from '$lib/stores/user';
	import { onMount } from 'svelte';
	import VerifyEmailForm from '$lib/components/auth/VerifyEmailForm.svelte';

	let email = '';
	let loading = false;
	let error = '';
	let resendLoading = false;
	let resendSuccess = false;
	let emailReceived = false;

	// Debug flags
	const DEBUG = true; // Set to false in production

	function debugLog(message, data = null) {
		if (DEBUG) {
			// console.log(`[VerifyEmail] ${message}`, data || '');
		}
	}

	// Validate that required functions and constants are available
	onMount(() => {
		// Debug: Check if imports are correct
		debugLog('verifyEmail function available:', typeof verifyEmail === 'function');
		debugLog('API_BASE_URL:', API_BASE_URL);
		debugLog('Page URL:', $page.url.href);

		// Validate imports
		if (typeof verifyEmail !== 'function') {
			// console.error('[VerifyEmail] verifyEmail function is not properly imported');
			error = 'Verification service is not available. Please refresh the page.';
			return;
		}

		if (!API_BASE_URL) {
			// console.error('[VerifyEmail] API_BASE_URL is not defined');
			error = 'Configuration error. Please contact support.';
			return;
		}

		// If user is already logged in and verified, redirect to profile
		if ($user && $user.is_verified) {
			debugLog('User already verified, redirecting to profile');
			goto('/profile');
			return;
		}

		// Get email from query parameter
		const queryEmail = $page.url.searchParams.get('email');
		debugLog('Email from query params:', queryEmail);

		if (queryEmail) {
			// Validate email format
			const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
			if (emailRegex.test(queryEmail)) {
				email = queryEmail;
				emailReceived = true;
				debugLog('Valid email set:', email);
			} else {
				// console.error('[VerifyEmail] Invalid email format in query params:', queryEmail);
				error = 'Invalid email format in URL. Please try again.';
				return;
			}
		} else {
			debugLog('No email in query params, redirecting to login');
			goto('/login');
			return;
		}

		// Check if verification code is in URL path
		const pathParts = $page.url.pathname.split('/');
		debugLog('URL path parts:', pathParts);

		if (pathParts.length > 2 && pathParts[2]) {
			const codeFromUrl = pathParts[2];
			debugLog('Verification code found in URL:', codeFromUrl);

			// Validate verification code format (6 digits)
			if (/^\d{6}$/.test(codeFromUrl)) {
				// Auto-submit verification if we have a valid code in URL
				debugLog('Auto-verifying with code from URL');
				handleVerify({ detail: { email, verificationCode: codeFromUrl } });
			} else {
				debugLog('Invalid verification code format in URL:', codeFromUrl);
			}
		}
	});

	async function handleVerify(event) {
		// FIXED: Changed variable name to avoid conflict with the imported function
		const { email: submittedEmail, verificationCode } = event.detail;

		debugLog('handleVerify called with:', {
			email: submittedEmail,
			codeLength: verificationCode?.length
		});

		// Input validation
		if (!submittedEmail || !verificationCode) {
			error = 'Email and verification code are required.';
			debugLog('Validation failed: missing email or code');
			return;
		}

		// Validate email format
		const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
		if (!emailRegex.test(submittedEmail)) {
			error = 'Please enter a valid email address.';
			debugLog('Validation failed: invalid email format');
			return;
		}

		// Validate verification code format (6 digits)
		if (!/^\d{6}$/.test(verificationCode)) {
			error = 'Verification code must be 6 digits.';
			debugLog('Validation failed: invalid code format');
			return;
		}

		try {
			loading = true;
			error = '';

			debugLog('Calling verifyEmail API...');

			// FIXED: Now verifyEmail correctly refers to the imported function
			const response = await verifyEmail(submittedEmail, verificationCode);

			debugLog('Verification API response:', response ? 'Success' : 'Failed');

			// Successful verification should redirect to login with verified email
			if (response) {
				debugLog('Verification successful, redirecting to login');
				const redirectUrl = `/login?email=${encodeURIComponent(submittedEmail)}&verified=true`;
				debugLog('Redirect URL:', redirectUrl);
				goto(redirectUrl);
			} else {
				throw new Error('Verification failed - no response data');
			}
		} catch (err) {
			// console.error('[VerifyEmail] Verification error:', err);

			// Handle specific error types
			if (err.message?.includes('expired')) {
				error = 'Verification code has expired. Please request a new one.';
			} else if (err.message?.includes('invalid')) {
				error = 'Invalid verification code. Please check and try again.';
			} else if (err.message?.includes('network') || err.message?.includes('fetch')) {
				error = 'Network error. Please check your connection and try again.';
			} else {
				error = err.message || $t('error.verificationFailed');
			}

			debugLog('Error details:', { message: err.message, stack: err.stack });
		} finally {
			loading = false;
			debugLog('Verification attempt completed');
		}
	}

	async function handleResendCode(event) {
		// FIXED: Variable naming is correct here
		const { email: resendEmail } = event.detail;

		debugLog('handleResendCode called for:', resendEmail);

		// Input validation
		if (!resendEmail) {
			error = 'Email is required for resending verification code.';
			debugLog('Resend validation failed: missing email');
			return;
		}

		// Validate email format
		const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
		if (!emailRegex.test(resendEmail)) {
			error = 'Please enter a valid email address.';
			debugLog('Resend validation failed: invalid email format');
			return;
		}

		try {
			resendLoading = true;
			error = '';
			resendSuccess = false;

			debugLog('Sending resend verification request...');

			// FIXED: Using API_BASE_URL constant instead of hardcoded URL
			const response = await fetch(`${API_BASE_URL}/accounts/resend-verification/`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					Accept: 'application/json'
				},
				body: JSON.stringify({ email: resendEmail })
			});

			debugLog('Resend API response status:', response.status);

			if (!response.ok) {
				const errorData = await response.json().catch(() => ({}));
				debugLog('Resend API error data:', errorData);

				throw new Error(
					errorData.error?.message ||
						errorData.message ||
						`Server error: ${response.status} ${response.statusText}`
				);
			}

			const data = await response.json();
			debugLog('Resend API success data:', data);

			// Show success message
			resendSuccess = true;
			debugLog('Verification code resent successfully');

			// Clear success message after 5 seconds
			setTimeout(() => {
				resendSuccess = false;
			}, 5000);
		} catch (err) {
			console.error('[VerifyEmail] Resend verification error:', err);

			// Handle specific error types
			if (err.message?.includes('rate') || err.message?.includes('limit')) {
				error = 'Too many requests. Please wait a few minutes before trying again.';
			} else if (err.message?.includes('not found') || err.message?.includes('404')) {
				error = 'User not found. Please check your email address.';
			} else if (err.message?.includes('network') || err.message?.includes('fetch')) {
				error = 'Network error. Please check your connection and try again.';
			} else {
				error = err.message || $t('error.resendVerificationFailed');
			}

			debugLog('Resend error details:', { message: err.message, stack: err.stack });
		} finally {
			resendLoading = false;
			debugLog('Resend attempt completed');
		}
	}
</script>

<svelte:head>
	<title>{$t('auth.verifyEmail')} | Real Estate Platform</title>
	<meta name="description" content="Verify your email address to complete registration" />
</svelte:head>

<div class="flex min-h-screen flex-col items-center justify-center px-4 py-12 sm:px-6 lg:px-8">
	<div
		class="w-full max-w-md transform space-y-8 rounded-xl bg-white p-8 shadow-lg transition-all dark:bg-gray-800"
	>
		<div>
			<div
				class="bg-primary-100 dark:bg-primary-900 mx-auto flex h-16 w-16 items-center justify-center rounded-full"
			>
				<svg
					class="text-primary-600 dark:text-primary-400 h-8 w-8"
					xmlns="http://www.w3.org/2000/svg"
					viewBox="0 0 20 20"
					fill="currentColor"
					aria-hidden="true"
				>
					<path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z" />
					<path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z" />
				</svg>
			</div>
			<h2 class="mt-4 text-center text-3xl font-bold tracking-tight text-gray-900 dark:text-white">
				{$t('auth.verifyEmail')}
			</h2>
			<p class="mt-3 text-center text-sm text-gray-600 dark:text-gray-400">
				{$t('auth.verifyInstructions')}
			</p>
		</div>

		<!-- Error Alert -->
		{#if error}
			<div
				class="rounded-lg border-l-4 border-red-500 bg-red-50 p-4 dark:border-red-600 dark:bg-red-900/30"
				role="alert"
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

		<!-- Success Alert -->
		{#if resendSuccess}
			<div
				class="rounded-lg border-l-4 border-green-500 bg-green-50 p-4 dark:border-green-600 dark:bg-green-900/30"
				role="alert"
			>
				<div class="flex items-start">
					<div class="flex-shrink-0">
						<svg
							class="h-5 w-5 text-green-500"
							xmlns="http://www.w3.org/2000/svg"
							viewBox="0 0 20 20"
							fill="currentColor"
							aria-hidden="true"
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
							{$t('auth.verificationCodeResent')}
						</h3>
					</div>
				</div>
			</div>
		{/if}

		<!-- Verification Form -->
		<div class="mt-6">
			<VerifyEmailForm {email} {loading} on:submit={handleVerify} on:resend={handleResendCode} />

			<!-- Back to Login Link -->
			<div class="mt-4 text-center">
				<a
					href="/login"
					class="text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300 py-2 text-sm font-medium transition-colors duration-200 hover:underline"
				>
					{$t('auth.backToLogin')}
				</a>
			</div>
		</div>

		<!-- Debug Information (only shown in development) -->
		{#if DEBUG}
			<details class="mt-4 text-xs text-gray-500 dark:text-gray-400">
				<summary class="cursor-pointer hover:text-gray-700 dark:hover:text-gray-300"
					>Debug Info</summary
				>
				<div class="mt-2 rounded bg-gray-50 p-3 dark:bg-gray-700">
					<p><strong>Email:</strong> {email || 'Not set'}</p>
					<p><strong>Email Received:</strong> {emailReceived}</p>
					<p><strong>Loading:</strong> {loading}</p>
					<p><strong>Resend Loading:</strong> {resendLoading}</p>
					<p><strong>API URL:</strong> {API_BASE_URL}</p>
					<p><strong>Current URL:</strong> {$page.url.href}</p>
					<p><strong>verifyEmail type:</strong> {typeof verifyEmail}</p>
				</div>
			</details>
		{/if}
	</div>
</div>
