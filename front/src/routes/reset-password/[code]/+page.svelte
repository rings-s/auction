<!-- src/routes/reset-password/[code]/+page.svelte -->
<script>
    import { goto } from '$app/navigation';
    import { page } from '$app/stores';
    import { resetPassword } from '$lib/api/auth';
    import { t } from '$lib/i18n/i18n';
    import { onMount } from 'svelte';
  
    let email = '';
    let resetCode = '';
    let newPassword = '';
    let confirmPassword = '';
    let loading = false;
    let error = '';
  
    onMount(() => {
      // Get code from path parameter
      if ($page.params.code) {
        resetCode = $page.params.code;
      }
      
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
        
        // Validate passwords
        if (newPassword !== confirmPassword) {
          throw new Error($t('error.passwordMismatch'));
        }
        
        // Reset password
        const response = await resetPassword(email, resetCode, newPassword, confirmPassword);
        
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
  
  <div class="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-gray-50 dark:bg-gray-900">
    <div class="max-w-md w-full space-y-8">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900 dark:text-white">
          {$t('auth.resetPassword')}
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600 dark:text-gray-400">
          {$t('auth.enterNewPassword')}
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
          <label for="reset_code" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
            {$t('auth.resetCode')}
          </label>
          <input
            type="text"
            id="reset_code"
            bind:value={resetCode}
            required
            class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
          />
        </div>
  
        <div>
          <label for="new_password" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
            {$t('auth.newPassword')}
          </label>
          <input
            type="password"
            id="new_password"
            bind:value={newPassword}
            required
            minlength="8"
            class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
          />
        </div>
  
        <div>
          <label for="confirm_password" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
            {$t('auth.confirmPassword')}
          </label>
          <input
            type="password"
            id="confirm_password"
            bind:value={confirmPassword}
            required
            minlength="8"
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
            {$t('auth.resetPassword')}
          </button>
  
          <a href="/login" class="text-center text-sm text-primary-600 hover:text-primary-500 dark:text-primary-400">
            {$t('auth.backToLogin')}
          </a>
        </div>
      </form>
    </div>
  </div>