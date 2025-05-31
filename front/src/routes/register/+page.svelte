<!-- src/routes/register/+page.svelte -->
<script>
  import { goto } from '$app/navigation';
  import { register } from '$lib/api/auth';
  import { t } from '$lib/i18n';
  import { onMount } from 'svelte';
  import { user } from '$lib/stores/user';
  import RegisterForm from '$lib/components/auth/RegisterForm.svelte';

  let loading = false;
  let error = '';
  let success = '';

  onMount(() => {
    if ($user) {
      goto('/profile');
    }
  });

  async function handleRegister(event) {
    const userData = event.detail;
    
    try {
      loading = true;
      error = '';
      success = '';

      // Debug log
      // console.log("Sending registration data:", {...userData, password: "[REDACTED]"});
      
      const result = await register(userData);
      // console.log("Registration success:", result);
      
      success = $t('auth.registrationSuccess');
      
      // Immediately redirect to verification page
      goto(`/verify-email?email=${encodeURIComponent(userData.email)}`);
      
    } catch (err) {
      // console.error('Registration error:', err);
      error = err.message || $t('error.registrationFailed');
    } finally {
      loading = false;
    }
  }
</script>

<svelte:head>
  <title>{$t('auth.register')} | Real Estate Platform</title>
</svelte:head>

<div class="min-h-screen flex flex-col items-center justify-center py-8 px-4 sm:px-6 lg:px-8 ">
  <div class="w-full max-w-lg space-y-6 bg-white dark:bg-gray-800 p-8 rounded-xl shadow-lg transform transition-all">
    <div>
      <h2 class="mt-2 text-center text-3xl font-bold tracking-tight text-gray-900 dark:text-white">
        {$t('auth.register')}
      </h2>
      <p class="mt-3 text-center text-sm text-gray-600 dark:text-gray-400">
        {$t('auth.alreadyAccount')}
        <a href="/login" class="font-medium text-primary-600 hover:text-primary-500 dark:text-primary-400 transition-colors duration-200 underline decoration-2 decoration-primary-500/30 hover:decoration-primary-500">
          {$t('auth.signIn')}
        </a>
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

    <RegisterForm
      {loading}
      on:submit={handleRegister}
    />
  </div>
</div>