<!-- src/routes/login/+page.svelte -->
<script>
  import { goto } from '$app/navigation';
  import { fade, fly } from 'svelte/transition';
  import LoginForm from '$lib/components/auth/LoginForm.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  
  // Handle successful login
  function handleLoginSuccess() {
    goto('/dashboard');
  }
</script>

<svelte:head>
  <title>Sign In | GUDIC Auctions</title>
</svelte:head>

<div class="min-h-[80vh] flex flex-col justify-center">
  <div class="max-w-md w-full mx-auto" in:fly={{ y: 20, duration: 600, delay: 200 }}>
    <!-- Decorative elements -->
    <div class="absolute -z-10 w-64 h-64 rounded-full bg-primary-blue/20 blur-3xl -top-10 -left-20 animate-blob"></div>
    <div class="absolute -z-10 w-64 h-64 rounded-full bg-primary-peach/20 blur-3xl -bottom-10 -right-20 animate-blob animation-delay-2000"></div>
    
    <!-- Login card -->
    <div class="relative glass-effect rounded-2xl shadow-xl p-8 border border-white/20">
      <!-- Logo -->
      <div class="flex justify-center mb-6">
        <div class="w-16 h-16 flex items-center justify-center rounded-full bg-gradient-to-br from-primary-blue to-primary-peach shadow-lg">
          <span class="text-white font-bold text-2xl">G</span>
        </div>
      </div>
      
      <!-- Title -->
      <div class="text-center mb-8">
        <h1 class="text-2xl font-bold text-text-dark mb-2">Welcome Back</h1>
        <p class="text-text-medium">Sign in to your GUDIC account</p>
      </div>
      
      <!-- Login Form -->
      <LoginForm on:success={handleLoginSuccess} />
      
      <!-- Separator -->
      <div class="my-6 flex items-center">
        <div class="flex-grow border-t border-primary-blue/10"></div>
        <div class="px-3 text-sm text-text-medium">or</div>
        <div class="flex-grow border-t border-primary-blue/10"></div>
      </div>
      
     
      
      <!-- Registration link -->
      <div class="text-center">
        <p class="text-text-medium text-sm mb-4">
          Don't have an account?
          <a href="/register" class="text-secondary-blue hover:underline font-medium">
            Create an account
          </a>
        </p>
        
        <a href="/" class="inline-flex items-center text-text-medium hover:text-secondary-blue text-sm">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Back to home
        </a>
      </div>
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