<!-- src/lib/components/auth/VerificationForm.svelte -->
<script>
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { t } from '$lib/i18n';
  import { createEventDispatcher } from 'svelte';
  import { authStore } from '$lib/stores/auth';
  import FormButton from '$lib/components/ui/FormButton.svelte';
  import FormInput from '$lib/components/ui/FormInput.svelte';
  import FormAlert from '$lib/components/ui/FormAlert.svelte';
  import { goto } from '$app/navigation';
  import authService from '$lib/services/auth';

  const dispatch = createEventDispatcher();

  // Get email from URL query params but don't display in form
  let email = '';

  onMount(() => {
    if ($page.url.searchParams.has('email')) {
      email = $page.url.searchParams.get('email');
    }
  });

  // Form data
  let verificationCode = '';

  // Form state
  let loading = false;
  let resending = false;
  let error = null;
  let resendError = null;
  let resendSuccess = false;
  let formSubmitted = false;

  // Validation errors
  let errors = {
    verificationCode: null
  };

  // Validate form
  function validate() {
    errors = {
      verificationCode: !verificationCode ? $t('auth.verification_code') + ' ' + $t('general.required') : null
    };

    return !Object.values(errors).some(error => error);
  }

  // Handle form submission
  async function handleSubmit() {
    formSubmitted = true;

    if (!validate() || !email) {
      return;
    }

    loading = true;
    error = null;

    try {
      const result = await authStore.verifyEmail(email, verificationCode);

      if (result.success) {
        dispatch('success');
        // Redirect to dashboard
        goto('/dashboard');
      } else {
        error = result.error;
      }
    } catch (e) {
      console.error('Verification error:', e);
      // Enhanced error handling
      if (e.error) {
        error = e.error;
      } else if (e.message) {
        error = e.message;
      } else {
        error = $t('system_messages.verification_failure');
      }
    } finally {
      loading = false;
    }
  }

  // Resend verification code
  async function resendCode() {
    if (!email) {
      resendError = $t('auth.errors.email_required');
      return;
    }

    resending = true;
    resendError = null;
    resendSuccess = false;

    try {
      const response = await authService.resendVerification(email);

      if (response && (response.status === 'success' || response.success === true)) {
        resendSuccess = true;
      } else {
        resendError = (response.error || response.message) || $t('system_messages.error_occurred');
      }
    } catch (e) {
      console.error('Resend verification error:', e);
      // Enhanced error handling
      if (e.error) {
        resendError = e.error;
      } else if (e.message) {
        resendError = e.message;
      } else {
        resendError = $t('system_messages.error_occurred');
      }
    } finally {
      resending = false;
    }
  }
</script>

<form on:submit|preventDefault={handleSubmit} class="space-y-6" novalidate>
{#if error}
  <FormAlert type="error" dismissible={true}>{error}</FormAlert>
{/if}

{#if resendError}
  <FormAlert type="error" dismissible={true}>{resendError}</FormAlert>
{/if}

{#if resendSuccess}
  <FormAlert type="success" dismissible={true}>
    {$t('auth.verification_sent')}
  </FormAlert>
{/if}

<div>
  <p class="mb-4 text-neutral-600 dark:text-neutral-400">
    {$t('auth.verification_info')}
  </p>
</div>

<FormInput
  type="text"
  name="verificationCode"
  id="verificationCode"
  bind:value={verificationCode}
  label={$t('auth.verification_code')}
  placeholder={$t('auth.verification_code')}
  error={formSubmitted && errors.verificationCode}
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
  {$t('auth.verify_account')}
</FormButton>

<div class="text-center">
  <button
    type="button"
    on:click={resendCode}
    class="text-sm font-medium text-primary hover:text-primary-dark hover:underline"
    disabled={resending}
  >
    {resending ? $t('general.loading') : $t('auth.resend_code')}
  </button>
</div>

<div class="text-center text-sm">
  <p class="text-neutral-600 dark:text-neutral-400">
    <a href="/auth/login" class="font-medium text-primary hover:text-primary-dark hover:underline">
      {$t('auth.login')}
    </a>
  </p>
</div>
</form>