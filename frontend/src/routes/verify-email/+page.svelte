<!-- src/routes/verify-email/+page.svelte -->
<script>
  import { page } from '$app/stores';
  import { fade, fly } from 'svelte/transition';
  import { goto } from '$app/navigation';
  import VerificationForm from '$lib/components/auth/VerificationForm.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  
  // Get email and verification code from URL if available
  let email = $page.url.searchParams.get('email') || '';
  let code = $page.url.searchParams.get('code') || '';
  
  // Handle successful verification
  function handleVerificationSuccess() {
    goto('/dashboard');
  }
</script>

<svelte:head>
  <title>Verify Email | GUDIC Auctions</title>
</svelte:head>

<div class="min-h-[80vh] flex flex-col justify-center py-12">
  <div class="max-w-md w-full mx-auto px-4" in:fly={{ y: 20, duration: 600, delay: 200 }}>
    <!-- Decorative elements -->
    <div class="absolute -z-10 w-64 h-64 rounded-full bg-primary-blue/20 blur-3xl -top-10 -left-20 animate-blob"></div>
    <div class="absolute -z-10 w-64 h-64 rounded-full bg-primary-peach/20 blur-3xl -bottom-10 -right-20 animate-blob animation-delay-2000"></div>
    
    <!-- Verification card -->
    <div class="relative glass-effect rounded-2xl shadow-xl p-8 border border-white/20">
      <!-- Logo -->
      <div class="flex justify-center mb-6">
        <div class="w-16 h-16 flex items-center justify-center rounded-full bg-gradient-to-br from-primary-blue to-primary-peach shadow-lg">
          <span class="text-white font-bold text-2xl">G</span>
        </div>
      </div>
      
      <!-- Envelope icon -->
      <div class="flex justify-center mb-6" in:fade={{ duration: 800, delay: 400 }}>
        <div class="relative w-24 h-24 flex items-center justify-center">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-24 w-24 text-secondary-blue/70" viewBox="0 0 20 20" fill="currentColor">
            <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z" />
            <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z" />
          </svg>
          <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-success absolute top-6 right-2" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
          </svg>
        </div>
      </div>
      
      <!-- Title -->
      <div class="text-center mb-8">
        <h1 class="text-2xl font-bold text-text-dark mb-2">Verify Your Email</h1>
        <p class="text-text-medium">
          {email ? `We've sent a verification code to ${email}` : 'Enter your email and the verification code we sent you'}
        </p>
      </div>
      
      <!-- Verification Form -->
      <VerificationForm 
        {email} 
        verificationCode={code} 
        redirectTo="/dashboard"
        on:success={handleVerificationSuccess}
      />
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
</style>