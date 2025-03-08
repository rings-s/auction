<!-- src/routes/register/+page.svelte -->
<script>
  import { goto } from '$app/navigation';
  import { fade, fly } from 'svelte/transition';
  import RegistrationForm from '$lib/components/auth/RegistrationForm.svelte';
  
  // State to track registration status
  let registrationComplete = false;
  let userEmail = '';
  
  // Handle successful registration
  function handleRegistrationSuccess(event) {
    const { email } = event.detail;
    userEmail = email;
    registrationComplete = true;
  }
  
  // Handle verification completion
  function handleVerificationSuccess() {
    goto('/dashboard');
  }
</script>

<svelte:head>
  <title>Create Account | GUDIC Auctions</title>
</svelte:head>

<div class="min-h-[80vh] flex flex-col justify-center py-12">
  <div class="max-w-lg w-full mx-auto px-4" in:fly={{ y: 20, duration: 600, delay: 200 }}>
    <!-- Decorative elements -->
    <div class="absolute -z-10 w-64 h-64 rounded-full bg-primary-blue/20 blur-3xl -top-10 -left-20 animate-blob"></div>
    <div class="absolute -z-10 w-64 h-64 rounded-full bg-primary-peach/20 blur-3xl -bottom-10 -right-20 animate-blob animation-delay-2000"></div>
    
    <!-- Registration card -->
    <div class="relative glass-effect rounded-2xl shadow-xl p-8 border border-white/20">
      <!-- Logo -->
      <div class="flex justify-center mb-6">
        <div class="w-16 h-16 flex items-center justify-center rounded-full bg-gradient-to-br from-primary-blue to-primary-peach shadow-lg">
          <span class="text-white font-bold text-2xl">G</span>
        </div>
      </div>
      
      <!-- Title with conditional rendering based on registration status -->
      <div class="text-center mb-8">
        {#if registrationComplete}
          <h1 class="text-2xl font-bold text-text-dark mb-2">
            Verification Required
          </h1>
          <p class="text-text-medium">
            We've sent a verification code to <strong>{userEmail}</strong>
          </p>
        {:else}
          <h1 class="text-2xl font-bold text-text-dark mb-2">Create Your Account</h1>
          <p class="text-text-medium">Join GUDIC to start bidding and selling</p>
        {/if}
      </div>
      
      <!-- Registration form or verification form based on status -->
      {#if registrationComplete}
        <div class="space-y-6">
          <!-- Verification Form would go here, importing VerificationForm component -->
          <!-- For now displaying a placeholder message -->
          <div class="bg-primary-blue/10 border-l-4 border-secondary-blue rounded-md p-4 mb-6">
            <p class="text-sm text-text-dark">
              Please check your email inbox and enter the verification code we sent you. 
              If you don't see it in your inbox, please check your spam folder.
            </p>
          </div>
          
          <div class="py-4">
            <label for="verification-code" class="block text-sm font-medium text-text-dark mb-1">
              Verification Code
            </label>
            <input
              type="text"
              id="verification-code"
              name="verification_code"
              class="form-input w-full rounded-md"
              placeholder="Enter 6-digit code"
            />
          </div>
          
          <button
            class="w-full bg-gradient-to-r from-secondary-blue to-secondary-peach text-white py-3 px-6 rounded-xl font-medium transition-all hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-secondary-blue"
          >
            Verify Email
          </button>
          
          <div class="text-center">
            <p class="text-sm text-text-medium">
              Didn't receive the code?
              <button
                type="button"
                class="font-medium text-secondary-blue hover:text-secondary-blue/80 transition-colors"
              >
                Resend Code
              </button>
            </p>
          </div>
        </div>
      {:else}
        <RegistrationForm on:success={handleRegistrationSuccess} />
      {/if}
      
      <!-- Login link (shown only during registration) -->
      {#if !registrationComplete}
        <div class="mt-6 text-center">
          <p class="text-text-medium text-sm mb-4">
            Already have an account?
            <a href="/login" class="text-secondary-blue hover:underline font-medium transition-colors">
              Sign in
            </a>
          </p>
          
          <a href="/" class="inline-flex items-center text-text-medium hover:text-secondary-blue text-sm transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to home
          </a>
        </div>
      {/if}
    </div>
  </div>
</div>

<style>
  /* Custom local styles */
  .glass-effect {
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    background: rgba(255, 255, 255, 0.6);
  }
  
  /* Form input styling */
  .form-input {
    border: 2px solid rgba(185, 220, 242, 0.3);
    padding: 0.75rem 1rem;
    font-size: 0.875rem;
    transition: all 0.2s ease;
  }
  
  .form-input:focus {
    border-color: var(--secondary-blue);
    box-shadow: 0 0 0 2px rgba(185, 220, 242, 0.2);
    outline: none;
  }
</style>