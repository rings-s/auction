<!-- src/lib/components/auth/PasswordReset.svelte -->
<script>
  import { t, language } from '$lib/i18n';
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { createEventDispatcher } from 'svelte';
  import { authStore } from '$lib/stores/auth';
  import FormButton from '$lib/components/ui/FormButton.svelte';
  import FormInput from '$lib/components/ui/FormInput.svelte';
  import FormAlert from '$lib/components/ui/FormAlert.svelte';
  import { goto } from '$app/navigation';
  import { browser } from '$app/environment';
  
  const dispatch = createEventDispatcher();
  
  // Mode: request or reset
  export let mode = 'request';
  
  // Initial values from URL
  let email = '';
  let resetCode = '';
  
  onMount(() => {
    if ($page?.url?.searchParams) {
      if ($page.url.searchParams.has('email')) {
        email = $page.url.searchParams.get('email');
      }
      
      if ($page.url.searchParams.has('code')) {
        resetCode = $page.url.searchParams.get('code');
        mode = 'reset';
      }
    }
  });
  
  // Form data for password reset
  let newPassword = '';
  let confirmPassword = '';
  
  // Form state
  let loading = false;
  let error = null;
  let success = false;
  let formSubmitted = false;
  
  // Validation errors
  let errors = {
    email: null,
    resetCode: null,
    newPassword: null,
    confirmPassword: null
  };
  
  // Validate request form
  function validateRequest() {
    errors = {
      email: !email ? $t('auth.errors.email_required') : null
    };
    
    return !errors.email;
  }
  
  // Validate reset form
  function validateReset() {
    errors = {
      email: !email ? $t('auth.errors.email_required') : null,
      resetCode: !resetCode ? $t('auth.verification_code') + ' ' + $t('general.required') : null,
      newPassword: !newPassword ? $t('auth.errors.password_required')
        : newPassword.length < 8 ? $t('auth.errors.password_length')
        : null,
      confirmPassword: !confirmPassword ? $t('auth.errors.password_required')
        : newPassword !== confirmPassword ? $t('auth.errors.passwords_not_match')
        : null
    };
    
    return !Object.values(errors).some(error => error);
  }
  
  // Handle request form submission
  async function handleRequestSubmit() {
    formSubmitted = true;
    
    if (!validateRequest()) {
      return;
    }
    
    loading = true;
    error = null;
    success = false;
    
    try {
      const result = await authStore.requestPasswordReset(email);
      
      if (result?.success) {
        success = true;
        dispatch('request-success', { email });
      } else {
        error = result?.error || $t('system_messages.error_occurred');
      }
    } catch (e) {
      console.error('Password reset request error:', e);
      // Enhanced error handling
      if (e.error) {
        error = e.error;
      } else if (e.message) {
        error = e.message;
      } else {
        error = $t('system_messages.error_occurred');
      }
    } finally {
      loading = false;
    }
  }
  
  // Handle reset form submission
  async function handleResetSubmit() {
    formSubmitted = true;
    
    if (!validateReset()) {
      return;
    }
    
    loading = true;
    error = null;
    success = false;
    
    try {
      // Fixed: Parameter order to match API expectation - email first, then code
      const result = await authStore.resetPassword(
        email,
        resetCode,
        newPassword,
        confirmPassword
      );
      
      if (result?.success) {
        success = true;
        
        // Store tokens and user data if present
        if (result.tokens && browser) {
          if (result.tokens.access) {
            try {
              localStorage.setItem('accessToken', result.tokens.access);
              localStorage.setItem('refreshToken', result.tokens.refresh || '');
              
              // Set auth cookie for server-side auth
              document.cookie = `accessToken=${result.tokens.access}; path=/; max-age=86400; SameSite=Strict`;
            } catch (storageError) {
              console.error('Storage error:', storageError);
              // Continue despite storage error
            }
          }
        }
        
        dispatch('reset-success');
        // Redirect to dashboard or login
        if (browser) {
          setTimeout(() => goto('/dashboard'), 1500);
        }
      } else {
        error = result?.error || $t('system_messages.password_reset_failure');
      }
    } catch (e) {
      console.error('Password reset error:', e);
      // Enhanced error handling
      if (e.error) {
        error = e.error;
      } else if (e.message) {
        error = e.message;
      } else {
        error = $t('system_messages.password_reset_failure');
      }
    } finally {
      loading = false;
    }
  }
  
  // Switch to reset mode
  function switchToResetMode() {
    mode = 'reset';
  }

  // Switch to request mode
  function switchToRequestMode() {
    mode = 'request';
  }
