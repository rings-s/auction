<!-- src/routes/verify-email/+page.svelte -->
<script>
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import { verifyEmail } from '$lib/api/auth';
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
  let autoVerify = false;

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
      emailReceived = true;
    } else {
      // Redirect to login if no email is provided
      goto('/login');
      return;
    }

    // Check if verification code is in URL path
    const pathParts = $page.url.pathname.split('/');
    if (pathParts.length > 2 && pathParts[2]) {
      // Set autoVerify to true to indicate we should automatically submit
      // when component is mounted
      autoVerify = true;
    }
  });

  async function handleVerify(event) {
    const { email: verifyEmail, verificationCode } = event.detail;
    
    try {
      loading = true;
      error = '';
      
      const response = await verifyEmail(verifyEmail, verificationCode);
      
      // Successful verification should redirect to login with verified email
      if (response) {
        goto(`/login?email=${encodeURIComponent(verifyEmail)}&verified=true`);
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

<div class="min-h-screen flex flex-col items-center justify-center py-12 px-4 sm:px-6 lg:px-8 ">
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

    <div class="mt-6">      
      <VerifyEmailForm
        {email}
        {loading}
        {autoVerify}
        on:submit={handleVerify}
        on:resend={handleResendCode}
      />

      <div class="mt-4 text-center">
        <a 
          href="/login" 
          class="text-sm py-2 text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300 font-medium hover:underline transition-colors duration-200"
        >
          {$t('auth.backToLogin')}
        </a>
      </div>
    </div>
  </div>
</div>