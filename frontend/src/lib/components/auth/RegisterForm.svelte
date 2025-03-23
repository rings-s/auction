<!-- src/lib/components/auth/RegisterForm.svelte -->
<script>
  import { t, language } from '$lib/i18n';
  import { createEventDispatcher } from 'svelte';
  import { onMount } from 'svelte';
  import { toast } from '$lib/stores/toast';
  import FormInput from '$lib/components/ui/FormInput.svelte';
  import FormButton from '$lib/components/ui/FormButton.svelte';
  import FormAlert from '$lib/components/ui/FormAlert.svelte';
  
  const dispatch = createEventDispatcher();
  
  // Form data
  let email = '';
  let firstName = '';
  let lastName = '';
  let password = '';
  let passwordConfirmation = '';
  let phoneNumber = '';
  let role = 'buyer'; // Default role
  let agreeToTerms = false;
  
  // Minimum required password length
  const MIN_PASSWORD_LENGTH = 8;
  
  // Form state
  let loading = false;
  let error = null;
  let formErrors = {}; // For field-specific errors
  let formSubmitted = false;
  let success = false;
  let debugMode = false;
  
  // Get API base URL for debugging
  let apiBaseUrl = '';
  onMount(() => {
    if (typeof window !== 'undefined') {
      apiBaseUrl = window.import?.meta?.env?.VITE_API_URL || 'http://localhost:8000/api';
      // Enable debug mode in development
      debugMode = window.location.hostname === 'localhost';
    }
  });
  
  // Role options - will be reactive to current language
  $: roleOptions = [
    { value: 'buyer', label: $t('auth.roles.buyer') },
    { value: 'seller', label: $t('auth.roles.seller') },
    { value: 'agent', label: $t('auth.roles.agent') }
  ];
  
  // Validation functions
  function validateEmail(value) {
    if (!value) return $t('auth.errors.email_required');
    if (!/\S+@\S+\.\S+/.test(value)) return $t('auth.errors.email_invalid');
    return null;
  }
  
  function validateRequired(value, fieldName) {
    return !value ? $t('auth.errors.field_required', { field: fieldName }) : null;
  }
  
  function validatePassword(value) {
    if (!value) return $t('auth.errors.password_required');
    if (value.length < MIN_PASSWORD_LENGTH) return $t('auth.errors.password_length', { length: MIN_PASSWORD_LENGTH });
    return null;
  }
  
  function validatePasswordMatch(password, confirmation) {
    if (!confirmation) return $t('auth.errors.password_confirmation_required');
    if (password !== confirmation) return $t('auth.errors.passwords_not_match');
    return null;
  }
  
  function validatePhoneNumber(value) {
    if (!value) return $t('auth.errors.phone_required');
    // Basic phone validation - can be enhanced for specific formats
    if (!/^[+]?[\d\s()-]{8,}$/.test(value)) return $t('auth.errors.phone_invalid');
    return null;
  }
  
  function validateTerms(checked) {
    return !checked ? $t('auth.errors.terms_required') : null;
  }
  
  // Validate entire form
  function validateForm() {
    formErrors = {
      email: validateEmail(email),
      firstName: validateRequired(firstName, $t('auth.first_name')),
      lastName: validateRequired(lastName, $t('auth.last_name')),
      password: validatePassword(password),
      passwordConfirmation: validatePasswordMatch(password, passwordConfirmation),
      phoneNumber: validatePhoneNumber(phoneNumber),
      agreeToTerms: validateTerms(agreeToTerms)
    };
    
    // Return true if no errors (all values are null)
    return !Object.values(formErrors).some(error => error !== null);
  }
  
  // Format registration data
  function formatRegistrationData() {
    return {
      email: email.trim(),
      first_name: firstName.trim(),
      last_name: lastName.trim(),
      password: password,
      password_confirmation: passwordConfirmation,
      confirm_password: passwordConfirmation,
      phone_number: phoneNumber.trim(),
      role: role,
      agree_to_terms: agreeToTerms,
    };
  }
  
  // Process field-specific errors from backend
  function processBackendErrors(errorData) {
    // Reset form errors
    formErrors = {
      email: null,
      firstName: null,
      lastName: null,
      password: null,
      passwordConfirmation: null,
      phoneNumber: null,
      agreeToTerms: null
    };
    
    // Default general error message
    let generalError = 'Registration failed';
    
    // If the error is a string, use it as the general error
    if (typeof errorData === 'string') {
      return { generalError, formErrors };
    }
    
    // Handle field errors
    if (typeof errorData === 'object' && errorData !== null) {
      // Map backend field names to our form field names
      const fieldMapping = {
        'email': 'email',
        'first_name': 'firstName',
        'last_name': 'lastName',
        'password': 'password',
        'password_confirmation': 'passwordConfirmation',
        'confirm_password': 'passwordConfirmation',
        'phone_number': 'phoneNumber',
        'agree_to_terms': 'agreeToTerms'
      };
      
      // Check for non-field errors
      if (errorData.non_field_errors) {
        generalError = Array.isArray(errorData.non_field_errors) 
          ? errorData.non_field_errors.join(', ') 
          : errorData.non_field_errors;
      }
      
      // Process each field error
      Object.entries(errorData).forEach(([field, errors]) => {
        if (field === 'non_field_errors') return;
        
        const formField = fieldMapping[field];
        if (formField) {
          formErrors[formField] = Array.isArray(errors) ? errors.join(', ') : errors;
        } else {
          generalError += ` ${field}: ${Array.isArray(errors) ? errors.join(', ') : errors}`;
        }
      });
    }
    
    return { generalError, formErrors };
  }
  
  // Handle form submission
  async function handleSubmit() {
    formSubmitted = true;
    
    // Validate form
    if (!validateForm()) {
      return;
    }
    
    loading = true;
    error = null;
    
    try {
      // Format registration data
      const userData = formatRegistrationData();
      
      // Direct fetch approach for better error handling
      const response = await fetch(`${apiBaseUrl}/accounts/register/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(userData),
        credentials: 'include'
      });
      
      // Get response text first
      const responseText = await response.text();
      let responseData;
      
      try {
        // Try to parse as JSON if possible
        responseData = responseText ? JSON.parse(responseText) : {};
      } catch (e) {
        // If not valid JSON, use the text directly
        responseData = responseText;
      }
      
      if (!response.ok) {
        console.error('Registration error response:', responseData);
        
        // Process field-specific errors
        const { generalError, formErrors: processedFormErrors } = processBackendErrors(responseData);
        formErrors = processedFormErrors;
        throw new Error(generalError);
      }
      
      // Registration successful
      success = true;
      toast.success($t('auth.register_success'));
      
      // Dispatch success event with email for verification
      dispatch('success', { email });
    } catch (e) {
      console.error('Registration error:', e);
      
      // Set general error message
      error = e.message || 'Registration failed';
      
      toast.error(error);
    } finally {
      loading = false;
    }
  }
</script>

<form on:submit|preventDefault={handleSubmit} class="space-y-6" novalidate>
  {#if error}
    <FormAlert type="error" dismissible={true}>{error}</FormAlert>
  {/if}

  {#if success}
    <FormAlert type="success" dismissible={true}>
      <p class="font-medium">{$t('auth.register_success')}</p>
      <p class="mt-1">{$t('auth.verification_required')}</p>
    </FormAlert>
  {/if}

  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
    <FormInput
      type="text"
      name="firstName"
      id="firstName"
      bind:value={firstName}
      label={$t('auth.first_name')}
      placeholder={$t('auth.first_name')}
      error={formSubmitted && formErrors.firstName}
      required={true}
      disabled={loading}
    />
    
    <FormInput
      type="text"
      name="lastName"
      id="lastName" 
      bind:value={lastName}
      label={$t('auth.last_name')}
      placeholder={$t('auth.last_name')}
      error={formSubmitted && formErrors.lastName}
      required={true}
      disabled={loading}
    />
  </div>

  <FormInput
    type="email"
    name="email"
    id="email"
    bind:value={email}
    label={$t('auth.email')}
    placeholder={$t('auth.email')}
    error={formSubmitted && formErrors.email}
    required={true}
    disabled={loading}
    forceLTR={true}
    autocomplete="email"
  />

  <FormInput
    type="tel"
    name="phoneNumber"
    id="phoneNumber"
    bind:value={phoneNumber}
    label={$t('auth.phone_number')}
    placeholder={$t('auth.phone_number')}
    error={formSubmitted && formErrors.phoneNumber}
    required={true}
    disabled={loading}
    forceLTR={true}
  />

  <div>
    <label for="role" class="block mb-1.5 text-sm font-medium text-neutral-800 dark:text-white">
      {$t('auth.roles.title')} <span class="text-error ml-0.5">*</span>
    </label>
    <select
      id="role"
      name="role"
      bind:value={role}
      class="w-full px-4 py-2.5 rounded-xl text-neutral-900 dark:text-white
        bg-white dark:bg-neutral-800
        border border-neutral-200 dark:border-neutral-700
        focus:ring-2 focus:ring-primary-300 dark:focus:ring-primary-800 focus:border-primary
        disabled:opacity-60"
      disabled={loading}
      dir={$language === 'ar' ? 'rtl' : 'ltr'}
    >
      {#each roleOptions as option}
        <option value={option.value}>{option.label}</option>
      {/each}
    </select>
  </div>

  <FormInput
    type="password"
    name="password"
    id="password"
    bind:value={password}
    label={$t('auth.password')}
    placeholder={$t('auth.password')}
    error={formSubmitted && formErrors.password}
    required={true}
    disabled={loading}
  />

  <div>
    <FormInput
      type="password"
      name="passwordConfirmation"
      id="passwordConfirmation"
      bind:value={passwordConfirmation}
      label={$t('auth.password_confirm')}
      placeholder={$t('auth.password_confirm')}
      error={formSubmitted && formErrors.passwordConfirmation}
      required={true}
      disabled={loading}
    />
    
    {#if !formSubmitted || !formErrors.password}
      <p class="mt-1 text-xs text-neutral-500 dark:text-neutral-400">
        {$t('auth.password_requirements', { length: MIN_PASSWORD_LENGTH })}
      </p>
    {/if}
  </div>

  <!-- Terms and Conditions -->
  <div>
    <div class="flex items-start">
      <div class="flex items-center h-5">
        <input
          id="agreeToTerms"
          name="agreeToTerms"
          type="checkbox"
          bind:checked={agreeToTerms}
          class="focus:ring-primary h-4 w-4 text-primary border-neutral-300 rounded"
          disabled={loading}
        />
      </div>
      <div class="ml-3 text-sm">
        <label for="agreeToTerms" class="text-neutral-800 dark:text-white">
          {$t('auth.agree_to_terms')} <span class="text-error ml-0.5">*</span>
        </label>
        <p class="text-neutral-500 dark:text-neutral-400">
          <a href="/terms" class="text-primary hover:underline">{$t('auth.terms_link')}</a>
        </p>
      </div>
    </div>
    {#if formSubmitted && formErrors.agreeToTerms}
      <p class="mt-1 text-sm text-error">{formErrors.agreeToTerms}</p>
    {/if}
  </div>

  <FormButton
    type="submit"
    variant="primary"
    fullWidth={true}
    loading={loading}
    disabled={loading}
  >
    {$t('auth.register')}
  </FormButton>

  <div class="text-center text-sm">
    <p class="text-neutral-600 dark:text-neutral-400">
      {$t('auth.already_have_account')}
      <a href="/auth/login" class="ml-1 font-medium text-primary hover:text-primary-dark">
        {$t('auth.login')}
      </a>
    </p>
  </div>
  
  <!-- Debug info for development -->
  {#if debugMode}
    <div class="mt-4 text-xs p-2 bg-neutral-100 dark:bg-neutral-800 rounded-xl">
      <details>
        <summary class="cursor-pointer text-neutral-500">Debug Info</summary>
        <div class="mt-2 p-2 bg-neutral-200 dark:bg-neutral-700 rounded-xl">
          <p class="mb-1 text-neutral-500 dark:text-neutral-300">API URL: {apiBaseUrl}</p>
          <p class="mb-1 text-neutral-500 dark:text-neutral-300">Form Errors: {JSON.stringify(formErrors)}</p>
          <p class="mb-1 text-neutral-500 dark:text-neutral-300">General Error: {error || 'None'}</p>
        </div>
      </details>
    </div>
  {/if}
</form>