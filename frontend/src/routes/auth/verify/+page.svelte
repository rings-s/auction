<!-- src/routes/auth/verify/+page.svelte -->
<script>
  import { t } from '$lib/i18n';
  import { isAuthenticated } from '$lib/stores/auth';
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  import { toast } from '$lib/stores/toast';
  import GlassCard from '$lib/components/ui/GlassCard.svelte';
  import VerificationForm from '$lib/components/auth/VerificationForm.svelte';
  import AuthBackground from '$lib/components/auth/AuthBackground.svelte';
  
  // If user is already authenticated, redirect to dashboard
  onMount(() => {
    if ($isAuthenticated) {
      goto('/dashboard');
    }
  });
  
  // Handle verification success
  function handleSuccess() {
    toast.success($t('auth.account_verified'));
    // Redirect handled by the component itself
  }
  
  // Page title
  const title = $t('auth.verify_account');
</script>

<svelte:head>
  <title>{title} | {$t('general.app_name')}</title>
</svelte:head>

<div class="flex flex-col min-h-screen">
  <AuthBackground />
  
  <main class="flex-1 flex items-center justify-center px-4 py-12 sm:px-6 lg:px-8">
    <div class="w-full max-w-md space-y-8">
      <GlassCard className="p-6 sm:p-8">
        <div class="mb-8">
          <div class="flex justify-center">
            <!-- Logo can be added here if needed -->
            <div class="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-6 h-6 text-primary">
                <path fill-rule="evenodd" d="M12 1.5a5.25 5.25 0 00-5.25 5.25v3a3 3 0 00-3 3v6.75a3 3 0 003 3h10.5a3 3 0 003-3v-6.75a3 3 0 00-3-3v-3c0-2.9-2.35-5.25-5.25-5.25zm3.75 8.25v-3a3.75 3.75 0 10-7.5 0v3h7.5z" clip-rule="evenodd" />
              </svg>
            </div>
          </div>
        </div>
        
        <VerificationForm on:success={handleSuccess} />
      </GlassCard>
    </div>
  </main>
</div>