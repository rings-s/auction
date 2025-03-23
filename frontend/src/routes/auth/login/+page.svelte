<!-- src/routes/auth/login/+page.svelte -->
<script>
  import { t } from '$lib/i18n';
  import { isAuthenticated } from '$lib/stores/auth';
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  import { browser } from '$app/environment';
  import { toast } from '$lib/stores/toast';
  import GlassCard from '$lib/components/ui/GlassCard.svelte';
  import LoginForm from '$lib/components/auth/LoginForm.svelte';
  import AuthBackground from '$lib/components/auth/AuthBackground.svelte';
  
  // If user is already authenticated, redirect to dashboard
  onMount(() => {
    if (browser && $isAuthenticated) {
      goto('/dashboard');
    }
  });
  
  // Handle login success
  function handleSuccess() {
    if (browser) {
      toast.success($t('auth.login_success'));
      goto('/dashboard');
    }
  }
  
  // Page title
  const title = $t('auth.login');
</script>

<svelte:head>
  <title>{title} | {$t('general.app_name')}</title>
</svelte:head>

<div class="flex flex-col min-h-screen">
  <AuthBackground />
  
  <main class="flex-1 flex items-center justify-center px-4 py-16 sm:px-6 lg:px-8">
    <div class="w-full max-w-md space-y-8">
      <GlassCard className="p-6 sm:p-8">
        <div class="mb-8">
          <div class="flex justify-center">
            <!-- Logo can be added here if needed -->
            <div class="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-6 h-6 text-primary">
                <path d="M11.47 3.84a.75.75 0 011.06 0l8.69 8.69a.75.75 0 101.06-1.06l-8.689-8.69a2.25 2.25 0 00-3.182 0l-8.69 8.69a.75.75 0 001.061 1.06l8.69-8.69z" />
                <path d="M12 5.432l8.159 8.159c.03.03.06.058.091.086v6.198c0 1.035-.84 1.875-1.875 1.875H15a.75.75 0 01-.75-.75v-4.5a.75.75 0 00-.75-.75h-3a.75.75 0 00-.75.75V21a.75.75 0 01-.75.75H5.625a1.875 1.875 0 01-1.875-1.875v-6.198a2.29 2.29 0 00.091-.086L12 5.43z" />
              </svg>
            </div>
          </div>
        </div>
        
        <LoginForm on:success={handleSuccess} />
      </GlassCard>
    </div>
  </main>
</div>