</script>

{#if mode === 'request'}
  <!-- Request Password Reset Form -->
  <form on:submit|preventDefault={handleRequestSubmit} class="space-y-6" novalidate>
    {#if error}
      <FormAlert type="error" dismissible={true}>{error}</FormAlert>
    {/if}
    
    {#if success}
      <FormAlert type="success" dismissible={true}>
        {$t('system_messages.password_reset_sent')}
      </FormAlert>
    {/if}
    
    <div>
      <p class="mb-4 text-neutral-600 dark:text-neutral-400">
        {$t('auth.reset_password_info')}
      </p>
    </div>
    
    <FormInput
      type="email"
      name="email"
      id="email"
      bind:value={email}
      label={$t('auth.email')}
      placeholder={$t('auth.email')}
      error={formSubmitted && errors.email}
      required={true}
      forceLTR={true}
    />
    
    <FormButton
      type="submit"
      variant="primary"
      fullWidth={true}
      loading={loading}
      disabled={loading}
    >
      {$t('auth.request_reset')}
    </FormButton>
    
    <div class="text-center">
      <p class="text-sm text-neutral-600 dark:text-neutral-400">
        {$t('auth.already_have_code')}
        <button
          type="button"
          on:click={switchToResetMode}
          class="ml-1 font-medium text-primary hover:text-primary-dark hover:underline"
        >
          {$t('auth.enter_code')}
        </button>
      </p>
    </div>
  </form>
{:else}
  <!-- Reset Password Form -->
  <form on:submit|preventDefault={handleResetSubmit} class="space-y-6" novalidate>
    {#if error}
      <FormAlert type="error" dismissible={true}>{error}</FormAlert>
    {/if}
    
    {#if success}
      <FormAlert type="success" dismissible={true}>
        {$t('system_messages.password_reset_success')}
      </FormAlert>
    {/if}
    
    <div>
      <p class="mb-4 text-neutral-600 dark:text-neutral-400">
        {$t('auth.enter_new_password_info')}
      </p>
    </div>
    
    <!-- Disable if email came from query parameter -->
    <FormInput
      type="email"
      name="email"
      id="email"
      bind:value={email}
      label={$t('auth.email')}
      placeholder={$t('auth.email')}
      error={formSubmitted && errors.email}
      required={true}
      disabled={!!email}
      forceLTR={true}
    />
    
    <!-- Disable if code came from query parameter -->
    <FormInput
      type="text"
      name="resetCode"
      id="resetCode"
      bind:value={resetCode}
      label={$t('auth.verification_code')}
      placeholder={$t('auth.verification_code')}
      error={formSubmitted && errors.resetCode}
      required={true}
      disabled={!!resetCode}
      forceLTR={true}
    />
    
    <FormInput
      type="password"
      name="newPassword"
      id="newPassword"
      bind:value={newPassword}
      label={$t('auth.new_password')}
      placeholder={$t('auth.new_password')}
      error={formSubmitted && errors.newPassword}
      required={true}
    />
    
    <FormInput
      type="password"
      name="confirmPassword"
      id="confirmPassword"
      bind:value={confirmPassword}
      label={$t('auth.password_confirm')}
      placeholder={$t('auth.password_confirm')}
      error={formSubmitted && errors.confirmPassword}
      required={true}
    />
    
    <FormButton
      type="submit"
      variant="primary"
      fullWidth={true}
      loading={loading}
      disabled={loading}
    >
      {$t('auth.reset_password')}
    </FormButton>
    
    <div class="text-center">
      <button
        type="button"
        on:click={switchToRequestMode}
        class="text-sm font-medium text-primary hover:text-primary-dark hover:underline"
      >
        {$t('general.back')}
      </button>
    </div>
  </form>
{/if}