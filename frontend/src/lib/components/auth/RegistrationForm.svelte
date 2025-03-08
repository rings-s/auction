<!-- src/lib/components/auth/RegistrationForm.svelte -->
<script>
  import { createEventDispatcher, onMount } from 'svelte';
  import { authStore } from '$lib/stores/authStore';
  import { notificationStore } from '$lib/stores/notificationStore';
  import Input from '$lib/components/ui/Input.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Alert from '$lib/components/ui/Alert.svelte';
  
  const dispatch = createEventDispatcher();
  
  // Form data - ensure field names exactly match backend expectations
  let formData = {
    email: '',
    password: '',
    password_confirmation: '', // Exact match for Django backend
    first_name: '',
    last_name: '',
    phone_number: '',
    date_of_birth: '',
    role: 'buyer' // Default role
  };
  
  // UI state
  let loading = false;
  let fieldErrors = {};
  let generalError = '';
  let debugMode = false; // Toggle for debug information
  let apiResponseData = null; // Store full API response for debugging
  let currentStep = 1; // Multi-step form (1: Basic Info, 2: Account Details)
  
  // Role options - should match backend Role.ROLE_CHOICES
  const roleOptions = [
    { value: 'buyer', label: 'Buyer' },
    { value: 'seller', label: 'Seller' },
    { value: 'inspector', label: 'Inspector' },
    { value: 'legal', label: 'Legal Representative' }
  ];
  
  // Field validation state
  let passwordFocused = false;
  let confirmPasswordFocused = false;
  
  // Validation helpers
  $: passwordsMatch = !confirmPasswordFocused || 
    formData.password === formData.password_confirmation;
  
  $: passwordStrength = !passwordFocused || formData.password.length === 0 ? 
    null : getPasswordStrength(formData.password);
  
  $: isBasicInfoValid = formData.first_name && formData.last_name && formData.email;
  
  $: isAccountValid = formData.password && 
    formData.password_confirmation && 
    passwordsMatch && 
    passwordStrength?.strength !== 'weak';
  
  $: isFormValid = isBasicInfoValid && isAccountValid && formData.role;
  
  // Format date to match Django's expected format (YYYY-MM-DD)
  function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return dateString;
    
    return date.toISOString().split('T')[0];
  }
  
  function getPasswordStrength(password) {
    // Simple password strength check
    if (password.length < 8) return { strength: 'weak', text: 'Weak', color: 'text-error' };
    
    let score = 0;
    if (password.length >= 12) score += 1;
    if (/[A-Z]/.test(password)) score += 1;
    if (/[a-z]/.test(password)) score += 1;
    if (/[0-9]/.test(password)) score += 1;
    if (/[^A-Za-z0-9]/.test(password)) score += 1;
    
    if (score >= 4) return { strength: 'strong', text: 'Strong', color: 'text-success' };
    if (score >= 2) return { strength: 'medium', text: 'Medium', color: 'text-warning' };
    return { strength: 'weak', text: 'Weak', color: 'text-error' };
  }
  
  // Navigate to next step
  function nextStep() {
    if (currentStep === 1 && isBasicInfoValid) {
      currentStep = 2;
    }
  }
  
  // Navigate to previous step
  function prevStep() {
    if (currentStep === 2) {
      currentStep = 1;
    }
  }
  
  // Reset all error states
  function resetErrors() {
    fieldErrors = {};
    generalError = '';
    apiResponseData = null;
  }
  
  // Handle field-specific errors from the API
  function processFieldErrors(errorResponse) {
    if (typeof errorResponse === 'object') {
      // Django typically returns field-level errors as an object
      fieldErrors = errorResponse;
      
      // Extract first error message for notification if there's no general error
      if (!generalError) {
        const firstErrorField = Object.keys(fieldErrors)[0];
        const firstErrorMessage = fieldErrors[firstErrorField];
        generalError = `${firstErrorField}: ${firstErrorMessage}`;
      }
    } else if (typeof errorResponse === 'string') {
      generalError = errorResponse;
    } else {
      generalError = 'Registration failed. Please check the form for errors.';
    }
  }
  
  async function handleSubmit() {
    if (!isFormValid) {
      generalError = 'Please complete all required fields correctly.';
      return;
    }
    
    loading = true;
    resetErrors();
    
    try {
      // Format data for API - clone to avoid modifying the form state
      const registrationData = { ...formData };
      
      // Format date to YYYY-MM-DD for backend
      if (registrationData.date_of_birth) {
        registrationData.date_of_birth = formatDate(registrationData.date_of_birth);
      }
      
      console.log('Submitting registration data:', registrationData);
      
      const result = await authStore.register(registrationData);
      console.log('Registration success:', result);
      apiResponseData = result;
      
      notificationStore.success('Registration successful! Please check your email for verification.');
      dispatch('success', { email: formData.email });
    } catch (err) {
      console.error('Registration error:', err);
      apiResponseData = err;
      
      // Handle different types of errors
      if (err.status === 400) {
        // Field-specific validation errors
        processFieldErrors(err.error);
      } else if (err.status === 429) {
        // Rate limiting
        generalError = err.error || 'Too many attempts. Please try again later.';
      } else if (err.status >= 500) {
        // Server errors
        generalError = 'Server error. Please try again later.';
      } else {
        // Other errors
        generalError = err.error || 'Registration failed. Please try again.';
      }
      
      // Display notification for error
      notificationStore.error(generalError || 'Registration failed');
    } finally {
      loading = false;
    }
  }
  
  // Function to check field-specific error
  function hasError(fieldName) {
    return fieldErrors[fieldName] ? true : false;
  }
  
  // Function to get field-specific error message
  function getErrorMessage(fieldName) {
    return fieldErrors[fieldName] || '';
  }
