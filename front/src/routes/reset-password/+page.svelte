<!-- src/routes/reset-password/+page.svelte -->
<script>
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import { requestPasswordReset } from '$lib/api/auth';
  import { t } from '$lib/i18n';
  import { onMount } from 'svelte';
  import RequestResetForm from '$lib/components/auth/RequestResetForm.svelte';

  let email = '';
  let loading = false;
  let error = '';
  let success = '';

  onMount(() => {
    // Get email from query parameter
    const queryEmail = $page.url.searchParams.get('email');
    if (queryEmail) {
      email = queryEmail;
    }
  });

  async function handleRequestReset(event) {
    const { email: submittedEmail } = event.detail;
    
    try {
      loading = true;
      error = '';
      success = '';
      
      await requestPasswordReset(submittedEmail);
      success = $t('auth.resetLinkSent');
      
      // Immediately redirect to the code verification page with a placeholder code
      // The email is passed as a query parameter
      const placeholderCode = 'verify'; // This will be replaced by the actual code from the email
      goto(`/reset-password/${placeholderCode}?email=${encodeURIComponent(submittedEmail)}`);
    } catch (err) {
      console.error('Password reset request error:', err);
      error = err.message || $t('error.resetRequestFailed');
    } finally {
      loading = false;
    }
  }
</script>

<svelte:head>
  <title>{$t('auth.resetPassword')} | Real Estate Platform</title>
</svelte:head>

<div class="min-h-screen flex flex-col items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-gradient-to-b from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
  <div class="w-full max-w-md space-y-8 bg-white dark:bg-gray-800 p-8 rounded-xl shadow-lg transform transition-all">
    <div>
      <h2 class="mt-2 text-center text-3xl font-bold tracking-tight text-gray-900 dark:text-white">
        {$t('auth.resetPassword')}
      </h2>
      <p class="mt-3 text-center text-sm text-gray-600 dark:text-gray-400">
        {$t('auth.resetInstructions')}
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

    {#if success}
      <div class="rounded-lg bg-green-50 dark:bg-green-900/30 p-4 border-l-4 border-green-500 dark:border-green-600">
        <div class="flex items-start">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-green-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-3">
            <h3 class="text-sm font-medium text-green-800 dark:text-green-200">
              {success}
            </h3>
          </div>
        </div>
      </div>
    {/if}

    <RequestResetForm
      {email}
      {loading}
      {error}
      {success}
      on:submit={handleRequestReset}
    />
  </div>
</div>