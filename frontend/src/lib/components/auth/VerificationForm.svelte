<script>
  import { createEventDispatcher } from 'svelte';
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  import { authStore } from '$lib/stores/authStore';
  import { notificationStore } from '$lib/stores/notificationStore';
  import Input from '$lib/components/ui/Input.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Alert from '$lib/components/ui/Alert.svelte';
  
  const dispatch = createEventDispatcher();
  
  // Props
  export let email = '';
  export let verificationCode = ''; // If provided in URL
  export let redirectTo = '/dashboard';
  
  // Component state
  let loading = false;
  let error = '';
  let resendLoading = false;
  let resendSuccess = false;
  let resendTimer = 0;
  let resendInterval;
  
  // Code input state - for individual digit inputs
  let codeDigits = ['', '', '', '', '', ''];
  let codeInputRefs = Array(6);
  
  // Watch digits and update verification code
  $: {
    verificationCode = codeDigits.join('');
  }
  
  onMount(() => {
    // Focus first digit input if we have email
    if (email && codeInputRefs[0]) {
      codeInputRefs[0].focus();
    }
    
    // If we have a code from URL, populate the digits
    if (verificationCode && verificationCode.length === 6) {
      codeDigits = verificationCode.split('');
    }
    
    // Clean up interval on component unmount
    return () => {
      if (resendInterval) {
        clearInterval(resendInterval);
      }
    };
  });
  
  // Handle digit input focus and navigation
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
  
  // Handle backspace to navigate to previous input
  function handleDigitKeydown(index, event) {
    if (event.key === 'Backspace') {
      if (codeDigits[index] === '' && index > 0) {
        codeInputRefs[index - 1].focus();
      }
    }
  }
  
  // Handle paste into code inputs
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

  async function handleVerify() {
    if (!email || !verificationCode || verificationCode.length !== 6) {
      error = 'Please enter the 6-digit verification code';
      return;
    }
    
    loading = true;
    error = '';
    
    try {
      console.log('Verifying email:', email, 'with code:', verificationCode);
      
      // Call the actual API through the auth store
      const result = await authStore.verifyEmail(email, verificationCode);
      
      if (result) {
        notificationStore.success('Email verified successfully!');
        
        // Emit success event
        dispatch('success');
        
        // Redirect to dashboard or specified route after a short delay
        setTimeout(() => {
          goto(redirectTo);
        }, 1000);
      }
    } catch (err) {
      console.error('Verification error:', err);
      
      // Specific error handling based on error codes
      if (err.code === 'invalid_code') {
        error = 'Invalid or expired verification code';
      } else if (err.code === 'verification_code_expired') {
        error = 'Your verification code has expired. Please request a new one.';
      } else if (err.status === 400) {
        error = err.error || 'Verification failed. Please check your code.';
      } else {
        error = err.error || 'Verification failed. Please try again.';
      }
      
      notificationStore.error(error);
    } finally {
      loading = false;
    }
  }
  
  async function handleResend() {
    if (!email) {
      error = 'Email address is required';
      return;
    }
    
    resendLoading = true;
    error = '';
    resendSuccess = false;
    
    try {
      // Call the resend verification API
      const result = await authStore.resendVerification(email);
      
      resendSuccess = true;
      notificationStore.success('Verification code has been sent to your email.');
      
      // Start countdown for resend button (5 minutes)
      resendTimer = 300;
      if (resendInterval) {
        clearInterval(resendInterval);
      }
      
      resendInterval = setInterval(() => {
        resendTimer -= 1;
        if (resendTimer <= 0) {
          clearInterval(resendInterval);
        }
      }, 1000);
    } catch (err) {
      console.error('Resend verification error:', err);
      
      // Specific error handling
      if (err.code === 'rate_limit' || err.status === 429) {
        error = 'Please wait before requesting another verification code';
      } else {
        error = err.error || 'Failed to resend verification code. Please try again.';
      }
      
      notificationStore.error(error);
    } finally {
      resendLoading = false;
    }
  }
  
  function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  }
</script>

<div class="space-y-6">
  <!-- Email field (shown if not provided) -->
  {#if !email}
    <Input
      type="email"
      id="verification-email"
      name="email"
      label="Email Address"
      bind:value={email}
      required
    />
  {/if}
  
  {#if error}
    <Alert variant="error">{error}</Alert>
  {/if}
  
  {#if resendSuccess}
    <Alert variant="success">
      Verification code has been sent to your email.
    </Alert>
  {/if}
  
  <p class="text-sm text-text-medium">
    Enter the 6-digit verification code sent to {email || "your email"}.
  </p>
  
  <!-- Code input with individual digits for better UX -->
  <div class="mt-6">
    <label for="verification-code" class="sr-only">Verification Code</label>
    
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
        />
      {/each}
    </div>
  </div>
  
  <div>
    <Button
      type="button"
      variant="primary"
      size="lg"
      fullWidth={true}
      disabled={loading || verificationCode.length !== 6}
      loading={loading}
      onClick={handleVerify}
    >
      Verify Email
    </Button>
  </div>
  
  <div class="text-center">
    <p class="text-sm text-text-medium mb-2">
      Didn't receive the code?
    </p>
    
    {#if resendTimer > 0}
      <p class="text-sm text-text-medium">
        You can request a new code in <span class="text-secondary-blue font-medium">{formatTime(resendTimer)}</span>
      </p>
    {:else}
      <Button
        type="button"
        variant="outline"
        size="md"
        disabled={resendLoading || !email}
        loading={resendLoading}
        onClick={handleResend}
      >
        Resend Verification Code
      </Button>
    {/if}
  </div>
  
  <div class="text-center text-sm">
    <p class="text-text-medium">
      Changed your mind?
      <a href="/login" class="font-medium text-secondary-blue hover:text-secondary-blue/80 transition-colors">
        Back to login
      </a>
    </p>
  </div>
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