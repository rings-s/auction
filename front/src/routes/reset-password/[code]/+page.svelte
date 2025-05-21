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

<div class="min-h-screen flex flex-col items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-gradient-to-b from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
  <div class="w-full max-w-md space-y-8 bg-white dark:bg-gray-800 p-8 rounded-xl shadow-lg transform transition-all">
    <div>
      <h2 class="mt-2 text-center text-3xl font-bold tracking-tight text-gray-900 dark:text-white">
        {$t('auth.resetPassword')}
      </h2>
      <p class="mt-3 text-center text-sm text-gray-600 dark:text-gray-400">
        {$t('auth.enterNewPassword')}
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

    <form class="mt-6 space-y-5" on:submit|preventDefault={handleSubmit}>
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
        <label for="reset_code" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          {$t('auth.resetCode')}
        </label>
        <div class="relative">
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <svg class="h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd" />
            </svg>
          </div>
          <input
            type="text"
            id="reset_code"
            bind:value={resetCode}
            required
            class="pl-10 appearance-none block w-full px-3 py-3 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-gray-900 dark:text-white dark:bg-gray-700 transition-colors duration-200"
            placeholder="123456"
          />
        </div>
      </div>

      <div>
        <label for="new_password" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          {$t('auth.newPassword')}
        </label>
        <div class="relative">
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <svg class="h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd" />
            </svg>
          </div>
          <input
            type="password"
            id="new_password"
            bind:value={newPassword}
            required
            minlength="8"
            class="pl-10 appearance-none block w-full px-3 py-3 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-gray-900 dark:text-white dark:bg-gray-700 transition-colors duration-200"
            placeholder="********"
          />
        </div>
      </div>

      <div>
        <label for="confirm_password" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          {$t('auth.confirmPassword')}
        </label>
        <div class="relative">
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <svg class="h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd" />
            </svg>
          </div>
          <input
            type="password"
            id="confirm_password"
            bind:value={confirmPassword}
            required
            minlength="8"
            class="pl-10 appearance-none block w-full px-3 py-3 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-gray-900 dark:text-white dark:bg-gray-700 transition-colors duration-200"
            placeholder="********"
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
          {$t('auth.resetPassword')}
        </button>

        <a 
          href="/login" 
          class="text-center text-sm py-2 px-4 border border-gray-300 dark:border-gray-600 rounded-lg font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-200"
        >
          {$t('auth.backToLogin')}
        </a>
      </div>
    </form>
  </div>
</div>