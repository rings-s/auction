<!-- src/routes/reset-password/+page.svelte -->
<script>
  import { page } from '$app/stores';
  import { fly, fade } from 'svelte/transition';
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  import { authStore } from '$lib/stores/authStore';
  import { notificationStore } from '$lib/stores/notificationStore';
  import PasswordResetForm from '$lib/components/auth/PasswordResetForm.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Alert from '$lib/components/ui/Alert.svelte';
  
  // Get token and email from URL if available
  let token = $page.url.searchParams.get('token') || '';
  let email = $page.url.searchParams.get('email') || '';
  
  // Success state
  let resetSuccess = false;
  
  // Handle successful password reset
  function handleResetSuccess(event) {
    resetSuccess = true;
    const { autoLogin } = event.detail;
    
    // If auto login, redirect to dashboard, otherwise to login
    setTimeout(() => {
      goto(autoLogin ? '/dashboard' : '/login');
    }, 2000);
  }
</script>

<svelte:head>
  <title>Reset Password | GUDIC Auctions</title>
</svelte:head>

<div class="min-h-[80vh] flex flex-col justify-center py-12">
  <div class="max-w-md w-full mx-auto px-4" in:fly={{ y: 20, duration: 600, delay: 200 }}>
    <!-- Decorative elements -->
    <div class="absolute -z-10 w-64 h-64 rounded-full bg-primary-blue/20 blur-3xl -top-10 -left-20 animate-blob"></div>
    <div class="absolute -z-10 w-64 h-64 rounded-full bg-primary-peach/20 blur-3xl -bottom-10 -right-20 animate-blob animation-delay-2000"></div>
    
    <!-- Password reset card -->
    <div class="relative glass-effect rounded-2xl shadow-xl p-8 border border-white/20">
      <!-- Logo -->
      <div class="flex justify-center mb-6">
        <div class="w-16 h-16 flex items-center justify-center rounded-full bg-gradient-to-br from-primary-blue to-primary-peach shadow-lg">
          <span class="text-white font-bold text-2xl">G</span>
        </div>
      </div>
      
      {#if resetSuccess}
        <!-- Success message after password reset -->
        <div class="text-center" in:fade={{ duration: 300 }}>
          <div class="mb-6">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          
          <h1 class="text-2xl font-bold text-text-dark mb-2">
            Password Reset Successful
          </h1>
          <p class="text-text-medium mb-6">
            Your password has been reset successfully. You will be redirected shortly.
          </p>
          
          <div class="inline-block">
            <div class="h-1.5 w-32 bg-neutral-100 rounded-full overflow-hidden">
              <div class="h-full rounded-full bg-success animate-progress"></div>
            </div>
          </div>
        </div>
      {:else}
        <!-- Reset password form -->
        <PasswordResetForm {email} on:success={handleResetSuccess} />
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
  
  /* Animation for progress bar */
  @keyframes progress {
    from { width: 0; }
    to { width: 100%; }
  }
  
  .animate-progress {
    animation: progress 2s linear forwards;
  }
</style>