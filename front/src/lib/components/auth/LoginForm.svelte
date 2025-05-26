<script>
    import { createEventDispatcher } from 'svelte';
    import { t } from '../../../../../i18n';
    import { fly, fade } from 'svelte/transition';
    import { toast } from '$lib/stores/toastStore';
    
    export let loading = false;
    export let redirectTo = '/';
    
    const dispatch = createEventDispatcher();
    
    let email = '';
    let password = '';
    let rememberMe = false;
    let showPassword = false;
    let emailError = '';
    let passwordError = '';
    let emailTouched = false;
    let passwordTouched = false;
    
    // Real-time validation
    $: if (emailTouched) emailError = validateEmail(email);
    $: if (passwordTouched) passwordError = validatePassword(password);
    $: isValid = email && password && !emailError && !passwordError;
    
    function validateEmail(value) {
      if (!value) return $t('auth.validation.emailRequired');
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(value)) return $t('auth.validation.emailInvalid');
      return '';
    }
    
    function validatePassword(value) {
      if (!value) return $t('auth.validation.passwordRequired');
      if (value.length < 8) return $t('auth.validation.passwordMinLength');
      return '';
    }
    
    async function handleSubmit() {
      emailTouched = true;
      passwordTouched = true;
      
      if (!isValid) {
        toast.error($t('error.invalidCredentials'));
        return;
      }
      
      dispatch('submit', { email, password, rememberMe });
    }
    
    function handleKeydown(e) {
      if (e.key === 'Enter' && isValid && !loading) {
        handleSubmit();
      }
    }
  </script>
  
  <form on:submit|preventDefault={handleSubmit} class="space-y-6" on:keydown={handleKeydown}>
    <!-- Email Field -->
    <div class="space-y-1">
      <label for="email" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
        {$t('auth.email')}
      </label>
      <div class="relative">
        <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <svg class="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
        </div>
        <input
          id="email"
          type="email"
          bind:value={email}
          on:blur={() => emailTouched = true}
          autocomplete="email"
          required
          class="
            appearance-none block w-full pl-10 pr-3 py-3
            border {emailError && emailTouched ? 'border-red-300 dark:border-red-600' : 'border-gray-300 dark:border-gray-600'}
            rounded-lg shadow-sm placeholder-gray-400 dark:placeholder-gray-500
            focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500
            {emailError && emailTouched ? 'text-red-900 dark:text-red-300' : 'text-gray-900 dark:text-white'}
            bg-white dark:bg-gray-800
            transition-all duration-200
          "
          placeholder={$t('auth.email')}
        />
        {#if emailError && emailTouched}
          <div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
            <svg class="h-5 w-5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
            </svg>
          </div>
        {/if}
      </div>
      {#if emailError && emailTouched}
        <p class="mt-1 text-sm text-red-600 dark:text-red-400" in:fly={{ y: -5, duration: 200 }}>
          {emailError}
        </p>
      {/if}
    </div>
  
    <!-- Password Field -->
    <div class="space-y-1">
      <label for="password" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
        {$t('auth.password')}
      </label>
      <div class="relative">
        <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <svg class="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
        </div>
        <input
          id="password"
          type={showPassword ? 'text' : 'password'}
          bind:value={password}
          on:blur={() => passwordTouched = true}
          autocomplete="current-password"
          required
          class="
            appearance-none block w-full pl-10 pr-10 py-3
            border {passwordError && passwordTouched ? 'border-red-300 dark:border-red-600' : 'border-gray-300 dark:border-gray-600'}
            rounded-lg shadow-sm placeholder-gray-400 dark:placeholder-gray-500
            focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500
            {passwordError && passwordTouched ? 'text-red-900 dark:text-red-300' : 'text-gray-900 dark:text-white'}
            bg-white dark:bg-gray-800
            transition-all duration-200
          "
          placeholder={$t('auth.password')}
        />
        <button
          type="button"
          on:click={() => showPassword = !showPassword}
          class="absolute inset-y-0 right-0 pr-3 flex items-center"
        >
          {#if showPassword}
            <svg class="h-5 w-5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
            </svg>
          {:else}
            <svg class="h-5 w-5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
          {/if}
        </button>
      </div>
      {#if passwordError && passwordTouched}
        <p class="mt-1 text-sm text-red-600 dark:text-red-400" in:fly={{ y: -5, duration: 200 }}>
          {passwordError}
        </p>
      {/if}
    </div>
  
    <!-- Remember Me & Forgot Password -->
    <div class="flex items-center justify-between">
      <div class="flex items-center">
        <input
          id="remember-me"
          type="checkbox"
          bind:checked={rememberMe}
          class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800"
        />
        <label for="remember-me" class="ml-2 block text-sm text-gray-700 dark:text-gray-300">
          {$t('auth.rememberMe')}
        </label>
      </div>
  
      <a 
        href="/reset-password" 
        class="text-sm font-medium text-primary-600 hover:text-primary-500 dark:text-primary-400 dark:hover:text-primary-300 transition-colors duration-200"
      >
        {$t('auth.forgotPassword')}
      </a>
    </div>
  
    <!-- Submit Button -->
    <button
      type="submit"
      disabled={loading || !isValid}
      class="
        relative w-full flex justify-center py-3 px-4 
        border border-transparent text-sm font-medium rounded-lg 
        text-white bg-primary-600 hover:bg-primary-700 
        focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 
        disabled:opacity-50 disabled:cursor-not-allowed
        transform transition-all duration-200 hover:scale-[1.02]
        {loading ? 'bg-primary-700' : ''}
      "
    >
      {#if loading}
        <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      {/if}
      {$t('auth.signIn')}
    </button>
  </form>