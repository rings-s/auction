<!-- src/routes/verify-email/+page.svelte -->
<script>
    import { goto } from '$app/navigation';
    import { page } from '$app/stores';
    import { verifyEmail } from '$lib/api/auth';
    import { t } from '$lib/i18n/i18n';
    import { user } from '$lib/stores/user';
    import { onMount } from 'svelte';
  
    let email = '';
    let verificationCode = '';
    let loading = false;
    let error = '';
  
    onMount(() => {
      // If user is already logged in and verified, redirect to profile
      if ($user && $user.is_verified) {
        goto('/profile');
        return;
      }
  
      // Get email from query parameter
      const queryEmail = $page.url.searchParams.get('email');
      if (queryEmail) {
        email = queryEmail;
      }
  
      // Check if verification code is in URL path
      const pathParts = $page.url.pathname.split('/');
      if (pathParts.length > 2 && pathParts[2]) {
        verificationCode = pathParts[2];
        if (email && verificationCode) {
          // Auto-verify if both email and code are present
          handleVerify();
        }
      }
    });
  
    async function handleVerify() {
      try {
        loading = true;
        error = '';
        
        const response = await verifyEmail(email, verificationCode);
        
        // Successful verification should return tokens and user data
        if (response) {
          goto('/profile');
        }
      } catch (err) {
        console.error('Verification error:', err);
        error = err.message || $t('error.verificationFailed');
      } finally {
        loading = false;
      }
    }
  
    async function handleResendCode() {
      try {
        loading = true;
        error = '';
        
        await fetch('http://localhost:8000/api/accounts/resend-verification/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ email }),
        });
        
        // Show success message
        error = $t('auth.verificationCodeResent');
      } catch (err) {
        console.error('Resend verification error:', err);
        error = err.message || $t('error.resendVerificationFailed');
      } finally {
        loading = false;
      }
    }
  </script>
  
  <svelte:head>
    <title>{$t('auth.verifyEmail')} | Real Estate Platform</title>
  </svelte:head>
  
  <div class="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-gray-50 dark:bg-gray-900">
    <div class="max-w-md w-full space-y-8">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900 dark:text-white">
          {$t('auth.verifyEmail')}
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600 dark:text-gray-400">
          {$t('auth.verifyInstructions')}
        </p>
      </div>
  
      <form class="mt-8 space-y-6" on:submit|preventDefault={handleVerify}>
        {#if error}
          <div class="rounded-md bg-red-50 dark:bg-red-900/30 p-4">
            <div class="flex">
              <div class="flex-shrink-0">
                <svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
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
  
        <div>
          <label for="email" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
            {$t('auth.email')}
          </label>
          <input
            type="email"
            id="email"
            bind:value={email}
            required
            class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
          />
        </div>
  
        <div>
          <label for="verification_code" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
            {$t('auth.verificationCode')}
          </label>
          <input
            type="text"
            id="verification_code"
            bind:value={verificationCode}
            required
            class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
          />
        </div>
  
        <div class="flex flex-col space-y-4">
          <button
            type="submit"
            disabled={loading}
            class="w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {#if loading}
              <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            {/if}
            {$t('auth.verifyAccount')}
          </button>
  
          <button
            type="button"
            on:click={handleResendCode}
            disabled={loading}
            class="w-full flex justify-center py-2 px-4 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {$t('auth.resendCode')}
          </button>
  
          <a href="/login" class="text-center text-sm text-primary-600 hover:text-primary-500 dark:text-primary-400">
            {$t('auth.backToLogin')}
          </a>
        </div>
      </form>
    </div>
  </div>