</script>

<form on:submit|preventDefault={handleSubmit} class="space-y-6">
  <!-- General error message -->
  {#if generalError}
    <Alert variant="error">
      {generalError}
    </Alert>
  {/if}
  
  <!-- Progress indicator -->
  <div class="flex items-center justify-between mb-6">
    <div class="flex items-center">
      <div class="h-8 w-8 rounded-full flex items-center justify-center {currentStep >= 1 ? 'bg-secondary-blue text-white' : 'bg-neutral-100 text-text-medium'}">
        1
      </div>
      <div class="h-1 w-10 mx-2 {currentStep >= 2 ? 'bg-secondary-blue' : 'bg-neutral-100'}"></div>
      <div class="h-8 w-8 rounded-full flex items-center justify-center {currentStep >= 2 ? 'bg-secondary-blue text-white' : 'bg-neutral-100 text-text-medium'}">
        2
      </div>
    </div>
    <div class="text-sm text-text-medium">
      Step {currentStep} of 2
    </div>
  </div>

  <!-- Step 1: Basic Information -->
  {#if currentStep === 1}
    <div class="space-y-4 fade-in-up">
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <!-- First Name field -->
        <Input
          type="text"
          id="first_name"
          name="first_name"
          label="First name"
          bind:value={formData.first_name}
          autocomplete="given-name"
          required
          error={getErrorMessage('first_name')}
        />

        <!-- Last Name field -->
        <Input
          type="text"
          id="last_name"
          name="last_name"
          label="Last name"
          bind:value={formData.last_name}
          autocomplete="family-name"
          required
          error={getErrorMessage('last_name')}
        />
      </div>

      <!-- Email field -->
      <Input
        type="email"
        id="email"
        name="email"
        label="Email address"
        bind:value={formData.email}
        autocomplete="email"
        required
        error={getErrorMessage('email')}
      />

      <!-- Phone number field -->
      <Input
        type="tel"
        id="phone_number"
        name="phone_number"
        label="Phone number"
        bind:value={formData.phone_number}
        autocomplete="tel"
        error={getErrorMessage('phone_number')}
        helper="International format recommended: +1234567890"
      />
      
      <!-- Date of birth field -->
      <Input
        type="date"
        id="date_of_birth"
        name="date_of_birth"
        label="Date of birth"
        bind:value={formData.date_of_birth}
        error={getErrorMessage('date_of_birth')}
      />
      
      <!-- Next button -->
      <div class="pt-4">
        <Button
          type="button"
          variant="primary"
          size="lg"
          fullWidth={true}
          disabled={!isBasicInfoValid}
          onClick={nextStep}
        >
          Continue
        </Button>
      </div>
    </div>
  {/if}

  <!-- Step 2: Account Details -->
  {#if currentStep === 2}
    <div class="space-y-4 fade-in-up">
      <!-- Password field -->
      <div>
        <Input
          type="password"
          id="password"
          name="password"
          label="Password"
          bind:value={formData.password}
          on:focus={() => passwordFocused = true}
          on:blur={() => passwordFocused = false}
          autocomplete="new-password"
          required
          error={getErrorMessage('password')}
          helper="At least 8 characters with a mix of letters, numbers, and symbols"
        />
        
        {#if passwordStrength}
          <div class="flex items-center mt-2">
            <div class="flex-1 h-1.5 bg-neutral-100 rounded-full overflow-hidden">
              <div class="h-full rounded-full {passwordStrength.strength === 'weak' ? 'bg-error' : passwordStrength.strength === 'medium' ? 'bg-warning' : 'bg-success'}" style="width: {passwordStrength.strength === 'weak' ? '33%' : passwordStrength.strength === 'medium' ? '66%' : '100%'}"></div>
            </div>
            <p class="ml-2 text-xs {passwordStrength.color}">
              {passwordStrength.text}
            </p>
          </div>
        {/if}
      </div>

      <!-- Confirm Password field -->
      <div>
        <Input
          type="password"
          id="password_confirmation"
          name="password_confirmation"
          label="Confirm password"
          bind:value={formData.password_confirmation}
          on:focus={() => confirmPasswordFocused = true}
          on:blur={() => confirmPasswordFocused = false}
          autocomplete="new-password"
          required
          error={!passwordsMatch ? 'Passwords do not match' : getErrorMessage('password_confirmation')}
        />
      </div>

      <!-- Role selection -->
      <div>
        <label for="role" class="block text-sm font-medium text-text-dark mb-2">I want to register as a</label>
        <div class="grid grid-cols-2 gap-3 mt-1">
          {#each roleOptions as option}
            <div 
              class="relative border p-3 rounded-lg cursor-pointer transition-all {formData.role === option.value ? 'bg-primary-blue/10 border-secondary-blue' : 'border-primary-blue/30 hover:border-primary-blue/50 hover:bg-primary-blue/5'}"
              on:click={() => formData.role = option.value}
              on:keypress={(e) => e.key === 'Enter' && (formData.role = option.value)}
              tabindex="0"
              role="radio"
              aria-checked={formData.role === option.value}
            >
              <input
                type="radio"
                name="role"
                id="role-{option.value}"
                value={option.value}
                class="sr-only"
                bind:group={formData.role}
              />
              <label for="role-{option.value}" class="text-sm font-medium text-text-dark block cursor-pointer">
                {option.label}
              </label>
              {#if formData.role === option.value}
                <div class="absolute top-1 right-1 h-4 w-4 text-secondary-blue">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                  </svg>
                </div>
              {/if}
            </div>
          {/each}
        </div>
        {#if hasError('role')}
          <p class="mt-1 text-xs text-error">{getErrorMessage('role')}</p>
        {/if}
      </div>
      
      <!-- Terms agreement -->
      <div class="mt-4">
        <div class="flex items-start">
          <div class="flex items-center h-5">
            <input
              id="terms"
              name="terms"
              type="checkbox"
              required
              class="h-4 w-4 rounded border-primary-blue/30 text-secondary-blue focus:ring-secondary-blue"
            />
          </div>
          <div class="ml-3 text-sm">
            <label for="terms" class="text-text-medium">
              I agree to the 
              <a href="/terms" class="text-secondary-blue hover:underline">Terms of Service</a>
              and 
              <a href="/privacy" class="text-secondary-blue hover:underline">Privacy Policy</a>
            </label>
          </div>
        </div>
      </div>
      
      <!-- Action buttons -->
      <div class="pt-4 flex space-x-4">
        <Button
          type="button"
          variant="outline"
          size="lg"
          onClick={prevStep}
        >
          Back
        </Button>
        
        <Button
          type="submit"
          variant="primary"
          size="lg"
          fullWidth={true}
          disabled={loading || !isFormValid}
          loading={loading}
        >
          {loading ? 'Creating Account...' : 'Create Account'}
        </Button>
      </div>
    </div>
  {/if}
</form>

<style>
  /* Custom animation for step transitions */
  .fade-in-up {
    animation: fadeInUp 0.5s forwards;
  }
  
  @keyframes fadeInUp {
    from {
      opacity: 0;
      transform: translateY(10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  
  /* Custom checkbox styling */
  input[type="checkbox"] {
    cursor: pointer;
    position: relative;
  }
  
  input[type="checkbox"]:checked {
    background-color: var(--secondary-blue);
    border-color: var(--secondary-blue);
  }
  
  input[type="checkbox"]:focus {
    box-shadow: 0 0 0 2px var(--primary-blue);
  }
</style>