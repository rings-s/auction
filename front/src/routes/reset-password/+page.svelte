<!-- src/routes/reset-password/+page.svelte -->
<script>
    import { goto } from '$app/navigation';
    import { page } from '$app/stores';
    import { requestPasswordReset } from '$lib/api/auth';
    import { t } from '$lib/i18n/i18n';
    import { onMount } from 'svelte';
  
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
  
    async function handleSubmit() {
      try {
        loading = true;
        error = '';
        success = '';
        
        await requestPasswordReset(email);
        success = $t('auth.resetLinkSent');
        
        // Clear the form after successful submission
        email = '';
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
  
  <div class="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-gray-50 dark:bg-gray-900">
    <div class="max-w-md w-full space-y-8">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900 dark:text-white">
          {$t('auth.resetPassword')}
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600 dark:text-gray-400">
          {$t('auth.resetInstructions')}
        </p>
      </div>
  
      <form class="mt-8 space-y-6" on:submit|preventDefault={handleSubmit}>
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
  
        {#if success}
          <div class="rounded-md bg-green-50 dark:bg-green-900/30 p-4">
            <div class="flex">
              <div class="flex-shrink-0">
                <svg class="h-5 w-5 text-green-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
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
            {$t('auth.sendResetLink')}
          </button>
  
          <a href="/login" class="text-center text-sm text-primary-600 hover:text-primary-500 dark:text-primary-400">
            {$t('auth.backToLogin')}
          </a>
        </div>
      </form>
    </div>
  </div>