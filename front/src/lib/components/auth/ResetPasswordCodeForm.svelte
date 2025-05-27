<script>
    import { createEventDispatcher } from 'svelte';
    import { t } from '$lib/i18n';
    import { fly } from 'svelte/transition';
    
    export let loading = false;
    export let email = '';
    export let resetCode = '';
    
    const dispatch = createEventDispatcher();
    
    let newPassword = '';
    let confirmPassword = '';
    let showNewPassword = false;
    let showConfirmPassword = false;
    let errors = {};
    let touched = {};
    
    // Password strength
    $: passwordStrength = calculatePasswordStrength(newPassword);
    
    function calculatePasswordStrength(pwd) {
      if (!pwd) return 0;
      let score = 0;
      if (pwd.length >= 8) score += 25;
      if (pwd.length >= 12) score += 25;
      if (/[a-z]/.test(pwd)) score += 12.5;
      if (/[A-Z]/.test(pwd)) score += 12.5;
      if (/[0-9]/.test(pwd)) score += 12.5;
      if (/[^A-Za-z0-9]/.test(pwd)) score += 12.5;
      return Math.min(100, score);
    }
    
    $: strengthColor = 
      passwordStrength === 0 ? 'bg-gray-200 dark:bg-gray-700' :
      passwordStrength < 30 ? 'bg-red-500' :
      passwordStrength < 60 ? 'bg-yellow-500' :
      passwordStrength < 80 ? 'bg-blue-500' : 'bg-green-500';
    
    // Validation
    function validateField(field, value) {
      switch (field) {
        case 'email':
          if (!value) return $t('auth.validation.emailRequired');
          const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
          if (!emailRegex.test(value)) return $t('auth.validation.emailInvalid');
          return '';
        
        case 'resetCode':
          if (!value) return $t('auth.validation.codeRequired');
          if (!/^\d{6}$/.test(value)) return $t('auth.validation.codeInvalid');
          return '';
        
        case 'newPassword':
          if (!value) return $t('auth.validation.passwordRequired');
          if (value.length < 8) return $t('auth.validation.passwordMinLength');
          return '';
        
        case 'confirmPassword':
          if (!value) return $t('auth.validation.passwordRequired');
          if (value !== newPassword) return $t('auth.validation.passwordMismatch');
          return '';
        
        default:
          return '';
      }
    }
    
    function handleBlur(field) {
      touched[field] = true;
      errors[field] = validateField(field, field === 'email' ? email : field === 'resetCode' ? resetCode : field === 'newPassword' ? newPassword : confirmPassword);
    }
    
    async function handleSubmit() {
      // Validate all fields
      touched = { email: true, resetCode: true, newPassword: true, confirmPassword: true };
      errors = {
        email: validateField('email', email),
        resetCode: validateField('resetCode', resetCode),
        newPassword: validateField('newPassword', newPassword),
        confirmPassword: validateField('confirmPassword', confirmPassword)
      };
      
      const hasErrors = Object.values(errors).some(error => error);
      if (hasErrors) return;
      
      dispatch('submit', { email, resetCode, newPassword, confirmPassword });
    }
  </script>
  
  <form on:submit|preventDefault={handleSubmit} class="space-y-5">
    <!-- Email -->
    <div class="space-y-1">
      <label for="email" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
        {$t('auth.email')}
      </label>
      <input
        id="email"
        type="email"
        bind:value={email}
        on:blur={() => handleBlur('email')}
        required
        class="
          appearance-none block w-full px-3 py-2.5
          border {errors.email && touched.email ? 'border-red-300 dark:border-red-600' : 'border-gray-300 dark:border-gray-600'}
          rounded-lg shadow-sm placeholder-gray-400 dark:placeholder-gray-500
          focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500
          text-gray-900 dark:text-white bg-white dark:bg-gray-800
          transition-all duration-200
        "
        placeholder="email@example.com"
      />
      {#if errors.email && touched.email}
        <p class="text-sm text-red-600 dark:text-red-400" in:fly={{ y: -5, duration: 200 }}>
          {errors.email}
        </p>
      {/if}
    </div>
  
    <!-- Reset Code -->
    <div class="space-y-1">
      <label for="reset_code" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
        {$t('auth.resetCode')}
      </label>
      <input
        id="reset_code"
        type="text"
        bind:value={resetCode}
        on:blur={() => handleBlur('resetCode')}
        maxlength="6"
        required
        class="
          appearance-none block w-full px-3 py-2.5
          border {errors.resetCode && touched.resetCode ? 'border-red-300 dark:border-red-600' : 'border-gray-300 dark:border-gray-600'}
          rounded-lg shadow-sm placeholder-gray-400 dark:placeholder-gray-500
          focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500
          text-gray-900 dark:text-white bg-white dark:bg-gray-800
          transition-all duration-200
          text-center text-xl font-mono tracking-widest
        "
        placeholder="123456"
      />
      {#if errors.resetCode && touched.resetCode}
        <p class="text-sm text-red-600 dark:text-red-400" in:fly={{ y: -5, duration: 200 }}>
          {errors.resetCode}
        </p>
      {/if}
    </div>
  
    <!-- New Password -->
    <div class="space-y-1">
      <label for="new_password" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
        {$t('auth.newPassword')}
      </label>
      <div class="relative">
        <input
          id="new_password"
          type={showNewPassword ? 'text' : 'password'}
          bind:value={newPassword}
          on:blur={() => handleBlur('newPassword')}
          required
          class="
            appearance-none block w-full pr-10 px-3 py-2.5
            border {errors.newPassword && touched.newPassword ? 'border-red-300 dark:border-red-600' : 'border-gray-300 dark:border-gray-600'}
            rounded-lg shadow-sm placeholder-gray-400 dark:placeholder-gray-500
            focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500
            text-gray-900 dark:text-white bg-white dark:bg-gray-800
            transition-all duration-200
          "
          placeholder="********"
        />
        <button
          type="button"
          on:click={() => showNewPassword = !showNewPassword}
          class="absolute inset-y-0 right-0 pr-3 flex items-center"
        >
          {#if showNewPassword}
            <svg class="h-5 w-5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
            </svg>
          {:else}
            <svg class="h-5 w-5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
          {/if}
        </button>
      </div>
      {#if errors.newPassword && touched.newPassword}
        <p class="text-sm text-red-600 dark:text-red-400" in:fly={{ y: -5, duration: 200 }}>
          {errors.newPassword}
        </p>
      {/if}
      
      <!-- Password Strength -->
      {#if newPassword}
        <div class="mt-2">
          <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 overflow-hidden">
            <div 
              class="h-full transition-all duration-300 ease-out {strengthColor}"
              style="width: {passwordStrength}%"
            ></div>
          </div>
        </div>
      {/if}
    </div>
  
    <!-- Confirm Password -->
    <div class="space-y-1">
      <label for="confirm_password" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
        {$t('auth.confirmPassword')}
      </label>
      <div class="relative">
        <input
          id="confirm_password"
          type={showConfirmPassword ? 'text' : 'password'}
          bind:value={confirmPassword}
          on:blur={() => handleBlur('confirmPassword')}
          required
          class="
            appearance-none block w-full pr-10 px-3 py-2.5
            border {errors.confirmPassword && touched.confirmPassword ? 'border-red-300 dark:border-red-600' : 'border-gray-300 dark:border-gray-600'}
            rounded-lg shadow-sm placeholder-gray-400 dark:placeholder-gray-500
            focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500
            text-gray-900 dark:text-white bg-white dark:bg-gray-800
            transition-all duration-200
          "
          placeholder="********"
        />
        <button
          type="button"
          on:click={() => showConfirmPassword = !showConfirmPassword}
          class="absolute inset-y-0 right-0 pr-3 flex items-center"
        >
          {#if showConfirmPassword}
            <svg class="h-5 w-5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
            </svg>
          {:else}
            <svg class="h-5 w-5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
          {/if}
        </button>
      </div>
      {#if errors.confirmPassword && touched.confirmPassword}
        <p class="text-sm text-red-600 dark:text-red-400" in:fly={{ y: -5, duration: 200 }}>
          {errors.confirmPassword}
        </p>
      {/if}
    </div>
  
    <!-- Submit Button -->
    <button
      type="submit"
      disabled={loading}
      class="
        relative w-full flex justify-center py-3 px-4 
        border border-transparent text-sm font-medium rounded-lg 
        text-white bg-primary-600 hover:bg-primary-700 
        focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 
        disabled:opacity-50 disabled:cursor-not-allowed
        transform transition-all duration-200 hover:scale-[1.02]
      "
    >
      {#if loading}
        <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      {/if}
      {$t('auth.resetPassword')}
    </button>
  </form>