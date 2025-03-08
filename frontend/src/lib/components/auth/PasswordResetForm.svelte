<!-- src/lib/components/auth/PasswordResetForm.svelte -->
<script>
  import { createEventDispatcher } from 'svelte';
  import { goto } from '$app/navigation';
  import { authStore } from '$lib/stores/authStore';
  import { notificationStore } from '$lib/stores/notificationStore';
  import Input from '$lib/components/ui/Input.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Alert from '$lib/components/ui/Alert.svelte';
  
  const dispatch = createEventDispatcher();
  
  // Props
  export let email = '';
  export let redirectTo = '/login';
  
  // Component state
  let step = email ? 'verify' : 'request';
  let loading = false;
  let error = '';
  let success = '';
  let resendCooldown = 0;
  let resendTimer;
  
  // Form data
  let requestEmail = email;
  let resetCode = '';
  let newPassword = '';
  let confirmPassword = '';
  
  // Code input state for better UX
  let codeDigits = ['', '', '', '', '', ''];
  let codeInputRefs = Array(6);
  
  // Watch digits and update reset code
  $: {
    resetCode = codeDigits.join('');
  }
  
  // Handle password strength
  $: passwordStrength = getPasswordStrength(newPassword);
  
  // Check if passwords match
  $: passwordsMatch = confirmPassword ? newPassword === confirmPassword : true;
  
  // When the component is destroyed, clear any timers
  function onDestroy() {
    if (resendTimer) {
      clearInterval(resendTimer);
    }
  }
  
  /**
   * Request password reset code
   */
  async function requestReset() {
    if (!requestEmail) {
      error = 'Email address is required';
      return;
    }
    
    loading = true;
    error = '';
    success = '';
    
    try {
      console.log('Requesting password reset for:', requestEmail);
      await authStore.requestPasswordReset(requestEmail);
      
      // Update step to verification
      email = requestEmail; // Set the email for future steps
      step = 'verify';
      success = 'A password reset code has been sent to your email address.';
      
      // Start cooldown timer
      startCooldownTimer();
      
      notificationStore.success('Password reset code sent successfully!');
    } catch (err) {
      console.error('Request password reset error:', err);
      
      if (err.code === 'rate_limit') {
        error = 'Please wait before requesting another reset code';
      } else {
        error = err.error || 'Failed to send reset code. Please try again.';
      }
      
      notificationStore.error(error);
    } finally {
      loading = false;
    }
  }
  
  /**
   * Verify reset code
   */
  async function verifyResetCode() {
    if (!email || !resetCode) {
      error = 'Email and reset code are required';
      return;
    }
    
    loading = true;
    error = '';
    success = '';
    
    try {
      console.log('Verifying reset code:', resetCode, 'for email:', email);
      // Call API to verify reset code
      await authStore.verifyResetCode(email, resetCode);
      
      // Update step to reset password
      step = 'reset';
      success = 'Reset code verified. Please set a new password.';
      
      notificationStore.success('Reset code verified successfully!');
    } catch (err) {
      console.error('Verify reset code error:', err);
      
      if (err.code === 'invalid_code') {
        error = 'Invalid reset code. Please check and try again.';
      } else if (err.code === 'reset_code_expired') {
        error = 'Reset code has expired. Please request a new one.';
        // Reset to request step
        step = 'request';
      } else {
        error = err.error || 'Failed to verify reset code. Please try again.';
      }
      
      notificationStore.error(error);
    } finally {
      loading = false;
    }
  }
  
  /**
   * Complete password reset with new password
   */
  async function resetPassword() {
    if (!email || !resetCode) {
      error = 'Email and reset code are required';
      return;
    }
    
    if (!newPassword || !confirmPassword) {
      error = 'Please enter and confirm your new password';
      return;
    }
    
    if (newPassword !== confirmPassword) {
      error = 'Passwords do not match';
      return;
    }
    
    if (passwordStrength.strength === 'weak') {
      error = 'Please use a stronger password';
      return;
    }
    
    loading = true;
    error = '';
    success = '';
    
    try {
      console.log('Resetting password for email:', email, 'with code:', resetCode);
      // Call API to reset password
      const result = await authStore.resetPassword(resetCode, email, newPassword, confirmPassword);
      
      success = 'Password has been reset successfully!';
      notificationStore.success(success);
      
      // If result contains tokens, user is automatically logged in
      if (result && result.access) {
        dispatch('success', { email, autoLogin: true });
        
        // Redirect after successful password reset and login
        setTimeout(() => {
          goto(redirectTo);
        }, 1500);
      } else {
        dispatch('success', { email, autoLogin: false });
        
        // Redirect to login
        setTimeout(() => {
          goto('/login');
        }, 1500);
      }
      
    } catch (err) {
      console.error('Reset password error:', err);
      
      if (err.code === 'invalid_code') {
        error = 'Invalid or expired reset code';
      } else if (err.code === 'password_mismatch') {
        error = 'Passwords do not match';
      } else if (err.code === 'invalid_password') {
        error = err.error || 'Password does not meet requirements';
      } else {
        error = err.error || 'Failed to reset password. Please try again.';
      }
      
      notificationStore.error(error);
    } finally {
      loading = false;
    }
  }
  
  /**
   * Resend reset code
   */
  async function resendResetCode() {
    if (resendCooldown > 0) {
      return;
    }
    
    if (!email) {
      email = requestEmail;
    }
    
    loading = true;
    error = '';
    success = '';
    
    try {
      console.log('Resending reset code to:', email);
      await authStore.requestPasswordReset(email);
      
      success = 'A new password reset code has been sent to your email address.';
      notificationStore.success(success);
      
      // Start cooldown timer
      startCooldownTimer();
      
    } catch (err) {
      console.error('Resend reset code error:', err);
      
      if (err.code === 'rate_limit') {
        error = 'Please wait before requesting another reset code';
      } else {
        error = err.error || 'Failed to send reset code. Please try again.';
      }
      
      notificationStore.error(error);
    } finally {
      loading = false;
    }
  }
  
  /**
   * Start cooldown timer for resend button
   */
  function startCooldownTimer() {
    resendCooldown = 60; // 60 seconds cooldown
    
    if (resendTimer) {
      clearInterval(resendTimer);
    }
    
    resendTimer = setInterval(() => {
      resendCooldown -= 1;
      if (resendCooldown <= 0) {
        clearInterval(resendTimer);
      }
    }, 1000);
  }
  
  /**
   * Format cooldown time
   */
  function formatCooldown(seconds) {
    return `${seconds}s`;
  }
  
  /**
   * Check password strength
   */
  function getPasswordStrength(password) {
    // Simple password strength check
    if (!password || password.length < 8) {
      return { strength: 'weak', text: 'Weak', color: 'text-error' };
    }
    
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
  
  /**
   * Handle digit input focus and navigation
   */
  function handleDigitInput(index, event) {
    const value = event.target.value;
    
    // Only allow numeric input
    if (!/^[0-9]$/.test(value) && value !== '') {
      codeDigits[index] = '';
      return;
    }
    
    // Update the digit
    codeDigits[index] = value;
    codeDigits = [...codeDigits]; // Force reactivity
    
    // Auto-focus next input
    if (value !== '' && index < 5) {
      codeInputRefs[index + 1].focus();
    }
  }
  
  /**
   * Handle backspace to navigate to previous input
   */
  function handleDigitKeydown(index, event) {
    if (event.key === 'Backspace') {
      if (codeDigits[index] === '' && index > 0) {
        codeInputRefs[index - 1].focus();
      }
    }
  }
  
  /**
   * Handle paste into code inputs
   */
  function handleCodePaste(event) {
    event.preventDefault();
    const pastedData = event.clipboardData.getData('text');
    
    // Only process if it looks like a code (numbers only)
    if (/^\d+$/.test(pastedData)) {
      const digits = pastedData.slice(0, 6).split('');
      
      // Fill available positions
      for (let i = 0; i < digits.length && i < 6; i++) {
        codeDigits[i] = digits[i];
      }
      
      codeDigits = [...codeDigits]; // Force reactivity
      
      // Focus the next empty input or the last one
      for (let i = 0; i < 6; i++) {
        if (!codeDigits[i]) {
          codeInputRefs[i].focus();
          return;
        }
      }
      
      // If all filled, focus the last one
      codeInputRefs[5].focus();
    }
  }
  
  /**
   * Go back to previous step
   */
  function goBack() {
    if (step === 'verify') {
      step = 'request';
    } else if (step === 'reset') {
      step = 'verify';
    }
    
    error = '';
    success = '';
  }
</script>

<div class="space-y-6">
  <!-- Request Reset Step -->
  {#if step === 'request'}
    <h2 class="text-xl font-semibold text-text-dark mb-4">Reset Your Password</h2>
    
    {#if error}
      <Alert variant="error">{error}</Alert>
    {/if}
    
    {#if success}
      <Alert variant="success">{success}</Alert>
    {/if}
    
    <p class="text-sm text-text-medium mb-6">
      Enter your email address and we'll send you instructions to reset your password.
    </p>
    
    <form on:submit|preventDefault={requestReset} class="space-y-4">
      <Input
        type="email"
        id="reset-email"
        name="email"
        label="Email Address"
        bind:value={requestEmail}
        required
        disabled={loading}
      />
      
      <div class="pt-2">
        <Button
          type="submit"
          variant="primary"
          size="lg"
          fullWidth={true}
          disabled={loading || !requestEmail}
          loading={loading}
        >
          Send Reset Instructions
        </Button>
      </div>
      
      <div class="text-center pt-4">
        <a href="/login" class="text-sm text-secondary-blue hover:text-secondary-blue/80">
          Back to login
        </a>
      </div>
    </form>
  {/if}
  
  <!-- Verify Reset Code Step -->
  {#if step === 'verify'}
    <h2 class="text-xl font-semibold text-text-dark mb-4">Verify Reset Code</h2>
    
    {#if error}
      <Alert variant="error">{error}</Alert>
    {/if}
    
    {#if success}
      <Alert variant="success">{success}</Alert>
    {/if}
    
    <p class="text-sm text-text-medium mb-4">
      Enter the 6-digit reset code sent to <span class="font-medium">{email}</span>
    </p>
    
    <form on:submit|preventDefault={verifyResetCode} class="space-y-6">
      <!-- Code input with individual digits for better UX -->
      <div>
        <label for="reset-code" class="block text-sm font-medium text-text-dark mb-2">Reset Code</label>
        
        <div class="flex justify-between items-center gap-2">
          {#each Array(6) as _, i}
            <input
              type="text"
              inputmode="numeric"
              maxlength="1"
              class="w-11 h-14 text-center text-xl text-text-dark font-semibold rounded-lg border-2 border-primary-blue/30 focus:border-secondary-blue focus:ring-2 focus:ring-primary-blue/20 transition-all"
              bind:value={codeDigits[i]}
              bind:this={codeInputRefs[i]}
              on:input={(e) => handleDigitInput(i, e)}
              on:keydown={(e) => handleDigitKeydown(i, e)}
              on:paste={handleCodePaste}
              disabled={loading}
            />
          {/each}
        </div>
      </div>
      
      <div class="flex space-x-4 pt-2">
        <Button
          type="button"
          variant="outline"
          size="lg"
          on:click={goBack}
          disabled={loading}
        >
          Back
        </Button>
        
        <Button
          type="submit"
          variant="primary"
          size="lg"
          fullWidth={true}
          disabled={loading || resetCode.length !== 6}
          loading={loading}
        >
          Verify Code
        </Button>
      </div>
      
      <div class="text-center pt-2">
        <p class="text-sm text-text-medium mb-2">
          Didn't receive the code?
        </p>
        
        {#if resendCooldown > 0}
          <p class="text-sm text-text-medium">
            You can request a new code in <span class="text-secondary-blue font-medium">{formatCooldown(resendCooldown)}</span>
          </p>
        {:else}
          <Button
            type="button"
            variant="text"
            size="sm"
            on:click={resendResetCode}
            disabled={loading || resendCooldown > 0}
          >
            Resend Reset Code
          </Button>
        {/if}
      </div>
    </form>
  {/if}
  
  <!-- Reset Password Step -->
  {#if step === 'reset'}
    <h2 class="text-xl font-semibold text-text-dark mb-4">Create New Password</h2>
    
    {#if error}
      <Alert variant="error">{error}</Alert>
    {/if}
    
    {#if success}
      <Alert variant="success">{success}</Alert>
    {/if}
    
    <p class="text-sm text-text-medium mb-6">
      Please create a new password for your account.
    </p>
    
    <form on:submit|preventDefault={resetPassword} class="space-y-4">
      <!-- Password field -->
      <div>
        <Input
          type="password"
          id="new-password"
          name="new-password"
          label="New Password"
          bind:value={newPassword}
          autocomplete="new-password"
          required
          disabled={loading}
          error={passwordStrength?.strength === 'weak' ? 'Password is too weak' : ''}
          helper="At least 8 characters with a mix of letters, numbers, and symbols"
        />
        
        {#if newPassword}
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
      <Input
        type="password"
        id="confirm-password"
        name="confirm-password"
        label="Confirm Password"
        bind:value={confirmPassword}
        autocomplete="new-password"
        required
        disabled={loading}
        error={!passwordsMatch && confirmPassword ? 'Passwords do not match' : ''}
      />
      
      <div class="flex space-x-4 pt-2">
        <Button
          type="button"
          variant="outline"
          size="lg"
          on:click={goBack}
          disabled={loading}
        >
          Back
        </Button>
        
        <Button
          type="submit"
          variant="primary"
          size="lg"
          fullWidth={true}
          disabled={loading || !newPassword || !confirmPassword || !passwordsMatch || passwordStrength.strength === 'weak'}
          loading={loading}
        >
          Reset Password
        </Button>
      </div>
    </form>
  {/if}
</div>

<style>
  /* Custom styling for digit inputs */
  input[type="text"] {
    -webkit-appearance: none;
    -moz-appearance: textfield;
  }
  
  /* Remove arrows from number inputs */
  input::-webkit-outer-spin-button,
  input::-webkit-inner-spin-button {
    -webkit-appearance: none;
    margin: 0;
  }
  
  /* Focus animation for code inputs */
  input:focus {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(185, 220, 242, 0.25);
  }
</style>