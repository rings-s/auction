<script>
  import { createEventDispatcher } from 'svelte';
  import { goto } from '$app/navigation';
  import { authStore } from '$lib/stores/authStore';
  import { notificationStore } from '$lib/stores/notificationStore';
  import Input from '$lib/components/ui/Input.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Alert from '$lib/components/ui/Alert.svelte';
  
  const dispatch = createEventDispatcher();
  
  export let redirectTo = '/dashboard';
  
  // Form data
  let email = '';
  let password = '';
  
  // Form state
  let loading = false;
  let error = '';
  let showResetPassword = false;
  let resetEmail = '';
  let resetSent = false;
  
  async function handleLogin() {
    if (!email || !password) {
      error = 'Please enter both email and password';
      return;
    }
    
    loading = true;
    error = '';
    
    try {
      // Call auth API through auth store
      await authStore.login(email, password);
      
      loading = false;
      
      // Show success notification
      notificationStore.success('Welcome back! You have successfully signed in.');
      
      // Redirect after successful login
      goto(redirectTo);
      
      // Emit success event
      dispatch('success');
      
    } catch (err) {
      console.error('Login error:', err);
      
      // Handle error based on response
      if (err.status === 401 || err.status === 403) {
        error = 'Invalid email or password';
      } else if (err.status === 429) {
        error = 'Too many login attempts. Please try again later.';
      } else {
        error = err.error || 'Login failed. Please try again.';
      }
      
      notificationStore.error(error);
      loading = false;
    }
  }
  
  async function handleResetPassword() {
    if (!resetEmail) {
      error = 'Please enter your email address';
      return;
    }
    
    loading = true;
    error = '';
    
    try {
      // Call your password reset API here
      // Example: await authStore.requestPasswordReset(resetEmail);
      
      // Simulate API call response
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      resetSent = true;
      showResetPassword = false;
      
      notificationStore.success('Password reset instructions have been sent to your email.');
    } catch (err) {
      console.error('Reset password error:', err);
      error = 'Failed to send reset instructions. Please try again.';
      notificationStore.error(error);
    } finally {
      loading = false;
    }
  }
  
  function toggleResetPassword() {
    showResetPassword = !showResetPassword;
    resetEmail = email;
    error = '';
  }
</script>

<div class="space-y-6">
  {#if resetSent}
    <Alert variant="success">
      If an account exists with this email, password reset instructions have been sent to your inbox.
    </Alert>
  {:else if showResetPassword}
    <form on:submit|preventDefault={handleResetPassword} class="space-y-6 fade-in-up">
      <h2 class="text-xl font-semibold text-text-dark">Reset Password</h2>
      
      {#if error}
        <Alert variant="error">{error}</Alert>
      {/if}
      
      <p class="text-sm text-text-medium">
        Enter your email address and we'll send you instructions to reset your password.
      </p>
      
      <Input
        type="email"
        id="reset-email"
        name="email"
        label="Email Address"
        bind:value={resetEmail}
        required
      />
      
      <div class="flex items-center justify-between space-x-4">
        <Button
          type="button"
          variant="outline"
          size="md"
          on:click={toggleResetPassword}
          disabled={loading}
        >
          Back to login
        </Button>
        
        <Button
          type="submit"
          variant="primary"
          size="md"
          disabled={loading}
          loading={loading}
        >
          Send Instructions
        </Button>
      </div>
    </form>
  {:else}
    <form on:submit|preventDefault={handleLogin} class="space-y-6">
      {#if error}
        <Alert variant="error">{error}</Alert>
      {/if}
      
      <Input
        type="email"
        id="email"
        name="email"
        label="Email Address"
        bind:value={email}
        autocomplete="email"
        required
      />
      
      <div>
        <Input
          type="password"
          id="password"
          name="password"
          label="Password"
          bind:value={password}
          autocomplete="current-password"
          required
        />
        <div class="mt-1 text-right">
          <button
            type="button"
            class="text-sm font-medium text-secondary-blue hover:text-secondary-blue/80 transition-colors"
            on:click={toggleResetPassword}
          >
            Forgot your password?
          </button>
        </div>
      </div>
      
      <div class="flex items-center justify-between">
        <div class="flex items-center">
          <input
            id="remember-me"
            name="remember-me"
            type="checkbox"
            class="h-4 w-4 rounded border-primary-blue/30 text-secondary-blue focus:ring-secondary-blue"
          />
          <label for="remember-me" class="ml-2 block text-sm text-text-medium">
            Remember me
          </label>
        </div>
      </div>
      
      <div>
        <Button
          type="submit"
          variant="primary"
          size="lg"
          fullWidth={true}
          disabled={loading}
          loading={loading}
        >
          Sign in
        </Button>
      </div>
    </form>
  {/if}
</div>

<style>
  /* Fade-in animation for the reset password form */
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