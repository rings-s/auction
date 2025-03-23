<!-- src/lib/components/auth/LoginForm.svelte -->
<script>
  import { createEventDispatcher } from 'svelte';
  import { t } from '$lib/i18n';
  import { isValidEmail, isNotEmpty } from '$lib/utils/validators';
  import { onMount } from 'svelte';
  import { toast } from '$lib/stores/toast';
  import authService from '$lib/services/auth';
  import { goto } from '$app/navigation';
  import FormInput from '$lib/components/ui/FormInput.svelte';
  import FormButton from '$lib/components/ui/FormButton.svelte';
  import FormAlert from '$lib/components/ui/FormAlert.svelte';
  import GlassCard from '$lib/components/ui/GlassCard.svelte';
  
  // Event dispatcher
  const dispatch = createEventDispatcher();
  
  // State management
  let email = '';
  let password = '';
  let rememberMe = true;
  let isSubmitting = false;
  let networkError = '';
  let debugMode = false;
  
  // Mode management
  let mode = 'login'; // login, forgotPassword
  let resetEmail = '';
  let resetSent = false;
  let resetLoading = false;
  let resetError = '';
  
  // Form validation
  let errors = {
    email: '',
    password: '',
    form: ''
  };
  
  // Enable debug mode in development
  onMount(() => {
    if (typeof window !== 'undefined') {
      debugMode = window.location.hostname === 'localhost';
    }
  });
  
  // Login function
  async function handleLogin() {
    // Reset errors
    errors = { email: '', password: '', form: '' };
    networkError = '';
    
    // Validate form
    if (!isNotEmpty(email)) {
      errors.email = $t('auth.errors.email_required');
    } else if (!isValidEmail(email)) {
      errors.email = $t('auth.errors.email_invalid');
    }
    
    if (!isNotEmpty(password)) {
      errors.password = $t('auth.errors.password_required');
    }
    
    // Check if there are any validation errors
    const isValid = !errors.email && !errors.password;
    
    if (isValid) {
      try {
        isSubmitting = true;
        
        // Use the auth service for login
        const result = await authService.login(email, password);
        
        // Successful login
        toast.success($t('auth.login_success'));
        dispatch('success');
      } catch (error) {
        console.error('Login error:', error);
        
        // Check for network issues
        if (error.message && error.message.includes('Failed to fetch')) {
          networkError = `${$t('system_messages.no_internet')}`;
          errors.form = $t('auth.network_error');
        } else {
          errors.form = error.message || $t('auth.login_failed');
        }
        
        toast.error(errors.form);
      } finally {
        isSubmitting = false;
      }
    }
  }
  
  // Password reset function
  async function handlePasswordReset() {
    // Reset errors
    resetError = '';
    
    // Validate email
    if (!isNotEmpty(resetEmail)) {
      resetError = $t('auth.errors.email_required');
      return;
    } else if (!isValidEmail(resetEmail)) {
      resetError = $t('auth.errors.email_invalid');
      return;
    }
    
    try {
      resetLoading = true;
      
      // Call the password reset service
      const response = await authService.requestPasswordReset(resetEmail);
      
      if (response && response.success) {
        resetSent = true;
        toast.success($t('system_messages.password_reset_sent'));
      } else {
        resetError = response?.error || $t('system_messages.error_occurred');
      }
    } catch (error) {
      console.error('Password reset error:', error);
      resetError = error.message || $t('system_messages.error_occurred');
    } finally {
      resetLoading = false;
    }
  }
  
  // Switch to password reset mode
  function switchToPasswordReset() {
    mode = 'forgotPassword';
    resetEmail = email; // Pre-fill with login email if exists
  }
  
  // Switch back to login mode
  function switchToLogin() {
    mode = 'login';
  }
</script>

