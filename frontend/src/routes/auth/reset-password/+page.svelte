<!-- src/routes/auth/reset-password/+page.svelte -->
<script>
  import { t } from '$lib/i18n';
  import { isAuthenticated } from '$lib/stores/auth';
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { toast } from '$lib/stores/toast';
  import GlassCard from '$lib/components/ui/GlassCard.svelte';
  import PasswordReset from '$lib/components/auth/PasswordReset.svelte';
  import AuthBackground from '$lib/components/auth/AuthBackground.svelte';
  
  // If user is already authenticated, redirect to dashboard
  onMount(() => {
    if ($isAuthenticated) {
      goto('/dashboard');
    }
  });
  
  // Determine initial mode based on URL parameters
  let initialMode = 'request';
  
  $: {
    if ($page.url.searchParams.has('code')) {
      initialMode = 'reset';
    }
  }
  
  // Handle reset success
  function handleResetSuccess() {
    toast.success($t('system_messages.password_reset_success'));
    // Redirect handled by the component itself
  }
  
  // Page title
  const title = $t('auth.reset_password');
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
                <path fill-rule="evenodd" d="M15.75 1.5a6.75 6.75 0 00-6.651 7.906c.067.39-.032.717-.221.906l-6.5 6.499a3 3 0 00-.878 2.121v2.818c0 .414.336.75.75.75H6a.75.75 0 00.75-.75v-1.5h1.5A.75.75 0 009 19.5V18h1.5a.75.75 0 00.53-.22l2.658-2.658c.19-.189.517-.288.906-.22A6.75 6.75 0 1015.75 1.5zm0 3a.75.75 0 000 1.5A2.25 2.25 0 0118 8.25a.75.75 0 001.5 0 3.75 3.75 0 00-3.75-3.75z" clip-rule="evenodd" />
              </svg>
            </div>
          </div>
        </div>
        
        <PasswordReset 
          mode={initialMode} 
          on:reset-success={handleResetSuccess} 
        />
      </GlassCard>
    </div>
  </main>
</div>