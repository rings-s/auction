<!-- src/routes/reset-password/[code]/+page.svelte -->
<script>
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { resetPassword } from '$lib/api/auth';
	import { t } from '$lib/i18n';
	import { onMount } from 'svelte';
	import ResetPasswordCodeForm from '$lib/components/auth/ResetPasswordCodeForm.svelte';

	let email = '';
	let resetCode = '';
	let loading = false;
	let error = '';
	let emailReceived = false;

	onMount(() => {
		// Initialize with empty reset code to avoid issues
		resetCode = '';

		// Get email from query parameter first
		const queryEmail = $page.url.searchParams.get('email');
		if (queryEmail) {
			email = queryEmail;
			emailReceived = true;
		} else {
			// Redirect to reset password page if no email is provided
			goto('/reset-password');
			return;
		}

		// Get code from path parameter after handling email
		if ($page.params.code && $page.params.code !== 'verify') {
			// Only set the code if it's a real code, not our placeholder
			resetCode = $page.params.code;
		}

		// Set focus on the reset code input field after a brief delay
		// only if we're using the placeholder code
		if ($page.params.code === 'verify') {
			setTimeout(() => {
				const resetCodeInput = document.getElementById('reset_code');
				if (resetCodeInput) {
					resetCodeInput.focus();
					// Ensure the input is empty
					resetCodeInput.value = '';
					resetCode = '';
				}
			}, 100);
		}
	});

	async function handleResetPassword(event) {
		const {
			email: submittedEmail,
			resetCode: submittedCode,
			newPassword,
			confirmPassword
		} = event.detail;

		try {
			loading = true;
			error = '';

			// Reset password
			const response = await resetPassword(
				submittedEmail,
				submittedCode,
				newPassword,
				confirmPassword
			);

			// Successful reset should return tokens and user data
			if (response) {
				goto('/login?resetSuccess=true');
			}
		} catch (err) {
			console.error('Password reset error:', err);
			error = err.message || $t('error.resetFailed');
		} finally {
			loading = false;
		}
	}
</script>

<svelte:head>
	<title>{$t('auth.resetPassword')} | Real Estate Platform</title>
</svelte:head>

<div class="flex min-h-screen flex-col items-center justify-center px-4 py-12 sm:px-6 lg:px-8">
	<div
		class="w-full max-w-md transform space-y-8 rounded-xl bg-white p-8 shadow-lg transition-all dark:bg-gray-800"
	>
		<div>
			<h2 class="mt-2 text-center text-3xl font-bold tracking-tight text-gray-900 dark:text-white">
				{$t('auth.resetPassword')}
			</h2>
			<p class="mt-3 text-center text-sm text-gray-600 dark:text-gray-400">
				{$t('auth.enterNewPassword')}
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

		<ResetPasswordCodeForm
			{email}
			{resetCode}
			{loading}
			{emailReceived}
			on:submit={handleResetPassword}
		/>
	</div>
</div>
