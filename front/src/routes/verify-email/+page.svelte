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
  let resendLoading = false;
  let resendSuccess = false;

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
      resendLoading = true;
      error = '';
      resendSuccess = false;
      
      await fetch('http://localhost:8000/api/accounts/resend-verification/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });
      
      // Show success message
      resendSuccess = true;
    } catch (err) {
      console.error('Resend verification error:', err);
      error = err.message || $t('error.resendVerificationFailed');
    } finally {
      resendLoading = false;
    }
  }
</script>

<svelte:head>
  <title>{$t('auth.verifyEmail')} | Real Estate Platform</title>
</svelte:head>

<div class="min-h-screen flex flex-col items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-gradient-to-b from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
  <div class="w-full max-w-md space-y-8 bg-white dark:bg-gray-800 p-8 rounded-xl shadow-lg transform transition-all">
    <div>
      <div class="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-primary-100 dark:bg-primary-900">
        <svg class="h-8 w-8 text-primary-600 dark:text-primary-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
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

    {#if error}
      <div class="rounded-lg bg-red-50 dark:bg-red-900/30 p-4 border-l-4 border-red-500 dark:border-red-600">
        <div class="flex items-start">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-red-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
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

    {#if resendSuccess}
      <div class="rounded-lg bg-green-50 dark:bg-green-900/30 p-4 border-l-4 border-green-500 dark:border-green-600">
        <div class="flex items-start">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-green-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
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

    <form class="mt-6 space-y-5" on:submit|preventDefault={handleVerify}>
      <div>
        <label for="email" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          {$t('auth.email')}
        </label>
        <div class="relative">
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <svg class="h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z" />
              <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z" />
            </svg>
          </div>
          <input
            type="email"
            id="email"
            bind:value={email}
            required
            class="pl-10 appearance-none block w-full px-3 py-3 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-gray-900 dark:text-white dark:bg-gray-700 transition-colors duration-200"
            placeholder="email@example.com"
          />
        </div>
      </div>

      <div>
        <label for="verification_code" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          {$t('auth.verificationCode')}
        </label>
        <div class="relative">
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <svg class="h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-14a3 3 0 00-3 3v2H7a1 1 0 000 2h1v1a1 1 0 01-1 1 1 1 0 100 2h6a1 1 0 100-2H8a1 1 0 01-1-1v-1h3a1 1 0 100-2h-3V7a1 1 0 112 0 1 1 0 102 0 3 3 0 00-3-3z" clip-rule="evenodd" />
            </svg>
          </div>
          <input
            type="text"
            id="verification_code"
            bind:value={verificationCode}
            required
            class="pl-10 appearance-none block w-full px-3 py-3 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-gray-900 dark:text-white dark:bg-gray-700 transition-colors duration-200"
            placeholder="123456"
          />
        </div>
      </div>

      <div class="flex flex-col space-y-4 pt-2">
        <button
          type="submit"
          disabled={loading}
          class="w-full flex justify-center items-center py-3 px-4 border border-transparent text-sm font-medium rounded-lg text-white bg-gradient-to-br from-primary-600 to-primary-700 hover:from-primary-700 hover:to-primary-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl transition-all duration-200 transform hover:-translate-y-0.5"
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
          disabled={resendLoading}
          class="flex justify-center items-center py-3 px-4 border border-gray-300 dark:border-gray-600 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
        >
          {#if resendLoading}
            <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-gray-700 dark:text-gray-300" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          {/if}
          {$t('auth.resendCode')}
        </button>

        <a 
          href="/login" 
          class="text-center text-sm py-2 text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300 font-medium hover:underline transition-colors duration-200"
        >
          {$t('auth.backToLogin')}
        </a>
      </div>
    </form>
  </div>
</div>