{#if mode === 'login'}
  <form on:submit|preventDefault={handleLogin} class="space-y-6">
    {#if errors.form}
      <FormAlert type="error" dismissible={true}>{errors.form}</FormAlert>
    {/if}

    {#if networkError}
      <FormAlert type="warning" dismissible={true}>
        {networkError}
      </FormAlert>
    {/if}

    <FormInput
      id="email"
      type="email"
      name="email"
      bind:value={email}
      label={$t('auth.email')}
      placeholder={$t('auth.email')}
      error={errors.email}
      autocomplete="email"
      forceLTR={true}
      required={true}
      disabled={isSubmitting}
    />

    <FormInput
      id="password"
      type="password"
      name="password"
      bind:value={password}
      label={$t('auth.password')}
      placeholder={$t('auth.password')}
      error={errors.password}
      autocomplete="current-password"
      required={true}
      disabled={isSubmitting}
    />

    <div class="flex items-center justify-between">
      <div class="flex items-center">
        <input
          id="remember-me"
          name="remember-me"
          type="checkbox"
          bind:checked={rememberMe}
          class="h-4 w-4 rounded border-neutral-300 text-primary focus:ring-primary"
        />
        <label for="remember-me" class="ml-2 block text-sm text-neutral-600 dark:text-neutral-400">
          {$t('auth.remember_me')}
        </label>
      </div>

      <button
        type="button"
        on:click={switchToPasswordReset}
        class="text-sm font-medium text-primary hover:text-primary-dark"
      >
        {$t('auth.forgot_password')}
      </button>
    </div>

    <FormButton
      type="submit"
      variant="primary"
      fullWidth={true}
      loading={isSubmitting}
      disabled={isSubmitting}
    >
      {$t('auth.login')}
    </FormButton>

    <div class="text-center text-sm">
      <p class="text-neutral-600 dark:text-neutral-400">
        {$t('auth.no_account')}
        <a href="/auth/register" class="ml-1 font-medium text-primary hover:text-primary-dark">
          {$t('auth.register_now')}
        </a>
      </p>
    </div>
  </form>
{:else if mode === 'forgotPassword'}
  <div class="space-y-6">
    {#if resetSent}
      <FormAlert type="success">
        {$t('system_messages.password_reset_sent')}
        <div class="mt-2 text-sm">
          <button
            type="button"
            on:click={switchToLogin}
            class="font-medium hover:underline"
          >
            {$t('auth.login')}
          </button>
        </div>
      </FormAlert>
    {:else}
      <div class="mb-4">
        <h3 class="text-lg font-medium text-neutral-800 dark:text-white mb-1">
          {$t('auth.reset_password')}
        </h3>
        <p class="text-sm text-neutral-600 dark:text-neutral-400">
          {$t('auth.reset_password_info')}
        </p>
      </div>

      {#if resetError}
        <FormAlert type="error" dismissible={true}>{resetError}</FormAlert>
      {/if}

      <FormInput
        id="reset-email"
        type="email"
        name="resetEmail"
        bind:value={resetEmail}
        label={$t('auth.email')}
        placeholder={$t('auth.email')}
        forceLTR={true}
        required={true}
        disabled={resetLoading}
      />

      <div class="flex flex-col space-y-3">
        <FormButton
          type="button"
          variant="primary"
          fullWidth={true}
          loading={resetLoading}
          disabled={resetLoading}
          onClick={handlePasswordReset}
        >
          {$t('auth.request_reset')}
        </FormButton>
        
        <FormButton
          type="button"
          variant="outline"
          fullWidth={true}
          disabled={resetLoading}
          onClick={switchToLogin}
        >
          {$t('general.back')}
        </FormButton>
      </div>
    {/if}
  </div>
{/if}

<!-- Debug info for development only -->
{#if debugMode && (errors.form || networkError || resetError)}
  <div class="mt-4 text-xs p-2 bg-neutral-100 dark:bg-neutral-800 rounded-xl">
    <details>
      <summary class="cursor-pointer text-neutral-500">Debug Info</summary>
      <div class="mt-2 p-2 bg-neutral-200 dark:bg-neutral-700 rounded-xl">
        <p class="mb-1 text-neutral-600 dark:text-neutral-300">Mode: {mode}</p>
        <p class="mb-1 text-neutral-600 dark:text-neutral-300">Error: {errors.form || resetError || 'None'}</p>
        <p class="mb-1 text-neutral-600 dark:text-neutral-300">Network: {networkError || 'None'}</p>
      </div>
    </details>
  </div>
{/if}