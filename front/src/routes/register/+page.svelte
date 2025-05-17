<!-- src/routes/register/+page.svelte -->
<script>
  import { goto } from '$app/navigation';
  import { register } from '$lib/api/auth';
  import { t } from '$lib/i18n/i18n';
  import { onMount } from 'svelte';
  import { user } from '$lib/stores/user';

  let userData = {
    email: '',
    password: '',
    confirm_password: '',
    first_name: '',
    last_name: '',
    phone_number: '',
    date_of_birth: '',
    role: 'user' // Default role
  };

  let loading = false;
  let error = '';
  let success = '';

  onMount(() => {
    if ($user) {
      goto('/profile');
    }
  });

  async function handleSubmit() {
      try {
        loading = true;
        error = '';
        success = '';
  
        // Validation
        if (userData.password !== userData.confirm_password) {
          throw new Error($t('error.passwordMismatch'));
        }
  
        // Debug log
        console.log("Sending registration data:", {...userData, password: "[REDACTED]"});
        
        const result = await register(userData);
        console.log("Registration success:", result);
        
        success = $t('auth.registrationSuccess');
        
        // Redirect to verification page after short delay
        setTimeout(() => {
          goto(`/verify-email?email=${encodeURIComponent(userData.email)}`);
        }, 2000);
        
      } catch (err) {
        console.error('Registration error:', err);
        error = err.message || $t('error.registrationFailed');
      } finally {
        loading = false;
      }
    }
</script>

<svelte:head>
  <title>{$t('auth.register')} | Real Estate Platform</title>
</svelte:head>

<div class="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-gray-50 dark:bg-gray-900">
  <div class="max-w-md w-full space-y-8">
    <div>
      <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900 dark:text-white">
        {$t('auth.register')}
      </h2>
      <p class="mt-2 text-center text-sm text-gray-600 dark:text-gray-400">
        {$t('auth.alreadyAccount')}
        <a href="/login" class="font-medium text-primary-600 hover:text-primary-500 dark:text-primary-400">
          {$t('auth.signIn')}
        </a>
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

      <!-- First name and Last name -->
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div>
          <label for="first_name" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
            {$t('auth.firstName')}
          </label>
          <input
            type="text"
            id="first_name"
            bind:value={userData.first_name}
            required
            class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
          />
        </div>
        <div>
          <label for="last_name" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
            {$t('auth.lastName')}
          </label>
          <input
            type="text"
            id="last_name"
            bind:value={userData.last_name}
            required
            class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
          />
        </div>
      </div>

      <!-- Email -->
      <div>
        <label for="email" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
          {$t('auth.email')}
        </label>
        <input
          type="email"
          id="email"
          bind:value={userData.email}
          required
          class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
        />
      </div>

      <!-- Phone and DOB -->
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div>
          <label for="phone_number" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
            {$t('auth.phoneNumber')}
          </label>
          <input
            type="tel"
            id="phone_number"
            bind:value={userData.phone_number}
            class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
          />
        </div>
        <div>
          <label for="date_of_birth" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
            {$t('auth.dateOfBirth')}
          </label>
          <input
            type="date"
            id="date_of_birth"
            bind:value={userData.date_of_birth}
            class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
          />
        </div>
      </div>
      
      <!-- User Role -->
      <div>
        <label for="role" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
          {$t('auth.userRole')}
        </label>
        <select
          id="role"
          bind:value={userData.role}
          class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
        >
          <option value="user">{$t('auth.roleUser')}</option>
          <option value="owner">{$t('auth.roleOwner')}</option>
          <option value="appraiser">{$t('auth.roleAppraiser')}</option>
          <option value="data_entry">{$t('auth.roleDataEntry')}</option>
        </select>
        <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
          {$t('auth.roleHelp')}
        </p>
      </div>

      <!-- Password -->
      <div>
        <label for="password" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
          {$t('auth.password')}
        </label>
        <input
          type="password"
          id="password"
          bind:value={userData.password}
          required
          minlength="8"
          class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
        />
      </div>

      <!-- Confirm Password -->
      <div>
        <label for="confirm_password" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
          {$t('auth.confirmPassword')}
        </label>
        <input
          type="password"
          id="confirm_password"
          bind:value={userData.confirm_password}
          required
          minlength="8"
          class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
        />
      </div>

      <!-- Submit Button -->
      <div>
        <button
          type="submit"
          disabled={loading}
          class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {#if loading}
            <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          {/if}
          {$t('auth.register')}
        </button>
      </div>
    </form>
  </div>
</div>